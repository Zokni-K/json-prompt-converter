"""
Nano Banana 2 JSON Prompt Converter — Streamlit UI
Run: streamlit run app.py
"""

import json
import re
import streamlit as st
from pathlib import Path
from datetime import datetime
from converter import convert

st.set_page_config(
    page_title="NB2 Prompt Converter",
    page_icon="🍌",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SAVE_BASE = Path(__file__).parent / "saved-prompts"
SAVE_BASE.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_json_str" not in st.session_state:
    st.session_state.last_json_str = ""
if "save_status" not in st.session_state:
    st.session_state.save_status = ""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_folders():
    return sorted([f.name for f in SAVE_BASE.iterdir() if f.is_dir()])

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:50].strip("-")

def save_prompt(folder: str, json_str: str, objective: str):
    folder_path = SAVE_BASE / folder
    folder_path.mkdir(exist_ok=True)
    slug = slugify(objective) or "prompt"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{slug}-{timestamp}.json"
    (folder_path / filename).write_text(json_str)
    return filename

def get_saved_prompts():
    result = {}
    for folder in sorted(SAVE_BASE.iterdir()):
        if folder.is_dir():
            files = sorted(folder.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
            if files:
                result[folder.name] = files
    return result

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
/* ── Base ─────────────────────────────────────────────── */
html, body, [data-testid="stApp"] {
    background-color: #0D0D0D;
    color: #FFFFFF;
}

/* ── Hide default Streamlit chrome ────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Typography ───────────────────────────────────────── */
h1, h2, h3, h4 { letter-spacing: -0.02em; }

/* ── Wordmark ─────────────────────────────────────────── */
.nb-wordmark {
    font-size: 13px; font-weight: 700;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: #C6FF00; margin-bottom: 0;
}

/* ── Hero ─────────────────────────────────────────────── */
.nb-hero-label {
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: #666666; margin-bottom: 8px;
}
.nb-hero-title {
    font-size: 42px; font-weight: 800;
    line-height: 1.1; color: #FFFFFF; margin: 0 0 6px 0;
}
.nb-hero-title span { color: #C6FF00; }
.nb-hero-sub {
    font-size: 14px; color: #777777;
    margin-bottom: 32px; line-height: 1.6;
}

/* ── Divider ──────────────────────────────────────────── */
.nb-divider {
    border: none; border-top: 1px solid #1E1E1E; margin: 28px 0;
}

/* ── Text area ────────────────────────────────────────── */
textarea {
    background-color: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-size: 15px !important;
    caret-color: #C6FF00; resize: vertical;
}
textarea:focus {
    border-color: #C6FF00 !important;
    box-shadow: 0 0 0 2px rgba(198,255,0,0.15) !important;
    outline: none !important;
}
[data-baseweb="textarea"] {
    background-color: #141414 !important;
    border-color: #242424 !important;
}
label[data-testid="stWidgetLabel"] p {
    color: #999999 !important; font-size: 12px !important;
    font-weight: 600 !important; text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── Select box ───────────────────────────────────────── */
[data-baseweb="select"] > div {
    background-color: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #C6FF00 !important;
}
[data-baseweb="popover"] { background-color: #1A1A1A !important; }
[role="option"] { background-color: #1A1A1A !important; color: #FFFFFF !important; }
[role="option"]:hover { background-color: #242424 !important; }

/* ── Text input ───────────────────────────────────────── */
input[type="text"] {
    background-color: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}
input[type="text"]:focus {
    border-color: #C6FF00 !important;
    box-shadow: 0 0 0 2px rgba(198,255,0,0.15) !important;
}

/* ── All buttons base ─────────────────────────────────── */
.stButton > button {
    font-weight: 800 !important; font-size: 12px !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    border-radius: 6px !important;
    transition: background 0.15s ease, transform 0.1s ease !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Primary (Convert) ────────────────────────────────── */
button[kind="primary"] {
    background-color: #C6FF00 !important;
    color: #0D0D0D !important;
    border: none !important;
}
button[kind="primary"]:hover { background-color: #D4FF33 !important; }

/* ── Secondary buttons (Save, Clear, Create) ──────────── */
button[kind="secondary"] {
    background-color: transparent !important;
    border: 1px solid #2A2A2A !important;
    color: #888888 !important;
}
button[kind="secondary"]:hover {
    border-color: #C6FF00 !important;
    color: #C6FF00 !important;
    background-color: rgba(198,255,0,0.05) !important;
}

/* ── Download button ──────────────────────────────────── */
.stDownloadButton > button {
    background-color: transparent !important;
    border: 1px solid #C6FF00 !important;
    color: #C6FF00 !important;
    font-weight: 700 !important; font-size: 12px !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    border-radius: 6px !important;
}
.stDownloadButton > button:hover {
    background-color: rgba(198,255,0,0.08) !important;
}

/* ── Save section card ────────────────────────────────── */
.save-card {
    background-color: #111111;
    border: 1px solid #1E1E1E;
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
}
.save-card-label {
    font-size: 11px; font-weight: 700;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: #555555; margin-bottom: 12px;
}

/* ── Metric cards ─────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: #141414;
    border: 1px solid #1E1E1E;
    border-radius: 10px;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] p {
    color: #666666 !important; font-size: 11px !important;
    font-weight: 600 !important; text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}
[data-testid="stMetricValue"] {
    color: #C6FF00 !important; font-size: 18px !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] { display: none; }

/* ── Code block ───────────────────────────────────────── */
[data-testid="stCodeBlock"] {
    background-color: #0A0A0A !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 10px !important;
}
[data-testid="stCodeBlock"] pre { background-color: #0A0A0A !important; }
[data-testid="stCodeBlock"] code {
    color: #CCCCCC !important; font-size: 13px !important;
}
.hljs-attr    { color: #C6FF00 !important; }
.hljs-string  { color: #88C0D0 !important; }
.hljs-number  { color: #B48EAD !important; }
.hljs-literal { color: #81A1C1 !important; }

/* ── Expander ─────────────────────────────────────────── */
[data-testid="stExpander"] {
    background-color: #141414 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #888888 !important; font-size: 12px !important;
    font-weight: 600 !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stExpander"] summary:hover { color: #C6FF00 !important; }

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0A0A0A !important;
    border-right: 1px solid #1A1A1A !important;
}
[data-testid="stSidebar"] h3 {
    color: #C6FF00 !important; font-size: 11px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] li { color: #777777 !important; font-size: 12px !important; line-height: 1.7 !important; }
[data-testid="stSidebar"] code {
    background-color: #141414 !important; border-radius: 3px !important;
    padding: 1px 5px !important; color: #C6FF00 !important;
}
[data-testid="stSidebarContent"] hr { border-color: #1E1E1E !important; }

/* ── Misc ─────────────────────────────────────────────── */
[data-testid="column"] { padding: 0 6px !important; }
[data-testid="stAlert"] {
    background-color: #141414 !important;
    border: 1px solid #C6FF00 !important;
    border-radius: 8px !important; color: #C6FF00 !important;
}
hr { border-color: #1E1E1E !important; margin: 24px 0 !important; }
[data-testid="stCaptionContainer"] p { color: #444444 !important; font-size: 11px !important; }
.stSuccess { background-color: #141414 !important; border-color: #C6FF00 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown('<p class="nb-wordmark">NB2.</p>', unsafe_allow_html=True)
st.markdown("""
<div style="margin-top: 24px; margin-bottom: 32px;">
    <p class="nb-hero-label">Structured image prompts</p>
    <h1 class="nb-hero-title">Turn any idea into a<br><span>JSON prompt.</span></h1>
    <p class="nb-hero-sub">
        Paste a plain description. Get a structured Nano Banana 2 prompt back instantly.<br>
        No tokens. No API calls. Pure keyword matching.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

prompt = st.text_area(
    "Your prompt",
    placeholder="e.g. a French Bulldog in a golden field at sunset, cinematic, wide angle",
    height=110,
    label_visibility="collapsed",
    key=f"prompt_{st.session_state.input_key}",
)

col_btn, col_clear, col_hint = st.columns([1, 1, 3])
with col_btn:
    convert_btn = st.button("Convert →", type="primary", use_container_width=True)
with col_clear:
    if st.button("Clear", use_container_width=True):
        st.session_state.input_key += 1
        st.session_state.last_result = None
        st.session_state.last_json_str = ""
        st.session_state.save_status = ""
        st.rerun()
with col_hint:
    st.caption("Try: `portrait`, `golden hour`, `cinematic`, `close-up`, `moody`")

# ---------------------------------------------------------------------------
# Convert
# ---------------------------------------------------------------------------

if convert_btn and prompt.strip():
    st.session_state.last_result = convert(prompt)
    st.session_state.last_json_str = json.dumps(st.session_state.last_result, indent=2)
    st.session_state.save_status = ""
elif convert_btn and not prompt.strip():
    st.warning("Enter a prompt first.")

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

if st.session_state.last_result:
    result = st.session_state.last_result
    json_str = st.session_state.last_json_str

    st.markdown('<hr class="nb-divider">', unsafe_allow_html=True)

    # Metric row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lighting", result["lighting"]["type"].split()[0].title())
    c2.metric("Lens", result["camera"]["lens"])
    c3.metric("Aperture", result["camera"]["aperture"])
    c4.metric("Aspect", result["settings"]["aspect_ratio"])

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # JSON output
    st.code(json_str, language="json")

    # Download
    col_dl, col_space = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="nb2_prompt.json",
            mime="application/json",
            use_container_width=True,
        )

    # ── Save section ────────────────────────────────────────
    st.markdown('<hr class="nb-divider">', unsafe_allow_html=True)
    st.markdown('<p class="save-card-label">Save Prompt</p>', unsafe_allow_html=True)

    folders = get_folders()
    folder_options = folders + ["+ Create new folder"]

    col_folder, col_new = st.columns([2, 2])

    with col_folder:
        selected = st.selectbox(
            "Folder",
            options=folder_options,
            label_visibility="collapsed",
        )

    new_folder_name = ""
    with col_new:
        if selected == "+ Create new folder":
            new_folder_name = st.text_input(
                "New folder name",
                placeholder="e.g. portraits, landscapes",
                label_visibility="collapsed",
            )
        else:
            st.markdown("<div style='height:38px'></div>", unsafe_allow_html=True)

    col_save, col_spacer = st.columns([1, 3])
    with col_save:
        save_btn = st.button("Save Prompt", use_container_width=True)

    if save_btn:
        target_folder = new_folder_name.strip() if selected == "+ Create new folder" else selected
        if not target_folder:
            st.warning("Enter a folder name first.")
        else:
            filename = save_prompt(
                target_folder,
                json_str,
                result.get("Objective", "prompt"),
            )
            st.session_state.save_status = f"Saved to {target_folder}/{filename}"
            st.rerun()

    if st.session_state.save_status:
        st.markdown(
            f"<p style='color:#C6FF00;font-size:12px;margin-top:8px'>{st.session_state.save_status}</p>",
            unsafe_allow_html=True,
        )

    # Breakdown
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.expander("What was detected"):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<span style='color:#C6FF00;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase'>Subject</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#cccccc;font-size:14px;margin:4px 0 16px'>{result['subject']['description'] or '—'}</p>", unsafe_allow_html=True)
            if result["subject"]["appearance"]:
                st.markdown(f"<p style='color:#888;font-size:13px'>Appearance: {result['subject']['appearance']}</p>", unsafe_allow_html=True)
            st.markdown("<span style='color:#C6FF00;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase'>Environment</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#cccccc;font-size:14px;margin:4px 0 4px'>{result['environment']['location'] or '—'}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#888;font-size:13px'>{result['environment']['time_of_day']}</p>", unsafe_allow_html=True)
        with col_b:
            st.markdown("<span style='color:#C6FF00;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase'>Style</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#cccccc;font-size:14px;margin:4px 0 4px'>{result['style']['aesthetic']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#888;font-size:13px'>{result['style']['color_grade']}</p>", unsafe_allow_html=True)
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown("<span style='color:#C6FF00;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase'>Negative Constraints</span>", unsafe_allow_html=True)
            for n in result["negative_constraints"]:
                st.markdown(f"<p style='color:#666;font-size:12px;margin:2px 0'>— {n}</p>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar — keyword reference + saved prompts browser
# ---------------------------------------------------------------------------

with st.sidebar:
    # Saved prompts browser
    saved = get_saved_prompts()
    if saved:
        st.markdown("### Saved Prompts")
        for folder_name, files in saved.items():
            with st.expander(f"{folder_name}  ({len(files)})"):
                for f in files:
                    # Clean display name: strip timestamp suffix
                    display = re.sub(r"-\d{8}-\d{6}$", "", f.stem).replace("-", " ").title()
                    col_name, col_del = st.columns([4, 1])
                    with col_name:
                        st.markdown(f"<p style='color:#aaa;font-size:12px;margin:2px 0'>{display}</p>", unsafe_allow_html=True)
                    with col_del:
                        if st.button("✕", key=f"del_{f}", help=f"Delete {f.name}"):
                            f.unlink()
                            st.rerun()
        st.divider()

    # Keyword reference
    st.markdown("### Lighting")
    st.markdown("`warm` · `dramatic` · `golden hour` · `soft` · `flash` · `neon` · `moody` · `studio` · `backlit` · `silhouette`")
    st.divider()
    st.markdown("### Camera")
    st.markdown("`portrait` · `wide` · `close-up` · `candid` · `street` · `editorial` · `macro` · `full body` · `low angle` · `overhead`")
    st.divider()
    st.markdown("### Style")
    st.markdown("`cinematic` · `vintage` · `noir` · `editorial` · `documentary` · `watercolor` · `anime` · `film` · `cyberpunk` · `minimalist`")
    st.divider()
    st.markdown("### Time of Day")
    st.markdown("`golden hour` · `night` · `sunrise` · `sunset` · `dusk` · `dawn` · `midday`")
    st.divider()
    st.markdown("### Aspect Ratio")
    st.markdown("`square` · `portrait` · `landscape` · `vertical` · `cinematic` · `widescreen`")
    st.divider()
    st.markdown("<p style='color:#333;font-size:11px'>Zero tokens. Runs locally.</p>", unsafe_allow_html=True)
