import os
import sys
import tempfile
import unittest

sys.path.append(os.path.abspath('../src'))
from src.communication import plot_ACPL_graph


class TestPlotACPLGraph(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to hold the plot
        self.test_dir = tempfile.mkdtemp()

    def test_plot_ACPL_graph_creates_file(self):
        # Modify get_unity_persistance_path function or use mock here to return the test directory path
        acpl_values = [0.1, -0.2, 0.3, -0.4, 0.5]  # Example ACPL values

        # Call the function under test
        plot = plot_ACPL_graph(acpl_values)

if __name__ == '__main__':
    unittest.main()
