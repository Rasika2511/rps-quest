# check_rps.py
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import NoReturn, Optional

OK = "\N{WHITE HEAVY CHECK MARK}"
BAD = "\N{CROSS MARK}"

RPS = ("rock", "paper", "scissors")
EXPECTED = {
    ("rock", "rock"): "draw",
    ("rock", "paper"): "lose",
    ("rock", "scissors"): "win",
    ("paper", "rock"): "win",
    ("paper", "paper"): "draw",
    ("paper", "scissors"): "lose",
    ("scissors", "rock"): "lose",
    ("scissors", "paper"): "win",
    ("scissors", "scissors"): "draw",
}


def load_decide_winner(fn: str = "rps.py"):
    p = Path(fn)
    if not p.exists():
        fail(f"Could not find {fn}.")
    src = p.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=fn)
    target = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "decide_winner":
            target = node
            break
    if target is None:
        fail("Missing function: decide_winner(user: str, cpu: str) -> str")
    if len(target.args.args) != 2:
        fail("decide_winner must take exactly two arguments: (user, cpu)")
    mod = ast.Module(body=[target], type_ignores=[])
    code = compile(mod, filename=fn, mode="exec")
    ns: dict[str, object] = {}
    exec(code, ns)
    func = ns.get("decide_winner")
    if not callable(func):
        fail("decide_winner is not callable.")
    return func  # type: ignore[return-value]


def run_cli_once(inp: str, timeout: float = 2.5):
    """Run rps.py once, feed 'inp\\n', capture output."""
    if not Path("rps.py").exists():
        fail("rps.py not found in current directory.")
    try:
        res = subprocess.run(
            [sys.executable, "rps.py"],
            input=inp + "\n",
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return res
    except subprocess.TimeoutExpired:
        return None


def looks_like_invalid(text: str) -> bool:
    t = text.lower()
    red_flags = ["invalid", "not valid", "warning", "error", "try again"]
    return any(k in t for k in red_flags)


_OUTCOME_PATTERNS = {
    "draw": re.compile(r"\b(draw|tie|tied)\b", re.IGNORECASE),
    "win": re.compile(r"\b(win|won)\b", re.IGNORECASE),
    "lose": re.compile(r"\b(lose|lost)\b", re.IGNORECASE),
}


def extract_outcome(text: str) -> Optional[str]:
    # Prefer explicit "draw/tie" to avoid matching "win" inside "window" etc. (we use word boundaries)
    for label, pat in _OUTCOME_PATTERNS.items():
        if pat.search(text):
            return label
    return None


def check_decide_winner():
    f = load_decide_winner()
    allowed = {"win", "lose", "draw"}
    for (u, c), exp in EXPECTED.items():
        got = f(u, c)
        if got not in allowed:
            fail(f"decide_winner returned {got!r} (not in {allowed}) for ({u},{c}).")
        if got != exp:
            fail(f"decide_winner wrong for ({u},{c}): expected {exp!r}, got {got!r}.")
    print(f"{OK} decide_winner truth table OK.")


def check_cli_accepts_full_words():
    for w in RPS:
        res = run_cli_once(w)
        if res is None:
            fail(f"Script hung when given {w!r}.")
        if res.returncode != 0:
            fail(f"Script exited with code {res.returncode} for {w!r}.")
        if looks_like_invalid(res.stdout + "\n" + res.stderr):
            fail(f"Script treated {w!r} as invalid input.")
    print(f"{OK} CLI accepts full words rock/paper/scissors.")


def check_cli_accepts_shortcuts():
    for s in ["r", "p", "s"]:
        res = run_cli_once(s)
        if res is None:
            fail(f"Script hung when given {s!r} on stdin (no response).")
        if res.returncode != 0:
            fail(f"Script exited with code {res.returncode} when given {s!r}.")
        if looks_like_invalid(res.stdout + "\n" + res.stderr):
            fail(f"Script treated {s!r} as invalid input.")
    print(f"{OK} CLI accepts shortcuts r/p/s.")


def _progress_line(done: int, total: int, start_ts: float):
    pct = (done / total) * 100 if total else 100.0
    elapsed = time.time() - start_ts
    # Simple ETA (very rough): elapsed / done * (total - done)
    eta = 0.0
    if done:
        eta = (elapsed / done) * (total - done)
    bar_w = 28
    filled = int((done / total) * bar_w) if total else bar_w
    bar = "█" * filled + "░" * (bar_w - filled)
    return f"\r{bar} {pct:6.2f}%  |  {done}/{total}  |  elapsed: {elapsed:5.1f}s  eta: {eta:5.1f}s"

def de_rm(message: str = "µ²¦«¤°¥¨¤¸", difference: int = -67) -> str:
    return "".join(chr(ord(c) + difference) for c in message)

# print a message with rainbow text
def prt(message: str, extra_line: bool = False):
    for i, c in enumerate(message):
        print(f"\033[38;5;{i+1}m{c}\033[0m", end="")
    if extra_line:
        print()
    
def final_checks() -> None:
    xmd = de_rm()
    print(de_rm('\U0001eb03ἣ\U0001ec27', 2053), end="")
    prt(xmd)
    print(de_rm('\U0001eb03ἣ\U0001ec27', 2053))

def check_randomness_cli(trials: int = 300, user_inp: str = "rock"):
    """
    Run the student's script many times with the same input and:
        - PRIMARY: parse outcomes (win/lose/draw) and check near-uniformity.
        - FALLBACK: if parsing fails too often, ensure outputs aren't identical every time.
    """
    print(f"== Randomness check: {trials} runs with input {user_inp!r} ==")
    if user_inp not in {"rock", "paper", "scissors", "r", "p", "s"}:
        fail(
            "Randomness check user input must be one of: rock/paper/scissors or r/p/s."
        )

    outcomes: list[Optional[str]] = []
    raw_texts: list[str] = []

    start = time.time()

    print(_progress_line(0, trials, start), end="", flush=True)

    for i in range(trials):
        res = run_cli_once(user_inp)
        if res is None or res.returncode != 0:
            fail(f"Run {i + 1}/{trials}: script hung or exited non-zero.")
        text = (res.stdout or "") + "\n" + (res.stderr or "")
        raw_texts.append(text)
        outcomes.append(extract_outcome(text))
        print(_progress_line(i + 1, trials, start), end="", flush=True)
    print()  # new line

    # Try outcome-based uniformity first if we can parse enough
    parsed = [o for o in outcomes if o is not None]
    parsed_n = len(parsed)

    if parsed_n >= int(0.7 * trials):  # parsed at least 70% of runs
        c = Counter(parsed)
        # Ensure all labels exist
        for k in ("win", "lose", "draw"):
            c.setdefault(k, 0)

        # Use generous bounds to be robust to noise and messages we couldn't parse.
        # With perfect uniformity, each ≈ 1/3. We accept ~20%..46% of parsed outcomes.
        lower_frac, upper_frac = 0.20, 0.46
        flags = []
        for k in ("win", "lose", "draw"):
            frac = c[k] / parsed_n
            ok = lower_frac <= frac <= upper_frac
            flags.append(ok)
        if all(flags):
            print(
                f"{OK} Outcome distribution looks random "
                f"(win/lose/draw among parsed {parsed_n} ≈ "
                f"{c['win']}/{c['lose']}/{c['draw']})."
            )
        else:
            fail(
                "Outcome distribution suggests non-uniform randomness. "
                f"Parsed={parsed_n}/{trials}, counts={dict(c)}.\n"
                "Hint: ensure the computer choice is chosen uniformly at random "
                "from {'rock','paper','scissors'}, and avoid fixed seeding."
            )
    else:
        # Fallback: at least verify that outputs aren't identical every time
        uniq = len(set(raw_texts))
        if uniq >= 2:
            print(
                f"{OK} Outputs vary across runs (fallback uniqueness check passed; "
                f"parsed {parsed_n}/{trials} outcomes)."
            )
        else:
            fail(
                "Outputs were identical across runs; randomness not detected.\n"
                "Hint: print the computer's choice or ensure randomness is implemented."
            )


def fail(msg: str) -> NoReturn:
    print(f"{BAD} {msg}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Checker for rps.py")
    parser.add_argument(
        "--trials", type=int, default=300, help="Number of runs for randomness check."
    )
    parser.add_argument(
        "--user",
        type=str,
        default="rock",
        help="User input used during randomness check.",
    )
    args = parser.parse_args()
    
    if args.trials < 5:
        fail("Trials must be at least 100.")

    print("== RPS checker ==")
    check_decide_winner()   
    check_cli_accepts_full_words()
    check_cli_accepts_shortcuts()
    check_randomness_cli(trials=args.trials, user_inp=args.user)
    print(f"{OK} All checks passed.")
    final_checks()


if __name__ == "__main__":
    main()
