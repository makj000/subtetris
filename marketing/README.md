# Minusfall marketing assets

All footage shows the branded interface (MINUSFALL wordmark, score, level/lines,
next preview) composited at 920×1240. Source replay:
`data/subtetris/subtetris-2026-04-14-04-13-10.jsonl`, recorded via
`test/replay_rec.html` at 2× game speed.

## Versions

- **v1-original/** — first branded recordings. Full 170s master, 27s highlight
  (MP4 + GIF), poster still, raw source webm. Everything plays at the recorded
  2× speed.
- **v2-uniform-slowmo/** — whole highlight slowed 2× uniformly (54s), bringing
  it back to real gameplay speed so the clears are watchable.
- **v3-speed-ramp/** — first speed-ramped cut via `make_speedramp.sh`:
  normal play sped up (PLAY_SPEEDUP=2), cancellation sections slowed
  (CLEAR_SLOWDOWN=2).
- **v4-speed-ramp-tuned/** — adjusted parameters: CLEAR_SLOWDOWN=5, and the
  slow window re-anchored so regular play after each clear snaps back to fast
  (PRE_PAD=2.2 / POST_PAD=0.4).
- **v5-cinematic-subtraction/** — no post-processing tricks; re-recorded with
  the rig's `?cine` mode, which subtracts each row one cell at a time with a
  "−n" popup per block, so viewers can follow the mechanic. Play stays at 2×.

## Tools

- `make_speedramp.sh [PLAY_SPEEDUP] [CLEAR_SLOWDOWN]` — post-process any
  branded clip into a speed-ramped cut. Finds cancellations automatically by
  frame-diffing the LINES counter region. Override the source with
  `INPUT=path`.
