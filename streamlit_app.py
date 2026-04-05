"""
Streamline — Personal Video Downloader
A Streamlit UI for yt-dlp with shadcn/ui dark theme.
"""

import streamlit as st
import asyncio
import threading
import uuid
import time
import json
import requests
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="Streamline — Personal Video Downloader",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_design_system():
    """Inject shadcn/ui default dark theme tokens, Geist fonts, and Streamlit widget overrides."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=Geist+Mono:wght@400;500;600&display=swap');

    :root {
      --background:             0 0% 3.9%;
      --foreground:             0 0% 98%;
      --card:                   0 0% 6.5%;
      --card-foreground:        0 0% 98%;
      --popover:                0 0% 6.5%;
      --popover-foreground:     0 0% 98%;
      --primary:                0 0% 98%;
      --primary-foreground:     0 0% 9%;
      --secondary:              0 0% 12%;
      --secondary-foreground:   0 0% 98%;
      --muted:                  0 0% 14.9%;
      --muted-foreground:       0 0% 63.9%;
      --accent:                 0 0% 17%;
      --accent-foreground:      0 0% 98%;
      --destructive:            0 62.8% 30.6%;
      --destructive-foreground: 0 0% 98%;
      --border:                 0 0% 14.9%;
      --input:                  0 0% 10%;
      --ring:                   0 0% 83.1%;
      --radius:                 0.5rem;
      --card-elevated:          0 0% 8.5%;
    }

    @keyframes shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }

    html, body, [class*="css"] {
      font-family: 'Geist', -apple-system, sans-serif !important;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
    .stApp {
      background-color: hsl(var(--background));
      color: hsl(var(--foreground));
    }
    .main .block-container {
      padding: 0 2rem 2.5rem 2rem;
      max-width: 1100px;
    }
    header[data-testid="stHeader"] {
      background: hsl(var(--background));
      border-bottom: 1px solid hsl(var(--border));
    }

    /* ── Input fields ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
      background-color: hsl(var(--input)) !important;
      border: 1px solid hsl(var(--border)) !important;
      border-radius: var(--radius) !important;
      color: hsl(var(--foreground)) !important;
      font-family: 'Geist', sans-serif !important;
      font-size: 0.875rem !important;
      height: 38px;
      padding: 0 0.75rem !important;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stTextArea > div > div > textarea {
      height: auto;
      padding: 0.5rem 0.75rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
      border-color: hsl(var(--ring)) !important;
      box-shadow: 0 0 0 3px hsl(var(--ring) / 0.12) !important;
      outline: none !important;
    }

    /* ── Labels ── */
    .stTextInput label, .stTextArea label, .stNumberInput label,
    .stSelectbox label, .stMultiSelect label, .stSlider label,
    .stDateInput label, .stFileUploader label, .stCheckbox label,
    .stRadio label span, .stToggle label {
      color: hsl(var(--muted-foreground)) !important;
      font-size: 0.75rem !important;
      font-weight: 500 !important;
      letter-spacing: 0.03em !important;
    }

    /* ── Select / Multiselect ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
      background-color: hsl(var(--input)) !important;
      border: 1px solid hsl(var(--border)) !important;
      border-radius: var(--radius) !important;
      color: hsl(var(--foreground)) !important;
      font-size: 0.875rem !important;
      min-height: 38px !important;
      transition: border-color 0.2s ease !important;
    }
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
      border-color: hsl(var(--ring)) !important;
      box-shadow: 0 0 0 3px hsl(var(--ring) / 0.12) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
      font-family: 'Geist', sans-serif !important;
      font-size: 0.875rem !important;
      font-weight: 500 !important;
      height: 38px;
      padding: 0 1.25rem !important;
      border-radius: var(--radius) !important;
      transition: all 0.15s ease !important;
      cursor: pointer;
      letter-spacing: 0.01em;
    }
    .stButton > button[kind="primary"] {
      background-color: hsl(var(--primary)) !important;
      color: hsl(var(--primary-foreground)) !important;
      border: none !important;
      font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
      opacity: 0.9 !important;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px hsl(var(--primary) / 0.15) !important;
    }
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind]) {
      background-color: hsl(var(--secondary)) !important;
      color: hsl(var(--secondary-foreground)) !important;
      border: 1px solid hsl(var(--border)) !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind]):hover {
      background-color: hsl(var(--accent)) !important;
      border-color: hsl(0 0% 22%) !important;
    }

    /* ── Tabs ── */
    [data-baseweb="tab-list"] {
      background: transparent !important;
      border-bottom: 1px solid hsl(var(--border)) !important;
      gap: 0 !important;
    }
    [data-baseweb="tab"] {
      background: transparent !important;
      color: hsl(var(--muted-foreground)) !important;
      font-family: 'Geist', sans-serif !important;
      font-size: 0.875rem !important;
      font-weight: 500 !important;
      padding: 0.75rem 1.125rem !important;
      border-bottom: 2px solid transparent !important;
      transition: color 0.2s ease, border-color 0.2s ease !important;
    }
    [data-baseweb="tab"]:hover {
      color: hsl(var(--foreground)) !important;
    }
    [aria-selected="true"][data-baseweb="tab"] {
      color: hsl(var(--foreground)) !important;
      border-bottom-color: hsl(var(--foreground)) !important;
    }
    [data-baseweb="tab-highlight"] {
      background-color: hsl(var(--foreground)) !important;
    }

    /* ── Expanders / Accordions ── */
    .streamlit-expanderHeader {
      background-color: hsl(var(--card)) !important;
      border: 1px solid hsl(var(--border)) !important;
      border-radius: var(--radius) !important;
      color: hsl(var(--foreground)) !important;
      font-family: 'Geist', sans-serif !important;
      font-size: 0.875rem !important;
      font-weight: 500 !important;
      padding: 0.75rem 1rem !important;
      transition: background-color 0.15s ease, border-color 0.15s ease !important;
    }
    .streamlit-expanderHeader:hover {
      background-color: hsl(var(--card-elevated)) !important;
      border-color: hsl(0 0% 20%) !important;
    }
    .streamlit-expanderContent {
      border: 1px solid hsl(var(--border)) !important;
      border-top: none !important;
      border-radius: 0 0 var(--radius) var(--radius) !important;
      background-color: hsl(var(--card)) !important;
      padding: 1.25rem !important;
    }

    /* ── Progress bars ── */
    .stProgress > div > div {
      background-color: hsl(var(--secondary)) !important;
      border-radius: 9999px !important;
      height: 5px !important;
      overflow: hidden;
    }
    .stProgress > div > div > div {
      background: linear-gradient(90deg, hsl(var(--foreground)), hsl(0 0% 80%), hsl(var(--foreground))) !important;
      background-size: 200% 100%;
      border-radius: 9999px !important;
      animation: shimmer 2s linear infinite;
    }

    /* ── Checkboxes ── */
    .stCheckbox > label > div:first-child {
      border-radius: calc(var(--radius) / 2) !important;
    }

    /* ── Alerts ── */
    .stAlert {
      border-radius: var(--radius) !important;
      border-width: 1px !important;
      font-size: 0.875rem !important;
    }

    /* ── DataFrames ── */
    .stDataFrame {
      border: 1px solid hsl(var(--border)) !important;
      border-radius: var(--radius) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: hsl(var(--background)); }
    ::-webkit-scrollbar-thumb { background: hsl(var(--border)); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: hsl(var(--muted-foreground)); }

    /* ── File uploader ── */
    .stFileUploader > div {
      background-color: hsl(var(--card)) !important;
      border: 1px dashed hsl(var(--border)) !important;
      border-radius: var(--radius) !important;
      transition: border-color 0.15s ease !important;
    }
    .stFileUploader > div:hover {
      border-color: hsl(0 0% 25%) !important;
    }

    /* ── Misc ── */
    hr { border-color: hsl(var(--border)) !important; margin: 1.5rem 0 !important; }
    code, .stCode {
      font-family: 'Geist Mono', monospace !important;
      font-size: 0.8125rem !important;
      background-color: hsl(var(--secondary)) !important;
      border-radius: calc(var(--radius) / 2) !important;
      padding: 0.125rem 0.375rem !important;
    }
    .stCodeBlock {
      background-color: hsl(var(--card)) !important;
      border: 1px solid hsl(var(--border)) !important;
      border-radius: var(--radius) !important;
    }
    .mono { font-family: 'Geist Mono', monospace !important; }

    /* ── Metrics ── */
    [data-testid="stMetricValue"] {
      font-family: 'Geist', sans-serif !important;
      font-size: 1.5rem !important;
      font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
      font-size: 0.6875rem !important;
      text-transform: uppercase !important;
      letter-spacing: 0.08em !important;
      color: hsl(var(--muted-foreground)) !important;
    }

    /* ════════════════════════════════════════
       Custom Streamline component classes
       ════════════════════════════════════════ */

    /* Cards */
    .sl-card {
      background-color: hsl(var(--card));
      border: 1px solid hsl(var(--border));
      border-radius: var(--radius);
      padding: 1rem 1.25rem;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .sl-card:hover {
      border-color: hsl(0 0% 22%);
    }
    .sl-card-elevated {
      background-color: hsl(var(--card-elevated));
      border: 1px solid hsl(var(--border));
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
    }

    /* Badges */
    .sl-badge {
      display: inline-flex; align-items: center;
      border-radius: 9999px;
      font-family: 'Geist Mono', monospace;
      font-size: 0.6875rem; font-weight: 500;
      padding: 0.1875rem 0.625rem;
      letter-spacing: 0.04em;
      white-space: nowrap;
    }
    .sl-badge-default  { background: hsl(var(--secondary)); color: hsl(var(--secondary-foreground)); }
    .sl-badge-success  { background: hsl(142 76% 10%); color: hsl(142 71% 45%); border: 1px solid hsl(142 76% 18%); }
    .sl-badge-error    { background: hsl(0 62% 15%); color: hsl(0 80% 65%); border: 1px solid hsl(0 62% 25%); }
    .sl-badge-warning  { background: hsl(38 92% 10%); color: hsl(38 92% 55%); border: 1px solid hsl(38 92% 20%); }
    .sl-badge-running  { background: hsl(217 91% 10%); color: hsl(217 91% 65%); border: 1px solid hsl(217 91% 20%); }

    /* Section headings */
    .sl-section {
      font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.1em;
      text-transform: uppercase; color: hsl(var(--muted-foreground));
      display: flex; align-items: center; gap: 0.75rem;
      margin: 1.5rem 0 1rem 0;
    }
    .sl-section::after {
      content: ''; flex: 1; height: 1px;
      background: linear-gradient(90deg, hsl(var(--border)), transparent);
    }

    /* Code preview */
    .sl-code-preview {
      font-family: 'Geist Mono', monospace; font-size: 0.78125rem;
      background: hsl(var(--card)); border: 1px solid hsl(var(--border));
      border-radius: var(--radius); padding: 1rem 1.125rem;
      color: hsl(var(--muted-foreground)); line-height: 1.7;
      white-space: pre-wrap; word-break: break-all;
      position: relative;
    }
    .sl-code-preview .hl { color: hsl(var(--foreground)); }

    /* Job cards */
    .sl-job-card {
      background: hsl(var(--card)); border: 1px solid hsl(var(--border));
      border-radius: var(--radius); padding: 1rem 1.25rem;
      margin-bottom: 0.75rem;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .sl-job-card:hover {
      border-color: hsl(0 0% 22%);
      box-shadow: 0 2px 8px hsl(0 0% 0% / 0.3);
    }
    .sl-job-title {
      font-size: 0.9375rem; font-weight: 600;
      color: hsl(var(--foreground));
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      margin-bottom: 0.375rem;
    }
    .sl-job-meta {
      font-family: 'Geist Mono', monospace;
      font-size: 0.6875rem; color: hsl(var(--muted-foreground));
      display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;
      margin-bottom: 0.625rem;
    }
    .sl-progress-detail {
      font-family: 'Geist Mono', monospace;
      font-size: 0.6875rem; color: hsl(var(--muted-foreground));
      margin-top: 0.5rem;
      display: flex; gap: 1.5rem; align-items: center;
    }
    .sl-progress-detail span {
      display: inline-flex; align-items: center; gap: 0.25rem;
    }

    /* Wordmark */
    .sl-wordmark {
      font-family: 'Geist', sans-serif;
      font-size: 1.25rem; font-weight: 700;
      letter-spacing: -0.03em;
      color: hsl(var(--foreground));
    }

    /* Empty states */
    .sl-empty-state {
      text-align: center; padding: 4rem 1rem;
      color: hsl(var(--muted-foreground));
    }
    .sl-empty-icon {
      font-size: 2.5rem; margin-bottom: 0.75rem;
      opacity: 0.5;
    }
    .sl-empty-title {
      font-size: 0.9375rem; font-weight: 600;
      letter-spacing: 0.015em; margin-bottom: 0.375rem;
      color: hsl(var(--muted-foreground));
    }
    .sl-empty-sub {
      font-size: 0.8125rem;
      color: hsl(0 0% 35%);
    }

    /* Auth page */
    .sl-auth-wrap {
      display: flex; justify-content: center; align-items: center;
      min-height: 65vh; padding: 2rem 0;
    }
    .sl-auth-card {
      background: hsl(var(--card));
      border: 1px solid hsl(var(--border));
      border-radius: calc(var(--radius) * 1.5);
      padding: 2.5rem 2rem 2rem;
      max-width: 400px; width: 100%;
      box-shadow: 0 0 80px hsl(0 0% 100% / 0.015),
                  0 8px 32px hsl(0 0% 0% / 0.4);
    }
    .sl-auth-title {
      font-family: 'Geist', sans-serif;
      font-size: 1.75rem; font-weight: 700;
      letter-spacing: -0.03em;
      color: hsl(var(--foreground));
      margin-bottom: 0.25rem;
    }
    .sl-auth-subtitle {
      font-size: 0.875rem;
      color: hsl(var(--muted-foreground));
      margin-bottom: 1.75rem;
    }

    /* Preview card */
    .sl-preview-card {
      background: hsl(var(--card));
      border: 1px solid hsl(var(--border));
      border-radius: var(--radius);
      padding: 1.25rem;
      display: flex; gap: 1.25rem; align-items: flex-start;
    }
    .sl-preview-thumb {
      width: 180px; min-width: 180px; border-radius: calc(var(--radius) * 0.75);
      overflow: hidden; aspect-ratio: 16/9; background: hsl(var(--secondary));
    }
    .sl-preview-thumb img { width: 100%; height: 100%; object-fit: cover; }
    .sl-preview-info { flex: 1; min-width: 0; }
    .sl-preview-title {
      font-size: 1rem; font-weight: 600; color: hsl(var(--foreground));
      margin-bottom: 0.375rem;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .sl-preview-meta {
      font-family: 'Geist Mono', monospace;
      font-size: 0.75rem; color: hsl(var(--muted-foreground));
      margin-bottom: 0.75rem;
    }

    /* Nav bar user info */
    .sl-nav-user {
      font-family: 'Geist Mono', monospace;
      font-size: 0.6875rem; color: hsl(var(--muted-foreground));
      padding: 0.375rem 0;
      display: flex; align-items: center; gap: 0.5rem;
    }
    .sl-nav-dot {
      width: 6px; height: 6px; border-radius: 50%;
      display: inline-block;
    }
    .sl-nav-dot-live { background: hsl(142 71% 45%); }
    .sl-nav-dot-demo { background: hsl(38 92% 55%); }

    /* Settings section cards */
    .sl-settings-card {
      background: hsl(var(--card));
      border: 1px solid hsl(var(--border));
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-bottom: 0.75rem;
    }
    .sl-settings-card h4 {
      font-size: 0.875rem; font-weight: 600;
      color: hsl(var(--foreground));
      margin: 0 0 0.75rem 0;
    }

    /* Version info */
    .sl-version-row {
      display: flex; align-items: center; gap: 0.5rem;
      font-family: 'Geist Mono', monospace;
      font-size: 0.8125rem; padding: 0.375rem 0;
      color: hsl(var(--foreground));
    }
    .sl-version-ok { color: hsl(142 71% 45%); }
    .sl-version-missing { color: hsl(0 80% 55%); }

    /* Pagination */
    .sl-pagination {
      display: flex; justify-content: center; align-items: center;
      gap: 0.75rem; padding: 1rem 0;
      font-family: 'Geist', sans-serif;
      font-size: 0.8125rem; color: hsl(var(--muted-foreground));
    }
    </style>
    """, unsafe_allow_html=True)


inject_design_system()


def init_state():
    defaults = {
        "token": None,
        "email": None,
        "jobs": {},
        "preview_info": None,
        "cookie_status": None,
        "dl_opts": {
            "format": "mp4",
            "quality": "best",
            "playlist": False,
            "embed_metadata": False,
            "embed_thumbnail": False,
            "write_thumbnail": False,
            "write_subs": False,
            "write_auto_subs": False,
            "subtitles_langs": [],
            "embed_subs": False,
            "extract_audio": False,
            "audio_format": None,
            "audio_quality": "192",
            "sponsorblock": None,
            "sponsorblock_categories": [],
            "rate_limit": None,
            "proxy_url": None,
            "outtmpl": None,
            "restrict_filenames": False,
            "windows_filenames": False,
            "no_part_files": False,
            "geo_bypass": False,
            "cookies_from_browser": None,
            "force_ipv4": False,
            "force_ipv6": False,
            "ignore_errors": False,
            "split_chapters": False,
            "remux": False,
            "normalize_audio": False,
            "write_info_json": False,
            "write_description": False,
            "write_comments": False,
            "convert_video": None,
            "convert_subs": None,
            "playlist_items": None,
            "playlist_start": None,
            "playlist_end": None,
            "playlist_reverse": False,
            "playlist_random": False,
            "date_before": None,
            "date_after": None,
            "min_duration": None,
            "max_duration": None,
            "min_views": None,
            "max_views": None,
            "match_title": None,
            "reject_title": None,
            "break_match_filters": False,
            "skip_livestreams": False,
            "age_limit": None,
            "concurrent_fragments": None,
            "fragment_retries": None,
            "skip_unavailable_fragments": False,
            "buffersize": None,
            "http_chunk_size": None,
            "download_archive": None,
            "overwrites": None,
            "keep_fragments": False,
            "sleep_requests": None,
            "sleep_interval": None,
            "downloader": None,
            "downloader_args": None,
            "source_address": None,
            "geo_bypass_country": None,
            "socket_timeout": None,
            "user_agent": None,
            "custom_headers": {},
            "username": None,
            "password": None,
            "twofactor": None,
            "netrc": False,
            "no_check_certificates": False,
            "prefer_insecure": False,
            "format_sort": None,
            "prefer_free_formats": False,
            "check_formats": False,
            "video_codec": None,
            "audio_codec": None,
            "merge_output_format": None,
            "trim_filenames": None,
            "extractor_args": {},
            "extract_flat": False,
            "power_mode_args": [],
        },
        "defaults": {},
        "format_data": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


API_BASE = "http://localhost:8000"


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result(timeout=30)
        else:
            return loop.run_until_complete(coro)
    except Exception:
        return asyncio.run(coro)


def _mock_job_runner(job_id: str):
    import random
    job = st.session_state.jobs.get(job_id)
    if not job:
        return
    job["status"] = "running"
    progress = 0.0
    while progress < 100.0:
        time.sleep(0.4)
        progress = min(100.0, progress + random.uniform(4, 12))
        job["progress"] = round(progress, 1)
        if job.get("_cancel"):
            job["status"] = "cancelled"
            return
    job["status"] = "done"
    job["progress"] = 100.0
    job["finished_at"] = datetime.utcnow().isoformat()


def api_login(email: str, password: str):
    try:
        r = requests.post(f"{API_BASE}/auth/login",
                          json={"email": email, "password": password}, timeout=5)
        if r.status_code == 200:
            return r.json()["access_token"], None
        return None, r.json().get("detail", "Login failed")
    except Exception as e:
        return None, f"Backend offline — running in demo mode. ({e})"


def api_register(email: str, password: str):
    try:
        r = requests.post(f"{API_BASE}/auth/register",
                          json={"email": email, "password": password}, timeout=5)
        if r.status_code == 200:
            return r.json()["access_token"], None
        return None, r.json().get("detail", "Registration failed")
    except Exception as e:
        return None, f"Backend offline — demo mode. ({e})"


def api_get_info(url: str):
    if not st.session_state.token:
        return None, "Not authenticated"
    try:
        r = requests.get(f"{API_BASE}/api/info",
                         params={"url": url},
                         headers={"Authorization": f"Bearer {st.session_state.token}"},
                         timeout=20)
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch info")
    except Exception:
        return {
            "title": "Demo Video Title (Backend Offline)",
            "uploader": "Demo Channel",
            "duration": 245,
            "thumbnail": "https://picsum.photos/seed/ytvid/640/360",
        }, None


def api_start_download(url, opts):
    if not st.session_state.token:
        return None, "Not authenticated"
    try:
        r = requests.post(
            f"{API_BASE}/api/download",
            json={"url": url, **opts},
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to start download")
    except Exception:
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "url": url,
            "format": opts.get("format", "mp4"),
            "quality": opts.get("quality", "best"),
            "playlist": opts.get("playlist", False),
            "status": "queued",
            "progress": 0.0,
            "title": st.session_state.preview_info.get("title", url) if st.session_state.preview_info else url,
            "created_at": datetime.utcnow().isoformat(),
            "finished_at": None,
            "filepath": None,
            "error_msg": None,
            "_cancel": False,
        }
        st.session_state.jobs[job_id] = job
        t = threading.Thread(target=_mock_job_runner, args=(job_id,), daemon=True)
        t.start()
        return job, None


def api_cancel_job(job_id):
    if job_id in st.session_state.jobs:
        st.session_state.jobs[job_id]["_cancel"] = True
        st.session_state.jobs[job_id]["status"] = "cancelled"
        return True
    try:
        r = requests.delete(
            f"{API_BASE}/api/queue/{job_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        return r.status_code == 200
    except Exception:
        return False


def api_get_history():
    try:
        r = requests.get(
            f"{API_BASE}/api/downloads",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return [j for j in st.session_state.jobs.values()
            if j.get("status") in ("done", "cancelled", "error")]


def api_upload_cookies(file_bytes):
    try:
        r = requests.post(
            f"{API_BASE}/api/settings/cookies/upload",
            files={"file": ("cookies.txt", file_bytes, "text/plain")},
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=10,
        )
        return r.status_code == 200, r.json().get("message", "Unknown response")
    except Exception as e:
        return False, f"Demo mode — cookie upload simulated. ({e})"


def api_get_formats(url: str):
    if not st.session_state.token:
        return None, "Not authenticated"
    try:
        r = requests.get(
            f"{API_BASE}/api/formats",
            params={"url": url},
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Failed to fetch formats")
    except Exception as e:
        return None, f"Error: {e}"


def api_get_defaults():
    if not st.session_state.token:
        return {}
    try:
        r = requests.get(
            f"{API_BASE}/api/settings/defaults",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def api_save_defaults(defaults: dict):
    if not st.session_state.token:
        return False
    try:
        r = requests.post(
            f"{API_BASE}/api/settings/defaults",
            json=defaults,
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        return r.status_code == 200
    except Exception:
        return False


def api_get_tool_versions():
    if not st.session_state.token:
        return None
    try:
        r = requests.get(
            f"{API_BASE}/api/settings/yt-dlp-version",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def fmt_bytes(n):
    if not n:
        return "—"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def fmt_speed(bps):
    if not bps:
        return "—"
    return fmt_bytes(int(bps)) + "/s"


def fmt_duration(secs):
    if not secs:
        return "—"
    secs = int(secs)
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def card(content, cls=""):
    return f'<div class="sl-card {cls}">{content}</div>'


def badge(text, variant="default"):
    return f'<span class="sl-badge sl-badge-{variant}">{text}</span>'


def status_badge(status):
    icons = {"queued": "○", "running": "◉", "done": "●", "error": "✕", "cancelled": "⊘", "finished": "●"}
    variant_map = {"queued": "default", "running": "running", "done": "success", "finished": "success", "error": "error", "cancelled": "default"}
    icon = icons.get(status, "○")
    variant = variant_map.get(status, "default")
    return badge(f"{icon} {status}", variant)


def section_heading(text):
    st.markdown(f'<div class="sl-section">{text}</div>', unsafe_allow_html=True)


def wordmark():
    return '<span class="sl-wordmark">Streamline</span>'


def empty_state(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="sl-empty-state">
      <div class="sl-empty-icon">{icon}</div>
      <div class="sl-empty-title">{title}</div>
      <div class="sl-empty-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def live_queue_jobs():
    return [j for j in st.session_state.jobs.values()
            if j.get("status") in ("queued", "running")]


def build_command_preview(opts: dict, url: str) -> str:
    """Generate a yt-dlp CLI command string from the dl_opts dict."""
    parts = ["yt-dlp"]

    if opts.get("format") and opts["format"] != "best":
        parts.append(f'-f "{opts["format"]}"')

    if opts.get("embed_metadata"):
        parts.append("--embed-metadata")
    if opts.get("embed_thumbnail"):
        parts.append("--embed-thumbnail")
    if opts.get("write_subs"):
        parts.append("--write-subs")
    if opts.get("subtitles_langs"):
        langs = opts["subtitles_langs"]
        if isinstance(langs, list) and langs:
            parts.append(f'--sub-langs {",".join(langs)}')
    if opts.get("write_auto_subs"):
        parts.append("--write-auto-subs")
    if opts.get("sponsorblock") == "remove":
        parts.append("--sponsorblock-remove all")
    elif opts.get("sponsorblock") == "mark":
        parts.append("--sponsorblock-mark all")
    if opts.get("rate_limit"):
        parts.append(f'--limit-rate {opts["rate_limit"]}')
    if opts.get("proxy_url"):
        parts.append(f'--proxy {opts["proxy_url"]}')
    if opts.get("outtmpl"):
        parts.append(f'-o "{opts["outtmpl"]}"')
    if opts.get("playlist"):
        parts.append("--yes-playlist")
    else:
        parts.append("--no-playlist")
    if opts.get("playlist_items"):
        parts.append(f'--playlist-items {opts["playlist_items"]}')
    if opts.get("extract_audio"):
        parts.append("--extract-audio")
    if opts.get("audio_format"):
        parts.append(f'--audio-format {opts["audio_format"]}')
    if opts.get("split_chapters"):
        parts.append("--split-chapters")
    if opts.get("geo_bypass"):
        parts.append("--geo-bypass")
    if opts.get("cookies_from_browser"):
        parts.append(f'--cookies-from-browser {opts["cookies_from_browser"]}')
    if opts.get("restrict_filenames"):
        parts.append("--restrict-filenames")
    if opts.get("windows_filenames"):
        parts.append("--windows-filenames")
    if opts.get("force_ipv4"):
        parts.append("--force-ipv4")
    if opts.get("force_ipv6"):
        parts.append("--force-ipv6")
    if opts.get("ignore_errors"):
        parts.append("--ignore-errors")
    if opts.get("prefer_free_formats"):
        parts.append("--prefer-free-formats")
    if opts.get("format_sort"):
        parts.append(f'--format-sort {opts["format_sort"]}')
    if opts.get("downloader"):
        parts.append(f'--downloader {opts["downloader"]}')

    if url:
        parts.append(f'"{url}"')

    if len(parts) <= 3:
        return " ".join(parts)
    return " \\\n  ".join(parts)


def render_auth():
    st.markdown('<div class="sl-auth-wrap">', unsafe_allow_html=True)
    _, col, _ = st.columns([1.2, 1, 1.2])
    with col:
        st.markdown(
            '<div class="sl-auth-title">Streamline</div>'
            '<div class="sl-auth-subtitle">Personal video downloader</div>',
            unsafe_allow_html=True,
        )

        tab = st.tabs(["Sign in", "Register"])

        with tab[0]:
            st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@example.com", key="auth_email_login")
            password = st.text_input("Password", type="password", placeholder="Password", key="auth_pw_login")
            st.markdown('<div style="height:0.25rem"></div>', unsafe_allow_html=True)
            if st.button("Sign in →", key="login_btn", use_container_width=True, type="primary"):
                if email and password:
                    with st.spinner(""):
                        token, err = api_login(email, password)
                    if err and "demo" not in err.lower():
                        st.error(err)
                    else:
                        st.session_state.token = token or "demo-token"
                        st.session_state.email = email
                        st.rerun()

        with tab[1]:
            st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@example.com", key="auth_email_reg")
            password = st.text_input("Password", type="password", placeholder="Choose a password", key="auth_pw_reg")
            st.markdown('<div style="height:0.25rem"></div>', unsafe_allow_html=True)
            if st.button("Create account →", key="reg_btn", use_container_width=True, type="primary"):
                if email and password:
                    with st.spinner(""):
                        token, err = api_register(email, password)
                    if err and "demo" not in err.lower():
                        st.error(err)
                    else:
                        st.session_state.token = token or "demo-token"
                        st.session_state.email = email
                        st.rerun()

        st.markdown(
            '<p style="font-size:0.75rem;color:hsl(0 0% 30%);margin-top:1.5rem;text-align:center">'
            'Backend offline? Use any credentials — demo mode.</p>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


def render_app():
    c1, c2, c3 = st.columns([2.5, 5, 2.5])
    with c1:
        st.markdown(
            f'<div style="padding:0.875rem 0 0.5rem">{wordmark()}</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown('<div style="height:0.75rem"></div>', unsafe_allow_html=True)
        if st.button("Sign out", key="logout_btn"):
            for k in ["token", "email", "jobs", "preview_info", "cookie_status", "dl_opts", "format_data"]:
                st.session_state.pop(k, None)
            st.rerun()

    if st.session_state.email:
        mode = "demo" if st.session_state.token == "demo-token" else "live"
        dot_cls = "sl-nav-dot-demo" if mode == "demo" else "sl-nav-dot-live"
        st.markdown(
            f'<div class="sl-nav-user">'
            f'<span class="sl-nav-dot {dot_cls}"></span>'
            f'{st.session_state.email}'
            f'<span style="opacity:0.4">·</span>'
            f'<span style="opacity:0.4">{mode}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    active_count = len([j for j in st.session_state.jobs.values() if j.get("status") in ("queued", "running")])
    queue_label = f"Queue ({active_count})" if active_count else "Queue"

    tabs = st.tabs(["Download", queue_label, "Formats", "History", "Settings"])

    with tabs[0]:
        render_download_tab()
    with tabs[1]:
        render_queue_tab()
    with tabs[2]:
        render_formats_tab()
    with tabs[3]:
        render_history_tab()
    with tabs[4]:
        render_settings_tab()


def render_download_tab():
    opts = st.session_state.dl_opts

    section_heading("Video URL")

    url = st.text_input(
        "URL",
        placeholder="https://youtube.com/watch?v=...  or paste a playlist URL",
        key="dl_url",
        value=opts.get("url", ""),
    )
    opts["url"] = url

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        fmt = st.selectbox(
            "Container",
            options=["mp4", "webm", "mkv", "mp3", "m4a", "best"],
            index=["mp4", "webm", "mkv", "mp3", "m4a", "best"].index(opts.get("format", "mp4")),
            key="dl_format",
        )
        opts["format"] = fmt
    with col2:
        is_audio = fmt in ("mp3", "m4a")
        quality_opts = ["audio"] if is_audio else ["best", "4k", "1440p", "1080p", "720p", "480p"]
        quality = st.selectbox(
            "Quality",
            options=quality_opts,
            index=quality_opts.index(opts.get("quality", "best")) if opts.get("quality") in quality_opts else 0,
            key="dl_quality",
        )
        opts["quality"] = quality
    with col3:
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        playlist = st.checkbox("Playlist mode", value=opts.get("playlist", False), key="playlist_toggle")
        opts["playlist"] = playlist

    st.markdown('<div style="height:0.25rem"></div>', unsafe_allow_html=True)

    with st.expander("🎬 Format & Quality", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            opts["format_sort"] = st.text_input(
                "Format Sort",
                value=opts.get("format_sort") or "",
                placeholder="e.g. res,fps,codec",
                key="opt_format_sort",
            ) or None
            opts["video_codec"] = st.selectbox(
                "Video Codec",
                options=[None, "h264", "h265", "vp9", "av1"],
                format_func=lambda x: "Any" if x is None else x.upper(),
                index=0 if opts.get("video_codec") is None else ["h264", "h265", "vp9", "av1"].index(opts["video_codec"]) + 1,
                key="opt_video_codec",
            )
            opts["prefer_free_formats"] = st.checkbox(
                "Prefer Free Formats",
                value=opts.get("prefer_free_formats", False),
                key="opt_prefer_free",
            )
        with c2:
            opts["audio_codec"] = st.selectbox(
                "Audio Codec",
                options=[None, "aac", "opus", "mp3", "flac"],
                format_func=lambda x: "Any" if x is None else x.upper(),
                index=0 if opts.get("audio_codec") is None else ["aac", "opus", "mp3", "flac"].index(opts["audio_codec"]) + 1,
                key="opt_audio_codec",
            )
            opts["merge_output_format"] = st.selectbox(
                "Merge Output",
                options=[None, "mp4", "mkv", "webm", "mov", "avi", "flv"],
                key="opt_merge_output",
            )
            opts["check_formats"] = st.checkbox(
                "Check Formats",
                value=opts.get("check_formats", False),
                key="opt_check_formats",
            )

    with st.expander("⚡ Post-Processing", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["extract_audio"] = st.checkbox(
                "Extract Audio",
                value=opts.get("extract_audio", False),
                key="opt_extract_audio",
            )
            opts["audio_format"] = st.selectbox(
                "Audio Format",
                options=[None, "mp3", "m4a", "flac", "opus", "vorbis", "wav", "aac"],
                key="opt_audio_format",
            )
            opts["audio_quality"] = st.text_input(
                "Audio Quality",
                value=opts.get("audio_quality", "192"),
                key="opt_audio_quality",
            )
            opts["normalize_audio"] = st.checkbox(
                "Normalize Audio",
                value=opts.get("normalize_audio", False),
                key="opt_normalize_audio",
            )
        with c2:
            opts["convert_video"] = st.selectbox(
                "Convert Video",
                options=[None, "mp4", "mkv", "webm", "mov", "avi", "flv"],
                key="opt_convert_video",
            )
            opts["embed_thumbnail"] = st.checkbox(
                "Embed Thumbnail",
                value=opts.get("embed_thumbnail", False),
                key="opt_embed_thumb",
            )
            opts["write_thumbnail"] = st.checkbox(
                "Write Thumbnail",
                value=opts.get("write_thumbnail", False),
                key="opt_write_thumb",
            )
            opts["embed_metadata"] = st.checkbox(
                "Embed Metadata",
                value=opts.get("embed_metadata", False),
                key="opt_embed_meta",
            )

        c3, c4 = st.columns(2)
        with c3:
            opts["embed_subs"] = st.checkbox(
                "Embed Subtitles",
                value=opts.get("embed_subs", False),
                key="opt_embed_subs",
            )
            opts["split_chapters"] = st.checkbox(
                "Split Chapters",
                value=opts.get("split_chapters", False),
                key="opt_split_chapters",
            )
            opts["remux"] = st.checkbox(
                "Remux",
                value=opts.get("remux", False),
                key="opt_remux",
            )
        with c4:
            opts["write_info_json"] = st.checkbox(
                "Write Info JSON",
                value=opts.get("write_info_json", False),
                key="opt_write_infojson",
            )
            opts["write_description"] = st.checkbox(
                "Write Description",
                value=opts.get("write_description", False),
                key="opt_write_desc",
            )
            opts["write_comments"] = st.checkbox(
                "Write Comments",
                value=opts.get("write_comments", False),
                key="opt_write_comments",
            )

    with st.expander("💬 Subtitles", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["write_subs"] = st.checkbox(
                "Write Subtitles",
                value=opts.get("write_subs", False),
                key="opt_write_subs",
            )
            opts["write_auto_subs"] = st.checkbox(
                "Write Auto-Subs",
                value=opts.get("write_auto_subs", False),
                key="opt_write_auto_subs",
            )
        with c2:
            opts["subtitles_langs"] = st.text_input(
                "Languages",
                value=",".join(opts.get("subtitles_langs") or []),
                placeholder="en,de,fr",
                key="opt_sub_langs",
            )
            opts["subtitles_format"] = st.selectbox(
                "Subtitle Format",
                options=[None, "srt", "vtt", "ass", "lrc"],
                key="opt_sub_format",
            )
            opts["convert_subs"] = st.selectbox(
                "Convert Subs",
                options=[None, "srt", "vtt", "ass", "lrc"],
                key="opt_convert_subs",
            )

    with st.expander("📋 Video Selection & Filters", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["playlist_items"] = st.text_input(
                "Playlist Items",
                value=opts.get("playlist_items") or "",
                placeholder="e.g. 1,3,5-7",
                key="opt_pl_items",
            ) or None
            opts["playlist_start"] = st.number_input(
                "Start Index",
                value=opts.get("playlist_start") or 0,
                min_value=0,
                key="opt_pl_start",
            ) or None
            opts["playlist_end"] = st.number_input(
                "End Index",
                value=opts.get("playlist_end") or 0,
                min_value=0,
                key="opt_pl_end",
            ) or None
            opts["playlist_reverse"] = st.checkbox(
                "Reverse Playlist",
                value=opts.get("playlist_reverse", False),
                key="opt_pl_reverse",
            )
            opts["playlist_random"] = st.checkbox(
                "Random Order",
                value=opts.get("playlist_random", False),
                key="opt_pl_random",
            )
        with c2:
            opts["date_before"] = st.text_input(
                "Date Before",
                value=opts.get("date_before") or "",
                placeholder="YYYYMMDD",
                key="opt_date_before",
            ) or None
            opts["date_after"] = st.text_input(
                "Date After",
                value=opts.get("date_after") or "",
                placeholder="YYYYMMDD",
                key="opt_date_after",
            ) or None
            opts["min_duration"] = st.number_input(
                "Min Duration (s)",
                value=opts.get("min_duration") or 0,
                min_value=0,
                key="opt_min_dur",
            ) or None
            opts["max_duration"] = st.number_input(
                "Max Duration (s)",
                value=opts.get("max_duration") or 0,
                min_value=0,
                key="opt_max_dur",
            ) or None
            opts["min_views"] = st.number_input(
                "Min Views",
                value=opts.get("min_views") or 0,
                min_value=0,
                key="opt_min_views",
            ) or None
            opts["max_views"] = st.number_input(
                "Max Views",
                value=opts.get("max_views") or 0,
                min_value=0,
                key="opt_max_views",
            ) or None

        c3, c4 = st.columns(2)
        with c3:
            opts["match_title"] = st.text_input(
                "Match Title Regex",
                value=opts.get("match_title") or "",
                key="opt_match_title",
            ) or None
            opts["reject_title"] = st.text_input(
                "Reject Title Regex",
                value=opts.get("reject_title") or "",
                key="opt_reject_title",
            ) or None
            opts["break_match_filters"] = st.checkbox(
                "Break on Match",
                value=opts.get("break_match_filters", False),
                key="opt_break_match",
            )
        with c4:
            opts["skip_livestreams"] = st.checkbox(
                "Skip Livestreams",
                value=opts.get("skip_livestreams", False),
                key="opt_skip_live",
            )
            opts["age_limit"] = st.number_input(
                "Age Limit",
                value=opts.get("age_limit") or 0,
                min_value=0,
                max_value=99,
                key="opt_age_limit",
            ) or None

    with st.expander("⚙ Download Behaviour", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["rate_limit"] = st.text_input(
                "Rate Limit",
                value=opts.get("rate_limit") or "",
                placeholder="e.g. 1M, 500K",
                key="opt_rate_limit",
            ) or None
            opts["concurrent_fragments"] = st.slider(
                "Concurrent Fragments",
                min_value=1,
                max_value=16,
                value=opts.get("concurrent_fragments") or 1,
                key="opt_conc_frag",
            )
            opts["retries"] = st.number_input(
                "Retries",
                value=opts.get("retries") or 0,
                min_value=1,
                max_value=20,
                key="opt_retries",
            ) or None
            opts["fragment_retries"] = st.number_input(
                "Fragment Retries",
                value=opts.get("fragment_retries") or 0,
                min_value=1,
                max_value=20,
                key="opt_frag_retries",
            ) or None
            opts["skip_unavailable_fragments"] = st.checkbox(
                "Skip Unavailable Frags",
                value=opts.get("skip_unavailable_fragments", False),
                key="opt_skip_unavail",
            )
        with c2:
            opts["buffersize"] = st.text_input(
                "Buffer Size",
                value=opts.get("buffersize") or "",
                placeholder="e.g. 1024",
                key="opt_buffersize",
            ) or None
            opts["http_chunk_size"] = st.text_input(
                "HTTP Chunk Size",
                value=opts.get("http_chunk_size") or "",
                key="opt_http_chunk",
            ) or None
            opts["ignore_errors"] = st.checkbox(
                "Continue on Error",
                value=opts.get("ignore_errors", False),
                key="opt_ignore_errors",
            )
            opts["download_archive"] = st.text_input(
                "Download Archive",
                value=opts.get("download_archive") or "",
                placeholder="Path to archive file",
                key="opt_archive",
            ) or None
            opts["keep_fragments"] = st.checkbox(
                "Keep Fragments",
                value=opts.get("keep_fragments", False),
                key="opt_keep_frags",
            )

        c3, c4 = st.columns(2)
        with c3:
            opts["sleep_requests"] = st.slider(
                "Sleep Between Requests (s)",
                min_value=0.0,
                max_value=10.0,
                value=float(opts.get("sleep_requests") or 0.0),
                step=0.5,
                key="opt_sleep_req",
            ) or None
            opts["sleep_interval"] = st.slider(
                "Sleep Between Downloads (s)",
                min_value=0.0,
                max_value=30.0,
                value=float(opts.get("sleep_interval") or 0.0),
                step=1.0,
                key="opt_sleep_dl",
            ) or None
        with c4:
            opts["downloader"] = st.selectbox(
                "Downloader",
                options=[None, "native", "ffmpeg", "aria2c", "curl", "wget"],
                key="opt_downloader",
            )
            opts["downloader_args"] = st.text_input(
                "Downloader Args",
                value=opts.get("downloader_args") or "",
                key="opt_dl_args",
            ) or None

    with st.expander("🌐 Network & Authentication", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["proxy_url"] = st.text_input(
                "Proxy URL",
                value=opts.get("proxy_url") or "",
                key="opt_proxy",
            ) or None
            opts["source_address"] = st.text_input(
                "Source IP",
                value=opts.get("source_address") or "",
                key="opt_source_ip",
            ) or None
            opts["force_ipv4"] = st.checkbox(
                "Force IPv4",
                value=opts.get("force_ipv4", False),
                key="opt_ipv4",
            )
            opts["force_ipv6"] = st.checkbox(
                "Force IPv6",
                value=opts.get("force_ipv6", False),
                key="opt_ipv6",
            )
            opts["geo_bypass"] = st.checkbox(
                "Geo Bypass",
                value=opts.get("geo_bypass", False),
                key="opt_geo_bypass",
            )
            opts["geo_bypass_country"] = st.text_input(
                "Geo Bypass Country",
                value=opts.get("geo_bypass_country") or "",
                placeholder="2-letter code",
                key="opt_geo_country",
            ) or None
            opts["socket_timeout"] = st.number_input(
                "Socket Timeout (s)",
                value=opts.get("socket_timeout") or 0,
                min_value=0,
                key="opt_socket_timeout",
            ) or None
        with c2:
            opts["user_agent"] = st.text_input(
                "User Agent",
                value=opts.get("user_agent") or "",
                key="opt_user_agent",
            ) or None
            opts["cookies_from_browser"] = st.selectbox(
                "Cookies from Browser",
                options=[None, "chrome", "firefox", "edge", "safari", "brave"],
                key="opt_cookies_browser",
            )
            opts["username"] = st.text_input(
                "Username",
                value=opts.get("username") or "",
                key="opt_username",
            ) or None
            opts["password"] = st.text_input(
                "Password",
                type="password",
                value=opts.get("password") or "",
                key="opt_password",
            ) or None
            opts["twofactor"] = st.text_input(
                "2FA Code",
                value=opts.get("twofactor") or "",
                key="opt_twofactor",
            ) or None
            opts["netrc"] = st.checkbox(
                "Use .netrc",
                value=opts.get("netrc", False),
                key="opt_netrc",
            )
            opts["no_check_certificates"] = st.checkbox(
                "No Check Certificates",
                value=opts.get("no_check_certificates", False),
                key="opt_no_cert",
            )
            opts["prefer_insecure"] = st.checkbox(
                "Prefer Insecure",
                value=opts.get("prefer_insecure", False),
                key="opt_prefer_insecure",
            )

    with st.expander("🛡 SponsorBlock", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["sponsorblock"] = st.selectbox(
                "SponsorBlock",
                options=[None, "mark", "remove"],
                format_func=lambda x: "None" if x is None else x.capitalize(),
                key="opt_sponsorblock",
            )
            opts["sponsorblock_categories"] = st.multiselect(
                "Categories",
                options=["sponsor", "intro", "outro", "selfpromo", "interaction", "music_offtopic", "preview", "filler"],
                default=opts.get("sponsorblock_categories") or [],
                key="opt_sb_categories",
            )
        with c2:
            opts["sponsorblock_api_url"] = st.text_input(
                "API URL",
                value=opts.get("sponsorblock_api_url", "https://sponsor.ajay.app"),
                key="opt_sb_api",
            )
            opts["sponsorblock_chapter_title"] = st.text_input(
                "Chapter Title",
                value=opts.get("sponsorblock_chapter_title") or "",
                placeholder="Template for marked segments",
                key="opt_sb_chapter",
            ) or None

    with st.expander("📁 Output Template", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["outtmpl"] = st.text_input(
                "Output Template",
                value=opts.get("outtmpl") or "",
                placeholder="%(title)s.%(ext)s",
                key="opt_outtmpl",
            ) or None
            opts["restrict_filenames"] = st.checkbox(
                "Restrict Filenames",
                value=opts.get("restrict_filenames", False),
                key="opt_restrict",
            )
            opts["windows_filenames"] = st.checkbox(
                "Windows Filenames",
                value=opts.get("windows_filenames", False),
                key="opt_windows",
            )
        with c2:
            opts["trim_filenames"] = st.number_input(
                "Trim Filenames",
                value=opts.get("trim_filenames") or 0,
                min_value=0,
                key="opt_trim",
            ) or None
            opts["no_part_files"] = st.checkbox(
                "No Part Files",
                value=opts.get("no_part_files", False),
                key="opt_no_part",
            )

        with st.expander("Template Variables Reference"):
            st.markdown("""
            | Variable | Description |
            |----------|-------------|
            | `%(title)s` | Video title |
            | `%(id)s` | Video ID |
            | `%(uploader)s` | Uploader name |
            | `%(upload_date)s` | YYYYMMDD |
            | `%(duration)s` | Duration in seconds |
            | `%(ext)s` | File extension |
            | `%(resolution)s` | e.g. 1920x1080 |
            | `%(fps)s` | Frames per second |
            | `%(tbr)s` | Total bitrate |
            | `%(vcodec)s` | Video codec |
            | `%(acodec)s` | Audio codec |
            | `%(filesize)s` | File size bytes |
            | `%(playlist_index)s` | Index in playlist |
            | `%(playlist_title)s` | Playlist title |
            | `%(channel)s` | Channel name |
            | `%(epoch)s` | Unix timestamp |
            | `%(autonumber)s` | Auto-incrementing number |
            | `%(release_date)s` | Release date YYYYMMDD |
            | `%(view_count)s` | View count |
            """)

    with st.expander("🔧 Extractor Options", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            opts["extract_flat"] = st.selectbox(
                "Flat Playlist",
                options=[False, True, "in_playlist"],
                format_func=lambda x: {False: "Disabled", True: "Enabled", "in_playlist": "If Known"}.get(x, "Disabled"),
                key="opt_extract_flat",
            )
        with c2:
            opts["extractor_args"] = st.text_area(
                "Extractor Args",
                value=json.dumps(opts.get("extractor_args") or {}, indent=2),
                height=100,
                key="opt_extractor_args",
            )

    section_heading("Actions")

    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
    with btn_col1:
        preview_clicked = st.button("Preview Info", key="preview_btn", use_container_width=True)
    with btn_col2:
        formats_clicked = st.button("List Formats", key="formats_btn", use_container_width=True)
    with btn_col3:
        dl_clicked = st.button("⬇ Download", key="dl_btn", use_container_width=True, type="primary")

    if preview_clicked:
        if not url:
            st.error("Please enter a URL.")
        else:
            with st.spinner("Fetching video info…"):
                info, err = api_get_info(url)
            if err:
                st.error(f"Error: {err}")
            else:
                st.session_state.preview_info = info

    if formats_clicked:
        if not url:
            st.error("Please enter a URL.")
        else:
            with st.spinner("Fetching formats…"):
                data, err = api_get_formats(url)
            if err:
                st.error(f"Error: {err}")
            else:
                st.session_state.format_data = data

    if st.session_state.preview_info:
        info = st.session_state.preview_info
        section_heading("Preview")
        thumb = info.get("thumbnail", "")
        title = info.get("title", "Unknown")
        uploader = info.get("uploader", "—")
        duration = fmt_duration(info.get("duration"))
        views = info.get("view_count")
        views_str = f" · {views:,.0f} views" if views else ""
        upload_date = info.get("upload_date", "")
        if upload_date and len(upload_date) == 8:
            upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

        fmts = info.get("formats", [])
        badge_html = ""
        if fmts:
            heights = sorted(
                set(f["height"] for f in fmts if f.get("height")),
                reverse=True,
            )[:6]
            badge_html = " ".join(
                f'<span class="sl-badge sl-badge-default">{h}p</span>' for h in heights
            )
            if any(f.get("acodec") and f.get("acodec") != "none" and not f.get("height") for f in fmts):
                badge_html += ' <span class="sl-badge sl-badge-default">audio</span>'

        p_col1, p_col2 = st.columns([1, 2.5])
        with p_col1:
            if thumb:
                st.image(thumb, use_container_width=True)
        with p_col2:
            st.markdown(f"""
            <div style="padding:0.25rem 0">
                <div class="sl-preview-title">{title}</div>
                <div class="sl-preview-meta">
                    {uploader} &nbsp;·&nbsp; {duration}{views_str}
                </div>
                <div style="display:flex;gap:0.375rem;flex-wrap:wrap;margin-bottom:0.5rem">{badge_html}</div>
                {'<div class="sl-preview-meta">Upload: ' + upload_date + '</div>' if upload_date else ''}
            </div>
            """, unsafe_allow_html=True)

    section_heading("Command Preview")
    cmd = build_command_preview(opts, url or "")
    st.code(cmd, language="bash")

    if dl_clicked:
        if not url:
            st.error("Please enter a URL.")
        else:
            with st.spinner("Queuing download…"):
                job, err = api_start_download(url, opts)
            if err:
                st.error(f"Error: {err}")
            else:
                if job and isinstance(job, dict) and "id" in job:
                    st.session_state.jobs[job["id"]] = {**job, "_cancel": False}
                st.success("Download queued! Check the **Queue** tab.")
                st.session_state.preview_info = None


def render_queue_tab():
    active = live_queue_jobs()

    if not active:
        empty_state("📭", "Queue empty", "Start a download from the Download tab")
        return

    section_heading(f"{len(active)} active download{'s' if len(active) > 1 else ''}")

    for job in active:
        jid = job["id"]
        status = job.get("status", "queued")
        progress = job.get("progress", 0.0)
        detail = job.get("progress_detail", {})

        meta_parts = [
            status_badge(status),
            badge(job.get("format", "?").upper()),
            badge(job.get("quality", "?")),
        ]
        if job.get("playlist"):
            meta_parts.append(badge("playlist", "warning"))

        url_display = (job.get("url", ""))[:55]
        if len(job.get("url", "")) > 55:
            url_display += "…"

        st.markdown(f"""
        <div class="sl-job-card">
          <div class="sl-job-title">{job.get('title') or 'Fetching title…'}</div>
          <div class="sl-job-meta">
            {''.join(meta_parts)}
            <span style="opacity:0.35">{url_display}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if status == "running":
            st.progress(min(int(progress), 100), text=f"{progress:.1f}%")
            speed = fmt_speed(detail.get("speed"))
            eta_raw = detail.get("eta")
            eta = f"{int(eta_raw // 60)}:{int(eta_raw % 60):02d}" if eta_raw else "—"
            downloaded = fmt_bytes(detail.get("downloaded_bytes"))
            total = fmt_bytes(detail.get("total_bytes") or detail.get("total_bytes_estimate"))
            st.markdown(f"""
            <div class="sl-progress-detail">
              <span>↓ {speed}</span>
              <span>ETA {eta}</span>
              <span>{downloaded} / {total}</span>
            </div>
            """, unsafe_allow_html=True)
        elif status == "queued":
            st.progress(0, text="Waiting in queue…")

        c1, c2 = st.columns([1, 5])
        with c1:
            if st.button("Cancel", key=f"cancel_{jid}", use_container_width=True):
                api_cancel_job(jid)
                st.rerun()

    running = any(j.get("status") == "running" for j in active)
    if running:
        st.markdown(
            '<div style="text-align:center;font-size:0.6875rem;color:hsl(0 0% 30%);'
            'padding:0.75rem 0">Auto-refreshing…</div>',
            unsafe_allow_html=True,
        )
        time.sleep(1.5)
        st.rerun()


def render_formats_tab():
    section_heading("Inspect Formats")

    f_col1, f_col2 = st.columns([4, 1])
    with f_col1:
        url = st.text_input(
            "URL to inspect",
            placeholder="https://youtube.com/watch?v=...",
            key="formats_url",
        )
    with f_col2:
        st.markdown('<div style="height:1.6rem"></div>', unsafe_allow_html=True)
        fetch_clicked = st.button("Fetch", key="fetch_formats_btn", type="primary", use_container_width=True)

    if fetch_clicked:
        if not url:
            st.error("Please enter a URL.")
        else:
            with st.spinner("Fetching formats…"):
                data, err = api_get_formats(url)
            if err:
                st.error(f"Error: {err}")
            else:
                st.session_state.format_data = data

    if st.session_state.get("format_data"):
        data = st.session_state.format_data
        title = data.get("title", "Unknown")
        uploader = data.get("uploader", "—")
        duration = fmt_duration(data.get("duration"))

        st.markdown(f"""
        <div class="sl-card" style="margin:0.75rem 0">
            <div class="sl-preview-title">{title}</div>
            <div class="sl-preview-meta">{uploader} &nbsp;·&nbsp; {duration}</div>
        </div>
        """, unsafe_allow_html=True)

        formats = data.get("formats", [])

        fc1, fc2 = st.columns([1, 1])
        with fc1:
            filter_type = st.radio("Filter", ["All", "Video Only", "Audio Only"], horizontal=True, key="fmt_filter")
        with fc2:
            sort_by = st.selectbox("Sort by", ["Resolution", "Bitrate", "Size", "Codec"], key="fmt_sort")

        if filter_type == "Video Only":
            formats = [f for f in formats if f.get("vcodec") and f.get("vcodec") != "none"]
        elif filter_type == "Audio Only":
            formats = [f for f in formats if (f.get("acodec") and f.get("acodec") != "none" and (not f.get("vcodec") or f.get("vcodec") == "none"))]

        if formats:
            st.dataframe(formats, use_container_width=True, height=350)

            a_col1, a_col2 = st.columns([2, 1])
            with a_col1:
                fmt_id = st.text_input("Use format ID", placeholder="e.g. 137+140", key="apply_fmt_id")
            with a_col2:
                st.markdown('<div style="height:1.6rem"></div>', unsafe_allow_html=True)
                if st.button("Apply to Download Tab →", key="apply_fmt_btn", use_container_width=True):
                    if fmt_id:
                        st.session_state.dl_opts["format"] = fmt_id
                        st.success(f"Format `{fmt_id}` applied.")
        else:
            empty_state("🎞️", "No formats found", "Try a different URL or filter")


def render_history_tab():
    section_heading("Download History")

    h_col1, h_col2 = st.columns([2, 1])
    with h_col1:
        search = st.text_input("Search", placeholder="Filter by title or URL…", key="history_search", label_visibility="collapsed")
    with h_col2:
        status_filter = st.multiselect(
            "Status",
            options=["done", "error", "cancelled"],
            key="history_status_filter",
            label_visibility="collapsed",
            placeholder="Filter by status",
        )

    jobs = api_get_history()

    if search:
        sl = search.lower()
        jobs = [j for j in jobs if sl in (j.get("title") or "").lower() or sl in (j.get("url") or "").lower()]

    if status_filter:
        jobs = [j for j in jobs if j.get("status") in status_filter]

    if not jobs:
        empty_state("📂", "No history yet", "Completed downloads will appear here")
        return

    jobs = list(reversed(jobs))

    # Pagination
    page_size = 20
    if "history_page" not in st.session_state:
        st.session_state.history_page = 0
    total_pages = max(1, (len(jobs) + page_size - 1) // page_size)
    page = min(st.session_state.history_page, total_pages - 1)
    page_jobs = jobs[page * page_size:(page + 1) * page_size]

    for job in page_jobs:
        status = job.get("status", "done")
        title = job.get("title") or job.get("url", "Unknown")
        created = job.get("created_at", "")[:16].replace("T", " ")
        filepath = job.get("filepath", "")
        error_msg = job.get("error_msg", "")

        meta_parts = [
            status_badge(status),
            f'<span class="sl-badge sl-badge-default">{job.get("format", "?").upper()}</span>',
            f'<span class="sl-badge sl-badge-default">{job.get("quality", "?")}</span>',
            f'<span style="opacity:0.4">{created}</span>',
        ]

        filepath_html = ""
        if filepath:
            filepath_html = (
                f'<div style="font-family:\'Geist Mono\',monospace;font-size:0.6875rem;'
                f'color:hsl(0 0% 35%);margin-top:0.375rem;overflow:hidden;text-overflow:ellipsis">'
                f'{filepath}</div>'
            )

        st.markdown(f"""
        <div class="sl-job-card">
            <div class="sl-job-title">{title}</div>
            <div class="sl-job-meta">{''.join(meta_parts)}</div>
            {filepath_html}
        </div>
        """, unsafe_allow_html=True)

        if error_msg:
            with st.expander("Error details"):
                st.code(error_msg, language=None)

        if status == "error":
            if st.button("↺ Retry", key=f"retry_{job.get('id', created)}"):
                st.session_state.dl_opts["url"] = job.get("url", "")
                st.success("URL loaded in Download tab. Switch tabs to retry.")

    # Pagination controls
    if total_pages > 1:
        p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
        with p_col1:
            if st.button("← Previous", key="hist_prev", disabled=(page == 0), use_container_width=True):
                st.session_state.history_page = max(0, page - 1)
                st.rerun()
        with p_col2:
            st.markdown(
                f'<div class="sl-pagination">Page {page + 1} of {total_pages}</div>',
                unsafe_allow_html=True,
            )
        with p_col3:
            if st.button("Next →", key="hist_next", disabled=(page >= total_pages - 1), use_container_width=True):
                st.session_state.history_page = min(total_pages - 1, page + 1)
                st.rerun()


def render_settings_tab():
    # ── Section 1: Cookie Authentication ──
    section_heading("Cookie Authentication")

    st.markdown("""
    <div class="sl-settings-card">
        <div style="display:flex;align-items:flex-start;gap:0.75rem">
          <span style="font-size:1.25rem">🍪</span>
          <div style="font-size:0.8125rem;color:hsl(var(--muted-foreground));line-height:1.6">
            Some platforms require authentication cookies. Export your browser cookies as a
            <code>cookies.txt</code> (Netscape format) using a browser extension, then upload here.
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📤 Upload cookies.txt"):
        uploaded = st.file_uploader(
            "Upload cookies.txt",
            type=["txt"],
            key="cookie_upload",
            help="Netscape HTTP Cookie File format",
            label_visibility="collapsed",
        )
        if uploaded:
            if st.button("Upload cookies", key="upload_cookie_btn", type="primary"):
                ok, msg = api_upload_cookies(uploaded.read())
                if ok:
                    st.success(msg)
                else:
                    st.warning(msg)

    with st.expander("🌐 Load from browser"):
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            browser = st.selectbox(
                "Browser",
                options=[None, "chrome", "firefox", "edge", "safari", "brave", "opera", "vivaldi"],
                format_func=lambda x: "Select browser…" if x is None else x.capitalize(),
                key="settings_cookie_browser",
            )
        with b_col2:
            profile = st.text_input("Profile (optional)", placeholder="Default", key="settings_cookie_profile")
        if browser:
            if st.button("Apply browser cookies", key="apply_browser_cookies"):
                st.session_state.dl_opts["cookies_from_browser"] = browser
                st.success(f"Browser cookies set to **{browser}**")

    with st.expander("📑 Bookmarklet (YouTube)"):
        bookmarklet_code = """javascript:(function(){
  var cs=document.cookie.split(';').map(c=>{var p=c.trim().split('=');return{name:p[0],value:p.slice(1).join('='),domain:location.hostname,path:'/',secure:true};});
  fetch('http://localhost:8000/api/settings/cookies/youtube',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer TOKEN'},body:JSON.stringify({cookies:cs})}).then(r=>r.json()).then(d=>alert('Streamline: '+d.message)).catch(e=>alert('Error: '+e));
})();"""
        st.code(bookmarklet_code, language="javascript")
        st.markdown(
            '<p style="font-size:0.75rem;color:hsl(var(--muted-foreground));line-height:1.6">'
            'Replace <code>TOKEN</code> with your Bearer token, drag to bookmarks bar. '
            'Click while on YouTube to sync cookies.</p>',
            unsafe_allow_html=True,
        )

    # ── Section 2: Default Download Options ──
    section_heading("Default Download Options")

    st.markdown(
        '<div class="sl-settings-card">'
        '<div style="font-size:0.8125rem;color:hsl(var(--muted-foreground));margin-bottom:0.75rem">'
        'Save your current download options as defaults, or load previously saved defaults.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    d_col1, d_col2, d_col3 = st.columns([1, 1, 2])
    with d_col1:
        if st.button("Load Defaults", key="load_defaults_btn", use_container_width=True):
            defaults = api_get_defaults()
            if defaults:
                st.session_state.defaults = defaults
                st.success("Defaults loaded")
            else:
                st.info("No saved defaults found")
    with d_col2:
        if st.button("Save Current", key="save_defaults_btn", use_container_width=True, type="primary"):
            if api_save_defaults(st.session_state.dl_opts):
                st.success("Defaults saved")
            else:
                st.warning("Failed to save defaults")

    # ── Section 3: yt-dlp Info ──
    section_heading("yt-dlp Info")

    if st.button("Check Versions", key="check_versions_btn"):
        versions = api_get_tool_versions()
        if versions:
            ytdlp_ver = versions.get("yt_dlp", "unknown")
            ffmpeg_ver = versions.get("ffmpeg", "")
            ffprobe_ver = versions.get("ffprobe", "")
            aria2c_ver = versions.get("aria2c", "")

            st.markdown(f"""
            <div class="sl-settings-card">
                <div class="sl-version-row">
                    <span class="sl-version-ok">✓</span>
                    <span>yt-dlp</span>
                    <span style="color:hsl(var(--muted-foreground))">{ytdlp_ver}</span>
                </div>
                <div class="sl-version-row">
                    <span class="{'sl-version-ok' if ffmpeg_ver else 'sl-version-missing'}">{'✓' if ffmpeg_ver else '✗'}</span>
                    <span>ffmpeg</span>
                    <span style="color:hsl(var(--muted-foreground))">{ffmpeg_ver or 'not found'}</span>
                </div>
                <div class="sl-version-row">
                    <span class="{'sl-version-ok' if ffprobe_ver else 'sl-version-missing'}">{'✓' if ffprobe_ver else '✗'}</span>
                    <span>ffprobe</span>
                    <span style="color:hsl(var(--muted-foreground))">{ffprobe_ver or 'not found'}</span>
                </div>
                <div class="sl-version-row">
                    <span class="{'sl-version-ok' if aria2c_ver else 'sl-version-missing'}">{'✓' if aria2c_ver else '✗'}</span>
                    <span>aria2c</span>
                    <span style="color:hsl(var(--muted-foreground))">{aria2c_ver or 'not found'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Could not fetch version info (backend offline?)")

    # ── Section 4: Session & Account ──
    section_heading("Session")

    cols = st.columns(4)
    with cols[0]:
        st.metric("User", st.session_state.email or "—")
    with cols[1]:
        total = len(st.session_state.jobs)
        st.metric("Total Jobs", total)
    with cols[2]:
        done = sum(1 for j in st.session_state.jobs.values() if j.get("status") == "done")
        st.metric("Completed", done)
    with cols[3]:
        mode = "Demo" if st.session_state.token == "demo-token" else "Live"
        st.metric("Mode", mode)


if not st.session_state.token:
    render_auth()
else:
    render_app()
