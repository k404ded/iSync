"""
PDF Document Parser for iSync.
Extracts pages, text blocks, headings, screenshots/figures, and exact location hierarchy.
"""

import io
import re
from typing import BinaryIO, Union, List, Optional
from pathlib import Path
from app.models.schemas import ContentChunk
from app.parsers.base import BaseParser


class PDFParser(BaseParser):
    def parse(self, source: Union[str, Path, BinaryIO], filename: str) -> List[ContentChunk]:
        file_bytes = None
        if isinstance(source, (str, Path)) and Path(source).is_file():
            with open(source, "rb") as f:
                file_bytes = f.read()
        elif hasattr(source, "read"):
            file_bytes = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
        elif isinstance(source, bytes):
            file_bytes = source
        else:
            file_bytes = bytes(source)

        try:
            return self._parse_with_pymupdf(file_bytes, filename)
        except Exception:
            return self._parse_with_pdfplumber(file_bytes, filename)

    def _parse_with_pymupdf(self, file_bytes: bytes, filename: str) -> List[ContentChunk]:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        chunks: List[ContentChunk] = []
        chunk_idx = 1

        curr_module: Optional[str] = None
        curr_lesson: Optional[str] = None
        curr_section: Optional[str] = None
        curr_heading: Optional[str] = None

        for page_idx in range(len(doc)):
            page_num = page_idx + 1
            page = doc[page_idx]

            # Detect images on page
            images = page.get_images()
            has_image = len(images) > 0

            blocks = page.get_text("blocks")
            for b in blocks:
                raw_text = b[4].strip()
                if not raw_text:
                    continue

                clean_text = " ".join(raw_text.split())

                # Heading & hierarchy extraction
                m_mod = re.search(r"\b(module\s+\d+[^:\n\.\-]*[:\-]?[^\n\.]*)", clean_text, re.IGNORECASE)
                if m_mod:
                    curr_module = m_mod.group(1).strip()

                m_les = re.search(r"\b(lesson\s+\d+[^:\n\.\-]*[:\-]?[^\n\.]*)", clean_text, re.IGNORECASE)
                if m_les:
                    curr_lesson = m_les.group(1).strip()

                m_sec = re.search(r"\b(section\s+\d+[^:\n\.\-]*[:\-]?[^\n\.]*)", clean_text, re.IGNORECASE)
                if m_sec:
                    curr_section = m_sec.group(1).strip()

                # Short heading line detection
                if len(clean_text) < 75 and (
                    clean_text.isupper()
                    or re.match(r"^(?:Module|Lesson|Section|Chapter|\d+\.|\d+\.\d+)\b", clean_text, re.IGNORECASE)
                    or clean_text.endswith(":")
                ):
                    curr_heading = clean_text

                # Image/Screenshot detection
                is_screenshot = False
                caption = None
                if re.search(r"\b(?:Figure|Screenshot|Image|Illustration)\s+\d+", clean_text, re.IGNORECASE):
                    is_screenshot = True
                    caption = clean_text
                elif has_image and any(k in clean_text.lower() for k in ["screenshot", "figure", "toolbar shown", "as shown below", "interface"]):
                    is_screenshot = True
                    caption = clean_text

                chunk = ContentChunk(
                    chunk_id=f"chunk_{chunk_idx:04d}",
                    document=filename,
                    doc_type="pdf",
                    module=curr_module,
                    lesson=curr_lesson,
                    section=curr_section,
                    page=page_num,
                    heading=curr_heading,
                    text=clean_text,
                    has_image_or_screenshot=is_screenshot or has_image,
                    image_caption=caption,
                    order_index=chunk_idx,
                )
                chunks.append(chunk)
                chunk_idx += 1

        doc.close()
        return chunks

    def _parse_with_pdfplumber(self, file_bytes: bytes, filename: str) -> List[ContentChunk]:
        import pdfplumber

        chunks: List[ContentChunk] = []
        chunk_idx = 1
        curr_module, curr_lesson = None, None

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                text = page.extract_text() or ""
                has_image = len(getattr(page, "images", [])) > 0

                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                for para in paragraphs:
                    clean = " ".join(para.split())
                    if not clean:
                        continue

                    if "module " in clean.lower():
                        curr_module = clean[:60]
                    if "lesson " in clean.lower():
                        curr_lesson = clean[:60]

                    chunk = ContentChunk(
                        chunk_id=f"chunk_{chunk_idx:04d}",
                        document=filename,
                        doc_type="pdf",
                        module=curr_module,
                        lesson=curr_lesson,
                        page=page_num,
                        text=clean,
                        has_image_or_screenshot=has_image,
                        order_index=chunk_idx,
                    )
                    chunks.append(chunk)
                    chunk_idx += 1

        return chunks
