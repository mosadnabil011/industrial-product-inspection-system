const apiurl = "./data.json";
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
const lineState = document.getElementById("lineStatus");
async function fetchlineState() {
    try {
        const res = await fetch(apiurl);
        const data = await res.json();


        lineState.textContent = data[0].status;
        lineState.classList.remove("bg-success", "bg-warning", "bg-danger");
        if (data[0].status === "Running") lineState.classList.add("bg-success");
        else if (data[0].status === "Stopped") lineState.classList.add("bg-warning");
        else lineState.classList.add("bg-danger");

    } catch (error) {
        console.error("Error fetching line status:", error);
        lineState.textContent = "Error";
        lineState.classList.remove("bg-success", "bg-warning");
        lineState.classList.add("bg-danger");
    }
}
// boxes data
const TBoxes = document.getElementById("Total Boxes")
const VBoxes = document.getElementById("Valid Boxes")
const IVBoxes = document.getElementById("Invalid Boxes")
const DR = document.getElementById("Defect Rate")
async function boxes() {
    try {
        const res = await fetch(apiurl);
        const data = await res.json();

        TBoxes.textContent = data[1].TotalBoxes;
        VBoxes.textContent = data[1].ValidBoxes;
        IVBoxes.textContent = data[1].InvalidBoxes;
        DR.textContent = data[1].DefectRate;


    }
    catch (error) {
        console.error("Error fetching Boxes:", error);
    }
}

fetchlineState();
boxes();
setInterval(fetchlineState, 1000);
setInterval(boxes, 1000);















