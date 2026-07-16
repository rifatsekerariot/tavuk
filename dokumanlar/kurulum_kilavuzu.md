# ARIOT Çoklu Sensör Kurulum Kılavuzu (100x16m Etlik Piliç Kümesi)

Akademik literatür (Aviagen, Cobb ve çevre kontrol makaleleri) referans alınarak, 100 metre uzunluk ve 16 metre genişliğindeki standart bir endüstriyel broiler (etlik piliç) kümesinde çevresel faktörlerin doğru okunabilmesi için sensör yerleşim standartları aşağıda listelenmiştir.

## 1. Optimum Sensör Sayısı ve Bölgeleme (Zoning)
Tek sensör kullanımı, kümes içindeki mikroklima farklılıklarını (soğuk/sıcak noktalar) gizlediği için modern tesislerde terk edilmiştir.
*   **Önerilen Sensör Sayısı:** **6 Adet**
*   **Bölgeleme:** Kümes uzunlamasına 6 sanal bölgeye (zone) ayrılmalıdır. (Her 16-17 metrede bir sensör grubu).

## 2. Sensör Konumlandırma Stratejisi (Yerleşim Planı)

> [!WARNING]
> **Orta Hat (Centerline) Hatası:** Tüm sensörleri kümesin tam ortasından geçen bir çizgi üzerine hizalamayın! Orta hat, hava akışının en stabil olduğu yerdir. Sensörlerin en az yarısı, ısı stresinin ve yalıtım kayıplarının ilk başladığı kenar duvarlara (sidewalls) yakın yerleştirilmelidir.

**Örnek Zig-Zag Yerleşim Modeli:**
1.  **Zone 1 (Giriş/Ped Bölgesi):** Padlerden (soğutma peteği) 10 metre içeride, sol duvara 4 metre mesafede.
2.  **Zone 2:** 25. metrede, sağ duvara 4 metre mesafede.
3.  **Zone 3 (Orta Alan):** 45. metrede, tam ortada (centerline).
4.  **Zone 4:** 60. metrede, sol duvara 4 metre mesafede.
5.  **Zone 5:** 75. metrede, sağ duvara 4 metre mesafede.
6.  **Zone 6 (Egzoz/Fan Bölgesi):** Fanlardan 10 metre önce, tam ortada.

## 3. Sensör Yüksekliği

> [!IMPORTANT]
> **Yükseklik Kuralı:** Sensörler her zaman hayvanın maruz kaldığı havayı ölçecek seviyede olmalıdır. Çatıya asılan sensörler yanlış sıcaklık okumasına neden olur.
*   **Civciv Dönemi:** Altlıktan (litter) 15 cm yukarıda.
*   **Yetişkin Dönemi:** Altlıktan 30 cm yukarıda (kuşlar büyüdükçe sensör kablosu/askısı ayarlanmalıdır).

## 4. Isıtıcı ve Hava Akımı Etkisi
*   Sensörler, radyan ısıtıcıların (brooder) tam altına veya doğrudan ısı vuran alanlara konulmamalıdır. (Yanıltıcı yüksek sıcaklık okuması). Isıtıcılardan en az 2.5 - 3 metre yatay uzaklıkta olmalıdır.
*   Taze hava girişlerinin (inlet) veya soğutma peteklerinin (pad) doğrudan üzerine üflediği noktalardan kaçınılmalıdır.

## 5. Yeni Yazılımın Karar Mekanizması Nasıl Çalışır?
Yeni ARIOT DSS yazılımı, bu 6 sensörden gelen verileri şu şekilde işler:
*   **Varyans Uyarıları (Delta T):** Sensörler arasındaki maksimum sıcaklık ile minimum sıcaklık farkı 3°C'yi aşarsa sistem *"Kötü Hava Dağılımı"* uyarısı fırlatır ve sirkülasyon fanlarının çalışmasını talep eder.
*   **Amonyak ve Zehirli Gazlar:** Gaz verilerinde sistem ortalama almaz! Eğer 5 sensörde amonyak 10 ppm, ancak Zone-3'te 30 ppm ise, sistem ortalamaya (13 ppm) güvenip susmaz; doğrudan Zone-3 için **Kritik Amonyak** uyarısı üretir.
