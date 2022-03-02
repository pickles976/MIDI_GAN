from mido import MidiFile, MidiTrack
from utils import midiToPng, preProcess, pngToMidi

song = "002_1943_TheBattleofMidway_03_04AirBattleA.mid"
# song3 = "045_Castlevania_01_02VampireKiller.mid"

midi = MidiFile(song,type=1,clip=True)

j = 0
for message in midi.tracks[1]:
    if j < 20:
        print(message)
    j += 1

i = 0
for track in midi.tracks:

    if i > 0:

        newTrack = []
        note1,note2 = [],[]

        j = 0
        for message in track:

            if not message.is_meta:

                message.channel = i - 1

                # if there is a current Note1 candidate
                if len(note1) > 0:
                    if message.type == "note_on":
                        if message.note == note1[0].note:
                            
                            # prevent zero-duration note
                            if note2:
                                temp = message.time
                                message.time = note2[0].time
                                note2[0].time = temp

                            note1.append(message)
                            for m in note1:
                                newTrack.append(m)
                            note1 = note2
                            note2 = []
                        else:
                            if message.velocity != 0:
                                message.velocity = 100
                            note2.append(message)
                    else:
                        note1.append(message)
                else:
                    if message.type == "note_on":
                        message.velocity = 100
                        note1.append(message)
                    else:
                        newTrack.append(message)

            else:
                newTrack.append(message)

        else:
            newTrack.append(message)

        midi.tracks[i] = newTrack

    i += 1
    
midi.save("vampire.mid")

print("New File: ")

j = 0
for msg in midi.tracks[1]:
    if j < 20:
        print(msg)
    j += 1


# preProcess("vampire.mid","vampire_process.mid")

# midi2 = MidiFile("vampire_process.mid")

# for track in midi2.tracks[0]:
#     print(track)

# midi2 = MidiFile("vampire_process.mid")

# midiToPng("vampire_process.mid","vampire.png")
# pngToMidi("vampire.png","test.mid")

# midi3 = MidiFile("test.mid")



