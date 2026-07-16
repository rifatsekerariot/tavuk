# 🌍 1 Yıllık (8 Dönem) Yapay Zeka Optimizasyon Simülasyonu

**Toplam Sürü:** 8 Dönem
**Dönem Başına Süre:** 45 Gün
**Yıllık Ortalama Yaşama Oranı:** %99.84

## Dönem (Flock) Bazlı Sonuçlar
| Dönem | Mevsim | Yaşama Oranı (%) | EPEF Puanı | Elektrik (Fan) | Isınma (Gaz/Kwh) |
|-------|--------|------------------|------------|----------------|------------------|
| 1 | Bahar | %99.83 | 398 | 6802 kWh | 169000 kWh |
| 2 | Yaz | %99.95 | 399 | 12851 kWh | 79000 kWh |
| 3 | Yaz | %99.95 | 399 | 14583 kWh | 48250 kWh |
| 4 | Yaz | %99.95 | 399 | 12851 kWh | 79000 kWh |
| 5 | Bahar | %99.83 | 398 | 6802 kWh | 169000 kWh |
| 6 | Kış | %99.93 | 399 | 3404 kWh | 204750 kWh |
| 7 | Kış | %99.34 | 396 | 2733 kWh | 212500 kWh |
| 8 | Kış | %99.93 | 399 | 3404 kWh | 204750 kWh |

## 🧠 Analiz Sonucu
Yapay Zeka (MPC) algoritması, dışarıdaki aşırı yaz sıcaklıkları ve kış donlarına rağmen tavukları **%99.84** başarı oranıyla yaşatmayı başarmıştır. Maliyet fonksiyonundaki (Ölüm Cezası) ağırlığı sayesinde, algoritma kışın ısıtıcı faturalarından kaçınmamış, yazın ise fanları maksimum kapasitede kullanarak ısı stresini tamamen önlemiştir.