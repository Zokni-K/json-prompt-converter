"""
Nano Banana 2 JSON Prompt Converter — Streamlit UI
Run: streamlit run app.py
"""

import json
import streamlit as st
from converter import convert

st.set_page_config(
    page_title="NB2 Prompt Converter",
    page_icon="🍌",
    layout="centered",
)

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
h1, h2, h3, h4 {
    letter-spacing: -0.02em;
}

/* ── Top wordmark ─────────────────────────────────────── */
.nb-wordmark {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #C6FF00;
    margin-bottom: 0;
}

/* ── Hero block ───────────────────────────────────────── */
.nb-hero-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #666666;
    margin-bottom: 8px;
}

.nb-hero-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.1;
    color: #FFFFFF;
    margin: 0 0 6px 0;
}

.nb-hero-title span {
    color: #C6FF00;
}

.nb-hero-sub {
    font-size: 14px;
    color: #777777;
    margin-bottom: 32px;
    line-height: 1.6;
}

/* ── Divider ──────────────────────────────────────────── */
.nb-divider {
    border: none;
    border-top: 1px solid #1E1E1E;
    margin: 28px 0;
}

/* ── Text area ────────────────────────────────────────── */
textarea {
    background-color: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-size: 15px !important;
    caret-color: #C6FF00;
    resize: vertical;
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
    color: #999999 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── Buttons ──────────────────────────────────────────── */
button[kind="primary"], .stButton > button {
    background-color: #C6FF00 !important;
    color: #0D0D0D !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 24px !important;
    transition: background 0.15s ease, transform 0.1s ease !important;
}
.stButton > button:hover {
    background-color: #D4FF33 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Download button ──────────────────────────────────── */
.stDownloadButton > button {
    background-color: transparent !important;
    border: 1px solid #C6FF00 !important;
    color: #C6FF00 !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 6px !important;
}
.stDownloadButton > button:hover {
    background-color: rgba(198,255,0,0.08) !important;
}

/* ── Metric cards ─────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: #141414;
    border: 1px solid #1E1E1E;
    border-radius: 10px;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] p {
    color: #666666 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}
[data-testid="stMetricValue"] {
    color: #C6FF00 !important;
    font-size: 18px !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] { display: none; }

/* ── Code block ───────────────────────────────────────── */
[data-testid="stCodeBlock"] {
    background-color: #0A0A0A !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 10px !important;
}
[data-testid="stCodeBlock"] pre {
    background-color: #0A0A0A !important;
}
[data-testid="stCodeBlock"] code {
    color: #CCCCCC !important;
    font-size: 13px !important;
}
/* JSON syntax colors */
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
    color: #888888 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stExpander"] summary:hover {
    color: #C6FF00 !important;
}

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0A0A0A !important;
    border-right: 1px solid #1A1A1A !important;
}
[data-testid="stSidebar"] h3 {
    color: #C6FF00 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] code {
    color: #777777 !important;
    font-size: 12px !important;
    line-height: 1.7 !important;
}
[data-testid="stSidebar"] code {
    background-color: #141414 !important;
    border-radius: 3px !important;
    padding: 1px 5px !important;
    color: #C6FF00 !important;
}
[data-testid="stSidebarContent"] hr {
    border-color: #1E1E1E !important;
}

/* ── Columns gap ──────────────────────────────────────── */
[data-testid="column"] { padding: 0 6px !important; }

/* ── Warning ──────────────────────────────────────────── */
[data-testid="stAlert"] {
    background-color: #141414 !important;
    border: 1px solid #C6FF00 !important;
    border-radius: 8px !important;
    color: #C6FF00 !important;
}

/* ── Horizontal rule ──────────────────────────────────── */
hr {
    border-color: #1E1E1E !important;
    margin: 24px 0 !important;
}

/* ── Caption text ─────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
    color: #444444 !important;
    font-size: 11px !important;
}
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
)

col_btn, col_hint = st.columns([1, 3])
with col_btn:
    convert_btn = st.button("Convert →", type="primary", use_container_width=True)
with col_hint:
    st.caption("Try: `portrait`, `golden hour`, `cinematic`, `close-up`, `moody`")

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

if convert_btn and prompt.strip():
    result = convert(prompt)

    st.markdown('<hr class="nb-divider">', unsafe_allow_html=True)

    # Metric row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lighting", result["lighting"]["type"].split()[0].title())
    c2.metric("Lens", result["camera"]["lens"])
    c3.metric("Aperture", result["camera"]["aperture"])
    c4.metric("Aspect", result["settings"]["aspect_ratio"])

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # JSON output
    json_str = json.dumps(result, indent=2)
    st.code(json_str, language="json")

    col_dl, col_space = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="nb2_prompt.json",
            mime="application/json",
            use_container_width=True,
        )

    # Breakdown
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

elif convert_btn and not prompt.strip():
    st.warning("Enter a prompt first.")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
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
