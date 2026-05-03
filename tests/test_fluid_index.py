import unittest
from pathlib import Path

from core.fluid_index import FluidIndexStore, default_fluid_index_path


SAMPLE_INDEX = {
    "schemaVersion": 1,
    "generatedAt": "2026-05-03T09:00:53+0800",
    "minecraftVersion": "1.7.10",
    "language": "zh_CN",
    "entryCount": 2,
    "entries": [
        {
            "fluidName": "water",
            "ctExpression": "<liquid:water>",
            "chineseName": "水",
            "englishName": "Water",
            "unlocalizedName": "fluid.tile.water",
            "temperature": 300,
            "density": 1000,
            "viscosity": 1000,
            "gaseous": False,
            "guid": "water",
        },
        {
            "fluidName": "liquid helium",
            "ctExpression": "<liquid:liquid helium>",
            "chineseName": "液氦",
            "englishName": "Liquid Helium",
            "unlocalizedName": "fluid.liquid helium",
            "temperature": 300,
            "density": 1000,
            "viscosity": 1000,
            "gaseous": False,
            "guid": "liquid helium",
        },
    ],
}


class FluidIndexStoreTest(unittest.TestCase):
    def test_loads_entries_and_metadata(self):
        fixture = Path(__file__).parent / "fixtures" / "fluid_index.json"
        store = FluidIndexStore.load(fixture)
        self.assertEqual(3, store.entry_count)
        self.assertEqual("zh_CN", store.language)
        self.assertEqual("<liquid:water>", store.entries[0].ct_expression)

    def test_searches_names_ids_and_ct_expressions(self):
        store = FluidIndexStore.from_data(SAMPLE_INDEX)
        self.assertEqual(["water"], [e.fluid_name for e in store.search("水")])
        self.assertEqual(["liquid helium"], [e.fluid_name for e in store.search("helium")])
        self.assertEqual(["liquid helium"], [e.fluid_name for e in store.search("<liquid:liquid")])

    def test_search_limits_results(self):
        store = FluidIndexStore.from_data(SAMPLE_INDEX)
        self.assertEqual(1, len(store.search("", limit=1)))

    def test_default_fluid_index_path_sits_next_to_item_index(self):
        self.assertEqual(
            Path("D:/Code/gtnh_item_doc_exporter/fluid_index.json"),
            default_fluid_index_path("D:/Code/gtnh_item_doc_exporter/item_index.json"),
        )


if __name__ == "__main__":
    unittest.main()
