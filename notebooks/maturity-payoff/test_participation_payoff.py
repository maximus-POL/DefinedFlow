"""Independent numerical, input-contract, CLI, and saved-notebook checks."""

import importlib.util
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parent / "participation_payoff.py"
spec = importlib.util.spec_from_file_location("participation_payoff", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
payment = module.maturity_payment


class ParticipationPayoffTests(unittest.TestCase):
    def test_notebook_cells_run_in_order_and_match_displayed_outputs(self):
        notebook = json.loads((SOURCE.parent / "maturity_payoff.ipynb").read_text())
        cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
        self.assertEqual(len(cells), 6)
        namespace = {}
        with patch.dict(sys.modules, {"participation_payoff": module}):
            for index, cell in enumerate(cells, 1):
                with self.subTest(cell=index):
                    self.assertEqual(cell["execution_count"], index)
                    captured = StringIO()
                    with redirect_stdout(captured):
                        exec(compile("".join(cell["source"]), f"notebook-cell-{index}", "exec"), namespace)
                    for output in cell["outputs"]:
                        self.assertEqual(output["output_type"], "stream")
                        self.assertEqual(output["name"], "stdout")
                    expected = "".join("".join(output["text"]) for output in cell["outputs"])
                    self.assertEqual(captured.getvalue(), expected)
        self.assertEqual(namespace["result"], payment("1000", "100", "120", "0.8"))
        self.assertEqual(namespace["exercise_payment"], "1150.00")

    def test_downside_flat_upside(self):
        for final, expected in [("80", "1000.00"), ("100", "1000.00"), ("120", "1160.00")]:
            with self.subTest(final=final):
                self.assertEqual(payment("1000", "100", final, "0.8"), expected)

    def test_at_and_around_payoff_boundary(self):
        for final, expected in [("99.99", "1000.00"), ("100", "1000.00"), ("100.01", "1000.08")]:
            with self.subTest(final=final):
                self.assertEqual(payment("1000", "100", final, "0.8"), expected)

    def test_zero_final_and_zero_participation(self):
        self.assertEqual(payment("1000", "100", "0", "0.8"), "1000.00")
        self.assertEqual(payment("1000", "100", "120", "0"), "1000.00")

    def test_full_participation(self):
        self.assertEqual(payment("1000", "100", "125", "1"), "1250.00")

    def test_exact_half_cent_rounds_up_only_at_end(self):
        self.assertEqual(payment("1", "1", "1.005", "1"), "1.01")
        self.assertEqual(payment("1", "1", "1.004999", "1"), "1.00")
        self.assertEqual(payment("1", "1", "1.005001", "1"), "1.01")
        self.assertEqual(payment("1", "3", "4", "1"), "1.33")
        self.assertEqual(payment("1", "3", "5", "1"), "1.67")

    def test_decimal_principal_and_no_intermediate_rounding(self):
        self.assertEqual(payment("1000.25", "100", "120", "0.8"), "1160.29")
        self.assertEqual(payment("3", "3", "4.005", "1"), "4.01")

    def test_documented_input_extremes(self):
        self.assertEqual(payment("1000000000", "0.000001", "1000000000", "1"), "1000000000000000000000000.00")
        self.assertEqual(payment("0.000001", "1", "0", "0"), "0.00")

    def test_invalid_decimal_forms_in_every_position(self):
        for invalid in ["", " ", "1 ", "-1", "+1", "NaN", "Infinity", "1e2", "0.0000001", "1,000", "١", "1000000001", 1, 0.8, None, True]:
            for position in range(4):
                args = ["1000", "100", "120", "0.8"]
                args[position] = invalid
                with self.subTest(invalid=invalid, position=position):
                    with self.assertRaises(ValueError):
                        payment(*args)

    def test_invalid_domains(self):
        for args in [("0", "100", "120", "0.8"), ("1000", "0", "120", "0.8"), ("1000", "100", "120", "1.000001")]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    payment(*args)

    def test_cli_output_and_failure(self):
        success = subprocess.run([sys.executable, str(SOURCE), "1000", "100", "120", "0.8"], capture_output=True, text=True)
        self.assertEqual(success.returncode, 0)
        self.assertEqual(success.stdout, "1160.00\n")
        failure = subprocess.run([sys.executable, str(SOURCE), "1000", "0", "120", "0.8"], capture_output=True, text=True)
        self.assertEqual(failure.returncode, 2)
        self.assertEqual(failure.stdout, "")
        self.assertIn("must be positive", failure.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
