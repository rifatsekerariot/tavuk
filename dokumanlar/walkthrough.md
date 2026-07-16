# Alarm Geçmişi Özelliği

Yapay zeka (SCADA) tarafından üretilen kritik (kırmızı) ve uyarı (sarı) seviyesindeki olayların geriye dönük kaydedilmesi ve arayüzden takip edilmesi için **Geçmiş Alarmlar** özelliği sisteme dahil edilmiştir.

## Neler Değişti?

### 1. Veritabanı Altyapısı
- `AlarmHistory` adında yeni bir PostgreSQL tablosu eklendi.
- Her alarm kayıt altına alınırken **Tekrarlama (Spam) Koruması** devreye sokuldu. Eğer aynı başlığa sahip bir alarm son 30 dakika içerisinde zaten kaydedildiyse tekrar eklenmesi engellenerek veritabanının şişmesi (log kirliliği) önlendi.

### 2. API Servisleri
- `/api/dashboard/live` endpoint'inde Biyolojik Motorun (biology.py) döndürdüğü uyarı listesi filtrelenip veritabanına otomatik eşzamanlandı.
- Arayüzün geçmiş alarmları sorgulayabilmesi için `/api/dashboard/alarms` adlı yeni bir uç nokta oluşturuldu. Sistem son 50 kritik olayı geriye dönük listeleyebilir hale geldi.

### 3. Kullanıcı Arayüzü (Dashboard)
- "Yapay Zeka Karar Motoru" başlığının hemen yanına "Geçmiş Alarmlar" butonu eklendi.
- Butona tıklandığında açılan **Modal (Açılır Pencere)** tasarımı entegre edildi.
- Alarmın derecesine (danger, critical, warning) göre renk kodlaması kullanıldı:
  - Kritik/Tehlikeli Alarmlar: Kırmızı çerçeve
  - Uyarılar: Turuncu çerçeve
- Alarmların oluştuğu tam saatler dakika hassasiyetiyle (Örn: 2026-07-10 17:05) görüntülenebilir hale geldi.

## Doğrulama
- ✅ `models.py` başarıyla güncellendi ve tablo yapısı SQLAlchemy ile otomatik oluşturuldu.
- ✅ Ön yüz (`main.js` & `index.html`) başarıyla derlenip docker üzerinde test edildi.
- ✅ Geliştirmeler uzak sunucuya (Production) başarıyla gönderildi (deploy edildi).
