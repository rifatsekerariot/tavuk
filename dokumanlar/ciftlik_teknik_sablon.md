# ARIOT - Akıllı Çiftlik Karar Destek Sistemi (Teknik Mimari ve Geliştirme Şablonu)

Bu doküman, projeyi inceleyecek veya üzerine yeni özellikler/fikirler geliştirecek olan bir Yapay Zeka (AI) veya yazılımcı için hazırlanmış teknik bir "Blueprint" (Şablon) niteliğindedir. Sistemin nasıl çalıştığını, hangi teknolojilerin kullanıldığını ve biyolojik/finansal algoritmaların mantığını içerir.

---

## 1. Projenin Amacı ve Özeti
ARIOT, endüstriyel kümes hayvancılığı (Etlik/Broiler ve Yumurtacı) yapan tesisler için geliştirilmiş, IoT (Nesnelerin İnterneti) tabanlı gerçek zamanlı bir "Biyolojik ve Finansal Karar Destek Sistemi"dir. 
Kümes içindeki sıcaklık, nem, karbondioksit (CO2) ve amonyak (NH3) verilerini okuyarak, hayvanların hissettiği fizyolojik stresi matematiksel olarak hesaplar. Bu stresi doğrudan TL/Dolar cinsinden finansal zarara çevirir ve çiftçiye anlık olarak "Aksiyon Reçeteleri" (Fanları aç, ısıtıcıyı kapat vb.) sunar.

## 2. Kullanılan Teknoloji Yığını (Tech Stack)
- **Backend (Sunucu):** Python 3.11, FastAPI, Uvicorn
- **Veritabanı:** PostgreSQL (SQLAlchemy ORM ile)
- **IoT Haberleşme:** Eclipse Mosquitto (MQTT Protokolü)
- **Frontend (Arayüz):** HTML5, Vanilla JavaScript, Tailwind CSS (Responsive, Glassmorphism UI), ApexCharts (Zaman serisi grafikleri)
- **Dış Veri Kaynakları:** OpenMeteo API (Açık hava durumu ve rüzgar hızı tespiti)
- **Altyapı & Dağıtım:** Docker, Docker Compose, Nginx (Reverse Proxy), Paramiko ile Remote SSH Deploy

---

## 3. Veritabanı Mimarisi (Data Models)
Sistem iki ana tablo üzerinde koşar:
1. **`FarmSettings` (Kümes Ayarları):** 
   - Kümesin kapasitesi, tavuk cinsi (Ross 308, Cobb 500 vb.), başlangıç sayısı, fan kapasiteleri, sensör adetleri.
   - Ekonomik veriler: Yem kilo fiyatı, Et kilo fiyatı, Elektrik kW fiyatı.
2. **`IoTData` (Zaman Serisi Sensör Verileri):**
   - Saniyede/Dakikada bir gelen veriler.
   - `zone_id` (Bölge numarası, örn: zone-1, zone-2), `t_in` (Sıcaklık), `rh_in` (Nem), `co2_ppm`, `nh3_ppm`, `timestamp`.

---

## 4. Çekirdek Algoritmalar (Biyoloji ve Finans Motoru `biology.py`)
Sistemin beyni olan bu modül, sensörden gelen ham verileri bilimsel formüllerle işler:

- **Rüzgar Soğutma Etkisi (Wind Chill):** Toplam fan kapasitesi ve kümesin kesit alanından hava hızı hesaplanır. Bu hız, okunan sıcaklıktan düşülerek tavuğun "Gerçekte Hissettiği Sıcaklık" (`t_eff`) bulunur.
- **FCR (Yem Dönüşüm Oranı) Bozulması:** Hissedilen sıcaklık 25°C'yi geçtiğinde veya Amonyak (NH3) 25ppm'i aştığında tavuklar yemi ete dönüştüremez. *Kristensen & Wathes (2000)* standartlarına göre günlük ekstra yem tüketimi hesaplanır.
- **Mortalite (Ölüm) Riski:** CO2 miktarı 3000ppm'i geçtiğinde Asit (Ascites) sendromu riski artar. Hissedilen sıcaklık 32°C'yi geçtiğinde kalp krizi riski üstel olarak (*Wathes et al., 2002*) artar. Sistem teorik ölüm sayısını hesaplar.
- **Finansal Zarar:** FCR bozulmasından kaynaklanan boşa giden yem (kg) güncel yem fiyatı ile; ölen tavukların et kaybı ise güncel et fiyatı ile çarpılarak "Günlük Toplam Kümülatif Zarar (TL)" olarak ekrana yansıtılır.
- **EPEF (European Production Efficiency Factor):** Sürünün genel sağlık ve başarı puanı matematiksel olarak güncel verilerden hesaplanır.

---

## 5. Uygulama İçi API Endpoint'leri
- `GET /api/dashboard/live`: Uygulamanın anlık kalbidir. Veritabanındaki en son sensör verilerini alır, 24 saatlik geçmişi çeker, `biology.py` üzerinden geçirir ve Front-End'e (UI) hesaplanmış zararları, EPEF'i, OpenMeteo verilerini, Yapay Zeka uyarılarını ve **Zone (bölge) bazlı güncel sensör okumalarını** JSON olarak döner.
- `GET /api/dashboard/history`: Belirli bir zaman aralığındaki (1 saat, 24 saat, 7 gün vb.) atmosferik ve gaz yoğunluk verilerini grafik çizdirilmesi için Front-End'e iletir.
- `POST /api/settings` & `POST /api/mortality`: Kullanıcı konfigürasyonlarını ve fire kayıtlarını sisteme işler.

---

## 6. Frontend Mimarisi ve Son Yapılan UI/UX Geliştirmeleri
- **SCADA / Endüstriyel Tasarım:** Uygulama "Admin Template" veya standart SaaS kalıplarından tamamen çıkartılarak gerçek bir operasyon odası (Control Room) hiyerarşisine oturtulmuştur. Zemin rengi saman/krem tonunda (`#F7F3EA`), vurgular toprak yeşilidir (`#2D3B2E`).
- **Veri Tipografisi ve Borsa Hissi (Ticker):** Bütün metrik değerlerinde sayılarının alt alta kusursuz hizalanması için `tabular-nums` destekli JetBrains Mono fontu kullanılır. Veriler IoT üzerinden (5 sn'de bir) güncellendiğinde rakamlar hafif bir animasyonla "Tick" atar.
- **Hiyerarşik Metrik Düzeni:** Eşit kartlardan oluşan sıkıcı yapı kırılarak; sol tarafa devasa boyutlu bir "Kümülatif Finansal Risk" paneli yerleştirilmiş (arkasında zarar ivmesini gösteren sparkline bulunur), diğer biyolojik veriler (EPEF, Yem İsrafı) yan tarafa şerit şeklinde dizilmiştir.
- **İmza Öğe (Yaşam Döngüsü Çizelgesi):** Ekranın en üstünde, hayvanların Brooding (0-10), Growing (11-30) ve Finishing (31-45) evrelerini ve güncel durumu gösteren tam genişlikte yatay bir timeline şeridi bulunur.
- **İkonografi ve Zaman Serisi Grafikleri:** Grafik alanlarının yüksekliği artırılarak sayfanın tam merkezine (aksiyon kartlarının üstüne) konumlandırılmıştır. Grafiğin arka planına "İdeal Sıcaklık Hedefi" gölgeli bir bant (annotation) olarak eklenir. Aksiyon reçetelerinde jenerik emojiler yerine trend okları kullanılır.
- **Landing Page ve Pazarlama Motoru:** Sistemin ana sayfasında dinamik bir fiyat hesaplama algoritması çalışır ve girilen kümes verilerine göre hesaplanan sensör konfigürasyonları doğrudan **WhatsApp** üzerinden şirkete iletilir.

---

## Yeni Bir Yapay Zekaya Yönelik Prompt / Fikir İsteme Talimatı
*Bu şablonu kopyalayıp başka bir AI modeline şu sözlerle verebilirsiniz:*

> "Yukarıda ARIOT adındaki akıllı kümes karar destek sisteminin teknik detayları yer alıyor. Sistemdeki sensör verisi toplama, biyolojik stres hesaplama ve finansal analiz altyapısı bu şekilde çalışıyor. Bu mimariyi göz önünde bulundurarak;
> 1. Bu sisteme ekleyebileceğim yeni ve yenilikçi özellikler neler olabilir? 
> 2. Gelecekte sensör yelpazesini genişletmek istesem hangi donanımları eklemeliyim ve bu donanımlar yazılım tarafındaki finansal tahminleme algoritmamı nasıl geliştirir?
> 3. Çiftçilerin kullanımını (engagement) artırmak için Gamification (oyunlaştırma) veya bildirim mekanizmaları açısından neler kurgulayabilirim?
> Lütfen teknik altyapımı bozmadan bana vizyon katacak fikirler üret."
