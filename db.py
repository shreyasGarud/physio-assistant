import os
import sqlite3
from datetime import date

DB_PATH = os.path.join("data", "physio.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER CHECK (age IS NULL OR age BETWEEN 0 AND 120),
    condition TEXT,
    contact TEXT,
    package_total INTEGER NOT NULL DEFAULT 0 CHECK (package_total >= 0),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    body_area TEXT,
    default_sets INTEGER NOT NULL DEFAULT 3 CHECK (default_sets >= 1),
    default_reps INTEGER NOT NULL DEFAULT 10 CHECK (default_reps >= 1),
    instructions TEXT NOT NULL,
    precautions TEXT,
    media_path TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    session_date TEXT NOT NULL,
    shorthand TEXT,
    note TEXT,
    pain_score INTEGER CHECK (pain_score IS NULL OR pain_score BETWEEN 0 AND 10),
    rom_joint TEXT,
    rom_degrees INTEGER CHECK (rom_degrees IS NULL OR rom_degrees BETWEEN 0 AND 360),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def connect(path=DB_PATH):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path=DB_PATH):
    with connect(path) as conn:
        conn.executescript(SCHEMA)


def _text(value, label, required=True):
    value = (value or "").strip()
    if required and not value:
        raise ValueError(label + " is required")
    return value or None


def _int_in_range(value, label, low, high):
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise ValueError("{} must be a whole number from {} to {}".format(label, low, high))
    return value


# ---------------------------------------------------------------- patients
def add_patient(name, age=None, condition=None, contact=None, package_total=0, path=DB_PATH):
    name = _text(name, "Name")
    age = _int_in_range(age, "Age", 0, 120)
    package_total = _int_in_range(package_total, "Package size", 0, 200)
    with connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO patients (name, age, condition, contact, package_total, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, age, _text(condition, "Condition", False), _text(contact, "Contact", False),
             package_total, date.today().isoformat()))
        return cur.lastrowid


def list_patients(path=DB_PATH):
    with connect(path) as conn:
        return conn.execute("SELECT * FROM patients ORDER BY name").fetchall()


def package_status(patient_id, path=DB_PATH):
    """Sessions used and remaining, worked out from the session records."""
    with connect(path) as conn:
        patient = conn.execute(
            "SELECT package_total FROM patients WHERE id = ?", (patient_id,)).fetchone()
        if patient is None:
            raise ValueError("Patient not found")
        used = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE patient_id = ?", (patient_id,)).fetchone()[0]
    total = patient["package_total"]
    return {"total": total, "used": used, "remaining": max(total - used, 0)}


# --------------------------------------------------------------- exercises
def add_exercise(name, instructions, body_area=None, default_sets=3, default_reps=10,
                 precautions=None, media_path=None, path=DB_PATH):
    name = _text(name, "Exercise name")
    instructions = _text(instructions, "Instructions")
    default_sets = _int_in_range(default_sets, "Sets", 1, 20)
    default_reps = _int_in_range(default_reps, "Reps", 1, 200)
    with connect(path) as conn:
        try:
            cur = conn.execute(
                "INSERT INTO exercises (name, body_area, default_sets, default_reps, "
                "instructions, precautions, media_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, _text(body_area, "Body area", False), default_sets, default_reps,
                 instructions, _text(precautions, "Precautions", False),
                 _text(media_path, "Media path", False)))
        except sqlite3.IntegrityError:
            raise ValueError("An exercise named '{}' already exists".format(name))
        return cur.lastrowid


def list_exercises(path=DB_PATH):
    with connect(path) as conn:
        return conn.execute("SELECT * FROM exercises ORDER BY name").fetchall()


# ---------------------------------------------------------------- sessions
def add_session(patient_id, shorthand=None, note=None, pain_score=None,
                rom_joint=None, rom_degrees=None, session_date=None, path=DB_PATH):
    pain_score = _int_in_range(pain_score, "Pain score", 0, 10)
    rom_degrees = _int_in_range(rom_degrees, "Range of motion", 0, 360)
    session_date = session_date or date.today().isoformat()
    try:
        date.fromisoformat(session_date)
    except ValueError:
        raise ValueError("Date must look like 2026-10-14")
    with connect(path) as conn:
        if conn.execute("SELECT 1 FROM patients WHERE id = ?", (patient_id,)).fetchone() is None:
            raise ValueError("Patient not found")
        cur = conn.execute(
            "INSERT INTO sessions (patient_id, session_date, shorthand, note, pain_score, "
            "rom_joint, rom_degrees, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (patient_id, session_date, _text(shorthand, "Shorthand", False),
             _text(note, "Note", False), pain_score, _text(rom_joint, "Joint", False),
             rom_degrees, date.today().isoformat()))
        return cur.lastrowid


def list_sessions(patient_id, path=DB_PATH):
    with connect(path) as conn:
        return conn.execute(
            "SELECT * FROM sessions WHERE patient_id = ? ORDER BY session_date, id",
            (patient_id,)).fetchall()
    
def update_exercise(exercise_id, name, instructions, body_area=None, default_sets=3,
                    default_reps=10, precautions=None, media_path=None, path=DB_PATH):
    name = _text(name, "Exercise name")
    instructions = _text(instructions, "Instructions")
    default_sets = _int_in_range(default_sets, "Sets", 1, 20)
    default_reps = _int_in_range(default_reps, "Reps", 1, 200)
    with connect(path) as conn:
        try:
            cur = conn.execute(
                "UPDATE exercises SET name = ?, body_area = ?, default_sets = ?, "
                "default_reps = ?, instructions = ?, precautions = ?, media_path = ? "
                "WHERE id = ?",
                (name, _text(body_area, "Body area", False), default_sets, default_reps,
                 instructions, _text(precautions, "Precautions", False),
                 _text(media_path, "Media path", False), exercise_id))
        except sqlite3.IntegrityError:
            raise ValueError("An exercise named '{}' already exists".format(name))
        if cur.rowcount == 0:
            raise ValueError("Exercise not found")


def delete_exercise(exercise_id, path=DB_PATH):
    with connect(path) as conn:
        cur = conn.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))
        if cur.rowcount == 0:
            raise ValueError("Exercise not found")

def get_patient(patient_id, path=DB_PATH):
    with connect(path) as conn:
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if row is None:
        raise ValueError("Patient not found")
    return row


def update_patient(patient_id, name, age=None, condition=None, contact=None,
                   package_total=0, path=DB_PATH):
    name = _text(name, "Name")
    age = _int_in_range(age, "Age", 0, 120)
    package_total = _int_in_range(package_total, "Package size", 0, 200)
    with connect(path) as conn:
        cur = conn.execute(
            "UPDATE patients SET name = ?, age = ?, condition = ?, contact = ?, "
            "package_total = ? WHERE id = ?",
            (name, age, _text(condition, "Condition", False), _text(contact, "Contact", False),
             package_total, patient_id))
        if cur.rowcount == 0:
            raise ValueError("Patient not found")


def delete_patient(patient_id, path=DB_PATH):
    """Removes the patient and all of their session records."""
    with connect(path) as conn:
        if conn.execute("SELECT 1 FROM patients WHERE id = ?", (patient_id,)).fetchone() is None:
            raise ValueError("Patient not found")
        conn.execute("DELETE FROM sessions WHERE patient_id = ?", (patient_id,))
        conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))

ALLOWED_SETTINGS = ("clinic_name", "clinic_contact", "general_note")


def get_setting(key, default="", path=DB_PATH):
    if key not in ALLOWED_SETTINGS:
        raise ValueError("Unknown setting")
    with connect(path) as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key, value, path=DB_PATH):
    if key not in ALLOWED_SETTINGS:
        raise ValueError("Unknown setting")
    value = (value or "").strip()
    if len(value) > 500:
        raise ValueError("Text is too long (500 characters at most)")
    with connect(path) as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            