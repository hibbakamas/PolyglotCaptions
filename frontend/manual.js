document.addEventListener("DOMContentLoaded", () => {
    const inputEl = document.getElementById("manualInput");
    const fromEl = document.getElementById("manualFrom");
    const toEl = document.getElementById("manualTo");
    const resultEl = document.getElementById("manualResult");
    const translateBtn = document.getElementById("manualBtn");
    const saveBtn = document.getElementById("saveManualBtn");

    // Check auth
    const token = localStorage.getItem("jwt");
    if (!token) {
        window.location.href = "/";
        return;
    }

    // -------------------------------
    // TRANSLATE BUTTON
    // -------------------------------
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

            if (!res.ok) {
                resultEl.textContent = data.detail || "Translation failed";
                return;
            }

            resultEl.textContent = data.translated_text || "(No translation)";
        } catch (err) {
            console.error(err);
            resultEl.textContent = "Error contacting API";
        }
    };

    // -------------------------------
    // SAVE BUTTON
    // -------------------------------
    saveBtn.onclick = async () => {
        const original = inputEl.value.trim();
        const translated = resultEl.textContent.trim();

        if (!original || !translated) return;

        try {
            const res = await fetch("/api/manual/save", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    transcript: original,
                    translated_text: translated,
                    from_lang: fromEl.value,
                    to_lang: toEl.value
                })
            });

            if (!res.ok) {
                alert("Save failed");
                return;
            }

            alert("Saved!");
        } catch (err) {
            console.error(err);
            alert("Error saving entry");
        }
    };
});
