#name=_Launchpad Toggler
#url=www.jammingsignal.com

import patterns
import channels
import mixer
import device
import transport
import arrangement
import general
import launchMapPages
import playlist
import ui
import screen
import midi
import utils
from enum import Enum   # Not included with FL by default - you need to add enum.py and types.py to C:\Program Files\Image-Line\Shared\Python\Lib (or equivalent)

EventNameT = ['Note Off', 'Note On ', 'Key Aftertouch', 'Control Change','Program Change',  'Channel Aftertouch', 'Pitch Bend', 'System Message' ]

class Colors(Enum):
    Off        = 0x0C
    RedLow     = 0x0D 
    RedFull    = 0x0F
    AmberLow   = 0x1D
    AmberFull  = 0x3F
    YellowFull = 0x3E
    GreenLow   = 0x1C
    GreenFull  = 0x3C

class States(Enum):
    Never = 1
    On    = 2
    Off   = 3

AllStates = [States.Never] * 80

# Helper Functions =========================
   
def Reset():
    if device.isAssigned():
       device.midiOutMsg(0xB0)
       device.midiOutMsg(0x0300B0)  

def SetLaunchPixel(row, col, color):
    Key = (0x10 * row) + col 
    device.midiOutMsg(midi.MIDI_NOTEON + (Key << 8) + (color.value<<16));

def NextState(num):
    if AllStates[num] == States.Never:
        AllStates[num] = States.On
    elif AllStates[num] == States.On:
        AllStates[num] = States.Off
    elif AllStates[num] == States.Off:
        AllStates[num] = States.On
    else:
        AllStates[num] = States.Off

def ShowState(row, col, num):
    newstate = AllStates[num]
    
    if newstate == States.Never:
        SetLaunchPixel(row, col, Colors.Off)
    elif newstate == States.On:
        SetLaunchPixel(row, col, Colors.GreenFull)
    elif newstate == States.Off:
        SetLaunchPixel(row, col, Colors.RedLow)
    else:
        SetLaunchPixel(row, col, Colors.AmberLow)

# Events =========================

def OnInit():    
    Reset()
    print('Init complete')

def OnDeInit():
	print('Deinit complete')

# Incoming
def OnMidiMsg(event):
    event.handled = True
    # print ("MIDI IN :: {:X} {:X} {:2X} {}".format(event.status, event.data1, event.data2,  EventNameT[(event.status - 0x80) // 16] + ': '+  utils.GetNoteName(event.data1)))    
    
    if event.data2 == 0:  # Only work on button release
        row = (event.note & 0xF0) >> 4
        col = (event.note & 0x0F)
        num = (row*8)+col
        # print("vals=", event.note, row, col, num)
        NextState(num)    
        ShowState(row, col, num)        
        
        
# Outgoing - Ignore
def OnMidiOutMsg(event):
    event.handled = True    