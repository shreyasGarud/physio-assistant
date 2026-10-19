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
    