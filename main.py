from mido import MidiFile, MidiTrack, Message
from utils import midiToPng, preProcess, pngToMidi

# song = "002_1943_TheBattleofMidway_03_04AirBattleA.mid"
# song = "045_Castlevania_01_02VampireKiller.mid"
song = "323_SuperMarioBros_2_02_03Overworld.mid"

midi = MidiFile(song,type=1,clip=True)

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
                                # replace missing note with control change
                                newTrack[note_off] = Message("control_change",channel=message.channel,control=7,value=10,time=message.time)
                                newTrack.pop(j)

            midi.tracks[i] = newTrack

        i += 1
    return midi


# standardize the midi track
midi = standardizeTrack(midi)    
midi.save("vampire.mid")

# pre-process the midi track
preProcess("vampire.mid","vampire_process.mid")
midi2 = MidiFile("vampire_process.mid")

# remove all of the zero-duration notes from the midi track
midi3 = removeNullNotes(midi2)
midi3.save("vampire_fixed.mid")

midiToPng("vampire_fixed.mid","vampire.png")
pngToMidi("vampire.png","test.mid")



