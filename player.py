#!/usr/bin/env python3

import numpy as np
import sounddevice as sd


def play(out=None, samplerate: int = 44100, start: float = 0):

    # return if no signal is given
    if out is None:
        return

    out = out / np.max(out)     # normalize the input signal
    index = start * samplerate  # skip to the desired start
    channels = len(out.shape)   # grab the number of channels

    def callback(buffer, frames, time, status):
        if status:
            print(status)
        nonlocal index

        if index + frames > len(out):
            sd.CallbackStop()

        if channels == 1:
            _out = out[index:index+frames]
            _out = np.pad(_out, (0, frames - len(_out)), mode='constant')
            _out = np.array([_out])
        else:
            _out = out[:, index:index+frames]
            _out = np.pad(_out, ((0, 0), (0, frames - len(_out[0]))), mode='constant')

        buffer[:] = _out.T
        index += frames

    try:
        with sd.OutputStream(channels=channels, samplerate=samplerate, callback=callback):
            print('press Return to quit')
            input()
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))
