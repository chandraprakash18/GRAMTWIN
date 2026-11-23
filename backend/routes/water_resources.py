
import json
import urllib.parse
import urllib.request

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/water/resources",
    tags=["Water Resources"]
)

# Hiware Bazar, Maharashtra
VILLAGE_LAT = 19.06861
VILLAGE_LON = 74.60111


@router.get("/")
def get_water_resources():

    query = f"""
    [out:json][timeout:25];
    (
        nwr(around:1500,{VILLAGE_LAT},{VILLAGE_LON})[man_made=water_well];
        nwr(around:1500,{VILLAGE_LAT},{VILLAGE_LON})[natural=water];
        nwr(around:1500,{VILLAGE_LAT},{VILLAGE_LON})[landuse=reservoir];
        nwr(around:1500,{VILLAGE_LAT},{VILLAGE_LON})[waterway~"river|stream|canal"];
        nwr(around:1500,{VILLAGE_LAT},{VILLAGE_LON})[man_made=dam];
        nwr(around:1500,{VILLAGE_LAT},{VILLAGE_LON})[waterway=dam];
    );
    out center tags;
    """

    data = urllib.parse.urlencode({
        "data": query
    }).encode("utf-8")

    endpoints = [
        "https://overpass.private.coffee/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass-api.de/api/interpreter"
    ]

    last_error = None

    for url in endpoints:

        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "User-Agent": "GRAMTWIN2.0/1.0",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        try:

            with urllib.request.urlopen(request, timeout=15) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )

            resources = []

            for element in result.get("elements", []):

                tags = element.get("tags", {})

                lat = element.get("lat")
                lon = element.get("lon")

                if lat is None or lon is None:
                    center = element.get("center", {})
                    lat = center.get("lat")
                    lon = center.get("lon")

                if lat is None or lon is None:
                    continue

                category = "Other"

                if tags.get("man_made") == "water_well":
                    category = "Wells"

                elif (
                    tags.get("man_made") == "dam"
                    or tags.get("waterway") == "dam"
                ):
                    category = "Check Dams"

                elif (
                    tags.get("landuse") == "reservoir"
                    or tags.get("water") == "reservoir"
                ):
                    category = "Reservoirs"

                elif tags.get("waterway") in [
                    "river", "stream", "canal"
                ]:
                    category = "Rivers & Canals"

                elif (
                    tags.get("natural") == "water"
                    or tags.get("water") == "pond"
                ):
                    category = "Ponds"

                resources.append({
                    "id": f"{element['type']}_{element['id']}",
                    "name": tags.get(
                        "name", "Unnamed water resource"
                    ),
                    "category": category,
                    "latitude": lat,
                    "longitude": lon,
                    "source": "OpenStreetMap"
                })

            return {
                "village": "Hiware Bazar",
                "source": "OpenStreetMap",
                "resource_count": len(resources),
                "resources": resources
            }

        except Exception as error:

            last_error = error

            print(
                f"Overpass server failed ({url}): {error}"
            )

    raise HTTPException(
        status_code=502,
        detail=f"All OpenStreetMap servers failed. Last error: {last_error}"
    )
