# Aoede
Make crappy music with this weird and unintuitive tool.

## Usage

```python
# Mary had a little lamb

import Aoede as ao

s = ao.Song()

# pick your pitches and note durations
notes = ['G3', 'E3', 'D3', 'C3', 'G2', 'E2', 'C2']
note_durations = {'quarter': 1, 'half': 2, 'whole': 4}

# create the notes
for note in notes:
    for k, v in note_durations.items():
        sound = s.make_sound(pitch=note, form='triangle', duration=v)
        s.add(sound, '{0}_{1}'.format(note, k))

# placements
s.insert('G3_quarter', 14)
s.insert('E3_quarter', [1, 5, 6, 13, 17, 21, 22, 23, 24, 27])
s.insert('D3_quarter', [2, 4, 9, 10, 18, 20, 25, 26, 28])
s.insert('C3_quarter', [3, 19])
s.insert('G3_half', 15)
s.insert('E3_half', 7)
s.insert('D3_half', 11)
s.insert('C3_whole', 29)

s.insert('G2_half', [11, 27])
s.insert('E2_half', [3, 7, 9, 15, 19, 23, 25])
s.insert('C2_half', [1, 5, 13, 17, 21])
s.insert('C2_whole', 29)

s.play()
```
