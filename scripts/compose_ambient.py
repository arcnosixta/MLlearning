"""Render an original, seamless IMlearning ambient loop (no external recordings).

Authoring utility: requires the project's existing NumPy dependency. The generated
PCM WAV is committed and copied as a static asset; deployment does not synthesize it.
"""
from pathlib import Path
import wave
import numpy as np

RATE = 22050
DURATION = 38.4
COUNT = int(RATE * DURATION)
audio = np.zeros(COUNT, dtype=np.float64)

def note(midi, start, duration, level, soft=True):
    frequency = 440 * 2 ** ((midi - 69) / 12)
    t = np.arange(int(duration * RATE)) / RATE
    attack = .65 if soft else .035
    release = 1.2 if soft else .65
    envelope = np.minimum(t / attack, 1) * np.minimum((duration - t) / release, 1)
    tone = np.sin(2 * np.pi * frequency * t)
    tone += .18 * np.sin(2 * np.pi * frequency * 2 * t)
    tone += .045 * np.sin(2 * np.pi * frequency * 3 * t)
    if not soft:
        envelope *= np.exp(-t * 1.8)
    signal = tone * envelope * level
    offset = int(start * RATE)
    # Notes crossing the end continue at the start: the loop has no dead gap.
    np.add.at(audio, (np.arange(len(t)) + offset) % COUNT, signal)

chords = [(48, 55, 59, 64), (45, 52, 55, 60), (41, 48, 52, 57), (43, 50, 57, 62)] * 2
melody = [(76, 79, 83, 79), (76, 72, 74, 76), (77, 76, 72, 69), (74, 79, 81, 74),
          (79, 76, 71, 76), (72, 76, 79, 76), (77, 81, 79, 76), (74, 71, 69, 67)]
for bar, chord in enumerate(chords):
    start = bar * 4.8
    for midi in chord:
        note(midi, start, 6.2, .043)
    note(chord[0] - 12, start, 4.7, .026)
    for beat, midi in enumerate(melody[bar]):
        note(midi, start + beat * 1.2 + .25, 2.1, .052, False)
        note(midi, start + beat * 1.2 + .85, 2.1, .012, False)

audio = np.tanh(audio * 1.6)
audio *= .7 / max(1, abs(audio).max())
target = Path(__file__).resolve().parents[1] / 'audio' / 'orbit.wav'
target.parent.mkdir(exist_ok=True)
with wave.open(str(target), 'wb') as output:
    output.setnchannels(1)
    output.setsampwidth(2)
    output.setframerate(RATE)
    output.writeframes((audio * 32767).astype('<i2').tobytes())
print(f'Composed Orbit: {DURATION}s, {target.stat().st_size} bytes')
