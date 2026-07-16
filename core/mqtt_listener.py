import paho.mqtt.client as mqtt
import json
import os
from sqlalchemy.orm import Session
from database.config import SessionLocal
from database.models import IoTData, FarmSettings
from core.biology import calculate_biology_and_finance

MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'farm/sensors')

def on_connect(client, userdata, flags, rc):
    print(f'Connected to MQTT Broker with result code {rc}')
    # Subscribe to base topic and all subtopics
    base_topic = MQTT_TOPIC.rstrip('/#')
    client.subscribe(f"{base_topic}/#")
    client.subscribe("farm/actuators")

virtual_operator_state = {
    "active_fans": 0,
    "heater_w": 0.0,
    "pad_cooling": False,
    "action_text": "Sistem başlatılıyor...",
    "action_history": [],
    "timestamp": 0
}

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        if topic == "farm/actuators":
            new_text = payload.get("action_text", "")
            # Only append to history if it changed or history is empty
            if not virtual_operator_state["action_history"] or virtual_operator_state["action_text"] != new_text:
                if new_text:
                    virtual_operator_state["action_history"].insert(0, {
                        "text": new_text,
                        "timestamp": payload.get("timestamp", 0)
                    })
                    # Keep only last 5 actions
                    virtual_operator_state["action_history"] = virtual_operator_state["action_history"][:5]
            
            virtual_operator_state["active_fans"] = payload.get("active_fans", 0)
            virtual_operator_state["heater_w"] = payload.get("heater_w", 0.0)
            virtual_operator_state["pad_cooling"] = payload.get("pad_cooling", False)
            virtual_operator_state["action_text"] = new_text
            virtual_operator_state["timestamp"] = payload.get("timestamp", 0)
            virtual_operator_state["diagnostic_alarm"] = payload.get("diagnostic_alarm")
            return
            
        obj = payload.get('object', payload)
        
        # Determine zone from topic (e.g., farm/sensors/zone-2)
        # Or from payload (e.g., {"zone": "zone-2"})
        zone_id = obj.get('zone', obj.get('zone_id', None))
        if not zone_id:
            # Fallback to topic suffix
            parts = topic.split('/')
            zone_id = parts[-1] if len(parts) > 1 else 'zone-1'
            if not zone_id.startswith('zone'):
                zone_id = f"zone-{zone_id}"
                
        # Ensure it's in the format 'zone-X'
        if isinstance(zone_id, int) or (isinstance(zone_id, str) and zone_id.isdigit()):
            zone_id = f"zone-{zone_id}"
            
        t_in = obj.get('temperature', obj.get('t_in', 25.0))
        rh_in = obj.get('humidity', obj.get('rh_in', 50.0))
        nh3_ppm = obj.get('nh3', obj.get('nh3_ppm', 0.0))
        co2_ppm = obj.get('co2', obj.get('co2_ppm', 400.0))
        
        db = SessionLocal()
        try:
            iot_record = IoTData(
                zone_id=zone_id,
                t_in=t_in,
                rh_in=rh_in,
                nh3_ppm=nh3_ppm,
                co2_ppm=co2_ppm
            )
            db.add(iot_record)
            db.commit()
            print(f'Saved IoT Data [{zone_id}]: T={t_in}, RH={rh_in}, NH3={nh3_ppm}, CO2={co2_ppm}')
        finally:
            db.close()
    except Exception as e:
        print(f'Error processing MQTT message: {e}')

def start_mqtt_listener():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    import time
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            print(f'Successfully connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}')
            break
        except Exception as e:
            print(f'MQTT Connection Failed: {e}. Retrying in 5 seconds...')
            time.sleep(5)

if __name__ == '__main__':
    start_mqtt_listener()
    import time
    while True:
        time.sleep(1)

