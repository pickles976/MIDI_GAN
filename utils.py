from mido import MidiFile, MidiTrack, Message, MetaMessage
import numpy as np
import cv2
import sys

# 128x128 = 16384
# 256x256 = 65,536
MIN_NOTE = 32 # smallest possible note, 32nd note
MIN_VALUE = 500000 # approx length of song
DIM = 256 
SIZE = DIM ** 2
NUM_TRACKS = 4

def preProcess(song,newsong):

    print(f"Processing {song}")

    try:

        midi = MidiFile(song)
        midi.type = 1

        tpb = midi.ticks_per_beat   # normalize the ticks per beat
        midi.ticks_per_beat = MIN_NOTE
        div = tpb / MIN_NOTE

        # remove duplicate tracks
        message_numbers = []
        duplicates = []

        for track in midi.tracks:
            if len(track) in message_numbers:
                duplicates.append(track)
            else:
                message_numbers.append(len(track))

        for track in duplicates:
            midi.tracks.remove(track)

        # loop through all midi tracks
        for track in midi.tracks:
            
            # print(track)

            i = 0
            for message in track:

                # normalize time, 1 == 32nd note
                if message.time:
                    message.time = int(message.time / div)

                # normalize data format
                if message.type and message.type == "note_off":
                    track[i] = Message('note_on', channel=message.channel,note=message.note, velocity=0, time=message.time)

                i += 1

        # save the midi with normalized timestamps
        midi.save(newsong)

    except:
        print("Pr-Processing failed!")

def pngToMidi(imgfile,midifile):

    print(f"Converting {imgfile} to {midifile}")

    try:

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
            track.append(MetaMessage("set_tempo",tempo=500000,time=0))
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

    except:

        print(f"Failed to convert {imgfile}!")

def midiToPng(song,image):

    print(f"Converting {song} to {image}")

    try:

        total = 0

        array = np.zeros(SIZE,np.uint8)

        midi = MidiFile(song)

        offset = int(SIZE / NUM_TRACKS)

        n = 0
        for midiTrack in midi.tracks:

            if len(midiTrack) > 24:

                track = [t for t in reversed(midiTrack)]

                i = offset * n # pointer to array index
                lim = offset * (n + 1)
                curNote = 0
                count = 0 # duration of current note
                lastCtrl = False # if the last message was a control message
                while len(track) > 0 and i < lim:

                    message = track.pop()
                    # print(message)

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
                                total += curNote * count
                                i += count + 1
                                count = 0

                # iterate
                n += 1

        if total > MIN_VALUE:
            array = np.reshape(array, (DIM, DIM))
            cv2.imwrite(image,array)
        else: 
            print("Song was too short!")

    except:
        print(f"Failed to convert {song}")


if __name__ == "__main__":

    args=sys.argv
    globals()[args[1]](*args[2:])

    # midiToPng("new_song.mid","song.png")
    # pngToMidi("song.png","png_song.mid")
    

        

        

