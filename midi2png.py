from mido import MidiFile, Message
import numpy as np
import cv2

# MIDI NOTES ARE 0-127 INCLUSIVE
# TRY TO TRANSLATE 

song = "new_song.mid"

DIM = 256
SIZE = DIM**2

# 128x128 = 16384
# 256x256 = 65,536
array = np.zeros(SIZE,np.uint8)

midi = MidiFile(song)
track = [t for t in reversed(midi.tracks[1])]

i = 0 # pointer to array index
curNote = 0
count = 0 # duration of current note
lastCtrl = False # if the last message was a control message
while len(track) > 0:

    message = track.pop()

    if not message.is_meta:

        # get message time
        t = message.time
        count += t

        # message type is note on
        if message.type == "note_on":

            v = message.velocity

            if v != 0: # if note on
                if t == 0: # if note is instant
                    curNote = message.note
                else: # if note is not instant
                    i += t + 1
                    count = 0
            else: # note off
                array[i:i+count+1] = curNote
                i += count + 1
                count = 0

array = np.reshape(array, (DIM, DIM))
cv2.imwrite('song.png',array)