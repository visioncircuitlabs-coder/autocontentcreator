from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from models import Signal


class TrendSource(Protocol):
    name: str

    def fetch(self, query_id: str) -> list[Signal]: ...


class ChatModel(Protocol):
    def complete_json(self, system: str, user: str, schema: type) -> BaseModel: ...


class ImageGen(Protocol):
    def generate(self, prompt: str, out_path: Path) -> Path: ...


class VideoGen(Protocol):
    def generate(self, prompt: str, out_path: Path) -> Path: ...
