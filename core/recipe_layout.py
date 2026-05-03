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
    "remove": RecipeLayout("删除匹配输入格", 16, 4, "删除目标输出格", 1, 1),
    "machine": RecipeLayout("机器输入格 16 格", 16, 4, "机器输出格 4 格", 4, 4),
}


def layout_for_kind(kind: str) -> RecipeLayout:
    return LAYOUTS.get(kind, LAYOUTS["shaped"])
