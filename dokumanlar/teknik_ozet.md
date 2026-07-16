# Akıllı Kümes Sağlık Takip Sistemi - Teknik Özet

Bu belge, `tavuk` klasöründe yer alan Akıllı Kümes Sürü Sağlığı Takip Sistemi'nin teknik mimarisini ve çalışma prensiplerini özetlemektedir. Proje, bilgisayarlı görü (computer vision) ve veri bilimi teknikleri kullanılarak sürünün davranışsal analizini yapar.

## 1. Sistem Mimarisi

Proje iki temel bileşenden oluşmaktadır:
- **Gerçek Zamanlı Web Uygulaması (`app.py`, `tracker.py`):** Yüklenen video akışları üzerinden kare (frame) bazlı analiz yapan Flask tabanlı sunucu.
- **Simülasyon Modülü (`kumes_saglik_simulasyonu.py`):** Işık ve zaman bağlamını dikkate alarak 48 saatlik sentetik sürü verisi (sağlıklı vs hastalıklı) üreten ve alarm algoritmalarını test eden NumPy destekli Python betiği.

## 2. Kullanılan Teknolojiler

- **Python & Flask:** Web arayüzünün sunumu ve video yükleme / akış (streaming) işlemleri.
- **YOLO (`best.pt`):** Kümesteki tavukları tanımak üzere proje için özel olarak eğitilmiş (custom trained) derin öğrenme modeli.
- **OpenCV (`cv2`):** Video karelerinin okunması, gri tonlamaya çevrilmesi ve görüntü üzerine çıktıların (bounding box, metin, kırmızı alarm filtresi) çizilmesi.
- **NumPy & Matplotlib:** Simülasyon modülünde matris işlemleri, istatistiksel hesaplamalar ve sonuçların görselleştirilmesi.

## 3. Algoritma ve Metrik Hesaplamaları (`tracker.py`)

Sistem sürü sağlığını iki temel metrik üzerinden ölçer:

### A. Hareket İndeksi (Motion Index)
Sürünün genel hareketliliğini ölçer.
- Ardışık iki kare arasındaki piksel farkları (`cv2.absdiff(curr_frame_gray, prev_frame_gray)`) alınır.
- Elde edilen fark matrisinin ortalaması (mean) **Hareket İndeksi** olarak kabul edilir. Hastalık durumunda sürünün yavaşlaması veya durması beklenir.

### B. Shannon Entropisi (Mekansal Dağılım)
Sürünün kümes içerisine ne kadar homojen dağıldığını ölçer.
- YOLO'dan gelen sınırlayıcı kutuların (bounding boxes) merkez noktaları hesaplanır.
- Kümes alanı sanal bir 10x10 grid (ızgara) yapısına bölünür.
- Tavukların hangi grid hücrelerinde yoğunlaştığı bulanarak bir olasılık dağılımı ($p$) elde edilir.
- Standart **Shannon Entropisi formülü** ($- \sum p \cdot \log_2(p)$) ile dağılım skoru hesaplanır. Hayvanların bir köşeye yığılması entropiyi düşürür.

## 4. Anomali Tespiti ve Alarm Karar Mekanizması

Yanlış alarmları (False Positive) önlemek için **Üç Katmanlı Filtre Mimarisi** kullanılır:

1. **Çift Sinyal Füzyonu (Dual Signal Fusion):** Anomali ihlalinin sayılabilmesi için hem hareketliliğin belirlenen eşiğin (`MOTION_THRESHOLD`) altına düşmesi hem de entropinin yığılma eşiğinin (`ENTROPY_THRESHOLD`) altına düşmesi **eş zamanlı** olarak gerçekleşmelidir.
2. **Kalıcılık Kriteri (Persistence Window):** İhlalin sadece anlık değil, ardışık olarak `PERSISTENCE_N` kare (veya simülasyonda N saat) boyunca devam etmesi durumunda sistem gerçek **"ALARM"** durumuna geçer.
3. **Bağlama Duyarlılık (Simülasyon Modülünde):** Eşik değerleri sabit değildir; aydınlatma rejimine (Aydınlık, Loş, Karanlık) göre referans veri (baseline) üzerinden dinamik hesaplanır ( $\mu - 2\sigma$ formülü ile).

## 5. Çıktı

- Sağlıklı durumda video üzerinde yeşil yazıyla izleme istatistikleri ve "STATUS: HEALTHY" mesajı verilir.
- Alarm durumunda video akışının üzerine kırmızı bir filtre (`cv2.addWeighted` ile) basılır ve "ALARM! OUTBREAK DETECTED!" uyarısı yansıtılır.

## 6. Performans Optimizasyonu (Frame Skipping)
Görüntü işleme sürecindeki CPU/GPU yükünü azaltmak ve FPS'i artırmak amacıyla **Frame Atlama (Frame Skipping)** mekanizması uygulanmıştır. 
- YOLO nesne tespiti, entropi ve hareket indeks hesaplamaları **her 3 karede 1 defa** çalıştırılır. 
- Aradaki işlenmeyen karelerde, son hesaplanan bounding box (sınırlayıcı kutular) ve metrikler ekranda gösterilmeye devam ederek akıcı bir video deneyimi sağlanır.
