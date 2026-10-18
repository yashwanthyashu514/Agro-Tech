# Module 1 – Location & Soil (no training needed)
karnataka_location_soil.csv : 9,676 villages/post offices -> district, taluk, pincode, lat/long, agro-zone, soil type
karnataka_taluk_soil.csv    : 175 taluks -> 10 agro-climatic zones -> dominant/secondary soil, zone rainfall
india_locations.csv         : 1.5 lakh locations, all states
add_soil_health_values.py   : adds real N, P, K, pH, OC from the Soil Health Card file (dataful.in/datasets/24072)
build_location_soil.py      : rebuilds the tables from raw sources
