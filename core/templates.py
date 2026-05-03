"""Built-in machine templates inspired by ModTweaker logger output."""
from dataclasses import dataclass
from typing import Dict, List


RECIPE_MAPS = [
    "gt.recipe.orewasher",
    "gt.recipe.thermalcentrifuge",
    "gt.recipe.compressor",
    "gt.recipe.extractor",
    "ic.recipe.recycler",
    "mc.recipe.furnace",
    "gt.recipe.microwave",
    "gt.recipe.scanner",
    "gt.recipe.rockbreaker",
    "gt.recipe.byproductlist",
    "gt.recipe.replicator",
    "gt.recipe.fakeAssemblylineProcess",
    "gt.recipe.plasmaarcfurnace",
    "gt.recipe.arcfurnace",
    "gt.recipe.printer",
    "gt.recipe.sifter",
    "gt.recipe.press",
    "gt.recipe.laserengraver",
    "gt.recipe.mixer",
    "gt.recipe.autoclave",
    "gt.recipe.electromagneticseparator",
    "gt.recipe.polarizer",
    "gt.recipe.macerator",
    "gt.recipe.chemicalbath",
    "gt.recipe.fluidcanner",
    "gt.recipe.brewer",
    "gt.recipe.fluidheater",
    "gt.recipe.distillery",
    "gt.recipe.fermenter",
    "gt.recipe.fluidsolidifier",
    "gt.recipe.fluidextractor",
    "gt.recipe.packager",
    "gt.recipe.unpackager",
    "gt.recipe.fusionreactor",
    "gt.recipe.complexfusionreactor",
    "gt.recipe.centrifuge",
    "gt.recipe.electrolyzer",
    "gt.recipe.blastfurnace",
    "gt.recipe.plasmaforge",
    "gt.recipe.transcendentplasmamixerrecipes",
    "gt.recipe.fakespaceprojects",
    "gt.recipe.primitiveblastfurnace",
    "gt.recipe.implosioncompressor",
    "gt.recipe.vacuumfreezer",
    "gt.recipe.chemicalreactor",
    "gt.recipe.largechemicalreactor",
    "gt.recipe.distillationtower",
    "gt.recipe.craker",
    "gt.recipe.pyro",
    "gt.recipe.wiremill",
    "gt.recipe.metalbender",
    "gt.recipe.alloysmelter",
    "gt.recipe.assembler",
    "gt.recipe.circuitassembler",
    "gt.recipe.canner",
    "gt.recipe.cncmachine",
    "gt.recipe.lathe",
    "gt.recipe.cuttingsaw",
    "gt.recipe.slicer",
    "gt.recipe.extruder",
    "gt.recipe.hammer",
    "gt.recipe.uuamplifier",
    "gt.recipe.massfab",
    "gt.recipe.dieselgeneratorfuel",
    "gt.recipe.extremedieselgeneratorfuel",
    "gt.recipe.gasturbinefuel",
    "gt.recipe.thermalgeneratorfuel",
    "gt.recipe.semifluidboilerfuels",
    "gt.recipe.plasmageneratorfuels",
    "gt.recipe.magicfuels",
    "gt.recipe.smallnaquadahreactor",
    "gt.recipe.largenaquadahreactor",
    "gt.recipe.fluidnaquadahreactor",
    "gt.recipe.hugenaquadahreactor",
    "gt.recipe.extrahugenaquadahreactor",
    "gt.recipe.fluidfuelnaquadahreactor",
    "gt.recipe.largeelectrolyzer",
    "gt.recipe.largecentrifuge",
    "gt.recipe.largemixer",
    "gt.recipe.largeboilerfakefuels",
    "gt.recipe.nanoforge",
    "gt.recipe.pcbfactory",
    "gt.recipe.ic2nuke",
    "gtpp.recipe.cokeoven",
    "gtpp.recipe.matterfab2",
    "gtpp.recipe.rocketenginefuel",
    "gtpp.recipe.quantumforcesmelter",
    "gtpp.recipe.geothermalfuel",
    "gtpp.recipe.chemicaldehydrator",
    "gtpp.recipe.vacfurnace",
    "gtpp.recipe.alloyblastsmelter",
    "gtpp.recipe.steamturbinefuel",
    "gtpp.recipe.lftr",
    "gtpp.recipe.nuclearsaltprocessingplant",
    "gtpp.recipe.oremill",
    "gtpp.recipe.fissionfuel",
    "gtpp.recipe.coldtrap",
    "gtpp.recipe.reactorprocessingunit",
    "gtpp.recipe.simplewasher",
    "gtpp.recipe.moleculartransformer",
    "gtpp.recipe.elementaldupe",
    "gtpp.recipe.fluidchemicaleactor",
    "gtpp.recipe.RTGgenerators",
    "gtpp.recipe.thermalgeneratorfuel",
    "gtpp.recipe.solartower",
    "gtpp.recipe.cyclotron",
    "gtpp.recipe.slowfusionreactor",
    "gtpp.recipe.componentassembler",
    "gtpp.recipe.fishpond",
    "gtpp.recipe.spargetower",
    "gtpp.recipe.cryogenicfreezer",
    "gtpp.recipe.multicentrifuge",
    "gtpp.recipe.multielectro",
    "gtpp.recipe.temp4",
    "gtpp.recipe.multimixer",
    "gtpp.recipe.multidehydrator",
    "gtpp.recipe.semifluidgeneratorfuels",
    "gtpp.recipe.flotationcell",
    "gtpp.recipe.treefarm",
    "bw.recipe.biolab",
    "bw.recipe.BacteriaVat",
    "bw.fuels.acidgens",
    "bw.recipe.cal",
    "bw.recipe.radhatch",
    "bw.recipe.htgr",
    "emt.recipe.fusioncrafting",
    "gg.recipe.naquadah_reactor",
    "gg.recipe.naquadah_fuel_refine_factory",
    "gg.recipe.neutron_activator",
    "gg.recipe.extreme_heat_exchanger",
    "gg.recipe.precise_assembler",
    "gg.recipe.componentassemblyline",
    "gt.recipe.fakerockbreaker",
    "gt.recipe.spaceResearch",
    "gt.recipe.spaceAssembler",
    "gt.recipe.spaceMining",
    "gt.recipe.eyeofharmony",
    "gt.recipe.researchStation",
    "gt.recipe.em_scanner",
    "gtnhlanth.recipe.digester",
    "gtnhlanth.recipe.disstank",
    "gt.recipe.electricimplosioncompressor",
]

RECIPE_MAP_NAMES_ZH = {
    "gt.recipe.orewasher": "洗矿机",
    "gt.recipe.thermalcentrifuge": "热力离心机",
    "gt.recipe.compressor": "压缩机",
    "gt.recipe.extractor": "提取机",
    "ic.recipe.recycler": "IC2 回收机",
    "mc.recipe.furnace": "原版熔炉",
    "gt.recipe.microwave": "微波炉",
    "gt.recipe.scanner": "扫描仪",
    "gt.recipe.rockbreaker": "岩浆固化者",
    "gt.recipe.byproductlist": "副产物列表",
    "gt.recipe.replicator": "复制机",
    "gt.recipe.fakeAssemblylineProcess": "模拟装配线流程",
    "gt.recipe.plasmaarcfurnace": "等离子电弧炉",
    "gt.recipe.arcfurnace": "电弧炉",
    "gt.recipe.printer": "打印机",
    "gt.recipe.sifter": "筛选机",
    "gt.recipe.press": "压印机",
    "gt.recipe.laserengraver": "激光蚀刻机",
    "gt.recipe.mixer": "搅拌机",
    "gt.recipe.autoclave": "高压釜",
    "gt.recipe.electromagneticseparator": "电磁离析机",
    "gt.recipe.polarizer": "两极磁化机",
    "gt.recipe.macerator": "研磨机",
    "gt.recipe.chemicalbath": "化学浸洗机",
    "gt.recipe.fluidcanner": "装罐机/流体灌装机",
    "gt.recipe.brewer": "酿造室",
    "gt.recipe.fluidheater": "流体加热器",
    "gt.recipe.distillery": "蒸馏室",
    "gt.recipe.fermenter": "发酵机",
    "gt.recipe.fluidsolidifier": "流体固化器",
    "gt.recipe.fluidextractor": "流体提取机",
    "gt.recipe.packager": "打包机",
    "gt.recipe.unpackager": "解包机",
    "gt.recipe.fusionreactor": "聚变反应堆",
    "gt.recipe.complexfusionreactor": "复杂聚变反应堆",
    "gt.recipe.centrifuge": "离心机",
    "gt.recipe.electrolyzer": "电解机",
    "gt.recipe.blastfurnace": "高炉",
    "gt.recipe.plasmaforge": "超维度等离子锻炉",
    "gt.recipe.transcendentplasmamixerrecipes": "超维度等离子搅拌机",
    "gt.recipe.fakespaceprojects": "模拟太空项目",
    "gt.recipe.primitiveblastfurnace": "砖高炉",
    "gt.recipe.implosioncompressor": "聚爆压缩机",
    "gt.recipe.vacuumfreezer": "真空冷冻机",
    "gt.recipe.chemicalreactor": "化学反应釜",
    "gt.recipe.largechemicalreactor": "大型化学反应釜",
    "gt.recipe.distillationtower": "蒸馏塔",
    "gt.recipe.craker": "石油裂化机",
    "gt.recipe.pyro": "热解炉",
    "gt.recipe.wiremill": "线材轧机",
    "gt.recipe.metalbender": "卷板机",
    "gt.recipe.alloysmelter": "合金炉",
    "gt.recipe.assembler": "组装机",
    "gt.recipe.circuitassembler": "电路组装机",
    "gt.recipe.canner": "装罐机",
    "gt.recipe.cncmachine": "CNC 加工机",
    "gt.recipe.lathe": "车床",
    "gt.recipe.cuttingsaw": "板材切割机",
    "gt.recipe.slicer": "食材切片机",
    "gt.recipe.extruder": "压模机",
    "gt.recipe.hammer": "锻造锤",
    "gt.recipe.uuamplifier": "UU 放大器",
    "gt.recipe.massfab": "质量发生器",
    "gt.recipe.dieselgeneratorfuel": "柴油发电燃料",
    "gt.recipe.extremedieselgeneratorfuel": "极限柴油发电燃料",
    "gt.recipe.gasturbinefuel": "燃气轮机燃料",
    "gt.recipe.thermalgeneratorfuel": "热力发电燃料",
    "gt.recipe.semifluidboilerfuels": "半流体锅炉燃料",
    "gt.recipe.plasmageneratorfuels": "等离子发电燃料",
    "gt.recipe.magicfuels": "魔法燃料",
    "gt.recipe.smallnaquadahreactor": "小型硅岩反应堆",
    "gt.recipe.largenaquadahreactor": "大型硅岩反应堆",
    "gt.recipe.fluidnaquadahreactor": "流体硅岩反应堆",
    "gt.recipe.hugenaquadahreactor": "巨型硅岩反应堆",
    "gt.recipe.extrahugenaquadahreactor": "超巨型硅岩反应堆",
    "gt.recipe.fluidfuelnaquadahreactor": "流体燃料硅岩反应堆",
    "gt.recipe.largeelectrolyzer": "大型电解机",
    "gt.recipe.largecentrifuge": "大型离心机",
    "gt.recipe.largemixer": "大型搅拌机",
    "gt.recipe.largeboilerfakefuels": "大型锅炉模拟燃料",
    "gt.recipe.nanoforge": "纳米锻炉",
    "gt.recipe.pcbfactory": "PCB工厂",
    "gt.recipe.ic2nuke": "IC2 核弹",
    "gtpp.recipe.cokeoven": "工业焦炉",
    "gtpp.recipe.matterfab2": "GT++ 物质发生器",
    "gtpp.recipe.rocketenginefuel": "火箭引擎 F-1A 燃料",
    "gtpp.recipe.quantumforcesmelter": "GT++ 量子力熔炉",
    "gtpp.recipe.geothermalfuel": "地热引擎燃料",
    "gtpp.recipe.chemicaldehydrator": "化学脱水机",
    "gtpp.recipe.vacfurnace": "真空干燥炉",
    "gtpp.recipe.alloyblastsmelter": "合金高炉",
    "gtpp.recipe.steamturbinefuel": "GT++ 蒸汽轮机燃料",
    "gtpp.recipe.lftr": "GT++ 液态氟钍反应堆",
    "gtpp.recipe.nuclearsaltprocessingplant": "GT++ 核盐处理厂",
    "gtpp.recipe.oremill": "GT++ 矿石研磨机",
    "gtpp.recipe.fissionfuel": "GT++ 裂变燃料",
    "gtpp.recipe.coldtrap": "GT++ 冷阱",
    "gtpp.recipe.reactorprocessingunit": "GT++ 反应堆处理单元",
    "gtpp.recipe.simplewasher": "GT++ 简易洗矿机",
    "gtpp.recipe.moleculartransformer": "GT++ 分子转换机",
    "gtpp.recipe.elementaldupe": "GT++ 元素复制",
    "gtpp.recipe.fluidchemicaleactor": "GT++ 流体化学反应釜",
    "gtpp.recipe.RTGgenerators": "GT++ RTG 发电机",
    "gtpp.recipe.thermalgeneratorfuel": "GT++ 热力发电燃料",
    "gtpp.recipe.solartower": "GT++ 太阳能塔",
    "gtpp.recipe.cyclotron": "COMET-紧凑式回旋加速器",
    "gtpp.recipe.slowfusionreactor": "GT++ 慢速聚变反应堆",
    "gtpp.recipe.componentassembler": "部件装配线",
    "gtpp.recipe.fishpond": "GT++ 鱼塘",
    "gtpp.recipe.spargetower": "GT++ 鼓泡塔",
    "gtpp.recipe.cryogenicfreezer": "凛冰冷冻机",
    "gtpp.recipe.multicentrifuge": "GT++ 多重离心机",
    "gtpp.recipe.multielectro": "GT++ 多重电解机",
    "gtpp.recipe.temp4": "GT++ 临时配方 4",
    "gtpp.recipe.multimixer": "GT++ 多重搅拌机",
    "gtpp.recipe.multidehydrator": "GT++ 多重脱水机",
    "gtpp.recipe.semifluidgeneratorfuels": "GT++ 半流体发电燃料",
    "gtpp.recipe.flotationcell": "工业浮选机",
    "gtpp.recipe.treefarm": "GT++ 林场",
    "bw.recipe.biolab": "BartWorks 生物实验室",
    "bw.recipe.BacteriaVat": "BartWorks 细菌培养罐",
    "bw.fuels.acidgens": "BartWorks 酸性发电燃料",
    "bw.recipe.cal": "BartWorks CAL 配方",
    "bw.recipe.radhatch": "BartWorks 辐射仓",
    "bw.recipe.htgr": "BartWorks 高温气冷反应堆",
    "emt.recipe.fusioncrafting": "EMT 聚变合成",
    "gg.recipe.naquadah_reactor": "GG 硅岩反应堆",
    "gg.recipe.naquadah_fuel_refine_factory": "GG 硅岩燃料精炼厂",
    "gg.recipe.neutron_activator": "GG 中子活化器",
    "gg.recipe.extreme_heat_exchanger": "GG 极限热交换器",
    "gg.recipe.precise_assembler": "GG 精密组装机",
    "gg.recipe.componentassemblyline": "GG 部件装配线",
    "gt.recipe.fakerockbreaker": "模拟碎石机",
    "gt.recipe.spaceResearch": "太空研究",
    "gt.recipe.spaceAssembler": "太空组装机",
    "gt.recipe.spaceMining": "太空采矿",
    "gt.recipe.eyeofharmony": "鸿蒙之眼",
    "gt.recipe.researchStation": "研究站",
    "gt.recipe.em_scanner": "EM 扫描仪",
    "gtnhlanth.recipe.digester": "GTNH Lanthanides 消化器",
    "gtnhlanth.recipe.disstank": "GTNH Lanthanides 溶解罐",
    "gt.recipe.electricimplosioncompressor": "电动聚爆压缩机",
}


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
        "GT RA2",
        16,
        9,
        4,
        4,
        "generic_gt",
        "gt.recipe.assembler",
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


LEGACY_GT_TEMPLATE_RECIPE_MAPS: Dict[str, str] = {
    "assembler_like": "gt.recipe.assembler",
    "cutter_like": "gt.recipe.cuttingsaw",
    "macerator_like": "gt.recipe.macerator",
    "mixer_like": "gt.recipe.mixer",
    "chemical_reactor_like": "gt.recipe.chemicalreactor",
    "blast_furnace_like": "gt.recipe.blastfurnace",
}


def template_options() -> List[MachineTemplate]:
    return list(TEMPLATES.values())


def normalize_template_id(template_id: str) -> str:
    value = template_id.strip()
    if value in TEMPLATES:
        return value
    if value in LEGACY_GT_TEMPLATE_RECIPE_MAPS:
        return "generic_gt_machine"
    return "generic_gt_machine"


def default_recipe_map_for_template(template_id: str) -> str:
    value = template_id.strip()
    if value in LEGACY_GT_TEMPLATE_RECIPE_MAPS:
        return LEGACY_GT_TEMPLATE_RECIPE_MAPS[value]
    template = TEMPLATES.get(normalize_template_id(value))
    if template is None:
        return "gt.recipe.assembler"
    return template.recipe_map or "gt.recipe.assembler"


def template_label(template_id: str) -> str:
    template = TEMPLATES[normalize_template_id(template_id)]
    return template.display_name


def template_label_options() -> List[str]:
    return [template.display_name for template in template_options()]


def template_id_from_label(label: str) -> str:
    value = label.strip()
    for template in template_options():
        if template.display_name == value:
            return template.template_id
    return normalize_template_id(value)


def recipe_map_options() -> List[str]:
    return list(RECIPE_MAPS)


def recipe_map_display_name(recipe_map: str) -> str:
    return RECIPE_MAP_NAMES_ZH.get(recipe_map, "未翻译配方映射")


def recipe_map_label(recipe_map: str) -> str:
    return f"{recipe_map_display_name(recipe_map)} ({recipe_map})"


def recipe_map_label_options() -> List[str]:
    return [recipe_map_label(recipe_map) for recipe_map in RECIPE_MAPS]


def recipe_map_id_from_label(label: str) -> str:
    value = label.strip()
    if value.endswith(")") and "(" in value:
        return value[value.rfind("(") + 1 : -1]
    return value
