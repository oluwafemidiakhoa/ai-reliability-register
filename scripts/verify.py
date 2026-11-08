#!/usr/bin/env python3
"""Verify every register entry. Exits non-zero, listing every problem, if anything is wrong.

Usage:  python3 scripts/verify.py

For each entries/REG-YYYY-NNN.json it checks:
  1. the entry validates against schema/entry.schema.json (a small built-in validator for exactly
     the JSON Schema keywords the schema uses; an unknown keyword is an error, never ignored);
  2. the file name matches sealed.id;
  3. sealed.seal_hash equals SHA-256 of the canonical serialisation (same function as seal.py);
  4. prediction and confidence are both set or both null;
  5. an entry with a prediction was sealed on or before the day it was published;
  6. an outcome is recorded only together with a result.

Standard library only, so it still runs when nothing else does.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRIES = os.path.join(ROOT, "entries")
SCHEMA = os.path.join(ROOT, "schema", "entry.schema.json")

# Must stay identical to seal.py.
def canonical_payload(entry):
    sealed = {k: v for k, v in entry["sealed"].items() if k != "seal_hash"}
    payload = {"auditor": entry["auditor"], "sealed": sealed}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def seal_hash(entry):
    return hashlib.sha256(canonical_payload(entry)).hexdigest()


# --- minimal JSON Schema validator -------------------------------------------------------------
ANNOTATIONS = {"$schema", "$id", "title", "description", "x-schema-version"}
TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def validate(value, schema, path, errors):
    for key in schema:
        if key not in ANNOTATIONS and key not in {
            "type", "const", "enum", "required", "properties", "additionalProperties", "pattern",
            "minLength", "minimum", "maximum", "items", "minItems", "uniqueItems",
        }:
            errors.append(f"schema keyword not supported by verify.py: {key} (at {path})")
    if "type" in schema:
        allowed = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(TYPES[t](value) for t in allowed):
            errors.append(f"{path}: expected {' or '.join(allowed)}, got {type(value).__name__}")
            return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
    if TYPES["integer"](value):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above {schema['maximum']}")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required field {req!r}")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                validate(v, props[k], f"{path}.{k}", errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected field {k!r}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            errors.append(f"{path}: items must be unique")
        if "items" in schema:
            for i, item in enumerate(value):
                validate(item, schema["items"], f"{path}[{i}]", errors)


# --- entry checks ------------------------------------------------------------------------------
def check_entry(path, schema):
    errors = []
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            entry = json.load(f)
    except (OSError, ValueError) as err:
        return [f"{name}: cannot read JSON: {err}"]
    validate(entry, schema, "entry", errors)
    if errors:
        return [f"{name}: {e}" for e in errors]
    sealed, open_ = entry["sealed"], entry["open"]
    if name != f"{sealed['id']}.json":
        errors.append(f"file name does not match sealed.id {sealed['id']}")
    expected = seal_hash(entry)
    if sealed["seal_hash"] != expected:
        errors.append(f"SEAL MISMATCH: stored {sealed['seal_hash']}, recomputed {expected}. "
                      "The auditor or the sealed block has changed since sealing.")
    if (sealed["prediction"] is None) != (sealed["confidence"] is None):
        errors.append("prediction and confidence must both be set or both be null")
    if sealed["prediction"] is not None and open_["published_at"] and open_["published_at"] < sealed["sealed_at"][:10]:
        errors.append("published before it was sealed: a prediction must be sealed before the audit")
    if open_["outcome"] is not None and open_["result"] is None:
        errors.append("an outcome needs a result")
    return [f"{name}: {e}" for e in errors]


def main():
    with open(SCHEMA, encoding="utf-8") as f:
        schema = json.load(f)
    files = sorted(f for f in os.listdir(ENTRIES) if f.endswith(".json"))
    if not files:
        print("verify: no entries found")
        return 1
    problems = []
    for f in files:
        problems += check_entry(os.path.join(ENTRIES, f), schema)
    stray = sorted(f for f in os.listdir(ENTRIES) if not f.endswith(".json") and not f.startswith("."))
    problems += [f"entries/{f}: only REG-YYYY-NNN.json files belong in entries/" for f in stray]
    if problems:
        print(f"verify: FAILED, {len(problems)} problem(s) in {len(files)} entr{'y' if len(files) == 1 else 'ies'}:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"verify: OK, {len(files)} entr{'y' if len(files) == 1 else 'ies'}; every seal_hash recomputes and every entry matches the schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
