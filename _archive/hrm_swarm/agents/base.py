"""Common agent structures."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Task:
    kind: str
    payload: Dict[str, object]
    priority: int = 0


@dataclass
class Result:
    kind: str
    ok: bool
    data: Dict[str, object]
    took_s: float
    meta: Dict[str, object] = field(default_factory=dict)


class Agent:
    NAME = "base"

    def __init__(self, cfg: Optional[Dict[str, object]] = None):
        self.cfg = cfg or {}

    def run(self, task: Task) -> Result:
        t0 = time.time()
        return Result(kind=self.NAME, ok=False, data={}, took_s=time.time() - t0)

    def shell(self, cmd: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

