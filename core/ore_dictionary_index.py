"""Load and search GTNH ore dictionary document exports."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from utils.helpers import load_json


def default_ore_dictionary_index_path(item_index_path: str | Path) -> Path:
    return Path(item_index_path).with_name("ore_dictionary_index.json")


@dataclass(frozen=True)
class OreDictionaryEntry:
    ore_name: str
    ct_expression: str
    item_count: int
    items: List[str]
    guid: str

    @classmethod
    def from_json(cls, data: dict) -> "OreDictionaryEntry":
        items = [str(item) for item in data.get("items", [])]
        return cls(
            ore_name=str(data.get("oreName", "")),
            ct_expression=str(data.get("ctExpression", "")),
            item_count=int(data.get("itemCount", len(items))),
            items=items,
            guid=str(data.get("guid", "")),
        )

    def search_text(self) -> str:
        return " ".join([self.ore_name, self.ct_expression, self.guid, *self.items]).lower()


class OreDictionaryIndexStore:
    def __init__(self, entries: Iterable[OreDictionaryEntry], language: str = "", generated_at: str = ""):
        self.entries: List[OreDictionaryEntry] = list(entries)
        self.language = language
        self.generated_at = generated_at
        self.entry_count = len(self.entries)
        self._search_text = [(entry, entry.search_text()) for entry in self.entries]

    @classmethod
    def load(cls, path: str | Path) -> "OreDictionaryIndexStore":
        return cls.from_data(load_json(path))

    @classmethod
    def from_data(cls, data: dict) -> "OreDictionaryIndexStore":
        entries = [OreDictionaryEntry.from_json(item) for item in data.get("entries", [])]
        return cls(entries, str(data.get("language", "")), str(data.get("generatedAt", "")))

    def search(self, query: str, limit: int = 500) -> List[OreDictionaryEntry]:
        normalized = query.strip().lower()
        if not normalized:
            return self.entries[:limit]
        results: List[OreDictionaryEntry] = []
        terms = normalized.split()
        for entry, text in self._search_text:
            if all(term in text for term in terms):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
