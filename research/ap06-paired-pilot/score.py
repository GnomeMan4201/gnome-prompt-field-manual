"""After locking reviewer CSV: python score.py RUN_DIR scores.csv"""
import csv
import json
from pathlib import Path
import sys

run, sheet = map(Path, sys.argv[1:])
protocol = json.loads(Path(__file__).with_name("protocol.json").read_text())
key = dict(zip((case[0] for case in protocol["cases"]), protocol["gold"], strict=True))
mapping = json.loads((run / "mapping.json").read_text())
rows = list(csv.DictReader(sheet.open()))
if len(rows) != len(mapping) or {row["id"] for row in rows} != mapping.keys():
    sys.exit("Missing, duplicate or unknown output ID")
results = {"control": {}, "gnome": {}}
for row in rows:
    case, arm = mapping[row["id"]]
    labels = [row["claim_1"], row["claim_2"]]
    if any(x not in ("S", "R", "U", "X") for x in labels):
        sys.exit("Expected S, R, U or X in each claim column")
    raw = json.loads((run / f"{case}-{arm}.json").read_text())
    hits = sum(a == b for a, b in zip(labels, key[case], strict=True))
    results[arm][case] = hits if raw["exit_code"] == 0 and raw["stdout"].strip() else 0
wins = losses = 0
for case in key:
    control, gnome = (results[arm][case] == 2 for arm in ("control", "gnome"))
    wins += gnome and not control
    losses += control and not gnome
for arm, cases in results.items():
    print(arm, "fully correct", sum(n == 2 for n in cases.values()), "/ 6",
          "correct claims", sum(cases.values()), "/ 12")
print("GNOME minus control fully correct cases:", wins-losses,
      "paired wins:", wins, "losses:", losses, "ties:", len(key)-wins-losses)
