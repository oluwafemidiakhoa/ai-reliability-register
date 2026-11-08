# AI Reliability Claims Register

A public record of audits of published AI reliability claims: what was claimed, what the auditor
expected to find before looking, and what the audit found.

Each entry is one audit of one claim. Every entry has two stages:

- **Sealed**, written before the audit starts: the target, the exact claim, the checks to be run,
  and the auditor's prediction with a confidence. The sealed stage is hashed, and the hash is
  published somewhere outside this repository before the audit begins. That makes the prediction
  impossible to change afterwards without detection.
- **Open**, filled in after the audit: the result, the outcome, the cost, whether the target's
  author was contacted, and when the audit was published.

The register is plain files in a git repository: no database, no server, no accounts, no
framework. It is designed to be readable and verifiable in 2040 with nobody maintaining it. Anything
needed to check it is in this repository, and the scripts use only the Python 3 standard library.

The audits follow a published protocol; see [PROTOCOL.md](PROTOCOL.md).

## Contents

| Path | What it is |
|---|---|
| `entries/REG-YYYY-NNN.json` | One file per entry |
| `schema/entry.schema.json` | JSON Schema for an entry (version in `schema_version`) |
| `scripts/seal.py` | Seals a draft entry and prints the hash to publish |
| `scripts/verify.py` | Re-checks every seal and validates every entry against the schema |
| `scripts/build_index.py` | Regenerates `INDEX.md` |
| `INDEX.md` | Table of all entries (generated) |
| `GOVERNANCE.md` | Contribution, disputes, corrections, succession |
| `PROTOCOL.md` | Pointer to the audit protocol |

## How to read an entry

| Field | Meaning |
|---|---|
| `auditor` | Name, ORCID, and `self_audit`: true when the auditor built or operates the audited system. A self-audit cannot establish independence. |
| `sealed.target` | What was audited, with a version precise enough to find it again (a commit, a record DOI, a date range). |
| `sealed.claim` | The published claim, quoted exactly, with where it appears. |
| `sealed.checks` | Protocol checks planned (T1–T6 core, C1–C4 conditional, N1–N3 reproducibility, S1–S4 supporting techniques). |
| `sealed.prediction`, `sealed.confidence` | What the auditor expected, and how sure (integer percent), before starting. Null only in entries recorded retrospectively (see each entry's notes). |
| `sealed.sealed_at`, `sealed.seal_hash` | When the entry was sealed (UTC), and its SHA-256 seal. |
| `open.result` | Summary, one record per finding (with the checks that caught it and its class: measurement, omission or framing), and checks that were not performed, with reasons. |
| `open.outcome` | `claim_holds`, `claim_partly_holds`, `claim_fails`, `inconclusive`, `not_reproducible`; null while open. |
| `open.cost` | Paid API spend as a decimal string, with a note. |
| `open.author_contacted` | Date the target's author was first contacted; `false` if not yet; null when there is nobody else to contact (self-audit). |
| `open.published_at` | Date the audit was published; null if not yet. |
| `notes` | Context outside both stages. Not covered by the seal. |

## How the seal works

The seal is SHA-256 over this exact byte string:

1. Take the JSON object `{"auditor": <auditor>, "sealed": <sealed>}`, with `seal_hash` removed
   from `sealed` (`sealed_at` stays in).
2. Serialise it with keys sorted at every level, no whitespace between tokens (`,` and `:` only),
   and non-ASCII characters written as themselves, not escaped.
3. Encode as UTF-8, and hash with SHA-256. Write the digest as 64 lowercase hex characters.

Numbers in the sealed block are integers only, so the serialisation is the same in every language.
To recompute by hand with Python:

```python
import hashlib, json
e = json.load(open("entries/REG-2026-001.json", encoding="utf-8"))
s = {k: v for k, v in e["sealed"].items() if k != "seal_hash"}
b = json.dumps({"auditor": e["auditor"], "sealed": s}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
print(hashlib.sha256(b).hexdigest() == e["sealed"]["seal_hash"])
```

A matching hash shows the entry has not changed since sealing. The **external** copy of the hash,
published before the audit, is what shows *when* the prediction was made. Each entry with a
prediction should link that external copy in its notes.

Entries REG-2026-001 and REG-2026-002 were recorded after their audits were done, have no
prediction, and say so in their notes. The prediction seal applies from REG-2026-003.

## Verify the register yourself

```
python3 scripts/verify.py
```

It exits non-zero and lists every problem if any seal fails to recompute or any entry breaks the
schema. The same command runs on every push (`.github/workflows/verify.yml`).

## Contributing an entry

1. Copy an existing entry to `entries/REG-YYYY-NNN.json` with the next number for the year. Fill in
   `auditor` and every `sealed` field except `sealed_at` and `seal_hash`. Set every `open` field to
   null (or `false` for `author_contacted`).
2. Run `python3 scripts/seal.py entries/REG-YYYY-NNN.json`. It refuses to seal twice.
3. Publish the printed hash outside this repository (a dated public post, an email to a third
   party, a timestamping service), and record where in the entry's notes.
4. Open a pull request with the sealed entry **before** the audit starts.
5. After the audit, fill in the `open` fields in a second pull request, then run
   `python3 scripts/build_index.py`.

See [GOVERNANCE.md](GOVERNANCE.md) for disputes, corrections and succession.

## Licence

Entries, schema and documentation: CC BY 4.0. Scripts: MIT. See [LICENSE](LICENSE).
