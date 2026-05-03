"""Parse a supported ZS script back into a recipe draft."""
from __future__ import annotations

import re
from typing import Optional

from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem


def parse_zs_script(script: str) -> RecipeDraft:
    text = script.strip()
    if "mods.gregtech.RecipeRemover.remove" in text:
        return _parse_gt_remover(text)
    if "mods.gregtech.RA2" in text and ".builder()" in text:
        return _parse_gt_machine(text)
    if "furnace.setFuel" in text:
        return _parse_fuel(text)
    if "furnace.addRecipe" in text:
        return _parse_furnace(text)
    if "furnace.remove" in text:
        return _parse_furnace_remove(text)
    if "recipes.addShapedMirrored" in text:
        return _parse_shaped(text, mirrored=True)
    if "recipes.addShaped" in text:
        return _parse_shaped(text, mirrored=False)
    if "recipes.addShapeless" in text:
        return _parse_shapeless(text)
    if "recipes.removeShaped" in text:
        return _parse_simple_remove(text, "shaped")
    if "recipes.removeShapeless" in text:
        return _parse_simple_remove(text, "shapeless")
    if "recipes.remove" in text:
        return _parse_simple_remove(text, "all")
    raise ValueError("未找到可导入的受支持 ZS 配方")


def _parse_gt_machine(text: str) -> RecipeDraft:
    item_inputs = _parse_item_array(_chain_arg(text, ".itemInputs"))
    item_outputs = _parse_item_array(_chain_arg(text, ".itemOutputs"))
    output_chances_arg = _optional_chain_arg(text, ".outputChances")
    fluid_inputs = [] if ".noFluidInputs()" in text else _parse_fluid_array(_optional_chain_arg(text, ".fluidInputs") or "[]")
    fluid_outputs = [] if ".noFluidOutputs()" in text else _parse_fluid_array(_optional_chain_arg(text, ".fluidOutputs") or "[]")
    return RecipeDraft(
        kind="machine",
        template_id="generic_gt_machine",
        recipe_map=_string_chain_arg(text, ".addTo") or "gt.recipe.assembler",
        item_inputs=item_inputs,
        item_outputs=item_outputs,
        output_chances=_parse_int_array(output_chances_arg) if output_chances_arg else [],
        fluid_inputs=fluid_inputs,
        fluid_outputs=fluid_outputs,
        duration=_int_chain_arg(text, ".duration", 200),
        eut=_int_chain_arg(text, ".eut", 30),
        special_value=_optional_int_chain_arg(text, ".specialValue"),
        special_item=_parse_item(_optional_chain_arg(text, ".specialItem") or ""),
        no_fluid_inputs=".noFluidInputs()" in text,
        no_fluid_outputs=".noFluidOutputs()" in text,
    )


def _parse_gt_remover(text: str) -> RecipeDraft:
    args = _function_args(text, "mods.gregtech.RecipeRemover.remove")
    if len(args) < 3:
        raise ValueError("GT 删除配方参数不足")
    return RecipeDraft(
        kind="remove",
        remove_mode="machine",
        template_id="generic_gt_machine",
        recipe_map=_unquote(args[0]),
        item_inputs=_parse_item_array(args[1]),
        fluid_inputs=_parse_fluid_array(args[2]),
    )


def _parse_shaped(text: str, mirrored: bool) -> RecipeDraft:
    function_name = "recipes.addShapedMirrored" if mirrored else "recipes.addShaped"
    args = _function_args(text, function_name)
    if len(args) < 2:
        raise ValueError("有序合成参数不足")
    rows = _array_tokens(args[1])
    inputs: list[Optional[ScriptItem]] = []
    for row in rows:
        inputs.extend(_parse_item_array(row))
    return RecipeDraft(
        kind="shaped",
        item_inputs=inputs,
        item_outputs=[_required_item(args[0])],
        shaped_mirrored=mirrored,
    )


def _parse_shapeless(text: str) -> RecipeDraft:
    args = _function_args(text, "recipes.addShapeless")
    if len(args) < 2:
        raise ValueError("无序合成参数不足")
    return RecipeDraft(kind="shapeless", item_outputs=[_required_item(args[0])], item_inputs=_parse_item_array(args[1]))


def _parse_furnace(text: str) -> RecipeDraft:
    args = _function_args(text, "furnace.addRecipe")
    if len(args) < 2:
        raise ValueError("熔炉配方参数不足")
    return RecipeDraft(
        kind="furnace",
        item_outputs=[_required_item(args[0])],
        item_inputs=[_required_item(args[1])],
        xp=float(args[2]) if len(args) > 2 else 0.0,
        include_furnace_xp=len(args) > 2,
    )


def _parse_fuel(text: str) -> RecipeDraft:
    args = _function_args(text, "furnace.setFuel")
    if len(args) < 2:
        raise ValueError("燃料脚本参数不足")
    return RecipeDraft(kind="fuel", item_inputs=[_required_item(args[0])], fuel_ticks=int(args[1]))


def _parse_furnace_remove(text: str) -> RecipeDraft:
    args = _function_args(text, "furnace.remove")
    if not args:
        raise ValueError("熔炉删除参数不足")
    return RecipeDraft(
        kind="remove",
        remove_mode="furnace",
        item_outputs=[_required_item(args[0])],
        item_inputs=[_required_item(args[1])] if len(args) > 1 else [],
    )


def _parse_simple_remove(text: str, remove_mode: str) -> RecipeDraft:
    function_name = {
        "shaped": "recipes.removeShaped",
        "shapeless": "recipes.removeShapeless",
    }.get(remove_mode, "recipes.remove")
    args = _function_args(text, function_name)
    if not args:
        raise ValueError("删除配方参数不足")
    return RecipeDraft(kind="remove", remove_mode=remove_mode, item_outputs=[_required_item(args[0])])


def _function_args(text: str, function_name: str) -> list[str]:
    start = text.find(function_name)
    if start < 0:
        raise ValueError(f"未找到调用: {function_name}")
    open_index = text.find("(", start + len(function_name))
    if open_index < 0:
        raise ValueError(f"调用缺少左括号: {function_name}")
    close_index = _matching_paren(text, open_index)
    return _split_top_level(text[open_index + 1 : close_index])


def _chain_arg(text: str, method_name: str) -> str:
    value = _optional_chain_arg(text, method_name)
    if value is None:
        raise ValueError(f"未找到链式参数: {method_name}")
    return value


def _optional_chain_arg(text: str, method_name: str) -> Optional[str]:
    start = text.find(method_name + "(")
    if start < 0:
        return None
    open_index = text.find("(", start + len(method_name))
    close_index = _matching_paren(text, open_index)
    return text[open_index + 1 : close_index].strip()


def _string_chain_arg(text: str, method_name: str) -> str:
    value = _optional_chain_arg(text, method_name)
    return _unquote(value) if value else ""


def _int_chain_arg(text: str, method_name: str, default: int) -> int:
    value = _optional_int_chain_arg(text, method_name)
    return default if value is None else value


def _optional_int_chain_arg(text: str, method_name: str) -> Optional[int]:
    value = _optional_chain_arg(text, method_name)
    if value is None or not value.strip():
        return None
    return int(value.strip())


def _matching_paren(text: str, open_index: int) -> int:
    depth = 0
    in_string = ""
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = ""
            continue
        if char in ("'", '"'):
            in_string = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("调用缺少右括号")


def _array_tokens(value: str) -> list[str]:
    text = value.strip()
    if not (text.startswith("[") and text.endswith("]")):
        raise ValueError("数组参数格式错误")
    inner = text[1:-1].strip()
    if not inner:
        return []
    return _split_top_level(inner)


def _parse_item_array(value: str) -> list[Optional[ScriptItem]]:
    return [_parse_item(token) for token in _array_tokens(value)]


def _parse_fluid_array(value: str) -> list[ScriptFluid]:
    return [fluid for token in _array_tokens(value) if (fluid := _parse_fluid(token)) is not None]


def _parse_int_array(value: str) -> list[int]:
    return [int(token.strip()) for token in _array_tokens(value)]


def _split_top_level(value: str) -> list[str]:
    parts: list[str] = []
    start = 0
    round_depth = square_depth = brace_depth = angle_depth = 0
    in_string = ""
    escaped = False
    for index, char in enumerate(value):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = ""
            continue
        if char in ("'", '"'):
            in_string = char
        elif char == "<":
            angle_depth += 1
        elif char == ">" and angle_depth:
            angle_depth -= 1
        elif char == "(":
            round_depth += 1
        elif char == ")":
            round_depth -= 1
        elif char == "[":
            square_depth += 1
        elif char == "]":
            square_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        elif char == "," and not any((round_depth, square_depth, brace_depth, angle_depth)):
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return parts


def _required_item(value: str) -> ScriptItem:
    item = _parse_item(value)
    if item is None:
        raise ValueError("需要物品表达式")
    return item


def _parse_item(value: str) -> Optional[ScriptItem]:
    text = value.strip()
    if not text or text == "null":
        return None
    base, amount = _split_amount(text)
    match = re.match(r"^(<[^>]+>)(.*)$", base, re.S)
    if not match:
        return ScriptItem(base, amount)
    return ScriptItem(match.group(1).strip(), amount, suffix=match.group(2).strip())


def _parse_fluid(value: str) -> Optional[ScriptFluid]:
    text = value.strip()
    if not text or text == "null":
        return None
    base, amount = _split_amount(text)
    return ScriptFluid(base, amount)


def _split_amount(value: str) -> tuple[str, int]:
    match = re.match(r"^(.*?)\s*\*\s*(-?\d+)\s*$", value, re.S)
    if not match:
        return value.strip(), 1
    return match.group(1).strip(), int(match.group(2))


def _unquote(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        return text[1:-1]
    return text
