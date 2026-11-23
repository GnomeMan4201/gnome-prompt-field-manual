"""Bounded timeout tests. No live model calls."""
import inspect
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from reactor_campaign_runner import run_campaign
from reactor_pair_runner import run_pairs
from reactor_local_runner import run_local_ollama_trial
from reactor_evidence_v2 import EvidenceError


def fixtures():
    campaign = json.loads(
        (ROOT / "examples/phase8c/campaign.json").read_text()
    )
    intervention = json.loads(
        (ROOT / "examples/phase8c/intervention.json").read_text()
    )
    return campaign, intervention


class TimeoutContractTests(unittest.TestCase):

    def test_default_timeouts(self):
        self.assertEqual(
            inspect.signature(run_campaign)
            .parameters["timeout"].default,
            120.0
        )
        self.assertEqual(
            inspect.signature(run_pairs)
            .parameters["timeout"].default,
            120.0
        )

    def test_campaign_rejects_invalid_timeouts(self):
        campaign, intervention = fixtures()

        for value in (0, -1, 301, float("nan"), True):
            with self.subTest(timeout=value):
                with self.assertRaisesRegex(
                    EvidenceError, "INVALID_TIMEOUT"
                ):
                    run_campaign(
                        campaign,
                        intervention,
                        "http://127.0.0.1:11434",
                        timeout=value
                    )

    def test_pair_runner_rejects_invalid_timeouts(self):
        campaign, _ = fixtures()

        for value in (0, -1, 301, float("nan"), True):
            with self.subTest(timeout=value):
                with self.assertRaisesRegex(
                    EvidenceError, "INVALID_TIMEOUT"
                ):
                    run_pairs(
                        campaign["plan"],
                        "http://127.0.0.1:11434",
                        "TEST",
                        timeout=value
                    )

    def test_adapter_accepts_300_seconds(self):
        raw = b'{"model":"fixture","response":"ok"}'

        with patch(
            "reactor_local_runner.http.client.HTTPConnection"
        ) as connection:
            response = connection.return_value.getresponse.return_value
            response.status = 200
            response.length = None
            response.read.return_value = raw

            result = run_local_ollama_trial(
                "http://127.0.0.1:11434",
                "fixture",
                "test prompt",
                timeout_seconds=300
            )

            self.assertTrue(result["ok"])
            connection.assert_called_once_with(
                "127.0.0.1", 11434, timeout=300
            )

    def test_adapter_rejects_invalid_timeouts(self):
        for value in (0, -1, 301, float("nan"), True):
            with self.subTest(timeout=value):
                result = run_local_ollama_trial(
                    "http://127.0.0.1:11434",
                    "fixture",
                    "test",
                    timeout_seconds=value
                )
                self.assertEqual(
                    result["errorClass"], "INVALID_TIMEOUT"
                )


if __name__ == "__main__":
    unittest.main()
