"""Self-contained HTML/JS Rule 90 viewer with iOS-safe chip sound."""

from __future__ import annotations

import json


def build_scrollca_html(
    *,
    width: int,
    visible_rows: int,
    speed_ms: int,
    sound_on: bool,
    running: bool,
    insert_chance: float = 0.08,
) -> str:
    """Return one HTML document that scrolls Rule 90 and plays chip blips.

    Sound uses a single AudioContext unlocked by a real tap/click inside this
    same document — required for iPhone Safari. The iframe is meant to stay
    mounted (only rebuilt when controls change), not remounted every row.
    """
    cfg = {
        "width": int(width),
        "visibleRows": int(visible_rows),
        "speedMs": int(speed_ms),
        "soundOn": bool(sound_on),
        "running": bool(running),
        "insertChance": float(insert_chance),
        "scrollart": "scrollart!",
        "alive": "█",
        "dead": " ",
        "scale": [
            196.00,
            233.08,
            261.63,
            311.13,
            349.23,
            392.00,
            466.16,
            523.25,
            622.25,
            698.46,
            783.99,
            932.33,
        ],
    }
    cfg_json = json.dumps(cfg)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  html, body {{
    margin: 0; padding: 0;
    background: #05070a;
    color: #9fd3ff;
    font-family: "IBM Plex Mono", "JetBrains Mono", "Fira Code", monospace;
  }}
  #bar {{
    display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
    padding: 8px 10px;
    border-bottom: 1px solid #243044;
    background: #10161f;
  }}
  button {{
    font: 12px monospace;
    padding: 8px 12px;
    cursor: pointer;
    background: #1b2838;
    color: #9fd3ff;
    border: 1px solid #3a516e;
    border-radius: 0;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }}
  button:disabled {{ opacity: 0.45; cursor: default; }}
  #status {{ font-size: 12px; color: #9fd3ff; }}
  #frame {{
    margin: 0;
    padding: 8px 10px 4px;
    white-space: pre;
    font-size: 11px;
    line-height: 1.05;
    overflow: hidden;
  }}
  #caption {{
    padding: 4px 10px 10px;
    font-size: 12px;
    color: #c5d4e8;
  }}
</style>
</head>
<body>
  <div id="bar">
    <button type="button" id="arm">Tap to enable sound</button>
    <span id="status">sound locked</span>
  </div>
  <pre id="frame"></pre>
  <div id="caption"></div>
  <script>
  (function () {{
    const CFG = {cfg_json};
    const armBtn = document.getElementById("arm");
    const statusEl = document.getElementById("status");
    const frameEl = document.getElementById("frame");
    const captionEl = document.getElementById("caption");

    const AC = window.AudioContext || window.webkitAudioContext;
    let ctx = null;
    let armed = false;
    let generation = 0;
    let lastLabel = false;
    let timer = null;

    function initialRow(w) {{
      const row = new Array(w).fill(0);
      row[Math.floor(w / 2)] = 1;
      return row;
    }}

    function nextRow(row) {{
      const w = row.length;
      const out = new Array(w);
      for (let i = 0; i < w; i++) {{
        const left = row[(i - 1 + w) % w];
        const right = row[(i + 1) % w];
        out[i] = left !== right ? 1 : 0;
      }}
      return out;
    }}

    function rowString(row) {{
      let s = "";
      for (let i = 0; i < row.length; i++) s += row[i] ? CFG.alive : CFG.dead;
      return s;
    }}

    function formatRow(row) {{
      let text = rowString(row);
      const label = CFG.scrollart;
      if (text.length < label.length) return {{ text, labeled: false }};
      if (Math.random() >= CFG.insertChance) return {{ text, labeled: false }};
      const pos = Math.floor(Math.random() * (text.length - label.length + 1));
      text = text.slice(0, pos) + label + text.slice(pos + label.length);
      return {{ text, labeled: true }};
    }}

    function soundParams(row) {{
      const w = row.length;
      let sum = 0, count = 0;
      for (let i = 0; i < w; i++) if (row[i]) {{ sum += i; count++; }}
      if (!count) return {{ silent: true }};
      const density = count / w;
      const centroid = sum / count;
      let degree = Math.round((centroid / Math.max(w - 1, 1)) * (CFG.scale.length - 1));
      degree = Math.max(0, Math.min(CFG.scale.length - 1, degree));
      return {{
        silent: false,
        frequency: CFG.scale[degree],
        amplitude: 0.08 + 0.18 * Math.sqrt(density),
        duty: 0.125 + 0.375 * density,
      }};
    }}

    function unlockAudio() {{
      // iOS: create + resume MUST run synchronously inside the gesture handler.
      if (!AC) {{
        statusEl.textContent = "audio unsupported";
        return false;
      }}
      if (!ctx) ctx = new AC();
      if (ctx.state === "suspended") ctx.resume();
      armed = true;
      statusEl.textContent = CFG.soundOn ? "sound armed" : "armed (enable 16-bit sound in sidebar)";
      armBtn.textContent = "Sound unlocked";
      return true;
    }}

    function playBlip(params, durSec) {{
      if (!CFG.soundOn || !armed || !ctx || params.silent) return;
      if (ctx.state === "suspended") ctx.resume();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const harmonics = 16;
      const real = new Float32Array(harmonics + 1);
      const imag = new Float32Array(harmonics + 1);
      for (let n = 1; n <= harmonics; n++) {{
        imag[n] = (2 / (n * Math.PI)) * Math.sin(n * Math.PI * params.duty);
      }}
      try {{
        osc.setPeriodicWave(ctx.createPeriodicWave(real, imag));
      }} catch (e) {{
        osc.type = "square";
      }}
      osc.frequency.value = params.frequency;
      const now = ctx.currentTime;
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(Math.max(params.amplitude, 0.0001), now + 0.004);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + durSec);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + durSec + 0.01);
    }}

    let row = initialRow(CFG.width);
    const history = [];

    function tick() {{
      const shown = formatRow(row);
      history.push(shown.text);
      if (history.length > CFG.visibleRows) history.splice(0, history.length - CFG.visibleRows);
      frameEl.textContent = history.join("\\n");
      generation += 1;
      lastLabel = shown.labeled;

      let soundNote = "sound off";
      if (CFG.soundOn) {{
        if (!armed) soundNote = "tap Enable sound";
        else if (shown.labeled) soundNote = "silent (scrollart!)";
        else soundNote = "16-bit blip";
      }}
      captionEl.textContent =
        "generation " + generation +
        " · " + CFG.width + " cells · " +
        (CFG.running ? "scrolling" : "paused") +
        " · " + soundNote +
        " · look for random “scrollart!” labels";

      if (CFG.soundOn && armed && !shown.labeled) {{
        playBlip(soundParams(row), Math.max(CFG.speedMs, 20) / 1000);
      }}

      row = nextRow(row);
    }}

    function onArm(ev) {{
      // Keep this handler sync for iOS Safari gesture chaining.
      if (ev) ev.preventDefault();
      unlockAudio();
      // Prime a near-silent blip so iOS fully routes audio on this gesture.
      if (ctx && CFG.soundOn) {{
        playBlip({{ silent: false, frequency: 440, amplitude: 0.0002, duty: 0.25 }}, 0.03);
      }}
    }}

    armBtn.addEventListener("click", onArm);
    armBtn.addEventListener("touchend", onArm, {{ passive: false }});

    if (!CFG.soundOn) {{
      armBtn.disabled = true;
      statusEl.textContent = "enable 16-bit sound in the sidebar";
    }} else {{
      statusEl.textContent = "iPhone: tap the button once to unlock audio";
    }}

    // First paint
    tick();
    if (CFG.running) {{
      timer = setInterval(tick, Math.max(CFG.speedMs, 20));
    }}
  }})();
  </script>
</body>
</html>
"""


def player_height(visible_rows: int, sound_on: bool) -> int:
    """Approximate iframe height for the scroll view + control bar."""
    bar = 48 if sound_on else 40
    return bar + 28 + int(visible_rows * 11.5) + 36
