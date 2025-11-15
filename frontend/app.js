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


 // Validation: check language selection
 if (fromSel.value === toSel.value) {
   statusEl.textContent = "Source and target language cannot be the same.";
   return;
  }


  // reset UI
  originalEl.textContent = "";
  translatedEl.textContent = "";
  metricsEl.textContent = "";
  statusEl.textContent = "Requesting microphone…";
 
 
  try {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("This browser doesn’t support microphone capture.");
    }
 
 
    let mimeType = "";
    if (MediaRecorder.isTypeSupported?.("audio/webm;codecs=opus")) {
      mimeType = "audio/webm;codecs=opus";
    } else if (MediaRecorder.isTypeSupported?.("audio/webm")) {
      mimeType = "audio/webm";
    } else if (MediaRecorder.isTypeSupported?.("audio/ogg;codecs=opus")) {
      mimeType = "audio/ogg;codecs=opus";
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
      stream.getTracks().forEach((t) => t.stop());
    };
 
 
    mediaRecorder.start(100);
    tickHandle = setInterval(async () => {
      if (!recording || sendInFlight || !buffers.length) return;
 
 
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
    recording = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
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
 
 
  if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
 };
 async function sendChunk(blob) {
  if (!blob || blob.size === 0) {
    statusEl.textContent = "No audio data to send.";
    return;
  }
 
 
  const form = new FormData();
  form.append("audio", blob, "chunk");
  form.append("from_lang", fromSel.value);
  form.append("to_lang", toSel.value);
 
 
  const t0 = performance.now();
  let res;
 
 
  try {
    res = await fetch(`${API_BASE}/caption`, { method: "POST", body: form });
  } catch (networkErr) {
    console.error(networkErr);
    statusEl.textContent = "Network error while sending chunk.";
    return;
  }
 
 
  const t1 = performance.now();
 
 
  if (!res.ok) {
    const text = await safeText(res);
    console.error("Server error:", text);
    statusEl.textContent = `Server error: ${res.status} ${res.statusText}`;
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
 
 
  if (!data.transcript || !data.translated_text) {
    statusEl.textContent = "Incomplete response from server.";
    return;
  }
 
 
  originalEl.textContent += (originalEl.textContent ? " " : "") + data.transcript;
  translatedEl.textContent += (translatedEl.textContent ? " " : "") + data.translated_text;
 
 
  const net = Math.round(t1 - t0);
  const size = blob.size ?? 0;
  metricsEl.textContent =
    `pair=${data.from_lang}→${data.to_lang} | ` +
    `processing=${data.processing_ms}ms net≈${net}ms chunk=${size}B`;
 
 
  statusEl.textContent = "Recording… sending 3s chunks";
 }
 
 
 async function safeText(res) {
  try {
    return await res.text();
  } catch {
    return "";
  }
 }
   