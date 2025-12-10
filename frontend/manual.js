document.addEventListener("DOMContentLoaded", () => {
    const inputEl = document.getElementById("manualInput");
    const fromEl = document.getElementById("manualFrom");
    const toEl = document.getElementById("manualTo");
    const resultEl = document.getElementById("manualResult");
    const detectedEl = document.getElementById("detectedLang");
    const translateBtn = document.getElementById("manualBtn");
    const saveBtn = document.getElementById("saveManualBtn");

    const token = localStorage.getItem("jwt");
    if (!token) {
        window.location.href = "/login.html";
        return;
    }

    function rememberPair() {
        const pairLabel = `${fromEl.value.toUpperCase()} → ${toEl.value.toUpperCase()}`;
        localStorage.setItem("preferredPair", pairLabel);
        const now = new Date();
        localStorage.setItem("lastSession", now.toISOString());
        localStorage.setItem("lastSessionHuman", now.toLocaleString());
    }

    function bumpSavedCount() {
        const current = Number(localStorage.getItem("savedTranslationsCount") || 0);
        localStorage.setItem("savedTranslationsCount", current + 1);
    }

    async function translateText() {
        const text = inputEl.value.trim();
        if (!text) return;

        resultEl.textContent = "Translating...";
        detectedEl.textContent = "";

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
            rememberPair();

            // Show detected language if auto-detect
            if (fromEl.value === "auto" && data.detected_language) {
                detectedEl.textContent = `Detected language: ${data.detected_language}`;
            } else {
                detectedEl.textContent = "";
            }

        } catch (err) {
            console.error(err);
            detectedEl.textContent = "";
            resultEl.textContent = "(translation failed)";
            alert("Translation failed");
        }
    }

    async function saveTranslation() {
        const transcript = inputEl.value.trim();
        const translated_text = resultEl.textContent.trim();
        if (!transcript || !translated_text) return;

        try {
            const res = await fetch("/api/manual/save", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    transcript,
                    translated_text,
                    from_lang: fromEl.value,
                    to_lang: toEl.value
                })
            });

            if (!res.ok) throw new Error("Save failed");
            bumpSavedCount();
            alert("Saved!");
        } catch (err) {
            console.error(err);
            alert("Save failed");
        }
    }

    translateBtn.addEventListener("click", translateText);
    saveBtn.addEventListener("click", saveTranslation);
});