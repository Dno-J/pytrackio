"""
pytrackio/_report.py
--------------------
Renders a clean, formatted performance report to stdout (or any stream).
Pure stdlib — zero dependencies.
"""

from __future__ import annotations

import io
from typing import IO, Optional

from ._tracker import get_registry


# ---------------------------------------------------------------------------
# Colour support (graceful fallback if terminal has no colour)
# ---------------------------------------------------------------------------

_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_CYAN   = "\033[96m"
_GREEN  = "\033[92m"
_RED    = "\033[91m"
_YELLOW = "\033[93m"
_DIM    = "\033[2m"


def _supports_colour(stream: IO[str]) -> bool:
    try:
        import os
        return hasattr(stream, "isatty") and stream.isatty() and os.name != "nt"
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Report renderer
# ---------------------------------------------------------------------------

def report(
    stream: Optional[IO[str]] = None,
    *,
    colour: Optional[bool] = None,
    show_counters: bool = True,
) -> str:
    """
    Print a formatted performance report and return it as a string.

    Usage::

        report()                        # print to stdout
        report(show_counters=False)     # hide counter section
        output = report(stream=None)    # capture as string

    Args:
        stream:         Output stream. Defaults to ``sys.stdout``.
        colour:         Force colour on/off. Auto-detected by default.
        show_counters:  Include the counters section.

    Returns:
        The report as a plain string (ANSI codes stripped).
    """
    import sys
    if stream is None:
        stream = sys.stdout

    use_colour = colour if colour is not None else _supports_colour(stream)

    buf      = io.StringIO()
    registry = get_registry()
    summaries = sorted(registry.all_summaries(), key=lambda s: s.total_ms, reverse=True)
    counters  = registry.all_counters()

    def c(code: str, text: str) -> str:
        return f"{code}{text}{_RESET}" if use_colour else text

    # ── Header ──────────────────────────────────────────────────────────────
    width = 72
    buf.write("\n")
    buf.write(c(_BOLD + _CYAN, "╔" + "═" * (width - 2) + "╗") + "\n")
    title = "pytrackio  —  Performance Report"
    pad   = (width - 2 - len(title)) // 2
    buf.write(c(_BOLD + _CYAN, "║") + " " * pad + c(_BOLD, title) + " " * (width - 2 - pad - len(title)) + c(_BOLD + _CYAN, "║") + "\n")
    uptime = f"uptime: {registry.uptime_seconds()}s"
    pad2   = width - 2 - len(uptime)
    buf.write(c(_BOLD + _CYAN, "║") + " " + c(_DIM, uptime) + " " * (pad2 - 1) + c(_BOLD + _CYAN, "║") + "\n")
    buf.write(c(_BOLD + _CYAN, "╠" + "═" * (width - 2) + "╣") + "\n")

    # ── Timings table ───────────────────────────────────────────────────────
    if summaries:
        col = [28, 7, 10, 9, 10, 8]  # widths
        headers = ["Function / Block", "Calls", "Avg (ms)", "Min(ms)", "Max (ms)", "Errors"]
        header_row = "║ " + "  ".join(h.ljust(col[i]) for i, h in enumerate(headers)) + " ║"
        buf.write(c(_BOLD, header_row) + "\n")
        buf.write(c(_CYAN, "╠" + "═" * (width - 2) + "╣") + "\n")

        for s in summaries:
            name_display = (s.name[:25] + "...") if len(s.name) > 28 else s.name
            err_display  = f"{s.errors} ({s.error_rate}%)" if s.errors else "—"
            err_colour   = _RED if s.errors else _GREEN

            row = (
                "║ "
                + name_display.ljust(col[0]) + "  "
                + str(s.calls).ljust(col[1]) + "  "
                + c(_YELLOW, f"{s.avg_ms:.2f}").ljust(col[2] + (9 if use_colour else 0)) + "  "
                + f"{s.min_ms:.2f}".ljust(col[3]) + "  "
                + f"{s.max_ms:.2f}".ljust(col[4]) + "  "
                + c(err_colour, err_display).ljust(col[5] + (9 if use_colour else 0))
                + " ║"
            )
            buf.write(row + "\n")
    else:
        buf.write("║" + "  No timing data recorded yet.".center(width - 2) + "║\n")

    # ── Counters section ────────────────────────────────────────────────────
    if show_counters and counters:
        buf.write(c(_CYAN, "╠" + "═" * (width - 2) + "╣") + "\n")
        counter_title = "Counters"
        buf.write(c(_BOLD + _CYAN, "║") + " " + c(_BOLD, counter_title) + " " * (width - 3 - len(counter_title)) + c(_BOLD + _CYAN, "║") + "\n")
        buf.write(c(_CYAN, "╠" + "─" * (width - 2) + "╣") + "\n")
        for ctr in sorted(counters, key=lambda x: x.name):
            line = f"  {ctr.name}:  {ctr.value}"
            buf.write(c(_CYAN, "║") + line.ljust(width - 2) + c(_CYAN, "║") + "\n")

    # ── Footer ──────────────────────────────────────────────────────────────
    buf.write(c(_BOLD + _CYAN, "╚" + "═" * (width - 2) + "╝") + "\n\n")

    output = buf.getvalue()
    stream.write(output)
    stream.flush()
    return output
