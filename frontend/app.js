function ensureLoggedIn() {
  const token = localStorage.getItem("jwt");
  if (!token) {
      alert("Please log in first.");
      window.location.href = "/login.html";
      return false;
  }
  return true;
}

function goRecord() {
  if (!ensureLoggedIn()) return;
  window.location.href = "/record";
}

function goManual() {
  if (!ensureLoggedIn()) return;
  window.location.href = "/manual";
}

function goHistory() {
  if (!ensureLoggedIn()) return;
  window.location.href = "/history";
}