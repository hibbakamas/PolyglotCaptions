// app.js – WAV recording version (works with Azure STT)

const API_BASE = window.location.origin;

const $ = (id) => document.getElementById(id);
const startBtn = $("startBtn");
const stopBtn = $("stopBtn");
const statusEl = $("status");
const originalEl = $("original");
const translatedEl = $("translated");
const metricsEl = $("metrics");
const fromSel = $("fromLang");
const toSel = $("toLang");
const buildMetaEl = $("buildMeta");

let recording = false;
let audioChunks = [];
let mediaRecorder = null;
let tickHandle = null;
let sendInFlight = false;

if (buildMetaEl) buildMetaEl.textContent = "local";

startBtn.onclick = async () => {
  if (recording) return;

  if (fromSel.value === toSel.value) {
    statusEl.textContent = "Source and target language cannot be the same.";
    return;
  }

  originalEl.textContent = "";
  translatedEl.textContent = "";
  metricsEl.textContent = "";
  statusEl.textContent = "Requesting microphone…";

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Force WAV recording (uncompressed PCM)
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: "audio/wav",
    });

    recording = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;

    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
    };

    mediaRecorder.start(100); // gather PCM chunks

    tickHandle = setInterval(async () => {
      if (!recording || sendInFlight || audioChunks.length === 0) return;

      const blob = new Blob(audioChunks, { type: "audio/wav" });
      audioChunks = [];

      sendInFlight = true;
      await sendChunk(blob);
      sendInFlight = false;

    }, 3000);

    statusEl.textContent = "Recording… sending 3s WAV chunks";

  } catch (err) {
    console.error("Mic error:", err);
    statusEl.textContent = err.message || "Microphone access error.";
  }
};

stopBtn.onclick = () => {
  if (!recording) return;
  recording = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;

  if (tickHandle) clearInterval(tickHandle);
  tickHandle = null;

  if (mediaRecorder && mediaRecorder.state !== "inactive")
    mediaRecorder.stop();

  statusEl.textContent = "Stopped.";
};

async function sendChunk(blob) {
  if (!blob || blob.size === 0) {
    statusEl.textContent = "No audio data.";
    return;
  }

  const form = new FormData();
  form.append("audio", blob, "chunk.wav");
  form.append("from_lang", fromSel.value);
  form.append("to_lang", toSel.value);

  const t0 = performance.now();
  let res;

  try {
    res = await fetch(`${API_BASE}/api/caption`, { method: "POST", body: form });
  } catch (err) {
    console.error("Network error:", err);
    statusEl.textContent = "Network error sending chunk.";
    return;
  }

  const t1 = performance.now();

  if (!res.ok) {
    const txt = await res.text();
    console.error("Server error:", txt);
    statusEl.textContent = `Server error ${res.status}`;
    return;
  }

  const data = await res.json();

  originalEl.textContent += (originalEl.textContent ? " " : "") + data.transcript;
  translatedEl.textContent += (translatedEl.textContent ? " " : "") + data.translated_text;

  metricsEl.textContent =
    `pair=${data.from_lang}→${data.to_lang} | ` +
    `processing=${data.processing_ms}ms net≈${Math.round(t1 - t0)}ms chunk=${blob.size}`;

  statusEl.textContent = "Recording… sending 3s WAV chunks";
}
