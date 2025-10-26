
#!/usr/bin/env python3
# hrm_swarm_scanner.py — Single-file HRM-style swarm scanner (Fedora-ready)
# Usage (example):
#   python3 hrm_swarm_scanner.py --root /run/media/emil/DATEN --target /run/media/emil/DATEN
# Optional:
#   --threads 8 --max-mb 512 --exclude '(\.git|node_modules)' --prefer-rg --yara
#
# Outputs:
#   <root>/_logs/hrm_swarm_<epoch>/hits.json, mnemonics.json, summary.json
#
# Requires: Python 3.9+, ripgrep (optional), yara (optional)

import os, sys, re, json, time, argparse, shutil, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------- Utils: validators & scoring -----------------------------

B58_ALPH = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
LEGACY_ADDR = re.compile(r"(?:^|[^A-Za-z0-9])([13][1-9A-HJ-NP-Za-km-z]{25,34})(?:[^A-Za-z0-9]|$)")
BECH32_ADDR = re.compile(r"(bc1[ac-hj-np-z02-9]{25,87}|tb1[ac-hj-np-z02-9]{25,87})")
WIF_RE = re.compile(r"(5[HJK][1-9A-HJ-NP-Za-km-z]{49,51}|[KL][1-9A-HJ-NP-Za-km-z]{51,52})")
ETH_PRIV_HEX = re.compile(r"\b0x[a-fA-F0-9]{64}\b")
MN_HEUR = re.compile(r"\b([a-z]{3,8}(?:\s+[a-z]{3,8}){11,23})\b", re.I)

def b58decode_check(s):
    num = 0
    for c in s:
        if c not in B58_ALPH:
            raise ValueError("bad base58")
        num = num * 58 + B58_ALPH.index(c)
    full = num.to_bytes((num.bit_length()+7)//8, 'big')
    if len(full) < 4:
        raise ValueError("too short")
    data, checksum = full[:-4], full[-4:]
    import hashlib
    if hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4] != checksum:
        raise ValueError("bad checksum")
    return data

def is_valid_wif(w):
    try:
        data = b58decode_check(w)
    except Exception:
        return False
    return data[:1] in (b"\x80", b"\xef") and len(data) in (33, 34)

def bech32_polymod(values):
    GENERATORS = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = (chk >> 25) & 0xff
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            if (b >> i) & 1:
                chk ^= GENERATORS[i]
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_verify(addr, hrps=("bc","tb")):
    addr = addr.strip().lower()
    if any(c < 33 or c > 126 for c in map(ord, addr)): return False
    if addr.rfind("1") == -1: return False
    hrp, data = addr[:addr.rfind("1")], addr[addr.rfind("1")+1:]
    if hrp not in hrps: return False
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    try:
        vals = [CHARSET.index(c) for c in data]
    except ValueError:
        return False
    return bech32_polymod(bech32_hrp_expand(hrp) + vals) == 1

def score_snippet(text):
    score, reasons = 0, []
    # bech32
    bech = BECH32_ADDR.findall(text)
    good_bech = [a for a in bech if bech32_verify(a)]
    if good_bech:
        score += 4 * len(good_bech); reasons.append(f"{len(good_bech)} bech32")
    # legacy
    good_leg = []
    for m in LEGACY_ADDR.finditer(text):
        a = m.group(1)
        try:
            v = b58decode_check(a)
            if v[:1] in (b"\x00", b"\x05", b"\x6f"):
                good_leg.append(a)
        except Exception:
            pass
    if good_leg:
        score += 3 * len(good_leg); reasons.append(f"{len(good_leg)} legacy")
    # WIF
    wifs = WIF_RE.findall(text)
    valid_wifs = [w for w in wifs if is_valid_wif(w)]
    if valid_wifs:
        score += 15; reasons.append("valid WIF")
    # ETH private hex
    if ETH_PRIV_HEX.search(text):
        score += 10; reasons.append("eth priv hex")
    # Mnemonic heuristic
    if MN_HEUR.search(text):
        score += 6; reasons.append("seed-like")
    return score, reasons

# ----------------------------- Agents (inline) -----------------------------

PATTERN = r'wallet\\.dat|electrum|metamask|keystore|bip(39|32)|mnemonic|seed( phrase)?|xpub|ypub|zpub|tpub|xprv|bc1[ac-hj-np-z02-9]{25,87}|tb1[ac-hj-np-z02-9]{25,87}|(^|[^A-Za-z0-9])[13][1-9A-HJ-NP-Za-km-z]{25,34}([^A-Za-z0-9]|$)|0x[a-fA-F0-9]{64}|(5[HJK][1-9A-HJ-NP-Za-km-z]{49,51})|(K|L)[1-9A-HJ-NP-Za-km-z]{51,52}'

def enumerate_files(root, max_mb=256, exclude=None, prune=None):
    size_limit = int(max_mb) * 1024 * 1024
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        if prune:
            dirnames[:] = [d for d in dirnames if d not in prune]
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(fp) <= size_limit:
                    if not exclude or not re.search(exclude, fp, flags=re.I):
                        out.append(fp)
            except Exception:
                pass
    return out

def run_content_scan(paths, threads=6, prefer_rg=True, workdir=".", timeout=900):
    if not paths: 
        return []
    lst = os.path.join(workdir, "scan_paths.txt")
    with open(lst, "w") as f:
        f.write("\n".join(p for p in paths if os.path.isfile(p)))
    
    # Prüfe ob Datei Inhalt hat
    if os.path.getsize(lst) == 0:
        return []
    
    hits = []
    use_rg = bool(prefer_rg and shutil.which("rg"))
    if use_rg:
        cmd = f'rg -a -n -H -U -e "{PATTERN}" --threads {max(1,threads)} -f "{lst}"'
    else:
        cmd = f'xargs -a "{lst}" -P {max(1,threads)} -I{{}} sh -c \'grep -aHnE "{PATTERN}" "{{}}" || true\''
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return hits  # Return what we have so far
    except Exception as e:
        # Log error but continue
        print(f"Warning: scan error: {e}", file=sys.stderr)
        return hits
    if r.returncode in (0,1):
        for line in r.stdout.splitlines():
            parts = line.split(":",2)
            if len(parts) == 3:
                fpath, ln, txt = parts
                s, rsn = score_snippet(txt)
                if s > 0:
                    hits.append({"file": fpath, "line": int(ln or 0), "score": s, "reasons": rsn, "snippet": txt[:500]})
    return hits

def run_yara_scan(paths, rules_text=None, rules_path=None, threads=6, workdir=".", timeout=900):
    if not shutil.which("yara"):
        return []
    if not paths:
        return []
    if rules_path and os.path.exists(rules_path):
        rpath = rules_path
    else:
        # minimal built-in
        rules_text = rules_text or (
            'rule ETH_Keystore { strings: $a="crypto" $b="kdf" $c="ciphertext" $d="mac" condition: all of them }\n'
            'rule Electrum { strings: $a="seed_version" $b="wallet_type" $c="keystore" condition: 2 of ($a,$b,$c) }\n'
        )
        rfd, rpath = tempfile.mkstemp(prefix="yar_", suffix=".yar", text=True)
        os.write(rfd, rules_text.encode("utf-8")); os.close(rfd)
    lst = os.path.join(workdir, "yara_paths.txt")
    with open(lst, "w") as f:
        f.write("\n".join(p for p in paths if os.path.isfile(p)))
    
    # Prüfe ob Datei Inhalt hat
    if os.path.getsize(lst) == 0:
        return []
    
    cmd = f'xargs -a "{lst}" -P {max(1,threads)} -I{{}} sh -c \'yara -s --nogc "{rpath}" "{{}}" 2>/dev/null | sed -e "s/^/{{}}\\t/"\''
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return []  # Return empty on timeout
    except Exception as e:
        print(f"Warning: YARA scan error: {e}", file=sys.stderr)
        return []
    hits = []
    if r.returncode in (0,1):
        for line in r.stdout.splitlines():
            try:
                fpath, rest = line.split("\t",1)
                hits.append({"file": fpath, "yara": rest})
            except Exception:
                pass
    return hits

def mnemonic_from_hits(hits):
    out = []
    for h in hits:
        m = MN_HEUR.search(h.get("snippet",""))
        if m:
            out.append({"file": h["file"], "line": h["line"], "mnemonic": m.group(1)})
    return out

# ----------------------------- HRM policy (inline fallback) -----------------------------

DEFAULT_POLICY = {
    "initial": {
        "params": {"max_mb":256, "threads":6, "prefer_rg": True, "exclude": None, "prune": ["node_modules",".git",".cache"]},
        "agents": ["enum","content"]
    },
    "escalation_rules": [
        {"if":"stats['hits_per_k'] >= 1.0 and stats['avg_score'] >= 6", "then":{"add":["yara","mnemonic"], "params":{"threads":6}}},
        {"if":"stats['hits_per_k'] < 0.05", "then":{"params":{"max_mb":512, "threads":10}}}
    ]
}

def load_vendor_policy():
    # Try to auto-extract policy from HRM-main.zip if present
    base = "/mnt/data/HRM-main.zip"
    if not os.path.exists(base):
        return None
    import zipfile
    try:
        with zipfile.ZipFile(base,"r") as zf:
            # try common policy names
            for name in zf.namelist():
                if name.lower().endswith(("policy.yaml","policy.yml","hrm_policy.yaml","hrm_policy.yml")):
                    data = zf.read(name).decode("utf-8","ignore")
                    try:
                        import yaml
                        return None, yaml.safe_load(data)
                    except Exception:
                        # naive parser: extremely minimal (expects a dict-ish JSON for fallback)
                        try:
                            return None, json.loads(data)
                        except Exception:
                            pass
            # no policy found
    except Exception:
        pass
    return None

def eval_rule(expr, stats):
    try:
        return bool(eval(expr, {"__builtins__":{}}, {"stats": stats}))
    except Exception:
        return False

# ----------------------------- Orchestrator -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Arbeits-Root (OUT wird hier erstellt)")
    ap.add_argument("--target", action="append", required=True, help="Scan-Ziel (mehrfach möglich)")
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--max-mb", type=int, default=None)
    ap.add_argument("--exclude", default=None)
    ap.add_argument("--prefer-rg", action="store_true")
    ap.add_argument("--no-prefer-rg", dest="prefer_rg", action="store_false")
    ap.add_argument("--yara", action="store_true", help="YARA-Stufe aktivieren (automatisch per HRM bei gutem Yield)")
    ap.add_argument("--rules", default=None, help="Pfad zu .yar")
    ap.add_argument("--workdir", default=".", help="Temp-Dateien")
    ap.set_defaults(prefer_rg=True)
    args = ap.parse_args()

    # Policy
    vendor = load_vendor_policy() or DEFAULT_POLICY
    if isinstance(vendor, tuple):
        # (path, dict) fallback; but we don't need path here
        _, policy = vendor
    else:
        policy = vendor

    params = dict(policy.get("initial",{}).get("params",{}))
    if args.threads: params["threads"] = args.threads
    if args.max_mb is not None: params["max_mb"] = args.max_mb
    if args.exclude: params["exclude"] = args.exclude
    params["prefer_rg"] = bool(args.prefer_rg)

    # Stage 1: enumerate all targets
    all_paths = []
    t0 = time.time()
    for t in args.target:
        all_paths.extend(enumerate_files(t, max_mb=params.get("max_mb",256), exclude=params.get("exclude"), prune=params.get("prune")))
    # Stage 2: content scan (chunked)
    hits = []
    chunksize = 2500
    with ThreadPoolExecutor(max_workers=max(1, params.get("threads",6))) as ex:
        futs = []
        for i in range(0, len(all_paths), chunksize):
            chunk = all_paths[i:i+chunksize]
            futs.append(ex.submit(run_content_scan, chunk, max(1, params.get("threads",6)//2), params.get("prefer_rg",True), args.workdir))
        for fut in as_completed(futs):
            hits.extend(fut.result())

    elapsed = max(0.001, time.time()-t0)
    stats = {
        "elapsed_s": round(elapsed, 2),
        "files": len(all_paths),
        "hits": len(hits),
        "hits_per_k": round(len(hits)/max(1, len(all_paths)/1000), 3),
        "avg_score": round(sum(h.get("score",0) for h in hits)/max(1,len(hits)), 2),
    }

    # HRM escalation
    run_yara = args.yara
    run_mn = False
    for rule in policy.get("escalation_rules", []):
        cond = rule.get("if")
        if cond and eval_rule(cond, stats):
            t = rule.get("then",{})
            add = t.get("add", [])
            if "yara" in add: run_yara = True
            if "mnemonic" in add: run_mn = True
            params.update(t.get("params", {}))

    # Optional stages
    yara_hits = run_yara_scan(all_paths, rules_path=args.rules, threads=params.get("threads",6), workdir=args.workdir) if run_yara else []
    mnems = mnemonic_from_hits(hits) if (run_mn or args.yara) else []

    # Write results
    outdir = os.path.join(args.root, "_logs", f"hrm_swarm_{int(time.time())}")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "hits.json"), "w") as f: json.dump(hits, f, indent=2)
    with open(os.path.join(outdir, "yara.json"), "w") as f: json.dump(yara_hits, f, indent=2)
    with open(os.path.join(outdir, "mnemonics.json"), "w") as f: json.dump(mnems, f, indent=2)
    with open(os.path.join(outdir, "summary.json"), "w") as f: json.dump(stats, f, indent=2)
    print(json.dumps({"out": outdir, **stats}, indent=2))

if __name__ == "__main__":
    main()
