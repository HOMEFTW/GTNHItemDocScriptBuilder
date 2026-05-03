"""Configuration and script persistence."""
from dataclasses import asdict, dataclass
from pathlib import Path
import re

from utils.helpers import load_json, save_json


DEFAULT_WINDOW_GEOMETRY = "1700x900"


@dataclass
class AppConfig:
    item_index_path: str = "D:/Code/gtnh_item_doc_exporter/item_index.json"
    gtnh_client_path: str = ""
    script_output_dir: str = ""
    window_geometry: str = DEFAULT_WINDOW_GEOMETRY
    last_template: str = "generic_gt_machine"
    last_recipe_map: str = "gt.recipe.assembler"

    @classmethod
    def load(cls, path: str | Path) -> "AppConfig":
        target = Path(path)
        if not target.exists():
            return cls()
        data = load_json(target)
        return cls(
            item_index_path=str(data.get("item_index_path", cls.item_index_path)),
            gtnh_client_path=str(data.get("gtnh_client_path", "")),
            script_output_dir=str(data.get("script_output_dir", "")),
            window_geometry=normalize_window_geometry(str(data.get("window_geometry", DEFAULT_WINDOW_GEOMETRY))),
            last_template=str(data.get("last_template", "generic_gt_machine")),
            last_recipe_map=str(data.get("last_recipe_map", "gt.recipe.assembler")),
        )

    def save(self, path: str | Path) -> None:
        save_json(path, asdict(self))


def save_script(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def normalize_window_geometry(geometry: str, min_width: int = 1700, min_height: int = 760) -> str:
    match = re.match(r"^(\d+)x(\d+)([+-]\d+[+-]\d+)?$", geometry.strip())
    if not match:
        return DEFAULT_WINDOW_GEOMETRY
    width = max(int(match.group(1)), min_width)
    height = max(int(match.group(2)), min_height)
    offset = match.group(3) or ""
    return f"{width}x{height}{offset}"
