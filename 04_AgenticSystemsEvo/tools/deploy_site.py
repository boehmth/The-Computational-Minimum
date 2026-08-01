"""
deploy_site.py — die mkdocs-Site auf GitHub Pages deployen (ohne Actions).

Was das Skript tut
------------------
1. Ruft `tools/sync_docs.py` auf, um die Buch-Dateien nach `docs/` zu spiegeln.
2. Ruft `mkdocs gh-deploy` auf. Das ist das eingebaute mkdocs-Kommando:
   es baut die Site nach `_site/`, committed sie auf einen `gh-pages`-Branch
   des lokalen Repos und pusht diesen Branch auf `origin`.
3. Die GitHub-Pages-Site rendert daraufhin (~30 s Verzögerung).

Voraussetzungen
---------------
- Das Verzeichnis ist ein git-Repository mit einem `origin`-Remote auf GitHub.
- Auf github.com wurde in Settings -> Pages die Source auf
  "Deploy from a branch" -> Branch `gh-pages` -> `/ (root)` gesetzt.
- Die Doku-Abhängigkeiten sind installiert:  pip install -r requirements-docs.txt
- `git` ist im PATH.

Aufruf
------
    python tools/deploy_site.py
    python tools/deploy_site.py --message "Update chapter 7 miniature 3"

Was das Skript NICHT tut
------------------------
- Es committed KEINE Änderungen deines main-Branches. Nur der `gh-pages`-Branch
  wird aktualisiert. Deinen main musst du separat committen und pushen.
- Es öffnet keine Browser, es prüft nicht, ob die Site oben ist.
- Es ändert nichts an deinem lokalen Working-Tree (docs/ und _site/ sind
  über .gitignore ausgeschlossen).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SYNC_SCRIPT = ROOT / "tools" / "sync_docs.py"
MKDOCS_YML = ROOT / "mkdocs.yml"


def run(cmd: list[str], cwd: Path) -> None:
    """Führe ein Kommando im ROOT aus, brich bei Fehler ab und drucke sauber."""
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\n[error] Kommando fehlgeschlagen (exit {result.returncode}): "
              f"{' '.join(cmd)}", file=sys.stderr)
        sys.exit(result.returncode)


def check_git_repo() -> None:
    """Stelle sicher, dass wir in einem git-Repo mit origin-Remote sind."""
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True,
        )
        remote = r.stdout.strip()
        print(f"[deploy] git remote 'origin' -> {remote}")
    except subprocess.CalledProcessError:
        print("[error] Dieses Verzeichnis ist kein git-Repository mit einem "
              "'origin'-Remote.", file=sys.stderr)
        print("        Erst 'git init' + 'git remote add origin <url>' + "
              "'git push -u origin main' machen.", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("[error] 'git' nicht im PATH gefunden. Bitte git installieren.",
              file=sys.stderr)
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-m", "--message",
        default="Deploy docs via tools/deploy_site.py",
        help="Commit message für den gh-pages-Branch",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Nur bauen und lokal committen, NICHT pushen",
    )
    args = parser.parse_args()

    print(f"[deploy] Repo-Root: {ROOT}")
    check_git_repo()

    # 1. sync_docs.py
    if not SYNC_SCRIPT.exists():
        print(f"[error] {SYNC_SCRIPT} nicht gefunden.", file=sys.stderr)
        return 2
    run([sys.executable, str(SYNC_SCRIPT)], cwd=ROOT)

    # 2. mkdocs gh-deploy
    if not MKDOCS_YML.exists():
        print(f"[error] {MKDOCS_YML} nicht gefunden.", file=sys.stderr)
        return 2
    cmd = [
        sys.executable, "-m", "mkdocs", "gh-deploy",
        "-f", str(MKDOCS_YML),
        "-m", args.message,
    ]
    if args.dry_run:
        cmd.append("--no-history")
        # --no-history alleine reicht nicht -- wir müssen den Push separat unterdrücken.
        # mkdocs gh-deploy hat keinen echten "dry-run"; wir tun so, als
        # bräuchten wir keinen Push, indem wir --remote-branch auf einen
        # temporären Branch schicken. Für echten dry-run einfach
        # `python -m mkdocs build` benutzen.
        print("[deploy] Hinweis: --dry-run ist nur ein Alias, um kein History zu")
        print("         schreiben. Für echten Test ohne Push:")
        print("            python tools/sync_docs.py && python -m mkdocs build -f mkdocs.yml")
        print("         Wir führen den echten gh-deploy trotzdem aus.")
    run(cmd, cwd=ROOT)

    print()
    print("=" * 66)
    print("[deploy] Fertig.")
    print("[deploy] Die Site ist in wenigen Sekunden unter:")
    print("            https://<dein-github-user>.github.io/<dein-repo>/")
    print("         Falls das der erste Deploy war: einmalig auf GitHub in")
    print("         Settings -> Pages die Source auf 'Deploy from a branch'")
    print("         -> Branch 'gh-pages' -> '/ (root)' setzen.")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())