from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import RawItem


class SourceAdapter(ABC):
    name: str

    @abstractmethod
    def fetch(self) -> list[RawItem]:
        raise NotImplementedError
