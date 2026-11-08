#!/usr/bin/env python3
"""Seal a draft register entry.

Usage:  python3 scripts/seal.py entries/REG-YYYY-NNN.json [--sealed-at YYYY-MM-DDTHH:MM:SSZ]

Writes sealed.sealed_at (now, UTC, unless --sealed-at is given) and sealed.seal_hash into the
file, then prints the hash. Publish that hash somewhere you do not control (a dated public post,
an email to a third party, a timestamping service) BEFORE the audit starts: the hash proves what
you predicted, and the external copy proves when.

The hash is SHA-256 over the canonical serialisation of {"auditor": ..., "sealed": ...} with
sealed.seal_hash removed: keys sorted, no whitespace, UTF-8, non-ASCII kept as is. The same
function is in verify.py; they must stay identical.

Standard library only. Refuses to re-seal an entry that already has a seal_hash.
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone

REQUIRED_BEFORE_SEAL = ("id", "target", "claim", "checks", "prediction", "confidence")


def canonical_payload(entry):
    sealed = {k: v for k, v in entry["sealed"].items() if k != "seal_hash"}
    payload = {"auditor": entry["auditor"], "sealed": sealed}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def seal_hash(entry):
    return hashlib.sha256(canonical_payload(entry)).hexdigest()


def no_floats(value, path="sealed"):
    if isinstance(value, float):
        raise SystemExit(f"refusing to seal: {path} is a float; use an integer or a string")
    if isinstance(value, dict):
        for k, v in value.items():
            no_floats(v, f"{path}.{k}")
    if isinstance(value, list):
        for i, v in enumerate(value):
            no_floats(v, f"{path}[{i}]")


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    path = argv[1]
    sealed_at = None
    if "--sealed-at" in argv:
        sealed_at = argv[argv.index("--sealed-at") + 1]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", sealed_at):
            raise SystemExit("--sealed-at must look like 2026-11-07T18:00:00Z")
    with open(path, encoding="utf-8") as f:
        entry = json.load(f)
    sealed = entry.get("sealed", {})
    if sealed.get("seal_hash"):
        raise SystemExit(f"refusing to re-seal {path}: it already has seal_hash {sealed['seal_hash']}")
    missing = [k for k in REQUIRED_BEFORE_SEAL if k not in sealed]
    if missing or "auditor" not in entry:
        raise SystemExit(f"refusing to seal: missing {', '.join(missing + ([] if 'auditor' in entry else ['auditor']))}")
    if (sealed["prediction"] is None) != (sealed["confidence"] is None):
        raise SystemExit("refusing to seal: prediction and confidence must both be set or both be null")
    no_floats(sealed)
    no_floats(entry["auditor"], "auditor")
    sealed["sealed_at"] = sealed_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sealed["seal_hash"] = seal_hash(entry)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{sealed['id']} sealed at {sealed['sealed_at']}")
    print(f"seal_hash: {sealed['seal_hash']}")
    print("Publish this hash externally before the audit starts.")


if __name__ == "__main__":
    main(sys.argv)
