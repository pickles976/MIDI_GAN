from mido import MidiFile, MidiTrack, Message, MetaMessage
import numpy as np
import cv2
import sys

# 128x128 = 16384
# 256x256 = 65,536
MIN_NOTE = 64 # smallest possible note, 32nd note
MIN_VALUE = 500000 # approx length of song
DIM = 256 
SIZE = DIM ** 2
NUM_TRACKS = 4

def preProcess(song,newsong):
    """ Remove duplicate tracks, standardize time, and change note_on to note_off
    """

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
            note_on = None
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
        print("Pre-Processing failed!")

def pngToMidi(imgfile,midifile):

    print(f"Converting {imgfile} to {midifile}")

    try:

        offset = int(SIZE / NUM_TRACKS)

        # create midifile
        midi = MidiFile(type=1)

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
            print(f"Song was too short! {total}")

    except:
        print(f"Failed to convert {song}")

# THESE ARE FOR THE NESDB MIDI FILES ONLY!!!

def midiToPng2(song,image):
    """ For use with special NES database MIDIs 
    """

    print(f"Converting {song} to {image}")

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
            curNote = None
            count = 0 # duration of current note
            while len(track) > 0 and i < lim:

                message = track.pop()

                if not message.is_meta:

                    # get message time
                    t = message.time
                    count += t

                    # message type is note on
                    if message.type == "note_on":

                        v = message.velocity

                        if v != 0: # if note on
                            curNote = message.note
                            count = 0

                            if t != 0: # if note is not instant
                                i += t + 1
                        else: # note off
                            array[i:i+count+1] = curNote
                            total += curNote * count
                            i += count + 1
                            count = 0
                            curNote = None

                    else: # deal with control changes in-between notes 
                        if not curNote:
                            i += count + 1
                            count = 0

            # iterate
            n += 1

    if total > MIN_VALUE:
        array = np.reshape(array, (DIM, DIM))
        cv2.imwrite(image,array)
    else: 
        print(f"Song was too short! {total}")

def removeNullNotes(midi):
    """ Removes the zero-duration notes created during the de-overlapping process.
    """

    print("Removing null notes")

    i = 0
    for track in midi.tracks:

        # track is after first track
        if i > 0:

            newTrack = track[:]
            note_off = len(track) - 1

            # loop through the track backwards
            for j in range(len(track) - 1,0,-1):
                
                message = newTrack[j]

                if not message.is_meta:
                    if message.type == "note_on":

                        # note off 
                        if message.velocity == 0:
                            note_off = j
                        else: # note on
                            if newTrack[note_off].time == 0:
                                # replace missing note with control change (duration 1 notes break songs)
                                newTrack[note_off] = Message("control_change",channel=message.channel,control=7,value=10,time=message.time)
                                newTrack.pop(j)

            midi.tracks[i] = newTrack

        i += 1
    return midi

def standardizeTrack(midi):
    """ Removes zero-duration notes and pads the empty space with
        a dummy control-change

    """

    i = 0
    for track in midi.tracks:

        # skip metadata track
        if i > 0:

            newTrack = []
            note1,note2 = [],[] # using dynamic-programming to un-overlap overlapping notes

            j = 0
            for message in track:

                if not message.is_meta:

                    message.channel = i - 1

                    # if there is a current Note1 candidate
                    if len(note1) > 0:
                        if message.type == "note_on": # if note message
                            if message.note == note1[0].note: # if note matches last note
                                
                                # swap note durations to cancel overlap
                                if note2:
                                    temp = message.time
                                    message.time = note2[0].time
                                    note2[0].time = temp

                                # add note1 to the track and clear note2, push note2 onto the note1 stack
                                note1.append(message)
                                for m in note1:
                                    newTrack.append(m)
                                note1 = note2
                                note2 = []
                            else: # max out the volume, get the overlapping note
                                if message.velocity != 0:
                                    message.velocity = 100
                                note2.append(message)
                        else: # just append control statements to note1
                            note1.append(message)
                    else: # note1 is empty, either it's the start of the track-- or no overlaps have occured
                        if message.type == "note_on": # max out the volume and initialize note1 stack
                            message.velocity = 100
                            note1.append(message)
                        else:
                            newTrack.append(message) # just append empty control messages

                else: # append meta messages
                    newTrack.append(message)

            # replace with fixed track
            midi.tracks[i] = newTrack

        # print(track)
        i += 1

    return midi

def preProcess2(midi):
    """ Remove duplicate tracks, standardize time, and change note_on to note_off
    """

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
        note_on = None
        i = 0
        for message in track:

            # normalize time, 1 == 32nd note
            if message.time:
                message.time = int(message.time / div)

            # normalize data format
            if message.type and message.type == "note_off":
                track[i] = Message('note_on', channel=message.channel,note=message.note, velocity=0, time=message.time)

            i += 1

    return midi


if __name__ == "__main__":

    args=sys.argv
    globals()[args[1]](*args[2:])
    

        

        

