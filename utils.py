from mido import MidiFile, MidiTrack, Message, MetaMessage
import numpy as np
import cv2

# 128x128 = 16384
# 256x256 = 65,536
MIN_NOTE = 32 # smallest possible note, 32nd note
DIM = 256 
SIZE = DIM ** 2
NUM_TRACKS = 4

def pngToMidi(imgfile,midifile):

    offset = int(SIZE / NUM_TRACKS)

    # create midifile
    midi = MidiFile()

    img = cv2.imread(imgfile,cv2.IMREAD_GRAYSCALE)
    array = np.asarray(img)
    array = np.reshape(array,SIZE)

    for n in range(NUM_TRACKS):

        # create midi track
        track = MidiTrack()
        midi.tracks.append(track)
        midi.ticks_per_beat = MIN_NOTE

        # start song
        track.append(MetaMessage("set_tempo",tempo=324324,time=0))
        # set instrument
        track.append(Message('program_change', program=87, time=0))
        track.append(Message('control_change', channel=0, control=10, value=64, time=0))

        currentNote = 0
        count = 0
        for i in range(offset*n,offset*(n+1),1):

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

    # save out to midi
    midi.save(midifile)

def midiToPng(song,image):

    array = np.zeros(SIZE,np.uint8)

    midi = MidiFile(song)

    offset = int(SIZE / NUM_TRACKS)

    n = 0
    for midiTrack in midi.tracks:

        print(midiTrack)
        if len(midiTrack) > 24:

            track = [t for t in reversed(midiTrack)]

            i = offset * n # pointer to array index
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

            # iterate
            n += 1

    array = np.reshape(array, (DIM, DIM))
    cv2.imwrite(image,array)

if __name__ == "__main__":

    midiToPng("new_song.mid","song.png")
    pngToMidi("song.png","png_song.mid")
    

        

        

