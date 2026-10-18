import pathlib
import sys
import tempfile
import shutil
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
sys.path.insert(0, str(ROOT/"evaluation"))

from flash_repair.agent import RepairAgent, ScriptedDouble, OpenAICompatibleModel, ToolRejected, target_file, run_tests
from run_evaluation import evaluate


class RealFixtureTests(unittest.TestCase):
    def test_initial_upgraded_dependency_is_broken(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace=pathlib.Path(tmp)/"project"
            shutil.copytree(ROOT/"fixtures/project", workspace)
            r=run_tests(workspace, ROOT/"fixtures/dependency_v2")
            self.assertFalse(r["pass"])
            self.assertIn("ImportError",r["stderr"])

    def test_baseline_and_adapted_protocol(self):
        receipt=evaluate()
        baseline, adapted=receipt["runs"]
        self.assertEqual(receipt["same_max_model_calls"],3)
        self.assertEqual(baseline["result"]["max_model_calls"],adapted["result"]["max_model_calls"])
        self.assertEqual(baseline["variant"],"baseline")
        self.assertEqual(adapted["variant"],"adapted")
        self.assertFalse(baseline["independent_final_test"]["pass"])
        self.assertTrue(adapted["independent_final_test"]["pass"])
        self.assertFalse(baseline["result"]["verified"])
        self.assertTrue(adapted["result"]["verified"])
        self.assertEqual(baseline["result"]["model_calls"],2)
        self.assertEqual(adapted["result"]["model_calls"],3)
        self.assertEqual(adapted["result"]["mutations"],2)
        self.assertEqual(adapted["result"]["test_runs"],2)
        self.assertTrue(any(not a["result"]["pass"] for a in adapted["result"]["actions"] if a["action"]=="run_tests"))

    def test_invalid_target_path_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ToolRejected):
                target_file(pathlib.Path(tmp), "../outside.py")

    def test_same_workspace_symlink_target_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = pathlib.Path(tmp)
            (workspace / "other.py").write_text("must not edit")
            (workspace / "app.py").symlink_to("other.py")
            with self.assertRaises(ToolRejected):
                target_file(workspace, "app.py")
            self.assertEqual((workspace / "other.py").read_text(), "must not edit")

    def test_stale_pass_invalidated(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace=pathlib.Path(tmp)/"project"
            shutil.copytree(ROOT/"fixtures/project",workspace)
            agent=RepairAgent(workspace,ROOT/"fixtures/dependency_v2", ScriptedDouble(),adapted=True)
            agent.mutation_version=1
            agent.passed_version=1
            self.assertTrue(agent.fresh_pass())
            agent.mutation_version=2
            self.assertFalse(agent.fresh_pass())

    def test_call_cap_cannot_claim_verified(self):
        class NeverFinish:
            def complete(self, messages):
                return {"action":"read","path":"app.py"}
        with tempfile.TemporaryDirectory() as tmp:
            workspace=pathlib.Path(tmp)/"project"
            shutil.copytree(ROOT/"fixtures/project",workspace)
            agent=RepairAgent(workspace,ROOT/"fixtures/dependency_v2",
                              NeverFinish(),adapted=True,max_model_calls=3)
            r=agent.run()
            self.assertEqual(r["model_calls"],3)
            self.assertFalse(r["verified"])
            self.assertEqual(r["status"],"budget_exhausted")


    def test_budget_exhaustion_not_verified_even_after_passing_test(self):
        class RefuseToFinish(ScriptedDouble):
            def complete(self, messages):
                proposal=super().complete(messages)
                if proposal["action"]=="finish":
                    return {"action":"read","path":"app.py"}
                return proposal
        with tempfile.TemporaryDirectory() as tmp:
            workspace=pathlib.Path(tmp)/"project"
            shutil.copytree(ROOT/"fixtures/project",workspace)
            a=RepairAgent(workspace,ROOT/"fixtures/dependency_v2",
                          RefuseToFinish(),adapted=True,max_model_calls=3)
            r=a.run()
            self.assertEqual(r["status"],"budget_exhausted")
            self.assertFalse(r["verified"])
            self.assertEqual(r["test_runs"],2)

    def test_malformed_model_payload_does_not_crash(self):
        class InvalidThenFinish:
            def __init__(self):
                self.calls=0
            def complete(self,messages):
                self.calls += 1
                if self.calls==1:
                    raise ValueError("invalid JSON")
                return {"action":"finish","summary":"Cannot repair"}
        with tempfile.TemporaryDirectory() as tmp:
            workspace=pathlib.Path(tmp)/"project"
            shutil.copytree(ROOT/"fixtures/project",workspace)
            result=RepairAgent(workspace,ROOT/"fixtures/dependency_v2",
                               InvalidThenFinish(),adapted=True,max_model_calls=2).run()
            self.assertEqual(result["status"],"complete_unverified")
            self.assertFalse(result["verified"])
            self.assertTrue(any(x["action"]=="rejected" for x in result["actions"]))

    def test_openai_compatible_chat_completions_http_shape(self):
        import json
        import threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        observations=[]
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                size=int(self.headers["Content-Length"])
                payload=json.loads(self.rfile.read(size))
                observations.append((self.path,payload))
                content=json.dumps({"action":"finish","summary":"offline HTTP fixture"})
                body=json.dumps({"choices":[{"message":{"content":content}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Content-Length",str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self,*args):
                pass
        srv=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        worker=threading.Thread(target=srv.serve_forever,daemon=True)
        worker.start()
        try:
            cli=OpenAICompatibleModel(f"http://127.0.0.1:{srv.server_port}/v1","test-model")
            reply=cli.complete([{"role":"user","content":"test"}])
            self.assertEqual(reply["action"],"finish")
            self.assertEqual(observations[0][0],"/v1/chat/completions")
            self.assertEqual(observations[0][1]["model"],"test-model")
        finally:
            srv.shutdown()
            srv.server_close()
            worker.join(timeout=2)


if __name__=="__main__":
    unittest.main()
