#name=_Launchpad Toggler
#url=www.jammingsignal.com

import device
import transport
import general
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
    Never = 0
    On    = 1
    Off   = 2

AllStates = [States.Never] * 80

Playing = False

# Helper Functions =========================
   
def Reset():
    if device.isAssigned():
       device.midiOutMsg(0xB0)
       device.midiOutMsg(0x0300B0)

def SendMIDI(command, channel, data1, data2):
     device.midiOutMsg((command | channel) + (data1 << 8) + (data2<<16));
     
def SetLaunchPixel(row, col, color):
    Key = (0x10 * row) + col 
    SendMIDI(midi.MIDI_NOTEON, 0, Key, color.value)

def NextState(num):
    if AllStates[num] == States.Never:
        AllStates[num] = States.On
    elif AllStates[num] == States.On:
        AllStates[num] = States.Off
    elif AllStates[num] == States.Off:
        AllStates[num] = States.On
    else:
        AllStates[num] = States.Off
        
    return AllStates[num]

def ShowState(row, col, state):    
    if state == States.Never:
        SetLaunchPixel(row, col, Colors.Off)
    elif state == States.On:
        SetLaunchPixel(row, col, Colors.GreenFull)
    elif state == States.Off:
        SetLaunchPixel(row, col, Colors.RedLow)
    else:
        SetLaunchPixel(row, col, Colors.AmberLow)  # Error

# Sends Mute *to* FL studio
def SendMute(num):
    #e = eventData() ????   Not sure how to do this.  TODO
    pass
     
def MuteRow(row):
    for col in range(8):
        num = (row*8)+col
        AllStates[num] = States.Never
        ShowState(row, col, States.Never)
        SendMute(num)

def MuteAll():
    for row in range(8):
        MuteRow(row)    

# Events =========================

def OnInit():    
    Reset()
    MuteAll()
    print('Init complete')

def OnDeInit():
    Reset()
    MuteAll()
    print('Deinit complete')
    
def OnIdle():
    global Playing

    playing_now = transport.isPlaying()
    
    if playing_now:
        if not Playing:
            print('Playback Started')
            Reset()
            MuteAll()            
    else:
        if Playing:    
            print('Playback Stopped')
            Reset()
            
    Playing = playing_now

# Incoming
def OnMidiMsg(event):    
    #print ("RAW MIDI IN :: {:X} {:d} {:2X} {}".format(event.status, event.data1, event.data2,  EventNameT[(event.status - 0x80) // 16] + ': '+  utils.GetNoteName(event.data1)))        
    
    channel = event.status & 0x0F
    command = event.status & 0xF0
    
    if event.data2 == 0:  # Only operate on button release
    
        # Top buttons get special handling in HandleCC() below
        if command == midi.MIDI_CONTROLCHANGE:
            HandleCC(event)
            return
    
        # Grid and side buttons
        else: # if command == midi.MIDI_NOTEON:
            row = (event.note & 0xF0) >> 4
            col = (event.note & 0x0F)
            num = (row*8)+col
            # print("vals=", event.note, row, col, num)
            
            # Side buttons have special meaning (mute all in row)
            if col == 8:
                MuteRow(row)
                event.handled = True
                return
            
            newstate = NextState(num)    
            ShowState(row, col, newstate)               
           
            event.status = midi.MIDI_CONTROLCHANGE | channel        
            event.data1 = num    # Remap to button number
            
            event.handled = False   # To allow passthru of modified event
            
            if newstate == States.On:
                event.data2 = 0x7F         # Maximum
            
            elif newstate == States.Off:
                event.data2 = 0x00         # Off
            
            else:  # Should not be possible, treat as error and ignore
                event.handled = True
        
        #print ("NEW MIDI IN :: {:X} {:X} {:2X} {} <<<<".format(event.status, event.data1, event.data2,  EventNameT[(event.status - 0x80) // 16] + ': '+  utils.GetNoteName(event.data1)))    
    else:
        event.handled = True  # Filter out button down
        
# Incoming CCs (Top Buttons)
def HandleCC(event):          
    event.handled = True
    button = event.note
    
    #if button == 0x68:  # up    
    #if button == 0x68:  # up   
    
    if button == 0x6C:  # Session
        pass
      
# Outgoing - Ignore
def OnMidiOutMsg(event):
    event.handled = True

beatdict = { 
    0: Colors.AmberLow,
    1: Colors.GreenFull,
    2: Colors.YellowFull
}
    
def OnUpdateBeatIndicator(value):
    SendMIDI(midi.MIDI_CONTROLCHANGE, 0, 0x6C, beatdict[value].value)
