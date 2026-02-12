import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import json

# azure_data = {
#     "australia-central": {"lat": -35.2809, "lon": 149.1300},
#     "australia-east": {"lat": -33.8688, "lon": 151.2093},
#     "australia-southeast": {"lat": -37.8136, "lon": 144.9631},
#     "austria-east": {"lat": 48.2082, "lon": 16.3738},
#     "belgium-central": {"lat": 50.8503, "lon": 4.3517},
#     "brazil-south": {"lat": -23.5505, "lon": -46.6333},
#     "canada-central": {"lat": 43.6532, "lon": -79.3832},
#     "canada-east": {"lat": 46.8139, "lon": -71.2080},
#     "central-india": {"lat": 18.5204, "lon": 73.8567},
#     "central-us": {"lat": 41.5898, "lon": -93.6156},
#     "chile-central": {"lat": -33.4489, "lon": -70.6693},
#     "china-east": {"lat": 31.2304, "lon": 121.4737},
#     "china-east-2": {"lat": 31.2304, "lon": 121.4737},
#     "china-north": {"lat": 39.9042, "lon": 116.4074},
#     "china-north-2": {"lat": 39.9042, "lon": 116.4074},
#     "china-north-3": {"lat": 39.6300, "lon": 118.1800},
#     "denmark-east": {"lat": 55.6761, "lon": 12.5683},
#     "east-asia": {"lat": 22.3193, "lon": 114.1694},
#     "east-us": {"lat": 39.0438, "lon": -77.4874},
#     "east-us-2": {"lat": 36.6646, "lon": -78.3889},
#     "east-us-3": {"lat": 33.7490, "lon": -84.3880},
#     "france-central": {"lat": 48.8566, "lon": 2.3522},
#     "germany-west-central": {"lat": 50.1109, "lon": 8.6821},
#     "greece-central": {"lat": 37.9838, "lon": 23.7275},
#     "india-south-central": {"lat": 17.3850, "lon": 78.4867},
#     "indonesia-central": {"lat": -6.2088, "lon": 106.8456},
#     "israel-central": {"lat": 32.0853, "lon": 34.7818},
#     "italy-north": {"lat": 45.4642, "lon": 9.1900},
#     "japan-east": {"lat": 35.6895, "lon": 139.6917},
#     "japan-west": {"lat": 34.6937, "lon": 135.5023},
#     "korea-central": {"lat": 37.5665, "lon": 126.9780},
#     "malaysia-west": {"lat": 3.1390, "lon": 101.6869},
#     "mexico-central": {"lat": 20.5888, "lon": -100.3899},
#     "newzealand-north": {"lat": -36.8485, "lon": 174.7633},
#     "north-central-us": {"lat": 41.8781, "lon": -87.6298},
#     "north-europe": {"lat": 53.3498, "lon": -6.2603},
#     "norway-east": {"lat": 59.9139, "lon": 10.7522},
#     "poland-central": {"lat": 52.2297, "lon": 21.0122},
#     "qatar-central": {"lat": 25.2854, "lon": 51.5310},
#     "saudi-arabia-east": {"lat": 26.4207, "lon": 50.0888},
#     "south-africa-north": {"lat": -26.2041, "lon": 28.0473},
#     "south-central-us": {"lat": 29.4241, "lon": -98.4936},
#     "south-india": {"lat": 13.0827, "lon": 80.2707},
#     "southeast-asia": {"lat": 1.3521, "lon": 103.8198},
#     "spain-central": {"lat": 40.4168, "lon": -3.7038},
#     "sweden-central": {"lat": 60.6749, "lon": 17.1413},
#     "switzerland-north": {"lat": 47.3769, "lon": 8.5417},
#     "taiwan-north": {"lat": 25.0330, "lon": 121.5654},
#     "thailand-south": {"lat": 13.7563, "lon": 100.5018},
#     "uae-north": {"lat": 25.2048, "lon": 55.2708},
#     "uk-south": {"lat": 51.5074, "lon": -0.1278},
#     "uk-west": {"lat": 51.4816, "lon": -3.1791},
#     "west-central-us": {"lat": 41.1400, "lon": -104.8202},
#     "west-europe": {"lat": 52.3676, "lon": 4.9041},
#     "west-us": {"lat": 37.3382, "lon": -121.8863},
#     "west-us-2": {"lat": 47.6062, "lon": -122.3321},
#     "west-us-3": {"lat": 33.4484, "lon": -112.0740},
# }

azure_data = {
    "australia-central": {
        "location": "Australia Central - Canberra",
        "lat": -35.2809,
        "lon": 149.13,
    },
    "australia-east": {
        "location": "Australia East - New South Wales",
        "lat": -33.8688,
        "lon": 151.2093,
    },
    "australia-southeast": {
        "location": "Australia Southeast - Victoria",
        "lat": -37.8136,
        "lon": 144.9631,
    },
    "austria-east": {
        "location": "Austria East - Vienna",
        "lat": 48.2082,
        "lon": 16.3738,
    },
    "belgium-central": {
        "location": "Belgium Central - Brussels",
        "lat": 50.8503,
        "lon": 4.3517,
    },
    "brazil-south": {
        "location": "Brazil South - São Paulo State",
        "lat": -23.5505,
        "lon": -46.6333,
    },
    "canada-central": {
        "location": "Canada Central - Toronto",
        "lat": 43.6532,
        "lon": -79.3832,
    },
    "canada-east": {
        "location": "Canada East - Quebec City",
        "lat": 46.8139,
        "lon": -71.2082,
    },
    "central-india": {
        "location": "Central India - Pune",
        "lat": 18.5204,
        "lon": 73.8567,
    },
    "central-us": {"location": "Central US - Iowa", "lat": 41.878, "lon": -93.0977},
    "chile-central": {
        "location": "Chile Central - Santiago",
        "lat": -33.4489,
        "lon": -70.6693,
    },
    "china-east": {
        "location": "China East - Shanghai",
        "lat": 31.2304,
        "lon": 121.4737,
    },
    "china-east-2": {
        "location": "China East 2 - Shanghai",
        "lat": 31.2304,
        "lon": 121.4737,
    },
    "china-north": {
        "location": "China North - Beijing",
        "lat": 39.9042,
        "lon": 116.4074,
    },
    "china-north-2": {
        "location": "China North 2 - Beijing",
        "lat": 39.9042,
        "lon": 116.4074,
    },
    "china-north-3": {
        "location": "China North 3 - Hebei",
        "lat": 38.0428,
        "lon": 114.5149,
    },
    "denmark-east": {
        "location": "Denmark East - Copenhagen",
        "lat": 55.6761,
        "lon": 12.5683,
    },
    "denmark-north-europe-4": {
        "location": "Denmark North Europe 4 - Esberg",
        "lat": 55.4674,
        "lon": 8.4506,
    },
    "east-asia": {"location": "East Asia - Hong Kong", "lat": 22.3193, "lon": 114.1694},
    "east-us": {"location": "East US - Virginia", "lat": 37.4316, "lon": -78.6569},
    "east-us-2": {"location": "East US 2 - Virginia", "lat": 37.4316, "lon": -78.6569},
    "east-us-3": {"location": "East US 3 - Georgia", "lat": 32.1656, "lon": -82.9001},
    "france-central": {
        "location": "France Central - Paris",
        "lat": 48.8566,
        "lon": 2.3522,
    },
    "germany-west-central": {
        "location": "Germany West Central - Frankfurt",
        "lat": 50.1109,
        "lon": 8.6821,
    },
    "greece-central": {
        "location": "Greece Central - Athens",
        "lat": 37.9838,
        "lon": 23.7275,
    },
    "india-south-central": {
        "location": "India South Central - Hyderabad",
        "lat": 17.385,
        "lon": 78.4867,
    },
    "indonesia-central": {
        "location": "Indonesia Central - Jakarta",
        "lat": -6.2088,
        "lon": 106.8456,
    },
    "israel-central": {
        "location": "Israel Central - Israel",
        "lat": 31.0461,
        "lon": 34.8516,
    },
    "italy-north": {"location": "Italy North - Milan", "lat": 45.4642, "lon": 9.1899},
    "japan-east": {
        "location": "Japan East - Tokyo, Saitama",
        "lat": 35.6762,
        "lon": 139.6503,
    },
    "japan-west": {"location": "Japan West - Osaka", "lat": 34.6937, "lon": 135.5023},
    "korea-central": {
        "location": "Korea Central - Seoul",
        "lat": 37.5665,
        "lon": 126.978,
    },
    "malaysia-west": {
        "location": "Malaysia West - Kuala Lumpur",
        "lat": 3.139,
        "lon": 101.6869,
    },
    "mexico-central": {
        "location": "Mexico Central - Querétaro State",
        "lat": 20.5888,
        "lon": -100.3899,
    },
    "new-zealand-north": {
        "location": "New Zealand North - Auckland",
        "lat": -36.8485,
        "lon": 174.7633,
    },
    "north-central-us": {
        "location": "North Central US - Illinois",
        "lat": 40.6331,
        "lon": -89.3985,
    },
    "north-europe": {
        "location": "North Europe - Ireland",
        "lat": 53.1424,
        "lon": -7.6921,
    },
    "north-europe-3": {
        "location": "North Europe 3 - Helsinki",
        "lat": 60.1699,
        "lon": 24.9384,
    },
    "norway-east": {"location": "Norway East - Oslo", "lat": 59.9139, "lon": 10.7522},
    "poland-central": {
        "location": "Poland Central - Warsaw",
        "lat": 52.2297,
        "lon": 21.0122,
    },
    "qatar-central": {
        "location": "Qatar Central - Doha",
        "lat": 25.2854,
        "lon": 51.531,
    },
    "saudi-arabia-east": {
        "location": "Saudi Arabia East - Dammam",
        "lat": 26.4207,
        "lon": 50.0888,
    },
    "south-africa-north": {
        "location": "South Africa North - Johannesburg",
        "lat": -26.2041,
        "lon": 28.0473,
    },
    "south-central-us": {
        "location": "South Central US - Texas - San Antonio",
        "lat": 29.4243,
        "lon": -98.4911,
    },
    "south-india": {
        "location": "South India - Chennai",
        "lat": 13.0827,
        "lon": 80.2707,
    },
    "southeast-asia": {
        "location": "Southeast Asia - Singapore",
        "lat": 1.3521,
        "lon": 103.8198,
    },
    "southeast-asia-3": {
        "location": "Southeast Asia 3 - Johor Bahru, Malaysia",
        "lat": 1.4927,
        "lon": 103.7414,
    },
    "spain-central": {
        "location": "Spain Central - Madrid",
        "lat": 40.4168,
        "lon": -3.7038,
    },
    "sweden-central": {
        "location": "Sweden Central - Gävle and Sandviken",
        "lat": 60.6749,
        "lon": 17.1413,
    },
    "switzerland-north": {
        "location": "Switzerland North - Zürich",
        "lat": 47.3769,
        "lon": 8.5417,
    },
    "taiwan-north": {
        "location": "Taiwan North - Taipei",
        "lat": 25.033,
        "lon": 121.5654,
    },
    "thailand-south": {
        "location": "Thailand South - Bangkok",
        "lat": 13.7563,
        "lon": 100.5018,
    },
    "uae-north": {"location": "UAE North - Dubai", "lat": 25.2048, "lon": 55.2708},
    "uk-south": {"location": "UK South - London", "lat": 51.5074, "lon": -0.1278},
    "uk-west": {"location": "UK West - Cardiff", "lat": 51.4816, "lon": -3.1791},
    "west-central-us": {
        "location": "West Central US - Wyoming",
        "lat": 42.756,
        "lon": -107.3025,
    },
    "west-europe": {
        "location": "West Europe - Netherlands",
        "lat": 52.1326,
        "lon": 5.2913,
    },
    "west-us": {"location": "West US - California", "lat": 36.7783, "lon": -119.4179},
    "west-us-2": {
        "location": "West US 2 - Washington",
        "lat": 47.7511,
        "lon": -120.7401,
    },
    "west-us-3": {"location": "West US 3 - Arizona", "lat": 34.0489, "lon": -111.0937},
}

aws_coordinates = {
    "us-east-1": {"lat": 39.0438, "lon": -77.4874},
    "us-east-2": {"lat": 39.9612, "lon": -82.9988},
    "us-west-1": {"lat": 37.8272, "lon": -122.2913},
    "us-west-2": {"lat": 45.5946, "lon": -121.1787},
    "ap-east-1": {"lat": 22.3193, "lon": 114.1694},
    "ap-south-1": {"lat": 19.076, "lon": 72.8777},
    "ap-northeast-2": {"lat": 37.5665, "lon": 126.978},
    "ap-southeast-1": {"lat": 1.3521, "lon": 103.8198},
    "ap-southeast-2": {"lat": -33.8688, "lon": 151.2093},
    "ap-northeast-1": {"lat": 35.6895, "lon": 139.6917},
    "ca-central-1": {"lat": 45.5017, "lon": -73.5673},
    "eu-central-1": {"lat": 50.1109, "lon": 8.6821},
    "eu-west-1": {"lat": 53.3498, "lon": -6.2603},
    "eu-west-2": {"lat": 51.5074, "lon": -0.1278},
    "eu-south-1": {"lat": 45.4642, "lon": 9.19},
    "eu-west-3": {"lat": 48.8566, "lon": 2.3522},
    "eu-north-1": {"lat": 59.3293, "lon": 18.0686},
    "me-south-1": {"lat": 26.2235, "lon": 50.5876},
    "sa-east-1": {"lat": -23.5505, "lon": -46.6333},
    "af-south-1": {"lat": 33.9249, "lon": 18.4241},
    "ap-southeast-3": {"lat": 6.2088, "lon": 106.8456},
    "ap-southeast-5": {"lat": 3.1390, "lon": 101.6869},
    "ap-southeast-4": {"lat": -37.8136, "lon": 144.9631},
    "ap-northeast-3": {"lat": 34.6937, "lon": 135.5023},
    "cn-north-1": {"lat": 39.9042, "lon": 116.4074},
    "cn-northwest-1": {"lat": 38.4872, "lon": 106.2309},
    "eu-south-2": {"lat": 40.4168, "lon": -3.7038},
    "eu-central-2": {"lat": 47.3769, "lon": 8.5417},
    "il-central-1": {"lat": 32.0853, "lon": 34.7818},
    "me-central-1": {"lat": 24.4539, "lon": 54.3773},
    "us-gov-east-1": {"lat": 38.8951, "lon": -77.0364},
    "us-gov-west-1": {"lat": 45.5231, "lon": -122.6765},
}

gcp_coordinates = {
    "asia-east1": {"lat": 24.051, "lon": 120.516},
    "asia-east2": {"lat": 22.3193, "lon": 114.1694},
    "asia-northeast1": {"lat": 35.6895, "lon": 139.6917},
    "asia-northeast2": {"lat": 34.6937, "lon": 135.5023},
    "asia-northeast3": {"lat": 37.5665, "lon": 126.978},
    "asia-south1": {"lat": 19.076, "lon": 72.8777},
    "asia-south2": {"lat": 28.6139, "lon": 77.209},
    "asia-southeast1": {"lat": 1.3521, "lon": 103.8198},
    "asia-southeast2": {"lat": -6.2088, "lon": 106.8456},
    "australia-southeast1": {"lat": -33.8688, "lon": 151.2093},
    "australia-southeast2": {"lat": -37.8136, "lon": 144.9631},
    "europe-central2": {"lat": 52.2297, "lon": 21.0122},
    "europe-north1": {"lat": 60.5693, "lon": 27.1878},
    "europe-west1": {"lat": 50.445, "lon": 3.82},
    "europe-west2": {"lat": 51.5074, "lon": -0.1278},
    "europe-west3": {"lat": 50.1109, "lon": 8.6821},
    "europe-west4": {"lat": 53.442, "lon": 6.83},
    "europe-west6": {"lat": 47.3769, "lon": 8.5417},
    "europe-west8": {"lat": 45.4642, "lon": 9.19},
    "europe-west9": {"lat": 48.8566, "lon": 2.3522},
    "me-central2": {"lat": 26.4207, "lon": 50.0888},
    "me-west1": {"lat": 32.0853, "lon": 34.7818},
    "northamerica-northeast1": {"lat": 45.5017, "lon": -73.5673},
    "northamerica-northeast2": {"lat": 43.6532, "lon": -79.3832},
    "southamerica-east1": {"lat": -23.5329, "lon": -46.792},
    "us-central1": {"lat": 41.2619, "lon": -95.8608},
    "us-east1": {"lat": 33.195, "lon": -80.013},
    "us-east4": {"lat": 39.0438, "lon": -77.4874},
    "us-east5": {"lat": 39.9612, "lon": -82.9988},
    "us-west1": {"lat": 45.5946, "lon": -121.1787},
    "us-west2": {"lat": 34.0522, "lon": -118.2437},
    "us-west3": {"lat": 40.7608, "lon": -111.891},
    "us-west4": {"lat": 36.1699, "lon": -115.1398},
    "us-south1": {"lat": 32.7767, "lon": -96.797},
}


def get_gcp_data():
    gcp_url = (
        "https://docs.cloud.google.com/compute/docs/regions-zones/gpu-regions-zones"
    )
    soup = BeautifulSoup(requests.get(gcp_url).text, "html.parser")
    table = soup.select_one("h2[id='view-using-table']").find_next("table")

    clean_data = []
    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue  # Skip header rows if they exist

        raw_zone = cols[0].get_text(strip=True)
        region = raw_zone.rsplit("-", 1)[0]

        # 1. Clean Location: Replace newlines and multiple spaces with a single space
        raw_location = cols[1].get_text(separator=" ", strip=True)
        clean_location = re.sub(r"\s+", " ", raw_location)
        # 2. Clean GPU Types: Split by the bullet point character and filter out empty strings
        raw_gpus = cols[2].get_text(separator="|", strip=True)
        # This regex splits by the bullet '•' or the pipe we inserted, then cleans whitespace
        gpu_list = [
            re.sub(r"\s+", " ", g).strip().replace("*", " (Limited availability)")
            for g in re.split(r"[•|]", raw_gpus)
            if g.strip()
        ]

        clean_data.append(
            {
                "region": region,
                "lat": gcp_coordinates[region]["lat"],
                "lon": gcp_coordinates[region]["lon"],
                "location": clean_location,
                "families": gpu_list,
            }
        )
    return clean_data


def get_aws_data():
    aws_url = (
        "https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html"
    )
    soup = BeautifulSoup(requests.get(aws_url).text, "html.parser")
    h2_tags = soup.find_all("h2", id=re.compile(r"^instance-types-"))

    cleaned_data = []
    for h2_tag in h2_tags:
        tag = h2_tag
        # <h2 id="instance-types-us-east-1">US East (N. Virginia) â <code class="code">us-east-1</code></h2>
        location = tag.text.strip().split("â")[0].strip()
        region = tag.select_one("code").text.strip()
        for li in tag.find_next("ul").find_all("li"):
            if "Accelerated Computing" in li.text.strip():
                # print(li.text.strip())
                gpu_types = (
                    li.text.strip()
                    .split("Accelerated Computing:")[1]
                    .strip()
                    .split("|")
                )
                gpu_types = [g.strip() for g in gpu_types]
                print(gpu_types)
                print(aws_coordinates[region])
                if "GovCloud" in location:
                    continue
                cleaned_data.append(
                    {
                        "region": region,
                        "lat": aws_coordinates[region]["lat"],
                        "lon": aws_coordinates[region]["lon"],
                        "location": location,
                        "families": gpu_types,
                    }
                )
    return cleaned_data


def get_azure_data():
    azure_url = "https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/table"
    soup = BeautifulSoup(requests.get(azure_url).text, "html.parser")

    script_tag = soup.find("script")

    data_list = []
    if script_tag:
        script_text = script_tag.string
        # 2. Use Regex to find the array
        # Pattern explanation:
        # const data =   : matches the variable declaration
        # (\[.*?\])      : captures everything inside and including the brackets
        # ;              : matches the trailing semicolon
        # re.DOTALL      : ensures the '.' matches newlines as well
        pattern = r"const data\s*=\s*(\[.*?\]);"
        match = re.search(pattern, script_text, re.DOTALL)
        if match:
            json_string = match.group(1)

            # 3. Parse the isolated JSON string into a Python list
            data_list = json.loads(json_string)

        if not data_list:
            raise RuntimeError("Azure data was not scrapped")

        gpu_machine_types = ["NC", "ND", "NG", "NV"]

        azure_gpu_vms = [
            d
            for d in data_list
            if d["OfferingName"] == "Virtual Machines"
            and any(d["ProductSkuName"].startswith(mt) for mt in gpu_machine_types)
            and d["CurrentState"] == "GA"
        ]
        gpus_per_region = defaultdict(list)
        # region_locations = {}
        for vm_type in azure_gpu_vms:
            region = (
                vm_type["RegionName"]
                .lower()
                .strip()
                .replace(" ", "-")
                .replace("-*", "")
            )
            gpus_per_region[region].append(vm_type["ProductSkuName"])
            # region_locations[region] = vm_type["RegionName"]

        cleaned_data = []
        reserved_regions = ("china-east-3", "australia-central-2", "korea-south")
        # https://datacenters.microsoft.com/globe/explore/?view=table
        for region in gpus_per_region:
            if region.startswith("usgov") or region in reserved_regions:
                continue
            cleaned_data.append(
                {
                    "region": region,
                    "lat": azure_data[region]["lat"],
                    "lon": azure_data[region]["lon"],
                    "location": azure_data[region]["location"],
                    "families": gpus_per_region[region],
                }
            )
    return cleaned_data


if __name__ == "__main__":
    for provider, func in {
        "aws": get_aws_data,
        "gcp": get_gcp_data,
        "azure": get_azure_data,
    }.items():
        try:
            data = func()
            with open(provider + ".json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(provider + " failed")
            print(e)
