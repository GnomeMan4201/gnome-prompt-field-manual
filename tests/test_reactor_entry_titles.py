"""Reactor entry labels: display headings are source-bound and match the manuscript.

Expected headings come from the standalone reader's static pages, a different surface
and parser from the canonical <pre> scan that produced the candidate packet. Display
titles name entries only; they do not verify bodies.
"""
import html
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "workbench/data/current_entry_identity_index.json"
PACKET = ROOT / "workbench/data/current_body_review.json"
READER = ROOT / "GNOME-Field-Manual.html"
ADAPTER = "./workbench/reactor/source-adapter.js"
STATIC = re.compile(r'<article class="book-page(?: print-spacer)?" id="page-(\d+)">(.*?)</article>', re.S)
BLOCK = re.compile(r'<(?:div class="source-block"|p class="flowing")>(.*?)</(?:div|p)>', re.S)


def static_headings(raw, ids):
    """Heading = an ID+title block immediately followed by a Criteria block."""
    found = {}
    for page, body in STATIC.findall(raw):
        blocks = [html.unescape(re.sub(r"<[^>]+>", "", b)).strip() for b in BLOCK.findall(body)]
        for i, block in enumerate(blocks):
            m = re.fullmatch(r"([A-Z]{1,5}-\d{2})\s+(\S.*)", block, re.S)
            if m and m[1] in ids and i + 1 < len(blocks) and re.match(r"Criteria\s*:", blocks[i + 1]):
                found.setdefault(m[1], []).append((int(page), " ".join(m[2].split())))
    return found


def heading_errors(expected, packet_rows):
    """IDs whose packet heading or heading page differs from the manuscript."""
    errors = {}
    for row in packet_rows:
        want = expected.get(row["entryId"], [])
        got = (row["start"]["page"], row["canonicalHeadingCandidate"])
        if want != [got]:
            errors[row["entryId"]] = {"expected": want, "packet": got}
    return errors


def run_adapter(identity, packet, script):
    """Load the real adapter in Node with fetch serving the two data files by path."""
    js = f"""
const files={{'../data/current_entry_identity_index.json':{json.dumps(identity)},'../data/current_body_review.json':{json.dumps(packet)}}};
globalThis.fetch=async p=>p in files&&files[p]!==null?{{ok:true,json:async()=>files[p]}}:{{ok:false,status:404}};
require('{ADAPTER}');const A=globalThis.ReactorSourceAdapter;
(async()=>{{try{{{script}}}catch(e){{console.log(JSON.stringify({{error:e.message}}));}}}})();"""
    out = subprocess.run(["node", "-"], input=js, cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


LOAD = "const x=await A.loadIndex();console.log(JSON.stringify({status:x.headingStatus,source:x.headingSource,verified:x.verifiedBodies,entries:x.entries.map(e=>({id:e.id,title:e.title,label:A.displayTitle(e),ref:A.buildSourceReference(e,false)}))}));"


class ReactorEntryTitles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.identity = json.loads(IDENTITY.read_text())
        cls.packet = json.loads(PACKET.read_text())
        cls.ids = [e["id"] for e in cls.identity["entries"]]
        cls.expected = static_headings(READER.read_text(encoding="utf-8"), set(cls.ids))

    def test_packet_headings_match_the_manuscript_for_every_id(self):
        self.assertEqual(len(self.ids), 91)
        self.assertEqual(sorted(self.expected), sorted(self.ids))
        errors = heading_errors(self.expected, self.packet["entries"])
        self.assertFalse(errors, f"packet heading differs from the manuscript for {sorted(errors)}: {errors}")

    def test_named_entries_and_distinct_titles(self):
        want = {"AP-04": "Scope Inflation Catch", "R-07": "Competing Hypotheses Table",
                "AP-06": "Passage Evidence Review", "SEC-08": "Collection Evidence Audit",
                "W-04": "Over-Smoothing Detector", "AP-01": "Over-Smoothing Publication Gate"}
        self.assertEqual({k: self.expected[k][0][1] for k in want}, want)
        # Every entry now has its own heading, so a title identifies one ID.
        by_title = {}
        for entry_id, [(page, title)] in self.expected.items():
            if entry_id in self.ids:
                by_title.setdefault(title, []).append(entry_id)
        shared = {t: ids for t, ids in by_title.items() if len(ids) > 1}
        self.assertFalse(shared, f"entries sharing a heading: {shared}")

    def test_adapter_displays_the_bound_heading_for_every_id(self):
        result = run_adapter(self.identity, self.packet, LOAD)
        self.assertEqual(result["status"], "BOUND")
        self.assertIn("canonicalHeadingCandidate", result["source"])
        self.assertEqual(result["verified"], 0)
        shown = {e["id"]: e["label"] for e in result["entries"]}
        self.assertEqual(list(shown), self.ids)
        wrong = {i: (shown[i], self.expected[i][0][1]) for i in self.ids if shown[i] != self.expected[i][0][1]}
        self.assertFalse(wrong, f"wrong Reactor labels for {sorted(wrong)}: {wrong}")

    def test_exports_keep_the_advisory_title_and_id(self):
        result = run_adapter(self.identity, self.packet, LOAD)
        advisory = {e["id"]: (e["titleCandidate"], e["titleAuthority"], e["status"]) for e in self.identity["entries"]}
        for entry in result["entries"]:
            ref = entry["ref"]
            with self.subTest(entry=entry["id"]):
                self.assertEqual(ref["entryId"], entry["id"])
                self.assertEqual((ref["titleCandidate"], ref["titleAuthority"], ref["editorialStatus"]), advisory[entry["id"]])
                self.assertEqual(ref["bodyStatus"], "UNVERIFIED_SOURCE_CANDIDATE")
                self.assertFalse(ref["inheritsCanonicalVerification"])

    def test_missing_or_stale_heading_source_is_visible(self):
        stale = json.loads(json.dumps(self.packet))
        stale["sourceHtmlSha256"] = "0" * 64
        other = json.loads(json.dumps(self.packet))
        other["entries"][0]["advisoryIdentityTitle"] = "built from another identity index"
        swapped = json.loads(json.dumps(self.packet))
        rows = {r["entryId"]: r for r in swapped["entries"]}
        rows["AP-04"]["canonicalHeadingCandidate"] = "Competing Hypotheses Table"
        cases = {"missing": (None, "HEADING_SOURCE_FETCH_FAILED:404"),
                 "stale": (stale, "PACKET_SOURCE_STALE"),
                 "other identity": (other, "PACKET_IDENTITY_MISMATCH:" + other["entries"][0]["entryId"]),
                 "heading not from its declaration line": (swapped, "PACKET_HEADING_INVALID:AP-04")}
        for name, (packet, status) in cases.items():
            with self.subTest(case=name):
                result = run_adapter(self.identity, packet, LOAD)
                self.assertEqual(result["status"], status)
                self.assertIsNone(result["source"])
                self.assertTrue(all(e["title"] is None for e in result["entries"]))
                self.assertTrue(all(e["label"].startswith("heading unavailable; advisory candidate: ") for e in result["entries"]))
                self.assertEqual([e["id"] for e in result["entries"]], self.ids)

    def test_release_state_unchanged(self):
        self.assertEqual(self.identity["bodyCoverage"], 0)
        self.assertEqual(self.packet["counts"]["VERIFIED"], 0)
        pending = [e["id"] for e in self.identity["entries"] if e["status"] == "PENDING"]
        self.assertEqual(pending, ["SEC-05"])
        self.assertEqual((ROOT / "VERSION").read_text().strip(), "1.0.0-rc.1")


if __name__ == "__main__":
    unittest.main()
