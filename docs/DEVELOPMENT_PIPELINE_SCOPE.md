# Development-process objective and retrieval coverage

**Status:** retrospective documentation of the completed, immutable Flash API construction experiment. Historical Git chronology, archived Cognee receipts, model/stub results and implementation are unchanged.

## Primary question

Can Cognee plus the Opensiro VSM Harness Index provide inspectable architectural references for a new harness, so the developer can **discover → inspect → compare → decide → build** with a provenance-linked Decision Trace?

The Python dependency-repair agent is the *construction target*, not a benchmark target. This case does **not** require a real Fast/Flash backend, repeated coding tasks or proof of model-quality improvement. Local tests and scripted A/B demonstration are supporting engineering evidence, not mandatory performance success gates.

## What the original experiment shows

| Stage | Published artifact | Supported claim / boundary |
| --- | --- | --- |
| Task and pinned source selection | [Stage 1 protocol](cognee-discovery.md), [selection manifest](../receipts/preflight/selection-manifest.json) | Problem and 128/577 included-assessment sample were fixed before architecture choice |
| Cognee import and audit | [Native import](../receipts/import/native-import.json), [independent audit](../receipts/audit/independent-audit.json) | Complete raw Markdown was ingested for each of 128 selected assessments; typed facts and source identity checked |
| Native discovery | [Frozen query plan](../receipts/preflight/query-plan.json), [raw native results](../receipts/discovery/native-lexical-results.json) | Seven native `CHUNKS_LEXICAL` searches across **768 S1–S5 chunks**, not entire Markdown; generated TLDR.md not consulted |
| Candidate comparison | [Post-query shortlist](../reports/post-discovery-shortlist.md), [pinned source comparison](../reports/candidate-comparison.md) | Assessment hits prompted later full-source inspection; shortlist is not a performance ranking |
| Architecture decision | [Decision record](architecture-decision.md), [append-only trace](../traces/decision-trace.jsonl) | Chose a bounded post-write test-feedback gate for a specific engineering reason, not because a VSM grade is a score |
| Produced code | [Harness implementation](../src/), [README](../README.md) | A concrete bounded Python-repair agent artifact exists; Cognee is a build-time dependency only |
| Optional engineering validation | [Recorded scripted comparison](../reports/evaluation.md) | One scripted protocol differential and local tests; **no real Flash-model evaluation** and no model-quality uplift claim |

## Completion semantics

**Construction-process:** source-grounded Cognee-first discovery, comparison, decision, implementation and attributable commits/receipts are the success criteria.

**Runtime correctness:** ordinary tests can be reported if executed; no missing benchmark is to be labeled a defect in the construction study.

**Model performance:** separately scoped, optional and `NOT_RUN` in the historical experiment.

For reusable future executions, the experimental [Cognee-first construction skill PR](https://github.com/opensiro/vsm-harness-skills/pull/52) defines stronger C1–C4 evidence requirements. Do **not** retrofit those future requirements, full-body retrieval, or unrun experiments into this frozen first case.
