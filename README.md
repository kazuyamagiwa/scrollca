# scrollca

Cellular automata scrollart!

Rule 90 scrolling Sierpiński triangle — available in Python, BASIC, C, and Streamlit.

## Python (terminal)

```bash
python3 rule90_scroll.py
```

Press `Ctrl+C` to stop.

## BASIC (FreeBASIC)

```bash
fbc rule90_scroll.bas -x rule90_scroll_bas
./rule90_scroll_bas
```

## C

```bash
gcc -O2 -o rule90_scroll_c rule90_scroll.c
./rule90_scroll_c
```

## Streamlit

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (usually http://localhost:8501). Use the sidebar to change width, visible rows, scroll speed, pause, reset, or enable **16-bit sound**.

Sound is a square/pulse blip driven by the foremost CA row (pitch from the alive-cell center, pulse width from density). Rows that display the random `scrollart!` overlay stay silent.
