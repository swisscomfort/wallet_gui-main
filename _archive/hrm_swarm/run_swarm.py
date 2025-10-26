#!/usr/bin/env python3
"""Simple HRM-driven swarm scanner orchestrator."""

from __future__ import annotations

import argparse
import json
import os
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml

from .agents import (
    ContentScanAgent,
    FileEnumAgent,
    MnemonicValidateAgent,
    YaraScanAgent,
)
from .agents.base import Agent, Task

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_POLICY = BASE_DIR / "hrm_policy.yaml"
VENDOR_DIR = BASE_DIR / "_vendor"

AGENT_MAP = {
    "file_enum": FileEnumAgent,
    "content_scan": ContentScanAgent,
    "yara_scan": YaraScanAgent,
    "mnemonic_validate": MnemonicValidateAgent,
}


def select_policy_file(root: Path) -> Optional[Path]:
    if not root.exists():
        return None
    priority = [
        root / "hrm_policy.yaml",
        root / "policy.yaml",
        root / "policies" / "hrm_policy.yaml",
        root / "policies" / "default.yaml",
    ]
    for candidate in priority:
        if candidate.is_file():
            return candidate
    yaml_files = sorted(root.rglob("*.yaml"))
    return yaml_files[0] if yaml_files else None


def locate_vendor_policy(base_dir: Path) -> Optional[Path]:
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)

    extracted_candidates = [
        base_dir / "HRM-main",
        VENDOR_DIR / "HRM-main",
        Path("/mnt/data/HRM-main"),
    ]
    for folder in extracted_candidates:
        policy = select_policy_file(folder)
        if policy:
            return policy

    env_zip = os.environ.get("HRM_MAIN_ZIP")
    zip_candidates = [
        base_dir / "HRM-main.zip",
        Path("/mnt/data/HRM-main.zip"),
        Path.cwd() / "HRM-main.zip",
    ]
    if env_zip:
        zip_candidates.insert(0, Path(env_zip))
    for zip_path in zip_candidates:
        if not zip_path.is_file():
            continue
        target_dir = VENDOR_DIR / zip_path.stem
        target_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(target_dir)
        except Exception:
            continue
        policy = select_policy_file(target_dir)
        if policy:
            return policy
    return None


def load_policy(explicit: Optional[str]) -> tuple[Dict[str, object], Path]:
    if explicit:
        policy_path = Path(explicit).expanduser()
        with open(policy_path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle), policy_path

    vendor_policy = locate_vendor_policy(BASE_DIR)
    if vendor_policy:
        with open(vendor_policy, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle), vendor_policy

    with open(DEFAULT_POLICY, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle), DEFAULT_POLICY


def eval_rule(expression: str, stats: Dict[str, float]) -> bool:
    if not expression:
        return False
    try:
        return bool(eval(expression, {"__builtins__": {}}, stats))
    except Exception:
        return False


def instantiate_agents(agent_names: Iterable[str], params: Dict[str, object]) -> List[Agent]:
    agents: List[Agent] = []
    for name in agent_names:
        factory = AGENT_MAP.get(name)
        if not factory:
            continue
        agents.append(factory(params))
    return agents


def enumerate_paths(agent: Agent, targets: List[str], params: Dict[str, object]) -> List[str]:
    collected: List[str] = []
    for target in targets:
        payload = {**params, "root": target}
        result = agent.run(Task(kind="file_enum", payload=payload))
        if result.ok:
            collected.extend(result.data.get("paths", []))
    return collected


def run_content_scans(agent: Agent, paths: List[str], params: Dict[str, object], workdir: Path) -> List[dict]:
    hits: List[dict] = []
    if not paths:
        return hits

    chunksize = int(params.get("chunk_size", 2000))
    threads = max(1, int(params.get("threads", 6)))
    scan_params = dict(params)
    scan_params.setdefault("threads", max(1, threads // 2))
    scan_params["workdir"] = str(workdir)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for idx in range(0, len(paths), chunksize):
            chunk = paths[idx : idx + chunksize]
            payload = dict(scan_params)
            payload["paths"] = chunk
            futures.append(executor.submit(agent.run, Task(kind="content_scan", payload=payload)))
        for future in as_completed(futures):
            result = future.result()
            if result.ok:
                hits.extend(result.data.get("hits", []))
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Base root where logs will be written")
    parser.add_argument(
        "--target",
        action="append",
        required=True,
        help="Target directory to scan (can be passed multiple times)",
    )
    parser.add_argument("--policy", help="Override policy file", default=None)
    parser.add_argument("--workdir", help="Temporary workspace", default=None)
    args = parser.parse_args()

    policy, policy_path = load_policy(args.policy)
    params = dict(policy.get("initial", {}).get("params", {}))
    agent_names = list(policy.get("initial", {}).get("agents", []))
    if not agent_names:
        agent_names = ["file_enum", "content_scan"]
    agents = instantiate_agents(agent_names, params)

    workdir = Path(args.workdir or BASE_DIR)
    workdir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Policy: {policy_path}")
    if not agents:
        raise SystemExit("no agents initialised")

    stage_start = time.time()
    print("[*] Stage 1: enumerate files")
    all_paths = enumerate_paths(agents[0], args.target, params)
    print(f"    enumerated {len(all_paths)} files")

    if len(agents) < 2:
        raise SystemExit("content_scan agent missing in policy")

    print("[*] Stage 2: content scan")
    scan_start = time.time()
    hits = run_content_scans(agents[1], all_paths, params, workdir)
    scan_elapsed = max(1e-6, time.time() - scan_start)
    print(f"    hits {len(hits)} (elapsed {scan_elapsed:.1f}s)")

    stats = {
        "hits_per_min": round(len(hits) / scan_elapsed * 60.0, 2),
        "avg_score": round(sum(h.get("score", 0) for h in hits) / max(1, len(hits)), 2),
        "elapsed_s": round(time.time() - stage_start, 2),
    }
    print(f"    stats {stats}")

    for rule in policy.get("escalation_rules", []):
        condition = rule.get("if", "")
        if eval_rule(condition, stats):
            params.update(rule.get("params", {}))
            for name in rule.get("add_agents", []):
                if name not in [agent.NAME for agent in agents]:
                    factory = AGENT_MAP.get(name)
                    if factory:
                        agents.append(factory(params))

    results: Dict[str, object] = {"hits": hits}
    for agent in agents[2:]:
        print(f"[*] Stage: {agent.NAME}")
        payload = {**params, **results, "paths": all_paths, "workdir": str(workdir)}
        res = agent.run(Task(kind=agent.NAME, payload=payload))
        if res.ok:
            results.update(res.data)

    root_path = Path(args.root)
    outdir = root_path / "_logs" / f"hrm_swarm_{int(time.time())}"
    outdir.mkdir(parents=True, exist_ok=True)

    hits_path = outdir / "hits.json"
    with open(hits_path, "w", encoding="utf-8") as handle:
        json.dump(results.get("hits", []), handle, indent=2)

    mn_path = outdir / "mnemonics.json"
    with open(mn_path, "w", encoding="utf-8") as handle:
        json.dump(results.get("mnemonics", []), handle, indent=2)

    print("[+] Done:", outdir)


if __name__ == "__main__":
    main()

