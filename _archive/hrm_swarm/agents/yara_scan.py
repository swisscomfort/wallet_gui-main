"""Agent that optionally runs yara rules over enumerated files."""

from __future__ import annotations

import os
import shutil
import time

from .base import Agent, Result, Task


class YaraScanAgent(Agent):
    NAME = "yara_scan"

    def run(self, task: Task) -> Result:
        t0 = time.time()
        rules = task.payload.get("rules")
        paths = task.payload.get("paths", [])
        threads = int(task.payload.get("threads", 4))
        workdir = task.payload.get("workdir", ".")

        if not rules or not os.path.exists(str(rules)) or not shutil.which("yara"):
            return Result(kind=self.NAME, ok=True, data={"yara_hits": []}, took_s=time.time() - t0)

        tmp = os.path.join(str(workdir), "paths_yara.txt")
        try:
            with open(tmp, "w", encoding="utf-8") as handle:
                handle.write("\n".join(p for p in paths if os.path.isfile(p)))
        except Exception as exc:
            return Result(
                kind=self.NAME,
                ok=False,
                data={"error": f"write paths list failed: {exc}"},
                took_s=time.time() - t0,
            )

        cmd = (
            f'xargs -a "{tmp}" -P {threads} -I{{}} sh -c '
            f'"yara -s --nogc \"{rules}\" \"{{}}\" 2>/dev/null | sed -e \"s/^/{{}}\\t/\""'
        )

        try:
            result = self.shell(cmd, timeout=int(task.payload.get("timeout", 900)))
        except Exception as exc:
            return Result(
                kind=self.NAME,
                ok=False,
                data={"error": f"yara failed: {exc}"},
                took_s=time.time() - t0,
            )

        hits: list[dict[str, str]] = []
        if result.returncode in (0, 1):
            for line in result.stdout.splitlines():
                try:
                    file_path, raw = line.split("\t", 1)
                except ValueError:
                    continue
                hits.append({"file": file_path, "raw": raw})

        return Result(kind=self.NAME, ok=True, data={"yara_hits": hits}, took_s=time.time() - t0)

