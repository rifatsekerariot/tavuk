# ARIOT - Yapay Zeka Kümes Otomasyonu Matematiksel Formülasyonları

Bu dokümanda sistemin arka planında koşan simülasyon, biyolojik modelleme, termodinamik (kütle ve ısı dengesi) ve Yapay Zeka (AI) Karar Destek mekanizmasına ait tüm formülasyonlar detaylandırılmıştır.

## 1. Kütle ve Isı Dengesi (Thermodynamics & Mass Balance)
Sensör verilerinin zaman içindeki değişimi (`mock_mqtt.py` içinde hesaplanır), kapalı sistem kütle dengesi (Mass Balance) prensibine göre çalışır.

### Hacim ve Hava Kütlesi
- Ortalama Çatı Yüksekliği: $H_{mean} = \text{Eaves\_H} + \frac{\text{Ridge\_H} - \text{Eaves\_H}}{2}$
- Kümes Hacmi: $V_{m^3} = W \times L \times H_{mean}$
- Havanın Kütlesi: $m_{air\_kg} = V_{m^3} \times 1.2$  (Havanın yoğunluğu $\approx 1.2 \text{ kg}/m^3$)

### Sıcaklık Değişimi ($\Delta T$)
Kümes içi sıcaklık, kazandırılan ve kaybedilen ısıların net farkına göre hesaplanır (Kütle Isı Transferi):
- Üretilen Toplam Isı (Sensible Heat): $Q_{gain} = (\text{Canlı Hayvan} \times \text{Isı}_{\text{hayvan}}) + \text{Isıtıcılar}_W$
- Havalandırma ile Kaybedilen Isı: $Q_{vent} = \text{HacimselDebi}_{m^3/h} \times 1.2 \times \frac{1006}{3600} \times (T_{in} - T_{out})$
- Yüzeylerden/Duvarlardan Kaybedilen Isı: $Q_{wall} = \text{Alan}_{m^2} \times U_{value} \times (T_{in} - T_{out})$
- Sicaklık Değişim Formülü: 
  $\Delta T = \frac{(Q_{gain} - Q_{vent} - Q_{wall} - Q_{cool}) \times (\Delta t_{saat} \times 3600)}{m_{air} \times C_p \times 10}$ 
 *(Not: Binanın termal kütlesi, havanın yaklaşık 10 katı olarak alınmıştır)*

### Amonyak (NH3) Üretim Modeli
Amonyak kuru ortamda azken, nemli (ıslak altlık) ortamda eksponansiyel artar.
- Taban Üretim: $NH3_{base\_mg/h} = \text{Hayvan Sayısı} \times 300 \text{ mg/h} \times \text{Aktivite Oranı}$
- Nem Etkisi Faktörü: $RH_{factor} = e^{\frac{RH - 55}{15}}$
- Gerçek Üretim: $NH3_{prod} = NH3_{base} \times RH_{factor}$
- Difüzyon ve Tahliye (Mass Balance): $\Delta NH3 = (NH3_{prod} - NH3_{vent}) \times \Delta t$

### Karbondioksit (CO2) Üretim Modeli
Tavukların ısı üretimine bağlı olarak CIGR(2002) standartlarına göre hesaplanır.
- $CO2_{prod\_m^3/h} = \left(\frac{Q_{gain}}{1000}\right) \times 0.185$
- Hacimsel derişime çevrilerek havalandırma ile seyreltilir.

---

## 2. Biyolojik ve Büyüme Modelleri (Biology & Growth)
Sürünün yaşına, ağırlığına ve maruz kaldığı strese göre biyolojik değişkenler (`physics.py` / `biology.py` içinde) modellenmiştir.

### Canlı Ağırlık Büyüme Eğrisi (Broiler Ross 308)
- $A\text{ğı}rl\text{ı}k_{kg} = \text{Başlangıç} + (0.015 \times \text{Yaş}) + (0.0012 \times \text{Yaş}^2)$

### Hedef İdeal Sıcaklık (Aviagen Standartları)
- Broiler için: $T_{target} = \max(20.0,\; 33.0 - (\text{Yaş} \times 0.371))$
- Yumurtacı için: $T_{target} = \max(21.0,\; 33.0 - (\text{Yaş} \times 0.34))$

### Rüzgar Etkisi (Wind Chill) ve Hissedilen Sıcaklık
Tünel havalandırmasında fanların oluşturduğu rüzgar hızı sıcaklığı düşürür:
- Ortalama Hava Hızı: $v_{m/s} = \frac{\text{Aktif Fanlar} \times \text{Fan Kapasitesi}}{\text{Kesit Alanı} \times 3600}$
- Soğutma Etkisi: $T_{windchill} = \min(v_{m/s}, 3.0) \times 2.5$
- Hissedilen Sıcaklık: $T_{eff} = T_{in} - T_{windchill}$

---

## 3. Performans ve Verimlilik Parametreleri

### Yem Dönüşüm Oranı (FCR) ve Stres Cezaları (Penalties)
Hayvanların sıcak ve amonyak stresinde büyüme durur, yem dönüşümü (FCR) bozulur.
- Isı Stresi Cezası ($T_{eff} > T_{target} + 0.5$): 
  $\Delta FCR_{heat} = \frac{(T_{eff} - T_{target} - 0.5) \times 0.025}{24}$
- Amonyak Stresi Cezası ($NH3 > 25\text{ppm}$): 
  $\Delta FCR_{nh3} = \frac{(NH3 - 25) \times 0.001}{24}$
- Final FCR = $FCR_{base} + \Delta FCR_{heat} + \Delta FCR_{nh3} + FCR_{historical\_dead}$

### Avrupa Üretim Verimlilik Faktörü (EPEF)
Bir tavuk sürüsünün uluslararası başarı puanıdır. Yem maliyeti ve büyüme oranının kesişimidir.
- EPEF = $\frac{(\text{Ortalama Ağırlık}_{kg} \times \text{Canlılık Oranı}_\%)}{FCR \times \text{Kesim Yaşı}} \times 100$

### Ölüm Riski (Mortality Risk - Wathes et al.)
- Sıcaklığa bağlı Asites / Kalp Krizi Oranı ($T_{eff} > 32^\circ C$): 
  $Mort_{heat} = 0.0005 \times e^{0.5 \times (T_{eff} - 32)}$
- Yüksek Karbondioksit Zehirlenmesi ($CO2 > 3000\text{ppm}$):
  $Mort_{co2} = 0.0001 \times \left(\frac{CO2 - 3000}{1000}\right)$

---

## 4. Yapay Zeka Karar Optimizasyon Formülü (Reward Function)
Sistemin beynindeki SCADA denetleyicisi (`mock_scada_controller.py`), mevcut koşullara göre kârı (profit) maksimize etmeyi, finansal zararı (cost) minimize etmeyi amaçlar.

### Maliyet (Cost) Fonksiyonu
$C_{toplam} = C_{enerji} + C_{yem\_israfi} + C_{olum\_kaybi} + C_{islak\_altlik} + C_{co2\_stresi} + C_{fan\_amortisman}$

1. $C_{enerji} = \text{KwH} \times \text{Birim Fiyat}$ (Klima ve Fan maliyeti)
2. $C_{yem\_israfi} = \text{Toplam Hayvan} \times (\Delta FCR) \times A\text{ğı}rl\text{ı}k \times \text{Yem Fiyatı}$ (Strese bağlı yenilen ama ete dönüşmeyen yemin maddi kaybı)
3. $C_{olum\_kaybi} = \text{Beklenen Ölüm Oranı} \times A\text{ğı}rl\text{ı}k \times \text{Et Fiyatı}$
4. $C_{islak\_altlik} = \max(0, RH - 70) \times 0.5$ (Fungal tedavi maliyeti projeksiyonu)
5. $C_{co2\_stresi} = \max(0, CO2 - 1500) \times 0.02$ (Gizli stres cezası)

**Hedef:** Yapay zeka, $Reward = -C_{toplam}$ fonksiyonunu en yüksek (sıfıra en yakın) yapacak olan `[fan_sayısı, isitici_w, pad_cooling]` kombinasyonunu seçerek donanıma komut gönderir.
