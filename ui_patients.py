import streamlit as st
import db
import insights
import theme
from ui_common import show_flash, done


def _age_or_none(value):
    return int(value) if value else None


def show():
    theme.page_header("👥", "Patients", "Records, packages and progress in one place")
    show_flash()
    st.info("Use fictional patients only while testing. Never type real names, phone "
            "numbers or medical details into a demo.")

    tab_all, tab_add = st.tabs(["All patients", "➕ Add patient"])

    with tab_add:
        with st.form("add_patient", clear_on_submit=True):
            name = st.text_input("Name")
            col1, col2 = st.columns(2)
            age = col1.number_input("Age (0 = not given)", min_value=0, max_value=120,
                                    value=0, step=1)
            package = col2.number_input("Package size (number of sessions)", min_value=0,
                                        max_value=200, value=10, step=1)
            condition = st.text_input("Condition (optional)")
            contact = st.text_input("Contact (optional)")
            saved = st.form_submit_button("Save patient", type="primary")
        if saved:
            try:
                db.add_patient(name, _age_or_none(age), condition, contact, int(package))
                done("Patient saved.")
            except ValueError as err:
                st.error(str(err))

    with tab_all:
        rows = insights.enrich(db.patients_summary())
        if not rows:
            st.caption("No patients yet. Use the **Add patient** tab.")
            return

        table = [{
            "Name": r["name"],
            "Condition": r["condition"] or "",
            "Sessions": "{} of {}".format(r["used"], r["package_total"]),
            "Last visit": r["last_session"] or "-",
            "Status": insights.status_label(r),
        } for r in rows]
        st.dataframe(table, hide_index=True)

        st.subheader("Edit or remove")
        query = st.text_input("Search patients", placeholder="name or condition").strip().lower()
        by_id = {r["id"]: r for r in rows}
        for r in rows:
            if query and query not in "{} {}".format(r["name"], r["condition"] or "").lower():
                continue
            label = "{} · {}".format(r["name"], insights.status_label(r))
            with st.expander(label):
                if r["package_total"] > 0:
                    st.progress(min(r["used"] / float(r["package_total"]), 1.0))
                    st.caption("{} sessions remaining".format(r["remaining"]))
                else:
                    st.caption("No package set.")

                full = dict(db.get_patient(r["id"]))
                with st.form("edit_patient_{}".format(r["id"])):
                    name = st.text_input("Name", value=full["name"])
                    col1, col2 = st.columns(2)
                    age = col1.number_input("Age (0 = not given)", min_value=0, max_value=120,
                                            value=full["age"] or 0, step=1)
                    package = col2.number_input("Package size", min_value=0, max_value=200,
                                                value=full["package_total"], step=1)
                    condition = st.text_input("Condition", value=full["condition"] or "")
                    contact = st.text_input("Contact", value=full["contact"] or "")
                    update = st.form_submit_button("Save changes")
                if update:
                    try:
                        db.update_patient(r["id"], name, _age_or_none(age), condition,
                                          contact, int(package))
                        done("Patient updated.")
                    except ValueError as err:
                        st.error(str(err))

                confirm = st.checkbox("Delete this patient and all their sessions",
                                      key="confirm_patient_{}".format(r["id"]))
                if st.button("Delete patient", key="del_patient_{}".format(r["id"]),
                             disabled=not confirm):
                    try:
                        db.delete_patient(r["id"])
                        done("Patient deleted.")
                    except ValueError as err:
                        st.error(str(err))
                        