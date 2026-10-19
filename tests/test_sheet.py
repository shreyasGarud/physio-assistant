import pytest
import sheet


def item(**overrides):
    base = {"name": "Demo exercise", "sets": 3, "reps": 10,
            "instructions": "Demo instructions.", "precautions": ""}
    base.update(overrides)
    return base


def test_sheet_contains_exercise_and_dose():
    html = sheet.render_sheet([item()], clinic_name="Demo Clinic")
    assert "Demo exercise" in html
    assert "3 sets" in html
    assert "Demo Clinic" in html


def test_html_in_text_is_escaped():
    html = sheet.render_sheet([item(instructions="<script>alert(1)</script>")])
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_needs_at_least_one_exercise():
    with pytest.raises(ValueError):
        sheet.render_sheet([])


def test_bad_sets_rejected():
    with pytest.raises(ValueError):
        sheet.render_sheet([item(sets=0)])
    with pytest.raises(ValueError):
        sheet.render_sheet([item(reps=500)])


def test_missing_instructions_rejected():
    with pytest.raises(ValueError):
        sheet.render_sheet([item(instructions="  ")])
        