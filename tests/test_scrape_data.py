from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import os
import runpy
import tempfile
import unittest
from unittest.mock import patch

import scrape_data


FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(
        self,
        text,
        status_error=None,
        mojibake_text=False,
        content_type="text/html; charset=utf-8",
    ):
        self.content = text.encode("utf-8")
        self.text = (
            self.content.decode("latin-1") if mojibake_text else text
        )
        self.status_error = status_error
        self.headers = {"content-type": content_type}

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error


class FetchHtmlTests(unittest.TestCase):
    def test_fetch_html_preserves_utf8_when_response_text_is_mojibake(self):
        html = "<html><body><h2>Africa (Cape Town) — af-south-1</h2></body></html>"
        response = FakeResponse(html, mojibake_text=True)

        with patch.object(scrape_data.requests, "get", return_value=response):
            content = scrape_data.fetch_html("AWS", "https://example.invalid")

        decoded = content.decode("utf-8") if isinstance(content, bytes) else content
        self.assertEqual(decoded, html)

    def test_fetch_html_rejects_successful_error_page(self):
        response = FakeResponse(
            "<html><head><title>Site Unavailable</title></head></html>"
        )

        with patch.object(scrape_data.requests, "get", return_value=response):
            with self.assertRaisesRegex(
                scrape_data.DataRefreshError,
                "GCP source returned an error page: Site Unavailable",
            ):
                scrape_data.fetch_html("GCP", "https://example.invalid")

    def test_fetch_html_rejects_non_html_content(self):
        response = FakeResponse("{}", content_type="application/json")

        with patch.object(scrape_data.requests, "get", return_value=response):
            with self.assertRaisesRegex(
                scrape_data.DataRefreshError,
                "unexpected content type: application/json",
            ):
                scrape_data.fetch_html("Azure", "https://example.invalid")


class RegionMetadataTests(unittest.TestCase):
    def test_aws_southern_hemisphere_latitudes_are_negative(self):
        self.assertEqual(scrape_data.aws_coordinates["af-south-1"]["lat"], -33.9249)
        self.assertEqual(scrape_data.aws_coordinates["ap-southeast-3"]["lat"], -6.2088)

    def test_aws_metadata_covers_accelerator_empty_regions(self):
        expected = {
            "ap-southeast-6",
            "ap-southeast-7",
            "ca-west-1",
            "mx-central-1",
        }

        self.assertTrue(expected.issubset(scrape_data.aws_coordinates))

    def test_all_region_coordinates_are_in_range(self):
        for provider, regions in scrape_data.region_metadata.items():
            for region, metadata in regions.items():
                with self.subTest(provider=provider, region=region):
                    self.assertGreaterEqual(metadata["lat"], -90)
                    self.assertLessEqual(metadata["lat"], 90)
                    self.assertGreaterEqual(metadata["lon"], -180)
                    self.assertLessEqual(metadata["lon"], 180)
                    self.assertTrue(metadata["location"])
                    self.assertIn(
                        metadata.get("status", "active"),
                        {"active", "announced", "restricted"},
                    )


class DataSnapshotTests(unittest.TestCase):
    @staticmethod
    def load(provider):
        path = Path(__file__).parents[1] / f"{provider}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_provider_snapshots_are_sorted_and_unique(self):
        for provider in ("aws", "gcp", "azure"):
            records = self.load(provider)
            regions = [record["region"] for record in records]
            with self.subTest(provider=provider):
                self.assertEqual(regions, sorted(regions))
                self.assertEqual(len(regions), len(set(regions)))
                for record in records:
                    self.assertEqual(
                        record["families"], sorted(set(record["families"]))
                    )

    def test_gcp_snapshot_contains_current_region_and_family_changes(self):
        records = {record["region"]: record for record in self.load("gcp")}

        self.assertEqual(records["australia-southeast2"]["families"], ["A3 High"])
        self.assertEqual(records["europe-west9"]["families"], ["A3 High"])
        self.assertFalse(
            any("N1+P100" in record["families"] for record in records.values())
        )

    def test_aws_snapshot_contains_current_family_changes(self):
        records = {record["region"]: record for record in self.load("aws")}

        self.assertFalse(
            any("G4ad" in record["families"] for record in records.values())
        )
        self.assertIn("P6-B200", records["ap-south-2"]["families"])
        self.assertIn("G7e", records["ap-southeast-3"]["families"])
        self.assertIn("P6-B300", records["sa-east-1"]["families"])

    def test_azure_snapshot_has_canonical_ids_and_nc_v6_regions(self):
        records = {record["region"]: record for record in self.load("azure")}

        for region, record in records.items():
            self.assertEqual(record["region_id"], region.replace("-", ""))
        self.assertIn(
            "NC_RTXPRO6000BSE_v6", records["southeast-asia"]["families"]
        )
        self.assertIn("NC_RTXPRO6000BSE_v6", records["west-us-2"]["families"])


class WorkflowTests(unittest.TestCase):
    def test_refresh_workflow_rejects_committed_data_drift(self):
        workflow = (
            Path(__file__).parents[1] / ".github/workflows/refresh-data.yml"
        ).read_text(encoding="utf-8")
        drift_check = "git diff --exit-code -- aws.json azure.json gcp.json"

        self.assertIn(drift_check, workflow)
        self.assertLess(workflow.index("actions/upload-artifact"), workflow.index(drift_check))

    def test_refresh_workflow_runs_monthly(self):
        workflow = (
            Path(__file__).parents[1] / ".github/workflows/refresh-data.yml"
        ).read_text(encoding="utf-8")

        self.assertIn('cron: "0 8 1 * *"', workflow)


class GcpParserTests(unittest.TestCase):
    def test_get_gcp_data_collapses_zones_and_deduplicates_families(self):
        html = (FIXTURES / "gcp.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            records = scrape_data.get_gcp_data()

        self.assertEqual(
            records,
            [
                {
                    "region": "us-central1",
                    "lat": 41.2619,
                    "lon": -95.8608,
                    "location": "Council Bluffs, Iowa, North America",
                    "families": ["A4X", "G4", "G4 (Fractional GPU)"],
                }
            ],
        )

    def test_get_gcp_data_reports_missing_region_metadata(self):
        html = (FIXTURES / "gcp-unknown-region.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            try:
                scrape_data.get_gcp_data()
            except Exception as exc:
                self.assertIsInstance(exc, RuntimeError)
                self.assertEqual(
                    str(exc),
                    "GCP region metadata is missing for: europe-new9",
                )
            else:
                self.fail("missing region metadata did not stop the refresh")

    def test_get_gcp_data_reports_http_failure(self):
        html = (FIXTURES / "gcp.html").read_text(encoding="utf-8")
        response = FakeResponse(
            html,
            status_error=scrape_data.requests.HTTPError("503 Service Unavailable"),
        )

        with patch.object(scrape_data.requests, "get", return_value=response):
            try:
                scrape_data.get_gcp_data()
            except Exception as exc:
                self.assertIsInstance(exc, RuntimeError)
                self.assertEqual(
                    str(exc),
                    "Failed to fetch GCP data: 503 Service Unavailable",
                )
            else:
                self.fail("HTTP failure did not stop the refresh")

    def test_get_gcp_data_reports_source_schema_change(self):
        html = (FIXTURES / "gcp-bad-schema.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            try:
                scrape_data.get_gcp_data()
            except Exception as exc:
                self.assertIsInstance(exc, RuntimeError)
                self.assertEqual(
                    str(exc),
                    "GCP source schema changed; expected columns: Zone, Location, GPU machine type",
                )
            else:
                self.fail("source schema change did not stop the refresh")


class AwsParserTests(unittest.TestCase):
    def test_get_aws_data_normalizes_heading_and_deduplicates_families(self):
        html = (FIXTURES / "aws.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            records = scrape_data.get_aws_data()

        self.assertEqual(
            records,
            [
                {
                    "region": "us-west-2",
                    "lat": 45.5946,
                    "lon": -121.1787,
                    "location": "US West (Oregon)",
                    "families": ["G7", "P6-B300"],
                }
            ],
        )

    def test_get_aws_data_reports_missing_region_metadata(self):
        html = (FIXTURES / "aws-unknown-region.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            try:
                scrape_data.get_aws_data()
            except Exception as exc:
                self.assertIsInstance(exc, RuntimeError)
                self.assertEqual(
                    str(exc),
                    "AWS region metadata is missing for: eu-new-9",
                )
            else:
                self.fail("missing region metadata did not stop the refresh")

    def test_get_aws_data_does_not_cross_region_section_boundaries(self):
        html = (FIXTURES / "aws-missing-list.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            records = scrape_data.get_aws_data()

        self.assertEqual([record["region"] for record in records], ["us-west-2"])

    def test_get_aws_data_reports_missing_region_headings(self):
        html = "<html><body><p>No region table</p></body></html>"

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            with self.assertRaisesRegex(
                scrape_data.DataRefreshError,
                "AWS source schema changed; no region headings were found",
            ):
                scrape_data.get_aws_data()

    def test_get_aws_data_excludes_govcloud_by_policy(self):
        html = """
        <html><body>
          <h2 id="instance-types-us-gov-east-1">
            AWS GovCloud (US-East) — <code>us-gov-east-1</code>
          </h2>
          <ul><li>Accelerated Computing: G6 | P6-B300</li></ul>
        </body></html>
        """

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            self.assertEqual(scrape_data.get_aws_data(), [])


class AzureParserTests(unittest.TestCase):
    def test_get_azure_data_finds_gpu_dataset_and_deduplicates_families(self):
        html = (FIXTURES / "azure.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            records = scrape_data.get_azure_data()

        self.assertEqual(
            records,
            [
                {
                    "region": "east-us",
                    "region_id": "eastus",
                    "lat": 37.4316,
                    "lon": -78.6569,
                    "location": "East US - Virginia",
                    "families": ["NCads A100 v4-Series"],
                },
                {
                    "region": "west-us",
                    "region_id": "westus",
                    "lat": 36.7783,
                    "lon": -119.4179,
                    "location": "West US - California",
                    "families": ["NVadsA10_v5-series"],
                },
            ],
        )

    def test_get_azure_data_reports_missing_region_metadata(self):
        html = (FIXTURES / "azure-unknown-region.html").read_text(encoding="utf-8")

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            try:
                scrape_data.get_azure_data()
            except Exception as exc:
                self.assertIsInstance(exc, RuntimeError)
                self.assertEqual(
                    str(exc),
                    "Azure region metadata is missing for: atlantis-central",
                )
            else:
                self.fail("missing region metadata did not stop the refresh")

    def test_get_azure_data_reports_invalid_embedded_json(self):
        html = """
        <html><body><script>
        const data = [{"OfferingName": "Virtual Machines",}];
        </script></body></html>
        """

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            with self.assertRaisesRegex(
                scrape_data.DataRefreshError,
                "Azure GPU availability data contains invalid JSON",
            ):
                scrape_data.get_azure_data()

    def test_get_azure_data_reports_unexpected_embedded_schema(self):
        html = """
        <html><body><script>
        const data = ["Virtual Machines"];
        </script></body></html>
        """

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            with self.assertRaisesRegex(
                scrape_data.DataRefreshError,
                "Azure GPU availability data has an unexpected schema",
            ):
                scrape_data.get_azure_data()

    def test_get_azure_data_reports_vm_without_region(self):
        html = """
        <html><body><script>
        const data = [
          {"OfferingName":"Virtual Machines","ProductSkuName":"NCv6","CurrentState":"GA"}
        ];
        </script></body></html>
        """

        with patch.object(scrape_data.requests, "get", return_value=FakeResponse(html)):
            with self.assertRaisesRegex(
                scrape_data.DataRefreshError,
                "Azure GPU availability data has a VM entry without a region",
            ):
                scrape_data.get_azure_data()

class RefreshTransactionTests(unittest.TestCase):
    def test_refresh_restores_previous_files_when_publish_fails(self):
        providers = ("aws", "gcp", "azure")
        previous = {
            provider: f'{{"generation": "old-{provider}"}}\n'
            for provider in providers
        }
        new_data = {
            provider: [{"generation": f"new-{provider}"}]
            for provider in providers
        }
        original_replace = Path.replace

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            for provider, content in previous.items():
                (output_dir / f"{provider}.json").write_text(
                    content, encoding="utf-8"
                )

            failure_injected = False

            def fail_second_publish(source, target):
                nonlocal failure_injected
                if (
                    Path(target) == output_dir / "gcp.json"
                    and not failure_injected
                ):
                    failure_injected = True
                    raise OSError("injected publish failure")
                return original_replace(source, target)

            with (
                patch.object(scrape_data, "get_aws_data", return_value=new_data["aws"]),
                patch.object(scrape_data, "get_gcp_data", return_value=new_data["gcp"]),
                patch.object(scrape_data, "get_azure_data", return_value=new_data["azure"]),
                patch.object(Path, "replace", autospec=True, side_effect=fail_second_publish),
            ):
                with self.assertRaisesRegex(
                    scrape_data.DataRefreshError,
                    "Failed to publish provider data",
                ):
                    scrape_data.refresh_data(output_dir)

            restored = {
                provider: (output_dir / f"{provider}.json").read_text(
                    encoding="utf-8"
                )
                for provider in providers
            }

        self.assertTrue(failure_injected)
        self.assertEqual(restored, previous)

    def test_script_writes_nothing_when_any_provider_fails(self):
        pages = {
            "cloud.google.com": (FIXTURES / "gcp.html").read_text(encoding="utf-8"),
            "aws.amazon.com": (FIXTURES / "aws.html").read_text(encoding="utf-8"),
            "azure.microsoft.com": "<html><body><script>const unrelated = [];</script></body></html>",
        }

        def fake_get(url, timeout):
            for host, html in pages.items():
                if host in url:
                    return FakeResponse(html)
            raise AssertionError(f"unexpected URL: {url}")

        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                with patch.object(scrape_data.requests, "get", side_effect=fake_get):
                    with redirect_stderr(io.StringIO()):
                        try:
                            runpy.run_module("scrape_data", run_name="__main__")
                        except SystemExit as exc:
                            exit_code = exc.code
                        else:
                            exit_code = 0
                generated = sorted(path.name for path in Path(tmpdir).glob("*.json"))
            finally:
                os.chdir(original_cwd)

        self.assertNotEqual(exit_code, 0)
        self.assertEqual(generated, [])

    def test_script_rejects_an_empty_provider_dataset(self):
        pages = {
            "cloud.google.com": (FIXTURES / "gcp-empty.html").read_text(encoding="utf-8"),
            "aws.amazon.com": (FIXTURES / "aws.html").read_text(encoding="utf-8"),
            "azure.microsoft.com": (FIXTURES / "azure.html").read_text(encoding="utf-8"),
        }

        def fake_get(url, timeout):
            for host, html in pages.items():
                if host in url:
                    return FakeResponse(html)
            raise AssertionError(f"unexpected URL: {url}")

        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                with patch.object(scrape_data.requests, "get", side_effect=fake_get):
                    with redirect_stderr(io.StringIO()):
                        try:
                            runpy.run_module("scrape_data", run_name="__main__")
                        except SystemExit as exc:
                            exit_code = exc.code
                        else:
                            exit_code = 0
                generated = sorted(path.name for path in Path(tmpdir).glob("*.json"))
            finally:
                os.chdir(original_cwd)

        self.assertNotEqual(exit_code, 0)
        self.assertEqual(generated, [])


if __name__ == "__main__":
    unittest.main()
