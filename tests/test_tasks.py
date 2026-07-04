import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from factory_public_test import Task, summarize_tasks


class SummarizeTasksTest(unittest.TestCase):
    def test_summarizes_status_counts_and_points(self):
        tasks = [
            Task("Write brief", "todo", 2),
            Task("Build prototype", "doing", 3),
            Task("Ship demo", "done", 5),
        ]

        self.assertEqual(
            summarize_tasks(tasks),
            {"todo": 1, "doing": 1, "done": 1, "points": 10},
        )

    def test_empty_task_list_has_zero_counts(self):
        self.assertEqual(
            summarize_tasks([]),
            {"todo": 0, "doing": 0, "done": 0, "points": 0},
        )

    def test_rejects_unknown_status(self):
        with self.assertRaisesRegex(ValueError, "Unsupported task status"):
            summarize_tasks([Task("Decide next step", "unknown")])


if __name__ == "__main__":
    unittest.main()

