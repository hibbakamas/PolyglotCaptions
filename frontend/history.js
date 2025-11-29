async function loadHistory() {
    const res = await fetch("/api/captions");
    const items = await res.json();

    const container = document.getElementById("historyList");
    container.innerHTML = "";

    items.forEach(item => {
        const block = document.createElement("div");
        block.className = "history-item";

        block.innerHTML = `
            <p><strong>From:</strong> ${item.FromLang} → <strong>To:</strong> ${item.ToLang}</p>
            <p><strong>Original:</strong> ${item.Transcript}</p>
            <p><strong>Translated:</strong> ${item.TranslatedText}</p>
            <button class="btn delete-btn" data-id="${item.Id}">Delete</button>
        `;

        container.appendChild(block);
    });

    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.onclick = async () => {
            const id = btn.getAttribute("data-id");
            if (!confirm("Delete this entry?")) return;

            await fetch(`/api/captions/${id}`, { method: "DELETE" });
            loadHistory();
        };
    });
}

loadHistory();
