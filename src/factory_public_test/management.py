from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Iterable


PROJECT_STATUSES = {"planned", "active", "paused", "done"}
TASK_STATUSES = {"todo", "doing", "blocked", "done"}
PRIORITIES = {"low", "medium", "high"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Project:
    id: int
    name: str
    owner: str
    status: str = "planned"
    description: str = ""
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class WorkItem:
    id: int
    project_id: int
    title: str
    assignee: str = ""
    status: str = "todo"
    priority: str = "medium"
    points: int = 1
    due_date: str = ""
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ManagementStore:
    """In-memory store for the demo management system."""

    def __init__(
        self,
        projects: Iterable[Project] | None = None,
        work_items: Iterable[WorkItem] | None = None,
    ) -> None:
        self._projects = {project.id: project for project in projects or []}
        self._work_items = {item.id: item for item in work_items or []}
        self._project_ids = count(self._next_id(self._projects))
        self._work_item_ids = count(self._next_id(self._work_items))

    @classmethod
    def seeded(cls) -> "ManagementStore":
        store = cls()
        launch = store.create_project(
            name="Factory trial workspace",
            owner="Dylan",
            status="active",
            description="Prepare a lightweight workspace for invited users.",
        )
        docs = store.create_project(
            name="Product docs refresh",
            owner="Alex",
            status="planned",
            description="Clean up onboarding notes before the next demo.",
        )
        store.create_work_item(
            project_id=launch.id,
            title="Invite first testers",
            assignee="Dylan",
            status="doing",
            priority="high",
            points=3,
        )
        store.create_work_item(
            project_id=launch.id,
            title="Capture feedback themes",
            assignee="Mia",
            status="todo",
            priority="medium",
            points=2,
        )
        store.create_work_item(
            project_id=docs.id,
            title="Review setup guide",
            assignee="Alex",
            status="blocked",
            priority="high",
            points=5,
        )
        store.create_work_item(
            project_id=docs.id,
            title="Publish quick-start checklist",
            assignee="Lee",
            status="done",
            priority="low",
            points=1,
        )
        return store

    def list_projects(self) -> list[Project]:
        return sorted(self._projects.values(), key=lambda project: project.id)

    def list_work_items(self, project_id: int | None = None) -> list[WorkItem]:
        items = self._work_items.values()
        if project_id is not None:
            self._require_project(project_id)
            items = [item for item in items if item.project_id == project_id]
        return sorted(items, key=lambda item: item.id)

    def create_project(
        self,
        name: str,
        owner: str,
        status: str = "planned",
        description: str = "",
    ) -> Project:
        name = self._require_text(name, "Project name")
        owner = self._require_text(owner, "Project owner")
        self._require_choice(status, PROJECT_STATUSES, "Project status")
        project = Project(
            id=next(self._project_ids),
            name=name,
            owner=owner,
            status=status,
            description=description.strip(),
        )
        self._projects[project.id] = project
        return project

    def update_project_status(self, project_id: int, status: str) -> Project:
        project = self._require_project(project_id)
        self._require_choice(status, PROJECT_STATUSES, "Project status")
        project.status = status
        return project

    def create_work_item(
        self,
        project_id: int,
        title: str,
        assignee: str = "",
        status: str = "todo",
        priority: str = "medium",
        points: int = 1,
        due_date: str = "",
    ) -> WorkItem:
        self._require_project(project_id)
        title = self._require_text(title, "Task title")
        self._require_choice(status, TASK_STATUSES, "Task status")
        self._require_choice(priority, PRIORITIES, "Task priority")
        points = self._require_points(points)
        item = WorkItem(
            id=next(self._work_item_ids),
            project_id=project_id,
            title=title,
            assignee=assignee.strip(),
            status=status,
            priority=priority,
            points=points,
            due_date=due_date.strip(),
        )
        self._work_items[item.id] = item
        return item

    def update_work_item(self, item_id: int, **changes: object) -> WorkItem:
        item = self._require_work_item(item_id)

        if "title" in changes:
            item.title = self._require_text(str(changes["title"]), "Task title")
        if "assignee" in changes:
            item.assignee = str(changes["assignee"]).strip()
        if "status" in changes:
            status = str(changes["status"])
            self._require_choice(status, TASK_STATUSES, "Task status")
            item.status = status
        if "priority" in changes:
            priority = str(changes["priority"])
            self._require_choice(priority, PRIORITIES, "Task priority")
            item.priority = priority
        if "points" in changes:
            item.points = self._require_points(changes["points"])
        if "due_date" in changes:
            item.due_date = str(changes["due_date"]).strip()

        return item

    def dashboard(self) -> dict[str, object]:
        projects = self.list_projects()
        work_items = self.list_work_items()
        task_counts = {status: 0 for status in sorted(TASK_STATUSES)}
        priority_counts = {priority: 0 for priority in sorted(PRIORITIES)}
        total_points = 0

        for item in work_items:
            task_counts[item.status] += 1
            priority_counts[item.priority] += 1
            total_points += item.points

        project_cards = []
        for project in projects:
            project_items = [
                item for item in work_items if item.project_id == project.id
            ]
            project_cards.append(
                {
                    **project.to_dict(),
                    "task_count": len(project_items),
                    "open_count": sum(
                        1 for item in project_items if item.status != "done"
                    ),
                    "blocked_count": sum(
                        1 for item in project_items if item.status == "blocked"
                    ),
                    "points": sum(item.points for item in project_items),
                }
            )

        return {
            "totals": {
                "projects": len(projects),
                "tasks": len(work_items),
                "open_tasks": sum(1 for item in work_items if item.status != "done"),
                "blocked_tasks": task_counts["blocked"],
                "points": total_points,
            },
            "task_counts": task_counts,
            "priority_counts": priority_counts,
            "projects": project_cards,
            "work_items": [item.to_dict() for item in work_items],
        }

    def _require_project(self, project_id: int) -> Project:
        try:
            return self._projects[int(project_id)]
        except (KeyError, ValueError) as exc:
            raise KeyError(f"Project not found: {project_id}") from exc

    def _require_work_item(self, item_id: int) -> WorkItem:
        try:
            return self._work_items[int(item_id)]
        except (KeyError, ValueError) as exc:
            raise KeyError(f"Task not found: {item_id}") from exc

    @staticmethod
    def _next_id(items: dict[int, object]) -> int:
        return max(items.keys(), default=0) + 1

    @staticmethod
    def _require_text(value: str, label: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"{label} is required")
        return value

    @staticmethod
    def _require_choice(value: str, choices: set[str], label: str) -> None:
        if value not in choices:
            allowed = ", ".join(sorted(choices))
            raise ValueError(f"{label} must be one of: {allowed}")

    @staticmethod
    def _require_points(value: object) -> int:
        try:
            points = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Task points must be a positive integer") from exc
        if points < 1:
            raise ValueError("Task points must be a positive integer")
        return points
