#name=_Mega Performance Mode
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

EventNameT = ['Note Off', 'Note On ', 'Key Aftertouch', 'Control Change','Program Change',  'Channel Aftertouch', 'Pitch Bend', 'System Message' ]

States = [False] * 80

Off        = 0x0C
RedLow     = 0x0D 
RedFull    = 0x0F
AmberLow   = 0x1D
AmberFull  = 0x3F
YellowFull = 0x3E
GreenLow   = 0x1C
GreenFull  = 0x3C

# Helper Functions =========================
   
def Reset():
    if device.isAssigned():
       device.midiOutMsg(0xB0)
       device.midiOutMsg(0x0300B0)  

def SetLaunchPixel(row, col, color):
    Key = (0x10 * row) + col 
    device.midiOutMsg(midi.MIDI_NOTEON + (Key << 8) + (color<<16));

def MuteTrack(num, state):

    num = num + 1 # only needed for tracks

    playlist.muteTrack(num)
    
    if playlist.isTrackMuted(num):
        playlist.setTrackColor(num, 0xFF0000)
    else:
        playlist.setTrackColor(num, 0x00FF00)

def MuteChannel(num, state):
    channels.muteChannel(num )
    
    if channels.isChannelMuted(num):
        channels.setChannelColor(num, 0xFF0000)
    else:
        channels.setChannelColor(num, 0x00FF00)

# Events =========================

def OnInit():    
    Reset()
    print('Init complete')

def OnDeInit():
	print('Deinit complete')

def OnMidiMsg(event):
    event.handled = True
    # print ("MIDI IN :: {:X} {:X} {:2X} {}".format(event.status, event.data1, event.data2,  EventNameT[(event.status - 0x80) // 16] + ': '+  utils.GetNoteName(event.data1)))    
    
    if event.data2 == 0:  # Only work on button release
        row = (event.note & 0xF0) >> 4
        col = (event.note & 0x0F)
        num = (row*8)+col
        # print("vals=", event.note, row, col, num)
        newstate = ~States[num]
        States[num] = newstate;
        
        if newstate:
            SetLaunchPixel(row, col, RedFull)
        else:
            SetLaunchPixel(row, col, Off)       
        
        MuteChannel(num, newstate)
        
    
def OnMidiOutMsg(event):
    event.handled = True
    
    if event.midiId == midi.MIDI_NOTEON:
        color = colors.get(event.midiChan)
        print ("channel =", event.midiChan) 
        print("color=", color)
        # print ("MIDI OUT:: {:X} {:X} {:2X} {}".format(event.status, event.data1, event.data2,  EventNameT[(event.status - 0x80) // 16] + ': '+  utils.GetNoteName(event.data1)))        
        self.ShowCharacter(event.note, color);
        
    if event.midiId == midi.MIDI_NOTEOFF:
        self.Reset()