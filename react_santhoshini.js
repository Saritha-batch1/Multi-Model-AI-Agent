const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');

const analyzeBtn = document.getElementById('analyzeBtn');
const demoBtn = document.getElementById('demoBtn');

function setStatus(text){
  statusEl.textContent = text;
}

function escapeHtml(str){
  return String(str)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

function renderResult(data){
  const redFlags = (data.red_flags || [])
    .map(x => '<div class="badge danger">' + escapeHtml(x) + '</div>')
    .join(' ');

  const concerns = (data.possible_conditions || [])
    .map(x => '<div class="badge warn">' + escapeHtml(x) + '</div>')
    .join(' ');

  const recs = (data.recommendations || [])
    .map(x => '<li>' + escapeHtml(x) + '</li>')
    .join('');

  const risk = data.risk_level || 'unknown';

  let riskBadge = '<span class="badge ok">' + escapeHtml(risk) + '</span>';
  if (risk === 'moderate') riskBadge = '<span class="badge warn">' + escapeHtml(risk) + '</span>';
  if (risk === 'high') riskBadge = '<span class="badge danger">' + escapeHtml(risk) + '</span>';

  resultEl.innerHTML = ''
    + '<div class="kv"><div>Risk level</div><div>' + riskBadge + '</div></div>'
    + '<div class="kv"><div>Urgent red flags</div><div>' + (redFlags || '<span class="badge ok">none detected</span>') + '</div></div>'
    + '<div class="kv"><div>Possible conditions</div><div>' + (concerns || '<span class="badge ok">none</span>') + '</div></div>'
    + '<div style="margin-top:10px; color: rgba(232,236,255,0.9);">Recommendations</div>'
    + '<ol style="margin-top:6px; color: rgba(168,178,209,1);">' + recs + '</ol>'
    + '<div style="margin-top:10px; color: rgba(168,178,209,1); font-size: 12px;">' + escapeHtml(data.disclaimer || '') + '</div>';
}

function payloadFromForm(){
  return {
    age: Number(document.getElementById('age').value || 0),
    sex: document.getElementById('sex').value,
    symptoms: document.getElementById('symptoms').value,
    vitals: {
      temp_c: Number(document.getElementById('temp_c').value || 0),
      hr: Number(document.getElementById('hr').value || 0),
      rr: Number(document.getElementById('rr').value || 0),
      spo2: Number(document.getElementById('spo2').value || 0)
    }
  };
}

async function analyze(){
  setStatus('Analyzing...');
  resultEl.innerHTML = '';

  const payload = payloadFromForm();

  try{
    const resp = await fetch('http://127.0.0.1:8000/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });

    if(!resp.ok){
      const txt = await resp.text();
      throw new Error('Backend error: ' + resp.status + ' ' + txt);
    }

    const data = await resp.json();
    setStatus('Done.');
    renderResult(data);
  }catch(err){
    setStatus('Error: ' + err.message);
    resultEl.innerHTML = '<div class="badge danger">Could not reach backend. Start it with: python backend.py</div>';
  }
}

function fillDemo(){
  document.getElementById('symptoms').value =
    'Fever and cough for 2 days, sore throat, mild shortness of breath when walking upstairs.';
  document.getElementById('temp_c').value = 38.3;
  document.getElementById('hr').value = 102;
  document.getElementById('rr').value = 22;
  document.getElementById('spo2').value = 95;
}

analyzeBtn.addEventListener('click', analyze);
demoBtn.addEventListener('click', fillDemo);