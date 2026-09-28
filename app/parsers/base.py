"""
Base parser interface for iSync document ingestion.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Union, List
from pathlib import Path
from app.models.schemas import ContentChunk


class BaseParser(ABC):
    @abstractmethod
    def parse(self, source: Union[str, Path, BinaryIO], filename: str) -> List[ContentChunk]:
        """
        Parses document into structured ContentChunks preserving exact source hierarchy:
        module, lesson, section, heading, page/slide/row.
        """
        pass
