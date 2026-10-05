"""16-bit-style retro sound derived from a Rule 90 CA row.

Sound is always computed from raw automaton cells (ALIVE/DEAD), never from
display overlays such as the "scrollart!" label.
"""

from __future__ import annotations

import math
import struct
import wave
from io import BytesIO

from rule90_scroll import ALIVE

# NTSC-ish chip-tune sample rate flavor; keep modest for short blips.
SAMPLE_RATE = 22050

# Square-wave pitches approximating a bright 16-bit arpeggio (Hz).
_CHIP_SCALE = (
    196.00,  # G3
    233.08,  # A#3
    261.63,  # C4
    311.13,  # D#4
    349.23,  # F4
    392.00,  # G4
    466.16,  # A#4
    523.25,  # C5
    622.25,  # D#5
    698.46,  # F5
    783.99,  # G5
    932.33,  # A#5
)


def row_sound_params(row) -> dict:
    """Map foremost CA row state to square-wave synthesis parameters.

    Returns frequency (Hz), amplitude (0..1), pulse duty (0.1..0.5), and
    whether the row is silent (no living cells).
    """
    width = len(row)
    if width == 0:
        return {
            "frequency": 0.0,
            "amplitude": 0.0,
            "duty": 0.25,
            "silent": True,
            "alive_count": 0,
            "density": 0.0,
        }

    alive_idx = [i for i, cell in enumerate(row) if cell == ALIVE]
    alive_count = len(alive_idx)
    density = alive_count / width
    if alive_count == 0:
        return {
            "frequency": 0.0,
            "amplitude": 0.0,
            "duty": 0.25,
            "silent": True,
            "alive_count": 0,
            "density": 0.0,
        }

    # Horizontal center of mass → scale degree (left low, right high).
    centroid = sum(alive_idx) / alive_count
    degree = int(round((centroid / max(width - 1, 1)) * (len(_CHIP_SCALE) - 1)))
    degree = max(0, min(len(_CHIP_SCALE) - 1, degree))
    frequency = _CHIP_SCALE[degree]

    # Sparse rows → thinner pulse + quieter; dense rows → fuller + louder.
    duty = 0.125 + 0.375 * density
    amplitude = 0.08 + 0.18 * math.sqrt(density)

    return {
        "frequency": frequency,
        "amplitude": amplitude,
        "duty": duty,
        "silent": False,
        "alive_count": alive_count,
        "density": density,
    }


def synthesize_square_pcm(
    frequency: float,
    duration_ms: int,
    amplitude: float = 0.2,
    duty: float = 0.25,
    sample_rate: int = SAMPLE_RATE,
) -> bytes:
    """Return little-endian signed 16-bit mono PCM for a pulse/square blip."""
    n_samples = max(1, int(sample_rate * duration_ms / 1000.0))
    if frequency <= 0 or amplitude <= 0:
        return b"\x00\x00" * n_samples

    period = sample_rate / frequency
    attack = max(1, int(0.004 * sample_rate))
    release = max(1, int(0.012 * sample_rate))
    peak = int(amplitude * 32767)
    out = bytearray()

    for i in range(n_samples):
        phase = (i % period) / period
        sample = peak if phase < duty else -peak
        # Tiny AD envelope so blips don't click like raw DC.
        if i < attack:
            env = i / attack
        elif i > n_samples - release:
            env = max(0.0, (n_samples - i) / release)
        else:
            env = 1.0
        out.extend(struct.pack("<h", int(sample * env)))
    return bytes(out)


def row_to_wav_bytes(row, duration_ms: int = 50) -> bytes | None:
    """Build a WAV blip from CA row state, or None if the row is silent."""
    params = row_sound_params(row)
    if params["silent"]:
        return None
    pcm = synthesize_square_pcm(
        frequency=params["frequency"],
        duration_ms=duration_ms,
        amplitude=params["amplitude"],
        duty=params["duty"],
    )
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)
    return buf.getvalue()
