from datetime import date
import streamlit as st
import streamlit.components.v1 as components
import db
import sheet
from ui_common import show_flash, done


def _clinic_details():
    with st.expander("Clinic details (shown on every sheet)"):
        with st.form("clinic_form"):
            name = st.text_input("Clinic name", value=db.get_setting("clinic_name"))
            contact = st.text_input("Clinic contact", value=db.get_setting("clinic_contact"))
            note = st.text_area(
                "Standard advice for patients (write this yourself)",
                value=db.get_setting("general_note"),
                help="Printed at the bottom of every sheet. Leave empty to show nothing.")
            saved = st.form_submit_button("Save clinic details")
        if saved:
            try:
                db.set_setting("clinic_name", name)
                db.set_setting("clinic_contact", contact)
                db.set_setting("general_note", note)
                done("Clinic details saved.")
            except ValueError as err:
                st.error(str(err))


def show():
    st.header("Home exercise sheet")
    show_flash()

    exercises = [dict(r) for r in db.list_exercises()]
    if not exercises:
        st.info("Add exercises to your library first, then come back here.")
        return

    _clinic_details()

    patients = [dict(r) for r in db.list_patients()]
    patient_options = [None] + [p["id"] for p in patients]
    by_id = {p["id"]: p for p in patients}
    patient_id = st.selectbox(
        "Patient", patient_options,
        format_func=lambda pid: "(no patient, generic sheet)" if pid is None else by_id[pid]["name"])

    label_default = by_id[patient_id]["name"] if patient_id else ""
    patient_label = st.text_input(
        "Name shown on the sheet", value=label_default,
        key="label_{}".format(patient_id),
        help="A first name or leave empty. Sheets get shared, so show only what is needed.")

    sheet_date = st.date_input("Date", value=date.today())

    ex_by_id = {e["id"]: e for e in exercises}
    chosen_ids = st.multiselect("Choose exercises", list(ex_by_id),
                                format_func=lambda eid: ex_by_id[eid]["name"])

    items = []
    for eid in chosen_ids:
        ex = ex_by_id[eid]
        st.markdown("**{}**".format(ex["name"]))
        col1, col2 = st.columns(2)
        sets = col1.number_input("Sets", min_value=1, max_value=20,
                                 value=ex["default_sets"], step=1, key="sets_{}".format(eid))
        reps = col2.number_input("Reps", min_value=1, max_value=200,
                                 value=ex["default_reps"], step=1, key="reps_{}".format(eid))
        items.append({"name": ex["name"], "sets": int(sets), "reps": int(reps),
                      "instructions": ex["instructions"], "precautions": ex["precautions"]})

    if not items:
        st.caption("Pick at least one exercise to see the sheet.")
        return

    try:
        html = sheet.render_sheet(
            items,
            clinic_name=db.get_setting("clinic_name"),
            clinic_contact=db.get_setting("clinic_contact"),
            patient_label=patient_label,
            general_note=db.get_setting("general_note"),
            sheet_date=sheet_date,
        )
    except ValueError as err:
        st.error(str(err))
        return

    st.subheader("Preview")
    components.html(html, height=700, scrolling=True)

    reviewed = st.checkbox("I have read this sheet and it is correct to share")
    st.download_button("Download sheet (HTML)", data=html,
                       file_name="exercise_sheet_{}.html".format(sheet_date.isoformat()),
                       mime="text/html", disabled=not reviewed)
    st.caption("To get a PDF: open the downloaded file in your browser, press Ctrl+P, "
               "and choose Save as PDF.")
    