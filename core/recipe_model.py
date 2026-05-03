"""Recipe draft models for ZS generation."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ScriptItem:
    expression: str
    amount: int = 1
    comment_name: str = ""
    suffix: str = ""

    def to_zs(self) -> str:
        base = self.expression.strip() + self.suffix.strip()
        if self.amount != 1:
            return f"{base} * {self.amount}"
        return base


@dataclass(frozen=True)
class ScriptFluid:
    name_or_expression: str
    amount: int

    def to_zs(self) -> str:
        value = self.name_or_expression.strip()
        if value.startswith("<"):
            base = value
        else:
            base = f"<liquid:{value}>"
        return f"{base} * {self.amount}"


@dataclass
class RecipeDraft:
    kind: str
    item_inputs: List[Optional[ScriptItem]] = field(default_factory=list)
    item_outputs: List[Optional[ScriptItem]] = field(default_factory=list)
    output_chances: List[int] = field(default_factory=list)
    fluid_inputs: List[ScriptFluid] = field(default_factory=list)
    fluid_outputs: List[ScriptFluid] = field(default_factory=list)
    duration: int = 200
    eut: int = 30
    special_value: Optional[int] = None
    xp: float = 0.0
    include_furnace_xp: bool = True
    shaped_mirrored: bool = False
    fuel_ticks: int = 1600
    remove_mode: str = "all"
    template_id: str = "generic_gt_machine"
    recipe_map: str = ""
    no_fluid_inputs: bool = False
    no_fluid_outputs: bool = False
