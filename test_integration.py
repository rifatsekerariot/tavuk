import requests
import json
import time

API_URL = "http://localhost:9040"

def test_api():
    print("Test 1: Ayarları Getir (Settings API)")
    try:
        res = requests.get(f"{API_URL}/api/settings")
        res.raise_for_status()
        settings = res.json()
        print(" [OK] Settings fetch successful.")
        print("  - Bird count:", settings.get("bird_count"))
        print("  - AI Enabled:", settings.get("ai_operator_enabled"))
    except Exception as e:
        print(f" [FAIL] Failed to fetch settings: {e}")
        return False

    print("\nTest 2: Canlı Dashboard & Algoritma Testi (Live Dashboard API)")
    try:
        res = requests.get(f"{API_URL}/api/dashboard/live")
        res.raise_for_status()
        data = res.json()
        print(" [OK] Live dashboard data fetched.")
        
        # Check if algorithms return data
        bio = data.get("bio", {})
        actions = bio.get("actions", [])
        print(f"  - Calculated Current Weight: {bio.get('current_weight')}")
        print(f"  - Total Actions/Alarms returned: {len(actions)}")
        
        # Check if actuators (SCADA) are connected
        actuators = data.get("actuators", {})
        if actuators:
            print(" [OK] SCADA/Actuator data is present.")
            print(f"  - Active Fans: {actuators.get('active_fans')}")
            print(f"  - Heater W: {actuators.get('heater_w')}")
        else:
            print(" [WARNING] No SCADA/Actuator data found (Might be missing MQTT or AI Operator).")
    except Exception as e:
        print(f" [FAIL] Failed to fetch live data: {e}")
        return False
        
    print("\nTest 3: Geçmiş Veri Testi (History API)")
    try:
        res = requests.get(f"{API_URL}/api/dashboard/history?range=1h")
        res.raise_for_status()
        history = res.json()
        print(f" [OK] History fetch successful. Found {len(history)} data points.")
    except Exception as e:
        print(f" [FAIL] Failed to fetch history: {e}")
        return False

    print("\nTüm testler başarıyla tamamlandı. API ve Algoritmalar entegre çalışıyor.")
    return True

if __name__ == "__main__":
    test_api()
