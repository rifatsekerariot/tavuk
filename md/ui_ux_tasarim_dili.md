# ARIOT - Kurumsal Çiftlik Kontrol Merkezi UI/UX Tasarım Dili ve Teknolojileri

Bu doküman, ARIOT projesi için uygulanan kullanıcı arayüzü (UI) ve kullanıcı deneyimi (UX) tasarım felsefesini, kullanılan teknolojileri ve yapılan görsel geliştirmeleri özetlemektedir.

## 1. Kullanılan Teknolojiler

Arayüzün hızlı, duyarlı (responsive) ve veri yoğunluklu olmasına rağmen akıcı çalışabilmesi için aşağıdaki modern web teknolojileri tercih edilmiştir:

- **HTML5 & Vanilla JavaScript**: Hafiflik ve maksimum performans için herhangi bir ağır framework (React/Vue vb.) kullanılmadan, standart JS standartları kullanılarak geliştirilmiştir.
- **TailwindCSS (CDN)**: Hızlı prototipleme ve utility-first (fayda odaklı) CSS yapılandırması için kullanılmıştır. Tasarım dilinin tutarlı olması sağlanmıştır.
- **ApexCharts**: Sensör geçmişini ve veri grafiklerini interaktif ve performanslı bir şekilde görselleştirmek için tercih edilmiştir.
- **Leaflet JS**: Tesisin coğrafi konumunu ve hava durumu bağlamını harita üzerinde göstermek için kullanılmıştır.
- **Google Fonts**: Modern tipografi için **Inter** (metinler) ve **JetBrains Mono** (rakamlar ve sensör verileri) kullanılmıştır.

## 2. Tasarım Felsefesi ve UI (Kullanıcı Arayüzü) Detayları

Tasarımda **"Kurumsal Endüstriyel (Solid Industrial)"** bir yaklaşım benimsenmiştir. Çiftlik yöneticilerinin kafa karışıklığı yaşamadan yüzlerce veriyi aynı anda okuyabilmesi hedeflenmiştir.

### Renk Paleti (Color Palette)
- **Zemin Rengi:** `#F7F3EA` (Saman/Krem Zemin) - Göz yormayan, çiftlik konseptine uygun organik bir sıcaklık.
- **Vurgu Renkleri:** `#2D3B2E` (Toprak Yeşili) - Organik, kurumsal ve ciddi bir vurgu rengi.
- **Panel Zeminleri:** `#ffffff` (Saf Beyaz) - Zeminle kontrast yaratarak verilerin okunabilirliğini artırır.
- **Uyarı Renkleri:** Standart tehlike/uyarı renkleri (Kırmızı, Turuncu) sadece acil müdahale gereken durumlarda dikkat çekmek için ayrılmıştır.

### Tipografi ve Okunabilirlik
- Veri gösterge panellerinde (dashboard), rakamlar değiştiğinde genişlikten dolayı arayüzün titremesini (jitter) engellemek adına **JetBrains Mono** monospace fontu `tabular-nums` (tablo rakamları) ayarıyla birlikte kullanılmıştır.
- Açıklama, etiket ve metinlerde ise son derece temiz ve modern olan **Inter** fontu tercih edilmiştir.

### Form ve Çerçeveler
- Paneller ince gri bir çerçeve (`border: 1px solid #d1d5db`) ve çok yumuşak bir gölge (`box-shadow: 0 1px 2px rgba(0,0,0,0.05)`) ile belirginleştirilmiştir. Bu sayede "cam (glassmorphism)" veya aşırı modern tasarım akımları yerine, endüstriyel olarak güven veren **katı (solid)** bir tasarım oluşturulmuştur.

## 3. UX (Kullanıcı Deneyimi) ve Etkileşimler

Kullanıcının sistemin canlı olduğunu hissetmesi ve dikkat etmesi gereken yerleri hızlıca fark etmesi için çeşitli mikro etkileşimler eklenmiştir:

- **Mikro Animasyonlar (Tick-up):** Veriler saniyede bir güncellenirken değer değiştiği anda rakam yukarı doğru zıplayıp anlık bir renk (turuncu/sarı) değiştirir. Bu `tick-up` animasyonu, kullanıcının verinin donmadığından emin olmasını sağlar.
- **Nabız (Pulse) Efektleri:** Aktif ve canlı okunan verilerin veya harita üzerindeki pinlerin yaydığı hafif nabız animasyonları (`@keyframes pulse`), sistemin gerçek zamanlı olarak çalıştığı algısını pekiştirir.
- **Modüler Yapı (Modal):** Sistem konfigürasyonları ve raporlar (Settings, EPEF Report) ana ekranı terk etmeden bir Modal (katman) içerisinde açılır. Böylece kullanıcının bağlamı (context) kaybetmemesi sağlanır.
- **Yapay Zeka Asistanı Geri Bildirimi:** Uyarılar doğrudan panonun (dashboard) tepesinde organik cümlelerle belirir. Teknik terimler (Örn: "Outlier Sapması") yerine, doğrudan kullanıcının ne yapması gerektiğini anlatan direktifler ("Lütfen cihazı kontrol edin") kullanılarak çiftçi dostu bir UX sağlanmıştır.
