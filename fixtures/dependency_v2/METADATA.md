# Synthetic dependency v2

This is a local, offline **test fixture**, not a released package or performance benchmark.

Version 1 exposed `stringcase.to_snake`. Version 2 removes that function and exposes `stringcase.snake_case`. A Python project retains its v1 import and call after its dependency is upgraded. The test requires a correct repair of both usage sites. PYTHONPATH points to this local v2 fixture; no network/package installation is needed.
