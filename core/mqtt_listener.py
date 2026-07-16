import paho.mqtt.client as mqtt
import json
import os
from sqlalchemy.orm import Session
from database.config import SessionLocal
from database.models import IoTData, FarmSettings, Device
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
            
        # Determine device ID from payload or topic
        device_id = None
        if "deviceInfo" in payload:
            device_id = payload["deviceInfo"].get("deviceName") or payload["deviceInfo"].get("devEui")
        if not device_id:
            device_id = payload.get("deviceName") or payload.get("devEui")
        if not device_id:
            # Fallback to topic parts
            parts = topic.split('/')
            device_id = parts[-1] if len(parts) > 1 else 'zone-1'
            if not device_id.startswith('zone') and not device_id.startswith('UG65'):
                device_id = f"UG65_{device_id}"

        db = SessionLocal()
        try:
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                # Device is unregistered!
                from core.adapters.registry import adapter_registry
                guessed_codec = adapter_registry.resolve_fallback(topic, payload)
                guessed_vendor = "Unknown"
                if guessed_codec:
                    guessed_vendor = guessed_codec.split('_')[0].capitalize()
                
                from database.models import AlarmHistory
                alarm = AlarmHistory(
                    type="warning",
                    title="Unregistered Device Detected",
                    desc=f"Payload received from unregistered device ID '{device_id}' on topic '{topic}'. Guessed vendor profile: {guessed_vendor}. Data discarded."
                )
                db.add(alarm)
                db.commit()
                print(f"WARNING: Discarded payload from unregistered device '{device_id}'")
                return
                
            from core.adapters.registry import adapter_registry
            adapter = adapter_registry.get_by_codec(device.codec_id)
            if not adapter:
                print(f"ERROR: Adapter not found for codec_id '{device.codec_id}'")
                return
                
            readings = adapter.decode(topic, payload, device)
            
            # Reduce to IoTData (long-to-wide format mapping)
            t_in, rh_in, nh3_ppm, co2_ppm = None, None, None, None
            ts = None
            for r in readings:
                if r.quality == "ok":
                    if not ts:
                        ts = r.timestamp
                    if r.metric == "temperature":
                        t_in = r.value
                    elif r.metric == "humidity":
                        rh_in = r.value
                    elif r.metric == "nh3":
                        nh3_ppm = r.value
                    elif r.metric == "co2":
                        co2_ppm = r.value
            
            if t_in is not None and rh_in is not None:
                iot_record = IoTData(
                    zone_id=device.zone_id,
                    t_in=t_in,
                    rh_in=rh_in,
                    nh3_ppm=nh3_ppm,
                    co2_ppm=co2_ppm,
                    timestamp=ts
                )
                db.add(iot_record)
                db.commit()
                print(f"Saved IoT Data [{device.zone_id}] from device [{device.id}]: T={t_in}, RH={rh_in}, NH3={nh3_ppm}, CO2={co2_ppm}")
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

