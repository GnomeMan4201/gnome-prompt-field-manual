import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from reactor_engine import validate_experiment  # noqa: E402


class TestReactorExperiments(unittest.TestCase):
    def test_rejects_missing_hypothesis_and_empty_inputs(self):
        errs = validate_experiment({"schemaVersion": "gnome.reactor.experiment.v1", "hypothesis": "", "rubric": {}, "dataset": {"inputs": []}})
        self.assertIn("MISSING_HYPOTHESIS", errs)
        self.assertIn("INVALID_SCORING_RUBRIC", errs)
        self.assertIn("EMPTY_INPUT_SET", errs)

    def test_rejects_duplicate_input_id(self):
        errs = validate_experiment({
            "schemaVersion": "gnome.reactor.experiment.v1",
            "hypothesis": "Evidence boundary reduces interpolation.",
            "rubric": {"criteria": ["cite_source"]},
            "dataset": {"inputs": [{"inputId": "I-1"}, {"inputId": "I-1"}]},
        })
        self.assertIn("DUPLICATE_INPUT_ID:I-1", errs)


if __name__ == "__main__":
    unittest.main()
