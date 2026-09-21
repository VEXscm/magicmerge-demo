#!/usr/bin/env python3
"""Build case/<id>/{base,ours,theirs} commits from fixtures/."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str, cwd: Path = ROOT) -> None:
    subprocess.check_call(["git", *args], cwd=cwd)


def git_out(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def write_file(rel: str, body: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if body == "" and rel.endswith("/DELETE"):
        return
    path.write_text(body)


def commit(message: str) -> str:
    git("add", "-A")
    git("commit", "-m", message)
    return git_out("rev-parse", "HEAD")


def main() -> None:
    if not (ROOT / ".git").exists():
        git("init", "-b", "main")
        git("config", "user.email", "demo@composal.ai")
        git("config", "user.name", "MagicMerge Demo")

    cases = json.loads((ROOT / "cases.json").read_text())
    # Keep README / scripts on main; do not carry fixture files into case branches.
    git("add", "README.md", "LICENSE", "demo", "scripts", "cases.json", "fixtures", ".gitignore")
    # Allow first commit to be empty of case files only.
    status = git_out("status", "--porcelain")
    if status:
        try:
            git("commit", "-m", "Document ten Vex monorepo conflicts at small scale")
        except subprocess.CalledProcessError:
            pass

    main_sha = git_out("rev-parse", "HEAD")
    for meta in cases:
        case_id = meta["id"]
        rel = meta["path"]
        fixture = ROOT / "fixtures" / case_id
        base = (fixture / "base").read_text()
        ours = (fixture / "ours").read_text()
        theirs = (fixture / "theirs").read_text()
        delete_theirs = meta.get("delete_theirs", False)

        git("switch", "--quiet", "--detach", main_sha)
        git("switch", "-C", f"case/{case_id}/base")
        write_file(rel, base)
        commit(f"{case_id}: base")

        git("switch", "-C", f"case/{case_id}/ours")
        write_file(rel, ours)
        commit(f"{case_id}: ours")

        git("switch", "--quiet", f"case/{case_id}/base")
        git("switch", "-C", f"case/{case_id}/theirs")
        if delete_theirs:
            target = ROOT / rel
            if target.exists():
                git("rm", "-f", rel)
            commit(f"{case_id}: theirs (delete)")
        else:
            write_file(rel, theirs)
            commit(f"{case_id}: theirs")

    git("switch", "--quiet", "main")
    print("seeded", len(cases), "cases")
    print(git_out("branch", "--list", "case/*"))


if __name__ == "__main__":
    main()
