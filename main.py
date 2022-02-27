from mido import MidiFile, tempo2bpm, Message, MidiTrack

# song = "1943-lev1.mid"
song = "PkmGS-Battle1.mid"

MIN_NOTE = 32
# song = "002_1943_TheBattleofMidway_03_04AirBattleA.mid"
# song = "new_song.mid"

midi = MidiFile(song)

# for message in midi.tracks[0]:
#     print(message)

tpb = midi.ticks_per_beat
midi.ticks_per_beat = MIN_NOTE

div = tpb / MIN_NOTE

print(tpb)
print(div)

# loop through all midi tracks
for track in midi.tracks:
    # print(track)
    for message in track:

        print(message)

        # normalize time, 1 == 32nd note
        if message.time:
            message.time = int(message.time / div)

        # normalize data format
        if message.type and message.type == "note_off":
            message = Message('note_on', note=message.note, velocity=message.velocity, time=message.time)

midi.save('new_song.mid')

# save isolate track
m = MidiFile(type=1)
m.ticks_per_beat = MIN_NOTE
m.tracks.append(midi.tracks[0])
m.tracks.append(midi.tracks[2])
m.save('isolated.mid')