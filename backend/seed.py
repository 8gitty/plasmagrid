import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("backend/firebase_key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_URL")
})

hospitals = [

    # ── BENGALURU CITY ─────────────────────────────────────
    {
        "id": "victoria", "name": "Victoria Hospital",
        "area": "Kalasipalya", "city": "Bengaluru",
        "type": "government", "lat": 12.9634, "lng": 77.5855,
        "scarcity": 72, "beds_available": 8, "blood_units": 12,
        "ambulances": 3, "oxygen_cylinders": 5, "trust_score": 100, "status": "active"
    },
    {
        "id": "bowring", "name": "Bowring & Lady Curzon Hospital",
        "area": "Shivajinagar", "city": "Bengaluru",
        "type": "government", "lat": 12.9840, "lng": 77.6033,
        "scarcity": 45, "beds_available": 22, "blood_units": 30,
        "ambulances": 5, "oxygen_cylinders": 18, "trust_score": 100, "status": "active"
    },
    {
        "id": "kc_general", "name": "KC General Hospital",
        "area": "Malleshwaram", "city": "Bengaluru",
        "type": "government", "lat": 13.0035, "lng": 77.5710,
        "scarcity": 28, "beds_available": 45, "blood_units": 68,
        "ambulances": 8, "oxygen_cylinders": 40, "trust_score": 100, "status": "active"
    },
    {
        "id": "jayadeva", "name": "Jayadeva Institute of Cardiology",
        "area": "Jayanagar", "city": "Bengaluru",
        "type": "government", "lat": 12.9250, "lng": 77.5938,
        "scarcity": 81, "beds_available": 4, "blood_units": 6,
        "ambulances": 2, "oxygen_cylinders": 3, "trust_score": 100, "status": "active"
    },
    {
        "id": "nimhans", "name": "NIMHANS",
        "area": "Hosur Road", "city": "Bengaluru",
        "type": "government", "lat": 12.9414, "lng": 77.5961,
        "scarcity": 33, "beds_available": 38, "blood_units": 22,
        "ambulances": 4, "oxygen_cylinders": 25, "trust_score": 100, "status": "active"
    },
    {
        "id": "esi_blr", "name": "ESI Hospital Rajajinagar",
        "area": "Rajajinagar", "city": "Bengaluru",
        "type": "government", "lat": 12.9916, "lng": 77.5510,
        "scarcity": 55, "beds_available": 16, "blood_units": 19,
        "ambulances": 3, "oxygen_cylinders": 12, "trust_score": 100, "status": "active"
    },
    {
        "id": "manipal_blr", "name": "Manipal Hospital",
        "area": "Old Airport Road", "city": "Bengaluru",
        "type": "private", "lat": 12.9592, "lng": 77.6489,
        "scarcity": 20, "beds_available": 60, "blood_units": 85,
        "ambulances": 10, "oxygen_cylinders": 55, "trust_score": 100, "status": "active"
    },
    {
        "id": "fortis_blr", "name": "Fortis Hospital Bannerghatta",
        "area": "Bannerghatta Road", "city": "Bengaluru",
        "type": "private", "lat": 12.8933, "lng": 77.5969,
        "scarcity": 38, "beds_available": 28, "blood_units": 40,
        "ambulances": 6, "oxygen_cylinders": 30, "trust_score": 100, "status": "active"
    },
    {
        "id": "apollo_blr", "name": "Apollo Hospital Bannerghatta",
        "area": "Bannerghatta Road", "city": "Bengaluru",
        "type": "private", "lat": 12.8973, "lng": 77.5953,
        "scarcity": 62, "beds_available": 14, "blood_units": 18,
        "ambulances": 4, "oxygen_cylinders": 10, "trust_score": 100, "status": "active"
    },
    {
        "id": "narayana", "name": "Narayana Health City",
        "area": "Bommasandra", "city": "Bengaluru",
        "type": "private", "lat": 12.8340, "lng": 77.6710,
        "scarcity": 25, "beds_available": 50, "blood_units": 72,
        "ambulances": 9, "oxygen_cylinders": 48, "trust_score": 100, "status": "active"
    },
    {
        "id": "columbia_blr", "name": "Columbia Asia Hospital Hebbal",
        "area": "Hebbal", "city": "Bengaluru",
        "type": "private", "lat": 13.0358, "lng": 77.5970,
        "scarcity": 49, "beds_available": 19, "blood_units": 25,
        "ambulances": 4, "oxygen_cylinders": 16, "trust_score": 100, "status": "active"
    },
    {
        "id": "sakra", "name": "Sakra World Hospital",
        "area": "Marathahalli", "city": "Bengaluru",
        "type": "private", "lat": 12.9565, "lng": 77.7010,
        "scarcity": 67, "beds_available": 11, "blood_units": 9,
        "ambulances": 2, "oxygen_cylinders": 7, "trust_score": 100, "status": "active"
    },
    {
        "id": "rotary_ttk", "name": "Rotary TTK Blood Bank",
        "area": "Subramanyanagar", "city": "Bengaluru",
        "type": "blood_bank", "lat": 12.9980, "lng": 77.5480,
        "scarcity": 18, "beds_available": 0, "blood_units": 210,
        "ambulances": 2, "oxygen_cylinders": 0, "trust_score": 100, "status": "active"
    },
    {
        "id": "stjohns_bb", "name": "St Johns Blood Bank",
        "area": "Koramangala", "city": "Bengaluru",
        "type": "blood_bank", "lat": 12.9250, "lng": 77.6229,
        "scarcity": 30, "beds_available": 0, "blood_units": 95,
        "ambulances": 1, "oxygen_cylinders": 0, "trust_score": 100, "status": "active"
    },
    {
        "id": "cats_depot", "name": "CATS Ambulance Central Depot",
        "area": "Rajajinagar", "city": "Bengaluru",
        "type": "ambulance_depot", "lat": 12.9900, "lng": 77.5550,
        "scarcity": 15, "beds_available": 0, "blood_units": 0,
        "ambulances": 24, "oxygen_cylinders": 60, "trust_score": 100, "status": "active"
    },

    # ── MYSURU ─────────────────────────────────────────────
    {
        "id": "mysuru_general", "name": "Mysuru District Hospital",
        "area": "Irwin Road", "city": "Mysuru",
        "type": "government", "lat": 12.3052, "lng": 76.6551,
        "scarcity": 68, "beds_available": 10, "blood_units": 14,
        "ambulances": 4, "oxygen_cylinders": 8, "trust_score": 100, "status": "active"
    },
    {
        "id": "jssh_mysuru", "name": "JSS Hospital Mysuru",
        "area": "MG Road", "city": "Mysuru",
        "type": "private", "lat": 12.3155, "lng": 76.6394,
        "scarcity": 42, "beds_available": 30, "blood_units": 45,
        "ambulances": 6, "oxygen_cylinders": 28, "trust_score": 100, "status": "active"
    },
    {
        "id": "cheluvamba", "name": "Cheluvamba Hospital",
        "area": "Vontikoppal", "city": "Mysuru",
        "type": "government", "lat": 12.3198, "lng": 76.6480,
        "scarcity": 74, "beds_available": 7, "blood_units": 8,
        "ambulances": 2, "oxygen_cylinders": 5, "trust_score": 100, "status": "active"
    },
    {
        "id": "mysuru_bb", "name": "Mysuru Blood Bank",
        "area": "Nazarbad", "city": "Mysuru",
        "type": "blood_bank", "lat": 12.3090, "lng": 76.6600,
        "scarcity": 22, "beds_available": 0, "blood_units": 130,
        "ambulances": 1, "oxygen_cylinders": 0, "trust_score": 100, "status": "active"
    },

    # ── MANGALURU ──────────────────────────────────────────
    {
        "id": "wenlock", "name": "Wenlock District Hospital",
        "area": "Hampankatta", "city": "Mangaluru",
        "type": "government", "lat": 12.8698, "lng": 74.8435,
        "scarcity": 76, "beds_available": 6, "blood_units": 10,
        "ambulances": 3, "oxygen_cylinders": 6, "trust_score": 100, "status": "active"
    },
    {
        "id": "kmc_manipal", "name": "KMC Hospital Mangaluru",
        "area": "Ambedkar Circle", "city": "Mangaluru",
        "type": "private", "lat": 12.8742, "lng": 74.8432,
        "scarcity": 35, "beds_available": 40, "blood_units": 55,
        "ambulances": 7, "oxygen_cylinders": 35, "trust_score": 100, "status": "active"
    },
    {
        "id": "father_muller", "name": "Father Muller Hospital",
        "area": "Kankanady", "city": "Mangaluru",
        "type": "private", "lat": 12.8879, "lng": 74.8432,
        "scarcity": 40, "beds_available": 25, "blood_units": 38,
        "ambulances": 5, "oxygen_cylinders": 22, "trust_score": 100, "status": "active"
    },
    {
        "id": "mangaluru_bb", "name": "Mangaluru Blood Bank",
        "area": "Lalbagh", "city": "Mangaluru",
        "type": "blood_bank", "lat": 12.8650, "lng": 74.8400,
        "scarcity": 28, "beds_available": 0, "blood_units": 88,
        "ambulances": 1, "oxygen_cylinders": 0, "trust_score": 100, "status": "active"
    },

    # ── HUBBALLI-DHARWAD ───────────────────────────────────
    {
        "id": "kims_hubli", "name": "KIMS Hospital Hubballi",
        "area": "Vidyanagar", "city": "Hubballi",
        "type": "private", "lat": 15.3647, "lng": 75.1240,
        "scarcity": 58, "beds_available": 18, "blood_units": 22,
        "ambulances": 4, "oxygen_cylinders": 15, "trust_score": 100, "status": "active"
    },
    {
        "id": "district_hubli", "name": "KIMS District Hospital Hubballi",
        "area": "Navanagar", "city": "Hubballi",
        "type": "government", "lat": 15.3590, "lng": 75.1350,
        "scarcity": 71, "beds_available": 9, "blood_units": 11,
        "ambulances": 3, "oxygen_cylinders": 7, "trust_score": 100, "status": "active"
    },
    {
        "id": "sdm_dharwad", "name": "SDM Hospital Dharwad",
        "area": "Sattur", "city": "Dharwad",
        "type": "private", "lat": 15.4589, "lng": 75.0078,
        "scarcity": 44, "beds_available": 22, "blood_units": 32,
        "ambulances": 4, "oxygen_cylinders": 20, "trust_score": 100, "status": "active"
    },
    {
        "id": "hubli_bb", "name": "Hubballi Blood Bank",
        "area": "Keshwapur", "city": "Hubballi",
        "type": "blood_bank", "lat": 15.3500, "lng": 75.1200,
        "scarcity": 32, "beds_available": 0, "blood_units": 75,
        "ambulances": 1, "oxygen_cylinders": 0, "trust_score": 100, "status": "active"
    },

    # ── BELAGAVI (BELGAUM) ─────────────────────────────────
    {
        "id": "belgaum_general", "name": "Belagavi District Hospital",
        "area": "Club Road", "city": "Belagavi",
        "type": "government", "lat": 15.8497, "lng": 74.4977,
        "scarcity": 65, "beds_available": 12, "blood_units": 15,
        "ambulances": 3, "oxygen_cylinders": 9, "trust_score": 100, "status": "active"
    },
    {
        "id": "kle_belgaum", "name": "KLE Hospital Belagavi",
        "area": "Nehru Nagar", "city": "Belagavi",
        "type": "private", "lat": 15.8519, "lng": 74.5044,
        "scarcity": 38, "beds_available": 35, "blood_units": 48,
        "ambulances": 6, "oxygen_cylinders": 30, "trust_score": 100, "status": "active"
    },

    # ── TUMAKURU ───────────────────────────────────────────
    {
        "id": "tumkur_general", "name": "Tumakuru District Hospital",
        "area": "B H Road", "city": "Tumakuru",
        "type": "government", "lat": 13.3379, "lng": 77.1173,
        "scarcity": 70, "beds_available": 8, "blood_units": 10,
        "ambulances": 2, "oxygen_cylinders": 6, "trust_score": 100, "status": "active"
    },
    {
        "id": "siddaganga_tumkur", "name": "Siddaganga Hospital Tumakuru",
        "area": "SS Puram", "city": "Tumakuru",
        "type": "private", "lat": 13.3410, "lng": 77.1020,
        "scarcity": 45, "beds_available": 20, "blood_units": 28,
        "ambulances": 3, "oxygen_cylinders": 18, "trust_score": 100, "status": "active"
    },

    # ── KALABURAGI (GULBARGA) ──────────────────────────────
    {
        "id": "gulbarga_general", "name": "Kalaburagi District Hospital",
        "area": "Super Market", "city": "Kalaburagi",
        "type": "government", "lat": 17.3297, "lng": 76.8343,
        "scarcity": 78, "beds_available": 5, "blood_units": 8,
        "ambulances": 2, "oxygen_cylinders": 4, "trust_score": 100, "status": "active"
    },
    {
        "id": "esic_gulbarga", "name": "ESIC Hospital Kalaburagi",
        "area": "Sedam Road", "city": "Kalaburagi",
        "type": "government", "lat": 17.3350, "lng": 76.8200,
        "scarcity": 60, "beds_available": 14, "blood_units": 16,
        "ambulances": 3, "oxygen_cylinders": 10, "trust_score": 100, "status": "active"
    },

    # ── SHIVAMOGGA ─────────────────────────────────────────
    {
        "id": "mcgann_shimoga", "name": "McGann Hospital Shivamogga",
        "area": "Sagar Road", "city": "Shivamogga",
        "type": "government", "lat": 13.9299, "lng": 75.5681,
        "scarcity": 66, "beds_available": 11, "blood_units": 13,
        "ambulances": 3, "oxygen_cylinders": 8, "trust_score": 100, "status": "active"
    },
    {
        "id": "manipal_shimoga", "name": "Manipal Hospital Shivamogga",
        "area": "Vinoba Nagar", "city": "Shivamogga",
        "type": "private", "lat": 13.9350, "lng": 75.5600,
        "scarcity": 40, "beds_available": 24, "blood_units": 35,
        "ambulances": 4, "oxygen_cylinders": 22, "trust_score": 100, "status": "active"
    },

    # ── DAVANAGERE ─────────────────────────────────────────
    {
        "id": "bapuji_davangere", "name": "Bapuji Hospital Davanagere",
        "area": "MCC B Block", "city": "Davanagere",
        "type": "private", "lat": 14.4644, "lng": 75.9218,
        "scarcity": 52, "beds_available": 17, "blood_units": 24,
        "ambulances": 4, "oxygen_cylinders": 16, "trust_score": 100, "status": "active"
    },
    {
        "id": "chigateri_davangere", "name": "Chigateri District Hospital",
        "area": "PJ Extension", "city": "Davanagere",
        "type": "government", "lat": 14.4680, "lng": 75.9244,
        "scarcity": 73, "beds_available": 7, "blood_units": 9,
        "ambulances": 2, "oxygen_cylinders": 5, "trust_score": 100, "status": "active"
    },

    # ── BALLARI ────────────────────────────────────────────
    {
        "id": "vims_ballari", "name": "VIMS Hospital Ballari",
        "area": "Cantonment", "city": "Ballari",
        "type": "government", "lat": 15.1394, "lng": 76.9214,
        "scarcity": 69, "beds_available": 9, "blood_units": 12,
        "ambulances": 3, "oxygen_cylinders": 7, "trust_score": 100, "status": "active"
    },

    # ── HASSAN ─────────────────────────────────────────────
    {
        "id": "hassan_general", "name": "Hassan District Hospital",
        "area": "Race Course Road", "city": "Hassan",
        "type": "government", "lat": 13.0072, "lng": 76.0962,
        "scarcity": 61, "beds_available": 13, "blood_units": 16,
        "ambulances": 3, "oxygen_cylinders": 9, "trust_score": 100, "status": "active"
    },

    # ── UDUPI ──────────────────────────────────────────────
    {
        "id": "udupi_district", "name": "Udupi District Hospital",
        "area": "Manipal", "city": "Udupi",
        "type": "government", "lat": 13.3409, "lng": 74.7421,
        "scarcity": 47, "beds_available": 20, "blood_units": 26,
        "ambulances": 3, "oxygen_cylinders": 14, "trust_score": 100, "status": "active"
    },
    {
        "id": "kasturba_manipal", "name": "Kasturba Hospital Manipal",
        "area": "Manipal", "city": "Udupi",
        "type": "private", "lat": 13.3527, "lng": 74.7890,
        "scarcity": 30, "beds_available": 45, "blood_units": 60,
        "ambulances": 8, "oxygen_cylinders": 40, "trust_score": 100, "status": "active"
    },

    # ── KARNATAKA STATE AMBULANCE HUB ──────────────────────
    {
        "id": "karnataka_108_hub", "name": "Karnataka 108 Ambulance State Hub",
        "area": "Yeshwanthpur", "city": "Bengaluru",
        "type": "ambulance_depot", "lat": 13.0250, "lng": 77.5380,
        "scarcity": 12, "beds_available": 0, "blood_units": 0,
        "ambulances": 48, "oxygen_cylinders": 120, "trust_score": 100, "status": "active"
    },

    # ── KARNATAKA STATE BLOOD GRID ─────────────────────────
    {
        "id": "ksbb_state", "name": "Karnataka State Blood Bank",
        "area": "Anand Rao Circle", "city": "Bengaluru",
        "type": "blood_bank", "lat": 12.9800, "lng": 77.5720,
        "scarcity": 15, "beds_available": 0, "blood_units": 350,
        "ambulances": 3, "oxygen_cylinders": 0, "trust_score": 100, "status": "active"
    }
]

# clear existing nodes first
ref = db.reference("/nodes")
ref.delete()
print("🗑️  Cleared old data")

# seed all new nodes
for h in hospitals:
    ref.child(h["id"]).set(h)
    print(f"✓ {h['city']:12} — {h['name']}")

print(f"\n✅ {len(hospitals)} Karnataka nodes seeded successfully.")
print(f"   Cities covered: Bengaluru, Mysuru, Mangaluru, Hubballi, Belagavi, Tumakuru, Kalaburagi, Shivamogga, Davanagere, Ballari, Hassan, Udupi")