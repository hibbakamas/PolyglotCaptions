document.addEventListener("DOMContentLoaded", () => {
    let mediaRecorder;
    let audioChunks = [];

    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");
    const statusEl = document.getElementById("status");
    const originalEl = document.getElementById("original");
    const translatedEl = document.getElementById("translated");

    const token = localStorage.getItem("jwt");
    if (!token) {
        window.location.href = "/";
        return;
    }

    async function startRecording() {
        try {
            audioChunks = [];
            originalEl.textContent = "";
            translatedEl.textContent = "";

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = sendAudioToBackend;

            mediaRecorder.start();

            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusEl.textContent = "Recording…";
        } catch (err) {
            console.error("Microphone error:", err);
            statusEl.textContent = "Microphone access denied or unavailable.";
        }
    }

    async function sendAudioToBackend() {
        statusEl.textContent = "Processing…";

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();

        formData.append("audio", audioBlob, "recording.webm");
        formData.append("from_lang", document.getElementById("fromLang").value);
        formData.append("to_lang", document.getElementById("toLang").value);

        try {
            const res = await fetch("/api/captions", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                statusEl.textContent = `Error: ${err.detail || res.statusText}`;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                return;
            }

            const data = await res.json();

            originalEl.textContent = data.transcript || "(no transcript)";
            translatedEl.textContent = data.translated || "(no translation)";

            const fromValue = document.getElementById("fromLang").value;
            const toValue = document.getElementById("toLang").value;
            const pairLabel = `${fromValue.toUpperCase()} → ${toValue.toUpperCase()}`;
            localStorage.setItem("preferredPair", pairLabel);

            const now = new Date();
            localStorage.setItem("lastSession", now.toISOString());
            localStorage.setItem("lastSessionHuman", now.toLocaleString());

            statusEl.textContent = "Done ✅";
        } catch (error) {
            console.error("Upload failed:", error);
            statusEl.textContent = "Error uploading audio.";
        } finally {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }

    stopBtn.onclick = () => {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            statusEl.textContent = "Stopping…";
        }
    };

    startBtn.onclick = startRecording;
});