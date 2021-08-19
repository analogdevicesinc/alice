#!/usr/bin/env python
# -*- charset utf8 -*-
from pysmu import *
import numpy
import math
import matplotlib.pyplot as plt
import matplotlib.animation

SampleRate = 100000
BUFFER = 4000 # 

# Add M1k session setup stuff here
# Setup ADAML1000
session = Session(ignore_dataflow=True, queue_size=10000)
# session.add_all()
if not session.devices:
        print( 'no device found')
        root.destroy()
        exit()
# session.configure()
devx = session.devices[0]
devx.set_led(0b010) # LED.green,
DevID = devx.serial
print( DevID)
print( devx.fwver)
print( devx.hwver)
print( devx.default_rate)
CHA = devx.channels['A']    # Open CHA
CHB = devx.channels['B']    # Open CHB
devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open

#output waveform
if not session.continuous:
	session.start(0)
CHA.mode = Mode.SVMI # Put CHA in Hi_Z mode
CHB.mode = Mode.SVMI # Put CHB in Hi_Z mode
#Available waveforms: sine, triangle, sawtooth, square, stairstep
#CHA.triangle( 0.5, 4.5, periodvalue, -(periodvalue/4) )
CHA.sine( 1.1, 3.9, 80, 0)
CHB.sine( 1.1, 3.9, 160, 0)
#
fig = plt.figure()
line1 = plt.plot([],[])[0]
line2 = plt.plot([],[])[0]

r = range(0,int(SampleRate/2+1),int(SampleRate/BUFFER))
l = len(r)

def init_line():
        global r, l
        
        line1.set_data(r, [-1000]*l)
        line2.set_data(r, [-1000]*l)
        return (line1,line2,)

def update_line(i):
        global BUFFER, r, l

        Adata = []
        Bdata = []
        # Read sample buffer from M1k here
        ADsignal1 = devx.read(BUFFER, -1, True)
        for index in range(BUFFER): #
                Adata.append((ADsignal1[index][0][0])-2.5) # CA voltage
                Bdata.append((ADsignal1[index][1][0])-2.5) # CB voltage
        #Adata = Adata * (numpy.kaiser(BUFFER, 14) * 3)
        #Bdata = Bdata * (numpy.kaiser(BUFFER, 14) * 3)
        Afdata = numpy.fft.rfft(Adata)
        Bfdata = numpy.fft.rfft(Bdata)
        Afdata = numpy.log10(numpy.sqrt(numpy.real(Afdata)**2+numpy.imag(Afdata)**2) / BUFFER) * 20
        Bfdata = numpy.log10(numpy.sqrt(numpy.real(Bfdata)**2+numpy.imag(Bfdata)**2) / BUFFER) * 20
        line1.set_data(r, Afdata)
        line2.set_data(r, Bfdata)
        return(line1,line2,)

plt.xscale('log')
plt.xlim(10, SampleRate/2+1)
plt.ylim(-120, 0)

plt.xlabel('Frequency')
plt.ylabel('dB')
plt.title('Spectrum')
plt.grid()

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, frames=100, interval=20, blit=True)

plt.show()
devx.set_led(0b001) # LED.Red,
