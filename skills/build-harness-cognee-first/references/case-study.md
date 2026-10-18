# Flash API case: a reproducible process example, not an architecture recipe

Repository: https://github.com/opensiro/harness-build-example-flash-api

Observed chronology in PR #1:
1. A Python dependency repair task and source selection were fixed before architectural discovery. Index commit 14a2182e2d6d0ecd851cef118906431b2c851aaa; connector d176484e85da55c84450d67040cb4a2d096353c7, with a disclosed one-line sharded-path fix.
2. A deterministic 128/577 included-assessment sample was imported into a fresh local Cognee 1.6.4 dataset: 2,661 graph nodes, 1,765 edges, 768 exact grades; independent audit PASS.
3. Seven preregistered CHUNKS_LEXICAL queries returned native hits (including irrelevant negative controls). **Only the six VSM function sections of each full ingested assessment were lexical-search chunks**, not the entire Markdown; TLDR.md was not used.
4. A post-query shortlist and nine upstream code inspections at pinned SHA preceded the architecture decision. The resulting small adaptation was a Carbon-inspired observed post-write test gate.
5. Local Python tests passed 9/9 at final review. A scripted task-specific double resulted in baseline final tests FAIL and adapted final tests PASS. **Real Fast/Flash model run NOT RUN; no model-quality uplift established.**

Primary evidence:
- [Discovery and its coverage](../../../docs/cognee-discovery.md)
- [Raw Cognee results](../../../receipts/discovery/native-lexical-results.json)
- [Independent audit](../../../receipts/audit/independent-audit.json)
- [Candidate comparison](../../../reports/candidate-comparison.md)
- [Decision Trace](../../../traces/decision-trace.jsonl)
- [Final evaluation](../../../reports/evaluation.md)

For a new game/research/coding task, run *fresh* retrieval and comparisons. Carbon or test gating is not a mandatory or privileged choice.
