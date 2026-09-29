"""streamlit_app.py – Defender Fraud Detection Dashboard (Dark Glass Edition)"""
import streamlit as st

st.set_page_config(
    page_title="Defender – Anti-Fraud",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛡</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "lang" not in st.session_state:
    st.session_state.lang = "ru"

# ─── DARK GLASS CSS + ANIMATIONS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ═══ RESET & BASE ═══════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body { font-family: 'Inter', -apple-system, sans-serif !important; }

/* ═══ ANIMATED BACKGROUND ════════════════════════════════════════════════════ */
.stApp {
    background: linear-gradient(-45deg, #050c1a, #0a1228, #051024, #081a30) !important;
    background-size: 400% 400% !important;
    animation: gradientBG 20s ease infinite !important;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Animated gradient orbs (injected as fixed divs) */
.bg-orb {
    position: fixed;
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    mix-blend-mode: screen;
    filter: blur(60px);
}
.bg-orb-1 {
    width: 600px; height: 600px;
    top: -100px; left: -150px;
    background: radial-gradient(circle, rgba(76,139,245,0.25) 0%, transparent 70%);
    animation: orb-drift-1 25s ease-in-out infinite;
}
.bg-orb-2 {
    width: 500px; height: 500px;
    top: 40%; right: -100px;
    background: radial-gradient(circle, rgba(0,212,180,0.2) 0%, transparent 70%);
    animation: orb-drift-2 30s ease-in-out infinite;
}
.bg-orb-3 {
    width: 400px; height: 400px;
    bottom: -50px; left: 30%;
    background: radial-gradient(circle, rgba(139,76,245,0.18) 0%, transparent 70%);
    animation: orb-drift-3 20s ease-in-out infinite;
}
.bg-orb-4 {
    width: 300px; height: 300px;
    top: 60%; left: 20%;
    background: radial-gradient(circle, rgba(245,76,76,0.12) 0%, transparent 70%);
    animation: orb-drift-4 35s ease-in-out infinite;
}

/* Grid overlay */
.bg-grid {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(76,139,245,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(76,139,245,0.06) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(circle at center, rgba(0,0,0,1) 30%, transparent 80%);
    -webkit-mask-image: radial-gradient(circle at center, rgba(0,0,0,1) 30%, transparent 80%);
    opacity: 0.8;
    animation: grid-pulse 8s ease-in-out infinite;
}

@keyframes orb-drift-1 {
    0%,100% { transform: translate(0,0) scale(1); }
    33%      { transform: translate(80px,-60px) scale(1.15); }
    66%      { transform: translate(-40px,80px) scale(0.90); }
}
@keyframes orb-drift-2 {
    0%,100% { transform: translate(0,0) scale(1); }
    40%      { transform: translate(-90px,50px) scale(1.10); }
    70%      { transform: translate(50px,-70px) scale(0.95); }
}
@keyframes orb-drift-3 {
    0%,100% { transform: translate(0,0) scale(1); }
    25%      { transform: translate(60px,40px) scale(1.20); }
    75%      { transform: translate(-60px,-30px) scale(0.85); }
}
@keyframes orb-drift-4 {
    0%,100% { transform: translate(0,0); }
    50%      { transform: translate(100px,-80px); }
}
@keyframes grid-pulse {
    0%,100% { opacity: 0.6; transform: scale(1); }
    50%     { opacity: 1.0; transform: scale(1.02); }
}

/* ═══ STREAMLIT MAIN AREA ════════════════════════════════════════════════════ */
section[data-testid="stMain"] {
    background: transparent !important;
}
section[data-testid="stMain"] > div {
    background: transparent !important;
    padding-top: 1.5rem;
}
/* Block containers */
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"] {
    background: transparent !important;
}

/* ═══ SIDEBAR ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: rgba(5, 12, 26, 0.85) !important;
    border-right: 1px solid rgba(76,139,245,0.15) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
}
section[data-testid="stSidebar"] * {
    color: #c8d6f0 !important;
}

/* ═══ GLASS CARD ═══════════════════════════════════════════════════════════════ */
.glass-card {
    background: rgba(255,255,255,0.035);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 4px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);
    transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.4s ease, border-color 0.4s ease;
    animation: card-appear 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;
}
.glass-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 16px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1), 0 0 20px rgba(76,139,245,0.15);
    border-color: rgba(76,139,245,0.3);
}

@keyframes card-appear {
    0% { opacity: 0; transform: translateY(30px) scale(0.97); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

/* Metric glass card */
.glass-metric {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    text-align: center;
    transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), background 0.4s ease;
    animation: card-appear 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;
}
.glass-metric:hover {
    background: rgba(255,255,255,0.06); transform: translateY(-3px) scale(1.02); border-color: rgba(76,139,245,0.3);
}

/* ═══ METRICS (native st.metric) ════════════════════════════════════════════ */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
    backdrop-filter: blur(12px) !important;
    animation: card-appear 0.4s ease both;
}
div[data-testid="metric-container"] label {
    color: #6b85b8 !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
div[data-testid="stMetricValue"] {
    color: #e8edf5 !important;
    font-size: 1.55rem !important;
    font-weight: 800 !important;
}
div[data-testid="stMetricDelta"] { color: #34d399 !important; }

/* ═══ HEADINGS ════════════════════════════════════════════════════════════════ */
h1 {
    color: #f0f4ff !important;
    font-weight: 900 !important;
    letter-spacing: -0.8px !important;
    background: linear-gradient(135deg, #ffffff, #8ab4f8);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
h2 { color: #dde6f8 !important; font-weight: 800 !important; letter-spacing: -0.4px !important; }
h3 { color: #c8d6f0 !important; font-weight: 700 !important; }
p, li, span, div { color: #a8bcd8; }
caption { color: #6b85b8 !important; font-size: 0.82rem !important; }

/* ═══ BUTTONS ════════════════════════════════════════════════════════════════ */
div.stButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: #c8d6f0 !important;
    border: 1px solid rgba(76,139,245,0.25) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.45rem 1.4rem !important;
    transition: all 0.2s ease !important;
    backdrop-filter: blur(8px) !important;
}
div.stButton > button:hover {
    background: rgba(76,139,245,0.15) !important;
    border-color: rgba(76,139,245,0.5) !important;
    color: #e8f0ff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(76,139,245,0.25) !important;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(76,139,245,0.7), rgba(99,102,241,0.7)) !important;
    color: white !important;
    border: 1px solid rgba(76,139,245,0.4) !important;
    box-shadow: 0 4px 20px rgba(76,139,245,0.3) !important;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(76,139,245,0.9), rgba(99,102,241,0.9)) !important;
    box-shadow: 0 6px 30px rgba(76,139,245,0.5) !important;
}

/* ═══ TABS ════════════════════════════════════════════════════════════════════ */
button[data-baseweb="tab"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #6b85b8 !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1.2rem !important;
    margin-right: 0.5rem !important;
    transition: all 0.2s ease !important;
}
button[data-baseweb="tab"]:hover {
    background: rgba(76,139,245,0.1) !important;
    color: #c8d6f0 !important;
    border-color: rgba(76,139,245,0.3) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: rgba(76,139,245,0.2) !important;
    color: #8ab4f8 !important;
    border-color: #4C8BF5 !important;
    box-shadow: 0 4px 12px rgba(76,139,245,0.15) !important;
}
div[data-baseweb="tab-highlight"] {
    display: none !important; /* Скрываем синюю линию по умолчанию */
}
div[data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: none !important;
    margin-bottom: 1rem !important;
}

/* ═══ INPUTS ═════════════════════════════════════════════════════════════════ */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #c8d6f0 !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stSelectbox"] > div > div:hover,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(76,139,245,0.4) !important;
    box-shadow: 0 0 0 2px rgba(76,139,245,0.1) !important;
}

/* ═══ DATAFRAMES ══════════════════════════════════════════════════════════════ */
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
div[data-testid="stDataFrame"] th {
    background: rgba(76,139,245,0.1) !important;
    color: #8ab4f8 !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}
div[data-testid="stDataFrame"] td { color: #c8d6f0 !important; }
div[data-testid="stDataFrame"] tr:hover td {
    background: rgba(76,139,245,0.07) !important;
}

/* ═══ ALERTS ══════════════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
    backdrop-filter: blur(12px) !important;
}
div[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(76,139,245,0.12) !important;
    border: 1px solid rgba(76,139,245,0.2) !important;
    color: #a8c4f0 !important;
}

/* ═══ EXPANDERS ═══════════════════════════════════════════════════════════════ */
details[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(12px) !important;
}
details[data-testid="stExpander"] summary {
    color: #8ab4f8 !important;
    font-weight: 600 !important;
}

/* ═══ CODE BLOCKS ═════════════════════════════════════════════════════════════ */
div[data-testid="stCode"], pre, code {
    background: rgba(0,0,0,0.4) !important;
    border: 1px solid rgba(76,139,245,0.15) !important;
    border-radius: 10px !important;
    color: #8ab4f8 !important;
}

/* ═══ RADIO (sidebar nav) ═════════════════════════════════════════════════════ */
div[data-testid="stRadio"] label {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    color: #7a95c0 !important;
    padding: 0.3rem 0 !important;
    transition: color 0.2s !important;
}
div[data-testid="stRadio"] label:hover { color: #c8d6f0 !important; }
div[data-testid="stRadio"] div[data-baseweb="radio"] div:first-child {
    border-color: rgba(76,139,245,0.4) !important;
}

/* ═══ FILE UPLOADER ═══════════════════════════════════════════════════════════ */
div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(76,139,245,0.25) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(76,139,245,0.5) !important;
}

/* ═══ SCROLLBAR ═══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: rgba(76,139,245,0.3);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(76,139,245,0.5); }

/* ═══ DIVIDER ═════════════════════════════════════════════════════════════════ */
hr {
    border: 0 !important;
    border-top: 1px solid rgba(76,139,245,0.12) !important;
    margin: 1.2rem 0 !important;
}

/* ═══ SPINNER ═════════════════════════════════════════════════════════════════ */
div[data-testid="stSpinner"] { color: #4C8BF5 !important; }

/* ═══ CAPTION ═════════════════════════════════════════════════════════════════ */
.stCaption p, p.caption {
    color: #4d6690 !important;
    font-size: 0.82rem !important;
}

/* ═══ PROGRESS ════════════════════════════════════════════════════════════════ */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #4C8BF5, #00D4B4) !important;
    border-radius: 4px !important;
    animation: progress-glow 2s ease-in-out infinite !important;
}
@keyframes progress-glow {
    0%,100% { box-shadow: 0 0 6px rgba(76,139,245,0.4); }
    50%      { box-shadow: 0 0 14px rgba(76,139,245,0.8); }
}

/* ═══ SUCCESS/WARNING/ERROR banners ══════════════════════════════════════════ */
div[data-testid="stSuccess"] {
    background: rgba(0,212,140,0.12) !important;
    border: 1px solid rgba(0,212,140,0.25) !important;
    border-radius: 12px !important;
}
div[data-testid="stWarning"] {
    background: rgba(250,180,50,0.12) !important;
    border: 1px solid rgba(250,180,50,0.25) !important;
    border-radius: 12px !important;
}
div[data-testid="stError"] {
    background: rgba(234,67,53,0.12) !important;
    border: 1px solid rgba(234,67,53,0.25) !important;
    border-radius: 12px !important;
}
div[data-testid="stInfo"] {
    background: rgba(76,139,245,0.10) !important;
    border: 1px solid rgba(76,139,245,0.20) !important;
    border-radius: 12px !important;
    color: #8ab4f8 !important;
}

/* ═══ PULSE animation for status dot ════════════════════════════════════════ */
@keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.6; transform: scale(0.85); }
}
@keyframes glow-text {
    0%,100% { text-shadow: 0 0 8px rgba(76,139,245,0.4); }
    50%      { text-shadow: 0 0 20px rgba(76,139,245,0.8); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
.shimmer {
    background: linear-gradient(90deg,
        rgba(255,255,255,0.05) 0%,
        rgba(255,255,255,0.12) 50%,
        rgba(255,255,255,0.05) 100%);
    background-size: 200% auto;
    animation: shimmer 3s linear infinite;
}

/* ═══ NAV item highlight ══════════════════════════════════════════════════════ */
.nav-item-active {
    background: rgba(76,139,245,0.15);
    border-left: 3px solid #4C8BF5;
    border-radius: 0 8px 8px 0;
    animation: nav-slide 0.3s ease;
}
@keyframes nav-slide {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}
</style>
""", unsafe_allow_html=True)

# ─── Animated background orbs ────────────────────────────────────────────────
st.markdown("""
<div class="bg-grid"></div>
<div class="bg-orb bg-orb-1"></div>
<div class="bg-orb bg-orb-2"></div>
<div class="bg-orb bg-orb-3"></div>
<div class="bg-orb bg-orb-4"></div>
""", unsafe_allow_html=True)

# ─── SVG icon library ─────────────────────────────────────────────────────────
SVG = {
    "shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "chart":  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
    "cpu":    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "compare":'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>',
    "search": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "bank":   '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>',
    "globe":  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
}

# ─── Import pages ─────────────────────────────────────────────────────────────
from modules import pg_overview, pg_training, pg_models, pg_predict, pg_external
from modules.i18n import t, lang_switch

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style="text-align:center; padding:1.5rem 0 1rem; animation:card-appear 0.5s ease;">
        <div style="
            width:52px; height:52px; margin:0 auto 10px;
            background:linear-gradient(135deg,rgba(76,139,245,0.3),rgba(99,102,241,0.3));
            border:1px solid rgba(76,139,245,0.4); border-radius:14px;
            display:flex; align-items:center; justify-content:center;
            box-shadow:0 4px 20px rgba(76,139,245,0.25);
        ">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
                 stroke="#4C8BF5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <polyline points="9 12 11 14 15 10"/>
            </svg>
        </div>
        <div style="font-size:1.2rem;font-weight:900;letter-spacing:-0.3px;
                    background:linear-gradient(135deg,#ffffff,#8ab4f8);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">
            Defender
        </div>
        <div style="font-size:0.68rem;color:#4d6690;font-weight:500;
                    letter-spacing:0.8px;text-transform:uppercase;margin-top:3px;">
            {t('nav.subtitle')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="margin:0.5rem 0 1rem;"/>', unsafe_allow_html=True)

    PAGES = {
        "nav.overview":   (pg_overview,  SVG["chart"]),
        "nav.training":   (pg_training,  SVG["cpu"]),
        "nav.comparison": (pg_models,    SVG["compare"]),
        "nav.predict":    (pg_predict,   SVG["search"]),
        "nav.external":   (pg_external,  SVG["bank"]),
    }

    if "current_page_key" not in st.session_state:
        st.session_state.current_page_key = "nav.overview"

    for p_key in PAGES.keys():
        btn_type = "primary" if st.session_state.current_page_key == p_key else "secondary"
        if st.sidebar.button(t(p_key), type=btn_type, use_container_width=True):
            st.session_state.current_page_key = p_key
            st.rerun()

    st.markdown('<hr style="margin:1rem 0 0.5rem;"/>', unsafe_allow_html=True)

    lang = st.session_state.get("lang", "ru")
    col_ru, col_kz = st.sidebar.columns(2)
    with col_ru:
        if st.button("RU", use_container_width=True,
                     type="primary" if lang == "ru" else "secondary",
                     key="btn_ru"):
            st.session_state.lang = "ru"
            st.rerun()
    with col_kz:
        if st.button("KZ", use_container_width=True,
                     type="primary" if lang == "kz" else "secondary",
                     key="btn_kz"):
            st.session_state.lang = "kz"
            st.rerun()

    st.sidebar.markdown(f"""
    <div style="font-size:0.65rem;color:#2d3d58;text-align:center;padding:1rem 0 0.5rem;">
        v1.0 &nbsp;•&nbsp; Defender &nbsp;•&nbsp; 2026
    </div>
    """, unsafe_allow_html=True)

# ── Render page ───────────────────────────────────────────────────────────────
page_module, _ = PAGES.get(st.session_state.current_page_key, PAGES["nav.overview"])
page_module.render()
