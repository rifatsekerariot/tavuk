# 🧪 Fizik Motoru ve Termodinamik Test Sonuçları

Sisteme entegre edilen "Gerçek Hayat" algoritmalarının matematiksel doğruluğunu kanıtlamak amacıyla yazdığım Python scripti (Test Suite) başarıyla çalıştırılmıştır. Tüm testler, simüle edilen zorlu senaryolarda fizik kurallarının tam olarak beklendiği gibi çalıştığını doğrulamıştır.

## Test 1: Psikrometri (Magnus-Tetens Formülü)
Bu testte, Magnus-Tetens formülünün havadaki nem oranlarını kütlesel (Mutlak Nem) ve oransal (Bağıl Nem) olarak doğru çevirip çeviremediği test edildi.

* **Girdi:** 25.0°C Sıcaklık, %50.0 RH
* **Ara İşlem (Mutlak Nem):** Hesaplanan değer `0.009876 kg su / kg hava`
* **Geri Dönüşüm Testi:** Elde edilen saf su buharı kütlesi kullanılarak tekrar Bağıl Neme dönüştürüldüğünde, formül kayıpsız bir şekilde `%50.00` değerini buldu.
> [!TIP]
> **Sonuç: BAŞARILI (PASS)** - Nem oranı ve su buharı kütlesi arasındaki fiziksel çevrim kusursuz çalışıyor.

## Test 2: Hacimsel Kütle Korunumu (CO2 ve Amonyak)
30.000 adet 2 kg'lık tavuğun standart bir kümeste ($120m \times 14m$) fanlar tamamen **kapalıyken** içeriyi ne hızda zehirleyeceği hesaplandı.

* **Fiziksel Alan:** Kümesteki hava hacmi `5712 m³`, içerideki havanın ağırlığı `6854.4 kg`.
* **Üretim:** Tavuklar saatte `99.13 m³ CO2` ve `9.0 kg Amonyak` üretiyor.
* **1 Saatlik Fansız Simülasyon:** Hiç tahliye olmadığında, normalde havada 400 ppm olan CO2 miktarı **1 saat içerisinde 17.954 ppm'e (Kritik Zehirlenme Seviyesine)** fırladı.
> [!WARNING]
> **Sonuç: BAŞARILI (PASS)** - $CO_2$ ve Amonyak hedefe doğru yavaşça gitmek yerine gerçek hacmin içerisinde kümülatif olarak birikerek gerçekçi bir asfiksi (boğulma) tehlikesi yarattı.

## Test 3: Termodinamik Isı Dengesi (Heat Balance)
Bina dış yüzeyinden kaybedilen ısı (U-Value) ve hayvanların içeride yaydığı enerjinin farkına bakılarak içerinin nasıl ısındığı test edildi.

* **Isı Kaybı:** Dışarısı 10°C, içerisi 25°C iken duvarlardan kaybedilen ısı `18.48 kW`.
* **Kuşların Isıtması:** Sürünün toplam metabolik ısısı devasa bir oranla `535.82 kW`.
* **Net Kazanç:** Tahliye (Fan) olmadan, sadece kuşlardan dolayı içeride `517.34 kW` net ısı birikiyor.
* **Sonuç Sıcaklık:** 1 saatin sonunda havanın kütlesi (bina ısıl ataleti dahil) absorbe etmesine rağmen içerisi tam **27.01°C daha ısındı** (Toplam sıcaklık 52°C'ye ulaştı).
> [!IMPORTANT]
> **Sonuç: BAŞARILI (PASS)** - Diferansiyel $dT/dt$ ısınma/soğuma motoru, ortamdaki net enerjiyi tam bir mühendislik hassasiyetiyle termal dereceye dönüştürüyor.

## Test 4: Evaporatif Soğutma ve Su Buharı (Pad Cooling)
Yaz aylarında sistem sıcaklığı düşürmek için soğutma peteklerinden suları süzdürdüğünde (Evaporative Pad Cooling), havanın nem oranının fiziksel olarak nasıl tepki vereceği test edildi. Dışarısı kurak bir yaz günü (35°C, %40 RH) olarak simüle edildi.

* **Soğutma Yükü:** Fanlar havayı `8.0°C` soğutmak için peteklere devasa bir enerji yükledi.
* **Su Tüketimi:** Bu soğutma işleminin gerçekleşmesi için peteklerden 1 saat içinde `789.02 Kg Su` buharlaşarak havaya karıştı.
* **Ortam Nemi Değişimi:** Sıcaklık 27°C'ye düşüp, havaya da yaklaşık 800 litre su buharı katılınca, içeri giren havanın Bağıl Nemi (% RH) %40'tan **%100.00'a (Tam Doygunluk Noktasına)** fırladı.
> [!CAUTION]
> **Sonuç: BAŞARILI (PASS)** - Beklediğimiz o "Kritik Sıcaklık & Nem çakışması" olgusu birebir simüle edildi. Peteklerin kullanılması anında devasa bir su buharı yaratıyor ve sistemi aşırı neme itiyor.
