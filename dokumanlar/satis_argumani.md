# ARIOT - Yapay Zeka Destekli Akıllı Kümes Asistanı 🐓💡

Tavukçuluk sadece yem verip beklemek değildir. Havalandırma hatası, amonyak birikmesi veya görünmez bir sıcaklık stresi, binlerce liralık yem israfına ve ölümlere sebep olabilir. **ARIOT**, kümesinizi sadece izlemekle kalmaz; size **kâr ettirecek aksiyonları söyleyen dijital bir çiftlik müdürü** gibi çalışır.

---

## 1. Program Nereye Bakar? (Hangi Verileri Toplar?)

ARIOT, kümesin dört bir yanına yerleştirilen akıllı sensörler sayesinde kümesinizin nabzını tutar:

- 🌡️ **Sıcaklık ve Nem:** Sadece tek bir noktaya değil, kümesin farklı bölgelerine (ön, orta, arka) bakarak hayvanların **gerçekte hissettiği** sıcaklığı (rüzgar soğutma etkisiyle birlikte) hesaplar.
- 💨 **Zehirli Gazlar (Amonyak ve Karbondioksit):** Kümesin altlığından (litter) yükselen ve hayvanı zehirleyerek gelişimini durduran amonyak (NH3) ve boğucu CO2 gazlarını ölçer.
- ⛅ **Dış Hava Durumu:** Dışarıdaki anlık hava durumunu internetten çeker ve içerideki durumla kıyaslar.
- 🐔 **Sürü Bilgileri:** Baktığınız tavuğun ırkına (Ross 308, Cobb 500, Yumurtacı vb.), yaşına, mevcut sayısına ve güncel ağırlığına bakar.
- ⚙️ **Fiziksel Kapasite:** Kümesin ebatlarını ve mevcut fanlarınızın toplam havalandırma kapasitesini (m³/saat) bilir.

---

## 2. Program Ne Yapar? (Nasıl Düşünür?)

Program, sensörlerden gelen bu verileri alır ve arka planda çalışan **Yapay Zeka Karar Motoruna** sokar. Bu motor, dünyanın en iyi üreticilerinin kullandığı "Yönetim Kılavuzları"nı ezbere bilir.

- **Irka Özel Davranır:** İçeride Cobb 500 etlik piliç mi var, yoksa Lohmann Brown yumurtacı tavuk mu? Hayvanın türüne ve tam olarak kaç günlük olduğuna göre "Şu an bu hayvanın tam olarak X dereceye ihtiyacı var" der.
- **Rüzgar Soğutmasını Anlar:** Termometre 28°C gösteriyor olabilir, ancak fanlar son hız çalışıyorsa hayvan o rüzgarda üşüyor (22°C hissediyor) olabilir. ARIOT bunu fark eder ve sizi uyarır.
- **Homojenliği Kontrol Eder:** "Kümesin ön tarafı serin ama arka taraftaki hayvanlar sıcaktan bunalmış" diyerek bölgesel sorunları tespit eder.

---

## 3. Neleri Hesapar? (Gizli Zararları Nasıl Bulur?)

Çiftçinin gözden kaçırabileceği "gizli para kayıplarını" saniye saniye hesaplar:

- 💰 **Stres Kaynaklı Yem İsrafı (FCR Kaybı):** Hayvan sıcaktan veya amonyaktan strese girdiğinde yem yemeye devam eder ama *bunu ete çeviremez*. Program, "Stres yüzünden hayvan yemi boşa harcıyor, dünden beri şu kadar TL zarar ettiniz" diye anlık hesap yapar.
- ☠️ **Teorik Ölüm Riski:** İçerideki hava koşullarının hayvanın kalbini veya solunumunu ne kadar zorladığını hesaplar ve "Bu şartlar devam ederse x saat içinde toplu ölümler başlayabilir" riskini ölçer.
- 📉 **Sürü Başarı Puanı (EPEF):** Etlik tavuklar için kârlılığın en büyük göstergesi olan EPEF puanını canlı olarak hesaplar. "Şu anki gidişatla kesime giderseniz performansınız ne olur?" sorusunu cevaplar.

---

## 4. Çıktı Olarak Ne Verir? (Ekranda Ne Görürsünüz?)

Sizi karmaşık grafiklere boğmaz. Direkt olarak **ne yapmanız gerektiğini** söyler:

> [!CAUTION]
> **Acil Aksiyon Reçetesi (Alarmlar)**
> - *"Arka bölgede Amonyak zehirlenme sınırını geçti. Altlık ıslaklığını kontrol et ve acil 2 fan daha aç!"*
> - *"Dış hava çok soğuk ve fanlar açık. İçerideki hayvanlar donmak üzere, ısıtıcıları devreye al ve fanları kıs!"*
> - *"Hedef sıcaklık 22°C olmalı ama hayvanlar 26°C hissediyor. Soğutma peteklerini (Pad) çalıştır."*

> [!TIP]
> **Canlı Finans ve Performans Tablosu**
> - **Toplam Zarar Sayacı:** Kötü havalandırma sebebiyle çöpe giden yemin ve ölen hayvanların toplam TL karşılığını gösterir. (Cüzdanınızı korur).
> - **Sürü Durumu:** "Şu an Büyüme (Grow-out) fazındasınız, hayvanlarınız gayet rahat, sistem kusursuz çalışıyor" gibi rahatlatıcı durum özetleri verir.

---

### Neden ARIOT'a Yatırım Yapmalısınız?

Eskiden kümesi "hissederek" yönetiyordunuz. Artık ARIOT ile **sayılarla ve verilerle** yöneteceksiniz.

1 saatlik geç fark edilen bir havalandırma hatasının sebep olacağı yem israfı (FCR bozulması) veya hayvan ölümü, ARIOT sisteminin kendi maliyetini fazlasıyla aşar. ARIOT; hatayı olmadan önce öngören, stresten kaynaklı yem israfını durduran ve günün sonunda üreticinin cebine doğrudan nakit kazandıran, **yorulmak bilmeyen akıllı bir dijital asistandır.**
