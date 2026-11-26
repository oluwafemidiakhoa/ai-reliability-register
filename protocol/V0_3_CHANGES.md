# Audit protocol: changes collected for version 0.3

This file collects proposed changes to the audit protocol this register follows (see
[PROTOCOL.md](../PROTOCOL.md)). The published protocol is **not** amended here: version 0.2
(7 November 2026, <https://doi.org/10.5281/zenodo.24036828>) stays as published. Changes are
collected until there are enough to warrant a new version.

Each entry gives the check, the current text, the gap, the proposed text, the application that
found it, and whether the problem was in the text or in how it was applied.

## 1. T1 Trivial comparator: "best" is chosen per metric

- **Proposed:** 2026-11-26. **Status:** collected for v0.3; not in any published version.
- **Current text (v0.2, T1 Pass):** "the headline beats the best trivial comparator by more than
  2 SE, and the target's documents report a trivial comparator." T1 Run already requires
  constant-per-class and majority classifiers plus stratified random (seeded, at least 1,000
  draws, mean and 95% range), and T1 Report already requires every comparator on every metric
  the target reports.
- **Gap:** the Pass criterion does not say that "best" is chosen separately for each metric. Read
  as one comparator chosen once, it lets the majority classifier, the best comparator on
  accuracy, stand in on macro-F1 or balanced accuracy, where a constant classifier is degenerate
  (its F1 is 0 on every class it never predicts).
- **Proposed text (T1 Pass):** the best trivial comparator is selected separately for each
  reported metric (majority-class for accuracy, stratified random for macro-F1 and balanced
  accuracy), and every comparator is reported on every metric.
- **Found by:** the GAIA-R001 research audit, 2026-11-26 (not published). Its first version
  compared a SUPPORT/CONTRADICT classifier on 85 claim–document links with the majority
  classifier only, and on accuracy only.
- **Whose error:** the auditor's. The misapplication was in the audit, not a defect in the v0.2
  text, which already required stratified random on every metric. The ambiguity above is the
  only gap in the text.
- **Worked example (that audit, corrected):**

  | Metric | Classifier | Majority (always-SUPPORT) | Stratified random | Matched comparator |
  |---|---|---|---|---|
  | Accuracy | 0.682 | 0.718 | 0.595 | majority |
  | Balanced accuracy | 0.564 | 0.500 | 0.500 | stratified random |
  | Macro-F1 | 0.566 | 0.418 | 0.499 (analytic 0.500) | stratified random |

  Against majority on macro-F1 the classifier appears to gain +0.148, with a cluster-bootstrap
  95% interval of [+0.039, +0.252]. Against the matched comparator, stratified random, the gain
  is +0.067, with interval [−0.087, +0.210]. The audit's conclusion, that the classifier does not
  beat its trivial comparators, held. Its reported comparison was wrong until corrected.
