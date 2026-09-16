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
