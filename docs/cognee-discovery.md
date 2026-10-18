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

- **Gate 1 PASS (actual fresh execution):** 128 included documents; [native import](../receipts/import/native-import.json) generated 2,661 graph nodes/1,765 edges/768 VSM facts; independent [audit PASS](../receipts/audit/independent-audit.json); all seven pre-registered [native lexical queries](../receipts/discovery/native-lexical-results.json) returned 15 hits each, including irrelevant negative-control hits. An Index grep was not substituted.
- **Gate 2 PASS (chronological evidence):** [post-Cognee shortlist](../reports/post-discovery-shortlist.md) and [published pinned upstream source comparison](../reports/candidate-comparison.md) at `751ba427c0e04170e7768cc4b9131af0b288cf4d` preceded [architecture selection](architecture-decision.md) and implementation.
- **Build followed both gates:** harness implementation and [actual offline evaluation](../reports/evaluation.md) occurred after Stage 1 receipts, pinned upstream comparison, and separate architecture-decision commit; real model-backed evaluation remains **NOT RUN**.

All results, including failures, will be added chronologically. The initial verification actions preceded the creation of the trace file and are explicitly labelled in [decision-trace.jsonl](../traces/decision-trace.jsonl); they are not misrepresented as contemporaneous logging.


## Actual Stage 1 execution and limitations

The dedicated fresh Cognee store was instantiated in CPU-VM RAM storage, with Cognee 1.6.4 and a **reused installed SDK only**, not a preexisting graph/dataset. The SDK was reused to avoid re-downloading large dependencies; the dataset, source snapshots, imported data and query receipts were newly generated. The local Index SHA, public connector branch SHA and disclosed compatibility patch were validated before import.

Native import completed in 40.913 seconds with 128 documents, 2,661 typed nodes, 1,765 edges, 768 exact six-function facts and 768 section chunks. The independent audit was a separate process and read-only over the new Cognee store; its checks included source IDs, graph nodes/edges, grades, owner refs and exact source provenance.

Seven `SearchType.CHUNKS_LEXICAL` queries were executed via Cognee's public native SDK. All seven returned 15 chunks. **Negative control did NOT return zero**; it matched generic vocabulary including `mechanics`. Both raw native responses and the post-result annotated hit index are retained; a local overlap count is neither Cognee's score nor performance evidence.

For standalone reproduction with the pinned local checkout and connector patch applied:

```bash
python tools/stage1.py import --index /path/to/index --connector /path/to/connector/packages/connector/opensiro-vsm --store /new/empty/store
python tools/stage1.py audit --index /path/to/index --connector /path/to/connector/packages/connector/opensiro-vsm --store /new/empty/store
python tools/stage1.py discover --index /path/to/index --connector /path/to/connector/packages/connector/opensiro-vsm --store /new/empty/store
```

Use the project-pinned selection manifest and Cognee 1.6.4; `--store` must start absent for import and be reused **only** for the read-only audit and discovery. Do not rerun ingestion against the same dataset. The default `CHUNKS_LEXICAL` mode uses no embeddings/paid LLM; it is not a semantic proof of candidate suitability.
