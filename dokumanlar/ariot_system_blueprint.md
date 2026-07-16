# ARIOT Akıllı Çiftlik Sistemi - Teknik Blueprint (Mimari Plan)

Bu belge, ARIOT Akıllı Kümes Yönetim Sisteminin (Faz 2) tam mimari yapısını, kullanılan algoritmaları, fizik motorunu ve yapay zeka modüllerini detaylandırmaktadır. Bu dökümanı satış görüşmelerinde, teknik sunumlarda ve gelecek geliştirme planlarında referans olarak kullanabilirsiniz.

---

## 1. Genel Sistem Mimarisi

Sistem, modern ve ölçeklenebilir bir **Mikroservis (Docker)** mimarisi üzerine inşa edilmiştir.

*   **Veritabanı (PostgreSQL):** Tüm sensör verilerini (`IoTData`) ve çiftlik ayarlarını (`FarmSettings`) kalıcı olarak saklar.
*   **Mesajlaşma Kuyruğu (Eclipse Mosquitto MQTT):** Sensörlerden gelen anlık yüksek frekanslı verilerin (telemetri) milisaniyeler içinde sisteme akmasını sağlar.
*   **Web API (FastAPI):** Veritabanı okumaları, biyolojik/finansal hesaplamalar ve arayüze veri aktarımı (SSE/Polling) işlerini yönetir.
*   **Arayüz (Frontend):** HTML, CSS ve Vanilla JS ile yazılmış, hızlı, duyarlı ve canlı verileri gösteren bir kontrol paneli.

---

## 2. Simülasyon ve Fizik Motoru (`mock_mqtt.py`)

Çiftlikte henüz gerçek sensörler takılı olmadığı için, sistemin test edilebilmesi adına dünyadaki en gelişmiş "Kümes Termodinamiği ve Gaz Dinamiği" fizik motorlarından biri kodlanmıştır.

*   **Termodinamik Kütle Dengesi:** Dışarıdaki hava sıcaklığı, fanların hızı, hayvanların yaydığı vücut ısısı ve ısıtıcıların gücü hesaplanarak kümes içindeki ısı artışı/azalışı simüle edilir (Joule/kgK cinsinden).
*   **Gaz Dinamiği (NH3 ve CO2):** Hayvan sayısına bağlı olarak saniyede üretilen amonyak ve karbondioksit hesaplanır. Fanlar çalıştığında, havalandırma kapasitesine (m³/h) göre bu gazların tahliyesi matematiksel olarak simüle edilir.
*   **Kör Nokta (Dead Zone) Simülasyonu:** Kümesin `zone-3` bölgesinde kasıtlı olarak %20'lik bir hava akımı kaybı (`zone_vent_efficiency = 0.8`) yaratılmıştır. Bu sayede yapay zekanın "homojen olmayan" kümes şartlarında (köşelerde biriken gazlar) nasıl tepki vereceği kanıtlanmıştır.

---

## 3. Biyoloji ve Finans Motoru (`core/biology.py`)

Bu modül, sadece sensör verilerini okumakla kalmaz; bu verilerin tavuğun bedeninde ve çiftçinin cebinde ne anlama geldiğini uluslararası akademik makalelere (CIGR, Wathes 2002) dayanarak hesaplar.

*   **Rüzgar Soğutma (Wind Chill) Etkisi:** Hava sıcak olsa bile fanlar çalıştığında rüzgarın tavuklar üzerindeki üşütücü etkisi hesaplanır (`t_eff`).
*   **Yem Dönüşüm Oranı (FCR) Kaybı:** Sıcaklık > 25°C veya Amonyak > 25 ppm olduğunda, hayvanların stresten dolayı yediği yemi ete dönüştürememesi hesaplanır ve TL cinsinden maliyeti çıkarılır.
*   **Ölüm (Mortality) Riski:** Aşırı sıcaklık ve CO2 (Ascites riski) durumunda saatlik ölüm ihtimalleri hesaplanır.
*   **EPEF (Avrupa Üretim Verimlilik Faktörü):** Sürünün genel sağlığı ve karlılığı standart bir puana dönüştürülür (Hedef: 300+).

---

## 4. Sanal Operatör Yapay Zekası (`mock_scada_controller.py`)

Geleneksel termostatların aksine sistemimiz **MPC (Model Predictive Control - Model Öngörülü Kontrol)** kullanır. Sistemin "Beyni" bu dosyadır.

### Çalışma Mantığı:
1.  **Geleceği Simüle Et:** Olası tüm cihaz kombinasyonlarını (Fanlar 0'dan 10'a kadar, Isıtıcılar kapalı/açık, Soğutma petekleri kapalı/açık) sanal olarak 5 dakika ileri sararak dener.
2.  **Ceza Puanlaması:** Her senaryo için ceza kesilir:
    *   *Amonyak Cezası:* NH3 25 ppm'i aşarsa feci ceza (Fanları açmaya zorlar).
    *   *Ölümcül Soğuk Cezası:* Rüzgar etkisiyle hissedilen sıcaklık 15°C'nin altına inerse ceza (Fanları kapatmaya veya ısıtıcı açmaya zorlar).
    *   *CO2 ve Nem Cezası:* CO2 > 2500 ppm veya RH > %70 ise ceza (Havalandırmaya zorlar).
    *   *Enerji Cezası:* Elektrik yakmamak için minik bir ceza (Sistemi tasarrufa zorlar).
3.  **Optimum Karar:** En az "ceza" puanını alan cihaz kombinasyonunu seçer ve SCADA sistemine (rölelere) komut gönderir.

---

## 5. Veri Akışı ve Tetikleme Zinciri (Data Flow)

1.  `mock_mqtt.py` -> Gerçek dünya fiziğini işletir ve MQTT sunucusuna (örn: `farm/sensors/zone-1`) veri gönderir (Her saniye).
2.  `core/mqtt_listener.py` -> Bu verileri anında alır ve PostgreSQL veritabanına yazar.
3.  `api/main.py` -> Veritabanındaki en güncel değerleri (`max` ve `avg` algoritmalarıyla) alır. Dış ortam hava durumunu (`OpenMeteo`) çeker.
4.  `api/main.py` -> Verileri `core/biology.py` modülüne yollayarak riskleri (FCR kaybı, üşüme vb.) hesaplatır.
5.  `mock_scada_controller.py` -> Tüm verileri alıp yapay zeka süzgecinden geçirerek fanlara ve ısıtıcılara müdahale eder.
6.  `frontend/` -> Kullanıcı arayüzü `/api/dashboard/live` adresinden bu büyük paketi alarak ekrandaki grafikleri ve uyarıları günceller.

---

## Sonuç ve Satış Argümanı
Bu mimari basit bir IoT (Sensör okuma) projesi değildir. Hayvan fizyolojisi, termodinamik fizik kuralları ve Model Predictive Control (Yapay Zeka) algoritmalarının birleştiği **Otonom bir Karar Destek Sistemidir**. Sistem, amonyağı tahliye etmek için fan açtığında yaşanacak ısı düşüşünü önceden öngörüp aynı anda ısıtıcıları ateşleyebilecek kadar ileri bir analitik zekaya sahiptir.
