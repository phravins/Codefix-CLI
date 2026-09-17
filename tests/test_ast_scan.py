import unittest
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pkg_dir = os.path.join(root_dir, "Codefix-CLI-main", "src")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

from debugger.ast_scan import scan as root_scan
from codefixcli.debugger.ast_scan import scan as pkg_scan

class TestASTScan(unittest.TestCase):
    def test_unused_imports(self):
        code = """
import sys
import math
from os import path, getcwd

x = sys.version
y = getcwd()
"""
        for scan_fn in (root_scan, pkg_scan):
            res = scan_fn(code)
            self.assertTrue(res["ok"])
            issues = res["issues"]
            unused = [i["message"] for i in issues if i["kind"] == "unused_import"]
            self.assertIn("Unused import: 'math'", unused)
            self.assertIn("Unused import: 'path'", unused)
            self.assertNotIn("Unused import: 'sys'", unused)
            self.assertNotIn("Unused import: 'getcwd'", unused)

    def test_used_imports_alias(self):
        code = """
import numpy as np
from datetime import datetime as dt

x = np.array([])
y = dt.now()
"""
        for scan_fn in (root_scan, pkg_scan):
            res = scan_fn(code)
            self.assertTrue(res["ok"])
            unused = [i["message"] for i in res["issues"] if i["kind"] == "unused_import"]
            self.assertEqual(len(unused), 0)

    def test_syntax_error(self):
        for scan_fn in (root_scan, pkg_scan):
            res = scan_fn("def foo(:")
            self.assertFalse(res["ok"])
            self.assertIn("syntax_error", res)

    def test_clean_code(self):
        code = "a = 1\nb = a + 1"
        for scan_fn in (root_scan, pkg_scan):
            res = scan_fn(code)
            self.assertTrue(res["ok"])
            self.assertEqual(len(res["issues"]), 0)

if __name__ == "__main__":
    unittest.main()
