# import some libraries
from pysmu import *
import matplotlib.pyplot as plot
import numpy as np

def updateawg():
    global periodvalue
    CHA.mode = Mode.SVMI # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    # CHA.triangle( 0.5, 4.5, periodvalue, -(periodvalue/4) )
    CHA.sine( 0.5, 4.5, periodvalue, -(periodvalue/4) )
# Setup ADAML1000
periodvalue=200
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
#CHA.triangle( 0.5, 4.5, periodvalue, -(periodvalue/4) )
CHA.sine( 0.5, 4.5, periodvalue, -(periodvalue/4) )
#
frequencies = np.arange(1000,10200,200)
samplingFrequency = 100000
RecordLen = 10000
# Start Value of the sample
start = 1
# Stop Value of the sample
stop = RecordLen+1
#start streaming samples

s1 = np.empty([0]) # For samples
s2 = np.empty([0]) # For signal

for frequency in frequencies:
    periodvalue = int((1.0/frequency)*samplingFrequency)
    updateawg()
    sub1 = np.arange(start, stop, 1)
    sub2 = []
    ADsignal1 = devx.read(RecordLen, -1, True)
    for index in range(RecordLen): # calculate average
        sub2.append((ADsignal1[index][0][0])-2.5) # Sum for average CA voltage 
        # yb.append(ADsignal1[index][1][0])
    # Apply Window function numpy.kaiser(SMPfft, 14) * 3
    sub2 = sub2 * (np.kaiser(RecordLen, 14) * 3)
    s1 = np.append(s1, sub1)
    s2 = np.append(s2, sub2)
    start = stop+1
    stop = start+RecordLen

# Plot the time signal
plot.subplot(211)
plot.plot(s1,s2)
plot.xlabel('Sample')
plot.ylabel('Amplitude')

# Plot the spectrogram

plot.subplot(212)
powerSpectrum, freqenciesFound, time, imageAxis = plot.specgram(s2, Fs=samplingFrequency)
plot.xlabel('Time')
plot.ylabel('Frequency')
plot.show()
devx.set_led(0b001) # LED.red,
