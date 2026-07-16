import paho.mqtt.client as mqtt
import json
import time
import random
import httpx

MQTT_BROKER = 'mqtt'
MQTT_PORT = 1883

def get_settings():
    try:
        r = httpx.get('http://web:8000/api/settings', timeout=5.0)
        return r.json()
    except Exception:
        try:
            r = httpx.get('http://localhost:8000/api/settings', timeout=5.0)
            return r.json()
        except Exception:
            return {'sensor_count': 6, 'mqtt_topic': 'farm/sensors'}

cumulative_dead_birds = 0.0
last_reported_dead = 0

# Global Actuator States from SCADA
actuator_state = {
    "active_fans": 0,
    "heater_w": 0.0,
    "pad_cooling": False
}

def on_connect(client, userdata, flags, rc):
    client.subscribe("farm/actuators")

def on_message(client, userdata, msg):
    global actuator_state
    try:
        data = json.loads(msg.payload.decode())
        if "active_fans" in data:
            actuator_state["active_fans"] = data["active_fans"]
        if "heater_w" in data:
            actuator_state["heater_w"] = data["heater_w"]
        if "pad_cooling" in data:
            actuator_state["pad_cooling"] = data["pad_cooling"]
    except Exception:
        pass

def publish_mock_data():
    global actuator_state
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Keep trying to connect if broker is not ready
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            break
        except Exception as e:
            print("Broker not ready, waiting...", e)
            time.sleep(2)
            
    client.loop_start()
    
    print('Mock MQTT script started for MULTI-SENSOR architecture. Press Ctrl+C to stop.')
    
    zones = {}
    # Caching external weather to avoid spamming the API every 5 seconds
    weather_cache = {'t_out': 20.0, 'last_fetch': 0, 'lat': None, 'lon': None}
    
    global cumulative_dead_birds, last_reported_dead
    
    while True:
        settings = get_settings()
        
        if not settings.get('demo_mode', False):
            time.sleep(5)
            continue
            
        sensor_count = settings.get('sensor_count', 6)
        base_topic = settings.get('mqtt_topic', 'farm/sensors')
        
        lat = settings.get('lat', 38.4237)
        lon = settings.get('lon', 27.1428)
        
        # If location changed, invalidate cache immediately
        if lat != weather_cache.get('lat') or lon != weather_cache.get('lon'):
            weather_cache['last_fetch'] = 0
            weather_cache['lat'] = lat
            weather_cache['lon'] = lon
            
        bird_count = settings.get('bird_count', 30000)
        bird_count = settings.get('bird_count', 30000)
        
        # Calculate dynamic bird weight based on age
        flock_start_date = settings.get('flock_start_date')
        bird_age_days = 0.0
        if flock_start_date:
            try:
                from datetime import datetime
                # Remove Z for isoformat parsing in Python 3.10- if present
                clean_date = flock_start_date.replace("Z", "+00:00")
                start_dt = datetime.fromisoformat(clean_date)
                start_dt = start_dt.replace(tzinfo=None)
                bird_age_days = (datetime.utcnow() - start_dt).total_seconds() / 86400.0
            except:
                bird_age_days = 0.0
                
        from core.biology import calculate_dynamic_weight
        flock_breed = settings.get('flock_breed', 'Ross 308 (Etlik)')
        initial_weight = settings.get('bird_weight', 1.8)
        bird_weight = calculate_dynamic_weight(initial_weight, bird_age_days, flock_breed)
        fan_count = settings.get('fan_count', 10)
        fan_capacity = settings.get('fan_capacity', 40000.0)
        
        now = time.time()
        if now - weather_cache['last_fetch'] > 600: # fetch every 10 mins
            try:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,windspeed_10m&forecast_days=14"
                r = httpx.get(url, timeout=5.0)
                if r.status_code == 200:
                    data = r.json()
                    weather_cache['t_out'] = float(data.get('current_weather', {}).get('temperature', 20.0))
                weather_cache['last_fetch'] = now
            except:
                pass
                
        t_out = weather_cache['t_out']
        
        # Target Temp based on breed and age
        if "Yumurtacı" in flock_breed:
            target_t = max(21.0, 33.0 - (bird_age_days * 0.34))
        else:
            target_t = max(20.0, 33.0 - (bird_age_days * 0.371))
            
        # Read actuator states from the SCADA controller (fallback to defaults if SCADA is offline)
        active_fans = actuator_state["active_fans"]
        if active_fans == 0: 
            active_fans = max(1, int(fan_count * 0.1)) # Prevent DivisionByZero if SCADA hasn't sent data yet
            
        heater_w = actuator_state["heater_w"]
            
        # BIOLOGICAL THERMODYNAMICS & DIURNAL CYCLE
        from datetime import datetime
        current_hour = datetime.now().hour
        # Birds are more active during the day (06:00 - 20:00)
        activity_multiplier = 1.15 if 6 <= current_hour <= 20 else 0.85
        
        shp_per_bird = 10.62 * (bird_weight ** 0.75) * activity_multiplier
        alive_birds = max(0, bird_count - cumulative_dead_birds)
        total_heat_w = (alive_birds * shp_per_bird) + heater_w
        
        total_vol_m3_h = active_fans * fan_capacity
        if total_vol_m3_h < 1000:
            total_vol_m3_h = 1000.0 
            
        m_dot_kg_s = (total_vol_m3_h * 1.2) / 3600.0
        cp_air = 1006.0 # J/(kg*K)
        
        # --- TRUE MASS BALANCE GAS & THERMO DYNAMICS ---
        # 1. Volume Calculation
        house_length = settings.get('house_length', 120.0)
        house_width = settings.get('house_width', 14.0)
        eaves_h = settings.get('eaves_h', 2.8)
        ridge_h = settings.get('ridge_h', 4.0)
        volume_m3 = house_width * house_length * (eaves_h + (ridge_h - eaves_h) / 2.0)
        if volume_m3 < 100: volume_m3 = 5000.0 # Safety fallback
        mass_air_kg = volume_m3 * 1.2
        
        # 2. Production Rates
        dt_hours = 60.0 / 3600.0 # 1 minute simulation step
        # CO2 Prod: 0.185 m3/h per 1000W heat (CIGR 2002)
        co2_prod_baseline_m3_h = (total_heat_w / 1000.0) * 0.185 
        # NH3 Prod: ~25-30 mg/h per kg of bird (realistic broiler emission)
        nh3_prod_baseline_mg_h = alive_birds * (25.0 * bird_weight) * activity_multiplier

        # 3. Thermodynamics & Psychrometrics
        import math
        wall_area_m2 = 2 * (house_length * eaves_h) + 2 * (house_width * ridge_h) + (house_length * house_width)
        U_value = 0.5 # W/m2K
        
        latent_heat_per_bird = 2.5 * activity_multiplier # Watts/bird
        # Latent heat of vaporization ~680 Wh/kg -> Water prod in kg/h
        water_prod_kg_h = alive_birds * (latent_heat_per_bird / 680.0)
        
        pad_cooling_active = actuator_state.get("pad_cooling", False)
        pad_cooling_effect = 0.0
        pad_added_water_kg_h = 0.0
        q_cool_w = 0.0
        if pad_cooling_active and active_fans > 0:
            # Drop incoming temp by up to 8C depending on outside air
            pad_cooling_effect = max(0.0, (t_out - 22.0) * 0.6)
            # Q_cool = m_dot_kg_s * cp_air * pad_cooling_effect (Watts)
            q_cool_w = m_dot_kg_s * cp_air * pad_cooling_effect
            pad_added_water_kg_h = q_cool_w / 680.0
            
        def get_es(t): return 6.112 * math.exp((17.67 * t) / (t + 243.5))
        def rh_to_w(rh, t):
            e = (rh / 100.0) * get_es(t)
            return 0.622 * e / max(1.0, (1013.25 - e))
        def w_to_rh(w, t):
            e = (w * 1013.25) / (w + 0.622)
            return min(100.0, max(0.0, (e / get_es(t)) * 100.0))
            
        outdoor_rh = 50.0 # Default outdoor RH
        w_out = rh_to_w(outdoor_rh, t_out)
        
        for i in range(1, sensor_count + 1):
            zone_id = f"zone-{i}"
            
            if zone_id not in zones:
                # Initialization
                zones[zone_id] = {
                    't': max(25.0, t_out),
                    'rh': 60.0,
                    'nh3': 5.0,
                    'co2': 600.0
                }
            
            z = zones[zone_id]
            
            # --- TRUE MASS BALANCE GAS DYNAMICS ---
            zone_vent_efficiency = 1.0 # No dead zones, all sensors identical
            eff_vol_m3_h = (total_vol_m3_h / sensor_count) * zone_vent_efficiency
            
            # Heat Balance (Temperature)
            # dT/dt = (Heat_gain - Heat_loss_vent - Heat_loss_wall) / Thermal_Mass
            q_gain = total_heat_w / sensor_count
            q_loss_vent = eff_vol_m3_h * 1.2 * (1006.0 / 3600.0) * (z['t'] - t_out)
            q_loss_wall = (U_value * wall_area_m2 / sensor_count) * (z['t'] - t_out)
            # Thermal mass of building = approx 10x air mass
            effective_thermal_mass_j_k = (mass_air_kg / sensor_count) * 1006.0 * 10.0
            
            delta_t = ((q_gain - q_loss_vent - q_loss_wall - (q_cool_w / sensor_count)) * (dt_hours * 3600.0)) / effective_thermal_mass_j_k
            z['t'] += delta_t + random.uniform(-0.05, 0.05)
            
            # Moisture Balance (Humidity)
            w_in = rh_to_w(z['rh'], z['t'])
            moisture_loss_kg_h = eff_vol_m3_h * 1.2 * (w_in - w_out)
            
            delta_w_kg = ((water_prod_kg_h / sensor_count) + (pad_added_water_kg_h / sensor_count) - moisture_loss_kg_h) * dt_hours
            new_w_in = w_in + (delta_w_kg / (mass_air_kg / sensor_count))
            
            z['rh'] = w_to_rh(new_w_in, z['t']) + random.uniform(-0.2, 0.2)
            
            # --- Gas Mass Balance Calculation ---
            # CO2
            co2_in = z['co2'] / 1e6
            co2_out = 400.0 / 1e6
            co2_loss_m3_h = eff_vol_m3_h * (co2_in - co2_out)
            delta_co2_m3 = ((co2_prod_baseline_m3_h / sensor_count) - co2_loss_m3_h) * dt_hours
            new_co2_in = co2_in + (delta_co2_m3 / (volume_m3 / sensor_count))
            z['co2'] = max(400.0, new_co2_in * 1e6) + random.uniform(-10.0, 10.0)
            
            # NH3
            rh_factor = max(0.1, math.exp((z['rh'] - 55.0) / 15.0))
            zone_nh3_prod_mg_h = (nh3_prod_baseline_mg_h / sensor_count) * rh_factor
            
            current_nh3_mg_m3 = z['nh3'] / 1.428
            vent_loss_nh3_mg_h = eff_vol_m3_h * current_nh3_mg_m3
            
            delta_nh3_mg = (zone_nh3_prod_mg_h - vent_loss_nh3_mg_h) * dt_hours
            mixing_inertia = 0.25 # Yavaş difüzyon (Ani fırlamaları yumuşatır)
            new_nh3_mg_m3 = current_nh3_mg_m3 + (delta_nh3_mg / (volume_m3 / sensor_count)) * mixing_inertia
            z['nh3'] = new_nh3_mg_m3 * 1.428 + random.uniform(-0.1, 0.1)
            
            # ----------------------------------------------------
            # SENSOR FAULT INJECTION (For Testing Outlier Filters)
            # Strict realistic bounds
            z['t'] = max(t_out - 10.0, min(z['t'], 60.0))
            z['rh'] = max(30.0, min(z['rh'], 95.0))
            z['nh3'] = max(0.0, min(z['nh3'], 200.0))
            z['co2'] = max(400.0, min(z['co2'], 10000.0))
            
            payload = {
                'applicationID': '1',
                'applicationName': 'AriotTest',
                'deviceName': f'UG65_{zone_id}',
                'object': {
                    'zone': zone_id,
                    'temperature': round(z['t'], 1),
                    'humidity': round(z['rh'], 1),
                    'nh3': round(z['nh3'], 1),
                    'co2': int(z['co2'])
                }
            }
            
            msg = json.dumps(payload)
            topic = f"{base_topic}/{zone_id}"
            client.publish(topic, msg)
            client.publish(f"{base_topic}/{zone_id}/co2", json.dumps(payload))
            
        # Watchdog heartbeat
        with open('/tmp/heartbeat', 'w') as f:
            f.write(str(time.time()))
            
        time.sleep(60)

if __name__ == "__main__":
    publish_mock_data()
