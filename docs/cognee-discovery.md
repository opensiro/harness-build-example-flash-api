# Cognee discovery protocol (Stage 1)

## Source and scope

Problem fixed before discovery: Python Dependency Repair for a Fast/Flash-tier coding agent. The future harness architecture is **not selected**.

Pinned canonical Index: `14a2182e2d6d0ecd851cef118906431b2c851aaa` ([commit](https://github.com/opensiro/vsm-harness-index/commit/14a2182e2d6d0ecd851cef118906431b2c851aaa)).

Pinned public OpenSiro Cognee connector: `d176484e85da55c84450d67040cb4a2d096353c7` ([review branch commit](https://github.com/opensiro/cognee-community/commit/d176484e85da55c84450d67040cb4a2d096353c7)); not an upstream release.

Connector compatibility: the pinned branch expects flat `assessments/<id>.md`; the pinned Index now uses `assessments/<first-two-id-characters>/<id>.md`. Exactly one local path check was changed; the patch is in [preflight receipts](../receipts/preflight/connector-shard-compat.patch). This is build-tool compatibility, not a harness mechanism.

## Admission and deterministic selection

Source admission was independently enumerated from the pinned Git tree and manifest: **577 included**, **48 excluded**, **15 proposed**. The manifest at [selection-manifest.json](../receipts/preflight/selection-manifest.json) predetermines **128** included records by sorting all included IDs on `(SHA256(UTF-8 id), id)` and taking the first 128. No task-, name-, or relevance-based prefilter. SHA256 of the newline-separated selected ID list: `f9f5f0edff4da0dc9ea4696e8c9cc54f4f411e9aac5c2a2b92d3f5ba1bdb92ff`.

The public assessment grades are **architectural function/ownership classifications**, not performance measurements. Assessment-level source evidence does not guarantee individual function-to-file provenance.

## Gates

- **Gate 1 pending:** require fresh, actual Cognee import; independent audit of the same dataset; native discovery query receipts with negative/irrelevant hits. An Index grep is not a substitute.
- **Gate 2 pending:** inspect only Cognee-derived candidates against canonical assessments and pinned upstream code; record source evidence and comparisons before choosing mechanisms.
- **No harness `src/` or evaluation claims before the gates.**

All results, including failures, will be added chronologically. The initial verification actions preceded the creation of the trace file and are explicitly labelled in [decision-trace.jsonl](../traces/decision-trace.jsonl); they are not misrepresented as contemporaneous logging.
