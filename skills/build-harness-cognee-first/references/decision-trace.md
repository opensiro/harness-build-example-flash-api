# Observable Decision Trace contract (experimental)

This reference belongs to the build-harness-cognee-first skill, **not** to the canonical VSM assessment format.

## Minimal event envelope

Use newline-delimited JSON in traces/decision-trace.jsonl, written append-only. Event types may vary, but meaningful decisions and observations should contain:

- event ID, event type, observation/recording timestamp (UTC), and experiment/run identity;
- task/problem being addressed, current gate/stage, and status;
- relevant source identity and pinned Git SHA/assessment content digest;
- input artifact references (native import/query/evaluation receipts) and output artifact references;
- candidate alternatives and externally inspectable reasons for selection/rejection **when an explicit design decision is made**;
- linked commit or file change and evaluation outcome as the workflow proceeds;
- explicit uncertainty, failures, and limitations.

Not every event needs every field: an import event records dataset facts; an architecture_decision event records considered options; a model-run event records backend and execution evidence.

## Required chronology

1. Problem, constraints, and precommitted source/query plan.
2. Actual Cognee import → independent audit → native queries, including raw negative hits.
3. Post-search candidates → full assessment reading → pinned upstream code comparison.
4. Recorded decision and rejections → adapted implementation.
5. Reproducible baseline/adapted test receipts → late corrections and reviews.

Keep previously published receipts immutable. For corrections append a new event pointing to the superseded record; never silently overwrite or fabricate the earlier state. If a trace starts after an action, label the entry as **retrospective record**, not contemporaneous evidence.

## Three search coverage fields

Always report source_ingested_scope, lexical_or_semantic_index_scope, and inspected_source_scope separately.

Example (historical Flash API case, not a template for every implementation):

- source_ingested_scope: 128 complete pinned assessment Markdown files.
- lexical_or_semantic_index_scope: six VSM function sections per assessment (768 DocumentChunks), CHUNKS_LEXICAL only.
- inspected_source_scope: selected full assessments and upstream files at pinned reviewed SHA.

Do not equate imported raw documents to an automatically searchable full-document index.

## Verification

The auditor should be able to follow receipt references and Git history in both directions: source → evidence → alternative comparison → decision → code change → test outcome. If a receipt or chronology gate is missing, mark it incomplete.
