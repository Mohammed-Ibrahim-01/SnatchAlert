"""
Seed script: uploads crime incidents into the database.
- 300 general incidents across Pakistan
- 200-400 Karachi-specific incidents spread across real neighborhoods

Run: python seed_crimes.py
     python seed_crimes.py 300 350   (general_count karachi_count)
"""

import os
import sys
import django
import random
from datetime import timedelta
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SnatchAlert.settings")
django.setup()

from django.utils import timezone
from accounts.models import CustomUser
from core.models import LocationDim, VictimDim, IncidentTypeDim, StolenItemDim
from reports.models import IncidentFact

# ── Karachi neighborhoods with real approximate coordinates ─────────────────
# Each entry: (district, neighborhood, base_lat, base_lon)
KARACHI_AREAS = [
    ("Saddar",          "Saddar Bazaar",        24.8607, 67.0105),
    ("Saddar",          "Empress Market",       24.8601, 67.0150),
    ("Saddar",          "Burns Road",           24.8650, 67.0200),
    ("Clifton",         "Clifton Block 2",      24.8138, 67.0300),
    ("Clifton",         "Clifton Block 5",      24.8200, 67.0350),
    ("Clifton",         "Sea View",             24.8050, 67.0250),
    ("DHA",             "DHA Phase 1",          24.7971, 67.0595),
    ("DHA",             "DHA Phase 4",          24.7800, 67.0700),
    ("DHA",             "DHA Phase 6",          24.7650, 67.0800),
    ("Gulshan-e-Iqbal", "Gulshan Block 1",      24.9215, 67.0944),
    ("Gulshan-e-Iqbal", "Gulshan Block 7",      24.9300, 67.1000),
    ("Gulshan-e-Iqbal", "Gulshan Block 13",     24.9100, 67.0850),
    ("Johar",           "Johar Chowrangi",      24.9408, 67.1322),
    ("Johar",           "Johar More",           24.9350, 67.1400),
    ("Johar",           "Johar Block 14",       24.9500, 67.1250),
    ("North Karachi",   "North Karachi Sector 5",  24.9800, 67.0650),
    ("North Karachi",   "North Karachi Sector 11", 24.9900, 67.0700),
    ("North Karachi",   "North Karachi Sector 14", 25.0000, 67.0600),
    ("Malir",           "Malir City",           24.8936, 67.2072),
    ("Malir",           "Malir Halt",           24.8800, 67.2200),
    ("Malir",           "Malir Cantt",          24.9000, 67.1900),
    ("Korangi",         "Korangi Crossing",     24.8300, 67.1300),
    ("Korangi",         "Korangi Industrial",   24.8200, 67.1500),
    ("Korangi",         "Landhi",               24.8450, 67.1700),
    ("Orangi",          "Orangi Town Sector 1", 24.9350, 66.9950),
    ("Orangi",          "Orangi Town Sector 5", 24.9500, 67.0050),
    ("Orangi",          "Orangi Town Sector 9", 24.9600, 67.0100),
    ("Lyari",           "Lyari Chowk",          24.8700, 66.9900),
    ("Lyari",           "Baghdadi",             24.8750, 66.9850),
    ("Lyari",           "Kalakot",              24.8650, 66.9950),
    ("Nazimabad",       "Nazimabad No. 1",      24.9100, 67.0400),
    ("Nazimabad",       "Nazimabad No. 3",      24.9200, 67.0500),
    ("Nazimabad",       "Nazimabad No. 5",      24.9050, 67.0300),
    ("Federal B Area",  "FB Area Block 1",      24.9350, 67.0750),
    ("Federal B Area",  "FB Area Block 7",      24.9450, 67.0800),
    ("Federal B Area",  "FB Area Block 13",     24.9250, 67.0700),
    ("Gulberg",         "Gulberg Town",         24.9000, 67.0600),
    ("Gulberg",         "Gulberg Chowrangi",    24.8950, 67.0550),
    ("SITE",            "SITE Area",            24.9050, 67.0100),
    ("SITE",            "SITE Superhighway",    24.9150, 67.0200),
    ("Kemari",          "Kemari Port",          24.8350, 66.9750),
    ("Kemari",          "Mauripur",             24.8500, 66.9800),
    ("Baldia",          "Baldia Town",          24.8900, 66.9700),
    ("Baldia",          "Mominabad",            24.8800, 66.9650),
    ("Surjani",         "Surjani Town Sector 4",25.0200, 67.0400),
    ("Surjani",         "Surjani Town Sector 7",25.0300, 67.0500),
    ("Bin Qasim",       "Bin Qasim Town",       24.7800, 67.3500),
    ("Bin Qasim",       "Port Qasim",           24.7600, 67.3700),
]

KARACHI_STREETS = [
    "Shahrah-e-Faisal", "M.A. Jinnah Road", "University Road",
    "Tariq Road", "Rashid Minhas Road", "Korangi Road",
    "Superhighway", "National Highway", "Lyari Expressway",
    "Sharea Pakistan", "Hassan Square", "Nagan Chowrangi Road",
]

# ── General Pakistan data ────────────────────────────────────────────────────
CITIES = [
    ("Lahore", "Punjab"), ("Islamabad", "Islamabad"),
    ("Rawalpindi", "Punjab"), ("Faisalabad", "Punjab"), ("Multan", "Punjab"),
    ("Peshawar", "KPK"), ("Quetta", "Balochistan"), ("Hyderabad", "Sindh"),
    ("Gujranwala", "Punjab"),
]

DISTRICTS_GENERAL = ["Gulberg", "DHA", "Model Town", "Saddar", "F-7", "G-9",
                     "Cantt", "Johar Town", "Bahria Town"]

STREETS_GENERAL = ["Main Boulevard", "Mall Road", "Jail Road", "Ferozpur Road",
                   "GT Road", "University Road", "Garden Road"]

INCIDENT_CATEGORIES = [
    ("Phone Snatching",  "Forceful or opportunistic theft of mobile phones"),
    ("Vehicle Theft",    "Theft of cars, motorcycles, or other vehicles"),
    ("Bag Snatching",    "Theft of handbags, backpacks, or purses"),
    ("Robbery",          "Theft with threat or use of force"),
    ("Burglary",         "Breaking and entering a property to commit theft"),
    ("Pickpocketing",    "Theft from a person's pocket without their knowledge"),
]

PHONE_BRANDS = ["Samsung", "Apple", "Huawei", "Xiaomi", "Oppo", "Vivo", "OnePlus"]
PHONE_MODELS = {
    "Samsung": ["Galaxy S23", "Galaxy A54", "Galaxy M33"],
    "Apple":   ["iPhone 14", "iPhone 13", "iPhone 12"],
    "Huawei":  ["P50", "Nova 9", "Mate 40"],
    "Xiaomi":  ["Redmi Note 12", "Mi 12", "Poco X5"],
    "Oppo":    ["Reno 8", "A96", "Find X5"],
    "Vivo":    ["V25", "Y75", "X80"],
    "OnePlus": ["11", "Nord CE 3", "10 Pro"],
}

VEHICLE_MAKES = ["Toyota", "Honda", "Suzuki", "Yamaha", "Honda Motorcycle"]
VEHICLE_MODELS = {
    "Toyota":           ["Corolla", "Yaris", "Hilux"],
    "Honda":            ["Civic", "City", "BR-V"],
    "Suzuki":           ["Alto", "Swift", "Cultus"],
    "Yamaha":           ["YBR 125", "YZF-R1", "FZ-S"],
    "Honda Motorcycle": ["CD 70", "CB 150F", "CG 125"],
}

GENDERS       = ["male", "female", "other"]
STATUSES      = ["reported", "investigating", "resolved", "closed"]
STATUS_WEIGHTS = [0.55, 0.25, 0.12, 0.08]

FIRST_NAMES = ["Ali", "Sara", "Ahmed", "Fatima", "Usman", "Ayesha", "Hassan",
               "Zainab", "Omar", "Nadia", "Bilal", "Hina", "Tariq", "Sana"]
LAST_NAMES  = ["Khan", "Ahmed", "Malik", "Hussain", "Iqbal", "Chaudhry",
               "Butt", "Sheikh", "Qureshi", "Siddiqui"]

# ── Helpers ──────────────────────────────────────────────────────────────────

def rand_imei():
    return "".join([str(random.randint(0, 9)) for _ in range(15)])

def rand_plate():
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    return f"{''.join(random.choices(letters, k=3))}-{''.join(str(random.randint(0,9)) for _ in range(4))}"

def rand_date(days_back=730):
    return timezone.now() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def rand_email(name):
    slug = name.lower().replace(" ", ".") + str(random.randint(10, 999))
    return f"{slug}@example.com"

def make_stolen_item(incident_type):
    value = Decimal(str(round(random.uniform(5000, 250000), 2)))
    cat = incident_type.category

    if cat == "Phone Snatching":
        brand = random.choice(PHONE_BRANDS)
        model = random.choice(PHONE_MODELS[brand])
        return StolenItemDim.objects.create(
            item_type="phone", phone_brand=brand, phone_model=model,
            imei=rand_imei(), value_estimate=value,
            description=f"Stolen {brand} {model}",
        ), value

    if cat == "Vehicle Theft":
        make  = random.choice(VEHICLE_MAKES)
        model = random.choice(VEHICLE_MODELS[make])
        itype = "bike" if "Motorcycle" in make or make == "Yamaha" else "car"
        return StolenItemDim.objects.create(
            item_type=itype, vehicle_make=make, vehicle_model=model,
            license_plate=rand_plate(), chassis_number=f"CH{random.randint(100000,999999)}",
            value_estimate=value, description=f"Stolen {make} {model}",
        ), value

    if cat == "Bag Snatching":
        return StolenItemDim.objects.create(
            item_type="bag", value_estimate=value,
            description="Snatched bag containing personal belongings",
        ), value

    return StolenItemDim.objects.create(
        item_type="other", value_estimate=value,
        description="Miscellaneous stolen item",
    ), value

def make_victim(city_name, streets):
    is_anon = random.random() < 0.2
    if is_anon:
        return None, True
    name = rand_name()
    victim = VictimDim.objects.create(
        name=name, age=random.randint(15, 65),
        gender=random.choice(GENDERS),
        phone_number=f"03{random.randint(100000000, 399999999)}",
        email=rand_email(name),
        address=f"{random.randint(1,200)} {random.choice(streets)}, {city_name}",
    )
    return victim, False

def create_incident(location, incident_type, reporter, city_name, streets):
    stolen_item, value = make_stolen_item(incident_type)
    victim, is_anon    = make_victim(city_name, streets)
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

    IncidentFact.objects.create(
        occurred_at=rand_date(),
        location=location,
        victim=victim,
        incident_type=incident_type,
        stolen_item=stolen_item,
        value_estimate=value,
        fir_filed=random.random() < 0.4,
        description=f"{incident_type.category} incident reported in {city_name}.",
        is_anonymous=is_anon,
        status=status,
        reported_by=reporter,
    )

# ── Seeding ──────────────────────────────────────────────────────────────────

def seed(general_count=300, karachi_count=350):
    total = general_count + karachi_count
    print(f"Seeding {general_count} general + {karachi_count} Karachi = {total} total incidents...")

    # Reporter user
    reporter, _ = CustomUser.objects.get_or_create(
        email="seeder@snatchalert.com",
        defaults={"first_name": "Seed", "last_name": "Bot", "role": "admin",
                  "is_verified": True, "is_staff": True},
    )
    if not reporter.has_usable_password():
        reporter.set_password("Seed@1234")
        reporter.save()

    # Incident types
    type_objs = []
    for cat, desc in INCIDENT_CATEGORIES:
        obj, _ = IncidentTypeDim.objects.get_or_create(category=cat, defaults={"description": desc})
        type_objs.append(obj)

    created = 0

    # ── 1. General Pakistan incidents ────────────────────────────────────────
    print(f"\n[1/2] Seeding {general_count} general incidents across Pakistan...")
    for _ in range(general_count):
        city_name, province = random.choice(CITIES)
        lat_base = {"Punjab": 31.5, "Sindh": 24.8, "Islamabad": 33.7,
                    "KPK": 34.0, "Balochistan": 30.2}.get(province, 30.0)
        lon_base = {"Punjab": 74.3, "Sindh": 67.0, "Islamabad": 73.0,
                    "KPK": 71.5, "Balochistan": 67.0}.get(province, 70.0)

        location = LocationDim.objects.create(
            province=province, city=city_name,
            district=random.choice(DISTRICTS_GENERAL),
            neighborhood=f"Block {random.randint(1, 20)}",
            street_address=f"{random.randint(1,500)} {random.choice(STREETS_GENERAL)}",
            latitude=Decimal(str(round(lat_base + random.uniform(-0.3, 0.3), 6))),
            longitude=Decimal(str(round(lon_base + random.uniform(-0.3, 0.3), 6))),
        )
        create_incident(location, random.choice(type_objs), reporter, city_name, STREETS_GENERAL)
        created += 1
        if created % 50 == 0:
            print(f"  {created}/{total} done...")

    # ── 2. Karachi-specific incidents ────────────────────────────────────────
    print(f"\n[2/2] Seeding {karachi_count} Karachi incidents across {len(KARACHI_AREAS)} neighborhoods...")
    for _ in range(karachi_count):
        district, neighborhood, base_lat, base_lon = random.choice(KARACHI_AREAS)

        # Small jitter so each incident has a unique coordinate on the map
        lat = Decimal(str(round(base_lat + random.uniform(-0.008, 0.008), 6)))
        lon = Decimal(str(round(base_lon + random.uniform(-0.008, 0.008), 6)))

        location = LocationDim.objects.create(
            province="Sindh", city="Karachi",
            district=district,
            neighborhood=neighborhood,
            street_address=f"{random.randint(1,300)} {random.choice(KARACHI_STREETS)}",
            latitude=lat,
            longitude=lon,
        )
        create_incident(location, random.choice(type_objs), reporter, "Karachi", KARACHI_STREETS)
        created += 1
        if created % 50 == 0:
            print(f"  {created}/{total} done...")

    print(f"\nDone. {created} total incidents seeded.")
    print(f"  General (Pakistan): {general_count}")
    print(f"  Karachi:            {karachi_count} across {len(KARACHI_AREAS)} neighborhoods")


if __name__ == "__main__":
    args = sys.argv[1:]
    general = int(args[0]) if len(args) > 0 else 300
    karachi = int(args[1]) if len(args) > 1 else 350
    seed(general, karachi)
