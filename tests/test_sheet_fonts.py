import sheet

ITEM = {"name": "Test", "sets": 3, "reps": 10, "instructions": "Test text.", "precautions": ""}


def test_devanagari_text_is_preserved():
    item = dict(ITEM, name="पाठीचा व्यायाम", instructions="क्ष त्र ज्ञ श्र ळ")
    html = sheet.render_sheet([item])
    assert "पाठीचा व्यायाम" in html
    assert "क्ष त्र ज्ञ श्र ळ" in html


def test_font_embedded_when_file_exists(tmp_path, monkeypatch):
    (tmp_path / "NotoSansDevanagari-Regular.ttf").write_bytes(b"fake font bytes")
    monkeypatch.setattr(sheet, "FONT_DIR", str(tmp_path))
    html = sheet.render_sheet([ITEM])
    assert "@font-face" in html
    assert "base64," in html


def test_no_font_face_when_font_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(sheet, "FONT_DIR", str(tmp_path))
    assert "@font-face" not in sheet.render_sheet([ITEM])
    