"""Deterministic solver for the DSO 429 Hourly Quiz.

Each question is matched against a known template, the exact answer is
computed, and the option numerically closest to it is chosen.
"""
import re
from datetime import datetime, timedelta

NUM = r"([\d,]+(?:\.\d+)?)"


def n(s):
    return float(s.replace(",", ""))


def parse_option(s):
    """Turn '$1,234.50', '12.5%', '1,533 units', '-15.1%' into a float."""
    m = re.search(r"-?[\d,]*\.?\d+", s.replace("$", ""))
    return n(m.group(0)) if m else None


def compute(q):
    """Return (kind, value). kind is 'num' or 'date'."""
    m = re.search(rf"investment of \${NUM} grows at {NUM}% compounded annually.*after {NUM} years", q)
    if m:
        p, r, t = n(m[1]), n(m[2]) / 100, n(m[3])
        return "num", p * (1 + r) ** t

    m = re.search(rf"generates \${NUM} in revenue against \${NUM} in cost of goods sold", q)
    if m:
        rev, cogs = n(m[1]), n(m[2])
        return "num", (rev - cogs) / rev * 100

    m = re.search(r"series runs ([\d,\s.-]+?)\. If the pattern", q)
    if m:
        xs = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", m[1])]
        diffs = {round(b - a, 9) for a, b in zip(xs, xs[1:])}
        if len(diffs) == 1:
            return "num", xs[-1] + diffs.pop()
        if all(x != 0 for x in xs):
            ratios = {round(b / a, 9) for a, b in zip(xs, xs[1:])}
            if len(ratios) == 1:
                return "num", xs[-1] * ratios.pop()
        # second differences (quadratic)
        d1 = [b - a for a, b in zip(xs, xs[1:])]
        d2 = {round(b - a, 9) for a, b in zip(d1, d1[1:])}
        if len(d2) == 1:
            return "num", xs[-1] + d1[-1] + d2.pop()
        # Fibonacci-like
        if all(abs(xs[i] - xs[i - 1] - xs[i - 2]) < 1e-9 for i in range(2, len(xs))):
            return "num", xs[-1] + xs[-2]
        return None

    m = re.search(rf"listed at \${NUM} is discounted by {NUM}%", q)
    if m:
        return "num", n(m[1]) * (1 - n(m[2]) / 100)

    m = re.search(rf"invoice for \${NUM} is converted to euros at {NUM} euros per US dollar", q)
    if m:
        return "num", n(m[1]) * n(m[2])

    m = re.search(rf"sells {NUM} units at \${NUM} each", q)
    if m:
        return "num", n(m[1]) * n(m[2])

    m = re.search(rf"Fixed costs are \${NUM}\. Each unit sells for \${NUM} with a variable cost of \${NUM}", q)
    if m:
        f, p, v = n(m[1]), n(m[2]), n(m[3])
        return "num", round(f / (p - v))

    m = re.search(rf"moved from \${NUM} to \${NUM}", q)
    if m:
        a, b = n(m[1]), n(m[2])
        return "num", (b - a) / a * 100

    m = re.search(rf"Region A had {NUM} orders averaging \${NUM}; region B had {NUM} orders averaging \${NUM}", q)
    if m:
        a, pa, b, pb = map(n, m.groups())
        return "num", (a * pa + b * pb) / (a + b)

    m = re.search(rf"holds {NUM} billing tickets, {NUM} technical tickets and {NUM} account tickets", q)
    if m:
        b, t, a = map(n, m.groups())
        return "num", b / (b + t + a) * 100

    m = re.search(rf"\${NUM} marketing budget is split between two channels in the ratio {NUM}:{NUM}", q)
    if m:
        total, x, y = map(n, m.groups())
        return "num", total * x / (x + y)

    m = re.search(r"signed on (\d{1,2} \w+ \d{4}) has a ([\d,]+)-day settlement period", q)
    if m:
        d = datetime.strptime(m[1], "%d %B %Y") + timedelta(days=int(n(m[2])))
        return "date", d

    return None


def parse_date(s):
    try:
        return datetime.strptime(s.strip(), "%d %B %Y")
    except ValueError:
        return None


def solve(q, options):
    """Return (letter, confident: bool)."""
    letters = "ABCD"
    res = compute(q)
    if res is None:
        return None, False
    kind, val = res
    if kind == "date":
        for L, o in zip(letters, options):
            if parse_date(o) == val:
                return L, True
        return None, False
    best, best_err, best_tol = None, float("inf"), 0
    for L, o in zip(letters, options):
        x = parse_option(o)
        if x is None:
            continue
        err = abs(x - val)
        if err < best_err:
            m = re.search(r"\.(\d+)", o)
            tol = 0.5 * 10 ** -(len(m[1]) if m else 0) + 1e-6
            best, best_err, best_tol = L, err, tol
    return best, best is not None and best_err <= best_tol
