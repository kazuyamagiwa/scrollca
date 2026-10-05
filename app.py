"""Streamlit viewer for Rule 90 scroll art."""

from datetime import timedelta

import streamlit as st

from rule90_scroll import initial_row, next_generation

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
    reset = st.button("Reset", use_container_width=True)


def _reset_state(new_width: int) -> None:
    row = initial_row(new_width)
    st.session_state.width = new_width
    st.session_state.current = row
    st.session_state.history = ["".join(row)]


if (
    "history" not in st.session_state
    or "current" not in st.session_state
    or st.session_state.get("width") != width
    or reset
):
    _reset_state(width)


@st.fragment(run_every=timedelta(milliseconds=speed_ms) if running else None)
def scroll_art():
    if running:
        nxt = next_generation(st.session_state.current)
        st.session_state.current = nxt
        st.session_state.history.append("".join(nxt))
        overflow = len(st.session_state.history) - visible_rows
        if overflow > 0:
            st.session_state.history = st.session_state.history[overflow:]

    frame = "\n".join(st.session_state.history[-visible_rows:])
    st.code(frame, language=None)
    st.caption(
        f"generation {len(st.session_state.history)} · "
        f"{width} cells · {'scrolling' if running else 'paused'}"
    )


scroll_art()
