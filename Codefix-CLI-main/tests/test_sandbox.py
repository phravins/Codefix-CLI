from unittest.mock import patch
import subprocess
from codefixcli.debugger.sandbox import run_in_sandbox


def test_sandbox_success():
    code = "print('Hello from sandbox')"
    res = run_in_sandbox(code, timeout=5)
    assert res["ok"] is True
    assert res["returncode"] == 0
    assert "Hello from sandbox" in res["stdout"]
    assert res["stderr"] == ""
    assert isinstance(res["elapsed"], float)


def test_sandbox_timeout_mocked():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["python"], timeout=1)):
        res = run_in_sandbox("import time; time.sleep(10)", timeout=1)
        assert res["ok"] is False
        assert res["timeout"] is True
        assert res["elapsed"] == 1


def test_sandbox_timeout_real():
    code = "import time; time.sleep(5)"
    timeout = 0.1
    res = run_in_sandbox(code, timeout=timeout)
    assert res["ok"] is False
    assert res["timeout"] is True
    assert res["elapsed"] == timeout


def test_sandbox_runtime_error():
    code = "x = 1 / 0"
    res = run_in_sandbox(code, timeout=5)
    assert res["ok"] is True
    assert res["returncode"] != 0
    assert "ZeroDivisionError" in res["stderr"]


def test_sandbox_general_exception():
    with patch("subprocess.run", side_effect=Exception("Unexpected subprocess error")):
        res = run_in_sandbox("print('hi')", timeout=5)
        assert res["ok"] is False
        assert res["error"] == "Unexpected subprocess error"
        assert res["elapsed"] == 0
