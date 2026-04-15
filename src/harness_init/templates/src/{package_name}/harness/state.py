"""Simple JSON state manager."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class StateManager:
    """Manage JSON-based state persistence."""

    def __init__(self, state_path: str = ".harness/state/state.json") -> None:
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = {}
        self.load()

    def load(self) -> dict[str, Any]:
        """Load state from disk."""
        if self.state_path.exists():
            with open(self.state_path, encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {}
        return self._data

    def save(self) -> None:
        """原子方式保存状态到磁盘。"""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path_str = tempfile.mkstemp(dir=self.state_path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            os.replace(tmp_path_str, self.state_path)
        except Exception:
            try:
                os.unlink(tmp_path_str)
            except OSError:
                pass
            raise

    def get(self, key: str, default: Any | None = None) -> Any:
        """Get a value by key."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value by key and persist."""
        self._data[key] = value
        self.save()
