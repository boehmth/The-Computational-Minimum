"""Common helpers shared by all six milestone chapters.

Deliberately tiny.  If you need something more, add it to the chapter
that needs it — not here.  Every helper here has to justify itself as
"used by at least two chapters".
"""

# ---------------------------------------------------------------------------
# Terminal setup: force stdout / stderr to UTF-8.
# Windows-Terminals kommen sonst mit den Unicode-Box-Zeichen (┏ ┃ ─ · →)
# nicht klar — cp1252 kann sie nicht kodieren und wirft UnicodeEncodeError.
# Wir machen das einmal hier, damit jede Miniatur davon profitiert, sobald
# sie irgendetwas aus `common` importiert.
# ---------------------------------------------------------------------------

import io as _io
import sys as _sys

for _stream_name in ("stdout", "stderr"):
    _stream = getattr(_sys, _stream_name, None)
    if _stream is None:
        continue
    # Only wrap real buffered streams (avoid double-wrapping in test harnesses).
    _buffer = getattr(_stream, "buffer", None)
    if _buffer is None:
        continue
    if getattr(_stream, "encoding", "").lower().replace("-", "") == "utf8":
        continue
    try:
        setattr(_sys, _stream_name,
                _io.TextIOWrapper(_buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True))
    except Exception:
        pass
