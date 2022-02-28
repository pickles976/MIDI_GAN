from mido import MidiFile, MidiTrack, Message, MetaMessage
import numpy as np
import cv2

MIN_NOTE = 32

midi = MidiFile()
track = MidiTrack()
midi.tracks.append(track)
midi.ticks_per_beat = MIN_NOTE

# start song
track.append(MetaMessage("set_tempo",tempo=324324,time=0))

# set instrument
track.append(Message('program_change', program=87, time=0))
track.append(Message('control_change', channel=0, control=10, value=64, time=0))

imgfile = "song.png"

img = cv2.imread(imgfile,cv2.IMREAD_GRAYSCALE)

array = np.asarray(img)
array = np.reshape(array,65536)

currentNote = 0
prevNote = 0
count = 0

for i in range(0,16248,1):

    # if the current spot in the array is a new note
    if array[i] != currentNote:

        # append the previous note
        if currentNote == 0: # the preceeding note was a rest
            track.append(Message("note_on",velocity=100,note=array[i],time=count))
        else: # the preceeding note was another note
            track.append(Message("note_on",velocity=0,note=currentNote,time=count))
            if array[i] != 0:
                track.append(Message("note_on",velocity=100,note=array[i],time=0))

        # update the current note and count
        currentNote = array[i]
        count = 0
    else:
        count += 1

midi.save('png_song.mid')
    

        

        

