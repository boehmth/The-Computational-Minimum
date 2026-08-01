"""
common/ui.py — small box-drawing helpers so every miniature reads the same.

Two shapes:
    hard_card(title, subtitle, body)  — for streams that matter (prompt,
                                        thinking, final answer)
    soft_frame(title, body_lines)     — for tables and summaries

Plus:
    phase_break(text)                 — a quiet section marker between phases
    wrap(text)                        — word-wrap + right-pad, for feeding
                                        soft_frame with prose

Everything renders in a plain ANSI terminal.  Width is 78 characters.
"""

from __future__ import annotations
import textwrap


WIDTH = 78
# Inhalte werden zwischen "┃  " (3 Zeichen) und "  ┃" (3 Zeichen) gerendert
# -> Content-Breite = WIDTH - 6.
INNER = WIDTH - 6


def hard_card(title, subtitle=None, body="", max_body_chars=1400):
    top = "┏" + "━" * (WIDTH - 2) + "┓"
    div = "┣" + "━" * (WIDTH - 2) + "┫"
    bot = "┗" + "━" * (WIDTH - 2) + "┛"
    print()
    print(top)
    for line in _wrap_pad(title, INNER):
        print(f"┃  {line}  ┃")
    if subtitle:
        for line in _wrap_pad(subtitle, INNER):
            print(f"┃  {line}  ┃")
    print(div)
    body = (body or "").strip()
    if len(body) > max_body_chars:
        body = body[:max_body_chars] + "\n... (truncated for demo)"
    for para in body.split("\n"):
        for line in _wrap_pad(para, INNER):
            print(f"┃  {line}  ┃")
    print(bot)


def soft_frame(title, body_lines):
    print()
    print("┌── " + title + " " + "─" * (WIDTH - len(title) - 6))
    for line in body_lines:
        print("│  " + line)
    print("└" + "─" * (WIDTH - 1))


def phase_break(text):
    bar = "━" * WIDTH
    print()
    print(bar)
    print(f"    {text}")
    print(bar)


def wrap(text, width=None):
    """Public wrapper for callers that want padded lines (e.g. for
    feeding a prose block into soft_frame)."""
    return _wrap_pad(text, width or INNER)


def _wrap_pad(text, width):
    if not text:
        return [" " * width]
    lines = []
    for para in str(text).split("\n"):
        wrapped = textwrap.wrap(para, width=width) or [""]
        lines.extend(wrapped)
    return [line.ljust(width) for line in lines]


def summarise_last_line(text):
    """The last non-empty (and not markdown-decorated) line of a text.
    Used for one-line answer summaries in closing frames."""
    for line in reversed((text or "").strip().splitlines()):
        stripped = (line.strip()
                    .lstrip("#").lstrip("*").lstrip("-").strip()
                    .rstrip("*").rstrip(":").rstrip("."))
        if stripped:
            return stripped[:70]
    return "(empty)"