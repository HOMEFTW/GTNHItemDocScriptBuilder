"""Recipe editor slot layouts."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RecipeLayout:
    input_title: str
    input_count: int
    input_columns: int
    output_title: str
    output_count: int
    output_columns: int


LAYOUTS = {
    "shaped": RecipeLayout("输入格 3 x 3", 9, 3, "输出格", 1, 1),
    "shapeless": RecipeLayout("输入格 3 x 3", 9, 3, "输出格", 1, 1),
    "furnace": RecipeLayout("输入格", 1, 1, "输出格", 1, 1),
    "fuel": RecipeLayout("燃料物品格", 1, 1, "无输出格", 0, 1),
    "remove_shaped": RecipeLayout("删除有序配方输入格 3 x 3", 9, 3, "删除目标输出格", 1, 1),
    "remove_shapeless": RecipeLayout("删除无序配方输入格 3 x 3", 9, 3, "删除目标输出格", 1, 1),
    "remove_furnace": RecipeLayout("删除熔炉输入格", 1, 1, "删除目标输出格", 1, 1),
    "remove_machine": RecipeLayout("删除 GT 配方输入格 16 格", 16, 4, "删除 GT 目标输出格 4 格", 4, 4),
    "machine": RecipeLayout("机器输入格 16 格", 16, 4, "机器输出格 4 格", 4, 4),
}

REMOVE_MODE_LABELS = {
    "shaped": "有序",
    "shapeless": "无序",
    "furnace": "熔炉",
    "machine": "GT",
}


def layout_for_kind(kind: str) -> RecipeLayout:
    return LAYOUTS.get(kind, LAYOUTS["shaped"])


def layout_key_for(recipe_kind: str, remove_mode: str = "shaped") -> str:
    if recipe_kind == "remove":
        return "remove_" + remove_mode_id_from_label(remove_mode)
    return recipe_kind


def remove_mode_label(mode_id: str) -> str:
    return REMOVE_MODE_LABELS.get(mode_id, REMOVE_MODE_LABELS["shaped"])


def remove_mode_label_options() -> list[str]:
    return list(REMOVE_MODE_LABELS.values())


def remove_mode_id_from_label(value: str) -> str:
    for mode_id, label in REMOVE_MODE_LABELS.items():
        if value == label or value == mode_id:
            return mode_id
    return "shaped"
