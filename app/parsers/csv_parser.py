"""
CSV Document Parser for iSync.
Parses tabular curriculum databases, feature glossaries, and syllabi using pandas.
Preserves row numbers, column headers, and structural fields.
"""

import io
from typing import BinaryIO, Union, List
from pathlib import Path
import pandas as pd
from app.models.schemas import ContentChunk
from app.parsers.base import BaseParser


class CSVParser(BaseParser):
    def parse(self, source: Union[str, Path, BinaryIO], filename: str) -> List[ContentChunk]:
        if isinstance(source, (str, Path)) and Path(source).is_file():
            df = pd.read_csv(str(source))
        elif hasattr(source, "read"):
            data = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            if isinstance(data, bytes):
                df = pd.read_csv(io.BytesIO(data))
            else:
                df = pd.read_csv(io.StringIO(str(data)))
        elif isinstance(source, str):
            df = pd.read_csv(io.StringIO(source))
        else:
            df = pd.read_csv(io.BytesIO(bytes(source)))

        chunks: List[ContentChunk] = []
        chunk_idx = 1
        cols = [c.strip() for c in df.columns]
        lower_cols = {c.lower(): c for c in cols}

        mod_col = lower_cols.get("module")
        les_col = lower_cols.get("lesson") or lower_cols.get("topic")
        sec_col = lower_cols.get("section")
        page_col = lower_cols.get("page") or lower_cols.get("page_number")
        term_col = lower_cols.get("term") or lower_cols.get("feature")

        for idx, row in df.iterrows():
            row_num = int(idx) + 1
            row_items = []
            for c in cols:
                val = str(row[c]).strip() if pd.notna(row[c]) else ""
                if val:
                    row_items.append(f"{c}: {val}")

            text = " | ".join(row_items)
            if not text:
                continue

            mod_val = str(row[mod_col]).strip() if mod_col and pd.notna(row[mod_col]) else None
            les_val = str(row[les_col]).strip() if les_col and pd.notna(row[les_col]) else None
            sec_val = str(row[sec_col]).strip() if sec_col and pd.notna(row[sec_col]) else None
            term_val = str(row[term_col]).strip() if term_col and pd.notna(row[term_col]) else None
            p_val = int(row[page_col]) if page_col and pd.notna(row[page_col]) and str(row[page_col]).isdigit() else None

            heading_val = term_val or les_val or f"Row {row_num}"

            chunk = ContentChunk(
                chunk_id=f"chunk_{chunk_idx:04d}",
                document=filename,
                doc_type="csv",
                module=mod_val,
                lesson=les_val,
                section=sec_val or f"Row {row_num}",
                page=p_val,
                row=row_num,
                heading=heading_val,
                text=text,
                order_index=chunk_idx,
                raw_metadata=row.to_dict(),
            )
            chunks.append(chunk)
            chunk_idx += 1

        return chunks
