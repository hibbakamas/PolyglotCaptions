document.addEventListener("DOMContentLoaded", () => {
    let mediaRecorder;
    let audioChunks = [];

    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");
    const statusEl = document.getElementById("status");
    const originalEl = document.getElementById("original");
    const translatedEl = document.getElementById("translated");

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

    async function sendAudioToBackend() {
        statusEl.textContent = "Processing…";

        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();

        formData.append("audio", audioBlob);
        formData.append("from_lang", document.getElementById("fromLang").value);
        formData.append("to_lang", document.getElementById("toLang").value);

        // Include JWT token in Authorization header
        const token = localStorage.getItem("jwt"); // adjust key if different
        console.log("DEBUG: Token being sent:", token);

        const res = await fetch("/api/captions", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            statusEl.textContent = `Error: ${err.detail || res.statusText}`;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            return;
        }

        const data = await res.json();

        originalEl.textContent = data.transcript || "(no transcript)";
        translatedEl.textContent = data.translated || "(no translation)";

        statusEl.textContent = "Done";
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    stopBtn.onclick = () => {
        mediaRecorder.stop();
        statusEl.textContent = "Stopping…";
    };

    startBtn.onclick = startRecording;
});
