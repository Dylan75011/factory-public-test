import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from factory_public_test import ManagementStore


class ManagementStoreTest(unittest.TestCase):
    def test_seeded_dashboard_has_projects_tasks_and_totals(self):
        dashboard = ManagementStore.seeded().dashboard()

        self.assertEqual(dashboard["totals"]["projects"], 2)
        self.assertEqual(dashboard["totals"]["tasks"], 4)
        self.assertEqual(dashboard["totals"]["blocked_tasks"], 1)
        self.assertEqual(dashboard["task_counts"]["done"], 1)

    def test_creates_project_and_task(self):
        store = ManagementStore()
        project = store.create_project("Support desk", "Mia", status="active")
        item = store.create_work_item(
            project.id,
            "Triage beta feedback",
            assignee="Lee",
            priority="high",
            points=3,
        )

        self.assertEqual(project.id, 1)
        self.assertEqual(item.project_id, project.id)
        self.assertEqual(store.dashboard()["totals"]["points"], 3)

    def test_updates_task_status(self):
        store = ManagementStore()
        project = store.create_project("Ops", "Dylan")
        item = store.create_work_item(project.id, "Prepare demo")

        updated = store.update_work_item(item.id, status="done")

        self.assertEqual(updated.status, "done")
        self.assertEqual(store.dashboard()["totals"]["open_tasks"], 0)

    def test_rejects_invalid_status(self):
        store = ManagementStore()
        project = store.create_project("Ops", "Dylan")

        with self.assertRaisesRegex(ValueError, "Task status"):
            store.create_work_item(project.id, "Prepare demo", status="waiting")

    def test_rejects_missing_project(self):
        store = ManagementStore()

        with self.assertRaisesRegex(KeyError, "Project not found"):
            store.create_work_item(404, "Prepare demo")


if __name__ == "__main__":
    unittest.main()

