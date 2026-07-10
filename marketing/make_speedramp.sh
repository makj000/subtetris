#!/bin/bash
# make_speedramp.sh — speed-ramped highlight: fast normal play, slow-motion cancellations.
#
# Parameters (positional or env):
#   PLAY_SPEEDUP   $1  speed multiplier for sections WITHOUT cancellation (default 2)
#   CLEAR_SLOWDOWN $2  slow-motion factor for cancellation sections       (default 2)
#
# Optional env overrides:
#   INPUT     source mp4 (default v1-original/minusfall-branded-highlight-27s.mp4)
#   PRE_PAD   seconds kept before each LINES-counter change (default 2.2).
#             The counter updates at the END of a chain, so the whole
#             highlight/subtract/cascade animation lies BEFORE the change.
#   POST_PAD  seconds kept after the change (default 0.4) — just a settle
#             beat; the next piece spawns ~0.1s after the counter ticks.
#
# Usage: ./make_speedramp.sh [PLAY_SPEEDUP] [CLEAR_SLOWDOWN]
# Cancellations are found automatically by watching the LINES counter region
# of the sidebar for changes (frame-difference luma spike > 1.0).

set -euo pipefail
cd "$(dirname "$0")"

PLAY_SPEEDUP="${1:-${PLAY_SPEEDUP:-2}}"
CLEAR_SLOWDOWN="${2:-${CLEAR_SLOWDOWN:-2}}"
INPUT="${INPUT:-v1-original/minusfall-branded-highlight-27s.mp4}"
PRE_PAD="${PRE_PAD:-2.2}"
POST_PAD="${POST_PAD:-0.4}"
OUT="minusfall-branded-highlight-ramp-f${PLAY_SPEEDUP}x-s${CLEAR_SLOWDOWN}x.mp4"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$INPUT")

# 1. Detect LINES-counter changes (crop is the LINES digits area of the 920x1240 frame)
EVENTS=$(ffmpeg -i "$INPUT" \
  -vf "crop=150:60:760:240,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-" \
  -f null - 2>/dev/null \
  | awk '/pts_time/{split($0,a,"pts_time:"); t=a[2]}
         /YAVG/{split($0,b,"="); if (b[2]+0 > 1.0 && t+0 > 1.0) print t}')

if [ -z "$EVENTS" ]; then
  echo "No cancellation events detected in $INPUT" >&2
  exit 1
fi
echo "Cancellation events at: $EVENTS" | tr '\n' ' '; echo

# 2. Build merged slow windows, then alternating fast/slow segments across [0, DUR]
FILTER=$(echo "$EVENTS" | awk -v pre="$PRE_PAD" -v post="$POST_PAD" -v dur="$DUR" \
  -v fast="$PLAY_SPEEDUP" -v slow="$CLEAR_SLOWDOWN" '
  { s = $1 - pre; e = $1 + post;
    if (s < 0) s = 0; if (e > dur) e = dur;
    if (n > 0 && s <= we[n]) { if (e > we[n]) we[n] = e; }   # merge overlap
    else { n++; ws[n] = s; we[n] = e; }
  }
  END {
    seg = 0; pos = 0; f = "";
    for (i = 1; i <= n; i++) {
      if (ws[i] > pos) {   # fast segment before this window
        seg++; f = f sprintf("[0:v]trim=start=%.3f:end=%.3f,setpts=(PTS-STARTPTS)/%s[v%d];", pos, ws[i], fast, seg);
      }
      seg++; f = f sprintf("[0:v]trim=start=%.3f:end=%.3f,setpts=(PTS-STARTPTS)*%s[v%d];", ws[i], we[i], slow, seg);
      pos = we[i];
    }
    if (pos < dur) {
      seg++; f = f sprintf("[0:v]trim=start=%.3f:end=%.3f,setpts=(PTS-STARTPTS)/%s[v%d];", pos, dur, fast, seg);
    }
    for (i = 1; i <= seg; i++) f = f sprintf("[v%d]", i);
    f = f sprintf("concat=n=%d:v=1:a=0,fps=30[out]", seg);
    print f;
  }')

# 3. Render
ffmpeg -y -i "$INPUT" -filter_complex "$FILTER" -map "[out]" \
  -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart "$OUT" 2>&1 | tail -1

echo "Wrote $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
