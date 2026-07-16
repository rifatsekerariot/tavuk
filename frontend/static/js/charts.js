// Global chart instances
let tempChart = null;
let actChart = null;
let flowChart = null;

window.renderCharts = function(series, inputs) {
    const hours = series.hours;
    
    // Y-Axis formatting settings for ApexCharts
    const commonOptions = {
        chart: {
            height: 500,
            animations: { enabled: false },
            toolbar: { show: true },
            background: 'transparent',
            fontFamily: 'Inter, sans-serif'
        },
        dataLabels: {
            enabled: false
        },
        markers: {
            size: 0,
            hover: { size: 5 }
        },
        theme: {
            mode: 'light'
        },
        stroke: {
            curve: 'smooth',
            width: 3
        },
        grid: {
            borderColor: '#f0f0f0',
            strokeDashArray: 4
        },
        tooltip: {
            theme: 'light'
        },
        xaxis: {
            categories: hours,
            tickAmount: Math.min(10, inputs.sim_days * 2), // Keep X-axis sparse so it doesn't overlap
            labels: { style: { colors: '#9c1c8c' } },
            axisBorder: { show: false },
            axisTicks: { show: false }
        }
    };

    // --- Temperature Chart ---
    const tempOptions = {
        ...commonOptions,
        chart: { ...commonOptions.chart, type: 'line', height: 400 },
        series: [
            { name: "Yeni Model", data: series.t_in_new },
            { name: "Klasik Model", data: series.t_in_cls },
            { name: "Dış Sıcaklık", data: series.t_out }
        ],
        stroke: { curve: 'smooth', width: [4, 3, 2], dashArray: [0, 0, 5] },
        colors: ['#9c1c8c', '#f59e0b', '#64748b'],
        yaxis: {
            labels: { style: { colors: '#9c1c8c' }, formatter: (val) => val.toFixed(1) },
            title: { text: "Sıcaklık (°C)", style: { color: '#9c1c8c', fontWeight: 700 } }
        },
        annotations: {
            yaxis: [
                {
                    y: inputs.t_target,
                    borderColor: '#10b981',
                    strokeDashArray: 0,
                    label: { borderColor: '#10b981', style: { color: '#fff', background: '#10b981', fontWeight: 700 }, text: 'Hedef' }
                },
                {
                    y: inputs.t_crit_max,
                    borderColor: '#ef4444',
                    strokeDashArray: 5,
                    label: { borderColor: '#ef4444', style: { color: '#fff', background: '#ef4444', fontWeight: 700 }, text: 'Kritik Max' }
                },
                {
                    y: inputs.t_crit_min,
                    borderColor: '#ef4444',
                    strokeDashArray: 5,
                    label: { borderColor: '#ef4444', style: { color: '#fff', background: '#ef4444', fontWeight: 700 }, text: 'Kritik Min', position: 'left' }
                }
            ],
            // X-Axis Day Markers
            xaxis: []
        }
    };

    // Add Day vertical lines
    for(let d=1; d<=inputs.sim_days; d++) {
        tempOptions.annotations.xaxis.push({
            x: (d*24).toString(),
            borderColor: '#9c1c8c',
            strokeDashArray: 4,
            label: { style: { color: '#fff', background: '#9c1c8c', fontWeight: 700 }, text: `${d}. Gün` }
        });
    }

    // Y-axis optimal band (background fill)
    tempOptions.annotations.yaxis.push({
        y: inputs.t_target - 1.0,
        y2: inputs.t_target + 1.0,
        fillColor: '#10b981',
        opacity: 0.1,
        label: { text: 'Optimal Bant', style: { color: '#10b981', background: 'transparent' } }
    });

    if(tempChart) tempChart.destroy();
    tempChart = new ApexCharts(document.querySelector("#apex-temp"), tempOptions);
    tempChart.render();

    // --- Actuator Chart ---
    const actOptions = {
        ...commonOptions,
        chart: { ...commonOptions.chart, type: 'area', height: 400 },
        series: [
            { name: "Yeni Model Fan", data: series.fans_new },
            { name: "Yeni Model Ped", data: series.pad_new.map(p => p * inputs.fan_count) },
            { name: "Klasik Model Fan", data: series.fans_cls }
        ],
        stroke: { curve: 'stepline', width: [3, 0, 3] },
        fill: { type: ['solid', 'solid', 'transparent'], opacity: [0.4, 0.2, 1] },
        colors: ['#9c1c8c', '#d946ef', '#f59e0b'],
        yaxis: {
            max: inputs.fan_count,
            labels: { style: { colors: '#9c1c8c' } },
            title: { text: "Aktif Fan Sayısı", style: { color: '#9c1c8c', fontWeight: 700 } }
        },
        annotations: { xaxis: tempOptions.annotations.xaxis } // same day markers
    };

    if(actChart) actChart.destroy();
    actChart = new ApexCharts(document.querySelector("#apex-act"), actOptions);
    actChart.render();

    // --- Required Flow Chart ---
    const flowOptions = {
        ...commonOptions,
        chart: { ...commonOptions.chart, type: 'area', height: 400 },
        series: [
            { name: "Gerekli Debi (m³/sa)", data: series.q_req_new }
        ],
        stroke: { curve: 'smooth', width: 3 },
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.6, opacityTo: 0.1, stops: [0, 100] } },
        colors: ['#b525a3'],
        yaxis: {
            labels: { 
                formatter: (val) => val.toLocaleString('tr-TR', {maximumFractionDigits:0}),
                style: { colors: '#9c1c8c' } 
            },
            title: { text: "Debi (m³/sa)", style: { color: '#9c1c8c', fontWeight: 700 } }
        },
        annotations: { xaxis: tempOptions.annotations.xaxis }
    };

    if(flowChart) flowChart.destroy();
    flowChart = new ApexCharts(document.querySelector("#apex-flow"), flowOptions);
    flowChart.render();
};
