const ROUTES = {
  home: "/dashboard",
  record: "/record",
  manual: "/manual",
  history: "/history",
};

const LOGIN_PAGE = "/";

function ensureSession() {
  const token = localStorage.getItem("jwt");
  if (!token) {
    window.location.href = LOGIN_PAGE;
    return null;
  }
  return token;
}

function handleNavigation(target) {
  const destination = ROUTES[target];
  if (!destination) return;
  if (!ensureSession()) return;
  window.location.href = destination;
}

function hydrateDashboard() {
  const token = ensureSession();
  if (!token) return;

  window.currentPolyglotToken = token;

  const sessionChip = document.getElementById("sessionState");
  if (sessionChip) {
    sessionChip.textContent = "Ready";
    sessionChip.classList.remove("status-chip--idle");
    sessionChip.classList.add("status-chip--ready");
  }

  const preferredPair = localStorage.getItem("preferredPair") || "English → Spanish";
  const preferredEl = document.getElementById("preferredPair");
  if (preferredEl) preferredEl.textContent = preferredPair;

  const lastSession = localStorage.getItem("lastSessionHuman") || "No sessions yet";
  const lastSessionEl = document.getElementById("lastSession");
  if (lastSessionEl) lastSessionEl.textContent = lastSession;

  const savedCount = Number(localStorage.getItem("savedTranslationsCount") || 0);
  const savedCountEl = document.getElementById("savedCount");
  if (savedCountEl) savedCountEl.textContent = savedCount;
}

document.addEventListener("DOMContentLoaded", () => {
  const token = ensureSession();
  if (!token) return;

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("jwt");
      window.location.href = LOGIN_PAGE;
    });
  }

  document.querySelectorAll("[data-nav]").forEach((btn) => {
    btn.addEventListener("click", () => handleNavigation(btn.dataset.nav));
    if (btn.dataset.nav === document.body.dataset.page) {
      btn.classList.add("is-active");
    }
  });

  const heroRecord = document.getElementById("heroRecord");
  if (heroRecord) heroRecord.addEventListener("click", () => handleNavigation("record"));

  const heroManual = document.getElementById("heroManual");
  if (heroManual) heroManual.addEventListener("click", () => handleNavigation("manual"));

  hydrateDashboard();
});