async function loadHistory() {
    const token = localStorage.getItem("jwt");
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const res = await fetch("/api/captions", {
            headers: { 
                "Authorization": `Bearer ${token}` 
            }
        });

        if (!res.ok) throw new Error("Failed to fetch history");

        const items = await res.json();
        const container = document.getElementById("historyList");
        container.innerHTML = "";

        if (!items || items.length === 0) {
            container.innerHTML = "<p>No captions found.</p>";
            return;
        }

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

        // Delete listeners
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.onclick = async () => {
                const id = btn.getAttribute("data-id");
                if (!confirm("Delete this entry?")) return;

                const delRes = await fetch(`/api/captions/${id}`, {
                    method: "DELETE",
                    headers: { "Authorization": `Bearer ${token}` }
                });

                if (!delRes.ok) {
                    alert("Failed to delete entry");
                    return;
                }

                loadHistory(); // reload list
            };
        });

    } catch (err) {
        console.error(err);
        document.getElementById("historyList").innerHTML =
            "<p>Error loading history.</p>";
    }
}

loadHistory();
