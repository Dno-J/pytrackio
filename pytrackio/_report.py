from __future__ import annotations
import io
from typing import IO, Optional
from ._tracker import get_registry

_RESET="\033[0m"; _BOLD="\033[1m"; _CYAN="\033[96m"
_GREEN="\033[92m"; _RED="\033[91m"; _YELLOW="\033[93m"; _DIM="\033[2m"

def _supports_colour(stream):
    try:
        import os; return hasattr(stream,"isatty") and stream.isatty() and os.name!="nt"
    except Exception: return False

def report(stream=None, *, colour=None, show_counters=True) -> str:
    """Print a formatted performance report.

    Usage::

        report()
        report(show_counters=False)
        report(colour=False)
    """
    import sys
    if stream is None: stream = sys.stdout
    use_colour = colour if colour is not None else _supports_colour(stream)
    buf = io.StringIO()
    registry  = get_registry()
    summaries = sorted(registry.all_summaries(), key=lambda s: s.total_ms, reverse=True)
    counters  = registry.all_counters()
    def c(code, text): return f"{code}{text}{_RESET}" if use_colour else text
    W = 72
    buf.write("\n")
    buf.write(c(_BOLD+_CYAN,"╔"+"═"*(W-2)+"╗")+"\n")
    title="pytrackio  —  Performance Report"
    pad=(W-2-len(title))//2
    buf.write(c(_BOLD+_CYAN,"║")+" "*pad+c(_BOLD,title)+" "*(W-2-pad-len(title))+c(_BOLD+_CYAN,"║")+"\n")
    uptime=f"uptime: {registry.uptime_seconds()}s"
    buf.write(c(_BOLD+_CYAN,"║")+" "+c(_DIM,uptime)+" "*(W-3-len(uptime))+c(_BOLD+_CYAN,"║")+"\n")
    buf.write(c(_BOLD+_CYAN,"╠"+"═"*(W-2)+"╣")+"\n")
    if summaries:
        col=[28,7,10,9,10,8]
        headers=["Function / Block","Calls","Avg (ms)","Min(ms)","Max (ms)","Errors"]
        buf.write(c(_BOLD,"║ "+"  ".join(h.ljust(col[i]) for i,h in enumerate(headers))+" ║")+"\n")
        buf.write(c(_CYAN,"╠"+"═"*(W-2)+"╣")+"\n")
        for s in summaries:
            nd=(s.name[:25]+"...") if len(s.name)>28 else s.name
            ed=f"{s.errors} ({s.error_rate}%)" if s.errors else "—"
            ec=_RED if s.errors else _GREEN
            ex=9 if use_colour else 0
            row=("║ "+nd.ljust(col[0])+"  "+str(s.calls).ljust(col[1])+"  "
                +c(_YELLOW,f"{s.avg_ms:.2f}").ljust(col[2]+ex)+"  "
                +f"{s.min_ms:.2f}".ljust(col[3])+"  "
                +f"{s.max_ms:.2f}".ljust(col[4])+"  "
                +c(ec,ed).ljust(col[5]+ex)+" ║")
            buf.write(row+"\n")
    else:
        buf.write("║"+"  No timing data recorded yet.".center(W-2)+"║\n")
    if show_counters and counters:
        buf.write(c(_CYAN,"╠"+"═"*(W-2)+"╣")+"\n")
        buf.write(c(_BOLD+_CYAN,"║")+" "+c(_BOLD,"Counters")+" "*(W-11)+c(_BOLD+_CYAN,"║")+"\n")
        buf.write(c(_CYAN,"╠"+"─"*(W-2)+"╣")+"\n")
        for ctr in sorted(counters, key=lambda x: x.name):
            line=f"  {ctr.name}:  {ctr.value}"
            buf.write(c(_CYAN,"║")+line.ljust(W-2)+c(_CYAN,"║")+"\n")
    buf.write(c(_BOLD+_CYAN,"╚"+"═"*(W-2)+"╝")+"\n\n")
    output=buf.getvalue()
    stream.write(output); stream.flush()
    return output
