import unittest
from pathlib import Path

from core.item_index import ItemIndexStore


SAMPLE_INDEX = {
    "schemaVersion": 1,
    "generatedAt": "2026-05-02T21:46:40+0800",
    "minecraftVersion": "1.7.10",
    "language": "zh_CN",
    "entryCount": 3,
    "entries": [
        {
            "modId": "minecraft",
            "registryId": "minecraft:iron_ingot",
            "meta": 0,
            "ctExpression": "<minecraft:iron_ingot>",
            "chineseName": "铁锭",
            "englishName": "Iron Ingot",
            "unlocalizedName": "item.ingotIron",
            "isBlock": False,
            "guid": "minecraft:iron_ingot:0",
            "nbtSummary": "",
        },
        {
            "modId": "minecraft",
            "registryId": "minecraft:glass",
            "meta": 0,
            "ctExpression": "<minecraft:glass>",
            "chineseName": "玻璃",
            "englishName": "Glass",
            "unlocalizedName": "tile.glass",
            "isBlock": True,
            "guid": "minecraft:glass:0",
            "nbtSummary": "",
        },
        {
            "modId": "gregtech",
            "registryId": "gregtech:gt.metaitem.01",
            "meta": 32700,
            "ctExpression": "<gregtech:gt.metaitem.01:32700>",
            "chineseName": "集成电路",
            "englishName": "Integrated Circuit",
            "unlocalizedName": "item.gt.integrated_circuit",
            "isBlock": False,
            "guid": "gregtech:gt.metaitem.01:32700",
            "nbtSummary": "",
        },
    ],
}


class ItemIndexStoreTest(unittest.TestCase):
    def test_loads_entries_and_metadata(self):
        fixture = Path(__file__).parent / "fixtures" / "item_index.json"
        store = ItemIndexStore.load(fixture)
        self.assertEqual(3, store.entry_count)
        self.assertEqual("zh_CN", store.language)
        self.assertEqual("<minecraft:iron_ingot>", store.entries[0].ct_expression)

    def test_searches_names_ids_and_ct_expressions(self):
        store = ItemIndexStore.from_data(SAMPLE_INDEX)
        self.assertEqual(["minecraft:iron_ingot"], [e.registry_id for e in store.search("铁")])
        self.assertEqual(["minecraft:glass"], [e.registry_id for e in store.search("glass")])
        self.assertEqual(["gregtech:gt.metaitem.01"], [e.registry_id for e in store.search("32700")])

    def test_search_limits_results(self):
        store = ItemIndexStore.from_data(SAMPLE_INDEX)
        self.assertEqual(2, len(store.search("", limit=2)))


if __name__ == "__main__":
    unittest.main()
