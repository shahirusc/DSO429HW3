"""Check solver.py against the published practice keys (rounds 1-48)."""
import csv
import sys

from solver import solve

questions, keys = sys.argv[1], sys.argv[2]
key = {(r["round_id"], r["q_index"]): r["answer"] for r in csv.DictReader(open(keys))}
right = wrong = unsure = 0
for r in csv.DictReader(open(questions)):
    k = (r["round_id"], r["q_index"])
    opts = [r[f"option_{c}"] for c in "abcd"]
    ans, conf = solve(r["question_text"], opts)
    if not conf:
        unsure += 1
    if k not in key:
        if not conf:
            print("UNSURE graded", k, r["question_text"], opts, ans)
        continue
    if ans == key[k]:
        right += 1
    else:
        wrong += 1
        print("WRONG", k, r["question_text"], opts, "got", ans, "key", key[k])
print(f"practice: {right} right, {wrong} wrong; low-confidence overall: {unsure}")
