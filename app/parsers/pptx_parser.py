"""
PowerPoint PPTX Document Parser for iSync.
Extracts slide numbers, slide titles, body text, notes, and diagrams.
"""

import io
from typing import BinaryIO, Union, List, Optional
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from app.models.schemas import ContentChunk
from app.parsers.base import BaseParser


class PPTXParser(BaseParser):
    def parse(self, source: Union[str, Path, BinaryIO], filename: str) -> List[ContentChunk]:
        if isinstance(source, (str, Path)) and Path(source).is_file():
            prs = Presentation(str(source))
        elif hasattr(source, "read"):
            data = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            prs = Presentation(io.BytesIO(data))
        else:
            prs = Presentation(io.BytesIO(bytes(source)))

        chunks: List[ContentChunk] = []
        chunk_idx = 1

        for slide_idx, slide in enumerate(prs.slides):
            slide_num = slide_idx + 1
            slide_title = None

            if slide.shapes.title and slide.shapes.title.text:
                slide_title = slide.shapes.title.text.strip()

            has_image = False
            texts: List[str] = []

            for shape in slide.shapes:
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    has_image = True

                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        t = para.text.strip()
                        if t:
                            texts.append(t)

                if shape.has_table:
                    for row in shape.table.rows:
                        row_vals = [c.text.strip() for c in row.cells if c.text.strip()]
                        if row_vals:
                            texts.append(" | ".join(row_vals))

            # Speaker notes
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                note_text = slide.notes_slide.notes_text_frame.text.strip()
                if note_text:
                    texts.append(f"[Speaker Notes]: {note_text}")

            combined_text = "\n".join(texts)
            if not combined_text and not has_image:
                continue

            chunk = ContentChunk(
                chunk_id=f"chunk_{chunk_idx:04d}",
                document=filename,
                doc_type="pptx",
                module=None,
                lesson=slide_title,
                section=f"Slide {slide_num}",
                slide=slide_num,
                heading=slide_title,
                text=combined_text if combined_text else f"[Slide {slide_num} visual illustration]",
                has_image_or_screenshot=has_image,
                order_index=chunk_idx,
            )
            chunks.append(chunk)
            chunk_idx += 1

        return chunks
