# Governance

The register has to stay trustworthy with nobody maintaining it. These rules are written so that
anyone can check whether they were followed, using only this repository.

## Contribution

- Anyone may contribute an entry, by pull request, following the steps in the README.
- A sealed entry must be merged, and its hash published outside this repository, **before** the
  audit starts. The external copy is the proof of timing; the git history is the second copy.
- The auditor named in an entry is responsible for its content. Maintainers check form (the entry
  verifies and validates), not findings.
- Entry numbers are assigned in order within each year. A number is never reused, even if an
  entry is withdrawn.

## Disputes

- The author of an audited claim may respond to any entry. Responses are added unedited as
  `responses/REG-YYYY-NNN-N.md`, and the entry's notes link to each response.
- A response never changes the sealed stage. If it shows that an open-stage finding is wrong, the
  finding is corrected under the rules below and the correction cites the response.
- Before publication, the auditor follows the protocol's contact rule: the target's author sees
  the findings first, by private channel, with 14 days to respond.

## Corrections

- **The sealed stage is never edited.** A seal that fails to recompute is a defect, and
  `scripts/verify.py` fails until it is resolved. If something in a sealed stage is wrong, leave
  it, and record the error in the notes and in the open-stage result.
- Open-stage fields may be corrected by pull request. Each correction adds a note to the entry
  starting "Corrected YYYY-MM-DD:" that says what changed and why. Git history keeps the earlier
  text.
- An entry is never deleted. A withdrawn entry stays in place, with its outcome left as recorded
  and a note starting "Withdrawn YYYY-MM-DD:" giving the reason.

## Succession

- The register is plain files. Any copy whose entries all verify with `scripts/verify.py`, and
  whose history is intact, is a valid copy; no maintainer or host is needed to check it.
- The maintainer deposits a snapshot of the repository in a long-term archive (for example
  Zenodo) at least once a year and after any batch of new entries, and lists the deposits below.
- If the maintainer has not responded to issues or pull requests for 12 months, any contributor
  may continue the register in a fork. They should state the fork in a pull request to this
  repository (even if it is never merged) and in the fork's README. Where forks diverge, readers
  should prefer the one whose entries all verify and that preserves the full earlier history.

## Archive deposits

| Date | Location |
|---|---|
| — | none yet |
