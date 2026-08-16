from fastapi.responses import HTMLResponse


def demo_page() -> HTMLResponse:
    return HTMLResponse("""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>FaceGate PoC</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; }
    body { margin: 0; background: #0b1220; color: #e5edf8; }
    main { max-width: 1000px; margin: auto; padding: 36px 20px; }
    h1 { margin-bottom: 6px; } .muted { color: #93a4ba; }
    .scenarios { display: flex; flex-wrap: wrap; gap: 10px; margin: 24px 0; }
    button { border: 1px solid #34455d; border-radius: 9px; padding: 10px 14px;
      background: #172337; color: white; cursor: pointer; }
    button:hover { background: #23344f; }
    .panel { background: #111b2c; border: 1px solid #26364d; border-radius: 14px;
      padding: 20px; margin-top: 16px; }
    .pipeline { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
    .step { min-height: 72px; padding: 12px 8px; border-radius: 9px; background: #1a2940;
      text-align: center; font-size: 13px; display: grid; place-content: center; }
    .step span { display: block; color: #91a5bf; margin-top: 5px; }
    .allow { color: #4ade80; } .deny { color: #fb7185; } .manual_review { color: #fbbf24; }
    .result { font-size: 24px; font-weight: 700; }
    pre { overflow: auto; white-space: pre-wrap; color: #bed0e8; }
    table { width: 100%; border-collapse: collapse; }
    td, th { padding: 8px; text-align: left; border-bottom: 1px solid #26364d; }
    @media (max-width: 750px) { .pipeline { grid-template-columns: repeat(2, 1fr); } }
  </style>
</head>
<body><main>
  <h1>FaceGate PoC</h1>
  <div class="muted">Mock CV pipeline · реальный decision engine, fallback, idempotency и audit</div>
  <div class="scenarios">
    <button onclick="run('e-1001')">✓ Happy path</button>
    <button onclick="run('e-1004')">? Близкие кандидаты</button>
    <button onclick="run('e-1003')">⊘ Spoof attempt</button>
    <button onclick="run('e-1005')">⌁ Offline stale cache</button>
  </div>
  <section class="panel">
    <div class="pipeline" id="pipeline">
      <div class="step">Camera event</div><div class="step">Quality</div>
      <div class="step">Liveness</div><div class="step">ANN match</div>
      <div class="step">Decision</div><div class="step">Turnstile</div>
    </div>
  </section>
  <section class="panel" id="outcome"><span class="muted">Выберите сценарий</span></section>
  <section class="panel"><h3>Audit событий этой демонстрации</h3>
    <table><thead><tr><th>Event</th><th>Decision</th><th>Turnstile</th><th>Audit ID</th></tr></thead>
    <tbody id="audit"><tr><td colspan="4" class="muted">Пока пусто</td></tr></tbody></table>
  </section>
  <section class="panel"><details><summary>Полный ответ API</summary><pre id="raw">—</pre></details></section>
</main>
<script>
const scenarios = {
  'e-1001': {network:'online', cache_age_minutes:0},
  'e-1003': {network:'online', cache_age_minutes:0},
  'e-1004': {network:'online', cache_age_minutes:0},
  'e-1005': {network:'offline', cache_age_minutes:240}
};
const seen = new Map();
async function run(eventId) {
  const payload = {event_id:eventId, gate_id:'gate-2', camera_id:'cam-2a',
    captured_at:new Date().toISOString(), frame_uri:`file://demo/frames/${eventId}.jpg`,
    metadata:{direction:'in', illumination:'normal', edge_node:'edge-gate-2', ...scenarios[eventId]}};
  const response = await fetch('/v1/access/verify', {method:'POST',
    headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await response.json();
  if (!response.ok) { document.querySelector('#outcome').innerHTML = `<pre>${JSON.stringify(data,null,2)}</pre>`; return; }
  const q = data.quality;
  document.querySelector('#pipeline').innerHTML = `
    <div class="step">Camera event<span>${data.event_id}</span></div>
    <div class="step">Quality<span>${q.quality_score} / min 0.60</span></div>
    <div class="step">Liveness<span>${q.liveness_score} / allow 0.75</span></div>
    <div class="step">ANN match<span>${data.match_score}; margin ${data.margin_to_second_best}</span></div>
    <div class="step">Decision<span class="${data.decision}">${data.decision}</span></div>
    <div class="step">Turnstile<span class="${data.decision}">${data.turnstile_command}</span></div>`;
  document.querySelector('#outcome').innerHTML = `<div class="result ${data.decision}">${data.decision} → ${data.turnstile_command}</div>
    <p>${data.reasons.join(' · ')}</p><span class="muted">employee: ${data.employee_id ?? 'не определён'} · latency: ${data.latency_ms} ms</span>`;
  document.querySelector('#raw').textContent = JSON.stringify(data, null, 2);
  seen.set(data.event_id, data);
  document.querySelector('#audit').innerHTML = [...seen.values()].map(x =>
    `<tr><td>${x.event_id}</td><td class="${x.decision}">${x.decision}</td><td>${x.turnstile_command}</td><td>${x.audit_id}</td></tr>`).join('');
}
</script></body></html>""")
