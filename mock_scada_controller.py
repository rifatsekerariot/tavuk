# [MOCK_SIMULATION_ONLY] 
# Can be safely removed in production.
# This script acts as a "Virtual Operator" that listens to the AI's Action Recipe
# and adjusts actuators blindly according to the AI's warnings. This allows us to test
# if the AI's recommendations actually restore the farm to an optimal state.

import paho.mqtt.client as mqtt
import json
import time
import httpx
import math

MQTT_BROKER = 'mqtt'
MQTT_PORT = 1883

def get_ai_dashboard():
    try:
        r = httpx.get('http://web:8000/api/dashboard/live', timeout=10.0)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error fetching dashboard: {e}")
    return {}

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    pass

def get_settings():
    try:
        r = httpx.get('http://web:8000/api/settings')
        return r.json()
    except:
        return {}

heater_on_since = 0
fans_max_since = 0
temp_at_heater_start = 0.0
temp_at_fan_start = 0.0
nh3_at_fan_start = 0.0

def run_operator_loop():
    client = mqtt.Client(client_id="mock_scada")
    client.on_connect = on_connect
    client.on_message = on_message
    
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            break
        except Exception as e:
            print("Operator MQTT connection failed, retrying...")
            time.sleep(2)
            
    client.loop_start()
    print("AI VIRTUAL OPERATOR started... Listening to AI prescriptions.")
    
    # Baseline normal states
    active_fans = 2 # Moderate default
    heater_w = 0.0
    
    while True:
        dashboard = get_ai_dashboard()
        biology = dashboard.get('biology', {})
        data = get_ai_dashboard()
        
        # We need fan_count from settings to know max capacity
        # The dashboard returns it in config or we can fetch settings
        try:
            settings_r = httpx.get('http://web:8000/api/settings')
            settings_data = settings_r.json()
            fan_count = settings_data.get('fan_count', 10)
        except:
            settings_data = {}
            fan_count = 10
            
        if not settings_data.get('demo_mode', False):
            time.sleep(5)
            continue
            
        bio = data.get('bio', {})
        raw = data.get('raw', {})
        openmeteo = data.get('openmeteo', {})
        
        current_t_eff = bio.get('current_t_eff', 25.0)
        target_temp = bio.get('target_temp', 25.0)
        
        # Get max NH3, CO2 and RH from zones
        zones = raw.get('zones', [])
        current_nh3 = max([z.get('nh3', 0.0) for z in zones]) if zones else raw.get('nh3', 0.0)
        current_co2 = max([z.get('co2', 400.0) for z in zones]) if zones else raw.get('co2', 400.0)
        current_rh = raw.get('rh_in', 60.0)
        
        action_text = "Tüm değerler optimum seviyede. Minimum havalandırma (dinlenme) modundayım."
        
        # --- MPC: MODEL PREDICTIVE CONTROL OPTIMIZER ---
        # Action Space
        possible_fans = [1, 2, int(fan_count/2), fan_count]
        possible_heaters = [0.0, 250000.0, 500000.0]
        
        # Physical Constants
        mean_h = (settings_data.get('ridge_h', 4.0) + settings_data.get('eaves_h', 2.8)) / 2.0
        width = settings_data.get('house_width', 14.0)
        length = settings_data.get('house_length', 120.0)
        volume = width * length * mean_h
        air_mass = volume * 1.2
        thermal_mass = air_mass * 1006.0 + (volume * 10000.0) # structure
        
        current_weight = bio.get('current_weight', 1.8)
        bird_count = settings_data.get('bird_count', 30000)
        fan_capacity = settings_data.get('fan_capacity', 30000.0)
        
        ai_enabled = settings_data.get('ai_operator_enabled', True)
        if ai_enabled:
            # Model Predictive Control (MPC) Cost Function Evaluator
            possible_fans = [0, 1, 2, 5, 10]
            possible_heaters = [0.0, 250000.0, 500000.0]
            possible_pads = [False, True]
            
            best_reward = -float('inf')
            best_action = (0, 0.0, False)
            best_reason = ""
            
            # Current Physics State
            t_in = raw.get('t_in', 25.0)
            try:
                t_out = float(openmeteo.get('t_out', 25.0))
            except:
                t_out = 25.0
            
            # Evaluate all possible actions
            for fan in possible_fans:
                for heater in possible_heaters:
                    for pad_cooling in possible_pads:
                        # 1. Physics Engine Prediction (dt = 5 mins)
                        t_incoming = t_out
                        if pad_cooling and fan > 0:
                            # Pad cooling efficiency: Drops temp by max ~8C depending on outside heat
                            max_drop = max(0.0, (t_out - 22.0) * 0.6)
                            t_incoming = t_out - max_drop
                            
                        q_gain_birds = bird_count * 10.6 * (current_weight ** 0.75)
                        m_dot = (fan * fan_capacity * 1.2) / 3600.0
                        cp_air = 1006.0
                        ua_wall = 0.5 * (width * length * 2)
                        
                        # Steady-state prediction (to prevent numeric instability in Euler integration)
                        numerator = q_gain_birds + heater + (m_dot * cp_air * t_incoming) + (ua_wall * t_out)
                        denominator = (m_dot * cp_air) + ua_wall
                        
                        if denominator > 0:
                            t_next = numerator / denominator
                        else:
                            t_next = t_in + ((q_gain_birds + heater - (ua_wall * (t_in - t_out))) * 300.0) / thermal_mass
                        
                        # Partial transition towards steady state in 5 minutes
                        time_constant = thermal_mass / max(denominator, 1.0)
                        dt = 300.0 # 5 mins
                        t_next = t_in + (t_next - t_in) * (1.0 - math.exp(-dt / time_constant))
                        
                        # Wind chill calculation
                        cross_area = width * mean_h
                        velocity = (fan * fan_capacity) / (cross_area * 3600.0)
                        wind_chill = min(velocity, 3.0) * 2.5
                        t_eff_next = t_next - wind_chill
                        temp_diff = abs(t_eff_next - target_temp)
                        
                        # Gas Predictions (dt = 5 mins)
                        nh3_prod_5m = current_weight * 0.5
                        nh3_clear_5m = (fan / max(1, fan_count)) * 12.0
                        predicted_nh3_5m = max(0.0, current_nh3 + nh3_prod_5m - nh3_clear_5m)
                        
                        co2_prod_5m = current_weight * 20.0
                        co2_clear_5m = (fan / max(1, fan_count)) * 300.0
                        predicted_co2_5m = max(400.0, current_co2 + co2_prod_5m - co2_clear_5m)
                        
                        rh_prod_5m = current_weight * 0.2
                        rh_clear_5m = (fan / max(1, fan_count)) * 6.0
                        predicted_rh_5m = max(30.0, current_rh + rh_prod_5m - rh_clear_5m)
                        
                        # 2. Financial & Biological Cost Function (₺ per 5-minute step)
                        # All units are in Turkish Liras (₺) to be mathematically aligned.
                        
                        feed_price = settings_data.get('feed_price', 15.0)
                        meat_price = settings_data.get('meat_price', 60.0)
                        electricity_price = settings_data.get('electricity_price', 3.5)
                        
                        # 2.1 Energy Cost (Electricity and fuel)
                        # A standard fan is ~1.1 kW. Running for 5 minutes (5/60 hours) consumes fan * 1.1 * 5/60 kWh
                        fan_kwh = fan * 1.1 * (5.0 / 60.0)
                        # Heater: heater (W) / 1000 * 5/60 hours to get kWh
                        heater_kwh = (heater / 1000.0) * (5.0 / 60.0)
                        # Pad cooling pump: ~0.5 kW when active
                        pad_kwh = 0.5 * (5.0 / 60.0) if pad_cooling else 0.0
                        
                        energy_cost = (fan_kwh + heater_kwh + pad_kwh) * electricity_price
                        
                        # 2.2 Biological FCR Penalty (Feed waste due to thermal/air stress)
                        # FCR penalty hourly rates from Aviagen and Kristensen & Wathes (2000)
                        fcr_penalty_5m = 0.0
                        if t_eff_next > target_temp + 0.5:
                            fcr_penalty_5m += (t_eff_next - (target_temp + 0.5)) * 0.025 / 24.0 * (5.0 / 60.0)
                        elif t_eff_next < target_temp - 2.0:
                            # Cold stress: birds consume ~2% more feed per degree below lower critical temperature (target - 2C)
                            fcr_penalty_5m += (target_temp - 2.0 - t_eff_next) * 0.02 / 24.0 * (5.0 / 60.0)
                            
                        if predicted_nh3_5m > 25.0:
                            fcr_penalty_5m += (predicted_nh3_5m - 25.0) * 0.001 / 24.0 * (5.0 / 60.0)
                        if predicted_nh3_5m > 50.0:
                            # Severe welfare and respiratory damage penalty (simulates blind/dead birds)
                            fcr_penalty_5m += (predicted_nh3_5m - 50.0) * 0.05 / 24.0 * (5.0 / 60.0)
                        
                        alive_birds = max(0, bird_count - bio.get('dead_birds', 0))
                        feed_loss_cost = alive_birds * (fcr_penalty_5m * current_weight) * feed_price
                        
                        # 2.3 Mortality Cost (Loss of meat value due to heat/CO2 stress)
                        # Mortality rate hourly equations from Wathes et al. (2002)
                        hourly_mort_rate = 0.0
                        if t_eff_next > 32.0:
                            hourly_mort_rate += 0.0005 * math.exp(0.5 * (t_eff_next - 32.0))
                        if predicted_co2_5m > 3000.0:
                            hourly_mort_rate += 0.0001 * (predicted_co2_5m - 3000.0) / 1000.0
                            
                        expected_deaths = alive_birds * hourly_mort_rate * (5.0 / 60.0)
                        death_loss_cost = expected_deaths * current_weight * meat_price
                        
                        # 2.4 Environmental Stress Penalties (Wet litter and stale air warning states)
                        # High humidity causes wet litter, estimated long-term treatment cost
                        wet_litter_penalty = max(0.0, predicted_rh_5m - 70.0) * 0.5
                        # Stale air discomfort penalty for high CO2 below the mortality threshold
                        co2_discomfort_penalty = max(0.0, predicted_co2_5m - 1500.0) * 0.02
                        
                        # 2.5 Fan Wear Cost (Actuator delta U penalty)
                        # Estimated lifetime wear cost of cycling a fan on/off (~1.0 ₺)
                        wear_cost = abs(fan - active_fans) * 1.0
                        
                        # Total reward is the negative of all financial costs
                        reward = -(energy_cost + feed_loss_cost + death_loss_cost + wet_litter_penalty + co2_discomfort_penalty + wear_cost)
                            
                        # 3. Select Best
                        if reward > best_reward:
                            best_reward = reward
                            best_action = (fan, heater, pad_cooling)
                            
                            if current_nh3 > 25.0 and fan > int(fan_count/2):
                                reason = f"Kritik amonyak (NH3) birikimi algılandı. Zehirlenmeyi önlemek için havalandırma (fan) artırıldı."
                            elif current_co2 > 2500.0 and fan > int(fan_count/2):
                                reason = f"Yüksek CO2 seviyesi (Asit fazlalığı riski). Temiz hava sağlamak için fanlar devrede."
                            elif current_rh > 70.0 and fan > int(fan_count/2):
                                reason = f"Kritik nem artışı algılandı. Altlık kuruması ve mantar önlemi için havalandırma artırıldı."
                            elif temp_diff <= 0.5 and heater == 0.0 and not pad_cooling:
                                reason = f"Tahmini konfor ideal (Sapma: {round(temp_diff,1)}°C). Sistem optimum İZLEME MODUNDA."
                            elif pad_cooling:
                                reason = f"Aşırı ısı stresi tespit edildi. Pad Cooling (Su Pompaları) devreye alındı."
                            elif heater > 0.0:
                                reason = f"Üşüme riski tespit edildi. Et kaybını önlemek için ısıtıcılar devreye alındı."
                            elif fan > int(fan_count/2):
                                reason = f"Isı stresi riski. Tavukları hayatta tutmak için fan kapasitesi artırıldı."
                            else:
                                reason = f"Hava kalitesi ve konfor dengesi sağlanıyor (İzleme Modu)."
                            best_reason = reason
            active_fans, heater_w, is_pad_cooling = best_action
        else:
            active_fans = settings_data.get('manual_active_fans', 2)
            heater_w = settings_data.get('manual_heater_w', 0.0)
            is_pad_cooling = settings_data.get('manual_pad_cooling', False)
            best_reason = "Kullanıcı Manuel Kontrol Modu (Yapay Zeka Devre Dışı)"
            
        # Ensure we don't exceed max fans
        active_fans = min(active_fans, fan_count)
        
        # ACTUATOR DIAGNOSTICS (WATCHDOG)
        global heater_on_since, temp_at_heater_start, fans_max_since, nh3_at_fan_start, temp_at_fan_start
        diagnostic_alarm = None
        now_ts = time.time()
        
        if heater_w > 0:
            if heater_on_since == 0:
                heater_on_since = now_ts
                temp_at_heater_start = raw.get('t_in', 25.0)
            elif now_ts - heater_on_since > 1800: # 30 mins
                if raw.get('t_in', 25.0) <= temp_at_heater_start + 0.5:
                    diagnostic_alarm = "Kritik Isıtıcı Arızası: Isıtıcı 30 dakikadır çalışmasına rağmen sıcaklık artmıyor! Yakıt bitmiş veya izolasyon kaçağı olabilir."
        else:
            heater_on_since = 0

        if active_fans >= max(1, fan_count * 0.8):
            if fans_max_since == 0:
                fans_max_since = now_ts
                nh3_at_fan_start = current_nh3
                temp_at_fan_start = raw.get('t_in', 25.0)
            elif now_ts - fans_max_since > 2700: # 45 mins
                if current_nh3 >= nh3_at_fan_start and raw.get('t_in', 25.0) >= temp_at_fan_start - 0.5:
                    diagnostic_alarm = "Kritik Havalandırma Arızası: Fanlar 45 dakikadır tam güçte çalışmasına rağmen etki etmiyor! Fan kayışı kopmuş veya baca tıkanmış olabilir."
        else:
            fans_max_since = 0
        
        payload = {
            "active_fans": active_fans,
            "heater_w": heater_w,
            "pad_cooling": is_pad_cooling,
            "action_text": best_reason,
            "timestamp": int(time.time()),
            "diagnostic_alarm": diagnostic_alarm
        }
        
        client.publish("farm/actuators", json.dumps(payload))
        
        # Watchdog heartbeat
        with open('/tmp/heartbeat_scada', 'w') as f:
            f.write(str(time.time()))
            
        time.sleep(5) # Act every 5 seconds to let the physical mock react

if __name__ == "__main__":
    run_operator_loop()
