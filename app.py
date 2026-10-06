"""Streamlit viewer for Rule 90 scroll art with iOS-safe 16-bit retro blips."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from scrollca_player import build_scrollca_html, player_height

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
    section[data-testid="stSidebar"] {
        background: #10161f;
        border-right: 1px solid #243044;
    }
    iframe {
        border: 1px solid #243044 !important;
        background: #05070a;
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
        "center, pulse width from density. Rows that show “scrollart!” stay silent."
    )
    if sound_on:
        st.info(
            "On iPhone/iPad: tap **Tap to enable sound** in the viewer once. "
            "iOS only unlocks audio inside that same view after a real tap."
        )
    reset = st.button("Reset", use_container_width=True)

# Bump a nonce on Reset so the iframe remounts and restarts the CA.
if "viewer_nonce" not in st.session_state:
    st.session_state.viewer_nonce = 0
if reset:
    st.session_state.viewer_nonce += 1

html = build_scrollca_html(
    width=width,
    visible_rows=visible_rows,
    speed_ms=speed_ms,
    sound_on=sound_on,
    running=running,
)
# Include nonce in a comment so Streamlit treats Reset as a new component payload.
html = f"<!-- nonce:{st.session_state.viewer_nonce} -->" + html

components.html(html, height=player_height(visible_rows, sound_on), scrolling=False)
