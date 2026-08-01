"""
sync_docs.py — spiegelt die Buch-Markdown-Dateien in einen `docs/`-Ordner.

Hintergrund
-----------
MkDocs verlangt, dass `docs_dir` ein Unterordner der Repo-Root ist (nicht
die Root selbst). Damit Autoren aber weiterhin `07_DynamicToolAgent/README.md`
editieren können — und nicht ein Duplikat davon in `docs/…` — sync-en wir die
relevanten Dateien vor jedem Build.

`docs/` ist damit *Build-Artefakt* und in .gitignore ausgeschlossen.

Was gespiegelt wird
-------------------
- Root-Dateien: index.md, PREFACE.md, ROADMAP.md, STYLE.md, README.md
- Alle sieben Kapitel-Ordner (01_… bis 07_…) rekursiv
- stylesheets/

Was nicht gespiegelt wird
-------------------------
- .env, sap_service_key.json (geheime Konfiguration)
- __pycache__/, *.pyc
- generated_tools/*.py (Runtime-generierter Code, keine Doku)
- _PLAN.md (interne Autoren-Notizen)

Aufruf
------
    python tools/sync_docs.py
    # dann mkdocs build oder mkdocs serve
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


# =============================================================================
#  Konfiguration
# =============================================================================

ROOT_FILES = [
    "index.md",
    "PREFACE.md",
    "PREFACE.en.md",
    "ROADMAP.md",
    "STYLE.md",
    "README.md",
    "README.en.md",
]

FOLDERS_TO_MIRROR = [
    ("01_TextInTextOut",     "01_TextInTextOut"),
    ("02_ToolsAndPlanning",  "02_ToolsAndPlanning"),
    ("03_TheLoop",           "03_TheLoop"),
    ("04_ReasoningInside",   "04_ReasoningInside"),
    ("05_ProtocolsAndScale", "05_ProtocolsAndScale"),
    ("06_WhenNotToBuild",    "06_WhenNotToBuild"),
    ("07_DynamicToolAgent",  "07_DynamicToolAgent"),
    ("stylesheets",          "stylesheets"),
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "_PLAN.md",
    "generated_tools",
    ".env",
]


def is_excluded(name: str) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if pat.startswith("*."):
            if name.endswith(pat[1:]):
                return True
        elif pat in name or pat == name:
            return True
    return False


# =============================================================================
#  Sync-Logik
# =============================================================================

def clean_docs() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True, exist_ok=True)
    print(f"[sync] docs/ zurueckgesetzt: {DOCS}")


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def sync_root_files() -> int:
    n = 0
    for name in ROOT_FILES:
        src = ROOT / name
        if not src.exists():
            print(f"[sync] Info: {name} nicht gefunden, uebersprungen")
            continue
        copy_file(src, DOCS / name)
        n += 1
    print(f"[sync] {n} Root-Dateien nach docs/ gespiegelt")
    return n


def sync_folder(src_rel: str, dst_rel: str) -> int:
    src_root = ROOT / src_rel
    dst_root = DOCS / dst_rel
    if not src_root.exists():
        print(f"[sync] Warnung: Ordner {src_rel} nicht gefunden, uebersprungen")
        return 0

    count = 0
    for src in src_root.rglob("*"):
        if src.is_dir():
            continue
        if any(is_excluded(part) for part in src.relative_to(src_root).parts):
            continue
        # Nur Markdown und CSS spiegeln — Python-Quellcode wird auf GitHub gelesen,
        # nicht in der Site.
        if src.suffix.lower() not in (".md", ".css", ".js"):
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        copy_file(src, dst)
        count += 1

    print(f"[sync] Ordner {src_rel} -> docs/{dst_rel}: {count} Dateien")
    return count


# =============================================================================
#  Link-Fixes für Ordner-Links
# =============================================================================

FOLDER_LINK_RE = re.compile(
    r"(\[[^\]]+\]\()"
    r"([^\s\)]*?/)"
    r"(\))"
)


def fix_folder_links_in_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    replacements = 0

    def _replace(m: re.Match) -> str:
        nonlocal replacements
        prefix, folder_link, suffix = m.group(1), m.group(2), m.group(3)
        if folder_link.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        # Nicht-Kapitel-Ordner nicht anfassen.
        if folder_link.endswith(("assets/", "src/", "notes/", "programs/", "examples/",
                                 "generated_tools/")):
            return m.group(0)
        replacements += 1
        return f"{prefix}{folder_link}README.md{suffix}"

    new_text = FOLDER_LINK_RE.sub(_replace, text)
    if replacements > 0:
        path.write_text(new_text, encoding="utf-8")
    return replacements


def fix_all_folder_links() -> int:
    total = 0
    files_touched = 0
    for md in DOCS.rglob("*.md"):
        n = fix_folder_links_in_file(md)
        total += n
        if n > 0:
            files_touched += 1
    print(f"[sync] Link-Normalisierung: {total} Ordner-Links in {files_touched} Dateien gefixt")
    return total


def main() -> int:
    print(f"[sync] Repo-Root: {ROOT}")
    print(f"[sync] Ziel:      {DOCS}")
    print()

    clean_docs()
    n = sync_root_files()
    for src_rel, dst_rel in FOLDERS_TO_MIRROR:
        n += sync_folder(src_rel, dst_rel)
    fix_all_folder_links()

    print()
    print(f"[sync] Fertig — {n} Dateien in docs/")
    print(f"[sync] Naechster Schritt:  python -m mkdocs build")
    return 0


if __name__ == "__main__":
    sys.exit(main())