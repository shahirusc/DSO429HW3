# DSO 429 · Homework 3 · The Hourly Quiz

Automated pipeline that answers every round of the hourly quiz.

- `solver.py` – recognises each question template, computes the exact answer, and picks the closest option.
- `run.py` – downloads `questions.csv`, answers every released round, writes `answers/round-NNNN.json`.
- `test_practice.py` – checks the solver against the practice keys (1200/1200 correct on rounds 1–48).
- `.github/workflows/answer.yml` – GitHub Actions job that runs every 5 minutes and pushes new answer files to `main`.
