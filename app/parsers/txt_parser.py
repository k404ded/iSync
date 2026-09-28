"""
Plain Text Document Parser for iSync.
Extracts lines and paragraphs, preserving line indices and sections.
"""

from typing import BinaryIO, Union, List
from pathlib import Path
from app.models.schemas import ContentChunk
from app.parsers.base import BaseParser


class TXTParser(BaseParser):
    def parse(self, source: Union[str, Path, BinaryIO], filename: str) -> List[ContentChunk]:
        if isinstance(source, (str, Path)) and Path(source).is_file():
            with open(source, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif hasattr(source, "read"):
            data = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            if isinstance(data, bytes):
                content = data.decode("utf-8", errors="ignore")
            else:
                content = str(data)
        else:
            content = str(source)

        chunks: List[ContentChunk] = []
        chunk_idx = 1
        lines = [l.strip() for l in content.splitlines() if l.strip()]

        for line_num, line in enumerate(lines, 1):
            chunk = ContentChunk(
                chunk_id=f"chunk_{chunk_idx:04d}",
                document=filename,
                doc_type="txt",
                section=f"Line {line_num}",
                row=line_num,
                text=line,
                order_index=chunk_idx,
            )
            chunks.append(chunk)
            chunk_idx += 1

        return chunks
