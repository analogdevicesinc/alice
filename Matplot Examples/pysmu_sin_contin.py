# Simple example of anamated Matplot ploting channel A and B voltages
# uses Contin mode where sweep is not sybced to AWG waveform start
# AWG A configured as SVMI sine wave Channel B configured as Hi_Z input

from pysmu import *
#waveform plotting
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

#plot settings
fig = plt.figure()
ax = plt.axes(xlim=(0, 2), ylim=(0, 5))
linea, = ax.plot([], [], lw=2)
lineb, = ax.plot([], [], lw=2)
periodvalue=200
x = np.linspace(0, 2, periodvalue)
ya = np.zeros(periodvalue)
yb = np.zeros(periodvalue)

def init():
	linea.set_data([], [])
	lineb.set_data([], [])
	return linea, lineb,

def animate(i):
        global x,y, periodvalue

        ADsignal1 = devx.read(2000, -1, True)
        ya = []
        yb = []
        for index in range(periodvalue): # calculate average
                ya.append(ADsignal1[index][0][0]) # Sum for average CA voltage 
                yb.append(ADsignal1[index][1][0])
        linea.set_data(x, np.array(ya))
        lineb.set_data(x, np.array(yb))
        return linea, lineb,

def updateawg():
        global periodvalue
        CHA.mode = Mode.SVMI # Put CHA in Hi Z mode
        CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
        CHA.sine( 0.5, 4.5, periodvalue, -(periodvalue/4) )
#
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
ADsignal1 = []              # Ain signal array channel

#output waveform
if not session.continuous:
	session.start(0)
CHA.mode = Mode.SVMI # Put CHA in Hi Z mode
CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
#Available waveforms: sine, triangle, sawtooth, square, stairstep
CHA.sine( 0.5, 4.5, periodvalue, -(periodvalue/4) )
# session.start(0)
#start streaming samples

#plot waveform
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=100, interval=20, blit=True)
plt.title("write A, read B")
plt.show()

#stop streaming
devx.set_led(0b001) # LED.red

