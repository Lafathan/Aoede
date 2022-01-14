#!/usr/bin/env python3
from typing import Union

import numpy as np
import soundfile as sf

from player import play

SR = 44100  # default sample rate
CN = 2  # default channel number

# wave generating functions
wave_functions = {
    'sine': lambda a, f, d, s: a * np.sin(2 * np.pi * f * np.linspace(0, d, int(d * s))),
    'sawtooth': lambda a, f, d, s: a * (2 * np.mod(2 * f * np.linspace(0, d, int(d * s)), 2) - 1),
    'square': lambda a, f, d, s: a * np.mod(np.floor(2 * f * np.linspace(0, d, int(d * s))), 2),
    'triangle': lambda a, f, d, s:
        a * 2 * np.abs(2 * (np.linspace(0, d, int(d * s)) * f - np.floor(np.linspace(0, d, int(d * s)) * f + 0.5))) - 1
}


class Sound(object):

    def __init__(self, data: np.array, samplerate: int):
        self.data = data
        self.samplerate = samplerate

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __len__(self):
        return len(self.data[0])

    def play(self):
        play(self.data, self.samplerate)

    @property
    def channels(self):
        if len(self.data.shape) == 1:
            return 1
        else:
            return self.data.shape[0]

    def export(self, file):
        sf.write(file=file, data=self.data.T, samplerate=self.samplerate)

    def resample(self, samplerate: int = SR):
        gcd = np.gcd.reduce([self.samplerate, samplerate])
        up_sample(self, int(samplerate / gcd))
        decimate(self, int(self.samplerate / gcd))
        self.samplerate = samplerate


class Wave(Sound):

    def __init__(self, samplerate: int = SR, channels: int = CN, amplitude: float = 1.0,
                 frequency: float = 440.0, duration: float = 1, form='sine'):
        self.samplerate = samplerate
        self._channels = channels
        self.amplitude = amplitude
        self.frequency = frequency
        self.duration = duration
        self.form = form
        self.generate()

    def generate(self):
        _data = wave_functions[self.form](self.amplitude, self.frequency, self.duration, self.samplerate)
        self.data = np.tile(_data, (self._channels, 1))


def up_sample(s: Sound, factor: int = 2):
    _x = np.linspace(0, len(s), len(s) * factor)
    x = np.arange(len(s))
    s.data = np.array([np.interp(_x, x, _) for _ in s.data])
    return


def decimate(s: Sound, factor: int = 2):
    s.data = s[:, ::factor]
    return


def ideal_filter(s: Sound, shape: str = 'lowpass', cutoff: Union[float, tuple] = 22500, gain: tuple = (0, 1)):

    # map to function for filter conditionals
    func_map = {
        'lowpass': lambda x: abs(x) > cutoff,
        'bandpass': lambda x: abs(x) < min(cutoff) or abs(x) > max(cutoff),
        'highpass': lambda x: abs(x) < cutoff,
        'notch': lambda x: min(cutoff) < abs(x) < max(cutoff)
    }

    # map to multiplier values
    mult = {
        True: gain[0],
        False: gain[1]
    }

    # calculate the fft
    _freq = np.fft.fftfreq(len(s), d=1.0 / s.samplerate)
    _fft = np.array([np.fft.fft(s[c]) for c in range(s.channels)])

    # apply filter to spectrum
    for i, freq in enumerate(_freq):
        for j in range(len(_fft)):
            _fft[j][i] *= mult[func_map[shape](freq)]

    # inverse fft
    s.data[:] = len(s) * np.array([np.fft.ifft(c) for c in _fft])

    return
