// ==================== THEME TOGGLE ====================
const toggleBtn = document.getElementById("themeToggleBtn");
const icon = document.getElementById("themeIcon");

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
        const res = await fetch("http://127.0.0.1:5000/api/control/status");
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
async function fetchBoxes() {
    try {
        const res = await fetch("http://127.0.0.1:5000/api/stats/summary");
        const data = await res.json();
        console.log("Boxes API response:", data);

        const ok = data.ok || 0;
        const notOk = data.not_ok || 0;
        const total = ok + notOk;

        if (TBoxes) TBoxes.textContent = total;
        if (VBoxes) VBoxes.textContent = ok;
        if (IVBoxes) IVBoxes.textContent = notOk;
        if (DR) DR.textContent = total > 0 ? ((notOk / total) * 100).toFixed(1) + "%" : "0%";

    } catch (e) {
        console.error("Fetch boxes data failed:", e);
        showErrorToast("Error fetching boxes data!");
    }
}

// ==================== TOGGLE FUNCTIONS ====================


const togglePusherBtn = document.getElementById('togglePusherBtn');


async function toggleMotor(typ, toggleTypeBtn) {
    toggleTypeBtn.disabled = true;
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/control/toggle-${typ}`, {
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



async function emergencyStop() {
    emergencyBtn.disabled = true;
    try {
        const response = await fetch("http://127.0.0.1:5000/api/control/emergency", {
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
// ==================== INIT ====================
fetchLineState();
fetchBoxes();
setInterval(fetchLineState, 1000);
setInterval(fetchBoxes, 1000);