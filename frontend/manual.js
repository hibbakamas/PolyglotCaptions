document.addEventListener("DOMContentLoaded", () => {
    const inputEl = document.getElementById("manualInput");
    const fromEl = document.getElementById("manualFrom");
    const toEl = document.getElementById("manualTo");
    const resultEl = document.getElementById("manualResult");
    const translateBtn = document.getElementById("manualBtn");
    const saveBtn = document.getElementById("saveManualBtn");

    const token = localStorage.getItem("jwt");
    if (!token) {
        window.location.href = "/static/login.html";
        return;
    }

    translateBtn.onclick = async () => {
        const text = inputEl.value.trim();
        if (!text) return;

        try {
            const res = await fetch("/api/manual/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    text,
                    from_lang: fromEl.value,
                    to_lang: toEl.value
                })
            });

            const data = await res.json();
            resultEl.textContent = data.translated_text || "(no translation)";
        } catch (err) {
            console.error(err);
            alert("Translation failed");
        }
    };

    saveBtn.onclick = async () => {
        if (!inputEl.value.trim() || !resultEl.textContent.trim()) return;

        try {
            const res = await fetch("/api/manual/save", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    transcript: inputEl.value,
                    translated_text: resultEl.textContent,
                    from_lang: fromEl.value,
                    to_lang: toEl.value
                })
            });

            if (!res.ok) throw new Error("Save failed");
            alert("Saved!");
        } catch (err) {
            console.error(err);
            alert("Save failed");
        }
    };
});
