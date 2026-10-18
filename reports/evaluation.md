# Evaluation — Python Dependency Repair

**Status:** Offline protocol evaluation complete on the fixed synthetic task. **Real Fast/Flash-model evaluation NOT RUN.** No model-quality or performance-uplift claim.

## What was executed

Actual Python 3.12.3 execution on CPU-VM against source commit `c8f439891263bb573e050402db75a35c926a5aca`, with a **new copy** of the same offline fixture for each variant. Source built only after public Cognee discovery, pinned assessment/upstream inspection and architecture decision.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 evaluation/run_evaluation.py --backend scripted \
  --output receipts/evaluation/scripted-results-v2.json
```

Result: **8 of 8 unit tests PASS**; included tests check initially broken dependency, source patch, test-gate feedback, stale-pass invalidation, exhausted call budget, malformed model output, blocked path and local OpenAI-compatible HTTP request/response structure.

| Measurement | Baseline | Adapted |
| --- | --- | --- |
| Max allowed model calls | 3 | 3 |
| Calls used (scripted double) | 2 | 3 |
| Mutations made | 1 | 2 |
| Enforced fresh tests within run | 0 | 2 |
| Model-facing final status | `complete_unverified` | `verified_complete` |
| Independent post-run fixture unit tests | FAIL | PASS |

**Interpretation:** The scripted double first changes the imported symbol but forgets to update its call site. In adapted mode the automatically executed tests expose that failure; the double's next programmed action repairs the use site, and a fresh test result passes. In baseline mode the double has no forced test result and chooses to finish. The same max call budget is available to both variants; actual calls and test execution differ by protocol.

The scripted double is deliberately designed to respond to the additional test feedback. **This does not measure intelligence, typical model behavior, general task success or causal performance uplift for LLMs.** The task is one synthetic dependency API rename, not a real package ecosystem regression.

## Original execution evidence

- [Final eight-test output](../receipts/evaluation/unit-tests-v2.log).
- [Final scripted execution receipt](../receipts/evaluation/scripted-results-v2.json), including both action traces, observed test output, fixture SHA256 and source Git revision.
- [Final command output](../receipts/evaluation/evaluation-v2-stdout.log).
- [Original earlier five-test receipt](../receipts/evaluation/unit-tests.log) and [original scripted comparison](../receipts/evaluation/scripted-results.json) remain preserved; they were not overwritten after the later robustness changes.
- [Checksums](../receipts/sha256-manifest.json) cover original Cognee import, audit, all native query results and evaluation files.

## Source and reproducibility boundary

Cognee is **build-time only**. The harness source itself imports only Python stdlib. Baseline and adapted use exactly the same task, input source and target file restriction, OpenAI-compatible model-action schema, read/replace/run-tests tools, and maximum model calls. Adapted has a mandatory fresh post-write test gate; that is the **only selected adaptation**. A fixed subprocess executes local Python unittest, not arbitrary model-authored shell commands.

For a separate real model-backed comparison set `OPENAI_BASE_URL`, `OPENAI_MODEL` and optionally `OPENAI_API_KEY`, then run:

```bash
PYTHONPATH=src python evaluation/run_evaluation.py --backend openai \
  --base-url "$OPENAI_BASE_URL" --model "$OPENAI_MODEL" \
  --output receipts/evaluation/live-model-REPLACE-WITH-ACTUAL-RUN.json
```

This command is an **optional reproduction example only**; no live model receipt exists, and no successful model run is claimed. Model must emit one JSON action in assistant text. The HTTP integration was checked with an offline local request/response test, **not** a real provider.

## Limits / negative findings

1. The synthetic dependency fixture lives on PYTHONPATH; it is not a released or network-installed Python package.
2. A scripted double is not evidence of real-model improvement. No real Fast/Flash endpoint was invoked.
3. The fixed local test runner is not a general sandbox for arbitrary untrusted software; do not run unknown repositories.
4. Success is task-and-receipt-local. There is no SWE-bench/Terminal-Bench claim, broad reliability sample, token-cost study, or statistical uplift.
5. The Index's S1–S5 grades are not numerical capability scores; using a Carbon-inspired deterministic test gate does not establish a new autonomous S3* function.
6. Cognee native lexical search returned unrelated hits (including a 15-hit negative control). Selection required separate source reading and pinned upstream inspection.

**Primary conclusion supported here:** the publicly preserved sequence `Problem → Cognee import/audit/native discovery → VSM and pinned upstream comparison → selected simple verification mechanism → running baseline/adapted protocol` is demonstrable and reproducible. Its **build process** is the object of this experiment, not alleged LLM uplift.
