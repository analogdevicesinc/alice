# Simple example of anamated Matplot ploting channel A and B voltages
# AWG A configured as SVMI triangel wave Channel B configured as Hi_Z input

from pysmu import *
#waveform plotting
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import time

#plot settings
fig = plt.figure()
ax = plt.axes(xlim=(0, 4), ylim=(0, 5))
linea, = ax.plot([], [], lw=2)
lineb, = ax.plot([], [], lw=2)
# AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
periodvalue=100000/0.5 # 10Hz?
x = np.linspace(0, 4, 400)
ya = np.zeros(400)
yb = np.zeros(400)


def init():
	linea.set_data([], [])
	lineb.set_data([], [])
	return linea, lineb,

def animate(i):
        global x, ya, yb

        #
        # session.flush()
        ADsignal1 = devx.read(50, -1, True)
        ya = np.roll(ya,1)
        yb = np.roll(yb,1)
        DCA = 0.0
        DCB = 0.0
        try:
                for index in range(50): # 
                        DCA += ADsignal1[index][0][0] #  
                        DCB += ADsignal1[index][1][0]
                ya[0]=DCA/50.0 
                yb[0]=DCB/50.0
        except:
                donothing()
        # time.sleep(0.001)
        linea.set_data(x, np.array(ya))
        lineb.set_data(x, np.array(yb))
        return linea, lineb,
## Nop
def donothing():
    global RUNstatus
    
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
CHA.triangle( 0.5, 4.5, periodvalue, -(periodvalue/4) )
#start streaming samples

#plot waveform interval is number of mSec between updates
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=50, interval=10, blit=True)
plt.title("A Output, B Input")
plt.show()

#stop streaming
devx.set_led(0b001) # LED.red,
session.end()
