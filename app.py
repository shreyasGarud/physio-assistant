import streamlit as st

st.set_page_config(page_title="Physio Assistant", page_icon="🩺", layout="wide")

import db
import theme
import ui_dashboard
import ui_patients
import ui_exercises
import ui_sheets

db.init_db()
theme.apply()
theme.sidebar_brand()

PAGES = {
    "🏠  Dashboard": ui_dashboard.show,
    "👥  Patients": ui_patients.show,
    "🏋️  Exercise library": ui_exercises.show,
    "📄  Home sheets": ui_sheets.show,
}
choice = st.sidebar.radio("Navigate", list(PAGES), label_visibility="collapsed")
theme.sidebar_footer()

theme.notice("This tool does not diagnose or suggest treatment. The clinician chooses the "
             "exercises and reviews everything. Demo data is fictional.")
PAGES[choice]()
