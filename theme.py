import base64
import html
import streamlit as st

_PATTERN = """<svg xmlns='http://www.w3.org/2000/svg' width='520' height='520' viewBox='0 0 520 520'>
<g fill='none' stroke='#0F766E' stroke-opacity='0.07' stroke-width='2'>
<circle cx='90' cy='90' r='60'/><circle cx='90' cy='90' r='36'/>
<circle cx='400' cy='170' r='80'/><circle cx='400' cy='170' r='50'/>
<circle cx='210' cy='400' r='70'/><circle cx='210' cy='400' r='42'/>
<path d='M0 300 Q130 240 260 300 T520 300'/>
<path d='M0 340 Q130 280 260 340 T520 340'/>
</g></svg>"""

_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding-top: 4rem; max-width: 1180px;}
[data-testid="stHeader"] {background: transparent;}

.stApp {
    background-color: #F3F8F7;
    background-image: url("data:image/svg+xml;base64,__PATTERN__");
    background-attachment: fixed;
}

/* Sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0B4F4A 0%, #0F766E 100%); }
[data-testid="stSidebar"] * { color: #ECFDF5 !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 10px 12px; border-radius: 10px; margin-bottom: 4px; transition: background 0.15s;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(255,255,255,0.12); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(255,255,255,0.22); font-weight: 700;
}
.brand { padding: 6px 4px 14px 4px; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 12px; }
.brand .logo { font-size: 2rem; }
.brand .name { font-size: 1.25rem; font-weight: 800; line-height: 1.1; }
.brand .tag { font-size: 0.8rem; opacity: 0.85; }
.side-foot { font-size: 0.78rem; opacity: 0.8; margin-top: 18px; }

/* Header banners */
.hero {
    background: linear-gradient(120deg, #0B4F4A 0%, #0F766E 55%, #14B8A6 100%);
    border-radius: 18px; padding: 26px 30px; margin-bottom: 18px; color: #FFFFFF;
    box-shadow: 0 8px 22px rgba(15, 118, 110, 0.28);
}
.hero h1 { color: #FFFFFF; margin: 0; padding: 0; font-size: 2.1rem; }
.hero p { color: #D9FBF3; margin: 6px 0 0 0; font-size: 1.05rem; }
.page-head { display: flex; align-items: center; gap: 14px; margin: 2px 0 16px 0; }
.page-head .icon {
    font-size: 1.7rem; width: 52px; height: 52px; display: flex; align-items: center;
    justify-content: center; border-radius: 14px; background: #E1F0EE;
}
.page-head h2 { margin: 0; padding: 0; color: #0B4F4A; font-size: 1.6rem; }
.page-head p { margin: 2px 0 0 0; color: #4B6B68; }

/* Notice strip */
.notice {
    background: #FFF8E6; border: 1px solid #F2D58A; border-left: 5px solid #D97706;
    border-radius: 10px; padding: 8px 14px; margin-bottom: 16px; font-size: 0.9rem; color: #5B4300;
}

/* Stat cards */
.stat {
    display: flex; align-items: center; gap: 14px; background: #FFFFFF;
    border: 1px solid #D5E8E5; border-top: 4px solid #14B8A6; border-radius: 14px;
    padding: 16px 18px; box-shadow: 0 3px 10px rgba(15, 118, 110, 0.08);
}
.stat .stat-icon { font-size: 1.8rem; }
.stat .stat-value { font-size: 1.9rem; font-weight: 800; color: #0B4F4A; line-height: 1.05; }
.stat .stat-label { font-weight: 600; color: #2F5551; }
.stat .stat-hint { font-size: 0.8rem; color: #6B8581; }

/* Cards, tabs, buttons */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF; border-radius: 14px; box-shadow: 0 2px 8px rgba(15, 118, 110, 0.07);
}
div[data-testid="stExpander"] { background: #FFFFFF; border-radius: 12px; border: 1px solid #D5E8E5; }
.stTabs [data-baseweb="tab"] { font-weight: 600; padding: 8px 16px; }
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    border-radius: 10px; font-weight: 600; transition: transform 0.1s, box-shadow 0.1s;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px); box-shadow: 0 4px 10px rgba(15, 118, 110, 0.25);
}
</style>
"""


def apply():
    encoded = base64.b64encode(_PATTERN.encode("utf-8")).decode("ascii")
    st.markdown(_CSS.replace("__PATTERN__", encoded), unsafe_allow_html=True)


def _e(text):
    return html.escape(str(text))


def hero(title, subtitle):
    st.markdown('<div class="hero"><h1>{}</h1><p>{}</p></div>'.format(_e(title), _e(subtitle)),
                unsafe_allow_html=True)


def page_header(icon, title, subtitle=""):
    st.markdown(
        '<div class="page-head"><div class="icon">{}</div><div><h2>{}</h2><p>{}</p></div></div>'
        .format(_e(icon), _e(title), _e(subtitle)), unsafe_allow_html=True)


def notice(text):
    st.markdown('<div class="notice">{}</div>'.format(_e(text)), unsafe_allow_html=True)


def stat_card(icon, value, label, hint=""):
    st.markdown(
        '<div class="stat"><div class="stat-icon">{}</div><div>'
        '<div class="stat-value">{}</div><div class="stat-label">{}</div>'
        '<div class="stat-hint">{}</div></div></div>'
        .format(_e(icon), _e(value), _e(label), _e(hint)), unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown(
        '<div class="brand"><div class="logo">🩺</div><div class="name">Physio Assistant</div>'
        '<div class="tag">Local · private · offline-first</div></div>', unsafe_allow_html=True)


def sidebar_footer():
    st.sidebar.markdown('<div class="side-foot">Your data stays on this computer.</div>',
                        unsafe_allow_html=True)
    