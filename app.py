"""Streamlit viewer for Rule 90 scroll art with 16-bit retro blips."""

from __future__ import annotations

import base64
from datetime import timedelta

import streamlit as st
import streamlit.components.v1 as components

from retro_sound import row_sound_params, row_to_wav_bytes
from rule90_scroll import SCROLLART, format_row, initial_row, next_generation

st.set_page_config(
    page_title="scrollca — Rule 90",
    page_icon="△",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at top, #1a2332 0%, #0b0f14 55%, #07090c 100%);
        color: #e8eef7;
    }
    h1, h2, h3, p, label, span, div {
        color: #e8eef7 !important;
    }
    div[data-testid="stCode"] {
        background: #05070a !important;
        border: 1px solid #243044;
        border-radius: 0;
    }
    div[data-testid="stCode"] pre, div[data-testid="stCode"] code {
        font-family: "IBM Plex Mono", "JetBrains Mono", "Fira Code", monospace !important;
        font-size: 11px !important;
        line-height: 1.05 !important;
        color: #9fd3ff !important;
        background: transparent !important;
    }
    section[data-testid="stSidebar"] {
        background: #10161f;
        border-right: 1px solid #243044;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("scrollca")
st.caption("Rule 90 cellular automaton — scrolling Sierpiński triangle")

with st.sidebar:
    st.header("Controls")
    width = st.slider("Width", min_value=21, max_value=201, value=101, step=2)
    visible_rows = st.slider("Visible rows", min_value=20, max_value=240, value=90)
    speed_ms = st.slider("Scroll interval (ms)", min_value=20, max_value=400, value=50, step=10)
    running = st.toggle("Scroll", value=True)
    sound_on = st.toggle("16-bit sound", value=False)
    st.caption(
        "Square-wave blips follow the foremost CA row: pitch from the alive-cell "
        "center, pulse width from density. Rows that show “scrollart!” stay silent. "
        "If your browser blocks audio, click Arm chip sound once."
    )
    reset = st.button("Reset", use_container_width=True)

if sound_on:
    components.html(
        """
        <button id="arm"
          style="font:12px monospace;padding:4px 8px;cursor:pointer;
                 background:#1b2838;color:#9fd3ff;border:1px solid #243044;">
          Arm chip sound
        </button>
        <span id="status" style="font:12px monospace;color:#9fd3ff;margin-left:8px;"></span>
        <script>
          const status = document.getElementById("status");
          const arm = document.getElementById("arm");
          const AC = window.AudioContext || window.webkitAudioContext;
          function mark(ok) {
            try { localStorage.setItem("scrollca_chip_armed", ok ? "1" : "0"); } catch (e) {}
            status.textContent = ok ? "armed" : "";
          }
          if (localStorage.getItem("scrollca_chip_armed") === "1") {
            status.textContent = "armed";
          }
          arm.onclick = async () => {
            if (!AC) { status.textContent = "unsupported"; return; }
            const ctx = new AC();
            await ctx.resume();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.frequency.value = 440;
            gain.gain.value = 0.0001;
            osc.connect(gain); gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.05);
            mark(true);
          };
        </script>
        """,
        height=36,
    )


def _reset_state(new_width: int) -> None:
    row = initial_row(new_width)
    st.session_state.width = new_width
    st.session_state.current = row
    display = format_row(row)
    st.session_state.history = [display]
    st.session_state.last_display = display


if (
    "history" not in st.session_state
    or "current" not in st.session_state
    or st.session_state.get("width") != width
    or reset
):
    _reset_state(width)


def _play_retro_blip(row, duration_ms: int) -> None:
    """Play a chiptune pulse blip derived from raw CA cells (not display text)."""
    params = row_sound_params(row)
    if params["silent"]:
        return

    wav = row_to_wav_bytes(row, duration_ms=max(duration_ms, 20))
    if wav is None:
        return
    b64 = base64.b64encode(wav).decode("ascii")
    dur = max(duration_ms, 20) / 1000.0
    components.html(
        f"""
        <audio id="blip" autoplay preload="auto"
               src="data:audio/wav;base64,{b64}"></audio>
        <script>
          (async () => {{
            const audio = document.getElementById("blip");
            const freq = {params["frequency"]:.4f};
            const amp = {params["amplitude"]:.5f};
            const duty = {params["duty"]:.5f};
            const dur = {dur:.4f};
            try {{
              audio.volume = 0.9;
              await audio.play();
              return;
            }} catch (e) {{}}
            try {{
              const AC = window.AudioContext || window.webkitAudioContext;
              if (!AC) return;
              const ctx = new AC();
              await ctx.resume();
              const osc = ctx.createOscillator();
              const gain = ctx.createGain();
              const harmonics = 16;
              const real = new Float32Array(harmonics + 1);
              const imag = new Float32Array(harmonics + 1);
              for (let n = 1; n <= harmonics; n++) {{
                imag[n] = (2 / (n * Math.PI)) * Math.sin(n * Math.PI * duty);
              }}
              osc.setPeriodicWave(ctx.createPeriodicWave(real, imag));
              osc.frequency.value = freq;
              const now = ctx.currentTime;
              gain.gain.setValueAtTime(0.0001, now);
              gain.gain.exponentialRampToValueAtTime(Math.max(amp, 0.0001), now + 0.004);
              gain.gain.exponentialRampToValueAtTime(0.0001, now + dur);
              osc.connect(gain); gain.connect(ctx.destination);
              osc.start(now); osc.stop(now + dur + 0.01);
            }} catch (e2) {{}}
          }})();
        </script>
        """,
        height=0,
    )


@st.fragment(run_every=timedelta(milliseconds=speed_ms) if running else None)
def scroll_art():
    muted_for_label = SCROLLART in st.session_state.get("last_display", "")
    if running:
        nxt = next_generation(st.session_state.current)
        st.session_state.current = nxt
        display = format_row(nxt)
        st.session_state.history.append(display)
        st.session_state.last_display = display
        overflow = len(st.session_state.history) - visible_rows
        if overflow > 0:
            st.session_state.history = st.session_state.history[overflow:]

        muted_for_label = SCROLLART in display
        # Sound uses raw CA row `nxt`; scrollart! overlay only affects display mute.
        if sound_on and not muted_for_label:
            _play_retro_blip(nxt, speed_ms)

    frame = "\n".join(st.session_state.history[-visible_rows:])
    st.code(frame, language=None)

    if not sound_on:
        sound_note = "sound off"
    elif muted_for_label:
        sound_note = "silent (scrollart!)"
    else:
        sound_note = "16-bit blip"
    st.caption(
        f"generation {len(st.session_state.history)} · "
        f"{width} cells · {'scrolling' if running else 'paused'} · "
        f"{sound_note} · look for random “scrollart!” labels"
    )


scroll_art()
