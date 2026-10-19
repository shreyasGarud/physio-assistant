from datetime import date
import insights

TODAY = date(2026, 10, 20)


def row(**changes):
    base = {"id": 1, "name": "Demo", "condition": None, "package_total": 10,
            "used": 5, "last_session": "2026-10-10"}
    base.update(changes)
    return insights.enrich([base], today=TODAY)[0]


def test_enrich_adds_remaining_and_days():
    r = row()
    assert r["remaining"] == 5
    assert r["days_since"] == 10


def test_status_labels():
    assert insights.status_label(row()) == "Follow up"
    assert insights.status_label(row(last_session="2026-10-18")) == "On track"
    assert insights.status_label(row(used=0, last_session=None)) == "Not started"
    assert insights.status_label(row(used=10)) == "Completed"
    assert insights.status_label(row(package_total=0, used=0, last_session=None)) == "No package"


def test_needs_followup_sorted_longest_gap_first():
    rows = insights.enrich([
        {"id": 1, "name": "A", "condition": None, "package_total": 10, "used": 4,
         "last_session": "2026-10-12"},
        {"id": 2, "name": "B", "condition": None, "package_total": 10, "used": 4,
         "last_session": "2026-10-05"},
        {"id": 3, "name": "C", "condition": None, "package_total": 10, "used": 4,
         "last_session": "2026-10-19"},
    ], today=TODAY)
    late = insights.needs_followup(rows)
    assert [r["name"] for r in late] == ["B", "A"]
    