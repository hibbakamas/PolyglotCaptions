async function loadHistory() {
    const token = localStorage.getItem("jwt");
    if (!token) {
        window.location.href = "/";
        return;
    }

    try {
        const res = await fetch("/api/captions", {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) throw new Error("Failed to fetch history");

        const items = await res.json();
        const container = document.getElementById("historyList");
        container.innerHTML = "";

        if (!items || items.length === 0) {
            container.innerHTML = "<p class=\"panel-copy\">No captions yet.</p>";
            return;
        }

        localStorage.setItem("savedTranslationsCount", items.length);

        items.forEach(item => {
            const block = document.createElement("div");
            block.className = "history-card";
            block.innerHTML = `
                <p class="metric-label">Language pair</p>
                <h3>${item.FromLang} → ${item.ToLang}</h3>
                <p><strong>Original</strong><br/>${item.Transcript}</p>
                <p><strong>Translated</strong><br/><span class="translated-text">${item.TranslatedText}</span></p>
                <div class="edit-area" style="display:none;">
                    <textarea class="edit-input">${item.TranslatedText}</textarea>
                    <div class="actions">
                        <button class="btn btn--accent save-btn" data-id="${item.Id}">Save</button>
                        <button class="btn btn--soft cancel-btn">Cancel</button>
                    </div>
                </div>
                <div class="actions">
                    <button class="btn btn--soft edit-btn" data-id="${item.Id}">Edit</button>
                    <button class="btn btn--danger delete-btn" data-id="${item.Id}">Delete</button>
                </div>
            `;
            container.appendChild(block);
        });

        document.querySelectorAll(".edit-btn").forEach(btn => {
            btn.onclick = () => {
                const card = btn.closest(".history-card");
                card.querySelector(".edit-area").style.display = "block";
                card.querySelector(".translated-text").style.display = "none";
                btn.style.display = "none";
            };
        });

        document.querySelectorAll(".cancel-btn").forEach(btn => {
            btn.onclick = () => {
                const parent = btn.closest(".history-card");
                parent.querySelector(".edit-area").style.display = "none";
                parent.querySelector(".translated-text").style.display = "inline";
                parent.querySelector(".edit-btn").style.display = "inline-block";
            };
        });

        document.querySelectorAll(".save-btn").forEach(btn => {
            btn.onclick = async () => {
                const parent = btn.closest(".history-card");
                const id = btn.dataset.id;
                const newText = parent.querySelector(".edit-input").value;

                const resp = await fetch(`/api/captions/${id}`, {
                    method: "PUT",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ translated_text: newText })
                });

                if (!resp.ok) return alert("Failed to update");
                loadHistory();
            };
        });

        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.onclick = async () => {
                const id = btn.dataset.id;
                const del = await fetch(`/api/captions/${id}`, {
                    method: "DELETE",
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (!del.ok) return alert("Failed to delete");
                loadHistory();
            };
        });

    } catch (err) {
        console.error(err);
        document.getElementById("historyList").innerHTML = "<p>Error loading history.</p>";
    }
}

loadHistory();