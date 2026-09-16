"""
python-docx yordamida Word hujjat yaratish: titul varag'i + reja + matn.
"""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION

from config import OUTPUT_DIR


def _set_normal_font(doc: Document, font_name="Times New Roman", size=14):
    style = doc.styles["Normal"]
    style.font.name = font_name
    style.font.size = Pt(size)


def build_document(
    turi: str,          # "Mustaqil ish" yoki "Referat"
    mavzu: str,
    ism_familiya: str,
    universitet: str,
    guruh: str,
    oqituvchi: str,
    content: dict,       # ai_service.generate_full_document natijasi
    file_id: str,
) -> str:
    doc = Document()
    _set_normal_font(doc)

    # ---- Titul varag'i ----
    def add_centered(text, bold=False, size=14, space_after=6):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)
        p.paragraph_format.space_after = Pt(space_after)
        return p

    add_centered("O'ZBEKISTON RESPUBLIKASI OLIY TA'LIM, FAN VA INNOVATSIYALAR VAZIRLIGI", bold=True)
    add_centered(universitet.upper(), bold=True, size=15)
    for _ in range(4):
        doc.add_paragraph()
    add_centered(turi.upper(), bold=True, size=18)
    add_centered(f'Mavzu: "{mavzu}"', bold=True, size=16)
    for _ in range(4):
        doc.add_paragraph()

    info_p = doc.add_paragraph()
    info_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    info_p.add_run(f"Bajardi: {ism_familiya}\n")
    if guruh:
        info_p.add_run(f"Guruh: {guruh}\n")
    if oqituvchi:
        info_p.add_run(f"Tekshirdi: {oqituvchi}\n")

    for _ in range(6):
        doc.add_paragraph()
    add_centered("Toshkent " + "2025")

    doc.add_page_break()
