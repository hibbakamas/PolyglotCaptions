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

    // --------------------------
    // START RECORDING
    // --------------------------
    async function startRecording() {
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
    }

    // --------------------------
    // SEND AUDIO → API
    // --------------------------
    async function sendAudioToBackend() {
        statusEl.textContent = "Processing…";

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();

        formData.append("audio", audioBlob);
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

            const data = await res.json();

            if (!res.ok) {
                statusEl.textContent = `Error: ${data.detail}`;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                return;
            }

            originalEl.textContent = data.transcript || "(no transcript)";
            translatedEl.textContent = data.translated || "(no translation)";
            statusEl.textContent = "Done";

        } catch (err) {
            console.error(err);
            statusEl.textContent = "Error contacting API";
        }

        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    // --------------------------
    // BUTTON HOOKS
    // --------------------------
    stopBtn.onclick = () => {
        mediaRecorder.stop();
        statusEl.textContent = "Stopping…";
    };

    startBtn.onclick = startRecording;
});
