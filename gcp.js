
// --- DATA ---
const gcpData = [
    {
        region: "asia-east1",
        location: "Changhua County, Taiwan",
        lat: 24.051,
        lng: 120.516,
        zones: {
            "G2": ["asia-east1-a", "asia-east1-b", "asia-east1-c"],
            "N1+T4": ["asia-east1-a", "asia-east1-c"],
            "N1+P100": ["asia-east1-a", "asia-east1-c"],
            "A3 Mega": ["asia-east1-c"],
            "A3 High": ["asia-east1-c"],
            "N1+V100": ["asia-east1-c"]
        }
    },
    {
        region: "asia-east2",
        location: "Hong Kong",
        lat: 22.3193,
        lng: 114.1694,
        zones: {
            "N1+T4": ["asia-east2-a", "asia-east2-c"]
        }
    },
    {
        region: "asia-northeast1",
        location: "Tokyo, Japan",
        lat: 35.6895,
        lng: 139.6917,
        zones: {
            "A2 Standard": ["asia-northeast1-a", "asia-northeast1-c"],
            "G2": ["asia-northeast1-a", "asia-northeast1-b", "asia-northeast1-c"],
            "N1+T4": ["asia-northeast1-a", "asia-northeast1-c"],
            "A4": ["asia-northeast1-b"],
            "A3 Edge": ["asia-northeast1-b"],
            "A3 Mega": ["asia-northeast1-b"],
            "A3 High": ["asia-northeast1-b"]
        }
    },
    {
        region: "asia-northeast2",
        location: "Osaka, Japan",
        lat: 34.6937,
        lng: 135.5023,
        zones: {}
    },
    {
        region: "asia-northeast3",
        location: "Seoul, South Korea",
        lat: 37.5665,
        lng: 126.978,
        zones: {
            "A3 Edge": ["asia-northeast3-a", "asia-northeast3-c"],
            "G2": ["asia-northeast3-a", "asia-northeast3-b"],
            "A2 Standard": ["asia-northeast3-b"],
            "N1+T4": ["asia-northeast3-b", "asia-northeast3-c"]
        }
    },
    {
        region: "asia-south1",
        location: "Mumbai, India",
        lat: 19.076,
        lng: 72.8777,
        zones: {
            "G2": ["asia-south1-a", "asia-south1-b", "asia-south1-c"],
            "N1+T4": ["asia-south1-a", "asia-south1-b"],
            "A3 Ultra": ["asia-south1-b"],
            "A3 Edge": ["asia-south1-c"]
        }
    },
    {
        region: "asia-south2",
        location: "Delhi, India",
        lat: 28.6139,
        lng: 77.209,
        zones: {
            "A3 Ultra": ["asia-south2-c"],
            "G4": ["asia-south2-c"]
        }
    },
    {
        region: "asia-southeast1",
        location: "Jurong West, Singapore",
        lat: 1.3496,
        lng: 103.7072,
        zones: {
            "G2": ["asia-southeast1-a", "asia-southeast1-b", "asia-southeast1-c"],
            "N1+T4": ["asia-southeast1-a", "asia-southeast1-b", "asia-southeast1-c"],
            "A4": ["asia-southeast1-b"],
            "A3 Mega": ["asia-southeast1-b", "asia-southeast1-c"],
            "A3 High": ["asia-southeast1-b", "asia-southeast1-c"],
            "A3 Edge": ["asia-southeast1-b", "asia-southeast1-c"],
            "A2 Standard": ["asia-southeast1-b", "asia-southeast1-c"],
            "G4": ["asia-southeast1-b", "asia-southeast1-c"],
            "N1+P4": ["asia-southeast1-b", "asia-southeast1-c"],
            "A2 Ultra": ["asia-southeast1-c"]
        }
    },
    {
        region: "asia-southeast2",
        location: "Jakarta, Indonesia",
        lat: -6.2088,
        lng: 106.8456,
        zones: {
            "N1+T4": ["asia-southeast2-a", "asia-southeast2-b"],
            "G4": ["asia-southeast2-b", "asia-southeast2-c"]
        }
    },
    {
        region: "australia-southeast1",
        location: "Sydney, Australia",
        lat: -33.8688,
        lng: 151.2093,
        zones: {
            "N1+T4": ["australia-southeast1-a", "australia-southeast1-c"],
            "N1+P4": ["australia-southeast1-a", "australia-southeast1-b"],
            "A3 Mega": ["australia-southeast1-c"],
            "N1+P100": ["australia-southeast1-c"]
        }
    },
    {
        region: "australia-southeast2",
        location: "Melbourne, Australia",
        lat: -37.8136,
        lng: 144.9631,
        zones: {}
    },
    {
        region: "europe-central2",
        location: "Warsaw, Poland",
        lat: 52.2297,
        lng: 21.0122,
        zones: {
            "N1+T4": ["europe-central2-b", "europe-central2-c"]
        }
    },
    {
        region: "europe-north1",
        location: "Hamina, Finland",
        lat: 60.5693,
        lng: 27.1878,
        zones: {
            "G4": ["europe-north1-a"]
        }
    },
    {
        region: "europe-west1",
        location: "St. Ghislain, Belgium",
        lat: 50.445,
        lng: 3.82,
        zones: {
            "A3 Ultra": ["europe-west1-b"],
            "A3 Mega": ["europe-west1-b", "europe-west1-c"],
            "A3 High": ["europe-west1-b", "europe-west1-c"],
            "G2": ["europe-west1-b", "europe-west1-c"],
            "N1+T4": ["europe-west1-b", "europe-west1-c", "europe-west1-d"],
            "N1+P100": ["europe-west1-b", "europe-west1-d"],
            "G4": ["europe-west1-c"]
        }
    },
    {
        region: "europe-west2",
        location: "London, England",
        lat: 51.5074,
        lng: -0.1278,
        zones: {
            "G2": ["europe-west2-a", "europe-west2-b"],
            "N1+T4": ["europe-west2-a", "europe-west2-b"],
            "G4": ["europe-west2-b"]
        }
    },
    {
        region: "europe-west3",
        location: "Frankfurt, Germany",
        lat: 50.1109,
        lng: 8.6821,
        zones: {
            "G2": ["europe-west3-a", "europe-west3-b"],
            "N1+T4": ["europe-west3-b"]
        }
    },
    {
        region: "europe-west4",
        location: "Eemshaven, Netherlands",
        lat: 53.442,
        lng: 6.83,
        zones: {
            "A3 Ultra": ["europe-west4-a"],
            "A2 Ultra": ["europe-west4-a"],
            "A2 Standard": ["europe-west4-a", "europe-west4-b"],
            "G4": ["europe-west4-a", "europe-west4-b"],
            "G2": ["europe-west4-a", "europe-west4-b", "europe-west4-c"],
            "N1+T4": ["europe-west4-a", "europe-west4-b", "europe-west4-c"],
            "N1+V100": ["europe-west4-a", "europe-west4-b", "europe-west4-c"],
            "N1+P100": ["europe-west4-a"],
            "A4": ["europe-west4-b"],
            "A3 Mega": ["europe-west4-b", "europe-west4-c"],
            "A3 Edge": ["europe-west4-b", "europe-west4-c"],
            "N1+P4": ["europe-west4-b", "europe-west4-c"],
            "A3 High": ["europe-west4-c"]
        }
    },
    {
        region: "europe-west6",
        location: "Zurich, Switzerland",
        lat: 47.3769,
        lng: 8.5417,
        zones: {
            "G2": ["europe-west6-b", "europe-west6-c"]
        }
    },
    {
        region: "europe-west8",
        location: "Milan, Italy",
        lat: 45.4642,
        lng: 9.19,
        zones: {
            "G4": ["europe-west8-b"]
        }
    },
    {
        region: "europe-west9",
        location: "Paris, France",
        lat: 48.8566,
        lng: 2.3522,
        zones: {
            "A3 Edge": ["europe-west9-c"]
        }
    },
    {
        region: "me-central2",
        location: "Dammam, Saudi Arabia",
        lat: 26.4207,
        lng: 50.0888,
        zones: {
            "G2": ["me-central2-a", "me-central2-c"]
        }
    },
    {
        region: "me-west1",
        location: "Tel Aviv, Israel",
        lat: 32.0853,
        lng: 34.7818,
        zones: {
            "A2 Standard": ["me-west1-a", "me-west1-c"],
            "N1+T4": ["me-west1-b", "me-west1-c"]
        }
    },
    {
        region: "northamerica-northeast1",
        location: "Montréal, Québec, Canada",
        lat: 45.5017,
        lng: -73.5673,
        zones: {
            "N1+P4": ["northamerica-northeast1-a", "northamerica-northeast1-b", "northamerica-northeast1-c"],
            "N1+T4": ["northamerica-northeast1-c"]
        }
    },
    {
        region: "northamerica-northeast2",
        location: "Toronto, Ontario, Canada",
        lat: 43.6532,
        lng: -79.3832,
        zones: {
            "G2": ["northamerica-northeast2-a", "northamerica-northeast2-b"],
            "A3 Edge": ["northamerica-northeast2-c"]
        }
    },
    {
        region: "southamerica-east1",
        location: "Osasco, São Paulo, Brazil",
        lat: -23.5329,
        lng: -46.792,
        zones: {
            "N1+T4": ["southamerica-east1-a", "southamerica-east1-c"]
        }
    },
    {
        region: "us-central1",
        location: "Council Bluffs, Iowa, USA",
        lat: 41.2619,
        lng: -95.8608,
        zones: {
            "A4X": ["us-central1-a"],
            "A3 Mega": ["us-central1-a", "us-central1-b", "us-central1-c"],
            "A3 High": ["us-central1-a", "us-central1-c"],
            "A3 Edge": ["us-central1-a", "us-central1-b", "us-central1-c"],
            "A2 Ultra": ["us-central1-a", "us-central1-c"],
            "A2 Standard": ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"],
            "G2": ["us-central1-a", "us-central1-b", "us-central1-c"],
            "N1+T4": ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"],
            "N1+P4": ["us-central1-a", "us-central1-c"],
            "N1+V100": ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"],
            "A4X Max": ["us-central1-b"],
            "A4": ["us-central1-b"],
            "A3 Ultra": ["us-central1-b"],
            "G4": ["us-central1-b", "us-central1-f"],
            "N1+P100": ["us-central1-c", "us-central1-f"]
        }
    },
    {
        region: "us-east1",
        location: "Moncks Corner, South Carolina, USA",
        lat: 33.195,
        lng: -80.013,
        zones: {
            "A4": ["us-east1-b"],
            "A2 Standard": ["us-east1-b"],
            "G4": ["us-east1-b"],
            "G2": ["us-east1-b", "us-east1-c", "us-east1-d"],
            "N1+P100": ["us-east1-b", "us-east1-c"],
            "N1+T4": ["us-east1-c", "us-east1-d"],
            "N1+V100": ["us-east1-c"],
            "A3 Ultra": ["us-east1-d"]
        }
    },
    {
        region: "us-east4",
        location: "Ashburn, Virginia, USA",
        lat: 39.0438,
        lng: -77.4874,
        zones: {
            "A3 Mega": ["us-east4-a", "us-east4-b", "us-east4-c"],
            "A3 High": ["us-east4-a", "us-east4-b"],
            "A3 Edge": ["us-east4-a", "us-east4-b", "us-east4-c"],
            "G2": ["us-east4-a", "us-east4-c"],
            "N1+T4": ["us-east4-a", "us-east4-b", "us-east4-c"],
            "N1+P4": ["us-east4-a", "us-east4-b", "us-east4-c"],
            "A4X Max": ["us-east4-b"],
            "A4": ["us-east4-b"],
            "A3 Ultra": ["us-east4-b"],
            "A2 Ultra": ["us-east4-c"],
            "G4": ["us-east4-c"]
        }
    },
    {
        region: "us-east5",
        location: "Columbus, Ohio, USA",
        lat: 39.9612,
        lng: -82.9988,
        zones: {
            "A2 Ultra": ["us-east5-a"],
            "A3 Ultra": ["us-east5-a"],
            "A3 Mega": ["us-east5-a"],
            "A3 High": ["us-east5-a"],
            "A3 Edge": ["us-east5-a"],
            "G4": ["us-east5-a", "us-east5-b", "us-east5-c"]
        }
    },
    {
        region: "us-west1",
        location: "The Dalles, Oregon, USA",
        lat: 45.5946,
        lng: -121.1787,
        zones: {
            "A3 Mega": ["us-west1-a", "us-west1-b"],
            "A3 High": ["us-west1-a", "us-west1-b"],
            "A3 Edge": ["us-west1-a", "us-west1-b"],
            "G2": ["us-west1-a", "us-west1-b", "us-west1-c"],
            "N1+T4": ["us-west1-a", "us-west1-b"],
            "N1+V100": ["us-west1-a", "us-west1-b"],
            "N1+P100": ["us-west1-a", "us-west1-b"],
            "A2 Standard": ["us-west1-b"],
            "G4": ["us-west1-b", "us-west1-c"],
            "A3 Ultra": ["us-west1-c"]
        }
    },
    {
        region: "us-west2",
        location: "Los Angeles, California, USA",
        lat: 34.0522,
        lng: -118.2437,
        zones: {
            "N1+T4": ["us-west2-b", "us-west2-c"],
            "N1+P4": ["us-west2-b", "us-west2-c"],
            "A4": ["us-west2-c"]
        }
    },
    {
        region: "us-west3",
        location: "Salt Lake City, Utah, USA",
        lat: 40.7608,
        lng: -111.891,
        zones: {
            "G4": ["us-west3-a"],
            "A4": ["us-west3-b", "us-west3-c"],
            "A2 Standard": ["us-west3-b"],
            "N1+T4": ["us-west3-b"]
        }
    },
    {
        region: "us-west4",
        location: "Las Vegas, Nevada, USA",
        lat: 36.1699,
        lng: -115.1398,
        zones: {
            "A3 Mega": ["us-west4-a"],
            "A3 High": ["us-west4-a"],
            "A3 Edge": ["us-west4-a"],
            "G2": ["us-west4-a", "us-west4-c"],
            "N1+T4": ["us-west4-a", "us-west4-b"],
            "G4": ["us-west4-a"],
            "A2 Standard": ["us-west4-b"]
        }
    },
    {
        region: "us-south1",
        location: "Dallas, Texas, USA",
        lat: 32.7767,
        lng: -96.797,
        zones: {
            "G4": ["us-south1-a", "us-south1-b"],
            "A4": ["us-south1-b"],
            "A3 Ultra": ["us-south1-b"]
        }
    }
];
