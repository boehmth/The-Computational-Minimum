"""
sync_docs.py — spiegelt die Buch-Markdown-Dateien in einen `docs/`-Ordner.

Hintergrund
-----------
MkDocs verlangt, dass `docs_dir` ein Unterordner der Repo-Root ist (nicht
die Root selbst). Damit Autoren aber weiterhin `01_Computing/01_CPU/README.md`
editieren koennen — und nicht ein Duplikat davon in `docs/01_CPU/…` — sync-
en wir die relevanten Dateien vor jedem Build.

`docs/` ist damit *Build-Artefakt* und in .gitignore ausgeschlossen.

Was gespiegelt wird
-------------------
- Root-Dateien: index.md, PREFACE.md, ROADMAP.md, STYLE.md
- Teil 1 komplett: 01_Computing/**/*.md, plus die assets/-Unterordner
- Die grundlagen/-Deep-Dives
- Teil 2 komplett: 02_MachineIntelligence/**/*.md
- Teil 3 komplett: 03_LanguageModelling/**/*.md
- Teil 4 komplett: 04_AgenticSystems/**/*.md
- stylesheets/ und javascripts/

Was nicht gespiegelt wird
-------------------------
- tools/, slides_appendix/ (nicht Teil des Buchs)

- kap1_extracted.txt (Zwischenextrakt)
- ROADMAP.md-Dateien in Unterordnern (interne Planung)
- assets_prompts.md (Autoren-Notizen)

Beim Sync werden ausserdem Markdown-interne Links, die auf .md-Dateien in
*ausgeschlossenen* Ordnern zeigen, unveraendert gelassen (MkDocs verwirft
sie mit einer Warnung; darum bauen wir spaeter ohne --strict die kritischen
Bereiche).

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

# Auf Windows-Konsolen (cp1252) sonst UnicodeEncodeError bei Umlauten.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# Ordner-Root des Repos (auch wenn das Skript aus tools/ aufgerufen wird)
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


# =============================================================================
#  Konfiguration: was wird gespiegelt?
# =============================================================================

# Root-Dateien, die 1:1 in docs/ landen
ROOT_FILES = [
    "index.md",
    "PREFACE.md",
    "ROADMAP.md",
    "STYLE.md",
]

# Ganze Ordner, die rekursiv gespiegelt werden. (src → dst-Suffix relativ zu docs/)
FOLDERS_TO_MIRROR = [
    ("01_Computing", "01_Computing"),
    ("02_MachineIntelligence", "02_MachineIntelligence"),
    ("03_LanguageModelling", "03_LanguageModelling"),
    ("04_AgenticSystems", "04_AgenticSystems"),
    ("stylesheets",  "stylesheets"),
    ("javascripts",  "javascripts"),
]


# Muster, die bei einem rekursiven Sync ausgeschlossen werden.
# Alles was hier passt, wird uebersprungen.
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "test_",       # Test-Dateien nicht in die Site
    "ROADMAP.md",  # Interne Planungs-Dateien
    "assets_prompts.md",
]


def is_excluded(name: str) -> bool:
    """Trifft einer der EXCLUDE_PATTERNS auf diesen Datei-/Ordnernamen zu?"""
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
    """Loesche den bisherigen docs/-Ordner komplett."""
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True, exist_ok=True)
    print(f"[sync] docs/ zurueckgesetzt: {DOCS}")


def copy_file(src: Path, dst: Path) -> None:
    """Kopiere src nach dst, mit Parent-Anlage."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def sync_root_files() -> int:
    n = 0
    for name in ROOT_FILES:
        src = ROOT / name
        if not src.exists():
            print(f"[sync] Warnung: {name} nicht gefunden im Repo-Root")
            continue
        copy_file(src, DOCS / name)
        n += 1
    print(f"[sync] {n} Root-Dateien nach docs/ gespiegelt")
    return n


def sync_folder(src_rel: str, dst_rel: str) -> int:
    """Rekursiv einen Ordner spiegeln, mit EXCLUDE_PATTERNS-Filter."""
    src_root = ROOT / src_rel
    dst_root = DOCS / dst_rel
    if not src_root.exists():
        print(f"[sync] Warnung: Ordner {src_rel} nicht gefunden, uebersprungen")
        return 0

    count = 0
    for src in src_root.rglob("*"):
        if src.is_dir():
            continue
        # Ausschluss-Filter auf jedem Pfad-Segment testen
        if any(is_excluded(part) for part in src.relative_to(src_root).parts):
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        copy_file(src, dst)
        count += 1

    print(f"[sync] Ordner {src_rel} -> docs/{dst_rel}: {count} Dateien")
    return count


# =============================================================================
#  Link-Fixes: Ordner-Links in Markdown-Files auf README.md-Links normalisieren
# =============================================================================
#
#  In den READMEs verweisen wir oft auf ganze Ordner:
#      [Kap. 1](01_CPU/)
#  Fuer GitHub-Ordner-Views ist das schoen (GitHub laedt automatisch die
#  darinliegende README.md), fuer MkDocs aber unerkennbar. Wir ersetzen
#  solche Links nur im gespiegelten docs/-Ordner, nicht im Original.
#
#  Regex-Muster: [Text](irgendein_pfad/) --> [Text](irgendein_pfad/README.md)
#  Ausgeschlossen: Ordner-Links, die auf `..` oder `#` enden.
# =============================================================================

# Regex fuer Ordner-Links im Markdown: [text](pfad/)  (endet mit /)
FOLDER_LINK_RE = re.compile(
    r"(\[[^\]]+\]\()"                # [text](
    r"([^\s\)]*?/)"                  # pfad/ (endet mit /)
    r"(\))"                          # )
)


def fix_folder_links_in_file(path: Path) -> int:
    """
    Ersetze in einer Markdown-Datei alle Ordner-Links [foo](bar/) durch
    Datei-Links [foo](bar/README.md). Gibt die Zahl der Ersetzungen zurueck.
    """
    text = path.read_text(encoding="utf-8")
    replacements = 0

    def _replace(m: re.Match) -> str:
        nonlocal replacements
        prefix, folder_link, suffix = m.group(1), m.group(2), m.group(3)
        # Externe URLs und Anker nicht anfassen
        if folder_link.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        # Ordner-Links, die auf einen bekannten Nicht-Kapitel-Namen zeigen
        # (z.B. `assets/`), lassen wir in Ruhe.
        if folder_link.endswith(("assets/", "src/", "notes/", "programs/", "examples/")):
            return m.group(0)
        replacements += 1
        return f"{prefix}{folder_link}README.md{suffix}"

    new_text = FOLDER_LINK_RE.sub(_replace, text)

    if replacements > 0:
        path.write_text(new_text, encoding="utf-8")

    return replacements


def fix_all_folder_links() -> int:
    """Auf alle .md-Dateien in docs/ anwenden."""
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
    print(f"[sync] Naechster Schritt:  python -m mkdocs build --strict")
    return 0


if __name__ == "__main__":
    sys.exit(main())