import datetime

def generate_action_recipes(series: dict) -> list:
    """
    Simülasyon sonuçlarını tarayarak kanıtlanmış akademik kurallara göre eylem reçeteleri üretir.
    Sadece önümüzdeki 48 saatlik (kısa vadeli) aksiyonları listeler.
    """
    actions = []
    
    # Sadece ilk 48 saati alalım (Aksiyon asistanı kısa vadelidir)
    max_horizon = min(48, len(series["t_in_new"]))
    t_in_new = series["t_in_new"][:max_horizon]
    hours = series["hours"][:max_horizon]
    
    heat_stress_threshold = 30.0
    
    def format_time(idx):
        val = hours[idx]
        if isinstance(val, str):
            # OpenMeteo formatı: 2026-07-09T14:00
            try:
                dt = datetime.datetime.fromisoformat(val)
                return dt.strftime("%d.%m.%Y %H:%00")
            except:
                return str(val)
        else:
            # Manuel/Sinüs formatı: int
            day = (idx // 24) + 1
            hr = idx % 24
            return f"{day}. Gün Saat {hr:02d}:00"
    
    for i in range(len(t_in_new)):
        t = t_in_new[i]
        
        if t > heat_stress_threshold:
            # Önceki 3 saat temiz miydi?
            is_new_wave = True
            for j in range(max(0, i-3), i):
                if t_in_new[j] > heat_stress_threshold:
                    is_new_wave = False
                    break
                    
            if is_new_wave:
                # 1. KURAL: Yem Kesme (Feed Withdrawal)
                feed_stop_idx = max(0, i - 2)
                actions.append({
                    "time": format_time(feed_stop_idx),
                    "type": "warning",
                    "title": "Yemlemeyi Durdurun",
                    "description": f"Saat {format_time(i)} itibariyle iç sıcaklık {t:.1f}°C'ye ulaşacak. Sindirim ısısının hayvanları yakmaması için yem hatlarını kaldırın. Sadece soğuk su verin."
                })
                
                # 2. KURAL: Fan Hazırlığı
                actions.append({
                    "time": format_time(i),
                    "type": "critical",
                    "title": "Maksimum Soğutma Protokolü",
                    "description": f"Isı stresi eşiği aşıldı! Tünel fanların tümünü devreye alın ve soğutma peteklerini ıslatın. Hedef hava hızı: Min. 2.5 m/s."
                })
    
    if not actions:
        actions.append({
            "time": "Önümüzdeki 48 Saat",
            "type": "success",
            "title": "Isı Stresi Riski Yok",
            "description": "Önümüzdeki 48 saatlik periyotta akut sıcaklık stresi beklenmiyor. Standart Aviagen havalandırma programınıza devam edebilirsiniz."
        })
        
    return actions
