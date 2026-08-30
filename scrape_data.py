import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import json
from pathlib import Path
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
    return response.text

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

        if region not in gcp_coordinates:
            raise DataRefreshError(
                f"GCP region metadata is missing for: {region}"
            )
        record = regions.setdefault(
            region,
            {
                "region": region,
                "lat": gcp_coordinates[region]["lat"],
                "lon": gcp_coordinates[region]["lon"],
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

    cleaned_data = []
    for h2_tag in h2_tags:
        tag = h2_tag
        region = tag.select_one("code").text.strip()
        heading = re.sub(r"\s+", " ", tag.get_text(" ", strip=True))
        location = re.sub(
            rf"\s*[—–-]\s*{re.escape(region)}\s*$", "", heading
        ).strip()
        for li in tag.find_next("ul").find_all("li"):
            if "Accelerated Computing" in li.text.strip():
                # print(li.text.strip())
                gpu_types = (
                    li.text.strip()
                    .split("Accelerated Computing:")[1]
                    .strip()
                    .split("|")
                )
                gpu_types = sorted({g.strip() for g in gpu_types if g.strip()})
                if "GovCloud" in location:
                    continue
                if region not in aws_coordinates:
                    raise DataRefreshError(
                        f"AWS region metadata is missing for: {region}"
                    )
                cleaned_data.append(
                    {
                        "region": region,
                        "lat": aws_coordinates[region]["lat"],
                        "lon": aws_coordinates[region]["lon"],
                        "location": location,
                        "families": gpu_types,
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
        candidate = json.loads(match.group(1))
        if any(item.get("OfferingName") == "Virtual Machines" for item in candidate):
            data_list = candidate
            break

    if not data_list:
        raise DataRefreshError("Azure GPU availability data was not found")

    gpu_machine_types = ["NC", "ND", "NG", "NV"]
    azure_gpu_vms = [
        item
        for item in data_list
        if item["OfferingName"] == "Virtual Machines"
        and any(item["ProductSkuName"].startswith(prefix) for prefix in gpu_machine_types)
        and item["CurrentState"] == "GA"
    ]
    gpus_per_region = defaultdict(set)
    for vm_type in azure_gpu_vms:
        region = (
            vm_type["RegionName"]
            .lower()
            .strip()
            .replace(" ", "-")
            .replace("-*", "")
        )
        gpus_per_region[region].add(vm_type["ProductSkuName"])

    cleaned_data = []
    reserved_regions = ("china-east-3", "australia-central-2", "korea-south")
    for region in gpus_per_region:
        if region.startswith("usgov") or region in reserved_regions:
            continue
        if region not in azure_data:
            raise DataRefreshError(
                f"Azure region metadata is missing for: {region}"
            )
        cleaned_data.append(
            {
                "region": region,
                "lat": azure_data[region]["lat"],
                "lon": azure_data[region]["lon"],
                "location": azure_data[region]["location"],
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
    with tempfile.TemporaryDirectory(dir=output_dir) as staging_dir:
        staging_path = Path(staging_dir)
        for provider, records in datasets.items():
            content = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
            (staging_path / f"{provider}.json").write_text(content, encoding="utf-8")
        for provider in datasets:
            (staging_path / f"{provider}.json").replace(
                output_dir / f"{provider}.json"
            )
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
