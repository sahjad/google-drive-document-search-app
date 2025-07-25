# Base class for file content extractors

from abc import ABC, abstractmethod
from io import BytesIO

class BaseExtractor(ABC):
    @abstractmethod
    def extract_text(self, file_stream: BytesIO) -> str:
        pass