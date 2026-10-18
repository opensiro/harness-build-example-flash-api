# Architecture decision — AFTER Cognee discovery and source comparison

**Decision recorded after:** public [native Cognee discovery](../receipts/discovery/native-lexical-results.json), independent [audit](../receipts/audit/independent-audit.json), and [candidate comparison](../reports/candidate-comparison.md) at commit `751ba427c0e04170e7768cc4b9131af0b288cf4d`.

## Chosen single adaptation

**Observed post-mutation test-evidence gate with bounded corrective feedback**, derived from the verified [Carbon harness agent](https://github.com/thecarbonlayer/carbon/blob/8fafacd56f10a6eeb6f3b095fa6af3dfb5681aaf/harness/agent.py#L498-L537) (found through Cognee D01 #4), with a fixed Python test runner motivated by [NemoCode's Python tooling](https://github.com/SampleBias/nemocode/blob/6f5489f289d0963cf0c6b7562c9491670000ccd2/src/python_tools.rs#L14-L35). This is **one adaptation**: test-evidence gating of completion, not two independent extensions. Carbon's wider agent runtime and NemoCode's Rust stack are not dependencies or copied implementations.

- Same minimal S1 agent and deterministic tool surface in baseline and adapted.
- After every actual file mutation, adapted runs the workspace's **fixed** Python test command, records exit code and bounded output, and feeds failure evidence into the next ordinary agent step, up to the same `max_model_calls` budget.
- A change is considered **verified** only if a passing test result was observed *after the latest mutation*. A completion claim without it remains unverified; exhausted call/test budget is an explicit failure, not silently accepted.
- Baseline offers a test tool but has no enforced post-mutation test gate. It may or may not run tests on its own.
- `Cognee` is never imported into harness runtime.

## Rejections, based on public comparison

Separate model verifiers from oh-my-claudecode and Metis would require additional independent models and complex handoffs; DynamicWorkflow adds multiagent orchestration; Hankweave/Zhi retry-policy machinery addresses transient failures rather than test-correctness after a source change. These are not needed for a small deterministic repair exercise.

## Bounded construction contract

- Single workspace, one editable Python file, fixed read/replace/test operations, no arbitrary shell or unrestricted command execution.
- Same task, tool definitions and max-call budget for baseline/adapted. Both can target an OpenAI-compatible chat-completions endpoint; local scripted test-double verifies the protocol only.
- No performance-uplift claim from scripted tests; a real Fast/Flash model run is separate and optional depending on available credentials/runtime.
- The fixture is a *synthetic offline* Python dependency-v2 API change, not a claim about a real upstream package regression.
- Record exact observed test results, source and fixture hashes, and important negatives/failures. The gate is a deterministic supporting primitive; it does not establish first-party autonomous VSM S3* in this new harness.

**Gate 2:** Source comparison and rationale published before any harness code. Implementation may now begin. Do not rewrite the earlier Decision Trace.
