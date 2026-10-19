from datetime import date


def enrich(summary, today=None):
    """Add 'remaining' and 'days_since' (days since the last session) to each row."""
    today = today or date.today()
    rows = []
    for r in summary:
        last = date.fromisoformat(r["last_session"]) if r["last_session"] else None
        row = dict(r)
        row["remaining"] = max(r["package_total"] - r["used"], 0)
        row["days_since"] = (today - last).days if last else None
        rows.append(row)
    return rows


def status_label(row, follow_up_days=7):
    if row["package_total"] == 0:
        return "No package"
    if row["used"] == 0:
        return "Not started"
    if row["remaining"] == 0:
        return "Completed"
    if row["days_since"] is not None and row["days_since"] >= follow_up_days:
        return "Follow up"
    return "On track"


def needs_followup(rows, follow_up_days=7):
    """Patients with sessions left whose last visit was long enough ago. Longest gap first."""
    late = [r for r in rows if status_label(r, follow_up_days) == "Follow up"]
    return sorted(late, key=lambda r: -r["days_since"])
