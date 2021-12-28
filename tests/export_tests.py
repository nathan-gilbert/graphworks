import json
import shutil
import tempfile
import unittest
from os import path

from graphworks.export.graphviz_utils import save_to_dot
from graphworks.export.json_utils import save_to_json
from graphworks.graph import Graph


class ExportTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_save_to_json(self):
        answer = "{\"label\": \"my graph\", \"directed\": false," \
                 " \"graph\": {\"A\": [\"B\"], \"B\": []}}"
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        save_to_json(graph, self.test_dir)

        outfile = path.join(self.test_dir, graph.get_label() + ".json")
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
        json_graph = {"label": "my graph", "graph": {"A": ["B"], "B": []}}
        graph = Graph(input_graph=json.dumps(json_graph))
        save_to_dot(graph, self.test_dir)

        outfile = path.join(self.test_dir, graph.get_label() + ".gv")
        with open(outfile) as dot_file:
            dot_lines = "".join(dot_file.readlines())
        self.assertEqual(dot_lines, answer)


if __name__ == '__main__':
    unittest.main()
