"""Fresh build-time Cognee experiment. No harness code; no architecture selection."""
from __future__ import annotations

import argparse
import asyncio
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import traceback


def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def append_trace(project, data):
    entry = {"recorded_at_utc": timestamp(), **data}
    with (project / "traces" / "decision-trace.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def prepare(args):
    project = Path(__file__).resolve().parents[1]
    connector = Path(args.connector).resolve()
    sys.path.insert(0, str(connector))
    from cognee_community_connector_opensiro_vsm.source import read_snapshot

    manifest = json.loads((project / "receipts/preflight/selection-manifest.json").read_text())
    source = read_snapshot(Path(args.index), manifest["index_sha"])
    selected = tuple(manifest["selected_ids"])
    assert len(selected) == manifest["selected_count"] == 128
    assert all(identifier in source.accepted for identifier in selected)
    assert hashlib.sha256(("\n".join(selected) + "\n").encode()).hexdigest() == manifest["selected_id_list_sha256"]
    store = Path(args.store).resolve()
    if args.phase == "import":
        assert not store.exists(), "Do not reuse a store after any attempt"
        store.mkdir(parents=True)
    else:
        assert store.exists(), "Store not found"
    os.environ.update(
        SYSTEM_ROOT_DIRECTORY=str(store / "system"),
        DATA_ROOT_DIRECTORY=str(store / "data"),
        DLT_DATA_DIR=str(store / "dlt"),
        PIPELINES_DIR=str(store / "dlt/pipelines"),
        COGNEE_SKIP_CONNECTION_TEST="true",
        TELEMETRY_DISABLED="1",
    )
    return project, connector, manifest, source, selected, store


async def do_import(project, manifest, snapshot, selected, store):
    from cognee_community_connector_opensiro_vsm.native import ingest_fresh

    append_trace(project, {
        "type": "cognee_import_started",
        "dataset": manifest["dataset"], "index_sha": snapshot.commit,
        "connector_sha": manifest["connector_review_sha"],
        "selected_count": len(selected),
        "sdk_version": importlib.metadata.version("cognee"),
        "note": "New isolated store; reuse of already installed Cognee SDK code only, no previous Cognee dataset"
    })
    result = await ingest_fresh(
        snapshot=snapshot, selected=selected, dataset=manifest["dataset"],
        tag="opensiro_vsm_canonical_example", lexical=True,
        attempt_root=store / "stage-attempts",
    )
    path = project / "receipts/import/native-import.json"
    write_json(path, {"observed_at_utc": timestamp(), "result": result,
                      "selection_sha256": manifest["selected_id_list_sha256"]})
    append_trace(project, {
        "type": "cognee_import_succeeded",
        "receipt": "receipts/import/native-import.json",
        "documents": result["documents"], "graph_nodes": result["graph_nodes"],
        "exact_grades": result["graded_facts"]
    })
    print(json.dumps(result, ensure_ascii=False), flush=True)


async def do_audit(project, manifest, snapshot, selected):
    from cognee_community_connector_opensiro_vsm.audit import audit_dataset
    audit = await audit_dataset(snapshot, selected, manifest["dataset"],
                                "opensiro_vsm_canonical_example", lexical=True)
    path = project / "receipts/audit/independent-audit.json"
    write_json(path, {"observed_at_utc": timestamp(), "result": audit})
    append_trace(project, {
        "type": "independent_cognee_audit",
        "result_status": audit["status"], "receipt": "receipts/audit/independent-audit.json",
        "documents": audit["documents"], "exact_grades": audit["exact_grades"]
    })
    print(json.dumps(audit, ensure_ascii=False), flush=True)


def as_json(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): as_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [as_json(v) for v in value]
    if hasattr(value, "model_dump"):
        return as_json(value.model_dump(mode="json"))
    if hasattr(value, "__dict__"):
        return as_json(vars(value))
    return repr(value)


async def do_discover(project, manifest):
    from cognee import search
    from cognee.modules.search.types import SearchType

    audit_path = project / "receipts/audit/independent-audit.json"
    audit = json.loads(audit_path.read_text())
    assert audit["result"]["status"] == "PASS", "No discovery before independent audit PASS"
    plan = json.loads((project / "receipts/preflight/query-plan.json").read_text())
    assert plan["dataset"] == manifest["dataset"] and plan["query_type"] == "CHUNKS_LEXICAL"
    receipt_path = project / "receipts/discovery/native-lexical-results.json"
    entries = []
    for item in plan["queries"]:
        append_trace(project, {"type": "native_discovery_query_started",
                               "query_id": item["id"], "mode": "CHUNKS_LEXICAL"})
        try:
            response = await search(query_text=item["text"], query_type=SearchType.CHUNKS_LEXICAL,
                                    datasets=[manifest["dataset"]])
            result = {"query_id": item["id"], "query": item["text"],
                      "intent": item["intent"], "query_type": "CHUNKS_LEXICAL",
                      "observed_at_utc": timestamp(), "status": "RETURNED",
                      "raw_response": as_json(response)}
        except Exception as error:
            result = {"query_id": item["id"], "query": item["text"],
                      "intent": item["intent"], "query_type": "CHUNKS_LEXICAL",
                      "observed_at_utc": timestamp(), "status": "ERROR",
                      "error_type": type(error).__name__, "error": str(error)}
        entries.append(result)
        write_json(receipt_path, {"schema_version": 1, "dataset": manifest["dataset"],
                    "plan": "receipts/preflight/query-plan.json", "completed_queries": len(entries),
                    "results": entries})
        append_trace(project, {"type": "native_discovery_query_finished",
                               "query_id": item["id"], "status": result["status"],
                               "receipt": "receipts/discovery/native-lexical-results.json"})
        print(item["id"], result["status"], flush=True)
    assert len(entries) == len(plan["queries"])
    print("NATIVE_DISCOVERY_RECORDED",len(entries),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["import", "audit", "discover"])
    parser.add_argument("--index", required=True)
    parser.add_argument("--connector", required=True)
    parser.add_argument("--store", required=True)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    try:
        project, connector, manifest, source, selected, store = prepare(args)
        if args.phase == "import":
            asyncio.run(do_import(project, manifest, source, selected, store))
        elif args.phase == "audit":
            asyncio.run(do_audit(project, manifest, source, selected))
        else:
            asyncio.run(do_discover(project, manifest))
    except Exception as error:
        path = project / "receipts" / args.phase / "failure.json"
        write_json(path, {"observed_at_utc": timestamp(), "stage": args.phase,
                          "status": "FAILED", "exception_type": type(error).__name__,
                          "error": str(error), "traceback": traceback.format_exc()})
        append_trace(project, {"type": args.phase + "_failed",
                              "receipt": str(path.relative_to(project)), "status": "FAILED",
                              "exception_type": type(error).__name__, "error": str(error),
                              "gate1": "BLOCKED"})
        raise


if __name__ == "__main__":
    main()
