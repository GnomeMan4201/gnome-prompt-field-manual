"""Run from this directory: python collect.py LLAMA_CLI GGUF NEW_OUTPUT_DIR"""
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
from uuid import uuid4

binary, model, output = map(Path, sys.argv[1:])
binary, model = binary.resolve(), model.resolve()
protocol = json.loads(Path(__file__).with_name("protocol.json").read_text())
with model.open("rb") as stream:
    assert hashlib.file_digest(stream, "sha256").hexdigest() == protocol["model_sha256"]
output.mkdir(exist_ok=False)
env = dict(os.environ, LD_LIBRARY_PATH=str(binary.parent))
blind = []
mapping = {}
for index, (case, source, submission) in enumerate(protocol["cases"]):
    first = protocol["order"][index]
    for arm in (first, "gnome" if first == "control" else "control"):
        question = "\n\n".join([protocol[arm], protocol["shared"], source, submission])
        prompt = "<|im_start|>user\n" + question + "<|im_end|>\n<|im_start|>assistant\n"
        args = ["--no-conversation", "--no-display-prompt", "--simple-io", "--log-disable",
                "--no-warmup", "--temp", "0", "--seed", "42", "-t", "2", "-c", "2048",
                "-n", "256", "-m", str(model), "-p", prompt]
        started = time.monotonic()
        try:
            proc = subprocess.run([str(binary), *args], env=env, stdin=subprocess.DEVNULL,
                                  capture_output=True, timeout=180)
            stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr, code = error.stdout or b"", error.stderr or b"", 124
        label = uuid4().hex[:12]
        mapping[label] = [case, arm]
        raw = {"case": case, "arm": arm, "prompt": prompt, "exit_code": code,
               "elapsed_seconds": round(time.monotonic()-started, 3),
               "stdout": stdout.decode(), "stderr": stderr.decode()}
        (output / f"{case}-{arm}.json").write_text(json.dumps(raw, indent=2)+"\n")
        blind.append({"id": label, "source": source, "submission": submission,
                      "output": raw["stdout"], "exit_code": code})
secrets.SystemRandom().shuffle(blind)
for name, data in [("blind", blind), ("mapping", mapping)]:
    (output / (name+".json")).write_text(json.dumps(data, indent=2)+"\n")
