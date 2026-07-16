let tempRhChart, gasChart, lossSparklineChart;
let map, marker;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    fetchSettings();
    fetchHistory();
    // Start WebSocket for real-time push instead of polling
    initWebSocket();
    applyUserRole();
});

let ws;
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;
    ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        processLiveData(data);
    };
    
    ws.onclose = () => {
        setTimeout(initWebSocket, 3000); // Reconnect
    };
}

function updateValueWithTick(id, newVal) {
    const el = document.getElementById(id);
    if (!el) return;
    if (el.innerText !== String(newVal)) {
        el.innerText = newVal;
        el.classList.remove('ticking');
        void el.offsetWidth; // trigger reflow
        el.classList.add('ticking');
    }
}

function initCharts() {
    const commonOptions = {
        chart: { 
            height: 250, 
            toolbar: { show: false }, 
            animations: { enabled: true, easing: 'linear', speed: 800, dynamicAnimation: { enabled: true, speed: 350 } },
            fontFamily: 'Inter, sans-serif'
        },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2 },
        xaxis: { categories: [], labels: { style: { colors: '#64748b', fontFamily: 'JetBrains Mono, monospace', fontSize: '10px' } }, axisBorder: { color: '#cbd5e1' }, axisTicks: { color: '#cbd5e1' } },
        yaxis: { labels: { style: { colors: '#64748b', fontFamily: 'JetBrains Mono, monospace', fontSize: '10px' } } },
        grid: { show: true, borderColor: '#e2e8f0', strokeDashArray: 0, xaxis: { lines: { show: true } }, yaxis: { lines: { show: true } } },
        tooltip: { theme: 'light', style: { fontFamily: 'JetBrains Mono, monospace', fontSize: '12px' }, marker: { show: false } }
    };

    const tempRhOptions = {
        ...commonOptions,
        series: [{ name: 'Sıcaklık (°C)', data: [] }, { name: 'Nem (%)', data: [] }],
        chart: { ...commonOptions.chart, type: 'area', height: 350 },
        colors: ['#2D3B2E', '#3b82f6'],
        fill: { type: 'solid', opacity: 0.1 }
    };
    tempRhChart = new ApexCharts(document.querySelector("#chart-temp-rh"), tempRhOptions);
    tempRhChart.render();

    const gasOptions = {
        ...commonOptions,
        series: [{ name: 'Amonyak (ppm)', data: [] }, { name: 'CO2 (ppm)', data: [] }],
        chart: { ...commonOptions.chart, type: 'area', height: 200 },
        colors: ['#f59e0b', '#64748b'],
        fill: { type: 'solid', opacity: 0.1 }
    };
    gasChart = new ApexCharts(document.querySelector("#chart-gas"), gasOptions);
    gasChart.render();

    const sparklineOptions = {
        chart: { type: 'line', width: '100%', height: '100%', sparkline: { enabled: true }, animations: { enabled: false } },
        stroke: { curve: 'smooth', width: 2 },
        colors: ['#ef4444'],
        series: [{ data: [] }],
        tooltip: { fixed: { enabled: false }, x: { show: false }, y: { title: { formatter: function (seriesName) { return '' } } }, marker: { show: false } }
    };
    lossSparklineChart = new ApexCharts(document.querySelector("#chart-loss-sparkline"), sparklineOptions);
    lossSparklineChart.render();
}

function fetchLive() {
    fetch('/api/dashboard/live?t=' + new Date().getTime())
        .then(r => r.json())
        .then(data => {
            processLiveData(data);
        })
        .catch(err => console.error(err));
}

function processLiveData(data) {
            if (data.status === 'waiting') {
                const wm = document.getElementById('watchdog-modal');
                if (data.module_down) {
                    if (wm) wm.classList.remove('hidden');
                } else {
                    if (wm) wm.classList.add('hidden');
                }
                return;
            }
            
            // Watchdog Modal Logic
            const watchdogModal = document.getElementById('watchdog-modal');
            if (data.module_down) {
                if (watchdogModal) watchdogModal.classList.remove('hidden');
            } else {
                if (watchdogModal) watchdogModal.classList.add('hidden');
            }
            // Raw IoT Data
            const raw = data.raw;
            updateValueWithTick('val-temp', raw.t_in.toFixed(1) + '°C');
            updateValueWithTick('val-rh', raw.rh_in.toFixed(1) + '%');
            updateValueWithTick('val-nh3', raw.nh3.toFixed(1) + ' ppm');
            updateValueWithTick('val-co2', raw.co2.toFixed(0) + ' ppm');

            // Zone Sensors
            if (raw.zones && raw.zones.length > 0) {
                const zoneList = document.getElementById('zone-sensors-list');
                if (zoneList) {
                    zoneList.innerHTML = raw.zones.map(z => `
                        <div class="min-w-[130px] flex-shrink-0 bg-slate-50 border border-slate-200 rounded-lg p-2 text-center shadow-sm">
                            <h4 class="text-[10px] font-bold text-slate-500 uppercase border-b border-slate-200 pb-1 mb-1">${z.zone.replace('-', ' ')}</h4>
                            <div class="space-y-1">
                                <div class="flex justify-between text-[11px]">
                                    <span class="text-slate-400">Sıc:</span>
                                    <span class="font-bold text-slate-700">${z.t_in.toFixed(1)}°C</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span class="text-slate-400">Nem:</span>
                                    <span class="font-bold text-slate-700">${z.rh_in ? z.rh_in.toFixed(1) : '--'}%</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span class="text-slate-400">NH3:</span>
                                    <span class="font-bold ${z.nh3 > 25 ? 'text-red-600' : 'text-slate-700'}">${z.nh3.toFixed(1)}</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span class="text-slate-400">CO2:</span>
                                    <span class="font-bold ${z.co2 > 3000 ? 'text-red-600' : 'text-slate-700'}">${z.co2 ? z.co2.toFixed(0) : '--'}</span>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }
            }

            // Bio / Financial Data
            const bio = data.bio;
            updateValueWithTick('val-total-loss', '₺' + bio.total_loss_tl.toLocaleString());
            updateValueWithTick('val-feed-loss', '₺' + bio.feed_loss_tl.toLocaleString());
            updateValueWithTick('val-energy-cost', '₺' + bio.energy_cost_tl.toLocaleString());
            updateValueWithTick('val-mortality-loss', '₺' + bio.mortality_loss_tl.toLocaleString());
            updateValueWithTick('val-epef', bio.epef);
            
            // Cycle Phase & Target Temp
            const badge = document.getElementById('ui-phase-badge');
            if (badge && bio.phase_name) {
                badge.classList.remove('hidden');
                badge.innerText = `${Math.floor(bio.bird_age_days || 0)}. Gün (${bio.phase_name})`;
            }
            const targetEl = document.getElementById('ui-target-temp');
            if (targetEl && bio.target_temp) {
                targetEl.innerText = `Hedef: ${bio.target_temp}°C`;
                
                // Update Target Band in Chart
                if(tempRhChart) {
                    tempRhChart.updateOptions({
                        annotations: {
                            yaxis: [{
                                y: bio.target_temp - 0.5,
                                y2: bio.target_temp + 0.5,
                                fillColor: '#2D3B2E',
                                opacity: 0.1,
                                label: { text: 'İdeal Aralık', style: { color: '#fff', background: '#2D3B2E', fontSize: '10px' } }
                            }]
                        }
                    }, false, false);
                }
            }
            
            const weightEl = document.getElementById('ui-current-weight');
            if (weightEl && bio.current_weight) {
                updateValueWithTick('ui-current-weight', bio.current_weight.toFixed(3));
            }
            
            const deadBirdsEl = document.getElementById('ui-dead-birds');
            if (deadBirdsEl && bio.dead_birds !== undefined) {
                updateValueWithTick('ui-dead-birds', bio.dead_birds);
            }
            
            // Update Lifecycle Timeline (Max 45 days)
            const lifecycleProgress = document.getElementById('ui-lifecycle-progress');
            const lifecycleMarker = document.getElementById('ui-lifecycle-marker');
            if (lifecycleProgress && bio.bird_age_days !== undefined) {
                const percent = Math.min(100, Math.max(0, (bio.bird_age_days / 45.0) * 100));
                lifecycleProgress.style.width = percent + '%';
                lifecycleMarker.style.left = percent + '%';
            }
            
            let epef_eval = "";
            let epef_color = "";
            if (bio.epef >= 400) { epef_eval = "Mükemmel (Hedefin Üzerinde)"; epef_color = "text-emerald-600"; }
            else if (bio.epef >= 350) { epef_eval = "Çok İyi (Yüksek Verim)"; epef_color = "text-green-600"; }
            else if (bio.epef >= 300) { epef_eval = "İyi (Normal Seviye)"; epef_color = "text-blue-600"; }
            else { epef_eval = "Zayıf (Müdahale Gerekli)"; epef_color = "text-red-600"; }
            const epefEvalEl = document.getElementById('val-epef-eval');
            if (epefEvalEl) {
                // epefEvalEl.innerText = epef_eval;
                // document.getElementById('val-epef').className = `text-2xl font-bold tabular-data tick-animate ${epef_color}`;
            }

            updateValueWithTick('val-fcr-penalty', '+' + bio.fcr_penalty.toFixed(4));
            updateValueWithTick('val-t-eff', bio.max_t_eff + '°C');
            updateValueWithTick('val-wind-chill', '-' + bio.wind_chill_deg + '°C');

            // OpenMeteo Data
            const om = data.openmeteo;
            if(om) {
                document.getElementById('om-location').innerText = om.location || 'Konum Seçilmedi';
                document.getElementById('om-temp').innerText = om.t_out + '°C';
                document.getElementById('om-wind').innerText = om.wind_speed + ' km/h';
            }

            document.getElementById('status-indicator').innerHTML = '<span class="pulse-dot w-2 h-2 bg-green-500 rounded-full"></span> Çevrimiçi';
            document.getElementById('status-indicator').className = 'flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 border border-green-200 rounded-md font-semibold text-xs';
            // Virtual Operator State
            if (data.actuators) {
                const totalFans = parseInt(document.getElementById('s-sensor_count').value) || 6; // Temporary fallback to sensor_count if fan_count is missing, but settings has fan_count.
                // Wait, we need total fans. We can fetch it from settings or just hardcode for UI if missing, but let's see if settings is available here.
                // Let's just use data.actuators.active_fans and guess the total or see if we can get settings.fan_count.
                
                const voActionHistory = document.getElementById('vo-action-history');
                const voFanText = document.getElementById('vo-fan-text');
                const voFanBar = document.getElementById('vo-fan-bar');
                const voHeaterStatus = document.getElementById('vo-heater-status');
                
                if (voActionHistory) {
                    if (data.actuators.action_history && data.actuators.action_history.length > 0) {
                        voActionHistory.innerHTML = '';
                        data.actuators.action_history.forEach((action, index) => {
                            const timeStr = new Date(action.timestamp * 1000).toLocaleTimeString();
                            const isLatest = index === 0;
                            const colorClass = isLatest ? 'text-green-400 font-bold' : 'text-slate-500 opacity-80';
                            const dot = isLatest ? '▶' : '·';
                            voActionHistory.innerHTML += `<p class="text-[13px] font-mono ${colorClass} leading-tight mb-1">${dot} [${timeStr}] ${action.text}</p>`;
                        });
                    } else if (data.actuators.action_text) {
                        voActionHistory.innerHTML = `<p class="text-sm font-mono text-green-400 leading-relaxed">${data.actuators.action_text}</p>`;
                    } else {
                        voActionHistory.innerHTML = `<p class="text-sm font-mono text-green-400 leading-relaxed">Durum bekleniyor...</p>`;
                    }
                }
                
                // We'll use 6 as a fallback for total fans if settings is not fully loaded here. In our system, total fans are typically 6 to 10.
                const activeFans = data.actuators.active_fans || 0;
                let totalFansCount = 6;
                const fanCountInput = document.getElementById('s-fan_count');
                if (fanCountInput && fanCountInput.value) {
                    totalFansCount = parseInt(fanCountInput.value);
                }
                
                if (voFanText) voFanText.innerText = `${activeFans}/${totalFansCount}`;
                if (voFanBar) {
                    const pct = Math.min(100, (activeFans / totalFansCount) * 100);
                    voFanBar.style.width = pct + '%';
                    
                    // Change color based on fan usage
                    if (pct > 80) { voFanBar.className = "bg-red-500 h-2.5 rounded-full transition-all duration-500"; }
                    else if (pct > 40) { voFanBar.className = "bg-amber-500 h-2.5 rounded-full transition-all duration-500"; }
                    else { voFanBar.className = "bg-indigo-500 h-2.5 rounded-full transition-all duration-500"; }
                }
                
                if (voHeaterStatus) {
                    if (data.actuators.heater_w > 0) {
                        voHeaterStatus.innerText = "AÇIK (" + (data.actuators.heater_w / 1000).toFixed(0) + " kW)";
                        voHeaterStatus.className = "px-3 py-1 text-xs font-bold rounded bg-orange-500 text-white animate-pulse";
                    } else {
                        voHeaterStatus.innerText = "KAPALI";
                        voHeaterStatus.className = "px-3 py-1 text-xs font-bold rounded bg-slate-600 text-slate-300";
                    }
                }
                
                const voPadStatus = document.getElementById('vo-pad-status');
                if (voPadStatus) {
                    if (data.actuators.pad_cooling) {
                        voPadStatus.innerText = "AÇIK (Aktif)";
                        voPadStatus.className = "px-3 py-1 text-xs font-bold rounded bg-cyan-500 text-white animate-pulse";
                    } else {
                        voPadStatus.innerText = "KAPALI";
                        voPadStatus.className = "px-3 py-1 text-xs font-bold rounded bg-slate-600 text-slate-300";
                    }
                }

                // Main Dashboard Actuator Updates
                updateValueWithTick('ui-fan-status', activeFans + '/' + totalFansCount);
                if (data.actuators.heater_w > 0) {
                    updateValueWithTick('ui-heater-status', 'ON (' + (data.actuators.heater_w / 1000).toFixed(0) + 'kW)');
                } else {
                    updateValueWithTick('ui-heater-status', 'OFF');
                }
                if (data.actuators.pad_cooling) {
                    updateValueWithTick('ui-pad-status', 'ON');
                } else {
                    updateValueWithTick('ui-pad-status', 'OFF');
                }
            }

            const date = new Date(data.timestamp);
            const dateStr = date.toLocaleDateString('tr-TR');
            const timeStr = date.toLocaleTimeString('tr-TR');
            
            const lastUpdateEl = document.getElementById('last-update');
            if (lastUpdateEl) lastUpdateEl.innerText = 'Son güncelleme: ' + timeStr;
            
            const topLastUpdateEl = document.getElementById('top-last-update');
            if (topLastUpdateEl) topLastUpdateEl.innerText = dateStr + ' ' + timeStr;

            updateActionList(raw, bio);
            fetchHistory(); // refresh chart
}

function updateActionList(raw, bio) {
    const list = document.getElementById('action-list');
    list.innerHTML = '';
    // Do NOT override list.className to preserve flex-row from HTML
    
    if (!bio.actions || bio.actions.length === 0) {
        list.innerHTML = `
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 flex items-center justify-center">
            <span class="text-gray-400 font-medium text-sm flex items-center gap-2">
                <svg class="animate-spin h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Karar motoru verileri işliyor...
            </span>
        </div>`;
        return;
    }

    bio.actions.forEach(action => {
        let iconSvg = "";
        let bgClass = "";
        let borderClass = "";
        let textClass = "";
        let iconBg = "";

        if (action.type === "danger" || action.type === "critical") {
            iconSvg = `<svg class="w-5 h-5 text-red-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path></svg>`;
            bgClass = "bg-red-50";
            borderClass = "border-l-4 border-l-red-600 border-t border-b border-r border-gray-200";
            textClass = "text-red-900";
            iconBg = "bg-red-100";
        } else if (action.type === "warning") {
            iconSvg = `<svg class="w-5 h-5 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>`;
            bgClass = "bg-amber-50";
            borderClass = "border-l-4 border-l-amber-500 border-t border-b border-r border-gray-200";
            textClass = "text-amber-900";
            iconBg = "bg-amber-100";
        } else if (action.type === "info") {
            iconSvg = `<svg class="w-5 h-5 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>`;
            bgClass = "bg-blue-50";
            borderClass = "border-l-4 border-l-blue-500 border-t border-b border-r border-gray-200";
            textClass = "text-blue-900";
            iconBg = "bg-blue-100";
        } else if (action.type === "success") {
            iconSvg = `<svg class="w-5 h-5 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>`;
            bgClass = "bg-[#F7F3EA]";
            borderClass = "border-l-4 border-l-[#2D3B2E] border-t border-b border-r border-gray-200";
            textClass = "text-[#2D3B2E]";
            iconBg = "bg-white";
        }

        // Pulse effect for critical alerts to grab immediate attention
        let pulseHtml = (action.type === "danger" || action.type === "critical") 
            ? `<span class="absolute -top-1 -right-1 flex h-3 w-3"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span></span>` 
            : "";

        list.innerHTML += `
            <div class="relative flex-none w-[320px] md:w-[350px] flex items-start gap-3 p-4 rounded bg-white ${borderClass} cursor-default snap-start shadow-sm">
                ${pulseHtml}
                <div class="flex-shrink-0 p-2 rounded-full ${iconBg} shadow-sm border border-white">
                    ${iconSvg}
                </div>
                <div class="flex-1">
                    <h4 class="font-bold text-sm ${textClass} mb-1 flex items-center justify-between font-mono tracking-tight">
                        ${action.title}
                        ${(action.type === "danger" || action.type === "critical") ? '<span class="text-[9px] uppercase tracking-wider bg-red-600 text-white px-1.5 py-0.5 rounded shadow-sm">ACİL</span>' : ''}
                    </h4>
                    <p class="text-[13px] text-gray-700 leading-snug font-medium mb-2">${action.desc}</p>
                    ${action.guide ? `
                        <div class="mt-2 pt-2 border-t border-dashed border-gray-300">
                            <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 block">Çiftçi Aksiyon Rehberi</span>
                            <div class="text-[12px] text-gray-600 leading-relaxed font-mono">
                                ${action.guide}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
}

function fetchHistory() {
    let range = '1h';
    const rangeEl = document.getElementById('history-range');
    if (rangeEl) range = rangeEl.value;

    fetch('/api/dashboard/history?range=' + range)
        .then(r => r.json())
        .then(data => {
            if(!data.length) return;
            const times = data.map(d => d.time);
            
            tempRhChart.updateSeries([
                { name: 'Sıcaklık (°C)', data: data.map(d => d.t_in) },
                { name: 'Nem (%)', data: data.map(d => d.rh_in) }
            ]);
            tempRhChart.updateOptions({ xaxis: { categories: times } }, false, false);
            
            gasChart.updateSeries([
                { name: 'Amonyak (ppm)', data: data.map(d => d.nh3) },
                { name: 'CO2 (ppm)', data: data.map(d => d.co2) }
            ]);
            gasChart.updateOptions({ xaxis: { categories: times } }, false, false);

            if(lossSparklineChart) {
                // Generate a cumulative loss curve for the sparkline (mock integration)
                // In a real app, this should come directly from history endpoint.
                let cumulative = 0;
                let lossData = data.map((d, i) => {
                    cumulative += (d.t_in > 33 ? 50 : 5);
                    return cumulative;
                });
                lossSparklineChart.updateSeries([{ data: lossData }]);
            }
        });
}

function initMap(lat, lon) {
    if (map) {
        map.setView([lat, lon], 12);
        marker.setLatLng([lat, lon]);
        return;
    }
    
    map = L.map('map').setView([lat, lon], 12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    marker = L.marker([lat, lon], {draggable: true}).addTo(map);
    
    // When dragged
    marker.on('dragend', function (e) {
        document.getElementById('s-lat').value = marker.getLatLng().lat.toFixed(4);
        document.getElementById('s-lon').value = marker.getLatLng().lng.toFixed(4);
    });

    // When clicked on map
    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        document.getElementById('s-lat').value = e.latlng.lat.toFixed(4);
        document.getElementById('s-lon').value = e.latlng.lng.toFixed(4);
    });
}

function openSettings() {
    document.getElementById('settings-modal').classList.remove('hidden');
    // Important: leaflet needs to recalculate size if it was initialized in hidden div
    setTimeout(() => {
        if(map) map.invalidateSize();
    }, 100);
}

function closeSettings() {
    document.getElementById('settings-modal').classList.add('hidden');
}

function fetchSettings() {
    fetch('/api/settings?t=' + new Date().getTime())
        .then(r => r.json())
        .then(data => {
            const fields = [
                'location_name', 'lat', 'lon', 'house_length', 'house_width',
                'ridge_h', 'eaves_h', 'bird_count', 'bird_weight',
                'fan_count', 'fan_capacity', 'feed_price', 'meat_price',
                'electricity_price', 'mqtt_topic', 'sensor_count', 'flock_breed'
            ];
            fields.forEach(f => {
                if (document.getElementById('s-' + f)) {
                    document.getElementById('s-' + f).value = data[f] || '';
                }
            });
            if (data.flock_start_date) {
                document.getElementById('s-flock_start_date').value = data.flock_start_date.slice(0, 16);
            }
            
            const fanSlider = document.getElementById('manual-fan-slider');
            if (fanSlider && data.fan_count) {
                fanSlider.max = data.fan_count;
            }
            
            const demoToggle = document.getElementById('ui-demo-toggle');
            if (demoToggle && data.demo_mode !== undefined) {
                demoToggle.checked = data.demo_mode;
            }
            
            const aiToggle = document.getElementById('ai-toggle-switch');
            if (aiToggle) {
                const enabled = data.ai_operator_enabled !== undefined ? data.ai_operator_enabled : true;
                aiToggle.checked = enabled;
                
                const statusText = document.getElementById('ai-status-text');
                const panel = document.getElementById('manual-control-panel');
                if (enabled) {
                    statusText.innerText = "AKTİF (Oto MPC)";
                    statusText.className = "text-[10px] text-green-400 font-medium";
                    panel.classList.add('opacity-50', 'pointer-events-none');
                } else {
                    statusText.innerText = "DEVRE DIŞI (Manuel)";
                    statusText.className = "text-[10px] text-red-400 font-medium";
                    panel.classList.remove('opacity-50', 'pointer-events-none');
                }
            }
            
            const manualFan = data.manual_active_fans !== undefined ? data.manual_active_fans : 2;
            if (fanSlider) fanSlider.value = manualFan;
            const fanVal = document.getElementById('manual-fan-val');
            if (fanVal) fanVal.innerText = manualFan;
            
            const heaterSelect = document.getElementById('manual-heater-select');
            if (heaterSelect && data.manual_heater_w !== undefined) {
                if (data.manual_heater_w === 0.0) heaterSelect.value = "0.0";
                else if (data.manual_heater_w === 250000.0) heaterSelect.value = "250000.0";
                else if (data.manual_heater_w === 500000.0) heaterSelect.value = "500000.0";
            }
            
            const padCheck = document.getElementById('manual-pad-check');
            if (padCheck) padCheck.checked = data.manual_pad_cooling !== undefined ? data.manual_pad_cooling : false;
            
            const lat = data.lat || 38.4237;
            const lon = data.lon || 27.1428;
            initMap(lat, lon);
        });
}
function saveSettings(e) {
    e.preventDefault();
    const payload = {
        location_name: document.getElementById('s-location_name').value,
        lat: parseFloat(document.getElementById('s-lat').value),
        lon: parseFloat(document.getElementById('s-lon').value),
        house_length: parseFloat(document.getElementById('s-house_length').value),
        house_width: parseFloat(document.getElementById('s-house_width').value),
        ridge_h: parseFloat(document.getElementById('s-ridge_h').value),
        eaves_h: parseFloat(document.getElementById('s-eaves_h').value),
        bird_count: parseInt(document.getElementById('s-bird_count').value),
        bird_weight: parseFloat(document.getElementById('s-bird_weight').value),
        flock_breed: document.getElementById('s-flock_breed').value,
        flock_start_date: document.getElementById('s-flock_start_date').value ? new Date(document.getElementById('s-flock_start_date').value).toISOString() : null,
        fan_count: parseInt(document.getElementById('s-fan_count').value),
        fan_capacity: parseFloat(document.getElementById('s-fan_capacity').value),
        feed_price: parseFloat(document.getElementById('s-feed_price').value),
        meat_price: parseFloat(document.getElementById('s-meat_price').value),
        electricity_price: parseFloat(document.getElementById('s-electricity_price').value),
        mqtt_topic: document.getElementById('s-mqtt_topic').value,
        sensor_count: parseInt(document.getElementById('s-sensor_count').value)
    };

    fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(res => {
        const s = document.getElementById('save-status');
        s.classList.remove('hidden');
        setTimeout(() => s.classList.add('hidden'), 3000);
        
        // Settings changed, instantly trigger a live fetch to refresh bio math
        fetchLive();
    });
}

// --------------------------------------------------
// DATA RESET LOGIC
// --------------------------------------------------
function resetMockData() {
    if (!confirm('Tüm geçmiş sensör verileri silinecek ve simülasyon sıfırdan başlayacak. Emin misiniz?')) {
        return;
    }
    
    fetch('/api/settings/reset', {
        method: 'POST'
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === 'ok') {
            alert(res.message);
            fetchLive();
        } else {
            alert('Hata: ' + res.message);
        }
    })
    .catch(err => {
        console.error(err);
        alert('Sıfırlama başarısız oldu.');
    });
}

// --------------------------------------------------
// MORTALITY MODAL LOGIC
// --------------------------------------------------
function openMortalityModal() {
    document.getElementById('mortality_input').value = 0;
    document.getElementById('mortality-modal').classList.remove('hidden');
}

function closeMortalityModal() {
    document.getElementById('mortality-modal').classList.add('hidden');
}

function saveMortality() {
    const deadBirds = parseInt(document.getElementById('mortality_input').value);
    if (isNaN(deadBirds) || deadBirds <= 0) {
        alert('Lütfen geçerli bir ölü sayısı girin.');
        return;
    }

    fetch('/api/mortality/report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ dead_birds: deadBirds })
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === 'ok') {
            alert(res.message);
            closeMortalityModal();
            // Optional: update Settings modal input if it is open
            const birdInput = document.getElementById('s-bird_count');
            if (birdInput) birdInput.value = res.new_bird_count;
            fetchLive();
        } else {
            alert('Hata: ' + res.message);
        }
    })
    .catch(err => {
        document.getElementById('s-lon').value = marker.getLatLng().lng.toFixed(4);
    });

    // When clicked on map
    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        document.getElementById('s-lat').value = e.latlng.lat.toFixed(4);
        document.getElementById('s-lon').value = e.latlng.lng.toFixed(4);
    });
}

function openSettings() {
    document.getElementById('settings-modal').classList.remove('hidden');
    // Important: leaflet needs to recalculate size if it was initialized in hidden div
    setTimeout(() => {
        if(map) map.invalidateSize();
    }, 100);
}

function closeSettings() {
    document.getElementById('settings-modal').classList.add('hidden');
}

function fetchSettings() {
    fetch('/api/settings?t=' + new Date().getTime())
        .then(r => r.json())
        .then(data => {
            const fields = [
                'location_name', 'lat', 'lon', 'house_length', 'house_width',
                'ridge_h', 'eaves_h', 'bird_count', 'bird_weight',
                'fan_count', 'fan_capacity', 'feed_price', 'meat_price',
                'electricity_price', 'mqtt_topic', 'sensor_count', 'flock_breed'
            ];
            fields.forEach(f => {
                if (document.getElementById('s-' + f)) {
                    document.getElementById('s-' + f).value = data[f] || '';
                }
            });
            if (data.flock_start_date) {
                document.getElementById('s-flock_start_date').value = data.flock_start_date.slice(0, 16);
            }
            
            const fanSlider = document.getElementById('manual-fan-slider');
            if (fanSlider && data.fan_count) {
                fanSlider.max = data.fan_count;
            }
            
            const demoToggle = document.getElementById('ui-demo-toggle');
            if (demoToggle && data.demo_mode !== undefined) {
                demoToggle.checked = data.demo_mode;
            }
            
            const aiToggle = document.getElementById('ai-toggle-switch');
            if (aiToggle) {
                const enabled = data.ai_operator_enabled !== undefined ? data.ai_operator_enabled : true;
                aiToggle.checked = enabled;
                
                const statusText = document.getElementById('ai-status-text');
                const panel = document.getElementById('manual-control-panel');
                if (enabled) {
                    statusText.innerText = "AKTİF (Oto MPC)";
                    statusText.className = "text-[10px] text-green-400 font-medium";
                    panel.classList.add('opacity-50', 'pointer-events-none');
                } else {
                    statusText.innerText = "DEVRE DIŞI (Manuel)";
                    statusText.className = "text-[10px] text-red-400 font-medium";
                    panel.classList.remove('opacity-50', 'pointer-events-none');
                }
            }
            
            const manualFan = data.manual_active_fans !== undefined ? data.manual_active_fans : 2;
            if (fanSlider) fanSlider.value = manualFan;
            const fanVal = document.getElementById('manual-fan-val');
            if (fanVal) fanVal.innerText = manualFan;
            
            const heaterSelect = document.getElementById('manual-heater-select');
            if (heaterSelect && data.manual_heater_w !== undefined) {
                if (data.manual_heater_w === 0.0) heaterSelect.value = "0.0";
                else if (data.manual_heater_w === 250000.0) heaterSelect.value = "250000.0";
                else if (data.manual_heater_w === 500000.0) heaterSelect.value = "500000.0";
            }
            
            const padCheck = document.getElementById('manual-pad-check');
            if (padCheck) padCheck.checked = data.manual_pad_cooling !== undefined ? data.manual_pad_cooling : false;
            
            const lat = data.lat || 38.4237;
            const lon = data.lon || 27.1428;
            initMap(lat, lon);
        });
}
function saveSettings(e) {
    e.preventDefault();
    const payload = {
        location_name: document.getElementById('s-location_name').value,
        lat: parseFloat(document.getElementById('s-lat').value),
        lon: parseFloat(document.getElementById('s-lon').value),
        house_length: parseFloat(document.getElementById('s-house_length').value),
        house_width: parseFloat(document.getElementById('s-house_width').value),
        ridge_h: parseFloat(document.getElementById('s-ridge_h').value),
        eaves_h: parseFloat(document.getElementById('s-eaves_h').value),
        bird_count: parseInt(document.getElementById('s-bird_count').value),
        bird_weight: parseFloat(document.getElementById('s-bird_weight').value),
        flock_breed: document.getElementById('s-flock_breed').value,
        flock_start_date: document.getElementById('s-flock_start_date').value ? new Date(document.getElementById('s-flock_start_date').value).toISOString() : null,
        fan_count: parseInt(document.getElementById('s-fan_count').value),
        fan_capacity: parseFloat(document.getElementById('s-fan_capacity').value),
        feed_price: parseFloat(document.getElementById('s-feed_price').value),
        meat_price: parseFloat(document.getElementById('s-meat_price').value),
        electricity_price: parseFloat(document.getElementById('s-electricity_price').value),
        mqtt_topic: document.getElementById('s-mqtt_topic').value,
        sensor_count: parseInt(document.getElementById('s-sensor_count').value)
    };

    fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(res => {
        const s = document.getElementById('save-status');
        s.classList.remove('hidden');
        setTimeout(() => s.classList.add('hidden'), 3000);
        
        // Settings changed, instantly trigger a live fetch to refresh bio math
        fetchLive();
    });
}

// --------------------------------------------------
// DATA RESET LOGIC
// --------------------------------------------------
function resetMockData() {
    if (!confirm('Tüm geçmiş sensör verileri silinecek ve simülasyon sıfırdan başlayacak. Emin misiniz?')) {
        return;
    }
    
    fetch('/api/settings/reset', {
        method: 'POST'
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === 'ok') {
            alert(res.message);
            fetchLive();
        } else {
            alert('Hata: ' + res.message);
        }
    })
    .catch(err => {
        console.error(err);
        alert('Sıfırlama başarısız oldu.');
    });
}

// --------------------------------------------------
// MORTALITY MODAL LOGIC
// --------------------------------------------------
function openMortalityModal() {
    document.getElementById('mortality_input').value = 0;
    document.getElementById('mortality-modal').classList.remove('hidden');
}

function closeMortalityModal() {
    document.getElementById('mortality-modal').classList.add('hidden');
}

function saveMortality() {
    const deadBirds = parseInt(document.getElementById('mortality_input').value);
    if (isNaN(deadBirds) || deadBirds <= 0) {
        alert('Lütfen geçerli bir ölü sayısı girin.');
        return;
    }

    fetch('/api/mortality/report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ dead_birds: deadBirds })
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === 'ok') {
            alert(res.message);
            closeMortalityModal();
            // Optional: update Settings modal input if it is open
            const birdInput = document.getElementById('s-bird_count');
            if (birdInput) birdInput.value = res.new_bird_count;
            fetchLive();
        } else {
            alert('Hata: ' + res.message);
        }
    })
    .catch(err => {
        console.error(err);
        alert('Sunucuya ulaşılamadı.');
    });
}

function toggleDemoMode(checkbox) {
    const isEnabled = checkbox.checked;
    fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ demo_mode: isEnabled })
    })
    .then(r => r.json())
    .then(data => {
        if(data.status !== 'ok') {
            alert('Hata: ' + data.message);
            checkbox.checked = !isEnabled;
        }
    })
    .catch(err => {
        console.error("Demo mode toggle error:", err);
        checkbox.checked = !isEnabled;
    });
}

// --------------------------------------------------
// SETUP & IOT SETUP MODAL LOGIC
// --------------------------------------------------
function openSetup() {
    const length = parseFloat(document.getElementById('s-house_length').value) || 100;
    const width = parseFloat(document.getElementById('s-house_width').value) || 14;
    const breed = document.getElementById('s-flock_breed').value || "Ross 308 (Etlik)";
    const dateInput = document.getElementById('s-flock_start_date').value;
    
    document.getElementById('setup-length').value = length;
    document.getElementById('setup-width').value = width;
    document.getElementById('setup-breed').value = breed;
    if (dateInput) {
        document.getElementById('setup-start-date').value = dateInput.split('T')[0];
    } else {
        document.getElementById('setup-start-date').value = new Date().toISOString().split('T')[0];
    }
    
    document.getElementById('setup-modal').classList.remove('hidden');
    calculateOptimalLayout();
}

function closeSetup() {
    document.getElementById('setup-modal').classList.add('hidden');
}

function openIotSetup() {
    document.getElementById('iot-setup-modal').classList.remove('hidden');
}

function closeIotSetup() {
    document.getElementById('iot-setup-modal').classList.add('hidden');
}

function calculateOptimalLayout() {
    const length = parseFloat(document.getElementById('setup-length').value) || 0;
    const width = parseFloat(document.getElementById('setup-width').value) || 0;
    
    if (length <= 0 || width <= 0) return;
    
    const sensorsPerRow = Math.max(2, Math.round(length / 20));
    const rows = width > 18 ? 2 : 1;
    const qtyTemp = sensorsPerRow * rows;
    
    document.getElementById('setup-sensor-count').innerText = `${qtyTemp} Adet`;
    document.getElementById('setup-height-desc').innerText = "Sıcaklık ve Nem sensörleri hayvanların bulunduğu seviyede (yerden 20-30 cm yükseklikte) ve hava akımının doğrudan vurmadığı, duvardan en az 1 m uzakta konumlandırılmalıdır.";
    
    const container = document.getElementById('setup-canvas-container');
    container.innerHTML = '';
    
    const houseDiv = document.createElement('div');
    houseDiv.className = 'border-2 border-slate-700 bg-slate-100 rounded relative shadow-inner w-full h-[140px]';
    
    for (let r = 0; r < rows; r++) {
        const topPercent = rows === 1 ? 50 : (r === 0 ? 30 : 70);
        for (let s = 0; s < sensorsPerRow; s++) {
            const leftPercent = ((s + 0.5) / sensorsPerRow) * 100;
            
            const sensorDot = document.createElement('div');
            sensorDot.className = 'absolute w-3.5 h-3.5 bg-indigo-600 rounded-full flex items-center justify-center -translate-x-1/2 -translate-y-1/2 cursor-help shadow';
            sensorDot.style.left = leftPercent + '%';
            sensorDot.style.top = topPercent + '%';
            sensorDot.title = `Sensör Bölgesi ${r * sensorsPerRow + s + 1}`;
            
            const pulseRing = document.createElement('span');
            pulseRing.className = 'absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75 animate-ping';
            sensorDot.appendChild(pulseRing);
            
            const dotInner = document.createElement('span');
            dotInner.className = 'relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-600 border border-white';
            sensorDot.appendChild(dotInner);
            
            const label = document.createElement('span');
            label.className = 'absolute -top-5 text-[8px] font-bold text-indigo-800 bg-white px-1 rounded shadow-sm border border-indigo-200';
            label.innerText = `S${r * sensorsPerRow + s + 1}`;
            sensorDot.appendChild(label);
            
            houseDiv.appendChild(sensorDot);
        }
    }
    
    container.appendChild(houseDiv);
}

function saveSetup() {
    const length = parseFloat(document.getElementById('setup-length').value);
    const width = parseFloat(document.getElementById('setup-width').value);
    const breed = document.getElementById('setup-breed').value;
    const startDate = document.getElementById('setup-start-date').value;
    
    if (isNaN(length) || isNaN(width) || length <= 0 || width <= 0) {
        alert('Lütfen geçerli ebatlar girin.');
        return;
    }
    
    const sensorsPerRow = Math.max(2, Math.round(length / 20));
    const rows = width > 18 ? 2 : 1;
    const qtyTemp = sensorsPerRow * rows;
    
    const payload = {
        house_length: length,
        house_width: width,
        flock_breed: breed,
        flock_start_date: startDate ? new Date(startDate).toISOString() : null,
        sensor_count: qtyTemp
    };
    
    fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === 'ok') {
            const status = document.getElementById('setup-save-status');
            status.classList.remove('hidden');
            setTimeout(() => status.classList.add('hidden'), 3000);
            fetchSettings();
            fetchLive();
        } else {
            alert('Hata: ' + res.message);
        }
    })
    .catch(err => {
        console.error(err);
        alert('Sunucu hatası.');
    });
}

function downloadSetupPDF() {
    const element = document.getElementById('setup-export-area');
    const opt = {
        margin: 10,
        filename: 'kumes_kurulum_krokisi.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
    };
    html2pdf().set(opt).from(element).save();
}

// --------------------------------------------------
// ALARM HISTORY MODAL LOGIC
// --------------------------------------------------
function openAlarmHistory() {
    document.getElementById('alarm-history-modal').classList.remove('hidden');
    fetchAlarms();
}

// Ensure globally accessible
window.openSetup = openSetup;
window.closeSetup = closeSetup;
window.openIotSetup = openIotSetup;
window.closeIotSetup = closeIotSetup;
window.calculateOptimalLayout = calculateOptimalLayout;
window.saveSetup = saveSetup;
window.downloadSetupPDF = downloadSetupPDF;
window.openAlarmHistory = openAlarmHistory;

function closeAlarmHistory() {
    document.getElementById('alarm-history-modal').classList.add('hidden');
}
window.closeAlarmHistory = closeAlarmHistory;

function fetchAlarms() {
    const list = document.getElementById('alarm-history-list');
    list.innerHTML = '<div class="text-[12px] text-ink-light">Yükleniyor...</div>';
    
    fetch('/api/dashboard/alarms')
        .then(r => r.json())
        .then(data => {
            if (!data || data.length === 0) {
                list.innerHTML = '<div class="text-[12px] text-ink-muted text-center py-4">Kayıtlı alarm bulunmuyor.</div>';
                return;
            }
            
            list.innerHTML = data.map(alarm => {
                let badgeColor = "bg-slate-100 text-slate-700";
                if (alarm.type === "danger" || alarm.type === "critical") badgeColor = "bg-red-100 text-red-700";
                else if (alarm.type === "warning") badgeColor = "bg-amber-100 text-amber-700";
                
                return `
                    <div class="panel mb-3 bg-white">
                        <div class="flex justify-between items-center mb-1.5">
                            <span class="text-[9px] font-mono text-ink-light">${alarm.timestamp}</span>
                            <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${badgeColor}">${alarm.type}</span>
                        </div>
                        <h4 class="text-[12px] font-bold text-ink mb-1">${alarm.title}</h4>
                        <p class="text-[11px] text-ink-muted leading-relaxed">${alarm.desc}</p>
                    </div>
                `;
            }).join('');
        })
        .catch(err => {
            console.error(err);
            list.innerHTML = '<div class="text-[12px] text-red-600">Alarmlar yüklenirken hata oluştu.</div>';
        });
}

// --------------------------------------------------
// ROLE BASED ACCESS CONTROL & AUTHENTICATION HANDLERS
// --------------------------------------------------
function applyUserRole() {
    fetch('/api/auth/me')
        .then(r => {
            if (!r.ok) {
                window.location.href = '/login';
                return;
            }
            return r.json();
        })
        .then(user => {
            if (!user) return;
            const role = user.role;
            const username = user.username;
            
            localStorage.setItem('user_role', role);
            localStorage.setItem('username', username);
            
            const roleBadge = document.getElementById('ui-role-badge');
            if (roleBadge) {
                if (role === 'admin') {
                    roleBadge.innerText = 'ADMİN (TAM YETKİ)';
                    roleBadge.className = 'text-[10px] font-bold px-2 py-0.5 rounded shadow-sm bg-sky-100 text-sky-700 uppercase';
                    
                    const changePwdBtn = document.getElementById('btn-change-pwd');
                    if (changePwdBtn) changePwdBtn.classList.remove('hidden');
                } else {
                    roleBadge.innerText = 'DEMO (SALT OKUR)';
                    roleBadge.className = 'text-[10px] font-bold px-2 py-0.5 rounded shadow-sm bg-slate-100 text-slate-600 uppercase';
                    
                    const hideElements = ['btn-setup', 'btn-settings', 'btn-iot-setup', 'btn-fire', 'ui-demo-mode-container'];
                    hideElements.forEach(id => {
                        const el = document.getElementById(id);
                        if (el) el.classList.add('hidden');
                    });
                }
            }
        })
        .catch(err => {
            console.error("Auth error:", err);
            window.location.href = '/login';
        });
}

function handleLogout() {
    fetch('/api/auth/logout', { method: 'POST' })
        .then(() => {
            localStorage.removeItem('user_role');
            localStorage.removeItem('username');
            window.location.href = '/login';
        })
        .catch(err => console.error("Logout failed:", err));
}

function openPasswordModal() {
    document.getElementById('old_password').value = '';
    document.getElementById('new_password').value = '';
    document.getElementById('password-error').classList.add('hidden');
    document.getElementById('password-success').classList.add('hidden');
    document.getElementById('password-modal').classList.remove('hidden');
}

function closePasswordModal() {
    document.getElementById('password-modal').classList.add('hidden');
}

function saveNewPassword(e) {
    e.preventDefault();
    const oldPwd = document.getElementById('old_password').value;
    const newPwd = document.getElementById('new_password').value;
    const errEl = document.getElementById('password-error');
    const succEl = document.getElementById('password-success');

    errEl.classList.add('hidden');
    succEl.classList.add('hidden');

    fetch('/api/auth/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
    })
    .then(async r => {
        const res = await r.json();
        if (!r.ok) throw new Error(res.detail || 'Şifre güncellenemedi.');
        return res;
    })
    .then(res => {
        succEl.innerText = res.message;
        succEl.classList.remove('hidden');
        setTimeout(closePasswordModal, 2000);
    })
    .catch(err => {
        errEl.innerText = err.message;
        errEl.classList.remove('hidden');
    });
}

window.applyUserRole = applyUserRole;
window.handleLogout = handleLogout;
window.openPasswordModal = openPasswordModal;
window.closePasswordModal = closePasswordModal;
window.saveNewPassword = saveNewPassword;

