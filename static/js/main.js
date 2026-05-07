const api_url = "http://127.0.0.1:5000";
// ==================== THEME TOGGLE ====================
const toggleBtn = document.getElementById("themeToggleBtn");
const icon = document.getElementById("themeIcon");
// let lastOk = null;
// let lastNotOk = null;
if (localStorage.getItem("theme")) {
    document.body.className = localStorage.getItem("theme");
    updateIcon();
}

toggleBtn.addEventListener("click", () => {
    if (document.body.classList.contains("dark")) {
        document.body.className = "light";
        localStorage.setItem("theme", "light");
    } else {
        document.body.className = "dark";
        localStorage.setItem("theme", "dark");
    }
    updateIcon();
});

function updateIcon() {
    if (document.body.classList.contains("dark")) {
        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon");
    } else {
        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun");
    }
}
///////////
const lineCtx = document.getElementById('lineChart');
const barCtx = document.getElementById('barChart');
const pieCtx = document.getElementById('pieChart');

const colorGood = '#1abc9c';
const colorBad = '#ffaf32';
// LINE

const lineChart = new Chart(lineCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Valid',
                data: [],
                borderColor: colorGood,
                tension: 0.3
            },
            {
                label: 'Invalid',
                data: [],
                borderColor: colorBad,
                tension: 0.3
            }
        ]
    },
    options: {
        responsive: false,
        plugins: {
            legend: { display: true }
        },
        scales: {
            y: { beginAtZero: true }
        }
    }
});
// pie
const pieChart = new Chart(pieCtx, {
    type: 'doughnut',
    data: {
        labels: ['Valid', 'Invalid'],
        datasets: [{
            data: [0, 0],
            backgroundColor: [colorGood, colorBad]
        }]
    },
    options: {
        cutout: '0%',
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    },
    plugins: [{
        id: 'percentText',
        afterDraw(chart) {
            const { ctx, chartArea } = chart;
            const data = chart.data.datasets[0].data;

            const total = data.reduce((a, b) => a + b, 0);

            if (total === 0) return;

            const meta = chart.getDatasetMeta(0);

            ctx.save();
            ctx.font = "bold 14px sans-serif";
            ctx.textAlign = "center";
            ctx.fillStyle = "#fff";

            meta.data.forEach((arc, index) => {
                const value = data[index];
                if (!value) return;

                const percent = ((value / total) * 100).toFixed(1) + "%";

                const pos = arc.tooltipPosition();

                ctx.fillText(percent, pos.x, pos.y);
            });

            ctx.restore();
        }
    }]
});

// BAR
// const barChart = new Chart(barCtx, {
//     type: 'bar',
//     data: {
//         labels: ['Valid', 'Invalid'],
//         datasets: [{
//             data: [0, 0],
//             backgroundColor: [colorGood, colorBad],
//             borderRadius: 8
//         }]
//     },
//     options: {
//         plugins: {
//             legend: { display: false }
//         },
//         scales: {
//             y: {
//                 beginAtZero: true
//             }
//         }
//     },
//     plugins: [{
//         id: 'labelPlugin',
//         afterDatasetsDraw(chart) {
//             const { ctx } = chart;
//             chart.data.datasets.forEach((dataset, i) => {
//                 const meta = chart.getDatasetMeta(i);
//                 meta.data.forEach((bar, index) => {
//                     const value = dataset.data[index];
//                     ctx.fillStyle = "#000";
//                     ctx.font = "bold 14px sans-serif";
//                     ctx.textAlign = "center";
//                     ctx.fillText(value, bar.x, bar.y - 5);
//                 });
//             });
//         }
//     }]
// });
const barChart = new Chart(barCtx, {
    type: 'bar',
    data: {
        labels: [],

        datasets: [
            {
                label: 'Valid',
                data: [],
                backgroundColor: colorGood,
                borderRadius: 8,
                barThickness: 'flex'
            },
            {
                label: 'Invalid',
                data: [],
                backgroundColor: colorBad,
                borderRadius: 8,
                barThickness: 'flex'
            }
        ]
    },
    options: {
        plugins: {
            legend: { display: true }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
function updateCharts(ok, notOk) {
    pieChart.data.datasets[0].data = [ok, notOk];
    pieChart.update();


}

// ==================== SIDEBAR COLLAPSE ====================
const btnCollapse = document.getElementById("btnCollapse");
const sidebar = document.getElementById("sidebar");
let savedState = localStorage.getItem("sidebarState");

if (savedState === "collapsed") sidebar.classList.add("sidebar-collapsed");

btnCollapse.addEventListener("click", () => {
    sidebar.classList.toggle("sidebar-collapsed");
    localStorage.setItem("sidebarState", sidebar.classList.contains("sidebar-collapsed") ? "collapsed" : "expanded");
});

// ==================== ELEMENTS ====================
const lineState = document.getElementById("lineStatus");
const mainStatus = document.getElementById("mainStatus");
const badStatus = document.getElementById("badStatus");
const pusherStatus = document.getElementById("pusherStatus");

const TBoxes = document.getElementById("TotalBoxes");
const VBoxes = document.getElementById("ValidBoxes");
const IVBoxes = document.getElementById("InvalidBoxes");
const DR = document.getElementById("DefectRate");

const toggleMainBtn = document.getElementById("toggleMainBtn");
const toggleBadBtn = document.getElementById("toggleBadBtn");
const toggleMotorBtn = document.getElementById("toggleMotorBtn");
const emergencyBtn = document.getElementById("emergencyBtn");

// ==================== TOAST FUNCTION ====================
function showErrorToast(msg) {
    const toastEl = document.getElementById("errorToast");
    if (!toastEl) return;
    toastEl.querySelector(".toast-body").textContent = msg;
    new bootstrap.Toast(toastEl).show();
}

// ==================== FETCH LINE STATUS ====================
async function fetchLineState() {
    try {
        const res = await fetch(`${api_url}/api/control/status`);
        const data = await res.json();
        console.log("Line API response:", data);

        const anyRunning = data.main || data.bad || data.pusher;
        if (lineState) lineState.textContent = anyRunning ? "Running" : "Stopped";
        if (lineState) lineState.className = "badge " + (anyRunning ? "bg-success" : "bg-danger");

        if (mainStatus) mainStatus.textContent = data.main ? "Running" : "Stopped";
        if (mainStatus) mainStatus.className = data.main ? "badge bg-success" : "badge bg-warning";

        if (badStatus) badStatus.textContent = data.bad ? "Running" : "Stopped";
        if (badStatus) badStatus.className = data.bad ? "badge bg-danger" : "badge bg-secondary";

        if (pusherStatus) pusherStatus.textContent = data.pusher ? "Running" : "Stopped";
        if (pusherStatus) pusherStatus.className = data.pusher ? "badge bg-primary" : "badge bg-secondary";


        updateButton(toggleMainBtn, data.main);
        updateButton(toggleBadBtn, data.bad);
        updateButton(togglePusherBtn, data.pusher);

    } catch (e) {
        console.error("Fetch line status failed:", e);
        showErrorToast("Error fetching line status!");
    }
}

function updateButton(btn, state) {
    if (!btn) return;

    if (state) {
        btn.textContent = "RUNNING";
        btn.classList.remove("btn-danger");
        btn.classList.add("btn-success");
    } else {
        btn.textContent = "STOP";
        btn.classList.remove("btn-success");
        btn.classList.add("btn-danger");
    }
}

// ==================== FETCH BOXES ====================
// async function fetchBoxes() {
//     try {
//         const res = await fetch(`${api_url}/api/stats/summary`);
//         const data = await res.json();
//         console.log("Boxes API response:", data);

//         const ok = data.ok || 0;
//         const notOk = data.not_ok || 0;
//         const total = ok + notOk;

//         if (TBoxes) TBoxes.textContent = total;
//         if (VBoxes) VBoxes.textContent = ok;
//         if (IVBoxes) IVBoxes.textContent = notOk;
//         if (DR) DR.textContent = total > 0 ? ((notOk / total) * 100).toFixed(1) + "%" : "0%";

//     } catch (e) {
//         console.error("Fetch boxes data failed:", e);
//         showErrorToast("Error fetching boxes data!");
//     }
// }


// let timeIndex = 0;

async function fetchBoxes() {
    try {
        const res = await fetch(`${api_url}/api/stats/summary`);
        const data = await res.json();

        const ok = data.ok || 0;
        const notOk = data.not_ok || 0;
        const total = ok + notOk;

        // UI
        TBoxes.textContent = total;
        VBoxes.textContent = ok;
        IVBoxes.textContent = notOk;
        DR.textContent = total > 0 ? ((notOk / total) * 100).toFixed(1) + "%" : "0%";

        // ================= Charts Update =================

        // Pie + Bar
        // pieChart.data.datasets[0].data = [ok, notOk];
        // barChart.data.datasets[0].data = [ok, notOk];

        // pieChart.update();
        // barChart.update();
        updateCharts(ok, notOk);

        // timeIndex++;

        // lineChart.data.labels.push(timeIndex);
        // lineChart.data.datasets[0].data.push(ok);
        // lineChart.data.datasets[1].data.push(notOk);

        // if (lineChart.data.labels.length > 20) {
        //     lineChart.data.labels.shift();
        //     lineChart.data.datasets[0].data.shift();
        //     lineChart.data.datasets[1].data.shift();
        // }

        // lineChart.update();
        //last
        // if (lastOk === null || ok !== lastOk || notOk !== lastNotOk) {

        //     /* The above code is incrementing the value of the variable `timeIndex` by 1. */
        //     timeIndex++;

        //     lineChart.data.labels.push(timeIndex);
        //     lineChart.data.datasets[0].data.push(ok);
        //     lineChart.data.datasets[1].data.push(notOk);

        //     if (lineChart.data.labels.length > 50) {
        //         lineChart.data.labels.shift();
        //         lineChart.data.datasets[0].data.shift();
        //         lineChart.data.datasets[1].data.shift();
        //     }

        //     lineChart.update();
        //     lineCtx.style.width = `${lineChart.data.labels.length * 80}px`;
        //     lastOk = ok;
        //     lastNotOk = notOk;
        // }

    } catch (e) {
        console.error("Fetch boxes data failed:", e);
    }
}

async function fetchWeekly() {
    try {

        const res = await fetch(`${api_url}/api/stats/weekly`);
        const data = await res.json();

        if (!data.weeks || !data.valid || !data.invalid) return;

        lineChart.data.labels = data.weeks;

        lineChart.data.datasets[0].data = data.valid;
        lineChart.data.datasets[1].data = data.invalid;

        lineChart.update();

        // Scroll Width
        lineCtx.style.width = `${data.weeks.length * 120}px`;

    } catch (e) {
        console.error("Weekly fetch error:", e);
    }
}
async function fetchMonthly() {
    try {
        const res = await fetch(`${api_url}/api/stats/monthly`);
        const data = await res.json();

        if (!data.months || !data.valid || !data.invalid) return;

        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

        barChart.data.labels = data.months.map(m => monthNames[parseInt(m) - 1]);
        barChart.data.datasets[0].data = data.valid;
        barChart.data.datasets[1].data = data.invalid;

        barChart.update();
        barCtx.style.width = `${data.months.length * 120}px`;

    } catch (e) {
        console.error("Monthly fetch error:", e);
    }
}
// ==================== TOGGLE FUNCTIONS ====================


const togglePusherBtn = document.getElementById('togglePusherBtn');


async function toggleMotor(typ, toggleTypeBtn) {
    toggleTypeBtn.disabled = true;
    try {
        const response = await fetch(`${api_url}/api/control/toggle-${typ}`, {
            method: 'POST',
        });
        const data = await response.json();

        if (data[`${typ}_motor`] === true) {
            toggleTypeBtn.textContent = 'RUNNING';
            toggleTypeBtn.classList.remove('btn-danger');
            toggleTypeBtn.classList.add('btn-success');

        } else {
            toggleTypeBtn.textContent = 'STOP';

            toggleTypeBtn.classList.remove('btn-success');
            toggleTypeBtn.classList.add('btn-danger');

        }
    } catch (err) {
        console.error('Error toggling motor:', err);
    } finally {
        toggleTypeBtn.disabled = false;
    }
}


async function togglePusher(button) {
    button.disabled = true;

    try {
        const res = await fetch(`${api_url}/api/control/status`);
        const data = await res.json();

        if (data.pusher) {
            await fetch(`${api_url}/api/control/stop-pusher`, {
                method: "POST"
            });

            button.textContent = "RUN PUSHER";
            button.classList.remove("btn-success");
            button.classList.add("btn-danger");

        } else {
            await fetch(`${api_url}/api/control/run-pusher`, {
                method: "POST"
            });

            button.textContent = "STOP PUSHER";
            button.classList.remove("btn-danger");
            button.classList.add("btn-success");
        }

    } catch (err) {
        console.error(err);
    } finally {
        button.disabled = false;
    }
}



async function emergencyStop() {
    emergencyBtn.disabled = true;
    try {
        const response = await fetch(`${api_url}/api/control/emergency`, {
            method: 'POST',
        });
        const data = await response.json();
        togglePusherBtn.textContent = 'STOP';
        togglePusherBtn.classList.add('btn-danger');
        togglePusherBtn.classList.remove('btn-success');

        toggleBadBtn.textContent = 'STOP';
        toggleBadBtn.classList.add('btn-danger');
        toggleBadBtn.classList.remove('btn-success');

        toggleMainBtn.textContent = 'STOP';
        toggleMainBtn.classList.add('btn-danger');
        toggleMainBtn.classList.remove('btn-success');

    } catch (err) {
        console.error('Error toggling motor:', err);
    } finally {
        emergencyBtn.disabled = false;
    }
}

// ==================== CHARTS ====================


async function generateReport() {
    const date = document.getElementById("reportDate").value;

    if (!date) {
        alert("Please select a date");
        return;
    }

    // فتح PDF في تاب جديدة
    window.open(`${api_url}/api/report?date=${date}`, "_blank");
}
// ==================== INIT ====================
fetchLineState();
fetchBoxes();
fetchMonthly();
fetchWeekly();
setInterval(fetchLineState, 1000);
setInterval(fetchBoxes, 1000);
setInterval(fetchMonthly, 60000);
setInterval(fetchWeekly, 300000);
