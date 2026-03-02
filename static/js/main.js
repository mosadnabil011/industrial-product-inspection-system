
const toggleBtn = document.getElementById("themeToggleBtn");
const icon = document.getElementById("themeIcon");

// theme toggle
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


// cloabsed sidebar
const btnCollapse = document.getElementById("btnCollapse");
const sidebar = document.getElementById("sidebar");
let savedState = localStorage.getItem("sidebarState");

if (savedState === null) {
    sidebar.classList.add("sidebar-collapsed");
} else if (savedState === "collapsed") {
    sidebar.classList.add("sidebar-collapsed");
}

btnCollapse.addEventListener("click", () => {
    sidebar.classList.toggle("sidebar-collapsed");

    if (sidebar.classList.contains("sidebar-collapsed")) {
        localStorage.setItem("sidebarState", "collapsed");
    } else {
        localStorage.setItem("sidebarState", "expanded");
    }
});


// line status
const apilineStatus = "http://localhost:3000/lineStatus";
const lineState = document.getElementById("lineStatus");
async function fetchlineState() {
    try {
        const res = await fetch(apilineStatus);
        const data = await res.json();


        lineState.textContent = data.status;
        lineState.classList.remove("bg-success", "bg-warning", "bg-danger");
        if (data.status === "Running") lineState.classList.add("bg-success");
        else if (data.status === "Stopped") lineState.classList.add("bg-warning");
        else lineState.classList.add("bg-danger");

    } catch (error) {
        console.error("Error fetching line status:", error);
        lineState.textContent = "Error";
        lineState.classList.remove("bg-success", "bg-warning");
        lineState.classList.add("bg-danger");
    }
}
// boxes data
const apistatistics = "http://localhost:3000/statistics";
const TBoxes = document.getElementById("Total Boxes")
const VBoxes = document.getElementById("Valid Boxes")
const IVBoxes = document.getElementById("Invalid Boxes")
const DR = document.getElementById("Defect Rate")
async function boxes() {
    try {
        const res = await fetch(apistatistics);
        const data = await res.json();

        TBoxes.textContent = data.TotalBoxes;
        VBoxes.textContent = data.ValidBoxes;
        IVBoxes.textContent = data.InvalidBoxes;
        DR.textContent = data.DefectRate;


    }
    catch (error) {
        console.error("Error fetching Boxes:", error);
    }
}
// control
const apiUrlLine = "http://localhost:3000/lines";

async function fetchData() {
    try {
        const res = await fetch(apiUrlLine);
        const data = await res.json();

        data.forEach(machine => updateUI(machine));

    } catch (error) {
        console.error("Error fetching machine data:", error);
    }
}

function updateUI(machine) {
    const element = document.getElementById(`status${machine.id}`);
    if (!element) return;

    element.textContent = machine.status;

    element.classList.remove("btn-success", "btn-danger", "disabled");

    element.classList.add(machine.status === "Running" ? "btn-success" : "btn-danger");
}

async function toggleLine(id) {
    try {
        const res = await fetch(`${apiUrlLine}/${id}`);
        const machine = await res.json();
        if (!machine) return;

        const newStatus = machine.status === "Running" ? "Stopped" : "Running";

        await fetch(`${apiUrlLine}/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });

        updateUI({ id, status: newStatus });

    } catch (error) {
        console.error("Error toggling line:", error);
    }
}
async function emergencyStop() {
    try {
        const res = await fetch(apiUrlLine);
        const data = await res.json();

        for (let machine of data) {
            if (machine.status !== "Stopped") {
                await fetch(`${apiUrlLine}/${machine.id}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status: "Stopped" })
                });

                updateUI({ id: machine.id, status: "Stopped" });
            }
        }

    } catch (error) {
        console.error("Error during emergency stop:", error);
    }
}









fetchlineState();
boxes();
fetchData();
setInterval(fetchlineState, 1000);
setInterval(boxes, 1000);















