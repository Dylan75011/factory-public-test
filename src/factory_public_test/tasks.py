from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Task:
    title: str
    status: str
    points: int = 1


def summarize_tasks(tasks: Iterable[Task]) -> dict[str, int]:
    summary = {"todo": 0, "doing": 0, "done": 0, "points": 0}

    for task in tasks:
        if task.status not in summary:
            raise ValueError(f"Unsupported task status: {task.status}")
        summary[task.status] += 1
        summary["points"] += task.points

    return summary

