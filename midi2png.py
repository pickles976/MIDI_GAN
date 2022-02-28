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
track = [t for t in reversed(midi.tracks[2])]


# i = 0
# curNote = 0
# instant = False # if the note time was 0
# while len(track) > 0:

#     message = track.pop()

#     if type(message) == Message:

#         t = message.time

#         if message.type == "note_on":

#             v = message.velocity

#             # note on
#             if v != 0:
#                 if t == 0:
#                     curNote = message.note
#                     array[i] = curNote
#                     instant = True
#                 else:
#                     array[i:i+t+1] = curNote
#             else: # note off
#                 if instant:
#                     t = t - 1 # compensate for t = 0 notes
        
#         elif message.type == "control_change":
#             if t != 0:
#                 array[i:i+t+1] = curNote

#         # move pointer
#         i = i + t + 1

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