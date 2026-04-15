"""Harness runner - minimal runnable version."""

import asyncio
import json
import shlex
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    name: str
    command: str
    status: TaskStatus = TaskStatus.PENDING
    output: str = ""
    error: str = ""


class HarnessRunner:
    """Harness task runner."""

    def __init__(self, plans_dir: str = ".harness/plans") -> None:
        self.plans_dir = Path(plans_dir)
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    async def run_plan(self, plan_path: str) -> dict[str, Any]:
        """Execute a plan."""
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)

        results: list[dict[str, Any]] = []
        for task_data in plan.get("tasks", []):
            task = Task(
                id=task_data["id"],
                name=task_data["name"],
                command=task_data["command"],
            )
            result = await self._execute_task(task)
            results.append(result)

            if result["status"] == "failed" and plan.get("stop_on_error", True):
                break

        return {
            "plan_id": plan["id"],
            "status": "success" if all(r["status"] == "success" for r in results) else "failed",
            "tasks": results,
        }

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING

        try:
            proc = await self._spawn_subprocess(task.command)
            stdout, stderr = await proc.communicate()
            task.output = stdout.decode("utf-8", errors="replace").strip()
            task.error = stderr.decode("utf-8", errors="replace").strip()
            task.status = TaskStatus.SUCCESS if proc.returncode == 0 else TaskStatus.FAILED
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)

        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "output": task.output,
            "error": task.error,
        }

    async def _spawn_subprocess(self, command: str) -> asyncio.subprocess.Process:
        """优先尝试无 shell 执行，失败时回退到 shell。"""
        try:
            cmd_parts = shlex.split(command)
        except ValueError:
            cmd_parts = []
        if cmd_parts:
            try:
                return await asyncio.create_subprocess_exec(
                    cmd_parts[0],
                    *cmd_parts[1:],
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            except (FileNotFoundError, OSError):
                pass
        return await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )


if __name__ == "__main__":
    runner = HarnessRunner()

    sample_plan = {
        "id": "plan_001",
        "name": "Hello Harness",
        "tasks": [
            {"id": "task_1", "name": "Say Hello", "command": "echo 'Hello'"},
            {"id": "task_2", "name": "Say World", "command": "echo 'World'"},
        ],
    }

    plan_path = ".harness/plans/plan_001.json"
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(sample_plan, f, indent=2)

    result = asyncio.run(runner.run_plan(plan_path))
    print(json.dumps(result, indent=2))
