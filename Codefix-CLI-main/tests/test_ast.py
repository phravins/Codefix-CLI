from codefixcli.debugger.ast_scan import scan

def test_syntax_error():
    res = scan("if True")
    assert res["ok"] is False

def test_clean_code():
    res = scan("x = 10\ny = x")
    assert res["ok"] is True
    assert len(res["issues"]) == 0

def test_unused_import():
    res = scan("import sys\nx = 10\ny = x")
    assert res["ok"] is True
    assert len(res["issues"]) == 1
    assert res["issues"][0]["kind"] == "unused_import"
    assert "sys" in res["issues"][0]["message"]
