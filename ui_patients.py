import streamlit as st
import db
from ui_common import show_flash, done


def _age_or_none(value):
    return int(value) if value else None


def _overview_rows(patients):
    rows = []
    for p in patients:
        status = db.package_status(p["id"])
        rows.append({
            "Name": p["name"],
            "Age": str(p["age"]) if p["age"] is not None else "",
            "Condition": p["condition"] or "",
            "Sessions used": "{} of {}".format(status["used"], status["total"]),
        })
    return rows


def show():
    st.header("Patients")
    show_flash()
    st.info("Use fictional patients only while testing. Never type real names, phone "
            "numbers or medical details into a demo.")

    with st.expander("➕ Add a patient", expanded=not db.list_patients()):
        with st.form("add_patient", clear_on_submit=True):
            name = st.text_input("Name")
            col1, col2 = st.columns(2)
            age = col1.number_input("Age (0 = not given)", min_value=0, max_value=120,
                                    value=0, step=1)
            package = col2.number_input("Package size (number of sessions)", min_value=0,
                                        max_value=200, value=10, step=1)
            condition = st.text_input("Condition (optional)")
            contact = st.text_input("Contact (optional)")
            saved = st.form_submit_button("Save patient")
        if saved:
            try:
                db.add_patient(name, _age_or_none(age), condition, contact, int(package))
                done("Patient saved.")
            except ValueError as err:
                st.error(str(err))

    patients = db.list_patients()
    st.subheader("Your patients ({})".format(len(patients)))
    if not patients:
        st.caption("No patients yet. Add one above.")
        return

    st.dataframe(_overview_rows(patients))

    st.subheader("Edit or remove")
    query = st.text_input("Search patients", placeholder="name or condition").strip().lower()
    for row in patients:
        p = dict(row)
        if query and query not in "{} {}".format(p["name"], p["condition"] or "").lower():
            continue
        status = db.package_status(p["id"])
        label = "{} · {} of {} sessions used".format(p["name"], status["used"], status["total"])
        with st.expander(label):
            if status["total"] > 0:
                st.progress(min(status["used"] / float(status["total"]), 1.0))
                st.caption("{} sessions remaining".format(status["remaining"]))
            else:
                st.caption("No package set.")

            with st.form("edit_patient_{}".format(p["id"])):
                name = st.text_input("Name", value=p["name"])
                col1, col2 = st.columns(2)
                age = col1.number_input("Age (0 = not given)", min_value=0, max_value=120,
                                        value=p["age"] or 0, step=1)
                package = col2.number_input("Package size", min_value=0, max_value=200,
                                            value=p["package_total"], step=1)
                condition = st.text_input("Condition", value=p["condition"] or "")
                contact = st.text_input("Contact", value=p["contact"] or "")
                update = st.form_submit_button("Save changes")
            if update:
                try:
                    db.update_patient(p["id"], name, _age_or_none(age), condition, contact,
                                      int(package))
                    done("Patient updated.")
                except ValueError as err:
                    st.error(str(err))

            confirm = st.checkbox("Delete this patient and all their sessions",
                                  key="confirm_patient_{}".format(p["id"]))
            if st.button("Delete patient", key="del_patient_{}".format(p["id"]),
                         disabled=not confirm):
                try:
                    db.delete_patient(p["id"])
                    done("Patient deleted.")
                except ValueError as err:
                    st.error(str(err))
                    