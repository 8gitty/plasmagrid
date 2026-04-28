"""
PlasmaGrid — Crisis Scenario Simulator
Use during demo to trigger realistic emergency scenarios.
Run: python backend/crisis.py
"""
import time
import requests

BASE = "http://localhost:5000"


def _update(node_id: str, scarcity: int):
    try:
        r = requests.post(
            f"{BASE}/update-node",
            json={"id": node_id, "scarcity": scarcity},
            timeout=10
        )
        data = r.json()
        if data.get("threat_detected"):
            print(f"    🛡 THREAT CAUGHT at {node_id} — immune layer activated")
        else:
            print(f"    ✓ {node_id} → scarcity {scarcity}")
    except Exception as e:
        print(f"    ❌ {node_id} failed: {e}")


def scenario_1_bengaluru_stampede():
    """
    Mass casualty event — Bengaluru Marathon stampede.
    Jayadeva cardiac + Victoria trauma surge simultaneously.
    """
    print("\n🚨 SCENARIO 1: Bengaluru Marathon Stampede")
    print("   3,000 runners. 47 casualties. Cardiac + trauma surge.")
    print("   Triggering crisis...\n")

    _update("jayadeva", 95)
    time.sleep(1)
    _update("victoria", 89)
    time.sleep(1)
    _update("apollo_blr", 82)
    time.sleep(1)
    _update("esi_blr", 77)

    print("\n   ✅ Crisis active across 4 Bengaluru hospitals")
    print("   → Click 'Run AI Allocation' on dashboard NOW")


def scenario_2_karnataka_blood_shortage():
    """
    State-wide blood shortage — monsoon accident season.
    Multiple cities simultaneously depleted.
    """
    print("\n🩸 SCENARIO 2: Karnataka Monsoon Blood Shortage")
    print("   NH-44 pile-up. State-wide blood depletion.")
    print("   Triggering across 6 hospitals...\n")

    nodes = [
        ("victoria", 88), ("wenlock", 85), ("sakra", 84),
        ("gulbarga_general", 90), ("chigateri", 87), ("vims_ballari", 83)
    ]
    for node_id, scarcity in nodes:
        _update(node_id, scarcity)
        time.sleep(0.8)

    print("\n   ✅ Blood shortage active across Bengaluru, Mangaluru, Davanagere, Kalaburagi, Ballari")
    print("   → Click 'Run AI Allocation' to see cross-city routing")


def scenario_3_cyberattack():
    """
    Ransomware attack on hospital data systems.
    Injects impossible data — triggers immune layer.
    """
    print("\n⚠️  SCENARIO 3: Cyberattack on Karnataka Health Network")
    print("   Injecting spoofed data — 20 → 99 in 5 seconds...")
    print("   (Physically impossible — immune layer should catch this)\n")

    _update("manipal_blr", 99)
    time.sleep(1)
    _update("kc_general", 98)

    print("\n   ✅ Attack injected — check Threat Monitor for quarantine alerts")
    print("   → Both nodes should be QUARANTINED by AI immune layer")


def scenario_4_coastal_disaster():
    """
    Cyclone hits Karnataka coast — Mangaluru + Udupi overwhelmed.
    """
    print("\n🌊 SCENARIO 4: Cyclone Vayu — Karnataka Coast")
    print("   Coastal hospitals overwhelmed. Inland resources needed.")
    print("   Triggering...\n")

    _update("wenlock", 92)
    time.sleep(1)
    _update("father_muller", 88)
    time.sleep(1)
    _update("kmc_mangaluru", 85)
    time.sleep(1)
    _update("udupi_district", 87)

    print("\n   ✅ Coastal crisis active — Mangaluru + Udupi")
    print("   → Watch slime mould route resources from Bengaluru to coast")


def reset_all():
    """Reset all Karnataka nodes to starting state."""
    print("\n🔄 Resetting Karnataka network to starting state...")

    starting = {
        "victoria": 72, "bowring": 45, "kc_general": 28, "jayadeva": 81,
        "nimhans": 33, "esi_blr": 55, "manipal_blr": 20, "fortis_blr": 38,
        "apollo_blr": 62, "narayana": 25, "columbia_blr": 49, "sakra": 67,
        "rotary_ttk": 18, "stjohns_bb": 30, "ksbb_state": 15, "cats_depot": 15,
        "ka108_hub": 12, "mysuru_general": 68, "jssh_mysuru": 42,
        "cheluvamba": 74, "mysuru_bb": 22, "wenlock": 76, "kmc_mangaluru": 35,
        "father_muller": 40, "mangaluru_bb": 28, "kims_hubli": 58,
        "district_hubli": 71, "sdm_dharwad": 44, "hubli_bb": 32,
        "belgaum_general": 65, "kle_belgaum": 38, "tumkur_general": 70,
        "siddaganga": 45, "gulbarga_general": 78, "esic_gulbarga": 60,
        "mcgann_shimoga": 66, "manipal_shimoga": 40, "bapuji_davangere": 52,
        "chigateri": 73, "vims_ballari": 69, "hassan_general": 61,
        "udupi_district": 47, "kasturba_manipal": 30,
    }
    for node_id, scarcity in starting.items():
        _update(node_id, scarcity)
        time.sleep(0.1)

    print("\n✅ All 43 Karnataka nodes reset to starting state.")


if __name__ == "__main__":
    print("\nPlasmaGrid Crisis Simulator — Karnataka State Network")
    print("=" * 55)
    print("Make sure Flask is running: python backend/app.py")
    print("=" * 55)
    print("\n1. Bengaluru Marathon Stampede (cardiac + trauma)")
    print("2. Karnataka Monsoon Blood Shortage (6 cities)")
    print("3. Cyberattack Simulation (immune layer demo)")
    print("4. Cyclone Vayu — Coastal Disaster (Mangaluru/Udupi)")
    print("5. Reset all nodes")

    choice = input("\nEnter scenario (1-5): ").strip()

    if choice == "1":   scenario_1_bengaluru_stampede()
    elif choice == "2": scenario_2_karnataka_blood_shortage()
    elif choice == "3": scenario_3_cyberattack()
    elif choice == "4": scenario_4_coastal_disaster()
    elif choice == "5": reset_all()
    else:               print("Invalid choice")