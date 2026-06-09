
const PANEL_PASSWORD = "goodfactory";

// ---- helpers ----
function isLoggedIn() {
  return sessionStorage.getItem("auth") === "true";
}

function setLoggedIn() {
  sessionStorage.setItem("auth", "true");
}

function logout() {
  sessionStorage.removeItem("auth");
  window.location.replace("login.html");
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.replace("login.html");
  }
}

// ---- login page logic ----
(function initLoginPage() {
  const form = document.getElementById("loginForm");
  if (!form) return;
  if (isLoggedIn()) {
    window.location.replace("dashboard.html");
    return;
  }

  const pwdInput = document.getElementById("password");
  const toggleBtn = document.getElementById("togglePwd");
  const eyeIcon = document.getElementById("eyeIcon");
  const errorAlert = document.getElementById("errorAlert");
  const loginBtn = document.getElementById("loginBtn");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");

  // إظهار / إخفاء الباسورد
  toggleBtn.addEventListener("click", () => {
    const isHidden = pwdInput.type === "password";
    pwdInput.type = isHidden ? "text" : "password";
    eyeIcon.className = isHidden ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
  });

  // submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const pwd = pwdInput.value.trim();

    if (!pwd) {
      showError("Please enter the password.");
      return;
    }

    // loading state
    loginBtn.disabled = true;
    btnText.classList.add("d-none");
    btnSpinner.classList.remove("d-none");

    await new Promise(r => setTimeout(r, 700));

    if (pwd === PANEL_PASSWORD) {
      setLoggedIn();
      window.location.replace("dashboard.html");
    } else {
      loginBtn.disabled = false;
      btnText.classList.remove("d-none");
      btnSpinner.classList.add("d-none");
      showError("Wrong password. Try again.");
      pwdInput.value = "";
      pwdInput.focus();
    }
  });

  function showError(msg) {
    document.getElementById("errorMsg").textContent = msg;
    errorAlert.classList.remove("d-none");
    errorAlert.classList.add("shake");
    setTimeout(() => errorAlert.classList.remove("shake"), 400);
  }
})();
