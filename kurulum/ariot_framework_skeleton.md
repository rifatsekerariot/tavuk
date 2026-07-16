# ARIOT Framework Skeleton & Documentation
Bu doküman, başka bir Yapay Zeka ajanı (AI IDE, Kod Asistanı vs.) veya bir yazılımcı tarafından bu projenin sıfırdan oluşturulması, modifiye edilmesi veya tamamen farklı bir endüstriye (örneğin sera, fabrika, depo) bir "iskelet" olarak uyarlanması için hazırlanmış KESİN, GERÇEK ve KOD BAZLI bir veri bankasıdır.

Bu framework'ün ana felsefesi şudur: **Sensör Verisi → Kural Motoru (Rule Engine) → Finansal Zarar (₺) Çevirisi → Canlı Arayüz (Live Push) → Dijital İkiz / Demo Simülasyonu**

---

## 1. Kullanılan Teknolojiler (Tech Stack)

* **Arka Yüz (Backend):** `Python 3.10+`, `FastAPI` (Asenkron API ve WebSockets destekli).
* **Veritabanı:** `PostgreSQL` (Kalıcı veri) ve `SQLAlchemy` ORM.
* **İletişim Protokolü:** `MQTT` (Mosquitto Broker). Hem gerçek sensörlerle hem de sanal cihazlarla düşük gecikmeli haberleşme.
* **Gerçek Zamanlı Akış (Real-time):** `WebSockets` (Frontend'e polling yaptırmadan sunucu tarafında veri oluştukça push etmek için).
* **Ön Yüz (Frontend):** Saf `Vanilla JavaScript`, `HTML5`, `TailwindCSS` (Stil ve tasarım), `ApexCharts` (Dinamik zaman serisi grafikleri).
* **Altyapı ve Dağıtım:** `Docker`, `docker-compose`. `Paramiko` kütüphanesiyle yazılmış özel deploy betikleri.

---

## 2. Sistemin Çalışma Şekli (Architecture Flow)

Sistem tamamen olay güdümlü (event-driven) çalışır:
1. **Veri Üretimi:** Fiziksel donanım (veya `mock_sensor`) MQTT üzerinden `farm/sensors` kanalına sıcaklık ve gaz verilerini basar.
2. **Dinleme ve Kayıt:** Arka planda çalışan `mqtt_listener.py` bu veriyi yakalar, JSON'dan parse eder ve doğrudan `PostgreSQL` veritabanına yazar.
3. **Akıllı Karar:** Frontend, WebSocket üzerinden FastAPI'ye bağlandığında, API veritabanındaki en güncel veriyi çeker ve `biology.py` içindeki Kural Motoru'na (Rule Engine) sokar.
4. **Finansallaştırma:** Kural motoru sadece "Sıcaklık yüksek" demez. "Sıcaklık 32 derece olduğu için tavuk strese girdi, yem israf oldu, bu durumun sana günlük maliyeti ₺18.50" şeklinde iş (business) modeline çevirir.
5. **Canlı Gösterim:** Hesaplanan bu finansal veriler, biyolojik indeksler (EPEF) ve alınması gereken aksiyonlar JSON'a çevrilip WebSocket üzerinden tarayıcıya "Push" edilir. Frontend DOM'u anında günceller.

---

## 3. Hangi Modül Ne İşe Yarar? (Directory Structure)

* **`core/mqtt_listener.py`:** MQTT Broker'a abone olan arka plan (background worker) dosyasıdır. Gelen sensör loglarını DB'ye yazar. *Dikkat: Kendi içinde `db = SessionLocal()` açar ve `finally` bloğunda kapatır.*
* **`core/biology.py`:** Sistemin "Beyni"dir. Biyolojik, matematiksel ve finansal tüm kurallar buradadır.
  * *Efektif Sıcaklık:* Rüzgar hızının sıcaklığı ne kadar düşürdüğünü hesaplar (Wind chill).
  * *FCR (Yem Dönüşüm) Cezası:* Amonyak ve sıcaklığa bağlı verim düşüşü hesaplar.
  * *Finansal Zarar:* Stres altındaki hayvanın boşuna yediği yem (Feed Loss) ve ölen hayvanın zararı (Mortality Loss) hesaplanıp ₺ cinsinden döndürülür.
* **`api/main.py`:** Sistemin dış dünyaya açılan kapısıdır (REST + WebSockets). Frontend buradan beslenir. "Ayarlar", "Demo Modu", "Fire Bildirimi" gibi uç noktaları barındırır.
* **`database/models.py`:** Tablo şemalarını tutar (`IoTData`, `FarmSettings`, `AlarmHistory`).
* **`mock_mqtt.py` (Dijital İkiz):** İçerisinde gerçek bir "Termodinamik Kütle Dengesi" ve "Gaz Difüzyon" fiziği barındırır. Ortamdaki havanın ısınması/soğuması gerçeğe yakın simüle edilir. 
* **`mock_scada_controller.py`:** Sanal operatördür. Sensör verisini okur, eşikler aşılırsa otomatik fan/ısıtıcı açar ve komutu MQTT'ye (`farm/actuators`) basar.
* **`frontend/templates/index.html` & `static/js/main.js`:** Arayüz (SPA). DOM manipülasyonu, ApexCharts konfigürasyonları ve WebSockets bağlantı yönetimi burada yapılır.

---

## 4. Çözülen Kritik Sorunlar ve Dersler (Lessons Learned)

Eğer bu iskelet kullanılacaksa, geçmişte yaşanan şu ölümcül hatalardan kaçınılmalıdır:

1. **WebSocket & Veritabanı Kilidi (Connection Pool Exhaustion):**
   * *Sorun:* `api/main.py`'deki WebSocket uç noktasında (endpoint) FastAPI'nin `Depends(get_db)` yapısı kullanılmıştı. WebSocket bağlantısı saatlerce açık kaldığı için veritabanı bağlantısı havuza (pool) geri dönemedi. 15. sekmeyi açan kullanıcıdan sonra tüm sunucu (API) çöktü ve kilitlendi.
   * *Çözüm:* WebSocket uç noktasına DB enjekte edilmedi. Onun yerine `while True:` döngüsü içinde anlık olarak `db = SessionLocal()` açıldı, veri okundu ve **anında `db.close()`** ile kapatıldı.
2. **Sanal Sensörlerde (Mock) Sonsuz Arıza Anomalisi:**
   * *Sorun:* Test amaçlı konan %0.5 olasılıklı "Bozuk Sensör" kodu, bir sensörün sıcaklığını 20 derece fırlattı. Ancak ortamın termodinamik hacmi çok büyük olduğu için sensörün soğuyup normale dönmesi simülasyonda saatler aldı. 
   * *Çözüm:* Fiziksel simülasyonlarda rastgele fırlamalar eklenirken dikkat edilmeli, strict (katı) limitler kullanılmalıdır.
3. **Frontend Cache (Önbellek) Sorunu:**
   * *Sorun:* `main.js` içinde kod düzeltilip sunucuya atıldığı halde, kullanıcı tarafında butonlar çalışmadı. Çünkü tarayıcılar eski bozuk JS dosyasını önbellekte tutuyordu.
   * *Çözüm:* `index.html` içinde script yüklemelerine versiyonlama eklendi: `<script src="/static/js/main.js?v=4"></script>`. (Cache Busting)

---

## 5. İskelet Olarak (Skeleton) Sıfırdan Kullanma Rehberi

Bu projeyi örneğin bir **"Akıllı Fabrika (Endüstri 4.0)"** projesine çevirmek isteyen bir yapay zeka ajanının izlemesi gereken yol haritası:

1. **İş Modelini (Domain) Tanımla:** `database/models.py` içindeki donanım tablosunu (Örn: Makine Titreşimi, Motor Sıcaklığı, Üretilen Adet) tasarla.
2. **Kural Motorunu (Rule Engine) Uyarla:** `core/biology.py` yerine `core/factory_rules.py` yarat. Matematiksel olarak "Titreşim %10 artarsa makinenin arıza yapma riski artar, üretimin durmasının maliyeti dakikada ₺5000'dir" şeklinde finansal çeviriyi yaz.
3. **MQTT Altyapısını Kur:** Gerçek fabrikadaki PLC'lerden veri okuyacak yapıyı `mqtt_listener.py` üzerinden SQL'e bağla.
4. **Hatasız WebSocket API'si Yaz:** `api/main.py` içinde KESİNLİKLE bağlantı (connection) sızdırmayan (döngü içinde aç-kapat) WebSocket endpointi yarat.
5. **Modern Bir UI Tasarla:** Veriyi `TailwindCSS` ile premium bir arayüzde sun ve saniyelik güncellemeleri `ApexCharts` ile ekrana yansıt.

Bu yapıya birebir sadık kalındığı sürece, saniyede binlerce sensör verisini çökmeden finansal bir tabloya çevirebilen devasa sistemler inşa edilebilir.
