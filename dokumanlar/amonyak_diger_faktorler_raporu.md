# ARIOT İleri Araştırma Raporu: Amonyak, CO2 ve Diğer Çevresel Sensör Fırsatları

ARIOT'un ısı stresi ve fan-soğutma yönetimi üzerindeki başarısını kanıtladıktan sonra, bir sonraki adım "Akıllı Kümesteki" diğer görünmez katilleri tespit edip engellemektir. Küresel üniversitelerin (Georgia Üniversitesi, Wageningen, vd.) araştırma verilerine dayalı olarak tavukçulukta optimize edilebilecek diğer hayati parametreler aşağıdadır:

## 1. Amonyak (NH3) Gazının Yönetimi

Amonyak, kümes zeminindeki dışkının ürik asidinin bakteriler tarafından parçalanmasıyla ortaya çıkar. Soğuk kış aylarında "ısıyı korumak için" havalandırmanın kısıldığı dönemlerde ölümcül seviyelere ulaşır.

> [!WARNING]
> **Kritik Eşik:** Sektör standardı ve akademik eşik **25 ppm**'dir (Milyonda 25 partikül). 50 ppm ve üzeri, sürüyü içeriden yok eder.

### Akademik Etkileri:
*   **FCR Bozulması ve Büyüme Kaybı:** Maryland ve Georgia Üniversitelerinin araştırmalarına göre; havada 50 ppm amonyak bulunması, hayvanın nihai kesim ağırlığını ortalama %5-8 oranında düşürür ve FCR'ı (Yemden Yararlanma) yaklaşık **8-10 puan** bozar. Hayvan, enerjisini büyümek yerine bağışıklık sistemini onarmaya harcar.
*   **Solunum Yolu Tahribatı:** Amonyak korozif (aşındırıcı) bir gazdır. Tavukların nefes borusundaki (trachea) mikro tüycükleri (siliaları) felç eder ve eritir. Bu da Newcastle (Yalancı Veba), Bronşit ve E.coli gibi hastalıklara davetiye çıkarır.
*   **ARIOT'a Eklenebilecek Vizyon:** Sisteme entegre edilecek bir NH3 sensörü, 25 ppm eşiği aşıldığında ısı kaybını (kışın) göze alarak dahi olsa minimum havalandırma (timer fan) periyotlarını zorla artırabilir ve akciğer tahribatını önleyebilir.

## 2. Karbondioksit (CO2) ve "Su Toplama" (Ascites) Sendromu

Tavuklar tıpkı küçük sobalar gibi oksijen yakar ve CO2 üretirler. Ayrıca kışın kümeste yanan kömür veya gaz sobaları da ciddi CO2 üretir.

> [!IMPORTANT]
> **Kritik Eşik:** Modern broiler için kabul edilen üst sınır **3.000 ppm**'dir.

### Akademik Etkileri:
*   **Ascites (Su Toplama):** Yüksek CO2 ve düşük oksijen (hipoksi) ortamında, hayvanın kalbi oksijensizliği telafi etmek için çok daha hızlı pompalamaya başlar. Bu aşırı yük, kalp yetmezliğine ve nihayetinde karın boşluğunda sıvı birikmesine (Ascites Sendromu) yol açar. Gelişimini tamamlamış (35+ gün) ve en çok et verecek ağır hayvanlar, uykularında kalp krizinden ölürler.
*   **ARIOT'a Eklenebilecek Vizyon:** CO2 seviyesi 3.000 ppm'i geçtiğinde, sistem soba arızası (karbonmonoksit sızıntısı ihtimali) veya yetersiz havalandırma uyarısı vererek taze hava sirkülasyonunu anlık başlatabilir.

## 3. Bağıl Nem (RH) ve Altlık (Litter) Kalitesi

Sıcaklığın tek başına bir anlamı olmadığı gibi (hissedilen sıcaklık önemlidir), havalandırmanın da nem kontrolü olmadan bir anlamı yoktur.

> [!NOTE]
> **Hedef Aralık:** İdeal bağıl nem %50 ile %65 arasındadır.

### Akademik Etkileri:
*   **Ayak Tabanı Yanıkları (Footpad Dermatitis - FPD):** %70 üzeri nem, altlığı ıslak ve yapışkan bir çamura dönüştürür. Islak altlıktaki yüksek amonyak ve pH, hayvanların ayak tabanlarını yakar. FPD, günümüzde kesimhanelerdeki en büyük "refah" red sebeplerinden biridir ve etin kalite sınıfını (Grade A'dan B'ye) düşürür.
*   **Göğüs Yanıkları (Breast Blisters):** Islak altlıkta yatan tavuğun göğüs etinde lezyonlar oluşur.
*   **ARIOT'a Eklenebilecek Vizyon:** İçerideki Bağıl Nem (RH) sensöründen gelen verilerle, ped (petek) pompalarının ne kadar çalışacağı sınırlandırılabilir (Şu anda sadece T_eff üzerinden soğutma yapıyoruz, gelecekte nemi de baz alarak pedi durdurabiliriz).

## 4. Aydınlatma (Işık Modülasyonu) ile Büyüme Kontrolü

Sürekli ışık altında (24 saat) bırakılan tavukların kalp ve iskelet sistemleri, devasa kas gelişimini kaldıramaz (Sudden Death Syndrome - Ani Ölüm).

### Akademik Etkileri:
*   **Aralıklı Aydınlatma:** Wageningen Üniversitesi araştırmaları, civcivlikten sonra günde 4-6 saatlik karanlık periyotlarının kemik (iskelet) yapısını güçlendirdiğini, ani kalp durmalarını azalttığını ve FCR oranını iyileştirdiğini net bir şekilde ortaya koymuştur. Işıklar kapandığında hayvanlar dinlenir ve yemi yağa/ete daha iyi dönüştürür.
*   **ARIOT'a Eklenebilecek Vizyon:** Işık sensörleri ve IoT röleleri ile ARIOT, sürünün yaşına ve ağırlığına göre otomatik bir "Karanlık-Aydınlık" dim (kısma) programı uygulayarak mortaliteyi fiziksel değil, psikolojik/metabolik olarak da çözebilir.

## Sonuç ve Stratejik Öneri
Eğer ARIOT sistemine **(1) NH3 Sensörü** ve **(2) CO2 Sensörü** donanımlarını eklerseniz, bu sistem sadece "Yaz Aylarındaki Isı Stresini" çözen bir araç olmaktan çıkar; **"Kış Aylarındaki Solunum Hastalıkları ve Amonyak Zehirlenmesini"** de çözen, 365 gün ve dört mevsim çiftçiye para kazandıran mutlak bir otomasyona dönüşür.
