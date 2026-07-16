# Alarm Geçmişi (Alarm History) Ekleme

Bu plan, SCADA ve Biyolojik modeller tarafından üretilen alarmların, durum normale döndükten sonra da "Geçmiş Alarmlar" (History) olarak görüntülenebilmesini sağlayacak geliştirmeleri içerir.

## User Review Required

> [!IMPORTANT]
> Veritabanı modeline yeni bir tablo (`AlarmHistory`) eklenecektir. Uygulama bir kez yeniden başlatıldığında tablo otomatik oluşacaktır.

## Proposed Changes

### Database Layer

#### [MODIFY] [models.py](file:///d:/Antigravity/tavuk/database/models.py)
- `AlarmHistory` sınıfı (tablosu) eklenecek.
  - `id` (Integer, Primary Key)
  - `timestamp` (DateTime, Default Now)
  - `type` (String: warning, danger, critical)
  - `title` (String)
  - `desc` (String)

### API Layer

#### [MODIFY] [main.py](file:///d:/Antigravity/tavuk/api/main.py)
- Başlangıçta veritabanı tablolarının yaratılması adımlarına yeni tablonun dahil edildiğinden emin olunacak.
- `/api/dashboard/live` endpoint'inde:
  - Üretilen `actions` (alarmlar) kontrol edilecek.
  - Eğer `type` değeri 'warning', 'danger' veya 'critical' ise ve son 30 dakika içinde aynı `title` ile bir alarm kaydedilmemişse, veritabanına eklenecek (Spam engelleme mekanizması).
- Yeni Endpoint: `/api/dashboard/alarms` 
  - Son 50 geçmiş alarmı JSON olarak dönecek.

### Frontend Layer

#### [MODIFY] [index.html](file:///d:/Antigravity/tavuk/frontend/templates/index.html)
- Canlı uyarılar kısmının altına veya yanına, "Son Alarmlar" (Recent Alarms) şeklinde kaydırılabilir (scrollable) bir liste eklenecek.
- Veya estetik bir "Alarm Geçmişi" butonu ile açılan bir Modal tasarlanacak (Arayüz karmaşasını engellemek için).

#### [MODIFY] [main.js](file:///d:/Antigravity/tavuk/frontend/static/js/main.js)
- `fetchAlarms()` adında yeni bir asenkron fonksiyon eklenecek.
- Bu fonksiyon her 30 saniyede bir çağrılarak geçmiş alarmları UI'da güncelleyecek.

## Verification Plan

### Automated Tests
- Gerekli görülürse test senaryosu çalıştırılacak.

### Manual Verification
- Arayüzden Alarm Geçmişi Modal'ı / Bölümü kontrol edilecek.
- Geçmiş kayıtların veritabanında spam yaratıp yaratmadığına (deduplication) loglardan bakılacak.
