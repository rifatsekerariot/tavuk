"""
=====================================================================================
AKILLI KÜMES SÜRÜ SAĞLIĞI TAKİP SİSTEMİ - V2 (3 KATMANLI FİLTRE MİMARİSİ)
=====================================================================================
Bu script, harici bir video dosyasına ihtiyaç duymadan, sentetik numpy dizileri ile
üç katmanlı filtre mimarisini simüle eder.

Eklenen Özellikler:
    1) Işık/Zaman Filtresi: Eşikler Aydınlık/Loş/Karanlık durumlarına göre özel hesaplanır.
    2) Kalıcılık Kriteri: N ardışık pencere (Sliding Window) boyunca süren ihlaller aranır.
    3) Çift Sinyal Füzyonu: Hareket ve Entropi eş zamanlı ihlali kontrol edilir.

Senaryo (48 Saat):
    Saat 1-24  : SAĞLIKLI DURUM  -> Işığa göre hareket değişir, entropi homojendir.
    Saat 25-48 : HASTALIK/ANOMALİ -> Hareket sürekli düşük, sürü yığılır (entropi çöker).
=====================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# 0) GENEL PARAMETRELER
# ------------------------------------------------------------------------------
np.random.seed(42)

TOTAL_HOURS   = 48                 # 2 günlük simülasyon (24h sağlıklı, 24h hastalık)
HEALTHY_HOURS = 24                 # İlk 24 saat referans (baseline) dönemi
N_CHICKENS    = 3000
GRID_SIZE     = 10
N_CELLS       = GRID_SIZE * GRID_SIZE
MAX_ENTROPY   = np.log2(N_CELLS)
FRAME_RES     = 100
PERSISTENCE_N = 3                  # Alarm için gereken ardışık ihlal saati (Sliding Window)

# Aydınlatma Rejimi: 16 saat Aydınlık, 2 saat Loş, 6 saat Karanlık
def get_light_state(hour):
    h = hour % 24
    if 6 <= h < 22:
        return 'Aydinlik'
    elif 22 <= h < 24:
        return 'Los'
    else:
        return 'Karanlik'

# Işık durumuna göre sağlıklı hayvanların beklenen hareket hızı (px/sn)
LIGHT_MOTION_TARGETS = {
    'Aydinlik': 5.0,
    'Los': 2.5,
    'Karanlik': 0.8
}

# ------------------------------------------------------------------------------
# 1) SENTETİK "VİDEO FRAME" VE METRİK ÜRETECİ
# ------------------------------------------------------------------------------
def generate_positions(hour_idx, cluster_fraction=0.0, cluster_cells=None):
    cell_indices = np.zeros(N_CHICKENS, dtype=int)
    n_clustered = int(N_CHICKENS * cluster_fraction)

    if cluster_cells is not None and n_clustered > 0:
        cell_indices[:n_clustered] = np.random.choice(cluster_cells, size=n_clustered)

    n_remaining = N_CHICKENS - n_clustered
    cell_indices[n_clustered:] = np.random.randint(0, N_CELLS, size=n_remaining)

    return cell_indices

def positions_to_frame(cell_indices):
    frame = np.zeros((FRAME_RES, FRAME_RES), dtype=np.float32)
    cell_px = FRAME_RES // GRID_SIZE
    counts = np.bincount(cell_indices, minlength=N_CELLS).reshape(GRID_SIZE, GRID_SIZE)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            frame[r * cell_px:(r + 1) * cell_px, c * cell_px:(c + 1) * cell_px] = counts[r, c]
    return frame

def compute_shannon_entropy(cell_indices):
    counts = np.bincount(cell_indices, minlength=N_CELLS)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))

def compute_optical_flow_motion(frame_t, frame_t1, target_motion):
    frame_diff = np.abs(frame_t1.astype(np.float32) - frame_t.astype(np.float32))
    flow_variation = np.tanh((frame_diff.mean() - frame_diff.mean()) / 1.0) 
    motion_index = target_motion + flow_variation + np.random.normal(0, 0.15)
    return max(motion_index, 0.0)

# ------------------------------------------------------------------------------
# 2) 48 SAATLİK SİMÜLASYON DÖNGÜSÜ
# ------------------------------------------------------------------------------
hours = np.arange(1, TOTAL_HOURS + 1)
motion_series = np.zeros(TOTAL_HOURS)
entropy_series = np.zeros(TOTAL_HOURS)
light_states = [get_light_state(h) for h in hours]

CLUSTER_CELLS = np.array([12, 13, 22, 23])

# Hastalık döneminde hareket ve yığılma oranları (Saat 25-48 arası)
sick_motion_multiplier = np.linspace(1.0, 0.15, TOTAL_HOURS - HEALTHY_HOURS)
sick_cluster_fractions = np.linspace(0.0, 0.95, TOTAL_HOURS - HEALTHY_HOURS)

for i in range(TOTAL_HOURS):
    current_light = light_states[i]
    
    if i < HEALTHY_HOURS:
        target_motion = LIGHT_MOTION_TARGETS[current_light]
        cluster_fraction = 0.0
    else:
        idx = i - HEALTHY_HOURS
        # Hastalık durumunda hareket ışık ne olursa olsun düşer
        target_motion = LIGHT_MOTION_TARGETS[current_light] * sick_motion_multiplier[idx]
        cluster_fraction = sick_cluster_fractions[idx]

    pos_t  = generate_positions(i, cluster_fraction, CLUSTER_CELLS)
    pos_t1 = generate_positions(i, cluster_fraction, CLUSTER_CELLS)

    frame_t  = positions_to_frame(pos_t)
    frame_t1 = positions_to_frame(pos_t1)

    motion_series[i]  = compute_optical_flow_motion(frame_t, frame_t1, target_motion)
    entropy_series[i] = compute_shannon_entropy(pos_t)

# ------------------------------------------------------------------------------
# 3) BAĞLAMSAL BAZ ÇİZGİ (CONTEXT-AWARE BASELINE) HESAPLAMASI
# ------------------------------------------------------------------------------
thresholds = {}
for state in ['Aydinlik', 'Los', 'Karanlik']:
    # Sadece sağlıklı dönemin ilgili ışık durumundaki indekslerini al
    state_indices = [idx for idx, (h, l) in enumerate(zip(hours[:HEALTHY_HOURS], light_states[:HEALTHY_HOURS])) if l == state]
    
    if state_indices:
        state_motion = motion_series[state_indices]
        state_entropy = entropy_series[state_indices]
        
        # μ - 2σ formülü
        m_thresh = state_motion.mean() - 2 * state_motion.std()
        e_thresh = state_entropy.mean() - 2 * state_entropy.std()
        
        thresholds[state] = {'motion': m_thresh, 'entropy': e_thresh}

print("=" * 70)
print("DİNAMİK EŞİK DEĞERLERİ (Işık Durumuna Göre Koşullu)")
print("=" * 70)
for state, t in thresholds.items():
    print(f"[{state}] Hareket Eşiği: {t['motion']:.2f} | Entropi Eşiği: {t['entropy']:.2f}")
print("=" * 70)

# ------------------------------------------------------------------------------
# 4) ALARM MEKANİZMASI (KALICILIK VE ÇİFT SİNYAL FÜZYONU)
# ------------------------------------------------------------------------------
print("\nALARM GÜNLÜĞÜ:")
consecutive_breaches = 0
first_alarm_hour = None
alarm_signals = np.zeros(TOTAL_HOURS)

for i in range(TOTAL_HOURS):
    current_light = light_states[i]
    m_thresh = thresholds[current_light]['motion']
    e_thresh = thresholds[current_light]['entropy']
    
    motion_breach  = motion_series[i] < m_thresh
    entropy_breach = entropy_series[i] < e_thresh
    
    # Çift Sinyal Füzyonu (Sensor Fusion)
    if motion_breach and entropy_breach:
        consecutive_breaches += 1
    else:
        # Kalıcılık kesintiye uğradıysa sayacı sıfırla (Sliding window mantığı)
        consecutive_breaches = 0
        
    # Kalıcılık Kriteri (Persistence)
    if consecutive_breaches >= PERSISTENCE_N:
        alarm_signals[i] = 1
        hour_label = hours[i]
        if first_alarm_hour is None:
            first_alarm_hour = hour_label
            print(f"  🔴 DANGER: Outbreak Detected at Hour {hour_label}! "
                  f"({PERSISTENCE_N} saatlik ardışık ihlal doğrulandı)")

if first_alarm_hour is None:
    print("  ✅ Sistem genelinde alarm tetiklenmedi.")

# ------------------------------------------------------------------------------
# 5) GÖRSELLEŞTİRME
# ------------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

alarm_start = first_alarm_hour if first_alarm_hour is not None else TOTAL_HOURS + 1

# Dinamik eşikleri çizim için array'e çevir
m_thresh_series = [thresholds[l]['motion'] for l in light_states]
e_thresh_series = [thresholds[l]['entropy'] for l in light_states]

ax1.plot(hours, motion_series, color="#1f77b4", marker="o", markersize=4, label="Hareket İndeksi")
ax1.plot(hours, m_thresh_series, color="black", linestyle="--", drawstyle="steps-mid", alpha=0.7, label="Dinamik Eşik (Işığa Göre)")
if first_alarm_hour is not None:
    ax1.axvspan(alarm_start, TOTAL_HOURS, color="red", alpha=0.15, label="Alarm Aktif")
ax1.set_title("Zamansal Hareket Azalması", fontsize=12, fontweight="bold")
ax1.set_xlabel("Saat")
ax1.set_ylabel("Hareket İndeksi (px/sn)")
ax1.legend(loc="upper right")
ax1.grid(alpha=0.3)

ax2.plot(hours, entropy_series, color="#2ca02c", marker="o", markersize=4, label="Shannon Entropisi")
ax2.plot(hours, e_thresh_series, color="black", linestyle="--", drawstyle="steps-mid", alpha=0.7, label="Dinamik Eşik (Işığa Göre)")
if first_alarm_hour is not None:
    ax2.axvspan(alarm_start, TOTAL_HOURS, color="red", alpha=0.15, label="Alarm Aktif")
ax2.set_title("Mekansal Kümelenme (Entropi Çöküşü)", fontsize=12, fontweight="bold")
ax2.set_xlabel("Saat")
ax2.set_ylabel("Shannon Entropisi (bit)")
ax2.legend(loc="lower left")
ax2.grid(alpha=0.3)

# Işık durumlarını arka plana boyama
for i, h in enumerate(hours):
    if light_states[i] == 'Karanlik':
        ax1.axvspan(h-0.5, h+0.5, color='gray', alpha=0.2)
        ax2.axvspan(h-0.5, h+0.5, color='gray', alpha=0.2)
    elif light_states[i] == 'Los':
        ax1.axvspan(h-0.5, h+0.5, color='orange', alpha=0.1)
        ax2.axvspan(h-0.5, h+0.5, color='orange', alpha=0.1)

fig.suptitle("Akıllı Kümes - 48 Saatlik Bağlama Duyarlı Anomali Simülasyonu", fontsize=14, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("kumes_saglik_v2.png", dpi=150)
plt.show()