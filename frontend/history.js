async function loadHistory() {
    const token = localStorage.getItem("jwt");
    if (!token) {
        window.location.href = "/static/login.html";
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
            container.innerHTML = "<p>No captions yet.</p>";
            return;
        }

        items.forEach(item => {
            const block = document.createElement("div");
            block.className = "history-item";
            block.innerHTML = `
                <p><strong>From:</strong> ${item.FromLang} → <strong>To:</strong> ${item.ToLang}</p>
                <p><strong>Original:</strong> ${item.Transcript}</p>
                <p><strong>Translated:</strong> <span class="translated-text">${item.TranslatedText}</span></p>
                <div class="edit-area" style="display:none;">
                    <textarea class="edit-input">${item.TranslatedText}</textarea>
                    <button class="btn save-btn" data-id="${item.Id}">Save</button>
                    <button class="btn cancel-btn">Cancel</button>
                </div>
                <button class="btn edit-btn" data-id="${item.Id}">Edit</button>
                <button class="btn delete-btn" data-id="${item.Id}">Delete</button>
            `;
            container.appendChild(block);
        });

        document.querySelectorAll(".edit-btn").forEach(btn => {
            btn.onclick = () => {
                const parent = btn.parentElement;
                parent.querySelector(".edit-area").style.display = "block";
                parent.querySelector(".translated-text").style.display = "none";
                btn.style.display = "none";
            };
        });

        document.querySelectorAll(".cancel-btn").forEach(btn => {
            btn.onclick = () => {
                const parent = btn.closest(".history-item");
                parent.querySelector(".edit-area").style.display = "none";
                parent.querySelector(".translated-text").style.display = "inline";
                parent.querySelector(".edit-btn").style.display = "inline-block";
            };
        });

        document.querySelectorAll(".save-btn").forEach(btn => {
            btn.onclick = async () => {
                const parent = btn.closest(".history-item");
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