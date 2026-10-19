import pytest
import db


@pytest.fixture
def path(tmp_path):
    p = str(tmp_path / "test.db")
    db.init_db(p)
    return p


def test_package_status_counts_sessions(path):
    pid = db.add_patient("Test Patient", age=40, package_total=10, path=path)
    db.add_session(pid, pain_score=7, path=path)
    db.add_session(pid, pain_score=5, path=path)
    status = db.package_status(pid, path=path)
    assert status == {"total": 10, "used": 2, "remaining": 8}


def test_pain_score_must_be_0_to_10(path):
    pid = db.add_patient("Test Patient", path=path)
    with pytest.raises(ValueError):
        db.add_session(pid, pain_score=11, path=path)
    with pytest.raises(ValueError):
        db.add_session(pid, pain_score=-1, path=path)


def test_session_needs_real_patient(path):
    with pytest.raises(ValueError):
        db.add_session(999, pain_score=3, path=path)


def test_duplicate_exercise_name_rejected(path):
    db.add_exercise("Bridging", "Lift your hips slowly.", path=path)
    with pytest.raises(ValueError):
        db.add_exercise("Bridging", "Another version.", path=path)


def test_empty_name_rejected(path):
    with pytest.raises(ValueError):
        db.add_patient("   ", path=path)


def test_bad_date_rejected(path):
    pid = db.add_patient("Test Patient", path=path)
    with pytest.raises(ValueError):
        db.add_session(pid, session_date="14-10-2026", path=path)
        
def test_update_exercise(path):
    eid = db.add_exercise("Bridging", "Lift your hips slowly.", path=path)
    db.update_exercise(eid, "Bridging", "Lift slowly and hold.", default_sets=2, path=path)
    row = db.list_exercises(path=path)[0]
    assert row["default_sets"] == 2
    assert row["instructions"] == "Lift slowly and hold."


def test_update_missing_exercise_rejected(path):
    with pytest.raises(ValueError):
        db.update_exercise(999, "Nothing", "Nothing here.", path=path)


def test_delete_exercise(path):
    eid = db.add_exercise("Bridging", "Lift your hips slowly.", path=path)
    db.delete_exercise(eid, path=path)
    assert db.list_exercises(path=path) == []

def test_update_patient(path):
    pid = db.add_patient("Demo Patient", age=40, package_total=5, path=path)
    db.update_patient(pid, "Demo Patient", age=41, package_total=8, path=path)
    row = db.get_patient(pid, path=path)
    assert row["age"] == 41
    assert row["package_total"] == 8


def test_update_missing_patient_rejected(path):
    with pytest.raises(ValueError):
        db.update_patient(999, "Nobody", path=path)

def test_delete_patient_removes_sessions(path):
    pid = db.add_patient("Demo Patient", package_total=5, path=path)
    db.add_session(pid, pain_score=4, path=path)
    db.delete_patient(pid, path=path)
    assert db.list_patients(path=path) == []
    assert db.list_sessions(pid, path=path) == []

def test_settings_roundtrip(path):
    assert db.get_setting("clinic_name", path=path) == ""
    db.set_setting("clinic_name", "Demo Clinic", path=path)
    db.set_setting("clinic_name", "Demo Clinic 2", path=path)
    assert db.get_setting("clinic_name", path=path) == "Demo Clinic 2"


def test_unknown_setting_rejected(path):
    with pytest.raises(ValueError):
        db.set_setting("something_else", "x", path=path)
        
def test_patients_summary_counts_and_last_date(path):
    pid = db.add_patient("Demo Patient", package_total=5, path=path)
    db.add_session(pid, pain_score=6, session_date="2026-10-01", path=path)
    db.add_session(pid, pain_score=4, session_date="2026-10-08", path=path)
    db.add_patient("Demo New", package_total=3, path=path)
    rows = {r["name"]: r for r in db.patients_summary(path=path)}
    assert rows["Demo Patient"]["used"] == 2
    assert rows["Demo Patient"]["last_session"] == "2026-10-08"
    assert rows["Demo New"]["used"] == 0
    assert rows["Demo New"]["last_session"] is None


def test_count_sessions_since(path):
    pid = db.add_patient("Demo Patient", package_total=5, path=path)
    db.add_session(pid, session_date="2026-10-01", path=path)
    db.add_session(pid, session_date="2026-10-10", path=path)
    assert db.count_sessions_since("2026-10-05", path=path) == 1
    with pytest.raises(ValueError):
        db.count_sessions_since("not a date", path=path)
        
   