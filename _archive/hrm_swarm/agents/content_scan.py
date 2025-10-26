"""Agent that runs ripgrep/grep to find wallet-related patterns."""

from __future__ import annotations

import os
import shutil
import time

from .base import Agent, Result, Task
from ..utils import score_text

PATTERN = (
    r"wallet\\.dat|electrum|metamask|keystore|bip(39|32)|mnemonic|"
    r"seed( phrase)?|xpub|ypub|zpub|tpub|xprv|bc1[ac-hj-np-z02-9]{25,87}|"
    r"tb1[ac-hj-np-z02-9]{25,87}|(^|[^A-Za-z0-9])[13][1-9A-HJ-NP-Za-km-z]{25,34}"
    r"([^A-Za-z0-9]|$)|0x[a-fA-F0-9]{64}|(5[HJK][1-9A-HJ-NP-Za-km-z]{49,51})|"
    r"(K|L)[1-9A-HJ-NP-Za-km-z]{51,52}"
)


class ContentScanAgent(Agent):
    NAME = "content_scan"

    def run(self, task: Task) -> Result:
        t0 = time.time()
        paths = task.payload.get("paths", [])
        threads = int(task.payload.get("threads", 4))
        workdir = task.payload.get("workdir", ".")
        hits: list[dict[str, object]] = []

        if not paths:
            return Result(kind=self.NAME, ok=True, data={"hits": []}, took_s=time.time() - t0)

        tmp = os.path.join(str(workdir), "paths.txt")
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

        use_rg = self.cfg.get("prefer_rg", True) and shutil.which("rg")
        cmd = (
            f'rg -a -n -H -U -e "{PATTERN}" --threads {threads} -f "{tmp}"'
            if use_rg
            else f'xargs -a "{tmp}" -P {threads} -I{{}} sh -c \'grep -aHnE "{PATTERN}" "{{}}" || true\''
        )

        try:
            result = self.shell(cmd, timeout=int(task.payload.get("timeout", 600)))
        except Exception as exc:
            return Result(
                kind=self.NAME,
                ok=False,
                data={"error": f"scan failed: {exc}"},
                took_s=time.time() - t0,
            )

        if result.returncode in (0, 1):
            for line in result.stdout.splitlines():
                parts = line.split(":", 2)
                if len(parts) == 3:
                    file_path, line_no, snippet = parts
                    score, reasons = score_text(snippet)
                    if score > 0:
                        hits.append(
                            {
                                "file": file_path,
                                "line": int(line_no),
                                "score": score,
                                "reasons": reasons,
                                "snippet": snippet[:400],
                            }
                        )

        return Result(kind=self.NAME, ok=True, data={"hits": hits}, took_s=time.time() - t0)

