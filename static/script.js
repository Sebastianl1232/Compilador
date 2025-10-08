const runBtn = document.getElementById('run');
const codeTA = document.getElementById('code');
const spinner = document.getElementById('spinner');
const status = document.getElementById('status');

// --- Paletas de color ---
// Definimos varias paletas con variables CSS. La UI aplica una paleta
// automáticamente y la almacena en localStorage para rotarla en la próxima visita.
const palettes = {
  soft: {
    '--bg': 'linear-gradient(180deg,#f6fbff 0%, #f3f6fb 40%, #fbfbfd 100%)',
    '--card': '#ffffff',
    '--primary': '#2563eb',
    '--muted': '#6b7280',
    '--output-bg': 'linear-gradient(180deg,#f8fbff 0%, #f6f9fb 100%)',
    '--btn-bg': '#2563eb',
    '--btn-text': '#ffffff',
    '--border': 'rgba(15,23,42,0.04)'
  },
  warm: {
    '--bg': 'linear-gradient(180deg,#fff8f5 0%, #fdf6f2 40%, #fffdfc 100%)',
    '--card': '#fffaf8',
    '--primary': '#d97706',
    '--muted': '#6b4b3b',
    '--output-bg': 'linear-gradient(180deg,#fffaf6 0%, #fff6f2 100%)',
    '--btn-bg': '#d97706',
    '--btn-text': '#ffffff',
    '--border': 'rgba(107,77,59,0.06)'
  },
  cool: {
    '--bg': 'linear-gradient(180deg,#f7fbff 0%, #f3f9fe 40%, #fbfdff 100%)',
    '--card': '#f8fcff',
    '--primary': '#0ea5e9',
    '--muted': '#4b6b7a',
    '--output-bg': 'linear-gradient(180deg,#f2fbff 0%, #eef9fe 100%)',
    '--btn-bg': '#0ea5e9',
    '--btn-text': '#ffffff',
    '--border': 'rgba(65,100,120,0.06)'
  }
};

function applyPalette(name){
  const root = document.documentElement;
  const p = palettes[name] || palettes.soft;
  Object.keys(p).forEach(k => root.style.setProperty(k, p[k]));
}

// Auto-rotar paleta en cada visita
try{
  const keys = Object.keys(palettes);
  const saved = localStorage.getItem('comp_theme');
  let next;
  if(saved && keys.includes(saved)){
    const idx = keys.indexOf(saved);
    next = keys[(idx + 1) % keys.length];
  } else {
    // elegir aleatorio si no hay guardado
    next = keys[Math.floor(Math.random() * keys.length)];
  }
  applyPalette(next);
  localStorage.setItem('comp_theme', next);
}catch(e){ applyPalette('soft'); }
// el editor simple (textarea). A continuación la funcionalidad de copiar
// contenido de cualquiera de los paneles usando botones con data-target.
document.addEventListener('click', (e)=>{
  const btn = e.target.closest('.copy-btn');
  if(!btn) return;
  const target = btn.getAttribute('data-target');
  const el = document.getElementById(target);
  if(!el) return;
  const text = el.textContent || el.innerText || '';
  // navigator.clipboard requiere HTTPS en producción; en localhost funciona.
  navigator.clipboard.writeText(text).then(()=>{
    btn.textContent = 'Copiado';
    setTimeout(()=>btn.textContent = 'Copiar',1200);
  }).catch(()=>{
    btn.textContent = 'Error';
    setTimeout(()=>btn.textContent = 'Copiar',1200);
  });
});

runBtn.addEventListener('click', async () => {
  const code = codeTA.value;
  // show spinner and disable inputs
  runBtn.disabled = true;
  codeTA.disabled = true;
  spinner.style.display = 'inline-block';
  status.textContent = 'Compilando...';
  try{
    const res = await fetch('/compile', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code})
    });
    const data = await res.json();
    // tokens
    document.getElementById('tokens').textContent = data.lex ? (Array.isArray(data.lex) ? data.lex.join('\n') : data.lex) : JSON.stringify(data.tokens || {}, null, 2);
    // parse / ast
    if (data.parse_text_centered) {
      document.getElementById('ast').textContent = data.parse_text_centered;
    } else if (data.parse_text) {
      document.getElementById('ast').textContent = data.parse_text;
    } else {
      document.getElementById('ast').textContent = JSON.stringify(data.ast || {}, null, 2);
    }
    // semantic
    if (data.semantic) {
      const sem = data.semantic;
      let out = '';
      out += `Verificación: ${sem.ok ? 'OK' : 'FALLÓ'} - ${sem.message}\n\n`;
      out += 'Symbols:\n';
      for (const k of Object.keys(sem.symbols || {})) {
        out += `  ${k}\n`;
      }
      out += '\nErrors:\n';
      if (sem.errors && sem.errors.length) {
        for (const e of sem.errors) out += `  - ${e}\n`;
      } else {
        out += '  (none)\n';
      }
      document.getElementById('semantic').textContent = out;
    }
    // validation badges
    if (data.validation) {
      const v = data.validation;
      function badge(ok, text){
        const cls = ok ? 'badge ok' : 'badge err';
        return `<span class="${cls}">${text}</span>`;
      }
      const el = document.getElementById('validation');
      el.innerHTML = '';
      el.innerHTML += `Léxico: ${badge(v.lexical.ok, v.lexical.ok ? 'OK' : 'FALLÓ')} - ${v.lexical.message}<br>`;
      el.innerHTML += `Sintáctico: ${badge(v.syntactic.ok, v.syntactic.ok ? 'OK' : 'FALLÓ')} - ${v.syntactic.message}<br>`;
      el.innerHTML += `Semántico: ${badge(v.semantic.ok, v.semantic.ok ? 'OK' : 'FALLÓ')} - ${v.semantic.message}`;
    }
  }catch(err){
    document.getElementById('tokens').textContent = 'Error: ' + err;
  }finally{
    spinner.style.display = 'none';
    status.textContent = '';
    runBtn.disabled = false;
    codeTA.disabled = false;
  }
});
