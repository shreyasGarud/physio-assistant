import streamlit as st
import db
import theme

st.set_page_config(page_title="Physio Assistant", page_icon="🩺", layout="wide")
db.init_db()
theme.apply()

theme.hero("🩺 Physio Assistant", "Notes, exercise sheets and progress tracking, kept on your own computer.")
st.warning(
    "This tool does not diagnose or suggest treatment. The clinician chooses the exercises "
    "and reviews everything. Demo data is fictional."
)

page = st.sidebar.radio("Go to", ["Exercise library"])


def show_exercise_library():
    st.header("Exercise library")
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
                st.success("Saved.")
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
                    st.success("Updated.")
                except ValueError as err:
                    st.error(str(err))

            confirm = st.checkbox("I want to delete this exercise",
                                  key="confirm_{}".format(ex["id"]))
            if st.button("Delete", key="del_{}".format(ex["id"]), disabled=not confirm):
                db.delete_exercise(ex["id"])
                st.rerun()


if page == "Exercise library":
    show_exercise_library()
    