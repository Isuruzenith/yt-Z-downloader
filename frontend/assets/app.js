// ── Auth helpers ──────────────────────────────────────────────────────────────
const TOKEN_KEY = 'yt_z_token';

function getToken()      { return localStorage.getItem(TOKEN_KEY); }
function setToken(t)     { localStorage.setItem(TOKEN_KEY, t); }
function clearToken()    { localStorage.removeItem(TOKEN_KEY); }
function authHeaders()   { return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` }; }

function requireAuth() {
  if (!getToken()) { location.href = '/login.html'; }
}

function logout() {
  clearToken();
  location.href = '/login.html';
}

// ── API wrapper ───────────────────────────────────────────────────────────────
async function api(path, opts = {}) {
  const res = await fetch('/api' + path, {
    ...opts,
    headers: { ...authHeaders(), ...(opts.headers || {}) },
  });
  if (res.status === 401) { clearToken(); location.href = '/login.html'; return; }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// ── Upload helper (multipart) ─────────────────────────────────────────────────
async function apiUpload(path, formData) {
  const res = await fetch('/api' + path, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: formData,
  });
  if (res.status === 401) { clearToken(); location.href = '/login.html'; return; }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// ── Toast notifications ───────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ── Nav badge (active queue count) ───────────────────────────────────────────
async function updateNavBadge() {
  const badge = document.getElementById('queue-badge');
  if (!badge || !getToken()) return;
  try {
    const jobs = await api('/queue');
    const active = jobs.filter(j => j.status === 'queued' || j.status === 'running').length;
    if (active > 0) {
      badge.textContent = active;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  } catch (_) { /* silent — badge is non-critical */ }
}

// ── Nav setup ─────────────────────────────────────────────────────────────────
function setupNav() {
  requireAuth();
  // Mark active link
  const path = location.pathname.replace(/\/$/, '') || '/index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href').replace(/\/$/, '') || '/index.html';
    if (path === href || (path === '/' && href === '/index.html')) {
      a.classList.add('active');
    }
  });
  updateNavBadge();
}

// ── Progress polling ──────────────────────────────────────────────────────────
let _pollInterval;

function startPolling(renderFn, interval = 2500) {
  clearInterval(_pollInterval);
  renderFn(); // immediate first call
  _pollInterval = setInterval(async () => {
    try {
      await renderFn();
    } catch (_) { /* ignore transient errors */ }
  }, interval);
}

function stopPolling() {
  clearInterval(_pollInterval);
}

// ── Clipboard auto-paste ──────────────────────────────────────────────────────
async function autoPasteUrl(inputId) {
  const input = document.getElementById(inputId);
  if (!input || !navigator.clipboard) return;
  try {
    const text = await navigator.clipboard.readText();
    if (text.startsWith('http') && !input.value) input.value = text;
  } catch (_) { /* clipboard permission denied */ }
}

// ── Time formatter ────────────────────────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' });
}

function fmtDuration(secs) {
  if (!secs) return '';
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = Math.floor(secs % 60);
  return h > 0
    ? `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
    : `${m}:${String(s).padStart(2,'0')}`;
}

// ── File download (fetch-as-blob so the Bearer token works) ──────────────────
async function downloadFile(jobId, filename, btnEl) {
  if (btnEl) { btnEl.disabled = true; btnEl.innerHTML = '<span class="spinner"></span>'; }
  try {
    const res = await fetch(`/api/queue/${jobId}/file`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (res.status === 401) { clearToken(); location.href = '/login.html'; return; }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = filename || 'download';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    toast(e.message, 'error');
  } finally {
    if (btnEl) { btnEl.disabled = false; btnEl.textContent = 'Save'; }
  }
}
