import os
import subprocess
import sys
import unittest
from pathlib import Path


PROGRAM_DIR = Path(__file__).resolve().parents[1]
DRIVER = PROGRAM_DIR / "Driver.py"


class DriverTests(unittest.TestCase):
    def run_driver(self, fixture, *arguments):
        environment = os.environ.copy()
        environment.pop("GITHUB_TOKEN", None)
        environment.pop("VERCEL_TOKEN", None)
        return subprocess.run(
            [sys.executable, str(DRIVER), str(Path(__file__).parent / fixture), *arguments],
            cwd=PROGRAM_DIR,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_dry_run_generates_escaped_html(self):
        result = self.run_driver("valid.sl", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = PROGRAM_DIR / "generated" / "index.html"
        self.assertTrue(output.exists())
        html = output.read_text(encoding="utf-8")
        self.assertIn("Contenido &lt;seguro&gt;", html)
        self.assertIn("No external API calls were made", result.stdout)

    def test_syntax_error_stops_compilation(self):
        result = self.run_driver("invalid_syntax.sl", "--dry-run")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Syntax error", result.stderr)
        self.assertIn("before any external API call", result.stderr)

    def test_semantic_error_stops_compilation(self):
        result = self.run_driver("invalid_semantics.sl", "--dry-run")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Semantic error", result.stderr)
        self.assertIn("before any external API call", result.stderr)

    def test_missing_credentials_return_usage_error(self):
        result = self.run_driver("valid.sl")
        self.assertEqual(result.returncode, 2)
        self.assertIn("GITHUB_TOKEN and VERCEL_TOKEN", result.stderr)


if __name__ == "__main__":
    unittest.main()
