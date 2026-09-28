"""
Parsers package for iSync.
"""

from app.parsers.base import BaseParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.pptx_parser import PPTXParser
from app.parsers.csv_parser import CSVParser
from app.parsers.txt_parser import TXTParser
from app.parsers.loader import DocumentLoader

__all__ = [
    "BaseParser",
    "PDFParser",
    "DOCXParser",
    "PPTXParser",
    "CSVParser",
    "TXTParser",
    "DocumentLoader",
]
