const awsData = [
    {
        region: "us-east-1",
        location: "US East (N. Virginia) — Ashburn, VA",
        lat: 39.0438,
        lng: -77.4874,
        families: ["DL1", "F1", "F2", "G4ad", "G4dn", "G5", "G5g", "G6", "G6e", "G6f", "Gr6", "G7e", "Inf1", "Inf2", "P3", "P4d", "P4de", "P5", "P5en", "P6-B200", "Trn1", "Trn1n", "VT1"]
    },
    {
        region: "us-east-2",
        location: "US East (Ohio) — Columbus, OH",
        lat: 39.9612,
        lng: -82.9988,
        families: ["G4ad", "G4dn", "G5", "G6", "G6e", "G6f", "Gr6", "Gr6f", "G7e", "Inf1", "Inf2", "P3", "P4d", "P5", "P5e", "P5en", "P6-B200", "Trn1", "Trn1n", "Trn2"]
    },
    {
        region: "us-west-1",
        location: "US West (N. California) — Bay Area",
        lat: 37.8272,
        lng: -122.2913,
        families: ["G4dn", "Inf1", "P5", "P5en"]
    },
    {
        region: "us-west-2",
        location: "US West (Oregon)",
        lat: 45.5152,
        lng: -122.6784,
        families: ["DL1", "DL2q", "F1", "F2", "G4ad", "G4dn", "G5", "G5g", "G6", "G6e", "G6f", "Gr6", "Inf1", "Inf2", "P3", "P4d", "P4de", "P5", "P5e", "P5en", "P6-B200", "Trn1", "Trn1n", "VT1"]
    },
    {
        region: "ap-east-1",
        location: "Asia Pacific (Hong Kong)",
        lat: 22.3193,
        lng: 114.1694,
        families: ["G4dn", "G5", "Inf1"]
    },
    {
        region: "ap-south-1",
        location: "Asia Pacific (Mumbai)",
        lat: 19.0760,
        lng: 72.8777,
        families: ["G4dn", "G5", "G6", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P4d", "P5", "P5en", "Trn1"]
    },
    {
        region: "ap-northeast-2",
        location: "Asia Pacific (Seoul)",
        lat: 37.5665,
        lng: 126.9780,
        families: ["F2", "G4dn", "G5", "G5g", "G6", "G6e", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P3", "P4d", "P5", "P5en"]
    },
    {
        region: "ap-southeast-1",
        location: "Asia Pacific (Singapore)",
        lat: 1.3521,
        lng: 103.8198,
        families: ["G4dn", "G5g", "Inf1", "Inf2", "P3", "P4de"]
    },
    {
        region: "ap-southeast-2",
        location: "Asia Pacific (Sydney)",
        lat: -33.8688,
        lng: 151.2093,
        families: ["F1", "F2", "G4dn", "G5", "G6", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P3", "P4d", "P5", "P5e", "Trn1"]
    },
    {
        region: "ap-northeast-1",
        location: "Asia Pacific (Tokyo)",
        lat: 35.6895,
        lng: 139.6917,
        families: ["F2", "G4ad", "G4dn", "G5", "G5g", "G6", "G6e", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P3", "P3dn", "P4d", "P4de", "P5", "P5en", "VT1"]
    },
    {
        region: "ca-central-1",
        location: "Canada (Central) — Montréal, QC",
        lat: 45.5017,
        lng: -73.5673,
        families: ["F2", "G4ad", "G4dn", "G5", "G6", "G6f", "Gr6", "Gr6f", "Inf1", "P3", "P4d", "P5"]
    },
    {
        region: "eu-central-1",
        location: "Europe (Frankfurt)",
        lat: 50.1109,
        lng: 8.6821,
        families: ["DL2q", "F1", "F2", "G4ad", "G4dn", "G5", "G5g", "G6", "G6e", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P3", "P4d", "P4de"]
    },
    {
        region: "eu-west-1",
        location: "Europe (Ireland)",
        lat: 53.3498,
        lng: -6.2603,
        families: ["F1", "G4ad", "G4dn", "G5", "Inf1", "Inf2", "P3", "P3dn", "P4d", "VT1"]
    },
    {
        region: "eu-west-2",
        location: "Europe (London)",
        lat: 51.5074,
        lng: -0.1278,
        families: ["F1", "F2", "G4ad", "G4dn", "G5", "G6", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P3", "P4d", "P5", "P5e"]
    },
    {
        region: "eu-south-1",
        location: "Europe (Milan)",
        lat: 45.4642,
        lng: 9.1900,
        families: ["G4dn", "Inf1"]
    },
    {
        region: "eu-west-3",
        location: "Europe (Paris)",
        lat: 48.8566,
        lng: 2.3522,
        families: ["G4dn", "G6", "Gr6", "Inf1", "Inf2"]
    },
    {
        region: "eu-north-1",
        location: "Europe (Stockholm)",
        lat: 59.3293,
        lng: 18.0686,
        families: ["G4dn", "G5", "G6", "G6e", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P4d", "P5", "P5e", "P5en"]
    },
    {
        region: "me-south-1",
        location: "Middle East (Bahrain)",
        lat: 26.2235,
        lng: 50.5876,
        families: ["G4dn", "Inf1"]
    },
    {
        region: "sa-east-1",
        location: "South America (São Paulo)",
        lat: -23.5505,
        lng: -46.6333,
        families: ["G4dn", "G5", "G6", "G6f", "Gr6", "Gr6f", "Inf1", "Inf2", "P4d", "P5", "P5e", "Trn2"]
    }
];