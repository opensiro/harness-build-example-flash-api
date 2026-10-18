"""Reproducible evaluation on one synthetic Python dependency upgrade.

Scripted backend demonstrates protocol behavior, NOT any LLM quality uplift.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from flash_repair.agent import (OpenAICompatibleModel, RepairAgent, ScriptedDouble, run_tests)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(backend: str = "scripted", base_url: str = "", model: str = "",
             api_key: str = "", max_calls: int = 3) -> dict:
    project = ROOT / "fixtures/project"
    dependency = ROOT / "fixtures/dependency_v2"
    files = sorted([*project.rglob("*.py"), *dependency.rglob("*.py")])
    receipts = []
    for adapted in (False, True):
        with tempfile.TemporaryDirectory(prefix="flash-dep-repair-") as tmp:
            target = Path(tmp)/"project"
            shutil.copytree(project, target)
            source = (target/"app.py").read_text()
            agent_model = ScriptedDouble() if backend == "scripted" else OpenAICompatibleModel(
                base_url, model, api_key)
            agent = RepairAgent(target, dependency, agent_model,
                                adapted=adapted, max_model_calls=max_calls)
            result = agent.run()
            external_test = run_tests(target, dependency)
            receipts.append({
                "variant": "adapted" if adapted else "baseline",
                "result": result,
                "independent_final_test": external_test,
                "source_before_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "source_after_sha256": file_hash(target/"app.py"),
                "source_after": (target/"app.py").read_text(),
            })
    sha = None
    try:
        sha = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT,
                                      text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, OSError):
        pass
    return {
        "schema_version":1,
        "created_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "backend":backend,
        "model":model if backend != "scripted" else "task-specific scripted double, NOT an LLM",
        "source_git_sha":sha,
        "python_version":platform.python_version(),
        "same_task":True, "same_max_model_calls":max_calls,
        "same_fixed_tool_surface":True,
        "fixture_file_sha256":{str(p.relative_to(ROOT)):file_hash(p) for p in files},
        "note":"Scripted double is deliberately conditional on fresh test feedback. It tests gates and protocol causality, not Fast/Flash model performance.",
        "runs":receipts,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--backend",choices=["scripted","openai"],default="scripted")
    parser.add_argument("--base-url",default=os.environ.get("OPENAI_BASE_URL",""))
    parser.add_argument("--model",default=os.environ.get("OPENAI_MODEL",""))
    parser.add_argument("--api-key-env",default="OPENAI_API_KEY")
    parser.add_argument("--max-calls",type=int,default=3)
    parser.add_argument("--output",default="")
    args=parser.parse_args()
    if args.backend=="openai" and (not args.base_url or not args.model):
        parser.error("openai backend requires --base-url and --model")
    result=evaluate(args.backend,args.base_url,args.model,
                    os.environ.get(args.api_key_env,""),args.max_calls)
    if args.output:
        dest=Path(args.output)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    for run in result["runs"]:
        print(run["variant"],"status",run["result"]["status"],
              "calls",run["result"]["model_calls"],
              "tests",run["result"]["test_runs"],
              "final_pass",run["independent_final_test"]["pass"])
    print("BACKEND",result["backend"],"LLM_UPLIFT_CLAIM",False)


if __name__=="__main__":
    main()
