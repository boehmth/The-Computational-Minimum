"""
extract_kap1.py — extrahiert den Fliesstext aus Kap1.docx in eine .txt-Datei.

Kein python-docx noetig: docx ist ein ZIP, document.xml enthaelt den Text
in <w:t>-Elementen. Wir gehen paragraphenweise, damit die Struktur bleibt.
"""
from __future__ import annotations
import os, re, sys, zipfile


def extract(docx_path: str, out_path: str) -> None:
    z = zipfile.ZipFile(docx_path)
    xml = z.read('word/document.xml').decode('utf-8')

    # Ein Paragraph == <w:p>...</w:p>. Innerhalb: <w:t>...</w:t> mit Text.
    paras = re.findall(r'<w:p[^>]*>(.*?)</w:p>', xml, re.S)
    lines = []
    for p in paras:
        # Ueberschriften erkennen (Style Heading N) fuer bessere Gliederung
        style_match = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        style = style_match.group(1) if style_match else ""

        text_parts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)
        line = ''.join(text_parts).strip()
        if not line:
            # trotzdem eine Leerzeile behalten
            lines.append('')
            continue

        if 'Heading1' in style or 'berschrift1' in style:
            lines.append(f'# {line}')
        elif 'Heading2' in style or 'berschrift2' in style:
            lines.append(f'## {line}')
        elif 'Heading3' in style or 'berschrift3' in style:
            lines.append(f'### {line}')
        elif 'Heading4' in style or 'berschrift4' in style:
            lines.append(f'#### {line}')
        else:
            lines.append(line)

    text = '\n\n'.join(lines)
    # Doppel-Leerzeilen komprimieren
    text = re.sub(r'\n{3,}', '\n\n', text)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"[extract] {len(paras)} Paragraphen -> {out_path}")
    print(f"[extract] Datei-Groesse: {len(text)} Zeichen")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src = os.path.expandvars(r'%USERPROFILE%\Downloads\Kap1.docx')
    dst = 'kap1_extracted.txt'
    extract(src, dst)
    # Erste 4000 Zeichen als Vorschau ausgeben
    with open(dst, encoding='utf-8') as f:
        preview = f.read(4000)
    print('\n--- VORSCHAU ---\n')
    print(preview)