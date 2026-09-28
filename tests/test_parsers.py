"""
Unit Tests for Document Parsers (PDF, DOCX, PPTX, CSV, TXT).
"""

from pathlib import Path
from app.config import SAMPLE_COURSES_DIR
from app.parsers import DocumentLoader, PDFParser, DOCXParser, PPTXParser, CSVParser, TXTParser


def test_txt_parser():
    parser = TXTParser()
    chunks = parser.parse("Line 1\nLine 2\nLine 3", "notes.txt")
    assert len(chunks) == 3
    assert chunks[0].document == "notes.txt"
    assert chunks[0].text == "Line 1"


def test_pdf_parser():
    pdf_path = SAMPLE_COURSES_DIR / "Sketching_Fundamentals.pdf"
    if not pdf_path.exists():
        from scripts.generate_sample_data import generate_sample_files
        generate_sample_files(SAMPLE_COURSES_DIR.parent.parent)

    parser = PDFParser()
    chunks = parser.parse(pdf_path, pdf_path.name)
    assert len(chunks) > 0
    pages = {c.page for c in chunks}
    assert 1 in pages and 2 in pages and 3 in pages
    # Check that toolbar page was captured
    page3_chunks = [c for c in chunks if c.page == 3]
    assert any("toolbar" in c.text.lower() for c in page3_chunks)


def test_docx_parser():
    docx_path = SAMPLE_COURSES_DIR / "Advanced_Parts_Assembly.docx"
    parser = DOCXParser()
    chunks = parser.parse(docx_path, docx_path.name)
    assert len(chunks) > 0
    texts = " ".join([c.text for c in chunks])
    assert "Mate Controller" in texts
    assert "Legacy 2D Drawing Export" in texts


def test_pptx_parser():
    pptx_path = SAMPLE_COURSES_DIR / "Constraints_and_Mates.pptx"
    parser = PPTXParser()
    chunks = parser.parse(pptx_path, pptx_path.name)
    assert len(chunks) >= 3
    slides = {c.slide for c in chunks}
    assert 1 in slides and 2 in slides and 3 in slides


def test_csv_parser():
    csv_path = SAMPLE_COURSES_DIR / "Feature_Glossary_Index.csv"
    parser = CSVParser()
    chunks = parser.parse(csv_path, csv_path.name)
    assert len(chunks) == 2
    assert any("Mate Controller" in c.text for c in chunks)


def test_document_loader_dispatch():
    loader = DocumentLoader()
    csv_path = SAMPLE_COURSES_DIR / "Feature_Glossary_Index.csv"
    chunks = loader.parse_document(csv_path, csv_path.name)
    assert len(chunks) == 2
