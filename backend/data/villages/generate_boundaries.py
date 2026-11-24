import json
import math
import numpy as np
from pathlib import Path

VILLAGES_DIR = Path(__file__).resolve().parent

villages_meta = json.loads((VILLAGES_DIR / "villages.json").read_text())

for v in villages_meta:
    lat_c, lon_c = v["center"]
    min_lon, min_lat, max_lon, max_lat = v["bbox"]
    d_lon = (max_lon - min_lon) / 2
    d_lat = (max_lat - min_lat) / 2
    
    # Generate realistic smoothed natural polygon points
    num_pts = 32
    coords = []
    np.random.seed(abs(int(lat_c * 1000 + lon_c * 1000)) % 10000)
    for i in range(num_pts):
        angle = 2 * math.pi * i / num_pts
        # natural variation in radius
        r_var = 0.82 + 0.18 * math.sin(3 * angle) + 0.12 * math.cos(5 * angle)
        pt_lon = round(lon_c + d_lon * 0.92 * r_var * math.cos(angle), 6)
        pt_lat = round(lat_c + d_lat * 0.92 * r_var * math.sin(angle), 6)
        coords.append([pt_lon, pt_lat])
    coords.append(coords[0]) # close ring

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "id": v["id"],
                    "name": v["name"],
                    "district": v["district"],
                    "state": v["state"],
                    "total_area_ha": v["total_area_ha"],
                    "center": v["center"],
                    "primary_crops": v["primary_crops"]
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
        ]
    }
    
    out_file = VILLAGES_DIR / v["geojson_file"]
    out_file.write_text(json.dumps(geojson, indent=2))
    print(f"Generated {out_file.name} with {len(coords)} boundary vertices.")
