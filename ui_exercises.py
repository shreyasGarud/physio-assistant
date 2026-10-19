import streamlit as st
import db
from ui_common import show_flash, done


def show():
    st.header("Exercise library")
    show_flash()
    st.caption("Add your own exercises once. Every home sheet will use your wording.")

    with st.expander("➕ Add an exercise", expanded=not db.list_exercises()):
        with st.form("add_exercise", clear_on_submit=True):
            name = st.text_input("Exercise name")
            body_area = st.text_input("Body area (optional)", placeholder="e.g. lower back")
            col1, col2 = st.columns(2)
            sets = col1.number_input("Default sets", min_value=1, max_value=20, value=3, step=1)
            reps = col2.number_input("Default reps", min_value=1, max_value=200, value=10, step=1)
            instructions = st.text_area("Instructions (in your own words)")
            precautions = st.text_area("Precautions (optional)")
            media = st.text_input("Photo or video file name or link (optional)")
            saved = st.form_submit_button("Save exercise")
        if saved:
            try:
                db.add_exercise(name, instructions, body_area, int(sets), int(reps),
                                precautions, media)
                done("Exercise saved.")
            except ValueError as err:
                st.error(str(err))

    exercises = db.list_exercises()
    st.subheader("Your exercises ({})".format(len(exercises)))
    query = st.text_input("Search", placeholder="name or body area").strip().lower()

    for row in exercises:
        ex = dict(row)
        if query and query not in "{} {}".format(ex["name"], ex["body_area"] or "").lower():
            continue
        label = ex["name"] + (" · " + ex["body_area"] if ex["body_area"] else "")
        with st.expander(label):
            with st.form("edit_{}".format(ex["id"])):
                name = st.text_input("Exercise name", value=ex["name"])
                body_area = st.text_input("Body area", value=ex["body_area"] or "")
                col1, col2 = st.columns(2)
                sets = col1.number_input("Default sets", min_value=1, max_value=20,
                                         value=ex["default_sets"], step=1)
                reps = col2.number_input("Default reps", min_value=1, max_value=200,
                                         value=ex["default_reps"], step=1)
                instructions = st.text_area("Instructions", value=ex["instructions"])
                precautions = st.text_area("Precautions", value=ex["precautions"] or "")
                media = st.text_input("Photo or video", value=ex["media_path"] or "")
                update = st.form_submit_button("Save changes")
            if update:
                try:
                    db.update_exercise(ex["id"], name, instructions, body_area, int(sets),
                                       int(reps), precautions, media)
                    done("Exercise updated.")
                except ValueError as err:
                    st.error(str(err))

            confirm = st.checkbox("I want to delete this exercise",
                                  key="confirm_{}".format(ex["id"]))
            if st.button("Delete", key="del_{}".format(ex["id"]), disabled=not confirm):
                try:
                    db.delete_exercise(ex["id"])
                    done("Exercise deleted.")
                except ValueError as err:
                    st.error(str(err))
                    