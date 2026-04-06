"""
Seed script: uploads up to 300 realistic crime incidents into the database.
Run with: python manage.py shell < seed_crimes.py
  or:     python seed_crimes.py  (from the SnatchAlert directory, Django must be configured)
"""

import os
import sys
import django
import random
from datetime import timedelta
from decimal import Decimal

# --- Django setup ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SnatchAlert.settings")
django.setup()

from django.utils import timezone
from accounts.models import CustomUser
from core.models import LocationDim, VictimDim, IncidentTypeDim, StolenItemDim
from reports.models import IncidentFact

# ── Seed data pools ──────────────────────────────────────────────────────────

PROVINCES = ["Punjab", "Sindh", "KPK", "Balochistan", "Islamabad"]

CITIES = [
    ("Lahore", "Punjab"), ("Karachi", "Sindh"), ("Islamabad", "Islamabad"),
    ("Rawalpindi", "Punjab"), ("Faisalabad", "Punjab"), ("Multan", "Punjab"),
    ("Peshawar", "KPK"), ("Quetta", "Balochistan"), ("Hyderabad", "Sindh"),
    ("Gujranwala", "Punjab"),
]

DISTRICTS = ["Gulberg", "DHA", "Model Town", "Saddar", "Clifton", "F-7", "G-9",
             "Cantt", "Johar Town", "Bahria Town"]

STREETS = ["Main Boulevard", "Mall Road", "Jail Road", "Ferozpur Road",
           "Shahrah-e-Faisal", "GT Road", "University Road", "Garden Road"]

INCIDENT_CATEGORIES = [
    ("Phone Snatching", "Forceful or opportunistic theft of mobile phones"),
    ("Vehicle Theft", "Theft of cars, motorcycles, or other vehicles"),
    ("Bag Snatching", "Theft of handbags, backpacks, or purses"),
    ("Robbery", "Theft with threat or use of force"),
    ("Burglary", "Breaking and entering a property to commit theft"),
    ("Pickpocketing", "Theft from a person's pocket without their knowledge"),
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
    "Toyota":            ["Corolla", "Yaris", "Hilux"],
    "Honda":             ["Civic", "City", "BR-V"],
    "Suzuki":            ["Alto", "Swift", "Cultus"],
    "Yamaha":            ["YBR 125", "YZF-R1", "FZ-S"],
    "Honda Motorcycle":  ["CD 70", "CB 150F", "CG 125"],
}

GENDERS = ["male", "female", "other"]
STATUSES = ["reported", "investigating", "resolved", "closed"]
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
    return timezone.now() - timedelta(days=random.randint(0, days_back),
                                      hours=random.randint(0, 23),
                                      minutes=random.randint(0, 59))

def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def rand_email(name):
    slug = name.lower().replace(" ", ".") + str(random.randint(10, 999))
    return f"{slug}@example.com"

# ── Main seeding logic ───────────────────────────────────────────────────────

def seed(total=300):
    print(f"Seeding {total} crime incidents...")

    # 1. Ensure a reporter user exists
    reporter, _ = CustomUser.objects.get_or_create(
        email="seeder@snatchalert.com",
        defaults={"first_name": "Seed", "last_name": "Bot", "role": "admin",
                  "is_verified": True, "is_staff": True},
    )
    if not reporter.has_usable_password():
        reporter.set_password("Seed@1234")
        reporter.save()

    # 2. Ensure incident type dimensions exist
    type_objs = []
    for cat, desc in INCIDENT_CATEGORIES:
        obj, _ = IncidentTypeDim.objects.get_or_create(category=cat, defaults={"description": desc})
        type_objs.append(obj)

    created = 0

    for i in range(total):
        # ── Location ──
        city_name, province = random.choice(CITIES)
        lat_base  = {"Punjab": 31.5, "Sindh": 24.8, "Islamabad": 33.7,
                     "KPK": 34.0, "Balochistan": 30.2}.get(province, 30.0)
        lon_base  = {"Punjab": 74.3, "Sindh": 67.0, "Islamabad": 73.0,
                     "KPK": 71.5, "Balochistan": 67.0}.get(province, 70.0)

        location = LocationDim.objects.create(
            province=province,
            city=city_name,
            district=random.choice(DISTRICTS),
            neighborhood=f"Block {random.randint(1, 20)}",
            street_address=f"{random.randint(1, 500)} {random.choice(STREETS)}",
            latitude=Decimal(str(round(lat_base + random.uniform(-0.3, 0.3), 6))),
            longitude=Decimal(str(round(lon_base + random.uniform(-0.3, 0.3), 6))),
        )

        # ── Incident type ──
        incident_type = random.choice(type_objs)
        is_phone   = incident_type.category == "Phone Snatching"
        is_vehicle = incident_type.category == "Vehicle Theft"

        # ── Stolen item ──
        stolen_item = None
        value = Decimal(str(round(random.uniform(5000, 250000), 2)))

        if is_phone:
            brand = random.choice(PHONE_BRANDS)
            model = random.choice(PHONE_MODELS[brand])
            stolen_item = StolenItemDim.objects.create(
                item_type="phone",
                phone_brand=brand,
                phone_model=model,
                imei=rand_imei(),
                value_estimate=value,
                description=f"Stolen {brand} {model}",
            )
        elif is_vehicle:
            make  = random.choice(VEHICLE_MAKES)
            model = random.choice(VEHICLE_MODELS[make])
            itype = "bike" if "Motorcycle" in make or make == "Yamaha" else "car"
            stolen_item = StolenItemDim.objects.create(
                item_type=itype,
                vehicle_make=make,
                vehicle_model=model,
                license_plate=rand_plate(),
                chassis_number=f"CH{random.randint(100000, 999999)}",
                value_estimate=value,
                description=f"Stolen {make} {model}",
            )
        elif incident_type.category == "Bag Snatching":
            stolen_item = StolenItemDim.objects.create(
                item_type="bag",
                value_estimate=value,
                description="Snatched bag containing personal belongings",
            )
        else:
            stolen_item = StolenItemDim.objects.create(
                item_type="other",
                value_estimate=value,
                description="Miscellaneous stolen item",
            )

        # ── Victim ──
        is_anon = random.random() < 0.2
        victim  = None
        if not is_anon:
            name = rand_name()
            victim = VictimDim.objects.create(
                name=name,
                age=random.randint(15, 65),
                gender=random.choice(GENDERS),
                phone_number=f"03{random.randint(100000000, 399999999)}",
                email=rand_email(name),
                address=f"{random.randint(1,200)} {random.choice(STREETS)}, {city_name}",
            )

        # ── Incident fact ──
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

        created += 1
        if created % 50 == 0:
            print(f"  {created}/{total} incidents created...")

    print(f"\nDone. {created} crime incidents seeded successfully.")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    seed(count)
