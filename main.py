from mido import MidiFile, MidiTrack, Message
from utils import midiToPng, preProcess2, removeNullNotes, midiToPng2, standardizeTrack

song = "002_1943_TheBattleofMidway_03_04AirBattleA.mid"
# song = "045_Castlevania_01_02VampireKiller.mid"
# song = "323_SuperMarioBros_2_02_03Overworld.mid"
# song = "PkmGS-Battle1.mid"
# song = "1943-lev1.mid"

midi = MidiFile(song,type=1,clip=True)
midi = standardizeTrack(midi)
midi = preProcess2(midi)
midi = removeNullNotes(midi)
midi.save("out.mid")
