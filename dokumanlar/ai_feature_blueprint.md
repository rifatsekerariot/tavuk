# ARIOT Yapay Zeka Özellik (Feature) Şablonu ve Sistem Mimarisi

Bu doküman, sisteme eklenen yapay zeka (AI) destekli karar mekanizmaları, matematiksel algoritmalar, kullanılan teknolojiler ve mimari süreçler için referans bir şablondur. Yeni bir biyolojik metrik, operasyonel alarm veya arayüz özelliği ekleneceği zaman buradaki standartlara uyulmalıdır.

## 1. Kullanılan Teknolojiler ve Mimari

ARIOT sistemi uçtan uca modern bir teknoloji yığını ile çalışır:

- **Arka Yüz (Backend):** Python tabanlı `FastAPI` (REST API ve WebSockets destekli).
- **Veritabanı:** `PostgreSQL` (Veri kalıcılığı) ve `SQLAlchemy` ORM.
- **İletişim Protokolü:** `MQTT` (Mosquitto Broker) ile sensörler (Publisher) ve SCADA ekranları (Subscriber) arası gerçek zamanlı veri akışı.
- **Canlı Veri Akışı (Real-time Push):** `WebSockets` kullanılarak HTTP pooling yükünden kaçınılır ve canlı veriler saniyenin onda biri hızında UI tarafına "push" edilir.
- **Ön Yüz (Frontend):** Saf Vanilla `JavaScript`, CSS Framework olarak `TailwindCSS` ve grafikleştirme için `ApexCharts`.
- **Konteynerleştirme ve Dağıtım:** `Docker` ve `docker-compose`. 
- **CI/CD ve Dağıtım Araçları:** SSH üzerinden doğrudan güncelleme atan özel `Paramiko` destekli Python betikleri (`deploy_ui.py`, `deploy_backend.py` vb.).

## 2. Biyolojik Karar Motoru (Rule Engine)

Tüm mantıksal hesaplamalar ve tavsiye metinleri `core/biology.py` içindeki `calculate_biology_and_finance` fonksiyonunda ele alınır. 

### 2.1 Çevresel Risk (Isı ve Gaz) Formülleri
* **Efektif Sıcaklık (Wind Chill):** $T_{eff} = T_{hava} - (V_{rüzgar} \times 2.5)$
* **Amonyak (NH3) Riski:** Sınır değer 25 ppm. Kristensen & Wathes (2000) standartlarına göre 25 ppm üzerindeki her 1 ppm'lik artış, günlük $0.001$ FCR (Yem Dönüşüm Oranı) cezası olarak yansır.
* **CO2 Riski:** Sınır değer 3000 ppm. 3000 ppm üzerindeki CO2 konsantrasyonu solunum sorunlarına ve asites riskine yol açar. Saatlik asites katsayısı $0.0001 \times \frac{CO_2 - 3000}{1000}$ şeklindedir.

### 2.2 Finansal Kayıp (Financial Loss) Hesaplamaları
Sistem, çevresel koşulların tavuk üzerinde yarattığı stresi finansal bir zarara dönüştürerek çiftlik sahibine gösterir.
* **Fire Kaybı (Mortality Loss):** `Toplam Ölü Tavuk × Ortalama Tavuk Ağırlığı (kg) × Et Satış Fiyatı (₺/kg)`
* **Yem Zayiatı (Feed Loss):** İki bileşeni vardır:
    1. **Stres Kaynaklı Yem İsrafı:** Kötü havalandırma (Yüksek ısı, CO2, NH3) yüzünden hayvanın metabolizması bozulur, yediği yemi ete çeviremez. Formül: `Hayatta Kalan Tavuk × FCR Cezasından Doğan Ekstra Yem × Yem Fiyatı`
    2. **Ölen Hayvanın Tükettiği Yem:** Ölen bir hayvan ölene kadar belli bir yem yemiştir ve bu yem artık ete dönüşmeyeceği için zarardır. Formül: `Ölen Tavuk Sayısı × Yaşına Göre Yediği Yem × Yem Fiyatı`
* **Enerji Maliyeti:** `Tüketilen Elektrik (kWh) × Elektrik Birim Fiyatı (₺/kWh)`

### 2.3 EPEF (European Production Efficiency Factor)
Avrupa Üretim Verimlilik Faktörü şu formülle hesaplanır:
$$EPEF = \frac{\text{Canlı Ağırlık (kg)} \times \text{Yaşama Gücü (\%)}}{\text{FCR (Yem Dönüşüm Oranı)} \times \text{Kesim Yaşı (Gün)}} \times 100$$
*Örnek:* 2.5 kg ağırlık, %95 yaşama gücü, 1.6 FCR ve 40 gün yaş için: `(2.5 * 95) / (1.6 * 40) * 100 = 371.0`

## 3. Akıllı SCADA ve Demo Modu Mimarisi

* **Demo Modu:** Sisteme demo_mode parametresi eklendiğinde (`FarmSettings.demo_mode`), ön yüz veya arka yüz, fiziksel MQTT sensörlerinin verisini beklemek yerine yapay veri üreticiye yetki verir.
* **Durum (State) Yönetimi:** Demo durumu API üzerinden `/api/settings` aracılığıyla veritabanına kaydedilir (`demo_mode: True/False`). Tarayıcı yenilense bile durum (state) veritabanında saklandığı için sistemin Demo/Canlı akış dengesi korunur.

## 4. Fiziksel Simülasyon (Termodinamik Motor) - `mock_mqtt.py`

Sistemi test edebilmek için gerçek sensörlerden veri alıyormuş gibi davranan bağımsız bir Docker konteyneri (`mock_sensor`) yazılmıştır. 

### Fiziksel Tepki Modeli
Eğer SCADA ekranından veya Sanal Operatörden (Dijital İkiz) fanlar açılırsa, simülatör şu matematiksel kuralı uygular:
* *Havalandırma (Fanlar) Artarsa:* İçerideki ısı $T$, Amonyak $NH_3$ ve Karbondioksit $CO_2$ parabolik bir şekilde düşüşe geçer. Formül: $Z_{yeni} = Z_{hedef} + (Z_{hedef} - Z_{mevcut}) \times 0.1$
* *Isıtıcı (Heater) Açılırsa:* İçerideki ısı hızla yükselir. 

> [!IMPORTANT]
> **Simülasyon Sınırları:** Demo modunda veya simülasyonda sistem kendi kendine "otomatik tavuk ölümü" üretmemelidir (Çünkü ölüm kalıcı bir zarardır ve demo anında kullanıcıya yanlış panik yaratır). `mock_mqtt.py` artık hayvan öldürmez, ölümler sadece SCADA paneli veya gerçek dünyadaki sensör entegrasyonu ile kümülatif olarak kaydedilmelidir.

## 5. Sorun Giderme ve Güvenlik Mekanizmaları

* **Bağlantı Yönetimi (Connection Pooling):** WebSocket uç noktaları (endpoint) çalışırken SQLAlchemy veritabanı bağlantısı `while True:` döngüsünün en üstünde oluşturulup döngü sonunda `finally: db.close()` ile kapatılmalıdır. Aksi halde PostgreSQL QueuePool (Havuz) aşımı (`QueuePool limit of size 5 overflow 10 reached`) hatası meydana gelir ve tüm API çöker.
* **Önbellek (Cache) Önleme:** JS ve CSS dosyalarının güncellemelerden sonra tarayıcılarda kalmaması (stale) için HTML içindeki asset (kaynak) yüklemelerinde `?v=X` veya Timestamp (zaman damgası) içeren Cache-Buster'lar ve API çağrılarında `Cache-Control: no-cache` header'ları kullanılmalıdır.

## 6. Yeni Kural Eklerken İzlenecek Standart
Yeni bir biyolojik karar (Rule Engine) ekleneceğinde:
1. `core/biology.py` dosyasına biyolojik formülü ekleyin.
2. `actions.append(...)` formatı ile durumu JSON olarak UI'a bildirin.
3. Parametreleri güncellerken kümülatif olan (tavuk sayısı gibi) parametreler için API isteklerinde `-1` çıkarma (azaltma) yapısını kullanın.
4. Yeni kodu ekledikten sonra mutlaka WebSocket bağlantılarının leak (sızdırma) yapmadığını loglardan teyit edin.
