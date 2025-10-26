# HRM Swarm Scanner Skeleton

This directory contains a minimal set of agents plus an orchestrator that demonstrates
an HRM-driven scanning workflow on Fedora systems.

* `run_swarm.py` – entry point orchestrator. Uses an optional `HRM-main.zip` bundle
  when found (see `HRM_MAIN_ZIP` env var) or falls back to `hrm_policy.yaml`.
* `agents/` – lightweight agents for file enumeration, content scanning, YARA analysis,
  and mnemonic validation.
* `rules/` – sample YARA rules applied during escalated scanning.
* `hrm_policy.yaml` – the default policy used when no vendor bundle is available.

Install dependencies (PyYAML plus external tools `ripgrep`/`yara`) and run:

```bash
python3 -m hrm_swarm.run_swarm --root /path/to/root --target /path/to/scan
```
