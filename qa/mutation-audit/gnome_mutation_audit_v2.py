"""GNOME verification mutation audit, baseline-controlled and scratch-only.
Run with Python 3.11+ against a clean, trusted Git checkout. Validators execute
repository code; use a disposable, offline environment. No result implies
semantic correctness or independent empirical reproduction.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time


def sub(path, old, new, count=1, both_readers=False):
    def f(root):
        files = [path] if not both_readers else ["index.html", "GNOME-Field-Manual.html"]
        for p in files:
            fp = root / p
            s = fp.read_text(encoding="utf-8")
            if s.count(old) != count:
                raise ValueError(f"{p}: expected {count} exact targets; found {s.count(old)}")
            fp.write_text(s.replace(old, new, count), encoding="utf-8")
    return f


def delete(path):
    def f(root):
        (root / path).unlink()
    return f


def json_edit(path, fn):
    def f(root):
        fp = root / path
        d = json.loads(fp.read_text(encoding="utf-8"))
        fn(d)
        fp.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f


def set_first_decision(d):
    d["entries"][0]["exclusions"][0]["decision"] = "ACCEPT_EXCLUSION"   # completed state, reviewer still null

def evidence_answer(d):
    d["observedAnswers"]["exact"][1] = "18ms"

def evidence_hash(d):
    k = next(iter(d["sourceBundles"])); h = d["sourceBundles"][k]["manifestSha256"]
    d["sourceBundles"][k]["manifestSha256"] = ("0" if h[0] != "0" else "1") + h[1:]

def body_verified(d):
    d["entries"][0]["bodyStatus"] = "VERIFIED"

MUTATIONS = [
    ("M01", "modified canonical text", "Semantic inversion of T-05 premise, canonical reader only",
     sub("index.html", "executed. It has failed badly.", "executed. It has succeeded.")),
    ("M02", "modified canonical text", "Same inversion applied consistently to BOTH readers",
     sub(None, "executed. It has failed badly.", "executed. It has succeeded.", both_readers=True)),
    ("M03", "broken cross-reference", "T-01 follow-up routed to T-09 (wrong ID, right name) in both readers",
     sub(None, "Run T-03 (Assumption Ledger)", "Run T-09 (Assumption Ledger)", both_readers=True)),
    ("M04", "broken page reference", "SEC-02 follow-up points SEC-09 at page 903 (nonexistent) in both readers",
     sub(None, "Indirect Injection Tracer, page 203", "Indirect Injection Tracer, page 903", both_readers=True)),
    ("M05", "invalid hash", "Phase VIII-C evidence-index manifest SHA-256 altered",
     json_edit("research/phase8c-qwen-0p5b/evidence-index.json", evidence_hash)),
    ("M06", "invalid research result", "Phase VIII-C recorded attack answer changed 999ms -> 18ms in evidence index",
     json_edit("research/phase8c-qwen-0p5b/evidence-index.json", evidence_answer)),
    ("M07", "invalid research result", "RESULTS.md exact-request sequence rewritten to all-18ms",
     sub("research/phase8c-qwen-0p5b/RESULTS.md", "Exact-request control/attack/attack/control: `['18ms', '999ms', '999ms', '18ms']`",
         "Exact-request control/attack/attack/control: `['18ms', '18ms', '18ms', '18ms']`")),
    ("M08", "missing evidence", "Delete SEC-05 unresolved-evidence record linked from index.html",
     delete("docs/BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md")),
    ("M09", "contradictory verification label", "current_body_review.json: T-01 bodyStatus PARTIAL -> VERIFIED",
     json_edit("workbench/data/current_body_review.json", body_verified)),
    ("M10", "incorrect adjudication state", "adjudication_queue.json: first decision completed with reviewer=null",
     json_edit("workbench/data/adjudication_queue.json", set_first_decision)),
    ("M11", "broken navigation", "Standalone reader: remove id=page-directory anchor target",
     sub("GNOME-Field-Manual.html", 'id="page-directory"', 'id="page-directory-x"')),
    ("M12", "missing publication asset", "Delete README banner image",
     delete("DC177E5E-70E7-4DED-A59D-469F51E607C0.png")),
    ("M13", "contradictory documentation", "README entry counts changed to 3 pending",
     sub("README.md", "reconciles to 1 pending ID", "reconciles to 3 pending IDs")),
    ("M14", "replication protocol tamper", "Phase VIII-D locked protocol temperature 0 -> 0.7",
     sub("research/phase8d-independent-replication/kit/protocol.json", '"temperature": 0', '"temperature": 0.7')),
    ("M15", "malformed metadata", "Identity index: T-04 title replaced with 'Concept Compression'",
     sub("workbench/data/current_entry_identity_index.json", '"titleCandidate": "(Weakest Link Isolator) on the highest-severity weakest link selected"', '"titleCandidate": "Concept Compression"')),
    ("M16", "correct fix (control)", "Fix known defect p.273 P-05 (RFC) -> P-07 (RFC Draft Generator), both readers",
     sub(None, "or P-05 (RFC):", "or P-07 (RFC Draft Generator):", both_readers=True)),
]

def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def extract_snapshot(src, expected, dest):
    head = git(src, "rev-parse", "HEAD").decode().strip()
    if head != expected:
        raise ValueError(f"HEAD {head} does not match expected commit {expected}")
    if git(src, "status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("source checkout is not clean")
    archive = git(src, "archive", "--format=tar", head)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        members = tf.getmembers()
        for m in members:
            if not (m.isfile() or m.isdir()) or not (dest / m.name).resolve().is_relative_to(dest):
                raise ValueError(f"unsafe archive member: {m.name}")
        tf.extractall(dest, members=members, filter="data")
    # A git archive alone cannot execute lineage tests that call git show/ls-tree.
    # Clone locally without hard links or alternates; retain independently copied
    # Git metadata alongside the validated archive, with no remote configured.
    with tempfile.TemporaryDirectory(prefix="gnome-history-") as tmp:
        clone = Path(tmp) / "repo"
        subprocess.run(["git", "clone", "--no-local", "--no-hardlinks", "--no-checkout",
                        str(src), str(clone)], check=True, capture_output=True)
        git(clone, "update-ref", "--no-deref", "HEAD", head)
        git(clone, "read-tree", head)
        git(clone, "remote", "remove", "origin")
        if git(clone, "rev-parse", "--is-shallow-repository").strip() != b"false":
            raise ValueError("complete Git history required")
        shutil.move(str(clone / ".git"), str(dest / ".git"))
    if git(dest, "rev-parse", "HEAD").decode().strip() != head:
        raise ValueError("scratch history HEAD mismatch")
    if git(dest, "status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("archive and scratch Git tree disagree")
    return head


def hashes(root):
    result = {}
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for name in sorted(files):
            p = Path(directory) / name
            if p.is_file():
                result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def run(cmd, cwd, timeout):
    started = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           errors="replace", timeout=timeout)
        out = p.stdout + "\n" + p.stderr
        if cmd[1:3] == ["-m", "unittest"]:
            # unittest prints tracebacks for ordinary assertion failures too.
            # Require an actual nonempty, zero-skip suite and distinguish
            # assertion failures from import/runtime errors.
            ran = re.search(r"^Ran ([1-9][0-9]*) tests? in ", out, re.M)
            ok = re.search(r"^OK\s*$", out, re.M)
            failed = re.search(r"^FAILED \(failures=([1-9][0-9]*)\)\s*$", out, re.M)
            if ran and p.returncode == 0 and ok:
                state = "PASS"
            elif ran and p.returncode == 1 and failed and not re.search(r"^ERROR:", out, re.M):
                state = "REJECTED_UNREVIEWED"
            else:
                state = "ERROR"
        elif p.returncode == 0:
            state = "PASS"
        elif (p.returncode != 1 or "Traceback (most recent call last)" in out
              or re.search(r"^ERROR:", out, re.M)):
            state = "ERROR"
        else:
            # A clean nonzero exit still requires human inspection for relevance.
            state = "REJECTED_UNREVIEWED"
        return {"state": state, "returncode": p.returncode, "output": out,
                "command": cmd, "seconds": round(time.monotonic()-started, 3)}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"state": "ERROR", "returncode": None, "output": str(exc), "command": cmd}


def assess(root, reports, timeout):
    reports.mkdir()
    py = sys.executable
    def report(n, ext): return str(reports / f"{n}.{ext}")
    specs = {
        "unittest": ([py, "-m", "unittest", "discover", "-s", "tests"], root),
        "validate_manual": ([py, "tools/validate_manual.py", "--input", "index.html", "--json", report("manual", "json"), "--markdown", report("manual", "md"), "--strict-warnings"], root),
        "reconcile_lineage": ([py, "tools/reconcile_entry_lineage.py", "--input", "index.html", "--json", report("lineage", "json"), "--markdown", report("lineage", "md"), "--expect-pending", "1", "--expect-drafted", "90", "--expect-total", "91", "--expect-pages", "315", "--enforce"], root),
        "audit_editorial": ([py, "tools/audit_editorial_lineage.py", "--input", "index.html", "--json", report("editorial", "json"), "--markdown", report("editorial", "md")], root),
        "body_review_verify": ([py, "tools/build_current_body_review.py", "--verify"], root),
        "kit_lock": (["sha256sum", "-c", "LOCK.sha256"], root / "research/phase8d-independent-replication/kit"),
    }
    if (root / "tools/check_subject_references.py").exists():
        specs["subject_reference_gate"] = ([py, "tools/check_subject_references.py", "--input", "index.html", "--input", "GNOME-Field-Manual.html", "--baseline", "qa/subject_reference_baseline.json"], root)
    results = {name: run(cmd, cwd, timeout) for name, (cmd, cwd) in specs.items()}
    results["generated_reports"] = {p.name: p.read_text(errors="replace") for p in reports.iterdir() if p.is_file()}
    return results


def verdict(baseline, current, control=False):
    base = {k:v["state"] for k,v in baseline.items() if k != "generated_reports"}
    now = {k:v["state"] for k,v in current.items() if k != "generated_reports"}
    if base.keys() != now.keys() or any(v != "PASS" for v in base.values()):
        return "INCONCLUSIVE_BASELINE"
    if any(v == "ERROR" for v in now.values()):
        return "INCONCLUSIVE_CHECK_ERROR"
    if any(v == "REJECTED_UNREVIEWED" for v in now.values()):
        return "CONTROL_REJECTED_REVIEW_REQUIRED" if control else "REJECTED_REVIEW_REQUIRED"
    return "CONTROL_ACCEPTED" if control else "SURVIVED_TESTED_CHECKS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--only", help="comma-separated mutation IDs")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    src, out = args.repo.resolve(), args.out.resolve()
    if out.is_relative_to(src): parser.error("output must be outside source checkout")
    if out.exists(): parser.error("refusing to overwrite output")
    if args.timeout <= 0: parser.error("timeout must be positive")
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit): parser.error("full commit SHA required")
    selected = set(args.only.split(",")) if args.only else {m[0] for m in MUTATIONS}
    if not selected or selected - {m[0] for m in MUTATIONS}: parser.error("unknown mutation ID")
    result = {"schema": "gnome.mutation-audit.v2", "commit": args.commit,
              "scope": "selected local checks; no browser, semantic, or empirical assurance",
              "baseline": None, "mutations": [], "missing_optional_checks": []}
    def save():
        # Exclusive first creation; subsequent updates are to this audit's file only.
        with out.open("x" if result["baseline"] is None else "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2); f.write("\n")
    with tempfile.TemporaryDirectory(prefix="gnome-mutation-") as tmp:
        temp = Path(tmp); snapshot = temp / "snapshot"; snapshot.mkdir()
        extract_snapshot(src, args.commit, snapshot)
        pristine = hashes(snapshot)
        save()
        base_root = temp / "base"; shutil.copytree(snapshot, base_root)
        baseline = assess(base_root, temp / "base-reports", args.timeout)
        result["baseline"] = baseline
        if "subject_reference_gate" not in baseline: result["missing_optional_checks"].append("subject_reference_gate")
        save()
        if any(v["state"] != "PASS" for k,v in baseline.items() if k != "generated_reports"):
            if hashes(snapshot) != pristine or git(src, "status", "--porcelain", "--untracked-files=all").strip() or git(src,"rev-parse","HEAD").decode().strip() != args.commit:
                raise RuntimeError("source integrity check failed")
            result["source_checkout_unchanged"] = True; save()
            print("Baseline failed; no mutation verdicts issued.", file=sys.stderr); return 2
        for mid, cat, desc, mutate in MUTATIONS:
            if mid not in selected: continue
            root = temp / mid; shutil.copytree(snapshot, root)
            record = {"id": mid, "category": cat, "description": desc, "control": mid == "M16"}
            try:
                mutate(root)
                after = hashes(root)
                changes = {k:{"before":pristine.get(k), "after":after.get(k)} for k in sorted(pristine.keys() | after.keys()) if pristine.get(k) != after.get(k)}
                if not changes: raise ValueError("mutation made no byte changes")
                record["changes"] = changes
            except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
                record.update(verdict="NOT_APPLIED", error=str(exc))
            else:
                record["checks"] = assess(root, temp / (mid + "-reports"), args.timeout)
                record["verdict"] = verdict(baseline, record["checks"], record["control"])
            result["mutations"].append(record); save()
            print(mid, record["verdict"], flush=True)
            shutil.rmtree(root)
        if hashes(snapshot) != pristine or git(src, "status", "--porcelain", "--untracked-files=all").strip() or git(src,"rev-parse","HEAD").decode().strip() != args.commit:
            raise RuntimeError("source integrity check failed")
    result["source_checkout_unchanged"] = True; save()
    # This audit never automatically counts an unreviewed rejection as a killed mutant.
    return 0 if all(r["verdict"] in {"REJECTED_REVIEW_REQUIRED", "CONTROL_ACCEPTED"} for r in result["mutations"]) else 1


if __name__ == "__main__":
    sys.exit(main())
