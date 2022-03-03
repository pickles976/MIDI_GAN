from utils import preProcess, preProcess2,standardizeTrack,removeNullNotes,midiToPng2, midiToPng, pngToMidi
import subprocess
import os
import sys
from mido import MidiFile

# RAW, PROCESS = "NES_MIDI_RAW","NES_MIDI_PROCESS"
# PNG, FINAL = "NES_PNG","NES_PNG_MIDI"

# RAW, PROCESS = "GB_MIDI_RAW","GB_MIDI_PROCESS"
# PNG, FINAL = "GB_PNG","GB_PNG_MIDI"

# RAW, PROCESS = "TEST_MIDI_RAW","TEST_MIDI_PROCESS"
# PNG, FINAL = "TEST_PNG","TEST_PNG_MIDI"


def process_v1():

    # pre-process files
    for fn in os.listdir(RAW):

        infile,outfile = os.path.join(RAW,fn), os.path.join(PROCESS,fn)
        preProcess(infile,outfile)

    # MIDI files to PNG
    for fn in os.listdir(PROCESS):

        name = fn.split(".")[0]
        infile,outfile = os.path.join(PROCESS,fn),os.path.join(PNG,name+".png")
        midiToPng(infile,outfile)

    # PNG back to MIDI
    for fn in os.listdir(PNG):

        name = fn.split(".")[0]
        infile,outfile = os.path.join(PNG,fn),os.path.join(FINAL,name+".mid")
        pngToMidi(infile,outfile)

def process_v2():
    """ Process the NES db midi files
    """
    RAW, PROCESS = "NESDB_MIDI_RAW","NESDB_MIDI_PROCESS"
    PNG, FINAL = "NESDB_PNG","NESDB_PNG_MIDI"

        # pre-process files
    for fn in os.listdir(RAW):

        infile,outfile = os.path.join(RAW,fn), os.path.join(PROCESS,fn)

        print(f"pre-processing {infile}")

        midi = MidiFile(infile,type=1,clip=True)
        midi = standardizeTrack(midi)
        midi = preProcess2(midi)
        midi = removeNullNotes(midi)
        midi.save(outfile)

    # MIDI files to PNG
    for fn in os.listdir(PROCESS):

        name = fn.split(".")[0]
        infile,outfile = os.path.join(PROCESS,fn),os.path.join(PNG,name+".png")
        midiToPng2(infile,outfile)

    # PNG back to MIDI
    for fn in os.listdir(PNG):

        name = fn.split(".")[0]
        infile,outfile = os.path.join(PNG,fn),os.path.join(FINAL,name+".mid")
        pngToMidi(infile,outfile)

if __name__ == "__main__":

    args=sys.argv
    globals()[args[1]](*args[2:])