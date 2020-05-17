import json
import shutil
import tempfile
import unittest
from os import path
from graphworks.graph import Graph
from graphworks.export.json import save_to_json
from graphworks.export.graphviz import save_to_dot


class ExportTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_save_to_json(self):
        answer = "{\"label\": \"my graph\", \"directed\": false, \"edges\": {\"A\": [\"B\"], \"B\": []}}"
        json_graph = {"label": "my graph", "edges": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        outfile = path.join(self.test_dir, graph.get_label())
        save_to_json(graph, outfile)

        with open(outfile) as dot_file:
            dot_lines = "".join(dot_file.readlines())
        self.assertEqual(dot_lines, answer)

    def test_save_to_graphviz(self):
        answer = """// my graph
graph {
	A [label=A]
	A -- B
	B [label=B]
}
"""

        json_graph = {"label": "my graph", "edges": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        outfile = path.join(self.test_dir, graph.get_label())
        save_to_dot(graph, outfile)

        with open(outfile + ".gv") as dot_file:
            dot_lines = "".join(dot_file.readlines())
        self.assertEqual(dot_lines, answer)


if __name__ == '__main__':
    unittest.main()
