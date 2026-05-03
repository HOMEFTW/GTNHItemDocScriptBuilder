import unittest
from pathlib import Path

from core.ore_dictionary_index import OreDictionaryIndexStore, default_ore_dictionary_index_path


SAMPLE_INDEX = {
    "schemaVersion": 1,
    "generatedAt": "2026-05-03T10:23:23+0800",
    "minecraftVersion": "1.7.10",
    "language": "zh_CN",
    "entryCount": 2,
    "entries": [
        {
            "oreName": "stickWood",
            "ctExpression": "<ore:stickWood>",
            "itemCount": 2,
            "items": ["<minecraft:stick>", "<BiomesOPlenty:bamboo>"],
            "guid": "stickWood",
        },
        {
            "oreName": "dustClay",
            "ctExpression": "<ore:dustClay>",
            "itemCount": 1,
            "items": ["<gregtech:gt.metaitem.01:2805>"],
            "guid": "dustClay",
        },
    ],
}


class OreDictionaryIndexStoreTest(unittest.TestCase):
    def test_loads_entries_and_metadata(self):
        store = OreDictionaryIndexStore.from_data(SAMPLE_INDEX)

        self.assertEqual(2, store.entry_count)
        self.assertEqual("zh_CN", store.language)
        self.assertEqual("<ore:stickWood>", store.entries[0].ct_expression)
        self.assertEqual(2, store.entries[0].item_count)

    def test_searches_names_ct_expressions_and_items(self):
        store = OreDictionaryIndexStore.from_data(SAMPLE_INDEX)

        self.assertEqual(["stickWood"], [entry.ore_name for entry in store.search("stick")])
        self.assertEqual(["dustClay"], [entry.ore_name for entry in store.search("<ore:dust")])
        self.assertEqual(["dustClay"], [entry.ore_name for entry in store.search("gt.metaitem.01:2805")])

    def test_search_limits_results(self):
        store = OreDictionaryIndexStore.from_data(SAMPLE_INDEX)

        self.assertEqual(1, len(store.search("", limit=1)))

    def test_default_ore_dictionary_index_path_sits_next_to_item_index(self):
        self.assertEqual(
            Path("D:/Code/gtnh_item_doc_exporter/ore_dictionary_index.json"),
            default_ore_dictionary_index_path("D:/Code/gtnh_item_doc_exporter/item_index.json"),
        )


if __name__ == "__main__":
    unittest.main()
