// frontend/app.js
const API_BASE = "http://127.0.0.1:8000";

const $ = (id) => document.getElementById(id);
const startBtn = $("startBtn");
const stopBtn = $("stopBtn");
const statusEl = $("status");
const originalEl = $("original");
const translatedEl = $("translated");
const metricsEl = $("metrics");
const fromSel = $("fromLang");
const toSel = $("toLang");

let mediaRecorder = null;
let recording = false;
let tickHandle = null;
let sendInFlight = false;

startBtn.onclick = async () => {
  if (recording) return;

  // reset UI
  originalEl.textContent = "";
  translatedEl.textContent = "";
  metricsEl.textContent = "";
  statusEl.textContent = "Requesting microphone…";

  try {
    // feature checks
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("This browser doesn’t support microphone capture.");
    }

    // pick a supported mime type
    let mimeType = "";
    if (MediaRecorder.isTypeSupported?.("audio/webm;codecs=opus")) {
      mimeType = "audio/webm;codecs=opus";
    } else if (MediaRecorder.isTypeSupported?.("audio/webm")) {
      mimeType = "audio/webm";
    } else if (MediaRecorder.isTypeSupported?.("audio/ogg;codecs=opus")) {
      mimeType = "audio/ogg;codecs=opus";
    } else {
      // fallback: let browser choose; backend should handle/convert if needed
      mimeType = "";
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);

    recording = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    statusEl.textContent = "Recording… sending 3s chunks";

    let buffers = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) buffers.push(e.data);
    };

    mediaRecorder.onstop = () => {
      // stop tracks to release mic permission light
      stream.getTracks().forEach((t) => t.stop());
    };

    // start collecting micro-chunks
    mediaRecorder.start(100);

    // send a chunk every 3 seconds
    tickHandle = setInterval(async () => {
      if (!recording) return;
      if (!buffers.length) return;
      if (sendInFlight) return; // avoid overlapping uploads if network is slow

      const blob = new Blob(buffers, { type: mimeType || "audio/webm" });
      buffers = [];
      try {
        sendInFlight = true;
        await sendChunk(blob);
      } finally {
        sendInFlight = false;
      }
    }, 3000);
  } catch (err) {
    console.error(err);
    statusEl.textContent = err?.message || "Microphone error.";
    // ensure UI back to idle
    recording = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      try { mediaRecorder.stop(); } catch {}
    }
    if (tickHandle) {
      clearInterval(tickHandle);
      tickHandle = null;
    }
  }
};

stopBtn.onclick = () => {
  if (!recording) return;
  recording = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  statusEl.textContent = "Stopped.";

  if (tickHandle) {
    clearInterval(tickHandle);
    tickHandle = null;
  }
  try {
    if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
  } catch {}
};

async function sendChunk(blob) {
  const form = new FormData();
  form.append("audio", blob, "chunk");

  const qs = new URLSearchParams({
    from_lang: fromSel.value,
    to_lang: toSel.value,
  });

  const t0 = performance.now();
  let res;
  try {
    res = await fetch(`${API_BASE}/transcribe?${qs}`, {
      method: "POST",
      body: form,
    });
  } catch (networkErr) {
    console.error(networkErr);
    statusEl.textContent = "Network error while sending chunk.";
    return;
  }
  const t1 = performance.now();

  if (!res.ok) {
    const text = await safeText(res);
    console.error("Server error:", text);
    statusEl.textContent = "Server error during transcription.";
    return;
  }

  let data;
  try {
    data = await res.json();
  } catch (parseErr) {
    console.error(parseErr);
    statusEl.textContent = "Invalid server response.";
    return;
  }

  // Append texts
  if (data?.original) {
    originalEl.textContent += (originalEl.textContent ? " " : "") + data.original;
  }
  if (data?.translated) {
    translatedEl.textContent += (translatedEl.textContent ? " " : "") + data.translated;
  }

  // Metrics line
  const net = Math.round(t1 - t0);
  const stt = data?.sttLatencyMs ?? 0;
  const trans = data?.transLatencyMs ?? 0;
  const total = data?.totalLatencyMs ?? 0;
  const size = data?.chunkBytes ?? blob.size ?? 0;

  metricsEl.textContent =
    `pair=${data?.fromLang || fromSel.value}→${data?.toLang || toSel.value} | ` +
    `stt=${stt}ms trans=${trans}ms total=${total}ms net≈${net}ms chunk=${size}B`;
}

// helper
async function safeText(res) {
  try { return await res.text(); } catch { return ""; }
}