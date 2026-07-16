import numpy as np
from pydantic import BaseModel
from typing import List, Dict, Any

class SimulationInput(BaseModel):
    length: float = 87.0
    width: float = 14.0
    ridge_h: float = 5.0
    eaves_h: float = 3.5
    
    fan_count: int = 14
    fan_capacity: float = 37000.0
    pad_count: int = 4
    circ_fan_count: int = 6
    inlet_count: int = 40
    
    bird_count: int = 30000
    bird_age: int = 30
    bird_weight: float = 1.5
    
    feed_price: float = 15.0
    meat_price: float = 60.0
    electricity_price: float = 3.5
    
    auto_target: bool = True
    t_target: float = 22.0
    t_crit_max: float = 28.0
    t_crit_min: float = 18.0
    rh_max: float = 75.0
    
    weather_type: str = "Gün Döngüsü (Sinüs Eğrisi)"
    t_out_fixed: float = 25.0
    rh_out_fixed: float = 60.0
    
    t_out_mean: float = 25.0
    t_out_amp: float = 7.0
    rh_out_mean: float = 60.0
    rh_out_amp: float = 15.0
    
    t_out_real: List[float] = []
    rh_out_real: List[float] = []
    
    sim_days: int = 3
    tau: float = 2.0

def run_simulation(inputs: SimulationInput) -> Dict[str, Any]:
    # Set t_target dynamically if requested
    if inputs.auto_target:
        inputs.t_target = max(20.0, 33.0 - (inputs.bird_age / 35.0) * 13.0)

    hours = int(inputs.sim_days * 24)
    time_index = np.arange(hours)
    
    if inputs.weather_type == "Gerçek Veri" and len(inputs.t_out_real) >= hours:
        t_out_arr = np.array(inputs.t_out_real[:hours])
        rh_out_arr = np.array(inputs.rh_out_real[:hours])
    elif inputs.weather_type == "Sabit Değer":
        t_out_arr = np.full(hours, inputs.t_out_fixed)
        rh_out_arr = np.full(hours, inputs.rh_out_fixed)
    else:
        # En düşük sıcaklık sabaha karşı (örn: saat 4), en yüksek öğleden sonra (saat 16)
        t_out_arr = inputs.t_out_mean + inputs.t_out_amp * np.sin(2 * np.pi * (time_index - 10) / 24)
        rh_out_arr = inputs.rh_out_mean - inputs.rh_out_amp * np.sin(2 * np.pi * (time_index - 10) / 24)

    # Fiziksel sabitler
    rho_air = 1.2 # kg/m3
    cp_air = 1005 # J/kg.K
    u_value = 0.4 # W/m2K, yalıtımlı kümes
    
    # Çatı ve duvar yüzey alanı hesabı (Pisagor teoremi ile)
    roof_pitch_length = np.sqrt((inputs.width / 2.0)**2 + (inputs.ridge_h - inputs.eaves_h)**2)
    roof_area = 2.0 * inputs.length * roof_pitch_length
    wall_area = 2.0 * (inputs.length + inputs.width) * inputs.eaves_h
    area_total = roof_area + wall_area
    
    total_mass_kg = inputs.bird_count * inputs.bird_weight
    hpu = (total_mass_kg * 10.0) / 1000.0 # 10 W/kg ortalama ısı üretimi varsayımıyla hpu hesaplanır

    # Sonuç dizileri
    res_t_in = []
    res_q_req = []
    res_fans_active = []
    res_pad_active = []
    
    res_t_in_class = []
    res_fans_class = []
    res_pad_active_class = []

    # Kontrol ve atalet için başlangıç değerleri
    t_in_prev = inputs.t_target
    t_in_class_prev = inputs.t_target
    fans_class_prev = 1

    for h in range(hours):
        t_out = t_out_arr[h]
        rh_out = rh_out_arr[h]
        
        # --- ÖNERİLEN MODEL (Isı-Enerji Dengesi) ---
        phi_s = 0.62 * (1000 + 12 * (20 - t_in_prev)) - 1.15e-7 * (t_in_prev**6)
        phi_s = max(phi_s, 0)
        phi_s_total = phi_s * hpu # Watt
        
        # Kabuk ısı transferi
        q_env = u_value * area_total * (t_in_prev - t_out)
        phi_s_net = max(0, phi_s_total - q_env)
        
        delta_t_req = inputs.t_target - t_out
        
        pad_active = False
        t_out_eff = t_out
        
        # Dışarısı çok sıcaksa ve nem uygunsa pedleri aç
        if delta_t_req <= 1.0 and rh_out < inputs.rh_max:
            pad_active = True
            t_out_eff = t_out - 6.0 # Pedlerin 6 derece soğuttuğunu varsayıyoruz
            delta_t_req = inputs.t_target - t_out_eff
            
        # Ped açılsın açılmasın, delta_t_req her durumda alt sınırla korunmalı
        delta_t_req = max(delta_t_req, 0.5)
                
        # Gerekli debi
        q_req = (phi_s_net * 3600) / (rho_air * cp_air * delta_t_req)
        
        fans_req = q_req / inputs.fan_capacity
        fans_active = min(inputs.fan_count, int(np.ceil(fans_req)))
        fans_active = max(1, fans_active) # minimum hava kalitesi havalandırması garantisi
        
        q_actual = fans_active * inputs.fan_capacity
        
        # Gerçekleşen iç sıcaklık (steady state)
        if q_actual > 0:
            actual_delta_t = (phi_s_net * 3600) / (rho_air * cp_air * q_actual)
        else:
            actual_delta_t = 10.0 # Fan çalışmıyorsa hızla ısınır
            
        t_steady_state = t_out_eff + actual_delta_t
        
        # Termal atalet (zaman sabiti) uygulaması
        t_in = t_in_prev + (t_steady_state - t_in_prev) / inputs.tau
        t_in_prev = t_in
        
        res_t_in.append(t_in)
        res_q_req.append(q_req)
        res_fans_active.append(fans_active)
        res_pad_active.append(1 if pad_active else 0)
        
        # --- KLASİK KONTROL MODELİ ---
        diff = t_in_class_prev - inputs.t_target
        
        # Histerezisli Kademe Kontrolü (Aşırı salınımı önler)
        fans_class = fans_class_prev
        if diff > 1.0:
            fans_class += 2 # Sıcaklık eşiği aştıysa fan artır
        elif diff < -0.5:
            fans_class -= 1 # Sıcaklık düştüyse fan azalt
            
        fans_class = max(1, min(inputs.fan_count, fans_class))
        fans_class_prev = fans_class
        
        q_class_actual = fans_class * inputs.fan_capacity
        
        # Klasik modelde de çok sıcaksa ve nem uygunsa ped devreye girsin
        pad_active_class = False
        if diff > 2.0 and rh_out < inputs.rh_max:
            pad_active_class = True
            t_out_eff_class = t_out - 6.0
        else:
            t_out_eff_class = t_out
            
        phi_s_class = 0.62 * (1000 + 12 * (20 - t_in_class_prev)) - 1.15e-7 * (t_in_class_prev**6)
        phi_s_class = max(phi_s_class, 0)
        phi_s_total_class = phi_s_class * hpu
        
        q_env_class = u_value * area_total * (t_in_class_prev - t_out)
        phi_s_net_class = max(0, phi_s_total_class - q_env_class)
        
        if q_class_actual > 0:
            actual_delta_t_class = (phi_s_net_class * 3600) / (rho_air * cp_air * q_class_actual)
        else:
            actual_delta_t_class = 10.0
            
        t_steady_state_class = t_out_eff_class + actual_delta_t_class
        
        # Termal atalet
        t_in_class = t_in_class_prev + (t_steady_state_class - t_in_class_prev) / inputs.tau
        t_in_class_prev = t_in_class
        
        res_t_in_class.append(t_in_class)
        res_fans_class.append(fans_class)
        res_pad_active_class.append(1 if pad_active_class else 0)

    # Calculate metrics
    warmup = 6 # İlk 6 saat soğuk başlangıç (cold start) ataleti sayılmaz
    if hours <= warmup:
        warmup = 0
        
    arr_t_in = np.array(res_t_in)
    arr_t_in_class = np.array(res_t_in_class)
    arr_fans_active = np.array(res_fans_active)
    arr_fans_class = np.array(res_fans_class)
    
    valid_t = arr_t_in[warmup:]
    valid_f = arr_fans_active[warmup:]
    valid_t_cls = arr_t_in_class[warmup:]
    valid_f_cls = arr_fans_class[warmup:]
    
    opt_new = float(np.sum((valid_t >= inputs.t_target - 1.0) & (valid_t <= inputs.t_target + 1.0)) / len(valid_t) * 100)
    crit_new = int(np.sum((valid_t >= inputs.t_crit_max) | (valid_t <= inputs.t_crit_min)))
    fans_new = float(np.sum(valid_f) + np.sum(arr_fans_active[:warmup]))
    
    opt_cls = float(np.sum((valid_t_cls >= inputs.t_target - 1.0) & (valid_t_cls <= inputs.t_target + 1.0)) / len(valid_t_cls) * 100)
    crit_cls = int(np.sum((valid_t_cls >= inputs.t_crit_max) | (valid_t_cls <= inputs.t_crit_min)))
    fans_cls = float(np.sum(valid_f_cls) + np.sum(arr_fans_class[:warmup]))

    return {
        "series": {
            "hours": time_index.tolist(),
            "t_out": t_out_arr.tolist(),
            "rh_out": rh_out_arr.tolist(),
            "t_in_new": res_t_in,
            "t_in_cls": res_t_in_class,
            "q_req_new": res_q_req,
            "fans_new": res_fans_active,
            "fans_cls": res_fans_class,
            "pad_new": res_pad_active,
            "pad_cls": res_pad_active_class
        },
        "metrics": {
            "opt_new": opt_new,
            "crit_new": crit_new,
            "fans_new": fans_new,
            "opt_cls": opt_cls,
            "crit_cls": crit_cls,
            "fans_cls": fans_cls,
            "t_target": inputs.t_target,
            "kwh_new": fans_new * 1.5,
            "kwh_cls": fans_cls * 1.5
        }
    }
