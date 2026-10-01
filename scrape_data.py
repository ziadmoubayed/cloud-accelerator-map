import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import json
from pathlib import Path
import shutil
import sys
import tempfile


class DataRefreshError(RuntimeError):
    """Raised when provider data cannot be refreshed safely."""


def fetch_html(provider, url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise DataRefreshError(f"Failed to fetch {provider} data: {exc}") from exc
    content = response.content
    content_type = getattr(response, "headers", {}).get("content-type", "")
    if content_type and "html" not in content_type.lower():
        raise DataRefreshError(
            f"{provider} source returned unexpected content type: {content_type}"
        )
    if not content or b"<html" not in content[:2048].lower():
        raise DataRefreshError(f"{provider} source did not return an HTML document")
    title_match = re.search(rb"<title[^>]*>(.*?)</title>", content, re.I | re.S)
    if title_match and re.search(
        rb"site unavailable|access denied|request blocked|service unavailable",
        title_match.group(1),
        re.I,
    ):
        title = re.sub(rb"\s+", b" ", title_match.group(1)).decode(
            "utf-8", errors="replace"
        )
        raise DataRefreshError(f"{provider} source returned an error page: {title}")
    return content


REGION_METADATA_PATH = Path(__file__).with_name("region_metadata.json")


def load_region_metadata(path=REGION_METADATA_PATH):
    try:
        metadata = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataRefreshError(f"Unable to load region metadata: {exc}") from exc

    missing = {"aws", "gcp", "azure"} - metadata.keys()
    if missing:
        raise DataRefreshError(
            f"Region metadata is missing providers: {', '.join(sorted(missing))}"
        )
    return metadata


region_metadata = load_region_metadata()
aws_coordinates = region_metadata["aws"]
gcp_coordinates = region_metadata["gcp"]
azure_data = region_metadata["azure"]

AWS_EXCLUDED_REGION_PREFIXES = ("us-gov-",)

# Microsoft documents these GA placements separately from the product-by-region
# payload. Keep them explicit until that payload includes the family.
AZURE_DOCUMENTED_GA_OVERRIDES = {
    "southeast-asia": {"NC_RTXPRO6000BSE_v6"},
    "west-us-2": {"NC_RTXPRO6000BSE_v6"},
}


def metadata_for(provider, region, metadata):
    if region not in metadata:
        raise DataRefreshError(
            f"{provider} region metadata is missing for: {region}"
        )
    record = metadata[region]
    lat = record.get("lat")
    lon = record.get("lon")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        raise DataRefreshError(
            f"{provider} region metadata has an invalid latitude for: {region}"
        )
    if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        raise DataRefreshError(
            f"{provider} region metadata has an invalid longitude for: {region}"
        )
    if not record.get("location"):
        raise DataRefreshError(
            f"{provider} region metadata has no location label for: {region}"
        )
    return record


def get_gcp_data():
    gcp_url = (
        "https://docs.cloud.google.com/compute/docs/regions-zones/gpu-regions-zones"
    )
    soup = BeautifulSoup(fetch_html("GCP", gcp_url), "html.parser")
    required_headers = {"zone", "location", "gpu machine type"}
    table = None
    headers = []
    for candidate in soup.find_all("table"):
        candidate_headers = [
            re.sub(r"\s+", " ", th.get_text(" ", strip=True)).lower()
            for th in candidate.find_all("th")
        ]
        if required_headers.issubset(candidate_headers):
            table = candidate
            headers = candidate_headers
            break
    if table is None:
        raise DataRefreshError(
            "GCP source schema changed; expected columns: "
            "Zone, Location, GPU machine type"
        )

    zone_index = headers.index("zone")
    location_index = headers.index("location")
    gpu_index = headers.index("gpu machine type")
    regions = {}
    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue  # Skip header rows if they exist

        raw_zone = cols[zone_index].get_text(strip=True)
        region = raw_zone.rsplit("-", 1)[0]

        # 1. Clean Location: Replace newlines and multiple spaces with a single space
        raw_location = cols[location_index].get_text(separator=" ", strip=True)
        clean_location = re.sub(r"\s+", " ", raw_location)
        # 2. Clean GPU Types: Split by the bullet point character and filter out empty strings
        raw_gpus = cols[gpu_index].get_text(separator="|", strip=True)
        # This regex splits by the bullet '•' or the pipe we inserted, then cleans whitespace
        gpu_list = [
            re.sub(r"\s+", " ", g).strip().replace("*", " (Limited availability)")
            for g in re.split(r"[•|]", raw_gpus)
            if g.strip()
        ]

        metadata = metadata_for("GCP", region, gcp_coordinates)
        record = regions.setdefault(
            region,
            {
                "region": region,
                "lat": metadata["lat"],
                "lon": metadata["lon"],
                "location": clean_location,
                "families": set(),
            },
        )
        record["families"].update(gpu_list)

    return [
        {**record, "families": sorted(record["families"])}
        for _, record in sorted(regions.items())
    ]


def get_aws_data():
    aws_url = (
        "https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html"
    )
    soup = BeautifulSoup(fetch_html("AWS", aws_url), "html.parser")
    h2_tags = soup.find_all("h2", id=re.compile(r"^instance-types-"))
    if not h2_tags:
        raise DataRefreshError(
            "AWS source schema changed; no region headings were found"
        )

    cleaned_data = []
    for h2_tag in h2_tags:
        code = h2_tag.select_one("code")
        if code is None:
            raise DataRefreshError(
                "AWS source schema changed; a region heading has no region code"
            )
        region = code.get_text(strip=True)
        next_heading = h2_tag.find_next("h2", id=re.compile(r"^instance-types-"))
        gpu_types = set()
        for element in h2_tag.next_elements:
            if element is next_heading:
                break
            if getattr(element, "name", None) != "li":
                continue
            item = re.sub(r"\s+", " ", element.get_text(" ", strip=True))
            if "Accelerated Computing" not in item:
                continue
            match = re.fullmatch(r"Accelerated Computing:\s*(.+)", item)
            if match is None:
                raise DataRefreshError(
                    "AWS source schema changed; unable to parse "
                    f"accelerated instance types for {region}"
                )
            gpu_types.update(
                family.strip()
                for family in match.group(1).split("|")
                if family.strip()
            )

        # GovCloud is intentionally outside the public/commercial map scope.
        if not gpu_types or region.startswith(AWS_EXCLUDED_REGION_PREFIXES):
            continue
        metadata = metadata_for("AWS", region, aws_coordinates)
        cleaned_data.append(
            {
                "region": region,
                "lat": metadata["lat"],
                "lon": metadata["lon"],
                "location": metadata["location"],
                "families": sorted(gpu_types),
            }
        )
    return sorted(cleaned_data, key=lambda record: record["region"])


def get_azure_data():
    azure_url = "https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/table"
    soup = BeautifulSoup(fetch_html("Azure", azure_url), "html.parser")

    data_list = []
    pattern = r"const data\s*=\s*(\[.*?\]);"
    for script_tag in soup.find_all("script"):
        script_text = script_tag.string or script_tag.get_text()
        match = re.search(pattern, script_text, re.DOTALL)
        if not match:
            continue
        try:
            candidate = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            raise DataRefreshError(
                "Azure GPU availability data contains invalid JSON"
            ) from exc
        if not isinstance(candidate, list) or not all(
            isinstance(item, dict) for item in candidate
        ):
            raise DataRefreshError(
                "Azure GPU availability data has an unexpected schema"
            )
        if any(item.get("OfferingName") == "Virtual Machines" for item in candidate):
            data_list = candidate
            break

    if not data_list:
        raise DataRefreshError("Azure GPU availability data was not found")

    gpu_machine_types = ["NC", "ND", "NG", "NV"]
    azure_gpu_vms = [
        item
        for item in data_list
        if item.get("OfferingName") == "Virtual Machines"
        and any(
            item.get("ProductSkuName", "").startswith(prefix)
            for prefix in gpu_machine_types
        )
        and item.get("CurrentState") == "GA"
    ]
    gpus_per_region = defaultdict(set)
    for vm_type in azure_gpu_vms:
        region_name = vm_type.get("RegionName")
        if not isinstance(region_name, str) or not region_name.strip():
            raise DataRefreshError(
                "Azure GPU availability data has a VM entry without a region"
            )
        region = (
            region_name
            .lower()
            .strip()
            .rstrip("*")
            .strip()
            .replace(" ", "-")
        )
        gpus_per_region[region].add(vm_type["ProductSkuName"])

    for region, families in AZURE_DOCUMENTED_GA_OVERRIDES.items():
        gpus_per_region[region].update(families)

    cleaned_data = []
    reserved_regions = ("china-east-3", "australia-central-2", "korea-south")
    for region in gpus_per_region:
        if region.startswith("usgov") or region in reserved_regions:
            continue
        metadata = metadata_for("Azure", region, azure_data)
        cleaned_data.append(
            {
                "region": region,
                "region_id": metadata.get("region_id", region.replace("-", "")),
                "lat": metadata["lat"],
                "lon": metadata["lon"],
                "location": metadata["location"],
                "families": sorted(gpus_per_region[region]),
            }
        )
    return sorted(cleaned_data, key=lambda record: record["region"])


def refresh_data(output_dir=Path(".")):
    providers = {
        "aws": get_aws_data,
        "gcp": get_gcp_data,
        "azure": get_azure_data,
    }
    datasets = {provider: loader() for provider, loader in providers.items()}
    empty_providers = [provider.upper() for provider, records in datasets.items() if not records]
    if empty_providers:
        raise DataRefreshError(
            f"Provider datasets are empty: {', '.join(empty_providers)}"
        )

    output_dir = Path(output_dir)
    with tempfile.TemporaryDirectory(dir=output_dir) as transaction_dir:
        transaction_path = Path(transaction_dir)
        staging_path = transaction_path / "new"
        backup_path = transaction_path / "previous"
        staging_path.mkdir()
        backup_path.mkdir()
        for provider, records in datasets.items():
            content = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
            (staging_path / f"{provider}.json").write_text(content, encoding="utf-8")

        published = []
        try:
            for provider in datasets:
                target = output_dir / f"{provider}.json"
                if target.exists():
                    shutil.copy2(target, backup_path / target.name)
            for provider in datasets:
                (staging_path / f"{provider}.json").replace(
                    output_dir / f"{provider}.json"
                )
                published.append(provider)
        except OSError as exc:
            rollback_errors = []
            for provider in reversed(published):
                target = output_dir / f"{provider}.json"
                backup = backup_path / target.name
                try:
                    if backup.exists():
                        backup.replace(target)
                    else:
                        target.unlink(missing_ok=True)
                except OSError as rollback_exc:
                    rollback_errors.append(f"{provider}: {rollback_exc}")
            message = f"Failed to publish provider data: {exc}"
            if rollback_errors:
                message += "; rollback also failed for " + ", ".join(
                    rollback_errors
                )
            else:
                message += "; previous files restored"
            raise DataRefreshError(message) from exc
    return datasets


def main():
    try:
        refresh_data()
    except DataRefreshError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
