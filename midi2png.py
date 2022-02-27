from mido import MidiFile, Message
import numpy as np
import cv2

song = "new_song.mid"

DIM = 256
SIZE = DIM**2

# 128x128 = 16384
# 256x256 = 65,536
array = np.zeros(SIZE,np.uint8)

midi = MidiFile(song)
track = [t for t in reversed(midi.tracks[2])]

i = 0
# toggle = True
while len(track) > 0:

    message = track.pop()

    if type(message) == Message:

        # get message time
        t = message.time

        curNote = 0

        # message type is note on
        if message.type == "note_on":

            v = message.velocity

            # if note off
            if t != 0:
                curNote = message.note
                array[i:i+t+1] = curNote # set pitch value for note
            if v != 0 and t != 0:
                print(message)

        elif message.type == "control_change":
            if t != 0:
                print(message)
                array[i:i+t+1] = curNote

        if t != 0:
            # move pointer, fk
            i = i + t + 1

array = np.reshape(array, (DIM, DIM))
cv2.imwrite('song.png',array)