from utils import preProcess, midiToPng, pngToMidi
import subprocess
import os

# RAW, PROCESS = "NES_MIDI_RAW","NES_MIDI_PROCESS"
# PNG, FINAL = "NES_PNG","NES_PNG_MIDI"

RAW, PROCESS = "GB_MIDI_RAW","GB_MIDI_PROCESS"
PNG, FINAL = "GB_PNG","GB_PNG_MIDI"


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