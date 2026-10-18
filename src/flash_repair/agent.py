"""Tiny Python dependency-repair agent.

One mutable source file; JSON actions; fixed, bounded subprocess test runner.
Cognee is intentionally absent from runtime.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
from typing import Any


SYSTEM = (
    "You are repairing a small Python project against a dependency API change. "
    'Output exactly one valid JSON object per turn, no Markdown fences. '
    'Valid actions: {"action":"read","path":"app.py"}, '
    '{"action":"replace","path":"app.py","old":"exact old text","new":"replacement"}, '
    '{"action":"run_tests"}, or {"action":"finish","summary":"..."}.'
    "Only app.py can be read/edited. Prefer running tests after editing. "
    "When a test fails, use the actual error as evidence to repair it. "
    "Never claim success without evidence."
)
MAX_OUTPUT = 8000


class ToolRejected(ValueError):
    pass


class ScriptedDouble:
    """Task-specific protocol fixture; NOT an LLM performance proxy."""

    def __init__(self):
        self.calls = 0

    def complete(self, messages: list[dict[str, str]]) -> dict[str, str]:
        self.calls += 1
        if self.calls == 1:
            return {"action": "replace", "path": "app.py",
                    "old": "from stringcase import to_snake",
                    "new": "from stringcase import snake_case"}
        feedback = "\n".join(m["content"] for m in messages if m["role"] == "user")
        if "TEST_RESULT FAIL" in feedback and "TEST_RESULT PASS" not in feedback:
            return {"action": "replace", "path": "app.py",
                    "old": "return to_snake(value)", "new": "return snake_case(value)"}
        return {"action": "finish", "summary": "Proposed compatibility repair complete."}


class OpenAICompatibleModel:
    """Standard chat completions with JSON-in-content (no vendor tool API)."""

    def __init__(self, base_url: str, model: str, api_key: str = ""):
        if not base_url.startswith(("https://", "http://")):
            raise ValueError("base_url must be HTTP(S)")
        if not model:
            raise ValueError("model is required")
        self.endpoint = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self.api_key = api_key

    def complete(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        body = json.dumps({"model": self.model, "messages": messages}).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key
        request = urllib.request.Request(self.endpoint, body, headers, method="POST")
        with urllib.request.urlopen(request, timeout=30) as resp:
            reply = json.load(resp)
        text = reply["choices"][0]["message"]["content"]
        if not isinstance(text, str):
            raise ValueError("Model returned no JSON text content")
        value = json.loads(text)
        if not isinstance(value, dict):
            raise ValueError("Model action must be an object")
        return value


def target_file(workspace: Path, name: str) -> Path:
    if name != "app.py":
        raise ToolRejected("Only app.py is admitted; arbitrary paths are blocked")
    path = (workspace / name).resolve()
    if path.parent != workspace.resolve() or path.is_symlink():
        raise ToolRejected("Target must be a non-symlink file directly in workspace")
    return path


def run_tests(workspace: Path, dependency_root: Path, *, timeout: int = 10) -> dict[str, Any]:
    # Fixed command (no shell), fixed synthetic dependency root, scrubbed environment.
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.pathsep.join((str(dependency_root.resolve()), str(workspace.resolve()))),
        "PYTHONDONTWRITEBYTECODE": "1",
        "HOME": str(workspace.resolve()),
        "LANG": "C.UTF-8",
    }
    try:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=workspace, env=env, capture_output=True, text=True, timeout=timeout,
            check=False,
        )
        return {
            "pass": result.returncode == 0,
            "exit_code": result.returncode,
            "timed_out": False,
            "stdout": result.stdout[-MAX_OUTPUT:],
            "stderr": result.stderr[-MAX_OUTPUT:],
        }
    except subprocess.TimeoutExpired as error:
        return {"pass": False, "exit_code": None, "timed_out": True,
                "stdout": str(error.stdout or "")[-MAX_OUTPUT:],
                "stderr": str(error.stderr or "")[-MAX_OUTPUT:]}


def test_feedback(result: dict[str, Any]) -> str:
    status = "PASS" if result["pass"] else "FAIL"
    return ("TEST_RESULT " + status + "\n" +
            json.dumps(result, ensure_ascii=False, sort_keys=True))


class RepairAgent:
    def __init__(self, workspace: Path, dependency_root: Path, model: Any,
                 *, adapted: bool = False, max_model_calls: int = 3):
        if max_model_calls < 1:
            raise ValueError("max_model_calls must be >= 1")
        self.workspace = workspace.resolve()
        self.dependency_root = dependency_root.resolve()
        self.model = model
        self.adapted = adapted
        self.max_model_calls = max_model_calls
        self.mutation_version = 0
        self.passed_version: int | None = None
        self.calls = 0
        self.test_runs = 0
        self.actions: list[dict[str, Any]] = []

    def fresh_pass(self) -> bool:
        return self.passed_version == self.mutation_version and self.passed_version is not None

    def _record_test(self) -> str:
        result = run_tests(self.workspace, self.dependency_root)
        self.test_runs += 1
        self.passed_version = self.mutation_version if result["pass"] else None
        self.actions.append({"action": "run_tests", "result": result,
                             "after_mutation": self.mutation_version,
                             "automatic_gate": self.adapted})
        return test_feedback(result)

    def _action(self, proposal: dict[str, Any]) -> str:
        kind = proposal.get("action")
        if kind == "read":
            path = target_file(self.workspace, proposal.get("path", ""))
            self.actions.append({"action": "read", "path": "app.py"})
            return "FILE_CONTENT\n" + path.read_text()[:MAX_OUTPUT]
        if kind == "replace":
            path = target_file(self.workspace, proposal.get("path", ""))
            old, new = proposal.get("old"), proposal.get("new")
            if not isinstance(old, str) or not isinstance(new, str) or not old:
                raise ToolRejected("replace requires non-empty old and string new")
            if len(old) > MAX_OUTPUT or len(new) > MAX_OUTPUT:
                raise ToolRejected("edit span exceeds tool budget")
            previous = path.read_text()
            if previous.count(old) != 1:
                raise ToolRejected("replace must match exactly once")
            path.write_text(previous.replace(old, new, 1))
            self.mutation_version += 1
            self.passed_version = None  # invalidate even a previously passing test
            self.actions.append({"action": "replace", "version": self.mutation_version,
                                 "old": old, "new": new})
            feedback = "EDIT_APPLIED mutation_version=" + str(self.mutation_version)
            if self.adapted:
                feedback += "\n" + self._record_test()
            return feedback
        if kind == "run_tests":
            return self._record_test()
        raise ToolRejected("unknown or forbidden action " + repr(kind))

    def run(self) -> dict[str, Any]:
        context = target_file(self.workspace, "app.py").read_text()
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content":
                        "Repair the Python project after dependency version 2 removed to_snake. "
                        "Tests are in tests/. Current app.py:\n" + context}]
        status = "budget_exhausted"
        summary = ""
        for _ in range(self.max_model_calls):
            self.calls += 1
            proposal: dict[str, Any] = {}
            try:
                proposal = self.model.complete(messages)
                if not isinstance(proposal, dict):
                    raise ToolRejected("Model result must be JSON object")
                if proposal.get("action") == "finish":
                    summary = str(proposal.get("summary", ""))[:1000]
                    status = ("verified_complete" if self.adapted and self.fresh_pass()
                              else "complete_unverified")
                    break
                response = self._action(proposal)
            except (ToolRejected, ValueError, TypeError, KeyError) as error:
                response = "TOOL_ERROR " + type(error).__name__ + ": " + str(error)
                self.actions.append({"action": "rejected", "error": response})
            messages.append({"role": "assistant", "content": json.dumps(proposal)})
            messages.append({"role": "user", "content": response})
        if self.adapted and self.mutation_version > 0 and not self.fresh_pass():
            if status == "budget_exhausted":
                status = "budget_exhausted_unverified"
        return {
            "status": status, "verified": status == "verified_complete",
            "adapted": self.adapted, "max_model_calls": self.max_model_calls,
            "model_calls": self.calls, "test_runs": self.test_runs,
            "mutations": self.mutation_version, "actions": self.actions,
            "summary": summary,
        }
