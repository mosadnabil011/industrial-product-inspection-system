let lineChart, pieChart, gaugeChart;
let history = [];

function updateCharts(ok, notOk) {
    const total = ok + notOk;
    const defect = total ? (notOk / total) * 100 : 0;

    // ===== LINE =====
    const now = new Date().toLocaleTimeString();
    history.push({ time: now, value: total });
    if (history.length > 10) history.shift();

    if (lineChart) lineChart.destroy();
    lineChart = new Chart(document.getElementById("lineChart"), {
        type: "line",
        data: {
            labels: history.map(h => h.time),
            datasets: [{
                label: "Production",
                data: history.map(h => h.value),
                borderColor: "#0d6efd"
            }]
        }
    });

    // ===== PIE =====
    if (pieChart) pieChart.destroy();
    pieChart = new Chart(document.getElementById("pieChart"), {
        type: "pie",
        data: {
            labels: ["Valid", "Invalid"],
            datasets: [{
                data: [ok, notOk],
                backgroundColor: ["#22c55e", "#ef4444"]
            }]
        }
    });

    // ===== GAUGE =====
    if (gaugeChart) gaugeChart.destroy();
    gaugeChart = new Chart(document.getElementById("gaugeChart"), {
        type: "doughnut",
        data: {
            datasets: [{
                data: [defect, 100 - defect],
                backgroundColor: ["#ffc107", "#198754"]
            }]
        },
        options: {
            rotation: -90,
            circumference: 180,
            plugins: { legend: { display: false } }
        }
    });
}