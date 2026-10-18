import pathlib
import sys
import tempfile
import shutil
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
sys.path.insert(0, str(ROOT/"evaluation"))

from flash_repair.agent import RepairAgent, ScriptedDouble, ToolRejected, target_file, run_tests
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


if __name__=="__main__":
    unittest.main()
