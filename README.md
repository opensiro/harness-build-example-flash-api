# Opensiro — Cognee-first Harness Construction (Python Dependency Repair)

This public experiment demonstrates the **causal build-time** use of Cognee and the Opensiro VSM Harness Index to identify, compare and select one design mechanism **before** building a tiny coding-agent harness.

## Traceable chronology

1. [Problem and dataset](docs/cognee-discovery.md) fixed before queries; Index commit `14a2182e2d6d0ecd851cef118906431b2c851aaa`, public connector review commit `d176484e85da55c84450d67040cb4a2d096353c7` plus one disclosed shard-layout fix.
2. [Precommitted 128 included records](receipts/preflight/selection-manifest.json), chosen by a deterministic SHA-256 ID rule (not hand-picked candidate harnesses).
3. Real native Cognee import [receipt](receipts/import/native-import.json): 128 records, 2,661 graph nodes, 1,765 edges, 768 grades. Independent [audit PASS](receipts/audit/independent-audit.json).
4. Seven preregistered [Cognee lexical queries](receipts/preflight/query-plan.json) produced [original native results](receipts/discovery/native-lexical-results.json) and [all-hits index](receipts/discovery/hit-index.json), **including irrelevant negative-control results**.
5. [Post-discovery shortlist](reports/post-discovery-shortlist.md) → [pinned upstream comparison](reports/candidate-comparison.md) → [architecture decision](docs/architecture-decision.md).
6. **Baseline** versus **adapted** harness and [evaluation](reports/evaluation.md). The single adaptation is a *fresh post-mutation observed-test gate with bounded feedback*, not a copied platform.

**Reusable build-time procedure:** [Cognee-first harness construction skill](skills/build-harness-cognee-first/SKILL.md) (experimental; not the canonical VSM assessment methodology). The [case-study guide](skills/build-harness-cognee-first/references/case-study.md) explains which observations can and cannot be generalized.

[Append-only Decision Trace](traces/decision-trace.jsonl) · [Receipt checksums](receipts/sha256-manifest.json) · [Final 9/9 review](receipts/evaluation/final-pr-review-validation.log) · [Experiment PR #1](https://github.com/opensiro/harness-build-example-flash-api/pull/1).

## Minimal harness

The task is to repair a small Python project after a **synthetic offline dependency upgrade** renamed a function. Both variants have the same maximum model-call budget, editable file, and fixed read/replace/test actions. The adapted variant automatically runs fresh Python unit tests after each write, feeds failure output to the same model, and refuses a verified completion unless tests passed *after the latest mutation*. The baseline has no enforced verification gate.

**Cognee is not installed, imported, or required at runtime.** No unrestricted model-generated shell commands. This is not a general-purpose secure container sandbox; only run against the included trusted test fixture.

Run without paid-model access:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python evaluation/run_evaluation.py --backend scripted --output receipts/evaluation/scripted-results.json
```

An OpenAI-compatible Fast/Flash-tier model can be used separately:

```bash
PYTHONPATH=src python evaluation/run_evaluation.py --backend openai \
  --base-url "https://your-provider.example/v1" --model "your-fast-model"
```

Optional API key is loaded from `OPENAI_API_KEY` (or `--api-key-env`). Model outputs must be one JSON action in message content; provider function-call extension is not needed. No API credentials go into receipts. Only mark a model-backed evaluation as completed if you actually run one.

## Limits

The scripted double intentionally reacts to fresh test failures and proves **the protocol difference**, not LLM quality uplift or task success across a benchmark. The dependency upgrade is a local API fixture (no package published/installed). VSM A/C/— are architectural grades, not performance scores. Cognee native lexical retrieval has false positives (see the astronomy control); upstream source inspection is essential. The adapted test gate is deterministic support, **not** a claim of autonomous S3*.

All upstream repositories remain untouched.
