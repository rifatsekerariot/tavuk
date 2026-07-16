window.realWeatherData = null;

document.addEventListener('DOMContentLoaded', () => {
    // Basic Leaflet Map Setup with Spotify Color Palette compatible tiles
    const map = L.map('map').setView([39.92077, 32.85411], 5); // Default: Turkey center

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OSM',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    let marker = L.marker([39.92077, 32.85411]).addTo(map);

    const statusEl = document.getElementById('weather-status');

    map.on('click', async function(e) {
        marker.setLatLng(e.latlng);
        const lat = e.latlng.lat.toFixed(4);
        const lng = e.latlng.lng.toFixed(4);
        
        statusEl.innerHTML = `<span class="animate-pulse">Open-Meteo'dan veriler çekiliyor...</span>`;
        statusEl.className = "text-center font-bold text-sm bg-spotify/20 text-spotify rounded-full py-2 px-4 transition-all duration-300";

        // Yüklenmesi istenen gün sayısı
        const requestedDays = parseInt(document.getElementById('sim_days').value) || 3;
        
        if (requestedDays > 14) {
            statusEl.innerHTML = `Uyarı: Gerçek hava durumu en fazla 14 günlük çekilebilir. 45 günlük simülasyonlar için lütfen Manuel "Gün Döngüsü" seçin!`;
            statusEl.className = "text-center font-bold text-sm bg-amber-100 text-amber-700 rounded-full py-2 px-4 transition-all duration-300 pop-in";
            return; // Çıkış yap, api hatası almamak için
        }
        
        const days = requestedDays;

        try {
            // Open-Meteo API Call
            const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&hourly=temperature_2m,relative_humidity_2m&forecast_days=${days}`);
            if(!response.ok) throw new Error("API Hatası");
            
            const data = await response.json();
            
            window.realWeatherData = {
                t_out: data.hourly.temperature_2m,
                rh_out: data.hourly.relative_humidity_2m
            };

            // Calculate simple averages for display
            const avgT = (data.hourly.temperature_2m.reduce((a,b)=>a+b,0) / data.hourly.temperature_2m.length).toFixed(1);
            
            statusEl.innerHTML = `📍 Konum Seçildi! Ort. Sıcaklık: ${avgT}°C (Gerçek Veriler Kullanılacak)`;
            statusEl.className = "text-center font-bold text-sm bg-green-100 text-green-700 rounded-full py-2 px-4 transition-all duration-300 pop-in";
            
            // Gizle manuel hava durumu panelini
            document.getElementById('manual-weather-container').style.display = 'none';

        } catch (error) {
            statusEl.innerHTML = `Hata! Veri Çekilemedi.`;
            statusEl.className = "text-center font-bold text-sm bg-red-100 text-red-700 rounded-full py-2 px-4 transition-all duration-300";
            window.realWeatherData = null;
        }
    });
});
