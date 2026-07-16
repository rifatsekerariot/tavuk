import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Broiler Havalandırma Simülasyonu", layout="wide")

st.title("Broiler Kümesi Isı-Enerji Dengesi ve Havalandırma Simülasyonu")
st.markdown("""
**Dikkat:** Bu simülasyon, duyulur ısı üretimi için *CIGR (2002)* basitleştirilmiş formülünü temel almaktadır. 
Gerçek saha uygulamalarında, yerel koşullara ve sensör verilerine dayalı kalibrasyon gerekebilir.
*Ölçekleme Varsayımı: 1 hpu (Isı Üreten Birim) = 1000 W toplam ısı üretimi. (Broiler için ortalama 10 W/kg kabul edilmiştir).*
""")

# --- AYARLAR / GİRDİ FORMU ---
st.header("1. Ayarlar ve Girdi Formu")

with st.expander("Kümes ve Ekipman Özellikleri", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    length = col1.number_input("Uzunluk (m)", value=87.0, min_value=1.0)
    width = col2.number_input("Genişlik (m)", value=14.0, min_value=1.0)
    ridge_h = col3.number_input("Mahya Yüksekliği (m)", value=5.0, min_value=1.0)
    eaves_h = col4.number_input("Saçak Yüksekliği (m)", value=3.5, min_value=1.0)

    col5, col6, col7, col8 = st.columns(4)
    fan_count = col5.number_input("Fan Sayısı", value=14, step=1, min_value=1)
    fan_capacity = col6.number_input("Fan Kapasitesi (m³/sa)", value=37000.0, min_value=100.0)
    pad_count = col7.number_input("Soğutma Pedi Sayısı", value=4, step=1, min_value=0)
    circ_fan_count = col8.number_input("Sirkülasyon Fanı Sayısı", value=6, step=1, min_value=0)
    
    inlet_count = st.number_input("Yan Duvar Giriş Sayısı", value=40, step=1, min_value=0)

with st.expander("Sürü Bilgileri", expanded=True):
    col1, col2, col3 = st.columns(3)
    bird_count = col1.number_input("Kuş Sayısı", value=30000, step=100, min_value=1)
    bird_age = col2.number_input("Kuş Yaşı (gün)", value=30, step=1, min_value=1)
    bird_weight = col3.number_input("Ortalama Canlı Ağırlık (kg)", value=1.5, step=0.1, min_value=0.01)

with st.expander("Çevresel Hedefler ve Koşullar", expanded=True):
    auto_target = st.checkbox("Hedef Sıcaklığı Yaşa Göre Otomatik Hesapla", value=True)
    if auto_target:
        calc_target = max(20.0, 33.0 - (bird_age / 35.0) * 13.0)
        t_target = st.number_input("Hedef İç Sıcaklık (°C) [Otomatik]", value=float(calc_target), step=0.5, disabled=True)
    else:
        t_target = st.number_input("Hedef İç Sıcaklık (°C)", value=22.0, step=0.5)

    col1, col2 = st.columns(2)
    t_crit_max = col1.number_input("Kritik Maksimum Sıcaklık (°C)", value=28.0, step=0.5)
    t_crit_min = col2.number_input("Kritik Minimum Sıcaklık (°C)", value=18.0, step=0.5)
    if t_crit_max <= t_crit_min:
        st.error("Kritik Maksimum Sıcaklık, Kritik Minimum Sıcaklıktan büyük olmalıdır.")
    
    rh_max = st.number_input("Maksimum Nem Eşiği (%)", value=75.0, step=1.0, min_value=0.0, max_value=100.0)
    
    st.subheader("Dış Hava Koşulları")
    weather_type = st.radio("Dış Sıcaklık Modeli", ["Sabit Değer", "Gün Döngüsü (Sinüs Eğrisi)"], index=1)
    if weather_type == "Sabit Değer":
        t_out_fixed = st.number_input("Dış Sıcaklık (°C)", value=25.0)
        rh_out_fixed = st.number_input("Dış Nem (%)", value=60.0, min_value=0.0, max_value=100.0)
    else:
        col3, col4 = st.columns(2)
        t_out_mean = col3.number_input("Ortalama Dış Sıcaklık (°C)", value=25.0)
        t_out_amp = col4.number_input("Sıcaklık Genliği (±°C)", value=7.0, min_value=0.0)
        col5, col6 = st.columns(2)
        rh_out_mean = col5.number_input("Ortalama Dış Nem (%)", value=60.0, min_value=0.0, max_value=100.0)
        rh_out_amp = col6.number_input("Nem Genliği (±%)", value=15.0, min_value=0.0)

    sim_days = st.number_input("Simülasyon Süresi (Gün)", value=3, step=1, min_value=1)
    tau = st.number_input("Binanın Isıl Zaman Sabiti (Saat)", value=2.0, step=0.5, min_value=0.1, help="Termal ataleti modeller. Sıcaklık ani değişmez.")

if st.button("Simülasyonu Çalıştır", type="primary"):
    
    # --- HESAPLAMA MANTIĞI ---
    hours = int(sim_days * 24)
    time_index = np.arange(hours)
    
    if weather_type == "Sabit Değer":
        t_out_arr = np.full(hours, t_out_fixed)
        rh_out_arr = np.full(hours, rh_out_fixed)
    else:
        # En düşük sıcaklık sabaha karşı (örn: saat 4), en yüksek öğleden sonra (saat 16)
        t_out_arr = t_out_mean + t_out_amp * np.sin(2 * np.pi * (time_index - 10) / 24)
        rh_out_arr = rh_out_mean - rh_out_amp * np.sin(2 * np.pi * (time_index - 10) / 24)

    # Fiziksel sabitler
    rho_air = 1.2 # kg/m3
    cp_air = 1005 # J/kg.K
    u_value = 0.4 # W/m2K, yalıtımlı kümes
    
    # Çatı ve duvar yüzey alanı hesabı (Pisagor teoremi ile)
    roof_pitch_length = np.sqrt((width / 2.0)**2 + (ridge_h - eaves_h)**2)
    roof_area = 2.0 * length * roof_pitch_length
    wall_area = 2.0 * (length + width) * eaves_h
    area_total = roof_area + wall_area
    
    total_mass_kg = bird_count * bird_weight
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
    t_in_prev = t_target
    t_in_class_prev = t_target
    fans_class_prev = 1

    for h in range(hours):
        t_out = t_out_arr[h]
        rh_out = rh_out_arr[h]
        
        # --- ÖNERİLEN MODEL (Isı-Enerji Dengesi) ---
        # phi_s (W/hpu) CIGR formülü
        phi_s = 0.62 * (1000 + 12 * (20 - t_in_prev)) - 1.15e-7 * (t_in_prev**6)
        phi_s = max(phi_s, 0)
        phi_s_total = phi_s * hpu # Watt
        
        # Kabuk ısı transferi
        q_env = u_value * area_total * (t_in_prev - t_out)
        phi_s_net = max(0, phi_s_total - q_env)
        
        delta_t_req = t_target - t_out
        
        pad_active = False
        t_out_eff = t_out
        
        # Dışarısı çok sıcaksa ve nem uygunsa pedleri aç
        if delta_t_req <= 1.0 and rh_out < rh_max:
            pad_active = True
            t_out_eff = t_out - 6.0 # Pedlerin 6 derece soğuttuğunu varsayıyoruz
            delta_t_req = t_target - t_out_eff
            
        # Ped açılsın açılmasın, delta_t_req her durumda alt sınırla korunmalı
        delta_t_req = max(delta_t_req, 0.5)
                
        # Gerekli debi
        q_req = (phi_s_net * 3600) / (rho_air * cp_air * delta_t_req)
        
        fans_req = q_req / fan_capacity
        fans_active = min(fan_count, int(np.ceil(fans_req)))
        fans_active = max(1, fans_active) # minimum hava kalitesi havalandırması garantisi
        
        q_actual = fans_active * fan_capacity
        
        # Gerçekleşen iç sıcaklık (steady state)
        if q_actual > 0:
            actual_delta_t = (phi_s_net * 3600) / (rho_air * cp_air * q_actual)
        else:
            actual_delta_t = 10.0 # Fan çalışmıyorsa hızla ısınır
            
        t_steady_state = t_out_eff + actual_delta_t
        
        # Termal atalet (zaman sabiti) uygulaması
        t_in = t_in_prev + (t_steady_state - t_in_prev) / tau
        t_in_prev = t_in
        
        res_t_in.append(t_in)
        res_q_req.append(q_req)
        res_fans_active.append(fans_active)
        res_pad_active.append(pad_active)
        
        # --- KLASİK KONTROL MODELİ ---
        diff = t_in_class_prev - t_target
        
        # Histerezisli Kademe Kontrolü (Aşırı salınımı önler)
        fans_class = fans_class_prev
        if diff > 1.0:
            fans_class += 2 # Sıcaklık eşiği aştıysa fan artır
        elif diff < -0.5:
            fans_class -= 1 # Sıcaklık düştüyse fan azalt
            
        fans_class = max(1, min(fan_count, fans_class))
        fans_class_prev = fans_class
        
        q_class_actual = fans_class * fan_capacity
        
        # Klasik modelde de çok sıcaksa ve nem uygunsa ped devreye girsin
        pad_active_class = False
        if diff > 2.0 and rh_out < rh_max:
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
        t_in_class = t_in_class_prev + (t_steady_state_class - t_in_class_prev) / tau
        t_in_class_prev = t_in_class
        
        res_t_in_class.append(t_in_class)
        res_fans_class.append(fans_class)
        res_pad_active_class.append(pad_active_class)

    # DataFrame oluşturma
    df = pd.DataFrame({
        "Saat": time_index,
        "Dış Sıcaklık (°C)": t_out_arr,
        "Yeni Model İç Sıcaklık (°C)": res_t_in,
        "Klasik Model İç Sıcaklık (°C)": res_t_in_class,
        "Yeni Model Gerekli Debi (m³/sa)": res_q_req,
        "Yeni Model Aktif Fan Sayısı": res_fans_active,
        "Klasik Model Aktif Fan Sayısı": res_fans_class,
        "Ped Durumu": np.where(res_pad_active, 1, 0),
        "Klasik Model Ped Durumu": np.where(res_pad_active_class, 1, 0)
    })
    
    # --- SONUÇ GÖSTERİMİ ---
    st.markdown("---")
    st.header("2. Simülasyon Sonuçları")
    
    # Metrikler
    st.subheader("Özet Karşılaştırma")
    
    def calc_metrics(t_series, f_series):
        warmup = 6 # İlk 6 saat soğuk başlangıç (cold start) ataleti sayılmaz
        if hours <= warmup:
            warmup = 0
            
        valid_t = t_series[warmup:]
        valid_f = f_series[warmup:]
        
        opt_time = np.sum((valid_t >= t_target - 1.0) & (valid_t <= t_target + 1.0)) / len(valid_t) * 100
        crit_time = np.sum((valid_t >= t_crit_max) | (valid_t <= t_crit_min))
        total_fans_hours = np.sum(valid_f) + np.sum(f_series[:warmup]) # fan-saat tüm simülasyon boyunca harcanır
        return opt_time, crit_time, total_fans_hours

    opt_new, crit_new, fans_new = calc_metrics(np.array(res_t_in), np.array(res_fans_active))
    opt_cls, crit_cls, fans_cls = calc_metrics(np.array(res_t_in_class), np.array(res_fans_class))
    
    st.info("Not: İç sıcaklık metrikleri (Optimal Süre ve Kritik Aşım) sistemin ısıl dengeye oturması için simülasyonun ilk 6 saati (Warm-up) dışarıda bırakılarak hesaplanmıştır.")
    
    col1, col2, col3 = st.columns(3)
    
    # 5. Renk Kodlaması: Kritik Aşım varsa col3 st.error ile sarmalanır.
    with col1:
        st.metric("Optimal Sıcaklıkta Geçen Süre", f"%{opt_new:.1f}", f"%{opt_new - opt_cls:.1f} (Klasik: %{opt_cls:.1f})")
    
    with col2:
        # 6. Fan-saat değerini kWh eşdeğerine çevirme (varsayım: 1 fan-saat = 1.5 kWh)
        kwh_new = fans_new * 1.5
        kwh_cls = fans_cls * 1.5
        st.metric("Toplam Fan (kWh Eşdeğeri)", f"≈{kwh_new:,.0f} kWh", f"{kwh_new - kwh_cls:,.0f} kWh (Klasik: {kwh_cls:,.0f})", delta_color="inverse", help="Hesaplamada 1 fan-saat = 1.5 kWh varsayılmıştır.")
        
    with col3:
        if crit_new > 0:
            st.error(f"Kritik Aşım: {crit_new} Saat (Klasik: {crit_cls})")
        else:
            st.success(f"Kritik Aşım: {crit_new} Saat (Klasik: {crit_cls})")
            
    # 9. Özet Cümle
    st.info(f"💡 **Özet:** Yeni model, klasik modele göre **%{opt_new - opt_cls:.1f}** daha uzun süre optimal sıcaklıkta kaldı ve **{kwh_cls - kwh_new:,.0f} kWh** enerji tasarrufu sağladı.")
    
    if np.any(np.array(res_t_in) >= 35.0) or np.any(np.array(res_t_in_class) >= 35.0):
        st.error("🚨 KRİTİK UYARI: Simülasyon sırasında iç sıcaklık 35°C'nin üzerine çıktı! Bu durum kuşlar için biyolojik olarak ölümcüldür (Lethal Heat Stress). Fan kapasitesi yetersiz olabilir veya dış hava aşırı sıcak/nemli.")

    # 8. Sekmeler
    tab1, tab2, tab3 = st.tabs(["Sıcaklık Grafiği", "Aktüatör Zaman Çizelgesi", "Gerekli Debi Grafiği"])
    
    with tab1:
        # 1 & 2. Plotly ile eşik çizgileri ve gölgeli bant
        fig_temp = go.Figure()
        fig_temp.add_hrect(y0=t_target - 1.0, y1=t_target + 1.0, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Optimal Bant", annotation_position="top left")
        fig_temp.add_hline(y=t_crit_max, line_dash="dash", line_color="red", annotation_text="Kritik Max")
        fig_temp.add_hline(y=t_crit_min, line_dash="dash", line_color="red", annotation_text="Kritik Min", annotation_position="bottom right")
        fig_temp.add_hline(y=t_target, line_dash="dot", line_color="darkgreen", annotation_text="Hedef")
        
        # 3. Gün çizgileri
        for d in range(1, int(sim_days) + 1):
            fig_temp.add_vline(x=d * 24, line_width=1, line_dash="dash", line_color="gray", opacity=0.4)
            
        fig_temp.add_trace(go.Scatter(x=df["Saat"], y=df["Yeni Model İç Sıcaklık (°C)"], name="Yeni Model İç Sıcaklık", line=dict(color="blue", width=2)))
        fig_temp.add_trace(go.Scatter(x=df["Saat"], y=df["Klasik Model İç Sıcaklık (°C)"], name="Klasik Model İç Sıcaklık", line=dict(color="orange", width=2)))
        fig_temp.add_trace(go.Scatter(x=df["Saat"], y=df["Dış Sıcaklık (°C)"], name="Dış Sıcaklık", line=dict(color="gray", dash="dot")))
        fig_temp.update_layout(height=450, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_temp, use_container_width=True)

    with tab2:
        # 4. Birleşik Fan ve Ped Grafiği
        fig_act = go.Figure()
        for d in range(1, int(sim_days) + 1):
            fig_act.add_vline(x=d * 24, line_width=1, line_dash="dash", line_color="gray", opacity=0.4)
            
        fig_act.add_trace(go.Scatter(x=df["Saat"], y=df["Yeni Model Aktif Fan Sayısı"], name="Yeni Model Fan", fill='tozeroy', line=dict(color="blue", width=1), opacity=0.4))
        fig_act.add_trace(go.Scatter(x=df["Saat"], y=df["Klasik Model Aktif Fan Sayısı"], name="Klasik Model Fan", mode='lines', line=dict(color="orange", width=2)))
        
        # Ped aktivasyonu max fan sayısına ölçeklenip arka plan bölgesi gibi gösterildi
        fig_act.add_trace(go.Scatter(x=df["Saat"], y=df["Ped Durumu"] * fan_count, name="Yeni Model Ped Aktif (Açık/Kapalı)", fill='tozeroy', line=dict(color="cyan", width=0), opacity=0.2))
        fig_act.add_trace(go.Scatter(x=df["Saat"], y=df["Klasik Model Ped Durumu"] * fan_count, name="Klasik Model Ped Aktif", mode='lines', line=dict(color="red", dash="dot", width=1)))
        
        fig_act.update_layout(height=450, margin=dict(l=0, r=0, t=30, b=0), yaxis_title="Aktif Fan Sayısı", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_act, use_container_width=True)

    with tab3:
        # 7. Büyük sayıların binlik ayraçla formatlanması
        fig_flow = go.Figure()
        for d in range(1, int(sim_days) + 1):
            fig_flow.add_vline(x=d * 24, line_width=1, line_dash="dash", line_color="gray", opacity=0.4)
            
        fig_flow.add_trace(go.Scatter(x=df["Saat"], y=df["Yeni Model Gerekli Debi (m³/sa)"], name="Gerekli Debi", fill='tozeroy', line=dict(color="purple", width=2)))
        fig_flow.update_layout(height=450, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(tickformat=",.0f"), yaxis_title="Debi (m³/sa)")
        st.plotly_chart(fig_flow, use_container_width=True)
