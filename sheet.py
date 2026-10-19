import base64
import os
from datetime import date
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
FONT_DIR = os.path.join(BASE_DIR, "fonts")
FONT_FILES = {"NotoSansDevanagari-Regular.ttf": 400, "NotoSansDevanagari-Bold.ttf": 700}

_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)


def _font_css():
    """Embed the Devanagari font in the sheet so it prints correctly everywhere."""
    rules = []
    for filename, weight in FONT_FILES.items():
        path = os.path.join(FONT_DIR, filename)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        rules.append(
            "@font-face {{ font-family: 'SheetDevanagari'; font-weight: {}; "
            "src: url(data:font/ttf;base64,{}) format('truetype'); }}".format(weight, data))
    return Markup("\n".join(rules))


def _whole(value, label, low, high):
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise ValueError("{} must be a whole number from {} to {}".format(label, low, high))
    return value


def render_sheet(items, clinic_name="", clinic_contact="", patient_label="",
                 general_note="", sheet_date=None):
    """Build the home exercise sheet as an HTML string.

    items: list of dicts with name, sets, reps, instructions, precautions.
    The text is used exactly as given. Nothing is generated or changed here.
    """
    if not items:
        raise ValueError("Choose at least one exercise")
    clean = []
    for it in items:
        name = (it.get("name") or "").strip()
        instructions = (it.get("instructions") or "").strip()
        if not name or not instructions:
            raise ValueError("Every exercise needs a name and instructions")
        clean.append({
            "name": name,
            "sets": _whole(it.get("sets"), "Sets", 1, 20),
            "reps": _whole(it.get("reps"), "Reps", 1, 200),
            "instructions": instructions,
            "precautions": (it.get("precautions") or "").strip(),
        })
    sheet_date = sheet_date or date.today()
    return _env.get_template("sheet.html").render(
        items=clean,
        clinic_name=(clinic_name or "").strip(),
        clinic_contact=(clinic_contact or "").strip(),
        patient_label=(patient_label or "").strip(),
        general_note=(general_note or "").strip(),
        sheet_date=sheet_date.strftime("%d %B %Y"),
        font_css=_font_css(),
    )
