document.addEventListener("DOMContentLoaded", () => {
    const usernameEl = document.getElementById("username");
    const passwordEl = document.getElementById("password");
    const msgEl = document.getElementById("msg");

    document.getElementById("loginBtn").onclick = async () => {
        const username = usernameEl.value.trim();
        const password = passwordEl.value.trim();
        if (!username || !password) return;

        const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("jwt", data.access_token);
            // redirect to main page
            window.location.href = "/static/index.html";
        } else {
            msgEl.textContent = data.detail || "Login failed";
        }
    };

    document.getElementById("registerBtn").onclick = async () => {
        const username = usernameEl.value.trim();
        const password = passwordEl.value.trim();
        if (!username || !password) return;

        const res = await fetch("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (res.ok) {
            msgEl.style.color = "green";
            msgEl.textContent = "Registered! You can login now.";
        } else {
            msgEl.style.color = "red";
            msgEl.textContent = data.detail || "Registration failed";
        }
    };
});
