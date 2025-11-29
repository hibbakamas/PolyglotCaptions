const inputEl = document.getElementById("manualInput");
const fromEl = document.getElementById("manualFrom");
const toEl = document.getElementById("manualTo");
const resultEl = document.getElementById("manualResult");
const translateBtn = document.getElementById("manualBtn");
const saveBtn = document.getElementById("saveManualBtn");

// TRANSLATE
translateBtn.onclick = async () => {
    const text = inputEl.value.trim();
    if (!text) return;

    const res = await fetch("/api/manual-translate", {
        method: "POST",
        headers: { "Content-Type": "application/json"},
        body: JSON.stringify({
            text,
            from_lang: fromEl.value,
            to_lang: toEl.value
        })
    });

    const data = await res.json();
    resultEl.textContent = data.translated_text || "(no translation)";
};

// SAVE TO DB
saveBtn.onclick = async () => {
    if (!inputEl.value.trim() || !resultEl.textContent.trim()) return;

    await fetch("/api/manual-captions", {
        method: "POST",
        headers: { "Content-Type": "application/json"},
        body: JSON.stringify({
            transcript: inputEl.value,
            translated_text: resultEl.textContent,
            from_lang: fromEl.value,
            to_lang: toEl.value
        })
    });

    alert("Saved!");
};
