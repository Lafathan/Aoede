#!/usr/bin/env python3
from typing import Union
from re import match

import numpy as np
import soundfile as sf

from sounds import Sound, Wave
from player import play

# default values
A0 = 27.5   # reference pitch
SR = 44100  # sample rate
CN = 2      # number of channels
BPM = 120   # beats per minute


class Song(object):

    def __init__(self, samplerate: int = SR, channels: int = CN, bpm: int = BPM):
        # initialize the elements of the song
        self._data = np.array([])
        self.samplerate = samplerate
        self.channels = channels
        self.bpm = bpm
        self.sounds = {}
        self.placements = {}

    def add(self, sound: Sound, name: str = None):
        # add a sound to the song for easy access
        if not name:
            # give it a name if one wasn't given
            name = str(len(self.sounds) + 1)
        self.sounds[name] = sound
        # create an empty list of placements
        self.placements[name] = []

    def insert(self, name: str, locations: Union[float, list]):
        # insert the sound into the song
        if name not in self.placements:
            print('Unknown sound')
            return
        # add the new locations to the sounds locations list
        if type(locations) == list:
            self.placements[name].extend(locations)
        else:
            self.placements[name].append(locations)

    def load_sound(self, file: str) -> Sound:
        # load a sound file
        data, samplerate = sf.read(file)
        s = Sound(data.T, samplerate)
        # add channels if necessary
        if s.channels == 1:
            s.data = np.tile(data, (self.channels, 1))
        # resample if necessary
        if samplerate != self.samplerate:
            s.resample(self.samplerate)
        # return the sound
        return s

    def make_sound(self, form: str = 'sine', amplitude: float = 1.0, pitch: Union[str, float] = 'A4',
                   duration: float = 4) -> Union[Wave, None]:
        # get duration in seconds
        duration = duration * 60 / self.bpm
        # get the pitch from a given note string
        if type(pitch) == str:
            m = match(r'^(?P<note>[ABCDEFG])(?P<semi>[b#])?(?P<octave>\d)$', pitch)
            # check formatting
            if not (m['note'] and m['octave']):
                print('Improper pitch string')
                return
            # calculate the "piano distance" from the frequency/key reference
            dist_from_ref = int(m['octave']) * 12 + round(1.64 * (ord(m['note']) - ord('A') + 1) - 1.57)
            if m['semi']:
                if m['semi'] == 'b':
                    dist_from_ref -= 1
                else:
                    dist_from_ref += 1
            # calculate the frequency
            frequency = A0 * np.power(2, dist_from_ref / 12)
        else:
            frequency = pitch
        # generate and return the sound
        return Wave(self.samplerate, self.channels, amplitude, frequency, duration, form)

    def generate_data(self):
        # make an empty array of sound data large enough to contain the whole song
        max_index = 0
        for name in self.sounds:
            sound, placements = self.sounds[name], self.placements[name]
            if placements:
                max_index = max([max_index, len(sound) + self.samplerate * 60 * max(placements) / self.bpm])
        data = np.tile(np.zeros(int(max_index) + 1), (self.channels, 1))

        # place all the sounds where they need to be placed
        for name in self.sounds:
            sound, placements = self.sounds[name], self.placements[name]
            for p in placements:
                first = int(self.samplerate * 60 * p / self.bpm)
                last = first + len(sound)
                for _ in range(self.channels):
                    data[_][first:last] += sound[_]

        self._data = data[:]

    def play(self, start: float = 0):
        # make sure the song data has been generated
        self.generate_data()
        # calculate the start offset
        _start = int(60 * start / self.bpm)
        # play the damn song
        play(self._data, self.samplerate, _start)
