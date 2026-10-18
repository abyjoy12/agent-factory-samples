import copy
import json
import unittest
from pathlib import Path

from scripts.prepare_lab_workflows import LAB_MODEL, graph_data, layout_graph, node_kind


def node(key, kind="agentStep"):
    return {"id": key, "type": "flowGenericNode", "position": {"x": 0, "y": 0},
            "width": 340, "measured": {"width": 340, "height": 100},
            "data": {"type": kind, "template": {}}}


class LabLayoutTests(unittest.TestCase):
    def test_parallel_cards_use_measured_bounds_and_keep_wiring(self):
        graph = {"nodes": [node("input", "chatInputComponent"), node("tools"), node("a"), node("b"), node("out")],
                 "edges": [{"source": "input", "target": "a", "sourceHandle": "message", "targetHandle": "prompt"},
                           {"source": "tools", "target": "a"}, {"source": "tools", "target": "b"},
                           {"source": "a", "target": "out"}, {"source": "b", "target": "out"}],
                 "_workflowMetadata": {"version": 5}}
        before = copy.deepcopy(graph)
        sizes = {"a": {"width": 620, "height": 1600}, "b": {"width": 280, "height": 800}}
        result = layout_graph(graph, sizes)
        self.assertEqual(graph, before)
        self.assertEqual(result["edges"], before["edges"])
        self.assertEqual(result["_workflowMetadata"], before["_workflowMetadata"])
        by_id = {n["id"]: n for n in result["nodes"]}
        for edge in result["edges"]:
            self.assertGreater(by_id[edge["target"]]["position"]["x"], by_id[edge["source"]]["position"]["x"])
        self.assertGreaterEqual(by_id["b"]["position"]["y"], by_id["a"]["position"]["y"] + 1700)
        self.assertGreaterEqual(by_id["out"]["position"]["x"], by_id["a"]["position"]["x"] + 720)
        for item in result["nodes"]:
            if item["type"] != "noteNode":
                self.assertNotIn("width", item)
                self.assertNotIn("measured", item)
        self.assertEqual(layout_graph(result, sizes), result)

    def test_large_existing_notes_are_preserved_above_the_reading_guide(self):
        note = {"id": "my-note", "type": "noteNode", "width": 800, "height": 900,
                "position": {"x": 0, "y": 0}, "data": {"noteDetails": {"text": "Keep this"}}}
        result = layout_graph({"nodes": [node("a"), note, dict(note, id="second-note")], "edges": []})
        first, second = result["nodes"][1:3]
        self.assertLess(first["position"]["y"] + first["height"], 0)
        self.assertGreater(second["position"]["x"], first["width"])
        self.assertEqual(first["data"], note["data"])

    def test_invalid_wiring_fails_without_mutation(self):
        for edges in ([{"source": "a", "target": "missing"}], [{"source": "a", "target": "a"}]):
            graph = {"nodes": [node("a")], "edges": edges}
            before = copy.deepcopy(graph)
            with self.assertRaises(ValueError):
                layout_graph(graph)
            self.assertEqual(before, graph)

    def test_catalog_uses_native_notes_lab_model_and_detailed_descriptions(self):
        root = Path(__file__).resolve().parents[1]
        paths = sorted((root / "agents").glob("*/*/workflow.json"))
        self.assertEqual(28, len(paths))
        agent_count = 0
        for path in paths:
            graph = graph_data(json.loads(path.read_text()))
            by_id = {n["id"]: n for n in graph["nodes"]}
            self.assertTrue(any(n["type"] == "noteNode" for n in graph["nodes"]), path)
            for edge in graph["edges"]:
                self.assertGreater(by_id[edge["target"]]["position"]["x"], by_id[edge["source"]]["position"]["x"], path)
            for item in graph["nodes"]:
                if item["type"] == "flowGenericNode":
                    self.assertNotIn("width", item, path)
                if node_kind(item) == "agentStep":
                    agent_count += 1
                    fields = item["data"]["template"]
                    self.assertEqual(LAB_MODEL, fields["llmToUse"]["value"], path)
                    description = fields["agent_description"]
                    self.assertEqual("textArea", description["componentType"], path)
                    self.assertIn("Sample questions:", description["value"], path)
                    self.assertGreaterEqual(description["value"].count("\n- "), 2, path)
                    self.assertGreater(len(description["value"]), 350, path)
        self.assertEqual(31, agent_count)
