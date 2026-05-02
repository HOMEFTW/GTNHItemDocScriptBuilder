"""Built-in machine templates inspired by ModTweaker logger output."""
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class MachineTemplate:
    template_id: str
    display_name: str
    max_item_inputs: int
    max_item_outputs: int
    max_fluid_inputs: int
    max_fluid_outputs: int
    style: str
    recipe_map: str = ""


TEMPLATES: Dict[str, MachineTemplate] = {
    "generic_gt_machine": MachineTemplate(
        "generic_gt_machine",
        "Generic GT Machine",
        16,
        4,
        4,
        4,
        "generic_gt",
        "gt.recipe.assembler",
    ),
    "assembler_like": MachineTemplate("assembler_like", "Assembler-like", 16, 4, 4, 4, "generic_gt", "gt.recipe.assembler"),
    "cutter_like": MachineTemplate("cutter_like", "Cutter-like", 16, 4, 4, 4, "generic_gt", "gt.recipe.cuttingsaw"),
    "macerator_like": MachineTemplate("macerator_like", "Macerator-like", 16, 4, 4, 4, "generic_gt", "gt.recipe.macerator"),
    "mixer_like": MachineTemplate("mixer_like", "Mixer-like", 16, 4, 4, 4, "generic_gt", "gt.recipe.mixer"),
    "chemical_reactor_like": MachineTemplate(
        "chemical_reactor_like",
        "Chemical Reactor-like",
        16,
        4,
        4,
        4,
        "generic_gt",
        "gt.recipe.chemicalreactor",
    ),
    "blast_furnace_like": MachineTemplate(
        "blast_furnace_like",
        "Blast Furnace-like",
        16,
        4,
        4,
        4,
        "generic_gt",
        "gt.recipe.blastfurnace",
    ),
    "thermal_expansion_furnace": MachineTemplate(
        "thermal_expansion_furnace",
        "Thermal Expansion Furnace",
        1,
        1,
        0,
        0,
        "te_furnace",
    ),
    "thermal_expansion_pulverizer": MachineTemplate(
        "thermal_expansion_pulverizer",
        "Thermal Expansion Pulverizer",
        1,
        2,
        0,
        0,
        "te_pulverizer",
    ),
    "appeng_grinder": MachineTemplate("appeng_grinder", "AE Grinder", 1, 3, 0, 0, "ae_grinder"),
    "appeng_inscriber": MachineTemplate("appeng_inscriber", "AE Inscriber", 3, 1, 0, 0, "ae_inscriber"),
}


def template_options() -> List[MachineTemplate]:
    return list(TEMPLATES.values())
