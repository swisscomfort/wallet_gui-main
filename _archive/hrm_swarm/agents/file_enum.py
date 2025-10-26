"""Agent that enumerates files under a root."""

from __future__ import annotations

import os
import re
import time

from .base import Agent, Result, Task


class FileEnumAgent(Agent):
    NAME = "file_enum"

    def run(self, task: Task) -> Result:
        t0 = time.time()
        root = task.payload.get("root")
        if not root:
            return Result(kind=self.NAME, ok=False, data={}, took_s=time.time() - t0)

        max_mb = int(task.payload.get("max_mb", 256))
        exclude = task.payload.get("exclude")
        size_limit = max_mb * 1024 * 1024
        paths: list[str] = []

        for dirpath, dirnames, filenames in os.walk(root):
            if self.cfg.get("prune_dirs"):
                dirnames[:] = [d for d in dirnames if d not in self.cfg["prune_dirs"]]
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                try:
                    if os.path.getsize(path) <= size_limit:
                        if not exclude or not re.search(str(exclude), path, flags=re.I):
                            paths.append(path)
                except Exception:
                    continue

        return Result(kind=self.NAME, ok=True, data={"paths": paths}, took_s=time.time() - t0)

