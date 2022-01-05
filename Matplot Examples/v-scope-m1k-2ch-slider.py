# Simple example of anamated Matplot ploting channel A and B voltages
# uses Contin mode where sweep is not sybced to AWG waveform start
# AWG A configured as SVMI sine wave Channel B configured as Hi_Z input

from pysmu import *
#waveform plotting
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.widgets import Slider

#plot settings
fig = plt.figure()
ax = plt.axes(xlim=(0, 2), ylim=(0, 5))
ax.grid()
ax.set_xlabel("Time")
ax.set_ylabel("Voltage")
linea, = ax.plot([], [], lw=2)
lineb, = ax.plot([], [], lw=2)
periodvalue=200
x = np.linspace(0, 2, periodvalue)
ya = np.zeros(periodvalue)
yb = np.zeros(periodvalue)
v_pp_a = 0.0
v_pp_b = 0.0
# Function to initalize plot lines
def init():
	linea.set_data([], [])
	lineb.set_data([], [])
	return linea, lineb,

# Function to animate plot
def animate(i):
        global x,y, periodvalue, v_pp_a, v_pp_b

        ADsignal1 = devx.read(2000, -1, True) # Capture samples
        ya = [] # Clear data arrays
        yb = []
        for index in range(periodvalue): # Split channel samples into separate arrays
                ya.append(ADsignal1[index][0][0]) 
                yb.append(ADsignal1[index][1][0])
        ya = np.array(ya)
        yb = np.array(yb)
        v_pp_a = np.max(ya) - np.min(ya)
        v_pp_b = np.max(yb) - np.min(yb)
        linea.set_data(x, ya + offset_slider.val) # add slider offset
        lineb.set_data(x, yb + offset_slider.val)
        return linea, lineb,

# Setup ADAML1000
session = Session(ignore_dataflow=True, queue_size=10000)
#
if not session.devices:
        print( 'no device found')
        root.destroy()
        exit()
else:
    print("Successfully connected to ADALM1000.")
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
if not session.continuous: # start a continuous streaming session
	session.start(0)
CHA.mode = Mode.SVMI # Put CHA in SVMI mode
CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
#Available waveforms: sine, triangle, sawtooth, square, stairstep
CHA.sine( 0.5, 4.5, periodvalue, -(periodvalue/4) )
#
#start streaming samples

#plot waveform
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=100, interval=20, blit=True)
plt.title("Source A, Measure B")

# Adjust plot placement so we can place the slider
plt.subplots_adjust(left=0.2)

# Make a vertically oriented slider to control the offset
ax_offset = plt.axes([0.05, 0.2, 0.0225, 0.63], facecolor='lemonchiffon')
offset_slider = Slider(ax=ax_offset, label="V Offset", valmin=-2.5, valmax=2.5, valinit=0, orientation="vertical")

plt.show()

#stop streaming
devx.set_led(0b001) # LED.red

