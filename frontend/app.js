// frontend/app.js
const API_BASE = "http://127.0.0.1:8000";
const els = id=>document.getElementById(id);
const startBtn=els("startBtn"),stopBtn=els("stopBtn"),statusEl=els("status");
const originalEl=els("original"),translatedEl=els("translated"),metricsEl=els("metrics");
const fromSel=els("fromLang"),toSel=els("toLang");
let mediaRecorder=null, recording=false;

startBtn.onclick = async () => {
  if(recording) return;
  originalEl.textContent=""; translatedEl.textContent=""; metricsEl.textContent="";
  statusEl.textContent="Requesting mic…";
  const stream = await navigator.mediaDevices.getUserMedia({audio:true});
  mediaRecorder = new MediaRecorder(stream,{mimeType:"audio/webm;codecs=opus"});
  recording=true; startBtn.disabled=true; stopBtn.disabled=false; statusEl.textContent="Recording…";
  let buffers=[]; mediaRecorder.ondataavailable=e=>{if(e.data?.size) buffers.push(e.data);};
  mediaRecorder.onstop=()=>stream.getTracks().forEach(t=>t.stop());
  mediaRecorder.start(100);
  const tick=setInterval(async()=>{
    if(!recording){clearInterval(tick);return;}
    if(buffers.length){
      const blob=new Blob(buffers,{type:"audio/webm"}); buffers=[];
      await sendChunk(blob);
    }
  },3000);
};
stopBtn.onclick=()=>{ if(!recording) return; recording=false; startBtn.disabled=false; stopBtn.disabled=true; statusEl.textContent="Stopped."; mediaRecorder?.stop(); };

async function sendChunk(blob){
  const form=new FormData(); form.append("audio",blob,"chunk.webm");
  const qs=new URLSearchParams({from_lang:fromSel.value,to_lang:toSel.value});
  const t0=performance.now();
  const res=await fetch(`${API_BASE}/transcribe?${qs}`,{method:"POST",body:form});
  const t1=performance.now();
  const data=await res.json();
  originalEl.textContent += (originalEl.textContent?" ":"") + data.original;
  translatedEl.textContent += (translatedEl.textContent?" ":"") + data.translated;
  metricsEl.textContent = `pair=${data.fromLang}→${data.toLang} | stt=${data.sttLatencyMs}ms trans=${data.transLatencyMs}ms total=${data.totalLatencyMs}ms net≈${Math.round(t1-t0)}ms chunk=${data.chunkBytes}B`;
}