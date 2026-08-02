"""
sitemap_plugin.py — kleines MkDocs-Plugin, das eine sitemap.xml erzeugt.

Hintergrund
-----------
In MkDocs 1.6 wurde das eingebaute `sitemap`-Plugin aus dem Kern entfernt.
Das Community-Paket ist auf PyPI nicht (mehr) verfuegbar, daher erzeugen
wir die sitemap.xml hier selbst — ohne externe Abhaengigkeit.

Das Plugin haengt sich an den `on_post_build`-Hook und schreibt eine
sitemap.xml in das site_dir, die alle Seiten der Site auflistet.

Aktivierung in mkdocs.yml:
    plugins:
      - search
      - meta
      - minify
      - sitemap:
          # optional: eigene Basis-URL (Default: site_url aus mkdocs.yml)
          # base_url: https://boehmt.github.io/The-Computational-Minimum/
"""
from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET
from pathlib import Path

from mkdocs.plugins import BasePlugin


class SitemapPlugin(BasePlugin):
    """Erzeugt eine sitemap.xml mit allen Seiten der Site."""

    def on_post_build(self, config, **kwargs) -> None:
        site_dir = Path(config["site_dir"])
        site_url = config.get("site_url", "").rstrip("/")

        # Ohne site_url koennen wir keine absoluten URLs bauen.
        if not site_url:
            print("[sitemap] Warnung: site_url nicht gesetzt, sitemap.xml uebersprungen")
            return

        # Namespace fuer das Sitemap-Protokoll
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        ET.register_namespace("", ns["sm"])

        urlset = ET.Element(f"{{{ns['sm']}}}urlset")
        today = datetime.date.today().isoformat()

        # Alle .html-Dateien im site_dir als Seiten aufnehmen
        for html in sorted(site_dir.rglob("*.html")):
            rel = html.relative_to(site_dir).as_posix()
            # index.html -> Basis-URL, sonst /pfad/
            if rel == "index.html":
                loc = f"{site_url}/"
            elif rel.endswith("/index.html"):
                loc = f"{site_url}/{rel[:-len('index.html')]}"
            else:
                loc = f"{site_url}/{rel}"

            url = ET.SubElement(urlset, f"{{{ns['sm']}}}url")
            loc_el = ET.SubElement(url, f"{{{ns['sm']}}}loc")
            loc_el.text = loc
            lastmod = ET.SubElement(url, f"{{{ns['sm']}}}lastmod")
            lastmod.text = today

        tree = ET.ElementTree(urlset)
        out = site_dir / "sitemap.xml"
        tree.write(out, encoding="utf-8", xml_declaration=True)
        print(f"[sitemap] sitemap.xml mit {len(urlset)} URLs geschrieben: {out}")
