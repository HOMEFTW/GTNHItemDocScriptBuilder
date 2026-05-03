"""Load and search GTNH fluid document exports."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from utils.helpers import load_json


def default_fluid_index_path(item_index_path: str | Path) -> Path:
    return Path(item_index_path).with_name("fluid_index.json")


@dataclass(frozen=True)
class FluidEntry:
    fluid_name: str
    ct_expression: str
    chinese_name: str
    english_name: str
    unlocalized_name: str
    temperature: int
    density: int
    viscosity: int
    gaseous: bool
    guid: str

    @classmethod
    def from_json(cls, data: dict) -> "FluidEntry":
        return cls(
            fluid_name=str(data.get("fluidName", "")),
            ct_expression=str(data.get("ctExpression", "")),
            chinese_name=str(data.get("chineseName", "")),
            english_name=str(data.get("englishName", "")),
            unlocalized_name=str(data.get("unlocalizedName", "")),
            temperature=int(data.get("temperature", 0)),
            density=int(data.get("density", 0)),
            viscosity=int(data.get("viscosity", 0)),
            gaseous=bool(data.get("gaseous", False)),
            guid=str(data.get("guid", "")),
        )

    def search_text(self) -> str:
        return " ".join(
            [
                self.fluid_name,
                self.ct_expression,
                self.chinese_name,
                self.english_name,
                self.unlocalized_name,
                self.guid,
            ]
        ).lower()


class FluidIndexStore:
    def __init__(self, entries: Iterable[FluidEntry], language: str = "", generated_at: str = ""):
        self.entries: List[FluidEntry] = list(entries)
        self.language = language
        self.generated_at = generated_at
        self.entry_count = len(self.entries)
        self._search_text = [(entry, entry.search_text()) for entry in self.entries]

    @classmethod
    def load(cls, path: str | Path) -> "FluidIndexStore":
        return cls.from_data(load_json(path))

    @classmethod
    def from_data(cls, data: dict) -> "FluidIndexStore":
        entries = [FluidEntry.from_json(item) for item in data.get("entries", [])]
        return cls(entries, str(data.get("language", "")), str(data.get("generatedAt", "")))

    def search(self, query: str, limit: int = 500) -> List[FluidEntry]:
        normalized = query.strip().lower()
        if not normalized:
            return self.entries[:limit]
        results: List[FluidEntry] = []
        terms = normalized.split()
        for entry, text in self._search_text:
            if all(term in text for term in terms):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
