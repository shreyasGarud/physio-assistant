import base64
import streamlit as st

_PATTERN = """<svg xmlns='http://www.w3.org/2000/svg' width='520' height='520' viewBox='0 0 520 520'>
<g fill='none' stroke='#0F766E' stroke-opacity='0.08' stroke-width='2'>
<circle cx='90' cy='90' r='60'/><circle cx='90' cy='90' r='36'/>
<circle cx='400' cy='170' r='80'/><circle cx='400' cy='170' r='50'/>
<circle cx='210' cy='400' r='70'/><circle cx='210' cy='400' r='42'/>
<path d='M0 300 Q130 240 260 300 T520 300'/>
<path d='M0 340 Q130 280 260 340 T520 340'/>
</g></svg>"""

_CSS = """
<style>
.stApp {
    background-color: #F4FAF9;
    background-image: url("data:image/svg+xml;base64,__PATTERN__");
    background-attachment: fixed;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F766E 0%, #115E59 100%);
}
[data-testid="stSidebar"] * { color: #F0FDFA !important; }
.hero {
    background: linear-gradient(120deg, #0F766E 0%, #14B8A6 100%);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 16px;
    color: #FFFFFF;
    box-shadow: 0 4px 14px rgba(15, 118, 110, 0.25);
}
.hero h1 { color: #FFFFFF; margin: 0; padding: 0; font-size: 2rem; }
.hero p { color: #E6FFFA; margin: 6px 0 0 0; font-size: 1.05rem; }
div[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid #CFE5E2;
    border-radius: 12px;
}
.stButton > button, .stFormSubmitButton > button { border-radius: 10px; }
</style>
"""


def apply():
    encoded = base64.b64encode(_PATTERN.encode("utf-8")).decode("ascii")
    st.markdown(_CSS.replace("__PATTERN__", encoded), unsafe_allow_html=True)


def hero(title, subtitle):
    # Only call this with fixed text written in code, never with user input.
    st.markdown(
        '<div class="hero"><h1>{}</h1><p>{}</p></div>'.format(title, subtitle),
        unsafe_allow_html=True,
    )
