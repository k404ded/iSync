"""
Word DOCX Document Parser for iSync.
Extracts headings, hierarchical sections, paragraphs, tables, and drawing elements.
"""

import io
from typing import BinaryIO, Union, List, Optional
from pathlib import Path
from docx import Document
from app.models.schemas import ContentChunk
from app.parsers.base import BaseParser


class DOCXParser(BaseParser):
    def parse(self, source: Union[str, Path, BinaryIO], filename: str) -> List[ContentChunk]:
        if isinstance(source, (str, Path)) and Path(source).is_file():
            doc = Document(str(source))
        elif hasattr(source, "read"):
            data = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            doc = Document(io.BytesIO(data))
        else:
            doc = Document(io.BytesIO(bytes(source)))

        chunks: List[ContentChunk] = []
        chunk_idx = 1
        est_page = 1
        para_counter = 0

        curr_module: Optional[str] = None
        curr_lesson: Optional[str] = None
        curr_section: Optional[str] = None
        curr_heading: Optional[str] = None

        for p in doc.paragraphs:
            text = p.text.strip()
            para_counter += 1
            if para_counter % 6 == 0:
                est_page += 1

            has_image = False
            for r in p.runs:
                xml = r._element.xml
                if "<w:drawing" in xml or "<w:pict" in xml or "<a:blip" in xml:
                    has_image = True
                    break

            if not text and not has_image:
                continue

            style_name = p.style.name.lower() if p.style else ""
            is_heading = style_name.startswith("heading") or style_name in ("title", "subtitle")

            if is_heading:
                curr_heading = text
                if "heading 1" in style_name or "title" in style_name:
                    curr_module = text
                elif "heading 2" in style_name:
                    curr_lesson = text
                elif "heading 3" in style_name:
                    curr_section = text

            if "module " in text.lower() and len(text) < 70:
                curr_module = text
            elif "lesson " in text.lower() and len(text) < 70:
                curr_lesson = text

            display_text = text if text else f"[Inline Figure in {curr_section or curr_lesson or 'Document'}]"

            chunk = ContentChunk(
                chunk_id=f"chunk_{chunk_idx:04d}",
                document=filename,
                doc_type="docx",
                module=curr_module,
                lesson=curr_lesson,
                section=curr_section,
                page=est_page,
                heading=curr_heading,
                text=display_text,
                has_image_or_screenshot=has_image,
                order_index=chunk_idx,
            )
            chunks.append(chunk)
            chunk_idx += 1

        # Tables
        for table in doc.tables:
            para_counter += 2
            rows_data = []
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    rows_data.append(" | ".join(cells))

            if rows_data:
                chunk = ContentChunk(
                    chunk_id=f"chunk_{chunk_idx:04d}",
                    document=filename,
                    doc_type="docx",
                    module=curr_module,
                    lesson=curr_lesson,
                    section=curr_section,
                    page=est_page,
                    heading=curr_heading,
                    text="Table Data:\n" + "\n".join(rows_data),
                    order_index=chunk_idx,
                )
                chunks.append(chunk)
                chunk_idx += 1

        return chunks
