import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.biology import calculate_biology_and_finance

def test_heatwave_rule():
    forecast_hourly = {
        "time": ["2026-07-10T12:00", "2026-07-11T14:00", "2026-07-12T15:00"],
        "temperature_2m": [25.0, 28.0, 36.5],
        "windspeed_10m": [10.0, 15.0, 5.0]
    }
    
    res = calculate_biology_and_finance(
        t_in_array=[26.0],
        rh_out_array=[],
        nh3_array=[10.0],
        co2_array=[800.0],
        fan_count=10,
        fan_capacity=40000,
        width=16,
        ridge_h=4.5,
        eaves_h=2.5,
        bird_count=30000,
        t_out=25.0,
        forecast_hourly=forecast_hourly
    )
    
    actions = res.get("actions", [])
    heatwave_alert = [a for a in actions if a["title"] == "Predictive AI: Gelecek Sıcak Hava Dalgası"]
    
    assert len(heatwave_alert) == 1, "Heatwave rule failed to trigger!"
    assert "36.5°C" in heatwave_alert[0]["desc"], "Heatwave description is incorrect!"
    print("test_heatwave_rule passed!")

def test_frost_rule():
    forecast_hourly = {
        "time": ["2026-07-10T12:00", "2026-07-11T03:00", "2026-07-12T15:00"],
        "temperature_2m": [25.0, 2.0, 15.0],
        "windspeed_10m": [10.0, 15.0, 5.0]
    }
    
    res = calculate_biology_and_finance(
        t_in_array=[26.0],
        rh_out_array=[],
        nh3_array=[10.0],
        co2_array=[800.0],
        fan_count=10,
        fan_capacity=40000,
        width=16,
        ridge_h=4.5,
        eaves_h=2.5,
        bird_count=30000,
        t_out=25.0,
        forecast_hourly=forecast_hourly
    )
    
    actions = res.get("actions", [])
    frost_alert = [a for a in actions if a["title"] == "Predictive AI: Don ve Termal Şok Riski"]
    
    assert len(frost_alert) == 1, "Frost rule failed to trigger!"
    assert "2.0°C" in frost_alert[0]["desc"], "Frost description is incorrect!"
    print("test_frost_rule passed!")

def test_storm_rule():
    forecast_hourly = {
        "time": ["2026-07-10T12:00", "2026-07-11T03:00", "2026-07-12T15:00"],
        "temperature_2m": [25.0, 15.0, 15.0],
        "windspeed_10m": [10.0, 75.0, 5.0]
    }
    
    res = calculate_biology_and_finance(
        t_in_array=[26.0],
        rh_out_array=[],
        nh3_array=[10.0],
        co2_array=[800.0],
        fan_count=10,
        fan_capacity=40000,
        width=16,
        ridge_h=4.5,
        eaves_h=2.5,
        bird_count=30000,
        t_out=25.0,
        forecast_hourly=forecast_hourly
    )
    
    actions = res.get("actions", [])
    storm_alert = [a for a in actions if a["title"] == "Predictive AI: Fırtına Uyarısı"]
    
    assert len(storm_alert) == 1, "Storm rule failed to trigger!"
    assert "75.0" in storm_alert[0]["desc"], "Storm description is incorrect!"
    print("test_storm_rule passed!")

if __name__ == "__main__":
    test_heatwave_rule()
    test_frost_rule()
    test_storm_rule()
    print("All predictive forecast tests passed successfully!")
