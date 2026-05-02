"""Load and search GTNH item document exports."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from utils.helpers import load_json


@dataclass(frozen=True)
class ItemEntry:
    mod_id: str
    registry_id: str
    meta: int
    ct_expression: str
    chinese_name: str
    english_name: str
    unlocalized_name: str
    is_block: bool
    guid: str
    nbt_summary: str

    @classmethod
    def from_json(cls, data: dict) -> "ItemEntry":
        return cls(
            mod_id=str(data.get("modId", "")),
            registry_id=str(data.get("registryId", "")),
            meta=int(data.get("meta", 0)),
            ct_expression=str(data.get("ctExpression", "")),
            chinese_name=str(data.get("chineseName", "")),
            english_name=str(data.get("englishName", "")),
            unlocalized_name=str(data.get("unlocalizedName", "")),
            is_block=bool(data.get("isBlock", False)),
            guid=str(data.get("guid", "")),
            nbt_summary=str(data.get("nbtSummary", "")),
        )

    def search_text(self) -> str:
        return " ".join(
            [
                self.mod_id,
                self.registry_id,
                str(self.meta),
                self.ct_expression,
                self.chinese_name,
                self.english_name,
                self.unlocalized_name,
                self.guid,
            ]
        ).lower()


class ItemIndexStore:
    def __init__(self, entries: Iterable[ItemEntry], language: str = "", generated_at: str = ""):
        self.entries: List[ItemEntry] = list(entries)
        self.language = language
        self.generated_at = generated_at
        self.entry_count = len(self.entries)
        self._search_text = [(entry, entry.search_text()) for entry in self.entries]

    @classmethod
    def load(cls, path: str | Path) -> "ItemIndexStore":
        return cls.from_data(load_json(path))

    @classmethod
    def from_data(cls, data: dict) -> "ItemIndexStore":
        entries = [ItemEntry.from_json(item) for item in data.get("entries", [])]
        return cls(entries, str(data.get("language", "")), str(data.get("generatedAt", "")))

    def search(self, query: str, limit: int = 500) -> List[ItemEntry]:
        normalized = query.strip().lower()
        if not normalized:
            return self.entries[:limit]
        results: List[ItemEntry] = []
        terms = normalized.split()
        for entry, text in self._search_text:
            if all(term in text for term in terms):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
