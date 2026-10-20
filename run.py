"""Fetch questions.csv, answer every round that has no answer file yet, write answers/round-NNNN.json.

Usage: python run.py [path-or-url-to-questions.csv]
Exits non-zero if any question could not be solved confidently (so the Actions run shows red),
but still writes a best-guess file so no round is ever missing.
"""
import csv
import io
import json
import os
import sys
import urllib.request
from collections import defaultdict

from solver import solve

URL = "https://raw.githubusercontent.com/FaisalXL/dso429-hourly-quiz/main/questions.csv"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "answers")


def load(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"Cache-Control": "no-cache"})
        text = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    else:
        text = open(src, encoding="utf-8").read()
    return list(csv.DictReader(io.StringIO(text)))


def main():
    rows = load(sys.argv[1] if len(sys.argv) > 1 else URL)
    rounds = defaultdict(list)
    for r in rows:
        rounds[int(r["round_id"])].append(r)

    os.makedirs(OUT, exist_ok=True)
    problems = []
    written = 0
    for rid in sorted(rounds):
        path = os.path.join(OUT, f"round-{rid:04d}.json")
        answers = {}
        for r in sorted(rounds[rid], key=lambda r: int(r["q_index"])):
            opts = [r[f"option_{c}"] for c in "abcd"]
            ans, conf = solve(r["question_text"], opts)
            if not conf:
                problems.append(f"round {rid} q{r['q_index']}: {r['question_text']} {opts} -> {ans}")
            answers[f"q{int(r['q_index'])}"] = ans or "A"
        data = {"round_id": rid, "answers": answers}
        new = json.dumps(data, indent=2) + "\n"
        old = open(path).read() if os.path.exists(path) else None
        if old != new:
            with open(path, "w") as f:
                f.write(new)
            written += 1
    print(f"{len(rounds)} rounds seen, {written} files written/updated")
    if problems:
        print("LOW CONFIDENCE:\n" + "\n".join(problems))
        sys.exit(1)


if __name__ == "__main__":
    main()
