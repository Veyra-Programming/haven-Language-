"""
Ani++ & Haven Signal Processing & Audio Engine (ani.signal / haven.signal)
Standard: Open Digital Continuity Standard (ODCS) Signal Subsystem
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides Fast Fourier Transform (FFT / DFT), Waveform Generators (Sine, Square,
Sawtooth, Triangle), Digital Low-Pass Filters, and pure-Python 16-bit PCM WAV audio synthesis.
"""

import math
import struct
import random
from typing import List, Tuple, Union, Optional


def dft(samples: List[Union[float, complex]]) -> List[complex]:
    """Computes the Discrete Fourier Transform (DFT) of a sequence."""
    N = len(samples)
    out: List[complex] = []
    for k in range(N):
        s = complex(0, 0)
        for n in range(N):
            angle = -2.0 * math.pi * k * n / N
            w = complex(math.cos(angle), math.sin(angle))
            s += samples[n] * w
        out.append(s)
    return out


def idft(spectrum: List[complex]) -> List[float]:
    """Computes the Inverse Discrete Fourier Transform (IDFT)."""
    N = len(spectrum)
    out: List[float] = []
    for n in range(N):
        s = complex(0, 0)
        for k in range(N):
            angle = 2.0 * math.pi * k * n / N
            w = complex(math.cos(angle), math.sin(angle))
            s += spectrum[k] * w
        out.append(s.real / N)
    return out


def fft(samples: List[Union[float, complex]]) -> List[complex]:
    """
    Computes the Fast Fourier Transform (FFT) using the radix-2 Cooley-Tukey algorithm.
    Pads with zeros to the next power of 2 if necessary.
    """
    n = len(samples)
    if n <= 1:
        return [complex(s) for s in samples]

    # Pad to power of 2
    next_pow2 = 1 << (n - 1).bit_length()
    if next_pow2 > n:
        x = [complex(s) for s in samples] + [complex(0, 0)] * (next_pow2 - n)
    else:
        x = [complex(s) for s in samples]

    return _fft_pow2(x)


def _fft_pow2(x: List[complex]) -> List[complex]:
    n = len(x)
    if n <= 1:
        return x
    even = _fft_pow2(x[0::2])
    odd = _fft_pow2(x[1::2])
    t = [complex(math.cos(-2 * math.pi * k / n), math.sin(-2 * math.pi * k / n)) * odd[k] for k in range(n // 2)]
    return [even[k] + t[k] for k in range(n // 2)] + [even[k] - t[k] for k in range(n // 2)]


def spectrum_magnitude(spectrum: List[complex]) -> List[float]:
    """Returns the absolute magnitude for each frequency bin."""
    return [round(abs(c), 6) for c in spectrum]


def sine_wave(freq: float, duration_s: float, sample_rate: int = 44100, amp: float = 1.0) -> List[float]:
    """Generates a pure sine wave."""
    n_samples = int(duration_s * sample_rate)
    return [amp * math.sin(2.0 * math.pi * freq * i / sample_rate) for i in range(n_samples)]


def square_wave(freq: float, duration_s: float, sample_rate: int = 44100, amp: float = 1.0) -> List[float]:
    """Generates a square wave."""
    n_samples = int(duration_s * sample_rate)
    period = sample_rate / freq
    return [amp if (i % period) < (period / 2.0) else -amp for i in range(n_samples)]


def sawtooth_wave(freq: float, duration_s: float, sample_rate: int = 44100, amp: float = 1.0) -> List[float]:
    """Generates a sawtooth wave."""
    n_samples = int(duration_s * sample_rate)
    period = sample_rate / freq
    return [amp * (2.0 * ((i % period) / period) - 1.0) for i in range(n_samples)]


def triangle_wave(freq: float, duration_s: float, sample_rate: int = 44100, amp: float = 1.0) -> List[float]:
    """Generates a triangle wave."""
    n_samples = int(duration_s * sample_rate)
    period = sample_rate / freq
    return [amp * (2.0 * abs(2.0 * ((i % period) / period) - 1.0) - 1.0) for i in range(n_samples)]


def lowpass_filter(samples: List[float], cutoff_freq: float, sample_rate: int = 44100) -> List[float]:
    """Applies a single-pole IIR low-pass filter to the input samples."""
    rc = 1.0 / (2.0 * math.pi * cutoff_freq)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)
    out: List[float] = []
    prev = 0.0
    for s in samples:
        filtered = prev + alpha * (s - prev)
        out.append(filtered)
        prev = filtered
    return out


def encode_wav(samples: List[float], sample_rate: int = 44100) -> bytes:
    """
    Encodes floating-point audio samples (normalized in [-1.0, 1.0]) into a standard
    16-bit mono RIFF WAV audio binary byte string.
    """
    num_samples = len(samples)
    bytes_per_sample = 2  # 16-bit
    data_size = num_samples * bytes_per_sample

    # Pack 16-bit PCM integer samples
    pcm_data = bytearray()
    for s in samples:
        clamped = max(-1.0, min(1.0, float(s)))
        int_sample = int(clamped * 32767.0)
        pcm_data.extend(struct.pack("<h", int_sample))

    # RIFF WAV header
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,              # Subchunk1Size (16 for PCM)
        1,               # AudioFormat (1 for PCM)
        1,               # NumChannels (Mono)
        sample_rate,     # SampleRate
        sample_rate * bytes_per_sample,  # ByteRate
        bytes_per_sample, # BlockAlign
        16,              # BitsPerSample
        b"data",
        data_size
    )
    return header + pcm_data
