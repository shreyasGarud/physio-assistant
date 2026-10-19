from datetime import date, timedelta, datetime
import streamlit as st
import db
import insights
import theme


def _greeting():
    hour = datetime.now().hour
    return "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"


def show():
    clinic = db.get_setting("clinic_name")
    theme.hero(_greeting() + (", " + clinic if clinic else ""),
               "Here is your clinic at a glance.")

    rows = insights.enrich(db.patients_summary())
    followups = insights.needs_followup(rows)
    week_start = (date.today() - timedelta(days=6)).isoformat()

    cols = st.columns(4)
    with cols[0]:
        theme.stat_card("👥", len(rows), "Patients", "in your records")
    with cols[1]:
        theme.stat_card("🏋️", db.count_exercises(), "Exercises", "in your library")
    with cols[2]:
        theme.stat_card("📅", db.count_sessions_since(week_start), "Sessions", "in the last 7 days")
    with cols[3]:
        theme.stat_card("🔔", len(followups), "Need follow-up", "7+ days since last visit")

    st.write("")
    if not rows:
        st.info("No patients yet. Open **Patients** in the sidebar to add your first one "
                "(use fictional data while testing).")
        return

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.subheader("🔔 Needs follow-up")
            if not followups:
                st.success("Everyone with sessions left has visited recently.")
            for r in followups:
                st.markdown("**{}**".format(r["name"]))
                st.caption("Last visit {} days ago · {} sessions left".format(
                    r["days_since"], r["remaining"]))
            fresh = [r for r in rows if insights.status_label(r) == "Not started"]
            if fresh:
                st.markdown("---")
                st.caption("Not started yet: " + ", ".join(r["name"] for r in fresh))

    with right:
        with st.container(border=True):
            st.subheader("📈 Package progress")
            shown = 0
            for r in rows:
                if r["package_total"] <= 0:
                    continue
                st.caption("{} · {} of {} sessions".format(r["name"], r["used"], r["package_total"]))
                st.progress(min(r["used"] / float(r["package_total"]), 1.0))
                shown += 1
                if shown == 6:
                    break
            if shown == 0:
                st.caption("No patients have a package set yet.")
                