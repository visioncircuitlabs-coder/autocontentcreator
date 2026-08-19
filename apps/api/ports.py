from typing import Protocol

from models import Signal


class TrendSource(Protocol):
    name: str

    def fetch(self, query_id: str) -> list[Signal]: ...
