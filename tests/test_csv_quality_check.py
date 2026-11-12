import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from csv_quality_check import profile


class ProfileTests(unittest.TestCase):
    def write_csv(self, contents):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "input.csv"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_distinguishes_blanks_from_malformed_records(self):
        path = self.write_csv('id,value\n1,  \n2\n3,"line 1\nline 2"\n4,x,extra\n')
        report = profile(path)
        self.assertEqual((report["rows"], report["valid_rows"], report["invalid_rows"]), (4, 2, 2))
        self.assertEqual(report["columns"][1]["blank_cells"], 1)
        self.assertEqual([item["start_line"] for item in report["invalid_examples"]], [3, 6])

    def test_keeps_positions_when_headers_repeat(self):
        report = profile(self.write_csv("\ufeffid;id; \n;1;2\n"), ";")
        self.assertEqual(report["duplicate_headers"], ["id"])
        self.assertEqual(report["blank_headers"], [3])
        self.assertEqual([column["blank_cells"] for column in report["columns"]], [1, 0, 0])

    def test_reports_invalid_quotes(self):
        with self.assertRaisesRegex(ValueError, "satır 2"):
            profile(self.write_csv('id,value\n1,"incomplete'))

    def test_cli_emits_json_and_fails_for_shape_issues(self):
        script = Path(__file__).resolve().parents[1] / "csv_quality_check.py"
        path = self.write_csv("id,value\n1\n")
        run = subprocess.run(
            [sys.executable, str(script), str(path), "--json", "--fail-on-issues"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(json.loads(run.stdout)["invalid_rows"], 1)
