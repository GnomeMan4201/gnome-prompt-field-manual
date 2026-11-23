"""Local provider evidence capture tests; no live inference."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"tests"))

from reactor_local_runner import run_local_ollama_trial
from reactor_pair_runner import run_pairs
from test_reactor_evidence_v2 import plan


RAW=b'{"model":"fixture-model","response":"{\\"answer\\":\\"42\\"}","done":true}'


class RawProviderEvidenceTests(unittest.TestCase):

    def test_adapter_preserves_exact_request_and_response(self):
        with patch(
            "reactor_local_runner.http.client.HTTPConnection"
        ) as connection:
            instance=connection.return_value
            response=instance.getresponse.return_value
            response.status=200
            response.length=None
            response.read.return_value=RAW

            result=run_local_ollama_trial(
                "http://127.0.0.1:11434",
                "fixture-model",
                "Question?",
                temperature=0,
                seed=42
            )

            self.assertTrue(result["ok"])
            self.assertEqual(result["rawResponse"].encode(),RAW)

            sent=instance.request.call_args.kwargs["body"]
            self.assertEqual(result["rawRequest"].encode(),sent)
            self.assertEqual(
                json.loads(sent)["options"],
                {"temperature":0,"seed":42}
            )

    def test_pair_binds_provider_bytes_and_hashes(self):
        p=plan()
        p["provider"]="ollama-local"
        p["model"]="fixture-model"

        with patch(
            "reactor_local_runner.http.client.HTTPConnection"
        ) as connection:
            instance=connection.return_value
            response=instance.getresponse.return_value
            response.status=200
            response.length=None
            response.read.return_value=RAW

            execution=run_pairs(
                p,
                "http://127.0.0.1:11434",
                "RAW-TEST"
            )

        self.assertTrue(execution["executionComplete"])
        self.assertEqual(len(execution["observations"]),2)

        for observation in execution["observations"]:
            evidence=observation["executionProvenance"]["providerEvidence"]

            self.assertEqual(
                hashlib.sha256(evidence["requestText"].encode()).hexdigest(),
                evidence["requestSha256"]
            )
            self.assertEqual(
                hashlib.sha256(evidence["responseText"].encode()).hexdigest(),
                evidence["responseSha256"]
            )
            self.assertEqual(
                json.loads(evidence["responseText"])["response"],
                observation["outputText"]
            )


if __name__=="__main__":
    unittest.main()
