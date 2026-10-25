"""Crisis scenario generators and hostile data stream injection for RescueSwarm AI."""

from __future__ import annotations
import random
import time
from typing import List
from rescueswarm.models import RawReport, SourceType


def generate_major_disaster_reports() -> List[RawReport]:
    """Generate the 47 chaotic crisis reports described in the problem statement."""
    reports: List[RawReport] = []
    base_time = time.time()

    # --- INCIDENT 1: Structural Collapse at Mall Road & East Corridor (CRITICAL - Multiple Casualties) ---
    # Genuine citizen reports
    reports.append(RawReport(
        source_type=SourceType.CITIZEN,
        source_id="citizen-phone-8921",
        timestamp=base_time - 32,
        location_name="Mall Road Sector 2 Commercial Plaza",
        lat=32.2392,
        lng=77.1883,
        text="Plaza building facade collapsed onto the street! At least 5-6 people trapped under rubble!",
        reported_casualties=6,
        reported_hazard="structural collapse",
        metadata={"nearest_node": "mall_road", "target_substation": "sub_station"},
    ))
    reports.append(RawReport(
        source_type=SourceType.CITIZEN,
        source_id="citizen-phone-4112",
        timestamp=base_time - 28,
        location_name="Mall Road Commercial Complex",
        lat=32.2390,
        lng=77.1881,
        text="Severe collapse near the mall plaza, screams coming from under debris. Need ambulances fast!",
        reported_casualties=5,
        reported_hazard="structural collapse",
        metadata={"nearest_node": "mall_road"},
    ))
    # IoT Seismic / Structural sensor
    reports.append(RawReport(
        source_type=SourceType.IOT_SENSOR,
        source_id="sensor-seismic-mall-04",
        timestamp=base_time - 35,
        location_name="Mall Road Sector 2 Infrastructure Node",
        lat=32.2391,
        lng=77.1882,
        text="SEISMIC_ALERT: Structural stress threshold exceeded (0.42g). Accelerometer anomaly detected.",
        reported_casualties=0,
        reported_hazard="structural collapse",
        metadata={"nearest_node": "mall_road"},
    ))
    # First Responder Field Unit
    reports.append(RawReport(
        source_type=SourceType.RESPONDER,
        source_id="police-patrol-unit-07",
        timestamp=base_time - 15,
        location_name="Mall Road Sector 2",
        lat=32.2393,
        lng=77.1885,
        text="Officer on scene confirms multi-story facade collapse. Multiple civilian casualties visible. Priority dispatch requested.",
        reported_casualties=6,
        reported_hazard="structural collapse",
        metadata={"nearest_node": "mall_road", "target_substation": "sub_station"},
    ))
    # Duplicate citizen call
    reports.append(RawReport(
        source_type=SourceType.CITIZEN,
        source_id="citizen-phone-8921",  # Same caller calling again
        timestamp=base_time - 10,
        location_name="Mall Road Complex",
        lat=32.2392,
        lng=77.1884,
        text="Calling again! Building collapsed! Are ambulances on their way?",
        reported_casualties=6,
        reported_hazard="structural collapse",
        metadata={"nearest_node": "mall_road"},
    ))
    # Manipulated / exaggerated post
    reports.append(RawReport(
        source_type=SourceType.SOCIAL_MEDIA,
        source_id="twitter-anon-bot-33",
        timestamp=base_time - 5,
        location_name="Mall Road",
        lat=32.2395,
        lng=77.1886,
        text="BOMB BLAST AT MALL ROAD! 500 DEAD ALREADY! CITY IS BURNING!",
        reported_casualties=500,
        reported_hazard="bomb blast",
        metadata={"nearest_node": "mall_road"},
    ))

    # --- INCIDENT 2: Flash Mudslide in Old Town Sector 4 ---
    reports.append(RawReport(
        source_type=SourceType.RESPONDER,
        source_id="ranger-outpost-02",
        timestamp=base_time - 40,
        location_name="Old Town Heritage Sector 4",
        lat=32.2491,
        lng=77.1824,
        text="Mudslide breached upper retaining wall. 2 injured, 1 residential access road blocked.",
        reported_casualties=2,
        reported_hazard="mudslide",
        metadata={"nearest_node": "old_town"},
    ))
    reports.append(RawReport(
        source_type=SourceType.WEATHER_RADAR,
        source_id="radar-hill-station-north",
        timestamp=base_time - 45,
        location_name="Old Town Slopes",
        lat=32.2494,
        lng=77.1828,
        text="PRECIP_SURGE: 78mm/hr intense rainfall triggered soil saturation on sector 4 slope.",
        reported_casualties=0,
        reported_hazard="mudslide",
        metadata={"nearest_node": "old_town"},
    ))
    reports.append(RawReport(
        source_type=SourceType.CITIZEN,
        source_id="citizen-phone-3301",
        timestamp=base_time - 20,
        location_name="Old Town Sector 4",
        lat=32.2488,
        lng=77.1822,
        text="Mud and rocks slid down into my neighbor's yard! People need help getting out.",
        reported_casualties=2,
        reported_hazard="mudslide",
        metadata={"nearest_node": "old_town"},
    ))

    # --- INCIDENT 3: Electrical Transformer Fire at Aleo Bridge Crossing ---
    reports.append(RawReport(
        source_type=SourceType.IOT_SENSOR,
        source_id="iot-grid-sensor-aleo-9",
        timestamp=base_time - 50,
        location_name="Aleo River Bridge Corridor",
        lat=32.2356,
        lng=77.1951,
        text="GRID_FAULT: 33kV step-down transformer arching and thermal runaway detected (185°C).",
        reported_casualties=0,
        reported_hazard="transformer fire",
        metadata={"nearest_node": "aleo_bridge"},
    ))
    reports.append(RawReport(
        source_type=SourceType.CITIZEN,
        source_id="citizen-phone-7729",
        timestamp=base_time - 25,
        location_name="Aleo Bridge Approach",
        lat=32.2354,
        lng=77.1948,
        text="Huge black smoke and sparks at the bridge transformer! Fire tender needed immediately.",
        reported_casualties=0,
        reported_hazard="transformer fire",
        metadata={"nearest_node": "aleo_bridge"},
    ))
    reports.append(RawReport(
        source_type=SourceType.RESPONDER,
        source_id="traffic-police-aleo",
        timestamp=base_time - 18,
        location_name="Aleo Bridge",
        lat=32.2358,
        lng=77.1953,
        text="Heavy smoke near bridge substation. Traffic slowing down, no casualties yet.",
        reported_casualties=0,
        reported_hazard="transformer fire",
        metadata={"nearest_node": "aleo_bridge"},
    ))

    # --- INCIDENT 4: River South Overflow / Waterlogging ---
    reports.append(RawReport(
        source_type=SourceType.IOT_SENSOR,
        source_id="river-water-gauge-south",
        timestamp=base_time - 60,
        location_name="Beas River South Causeway",
        lat=32.2281,
        lng=77.1852,
        text="HYDRO_WARN: River level +1.8m above safety datum. Water logging low-lying causeway.",
        reported_casualties=0,
        reported_hazard="river surge",
        metadata={"nearest_node": "river_south"},
    ))
    reports.append(RawReport(
        source_type=SourceType.CITIZEN,
        source_id="citizen-phone-5541",
        timestamp=base_time - 22,
        location_name="Beas River Causeway",
        lat=32.2279,
        lng=77.1849,
        text="Water coming up onto the lower road. Cars turning back.",
        reported_casualties=0,
        reported_hazard="river surge",
        metadata={"nearest_node": "river_south"},
    ))

    # Fill remaining reports (to total exactly 47 reports) with realistic background crisis telemetry:
    # duplicates, sensor pings, minor panic posts, hospital admission alerts
    target_total = 47
    cluster_templates = [
        ("Mall Road Sector 2", 32.2391, 77.1882, "structural collapse", "mall_road", 5),
        ("Old Town Sector 4", 32.2490, 77.1825, "mudslide", "old_town", 2),
        ("Aleo Bridge Corridor", 32.2355, 77.1950, "transformer fire", "aleo_bridge", 0),
        ("River South Causeway", 32.2280, 77.1850, "river surge", "river_south", 0),
    ]

    while len(reports) < target_total:
        template = random.choice(cluster_templates)
        loc_name, lat, lng, hazard, node, casualties = template
        jitter_lat = lat + random.uniform(-0.0015, 0.0015)
        jitter_lng = lng + random.uniform(-0.0015, 0.0015)
        src = random.choices(
            [SourceType.CITIZEN, SourceType.IOT_SENSOR, SourceType.HOSPITAL, SourceType.SOCIAL_MEDIA],
            weights=[0.45, 0.30, 0.15, 0.10],
        )[0]

        reports.append(RawReport(
            source_type=src,
            source_id=f"stream-{random.randint(1000, 9999)}",
            timestamp=base_time - random.randint(5, 75),
            location_name=loc_name,
            lat=round(jitter_lat, 5),
            lng=round(jitter_lng, 5),
            text=f"Telemetry feed #{len(reports)+1}: {hazard.title()} advisory at {loc_name}.",
            reported_casualties=casualties,
            reported_hazard=hazard,
            metadata={"nearest_node": node},
        ))

    return reports


def generate_hostile_fake_rumor() -> RawReport:
    """Generate the hostile/manipulated rumor: 100 people trapped at Location X with zero sensor proof."""
    return RawReport(
        source_type=SourceType.SOCIAL_MEDIA,
        source_id="unverified-telegram-broadcast-88",
        timestamp=time.time(),
        location_name="Location X (High School Gymnasium)",
        lat=32.2440,
        lng=77.1910,
        text="URGENT RED ALERT: 100 PEOPLE TRAPPED UNDER RUINS AT LOCATION X! IMMEDIATE SQUAD DISPATCH REQUIRED!",
        reported_casualties=100,
        reported_hazard="mass casualty collapse",
        credibility_prior=0.15,
        is_adversarial_or_rumor=True,
        metadata={"nearest_node": "mall_road", "is_fake_injection": True},
    )
