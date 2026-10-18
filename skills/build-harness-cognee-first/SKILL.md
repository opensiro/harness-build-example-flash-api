---
name: build-harness-cognee-first
description: Research and build a new AI agent harness by using real Cognee search over pinned Opensiro VSM assessments before selecting an architecture, with source inspection, decision trace, and reproducible evaluation.
---

# Cognee-first harness construction

## Purpose and scope

Use this skill for a *new harness construction* experiment, not for producing or changing a canonical VSM assessment. Choose and implement an architecture from actual build-time research: a defined task, a pinned assessment corpus imported into Cognee, native retrieval, source-backed comparisons, an explicit design decision, then a baseline/adapted evaluation. Cognee must not become an implicit runtime dependency.

This is an **experimental skill local to the example repository**. It does not amend assess-vsm-harness, the VSM Profile, or the Index admission rules. Its historical [Flash API case](references/case-study.md) illustrates process and failure modes, not a recommended architectural outcome.

## Stage 0 — task and source preflight

1. Read the current public [Opensiro bootstrap](https://github.com/opensiro/vsm-oss-organization/blob/main/START_HERE.md) and follow its owning-repository routing.
2. Declare the target task, success/failure criteria, safe execution boundary, model/backend availability, call and cost budgets, evaluation design, and a deliberately minimal baseline *contract*. Do not preselect an adapted mechanism or upstream winners.
3. Pin the Index Git commit, connector commit, assessment/Profile dependency versions, and available public sources. Verify canonical inclusion against the pinned Index. Record all pins and connector fixes. Preserve historical references; do not silently upgrade frozen sources.
4. Plan dataset selection by a stated, reproducible rule **before retrieval**; disclose exclusions and how the selection may miss relevant systems. Prefer broad coverage when feasible, rather than a handpicked shortlist.

## Gate 1 — execute real Cognee discovery

1. Before construction, prepare a **fresh, isolated** Cognee dataset, respecting the connector's fresh-only and failed-attempt restrictions.
2. Import the pinned included assessment records through an actual Cognee source ingestion. Record document identities, counts, hashes, index and connector pins, elapsed time, failures, and importer receipt.
3. Independently audit the resulting dataset's source identity, provenance, graph facts, and exact literal autonomy grades. A failed audit blocks Cognee-dependent claims.
4. Before searching, register task-grounded native queries and at least one useful negative/control query. Run actual native Cognee searches, recording search mode, indexed fields/chunks, all raw hits and ranks, irrelevant results, errors, and empty hits. Do not substitute grep, a cached answer, a mock graph, or a retrospective replay for a passing Cognee-first gate.
5. Explicitly distinguish:
   - **Ingested source:** which full assessment documents are stored.
   - **Indexed retrieval:** exactly which sections/text/fields the search can return.
   - **Later source inspection:** which complete assessments and upstream files are actually read.
   The first example ingested full Markdown but indexed only six S1–S5 function sections for lexical search. Its TLDR.md was not the search corpus. Never present section-only lexical retrieval as full-document search.
6. If a broader architectural search needs full-body indexing, implement and validate it as a **new** experiment/dataset. Do not claim it happened in the historical case. If native ingestion, audit, or search is blocked, stop Gate 1 and report partial work without inventing results.

**Gate 1 pass:** original native import, audit PASS, registered query plan, actual result receipts including negative results, and a documented retrieval coverage boundary.

## Gate 2 — source-backed shortlist and design

1. Only after Gate 1, derive a shortlist from its actual hits. Consider additional public research/GitHub evidence explicitly as *outside-Index sources*, not fabricated indexed hits or VSM grades.
2. Read the **full canonical assessment** for each shortlisted system; then inspect the relevant upstream implementation at its actual pinned reviewed SHA. Record file/line links and evidence for the claimed mechanism. Relevance in one chunk is not implementation proof.
3. Compare task fit, complexity, expected benefit, licensing, failure modes, and available evaluation evidence. Include a no-adaptation baseline, plausible alternatives, and rejected choices. Neither S4 presence nor A/C/P values are performance rankings; feedback inside one task is not automatically S4.
4. Commit/publish a candidate comparison *before* recording the selected mechanism. Select the smallest justified adaptation, or explicitly select none.

**Gate 2 pass:** traceable retrieved hits → complete assessment and pinned GitHub inspection → alternative comparison → recorded decision, in that order. Existing case-study conclusions are not reusable as fresh findings.

## Stage 3 — implementation and measurement

- Build the smallest executable baseline and add only the selected adaptation. A task fixture or baseline scaffold may be prepared before Gate 1, but no adaptation or architecture-choice code before Gates 1 and 2.
- Keep model, initial task, tool surface, resource budgets, and conditions comparable. Log where enforced tests/additional tool calls legitimately make actual usage differ.
- Evaluate with real tests and preserved action/observation receipts. Distinguish offline deterministic checks, scripted doubles, and actual model-backed runs. No fake model/benchmark performance, no statistical claims from a single fixture.
- Preserve implementation and evaluation revisions, failure cases, source permissions/licensing, and exact commands. Do not alter third-party upstream repositories without separate authorization.

## Mandatory observable Decision Trace

Preserve at least: task definition; pinned source and coverage; precommitted dataset/query plan; import/audit; raw native query receipts; shortlisted and rejected candidates; full-source inspection; explicit architectural decision; implementation; baseline/adapted evaluation; and subsequent corrections.

Use an append-only event log with timestamps, source references, decision IDs, rejected options, related commits and artifact paths. Record what was *actually observed*; do not invent hidden reasoning or re-time earlier actions. See [Decision Trace contract](references/decision-trace.md).

## Deliverables and completion

- A task README with reproducible commands and environmental limits.
- Discovery and retrieval-coverage report, source manifest, native import/search results, and audit receipt.
- Source-backed candidate comparison and architecture decision.
- Append-only Decision Trace, links to relevant implementation commits, and baseline/adapted evaluation receipts.
- Explicit PASS / FAIL / NOT RUN statements; a real-model run is NOT RUN until its own receipt exists.

**Full success** requires both Cognee and source-selection gates, implemented baseline/adapted variants, and recorded tests with honest claims. If a gate fails, publish a bounded partial report instead of calling the entire workflow successful.
