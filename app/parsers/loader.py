"""
Unified Document Loader and Router for iSync.
Routes files of various types (PDF, DOCX, PPTX, CSV, TXT) to the appropriate parser.
"""

from typing import List, Union, BinaryIO
from pathlib import Path
from app.models.schemas import ContentChunk
from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.pptx_parser import PPTXParser
from app.parsers.csv_parser import CSVParser
from app.parsers.txt_parser import TXTParser


class DocumentLoader:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.pptx_parser = PPTXParser()
        self.csv_parser = CSVParser()
        self.txt_parser = TXTParser()

    def parse_document(self, file_source: Union[str, Path, BinaryIO, any], filename: str) -> List[ContentChunk]:
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            return self.pdf_parser.parse(file_source, filename)
        elif ext in (".docx", ".doc"):
            return self.docx_parser.parse(file_source, filename)
        elif ext in (".pptx", ".ppt"):
            return self.pptx_parser.parse(file_source, filename)
        elif ext in (".csv", ".tsv"):
            return self.csv_parser.parse(file_source, filename)
        elif ext in (".txt", ".md"):
            return self.txt_parser.parse(file_source, filename)
        else:
            return self.txt_parser.parse(file_source, filename)

    def parse_multiple(self, files: List[Union[str, Path, any]]) -> List[ContentChunk]:
        all_chunks: List[ContentChunk] = []
        for f in files:
            name = getattr(f, "name", None) or Path(f).name
            chunks = self.parse_document(f, name)
            all_chunks.extend(chunks)
        return all_chunks
