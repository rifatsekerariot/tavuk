# ARIOT Akıllı Kümes İklimlendirme ve Biyolojik Simülasyon Motoru
## Teknik Mimari ve Algoritma Dokümantasyonu

### 1. Çözülen Temel Sorun (Problem Tanımı)
Geleneksel kümes iklimlendirme sistemleri (Klasik Termostat Kontrolcüleri) yalnızca ortamdaki kuru termometre sıcaklığına odaklanır. Hayvanın yaşına, yaydığı metabolik ısıya ve rüzgarın yarattığı aerodinamik soğutma etkisine **kördür**. Bu "statik tablo" yaklaşımı, özellikle yaz aylarında veya yoğun ısı stresi anlarında fanların yanlış ya da gecikmeli çalışmasına sebep olur. Sonuç olarak:
*   Yem Dönüşüm Oranında (FCR) ciddi bozulmalar,
*   Akut ısı stresi kaynaklı toplu sürü ölümleri (Mortalite),
*   Gereksiz fan çalışmasından kaynaklanan enerji israfı meydana gelir.

**ARIOT**, kümesteki termodinamik dengeyi ve kuşların biyolojik tepkilerini saniye saniye hesaplayan **yapay zeka destekli dinamik bir fizik motorudur.** Kılavuzlardaki (örn: Ross 308) hedef standartları baz alarak, o standarda *en düşük enerji tüketimi ve en yüksek sürü verimliliğiyle* nasıl ulaşılacağını hesaplar.

---

### 2. Kullanılan Bilimsel Algoritmalar ve Biyolojik Dayanaklar

#### 2.1. Hissedilen Sıcaklık ve Rüzgar Soğutma (Wind-Chill) Modeli
Sistem ortam sıcaklığını baz almaz; kuşun **gerçekten hissettiği efektif sıcaklığı ($T_{eff}$)** hesaplar.
*   **Aerodinamik Hız:** Kümesin en, boy, mahya/saçak yüksekliği ve fan kapasiteleri alınarak, kümesteki hava akım hızı (m/s) anlık hesaplanır.
*   **UGA (University of Georgia) Formülü:** Endüstri standardı kabul edilen bu yaklaşıma göre; kuşların üzerindeki her 1 m/s'lik hava akımı, hissedilen sıcaklığı yaklaşık **2.5°C** düşürür (Maksimum etki limiti kuşların tüylenme yapısı gereği 3.0 m/s'de asimptota ulaşır).
*   **Sonuç:** Klasik sistem panosu ortamı 35°C okuyup felaket alarmı verirken; ARIOT anında devreye girip fanları maksimize eder, 3.0 m/s rüzgar yaratır ve tavukların ortamı 27.5°C olarak hissetmesini sağlayarak onları kurtarır.

#### 2.2. Yem Dönüşüm (FCR) ve Mortalite (Ölüm) Ceza Logaritmaları
*   **FCR Bozulması:** Hissedilen sıcaklık 25°C'yi geçtiği anda tavuk, solunum yoluyla soğumaya (panting) çalışırken enerjisini tüketir ve FCR bozulur. Algoritma (St-Pierre vd. araştırmalarına dayanarak), 25°C üzerindeki her 1°C'lik aşımda saatlik olarak FCR değerine $0.025/24$ oranında ceza puanı ekler.
*   **Mortalite Eğrisi:** Hissedilen sıcaklık 32°C'yi aştığında hücre düzeyinde stres başlar. Algoritmamız, 32°C eşiğinden sonra logaritmik eksponansiyel bir ölüm eğrisi çizer (Örn: $0.0005 \times e^{0.5 \times (T - 32)}$). Böylece 35°C'lik kriz anlarında saniye saniye ölecek tavuk sayısını belirler.

---

### 3. Sektörel ve Finansal Göstergeler

ARIOT simülasyonu tamamladığında elde ettiği fiziksel verileri tüm dünyanın kabul ettiği tarımsal finans indekslerine dönüştürür.

#### 3.1. EPEF (Avrupa Üretim Etkinlik Faktörü / VIG)
Sistem, klasik bir kümes ile ARIOT sisteminin performansını **EPEF (VIG)** skoru üzerinden karşılaştırır.
*   **Formül:** $EPEF = \frac{\text{Canlı Ağırlık (kg)} \times \text{Yaşama Gücü (\%)}}{\text{FCR} \times \text{Kesim Yaşı (Gün)}} \times 100$
*   Sistem, standart baz FCR'yi (örn: 1.55) baz alır. Üzerine kendi hesapladığı ısı stresi FCR cezasını ekler. Başlangıçtaki sürü sayısından, logaritmik ölüm eğrisine göre ölen hayvanları çıkartarak "Yaşama Gücü"nü bulur ve nihai skoru üretir.

#### 3.2. Gerçek Elektrik Tüketimi (kWh) Entegrasyonu
Çiftçilere gerçekçi bir "Net Tasarruf" sunmak için elektrik masrafları saklanmaz, şeffafça sürece dahil edilir:
*   Fizik motoru, hedef sıcaklığı tutturmak için çalışması gereken **"Fan-Saat"** toplamını anlık kaydeder.
*   Ortalama bir tünel fanın motor gücü (1.5 kW) ile çarpılarak **Toplam Elektrik Tüketimi (kWh)** bulunur.
*   Bu tüketim, çiftçinin girdiği "Elektrik Birim Fiyatı" ile çarpılır.

#### 3.3. Net Finansal Tasarruf Formülü
Sistemin ekrana yansıttığı o büyük TL tasarruf rakamı şu formülle kanıtlanır:
$$ \text{Net Tasarruf} = (\text{Engellenen Ölüm Parası} + \text{Engellenen Yem İsrafı Parası}) - \text{ARIOT'un Harcadığı Ekstra Fan Elektrik Parası} $$
ARIOT, tavukları yaşatmak için daha çok fan çalıştırıp 500 TL ekstra elektrik yaktırsa bile, önlediği FCR ve ölüm kaybıyla 40.000 TL kazandırarak aradaki devasa net tasarrufu ispatlar.

---

### 4. Veri Besleme (Data Feeding) ve Altyapı
*   **Gerçekçi Hava Durumu:** ARIOT, OpenMeteo uydu API'sine bağlıdır. Seçilen GPS lokasyonunun 14 günlük saatlik sıcaklık ve bağıl nem (RH) tahminini çeker. Simülasyon laboratuvarda değil, çiftçinin arazisindeki gerçek iklimde koşulur.
*   **45 Günlük Yaşam Döngüsü:** Uzun vadeli analizler için API sınırı devreden çıkarılarak, "Gün Döngüsü (Sinüs Eğrisi)" ile tam bir 45 günlük broiler yetişme periyodu test edilebilir.
*   **Termal Atalet (Tau):** Kümesin yapısal malzemesi (yalıtım) göz önünde bulundurularak, dış havanın içeriye sızma veya binanın soğuma/ısınma direnci Newton'un Soğuma Yasası entegre edilerek hesaplanır.

### Özet
ARIOT; klasik sensörlere bağlı kalarak çiftçiye sadece "içerisi çok sıcak" diyen değil, **"içerisi çok sıcak ama rüzgar hızı yaratarak ölümleri engelledim, FCR'yi düzelttim ve bu krizden seni x.000 TL net kârla çıkardım"** diyebilen, dünya standartlarında (VIG destekli) bir yapay zeka iklimlendirme mühendisi olarak tasarlanmıştır.
