# Tavuk Kümesi SCADA ve Biyolojik Karar Destek Sistemi

Bu sistem, tavuk kümeslerinin havalandırma, ısıtma, nem ve evaporatif soğutma (ped) sistemlerini termodinamik ve biyolojik modelleme kuralları çerçevesinde optimize eden akıllı bir SCADA ve karar destek yazılımıdır.

## Temel Özellikler

1. **Evaporatif Soğutma Ped Teşhisi**:
   - ASHRAE ve ASABE standartlarında Doygunluk Verimi ($\eta_{sat}$) hesabı.
   - Su pompası durumu ile kireçlenme (Scaling) veya kuru bölge (Dry Channeling) tespiti ve hedef iç sıcaklık kalibrasyonu.
2. **Biyolojik Modelleme (Wathes & Kristensen)**:
   - Rüzgar Soğutma (Wind Chill) etkisiyle hissedilen sıcaklık ($T_{eff}$) hesabı.
   - Amonyak ($NH_3$) ve karbondioksit ($CO_2$) birikimine dayalı FCR (Yem Dönüşüm Oranı) cezası ve kritik ölüm riski modellemesi.
3. **Model Predictive Control (MPC)**:
   - 5 dakikalık adımlarla en düşük maliyetli (enerji tüketimi, yem israfı, ölüm kayıpları ve fan aşınma maliyetleri) fan, ısıtıcı ve soğutma ped durumunu seçen optimizasyon motoru.
4. **Predictive AI**:
   - 14 günlük hava tahmini verilerini analiz ederek don, termal şok, sıcaklık dalgaları veya fırtınalara karşı erken uyarı bildirimleri.

## Kurulum ve Çalıştırma

### Bağımlılıkların Yüklenmesi
```bash
pip install -r requirements.txt
```

### Testleri Çalıştırma
```bash
python -m unittest test_algorithms.py test_scada.py
```
