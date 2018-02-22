#!/usr/bin/python
# ADALM2000 alice-desktop 2.0.py(w) (2-22-2018)
# For Python version > = 2.7.8
# With external module iio.py 
# 
# Created by D Mercer ()
#
import math
import time
try:
    import numpy
    numpy_found = True
except:
    numpy_found = False
import csv
import wave
import os
import urllib2
import struct
import subprocess
from time import gmtime, strftime
import tkFont
from Tkinter import *
from ttk import *
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from tkSimpleDialog import askstring
from tkMessageBox import *
import webbrowser
try:
    import iio
    libiio_found = True
except:
    libiio_found = False
from sys import argv
#
RevDate = "(22 Feb 2018)"
SwTitle = "ALICE DeskTop 2.0 "
Version_url = 'https://github.com/analogdevicesinc/alice/releases/download/2.0.0/alice-desktop-2.0-setup.exe'
# samll bit map of ADI logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root=Tk()
root.title( SwTitle + RevDate + ": ALM2000 Oscilloscope")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
global DevID, PlusUS, NegUS, FWRev, HWRev
# Window graph area Values that can be modified
GRW = 720               # Width of the time grid 720 default
GRH = 390               # Height of the time grid 390 default
X0L = 55                # Left top X value of time grid
Y0T = 25                # Left top Y value of time grid
#
GRWF = 720              # Width of the spectrum grid 720 default
GRHF = 390              # Height of the spectrum grid 390 default
X0LF = 37               # Left top X value of spectrum grid
Y0TF = 25               # Left top Y value of spectrum grid
#
GRWBP = 720             # Width of the Bode Plot grid 720 default
GRHBP = 390             # Height of the Bode Plot grid 390 default
X0LBP = 37              # Left top X value of Bode Plot grid
Y0TBP = 25              # Left top Y value of Bode Plot grid
#
GRWXY = 420             # Width of the XY grid 420 default
GRHXY = 390             # Height of the XY grid 390 default
X0LXY = 37              # Left top X value of XY grid
Y0TXY = 25              # Left top Y value of XY grid
#
GRWIA = 400             # Width of the grid 400 default
GRHIA = 400             # Height of the grid 400 default
X0LIA = 37              # Left top X value of grid
Y0TIA = 25              # Left top Y value of grid
#
MouseX = MouseY = -10
# Colors that can be modified
# Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORframes = "#000080"   # 50% blue
COLORcanvas = "#000000"   # 100% black
COLORgrid = "#808080"     # 50% Gray
COLORzeroline = "#0000ff" # 100% blue
COLORtrace1 = "#00ff00"   # 100% green
COLORtrace2 = "#ff8000"   # 100% orange
COLORtrace3 = "#00ffff"   # 100% cyan
COLORtrace4 = "#ffff00"   # 100% yellow
COLORtrace5 = "#ff00ff"   # 100% magenta
COLORtrace6 = "#C80000"   # 90% red
COLORtrace7 = "#8080ff"  # 100% purple
COLORtraceR1 = "#008000"   # 50% green
COLORtraceR2 = "#905000"   # 50% orange
COLORtraceR3 = "#008080"   # 50% cyan
COLORtraceR4 = "#808000"   # 50% yellow
COLORtraceR5 = "#850085"   # 50% magenta
COLORtraceR6 = "#800000"   # 80% red
COLORtraceR7 = "#4040a0"  # 80% purple
COLORtext = "#ffffff"     # 100% white
COLORtrigger = "#ff0000"  # 100% red
COLORsignalband = "#ff0000" # 100% red
# Set up variable for width of grid lines in pixels
FWRev = 0.14
HWRev = 0.2
# Set sample buffer size
HoldOff = 0.0
AWGASampleRate = 750000         # Sample rate of the AWG A channel
AWGBSampleRate = 750000         # Sample rate of the AWG B channel
SAMPLErate = 100000 # Scope sample rate
DigPatSampleRate = 100000000 # digital pattern sample rate
HalfSAMPLErate = SAMPLErate/2.0
OverSampleRate = 1 # Scope sample rate multiplier ( OSR )
MinSamples = 1000
MaxSamples = 16384 # Maximum time buffer 8192
# set initial trigger conditions
TRIGGERlevel = 0.0          # Triggerlevel in volts
# default math equations
MathString = "VBuffA[t] + VBuffB[t]"
MathUnits = " V"
MathXString = "VBuffA[t]"
MathXUnits = " V"
MathYString = "VBuffB[t]"
MathYUnits = " V"
UserAString = "MaxV1-VATop"
UserALabel = "OverShoot"
UserBString = "MinV2-VBBase"
UserBLabel = "UnderShoot"
AWGAMathString = "(VBuffA + VBuffB)/2"
AWGBMathString = "(VBuffA + VBuffB)/2"
FFTUserWindowString = "numpy.kaiser(SMPfft, 14) * 3"
DigFilterAString = "numpy.sinc(numpy.linspace(-1, 1, 91))"
DigFilterBString = "numpy.sinc(numpy.linspace(-1, 1, 91))"
ChaMeasString1 = "DCV1"
ChaMeasString2 = "MaxV1"
ChaMeasString3 = "MinV1"
ChaMeasString4 = "SV1"
ChaMeasString5 = "MaxV1-MinV1"
ChaMeasString6 = "math.sqrt(SV1**2 - DCV1**2)"
ChbMeasString1 = "DCV2"
ChbMeasString2 = "MaxV2"
ChbMeasString3 = "MinV2"
ChbMeasString4 = "SV2"
ChbMeasString5 = "MaxV2-MinV2"
ChbMeasString6 = "math.sqrt(SV2**2 - DCV2**2)"
ChaLableSrring1 = "CH1-DCV "
ChaLableSrring2 = "Max V1 "
ChaLableSrring3 = "Min V1 "
ChaLableSrring4 = "CH1-TRMS "
ChaLableSrring5 = "CH1-VP-P "
ChaLableSrring6 = "CH1-ACRMS "
ChbLableSrring1 = "CH2-DCV "
ChbLableSrring2 = "Max V2 "
ChbLableSrring3 = "Min V2 "
ChbLableSrring4 = "CH2-TRMS "
ChbLableSrring5 = "CH2-VP-P "
ChbLableSrring6 = "CH2-ACRMS "
# defaukt trace width in pixels / number of averages
GridWidth = IntVar(0)
GridWidth.set(1)
TRACEwidth = IntVar(0)
TRACEwidth.set(1)
TRACEaverage = IntVar(0) # Number of average sweeps for average mode
TRACEaverage.set(8)
Vdiv = IntVar(0)
Vdiv.set(10)            # Number of vertical divisions for spectrum / Bode
HarmonicMarkers = IntVar(0)
HarmonicMarkers.set(3)
ZEROstuffing = IntVar(0) # The zero stuffing value is 2 ** ZERO stuffing, calculated on initialize
ZEROstuffing.set(1)
FFTwindow = IntVar(0)   # FFT window function variable
FFTwindow.set(5)        # FFTwindow 0=None (rectangular B=1), 1=Cosine (B=1.24), 2=Triangular non-zero endpoints (B=1.33),
                        # 3=Hann (B=1.5), 4=Blackman (B=1.73), 5=Nuttall (B=2.02), 6=Flat top (B=3.77)
Vdiv = IntVar(0)
Vdiv.set(10)            # Number of vertical divisions for spectrum / Bode
RelPhaseCorrection = 15
EnableCommandInterface = 1
EnableMuxMode = 1
EnableMinigenMode = 0
EnablePmodDA1Mode = 0
EnableDigPotMode = 0
EnableGenericSerialMode = 0
EnableDigitalFilter = 0
EnableMeasureScreen = 1
MouseFocus = 1
HistAsPercent = 0
ShowBallonHelp = 0
# hard coded rough calibration numbers
AWGAgain = 4600 # 6100
AWGAoffset = 2000
AWGBgain = 4600 # 6100
AWGBoffset = 2000
CH1hwOffset = 2009
CH2hwOffset = 2009
CH1_H_Gain = 3.488
CH1_L_Gain = 36.42
CH2_H_Gain = 3.49
CH2_L_Gain = 36.44
ch1_multiplier = CH1_L_Gain
ch2_multiplier = CH2_L_Gain
CH1GainSA = IntVar(0)
CH2GainSA = IntVar(0)
CH1GainSA.set(0)
CH2GainSA.set(0)
OldCH1Gain = CH1GainSA.get()
OldCH2Gain = CH2GainSA.get()
OldCH1pdvRange = CH1pdvRange = 1.0
OldCH2pdvRange = CH2pdvRange = 1.0
AwgLayout = "Horz"
Style_String = 'alt'
MarkerLoc = 'UL' # can be UL, UR, LL, LR
LoopBackGain = 2.305 # 8.12
TriggerMethod = "HW" # use SW or sw for software trigger use HW or hw for hardware trigger
# Check if there is an alice_init.ini file to read in
try:
    InitFile = open("alice_init.ini")
    for line in InitFile:
        try:
            exec( line.rstrip() )
        except:
            print "Skiping " + line.rstrip()
    InitFile.close()
except:
    print "No Init File Read"
#
root.style = Style()
#('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
if MouseFocus == 1:
    root.tk_focusFollowsMouse()
DevID = "m2k"
# Vertical Sensitivity list in v/div
CHvpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0)
CH1pdvRange = 1.0
CH2pdvRange = 1.0
# Time list in ms/div
TMpdiv = (0.00005, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)
ResScalediv = (10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000)
# AWG variables
AWGAAmplvalue = 0.0
AWGAOffsetvalue = 0.0
AWGAFreqvalue = 0.0
AWGAPhasevalue = 0
AWGAdelayvalue = 0
AWGADutyCyclevalue = 50
AWGAWave = 'dc'
AWGBAmplvalue = 0.0
AWGBOffsetvalue = 0.0
AWGBFreqvalue = 0.0
AWGBPhasevalue = 0
AWGBdelayvalue = 0
AWGBDutyCyclevalue = 50
AWGBWave = 'dc'
#
DCV1 = DCV2 = MinV1 = MaxV1 = MinV2 = MaxV2 = MidV1 = PPV1 = MidV2 = PPV2 = SV1 = SVA_B = 0
CHAperiod = CHAfreq = CHBperiod = CHBfreq = 0
# Calibration coefficients
CHAVGain = CHBVGain = 1.0
CHAVOffset = CHBVOffset = 0.0
# Initialisation of general variables
CHAOffset = CHBOffset = CHBAOffset = CHBBOffset = CHBCOffset = CHBDOffset = 0.0
# Other global variables required in various routines
CANVASwidth = GRW + 2 * X0L # The canvas width
CANVASheight = GRH + 80     # The canvas height

Ymin = Y0T                  # Minimum position of time grid (top)
Ymax = Y0T + GRH            # Maximum position of time grid (bottom)
Xmin = X0L                  # Minimum position of time grid (left)
Xmax = X0L + GRW            # Maximum position of time grid (right)

ADsignal1 = []              # Ain signal array channel A and B
VBuffA = []
VBuffB = []
VBuffMA = []
VBuffMB = []
VBuffMC = []
VBuffMD = []
#
VAets = []
VBets = []
#
DFiltACoef = [1]
DFiltBCoef = [1]
DigFiltA = IntVar(0)
DigFiltA.set(0)
DigFiltB = IntVar(0)
DigFiltB.set(0)
DigBuffA = IntVar(0)
DigBuffB = IntVar(0)
DigBuffA.set(0)
DigBuffB.set(0)
VFilterA = {}
VFilterB = {}
#
AWGAwaveform = [1]
AWGBwaveform = [1]
AWGAbinform = [1]
AWGBbinform = [1]
VmemoryA = numpy.ones(1)    # The memory for averaging
VmemoryB = numpy.ones(1)
TRACEresetTime = True       # True for first new trace, false for averageing
TRACEresetFreq = True       # True for first new trace, false for averageing
AWGScreenStatus = IntVar(0)

T1Vline = []                # Voltage Trace line channel 1
T2Vline = []                # Voltage Trace line channel 2
TMAVline = []               # Voltage Trace line MUX channel A
TMBVline = []               # Voltage Trace line MUX channel B
TMCVline = []               # Voltage Trace line MUX channel C
TMDVline = []               # Voltage Trace line MUX channel D
TMBRline = []               # V reference Trace line MUX channel B
TMCRline = []               # V reference line MUX channel C
TXYline = []                # XY Trace line
TXYRline = []               # XY reference trace line
Tmathline = []              # Math trace line
TMXline = []                # X math Trace line
TMYline = []                # Y math Trace line
T1VRline = []               # V reference Trace line channel 1
T2VRline = []               # V reference Trace line channel 2
TMRline = []                # Math reference Trace line
Triggerline = []            # Triggerline
Triggersymbol = []          # Trigger symbol
SHOWsamples = 2000          # Number of samples on the screen   
SCstart = 0                 # Start sample of the trace
HozPoss = 0.0
#
TRACES = 1                  # Number of traces 1 or 2
TRACESread = 0              # Number of traces that have been read from ALM
ScreenTrefresh = IntVar(0)
ScreenXYrefresh = IntVar(0)
#
NSteps = IntVar(0)  # number of frequency sweep steps
NSteps.set(128)
LoopNum = IntVar(0)
LoopNum.set(1)
LastWindow = -1
LastSMPfft = 0
FBins = numpy.linspace(0, HalfSAMPLErate, num=16384)
FStep = numpy.linspace(0, 16383, num=NSteps.get())
FSweepMode = IntVar(0)
FSweepCont = IntVar(0)
FStepSync = IntVar(0)
FSweepSync = IntVar(0)
ShowCA_VdB = IntVar(0)   # curves to display variables
ShowCA_P = IntVar(0)
ShowCB_VdB = IntVar(0)
ShowCB_P = IntVar(0)
ShowMarkerBP = IntVar(0)
ShowCA_RdB = IntVar(0)
ShowCA_RP = IntVar(0)
ShowCB_RdB = IntVar(0)
ShowCB_RP = IntVar(0)
ShowMathBP = IntVar(0)
ShowRMathBP = IntVar(0)
FSweepAdB = []
FSweepBdB = []
FSweepAPh = []
FSweepBPh = []
BDSweepFile = IntVar(0)
FileSweepFreq = []
FileSweepAmpl = []
#
MarkerNum = MarkerFreqNum = 0
ShowTCur = IntVar(0)
ShowVCur = IntVar(0)
TCursor = VCursor = 0
ShowXCur = IntVar(0)
ShowYCur = IntVar(0)
XCursor = YCursor = 0
ShowFCur = IntVar(0)
ShowdBCur = IntVar(0)
FCursor = dBCursor = 0
ShowBPCur = IntVar(0)
ShowBdBCur = IntVar(0)
RUNstatus = IntVar(0)       # 0 stopped, 1 start, 2 running, 3 stop and restart, 4 stop
PowerStatus = 1
TRIGGERsample = 0           # AD sample trigger point
DX = 0                      # interpolated trigger point
# Spectrum Values that can be modified
DBdivlist = [1, 2, 3, 5, 10, 15, 20]    # dB per division
DBdivindex = IntVar(0)      # 10 dB/div as initial value
DBdivindex.set(4)
DBlevel = IntVar(0)     # Reference level
DBlevel.set(0)
DBdivindexBP = IntVar(0)      # 10 dB/div as initial value
DBdivindexBP.set(4)
DBlevelBP = IntVar(0)     # Reference level
DBlevelBP.set(0)
hldn = 0
SpectrumScreenStatus = IntVar(0)
SmoothCurvesSA = IntVar(0)
SmoothCurvesBP = IntVar(0)
CutDC = IntVar(0)
IAScreenStatus = IntVar(0)
ImpedanceMagnitude  = 0.0 # in ohms 
ImpedanceAngle = 12.0 # in degrees 
ImpedanceRseries = 0.0 # in ohms 
ImpedanceXseries = 0.0 # in ohms
OverRangeFlagA = 0
OverRangeFlagB = 0
PeakdbA = 10
PeakdbB = 10
PeakRelPhase = 0.0
PeakfreqA = 100
PeakfreqB = 1000
OhmStatus = IntVar(0)
OhmRunStatus = IntVar(0)
FFTbandwidth = 0                # The FFT bandwidth
FFTBuffA = [] # Clear the FFTBuff array for trace A
FFTBuffB = [] # Clear the FFTBuff array for trace B
FFTresultA = []                 # FFT result CHA
PhaseA = []
FFTresultB = []                 # FFT result CHB
PhaseB = []
FFTwindowname = "--"            # The FFT window name
FFTmemoryA = numpy.ones(1)       # The memory for averaging
PhaseMemoryA = numpy.ones(1)
FFTmemoryB = numpy.ones(1)       # The memory for averaging
PhaseMemoryB = numpy.ones(1)
SMPfftpwrTwo = IntVar(0)        # The power of two of SMPfft
SMPfftpwrTwo.set(11)
SMPfft = 2 ** SMPfftpwrTwo.get()    # Initialize
Two28 = 268435456
FFTwindowshape = numpy.ones(SMPfft) # The FFT window curve
T1Fline = []                # Frequency Trace line channel A
T2Fline = []                # Frequency Trace line channel B
T1Pline = []                # Phase angle Trace line channel A - B
T2Pline = []                # Phase angle Trace line channel B - A
T1FRline = []               # F reference Trace line channel A
T2FRline = []               # F reference Trace line channel B
T1PRline = []               # Phase reference Trace line channel A - B
T2PRline = []               # Phase reference Trace line channel B - A
TFMline = []                # Frequency Math Trace
TFRMline = []               # Frequency reference Math Trace
FreqTraceMode = IntVar(0)   # 1 normal mode, 2 max hold mode, 3 average mode
FreqTraceMode.set(1)
#
TAFline = []                # Bode Freq Trace line channel A
TBFline = []                # Bode Freq Trace line channel B
TAPline = []                # Bode Phase angle Trace line channel A - B
TBPline = []                # Bode Phase angle Trace line channel B - A
TAFRline = []               # Bode F reference Trace line channel A
TBFRline = []               # Bode F reference Trace line channel B
TAPRline = []               # Bode Phase reference Trace line channel A - B
TBPRline = []               # Bode Phase reference Trace line channel B - A
TBPMline = []               # Bode Frequency Math Trace
TBPRMline = []              # Bode Frequency reference Math Trace
#
MinSamplesSA = 64
MaxSamplesSA = 65536
#
XYScreenStatus = IntVar(0)
Xsignal = IntVar(0)   # Signal for X axis variable
Xsignal.set(1)
Ysignal = IntVar(0)   # Signal for X axis variable
Ysignal.set(3)
ShowRXY = IntVar(0)   # show reference XY trace
# show Analog Input Mux Variables
Show_CBA = IntVar(0)
Show_CBB = IntVar(0)
Show_CBC = IntVar(0)
Show_CBD = IntVar(0)
D0 = IntVar(0)
D1 = IntVar(0)
D2 = IntVar(0)
D3 = IntVar(0)
D4 = IntVar(0)
D5 = IntVar(0)
D6 = IntVar(0)
D7 = IntVar(0)
DEnab0 = IntVar(0)
DEnab1 = IntVar(0)
DEnab2 = IntVar(0)
DEnab3 = IntVar(0)
DEnab4 = IntVar(0)
DEnab5 = IntVar(0)
DEnab6 = IntVar(0)
DEnab7 = IntVar(0)
DEnab10 = IntVar(0)
DEnab11 = IntVar(0)
DEnab12 = IntVar(0)
DEnab13 = IntVar(0)
DEnab14 = IntVar(0)
DEnab15 = IntVar(0)
DEnab8 = IntVar(0)
DEnab9 = IntVar(0)
# 25x25 bit map of high going pulse in .gif
hipulse = """
R0lGODlhGQAYAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/
/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm
AABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/
MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm
ZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/
mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm
zGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/
/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ
AJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA
M8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ
ZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A
mf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z
zP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///ywAAAAAGQAYAAAIZwAfCBxI
sKDBgw8AKFzIsKFChA4jMoQoUSJFAAgHLryYUeDGgx8zhiw4EuRDkxg7ltR4UmRLki9RclQZk2VK
lzdh5pTJE+dMnz1/6uyYsKZHowRXHt1pcGREohUbQo2qNKlDolgFBgQAOw==
"""
hipulseimg = PhotoImage(data=hipulse)
# 25x25 bit map of low going pulse in .gif
lowpulse = """
R0lGODlhGQAYAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/
/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm
AABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/
MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm
ZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/
mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm
zGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/
/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ
AJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA
M8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ
ZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A
mf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z
zP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///ywAAAAAGQAYAAAIZwAfCBxI
sKBBggASKgRwEOHChwsbDoRIkaHEBxQdWpSosGHHix8NhvSYkORGkyhBljw4kuVKkS9TwjzpkubE
mDVl6tR4ESPOmzYLtgTac6hAozxzqgzqkynRmhUhmoz6cCpVpD0vBgQAOw==
"""
lowpulseimg = PhotoImage(data=lowpulse)
# Tool Tip Ballon help stuff
class CreateToolTip(object):
    # create a tooltip for a given widget
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 100   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
#
# =========== Start widgets routines =============================
def BSaveConfig(filename):
    global TgInput, TgEdge, SingleShot, AutoLevel, HozPossentry
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, Ysignal, AutoCenterA, AutoCenterB
    global CHAsb, CHBsb, HScale, FreqTraceMode, MC1sb, MC2sb
    global CHAsbxy, CHBsbxy, HoldOffentry, MC1sbxy, MC2sbxy, MC1VPosEntryxy, MC2VPosEntryxy
    global CHAVPosEntryxy, CHBVPosEntryxy
    global ShowC1_V, ShowC2_V, MathTrace, MathUnits, MathXUnits, MathYUnits
    global CHAVPosEntry, CHBVPosEntry, MC1VPosEntry, MC2VPosEntry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGATerm, AWGAMode, AWGARepeatFlag, AWGBRepeatFlag
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBPhaseEntry, AWGBShape, AWGBMode
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2
    global MeasPPV2, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasPhase, MeasRMSVA_B
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC, PatGenScreenStatus, DigScreenStatus
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global SMPfftpwrTwo, SMPfft, StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, XYScreenStatus, IAScreenStatus, SpectrumScreenStatus
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry, AWGAPhaseDelay, AWGBPhaseDelay
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasDelay
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxScreenStatus
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry, muxwindow
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global SmoothCurvesBP, SingleShotBP, bodewindow
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMarkerBP, BodeDisp
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP, ShowMathBP, ShowRMathBP
    global BPSweepMode, BPSweepCont, BodeScreenStatus, RevDate, SweepStepBodeEntry
    global HScaleBP, StopBodeEntry, StartBodeEntry, ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global Show_MathX, Show_MathY
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global minigenwindow, MinigenMode, MinigenScreenStatus, MinigenFclk, MinigenFout
    global PatGenScreenStatus, DEnab0, DEnab1, DEnab2, DEnab3, DEnab4, DEnab5, DEnab6, DEnab7
    global DEnab10, DEnab11, DEnab12, DEnab13, DEnab14, DEnab15, DEnab8, DEnab9
    global Dpg0FreqEntry, Dpg1FreqEntry, Dpg2FreqEntry, Dpg3FreqEntry, Dpg4FreqEntry, Dpg5FreqEntry
    global Dpg6FreqEntry, Dpg7FreqEntry, Dpg8FreqEntry, Dpg9FreqEntry, DpgWidthEntry
    global Dpg10FreqEntry, Dpg11FreqEntry, Dpg12FreqEntry, Dpg13FreqEntry, Dpg14FreqEntry, Dpg15FreqEntry
    global Dpg0DutyEntry, Dpg1DutyEntry, Dpg2DutyEntry, Dpg3DutyEntry, Dpg4DutyEntry, Dpg5DutyEntry
    global Dpg6DutyEntry, Dpg7DutyEntry, Dpg8DutyEntry, Dpg9DutyEntry, pgwin
    global Dpg10DutyEntry, Dpg11DutyEntry, Dpg12DutyEntry, Dpg13DutyEntry, Dpg14DutyEntry, Dpg15DutyEntry
    global Dpg0DelayEntry, Dpg1DelayEntry, Dpg2DelayEntry, Dpg3DelayEntry, Dpg4DelayEntry, Dpg5DelayEntry
    global Dpg6DelayEntry, Dpg7DelayEntry, Dpg8DelayEntry, Dpg9DelayEntry
    global Dpg10DelayEntry, Dpg11DelayEntry, Dpg12DelayEntry, Dpg13DelayEntry, Dpg14DelayEntry, Dpg15DelayEntry
    
    # open Config file for Write
    ConfgFile = open(filename, "w")
    # Save Window placements
    ConfgFile.write("root.geometry('+" + str(root.winfo_x()) + '+' + str(root.winfo_y()) + "')\n")
    ConfgFile.write("awgwindow.geometry('+" + str(awgwindow.winfo_x()) + '+' + str(awgwindow.winfo_y()) + "')\n")
    ConfgFile.write('global GRW; GRW = ' + str(GRW) + '\n')
    ConfgFile.write('global GRH; GRH = ' + str(GRH) + '\n')
    # Windows configuration
    if XYScreenStatus.get() > 0:
        ConfgFile.write('global GRWXY; GRWXY = ' + str(GRWXY) + '\n')
        ConfgFile.write('global GRHXY; GRHXY = ' + str(GRHXY) + '\n')
        ConfgFile.write('MakeXYWindow()\n')
        ConfgFile.write("xywindow.geometry('+" + str(xywindow.winfo_x()) + '+' + str(xywindow.winfo_y()) + "')\n")
        ConfgFile.write('CHAsbxy.delete(0,END)\n')
        ConfgFile.write('CHAsbxy.insert(0, ' + CHAsbxy.get() + ')\n')
        ConfgFile.write('CHAVPosEntryxy.delete(0,END)\n')
        ConfgFile.write('CHAVPosEntryxy.insert(4, ' + CHAVPosEntryxy.get() + ')\n')
        ConfgFile.write('CHBsbxy.delete(0,END)\n')
        ConfgFile.write('CHBsbxy.insert(0, ' + CHBsbxy.get() + ')\n')
        ConfgFile.write('CHBVPosEntryxy.delete(0,END)\n')
        ConfgFile.write('CHBVPosEntryxy.insert(4, ' + CHBVPosEntryxy.get() + ')\n')
        ConfgFile.write('MC1sbxy.delete(0,END)\n')
        ConfgFile.write('MC1sbxy.insert(0, ' + MC1sbxy.get() + ')\n')
        ConfgFile.write('MC1VPosEntryxy.delete(0,END)\n')
        ConfgFile.write('MC1VPosEntryxy.insert(4, ' + MC1VPosEntryxy.get() + ')\n')
        ConfgFile.write('MC2sbxy.delete(0,END)\n')
        ConfgFile.write('MC2sbxy.insert(0, ' + MC2sbxy.get() + ')\n')
        ConfgFile.write('MC2VPosEntryxy.delete(0,END)\n')
        ConfgFile.write('MC2VPosEntryxy.insert(4, ' + MC2VPosEntryxy.get() + ')\n')
    else:
        ConfgFile.write('DestroyXYScreen()\n')
    if IAScreenStatus.get() > 0:
        ConfgFile.write('global GRWIA; GRWIA = ' + str(GRWIA) + '\n')
        ConfgFile.write('global GRHIA; GRHIA = ' + str(GRHIA) + '\n')
        ConfgFile.write('MakeIAWindow()\n')
        ConfgFile.write("iawindow.geometry('+" + str(iawindow.winfo_x()) + '+' + str(iawindow.winfo_y()) + "')\n")
        ConfgFile.write('RsystemEntry.delete(0,END)\n')
        ConfgFile.write('RsystemEntry.insert(5, ' + RsystemEntry.get() + ')\n')
        ConfgFile.write('ResScale.delete(0,END)\n')
        ConfgFile.write('ResScale.insert(5, ' + ResScale.get() + ')\n')
        ConfgFile.write('GainCorEntry.delete(0,END)\n')
        ConfgFile.write('GainCorEntry.insert(5, ' + GainCorEntry.get() + ')\n')
        ConfgFile.write('PhaseCorEntry.delete(0,END)\n')
        ConfgFile.write('PhaseCorEntry.insert(5, ' + PhaseCorEntry.get() + ')\n')
    else:
        ConfgFile.write('DestroyIAScreen()\n')
    if SpectrumScreenStatus.get() > 0:
        ConfgFile.write('global GRWF; GRWF = ' + str(GRWF) + '\n')
        ConfgFile.write('global GRHF; GRHF = ' + str(GRHF) + '\n')
        ConfgFile.write('MakeSpectrumWindow()\n')
        ConfgFile.write("freqwindow.geometry('+" + str(freqwindow.winfo_x()) + '+' + str(freqwindow.winfo_y()) + "')\n")
        ConfgFile.write('ShowC1_VdB.set(' + str(ShowC1_VdB.get()) + ')\n')
        ConfgFile.write('ShowC1_P.set(' + str(ShowC1_P.get()) + ')\n')
        ConfgFile.write('ShowC2_VdB.set(' + str(ShowC2_VdB.get()) + ')\n')
        ConfgFile.write('ShowC2_P.set(' + str(ShowC2_P.get()) + ')\n')
        ConfgFile.write('StartFreqEntry.delete(0,END)\n')
        ConfgFile.write('StartFreqEntry.insert(5, ' + StartFreqEntry.get() + ')\n')
        ConfgFile.write('StopFreqEntry.delete(0,END)\n')
        ConfgFile.write('StopFreqEntry.insert(5, ' + StopFreqEntry.get() + ')\n')
        ConfgFile.write('HScale.set(' + str(HScale.get()) + ')\n')
        ConfgFile.write('FreqTraceMode.set(' + str(FreqTraceMode.get()) + ')\n')
    else:
        ConfgFile.write('DestroySpectrumScreen()\n')
    if DigScreenStatus.get() > 0:
        ConfgFile.write('MakeDigScreen()\n')
        ConfgFile.write("win2.geometry('+" + str(win2.winfo_x()) + '+' + str(win2.winfo_y()) + "')\n")
    else:
        ConfgFile.write('DestroyDigScreen()\n')
    if MuxScreenStatus.get() == 1:
        ConfgFile.write('MakeMuxModeWindow()\n')
        ConfgFile.write("muxwindow.geometry('+" + str(muxwindow.winfo_x()) + '+' + str(muxwindow.winfo_y()) + "')\n")
        ConfgFile.write('Show_CBA.set(' + str(Show_CBA.get()) + ')\n')
        ConfgFile.write('Show_CBB.set(' + str(Show_CBB.get()) + ')\n')
        ConfgFile.write('Show_CBC.set(' + str(Show_CBC.get()) + ')\n')
        ConfgFile.write('Show_CBD.set(' + str(Show_CBD.get()) + ')\n')
        ConfgFile.write('CHB_Asb.delete(0,END)\n')
        ConfgFile.write('CHB_Asb.insert(0, ' + CHB_Asb.get() + ')\n')
        ConfgFile.write('CHB_Bsb.delete(0,END)\n')
        ConfgFile.write('CHB_Bsb.insert(0, ' + CHB_Bsb.get() + ')\n')
        ConfgFile.write('CHB_Csb.delete(0,END)\n')
        ConfgFile.write('CHB_Csb.insert(0, ' + CHB_Csb.get() + ')\n')
        ConfgFile.write('CHB_Dsb.delete(0,END)\n')
        ConfgFile.write('CHB_Dsb.insert(0, ' + CHB_Dsb.get() + ')\n')
        ConfgFile.write('CHB_APosEntry.delete(0,END)\n')
        ConfgFile.write('CHB_APosEntry.insert(4, ' + CHB_APosEntry.get() + ')\n')
        ConfgFile.write('CHB_BPosEntry.delete(0,END)\n')
        ConfgFile.write('CHB_BPosEntry.insert(4, ' + CHB_BPosEntry.get() + ')\n')
        ConfgFile.write('CHB_CPosEntry.delete(0,END)\n')
        ConfgFile.write('CHB_CPosEntry.insert(4, ' + CHB_CPosEntry.get() + ')\n')
        ConfgFile.write('CHB_DPosEntry.delete(0,END)\n')
        ConfgFile.write('CHB_DPosEntry.insert(4, ' + CHB_DPosEntry.get() + ')\n')
    else:
        ConfgFile.write('DestroyMuxScreen()\n')
    if BodeScreenStatus.get() == 1:
        ConfgFile.write('global GRWBP; GRWBP = ' + str(GRWBP) + '\n')
        ConfgFile.write('global GRHBP; GRHBP = ' + str(GRHBP) + '\n')
        ConfgFile.write('MakeBodeWindow()\n')
        ConfgFile.write("bodewindow.geometry('+" + str(bodewindow.winfo_x()) + '+' + str(bodewindow.winfo_y()) + "')\n")
        ConfgFile.write('ShowCA_VdB.set(' + str(ShowCA_VdB.get()) + ')\n')
        ConfgFile.write('ShowCB_VdB.set(' + str(ShowCB_VdB.get()) + ')\n')
        ConfgFile.write('ShowCA_P.set(' + str(ShowCA_P.get()) + ')\n')
        ConfgFile.write('ShowCB_P.set(' + str(ShowCB_P.get()) + ')\n')
        ConfgFile.write('ShowCA_RdB.set(' + str(ShowCA_RdB.get()) + ')\n')
        ConfgFile.write('ShowCA_RP.set(' + str(ShowCA_RP.get()) + ')\n')
        ConfgFile.write('ShowCB_RdB.set(' + str(ShowCB_RdB.get()) + ')\n')
        ConfgFile.write('ShowCB_RP.set(' + str(ShowCB_RP.get()) + ')\n')
        ConfgFile.write('BodeDisp.set(' + str(BodeDisp.get()) + ')\n')
        ConfgFile.write('ShowMarkerBP.set(' + str(ShowMarkerBP.get()) + ')\n')
        ConfgFile.write('ShowMathBP.set(' + str(ShowMathBP.get()) + ')\n')
        ConfgFile.write('ShowRMathBP.set(' + str(ShowRMathBP.get()) + ')\n')
        ConfgFile.write('HScaleBP.set(' + str(HScaleBP.get()) + ')\n')
        ConfgFile.write('NSteps.set(' + str(NSteps.get()) + ')\n')
        ConfgFile.write('DBdivindexBP.set(' + str(DBdivindexBP.get()) + ')\n')
        ConfgFile.write('DBlevelBP.set(' + str(DBlevelBP.get()) + ')\n')
        ConfgFile.write('FSweepMode.set(' + str(FSweepMode.get()) + ')\n')
        ConfgFile.write('SweepStepBodeEntry.delete(0,END)\n')
        ConfgFile.write('SweepStepBodeEntry.insert(4, ' + SweepStepBodeEntry.get() + ')\n')
        ConfgFile.write('StopBodeEntry.delete(0,END)\n')
        ConfgFile.write('StopBodeEntry.insert(4, ' + StopBodeEntry.get() + ')\n')
        ConfgFile.write('StartBodeEntry.delete(0,END)\n')
        ConfgFile.write('StartBodeEntry.insert(4, ' + StartBodeEntry.get() + ')\n')
    else:
        ConfgFile.write('DestroyBodeScreen()\n')
    if MeasureStatus.get() == 1:
        # Save strings
        ConfgFile.write('global ChaLableSrring1; ChaLableSrring1 = "' + ChaLableSrring1 + '"\n')
        ConfgFile.write('global ChaLableSrring2; ChaLableSrring2 = "' + ChaLableSrring2 + '"\n')
        ConfgFile.write('global ChaLableSrring3; ChaLableSrring3 = "' + ChaLableSrring3 + '"\n')
        ConfgFile.write('global ChaLableSrring4; ChaLableSrring4 = "' + ChaLableSrring4 + '"\n')
        ConfgFile.write('global ChaLableSrring5; ChaLableSrring5 = "' + ChaLableSrring5 + '"\n')
        ConfgFile.write('global ChaLableSrring6; ChaLableSrring6 = "' + ChaLableSrring6 + '"\n')
        ConfgFile.write('global ChbLableSrring1; ChbLableSrring1 = "' + ChbLableSrring1 + '"\n')
        ConfgFile.write('global ChbLableSrring2; ChbLableSrring2 = "' + ChbLableSrring2 + '"\n')
        ConfgFile.write('global ChbLableSrring3; ChbLableSrring3 = "' + ChbLableSrring3 + '"\n')
        ConfgFile.write('global ChbLableSrring4; ChbLableSrring4 = "' + ChbLableSrring4 + '"\n')
        ConfgFile.write('global ChbLableSrring5; ChbLableSrring5 = "' + ChbLableSrring5 + '"\n')
        ConfgFile.write('global ChbLableSrring6; ChbLableSrring6 = "' + ChbLableSrring6 + '"\n')
        ConfgFile.write('global ChaMeasString1; ChaMeasString1 = "' + ChaMeasString1 + '"\n')
        ConfgFile.write('global ChaMeasString2; ChaMeasString2 = "' + ChaMeasString2 + '"\n')
        ConfgFile.write('global ChaMeasString3; ChaMeasString3 = "' + ChaMeasString3 + '"\n')
        ConfgFile.write('global ChaMeasString4; ChaMeasString4 = "' + ChaMeasString4 + '"\n')
        ConfgFile.write('global ChaMeasString5; ChaMeasString5 = "' + ChaMeasString5 + '"\n')
        ConfgFile.write('global ChaMeasString6; ChaMeasString6 = "' + ChaMeasString6 + '"\n')
        ConfgFile.write('global ChbMeasString1; ChbMeasString1 = "' + ChbMeasString1 + '"\n')
        ConfgFile.write('global ChbMeasString2; ChbMeasString2 = "' + ChbMeasString2 + '"\n')
        ConfgFile.write('global ChbMeasString3; ChbMeasString3 = "' + ChbMeasString3 + '"\n')
        ConfgFile.write('global ChbMeasString4; ChbMeasString4 = "' + ChbMeasString4 + '"\n')
        ConfgFile.write('global ChbMeasString5; ChbMeasString5 = "' + ChbMeasString5 + '"\n')
        ConfgFile.write('global ChbMeasString6; ChbMeasString6 = "' + ChbMeasString6 + '"\n')
        ConfgFile.write('MakeMeasureScreen()\n')
        ConfgFile.write("measurewindow.geometry('+" + str(measurewindow.winfo_x()) + '+' + str(measurewindow.winfo_y()) + "')\n")
    else:
        ConfgFile.write('DestroyMeasureScreen()\n')
    if MinigenScreenStatus.get() == 1:
        ConfgFile.write('MakeMinigenWindow()\n')
        ConfgFile.write("minigenwindow.geometry('+" + str(minigenwindow.winfo_x()) + '+' + str(minigenwindow.winfo_y()) + "')\n")
        ConfgFile.write('MinigenMode.set(' + str(MinigenMode.get()) + ')\n')
        ConfgFile.write('MinigenFout.delete(0,END)\n')
        ConfgFile.write('MinigenFout.insert(4, ' + MinigenFout.get() + ')\n')
        ConfgFile.write('MinigenFclk.delete(0,END)\n')
        ConfgFile.write('MinigenFclk.insert(4, ' + MinigenFclk.get() + ')\n')
    else:
        ConfgFile.write('DestroyMinigenScreen()\n')
    if PatGenScreenStatus.get() == 1:
        ConfgFile.write('MakePatGenScreen()\n')
        ConfgFile.write("pgwin.geometry('+" + str(pgwin.winfo_x()) + '+' + str(pgwin.winfo_y()) + "')\n")
        ConfgFile.write('DEnab0.set(' + str(DEnab0.get()) + ')\n')
        ConfgFile.write('DEnab1.set(' + str(DEnab1.get()) + ')\n')
        ConfgFile.write('DEnab2.set(' + str(DEnab2.get()) + ')\n')
        ConfgFile.write('DEnab3.set(' + str(DEnab3.get()) + ')\n')
        ConfgFile.write('DEnab4.set(' + str(DEnab4.get()) + ')\n')
        ConfgFile.write('DEnab5.set(' + str(DEnab5.get()) + ')\n')
        ConfgFile.write('DEnab6.set(' + str(DEnab6.get()) + ')\n')
        ConfgFile.write('DEnab7.set(' + str(DEnab7.get()) + ')\n')
        ConfgFile.write('DEnab10.set(' + str(DEnab10.get()) + ')\n')
        ConfgFile.write('DEnab11.set(' + str(DEnab11.get()) + ')\n')
        ConfgFile.write('DEnab12.set(' + str(DEnab12.get()) + ')\n')
        ConfgFile.write('DEnab13.set(' + str(DEnab13.get()) + ')\n')
        ConfgFile.write('DEnab14.set(' + str(DEnab14.get()) + ')\n')
        ConfgFile.write('DEnab15.set(' + str(DEnab15.get()) + ')\n')
        ConfgFile.write('DEnab8.set(' + str(DEnab8.get()) + ')\n')
        ConfgFile.write('DEnab9.set(' + str(DEnab9.get()) + ')\n')
        ConfgFile.write('Dpg0FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg1FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg2FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg3FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg4FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg5FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg6FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg7FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg8FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg9FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg10FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg11FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg12FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg13FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg14FreqEntry.delete(0,END)\n')
        ConfgFile.write('Dpg15FreqEntry.delete(0,END)\n')
        ConfgFile.write('DpgWidthEntry.delete(0,END)\n')
        #
        ConfgFile.write('Dpg0FreqEntry.insert(4, ' + Dpg0FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg1FreqEntry.insert(4, ' + Dpg1FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg2FreqEntry.insert(4, ' + Dpg2FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg3FreqEntry.insert(4, ' + Dpg3FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg4FreqEntry.insert(4, ' + Dpg4FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg5FreqEntry.insert(4, ' + Dpg5FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg6FreqEntry.insert(4, ' + Dpg6FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg7FreqEntry.insert(4, ' + Dpg7FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg8FreqEntry.insert(4, ' + Dpg8FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg9FreqEntry.insert(4, ' + Dpg9FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg10FreqEntry.insert(4, ' + Dpg10FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg11FreqEntry.insert(4, ' + Dpg11FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg12FreqEntry.insert(4, ' + Dpg12FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg13FreqEntry.insert(4, ' + Dpg13FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg14FreqEntry.insert(4, ' + Dpg14FreqEntry.get() + ')\n')
        ConfgFile.write('Dpg15FreqEntry.insert(4, ' + Dpg15FreqEntry.get() + ')\n')
        ConfgFile.write('DpgWidthEntry.insert(4, ' + DpgWidthEntry.get() + ')\n')
        #
        ConfgFile.write('Dpg0DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg1DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg2DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg3DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg4DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg5DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg6DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg7DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg8DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg9DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg10DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg11DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg12DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg13DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg14DutyEntry.delete(0,END)\n')
        ConfgFile.write('Dpg15DutyEntry.delete(0,END)\n')
        #
        ConfgFile.write('Dpg0DutyEntry.insert(4, ' + Dpg0DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg1DutyEntry.insert(4, ' + Dpg1DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg2DutyEntry.insert(4, ' + Dpg2DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg3DutyEntry.insert(4, ' + Dpg3DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg4DutyEntry.insert(4, ' + Dpg4DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg5DutyEntry.insert(4, ' + Dpg5DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg6DutyEntry.insert(4, ' + Dpg6DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg7DutyEntry.insert(4, ' + Dpg7DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg8DutyEntry.insert(4, ' + Dpg8DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg9DutyEntry.insert(4, ' + Dpg9DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg10DutyEntry.insert(4, ' + Dpg10DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg11DutyEntry.insert(4, ' + Dpg11DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg12DutyEntry.insert(4, ' + Dpg12DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg13DutyEntry.insert(4, ' + Dpg13DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg14DutyEntry.insert(4, ' + Dpg14DutyEntry.get() + ')\n')
        ConfgFile.write('Dpg15DutyEntry.insert(4, ' + Dpg15DutyEntry.get() + ')\n')
        #
        ConfgFile.write('Dpg0DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg1DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg2DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg3DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg4DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg5DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg6DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg7DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg8DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg9DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg10DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg11DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg12DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg13DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg14DelayEntry.delete(0,END)\n')
        ConfgFile.write('Dpg15DelayEntry.delete(0,END)\n')
        #
        ConfgFile.write('Dpg0DelayEntry.insert(4, ' + Dpg0DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg1DelayEntry.insert(4, ' + Dpg1DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg2DelayEntry.insert(4, ' + Dpg2DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg3DelayEntry.insert(4, ' + Dpg3DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg4DelayEntry.insert(4, ' + Dpg4DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg5DelayEntry.insert(4, ' + Dpg5DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg6DelayEntry.insert(4, ' + Dpg6DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg7DelayEntry.insert(4, ' + Dpg7DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg8DelayEntry.insert(4, ' + Dpg8DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg9DelayEntry.insert(4, ' + Dpg9DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg10DelayEntry.insert(4, ' + Dpg10DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg11DelayEntry.insert(4, ' + Dpg11DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg12DelayEntry.insert(4, ' + Dpg12DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg13DelayEntry.insert(4, ' + Dpg13DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg14DelayEntry.insert(4, ' + Dpg14DelayEntry.get() + ')\n')
        ConfgFile.write('Dpg15DelayEntry.insert(4, ' + Dpg15DelayEntry.get() + ')\n')
    else:
        ConfgFile.write('DestroyPatGenScreen()\n')
    #
    ConfgFile.write('TRIGGERentry.delete(0,END)\n')
    ConfgFile.write('TRIGGERentry.insert(4, ' + TRIGGERentry.get() + ')\n')
    ConfgFile.write('HoldOffentry.delete(0,"end")\n')
    ConfgFile.write('HoldOffentry.insert(0, ' + HoldOffentry.get() + ')\n')
    ConfgFile.write('HozPossentry.delete(0,"end")\n')
    ConfgFile.write('HozPossentry.insert(0, ' + HozPossentry.get() + ')\n')
    ConfgFile.write('TMsb.delete(0,END)\n')
    ConfgFile.write('TMsb.insert(0, ' + TMsb.get() + ')\n')
    ConfgFile.write('TgInput.set(' + str(TgInput.get()) + ')\n')
    ConfgFile.write('AutoLevel.set(' + str(AutoLevel.get()) + ')\n')
    ConfgFile.write('SingleShot.set(' + str(SingleShot.get()) + ')\n')
    ConfgFile.write('TgEdge.set(' + str(TgEdge.get()) + ')\n')
    ConfgFile.write('Xsignal.set(' + str(Xsignal.get()) + ')\n')
    ConfgFile.write('Ysignal.set(' + str(Ysignal.get()) + ')\n')
    #
    ConfgFile.write('TimeDisp.set(' + str(TimeDisp.get()) + ')\n')
    ConfgFile.write('XYDisp.set(' + str(XYDisp.get()) + ')\n')
    ConfgFile.write('FreqDisp.set(' + str(FreqDisp.get()) + ')\n')
    ConfgFile.write('IADisp.set(' + str(IADisp.get()) + ')\n')
    ConfgFile.write('ShowC1_V.set(' + str(ShowC1_V.get()) + ')\n')
    ConfgFile.write('ShowC2_V.set(' + str(ShowC2_V.get()) + ')\n')
    ConfgFile.write('Show_MathX.set(' + str(Show_MathX.get()) + ')\n')
    ConfgFile.write('Show_MathY.set(' + str(Show_MathY.get()) + ')\n')
    ConfgFile.write('AutoCenterA.set(' + str(AutoCenterA.get()) + ')\n')
    ConfgFile.write('AutoCenterB.set(' + str(AutoCenterB.get()) + ')\n')
    ConfgFile.write('TRACEmodeTime.set(' + str(TRACEmodeTime.get()) + ')\n')
    #
    ConfgFile.write('CHAVPosEntry.delete(0,END)\n')
    ConfgFile.write('CHAVPosEntry.insert(4, ' + CHAVPosEntry.get() + ')\n')
    ConfgFile.write('CHAsb.delete(0,END)\n')
    ConfgFile.write('CHAsb.insert(0, ' + CHAsb.get() + ')\n')
    #
    ConfgFile.write('CHBVPosEntry.delete(0,END)\n')
    ConfgFile.write('CHBVPosEntry.insert(4, ' + CHBVPosEntry.get() + ')\n')
    ConfgFile.write('CHBsb.delete(0,END)\n')
    ConfgFile.write('CHBsb.insert(0, ' + CHBsb.get() + ')\n')
    #
    ConfgFile.write('MC1VPosEntry.delete(0,END)\n')
    ConfgFile.write('MC1VPosEntry.insert(4, ' + MC1VPosEntry.get() + ')\n')
    ConfgFile.write('MC1sb.delete(0,END)\n')
    ConfgFile.write('MC1sb.insert(0, ' + MC1sb.get() + ')\n')
    #
    ConfgFile.write('MC2VPosEntry.delete(0,END)\n')
    ConfgFile.write('MC2VPosEntry.insert(4, ' + MC2VPosEntry.get() + ')\n')
    ConfgFile.write('MC2sb.delete(0,END)\n')
    ConfgFile.write('MC2sb.insert(0, ' + MC2sb.get() + ')\n')
    # AWG stuff
    ConfgFile.write('AWGAMode.set('+ str(AWGAMode.get()) + ')\n')
    ConfgFile.write('AWGAPhaseDelay.set('+ str(AWGAPhaseDelay.get()) + ')\n')
    ConfgFile.write('AWGAAmplEntry.delete(0,END)\n')
    ConfgFile.write('AWGAAmplEntry.insert(4, ' + AWGAAmplEntry.get() + ')\n')
    ConfgFile.write('AWGAOffsetEntry.delete(0,END)\n')
    ConfgFile.write('AWGAOffsetEntry.insert(4, ' + AWGAOffsetEntry.get() + ')\n')
    ConfgFile.write('AWGAFreqEntry.delete(0,END)\n')
    ConfgFile.write('AWGAFreqEntry.insert(4, ' + AWGAFreqEntry.get() + ')\n')
    ConfgFile.write('AWGAPhaseEntry.delete(0,END)\n')
    ConfgFile.write('AWGAPhaseEntry.insert(4, ' + AWGAPhaseEntry.get() + ')\n')
    ConfgFile.write('AWGADutyCycleEntry.delete(0,END)\n')
    ConfgFile.write('AWGADutyCycleEntry.insert(4, ' + AWGADutyCycleEntry.get() + ')\n')
    ConfgFile.write('AWGAShape.set(' + str(AWGAShape.get()) + ')\n')
    #
    ConfgFile.write('AWGBMode.set('+ str(AWGBMode.get()) + ')\n')
    ConfgFile.write('AWGBPhaseDelay.set('+ str(AWGBPhaseDelay.get()) + ')\n')
    ConfgFile.write('AWGBAmplEntry.delete(0,END)\n')
    ConfgFile.write('AWGBAmplEntry.insert(4, ' + AWGBAmplEntry.get() + ')\n')
    ConfgFile.write('AWGBOffsetEntry.delete(0,END)\n')
    ConfgFile.write('AWGBOffsetEntry.insert(4, ' + AWGBOffsetEntry.get() + ')\n')
    ConfgFile.write('AWGBFreqEntry.delete(0,END)\n')
    ConfgFile.write('AWGBFreqEntry.insert(4, ' + AWGBFreqEntry.get() + ')\n')
    ConfgFile.write('AWGBPhaseEntry.delete(0,END)\n')
    ConfgFile.write('AWGBPhaseEntry.insert(4, ' + AWGBPhaseEntry.get() + ')\n')
    ConfgFile.write('AWGBDutyCycleEntry.delete(0,END)\n')
    ConfgFile.write('AWGBDutyCycleEntry.insert(4, ' + AWGBDutyCycleEntry.get() + ')\n')
    ConfgFile.write('AWGBShape.set(' + str(AWGBShape.get()) + ')\n')
    #
    ConfgFile.write('CHAVGainEntry.delete(0,END)\n')
    ConfgFile.write('CHAVGainEntry.insert(4, ' + CHAVGainEntry.get() + ')\n')
    ConfgFile.write('CHBVGainEntry.delete(0,END)\n')
    ConfgFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
    ConfgFile.write('CHAVOffsetEntry.delete(0,END)\n')
    ConfgFile.write('CHAVOffsetEntry.insert(4, ' + CHAVOffsetEntry.get() + ')\n')
    ConfgFile.write('CHBVOffsetEntry.delete(0,END)\n')
    ConfgFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')
    #
    ConfgFile.write('MeasDCV1.set(' + str(MeasDCV1.get()) + ')\n')
    ConfgFile.write('MeasMinV1.set(' + str(MeasMinV1.get()) + ')\n')
    ConfgFile.write('MeasMaxV1.set(' + str(MeasMaxV1.get()) + ')\n')
    ConfgFile.write('MeasBaseV1.set(' + str(MeasBaseV1.get()) + ')\n')
    ConfgFile.write('MeasTopV1.set(' + str(MeasTopV1.get()) + ')\n')
    ConfgFile.write('MeasMidV1.set(' + str(MeasMidV1.get()) + ')\n')
    ConfgFile.write('MeasPPV1.set(' + str(MeasPPV1.get()) + ')\n')
    ConfgFile.write('MeasRMSV1.set(' + str(MeasRMSV1.get()) + ')\n')
    ConfgFile.write('MeasDiffAB.set(' + str(MeasDiffAB.get()) + ')\n')
    ConfgFile.write('MeasRMSVA_B.set(' + str(MeasRMSVA_B.get()) + ')\n')
    ConfgFile.write('MeasDCV2.set(' + str(MeasDCV2.get()) + ')\n')
    ConfgFile.write('MeasMinV2.set(' + str(MeasMinV2.get()) + ')\n')
    ConfgFile.write('MeasMaxV2.set(' + str(MeasMaxV2.get()) + ')\n')
    ConfgFile.write('MeasBaseV2.set(' + str(MeasBaseV2.get()) + ')\n')
    ConfgFile.write('MeasTopV2.set(' + str(MeasTopV2.get()) + ')\n')
    ConfgFile.write('MeasMidV2.set(' + str(MeasMidV2.get()) + ')\n')
    ConfgFile.write('MeasPPV2.set(' + str(MeasPPV2.get()) + ')\n')
    ConfgFile.write('MeasRMSV2.set(' + str(MeasRMSV2.get()) + ')\n')
    ConfgFile.write('MeasDiffBA.set(' + str(MeasDiffBA.get()) + ')\n')
    #
    ConfgFile.write('MeasAHW.set(' + str(MeasAHW.get()) + ')\n')
    ConfgFile.write('MeasALW.set(' + str(MeasALW.get()) + ')\n')
    ConfgFile.write('MeasADCy.set(' + str(MeasADCy.get()) + ')\n')
    ConfgFile.write('MeasAPER.set(' + str(MeasAPER.get()) + ')\n')
    ConfgFile.write('MeasAFREQ.set(' + str(MeasAFREQ.get()) + ')\n')
    ConfgFile.write('MeasBHW.set(' + str(MeasBHW.get()) + ')\n')
    ConfgFile.write('MeasBLW.set(' + str(MeasBLW.get()) + ')\n')
    ConfgFile.write('MeasBDCy.set(' + str(MeasBDCy.get()) + ')\n')
    ConfgFile.write('MeasBPER.set(' + str(MeasBPER.get()) + ')\n')
    ConfgFile.write('MeasBFREQ.set(' + str(MeasBFREQ.get()) + ')\n')
    ConfgFile.write('MeasPhase.set(' + str(MeasPhase.get()) + ')\n')
    ConfgFile.write('MeasDelay.set(' + str(MeasDelay.get()) + ')\n')
    #
    ConfgFile.write('MathTrace.set(' + str(MathTrace.get()) + ')\n')
    # Save strings
    ConfgFile.write('global MathString; MathString = "' + MathString + '"\n')
    ConfgFile.write('global MathXString; MathXString = "' + MathXString + '"\n')
    ConfgFile.write('global MathYString; MathYString = "' + MathYString + '"\n')
    ConfgFile.write('global MathUnits; MathUnits = "' + MathUnits + '"\n')
    ConfgFile.write('global MathXUnits; MathXUnits = "' + MathXUnits + '"\n')
    ConfgFile.write('global MathYUnits; MathYUnits = "' + MathYUnits + '"\n')
    ConfgFile.write('global UserAString; UserAString = "' + UserAString + '"\n')
    ConfgFile.write('global UserALabel; UserALabel = "' + UserALabel + '"\n')
    ConfgFile.write('global UserBString; UserBString = "' + UserBString + '"\n')
    ConfgFile.write('global UserBLabel; UserBLabel = "' + UserBLabel + '"\n')
    ConfgFile.write('global AWGAMathString; AWGAMathString = "' + AWGAMathString + '"\n')
    ConfgFile.write('global AWGBMathString; AWGBMathString = "' + AWGBMathString + '"\n')
    ConfgFile.write('global FFTUserWindowString; FFTUserWindowString= "' +  FFTUserWindowString + '"\n')
    ConfgFile.write('global DigFilterAString; DigFilterAString = "' + DigFilterAString + '"\n')
    ConfgFile.write('global DigFilterBString; DigFilterBString = "' + DigFilterBString + '"\n')
    # extra Spectrum stuff
    if SpectrumScreenStatus.get() > 0 or IAScreenStatus.get() > 0 or BodeScreenStatus.get() > 0:
        ConfgFile.write('SMPfftpwrTwo.set(' + str(SMPfftpwrTwo.get()) + ')\n')
        ConfgFile.write('FFTwindow.set(' + str(FFTwindow.get()) + ')\n')
        ConfgFile.write('ZEROstuffing.set(' + str(ZEROstuffing.get()) + ')\n')
        ConfgFile.write('Vdiv.set(' + str(Vdiv.get()) + ')\n')
        #
        ConfgFile.write('DBdivindex.set(' + str(DBdivindex.get()) + ')\n')
        ConfgFile.write('DBlevel.set(' + str(DBlevel.get()) + ')\n')
        ConfgFile.write('TRACEaverage.set(' + str(TRACEaverage.get()) + ')\n')
        ConfgFile.write('CutDC.set(' + str(CutDC.get()) + ')\n')
    #
    ConfgFile.close()

def BSaveConfigIA():
    global iawindow

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=iawindow)
    BSaveConfig(filename)

def BSaveConfigSA():
    global freqwindow

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=freqwindow)
    BSaveConfig(filename)
#
def BSaveConfigBP():
    global bodewindow

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=bodewindow)
    BSaveConfig(filename)
#
def BSaveConfigTime():
    global root
    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=root)
    BSaveConfig(filename)
#    
def BLoadConfig(filename):
    global TgInput, TgEdge, SingleShot, AutoLevel, DevID
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, Ysignal, AutoCenterA, AutoCenterB
    global CHAsb, CHAIsb, CHBsb, CHBIsb, HScale, FreqTraceMode
    global CHAsbxy, CHBsbxy, HoldOffentry, MC1sb, MC2sb
    global CHAVPosEntryxy, CHBVPosEntryxy, MC1sbxy, MC2sbxy, MC1VPosEntryxy, MC2VPosEntryxy
    global ShowC1_V, ShowC2_V, MathTrace, HozPossentry
    global CHAVPosEntry, CHBVPosEntry, MC1VPosEntry, MC2VPosEntry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGAMode, AWGARepeatFlag, AWGBRepeatFlag
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBPhaseEntry, AWGBShape, AWGBMode
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasPhase, MeasDelay
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ, MeasRMSVA_B
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global SMPfftpwrTwo, SMPfft, StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, AWGAPhaseDelay, AWGBPhaseDelay
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxScreenStatus
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry, muxwindow
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry, Show_MathX, Show_MathY
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global PatGenScreenStatus, DEnab0, DEnab1, DEnab2, DEnab3, DEnab4, DEnab5, DEnab6, DEnab7
    global DEnab10, DEnab11, DEnab12, DEnab13, DEnab14, DEnab15, DEnab8, DEnab9
    global Dpg0FreqEntry, Dpg1FreqEntry, Dpg2FreqEntry, Dpg3FreqEntry, Dpg4FreqEntry, Dpg5FreqEntry
    global Dpg6FreqEntry, Dpg7FreqEntry, Dpg8FreqEntry, Dpg9FreqEntry, DpgWidthEntry
    global Dpg10FreqEntry, Dpg11FreqEntry, Dpg12FreqEntry, Dpg13FreqEntry, Dpg14FreqEntry, Dpg15FreqEntry
    global Dpg0DutyEntry, Dpg1DutyEntry, Dpg2DutyEntry, Dpg3DutyEntry, Dpg4DutyEntry, Dpg5DutyEntry
    global Dpg6DutyEntry, Dpg7DutyEntry, Dpg8DutyEntry, Dpg9DutyEntry, pgwin
    global Dpg10DutyEntry, Dpg11DutyEntry, Dpg12DutyEntry, Dpg13DutyEntry, Dpg14DutyEntry, Dpg15DutyEntry
    global Dpg0DelayEntry, Dpg1DelayEntry, Dpg2DelayEntry, Dpg3DelayEntry, Dpg4DelayEntry, Dpg5DelayEntry
    global Dpg6DelayEntry, Dpg7DelayEntry, Dpg8DelayEntry, Dpg9DelayEntry
    global Dpg10DelayEntry, Dpg11DelayEntry, Dpg12DelayEntry, Dpg13DelayEntry, Dpg14DelayEntry, Dpg15DelayEntry
    
    # Read configuration values from file
    try:
        ConfgFile = open(filename)
        for line in ConfgFile:
            try:
                exec( line.rstrip() )
            except:
                print "Skipping " + line.rstrip()
        ConfgFile.close()
        if DevID != "No Device":
            BAWGAPhaseDelay()
            BAWGBPhaseDelay()
            UpdateAWGA()
            UpdateAWGB()
            if PatGenScreenStatus.get() == 1:
                UpdatePatGen()
        TimeCheckBox()
        XYCheckBox()
        FreqCheckBox()
        BodeCheckBox()
        IACheckBox()
        OhmCheckBox()
    except:
        print "Config File Not Found."

def BLoadConfigIA():
    global iawindow

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=iawindow)
    BLoadConfig(filename)
#
def BLoadConfigSA():
    global freqwindow

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=freqwindow)
    BLoadConfig(filename)
#
def BLoadConfigBP():
    global bodewindow

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=bodewindow)
    BLoadConfig(filename)
#
def BLoadConfigTime():
    global root

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")], parent=root)
    BLoadConfig(filename)
    UpdateTimeTrace()

def BgColor():
    global COLORtext, COLORcanvas, ColorMode, Bodeca, BodeScreenStatus
    global ca, Freqca, SpectrumScreenStatus, XYca, XYScreenStatus, IAca, IAScreenStatus

    if ColorMode.get() > 0:
        COLORtext = "#000000"   # 100% black
        COLORtrace4 = "#a0a000" # 50% yellow
        COLORtraceR4 = "#606000"   # 25% yellow
        COLORcanvas = "#ffffff"     # 100% white
    else:
        COLORcanvas = "#000000"   # 100% black
        COLORtrace4 = "#ffff00" # 100% yellow
        COLORtraceR4 = "#808000"   # 50% yellow
        COLORtext = "#ffffff"     # 100% white
    ca.config(background=COLORcanvas)
    UpdateTimeScreen()
    if SpectrumScreenStatus.get() > 0:
        Freqca.config(background=COLORcanvas)
        UpdateFreqScreen()
    if XYScreenStatus.get() > 0:
        XYca.config(background=COLORcanvas)
        UpdateXYScreen()
    if IAScreenStatus.get() > 0:
        IAca.config(background=COLORcanvas)
        UpdateIAScreen()
    if BodeScreenStatus.get() > 0:
        Bodeca.config(background=COLORcanvas)
        UpdateBodeScreen()
#    
def BSaveScreen():
    global CANVASwidth, CANVASheight
    global COLORtext, MarkerNum, ColorMode
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")])
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n")
    if MarkerNum > 0 or ColorMode.get() > 0:
        ca.postscript(file=filename, height=CANVASheight, width=CANVASwidth, colormode='color', rotate=Orient)
    else:    # temp change text color to black
        COLORtext = "#000000"
        UpdateTimeScreen()
        # first save postscript file
        ca.postscript(file=filename, height=CANVASheight, width=CANVASwidth, colormode='color', rotate=Orient)
        # now convert to bit map
        # img = Image.open("screen_shot.eps")
        # img.save("screen_shot.gif", "gif")
        COLORtext = "#ffffff"
        UpdateTimeScreen()
#
def BSaveScreenXY():
    global CANVASwidthXY, CANVASheightXY, xywindow
    global COLORtext, MarkerNum, ColorMode, XYca
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent=xywindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=xywindow)
    if MarkerNum > 0 or ColorMode.get() > 0:
        XYca.postscript(file=filename, height=CANVASheightXY, width=CANVASwidthXY, colormode='color', rotate=Orient)
    else:    # temp chnage text corlor to black
        COLORtext = "#000000"
        UpdateXYScreen()
        # first save postscript file
        XYca.postscript(file=filename, height=CANVASheightXY, width=CANVASwidthXY, colormode='color', rotate=Orient)
        # now convert to bit map
        # img = Image.open("screen_shot.eps")
        # img.save("screen_shot.gif", "gif")
        COLORtext = "#ffffff"
        UpdateXYScreen()
#
def BSaveScreenIA():
    global CANVASwidthIA, CANVASheightIA
    global COLORtext, IAca, ColorMode, iawindow
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent=iawindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=iawindow)
    if ColorMode.get() > 0:
        IAca.postscript(file=filename, height=CANVASheightIA, width=CANVASwidthIA, colormode='color', rotate=Orient)
    else: # temp change text color to black for Black BG
        COLORtext = "#000000"
        UpdateIAScreen()
        # save postscript file
        IAca.postscript(file=filename, height=CANVASheightIA, width=CANVASwidthIA, colormode='color', rotate=Orient)
        # 
        COLORtext = "#ffffff"
        UpdateIAScreen()
#
def BSaveScreenBP():
    global CANVASwidthBP, CANVASheightBP
    global COLORtext, Bodeca, bodewindow
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent = bodewindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=bodewindow)
    if MarkerNum > 0 or ColorMode.get() > 0:
        Bodeca.postscript(file=filename, height=CANVASheightBP, width=CANVASwidthBP, colormode='color', rotate=Orient)
    else: # temp change text color to black
        COLORtext = "#000000"
        UpdateBodeScreen()
        # save postscript file
        Bodeca.postscript(file=filename, height=CANVASheightBP, width=CANVASwidthBP, colormode='color', rotate=Orient)
        # 
        COLORtext = "#ffffff"
        UpdateBodeScreen()
#
def BSaveData():
    global VBuffA, VBuffB, VFilterA, VFilterB, SAMPLErate

    # open file to save data
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(filename, 'a')
    DataFile.write( 'Sample-#, C1-V, C1-V, Sample Rate = ' + str(SAMPLErate) + '\n' )
    for index in range(len(VBuffA)):
        DataFile.write( str(index) + ', ' + str(VBuffA[index]) + ', ' + str(VBuffB[index]) + '\n')
    DataFile.close()
#
def BReadData():
    global VBuffA, VBuffB, SHOWsamples, VFilterA, VFilterB

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")])
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
        VBuffA = []
        VBuffB = []
        SHOWsamples = 0
        for row in csv_f:
            try:
                VBuffA.append(float(row[1]))
                VBuffB.append(float(row[3]))
                SHOWsamples = SHOWsamples + 1
            except:
                print 'skipping non-numeric row'
        VBuffA = numpy.array(VBuffA)
        VBuffB = numpy.array(VBuffB)
        CSVFile.close()
        UpdateTimeTrace()
    except:
        showwarning("WARNING","No such file found or wrong format!")
#
def BHelp():
    # open a URL, in this case, the ALICE desk-top-users-guide
    url = "https://wiki.analog.com/university/tools/m2k/alice/users-guide-m2k"
    webbrowser.open(url,new=2)

def BAbout():
    global RevDate, FWRev, HWRev, DevID, Version_url
    # show info on software / firmware / hardware
    try:
        u = urllib2.urlopen(Version_url)
        meta = u.info()
        time_string = str(meta.getheaders("Last-Modified"))
    except:
        time_string = "       Unavailable"
    libstring = ' Library version: %u.%u (git tag: %s)' % iio.version
    showinfo("About ALICE", SwTitle + RevDate + "\n" + libstring + "\n"
             "Latest Version: " + time_string[7:18] + "\n" +
             "ADALM2000 Hardware Rev " + HWRev + "\n" +
             "Firmware Rev " + FWRev + "\n" +
             "Board Serial Number " + DevID + "\n" +
             "Software is provided as is without any Warranty")
    
def BSnapShot():
    global T1Vline, T2Vline
    global TXYline, Tmathline, TMRline, TXYRline
    global T1VRline, T2VRline, TMCVline, TMDVline
    global ShowC1_V, ShowC2_V, ShowMath, MathTrace
    global MuxScreenStatus, TMCRline, TMBRline, TMAVline, TMBVline, TMCVline, TMDVline
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxEnb

    if ShowC1_V.get() == 1:
        T1VRline = T1Vline               # V reference Trace line channel 1
    if ShowC2_V.get() == 1:
        T2VRline = T2Vline               # V reference Trace line channel 2
    if MathTrace.get() > 0:
        TMRline = Tmathline              # Math reference Trace line
    if MuxScreenStatus.get() > 0:
        if Show_CBA.get() > 0:
            T2VRline = TMAVline # V reference Trace line Mux channel A
        if Show_CBB.get() > 0:
            TMBRline = TMBVline # V reference Trace line Mux channel B
        if Show_CBC.get() > 0:
            TMCRline = TMCVline # V reference Trace line Mux channel C
        if Show_CBD.get() > 0:
            T2IRline = TMDVline # V reference Trace line Mux channel D
    if len(TXYline) > 4:
        TXYRline = TXYline               # XY reference trace line    
#
def BSaveCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DevID

    devidstr = DevID[17:31]
    filename = devidstr + "_O.cal"
    CalFile = open(filename, "w")
    #
    CalFile.write('CHAVGainEntry.delete(0,END)\n')
    CalFile.write('CHAVGainEntry.insert(4, ' + CHAVGainEntry.get() + ')\n')
    CalFile.write('CHBVGainEntry.delete(0,END)\n')
    CalFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
    CalFile.write('CHAVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAVOffsetEntry.insert(4, ' + CHAVOffsetEntry.get() + ')\n')
    CalFile.write('CHBVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')
    #
    CalFile.close()

def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DevID

    devidstr = DevID[17:31]
    filename = devidstr + "_O.cal"
    try:
        CalFile = open(filename)
        for line in CalFile:
            exec( line.rstrip() )
        CalFile.close()
    except:
        print "Cal file for this device not found"
#
def BSampleAveragemode():
    global SampleModeTime, OverSampleRate

    SampleModeTime.set(1)
    s = askstring("Sample averaging", "Value: " + str(OverSampleRate) + "\n\nNew value:\n(1-n)")

    if (s == None):         # If Cancel pressed, then None
        return()

    try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
        v = int(s)
    except:
        s = "error"

    if s != "error":
        OverSampleRate = int(v)

    if OverSampleRate < 1:
        OverSampleRate = 1

#
def BTimeAveragemode():
    global RUNstatus, TRACEaverage, TRACEmodeTime

    TRACEmodeTime.set(1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateTimeScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)
#
def BTraceWidth():
    global RUNstatus, TRACEwidth

    if RUNstatus.get() == 0:      # Update if stopped
        UpdatTimeScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)
#
def BUserAMeas():
    global UserAString, UserALabel, MeasUserA

    TempString = UserALabel
    UserALabel = askstring("Measurement Label", "Current Label: " + UserALabel + "\n\nNew Label:\n", initialvalue=UserALabel)
    if (UserALabel == None):         # If Cancel pressed, then None
        MeasUserA.set(0)
        UserALabel = TempString
        return
    TempString = UserAString
    UserAString = askstring("Measurement Formula", "Current Formula: " + UserAString + "\n\nNew Formula:\n", initialvalue=UserAString)
    if (UserAString == None):         # If Cancel pressed, then None
        MeasUserA.set(0)
        UserAString = TempString
        return
    MeasUserA.set(1)
#
def BUserBMeas():
    global UserBString, UserBLabel, MeasUserB

    TempString = UserBLabel
    UserBLabel = askstring("Measurement Label", "Current Label: " + UserBLabel + "\n\nNew Label:\n", initialvalue=UserBLabel)
    if (UserBLabel == None):         # If Cancel pressed, then None
        MeasUserB.set(0)
        UserBLabel = TempString
        return
    TempString = UserBString
    UserBString = askstring("Measurement Formula", "Current Formula: " + UserBString + "\n\nNew Formula:\n", initialvalue=UserBString)
    if (UserBString == None):         # If Cancel pressed, then None
        MeasUserB.set(0)
        UserBString = TempString
        return
    MeasUserB.set(1)
#
def BEnterMathString():
    global RUNstatus, MathString, MathUnits

    TempString = MathString
    MathString = askstring("Math Formula", "Current Formula: " + MathString + "\n\nNew Formula:\n", initialvalue=MathString)
    if (MathString == None):         # If Cancel pressed, then None
        MathString = TempString
    TempString = MathUnits
    MathUnits = askstring("Math Units", "Current Units: " + MathUnits + "\n\nNew Units:\n", initialvalue=MathUnits)
    if (MathUnits == None):         # If Cancel pressed, then None
        MathUnits = TempString
    if RUNstatus.get() > 0:
        UpdateTimeTrace()

def BEnterMathXString():
    global RUNstatus, XYScreenStatus, MathXString, xywindow, MathXUnits

    TempString = MathXString
    if XYScreenStatus.get() == 0:
        MathXString = askstring("X Math Formula", "Current X Formula: " + MathXString + "\n\nNew X Formula:\n", initialvalue=MathXString)
        if (MathXString == None):         # If Cancel pressed, then None
            MathXString = TempString
        TempString = MathXUnits
        MathXUnits = askstring("X Math Units", "Current X Units: " + MathXUnits + "\n\nNew X Units:\n", initialvalue=MathXUnits)
        if (MathXUnits == None):         # If Cancel pressed, then None
            MathXUnits = TempString
    else:
        MathXString = askstring("X Math Formula", "Current X Formula: " + MathXString + "\n\nNew X Formula:\n", initialvalue=MathXString, parent=xywindow)
        if (MathXString == None):         # If Cancel pressed, then None
            MathXString = TempString
        TempString = MathXUnits
        MathXUnits = askstring("X Units", "Current X Units: " + MathXUnits + "\n\nNew X Units:\n", initialvalue=MathXUnits, parent=xywindow)
        if (MathXUnits == None):         # If Cancel pressed, then None
            MathXUnits = TempString
        if RUNstatus.get() > 0:
            UpdateXYTrace()
    
def BEnterMathYString():
    global RUNstatus, XYScreenStatus, MathYString, xywindow, MathYUnits

    TempString = MathYString
    if XYScreenStatus.get() == 0:
        MathYString = askstring("Y Math Formula", "Current Y Formula: " + MathYString + "\n\nNew Y Formula:\n", initialvalue=MathYString)
        if (MathYString == None):         # If Cancel pressed, then None
            MathYString = TempString
        TempString = MathYUnits
        MathYUnits = askstring("Y Math Units", "Current Y Units: " + MathYUnits + "\n\nNew Y Units:\n", initialvalue=MathYUnits)
        if (MathYUnits == None):         # If Cancel pressed, then None
            MathYUnits = TempString
    else:
        MathYString = askstring("Y Math Formula", "Current Y Formula: " + MathYString + "\n\nNew Y Formula:\n", initialvalue=MathYString, parent=xywindow)
        if (MathYString == None):         # If Cancel pressed, then None
            MathYString = TempString
        TempString = MathYUnits
        MathYUnits = askstring("Y Units", "Current Y Units: " + MathYUnits + "\n\nNew Y Units:\n", initialvalue=MathYUnits, parent=xywindow)
        if (MathYUnits == None):         # If Cancel pressed, then None
            MathYUnits = TempString
        if RUNstatus.get() > 0:
            UpdateXYTrace()
#
def BSetMarkerLocation():
    global MarkerLoc

    TempString = MarkerLoc
    MarkerLoc = askstring("Marker Text Location", "Current Marker Text Location: " + MarkerLoc + "\n\nNew Location: (UL, UR, LL, LR)\n", initialvalue=MarkerLoc)
    if (MarkerLoc == None):         # If Cancel pressed, then None
        MarkerLoc = TempString
    UpdateTimeTrace()
#
def donothing():
    global RUNstatus
    
def DoNothing(event):
    global RUNstatus
    
def BShowCurvesAll():
    global ShowC1_V, ShowC2_V
    ShowC1_V.set(1)
    ShowC2_V.set(1)
    UpdateTimeTrace()

def BShowCurvesNone():
    global ShowC1_V, ShowC2_V
    ShowC1_V.set(0)
    ShowC2_V.set(0)
    UpdateTimeTrace()
    
def BTriggerEdge():
    global TgEdge
                                       
# TRIGCOND trigcondRisingPositive = 0
# TRIGCOND trigcondFallingNegative = 1

def BTrigger50p():
    global TgInput, TRIGGERlevel, TRIGGERentry
    global MaxV1, MinV1, MaxV2, MinV2
    # set new trigger level to mid point of waveform    
    MidV1 = (MaxV1+MinV1)/2
    MidV2 = (MaxV2+MinV2)/2
    if (TgInput.get() == 0):
        DCString = "0.0"
    elif (TgInput.get() == 1 ):
        DCString = ' {0:.2f}'.format(MidV1)
    elif (TgInput.get() == 3 ):
        DCString = ' {0:.2f}'.format(MidV2)

    TRIGGERlevel = eval(DCString)
    TRIGGERentry.delete(0,END)
    TRIGGERentry.insert(4, DCString)
    
    UpdateTimeTrace()           # Always Update
    
def BTriggerMode(): # place holder for future hardware triggering if implemented
    global TgInput, m2k_adc0_trigger, m2k_adc1_trigger, m2k_adc3_trigger, m2k_adc4_trigger, m2k_adc5_trigger, m2k_adc6_trigger

    m2k_adc0_trigger.attrs["trigger"].value = 'edge-rising'
    m2k_adc0_trigger.attrs["trigger_level"].value = str(0)
    m2k_adc0_trigger.attrs["trigger_hysteresis"].value = str(10)
    m2k_adc1_trigger.attrs["trigger"].value = 'edge-rising'
    m2k_adc4_trigger.attrs["mode"].value = 'analog'
    m2k_adc6_trigger.attrs["logic_mode"].value = 'a'

    if (TgInput.get() == 0):
        m2k_adc4_trigger.attrs["mode"].value = 'always'
        m2k_adc5_trigger.attrs["mode"].value = 'always'
    elif (TgInput.get() == 1): # trigger rising edge 
        m2k_adc0_trigger.attrs["trigger"].value = 'edge-rising'
        m2k_adc1_trigger.attrs["trigger"].value = 'edge-rising'
    elif (TgInput.get() == 3): # trigger falling edge
        m2k_adc0_trigger.attrs["trigger"].value = 'edge-falling'
        m2k_adc1_trigger.attrs["trigger"].value = 'edge-falling'
        # 0 disables auto trigger
        
def BTriglevel(event):
    global TRIGGERlevel, TRIGGERentry, m2k_adc0_trigger, m2k_adc1_trigger
    global ch1_multiplier, ch2_multiplier

    # evalute entry string to a numerical value
    try:
        TRIGGERlevel = float(eval(TRIGGERentry.get()))
    except:
        TRIGGERentry.delete(0,END)
        TRIGGERentry.insert(0, TRIGGERlevel)
    # set new trigger level
    tgl_a = int(TRIGGERlevel*2048/ch1_multiplier)
    m2k_adc0_trigger.attrs["trigger_level"].value = str(tgl_a)
    tgl_b = int(TRIGGERlevel*2048/ch2_multiplier)
    m2k_adc1_trigger.attrs["trigger_level"].value = str(tgl_b)
    UpdateTimeTrace()           # Always Update

def BHoldOff(event):
    global HoldOff, HoldOffentry

    try:
        HoldOff = float(eval(HoldOffentry.get()))
    except:
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, HoldOff)
#
def BHozPoss(event):
    global HozPoss, HozPossentry

    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
#
def SetTriggerPoss():
    global HozPossentry, TgInput, TMsb

    # get time scale
    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    # prevent divide by zero error
    if TIMEdiv < 0.00005:
        TIMEdiv = 0.00005
    if TgInput.get() > 0:
        HozPoss = -5 * TIMEdiv
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
#
def IncHoldOff():
    global HoldOffentry, HoldOff, TgInput, TMsb

# get time scale
    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    # prevent divide by zero error
    if TIMEdiv < 0.00005:
        TIMEdiv = 0.00005
    if TgInput.get() == 0:
        HoldOff = HoldOff + TIMEdiv
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, HoldOff)
        
def SetVAPoss():
    global CHAVPosEntry, DCV1
    
    CHAVPosEntry.delete(0,"end")
    CHAVPosEntry.insert(0, ' {0:.2f}'.format(DCV1))
#
def SetVBPoss():
    global CHBVPosEntry, DCV2
    
    CHBVPosEntry.delete(0,"end")
    CHBVPosEntry.insert(0, ' {0:.2f}'.format(DCV2))
#
def SetXYVAPoss():
    global CHAVPosEntryxy, DCV1
    
    CHAVPosEntryxy.delete(0,"end")
    CHAVPosEntryxy.insert(0, ' {0:.2f}'.format(DCV1))
#
def SetXYVBPoss():
    global CHBVPosEntryxy, DCV2
    
    CHBVPosEntryxy.delete(0,"end")
    CHBVPosEntryxy.insert(0, ' {0:.2f}'.format(DCV2))
#    
def Bcloseexit():
    global RUNstatus, ctx, PlusUS, NegUS, ad5627, ad5625, m2k_fabric, dac_a_pd, dac_b_pd
    global AWG1Offset, AWG2Offset, m2k_AWG1pd, m2k_AWG2pd, AWGAoffset, AWGBoffset
    
    RUNstatus.set(0)
    if DevID != "No Device":
        PlusUS.attrs["powerdown"].value = str(1) # power down positve user supply
        PlusUS.attrs["raw"].value = str(0) # set value to zero volts
        NegUS.attrs["powerdown"].value = str(1) # power down negative user supply
        NegUS.attrs["raw"].value = str(0) # set value to zero volts
        #
        m2k_fabric.attrs["clk_powerdown"].value = '1'
        m2k_AWG1pd.attrs["powerdown"].value = '1'
        m2k_AWG2pd.attrs["powerdown"].value = '1'
        AWG1Offset.attrs["powerdown"].value = '1'
        AWG2Offset.attrs["powerdown"].value = '1'
        dac_a_pd.attrs["powerdown"].value = '1'
        dac_b_pd.attrs["powerdown"].value = '1'
        AWG1Offset.attrs["raw"].value = '2000' # str(AWGAoffset)
        AWG2Offset.attrs["raw"].value = '2000' # str(AWGBoffset)
    #
    BSaveConfig("alice-last-config.cfg")
    # close ALM and exit
    root.destroy()
    exit()

def BStart():
    global RUNstatus, PowerStatus, PwrBt, DevID, FWRevOne
    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
##    elif FWRevOne == 0.0:
##        showwarning("WARNING","Out of data Firmware!")
    else:
        if PowerStatus == 0:
            PowerStatus = 1
            PwrBt.config(bg="green",text="PWR-On")
            # turn on analog power
        if (RUNstatus.get() == 0):
            RUNstatus.set(1)
    # UpdateTimeScreen()          # Always Update

def BStop():
    global RUNstatus, TimeDisp, XYDisp, FreqDisp, IADisp
    
    if (RUNstatus.get() == 1):
        RUNstatus.set(0)
    elif (RUNstatus.get() == 2):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 3):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 4):
        RUNstatus.set(3)
    if TimeDisp.get() > 0:
        UpdateTimeScreen()          # Always Update screens as necessary
    if XYDisp.get() > 0:
        UpdateXYScreen()
    if FreqDisp.get() > 0:
        UpdateFreqScreen()
    if IADisp.get() > 0:
        UpdateIAScreen()

def BPower():
    global RUNstatus, PowerStatus, PwrBt, ctx, PlusUS, NegUS, ad5627
    
    if (RUNstatus.get() == 1):
        BStop()
    if PowerStatus == 1:
        PowerStatus = 0
        PwrBt.config(bg="red",text="PWR-Off")
        PlusUS.attrs["powerdown"].value = str(1) # power down positve user supply
        NegUS.attrs["powerdown"].value = str(1) # power down negative user supply
    else:
        PowerStatus = 1
        PwrBt.config(bg="green",text="PWR-On")
        PlusUS.attrs["powerdown"].value = str(0) # power up positve user supply
        NegUS.attrs["powerdown"].value = str(0) # power up negative user supply
    
def BTime():
    global TIMEdiv, TMsb, RUNstatus

    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
        
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)

    UpdateTimeTrace()           # Always Update

def BCHAlevel():
    global CHAsb
    
    try:
        CH1vpdvLevel = float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,END)
        CHAsb.insert(0, CH1vpdvLevel)
    UpdateTimeTrace()           # Always Update

def BCHBlevel():
    global CHBsb
    
    try:
        CH2vpdvLevel = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2vpdvLevel)
    UpdateTimeTrace()           # Always Update    

def BOffsetA(event):
    global CHAOffset, CHAVPosEntry

    try:
        CHAOffset = float(eval(CHAVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    # set new offset level
    UpdateTimeTrace()           # Always Update

def BOffsetB(event):
    global CHBOffset, CHBVPosEntry

    try:
        CHBOffset = float(eval(CHBVPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    # set new offset level
    UpdateTimeTrace()           # Always Update
# set check box colors
def TimeCheckBox():
    global TimeDisp, ckb1
    if TimeDisp.get() == 1:
        ckb1.config(style="Enab.TCheckbutton")
    else:
        ckb1.config(style="Disab.TCheckbutton")
#
def XYCheckBox():
    global XYDisp, ckb2
    if XYDisp.get() == 1:
        ckb2.config(style="Enab.TCheckbutton")
    else:
        ckb2.config(style="Disab.TCheckbutton")
#
def FreqCheckBox():
    global FreqDisp, ckb3
    if FreqDisp.get() == 1:
        ckb3.config(style="Enab.TCheckbutton")
    else:
        ckb3.config(style="Disab.TCheckbutton")
#
def BodeCheckBox():
    global BodeDisp, ckb5
    if BodeDisp.get() == 1:
        ckb5.config(style="Enab.TCheckbutton")
    else:
        ckb5.config(style="Disab.TCheckbutton")
#
def IACheckBox():
    global IADisp, ckb4
    if IADisp.get() == 1:
        ckb4.config(style="Enab.TCheckbutton")
    else:
        ckb4.config(style="Disab.TCheckbutton")
#
def OhmCheckBox():
    global OhmDisp, ckb6
    if OhmDisp.get() == 1:
        ckb6.config(style="Enab.TCheckbutton")
    else:
        ckb6.config(style="Disab.TCheckbutton")
#
# ========================= Main routine ====================================
def Analog_In():
    global RUNstatus, SingleShot, TimeDisp, XYDisp, FreqDisp, SpectrumScreenStatus, HWRevOne
    global IADisp, IAScreenStatus, CutDC, AWGBMode, MuxEnb, BodeScreenStatus, BodeDisp, OhmDisp
    global MuxScreenStatus, VBuffA, VBuffB, VBuffMA, VBuffMB, VBuffMC, VBuffMD, MuxSync
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, ShowC1_V, ShowC2_V, SMPfft, FStep, MuxChan
    global ckb1, ckb2, ckb3, ckb4, ckb5, ckb6, OhmRunStatus, enb1, VFilterA, VFilterB
    global cts, logic, Dig0, Dig1, Dig2, Dig3, Dig4, Dig5, TimeBuffer, m2k_adc, SHOWsamples
    global PlusUS_RB, plusUSrb, NegUS_RB, negUSrb, PlusUSEnab, NegUSEnab
    # Main loop
    while (True):
        if (RUNstatus.get() == 1) or (RUNstatus.get() == 2):
            if PlusUSEnab.get() > 0: # Read back scaled values for user power supplies
                posrb_val = float(PlusUS_RB.attrs['scale'].value) * float(PlusUS_RB.attrs['raw'].value)/498
                posrb_str = ' {0:.3f} '.format(posrb_val)
                plusUSrb.configure(text=posrb_str)
            if NegUSEnab.get() > 0:
                negrb_val = float(NegUS_RB.attrs['scale'].value) * float(NegUS_RB.attrs['raw'].value)/495.5
                negrb_str = ' {0:.3f} '.format(negrb_val * -1)
                negUSrb.configure(text=negrb_str)
            #
            if TimeDisp.get() > 0 or XYDisp.get() > 0:
                if MuxScreenStatus.get() == 0:
                    Analog_Time_In()
                else:
                    ShowC2_V.set(0) # force B voltage trace off
                    if MuxEnb.get() == 1:
                        PIO2 = 1
                    else:
                        PIO2 = 0
                    if MuxSync.get() == 0:
                        PIO3 = 1
                        PIO3x = 0
                    else:
                        PIO3 = 0
                        PIO3x = 1
                    if Show_CBD.get() == 1:
                        MuxChan = 3
                        Dig0.attrs["direction"].value = 'out'
                        Dig0.attrs["raw"].value = str(1) # set PIO 0 to 1
                        Dig1.attrs["direction"].value = 'out'
                        Dig1.attrs["raw"].value = str(1) # set PIO 1 to 1
                        Dig2.attrs["direction"].value = 'out'
                        Dig2.attrs["raw"].value = str(PIO2) # set PIO 2 to 0
                        Dig3.attrs["direction"].value = 'out'
                        Dig3.attrs["raw"].value = str(PIO3) # set PIO 3 to sync pulse for sweep start
                        time.sleep(0.001)
                        Dig3.attrs["direction"].value = 'out'
                        Dig3.attrs["raw"].value = str(PIO3x) # set PIO 3 to return value
                        del(TimeBuffer) # delete old buffer and make a new one
                        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
                        Analog_Time_In()
                        
                    if Show_CBC.get() == 1:
                        MuxChan = 2
                        Dig0.attrs["direction"].value = 'out'
                        Dig0.attrs["raw"].value = '0' # set PIO 0 to 0
                        Dig1.attrs["direction"].value = 'out'
                        Dig1.attrs["raw"].value = '1' # set PIO 1 to 1
                        Dig2.attrs["direction"].value = 'out'
                        Dig2.attrs["raw"].value = str(PIO2) # set PIO 2 to 0
                        Dig3.attrs["direction"].value = 'out'
                        Dig3.attrs["raw"].value = str(PIO3) # set PIO 3 to sync pulse for sweep start
                        time.sleep(0.001)
                        Dig3.attrs["raw"].value = str(PIO3x) # set PIO 3 to return value
                        del(TimeBuffer) # delete old buffer and make a new one
                        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
                        Analog_Time_In()
                        
                    if Show_CBB.get() == 1:
                        MuxChan = 1
                        Dig0.attrs["direction"].value = 'out'
                        Dig0.attrs["raw"].value = '1' # set PIO 0 to 1
                        Dig1.attrs["direction"].value = 'out'
                        Dig1.attrs["raw"].value = '0' # set PIO 1 to 0
                        Dig2.attrs["direction"].value = 'out'
                        Dig2.attrs["raw"].value = str(PIO2) # set PIO 2 to 0
                        Dig3.attrs["direction"].value = 'out'
                        Dig3.attrs["raw"].value = str(PIO3) # set PIO 3 to sync pulse for sweep start
                        time.sleep(0.001)
                        Dig3.attrs["raw"].value = str(PIO3x) # set PIO 3 to return value
                        del(TimeBuffer) # delete old buffer and make a new one
                        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
                        Analog_Time_In()
                        
                    if Show_CBA.get() == 1 or ShowC1_V.get() == 1:
                        MuxChan = 0
                        Dig0.attrs["direction"].value = 'out'
                        Dig0.attrs["raw"].value = str(0) # set PIO 0 to 0
                        Dig1.attrs["direction"].value = 'out'
                        Dig1.attrs["raw"].value = str(0) # set PIO 1 to 0
                        Dig2.attrs["direction"].value = 'out'
                        Dig2.attrs["raw"].value = str(PIO2) # set PIO 2 to 0
                        Dig3.attrs["direction"].value = 'out'
                        Dig3.attrs["raw"].value = str(PIO3) # set PIO 3 to sync pulse for sweep start
                        time.sleep(0.001)
                        Dig3.attrs["raw"].value = str(PIO3x) # set PIO 3 to return value
                        del(TimeBuffer) # delete old buffer and make a new one
                        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
                        Analog_Time_In()
                        
            if (FreqDisp.get() > 0 and SpectrumScreenStatus.get() == 1) or (IADisp.get() > 0 and IAScreenStatus.get() == 1) or (BodeDisp.get() > 0 and BodeScreenStatus.get() == 1):
                if IADisp.get() > 0 or BodeDisp.get() > 0:
                    CutDC.set(1)
                Analog_Freq_In()
        elif OhmRunStatus.get() == 1 and OhmDisp.get() == 1:
            Ohm_Analog_In()
        root.update_idletasks()
        root.update()
#
def Ohm_Analog_In():
    global CHATestVEntry, CHATestREntry, OhmA0, TimeBuffer, ADsignal1
    global OverSampleRate, SAMPLErate, AWGAOffsetEntry
    global m2k_adc0_trigger, m2k_adc1_trigger, m2k_adc3_trigger, m2k_adc4_trigger, m2k_adc5_trigger, m2k_adc6_trigger
    global CH1_H_Gain, CH1_L_Gain, CH2_H_Gain, CH2_L_Gain, OldShowSamples, SHOWsamples
    global CH1_H_Gain1K, CH1_L_Gain1K, CH2_H_Gain1K, CH2_L_Gain1K
    global CH1_H_Gain10K, CH1_L_Gain10K, CH2_H_Gain10K, CH2_L_Gain10K
    global CH1_H_Gain100K, CH1_L_Gain100K, CH2_H_Gain100K, CH2_L_Gain100K
    global CH1_H_Gain1M, CH1_L_Gain1M, CH2_H_Gain1M, CH2_L_Gain1M
    global CH1_H_Gain10M, CH1_L_Gain10M, CH2_H_Gain10M, CH2_L_Gain10M
    global CH1_H_Gain100M, CH1_L_Gain100M, CH2_H_Gain100M, CH2_L_Gain100M
    global Scope1Offset, CH1hwOffset, Scope2Offset, CH2hwOffset, ad5625, ctx
    
    OldShowSamples = SHOWsamples
    NewSAMPLErate = 100000
    CH1_H_Gain = CH1_H_Gain100K
    CH1_L_Gain = CH1_L_Gain100K
    CH2_H_Gain = CH2_H_Gain100K
    CH2_L_Gain = CH2_L_Gain100K
    if NewSAMPLErate != SAMPLErate:
        SAMPLErate = NewSAMPLErate
        m2k_adc.attrs["oversampling_ratio"].value = str(OverSampleRate)
        m2k_adc.attrs["sampling_frequency"].value = str(SAMPLErate)
# get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntry.get()))
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntry.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
# get the vertical ranges
    try:
        CH1pdvRange = float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,END)
        CHAsb.insert(0, CH1vpdvRange)
    try:
        CH2pdvRange = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2vpdvRange)
#
    if CH1pdvRange < 1.0:
        m2k_adc0.attrs["gain"].value = 'high'
        ch1_multiplier = CH1_H_Gain
        HwOffset = int(float(CHAVPosEntry.get())*1000/2.84)
        NewOffset = CH1hwOffset - HwOffset
        if NewOffset > 4095:
            NewOffset = 4095
        if NewOffset < 0:
            NewOffset = 0
        Scope1Offset.attrs["raw"].value = str(NewOffset)
    else:
        m2k_adc0.attrs["gain"].value = 'low'
        ch1_multiplier = CH1_L_Gain
        Scope1Offset.attrs["raw"].value = str(CH1hwOffset)
    if CH2pdvRange < 1.0:
        m2k_adc1.attrs["gain"].value = 'high'
        ch2_multiplier = CH2_H_Gain
        HwOffset = int(float(CHBVPosEntry.get())*1000/2.84)
        NewOffset = CH2hwOffset - HwOffset
        if NewOffset > 4095:
            NewOffset = 4095
        if NewOffset < 0:
            NewOffset = 0
        Scope2Offset.attrs["raw"].value = str(NewOffset)
    else:
        m2k_adc1.attrs["gain"].value = 'low'
        ch2_multiplier = CH2_L_Gain
        Scope2Offset.attrs["raw"].value = str(NewOffset)
#
    try:
        chatestv = float(eval(CHATestVEntry.get()))
    except:
        CHATestVEntry.delete(0,END)
        CHATestVEntry.insert(0, chatestv)
    try:
        chatestr = float(eval(CHATestREntry.get()))
    except:
        CHATestREntry.delete(0,END)
        CHATestREntry.insert(0, chatestr)
    #
    DCVA0 = DCVB0 = 0.0 # initalize measurment variable
    RIN = 1041000 # nominal ALM2000 input resistance is 1.041 Mohm
    m2k_adc4_trigger.attrs["mode"].value = 'always' # turn off triggering
    m2k_adc5_trigger.attrs["mode"].value = 'always'
    # set AWG 1 to DC value
    AWGAOffsetEntry.delete(0,"end")
    AWGAOffsetEntry.insert(0, chatestv)
    AWGAShape.set(0)
    UpdateAWGA()
    # Get A0 and B0 data
    SHOWsamples = 200
    if OldShowSamples != SHOWsamples:
        del(TimeBuffer) # delete old buffer and make a new one
        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
    TimeBuffer.refill() # fill the buffer
    x = TimeBuffer.read() # read the buffer
    ADsignal1 = []
    VBuffA = [] # Clear the V Buff array for trace A
    VBuffB = [] # Clear the V Buff array for trace B
    for n in range (0, len(x), 2): # formated as hex unsigned 12 bits little-endian
        ADsignal1.append(struct.unpack_from("<h", x, n)[0])
    n = 0
    rec_length = len(ADsignal1)
    while n < rec_length:
        VCH1 = float(ADsignal1[n])
        VCH2 = float(ADsignal1[n+1])
        DCVA0 = DCVA0 + ((VCH1/2048.0)*ch1_multiplier) # scale to volts
        DCVB0 = DCVB0 + ((VCH2/2048.0)*ch2_multiplier) # scale to volts
        n = n + 2
#
    DCVA0 = DCVA0 / 200.0 # calculate average
    DCVB0 = DCVB0 / 200.0 # calculate average
    DCVA0 = DCVA0 + CHAOffset
    DCVB0 = DCVB0 + CHBOffset
    DCM = chatestr * (DCVB0/(DCVA0-DCVB0))
    DCR = (DCM * RIN) / (RIN - DCM) # correct for channel B input resistance
    if DCR < 1000:
        OhmString = '{0:.2f} '.format(DCR) + "Ohms "# format with 2 decimal places
    else:
        OhmString = '{0:.3f} '.format(DCR/1000) + "KOhms " # divide by 1000 and format with 3 decimal places
    IAString = "Meas " + ' {0:.2f} '.format(DCVA0) + " V"
    OhmA0.config(text = OhmString) # change displayed value
#
    time.sleep(0.1)
#
def m2k_capture():
    global m2k_adc, TimeBuffer, SHOWsamples, TgInput, Is_Triggered

    # TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
    # buf = iio.Buffer(m2k_adc, 1000, False)
    try:
        TimeBuffer.refill()
        # print("Got data")
        if TgInput.get() > 0: # check to see if triggering is not none
            Is_Triggered = 1
        else:
            Is_Triggered = 0
        return True
    except:
        # print("Timeout")
        return False
#
def Analog_Time_In():   # Read the analog data and store the data into the arrays
    global ADsignal1, TimeBuffer, VBuffA, VBuffB, VFilterA, VFilterB
    global VmemoryA, VmemoryB, VBuffMA, VBuffMB, VBuffMC, VBuffMD, MuxChan
    global AWGAMode, AWGBMode, TMsb, HoldOff, HoldOffentry, HozPoss, HozPossentry
    global MuxScreenStatus
    global TRACEresetTime, TRACEmodeTime, TRACEaverage, TRIGGERsample, TRIGGERlevel
    global CHA, CHB, m2k_adc, adc0, adc1, m2k_adc0, m2k_adc1, LoopBackGain
    global TRACES, TRACESread, TRACEsize, Awg_divider, ADC_0_gain, ADC_0_gain
    global RUNstatus, SingleShot, TimeDisp, XYDisp, FreqDisp
    global TIMEdiv1x, TIMEdiv, hldn, GRW, OldShowSamples
    global SAMPLErate, OverSampleRate, SHOWsamples, MinSamples, MaxSamples, AWGASampleRate, AWGBSampleRate
    global TRACErefresh, AWGScreenStatus, XYScreenStatus, MeasureStatus
    global SCREENrefresh, DCrefresh, ShowLoopBack, m2k_fabric, m2k_adc_trigger
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2, SV1, SV2, SVA_B
    global TgEdge, TgInput, AutoLevel, Is_Triggered, TriggerMethod
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHBVPosEntry, ch1_multiplier, ch2_multiplier, CH1PosFactor, CH2PosFactor
    global InOffA, InGainA, InOffB, InGainB, OldCH1pdvRange, OldCH2pdvRange, CH1pdvRange, CH2pdvRange
    global DigFiltA, DigFiltB, DFiltACoef, DFiltBCoef, DigBuffA, DigBuffB
    global m2k_adc0_trigger, m2k_adc1_trigger, m2k_adc3_trigger, m2k_adc4_trigger, m2k_adc5_trigger, m2k_adc6_trigger
    global CH1_H_Gain, CH1_L_Gain, CH2_H_Gain, CH2_L_Gain
    global CH1_H_Gain1K, CH1_L_Gain1K, CH2_H_Gain1K, CH2_L_Gain1K
    global CH1_H_Gain10K, CH1_L_Gain10K, CH2_H_Gain10K, CH2_L_Gain10K
    global CH1_H_Gain100K, CH1_L_Gain100K, CH2_H_Gain100K, CH2_L_Gain100K
    global CH1_H_Gain1M, CH1_L_Gain1M, CH2_H_Gain1M, CH2_L_Gain1M
    global CH1_H_Gain10M, CH1_L_Gain10M, CH2_H_Gain10M, CH2_L_Gain10M
    global CH1_H_Gain100M, CH1_L_Gain100M, CH2_H_Gain100M, CH2_L_Gain100M
    global Scope1Offset, CH1hwOffset, Scope2Offset, CH2hwOffset, ad5625, ctx
    
    # get time scale in mS/div
    OldShowSamples = SHOWsamples
    if ShowLoopBack.get() == 1:
        m2k_fabric.attrs["calibration_mode"].value = 'dac'
    else:
        m2k_fabric.attrs["calibration_mode"].value = 'none'
    try:
        TIMEdiv = eval(TMsb.get())
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    if TIMEdiv < 0.00005:
        TIMEdiv = 0.00005
    #
    if TRACEmodeTime.get() == 0 and TRACEresetTime == False:
        TRACEresetTime = True   # Clear the memory for averaging
    elif TRACEmodeTime.get() == 1:
        if TRACEresetTime == True:
            TRACEresetTime = False
        VmemoryA = VBuffA # Save previous trace in memory in trace average mode
        VmemoryB = VBuffB
    # see if time base hase changed and adjust gain corrections
    TryRate = (GRW*1000)/(10*TIMEdiv)
    if TryRate <= 1000:
        NewSAMPLErate = 1000
        CH1_H_Gain = CH1_H_Gain1K
        CH1_L_Gain = CH1_L_Gain1K
        CH2_H_Gain = CH2_H_Gain1K
        CH2_L_Gain = CH2_L_Gain1K
    elif TryRate > 1000 and TryRate <= 10000:
        NewSAMPLErate = 10000
        CH1_H_Gain = CH1_H_Gain10K
        CH1_L_Gain = CH1_L_Gain10K
        CH2_H_Gain = CH2_H_Gain10K
        CH2_L_Gain = CH2_L_Gain10K
    elif TryRate > 10000 and TryRate <= 100000:
        NewSAMPLErate = 100000
        CH1_H_Gain = CH1_H_Gain100K
        CH1_L_Gain = CH1_L_Gain100K
        CH2_H_Gain = CH2_H_Gain100K
        CH2_L_Gain = CH2_L_Gain100K
    elif TryRate > 100000 and TryRate <= 1000000:
        NewSAMPLErate = 1000000
        CH1_H_Gain = CH1_H_Gain1M
        CH1_L_Gain = CH1_L_Gain1M
        CH2_H_Gain = CH2_H_Gain1M
        CH2_L_Gain = CH2_L_Gain1M 
    elif TryRate > 1000000 and TryRate <= 10000000:
        NewSAMPLErate = 10000000
        CH1_H_Gain = CH1_H_Gain10M
        CH1_L_Gain = CH1_L_Gain10M
        CH2_H_Gain = CH2_H_Gain10M
        CH2_L_Gain = CH2_L_Gain10M 
    elif TryRate > 10000000:
        NewSAMPLErate = 100000000
        CH1_H_Gain = CH1_H_Gain100M
        CH1_L_Gain = CH1_L_Gain100M
        CH2_H_Gain = CH2_H_Gain100M
        CH2_L_Gain = CH2_L_Gain100M 
    if NewSAMPLErate != SAMPLErate:
        SAMPLErate = NewSAMPLErate
        m2k_adc.attrs["oversampling_ratio"].value = str(OverSampleRate)
        m2k_adc.attrs["sampling_frequency"].value = str(SAMPLErate)
        if CH1pdvRange < 1.0:
            ch1_multiplier = CH1_H_Gain
        else:
            ch1_multiplier = CH1_L_Gain
        if CH2pdvRange < 1.0:
            ch2_multiplier = CH2_H_Gain
        else:
            ch2_multiplier = CH2_L_Gain
# get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntry.get()))
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntry.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
# Do input probe Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
    try:
        InOffA = float(eval(CHAVOffsetEntry.get()))
    except:
        CHAVOffsetEntry.delete(0,END)
        CHAVOffsetEntry.insert(0, InOffA)
    try:
        InGainA = float(eval(CHAVGainEntry.get()))
    except:
        CHAVGainEntry.delete(0,END)
        CHAVGainEntry.insert(0, InGainA)
    try:
        InOffB = float(eval(CHBVOffsetEntry.get()))
    except:
        CHBVOffsetEntry.delete(0,END)
        CHBVOffsetEntry.insert(0, InOffB)
    try:
        InGainB = float(eval(CHBVGainEntry.get()))
    except:
        CHBVGainEntry.delete(0,END)
        CHBVGainEntry.insert(0, InGainB)
# evalute entry string to a numerical value
    try:
        if AutoLevel.get() == 1:
            if TgInput.get() == 1:
                TRIGGERlevel = (MinV1 + MaxV1)/2
            if TgInput.get() == 3:
                TRIGGERlevel = (MinV2 + MaxV2)/2
            TRIGGERentry.delete(0,"end")
            TRIGGERentry.insert(0, ' {0:.4f} '.format(TRIGGERlevel))
        else:
            TRIGGERlevel = eval(TRIGGERentry.get())
    except:
        TRIGGERentry.delete(0,END)
        TRIGGERentry.insert(0, TRIGGERlevel)
# get the vertical ranges
    try:
        CH1pdvRange = float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,END)
        CHAsb.insert(0, CH1vpdvRange)
    try:
        CH2pdvRange = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2vpdvRange)
    if CH1pdvRange < 1.0:
        if OldCH1pdvRange != CH1pdvRange:
            m2k_adc0.attrs["gain"].value = 'high'
            ch1_multiplier = CH1_H_Gain
        HwOffset = int(float(CHAVPosEntry.get())*CH1PosFactor)
        NewOffset = CH1hwOffset - HwOffset
        if NewOffset > 4095:
            NewOffset = 4095
        if NewOffset < 0:
            NewOffset = 0
        if ShowLoopBack.get() == 1:
            Scope1Offset.attrs["raw"].value = str(CH1hwOffset)
        else:
            Scope1Offset.attrs["raw"].value = str(NewOffset)
    else:
        if OldCH1pdvRange != CH1pdvRange:
            m2k_adc0.attrs["gain"].value = 'low'
            ch1_multiplier = CH1_L_Gain
        # HwOffset = int(float(CHAVPosEntry.get())*1000/36)
        # NewOffset = CH1hwOffset - HwOffset
        Scope1Offset.attrs["raw"].value = str(CH1hwOffset)
    if CH2pdvRange < 1.0:
        if OldCH2pdvRange != CH2pdvRange:
            m2k_adc1.attrs["gain"].value = 'high'
            ch2_multiplier = CH2_H_Gain
        HwOffset = int(float(CHBVPosEntry.get())*CH2PosFactor)
        NewOffset = CH2hwOffset - HwOffset
        if NewOffset > 4095:
            NewOffset = 4095
        if NewOffset < 0:
            NewOffset = 0
        if ShowLoopBack.get() == 1:
            Scope2Offset.attrs["raw"].value = str(CH2hwOffset)
        else:
            Scope2Offset.attrs["raw"].value = str(NewOffset)
    else:
        if OldCH2pdvRange != CH2pdvRange:
            m2k_adc1.attrs["gain"].value = 'low'
            ch2_multiplier = CH2_L_Gain
        # HwOffset = int(float(CHBVPosEntry.get())*1000/36)
        # NewOffset = CH2hwOffset - HwOffset
        Scope2Offset.attrs["raw"].value = str(CH2hwOffset)
    OldCH1pdvRange = CH1pdvRange
    OldCH2pdvRange = CH2pdvRange
    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
            HoldOffentry.delete(0,END)
            HoldOffentry.insert(0, HoldOff)
    except:
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, HoldOff)
#
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
#
    if TriggerMethod == "HW" or TriggerMethod == "hw":
        if TgInput.get() == 0:
            m2k_adc4_trigger.attrs["mode"].value = 'always'
            m2k_adc5_trigger.attrs["mode"].value = 'always'
        elif TgInput.get() == 1:
            m2k_adc4_trigger.attrs["mode"].value = 'analog'
            m2k_adc5_trigger.attrs["mode"].value = 'always'
            tgl_a = int((TRIGGERlevel*2048.0)/ch1_multiplier)
            m2k_adc0_trigger.attrs["trigger_level"].value = str(tgl_a)
            m2k_adc6_trigger.attrs["logic_mode"].value = 'a'
        elif TgInput.get() == 3:
            m2k_adc4_trigger.attrs["mode"].value = 'always'
            m2k_adc5_trigger.attrs["mode"].value = 'analog'
            tgl_b = int((TRIGGERlevel*2048.0)/ch2_multiplier)
            m2k_adc1_trigger.attrs["trigger_level"].value = str(tgl_b)
            m2k_adc6_trigger.attrs["logic_mode"].value = 'b'
        if TgEdge.get() == 0:
            m2k_adc0_trigger.attrs["trigger"].value = 'edge-rising'
            m2k_adc1_trigger.attrs["trigger"].value = 'edge-rising'
        else:
            m2k_adc0_trigger.attrs["trigger"].value = 'edge-falling'
            m2k_adc1_trigger.attrs["trigger"].value = 'edge-falling'
    else:
        m2k_adc4_trigger.attrs["mode"].value = 'always'
        m2k_adc5_trigger.attrs["mode"].value = 'always'
#
    hldn = int(HoldOff * SAMPLErate/1000 )
    hozpos = int(HozPoss * SAMPLErate/1000 )
    if hozpos < 0:
        hozpos = 0
    twoscreens = int(SAMPLErate * 20.0 * TIMEdiv / 1000.0) # number of samples to acquire, 2 screen widths
##    if hldn+hozpos > MaxSamples-twoscreens:
##        hldn = MaxSamples-twoscreens-hozpos
##        HoldOffentry.delete(0,END)
##        HoldOffentry.insert(0, hldn*1000/SAMPLErate)
    if SAMPLErate == 1000:
        SHOWsamples = 1000
    elif SAMPLErate == 10000:
        SHOWsamples = 10000
    else:
        SHOWsamples = 16384 # twoscreens + hldn + hozpos
    if SHOWsamples > MaxSamples: # or a Max of 16,384 samples
        SHOWsamples = MaxSamples
    if SHOWsamples < MinSamples: # or a Min of 1000 samples
        SHOWsamples = MinSamples
# Starting acquisition
    #time.sleep(0.05)
    if OldShowSamples != SHOWsamples: # number of samples has changed
        del(TimeBuffer) # delete old buffer and make a new one
        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
    if TriggerMethod == "HW" or TriggerMethod == "hw":
        Is_Triggered = m2k_adc_trigger.reg_read(0x3c) # m2k_adc_trigger.attrs["triggered"].value
        if Is_Triggered != 0:
            m2k_adc_trigger.reg_write(0x3c, 0x01)
        else:
            m2k_adc4_trigger.attrs["mode"].value = 'always'
            m2k_adc5_trigger.attrs["mode"].value = 'always'
        TimeBuffer.refill() # fill the buffer
    else:
        TimeBuffer.refill() # fill the buffer
    x = TimeBuffer.read() # read the buffer
    ADsignal1 = []
    VBuffA = [] # Clear the V Buff array for trace A
    VBuffB = [] # Clear the V Buff array for trace B
    for n in range (0, len(x), 2): # formated as hex unsigned 12 bits little-endian
        ADsignal1.append(struct.unpack_from("<h", x, n)[0])
    n = 0
    rec_length = len(ADsignal1)
    while n < rec_length:
        VCH1 = float(ADsignal1[n])
        VCH2 = float(ADsignal1[n+1])
        if ShowLoopBack.get() == 1: # /Awg_divider *8.25
            TempV = (((VCH1/2048.0)*LoopBackGain)*ADC_0_gain*CH1_H_Gain) - CHAOffset # scale to volts
            VBuffA.append(TempV) 
            TempV = (((VCH2/2048.0)*LoopBackGain)*ADC_1_gain*CH2_H_Gain) - CHBOffset
            VBuffB.append(TempV)
        else:
            VBuffA.append((VCH1/2048.0)*ch1_multiplier) # scale to volts
            VBuffB.append((VCH2/2048.0)*ch2_multiplier)
        n = n + 2
#
    SHOWsamples = len(VBuffA)
    VBuffA = numpy.array(VBuffA)
    VBuffB = numpy.array(VBuffB)
    if CH1pdvRange < 1.0:
        VBuffA = VBuffA + CHAOffset
    if CH2pdvRange < 1.0:
        VBuffB = VBuffB + CHBOffset
    VBuffA = (VBuffA - InOffA) * InGainA
    VBuffB = (VBuffB - InOffB) * InGainB
    TRACESread = 2
# check if digital filter box checked
    if DigFiltA.get() == 1:
        if len(DFiltACoef) > 1:
            if DigBuffA.get() == 1: # send to buffer
                VFilterA = numpy.convolve(VBuffA, DFiltACoef)
            else:
                VBuffA = numpy.convolve(VBuffA, DFiltACoef)
    if DigFiltB.get() == 1:
        if len(DFiltBCoef) > 1:
            if DigBuffB.get() == 1:
                VFilterB = numpy.convolve(VBuffB, DFiltBCoef)
            else:
                VBuffB = numpy.convolve(VBuffB, DFiltBCoef)
#
    if TriggerMethod == "SW" or TriggerMethod == "sw":
        FindTriggerSample() # Find trigger sample point if necessary
    if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
        # Average mode 1, add difference / TRACEaverage to array
        if TriggerMethod == "SW" or TriggerMethod == "sw":
            # FindTriggerSample() # Find trigger sample point if necessary
            if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
                LShift = 0 - TRIGGERsample
                VBuffA = numpy.roll(VBuffA, LShift)
                VBuffB = numpy.roll(VBuffB, LShift)
                TRIGGERsample = hozpos # set trigger sample to index 0 offset by horizontal position
        try:
            VBuffA = VmemoryA + (VBuffA - VmemoryA) / TRACEaverage.get()
            VBuffB = VmemoryB + (VBuffB - VmemoryB) / TRACEaverage.get()
        except:
            # buffer size mismatch so reset memory buffers
            VmemoryA = VBuffA
            VmemoryB = VBuffB
    if MuxScreenStatus.get() > 0:
        if Show_CBA.get() == 1 and MuxChan == 0:
            VBuffMA = VBuffB
        if Show_CBB.get() == 1 and MuxChan == 1:
            VBuffMB = VBuffB
        if Show_CBC.get() == 1 and MuxChan == 2:
            VBuffMC = VBuffB
        if Show_CBD.get() == 1 and MuxChan == 3:
            VBuffMD = VBuffB
# DC value = average of the data record
    Endsample = SHOWsamples - 1
    DCV1 = numpy.mean(VBuffA[hldn:Endsample])
    DCV2 = numpy.mean(VBuffB[hldn:Endsample])
# find min and max values
    MinV1 = numpy.amin(VBuffA[hldn:Endsample])
    MaxV1 = numpy.amax(VBuffA[hldn:Endsample])
    MinV2 = numpy.amin(VBuffB[hldn:Endsample])
    MaxV2 = numpy.amax(VBuffB[hldn:Endsample])
# RMS value = square root of average of the data record squared
    SV1 = numpy.sqrt(numpy.mean(numpy.square(VBuffA[hldn:Endsample])))
    SV2 = numpy.sqrt(numpy.mean(numpy.square(VBuffB[hldn:Endsample])))
    SVA_B = numpy.sqrt(numpy.mean(numpy.square(VBuffA[hldn:Endsample]-VBuffB[hldn:Endsample])))
#
    if TimeDisp.get() > 0:
        UpdateTimeAll()     # Update Data, trace and time screen
    if XYDisp.get() > 0 and XYScreenStatus.get() > 0:
        UpdateXYAll()         # Update Data, trace and XY screen
    if SingleShot.get() == 1: # Single shot manual trigger is on
        RUNstatus.set(0)
    if MeasureStatus.get() > 0:
        UpdateMeasureScreen()
    # RUNstatus = 3: Stop
    # RUNstatus = 4: Stop and restart
    if (RUNstatus.get() == 3) or (RUNstatus.get() == 4):
        if RUNstatus.get() == 3:
            RUNstatus.set(0) 
        if RUNstatus.get() == 4:          
            RUNstatus.set(1)

        if TimeDisp.get() > 0:
            UpdateTimeScreen()
        if XYDisp.get() > 0 and XYScreenStatus.get() > 0:
            UpdateXYScreen()
        # Update tasks and screens by TKinter
        # update screens
#
def FindTriggerSample():
    global AutoLevel, TgInput, TRIGGERlevel, TRIGGERentry, DX, SAMPLErate
    global HoldOffentry, HozPossentry, TRIGGERsample, TRACEsize, HozPoss, hozpos
    global MinV1, MaxV1, MinI1, MaxI1, MinV2, MaxV2, MinI2, MaxI2
    global VBuffA, VBuffB, IBuffA, IBuffB, Is_Triggered
    global InOffA, InGainA, InOffB, InGainB
    
    # Set the TRACEsize variable
    TRACEsize = SHOWsamples # Set the trace length
    DX = 0
    # Find trigger sample
    try:
        if AutoLevel.get() == 1:
            if TgInput.get() == 1:
                TRIGGERlevel = (MinV1 + MaxV1)/2
            if TgInput.get() == 2:
                TRIGGERlevel = (MinI1 + MaxI1)/2
            if TgInput.get() == 3:
                TRIGGERlevel = (MinV2 + MaxV2)/2
            if TgInput.get() == 4:
                TRIGGERlevel = (MinI2 + MaxI2)/2
            TRIGGERentry.delete(0,"end")
            TRIGGERentry.insert(0, ' {0:.4f} '.format(TRIGGERlevel))
        else:
            TRIGGERlevel = eval(TRIGGERentry.get())
    except:
        TRIGGERentry.delete(0,END)
        TRIGGERentry.insert(0, TRIGGERlevel)
# Start from first sample after HoldOff
    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
            HoldOffentry.delete(0,END)
            HoldOffentry.insert(0, HoldOff)
    except:
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, HoldOff)
# slide trace left right by HozPoss
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
        
    hldn = int(HoldOff * SAMPLErate/1000)
    hozpos = int(HozPoss * SAMPLErate/1000)
    if hozpos >= 0:
        TRIGGERsample = hldn
    else:
        TRIGGERsample = abs(hozpos)
#      
    Nmax = int(TRACEsize / 1.5) # first 2/3 of data set
    DX = 0
    if TRIGGERlevel >= 0.0:
        PosHist = 0.98
        NegHist = 1.02
    else:
        PosHist = 1.02
        NegHist = 0.98
    n = TRIGGERsample
    if (TgInput.get() == 1 ):
        TRIGGERlevel2 = PosHist * TRIGGERlevel # Hysteresis to avoid triggering on noise
        if TRIGGERlevel2 < MinV1:
            TRIGGERlevel2 = MinV1
        if TRIGGERlevel2 > MaxV1:
            TRIGGERlevel2 = MaxV1
        ChInput = VBuffA[int(n)]
        Prev = ChInput
        while ( ChInput >= TRIGGERlevel2) and n < Nmax:
            n = n + 1
            ChInput = VBuffA[int(n)]
        while (ChInput <= TRIGGERlevel) and n < Nmax:
            Prev = ChInput
            n = n + 1
            ChInput = VBuffA[int(n)]
        DY = ChInput - Prev
        if DY != 0.0:
            DX = (TRIGGERlevel - Prev)/DY # calculate interpolated trigger point
        else:
            DX = 0
        if TgEdge.get() == 1:
            TRIGGERlevel2 = NegHist * TRIGGERlevel
            if TRIGGERlevel2 < MinV1:
                TRIGGERlevel2 = MinV1
            if TRIGGERlevel2 > MaxV1:
                TRIGGERlevel2 = MaxV1
            ChInput = VBuffA[int(n)]
            Prev = ChInput
            while (ChInput <= TRIGGERlevel2) and n < Nmax:
                n = n + 1
                ChInput = VBuffA[int(n)]
            while (ChInput >= TRIGGERlevel) and n < Nmax:
                Prev = ChInput
                n = n + 1
                ChInput = VBuffA[int(n)]
            DY = Prev - ChInput
            if DY != 0.0:
                DX = (Prev - TRIGGERlevel)/DY # calculate interpolated trigger point
            else:
                DX = 0
#
    elif (TgInput.get() == 3 ):
        TRIGGERlevel2 = PosHist * TRIGGERlevel # Hysteresis to avoid triggering on noise
        if TRIGGERlevel2 < MinV2:
            TRIGGERlevel2 = MinV2
        if TRIGGERlevel2 > MaxV2:
            TRIGGERlevel2 = MaxV2
        ChInput = VBuffB[int(n)]
        Prev = ChInput
        while (ChInput >= TRIGGERlevel2) and n < Nmax:
            n = n + 1
            ChInput = VBuffB[int(n)]
        while (ChInput <= TRIGGERlevel) and n < Nmax:
            Prev = ChInput
            n = n + 1
            ChInput = VBuffB[int(n)]
        DY = ChInput - Prev
        if DY != 0.0:
            DX = (TRIGGERlevel - Prev)/DY # calculate interpolated trigger point
        else:
            DX = 0
        if TgEdge.get() == 1:
            TRIGGERlevel2 = NegHist * TRIGGERlevel
            if TRIGGERlevel2 < MinV2:
                TRIGGERlevel2 = MinV2
            if TRIGGERlevel2 > MaxV2:
                TRIGGERlevel2 = MaxV2
            ChInput = VBuffB[int(n)] 
            Prev = ChInput
            while (ChInput <= TRIGGERlevel2) and n < Nmax:
                n = n + 1
                ChInput = VBuffB[int(n)] 
            while (ChInput >= TRIGGERlevel) and n < Nmax:
                Prev = ChInput
                n = n + 1
                ChInput = VBuffB[int(n)] 
            DY = Prev - ChInput
            if DY != 0.0:
                DX = (Prev - TRIGGERlevel)/DY # calculate interpolated trigger point
            else:
                DX = 0
# check to insure trigger point is in bounds                
    if n < Nmax:
        TRIGGERsample = n - 1
        Is_Triggered = 1
    elif n >= Nmax: # Didn't find edge in first 2/3 of data set
        TRIGGERsample = 1 + hldn # reset to begining
        Is_Triggered = 0
    if DX > 1:
        DX = 1 # never more than 100% of a sample period
    elif DX < 0:
        DX = 0 # never less than 0% of a sample period
    if math.isnan(DX):
        DX = 0
    TRIGGERsample = TRIGGERsample + hozpos
#
def MakeHistogram():
    global VBuffA, VBuffB, HBuffA, HBuffB, VFilterA, VFilterB
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global ShowC1_V, ShowC2_V, Xsignal
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global VABase, VATop, VBBase, VBTop

    if ShowC1_V.get() == 1 or Xsignal.get() == 6:
        CHAGridMax = (5 * CH1pdvRange ) + CHAOffset # Calculate CHA Grid Min and Max
        CHAGridMin = (-5 * CH1pdvRange ) + CHAOffset
        VAMid = (MinV1 + MaxV1)/2 # Find CHA mid value
        HBuffA = numpy.histogram(VBuffA, bins=5000, range=[CHAGridMin, CHAGridMax] )
        LowerPeak = 0
        UpperPeak = 0
        b = 0
        while (b < 4999):
            if HBuffA[0][b] > HBuffA[0][LowerPeak] and HBuffA[1][b] < VAMid:
                LowerPeak = b
                VABase = HBuffA[1][b]
            if HBuffA[0][b] > HBuffA[0][UpperPeak] and HBuffA[1][b] > VAMid:
                UpperPeak = b
                VATop = HBuffA[1][b]
            b = b + 1
    if ShowC2_V.get() == 1 or Xsignal.get() == 7:
        CHBGridMax = (5 * CH2pdvRange ) + CHBOffset # Calculate CHB Grid Min and Max
        CHBGridMin = (-5 * CH2pdvRange ) + CHBOffset
        VBMid = (MinV2 + MaxV2)/2 # Find CHB mid value
        HBuffB = numpy.histogram(VBuffB, bins=5000, range=[CHBGridMin, CHBGridMax] )
        LowerPeak = 0
        UpperPeak = 0
        b = 0
        while (b < 4999):
            if HBuffB[0][b] > HBuffB[0][LowerPeak] and HBuffB[1][b] < VBMid:
                LowerPeak = b
                VBBase = HBuffB[1][b]
            if HBuffB[0][b] > HBuffB[0][UpperPeak] and HBuffB[1][b] > VBMid:
                UpperPeak = b
                VBTop = HBuffB[1][b]
            b = b + 1
#
def BHistAsPercent():
    global HistAsPercent

    if askyesno("Plot as Percent", "Plot Histogram as Percent?", parent=xywindow):
        HistAsPercent = 1
    else:
        HistAsPercent = 0
#
def FindRisingEdge():
    global MinV1, MaxV1, MinV2, MaxV2, HoldOff
    global VBuffA, VBuffB, hldn, SHOWsamples, VFilterA, VFilterB
    global SHOWsamples, SAMPLErate, CHAperiod, CHAfreq, CHBperiod, CHBfreq
    global CHAHW, CHALW, CHADCy, CHBHW, CHBLW, CHBDCy, ShowC1_V, ShowC2_V
    global CHABphase, CHBADelayR1, CHBADelayR2, CHBADelayF
    
    anr1 = bnr1 = 0
    anf1 = bnf1 = 1
    anr2 = bnr2 = 2
    
# search channel 1
    Endsample = SHOWsamples - 1
    #
    if ShowC1_V.get() == 1:
        MidV1 = (MaxV1+MinV1)/2
        Arising = [i for (i, val) in enumerate(VBuffA[0:Endsample]) if val >= MidV1 and VBuffA[i-1] < MidV1]
        Afalling = [i for (i, val) in enumerate(VBuffA[0:Endsample]) if val <= MidV1 and VBuffA[i-1] > MidV1]
        AIrising = [i - (VBuffA[i] - MidV1)/(VBuffA[i] - VBuffA[i-1]) for i in Arising]
        AIfalling = [i - (MidV1 - VBuffA[i])/(VBuffA[i-1] - VBuffA[i]) for i in Afalling]
        
        CHAfreq = SAMPLErate / numpy.mean(numpy.diff(AIrising))
        CHAperiod = (numpy.mean(numpy.diff(AIrising)) * 1000.0) / SAMPLErate # time in mSec
        if len(Arising) > 0 and len(Afalling) > 0:
            if Arising[0] > 0:
                try:
                    anr1 = AIrising[0]
                except:
                    anr1 = 0
                try:
                    anr2 = AIrising[1]
                except:
                    anr2 = SHOWsamples
                try:
                    if AIfalling[0] < AIrising[0]:
                        anf1 = AIfalling[1]
                    else:
                        anf1 = AIfalling[0]
                except:
                    anf1 = 1
            else:
                try:
                    anr1 = AIrising[1]
                except:
                    anr1 = 0
                try:
                    anr2 = AIrising[2]
                except:
                    anr2 = SHOWsamples
                try:
                    if AIfalling[1] < AIrising[1]:
                        anf1 = AIfalling[2]
                    else:
                        anf1 = AIfalling[1]
                except:
                    anf1 = 1
# search channel 2
    if ShowC2_V.get() == 1:
        MidV2 = (MaxV2+MinV2)/2
        Brising = [i for (i, val) in enumerate(VBuffB[0:Endsample]) if val >= MidV2 and VBuffB[i-1] < MidV2]
        Bfalling = [i for (i, val) in enumerate(VBuffB[0:Endsample]) if val <= MidV2 and VBuffB[i-1] > MidV2]
        BIrising = [i - (VBuffB[i] - MidV2)/(VBuffB[i] - VBuffB[i-1]) for i in Brising]
        BIfalling = [i - (MidV2 - VBuffB[i])/(VBuffB[i-1] - VBuffB[i]) for i in Bfalling]
        
        CHBfreq = SAMPLErate / numpy.mean(numpy.diff(BIrising))
        CHBperiod = (numpy.mean(numpy.diff(BIrising)) * 1000.0) / SAMPLErate # time in mSec
        if len(Brising) > 0 and len(Bfalling) > 0:
            if Brising[0] > 0:
                try:
                    bnr1 = BIrising[0]
                except:
                    bnr1 = 0
                try:
                    bnr2 = BIrising[1]
                except:
                    bnr2 = SHOWsamples
                try:
                    if BIfalling[0] < BIrising[0]:
                        bnf1 = BIfalling[1]
                    else:
                        bnf1 = BIfalling[0]
                except:
                    bnf1 = 1
            else:
                try:
                    bnr1 = BIrising[1]
                except:
                    bnr1 = 0
                try:
                    bnr2 = BIrising[2]
                except:
                    bnr2 = SHOWsamples
                try:
                    if BIfalling[1] < BIrising[1]:
                        bnf1 = BIfalling[2]
                    else:
                        bnf1 = BIfalling[1]
                except:
                    bnf1 = 1
    #
    CHAHW = float(((anf1 - anr1) * 1000.0) / SAMPLErate)
    CHALW = float(((anr2 - anf1) * 1000.0) / SAMPLErate)
    CHADCy = float(anf1 - anr1) / float(anr2 - anr1) * 100.0 # in percent
    CHBHW = float(((bnf1 - bnr1) * 1000.0) / SAMPLErate)
    CHBLW = float(((bnr2 - bnf1) * 1000.0) / SAMPLErate)
    CHBDCy = float(bnf1 - bnr1) / float(bnr2 - bnr1) * 100.0 # in percent
#
    if bnr1 > anr1:
        CHBADelayR1 = float((bnr1 - anr1) * 1000.0 / SAMPLErate)
    else:
        CHBADelayR1 = float((bnr2 - anr1) * 1000.0 / SAMPLErate)
    CHBADelayR2 = float((bnr2 - anr2) * 1000.0 / SAMPLErate)
    CHBADelayF = float((bnf1 - anf1) * 1000.0 / SAMPLErate)
    try:
        CHABphase = 360.0*(float((bnr1 - anr1) * 1000.0 / SAMPLErate))/CHAperiod
    except:
        CHABphase = 0.0
    if CHABphase < 0.0:
        CHABphase = CHABphase + 360.0
#
def DestroyDigScreen():
    global win2, DigScreenStatus
    
    DigScreenStatus.set(0)
    win2.destroy()

def sel():
    global Dig0, Dig1, Dig2, Dig3, Dig4, Dig5, Dig6, Dig7, logic, ctx
    global Dig10, Dig11, Dig12, Dig13, Dig14, Dig15, Dig8, Dig9
    global D0, D1, D2, D3, D4, D5, D6, D7
    # sending 0x50 = set to 0, 0x51 = set to 1
    if D0.get() > -1:
        Dig0.attrs["direction"].value = 'out'
        Dig0.attrs["raw"].value = str(D0.get()) # set PIO 0
    else:
        Dig0.attrs["direction"].value = 'in'
    if D1.get() > -1:
        Dig1.attrs["direction"].value = 'out'
        Dig1.attrs["raw"].value = str(D1.get()) # set PIO 1
    else:
        Dig1.attrs["direction"].value = 'in'
    if D2.get() > -1:
        Dig2.attrs["direction"].value = 'out'
        Dig2.attrs["raw"].value = str(D2.get()) # set PIO 0
    else:
        Dig2.attrs["direction"].value = 'in'
    if D3.get() > -1:
        Dig3.attrs["direction"].value = 'out'
        Dig3.attrs["raw"].value = str(D3.get()) # set PIO 0
    else:
        Dig3.attrs["direction"].value = 'in'
    if D4.get() > -1:
        Dig4.attrs["direction"].value = 'out'
        Dig4.attrs["raw"].value = str(D4.get()) # set PIO 0
    else:
        Dig4.attrs["direction"].value = 'in'
    if D5.get() > -1:
        Dig5.attrs["direction"].value = 'out'
        Dig5.attrs["raw"].value = str(D5.get()) # set PIO 0
    else:
        Dig5.attrs["direction"].value = 'in'
    if D6.get() > -1:
        Dig6.attrs["direction"].value = 'out'
        Dig6.attrs["raw"].value = str(D6.get()) # set PIO 0
    else:
        Dig6.attrs["direction"].value = 'in'
    if D7.get() > -1:
        Dig7.attrs["direction"].value = 'out'
        Dig7.attrs["raw"].value = str(D7.get()) # set PIO 0
    else:
        Dig7.attrs["direction"].value = 'in'
        
def MakeDigScreen():
    global D0, D1, D2, D3, D4, D5, D6, D7
    global DigScreenStatus, PatGenScreenStatus, win2, MuxScreenStatus
    # setup Dig output window
    if DigScreenStatus.get() == 0 and PatGenScreenStatus.get() == 0 and MuxScreenStatus.get() == 0:
        DigScreenStatus.set(1)
        win2 = Toplevel()
        win2.title("Dig Out")
        win2.resizable(FALSE,FALSE)
        win2.protocol("WM_DELETE_WINDOW", DestroyDigScreen)
        rb1 = Radiobutton(win2, text="D0-0", variable=D0, value=0, command=sel )
        rb1.grid(row=2, column=0, sticky=W)
        rb0z = Radiobutton(win2, text="D0-Z", variable=D0, value=-1, command=sel )
        rb0z.grid(row=2, column=1, sticky=W)
        rb2 = Radiobutton(win2, text="D0-1", variable=D0, value=1, command=sel )
        rb2.grid(row=2, column=2, sticky=W)
        rb3 = Radiobutton(win2, text="D1-0", variable=D1, value=0, command=sel )
        rb3.grid(row=3, column=0, sticky=W)
        rb3z = Radiobutton(win2, text="D1-Z", variable=D1, value=-1, command=sel )
        rb3z.grid(row=3, column=1, sticky=W)
        rb4 = Radiobutton(win2, text="D1-1", variable=D1, value=1, command=sel )
        rb4.grid(row=3, column=2, sticky=W)
        rb5 = Radiobutton(win2, text="D2-0", variable=D2, value=0, command=sel )
        rb5.grid(row=4, column=0, sticky=W)
        rb5z = Radiobutton(win2, text="D2-Z", variable=D2, value=-1, command=sel )
        rb5z.grid(row=4, column=1, sticky=W)
        rb6 = Radiobutton(win2, text="D2-1", variable=D2, value=1, command=sel )
        rb6.grid(row=4, column=2, sticky=W)
        rb7 = Radiobutton(win2, text="D3-0", variable=D3, value=0, command=sel )
        rb7.grid(row=5, column=0, sticky=W)
        rb7z = Radiobutton(win2, text="D3-Z", variable=D3, value=-1, command=sel )
        rb7z.grid(row=5, column=1, sticky=W)
        rb8 = Radiobutton(win2, text="D3-1", variable=D3, value=1, command=sel )
        rb8.grid(row=5, column=2, sticky=W)
        rb9 = Radiobutton(win2, text="D4-0", variable=D4, value=0, command=sel )
        rb9.grid(row=6, column=0, sticky=W)
        rb9z = Radiobutton(win2, text="D4-Z", variable=D4, value=-1, command=sel )
        rb9z.grid(row=6, column=1, sticky=W)
        rb10 = Radiobutton(win2, text="D4-1", variable=D4, value=1, command=sel )
        rb10.grid(row=6, column=2, sticky=W)
        rb11 = Radiobutton(win2, text="D5-0", variable=D5, value=0, command=sel )
        rb11.grid(row=7, column=0, sticky=W)
        rb11z = Radiobutton(win2, text="D5-Z", variable=D5, value=-1, command=sel )
        rb11z.grid(row=7, column=1, sticky=W)
        rb12 = Radiobutton(win2, text="D5-1", variable=D5, value=1, command=sel )
        rb12.grid(row=7, column=2, sticky=W)
        rb13 = Radiobutton(win2, text="D6-0", variable=D6, value=0, command=sel )
        rb13.grid(row=8, column=0, sticky=W)
        rb13z = Radiobutton(win2, text="D6-Z", variable=D6, value=-1, command=sel )
        rb13z.grid(row=8, column=1, sticky=W)
        rb13 = Radiobutton(win2, text="D6-1", variable=D6, value=1, command=sel )
        rb13.grid(row=8, column=2, sticky=W)
        rb14 = Radiobutton(win2, text="D7-0", variable=D7, value=0, command=sel )
        rb14.grid(row=9, column=0, sticky=W)
        rb14z = Radiobutton(win2, text="D7-Z", variable=D7, value=-1, command=sel )
        rb14z.grid(row=9, column=1, sticky=W)
        rb15 = Radiobutton(win2, text="D7-1", variable=D7, value=1, command=sel )
        rb15.grid(row=9, column=2, sticky=W)
        dismissbutton = Button(win2, text="Dismiss", command=DestroyDigScreen)
        dismissbutton.grid(row=10, column=0, sticky=W)
#
def PatGenScroll(event):
    onTextScroll(event)
    UpdatePatGen()
    
def MakePatGenScreen():
    global DEnab0, DEnab1, DEnab2, DEnab3, DEnab4, DEnab5, DEnab6, DEnab7
    global DEnab10, DEnab11, DEnab12, DEnab13, DEnab14, DEnab15, DEnab8, DEnab9
    global Dpg0FreqEntry, Dpg1FreqEntry, Dpg2FreqEntry, Dpg3FreqEntry, Dpg4FreqEntry, Dpg5FreqEntry
    global Dpg6FreqEntry, Dpg7FreqEntry, Dpg8FreqEntry, Dpg9FreqEntry, DpgWidthEntry
    global Dpg10FreqEntry, Dpg11FreqEntry, Dpg12FreqEntry, Dpg13FreqEntry, Dpg14FreqEntry, Dpg15FreqEntry
    global Dpg0DutyEntry, Dpg1DutyEntry, Dpg2DutyEntry, Dpg3DutyEntry, Dpg4DutyEntry, Dpg5DutyEntry
    global Dpg6DutyEntry, Dpg7DutyEntry, Dpg8DutyEntry, Dpg9DutyEntry
    global Dpg10DutyEntry, Dpg11DutyEntry, Dpg12DutyEntry, Dpg13DutyEntry, Dpg14DutyEntry, Dpg15DutyEntry
    global Dpg0DelayEntry, Dpg1DelayEntry, Dpg2DelayEntry, Dpg3DelayEntry, Dpg4DelayEntry, Dpg5DelayEntry
    global Dpg6DelayEntry, Dpg7DelayEntry, Dpg8DelayEntry, Dpg9DelayEntry
    global Dpg10DelayEntry, Dpg11DelayEntry, Dpg12DelayEntry, Dpg13DelayEntry, Dpg14DelayEntry, Dpg15DelayEntry
    global PatGenScreenStatus, DigScreenStatus, pgwin, MuxScreenStatus, LenLab
    global Ckb0, Ckb1, Ckb2, Ckb3, Ckb4, Ckb5, Ckb6, Ckb7, Ckb8, Ckb9, Ckb10, Ckb11, Ckb12, Ckb13, Ckb14, Ckb15
    # setup Dig Pattern output window
    if PatGenScreenStatus.get() == 0 and DigScreenStatus.get() == 0 and MuxScreenStatus.get() == 0:
        PatGenScreenStatus.set(1)
        pgwin = Toplevel()
        pgwin.title("Digital Pattern Generator")
        pgwin.resizable(FALSE,FALSE)
        pgwin.protocol("WM_DELETE_WINDOW", DestroyPatGenScreen)
        Lab0 = Label(pgwin, text="Enable")
        Lab0.grid(row=0, column=0, sticky=W)
        Lab1 = Label(pgwin, text="Name")
        Lab1.grid(row=0, column=1, sticky=W)
        Lab2 = Label(pgwin, text="Freq Hz")
        Lab2.grid(row=0, column=2, sticky=W)
        Lab3 = Label(pgwin, text="Duty Cycle %")
        Lab3.grid(row=0, column=3, sticky=W)
        Lab4 = Label(pgwin, text="Delay mS")
        Lab4.grid(row=0, column=4, sticky=W)
        Ckb0 = Checkbutton(pgwin, text="    DIO-0", variable=DEnab0, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb0.grid(row=1, column=0, columnspan=2, sticky=W)
        Dpg0FreqEntry = Entry(pgwin, width=7)
        Dpg0FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg0FreqEntry.bind('<Key>', onTextKey)
        Dpg0FreqEntry.delete(0,"end")
        Dpg0FreqEntry.insert(0,100.0)
        Dpg0FreqEntry.grid(row=1, column=2, sticky=N)
        Dpg0DutyEntry = Entry(pgwin, width=4)
        Dpg0DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg0DutyEntry.bind('<Key>', onTextKey)
        Dpg0DutyEntry.delete(0,"end")
        Dpg0DutyEntry.insert(0,50.0)
        Dpg0DutyEntry.grid(row=1, column=3, sticky=N)
        Dpg0DelayEntry = Entry(pgwin, width=7)
        Dpg0DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg0DelayEntry.bind('<Key>', onTextKey)
        Dpg0DelayEntry.delete(0,"end")
        Dpg0DelayEntry.insert(0,0.0)
        Dpg0DelayEntry.grid(row=1, column=4, sticky=W)
        Ckb1 = Checkbutton(pgwin, text="    DIO-1", variable=DEnab1, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb1.grid(row=2, column=0, columnspan=2, sticky=W)
        Dpg1FreqEntry = Entry(pgwin, width=7)
        Dpg1FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg1FreqEntry.bind('<Key>', onTextKey)
        Dpg1FreqEntry.delete(0,"end")
        Dpg1FreqEntry.insert(0,100.0)
        Dpg1FreqEntry.grid(row=2, column=2, sticky=N)
        Dpg1DutyEntry = Entry(pgwin, width=4)
        Dpg1DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg1DutyEntry.bind('<Key>', onTextKey)
        Dpg1DutyEntry.delete(0,"end")
        Dpg1DutyEntry.insert(0,50.0)
        Dpg1DutyEntry.grid(row=2, column=3, sticky=N)
        Dpg1DelayEntry = Entry(pgwin, width=7)
        Dpg1DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg1DelayEntry.bind('<Key>', onTextKey)
        Dpg1DelayEntry.delete(0,"end")
        Dpg1DelayEntry.insert(0,0.0)
        Dpg1DelayEntry.grid(row=2, column=4, sticky=W)
        Ckb2 = Checkbutton(pgwin, text="    DIO-2", variable=DEnab2, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb2.grid(row=3, column=0, columnspan=2, sticky=W)
        Dpg2FreqEntry = Entry(pgwin, width=7)
        Dpg2FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg2FreqEntry.bind('<Key>', onTextKey)
        Dpg2FreqEntry.delete(0,"end")
        Dpg2FreqEntry.insert(0,100.0)
        Dpg2FreqEntry.grid(row=3, column=2, sticky=N)
        Dpg2DutyEntry = Entry(pgwin, width=4)
        Dpg2DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg2DutyEntry.bind('<Key>', onTextKey)
        Dpg2DutyEntry.delete(0,"end")
        Dpg2DutyEntry.insert(0,50.0)
        Dpg2DutyEntry.grid(row=3, column=3, sticky=N)
        Dpg2DelayEntry = Entry(pgwin, width=7)
        Dpg2DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg2DelayEntry.bind('<Key>', onTextKey)
        Dpg2DelayEntry.delete(0,"end")
        Dpg2DelayEntry.insert(0,0.0)
        Dpg2DelayEntry.grid(row=3, column=4, sticky=W)
        Ckb3 = Checkbutton(pgwin, text="    DIO-3", variable=DEnab3, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb3.grid(row=4, column=0, columnspan=2, sticky=W)
        Dpg3FreqEntry = Entry(pgwin, width=7)
        Dpg3FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg3FreqEntry.bind('<Key>', onTextKey)
        Dpg3FreqEntry.delete(0,"end")
        Dpg3FreqEntry.insert(0,100.0)
        Dpg3FreqEntry.grid(row=4, column=2, sticky=N)
        Dpg3DutyEntry = Entry(pgwin, width=4)
        Dpg3DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg3DutyEntry.bind('<Key>', onTextKey)
        Dpg3DutyEntry.delete(0,"end")
        Dpg3DutyEntry.insert(0,50.0)
        Dpg3DutyEntry.grid(row=4, column=3, sticky=N)
        Dpg3DelayEntry = Entry(pgwin, width=7)
        Dpg3DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg3DelayEntry.bind('<Key>', onTextKey)
        Dpg3DelayEntry.delete(0,"end")
        Dpg3DelayEntry.insert(0,0.0)
        Dpg3DelayEntry.grid(row=4, column=4, sticky=W)
        Ckb4 = Checkbutton(pgwin, text="    DIO-4", variable=DEnab4, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb4.grid(row=5, column=0, columnspan=2, sticky=W)
        Dpg4FreqEntry = Entry(pgwin, width=7)
        Dpg4FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg4FreqEntry.bind('<Key>', onTextKey)
        Dpg4FreqEntry.delete(0,"end")
        Dpg4FreqEntry.insert(0,100.0)
        Dpg4FreqEntry.grid(row=5, column=2, sticky=N)
        Dpg4DutyEntry = Entry(pgwin, width=4)
        Dpg4DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg4DutyEntry.bind('<Key>', onTextKey)
        Dpg4DutyEntry.delete(0,"end")
        Dpg4DutyEntry.insert(0,50.0)
        Dpg4DutyEntry.grid(row=5, column=3, sticky=N)
        Dpg4DelayEntry = Entry(pgwin, width=7)
        Dpg4DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg4DelayEntry.bind('<Key>', onTextKey)
        Dpg4DelayEntry.delete(0,"end")
        Dpg4DelayEntry.insert(0,0.0)
        Dpg4DelayEntry.grid(row=5, column=4, sticky=W)
        Ckb5 = Checkbutton(pgwin, text="    DIO-5", variable=DEnab5, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb5.grid(row=6, column=0, columnspan=2, sticky=W)
        Dpg5FreqEntry = Entry(pgwin, width=7)
        Dpg5FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg5FreqEntry.bind('<Key>', onTextKey)
        Dpg5FreqEntry.delete(0,"end")
        Dpg5FreqEntry.insert(0,100.0)
        Dpg5FreqEntry.grid(row=6, column=2, sticky=N)
        Dpg5DutyEntry = Entry(pgwin, width=4)
        Dpg5DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg5DutyEntry.bind('<Key>', onTextKey)
        Dpg5DutyEntry.delete(0,"end")
        Dpg5DutyEntry.insert(0,50.0)
        Dpg5DutyEntry.grid(row=6, column=3, sticky=N)
        Dpg5DelayEntry = Entry(pgwin, width=7)
        Dpg5DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg5DelayEntry.bind('<Key>', onTextKey)
        Dpg5DelayEntry.delete(0,"end")
        Dpg5DelayEntry.insert(0,0.0)
        Dpg5DelayEntry.grid(row=6, column=4, sticky=W)
        Ckb6 = Checkbutton(pgwin, text="    DIO-6", variable=DEnab6, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb6.grid(row=7, column=0, columnspan=2, sticky=W)
        Dpg6FreqEntry = Entry(pgwin, width=7)
        Dpg6FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg6FreqEntry.bind('<Key>', onTextKey)
        Dpg6FreqEntry.delete(0,"end")
        Dpg6FreqEntry.insert(0,100.0)
        Dpg6FreqEntry.grid(row=7, column=2, sticky=N)
        Dpg6DutyEntry = Entry(pgwin, width=4)
        Dpg6DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg6DutyEntry.bind('<Key>', onTextKey)
        Dpg6DutyEntry.delete(0,"end")
        Dpg6DutyEntry.insert(0,50.0)
        Dpg6DutyEntry.grid(row=7, column=3, sticky=N)
        Dpg6DelayEntry = Entry(pgwin, width=7)
        Dpg6DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg6DelayEntry.bind('<Key>', onTextKey)
        Dpg6DelayEntry.delete(0,"end")
        Dpg6DelayEntry.insert(0,0.0)
        Dpg6DelayEntry.grid(row=7, column=4, sticky=W)
        Ckb7 = Checkbutton(pgwin, text="    DIO-7", variable=DEnab7, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb7.grid(row=8, column=0, columnspan=2, sticky=W)
        Dpg7FreqEntry = Entry(pgwin, width=7)
        Dpg7FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg7FreqEntry.bind('<Key>', onTextKey)
        Dpg7FreqEntry.delete(0,"end")
        Dpg7FreqEntry.insert(0,100.0)
        Dpg7FreqEntry.grid(row=8, column=2, sticky=N)
        Dpg7DutyEntry = Entry(pgwin, width=4)
        Dpg7DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg7DutyEntry.bind('<Key>', onTextKey)
        Dpg7DutyEntry.delete(0,"end")
        Dpg7DutyEntry.insert(0,50.0)
        Dpg7DutyEntry.grid(row=8, column=3, sticky=N)
        Dpg7DelayEntry = Entry(pgwin, width=7)
        Dpg7DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg7DelayEntry.bind('<Key>', onTextKey)
        Dpg7DelayEntry.delete(0,"end")
        Dpg7DelayEntry.insert(0,0.0)
        Dpg7DelayEntry.grid(row=8, column=4, sticky=W)
        Ckb8 = Checkbutton(pgwin, text="    DIO-8", variable=DEnab8, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb8.grid(row=9, column=0, columnspan=2, sticky=W)
        Dpg8FreqEntry = Entry(pgwin, width=7)
        Dpg8FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg8FreqEntry.bind('<Key>', onTextKey)
        Dpg8FreqEntry.delete(0,"end")
        Dpg8FreqEntry.insert(0,100.0)
        Dpg8FreqEntry.grid(row=9, column=2, sticky=N)
        Dpg8DutyEntry = Entry(pgwin, width=4)
        Dpg8DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg8DutyEntry.bind('<Key>', onTextKey)
        Dpg8DutyEntry.delete(0,"end")
        Dpg8DutyEntry.insert(0,50.0)
        Dpg8DutyEntry.grid(row=9, column=3, sticky=N)
        Dpg8DelayEntry = Entry(pgwin, width=7)
        Dpg8DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg8DelayEntry.bind('<Key>', onTextKey)
        Dpg8DelayEntry.delete(0,"end")
        Dpg8DelayEntry.insert(0,0.0)
        Dpg8DelayEntry.grid(row=9, column=4, sticky=W)
        Ckb9 = Checkbutton(pgwin, text="    DIO-9", variable=DEnab9, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb9.grid(row=10, column=0, columnspan=2, sticky=W)
        Dpg9FreqEntry = Entry(pgwin, width=7)
        Dpg9FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg9FreqEntry.bind('<Key>', onTextKey)
        Dpg9FreqEntry.delete(0,"end")
        Dpg9FreqEntry.insert(0,100.0)
        Dpg9FreqEntry.grid(row=10, column=2, sticky=N)
        Dpg9DutyEntry = Entry(pgwin, width=4)
        Dpg9DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg9DutyEntry.bind('<Key>', onTextKey)
        Dpg9DutyEntry.delete(0,"end")
        Dpg9DutyEntry.insert(0,50.0)
        Dpg9DutyEntry.grid(row=10, column=3, sticky=N)
        Dpg9DelayEntry = Entry(pgwin, width=7)
        Dpg9DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg9DelayEntry.bind('<Key>', onTextKey)
        Dpg9DelayEntry.delete(0,"end")
        Dpg9DelayEntry.insert(0,0.0)
        Dpg9DelayEntry.grid(row=10, column=4, sticky=W)
        Ckb10 = Checkbutton(pgwin, text="    DIO-10", variable=DEnab10, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb10.grid(row=11, column=0, columnspan=2, sticky=W)
        Dpg10FreqEntry = Entry(pgwin, width=7)
        Dpg10FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg10FreqEntry.bind('<Key>', onTextKey)
        Dpg10FreqEntry.delete(0,"end")
        Dpg10FreqEntry.insert(0,100.0)
        Dpg10FreqEntry.grid(row=11, column=2, sticky=N)
        Dpg10DutyEntry = Entry(pgwin, width=4)
        Dpg10DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg10DutyEntry.bind('<Key>', onTextKey)
        Dpg10DutyEntry.delete(0,"end")
        Dpg10DutyEntry.insert(0,50.0)
        Dpg10DutyEntry.grid(row=11, column=3, sticky=N)
        Dpg10DelayEntry = Entry(pgwin, width=7)
        Dpg10DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg10DelayEntry.bind('<Key>', onTextKey)
        Dpg10DelayEntry.delete(0,"end")
        Dpg10DelayEntry.insert(0,0.0)
        Dpg10DelayEntry.grid(row=11, column=4, sticky=W)
        Ckb11 = Checkbutton(pgwin, text="    DIO-11", variable=DEnab11, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb11.grid(row=12, column=0, columnspan=2, sticky=W)
        Dpg11FreqEntry = Entry(pgwin, width=7)
        Dpg11FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg11FreqEntry.bind('<Key>', onTextKey)
        Dpg11FreqEntry.delete(0,"end")
        Dpg11FreqEntry.insert(0,100.0)
        Dpg11FreqEntry.grid(row=12, column=2, sticky=N)
        Dpg11DutyEntry = Entry(pgwin, width=4)
        Dpg11DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg11DutyEntry.bind('<Key>', onTextKey)
        Dpg11DutyEntry.delete(0,"end")
        Dpg11DutyEntry.insert(0,50.0)
        Dpg11DutyEntry.grid(row=12, column=3, sticky=N)
        Dpg11DelayEntry = Entry(pgwin, width=7)
        Dpg11DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg11DelayEntry.bind('<Key>', onTextKey)
        Dpg11DelayEntry.delete(0,"end")
        Dpg11DelayEntry.insert(0,0.0)
        Dpg11DelayEntry.grid(row=12, column=4, sticky=W)
        Ckb12 = Checkbutton(pgwin, text="    DIO-12", variable=DEnab12, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb12.grid(row=13, column=0, columnspan=2, sticky=W)
        Dpg12FreqEntry = Entry(pgwin, width=7)
        Dpg12FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg12FreqEntry.bind('<Key>', onTextKey)
        Dpg12FreqEntry.delete(0,"end")
        Dpg12FreqEntry.insert(0,100.0)
        Dpg12FreqEntry.grid(row=13, column=2, sticky=N)
        Dpg12DutyEntry = Entry(pgwin, width=4)
        Dpg12DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg12DutyEntry.bind('<Key>', onTextKey)
        Dpg12DutyEntry.delete(0,"end")
        Dpg12DutyEntry.insert(0,50.0)
        Dpg12DutyEntry.grid(row=13, column=3, sticky=N)
        Dpg12DelayEntry = Entry(pgwin, width=7)
        Dpg12DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg12DelayEntry.bind('<Key>', onTextKey)
        Dpg12DelayEntry.delete(0,"end")
        Dpg12DelayEntry.insert(0,0.0)
        Dpg12DelayEntry.grid(row=13, column=4, sticky=W)
        Ckb13 = Checkbutton(pgwin, text="    DIO-13", variable=DEnab13, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb13.grid(row=14, column=0, columnspan=2, sticky=W)
        Dpg13FreqEntry = Entry(pgwin, width=7)
        Dpg13FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg13FreqEntry.bind('<Key>', onTextKey)
        Dpg13FreqEntry.delete(0,"end")
        Dpg13FreqEntry.insert(0,100.0)
        Dpg13FreqEntry.grid(row=14, column=2, sticky=N)
        Dpg13DutyEntry = Entry(pgwin, width=4)
        Dpg13DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg13DutyEntry.bind('<Key>', onTextKey)
        Dpg13DutyEntry.delete(0,"end")
        Dpg13DutyEntry.insert(0,50.0)
        Dpg13DutyEntry.grid(row=14, column=3, sticky=N)
        Dpg13DelayEntry = Entry(pgwin, width=7)
        Dpg13DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg13DelayEntry.bind('<Key>', onTextKey)
        Dpg13DelayEntry.delete(0,"end")
        Dpg13DelayEntry.insert(0,0.0)
        Dpg13DelayEntry.grid(row=14, column=4, sticky=W)
        Ckb14 = Checkbutton(pgwin, text="    DIO-14", variable=DEnab14, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb14.grid(row=15, column=0, columnspan=2, sticky=W)
        Dpg14FreqEntry = Entry(pgwin, width=7)
        Dpg14FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg14FreqEntry.bind('<Key>', onTextKey)
        Dpg14FreqEntry.delete(0,"end")
        Dpg14FreqEntry.insert(0,100.0)
        Dpg14FreqEntry.grid(row=15, column=2, sticky=N)
        Dpg14DutyEntry = Entry(pgwin, width=4)
        Dpg14DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg14DutyEntry.bind('<Key>', onTextKey)
        Dpg14DutyEntry.delete(0,"end")
        Dpg14DutyEntry.insert(0,50.0)
        Dpg14DutyEntry.grid(row=15, column=3, sticky=N)
        Dpg14DelayEntry = Entry(pgwin, width=7)
        Dpg14DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg14DelayEntry.bind('<Key>', onTextKey)
        Dpg14DelayEntry.delete(0,"end")
        Dpg14DelayEntry.insert(0,0.0)
        Dpg14DelayEntry.grid(row=15, column=4, sticky=W)
        Ckb15 = Checkbutton(pgwin, text="    DIO-15", variable=DEnab15, style="Disab.TCheckbutton", command=UpdatePatGen)
        Ckb15.grid(row=16, column=0, columnspan=2, sticky=W)
        Dpg15FreqEntry = Entry(pgwin, width=7)
        Dpg15FreqEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg15FreqEntry.bind('<Key>', onTextKey)
        Dpg15FreqEntry.delete(0,"end")
        Dpg15FreqEntry.insert(0,100.0)
        Dpg15FreqEntry.grid(row=16, column=2, sticky=N)
        Dpg15DutyEntry = Entry(pgwin, width=4)
        Dpg15DutyEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg15DutyEntry.bind('<Key>', onTextKey)
        Dpg15DutyEntry.delete(0,"end")
        Dpg15DutyEntry.insert(0,50.0)
        Dpg15DutyEntry.grid(row=16, column=3, sticky=N)
        Dpg15DelayEntry = Entry(pgwin, width=7)
        Dpg15DelayEntry.bind('<MouseWheel>', PatGenScroll)
        Dpg15DelayEntry.bind('<Key>', onTextKey)
        Dpg15DelayEntry.delete(0,"end")
        Dpg15DelayEntry.insert(0,0.0)
        Dpg15DelayEntry.grid(row=16, column=4, sticky=W)
        LenLab = Label(pgwin, text="Lemgth = ")
        LenLab.grid(row=17, column=0, columnspan=3, sticky=W)
        LoadDigPat = Button(pgwin, text="Load from File", command=PatGenReadFile)
        LoadDigPat.grid(row=17, column=3, columnspan=2, sticky=W)
        WidLab = Label(pgwin, text="Enter Width")
        WidLab.grid(row=18, column=0, columnspan=2, sticky=W)
        DpgWidthEntry = Entry(pgwin, width=3)
        DpgWidthEntry.bind('<MouseWheel>', DpgWidthScroll)
        DpgWidthEntry.bind("<Return>", BSetDigChan)
        DpgWidthEntry.bind('<Key>', onTextKey)
        DpgWidthEntry.delete(0,"end")
        DpgWidthEntry.insert(0,1)
        DpgWidthEntry.grid(row=18, column=2, sticky=W)
        dismissbutton = Button(pgwin, text="Dismiss", command=DestroyPatGenScreen)
        dismissbutton.grid(row=18, column=4, sticky=W)
# Dpg0FreqEntry.bind("<Return>", BOffsetB)
def DpgWidthScroll(event):
    onTextScroll(event)
    SetDigChan()
    
def BSetDigChan(temp):
    SetDigChan()
    
def SetDigChan():
    global DEnab0, DEnab1, DEnab2, DEnab3, DEnab4, DEnab5, DEnab6, DEnab7
    global DEnab10, DEnab11, DEnab12, DEnab13, DEnab14, DEnab15, DEnab8, DEnab9
    global Dig0, Dig1, Dig2, Dig3, Dig4, Dig5, Dig6, Dig7, logic, ctx
    global Dig10, Dig11, Dig12, Dig13, Dig14, Dig15, Dig8, Dig9, DpgWidthEntry
    global PatGen0, PatGen1, PatGen2, PatGen3, PatGen4, PatGen5, PatGen6, PatGen7, Dig_Out
    global PatGen8, PatGen9, PatGen10, PatGen11, PatGen12, PatGen13, PatGen14, PatGen15
    global Ckb0, Ckb1, Ckb2, Ckb3, Ckb4, Ckb5, Ckb6, Ckb7, Ckb8, Ckb9, Ckb10, Ckb11, Ckb12, Ckb13, Ckb14, Ckb15

    try:
        DpgWidth = int(DpgWidthEntry.get())
    except:
        DpgWidthEntry.delete(0,"end")
        DpgWidthEntry.insert(0,1)
        DpgWidth = 1
    if DpgWidth >= 1:
        PatGen0.enabled = True
        Dig0.attrs["direction"].value = 'out'
        Ckb0.config(style="Enab.TCheckbutton")
        DEnab0.set(1)
    else:
        PatGen0.enabled = False
        Dig0.attrs["direction"].value = 'in'
        Ckb0.config(style="Disab.TCheckbutton")
        DEnab0.set(0)
    if DpgWidth >= 2:
        PatGen1.enabled = True
        Dig1.attrs["direction"].value = 'out'
        Ckb1.config(style="Enab.TCheckbutton")
        DEnab1.set(1)
    else:
        PatGen1.enabled = False
        Dig1.attrs["direction"].value = 'in'
        Ckb1.config(style="Disab.TCheckbutton")
        DEnab1.set(0)
    if DpgWidth >= 3:
        PatGen2.enabled = True
        Dig2.attrs["direction"].value = 'out'
        Ckb2.config(style="Enab.TCheckbutton")
        DEnab2.set(1)
    else:
        PatGen2.enabled = False
        Dig2.attrs["direction"].value = 'in'
        Ckb2.config(style="Disab.TCheckbutton")
        DEnab2.set(0)
    if DpgWidth >= 4:
        PatGen3.enabled = True
        Dig3.attrs["direction"].value = 'out'
        Ckb3.config(style="Enab.TCheckbutton")
        DEnab3.set(1)
    else:
        PatGen3.enabled = False
        Dig3.attrs["direction"].value = 'in'
        Ckb3.config(style="Disab.TCheckbutton")
        DEnab3.set(0)
    if DpgWidth >= 5:
        PatGen4.enabled = True
        Dig4.attrs["direction"].value = 'out'
        Ckb4.config(style="Enab.TCheckbutton")
        DEnab4.set(1)
    else:
        PatGen4.enabled = False
        Dig4.attrs["direction"].value = 'in'
        Ckb4.config(style="Disab.TCheckbutton")
        DEnab4.set(0)
    if DpgWidth >= 6:
        PatGen5.enabled = True
        Dig5.attrs["direction"].value = 'out'
        Ckb5.config(style="Enab.TCheckbutton")
        DEnab5.set(1)
    else:
        PatGen5.enabled = False
        Dig5.attrs["direction"].value = 'in'
        Ckb5.config(style="Disab.TCheckbutton")
        DEnab5.set(0)
    if DpgWidth >= 7:
        PatGen6.enabled = True
        Dig6.attrs["direction"].value = 'out'
        Ckb6.config(style="Enab.TCheckbutton")
        DEnab6.set(1)
    else:
        PatGen6.enabled = False
        Dig6.attrs["direction"].value = 'in'
        Ckb6.config(style="Disab.TCheckbutton")
        DEnab6.set(0)
    if DpgWidth >= 8:
        PatGen7.enabled = True
        Dig7.attrs["direction"].value = 'out'
        Ckb7.config(style="Enab.TCheckbutton")
        DEnab7.set(1)
    else:
        PatGen7.enabled = False
        Dig7.attrs["direction"].value = 'in'
        Ckb7.config(style="Disab.TCheckbutton")
        DEnab7.set(0)
    if DpgWidth >= 9:
        PatGen8.enabled = True
        Dig8.attrs["direction"].value = 'out'
        Ckb8.config(style="Enab.TCheckbutton")
        DEnab8.set(1)
    else:
        PatGen8.enabled = False
        Dig8.attrs["direction"].value = 'in'
        Ckb8.config(style="Disab.TCheckbutton")
        DEnab8.set(0)
    if DpgWidth >= 10:
        PatGen9.enabled = True
        Dig9.attrs["direction"].value = 'out'
        Ckb9.config(style="Enab.TCheckbutton")
        DEnab9.set(1)
    else:
        PatGen9.enabled = False
        Dig9.attrs["direction"].value = 'in'
        Ckb9.config(style="Disab.TCheckbutton")
        DEnab9.set(0)
    if DpgWidth >= 11:
        PatGen10.enabled = True
        Dig10.attrs["direction"].value = 'out'
        Ckb10.config(style="Enab.TCheckbutton")
        DEnab10.set(1)
    else:
        PatGen10.enabled = False
        Dig10.attrs["direction"].value = 'in'
        Ckb10.config(style="Disab.TCheckbutton")
        DEnab10.set(0)
    if DpgWidth >= 12:
        PatGen11.enabled = True
        Dig11.attrs["direction"].value = 'out'
        Ckb11.config(style="Enab.TCheckbutton")
        DEnab11.set(1)
    else:
        PatGen11.enabled = False
        Dig11.attrs["direction"].value = 'in'
        Ckb11.config(style="Disab.TCheckbutton")
        DEnab11.set(0)
    if DpgWidth >= 13:
        PatGen12.enabled = True
        Dig12.attrs["direction"].value = 'out'
        Ckb12.config(style="Enab.TCheckbutton")
        DEnab12.set(1)
    else:
        PatGen12.enabled = False
        Dig12.attrs["direction"].value = 'in'
        Ckb12.config(style="Disab.TCheckbutton")
        DEnab12.set(0)
    if DpgWidth >= 14:
        PatGen13.enabled = True
        Dig13.attrs["direction"].value = 'out'
        Ckb13.config(style="Enab.TCheckbutton")
        DEnab13.set(1)
    else:
        PatGen13.enabled = False
        Dig13.attrs["direction"].value = 'in'
        Ckb13.config(style="Disab.TCheckbutton")
        DEnab13.set(0)
    if DpgWidth >= 15:
        PatGen14.enabled = True
        Dig14.attrs["direction"].value = 'out'
        Ckb14.config(style="Enab.TCheckbutton")
        DEnab14.set(1)
    else:
        PatGen14.enabled = False
        Dig14.attrs["direction"].value = 'in'
        Ckb14.config(style="Disab.TCheckbutton")
        DEnab14.set(0)
    if DpgWidth >= 16:
        PatGen15.enabled = True
        Dig15.attrs["direction"].value = 'out'
        Ckb15.config(style="Enab.TCheckbutton")
        DEnab15.set(1)
    else:
        PatGen15.enabled = False
        Dig15.attrs["direction"].value = 'in'
        Ckb15.config(style="Disab.TCheckbutton")
        DEnab15.set(0)
    
def PatGenReadFile():
    global pgwin, LenLab
    global DigBuff0, MaxPatLength

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=pgwin)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=pgwin)
    DigPattern1 = []
    ColumnNum = 0
    ColumnSel = 0
    MaxPatLength = 0
    for row in csv_f:
        if len(row) > 1 and ColumnSel == 0:
            RequestColumn = askstring("Which Column?", "File contains 1 to " + str(len(row)) + " columns\n\nEnter column number to import:\n", initialvalue=1, parent=pgwin)
            ColumnNum = int(RequestColumn) - 1
            ColumnSel = 1
        try:
            DigPattern1.append(int(eval(row[ColumnNum])))
            MaxPatLength = MaxPatLength + 1
        except:
            print 'skipping non-numeric row'
    if len(DigPattern1) > 2:
        SetDigChan()
        DigPattern1 = bytearray(numpy.array(DigPattern1,dtype="int16"))
        try:
            DigBuff0 = iio.Buffer(Dig_Out, int(MaxPatLength), True)
        except:
            del(DigBuff0)
            DigBuff0 = iio.Buffer(Dig_Out, int(MaxPatLength), True)
        DigBuff0.write(DigPattern1)
        DigBuff0.push()
    else:
        try:
            del(DigBuff0)
        except:
            donothing()
        
    LenLab.config(text = "Length = " + str(int(len(DigPattern1))/2)) # change displayed value
    CSVFile.close()
#
def MakeDigWave(BitPos):
    global Dpgwaveform, DigPattern1, MaxPatLength, DigPatSampleRate, Dpgperiod, DpgDuty, DpgDelay
    
    Dpgwaveform = []
    
    PulseWidth = int(Dpgperiod * DpgDuty)
    if PulseWidth <= 0:
        PulseWidth = 1
    Remainder = int(Dpgperiod - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    Cycles = int(MaxPatLength / int(Dpgperiod))
    j = 0
    while j < Cycles:
        for i in range(PulseWidth):
            Dpgwaveform.append(BitPos)
        for i in range(Remainder):
            Dpgwaveform.append(0)
        j = j + 1
    Fraction = int(MaxPatLength - len(Dpgwaveform))
    if Fraction > PulseWidth:
        for i in range(PulseWidth):
            Dpgwaveform.append(BitPos)
    Dpgwaveform = numpy.array(Dpgwaveform)
    Delayvalue = DpgDelay * DigPatSampleRate / 1000
    Dpgwaveform = numpy.roll(Dpgwaveform, int(Delayvalue))
    Fraction = int(MaxPatLength - len(Dpgwaveform))
    if Fraction > 0:
        Dpgwaveform = numpy.pad(Dpgwaveform, (0, Fraction), 'edge')
    if len(DigPattern1) > 0:
        DigPattern1 = DigPattern1 + Dpgwaveform
    else:
        DigPattern1 = numpy.array(Dpgwaveform)

def UpdatePatGen():
    global DEnab0, DEnab1, DEnab2, DEnab3, DEnab4, DEnab5, DEnab6, DEnab7
    global DEnab10, DEnab11, DEnab12, DEnab13, DEnab14, DEnab15, DEnab8, DEnab9
    global Dpg0FreqEntry, Dpg1FreqEntry, Dpg2FreqEntry, Dpg3FreqEntry, Dpg4FreqEntry, Dpg5FreqEntry
    global Dpg6FreqEntry, Dpg7FreqEntry, Dpg8FreqEntry, Dpg9FreqEntry
    global Dpg10FreqEntry, Dpg11FreqEntry, Dpg12FreqEntry, Dpg13FreqEntry, Dpg14FreqEntry, Dpg15FreqEntry
    global Dpg0DutyEntry, Dpg1DutyEntry, Dpg2DutyEntry, Dpg3DutyEntry, Dpg4DutyEntry, Dpg5DutyEntry
    global Dpg6DutyEntry, Dpg7DutyEntry, Dpg8DutyEntry, Dpg9DutyEntry
    global Dpg10DutyEntry, Dpg11DutyEntry, Dpg12DutyEntry, Dpg13DutyEntry, Dpg14DutyEntry, Dpg15DutyEntry
    global Dpg0DelayEntry, Dpg1DelayEntry, Dpg2DelayEntry, Dpg3DelayEntry, Dpg4DelayEntry, Dpg5DelayEntry
    global Dpg6DelayEntry, Dpg7DelayEntry, Dpg8DelayEntry, Dpg9DelayEntry
    global Dpg10DelayEntry, Dpg11DelayEntry, Dpg12DelayEntry, Dpg13DelayEntry, Dpg14DelayEntry, Dpg15DelayEntry
    global PatGenScreenStatus, ctx, DigPatSampleRate, DigBuff0, DigPattern1, LenLab
    global PatGen0, PatGen1, PatGen2, PatGen3, PatGen4, PatGen5, PatGen6, PatGen7, Dig_Out
    global PatGen8, PatGen9, PatGen10, PatGen11, PatGen12, PatGen13, PatGen14, PatGen15
    global Ckb0, Ckb1, Ckb2, Ckb3, Ckb4, Ckb5, Ckb6, Ckb7, Ckb8, Ckb9, Ckb10, Ckb11, Ckb12, Ckb13, Ckb14, Ckb15
    global Dig0, Dig1, Dig2, Dig3, Dig4, Dig5, Dig6, Dig7, logic
    global Dig10, Dig11, Dig12, Dig13, Dig14, Dig15, Dig8, Dig9
    global Dpgwaveform, MaxPatLength, Dpgperiod, DpgDuty, DpgDelay

    DigPattern1 = [] # start with empty pattern
    MinFreq = 50000000.0
    Delayvalue = 0.0
    if DEnab0.get() == 1:
        try:
            Dpg0Freq = float(Dpg0FreqEntry.get())
        except:
            Dpg0FreqEntry.delete(0,"end")
            Dpg0FreqEntry.insert(0,100.0)
            Dpg0Freq = 100.0
        if Dpg0Freq < MinFreq:
            MinFreq = Dpg0Freq
    if DEnab1.get() == 1:
        try:
            Dpg1Freq = float(Dpg1FreqEntry.get())
        except:
            Dpg1FreqEntry.delete(0,"end")
            Dpg1FreqEntry.insert(0,100.0)
            Dpg1Freq = 100.0
        if Dpg1Freq < MinFreq:
            MinFreq = Dpg1Freq
    if DEnab2.get() == 1:
        try:
            Dpg2Freq = float(Dpg2FreqEntry.get())
        except:
            Dpg2FreqEntry.delete(0,"end")
            Dpg2FreqEntry.insert(0,100.0)
            Dpg2Freq = 100.0
        if Dpg2Freq < MinFreq:
            MinFreq = Dpg2Freq
    if DEnab3.get() == 1:
        try:
            Dpg3Freq = float(Dpg3FreqEntry.get())
        except:
            Dpg3FreqEntry.delete(0,"end")
            Dpg3FreqEntry.insert(0,100.0)
            Dpg3Freq = 100.0
        if Dpg3Freq < MinFreq:
            MinFreq = Dpg3Freq
    if DEnab4.get() == 1:
        try:
            Dpg4Freq = float(Dpg4FreqEntry.get())
        except:
            Dpg4FreqEntry.delete(0,"end")
            Dpg4FreqEntry.insert(0,100.0)
            Dpg4Freq = 100.0
        if Dpg4Freq < MinFreq:
            MinFreq = Dpg4Freq
    if DEnab5.get() == 1:
        try:
            Dpg5Freq = float(Dpg5FreqEntry.get())
        except:
            Dpg5FreqEntry.delete(0,"end")
            Dpg5FreqEntry.insert(0,100.0)
            Dpg5Freq = 100.0
        if Dpg5Freq < MinFreq:
            MinFreq = Dpg5Freq
    if DEnab6.get() == 1:
        try:
            Dpg6Freq = float(Dpg6FreqEntry.get())
        except:
            Dpg6FreqEntry.delete(0,"end")
            Dpg6FreqEntry.insert(0,100.0)
            Dpg6Freq = 100.0
        if Dpg6Freq < MinFreq:
            MinFreq = Dpg6Freq
    if DEnab7.get() == 1:
        try:
            Dpg7Freq = float(Dpg7FreqEntry.get())
        except:
            Dpg7FreqEntry.delete(0,"end")
            Dpg7FreqEntry.insert(0,100.0)
            Dpg7Freq = 100.0
        if Dpg7Freq < MinFreq:
            MinFreq = Dpg7Freq
    if DEnab8.get() == 1:
        try:
            Dpg8Freq = float(Dpg8FreqEntry.get())
        except:
            Dpg8FreqEntry.delete(0,"end")
            Dpg8FreqEntry.insert(0,100.0)
            Dpg8Freq = 100.0
        if Dpg8Freq < MinFreq:
            MinFreq = Dpg8Freq
    if DEnab9.get() == 1:
        try:
            Dpg9Freq = float(Dpg9FreqEntry.get())
        except:
            Dpg9FreqEntry.delete(0,"end")
            Dpg9FreqEntry.insert(0,100.0)
            Dpg9Freq = 100.0
        if Dpg9Freq < MinFreq:
            MinFreq = Dpg9Freq
    if DEnab10.get() == 1:
        try:
            Dpg10Freq = float(Dpg10FreqEntry.get())
        except:
            Dpg10FreqEntry.delete(0,"end")
            Dpg10FreqEntry.insert(0,100.0)
            Dpg10Freq = 100.0
        if Dpg10Freq < MinFreq:
            MinFreq = Dpg10Freq
    if DEnab11.get() == 1:
        try:
            Dpg11Freq = float(Dpg11FreqEntry.get())
        except:
            Dpg11FreqEntry.delete(0,"end")
            Dpg11FreqEntry.insert(0,100.0)
            Dpg11Freq = 100.0
        if Dpg11Freq < MinFreq:
            MinFreq = Dpg11Freq
    if DEnab12.get() == 1:
        try:
            Dpg12Freq = float(Dpg12FreqEntry.get())
        except:
            Dpg12FreqEntry.delete(0,"end")
            Dpg12FreqEntry.insert(0,100.0)
            Dpg12Freq = 100.0
        if Dpg12Freq < MinFreq:
            MinFreq = Dpg12Freq
    if DEnab13.get() == 1:
        try:
            Dpg13Freq = float(Dpg13FreqEntry.get())
        except:
            Dpg13FreqEntry.delete(0,"end")
            Dpg13FreqEntry.insert(0,100.0)
            Dpg13Freq = 100.0
        if Dpg13Freq < MinFreq:
            MinFreq = Dpg13Freq
    if DEnab14.get() == 1:
        try:
            Dpg14Freq = float(Dpg14FreqEntry.get())
        except:
            Dpg14FreqEntry.delete(0,"end")
            Dpg14FreqEntry.insert(0,100.0)
            Dpg14Freq = 100.0
        if Dpg14Freq < MinFreq:
            MinFreq = Dpg14Freq
    if DEnab15.get() == 1:
        try:
            Dpg15Freq = float(Dpg15FreqEntry.get())
        except:
            Dpg15FreqEntry.delete(0,"end")
            Dpg15FreqEntry.insert(0,100.0)
            Dpg15Freq = 100.0
        if Dpg15Freq < MinFreq:
            MinFreq = Dpg15Freq
#
    try:
        MaxPatLength = int(DigPatSampleRate/MinFreq)
    except:
        MinFreq = 100
        MaxPatLength = int(DigPatSampleRate/MinFreq)
    if DEnab0.get() == 1:
        PatGen0.enabled = True
        Dig0.attrs["direction"].value = 'out'
        Ckb0.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg0DutyEntry.get())/100.0
        except:
            Dpg0DutyEntry.delete(0,"end")
            Dpg0DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg0DelayEntry.get())
        except:
            Dpg0DelayEntry.delete(0,"end")
            Dpg0DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg0Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg0Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(1)
    else:
        PatGen0.enabled = False
        Dig0.attrs["direction"].value = 'in'
        Ckb0.config(style="Disab.TCheckbutton")
#
    if DEnab1.get() == 1:
        PatGen1.enabled = True
        Dig1.attrs["direction"].value = 'out'
        Ckb1.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg1DutyEntry.get())/100.0
        except:
            Dpg1DutyEntry.delete(0,"end")
            Dpg1DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg1DelayEntry.get())
        except:
            Dpg1DelayEntry.delete(0,"end")
            Dpg1DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg1Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg1Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(2)
    else:
        PatGen1.enabled = False
        Dig1.attrs["direction"].value = 'in'
        Ckb1.config(style="Disab.TCheckbutton")
#
    if DEnab2.get() == 1:
        PatGen2.enabled = True
        Dig2.attrs["direction"].value = 'out'
        Ckb2.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg2DutyEntry.get())/100.0
        except:
            Dpg2DutyEntry.delete(0,"end")
            Dpg2DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg2DelayEntry.get())
        except:
            Dpg2DelayEntry.delete(0,"end")
            Dpg2DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg2Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg2Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(4)
    else:
        PatGen2.enabled = False
        Dig2.attrs["direction"].value = 'in'
        Ckb2.config(style="Disab.TCheckbutton")
#
    if DEnab3.get() == 1:
        PatGen3.enabled = True
        Dig3.attrs["direction"].value = 'out'
        Ckb3.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg3DutyEntry.get())/100.0
        except:
            Dpg3DutyEntry.delete(0,"end")
            Dpg3DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg3DelayEntry.get())
        except:
            Dpg3DelayEntry.delete(0,"end")
            Dpg3DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg3Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg3Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(8)
    else:
        PatGen3.enabled = False
        Dig3.attrs["direction"].value = 'in'
        Ckb3.config(style="Disab.TCheckbutton")
#
    if DEnab4.get() == 1:
        PatGen4.enabled = True
        Dig4.attrs["direction"].value = 'out'
        Ckb4.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg4DutyEntry.get())/100.0
        except:
            Dpg4DutyEntry.delete(0,"end")
            Dpg4DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg4DelayEntry.get())
        except:
            Dpg4DelayEntry.delete(0,"end")
            Dpg4DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg4Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg4Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(16)
    else:
        PatGen4.enabled = False
        Dig4.attrs["direction"].value = 'in'
        Ckb4.config(style="Disab.TCheckbutton")
#
    if DEnab5.get() == 1:
        PatGen5.enabled = True
        Dig5.attrs["direction"].value = 'out'
        Ckb5.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg5DutyEntry.get())/100.0
        except:
            Dpg5DutyEntry.delete(0,"end")
            Dpg5DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg5DelayEntry.get())
        except:
            Dpg5DelayEntry.delete(0,"end")
            Dpg5DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg5Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg5Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(32)
    else:
        PatGen5.enabled = False
        Dig5.attrs["direction"].value = 'in'
        Ckb5.config(style="Disab.TCheckbutton")
#
    if DEnab6.get() == 1:
        PatGen6.enabled = True
        Dig6.attrs["direction"].value = 'out'
        Ckb6.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg6DutyEntry.get())/100.0
        except:
            Dpg6DutyEntry.delete(0,"end")
            Dpg6DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg6DelayEntry.get())
        except:
            Dpg6DelayEntry.delete(0,"end")
            Dpg6DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg6Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg6Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(64)
    else:
        PatGen6.enabled = False
        Dig6.attrs["direction"].value = 'in'
        Ckb6.config(style="Disab.TCheckbutton")
#
    if DEnab7.get() == 1:
        PatGen7.enabled = True
        Dig7.attrs["direction"].value = 'out'
        Ckb7.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg7DutyEntry.get())/100.0
        except:
            Dpg7DutyEntry.delete(0,"end")
            Dpg7DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg7DelayEntry.get())
        except:
            Dpg7DelayEntry.delete(0,"end")
            Dpg7DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg7Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg7Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(128)
    else:
        PatGen7.enabled = False
        Dig7.attrs["direction"].value = 'in'
        Ckb7.config(style="Disab.TCheckbutton")
#
    if DEnab8.get() == 1:
        PatGen8.enabled = True
        Dig8.attrs["direction"].value = 'out'
        Ckb8.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg8DutyEntry.get())/100.0
        except:
            Dpg8DutyEntry.delete(0,"end")
            Dpg8DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg8DelayEntry.get())
        except:
            Dpg8DelayEntry.delete(0,"end")
            Dpg8DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg8Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg8Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(256)
    else:
        PatGen8.enabled = False
        Dig8.attrs["direction"].value = 'in'
        Ckb8.config(style="Disab.TCheckbutton")
#
    if DEnab9.get() == 1:
        PatGen9.enabled = True
        Dig9.attrs["direction"].value = 'out'
        Ckb9.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg9DutyEntry.get())/100.0
        except:
            Dpg9DutyEntry.delete(0,"end")
            Dpg9DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg9DelayEntry.get())
        except:
            Dpg9DelayEntry.delete(0,"end")
            Dpg9DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg9Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg9Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(512)
    else:
        PatGen9.enabled = False
        Dig9.attrs["direction"].value = 'in'
        Ckb9.config(style="Disab.TCheckbutton")
#
    if DEnab10.get() == 1:
        PatGen10.enabled = True
        Dig10.attrs["direction"].value = 'out'
        Ckb10.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg10DutyEntry.get())/100.0
        except:
            Dpg10DutyEntry.delete(0,"end")
            Dpg10DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg10DelayEntry.get())
        except:
            Dpg10DelayEntry.delete(0,"end")
            Dpg10DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg10Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg10Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(1024)
    else:
        PatGen10.enabled = False
        Dig10.attrs["direction"].value = 'in'
        Ckb10.config(style="Disab.TCheckbutton")
#
    if DEnab11.get() == 1:
        PatGen11.enabled = True
        Dig11.attrs["direction"].value = 'out'
        Ckb11.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg11DutyEntry.get())/100.0
        except:
            Dpg11DutyEntry.delete(0,"end")
            Dpg11DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg11DelayEntry.get())
        except:
            Dpg11DelayEntry.delete(0,"end")
            Dpg11DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg11Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg11Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(2048)
    else:
        PatGen11.enabled = False
        Dig11.attrs["direction"].value = 'in'
        Ckb11.config(style="Disab.TCheckbutton")
#
    if DEnab12.get() == 1:
        PatGen12.enabled = True
        Dig12.attrs["direction"].value = 'out'
        Ckb12.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg12DutyEntry.get())/100.0
        except:
            Dpg12DutyEntry.delete(0,"end")
            Dpg12DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg12DelayEntry.get())
        except:
            Dpg12DelayEntry.delete(0,"end")
            Dpg12DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg12Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg12Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(4096)
    else:
        PatGen12.enabled = False
        Dig12.attrs["direction"].value = 'in'
        Ckb12.config(style="Disab.TCheckbutton")
#
    if DEnab13.get() == 1:
        PatGen13.enabled = True
        Dig13.attrs["direction"].value = 'out'
        Ckb13.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg13DutyEntry.get())/100.0
        except:
            Dpg13DutyEntry.delete(0,"end")
            Dpg13DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg13DelayEntry.get())
        except:
            Dpg13DelayEntry.delete(0,"end")
            Dpg13DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg13Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg13Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(8192)
    else:
        PatGen13.enabled = False
        Dig13.attrs["direction"].value = 'in'
        Ckb13.config(style="Disab.TCheckbutton")
#
    if DEnab14.get() == 1:
        PatGen14.enabled = True
        Dig14.attrs["direction"].value = 'out'
        Ckb14.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg14DutyEntry.get())/100.0
        except:
            Dpg14DutyEntry.delete(0,"end")
            Dpg14DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg14DelayEntry.get())
        except:
            Dpg14DelayEntry.delete(0,"end")
            Dpg14DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg14Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg14Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(16384)
    else:
        PatGen14.enabled = False
        Dig14.attrs["direction"].value = 'in'
        Ckb14.config(style="Disab.TCheckbutton")
#
    if DEnab15.get() == 1:
        PatGen15.enabled = True
        Dig15.attrs["direction"].value = 'out'
        Ckb15.config(style="Enab.TCheckbutton")
        try:
            DpgDuty = float(Dpg15DutyEntry.get())/100.0
        except:
            Dpg15DutyEntry.delete(0,"end")
            Dpg15DutyEntry.insert(0,50.0)
            DpgDuty = 0.5
        try:
            DpgDelay = float(Dpg15DelayEntry.get())
        except:
            Dpg15DelayEntry.delete(0,"end")
            Dpg15DelayEntry.insert(0,0.0)
            DpgDelay = 0.0
        if Dpg15Freq > 0.0:
            Dpgperiod = DigPatSampleRate/Dpg15Freq
        else:
            Dpgperiod = 10.0
        #
        MakeDigWave(32768)
    else:
        PatGen15.enabled = False
        Dig15.attrs["direction"].value = 'in'
        Ckb15.config(style="Disab.TCheckbutton")
#
    if len(DigPattern1) > 2:
        DigPattern1 = bytearray(numpy.array(DigPattern1,dtype="int16"))
        try:
            DigBuff0 = iio.Buffer(Dig_Out, int(MaxPatLength), True)
        except:
            del(DigBuff0)
            DigBuff0 = iio.Buffer(Dig_Out, int(MaxPatLength), True)
        DigBuff0.write(DigPattern1)
        DigBuff0.push()
    else:
        try:
            del(DigBuff0)
        except:
            donothing()
        
    LenLab.config(text = "Length = " + str(int(len(DigPattern1))/2)) # change displayed value
#
def DestroyPatGenScreen():
    global pgwin, PatGenScreenStatus
    
    PatGenScreenStatus.set(0)
    pgwin.destroy()

def UpdateTimeAll():        # Update Data, trace and time screen
    
    MakeTimeTrace()         # Update the traces
    UpdateTimeScreen()      # Update the screen 

def UpdateTimeTrace():      # Update time trace and screen
    
    MakeTimeTrace()         # Update traces
    UpdateTimeScreen()      # Update the screen

def UpdateTimeScreen():     # Update time screen with trace and text
    
    MakeTimeScreen()        # Update the screen
    root.update()       # Activate updated screens    

def UpdateXYAll():        # Update Data, trace and XY screen
    
    MakeXYTrace()         # Update the traces
    UpdateXYScreen()      # Update the screen 

def UpdateXYTrace():      # Update XY trace and screen
    
    MakeXYTrace()         # Update traces
    UpdateXYScreen()      # Update the screen

def UpdateXYScreen():     # Update XY screen with trace and text
    
    MakeXYScreen()        # Update the screen
    root.update()       # Activate updated screens
#
def MakeTimeTrace():    # Make the traces
    global VBuffA, VBuffB, VFilterA, VFilterB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD, MuxScreenStatus
    global VmemoryA, VmemoryB
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global T1Vline, T2Vline
    global TMAVline, TMBVline, TMCVline, TMDVline
    global Tmathline, TMXline, TMYline
    global MathString, MathXString, MathYString
    global Triggerline, Triggersymbol, TgInput, TgEdge, HoldOff, HoldOffentry
    global X0L, Y0T, GRW, GRH
    global Ymin, Ymax, Xmin, Xmax
    global SHOWsamples, ZOHold, AWGBMode
    global ShowC1_V, ShowC2_V
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global Show_MathX, Show_MathY
    global TRACES, TRACESread, RUNstatus
    global AutoCenterA, AutoCenterB
    global CHAsb, CHBsb, CHAOffset, CHBOffset
    global MC1sb, MC2sb, MC1VPosEntry, MC2VPosEntry
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate, SCstart
    global TRIGGERsample, TRACEsize, DX
    global TRIGGERlevel, TRIGGERentry, AutoLevel
    global InOffA, InGainA, InOffB, InGainB
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAVPosEntry
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global HozPoss, HozPossentry

    # Set the TRACEsize variable
    if len(VBuffA) < 100:
        return
    TRACEsize = SHOWsamples               # Set the trace length
    SCstart = 0
    ylo = 0.0
    xlo = 0.0
    # get time scale
    try:
        TIMEdiv = eval(TMsb.get())
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    if TIMEdiv < 0.00005:
        TIMEdiv = 0.00005
    #
    # Check for Auto Centering
    if AutoCenterA.get() > 0:
        CHAOffset = DCV1
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, ' {0:.2f}'.format(CHAOffset))
    if AutoCenterB.get() > 0:
        CHBOffset = DCV2
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, ' {0:.2f}'.format(CHBOffset))
    # get the vertical ranges
    try:
        CH1pdvRange = float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,END)
        CHAsb.insert(0, CH1vpdvRange)
    try:
        CH2pdvRange = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2vpdvRange)
    try:
        MC1pdvRange = float(eval(MC1sb.get()))
    except:
        MC1sb.delete(0,END)
        MC1sb.insert(0, MC1vpdvRange)
    try:
        MC2pdvRange = float(eval(MC2sb.get()))
    except:
        MC2sb.delete(0,END)
        MC2sb.insert(0, MC2vpdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntry.get()))
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntry.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    try:
        MC1Offset = float(eval(MC1VPosEntry.get()))
    except:
        MC1VPosEntry.delete(0,END)
        MC1VPosEntry.insert(0, MC1Offset)
    try:
        MC2Offset = float(eval(MC2VPosEntry.get()))
    except:
        MC2VPosEntry.delete(0,END)
        MC2VPosEntry.insert(0, MC2Offset)
    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
        
    #  drawing the traces 
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        T1Vline = []                    # Trace line channel 1 V
        T2Vline = []                    # Trace line channel 2 V
        TMAVline = []                   # V Trace line Mux channel A
        TMBVline = []                   # V Trace line Mux channel B
        TMCVline = []                   # V Trace line Mux channel C
        TMDVline = []                   # V Trace line Mux channel D
        Tmathline = []                  # math trce line
        return() 
# get probe adjustment entries
    try:
        InOffA = float(eval(CHAVOffsetEntry.get()))
    except:
        CHAVOffsetEntry.delete(0,END)
        CHAVOffsetEntry.insert(0, InOffA)
    try:
        InGainA = float(eval(CHAVGainEntry.get()))
    except:
        CHAVGainEntry.delete(0,END)
        CHAVGainEntry.insert(0, InGainA)
    try:
        InOffB = float(eval(CHBVOffsetEntry.get()))
    except:
        CHBVOffsetEntry.delete(0,END)
        CHBVOffsetEntry.insert(0, InOffB)
    try:
        InGainB = float(eval(CHBVGainEntry.get()))
    except:
        CHBVGainEntry.delete(0,END)
        CHBVGainEntry.insert(0, InGainB)

    # set and/or corrected for in range
    SCmin = int(-1 * TRIGGERsample)
    SCmax = int(TRACEsize - TRIGGERsample - 20)
    if SCstart < SCmin:             # No reading before start of array
        SCstart = SCmin
    if SCstart  > SCmax:            # No reading after end of array
        SCstart = SCmax

    # Make Trace lines etc.

    Yconv1 = float(GRH/10.0) / CH1pdvRange    # Vertical Conversion factors from samples to screen points
    Yconv2 = float(GRH/10.0) / CH2pdvRange
    Xconv1 = float(GRW/10.0) / CH1pdvRange    # Horizontal Conversion factors from samples to screen points
    Xconv2 = float(GRW/10.0) / CH2pdvRange

    if MuxScreenStatus.get() == 1: # if using analog Mux set up axis controls
        try:
            CHMApdvRange = float(eval(CHB_Asb.get()))
        except:
            CHB_Asb.delete(0,END)
            CHB_Asb.insert(0, CHMApdvRange)
        try:
            CHMBpdvRange = float(eval(CHB_Bsb.get()))
        except:
            CHB_Bsb.delete(0,END)
            CHB_Bsb.insert(0, CHMBpdvRange)
        try:
            CHMCpdvRange = float(eval(CHB_Csb.get()))
        except:
            CHB_Csb.delete(0,END)
            CHB_Csb.insert(0, CHMCpdvRange)
        try:
            CHMDpdvRange = float(eval(CHB_Dsb.get()))
        except:
            CHB_Dsb.delete(0,END)
            CHB_Dsb.insert(0, CHMDpdvRange)
        YconvMA = float(GRH/10.0) / CHMApdvRange
        YconvMB = float(GRH/10.0) / CHMBpdvRange
        YconvMC = float(GRH/10.0) / CHMCpdvRange
        YconvMD = float(GRH/10.0) / CHMDpdvRange
        try:
            CHBAOffset = float(eval(CHB_APosEntry.get()))
        except:
            CHB_APosEntry.delete(0,END)
            CHB_APosEntry.insert(0, CHBAOffset)
        try:
            CHBBOffset = float(eval(CHB_BPosEntry.get()))
        except:
            CHB_BPosEntry.delete(0,END)
            CHB_BPosEntry.insert(0, CHBBOffset)
        try:
            CHBCOffset = float(eval(CHB_CPosEntry.get()))
        except:
            CHB_CPosEntry.delete(0,END)
            CHB_CPosEntry.insert(0, CHBCOffset)
        try:
            CHBDOffset = float(eval(CHB_DPosEntry.get()))
        except:
            CHB_DPosEntry.delete(0,END)
            CHB_DPosEntry.insert(0, CHBDOffset)
# include ploting X and Y math formulas vs time
    YconvMC1 = float(GRH/10) / MC1pdvRange    # Vertical Conversion factors from samples to screen points
    YconvMC2 = float(GRH/10) / MC2pdvRange
    CHMYOffset = MC2Offset
    CHMXOffset = MC1Offset
    c1 = GRH / 2.0 + Y0T    # fixed correction channel 1
    c2 = GRH / 2.0 + Y0T    # fixed correction channel 2
 
    DISsamples = SAMPLErate * 10.0 * TIMEdiv / 1000 # number of samples to display
    T1Vline = []                    # V Trace line channel 1
    T2Vline = []                    # V Trace line channel 2
    TMAVline = []                   # V Trace line Mux channel A
    TMBVline = []                   # V Trace line Mux channel B
    TMCVline = []                   # V Trace line Mux channel C
    TMDVline = []                   # V Trace line Mux channel D
    Tmathline = []                  # math trce line
    TMXline = []                    # X math Trace line
    TMYline = []                    # Y math Trace line
    if len(VBuffA) < 4 and len(VBuffB) < 4:
        return
    t = int(SCstart + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
    if t < 0:
        t = 0
    x = 0                           # Horizontal screen pixel
#
    if (DISsamples <= GRW):
        Xstep = GRW / DISsamples
        # adjust start pixel for interpolated trigger point
        x = 0 - int(Xstep*DX)
        Tstep = 1
        x1 = 0.0                      # x position of trace line
        y1 = 0.0                    # y position of trace line
        ypv1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
        ypv2 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
        if MuxScreenStatus.get() == 1:
            if len(VBuffMA) > 4:
                ypvma = int(c2 - YconvMA * (VBuffMA[t] - CHBAOffset))
            if len(VBuffMB) > 4:
                ypvmb = int(c2 - YconvMB * (VBuffMB[t] - CHBBOffset))
            if len(VBuffMC) > 4:
                ypvmc = int(c2 - YconvMC * (VBuffMC[t] - CHBCOffset))
            if len(VBuffMD) > 4:
                ypvmd = int(c2 - YconvMD * (VBuffMD[t] - CHBDOffset))
        ypm = ypmx = ypmy = GRH / 2 + Y0T
        if TgInput.get() == 0:
            Xlimit = GRW
        else:
            Xlimit = GRW+Xstep
        while x <= Xlimit:
            if t < TRACEsize:
                x1 = x + X0L
                y1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
                if y1 < Ymin: # clip waveform if going off grid
                    y1 = Ymin
                if y1 > Ymax:
                    y1 = Ymax
                if ShowC1_V.get() == 1 :
                    if ZOHold.get() == 1:
                        T1Vline.append(int(x1))
                        T1Vline.append(int(ypv1))
                        T1Vline.append(int(x1))
                        T1Vline.append(int(y1))
                    else:    
                        T1Vline.append(int(x1))
                        T1Vline.append(int(y1))
                    ypv1 = y1
                        
                if ShowC2_V.get() == 1:
                    
                    y1 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        T2Vline.append(int(x1))
                        T2Vline.append(int(ypv2))
                        T2Vline.append(int(x1))
                        T2Vline.append(int(y1))
                    else:
                        T2Vline.append(int(x1))
                        T2Vline.append(int(y1))
                    ypv2 = y1
                if Show_CBA.get() == 1 and MuxScreenStatus.get() == 1 and len(VBuffMA)>4:
                    y1 = int(c2 - YconvMA * (VBuffMA[t] - CHBAOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        TMAVline.append(int(x1))
                        TMAVline.append(int(ypvma))
                        TMAVline.append(int(x1))
                        TMAVline.append(int(y1))
                    else:
                        TMAVline.append(int(x1))
                        TMAVline.append(int(y1))
                    ypvma = y1
                if Show_CBB.get() == 1 and MuxScreenStatus.get() == 1 and len(VBuffMB)>4:
                    y1 = int(c2 - YconvMB * (VBuffMB[t] - CHBBOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        TMBVline.append(int(x1))
                        TMBVline.append(int(ypvmb))
                        TMBVline.append(int(x1))
                        TMBVline.append(int(y1))
                    else:
                        TMBVline.append(int(x1))
                        TMBVline.append(int(y1))
                    ypvmb = y1
                if Show_CBC.get() == 1 and MuxScreenStatus.get() == 1 and len(VBuffMC)>4:
                    y1 = int(c2 - YconvMC * (VBuffMC[t] - CHBCOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        TMCVline.append(int(x1))
                        TMCVline.append(int(ypvmc))
                        TMCVline.append(int(x1))
                        TMCVline.append(int(y1))
                    else:
                        TMCVline.append(int(x1))
                        TMCVline.append(int(y1))
                    ypvmc = y1
                if Show_CBD.get() == 1 and MuxScreenStatus.get() == 1 and len(VBuffMD)>4:
                    y1 = int(c2 - YconvMD * (VBuffMD[t] - CHBDOffset))
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1:
                        TMDVline.append(int(x1))
                        TMDVline.append(int(ypvmd))
                        TMDVline.append(int(x1))
                        TMDVline.append(int(y1))
                    else:
                        TMDVline.append(int(x1))
                        TMDVline.append(int(y1))
                    ypvmd = y1
                
                if MathTrace.get() > 0:
                    if MathTrace.get() == 1: # plot sum of C1-V and C2-V
                        y1 = int(c1 - YconvMC1 * (VBuffA[t] + VBuffB[t] - MC1Offset))

                    elif MathTrace.get() == 2: # plot difference of C1-V and C2-V 
                        y1 = int(c1 - YconvMC1 * (VBuffA[t] - VBuffB[t] - MC1Offset))

                    elif MathTrace.get() == 3: # plot difference of C2-V and C1-V 
                        y1 = int(c2 - YconvMC1 * (VBuffB[t] - VBuffA[t] - MC1Offset))

                    elif MathTrace.get() == 10: # plot ratio of C2-V and CA1-V
                        try:
                            y1 = int(c1 - YconvMC1 * ((VBuffB[t] / VBuffA[t]) - MC1Offset)) #  voltage gain 1 to 2
                        except:
                            y1 = int(c1 - YconvMC1 * ((VBuffB[t] / 0.000001) - MC1Offset)) # divide by small number rather than zero
                    elif MathTrace.get() == 12: # plot from equation string
                        # MathString = "(VBuffA[t]+ VBuffB[t] - CHAOffset)"
                        try:
                            MathResult = eval(MathString)
                            MathResult = MathResult - MC1Offset
                            y1 = int(c1 - YconvMC1 * MathResult)
                        except:
                            RUNstatus.set(0)
                            x = Xlimit + 1 # exit loop
                            BEnterMathString()
                        
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        Tmathline.append(int(x1))
                        Tmathline.append(int(ypm))
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    else:    # connet the dots with single line
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    ypm = y1
                if Show_MathX.get() > 0:
                    try:
                        MathResult = eval(MathXString)
                        MathResult = MathResult - MC1Offset
                        y1 = int(c1 - YconvMC1 * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = Xlimit + 1 # exit loop
                        BEnterMathXString()
                        
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMXline.append(int(x1))
                        TMXline.append(int(ypmx))
                        TMXline.append(int(x1))
                        TMXline.append(int(y1))
                    else:    # connet the dots with single line
                        TMXline.append(int(x1))
                        TMXline.append(int(y1))
                    ypmx = y1
                if Show_MathY.get() > 0:
                    try:
                        MathResult = eval(MathYString)
                        MathResult = MathResult - MC2Offset
                        y1 = int(c1 - YconvMC2 * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = Xlimit + 1 # exit loop
                        BEnterMathYString()
                        
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMYline.append(int(x1))
                        TMYline.append(int(ypmy))
                        TMYline.append(int(x1))
                        TMYline.append(int(y1))
                    else:    # connet the dots with single line
                        TMYline.append(int(x1))
                        TMYline.append(int(y1))
                    ypmy = y1
            t = int(t + Tstep)
            x = x + Xstep
            
    if (DISsamples > GRW): # if the number of samples is larger than the grid width need to ship over samples
        Xstep = 1
        Tstep = DISsamples / GRW    # number of samples to skip per grid pixel
        x1 = 0                      # x position of trace line
        ylo = 0.0                   # ymin position of trace 1 line
        yhi = 0.0                   # ymax position of trace 1 line

        t = int(SCstart + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
        if t < 0:
            t = 0
        x = 0               # Horizontal screen pixel
        ft = t              # time point with fractions
        while (x <= GRW):
            if (t < TRACEsize):
                x1 = x + X0L
                ylo = VBuffA[t] - CHAOffset
                yhi = ylo
                n = t
                while n < (t + Tstep) and n < TRACEsize:
                    if ( ShowC1_V.get() == 1 ):
                        v = VBuffA[t] - CHAOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                    n = n + 1
                ylo = int(c1 - Yconv1 * ylo)
                yhi = int(c1 - Yconv1 * yhi)
                if ( ShowC1_V.get() == 1 ):
                    if (ylo < Ymin):
                        ylo = Ymin
                    if (ylo > Ymax):
                        ylo = Ymax

                    if (yhi < Ymin):
                        yhi = Ymin
                    if (yhi > Ymax):
                        yhi = Ymax
                    T1Vline.append(int(x1))
                    T1Vline.append(int(ylo))        
                    T1Vline.append(int(x1))
                    T1Vline.append(int(yhi))
                ylo = VBuffB[t] - CHBOffset
                yhi = ylo
                n = t
                if MuxScreenStatus.get() == 0:
                    while n < (t + Tstep) and n < TRACEsize:
                        if ( ShowC2_V.get() == 1 ):
                            v = VBuffB[t] - CHBOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        n = n + 1
                    if ( ShowC2_V.get() == 1 ):
                        ylo = int(c2 - Yconv2 * ylo)
                        yhi = int(c2 - Yconv2 * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax

                        if (yhi < Ymin):
                             yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        T2Vline.append(int(x1))
                        T2Vline.append(int(ylo))        
                        T2Vline.append(int(x1))
                        T2Vline.append(int(yhi))
                else:
                    if Show_CBA.get() == 1 and len(VBuffMA)>4:
                        if t < len(VBuffMA):
                            ylo = VBuffMA[t] - CHBAOffset
                        yhi = ylo
                        n = t
                        while n < (t + Tstep) and n < len(VBuffMA):
                            v = VBuffMA[t] - CHBAOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                            n = n + 1
                        ylo = int(c2 - YconvMA * ylo)
                        yhi = int(c2 - YconvMA * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax

                        if (yhi < Ymin):
                             yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        TMAVline.append(int(x1))
                        TMAVline.append(int(ylo))        
                        TMAVline.append(int(x1))
                        TMAVline.append(int(yhi))
                    if Show_CBB.get() == 1 and len(VBuffMB)>4:
                        if t < len(VBuffMB):
                            ylo = VBuffMB[t] - CHBBOffset
                        yhi = ylo
                        n = t
                        while n < (t + Tstep) and n < len(VBuffMB):
                            v = VBuffMB[t] - CHBBOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                            n = n + 1
                        ylo = int(c2 - YconvMB * ylo)
                        yhi = int(c2 - YconvMB * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax

                        if (yhi < Ymin):
                             yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        TMBVline.append(int(x1))
                        TMBVline.append(int(ylo))        
                        TMBVline.append(int(x1))
                        TMBVline.append(int(yhi))
                    if Show_CBC.get() == 1 and len(VBuffMC)>4:
                        if t < len(VBuffMC):
                            ylo = VBuffMC[t] - CHBCOffset
                        yhi = ylo
                        n = t
                        while n < (t + Tstep) and n < len(VBuffMC):
                            v = VBuffMC[t] - CHBCOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                            n = n + 1
                        ylo = int(c2 - YconvMC * ylo)
                        yhi = int(c2 - YconvMC * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax

                        if (yhi < Ymin):
                             yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        TMCVline.append(int(x1))
                        TMCVline.append(int(ylo))        
                        TMCVline.append(int(x1))
                        TMCVline.append(int(yhi))
                    if Show_CBD.get() == 1 and len(VBuffMD)>4:
                        if t < len(VBuffMD):
                            ylo = VBuffMD[t] - CHBDOffset
                        yhi = ylo
                        n = t
                        while n < (t + Tstep) and n < len(VBuffMD):
                            v = VBuffMD[t] - CHBDOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                            n = n + 1
                        ylo = int(c2 - YconvMD * ylo)
                        yhi = int(c2 - YconvMD * yhi)
                        if (ylo < Ymin):
                            ylo = Ymin
                        if (ylo > Ymax):
                            ylo = Ymax

                        if (yhi < Ymin):
                             yhi = Ymin
                        if (yhi > Ymax):
                            yhi = Ymax
                        TMDVline.append(int(x1))
                        TMDVline.append(int(ylo))        
                        TMDVline.append(int(x1))
                        TMDVline.append(int(yhi))
                if MathTrace.get() > 0:
                    if MathTrace.get() == 1: # plot sum of C1-V and C2-V
                        y1 = int(c1 - YconvMC1 * (VBuffA[t] + VBuffB[t] - MC1Offset))

                    elif MathTrace.get() == 2: # plot difference of C1-V and C2-V 
                        y1 = int(c1 - YconvMC1 * (VBuffA[t] - VBuffB[t] - MC1Offset))

                    elif MathTrace.get() == 3: # plot difference of C2-V and C1-V 
                        y1 = int(c2 - YconvMC1 * (VBuffB[t] - VBuffA[t] - MC1Offset))

                    elif MathTrace.get() == 10: # plot ratio of C2-V and C1-V
                        try:
                            y1 = int(c1 - YconvMC1 * ((VBuffB[t] / VBuffA[t]) - MC1Offset)) #  voltage gain 1 to 2
                        except:
                            y1 = int(c1 - YconvMC1 * ((VBuffB[t] / 0.000001) - MC1Offset)) # divide by small number rather than zero

                    elif MathTrace.get() == 12: # plot from equation string
                        # MathString = "(VBuffA[t]+ VBuffB[t] - CHAOffset)"
                        try:
                            MathResult = eval(MathString)
                            MathResult = MathResult - MC1Offset
                            y1 = int(c1 - YconvMC1 * MathResult)
                        except:
                            RUNstatus.set(0)
                            x = GRW + 1 # exit loop
                            BEnterMathString()
                        
                    if (y1 < Ymin):
                        y1 = Ymin
                    if (y1 > Ymax):
                        y1 = Ymax
                    if (ZOHold.get() == 1):
                        Tmathline.append(int(x1))
                        Tmathline.append(int(ypm))
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    else:    
                        Tmathline.append(int(x1))
                        Tmathline.append(int(y1))
                    ypm = y1
                if Show_MathX.get() > 0:
                    try:
                        MathResult = eval(MathXString)
                        MathResult = MathResult - MC1Offset
                        y1 = int(c1 - YconvMC1 * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = GRW + 1 # exit loop
                        BEnterMathXString()
                        
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMXline.append(int(x1))
                        TMXline.append(int(ypmx))
                        TMXline.append(int(x1))
                        TMXline.append(int(y1))
                    else:    # connet the dots with single line
                        TMXline.append(int(x1))
                        TMXline.append(int(y1))
                    ypmx = y1
                if Show_MathY.get() > 0:
                    try:
                        MathResult = eval(MathYString)
                        MathResult = MathResult - MC2Offset
                        y1 = int(c1 - YconvMC2 * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = GRW + 1 # exit loop
                        BEnterMathYString()
                        
                    if y1 < Ymin: # clip waveform if going off grid
                        y1 = Ymin
                    if y1 > Ymax:
                        y1 = Ymax
                    if ZOHold.get() == 1: # connet the dots with stair step
                        TMYline.append(int(x1))
                        TMYline.append(int(ypmy))
                        TMYline.append(int(x1))
                        TMYline.append(int(y1))
                    else:    # connet the dots with single line
                        TMYline.append(int(x1))
                        TMYline.append(int(y1))
                    ypmy = y1
            ft = ft + Tstep
            t = int(ft)
            x = x + Xstep

    # Make trigger triangle pointer
    Triggerline = []                # Trigger pointer
    Triggersymbol = []              # Trigger symbol
    if TgInput.get() > 0:
        if TgInput.get() == 1 : # triggering on C1-V
            x1 = X0L
            ytemp = Yconv1 * (float(TRIGGERlevel)-CHAOffset) #
            y1 = int(c1 - ytemp)
        elif TgInput.get() == 3:  # triggering on C2-V
            x1 = X0L
            ytemp = Yconv2 * (float(TRIGGERlevel)-CHBOffset) #         
            y1 = int(c2 - ytemp)
            
        if (y1 < Ymin):
            y1 = Ymin
        if (y1 > Ymax):
            y1 = Ymax
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1+5))
        Triggerline.append(int(x1+5))
        Triggerline.append(int(y1))
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1-5))
        Triggerline.append(int(x1-5))
        Triggerline.append(int(y1+5))
        x1 = X0L + (GRW/2)
        if TgEdge.get() == 0: # draw rising edge symbol
            y1 = -3
            y2 = -13
        else:
            y1 = -13
            y2 = -3
        Triggersymbol.append(int(x1-10))
        Triggersymbol.append(int(Ymin+y1))
        Triggersymbol.append(int(x1))
        Triggersymbol.append(int(Ymin+y1))
        Triggersymbol.append(int(x1))
        Triggersymbol.append(int(Ymin+y2))
        Triggersymbol.append(int(x1+10))
        Triggersymbol.append(int(Ymin+y2))
#
def MakeXYTrace():    # Make the traces
    global VBuffA, VBuffB, VFilterA, VFilterB
    global VmemoryA, VmemoryB
    global TXYline, MathXString, MathYString
    global HoldOff, HoldOffentry
    global X0LXY, Y0TXY, GRWXY, GRHXY
    global YminXY, YmaxXY, XminXY, XmaxXY
    global SHOWsamples, ZOHold, AWGBMode
    global ShowC1_V, ShowC2_V
    global TRACES, TRACESread, RUNstatus
    global Xsignal, Ysignal
    global CHAsbxy, CHBsbxy, CHAOffset, CHBOffset, MC1sbxy, MC2sbxy, MC1VPosEntryxy, MC2VPosEntryxy
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate
    global SCstart, MathString
    global TRIGGERsample, TRACEsize, DX
    global TRIGGERlevel, TRIGGERentry, AutoLevel
    global InOffA, InGainA, InOffB, InGainB
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntryxy, CHAVPosEntryxy
    global HozPoss, HozPossentry

    try:
        TIMEdiv = eval(TMsb.get())
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    if TIMEdiv < 0.00005:
        TIMEdiv = 0.00005
    #
    # Set the TRACEsize variable
    if len(VBuffA) < 100:
        return
    # TRACEsize = SHOWsamples               # Set the trace length
    TRACEsize = int(SAMPLErate * 20.0 * TIMEdiv / 1000.0) # number of samples to show, 2 time screen widths
    SCstart = 0
    ylo = 0.0
    xlo = 0.0
    # get the vertical ranges
    try:
        CH1pdvRange = float(eval(CHAsbxy.get()))
    except:
        CHAsbxy.delete(0,END)
        CHAsbxy.insert(0, CH1vpdvRange)
    try:
        CH2pdvRange = float(eval(CHBsbxy.get()))
    except:
        CHBsbxy.delete(0,END)
        CHBsbxy.insert(0, CH2vpdvRange)
    try:
        MC1pdvRange = float(eval(MC1sbxy.get()))
    except:
        MC1sbxy.delete(0,END)
        MC1sb.insert(0, MC1vpdvRange)
    try:
        MC2pdvRange = float(eval(MC2sbxy.get()))
    except:
        MC2sbxy.delete(0,END)
        MC2sbxy.insert(0, MC2vpdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntryxy.get()))
    except:
        CHAVPosEntryxy.delete(0,END)
        CHAVPosEntryxy.insert(0, CHAOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntryxy.get()))
    except:
        CHBVPosEntryxy.delete(0,END)
        CHBVPosEntryxy.insert(0, CHBOffset)
    try:
        MC1Offset = float(eval(MC1VPosEntryxy.get()))
    except:
        MC1VPosEntryxy.delete(0,END)
        MC1VPosEntryxy.insert(0, MC1Offset)
    try:
        MC2Offset = float(eval(MC2VPosEntryxy.get()))
    except:
        MC2VPosEntryxy.delete(0,END)
        MC2VPosEntryxy.insert(0, MC2Offset)    # get the vertical offsets

    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    #
    Yconv1 = float(GRHXY/10.0) / CH1pdvRange    # Vertical Conversion factors from samples to screen points
    Yconv2 = float(GRHXY/10.0) / CH2pdvRange
    Xconv1 = float(GRWXY/10.0) / CH1pdvRange    # Horizontal Conversion factors from samples to screen points
    Xconv2 = float(GRWXY/10.0) / CH2pdvRange
    YconvMC1 = float(GRHXY/10.0) / MC1pdvRange    # Vertical Conversion factors from samples to screen points
    YconvMC2 = float(GRHXY/10.0) / MC2pdvRange
    XconvMC1 = float(GRWXY/10.0) / MC1pdvRange    # Horizontal Conversion factors from samples to screen points
    XconvMC2 = float(GRWXY/10.0) / MC2pdvRange

    # draw an X/Y plot
    TXYline = []        # XY Trace line
    t = int(TRIGGERsample) # skip over sampled before hold off time and trigger point
    c1 = GRHXY / 2.0 + Y0TXY   # fixed correction channel A
    c2 = GRWXY / 2.0 + X0LXY   # Hor correction factor
    while (t < TRACEsize):
        if (Xsignal.get() == 3 and Ysignal.get() == 1): # mode CAV/CBV
            ylo = VBuffA[t] - CHAOffset
            xlo = VBuffB[t] - CHBOffset
            ylo = int(c1 - Yconv1 * ylo)
            xlo = int(c2 + Xconv2 * xlo)
        elif (Xsignal.get() == 1 and Ysignal.get() == 3): # mode CBV/CAV
            ylo = VBuffB[t] - CHBOffset
            xlo = VBuffA[t] - CHAOffset
            ylo = int(c1 - Yconv2 * ylo)
            xlo = int(c2 + Xconv1 * xlo)
        elif (Xsignal.get() == 5 and Ysignal.get() == 3): # mode CBV/Math
            if ( MathTrace.get() == 2): # plot difference of C1-V and C2-V
                ylo = VBuffB[t] - CHBOffset
                ylo = int(c1 - Yconv2 * ylo)
                xlo = VBuffA[t] - VBuffB[t] - MC1Offset
                xlo = int(c2 + XconvMC1 * xlo)
        elif (Xsignal.get() == 3 and Ysignal.get() == 5): # mode Math/C2V
            if MathTrace.get() == 2: # plot difference of C1-V and C2-V
                ylo = VBuffA[t] - VBuffB[t] - MC1Offset
                ylo = int(c1 - YconvMC1 * ylo)
                xlo = VBuffB[t] - CHBOffset
                xlo = int(c2 + Xconv2 * xlo)
        elif (Xsignal.get() == 5 and Ysignal.get() == 1): # mode C1V/Math
            if MathTrace.get() == 3: # plot difference of C2-V and C1-V
                ylo = VBuffA[t] - CHAOffset
                ylo = int(c1 - Yconv1 * ylo)
                xlo = VBuffB[t] - VBuffA[t] - MC1Offset
                xlo = int(c2 + XconvMC1 * xlo)
        elif (Xsignal.get() == 1 and Ysignal.get() == 5): # mode Math/C1V
            if MathTrace.get() == 3: # plot difference of C2-V and C1-V
                ylo = VBuffB[t] - VBuffA[t] - MC1Offset
                ylo = int(c1 - YconvMC1 * ylo)
                xlo = VBuffA[t] - CHAOffset
                xlo = int(c2 + Xconv1 * xlo)
        elif (Xsignal.get() == 5 and Ysignal.get() == 5): # mode MathYString/MathXString
            try:
                MathResult = eval(MathYString)
                MathResult = MathResult - MC2Offset
                ylo = int(c1 - YconvMC2 * MathResult)
            except:
                RUNstatus.set(0)
                t = TRACEsize # exit loop
                BEnterMathYString()
            try:
                MathResult = eval(MathXString)
                MathResult = MathResult - MC1Offset
                xlo = int(c2 + XconvMC1 * MathResult)
            except:
                RUNstatus.set(0)
                t = TRACEsize # exit loop
                BEnterMathXString()
        if ylo < YminXY: # clip waveform if going off grid
            ylo  = YminXY
        if ylo > YmaxXY:
            ylo  = YmaxXY
        if xlo < XminXY: # clip waveform if going off grid
            xlo  = XminXY
        if xlo > XmaxXY:
            xlo  = XmaxXY
        TXYline.append(int(xlo))
        TXYline.append(int(ylo))
        t = int(t + 1)
        
def MakeTimeScreen():     # Update the screen with traces and text
    global T1Vline, T2Vline, TXYline # active trave lines
    global TMXline, TMYline
    global T1VRline, T2VRline # reference trace lines
    global Triggerline, Triggersymbol, Tmathline, TMRline, TXYRline, Is_Triggered
    global VBuffA, VBuffB, VFilterA, VFilterB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD, MuxScreenStatus
    global TMAVline, TMBVline, TMCVline, TMDVline, TMCRline, TMBRline
    global VmemoryA, VmemoryB
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global MouseX, MouseY, MouseWidget
    global Ymin, Ymax
    global ShowXCur, ShowYCur, TCursor, VCursor
    global SHOWsamples  # Number of samples in data record
    global ShowC1_V, ShowC2_V, ShowRXY, Show_MathX, Show_MathY
    global ShowRA_V, ShowRB_V, ShowMath, MathUnits, MathXUnits, MathYUnits
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global Xsignal, Ysignal, MathTrace
    global RUNstatus, SingleShot    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global CHAsb, MC1sb        # spinbox Index for channel 1 V
    global CHBsb, MC2sb        # spinbox Index for channel 2 V
    global CHAOffset    # Offset value for channel 1 V
    global CHBOffset    # Offset value for channel 2 V     
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate, OverSampleRate
    global TRIGGERsample, TRIGGERlevel, HoldOff, HoldOffentry, TgInput
    global COLORgrid, COLORzeroline, COLORtext, COLORtrigger, COLORtrace7, COLORtraceR7 # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6
    global COLORtraceR1, COLORtraceR2, COLORtraceR3, COLORtraceR4, COLORtraceR5, COLORtraceR6
    global CANVASwidth, CANVASheight
    global TRACErefresh, TRACEmode, TRACEwidth, GridWidth
    global ScreenTrefresh, SmoothCurves
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2, CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
    global SV1, SV2, CHABphase, SVA_B
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasRMSV1, MeasRMSV2, MeasPhase, MeasRMSVA_B
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global AWGAShape, AWGBShape, MeasDiffAB, MeasDiffBA 
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAVPosEntry
    global MC1VPosEntry, MC1VPosEntry
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global DigScreenStatus
    global Dig0, Dig1, Dig2, Dig3, Dig4, Dig5, Dig6, Dig7, logic, ctx
    global Dig10, Dig11, Dig12, Dig13, Dig14, Dig15, Dig8, Dig9
    global D0, D1, D2, D3, D4, D5, D6, D7
    global DevID, MarkerNum, MarkerScale
    global HozPoss, HozPossentry
    global VABase, VATop, VBBase, VBTop, UserALabel, UserAString, UserBLabel, UserBString
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasUserA, MeasUserB
    global CHBADelayR1, CHBADelayR2, CHBADelayF, MeasDelay
    # m2k dev info
    try:
        InOffA = float(eval(CHAVOffsetEntry.get()))
    except:
        CHAVOffsetEntry.delete(0,END)
        CHAVOffsetEntry.insert(0, InOffA)
    try:
        InGainA = float(eval(CHAVGainEntry.get()))
    except:
        CHAVGainEntry.delete(0,END)
        CHAVGainEntry.insert(0, InGainA)
    try:
        InOffB = float(eval(CHBVOffsetEntry.get()))
    except:
        CHBVOffsetEntry.delete(0,END)
        CHBVOffsetEntry.insert(0, InOffB)
    try:
        InGainB = float(eval(CHBVGainEntry.get()))
    except:
        CHBVGainEntry.delete(0,END)
        CHBVGainEntry.insert(0, InGainB)
    # get time scale
    try:
        TIMEdiv = eval(TMsb.get())
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    if TIMEdiv < 0.00005:
        TIMEdiv = 0.00005
    #
    # get the vertical ranges
    try:
        CH1pdvRange = float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,END)
        CHAsb.insert(0, CH1vpdvRange)
    try:
        CH2pdvRange = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2vpdvRange)
    try:
        MC1pdvRange = float(eval(MC1sb.get()))
    except:
        MC1sb.delete(0,END)
        MC1sb.insert(0, MC1pdvRange)
    try:
        MC2pdvRange = float(eval(MC2sb.get()))
    except:
        MC2sb.delete(0,END)
        MC2sb.insert(0, MC2pdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntry.get()))
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntry.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    try:
        MC1Offset = float(eval(MC1VPosEntry.get()))
    except:
        MC1VPosEntry.delete(0,END)
        MC1VPosEntry.insert(0, MC1Offset)
    try:
        MC2Offset = float(eval(MC2VPosEntry.get()))
    except:
        MC2VPosEntry.delete(0,END)
        MC2VPosEntry.insert(0, MC2Offset)
    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
    except:
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, HoldOff)
    # slide trace left right by HozPoss
    try:
        HozPoss = float(eval(HozPossentry.get()))
    except:
        HozPossentry.delete(0,END)
        HozPossentry.insert(0, HozPoss)
    if MuxScreenStatus.get() == 1: # if using analog Mux set up axis controls
        try:
            CHMApdvRange = float(eval(CHB_Asb.get()))
        except:
            CHB_Asb.delete(0,END)
            CHB_Asb.insert(0, CHMApdvRange)
        try:
            CHMBpdvRange = float(eval(CHB_Bsb.get()))
        except:
            CHB_Bsb.delete(0,END)
            CHB_Bsb.insert(0, CHMBpdvRange)
        try:
            CHMCpdvRange = float(eval(CHB_Csb.get()))
        except:
            CHB_Csb.delete(0,END)
            CHB_Csb.insert(0, CHMCpdvRange)
        try:
            CHMDpdvRange = float(eval(CHB_Dsb.get()))
        except:
            CHB_Dsb.delete(0,END)
            CHB_Dsb.insert(0, CHMDpdvRange)
        if CHMApdvRange < 0.001:
            CHMApdvRange = 0.001
        if CHMBpdvRange < 0.001:
            CHMBpdvRange = 0.001
        if CHMCpdvRange < 0.001:
            CHMCpdvRange = 0.001
        if CHMDpdvRange < 0.001:
            CHMDpdvRange = 0.001
        try:
            CHBAOffset = float(eval(CHB_APosEntry.get()))
        except:
            CHB_APosEntry.delete(0,END)
            CHB_APosEntry.insert(0, CHBAOffset)
        try:
            CHBBOffset = float(eval(CHB_BPosEntry.get()))
        except:
            CHB_BPosEntry.delete(0,END)
            CHB_BPosEntry.insert(0, CHBBOffset)
        try:
            CHBCOffset = float(eval(CHB_CPosEntry.get()))
        except:
            CHB_CPosEntry.delete(0,END)
            CHB_CPosEntry.insert(0, CHBCOffset)
        try:
            CHBDOffset = float(eval(CHB_DPosEntry.get()))
        except:
            CHB_DPosEntry.delete(0,END)
            CHB_DPosEntry.insert(0, CHBDOffset)        
    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    vt = HoldOff + HozPoss # invert sign and scale to mSec
    if ScreenTrefresh.get() == 0:
        # Delete all items on the screen
        de = ca.find_enclosed( -1000, -1000, CANVASwidth+1000, CANVASheight+1000)
        MarkerNum = 0
        for n in de: 
            ca.delete(n)
        # Draw horizontal grid lines
        i = 0
        x1 = X0L
        x2 = X0L + GRW
        mg_siz = GRW/10.0
        mg_inc = mg_siz/5.0
        while (i < 11):
            y = Y0T + i * GRH/10.0
            Dline = [x1,y,x2,y]
            if i == 5:
                ca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5):
                        Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                        ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
            else:
                ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())

            if (ShowC1_V.get() == 1):
                Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                #
                Vaxis_label = str(Vaxis_value)
                ca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
                
            if (ShowC2_V.get() == 1):
                Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                Vaxis_label = str(Vaxis_value)
                ca.create_text(x1-26, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", 8 ))
            if Show_MathX.get() == 1 or MathTrace.get() > 0:
                Maxis_value = 1.0 * (((5-i) * MC1pdvRange ) + MC1Offset)
                Maxis_label = str(Maxis_value)
                ca.create_text(x2+2, y, text=Maxis_label, fill=COLORtrace5, anchor="w", font=("arial", 8 ))
            if Show_MathY.get() == 1:
                Maxis_value = 1.0 * (((5-i) * MC2pdvRange ) + MC2Offset)
                Maxis_label = str(Maxis_value)
                ca.create_text(x2+28, y, text=Maxis_label, fill=COLORtrace7, anchor="w", font=("arial", 8 ))

            if MuxScreenStatus.get() == 1:
                if Show_CBA.get() == 1: 
                    Vaxis_value = (((5-i) * CHMApdvRange ) + CHBAOffset)
                    Vaxis_label = str(Vaxis_value)
                    ca.create_text(x1-26, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", 8 ))
                if Show_CBB.get() == 1: 
                    Iaxis_value = 1.0 * (((5-i) * CHMBpdvRange ) + CHBBOffset)
                    Iaxis_label = str(Iaxis_value)
                    ca.create_text(x2+2, y, text=Iaxis_label, fill=COLORtrace6, anchor="w", font=("arial", 8 ))
                if Show_CBC.get() == 1: #
                    Iaxis_value = 1.0 * (((5-i) * CHMCpdvRange ) + CHBCOffset)
                    Iaxis_label = str(Iaxis_value)
                    ca.create_text(x2+21, y, text=Iaxis_label, fill=COLORtrace7, anchor="w", font=("arial", 8 ))
                if Show_CBD.get() == 1:
                    Iaxis_value = 1.0 * (((5-i) * CHMDpdvRange ) + CHBDOffset)
                    Iaxis_label = str(Iaxis_value)
                    ca.create_text(x2+38, y, text=Iaxis_label, fill=COLORtrace4, anchor="w", font=("arial", 8 ))
            i = i + 1
        # Draw vertical grid lines
        i = 0
        y1 = Y0T
        y2 = Y0T + GRH
        mg_siz = GRH/10.0
        mg_inc = mg_siz/5.0
        vx = TIMEdiv
        while (i < 11):
            x = X0L + i * GRW/10.0
            Dline = [x,y1,x,y2]
            if (i == 5):
                ca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue vertical line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5):
                        Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                        ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
    #
                if vx >= 1000:
                    axis_value = ((i * vx)+ vt) / 1000
                    axis_label = str(int(axis_value)) + " S"
                if vx < 1000 and vx >= 1:
                    axis_value = (i * vx) + vt
                    axis_label = str(int(axis_value)) + " mS"
                if vx < 1:
                    axis_value = ((i * vx) + vt) * 1000
                    axis_label = ' {0:.2f} '.format(axis_value) + " uS"
                ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
            else:
                ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                if vx >= 1000:
                    axis_value = ((i * vx)+ vt) / 1000
                    axis_label = str(int(axis_value)) + " S"
                if vx < 1000 and vx >= 1:
                    axis_value = (i * vx) + vt
                    axis_label = str(int(axis_value)) + " mS"
                if vx < 1:
                    axis_value = ((i * vx) + vt) * 1000
                    axis_label = ' {0:.2f} '.format(axis_value) + " uS"
                ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
                        
            i = i + 1
    # Write the trigger line if available
    if len(Triggerline) > 2:                    # Avoid writing lines with 1 coordinate
        ca.create_polygon(Triggerline, outline=COLORtrigger, fill=COLORtrigger, width=1)
        ca.create_line(Triggersymbol, fill=COLORtrigger, width=GridWidth.get())
        if TgInput.get() == 1:
            TgLabel = "C1-V"
        if TgInput.get() == 3:
            TgLabel = "C2-V"
        if Is_Triggered == 1:
            TgLabel = TgLabel + " Triggered"
        else:
            TgLabel = TgLabel + " Not Triggered"
        x = X0L + (GRW/2) + 12
        ca.create_text(x, Ymin-8, text=TgLabel, fill=COLORtrigger, anchor="w", font=("arial", 8 ))
    # Draw T - V Cursor lines if required
    if MarkerScale.get() == 1:
        Yconv1 = float(GRH/10) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORmarker = COLORtrace1
        Units = " V"
    if MarkerScale.get() == 2:
        Yconv1 = float(GRH/10) / CH2pdvRange
        Yoffset1 = CHBOffset
        COLORmarker = COLORtrace2
        Units = " V"
    if MarkerScale.get() == 3:
        Yconv1 = float(GRH/10) / MC1pdvRange
        Yoffset1 = MC2Offset
        COLORmarker = COLORtrace5
        Units = MathXUnits
    if MarkerScale.get() == 4:
        Yconv1 = float(GRH/10) / MC2pdvRange
        Yoffset1 = MC2Offset
        COLORmarker = COLORtrace7
        Units = MathYUnits
#
    if ShowTCur.get() > 0:
        Dline = [TCursor, Y0T, TCursor, Y0T+GRH]
        ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
        DISsamples = (10.0 * TIMEdiv) # grid width in time 
        Tstep = DISsamples / GRW # time in mS per pixel
        Tpoint = ((TCursor-X0L) * Tstep) + vt
        if Tpoint >= 1000:
            V_label = '{0:.2f} '.format(Tpoint/1000.0) + " S"
        if Tpoint < 1000 and Tpoint >= 1:
            V_label = '{0:.2f} '.format(Tpoint) + " mS"
        if Tpoint < 1 and Tpoint >= 0.1:
            V_label = '{0:.3f} '.format(Tpoint) + " mS"
        if Tpoint < 0.1 and Tpoint >= 0.01:
            V_label = '{0:.2f} '.format(Tpoint*1000) + " uS"
        if Tpoint < 0.01 and Tpoint >= 0.001:
            V_label = '{0:.3f} '.format(Tpoint*1000) + " uS"
        if Tpoint < 0.001:
            V_label = '{0:.2f} '.format(Tpoint*1000000) + " nS"
        ca.create_text(TCursor+1, VCursor-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
    if ShowVCur.get() > 0:
        Dline = [X0L, VCursor, X0L+GRW, VCursor]
        ca.create_line(Dline, dash=(4,3), fill=COLORmarker, width=GridWidth.get())
        c1 = GRH / 2 + Y0T    # fixed Y correction 
        yvolts = ((VCursor-c1)/Yconv1) - Yoffset1
        V1String = ' {0:.3f} '.format(-yvolts)
        V_label = V1String + Units
        ca.create_text(TCursor+1, VCursor+5, text=V_label, fill=COLORmarker, anchor="w", font=("arial", 8 ))
    if ShowTCur.get() == 0 and ShowVCur.get() == 0 and MouseWidget == ca:
        if MouseX > X0L and MouseX < X0L+GRW and MouseY > Y0T and MouseY < Y0T+GRH:
            Dline = [MouseX, Y0T, MouseX, Y0T+GRH]
            ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            DISsamples = (10.0 * TIMEdiv) # grid width in time 
            Tstep = DISsamples / GRW # time in mS per pixel
            Tpoint = ((MouseX-X0L) * Tstep) + vt
            if Tpoint >= 1000:
                V_label = '{0:.2f} '.format(Tpoint/1000.0) + " S"
            if Tpoint < 1000 and Tpoint >= 1:
                V_label = '{0:.2f} '.format(Tpoint) + " mS"
            if Tpoint < 1 and Tpoint >= 0.1:
                V_label = '{0:.3f} '.format(Tpoint) + " mS"
            if Tpoint < 0.1 and Tpoint >= 0.01:
                V_label = '{0:.2f} '.format(Tpoint*1000) + " uS"
            if Tpoint < 0.01 and Tpoint >= 0.001:
                V_label = '{0:.3f} '.format(Tpoint*1000) + " uS"
            if Tpoint < 0.001:
                V_label = '{0:.2f} '.format(Tpoint*1000000) + " nS"
            ca.create_text(MouseX+1, MouseY-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
            Dline = [X0L, MouseY, X0L+GRW, MouseY]
            ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            c1 = GRH / 2 + Y0T    # fixed Y correction 
            yvolts = ((MouseY-c1)/Yconv1) - Yoffset1
            V1String = ' {0:.3f} '.format(-yvolts)
            V_label = V1String + Units
            ca.create_text(MouseX+1, MouseY+5, text=V_label, fill=COLORmarker, anchor="w", font=("arial", 8 ))
#
    SmoothBool = SmoothCurves.get()
    # Write the traces if available
    if len(T1Vline) > 4: # Avoid writing lines with 1 coordinate    
        ca.create_line(T1Vline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())   # Write the voltage trace 1
    if len(T2Vline) > 4: # Write the trace 2 if active
        ca.create_line(T2Vline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(Tmathline) > 4 and MathTrace.get() > 0: # Write Math tace if active
        ca.create_line(Tmathline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TMXline) > 4 : # Write X Math tace if active
        ca.create_line(TMXline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TMYline) > 4 : # Write Y Math tace if active
        ca.create_line(TMYline, fill=COLORtrace7, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if MuxScreenStatus.get() == 1:
        if len(TMAVline) > 4:  # Avoid writing lines with 1 coordinate    
            ca.create_line(TMAVline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if len(TMBVline) > 4: # Avoid writing lines with 1 coordinate    
            ca.create_line(TMBVline, fill=COLORtrace6, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if len(TMCVline) > 4: # Avoid writing lines with 1 coordinate    
            ca.create_line(TMCVline, fill=COLORtrace7, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if len(TMDVline) > 4: # Avoid writing lines with 1 coordinate    
            ca.create_line(TMDVline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowRB_V.get() == 1 and len(TMBRline) > 4:
            ca.create_line(TMBRline, fill=COLORtraceR6, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRA_V.get() == 1 and len(T1VRline) > 4:
        ca.create_line(T1VRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRB_V.get() == 1 and len(T2VRline) > 4:
        ca.create_line(T2VRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMath.get() == 1 and len(TMRline) > 4:
        ca.create_line(TMRline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())

    # General information on top of the grid
    # Sweep information
    if (RUNstatus.get() == 0) or (RUNstatus.get() == 3):
        sttxt = "Stopped"
    else:
        sttxt = "Running"
    if SingleShot.get() == 1:
        sttxt = "Single Shot"
    if TRACEmodeTime.get() == 1:
        sttxt = sttxt + " Averaging"
    if ScreenTrefresh.get() == 1:
        sttxt = sttxt + " Persistance ON"
        # Delete text at bottom of screen
        de = ca.find_enclosed( X0L-1, Y0T+GRH+12, CANVASwidth, Y0T+GRH+100)
        for n in de: 
            ca.delete(n)
        # Delete text at top of screen
        de = ca.find_enclosed( X0L-1, -1, CANVASwidth, 20)
        for n in de: 
            ca.delete(n)
    if SAMPLErate >= 1000000:
        SR_string = str(int(SAMPLErate/1000000)) + " MSPS"
    else:
        SR_string = str(int(SAMPLErate/1000)) + " KSPS"
    txt = "Device ID " + DevID[17:31] + " Sample rate: " + SR_string + " Buffer:" + str(SHOWsamples) + " " + sttxt
    x = X0L-38
    y = 12
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    # digital I/O indicators
    x2 = X0L + GRW
    BoxColor = "#808080"   # gray
    if DigScreenStatus.get() == 1 or MuxScreenStatus.get() == 1:
        if D0.get() == -1:
            Dval = Dig0.attrs["raw"].value
            if Dval == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval == '0':
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-12, 6, x2, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-12, 6, x2, 18, fill="yellow")
        if D1.get() == -1:
            Dval = Dig1.attrs["raw"].value
            if Dval == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval == '0':
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-26, 6, x2-14, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-26, 6, x2-14, 18, fill="yellow")
        if D2.get() == -1:
            Dval = Dig2.attrs["raw"].value
            if Dval == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval == '0':
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-40, 6, x2-28, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-40, 6, x2-28, 18, fill="yellow")
        if D3.get() == -1:
            Dval = Dig3.attrs["raw"].value
            if Dval == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval == '0':
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-54, 6, x2-42, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-54, 6, x2-42, 18, fill="yellow")
        ca.create_text(x2-56, 12, text="Digital Inputs", anchor=E, fill=COLORtext)
    # Time sweep information and view at information
    vx = TIMEdiv
    if vx >= 1000:
        txt = str(int(vx/1000)) + " S/div"
    if vx < 1000 and vx >= 1:
        txt = str(int(vx)) + " mS/div"
    if vx < 1 and vx >= 0.001:
        txt = str(int(vx * 1000)) + " uS/div"
    if vx < 0.001:
        txt = str(int(vx * 1000000)) + " nS/div"

    txt = txt + "  "
    #
    vt = HoldOff + HozPoss # invert sign and scale to mSec
    txt = txt + "View at "
    if abs(vt) >= 1000:
        txt = txt + str(vt / 1000) + " S "
    if abs(vt) < 1000 and abs(vt) >= 1:
        txt = txt + str(vt) + " mS "
    if abs(vt) < 1:
        txt = txt + str(vt * 1000) + " uS "
    # print period and frequency of displayed channels
    V_label = " "
    if ShowC1_V.get() == 1 or ShowC2_V.get() == 1:
        FindRisingEdge()
        if ShowC1_V.get() == 1:
            if MeasAHW.get() == 1:
                txt = txt + " C1 Hi Width = "
                if CHAHW >= 1000:
                    V_label = '{0:.2f} '.format(CHAHW/1000.0) + " S "
                if CHAHW < 1000 and CHAHW >= 1:
                    V_label = '{0:.2f} '.format(CHAHW) + " mS "
                if CHAHW < 1 and CHAHW >= 0.1:
                    V_label = '{0:.3f} '.format(CHAHW) + " mS "
                if CHAHW < 0.1 and CHAHW >= 0.01:
                    V_label = '{0:.2f} '.format(CHAHW*1000) + " uS "
                if CHAHW < 0.01 and CHAHW >= 0.001:
                    V_label = '{0:.3f} '.format(CHAHW*1000) + " uS "
                if CHAHW< 0.001:
                    V_label = '{0:.2f} '.format(CHAHW*1000000) + " nS "
                txt = txt + V_label
            if MeasALW.get() == 1:
                txt = txt + " C1 Lo Width = "
                if CHALW >= 1000:
                    V_label = '{0:.2f} '.format(CHALW/1000.0) + " S "
                if CHALW < 1000 and CHALW >= 1:
                    V_label = '{0:.2f} '.format(CHALW) + " mS "
                if CHALW < 1 and CHALW >= 0.1:
                    V_label = '{0:.3f} '.format(CHALW) + " mS "
                if CHALW < 0.1 and CHALW >= 0.01:
                    V_label = '{0:.2f} '.format(CHALW*1000) + " uS "
                if CHALW < 0.01 and CHALW >= 0.001:
                    V_label = '{0:.3f} '.format(CHALW*1000) + " uS "
                if CHALW< 0.001:
                    V_label = '{0:.2f} '.format(CHALW*1000000) + " nS "
                txt = txt + V_label
            if MeasADCy.get() == 1:
                txt = txt + " C1 DutyCycle = "
                V1String = ' {0:.1f} '.format(CHADCy)
                txt = txt + str(V1String) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " C1 Period = "
                if CHAperiod >= 1000:
                    V_label = '{0:.2f} '.format(CHAperiod/1000.0) + " S "
                if CHAperiod < 1000 and CHAperiod >= 1:
                    V_label = '{0:.2f} '.format(CHAperiod) + " mS "
                if CHAperiod < 1 and CHAperiod >= 0.1:
                    V_label = '{0:.3f} '.format(CHAperiod) + " mS "
                if CHAperiod < 0.1 and CHAperiod >= 0.01:
                    V_label = '{0:.2f} '.format(CHAperiod*1000) + " uS "
                if CHAperiod < 0.01 and CHAperiod >= 0.001:
                    V_label = '{0:.3f} '.format(CHAperiod*1000) + " uS "
                if CHAperiod < 0.001:
                    V_label = '{0:.2f} '.format(CHAperiod*1000000) + " nS "
                txt = txt + V_label
            if MeasAFREQ.get() == 1:
                txt = txt + " C1 Freq = "
                if CHAfreq >= 1000000:
                    V1String = ' {0:.3f} '.format(CHAfreq/1000000.0)
                    txt = txt + str(V1String) + " MHz"
                elif CHAfreq >= 1000:
                    V1String = ' {0:.3f} '.format(CHAfreq/1000.0)
                    txt = txt + str(V1String)+ " KHz" 
                else:
                    V1String = ' {0:.1f} '.format(CHAfreq)
                    txt = txt + str(V1String) + " Hz "
        if ShowC2_V.get() == 1:
            if MeasBHW.get() == 1:
                txt = txt + " C2 Hi Width = "
                if CHBHW >= 1000:
                    V_label = '{0:.2f} '.format(CHBHW/1000.0) + " S "
                if CHBHW < 1000 and CHBHW >= 1:
                    V_label = '{0:.2f} '.format(CHBHW) + " mS "
                if CHBHW < 1 and CHBHW >= 0.1:
                    V_label = '{0:.3f} '.format(CHBHW) + " mS "
                if CHBHW < 0.1 and CHBHW >= 0.01:
                    V_label = '{0:.2f} '.format(CHBHW*1000) + " uS "
                if CHBHW < 0.01 and CHBHW >= 0.001:
                    V_label = '{0:.3f} '.format(CHBHW*1000) + " uS "
                if CHBHW< 0.001:
                    V_label = '{0:.2f} '.format(CHBHW*1000000) + " nS "
                txt = txt + V_label
            if MeasBLW.get() == 1:
                txt = txt + " C2 Lo Width = "
                if CHBLW >= 1000:
                    V_label = '{0:.2f} '.format(CHBLW/1000.0) + " S "
                if CHBLW < 1000 and CHBLW >= 1:
                    V_label = '{0:.2f} '.format(CHBLW) + " mS "
                if CHBLW < 1 and CHBLW >= 0.1:
                    V_label = '{0:.3f} '.format(CHBLW) + " mS "
                if CHBLW < 0.1 and CHBLW >= 0.01:
                    V_label = '{0:.2f} '.format(CHBLW*1000) + " uS "
                if CHBLW < 0.01 and CHBLW >= 0.001:
                    V_label = '{0:.3f} '.format(CHBLW*1000) + " uS "
                if CHBLW< 0.001:
                    V_label = '{0:.2f} '.format(CHBLW*1000000) + " nS "
                txt = txt + V_label
            if MeasBDCy.get() == 1:
                txt = txt + " C2 DutyCycle = "
                V1String = ' {0:.1f} '.format(CHBDCy)
                txt = txt + str(V1String) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " C2 Period = "
                if CHBperiod >= 1000:
                    V_label = '{0:.2f} '.format(CHBperiod/1000.0) + " S "
                if CHBperiod < 1000 and CHBperiod >= 1:
                    V_label = '{0:.2f} '.format(CHBperiod) + " mS "
                if CHBperiod < 1 and CHBperiod >= 0.1:
                    V_label = '{0:.3f} '.format(CHBperiod) + " mS "
                if CHBperiod < 0.1 and CHBperiod >= 0.01:
                    V_label = '{0:.2f} '.format(CHBperiod*1000) + " uS "
                if CHBperiod < 0.01 and CHBperiod >= 0.001:
                    V_label = '{0:.3f} '.format(CHBperiod*1000) + " uS "
                if CHBperiod < 0.001:
                    V_label = '{0:.2f} '.format(CHBperiod*1000000) + " nS "
                txt = txt + V_label
            if MeasBFREQ.get() == 1:
                txt = txt + " C2 Freq = "
                if CHBfreq >= 1000000:
                    V1String = ' {0:.3f} '.format(CHBfreq/1000000.0)
                    txt = txt + str(V1String) + " MHz"
                elif CHBfreq >= 1000:
                    V1String = ' {0:.3f} '.format(CHBfreq/1000.0)
                    txt = txt + str(V1String)+ " KHz" 
                else:
                    V1String = ' {0:.1f} '.format(CHBfreq)
                    txt = txt + str(V1String) + " Hz "
        if MeasPhase.get() == 1:
            txt = txt + " C1-2 Phase = "
            V1String = ' {0:.1f} '.format(CHABphase)
            txt = txt + str(V1String) + " deg "
        if MeasDelay.get() == 1:
            txt = txt + " C2-1 Delay = "
            if CHBADelayR1 >= 1000:
                V_label = '{0:.2f} '.format(CHBADelayR1/1000.0) + " S "
            if CHBADelayR1 < 1000 and CHBADelayR1 >= 1:
                V_label = '{0:.2f} '.format(CHBADelayR1) + " mS "
            if CHBADelayR1 < 1 and CHBADelayR1 >= 0.1:
                V_label = '{0:.3f} '.format(CHBADelayR1) + " mS "
            if CHBADelayR1 < 0.1 and CHBADelayR1 >= 0.01:
                V_label = '{0:.2f} '.format(CHBADelayR1*1000) + " uS "
            if CHBADelayR1 < 0.01 and CHBADelayR1 >= 0.001:
                V_label = '{0:.3f} '.format(CHBADelayR1*1000) + " uS "
            if CHBADelayR1 < 0.001:
                V_label = '{0:.2f} '.format(CHBADelayR1*1000000) + " nS "
            txt = txt + V_label
         
    x = X0L-38
    y = Y0T+GRH+20
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    if MeasTopV1.get() == 1 or MeasBaseV1.get() == 1 or MeasTopV2.get() == 1 or MeasBaseV2.get() == 1:
        MakeHistogram()
    txt = " "
    if ShowC1_V.get() == 1:
    # Channel 1 information
        txt = "CH1: "
        txt = txt + str(CH1pdvRange) + " V/div"
        if MeasDCV1.get() == 1:
            V1String = ' {0:.4f} '.format(DCV1)
            txt = txt + " AvgV = " + V1String
        if MeasMaxV1.get() == 1:
            V1String = ' {0:.4f} '.format(MaxV1)
            txt = txt +  " MaxV = " + V1String
        if MeasTopV1.get() == 1:
            V1String = ' {0:.4f} '.format(VATop)
            txt = txt +  " Top = " + V1String
        if MeasMinV1.get() == 1:
            V1String = ' {0:.4f} '.format(MinV1)
            txt = txt +  " MinV = " + V1String
        if MeasBaseV1.get() == 1:
            V1String = ' {0:.4f} '.format(VABase)
            txt = txt +  " Base = " + V1String
        if MeasMidV1.get() == 1:
            MidV1 = (MaxV1+MinV1)/2
            V1String = ' {0:.4f} '.format(MidV1)
            txt = txt +  " MidV = " + V1String
        if MeasPPV1.get() == 1:
            PPV1 = MaxV1-MinV1
            V1String = ' {0:.4f} '.format(PPV1)
            txt = txt +  " P-PV = " + V1String
        if MeasRMSV1.get() == 1:
            V1String = ' {0:.4f} '.format(SV1)
            txt = txt +  " RMS = " + V1String
        if MeasRMSVA_B.get() == 1:
            V1String = ' {0:.4f} '.format(SVA_B)
            txt = txt +  " 1-2 RMS = " + V1String
        if MeasDiffAB.get() == 1:
            V1String = ' {0:.4f} '.format(DCV1-DCV2)
            txt = txt +  " C1-C2 = " + V1String
        if MeasUserA.get() == 1:
            try:
                TempValue = eval(UserAString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserALabel + " = " + V1String

    x = X0L-38
    y = Y0T+GRH+32
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    txt= " "
    # Channel B information
    if MuxScreenStatus.get() == 1:
        txt = "CH2-Mux: "
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String
    if ShowC2_V.get() == 1:
        txt = "CH2: "
        txt = txt + str(CH2pdvRange) + " V/div"
        if MeasDCV2.get() == 1:
            V1String = ' {0:.4f} '.format(DCV2)
            txt = txt + " AvgV = " + V1String
        if MeasMaxV2.get() == 1:
            V1String = ' {0:.4f} '.format(MaxV2)
            txt = txt +  " MaxV = " + V1String
        if MeasTopV2.get() == 1:
            V1String = ' {0:.4f} '.format(VBTop)
            txt = txt +  " Top = " + V1String
        if MeasMinV2.get() == 1:
            V1String = ' {0:.4f} '.format(MinV2)
            txt = txt +  " MinV = " + V1String
        if MeasBaseV2.get() == 1:
            V1String = ' {0:.4f} '.format(VBBase)
            txt = txt +  " Base = " + V1String
        if MeasMidV2.get() == 1:
            MidV2 = (MaxV2+MinV2)/2
            V1String = ' {0:.4f} '.format(MidV2)
            txt = txt +  " MidV = " + V1String
        if MeasPPV2.get() == 1:
            PPV2 = MaxV2-MinV2
            V1String = ' {0:.4f} '.format(PPV2)
            txt = txt +  " P-PV = " + V1String
        if MeasRMSV2.get() == 1:
            V1String = ' {0:.4f} '.format(SV2)
            txt = txt +  " RMS = " + V1String
        if MeasDiffBA.get() == 1:
            V1String = ' {0:.4f} '.format(DCV2-DCV1)
            txt = txt +  " C2-C1 = " + V1String
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String
#
    x = X0L-38
    y = Y0T+GRH+44
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
#
def MakeXYScreen():
    global TXYline # active trave lines
    global Tmathline, TMRline, TXYRline
    global X0LXY        # Left top X value
    global Y0TXY        # Left top Y value
    global GRWXY        # Screenwidth
    global GRHXY        # Screenheight
    global Ymin, Ymax, XYca, MouseX, MouseY, MouseWidget
    global ShowXCur, ShowYCur, XCursor, YCursor
    global SHOWsamples  # Number of samples in data record
    global ShowRXY, ShowMath, MathUnits, MathXUnits, MathYUnits
    global Xsignal, Ysignal
    global RUNstatus, SingleShot    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global CHAsbxy      # spinbox Index for channel 1 V
    global CHBsbxy      # spinbox Index for channel 2 V
    global CHAOffset    # Offset value for channel 1 V
    global CHBOffset    # Offset value for channel 2 V 
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate
    global TRIGGERsample, TRIGGERlevel, HoldOff, HoldOffentry
    global COLORgrid, COLORzeroline, COLORtext, COLORtrigger, COLORtrace7 # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5
    global COLORtraceR1, COLORtraceR2, COLORtraceR3, COLORtraceR4, COLORtraceR5
    global CANVASwidthXY, CANVASheightXY
    global TRACErefresh, TRACEmode, TRACEwidth, GridWidth
    global ScreenXYrefresh, SmoothCurves
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2, CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
    global SV1, SV2, CHABphase
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasRMSV1, MeasRMSV2, MeasPhase
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global AWGAShape, AWGBShape
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntryxy, CHAVPosEntryxy
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global DigScreenStatus
    global Dig0, Dig1, Dig2, Dig3, Dig4, Dig5, Dig6, Dig7, logic, ctx
    global Dig10, Dig11, Dig12, Dig13, Dig14, Dig15, Dig8, Dig9
    global D0, D1, D2, D3, D4, D5, D6, D7
    global DevID, MarkerXYNum, MarkerXYScale
    global HozPoss, HozPossentry
    global MC1sbxy, MC2sbxy, MC1VPosEntryxy, MC2VPosEntryxy
    global HistAsPercent, VBuffA, VBuffB, HBuffA, HBuffB, VFilterA, VFilterB
    global VABase, VATop, VBBase, VBTop, UserALabel, UserAString, UserBLabel, UserBString
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasUserA, MeasUserB
    # m1k dev info
    try:
        InOffA = float(eval(CHAVOffsetEntry.get()))
    except:
        CHAVOffsetEntry.delete(0,END)
        CHAVOffsetEntry.insert(0, InOffA)
    try:
        InGainA = float(eval(CHAVGainEntry.get()))
    except:
        CHAVGainEntry.delete(0,END)
        CHAVGainEntry.insert(0, InGainA)
    try:
        InOffB = float(eval(CHBVOffsetEntry.get()))
    except:
        CHBVOffsetEntry.delete(0,END)
        CHBVOffsetEntry.insert(0, InOffB)
    try:
        InGainB = float(eval(CHBVGainEntry.get()))
    except:
        CHBVGainEntry.delete(0,END)
        CHBVGainEntry.insert(0, InGainB)
#
    try:
        CH1pdvRange = float(eval(CHAsbxy.get()))
    except:
        CHAsbxy.delete(0,END)
        CHAsbxy.insert(0, CH1vpdvRange)
    try:
        CH2pdvRange = float(eval(CHBsbxy.get()))
    except:
        CHBsbxy.delete(0,END)
        CHBsbxy.insert(0, CH2vpdvRange)
    try:
        MC1pdvRange = float(eval(MC1sbxy.get()))
    except:
        MC1sbxy.delete(0,END)
        MC1sb.insert(0, MC1vpdvRange)
    try:
        MC2pdvRange = float(eval(MC2sbxy.get()))
    except:
        MC2sbxy.delete(0,END)
        MC2sbxy.insert(0, MC2vpdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntryxy.get()))
    except:
        CHAVPosEntryxy.delete(0,END)
        CHAVPosEntryxy.insert(0, CHAOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntryxy.get()))
    except:
        CHBVPosEntryxy.delete(0,END)
        CHBVPosEntryxy.insert(0, CHBOffset)
    try:
        MC1Offset = float(eval(MC1VPosEntryxy.get()))
    except:
        MC1VPosEntryxy.delete(0,END)
        MC1VPosEntryxy.insert(0, MC1Offset)
    try:
        MC2Offset = float(eval(MC2VPosEntryxy.get()))
    except:
        MC2VPosEntryxy.delete(0,END)
        MC2VPosEntryxy.insert(0, MC2Offset)
    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    # If drawing histograms adjust offset based on range such that bottom grid is zero
    if  Xsignal.get() == 6:
        MC1Offset = 5 * MC1pdvRange
    if  Xsignal.get() == 7:
        MC2Offset = 5 * MC2pdvRange
    if ScreenXYrefresh.get() == 0:
        # Delete all items on the screen
        de = XYca.find_enclosed( -1000, -1000, CANVASwidthXY+1000, CANVASheightXY+1000)
        MarkerXYNum = 0
        for n in de: 
            XYca.delete(n)
        # Draw horizontal grid lines
        i = 0
        x1 = X0LXY
        x2 = X0LXY + GRWXY
        mg_siz = GRWXY/10.0
        mg_inc = mg_siz/5.0
        while (i < 11):
            y = Y0TXY + i * GRHXY/10.0
            Dline = [x1,y,x2,y]
            if i == 5:
                XYca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5): # make tick marks
                        Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                        XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
            else:
                XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            if Xsignal.get() == 6:
                Iaxis_value = 1.0 * (((5-i) * MC1pdvRange ) + MC1Offset)
                Iaxis_label = str(Iaxis_value)
                XYca.create_text(x1-3, y, text=Iaxis_label, fill=COLORtrace5, anchor="e", font=("arial", 8 ))
            elif Xsignal.get() == 7:
                Iaxis_value = 1.0 * (((5-i) * MC2pdvRange ) + MC2Offset)
                Iaxis_label = str(Iaxis_value)
                XYca.create_text(x1-3, y, text=Iaxis_label, fill=COLORtrace7, anchor="e", font=("arial", 8 ))
            elif Ysignal.get() == 1:
                Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                Vaxis_label = str(Vaxis_value)
                XYca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
            elif Ysignal.get() == 3:
                Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                Vaxis_label = str(Vaxis_value)
                XYca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", 8 ))
            elif Ysignal.get() == 5:
                TempCOLOR = COLORtrace7
                if MathTrace.get() == 2:
                    Vaxis_value = (((5-i) * MC2pdvRange ) + MC2Offset)
                elif MathTrace.get() == 3:
                    Vaxis_value = (((5-i) * MC2pdvRange ) + MC2Offset)
                else:
                     Vaxis_value = (((5-i) * MC2pdvRange ) + MC2Offset)
                Vaxis_label = str(Vaxis_value)
                XYca.create_text(x1-3, y, text=Vaxis_label, fill=TempCOLOR, anchor="e", font=("arial", 8 ))
            i = i + 1
        # Draw vertical grid lines
        i = 0
        y1 = Ymin = Y0TXY
        y2 = Ymax = Y0TXY + GRHXY
        mg_siz = GRHXY/10.0
        mg_inc = mg_siz/5.0
        # 
        while (i < 11):
            x = X0LXY + i * GRWXY/10.0
            Dline = [x,y1,x,y2]
            if (i == 5):
                XYca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue vertical line at center of grid
                k = 0
                while (k < 10): # make tick marks
                    l = 1
                    while (l < 5):
                        Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                        XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
                if Xsignal.get() == 1: # 
                    Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 6:
                    Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 3:
                    Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 7:
                    Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 5:
                    TempCOLOR = COLORtrace5
                    if MathTrace.get() == 2:
                        Vaxis_value = (((i-5) * MC1pdvRange ) + MC1Offset)
                    elif MathTrace.get() == 3:
                        Vaxis_value = (((i-5) * MC1pdvRange ) + MC1Offset)
                    else:
                        Vaxis_value = (((i-5) * MC1pdvRange ) + MC1Offset)
                        TempCOLOR = COLORtrace5
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=TempCOLOR, anchor="n", font=("arial", 8 ))
            else:
                XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                if Xsignal.get() == 1:
                    Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 6:
                    Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 3:
                    Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 7:
                    Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 5:
                    TempCOLOR = COLORtrace5
                    if MathTrace.get() == 2:
                        Vaxis_value = (((i-5) * MC1pdvRange ) + MC1Offset)
                    elif MathTrace.get() == 3:
                        Vaxis_value = (((i-5) * MC1pdvRange ) + MC1Offset)
                    else:
                        Vaxis_value = (((i-5) * MC1pdvRange ) + MC1Offset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=TempCOLOR, anchor="n", font=("arial", 8 ))
            i = i + 1
# Draw traces
    if len(TXYline) > 4:                    # Avoid writing lines with 1 coordinate
        if  Xsignal.get() == 1:
            XYca.create_line(TXYline, fill=COLORtrace1, width=TRACEwidth.get())
        elif  Xsignal.get() == 3:
            XYca.create_line(TXYline, fill=COLORtrace2, width=TRACEwidth.get())
        elif  Xsignal.get() == 5 or Ysignal.get() == 5:
            XYca.create_line(TXYline, fill=COLORtrace5, width=TRACEwidth.get())
    if len(TXYRline) > 4 and ShowRXY.get() == 1:
        XYca.create_line(TXYRline, fill=COLORtraceR5, width=TRACEwidth.get())
# Draw Histogram Traces
    if  Xsignal.get() == 6:
        MakeHistogram()
        b = 0
        Yconv1 = float(GRHXY/10) / MC1pdvRange
        Xconv1 = float(GRWXY/10) / CH1pdvRange
        y1 = Y0TXY + GRHXY
        # print Yconv1, y1
        c2 = GRWXY / 2 + X0LXY   # Hor correction factor
        while b < 4999: #
            if HistAsPercent == 1: # convert to percent of total sample count
                ylo = float(HBuffA[0][b]) / len(VBuffA)
                ylo = ylo * 100.0
            else:
                ylo = HBuffA[0][b] #
            ylo = int(y1 - (Yconv1 * ylo))
            if ylo >  Ymax:
                ylo = Ymax
            if ylo < Ymin:
                ylo = Ymin
            xlo = HBuffA[1][b] - CHAOffset
            xlo = int(c2 + Xconv1 * xlo)
            Dline = [xlo,y1,xlo,ylo]
            XYca.create_line(Dline, fill=COLORtrace1)
            b = b + 1
    if  Xsignal.get() == 7:
        MakeHistogram()
        b = 0
        Yconv1 = float(GRHXY/10) / MC2pdvRange
        Xconv1 = float(GRWXY/10) / CH2pdvRange
        y1 = Y0TXY + GRHXY
        c2 = GRWXY / 2 + X0LXY   # Hor correction factor
        while b < 4999: #
            if HistAsPercent == 1: # convert to percent
                ylo = float(HBuffB[0][b]) / len(VBuffB)
                ylo = ylo * 100.0
            else:
                ylo = HBuffB[0][b]
            ylo = int(y1 - Yconv1 * ylo)
            if ylo >  Ymax:
                ylo = Ymax
            if ylo < Ymin:
                ylo = Ymin
            xlo = HBuffB[1][b] - CHBOffset
            xlo = int(c2 + Xconv1 * xlo)
            Dline = [xlo,y1,xlo,ylo]
            XYca.create_line(Dline, fill=COLORtrace2)
            b = b + 1
# Draw X - Y Cursor lines if required
    if Xsignal.get() == 1 or Xsignal.get() == 6:
        Xconv1 = float(GRWXY/10) / CH1pdvRange
        Xoffset1 = CHAOffset
        COLORXmarker = COLORtrace1
        XUnits = " V"
    if Xsignal.get() == 3 or Xsignal.get() == 7:
        Xconv1 = float(GRWXY/10) / CH2pdvRange
        Xoffset1 = CHBOffset
        COLORXmarker = COLORtrace2
        XUnits = " V"
    if Xsignal.get() == 5:
        COLORXmarker = COLORtrace5
        XUnits = MathXUnits
        Xconv1 = float(GRWXY/10) /  MC1pdvRange
        Xoffset1 = MC1Offset
#
    if Ysignal.get() == 1:
        Yconv1 = float(GRHXY/10) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORYmarker = COLORtrace1
        YUnits = " V"
    if Ysignal.get() == 3:
        Yconv1 = float(GRHXY/10) / CH2pdvRange
        Yoffset1 = CHBOffset
        COLORYmarker = COLORtrace2
        YUnits = " V"
    if Ysignal.get() == 5:
        COLORYmarker = COLORtrace7
        Yconv1 = float(GRHXY/10) /MC2pdvRange
        YUnits = MathYUnits
        Yoffset1 = MC2Offset
#
    if ShowXCur.get() > 0:
        Dline = [XCursor, Y0TXY, XCursor, Y0TXY+GRHXY]
        XYca.create_line(Dline, dash=(4,3), fill=COLORXmarker, width=GridWidth.get())
        c1 = GRWXY / 2 + X0LXY    # fixed X correction 
        xvolts = Xoffset1 - ((c1-XCursor)/Xconv1)
        XString = ' {0:.3f} '.format(xvolts)
        V_label = XString + XUnits
        XYca.create_text(XCursor+1, YCursor-5, text=V_label, fill=COLORXmarker, anchor="w", font=("arial", 8 ))
    if ShowYCur.get() > 0:
        Dline = [X0LXY, YCursor, X0LXY+GRWXY, YCursor]
        XYca.create_line(Dline, dash=(4,3), fill=COLORYmarker, width=GridWidth.get())
        c1 = GRHXY / 2 + Y0TXY    # fixed Y correction 
        yvolts = ((YCursor-c1)/Yconv1) - Yoffset1
        V1String = ' {0:.3f} '.format(-yvolts)
        V_label = V1String + YUnits
        XYca.create_text(XCursor+1, YCursor+5, text=V_label, fill=COLORYmarker, anchor="w", font=("arial", 8 ))
    if ShowXCur.get() == 0 and ShowYCur.get() == 0 and MouseWidget == XYca:
        if MouseX > X0LXY and MouseX < X0LXY+GRWXY and MouseY > Y0TXY and MouseY < Y0TXY+GRHXY:
            Dline = [MouseX, Y0TXY, MouseX, Y0TXY+GRHXY]
            XYca.create_line(Dline, dash=(4,3), fill=COLORXmarker, width=GridWidth.get())
            c1 = GRWXY / 2.0 + X0LXY    # fixed X correction 
            xvolts = Xoffset1 - ((c1-MouseX)/Xconv1)
            XString = ' {0:.3f} '.format(xvolts)
            V_label = XString + XUnits
            XYca.create_text(MouseX+1, MouseY-5, text=V_label, fill=COLORXmarker, anchor="w", font=("arial", 8 ))
            Dline = [X0LXY, MouseY, X0LXY+GRWXY, MouseY]
            XYca.create_line(Dline, dash=(4,3), fill=COLORYmarker, width=GridWidth.get())
            c1 = GRHXY / 2 + Y0TXY    # fixed Y correction 
            yvolts = ((MouseY-c1)/Yconv1) - Yoffset1
            V1String = ' {0:.3f} '.format(-yvolts)
            V_label = V1String + YUnits
            XYca.create_text(MouseX+1, MouseY+5, text=V_label, fill=COLORYmarker, anchor="w", font=("arial", 8 ))
#
# General information on top of the grid
# Sweep information
    if (RUNstatus.get() == 0) or (RUNstatus.get() == 3):
        sttxt = "Stopped"
    else:
        sttxt = "Running"
    if SingleShot.get() == 1:
        sttxt = "Single Shot"
    if TRACEmodeTime.get() == 1:
        sttxt = sttxt + " Averaging"
    if ScreenXYrefresh.get() == 1:
        sttxt = sttxt + " Persistance ON"
        # Delete text at bottom of screen
        de = XYca.find_enclosed( X0LXY-1, Y0TXY+GRHXY+19, CANVASwidthXY, Y0TXY+GRHXY+100)
        for n in de: 
            XYca.delete(n)
        # Delete text at top of screen
        de = XYca.find_enclosed( X0LXY-1, -1, CANVASwidthXY, 20)
        for n in de: 
            XYca.delete(n)
    if SAMPLErate >= 1000000:
        SR_string = str(int(SAMPLErate/1000000)) + " MSPS"
    else:
        SR_string = str(int(SAMPLErate/1000)) + " KSPS"
    txt = "Device ID " + DevID[17:31] + " Sample rate: " + SR_string + " " + sttxt
    x = X0LXY
    y = 12
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    # digital I/O indicators
    x2 = X0LXY + GRWXY
    BoxColor = "#808080"   # gray
    if DigScreenStatus.get() == 1 :
        if D0.get() == -1:
            Dval = Dig0.attrs["raw"].value
            if Dval[0] == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == '0':
                BoxColor = "#ff0000"   # 100% red
            XYca.create_rectangle(x2-12, 6, x2, 18, fill=BoxColor)
        else:
            XYca.create_rectangle(x2-12, 6, x2, 18, fill="yellow")
        if D1.get() == -1:
            Dval = Dig1.attrs["raw"].value
            if Dval[0] == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == '0':
                BoxColor = "#ff0000"   # 100% red
            XYca.create_rectangle(x2-26, 6, x2-14, 18, fill=BoxColor)
        else:
            XYca.create_rectangle(x2-26, 6, x2-14, 18, fill="yellow")
        if D2.get() == -1:
            Dval = Dig2.attrs["raw"].value
            if Dval[0] == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == '0':
                BoxColor = "#ff0000"   # 100% red
            XYca.create_rectangle(x2-40, 6, x2-28, 18, fill=BoxColor)
        else:
            XYca.create_rectangle(x2-40, 6, x2-28, 18, fill="yellow")
        if D3.get() == -1:
            Dval = Dig3.attrs["raw"].value
            if Dval[0] == '1':
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == '0':
                BoxColor = "#ff0000"   # 100% red
            XYca.create_rectangle(x2-54, 6, x2-42, 18, fill=BoxColor)
        else:
            XYca.create_rectangle(x2-54, 6, x2-42, 18, fill="yellow")
        XYca.create_text(x2-56, 12, text="Digital Inputs", anchor=E, fill=COLORtext)
    # print period and frequency of displayed channels
    txt = " "
    if Xsignal.get() == 1 or Xsignal.get() == 3:
        FindRisingEdge()
        if Xsignal.get() == 1:
            if MeasAHW.get() == 1:
                txt = txt + " C1 Hi Width = "
                V1String = ' {0:.2f} '.format(CHAHW)
                txt = txt + str(V1String) + " mS "
            if MeasALW.get() == 1:
                txt = txt + " C1 Lo Width = "
                V1String = ' {0:.2f} '.format(CHALW)
                txt = txt + str(V1String) + " mS "
            if MeasADCy.get() == 1:
                txt = txt + " C1 DutyCycle = "
                V1String = ' {0:.1f} '.format(CHADCy)
                txt = txt + str(V1String) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " C1 Period = "
                V1String = ' {0:.2f} '.format(CHAperiod)
                txt = txt + str(V1String) + " mS "
            if MeasAFREQ.get() == 1:
                txt = txt + " C1 Freq = "
                V1String = ' {0:.1f} '.format(CHAfreq)
                txt = txt + str(V1String) + " Hz "
        if Xsignal.get() == 3:
            if MeasBHW.get() == 1:
                txt = txt + " C2 Hi Width = "
                V1String = ' {0:.2f} '.format(CHBHW)
                txt = txt + str(V1String) + " mS "
            if MeasBLW.get() == 1:
                txt = txt + " C2 Lo Width = "
                V1String = ' {0:.2f} '.format(CHBLW)
                txt = txt + str(V1String) + " mS "
            if MeasBDCy.get() == 1:
                txt = txt + " C2 DutyCycle = "
                V1String = ' {0:.1f} '.format(CHBDCy)
                txt = txt + str(V1String) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " C2 Period = "
                V1String = ' {0:.2f} '.format(CHBperiod)
                txt = txt + str(V1String) + " mS "
            if MeasBFREQ.get() == 1:
                txt = txt + " C2 Freq = "
                V1String = ' {0:.1f} '.format(CHBfreq)
                txt = txt + str(V1String) + " Hz "
        if MeasPhase.get() == 1:
            txt = txt + " C1-2 Phase = "
            V1String = ' {0:.1f} '.format(CHABphase)
            txt = txt + str(V1String) + " deg "
            
    x = X0LXY
    y = Y0TXY+GRHXY+20
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    txt = " "
    if Xsignal.get() == 1 or Ysignal.get() == 1 or Xsignal.get() == 6:
    # Channel 1 information
        txt = "CH1: "
        txt = txt + str(CH1pdvRange) + " V/div"
        if MeasDCV1.get() == 1:
            V1String = ' {0:.4f} '.format(DCV1)
            txt = txt + " AvgV = " + V1String
        if MeasMaxV1.get() == 1:
            V1String = ' {0:.4f} '.format(MaxV1)
            txt = txt +  " MaxV = " + V1String
        if MeasTopV1.get() == 1:
            V1String = ' {0:.4f} '.format(VATop)
            txt = txt +  " Top = " + V1String
        if MeasMinV1.get() == 1:
            V1String = ' {0:.4f} '.format(MinV1)
            txt = txt +  " MinV = " + V1String
        if MeasBaseV1.get() == 1:
            V1String = ' {0:.4f} '.format(VABase)
            txt = txt +  " Top = " + V1String
        if MeasMidV1.get() == 1:
            MidV1 = (MaxV1+MinV1)/2
            V1String = ' {0:.4f} '.format(MidV1)
            txt = txt +  " MidV = " + V1String
        if MeasPPV1.get() == 1:
            PPV1 = MaxV1-MinV1
            V1String = ' {0:.4f} '.format(PPV1)
            txt = txt +  " P-PV = " + V1String
        if MeasRMSV1.get() == 1:
            V1String = ' {0:.4f} '.format(SV1)
            txt = txt +  " RMS = " + V1String
        if MeasUserA.get() == 1:
            try:
                TempValue = eval(UserAString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserALabel + " = " + V1String
        
    x = X0LXY
    y = Y0TXY+GRHXY+32
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    txt= " "
    # Channel 2 information
    if Xsignal.get() == 3 or Ysignal.get() == 3 or Xsignal.get() == 7:
        txt = "CH2: "
        txt = txt + str(CH2pdvRange) + " V/div"
        if MeasDCV2.get() == 1:
            V1String = ' {0:.4f} '.format(DCV2)
            txt = txt + " AvgV = " + V1String
        if MeasMaxV2.get() == 1:
            V1String = ' {0:.4f} '.format(MaxV2)
            txt = txt +  " MaxV = " + V1String
        if MeasTopV2.get() == 1:
            V1String = ' {0:.4f} '.format(VBTop)
            txt = txt +  " Top = " + V1String
        if MeasMinV2.get() == 1:
            V1String = ' {0:.4f} '.format(MinV2)
            txt = txt +  " MinV = " + V1String
        if MeasBaseV2.get() == 1:
            V1String = ' {0:.4f} '.format(VBBase)
            txt = txt +  " Top = " + V1String
        if MeasMidV2.get() == 1:
            MidV2 = (MaxV2+MinV2)/2
            V1String = ' {0:.4f} '.format(MidV2)
            txt = txt +  " MidV = " + V1String
        if MeasPPV2.get() == 1:
            PPV2 = MaxV2-MinV2
            V1String = ' {0:.4f} '.format(PPV2)
            txt = txt +  " P-PV = " + V1String
        if MeasRMSV2.get() == 1:
            V1String = ' {0:.4f} '.format(SV2)
            txt = txt +  " RMS = " + V1String
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String
            
    x = X0LXY
    y = Y0TXY+GRHXY+44
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
#
def SetScaleA():
    global MarkerScale, CHAlab, CHBlab, MC1lab, MC2lab

    MarkerScale.set(1)
    CHAlab.config(style="Rtrace1.TButton")
    CHBlab.config(style="Strace2.TButton")
    MC1lab.config(style="Strace5.TButton")
    MC2lab.config(style="Strace7.TButton")
#
def SetScaleMC1():
    global MarkerScale, CHAlab, CHBlab, MC1lab, MC2lab

    MarkerScale.set(3)
    MC1lab.config(style="Rtrace5.TButton")
    CHAlab.config(style="Strace1.TButton")
    CHBlab.config(style="Strace2.TButton")
    MC2lab.config(style="Strace7.TButton")
#
def SetScaleB():
    global MarkerScale, CHAlab, CHBlab, MC1lab, MC2lab

    MarkerScale.set(2)
    CHAlab.config(style="Strace1.TButton")
    CHBlab.config(style="Rtrace2.TButton")
    MC1lab.config(style="Strace5.TButton")
    MC2lab.config(style="Strace7.TButton")

def SetScaleMC2():
    global MarkerScale, CHAlab, CHBlab, MC1lab, MC2lab

    MarkerScale.set(4)
    MC2lab.config(style="Rtrace7.TButton")
    CHAlab.config(style="Strace1.TButton")
    CHBlab.config(style="Strace2.TButton")
    MC1lab.config(style="Strace5.TButton")
#
def SetXYScaleA():
    global MarkerXYScale, CHAxylab, CHBxylab, MC1labxy, MC2labxy

    MarkerXYScale.set(1)
    CHAxylab.config(style="Rtrace1.TButton")
    CHBxylab.config(style="Strace2.TButton")
    MC1labxy.config(style="Strace5.TButton")
    MC2labxy.config(style="Strace7.TButton")
#
def SetXYScaleMC1():
    global MarkerXYScale, MC1labxy, MC2labxy, CHAxylab, CHBxylab

    MarkerXYScale.set(3)
    MC1labxy.config(style="Rtrace5.TButton")
    CHAxylab.config(style="Strace1.TButton")
    CHBxylab.config(style="Strace2.TButton")
    MC2labxy.config(style="Strace7.TButton")
#
def SetXYScaleB():
    global MarkerXYScale, CHAxylab, CHBxylab, MC1labxy, MC2labxy

    MarkerXYScale.set(2)
    CHBxylab.config(style="Rtrace2.TButton")
    CHAxylab.config(style="Strace1.TButton")
    MC1labxy.config(style="Strace5.TButton")
    MC2labxy.config(style="Strace7.TButton")
#
def SetXYScaleMC2():
    global MarkerXYScale, MC1labxy, MC2labxy, CHAxylab, CHBxylab

    MarkerXYScale.set(4)
    MC2labxy.config(style="Rtrace7.TButton")
    CHAxylab.config(style="Strace1.TButton")
    CHBxylab.config(style="Strace2.TButton")
    MC1labxy.config(style="Strace5.TButton")
#
def onCanvasClickRight(event):
    global ShowTCur, ShowVCur, TCursor, VCursor, RUNstatus, ca

    TCursor = event.x
    VCursor = event.y
    if RUNstatus.get() == 0:
        UpdateTimeScreen()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
def onCanvasClickScroll(event):
    global ShowTCur, ShowVCur, TCursor, VCursor, RUNstatus, ca
    if event.widget == ca:
        if ShowTCur.get() > 0 or ShowVCur.get() > 0: # move cursors if shown
            ShiftKeyDwn = event.state & 1
            if ShowTCur.get() > 0 and ShiftKeyDwn == 0:
                TCursor = TCursor + event.delta/100
            elif ShowVCur.get() > 0 or ShiftKeyDwn == 1:
                VCursor = VCursor - event.delta/100
        else:
            try:
                onSpinBoxScroll(event) # if cursor are not showing scroll the Horx time base
            except:
                donothing()
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
#
def onCanvasUpArrow(event):
    global ShowVCur, VCursor, YCursor, dBCursor, BdBCursor, RUNstatus, ca, XYca, Freqca, Bodeca
    ShiftKeyDwn = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and ShiftKeyDwn == 0:
            VCursor = VCursor - 1
        elif ShowVCur.get() > 0 and ShiftKeyDwn == 1:
            VCursor = VCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowYCur.get() > 0 and ShiftKeyDwn == 0:
                YCursor = YCursor - 1
            elif ShowYCur.get() > 0 and ShiftKeyDwn == 1:
                YCursor = YCursor - 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowdBCur.get() > 0 and ShiftKeyDwn == 0:
                dBCursor = dBCursor - 1
            elif ShowdBCur.get() > 0 and ShiftKeyDwn == 1:
                dBCursor = dBCursor - 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBdBCur.get() > 0 and ShiftKeyDwn == 0:
                BdBCursor = BdBCursor - 1
            elif ShowBdBCur.get() > 0 and ShiftKeyDwn == 1:
                BdBCursor = BdBCursor - 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasDownArrow(event):
    global ShowVCur, VCursor, YCursor, dBCursor, BdBCursor, RUNstatus, ca, XYca, Freqca
    ShiftKeyDwn = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and ShiftKeyDwn == 0:
            VCursor = VCursor + 1
        elif ShowVCur.get() > 0 and ShiftKeyDwn == 1:
            VCursor = VCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowYCur.get() > 0 and ShiftKeyDwn == 0:
                YCursor = YCursor + 1
            elif ShowYCur.get() > 0 and ShiftKeyDwn == 1:
                YCursor = YCursor + 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowdBCur.get() > 0 and ShiftKeyDwn == 0:
                dBCursor = dBCursor + 1
            elif ShowdBCur.get() > 0 and ShiftKeyDwn == 1:
                dBCursor = dBCursor + 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBdBCur.get() > 0 and ShiftKeyDwn == 0:
                BdBCursor = BdBCursor + 1
            elif ShowBdBCur.get() > 0 and ShiftKeyDwn == 1:
                BdBCursor = BdBCursor + 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasLeftArrow(event):
    global ShowTCur, TCursor, XCursor, FCursor, BPCursor, RUNstatus, ca, XYca, Freqca
    ShiftKeyDwn = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and ShiftKeyDwn == 0:
            TCursor = TCursor - 1
        elif ShowTCur.get() > 0 and ShiftKeyDwn == 1:
            TCursor = TCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowXCur.get() > 0 and ShiftKeyDwn == 0:
                XCursor = XCursor - 1
            elif ShowXCur.get() > 0 and ShiftKeyDwn == 1:
                XCursor = XCursor - 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowFCur.get() > 0 and ShiftKeyDwn == 0:
                FCursor = FCursor - 1
            elif ShowFCur.get() > 0 and ShiftKeyDwn == 1:
                FCursor = FCursor - 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBPCur.get() > 0 and ShiftKeyDwn == 0:
                BPCursor = BPCursor - 1
            elif ShowBPCur.get() > 0 and ShiftKeyDwn == 1:
                BPCursor = BPCursor - 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasRightArrow(event):
    global ShowTCur, TCursor, XCursor, FCursor, BPCursor, RUNstatus, ca, XYca, Freqca
    ShiftKeyDwn = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and ShiftKeyDwn == 0:
            TCursor = TCursor + 1
        elif ShowTCur.get() > 0 and ShiftKeyDwn == 1:
            TCursor = TCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowXCur.get() > 0 and ShiftKeyDwn == 0:
                XCursor = XCursor + 1
            elif ShowXCur.get() > 0 and ShiftKeyDwn == 1:
                XCursor = XCursor + 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowFCur.get() > 0 and ShiftKeyDwn == 0:
                FCursor = FCursor + 1
            elif ShowFCur.get() > 0 and ShiftKeyDwn == 1:
                FCursor = FCursor + 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBPCur.get() > 0 and ShiftKeyDwn == 0:
                BPCursor = BPCursor + 1
            elif ShowBPCur.get() > 0 and ShiftKeyDwn == 1:
                BPCursor = BPCursor + 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasClickLeft(event):
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global ca, MarkerLoc
    global HoldOffentry, Xsignal, Ysignal, COLORgrid, COLORtext
    global TMsb, CHAsb, CHBsb, CHAIsb, CHBIsb, MarkerScale, HozPossentry
    global CHAVPosEntry, MC1PosEntry, CHBVPosEntry, MC2PosEntry
    global SAMPLErate, RUNstatus, MarkerNum, PrevV, PrevT, HozPoss
    global COLORtrace1, COLORtrace2, MathUnits, MathXUnits, MathYUnits
    global CH1pdvRange, CH2pdvRange, MC1pdvRange, MC2pdvRange
    global CHAOffset, MC1Offset, CHBOffset, MC2Offset
    # add markers only if stopped
    if (RUNstatus.get() == 0):
        MarkerNum = MarkerNum + 1
        # get time scale
        try:
            TIMEdiv = float(eval(TMsb.get()))
        except:
            TIMEdiv = 0.5
            TMsb.delete(0,"end")
            TMsb.insert(0,TIMEdiv)
        # prevent divide by zero error
        if TIMEdiv < 0.00005:
            TIMEdiv = 0.00005
        # get the vertical ranges
        # slide trace left right by HozPoss
        try:
            HozPoss = float(eval(HozPossentry.get()))
        except:
            HozPossentry.delete(0,END)
            HozPossentry.insert(0, HozPoss)
        try:
            CH1pdvRange = float(eval(CHAsb.get()))
        except:
            CHAsb.delete(0,END)
            CHAsb.insert(0, CH1vpdvRange)
        try:
            CH2pdvRange = float(eval(CHBsb.get()))
        except:
            CHBsb.delete(0,END)
            CHBsb.insert(0, CH2vpdvRange)
        try:
            MC1pdvRange = float(eval(MC1sb.get()))
        except:
            MC1sb.delete(0,END)
            MC1sb.insert(0, MC1vpdvRange)
        try:
            MC2pdvRange = float(eval(MC2sb.get()))
        except:
            MC2sb.delete(0,END)
            MC2sb.insert(0, MC2vpdvRange)
        # get the vertical offsets
        try:
            CHAOffset = float(eval(CHAVPosEntry.get()))
        except:
            CHAVPosEntry.delete(0,END)
            CHAVPosEntry.insert(0, CHAOffset)
        try:
            CHBOffset = float(eval(CHBVPosEntry.get()))
        except:
            CHBVPosEntry.delete(0,END)
            CHBVPosEntry.insert(0, CHBOffset)
        try:
            MC1Offset = float(eval(MC1VPosEntry.get()))
        except:
            MC1VPosEntry.delete(0,END)
            MC1VPosEntry.insert(0, MC1Offset)
        try:
            MC2Offset = float(eval(MC2VPosEntry.get()))
        except:
            MC2VPosEntry.delete(0,END)
            MC2VPosEntry.insert(0, MC2Offset)
        # prevent divide by zero error
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
        if CH2pdvRange < 0.001:
            CH2pdvRange = 0.001
        try:
            HoldOff = float(eval(HoldOffentry.get()))
            if HoldOff < 0:
                HoldOff = 0
        except:
            HoldOffentry.delete(0,END)
            HoldOffentry.insert(0, HoldOff)
#
        if MarkerScale.get() == 1:
            Yconv1 = float(GRH/10) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORmarker = COLORtrace1
            Units = " V"
        elif MarkerScale.get() == 2:
            Yconv1 = float(GRH/10) / CH2pdvRange
            Yoffset1 = CHBOffset
            COLORmarker = COLORtrace2
            Units = " V"
        elif MarkerScale.get() == 3:
            Yconv1 = float(GRH/10) / MC1pdvRange
            Yoffset1 = MC1Offset
            COLORmarker = COLORtrace5
            Units = MathXUnits
        elif MarkerScale.get() == 4:
            Yconv1 = float(GRH/10) / MC2pdvRange
            Yoffset1 = MC2Offset
            COLORmarker = COLORtrace7
            Units = MathYUnits
        else:
            Yconv1 = float(GRH/10) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORmarker = COLORtrace1
        c1 = GRH / 2 + Y0T    # fixed correction channel A
        xc1 = GRW / 2 + X0L
        c2 = GRH / 2 + Y0T    # fixed correction channel B
        # draw X at marker point and number
        ca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORmarker)
        ca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORmarker)
        DISsamples = (10.0 * TIMEdiv) # grid width in time 
        Tstep = DISsamples / GRW # time in mS per pixel
        Tpoint = ((event.x-X0L) * Tstep) + HoldOff + HozPoss
        yvolts = ((event.y-c1)/Yconv1) - Yoffset1
        if MarkerScale.get() == 1 or MarkerScale.get() == 2:
            V1String = ' {0:.3f} '.format(-yvolts)
        else:
            V1String = ' {0:.1f} '.format(-yvolts)
        if Tpoint >= 1000:
            TString = '{0:.2f} '.format(Tpoint/1000.0) + " S"
        if Tpoint < 1000 and Tpoint >= 1:
            TString = '{0:.2f} '.format(Tpoint) + " mS"
        if Tpoint < 1 and Tpoint >= 0.1:
            TString = '{0:.3f} '.format(Tpoint) + " mS"
        if Tpoint < 0.1 and Tpoint >= 0.01:
            TString = '{0:.2f} '.format(Tpoint*1000) + " uS"
        if Tpoint < 0.01 and Tpoint >= 0.001:
            TString = '{0:.3f} '.format(Tpoint*1000) + " uS"
        if Tpoint < 0.001:
            TString = '{0:.2f} '.format(Tpoint*1000000) + " nS"
        V_label = str(MarkerNum) + " " + TString + V1String + Units
        if MarkerNum > 1:
            if MarkerScale.get() == 1 or MarkerScale.get() == 2:
                DeltaV = ' {0:.3f} '.format(PrevV-yvolts)
            else:
                DeltaV = ' {0:.1f} '.format(PrevV-yvolts)
            DeltaT = Tpoint-PrevT
            if DeltaT >= 1000:
                TString = '{0:.2f} '.format(DeltaT/1000.0) + " S"
            if DeltaT < 1000 and DeltaT >= 1:
                TString = '{0:.2f} '.format(DeltaT) + " mS"
            if DeltaT < 1 and DeltaT >= 0.1:
                TString = '{0:.3f} '.format(DeltaT) + " mS"
            if DeltaT < 0.1 and DeltaT >= 0.01:
                TString = '{0:.2f} '.format(DeltaT*1000) + " uS"
            if DeltaT < 0.01 and DeltaT >= 0.001:
                TString = '{0:.3f} '.format(DeltaT*1000) + " uS"
            if DeltaT < 0.001:
                TString = '{0:.2f} '.format(DeltaT*1000000) + " nS"
            V_label = V_label + " Delta " + TString + DeltaV + Units
        # place in upper left unless specified otherwise
        x = X0L + 5
        y = Y0T + 3 + (MarkerNum*10)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0L + GRW - 5
            y = Y0T + 3 + (MarkerNum*10)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0L + 5
            y = Y0T + GRH + 3 - (MarkerNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0L + GRW - 5
            y = Y0T + GRH + 3 - (MarkerNum*10)
            Justify = 'e'
        ca.create_text(event.x+4, event.y, text=str(MarkerNum), fill=COLORmarker, anchor=Justify, font=("arial", 8 ))
        ca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", 8 ))
        PrevV = yvolts
        PrevT = Tpoint
#
def onCanvasOne(event):
    global ShowC1_V

    if ShowC1_V.get() == 0:
        ShowC1_V.set(1)
    else:
        ShowC1_V.set(0)
#
def onCanvasTwo(event):
    global ShowC2_V

    if ShowC2_V.get() == 0:
        ShowC2_V.set(1)
    else:
        ShowC2_V.set(0)
# 
def onCanvasThree(event):
    global Show_MathX

    if Show_MathX.get() == 0:
        Show_MathX.set(1)
    else:
        Show_MathX.set(0)
#
def onCanvasFour(event):
    global Show_MathY

    if Show_MathY.get() == 0:
        Show_MathY.set(1)
    else:
        Show_MathY.set(0)
#
def onCanvasFive(event):
    global MathTrace

    MathTrace.set(1)
#
def onCanvasSix(event):
    global MathTrace

    MathTrace.set(2)
# 
def onCanvasSeven(event):
    global MathTrace

    MathTrace.set(3)
#
def onCanvasEight(event):
    global MathTrace

    MathTrace.set(10)
#
def onCanvasNine(event):
    global MathTrace

    MathTrace.set(12)
#
def onCanvasZero(event):
    global MathTrace

    MathTrace.set(0)
#
def onCanvasLoopBack(event):
    global ShowLoopBack

    if ShowLoopBack.get() == 0:
        ShowLoopBack.set(1)
    else:
        ShowLoopBack.set(0)
#
def onCanvasTrising(event):
    global TgEdge

    TgEdge.set(0)
#
def onCanvasTfalling(event):
    global TgEdge

    TgEdge.set(1)
#
def onCanvasSnap(event):

    BSnapShot()
#
def onCanvasAverage(event):
    global TRACEmodeTime

    if TRACEmodeTime.get() == 0:
        TRACEmodeTime.set(1)
    else:
        TRACEmodeTime.set(0)
#
def onCanvasShowTcur(event):
    global ShowTCur

    if ShowTCur.get() == 0:
        ShowTCur.set(1)
    else:
        ShowTCur.set(0)
#
def onCanvasShowVcur(event):
    global ShowVCur

    if ShowVCur.get() == 0:
        ShowVCur.set(1)
    else:
        ShowVCur.set(0)
#
def onCanvasXYRightClick(event):
    global ShowXCur, ShowYCur, XCursor, YCursor, RUNstatus, XYca

    XCursor = event.x
    YCursor = event.y
    if RUNstatus.get() == 0:
        UpdateXYScreen()
    XYca.bind_all('<MouseWheel>', onCanvasXYScrollClick)
#
def onCanvasXYScrollClick(event):
    global ShowXCur, ShowYCur, XCursor, YCursor, RUNstatus, XYca
    if event.widget == XYca:
        ShiftKeyDwn = event.state & 1
        if ShowXCur.get() > 0 and ShiftKeyDwn == 0:
            XCursor = XCursor + event.delta/100
        elif ShowYCur.get() > 0 or ShiftKeyDwn == 1:
            YCursor = YCursor - event.delta/100
        if RUNstatus.get() == 0:
            UpdateXYScreen()
#
def onCanvasXYLeftClick(event):
    global X0LXY          # Left top X value
    global Y0TXY          # Left top Y value
    global GRWXY          # Screenwidth
    global GRHXY          # Screenheight
    global XYca, MarkerLoc
    global HoldOffentry, Xsignal, Ysignal, COLORgrid, COLORtext
    global TMsb, CHAsbxy, CHBsbxy, MarkerXYScale
    global CHAVPosEntryxy, CHBVPosEntryxy
    global SAMPLErate, RUNstatus, MarkerXYNum, MarkerXYScale, PrevX, PrevY
    global COLORtrace1, COLORtrace2, MathUnits, MathXUnits, MathYUnits
    global CH1pdvRange, CH2pdvRange
    global CHAOffset, CHBOffset
    # add markers only if stopped
    # 
    if (RUNstatus.get() == 0):
        MarkerXYNum = MarkerXYNum + 1
        try:
            CH1pdvRange = float(eval(CHAsbxy.get()))
        except:
            CHAsbxy.delete(0,END)
            CHAsbxy.insert(0, CH1vpdvRange)
        try:
            CH2pdvRange = float(eval(CHBsbxy.get()))
        except:
            CHBsb.delete(0,END)
            CHBsb.insert(0, CH2vpdvRange)
        try:
            MC1pdvRange = float(eval(MC1sbxy.get()))
        except:
            MC1sbxy.delete(0,END)
            MC1sbxy.insert(0, MC1vpdvRange)
        try:
            MC2pdvRange = float(eval(MC2sbxy.get()))
        except:
            MC2sb.delete(0,END)
            MC2sb.insert(0, MC2vpdvRange)
        # get the vertical offsets
        try:
            CHAOffset = float(eval(CHAVPosEntryxy.get()))
        except:
            CHAVPosEntryxy.delete(0,END)
            CHAVPosEntryxy.insert(0, CHAOffset)
        try:
            CHBOffset = float(eval(CHBVPosEntryxy.get()))
        except:
            CHBVPosEntryxy.delete(0,END)
            CHBVPosEntryxy.insert(0, CHBOffset)
        try:
            MC1Offset = float(eval(MC1VPosEntryxy.get()))
        except:
            MC1VPosEntryxy.delete(0,END)
            MC1VPosEntryxy.insert(0, MC1Offset)
        try:
            MC2Offset = float(eval(MC2VPosEntryxy.get()))
        except:
            MC2VPosEntryxy.delete(0,END)
            MC2VPosEntryxy.insert(0, MC2Offset)
        # prevent divide by zero error
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
        if CH2pdvRange < 0.001:
            CH2pdvRange = 0.001
        try:
            HoldOff = float(eval(HoldOffentry.get()))
            if HoldOff < 0:
                HoldOff = 0
        except:
            HoldOffentry.delete(0,END)
            HoldOffentry.insert(0, HoldOff)
    #
        Yconv1 = float(GRHXY/10) / CH1pdvRange    # Conversion factors from samples to screen points
        Xconv1 = float(GRWXY/10) / CH1pdvRange
        XconvMC1 = float(GRWXY/10) / MC1pdvRange
        Yconv2 = float(GRHXY/10) / CH2pdvRange
        YconvMC2 = float(GRHXY/10) / MC2pdvRange
        Xconv2 = float(GRWXY/10) / CH2pdvRange
        if MarkerXYScale.get() == 1:
            COLORmarker = COLORtrace1
        elif MarkerXYScale.get() == 2:
            COLORmarker = COLORtrace2
        elif MarkerXYScale.get() == 3:
            COLORmarker = COLORtrace5
        elif MarkerXYScale.get() == 4:
            COLORmarker = COLORtrace7
        c1 = GRHXY / 2 + Y0TXY    # fixed correction channel A
        xc1 = GRWXY / 2 + X0LXY
        c2 = GRHXY / 2 + Y0TXY    # fixed correction channel B
        # draw X at marker point and number
        XYca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORmarker)
        XYca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORmarker)
        XYca.create_text(event.x+4, event.y, text=str(MarkerXYNum), fill=COLORmarker, anchor="w", font=("arial", 8 ))
        #
        if Xsignal.get()==1 or Xsignal.get()==6:
            xvolts = ((xc1-event.x)/Xconv1) - CHAOffset
            XUnits = " V"
        if Ysignal.get()==1:
            yvolts = ((event.y-c1)/Yconv1) - CHAOffset
            YUnits = " V"
        if Ysignal.get()==3:
            yvolts = ((event.y-c2)/Yconv2) - CHBOffset
            YUnits = " V"
        if Xsignal.get()==3 or Xsignal.get()==7:
            xvolts = ((xc1-event.x)/Xconv2) - CHBOffset
            XUnits = " V"
        if Xsignal.get()==5:
            xvolts = ((xc1-event.x)/XconvMC1) - MC1Offset
            XUnits = MathXUnits
        if Ysignal.get()==5:
            yvolts = ((event.y-c2)/YconvMC2) - MC2Offset
            YUnits = MathYUnits
        VyString = ' {0:.3f} '.format(-yvolts)
        VxString = ' {0:.3f} '.format(-xvolts)
        V_label = str(MarkerXYNum) + " " + VxString + XUnits + ", " + VyString + YUnits
        if MarkerNum > 1:
            DeltaY = ' {0:.3f} '.format(PrevY-yvolts)
            DeltaX = ' {0:.3f} '.format(PrevX-xvolts)
            V_label = V_label + " Delta " + DeltaX + XUnits + ", " + DeltaY + YUnits
        x = X0LXY + 5
        y = Y0TXY + 3 + (MarkerXYNum*10)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0LXY + GRWXY - 5
            y = Y0TXY + 3 + (MarkerXYNum*10)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0LXY + 5
            y = Y0TXY + GRHXY + 3 - (MarkerXYNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0LXY + GRWXY - 5
            y = Y0TXY + GRHXY + 3 - (MarkerXYNum*10)
            Justify = 'e'
        XYca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", 8 ))
        PrevY = yvolts
        PrevX = xvolts
#
def ReConnectDevice():

    if DevID == "No Device":
        ConnectDevice()
    time.sleep(0.2)
    SelfCalibration() # Run a sel calibration to start
    
def ConnectDevice():
    global DevID, bcon, PlusUS, NegUS, FWRev, HWRev, ctx, ad5627, ad5625, m2k_fabric, m2k_adc_trigger
    global ad9963, m2k_adc, m2k_dds, m2k_dac_a, m2k_dac_b, PlusUS_RB, NegUS_RB
    global AWG1Offset, AWG2Offset, Scope1Offset, Scope2Offset, m2k_AWG1pd, m2k_AWG2pd
    global AWGAgain, AWGAoffset, AWGBgain, AWGBoffset
    global m2k_adc0, m2k_adc1, adc0, adc1, SAMPLErate, OverSampleRate, AWGASampleRate, AWGBSampleRate
    global m2k_adc_trigger, m2k_adc0_trigger, m2k_adc1_trigger, m2k_adc2_trigger, m2k_adc3_trigger
    global m2k_adc4_trigger, m2k_adc5_trigger, m2k_adc6_trigger, m2k_dac_a, m2k_dac_b, dac_a, dac_b
    global dac_a_pd, dac_b_pd, Buff0, Buff1, TimeBuffer, SHOWsamples
    global Dig0, Dig1, Dig2, Dig3, Dig4, Dig5, Dig6, Dig7, logic
    global Dig10, Dig11, Dig12, Dig13, Dig14, Dig15, Dig8, Dig9, DigBuff0
    global PatGen0, PatGen1, PatGen2, PatGen3, PatGen4, PatGen5, PatGen6, PatGen7, Dig_Out
    global PatGen8, PatGen9, PatGen10, PatGen11, PatGen12, PatGen13, PatGen14, PatGen15
    
    print('Library version: %u.%u (git tag: %s)' % iio.version)
    contexts = iio.scan_contexts()
    if len(contexts) < 1:
        print 'No Device plugged IN!'
        DevID = "No Device"
        bcon.configure(text="Recon", style="RConn.TButton")
        return
    uri = next(iter(contexts), None)
    ctx = iio.Context(uri)
    bcon.configure(text="Conn",  style="GConn.TButton")
    DevID = ctx.attrs['hw_serial']
    print DevID
    HWRev = ctx.attrs['hw_model']
    # ctx.set_timeout(1000)
    FWRev = ctx.attrs['fw_version'] # "Unknown "
# set time out to 10 Sec ????
    ctx.set_timeout(10000)
# User power supply
    ad5627 = ctx.find_device("ad5627")
    PlusUS = ad5627.find_channel("voltage0", True)
    NegUS = ad5627.find_channel("voltage1", True)
    PlusUS.attrs["powerdown"].value = str(1) # power down positve user supply
    PlusUS.attrs["raw"].value = str(0) # set value to zero volts
    NegUS.attrs["powerdown"].value = str(1) # power down negative user supply
    NegUS.attrs["raw"].value = str(0) # set value to zero volts
# AD9963 AUX channels
    ad9963 = ctx.find_device("ad9963")
    NegUS_RB = ad9963.find_channel("voltage1", False) # Neg US readback
    PlusUS_RB = ad9963.find_channel("voltage2", False) # Plus US readback
# Offset DACs
    ad5625 = ctx.find_device("ad5625")
    AWG1Offset = ad5625.find_channel("voltage0", True)
    AWG2Offset = ad5625.find_channel("voltage1", True)
    Scope1Offset = ad5625.find_channel("voltage2", True)
    Scope2Offset = ad5625.find_channel("voltage3", True)
# set offset DACs to mid range
    AWG1Offset.attrs["raw"].value = str(AWGAoffset)
    AWG2Offset.attrs["raw"].value = str(AWGBoffset)
    Scope1Offset.attrs["raw"].value = '2009'
    Scope2Offset.attrs["raw"].value = '2028'
#
    m2k_fabric = ctx.find_device("m2k-fabric")
    m2k_fabric.attrs["clk_powerdown"].value = '0'
#
    m2k_adc0 = m2k_fabric.find_channel("voltage0", False)
    m2k_adc1 = m2k_fabric.find_channel("voltage1", False)
    m2k_adc0.attrs["gain"].value = 'low'
    m2k_adc1.attrs["gain"].value = 'low'
#
    m2k_adc = ctx.find_device("m2k-adc")
    adc0 = m2k_adc.find_channel("voltage0", False)
    adc1 = m2k_adc.find_channel("voltage1", False)
# set sample rate and enable scope input channels
    m2k_adc.attrs["oversampling_ratio"].value = str(OverSampleRate)
    m2k_adc.attrs["sampling_frequency"].value = str(SAMPLErate)
    adc0.enabled = True
    adc1.enabled = True
# Power up M2K outputs
    m2k_AWG1pd = m2k_fabric.find_channel("voltage0", False)
    m2k_AWG2pd = m2k_fabric.find_channel("voltage1", False)
    dac_a_pd = m2k_fabric.find_channel("voltage0", True)
    dac_b_pd = m2k_fabric.find_channel("voltage1", True)
    m2k_AWG1pd.attrs["powerdown"].value = '0'
    m2k_AWG2pd.attrs["powerdown"].value = '0'
    AWG1Offset.attrs["powerdown"].value = '0'
    AWG2Offset.attrs["powerdown"].value = '0'
    Scope1Offset.attrs["powerdown"].value = '0'
    Scope2Offset.attrs["powerdown"].value = '0'
# Scope HW trigger stuff
    m2k_adc_trigger = ctx.find_device("m2k-adc-trigger")
    m2k_adc0_trigger = m2k_adc_trigger.find_channel("voltage0", False)
    m2k_adc1_trigger = m2k_adc_trigger.find_channel("voltage1", False)
    m2k_adc2_trigger = m2k_adc_trigger.find_channel("voltage2", False)
    m2k_adc3_trigger = m2k_adc_trigger.find_channel("voltage3", False)
    m2k_adc4_trigger = m2k_adc_trigger.find_channel("voltage4", False)
    m2k_adc5_trigger = m2k_adc_trigger.find_channel("voltage5", False)
    m2k_adc6_trigger = m2k_adc_trigger.find_channel("voltage6", False)
    m2k_adc0_trigger.attrs["trigger_hysteresis"].value = str(10)
    m2k_adc1_trigger.attrs["trigger_hysteresis"].value = str(10)
    m2k_adc4_trigger.attrs["mode"].value = 'always'
    m2k_adc5_trigger.attrs["mode"].value = 'always'
# AWG DAC stuff
    m2k_dac_a = ctx.find_device("m2k-dac-a")
    m2k_dac_b = ctx.find_device("m2k-dac-b")
    dac_a = m2k_dac_a.find_channel("voltage0", True)
    dac_b = m2k_dac_b.find_channel("voltage0", True)
    dac_a.enabled = True
    dac_b.enabled = True
    dac_a_pd.attrs["powerdown"].value = '0'
    dac_b_pd.attrs["powerdown"].value = '0'
    m2k_dac_a.attrs["sampling_frequency"].value = str(AWGASampleRate)
    m2k_dac_b.attrs["sampling_frequency"].value = str(AWGBSampleRate)
    m2k_dac_a.attrs["dma_sync"].value = '0' # 
    m2k_dac_b.attrs["dma_sync"].value = '0'
    Buff0 = iio.Buffer(m2k_dac_a, 4096, True) # pre make some temp buffers
    Buff1 = iio.Buffer(m2k_dac_b, 4096, True)
    TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, True)
    TimeBuffer.refill()
    del(TimeBuffer)
    TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
# Digital Input / OutPut channels
    logic = ctx.find_device("m2k-logic-analyzer")
    Dig0 = logic.find_channel("voltage0", False)
    Dig1 = logic.find_channel("voltage1", False)
    Dig2 = logic.find_channel("voltage2", False)
    Dig3 = logic.find_channel("voltage3", False)
    Dig4 = logic.find_channel("voltage4", False)
    Dig5 = logic.find_channel("voltage5", False)
    Dig6 = logic.find_channel("voltage6", False)
    Dig7 = logic.find_channel("voltage7", False)
    Dig8 = logic.find_channel("voltage8", False)
    Dig9 = logic.find_channel("voltage9", False)
    Dig10 = logic.find_channel("voltage10", False)
    Dig11 = logic.find_channel("voltage11", False)
    Dig12 = logic.find_channel("voltage12", False)
    Dig13 = logic.find_channel("voltage13", False)
    Dig14 = logic.find_channel("voltage14", False)
    Dig15 = logic.find_channel("voltage15", False)
# Digital patten generator output stuff
    Dig_Out = ctx.find_device("m2k-logic-analyzer-tx")
    PatGen0 = Dig_Out.find_channel("voltage0", True)
    PatGen1 = Dig_Out.find_channel("voltage1", True)
    PatGen2 = Dig_Out.find_channel("voltage2", True)
    PatGen3 = Dig_Out.find_channel("voltage3", True)
    PatGen4 = Dig_Out.find_channel("voltage4", True)
    PatGen5 = Dig_Out.find_channel("voltage5", True)
    PatGen6 = Dig_Out.find_channel("voltage6", True)
    PatGen7 = Dig_Out.find_channel("voltage7", True)
    PatGen8 = Dig_Out.find_channel("voltage8", True)
    PatGen9 = Dig_Out.find_channel("voltage9", True)
    PatGen10 = Dig_Out.find_channel("voltage10", True)
    PatGen11 = Dig_Out.find_channel("voltage11", True)
    PatGen12 = Dig_Out.find_channel("voltage12", True)
    PatGen13 = Dig_Out.find_channel("voltage13", True)
    PatGen14 = Dig_Out.find_channel("voltage14", True)
    PatGen15 = Dig_Out.find_channel("voltage15", True)
    # make a temp digital pattern buffer
    # DigBuff0 = iio.Buffer(Dig_Out, 8192, True)
#
def Wrap(InArray, WrFactor):
    # Build new array by skipping WrFactor samples and wrapping back around
    # [1,2,3,4,5,6} becomes [1,3,5,2,4,6]
    # effectively multiplies the frequency content by WrFactor
    OutArray = []
    OutArray = numpy.array(OutArray)
    InArray = numpy.array(InArray)
    EndIndex = len(InArray)
    StartIndex = 0
    while StartIndex < WrFactor:
        OutArray = numpy.concatenate((OutArray, InArray[StartIndex:EndIndex:WrFactor]), axis=0)
        StartIndex = StartIndex + 1
    return OutArray

def UnWrap(InArray, WrFactor):
    # Build new array by splitting arrray into WrFactor sections and interleaving samples from each section
    # [1,2,3,4,5,6} becomes [1,4,2,5,3,6]
    # effectively divided the frequency content by WrFactor
    OutArray = []
    InArray = numpy.array(InArray)
    EndIndex = int(len(InArray)/WrFactor)
    StartIndex = 0
    while StartIndex < EndIndex:
        LoopIndex = 0
        while LoopIndex < WrFactor:
            OutArray.append(InArray[StartIndex+LoopIndex])
            LoopIndex = LoopIndex + 1
        StartIndex = StartIndex + 1
    OutArray = numpy.array(OutArray)
    return OutArray
#
def Write_WAV(data, repeat, filename):
    global SAMPLErate
    # write data array to mono .wav file 100KSPS
    # copy buffer repeat times in output file
    # Use : Write_WAV(VBuffB, 2, "write_wave_1.wav")
    wavfile = wave.open(filename, "w")
    nchannels = 1
    sampwidth = 2
    framerate = SAMPLErate
    amplitude = 32766
    nframes = len(data)
    comptype = "NONE"
    compname = "not compressed"
    wavfile.setparams((nchannels,
                        sampwidth,
                        framerate,
                        nframes,
                        comptype,
                        compname))
    # Normalize data
    ArrN = numpy.array(data)
    ArrN /= numpy.max(numpy.abs(data))
    frames = []
    for s in ArrN:
        mul = int(s * amplitude)
        # print "s: %f mul: %d" % (s, mul)
        frames.append(struct.pack('h', mul))
    # print len(frames)
    frames = ''.join(frames)
    # print len(frames)
    for x in xrange(0, repeat):
        # print x
        wavfile.writeframes(frames)
    wavfile.close()
    
# =========== Awg functions ==================
def BAWGAAmpl(temp):
    global AWGAAmplEntry, AWGAAmplvalue

    try:
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
        if AWGAAmplvalue > 5.00:
            AWGAAmplvalue = 5.00
            AWGAAmplEntry.delete(0,"end")
            AWGAAmplEntry.insert(0, AWGAAmplvalue)
        if AWGAAmplvalue < -5.00:
            AWGAAmplvalue = -5.00
            AWGAAmplEntry.delete(0,"end")
            AWGAAmplEntry.insert(0, AWGAAmplvalue)
    except:
        AWGAAmplEntry.delete(0,"end")
        AWGAAmplEntry.insert(0, AWGAAmplvalue)
    
def BAWGAOffset(temp):
    global AWGAOffsetEntry, AWGAOffsetvalue

    try:
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
        if AWGAOffsetvalue > 5.00:
            AWGAOffsetvalue = 5.00
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
        if AWGAOffsetvalue < -5.00:
            AWGAOffsetvalue = -5.00
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
    except:
        AWGAOffsetEntry.delete(0,"end")
        AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
    
def BAWGAFreq(temp):
    global AWGAFreqEntry, AWGAFreqvalue, AWGASampleRate, m2k_dac_a, AWGAgain
    global AWGAgain7M, AWGAgain75M, AWGAgain75K, AWGAgain750K

    try:
        AWGAFreqvalue = float(eval(AWGAFreqEntry.get()))
    except:
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)

    if AWGAFreqvalue > 25000000: # max freq is 25 MHz
        AWGAFreqvalue = 25000000
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue <= 0: # Set negative frequency entry to 0
        AWGAFreqvalue = 1
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue <= 10000: # 10 times 7500
        AWGASampleRate = 7500000
        AWGAgain = AWGAgain7M
##    elif AWGAFreqvalue > 7500 and AWGAFreqvalue < 75000: # 10 times 75000
##        AWGASampleRate = 7500000
    elif AWGAFreqvalue > 10000 and AWGAFreqvalue < 25000000: # 10 times 750000
        AWGASampleRate = 75000000
        AWGAgain = AWGAgain75M
    m2k_dac_a.attrs["sampling_frequency"].value = str(AWGASampleRate)

def BAWGAPhaseDelay():
    global AWGAPhaseDelay, phasealab, awgaph, awgadel

    if AWGAPhaseDelay.get() == 0:
        phasealab.configure(text="Deg")
        awgaph.configure(style="WPhase.TRadiobutton")
        awgadel.configure(style="GPhase.TRadiobutton")
    elif AWGAPhaseDelay.get() == 1:
        phasealab.configure(text="mSec")
        awgaph.configure(style="GPhase.TRadiobutton")
        awgadel.configure(style="WPhase.TRadiobutton")
    
def BAWGAPhase(temp):
    global AWGAPhaseEntry, AWGAPhasevalue

    try:
        AWGAPhasevalue = float(eval(AWGAPhaseEntry.get()))
    except:
        AWGAPhaseEntry.delete(0,"end")
        AWGAPhaseEntry.insert(0, AWGAPhasevalue)

    if AWGAPhasevalue > 360: # max phase is 360 degrees
        AWGAPhasevalue = 360
        AWGAPhaseEntry.delete(0,"end")
        AWGAPhaseEntry.insert(0, AWGAPhasevalue)
    if AWGAPhasevalue < 0: # min phase is 0 degrees
        AWGAPhasevalue = 0
        AWGAPhaseEntry.delete(0,"end")
        AWGAPhaseEntry.insert(0, AWGAPhasevalue)
        
def BAWGADutyCycle(temp):
    global AWGADutyCycleEntry, AWGADutyCyclevalue, AWGAShape

    try:
        AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))/100.0
    except:
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)

    if AWGADutyCyclevalue > 1 and AWGAShape.get()!= 14: # max duty cycle is 100%
        AWGADutyCyclevalue = 1
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue*100)
    if AWGADutyCyclevalue < 0: # min duty cycle is 0%
        AWGADutyCyclevalue = 0
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)

def AWGAReadFile():
    global AWGAwaveform, AWGALength, awgwindow, AWGAgain, AWGASampleRate
    global AWGAgain75M, AWGAgain7M, AWGAgain750K, AWGAgain75K

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
    RequestRate = askstring("Pick Sample Rate", "Select sample rate from\n75000000\n7500000\n750000\n75000\nEnter Value:\n", initialvalue=750000, parent=awgwindow)
    try:
        AWGASampleRate = int(RequestRate)
    except:
        AWGASampleRate = 75000
    if AWGASampleRate == 75000000:
        AWGAgain = AWGAgain75M
    if AWGASampleRate == 7500000:
        AWGAgain = AWGAgain7M
    if AWGASampleRate == 750000:
        AWGAgain = AWGAgain750K
    if AWGASampleRate == 75000:
        AWGAgain = AWGAgain75K
    m2k_dac_a.attrs["sampling_frequency"].value = str(AWGASampleRate)
    AWGAwaveform = []
    ColumnNum = 0
    ColumnSel = 0
    for row in csv_f:
        if len(row) > 1 and ColumnSel == 0:
            RequestColumn = askstring("Which Column?", "File contains 1 to " + str(len(row)) + " columns\n\nEnter column number to import:\n", initialvalue=1, parent=awgwindow)
            ColumnNum = int(RequestColumn) - 1
            ColumnSel = 1
        try:
            AWGAwaveform.append(float(row[ColumnNum]))
        except:
            print 'skipping non-numeric row'
    AWGAwaveform = numpy.array(AWGAwaveform)
    CSVFile.close()

def AWGAReadWAV():
    global AWGAwaveform, AWGALength, AWGAShape, awgwindow, AWGBwaveform, AWGBLength, AWGBShape
    global AWGASampleRate, m2k_dac_a, AWGBSampleRate, m2k_dac_b, AWGAOffsetvalue, AWGAAmplvalue
    global AWGBModeLabel, AWGBbinform
    global AWGAgain75M, AWGAgain7M, AWGAgain750K, AWGAgain75K, AWGAgain
    global AWGBgain75M, AWGBgain7M, AWGBgain750K, AWGBgain75K, AWGBgain

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)

    ScaleFactor = (5.0 / 32768.0) # (AWGAOffsetvalue-AWGAAmplvalue)

# Read values from WAV file
    filename = askopenfilename(defaultextension = ".wav", filetypes=[("WAV files", "*.wav")], parent=awgwindow)
    try:
        spf = wave.open(filename,'r')
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
        return()
    RequestRate = askstring("Pick Sample Rate", "Select sample rate from\n75000000\n7500000\n750000\n75000\nEnter Value:\n", initialvalue=750000, parent=awgwindow)
    try:
        AWGASampleRate = int(RequestRate)
    except:
        AWGASampleRate = 75000
    if AWGASampleRate == 75000000:
        AWGAgain = AWGAgain75M
    if AWGASampleRate == 7500000:
        AWGAgain == AWGAgain7M
    if AWGASampleRate == 750000:
        AWGAgain = AWGAgain750K
    if AWGASampleRate == 75000:
        AWGAgain = AWGAgain75K
    m2k_dac_a.attrs["sampling_frequency"].value = str(AWGASampleRate)
    AWGAwaveform = []
    AWGBwaveform = []
    Length = spf.getnframes()
    if Length > 90000:
        Length = 90000
    # If Stereo put first channel in AWGA and second channel in AWGB
    if spf.getnchannels() == 2:
        showwarning("Split Stereo","Left to AWGA Right to AWGB", parent=awgwindow)
        signal = spf.readframes(Length)
        Stereo = numpy.fromstring(signal, 'Int16') # convert strings to Int
        n = 0
        while n < Length*2:
            AWGAwaveform.append(Stereo[n])
            n = n + 1
            AWGBwaveform.append(Stereo[n])
            n = n + 1
        AWGBShape.set(AWGAShape.get())
        AWGBSampleRate = AWGASampleRate
        if AWGBSampleRate == 75000000:
            AWGBgain = AWGBgain75M
        if AWGBSampleRate == 7500000:
            AWGBgain = AWGBgain7M
        if AWGBSampleRate == 750000:
            AWGBgain = AWGBgain750K
        if AWGBSampleRate == 75000:
            AWGBgain = AWGBgain75K
        m2k_dac_b.attrs["sampling_frequency"].value = str(AWGBSampleRate)
        AWGAwaveform = numpy.array(AWGAwaveform)
        AWGBwaveform = numpy.array(AWGBwaveform)
        AWGAwaveform = AWGAwaveform * ScaleFactor
        AWGBwaveform = AWGBwaveform * ScaleFactor
        InvGain = -1.0 * AWGBgain
        AWGBbinform = AWGBwaveform * InvGain
        AWGBbinform = bytearray(numpy.array(AWGBbinform,dtype="int16"))
        AWGBLength.config(text = "L = " + str(int(len(AWGBbinform)/2))) # change displayed value
        AWGBModeLabel.config(text = "WAV File Shape" ) # change displayed value
    else:
    #Extract Raw Audio from Wav File
        signal = spf.readframes(Length)
        WAVsignal = numpy.fromstring(signal, 'Int16') # convert strings to Int
        # offset and scale for -5, 5 V range
        AWGAwaveform = WAVsignal * ScaleFactor
    spf.close()

def AWGAWriteFile():
    global AWGAwaveform, AWGALength, awgwindow
    
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    numpy.savetxt(filename, AWGAwaveform, delimiter=",", fmt='%2.4f')
#
def AWGAEnterMath():
    global AWGAwaveform, AWGASampleRate, VBuffA, VBuffB, VFilterA, VFilterB
    global AWGBwaveform, VmemoryA, VmemoryB, ImemoryA, ImemoryB, AWGAMathString
    global FFTBuffA, FFTBuffB, FFTwindowshape, AWGALength, awgwindow
    global DFiltACoef, DFiltBCoef, AWGAgain, AWGAoffset

    TempString = AWGAMathString
    AWGAMathString = askstring("AWG 1 Math Formula", "Current Formula: " + AWGAMathString + "\n\nNew Formula:\n", initialvalue=AWGAMathString, parent=awgwindow)
    if (AWGAMathString == None):         # If Cancel pressed, then None
        AWGAMathString = TempString
        return
#
def AWGAMakeMath():
    global AWGAwaveform, AWGASampleRate, VBuffA, VBuffB, VFilterA, VFilterB
    global AWGBwaveform, VmemoryA, VmemoryB, ImemoryA, ImemoryB, AWGAMathString
    global FFTBuffA, FFTBuffB, FFTwindowshape, AWGALength, awgwindow
    global DFiltACoef, DFiltBCoef, AWGAgain, AWGAoffset

    AWGAwaveform = eval(AWGAMathString)
    AWGAwaveform = numpy.array(AWGAwaveform)
#
def AWGAMakeDC():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset, phasealab, duty1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 1.0
    MaxV = AWGAOffsetvalue
    AWGAwaveform = []
    Width = int(AWGAperiodvalue)
    if Width <=0:
        Width = 1
    for i in range(Width):
        AWGAwaveform.append(MaxV)
    AWGAwaveform = numpy.array(AWGAwaveform)
#
def AWGAMakeSine():
    global AWGAwaveform, AWGASampleRate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAperiodvalue
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWGAgain, AWGAoffset, AWGAPhaseDelay
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)

    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 10.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
    Cycles = int(37500/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1
    RecLength = Cycles * AWGAperiodvalue
    AWGAwaveform = []
    AWGAwaveform = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / 2.0
    offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2.0
    AWGAwaveform = (AWGAwaveform * amplitude) + offset # scale and offset the waveform
    AWGAwaveform = numpy.roll(AWGAwaveform, int(AWGAdelayvalue))
    BAWGAPhaseDelay()
    duty1lab.config(text="%")
#
def AWGAMakeFourier():
    global AWGAwaveform, AWGASampleRate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWGAgain, AWGAoffset
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGADutyCycle(temp)
    
    Max_term = int(AWGADutyCyclevalue*100)
    AWGAwaveform = []
    AWGAwaveform = numpy.cos(numpy.linspace(0, 2*numpy.pi, AWGASampleRate/AWGAFreqvalue)) # the fundamental
    k = 3
    while k <= Max_term:
        # Add odd harmonics up to max_term
        Harmonic = (math.sin(k*numpy.pi/2)/k)*(numpy.cos(numpy.linspace(0, k*2*numpy.pi, AWGASampleRate/AWGAFreqvalue)))
        AWGAwaveform = AWGAwaveform + Harmonic
        k = k + 2 # skip even numbers
    amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / 2.0
    offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2.0
    AWGAwaveform = (AWGAwaveform * amplitude) + offset # scale and offset the waveform
    duty1lab.config(text="Harmonics")
#
def AWGAMakeSinc():
    global AWGAwaveform, AWGASampleRate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAperiodvalue
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWGAgain, AWGAoffset, AWGAPhaseDelay
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)

    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
    Cycles = int(AWGADutyCyclevalue*100)
    NCycles = -1 * Cycles
    AWGAwaveform = []
    AWGAwaveform = numpy.sinc(numpy.linspace(NCycles, Cycles, AWGASampleRate/AWGAFreqvalue))
    amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / 2.0
    offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2.0
    AWGAwaveform = (AWGAwaveform * amplitude) + offset # scale and offset the waveform
    Cycles = int(37500/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1
    if Cycles > 1:
        Extend = int((Cycles-1.0)*AWGAperiodvalue/2.0)
        AWGAwaveform = numpy.pad(AWGAwaveform, (Extend,Extend), 'wrap')
    AWGAwaveform = numpy.roll(AWGAwaveform, int(AWGAdelayvalue))
    BAWGAPhaseDelay()
    duty1lab.config(text="Cycles")
#
def AWGAMakeSSQ():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset, phasealab, duty1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
        
    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
    Cycles = int(37500/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1      
    MaxV = AWGAOffsetvalue
    MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*AWGASampleRate/1000)
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGAperiodvalue * (1.0-AWGADutyCyclevalue))
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int((AWGAperiodvalue - PulseWidth - SlopeValue)/2)
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepAmp = (MaxV - MinV)/2
    StepOff = (MaxV + MinV)/2
    AWGAwaveform = StepAmp * (numpy.cos(numpy.linspace(0, 2*numpy.pi, SlopeValue*2))) + StepOff
    MidArray = numpy.ones(PulseWidth) * MinV
    AWGAwaveform = numpy.insert(AWGAwaveform, SlopeValue, MidArray)
    AWGAwaveform = numpy.pad(AWGAwaveform, (Remainder, Remainder), 'edge')
    if Cycles > 1:
        Extend = int((Cycles-1.0)*AWGAperiodvalue/2.0)
        AWGAwaveform = numpy.pad(AWGAwaveform, (Extend,Extend), 'wrap')
    duty1lab.config(text="%")
    phasealab.config(text = "Rise Time")
#
def AWGAMakeSquare():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset, phasealab, duty1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
    Cycles = int(37500/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1         
    MaxV = AWGAOffsetvalue
    MinV = AWGAAmplvalue
    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    for j in range(Cycles):
        for i in range(PulseWidth):
            AWGAwaveform.append(MaxV)
        for i in range(Remainder):
            AWGAwaveform.append(MinV)
    AWGAwaveform = numpy.array(AWGAwaveform)
    AWGAwaveform = numpy.roll(AWGAwaveform, int(AWGAdelayvalue))
    duty1lab.config(text="%")
    BAWGAPhaseDelay()
#
def AWGAMakeTrapazoid():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset, phasealab, duty1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
    Cycles = int(37500/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1        
    MaxV = AWGAOffsetvalue
    MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*AWGASampleRate/1000)
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth) - SlopeValue
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = ((MaxV - MinV) / SlopeValue)
    for j in range(Cycles):
        SampleValue = MinV
        for i in range(SlopeValue):
            AWGAwaveform.append(SampleValue)
            SampleValue = SampleValue + StepValue
        for i in range(PulseWidth):
            AWGAwaveform.append(MaxV)
        for i in range(SlopeValue):
            AWGAwaveform.append(SampleValue)
            SampleValue = SampleValue - StepValue
        for i in range(Remainder):
            AWGAwaveform.append(MinV)
    AWGAwaveform = numpy.array(AWGAwaveform)
    duty1lab.config(text="%")
    phasealab.config(text = "Rise Time")
#
def AWGAMakeRamp():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset, phasealab, duty1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
    Cycles = int(37500/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1        
    MaxV = AWGAOffsetvalue
    MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*AWGASampleRate/1000) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = ((MaxV - MinV) / SlopeValue)
    SampleValue = MinV
    for j in range(Cycles):
        SampleValue = MinV
        for i in range(SlopeValue):
            AWGAwaveform.append(SampleValue)
            SampleValue = SampleValue + StepValue
        for i in range(PulseWidth):
            AWGAwaveform.append(MaxV)
        for i in range(Remainder):
            AWGAwaveform.append(MinV)
    AWGAwaveform = numpy.array(AWGAwaveform)
    duty1lab.config(text="%")
    phasealab.config(text = "Slope Time")
#
def AWGAMakeUpDownRamp():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset, duty1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = int(AWGASampleRate/AWGAFreqvalue)
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
    Cycles = int(37500/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1
    MaxV = AWGAOffsetvalue
    MinV = AWGAAmplvalue
    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    UpStepValue = ((MaxV - MinV) / PulseWidth)
    DownStepValue = ((MaxV - MinV) / Remainder)
    for j in range(Cycles):
        SampleValue = MaxV # MinV
        for i in range(PulseWidth):
            AWGAwaveform.append(SampleValue)
            SampleValue = SampleValue - UpStepValue
        for i in range(Remainder):
            AWGAwaveform.append(SampleValue)
            SampleValue = SampleValue + DownStepValue
    AWGAwaveform = numpy.array(AWGAwaveform)
    AWGAwaveform = numpy.roll(AWGAwaveform, int(AWGAdelayvalue))
    BAWGAPhaseDelay()
    duty1lab.config(text = "Symmetry")
#
def AWGAMakeTriangle():
    global AWGADutyCycleEntry
    
    AWGADutyCycleEntry.delete(0,"end")
    AWGADutyCycleEntry.insert(0, 50)
    AWGAMakeUpDownRamp()
#
def AWGAMakeSawtooth():
    global AWGADutyCycleEntry
    
    AWGADutyCycleEntry.delete(0,"end")
    AWGADutyCycleEntry.insert(0, 99)
    AWGAMakeUpDownRamp()
#
def AWGAMakeImpulse():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    MaxV = AWGAOffsetvalue
    MinV = AWGAAmplvalue
    MidV = MinV+MaxV/2.0
    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue / 2.0)
    if AWGAPhaseDelay.get() == 0:
        DelayValue = int(AWGAperiodvalue*(AWGAPhasevalue/360))
    elif AWGAPhaseDelay.get() == 1:
        DelayValue = int(AWGAPhasevalue*100)
    for i in range(DelayValue-PulseWidth):
        AWGAwaveform.append(MidV)
    for i in range(PulseWidth):
        AWGAwaveform.append(MaxV)
    for i in range(PulseWidth):
        AWGAwaveform.append(MinV)
    DelayValue = int(AWGAperiodvalue-DelayValue)
    for i in range(DelayValue-PulseWidth):
        AWGAwaveform.append(MidV)
    AWGAwaveform = numpy.array(AWGAwaveform)
#
def AWGAMakeStair():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay
    global AWGAFreqvalue, AWGAperiodvalue, AWGASampleRate, AWGADutyCyclevalue, AWGAPhasevalue
    global AWGAgain, AWGAoffset, duty1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGASampleRate / 1000
        
    MaxV = AWGAOffsetvalue
    MinV = AWGAAmplvalue
    AWGAwaveform = []
    Treads = int(AWGADutyCyclevalue*100.0)
    if Treads < 2:
        Treads = 2
    TreadWidth = int(AWGAperiodvalue / Treads)
    TreadHight = (MaxV-MinV)/(Treads-1)
    for i in range(Treads):
        for j in range(TreadWidth):
            AWGAwaveform.append(MinV)
        MinV = MinV + TreadHight
#
    AWGAwaveform = numpy.array(AWGAwaveform)
    AWGAwaveform = numpy.roll(AWGAwaveform, int(AWGAdelayvalue))
    BAWGAPhaseDelay()
    duty1lab.config(text = "Steps")
    
def AWGAMakeUUNoise():
    global AWGAwaveform, AWGASampleRate, AWGAAmplvalue, AWGAOffsetvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue, AWGAgain, AWGAoffset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAAmplvalue > AWGAOffsetvalue:
        MinV = AWGAOffsetvalue
        MaxV = AWGAAmplvalue
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    AWGAwaveform = numpy.random.uniform(MinV, MaxV, int(AWGAperiodvalue))
    
def AWGAMakeUGNoise():
    global AWGAwaveform, AWGASampleRate, AWGAAmplvalue, AWGAOffsetvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue, AWGAgain, AWGAoffset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAAmplvalue > AWGAOffsetvalue:
        MinV = AWGAOffsetvalue
        MaxV = AWGAAmplvalue
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    AWGAwaveform = numpy.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGAperiodvalue))
#
def UpdateAWGA():
    global AWGAAmplvalue, AWGAOffsetvalue, AWGBwaveform
    global AWGAFreqvalue, AWGAPhasevalue, AWGAPhaseDelay
    global AWGADutyCyclevalue, FSweepMode, AWGARepeatFlag
    global AWGAWave, AWGAMode, AWGAwaveform, AWGAIOMode
    global AWGASampleRate, AWG1Offset, ctx, ad5625, m2k_AWG1pd, m2k_fabric, dac_a_pd
    global AWGAgain, AWGAoffset, AWGBgain, AWGBoffset, m2k_dac_a, m2k_dac_b, Buff0, Buff1
    global AWGAModeLabel, DevID, HWRevOne
    global AWGAShape, AWGAbinform, AWGBbinform
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGASampleRate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
        
    if AWGAMode.get() == 0: # power up AWG 1
        m2k_AWG1pd.attrs["powerdown"].value = '0'
        AWG1Offset.attrs["powerdown"].value = '0'
        dac_a_pd.attrs["powerdown"].value = '0'
    elif AWGAMode.get() == 2: # Power down AWG 1
        AWG1Offset.attrs["powerdown"].value = '1'
        m2k_AWG1pd.attrs["powerdown"].value = '1'
        dac_a_pd.attrs["powerdown"].value = '1'
    if AWGAShape.get() == 0:
        label_txt = 'DC'
        AWGAMakeDC()
    if AWGAShape.get() == 1:
        label_txt = 'Sine'
        AWGAMakeSine()
    if AWGAShape.get() == 2:
        label_txt = 'Triangle'
        AWGAMakeTriangle()
    if AWGAShape.get() == 3:
        label_txt = 'Sawtooth'
        AWGAMakeSawtooth()
    if AWGAShape.get() == 4:
        label_txt = 'Square'
        AWGAMakeSquare()
    if AWGAShape.get() == 5:
        label_txt = "StairStep"
        AWGAMakeStair()
    if AWGAShape.get() == 9:
        label_txt = "Impulse"
        AWGAMakeImpulse()
    if AWGAShape.get() == 11:
        label_txt = "Trapezoid"
        AWGAMakeTrapazoid()
    if AWGAShape.get() == 15:
        label_txt = "SSQ Pulse"
        AWGAMakeSSQ()
    if AWGAShape.get() == 12:
        label_txt = "U-D Ramp"
        AWGAMakeUpDownRamp()
    if AWGAShape.get() == 17:
        label_txt = "Ramp"
        AWGAMakeRamp()
    if AWGAShape.get() == 14:
        label_txt = "Fourier Series"
        AWGAMakeFourier()
    if AWGAShape.get() == 16:
        label_txt = "Sin X/X"
        AWGAMakeSinc()
    if AWGAShape.get() == 7:
        label_txt = "UU Noise"
        AWGAMakeUUNoise()
    if AWGAShape.get() == 8:
        label_txt = "UG Noise"
        AWGAMakeUGNoise()
    if AWGAShape.get() == 10:
        label_txt = "Math"
        AWGAMakeMath()
    if AWGAShape.get() == 6:
        label_txt = "CSV File"
        AWGAReadFile()
    if AWGAShape.get() == 13:
        label_txt = "WAV File"
        AWGAReadWAV()
    label_txt = label_txt + " Shape"
    AWGAModeLabel.config(text = label_txt ) # change displayed value
#
    InvGain = -1.0 * AWGAgain
    AWGAbinform = AWGAwaveform * InvGain
    AWGAbinform = bytearray(numpy.array(AWGAbinform,dtype="int16"))
    AWGALength.config(text = "L = " + str(int(len(AWGAbinform)/2))) # change displayed value
    m2k_dac_a.attrs["dma_sync"].value = '1' 
    m2k_dac_b.attrs["dma_sync"].value = '1'
    blenght = int(len(AWGAbinform)/2)
    if blenght < 10:
        blenght = 100
    try:
        Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
    except:
        del(Buff0) # delete old buffer and make a new one
        Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
    Buff0.write(AWGAbinform)
    Buff0.push()
    #
    blenght = int(len(AWGBbinform)/2)
    if blenght > 10:
        try:
            Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
        except:
            del(Buff1) # delete old buffer and make a new one
            Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
        Buff1.write(AWGBbinform)
        Buff1.push()
    m2k_dac_a.attrs["dma_sync"].value = '0' # resyn AWG channels
    m2k_dac_b.attrs["dma_sync"].value = '0'
    # 
def UpdateAWGAT(temp):
    UpdateAWGA()
    
def BAWGBAmpl(temp):
    global AWGBAmplEntry, AWGBAmplvalue

    try:
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
        if AWGBAmplvalue > 5.00:
            AWGBAmplvalue = 5.00
            AWGBAmplEntry.delete(0,"end")
            AWGBAmplEntry.insert(0, AWGBAmplvalue)
        if AWGBAmplvalue < -5.00:
            AWGBAmplvalue = -5.00
            AWGBAmplEntry.delete(0,"end")
            AWGBAmplEntry.insert(0, AWGBAmplvalue)   
    except:
        AWGBAmplEntry.delete(0,"end")
        AWGBAmplEntry.insert(0, AWGBAmplvalue)
    
def BAWGBOffset(temp):
    global AWGBOffsetEntry, AWGBOffsetvalue

    try:
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
        if AWGBOffsetvalue > 5.00:
            AWGBOffsetvalue = 5.00
            AWGBOffsetEntry.delete(0,"end")
            AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
        if AWGBOffsetvalue < -5.00:
            AWGBOffsetvalue = -5.00
            AWGBOffsetEntry.delete(0,"end")
            AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
    except:
        AWGBOffsetEntry.delete(0,"end")
        AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
    
def BAWGBFreq(temp):
    global AWGBFreqEntry, AWGBFreqvalue, AWGBSampleRate, m2k_dac_b, AWGBgain, AWGBgain7M, AWGBgain75M

    try:
        AWGBFreqvalue = float(eval(AWGBFreqEntry.get()))
    except:
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)

    if AWGBFreqvalue > 25000000: # max freq is 25 MHz
        AWGBFreqvalue = 25000000
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue <= 0: # Set negative frequency entry to 0
        AWGBFreqvalue = 1
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue <= 10000: # 10 times 7500
        AWGBSampleRate = 7500000
        AWGBgain = AWGBgain7M
##    elif AWGBFreqvalue > 7500 and AWGBFreqvalue < 75000: # 10 times 75000
##        AWGBSampleRate = 7500000
    elif AWGBFreqvalue > 10000 and AWGBFreqvalue < 25000000: # 10 times 750000
        AWGBSampleRate = 75000000
        AWGBgain = AWGBgain75M
    m2k_dac_b.attrs["sampling_frequency"].value = str(AWGBSampleRate)

def BAWGBPhaseDelay():
    global AWGbPhaseDelay, phaseblab, awgbph, awgbdel

    if AWGBPhaseDelay.get() == 0:
        phaseblab.configure(text="Deg")
        awgbph.configure(style="WPhase.TRadiobutton")
        awgbdel.configure(style="GPhase.TRadiobutton")
    elif AWGBPhaseDelay.get() == 1:
        phaseblab.configure(text="mSec")
        awgbph.configure(style="GPhase.TRadiobutton")
        awgbdel.configure(style="WPhase.TRadiobutton")
        
def BAWGBPhase(temp):
    global AWGBPhaseEntry, AWGBPhasevalue

    try:
        AWGBPhasevalue = float(eval(AWGBPhaseEntry.get()))
    except:
        AWGBPhaseEntry.delete(0,"end")
        AWGBPhaseEntry.insert(0, AWGBPhasevalue)

    if AWGBPhasevalue > 360: # max phase is 360 degrees
        AWGBPhasevalue = 360
        AWGBPhaseEntry.delete(0,"end")
        AWGBPhaseEntry.insert(0, AWGBPhasevalue)
    if AWGBPhasevalue < 0: # min phase is 0 degrees
        AWGBPhasevalue = 0
        AWGBPhaseEntry.delete(0,"end")
        AWGBPhaseEntry.insert(0, AWGBPhasevalue)
    
def BAWGBDutyCycle(temp):
    global AWGBDutyCycleEntry, AWGBDutyCyclevalue, AWGBShape

    try:
        AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))/100
    except:
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)

    if AWGBDutyCyclevalue > 1 and AWGBShape.get()!= 14: # max duty cycle is 100%
        AWGBDutyCyclevalue = 1
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue*100)
    if AWGBDutyCyclevalue < 0: # min duty cycle is 0%
        AWGBDutyCyclevalue = 0
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
#
def AWGBReadFile():
    global AWGBwaveform, AWGBLength, awgwindow, AWGBSampleRate, AWGBgain
    global AWGBgain75M, AWGBgain7M, AWGBgain750K, AWGBgain75K

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
    RequestRate = askstring("Pick Sample Rate", "Select sample rate from\n75000000\n7500000\n750000\n75000\nEnter Value:\n", initialvalue=750000, parent=awgwindow)
    try:
        AWGBSampleRate = int(RequestRate)
    except:
        AWGBSampleRate = 75000
    if AWGBSampleRate == 75000000:
        AWGBgain = AWGBgain75M
    if AWGBSampleRate == 7500000:
        AWGBgain = AWGBgain7M
    if AWGBSampleRate == 750000:
        AWGBgain = AWGBgain750K
    if AWGBSampleRate == 75000:
        AWGBgain = AWGBgain75K
    m2k_dac_b.attrs["sampling_frequency"].value = str(AWGBSampleRate)
    AWGBwaveform = []
    ColumnNum = 0
    ColumnSel = 0
    for row in csv_f:
        if len(row) > 1 and ColumnSel == 0:
            RequestColumn = askstring("Which Column?", "File contains 1 to " + str(len(row)) + " columns\n\nEnter column number to import:\n", initialvalue=1, parent=awgwindow)
            ColumnNum = int(RequestColumn) - 1
            ColumnSel = 1
        try:
            AWGBwaveform.append(float(row[ColumnNum]))
        except:
            print 'skipping non-numeric row'
    AWGBwaveform = numpy.array(AWGBwaveform)
    CSVFile.close()

def AWGBReadWAV():
    global AWGBwaveform, AWGBLength, awgwindow
    global AWGBSampleRate, m2k_dac_b, AWGBOffsetvalue, AWGBAmplvalue
    global AWGBgain75M, AWGBgain7M, AWGBgain750K, AWGBgain75K, AWGBgain

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)

    ScaleFactor = (5.0 / 32768.0) # (AWGBOffsetvalue-AWGBAmplvalue)/20.0
# Read values from WAV file
    filename = askopenfilename(defaultextension = ".wav", filetypes=[("WAV files", "*.wav")], parent=awgwindow)
    try:
        spf = wave.open(filename,'r')
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
        return()
    #If Stereo
    if spf.getnchannels() == 2:
        showwarning("WARNING","Only mono files supported!", parent=awgwindow)
        return()
    RequestRate = askstring("Pick Sample Rate", "Select sample rate from\n75000000\n7500000\n750000\n75000\nEnter Value:\n", initialvalue=750000, parent=awgwindow)
    try:
        AWGBSampleRate = float(RequestRate)
    except:
        AWGBSampleRate = 75000
    if AWGBSampleRate == 75000000:
        AWGBgain = AWGBgain75M
    if AWGBSampleRate == 7500000:
        AWGBgain = AWGBgain7M
    if AWGBSampleRate == 750000:
        AWGBgain = AWGBgain750K
    if AWGBSampleRate == 75000:
        AWGBgain = AWGBgain75K
    m2k_dac_b.attrs["sampling_frequency"].value = str(AWGBSampleRate)
    AWGBwaveform = []
    #Extract Raw Audio from Wav File
    Length = spf.getnframes()
    if Length > 90000: # limit to first 90K samples
        Length = 90000
    signal = spf.readframes(Length)
    WAVsignal = numpy.fromstring(signal, 'Int16') # convert strings to Int
    # offset and scale for -5, 5 V range
    AWGBwaveform = numpy.array(WAVsignal)
    AWGBwaveform = AWGBwaveform * ScaleFactor
    spf.close()

def AWGBWriteFile():
    global AWGBwaveform, AWGBLength, awgwindow

    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    numpy.savetxt(filename, AWGBwaveform, delimiter=",", fmt='%2.4f')

def AWGBEnterMath():
    global AWGAwaveform, AWGBSampleRate, VBuffA, VBuffB, VFilterA, VFilterB
    global AWGBwaveform, VmemoryA, VmemoryB, ImemoryA, ImemoryB, AWGBMathString
    global FFTBuffA, FFTBuffB, FFTwindowshape, AWGBLength, awgwindow
    global DFiltACoef, DFiltBCoef, AWGBgain, AWGBoffset

    TempString = AWGBMathString
    AWGBMathString = askstring("AWG 2 Math Formula", "Current Formula: " + AWGBMathString + "\n\nNew Formula:\n", initialvalue=AWGBMathString, parent=awgwindow)
    if (AWGBMathString == None):         # If Cancel pressed, then None
        AWGBMathString = TempString
        return
#
def AWGBMakeMath():
    global AWGAwaveform, AWGBSampleRate, VBuffA, VBuffB, VFilterA, VFilterB
    global AWGBwaveform, VmemoryA, VmemoryB, ImemoryA, ImemoryB, AWGBMathString
    global FFTBuffA, FFTBuffB, FFTwindowshape, AWGBLength, awgwindow
    global DFiltACoef, DFiltBCoef, AWGBgain, AWGBoffset

    AWGBwaveform = eval(AWGBMathString)
    AWGBwaveform = numpy.array(AWGBwaveform)
#
def AWGBMakeDC():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset, phaseblab, duty2lab
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 1.0

    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
        
    MaxV = AWGBOffsetvalue 
    AWGBwaveform = []
    Width = int(AWGBperiodvalue)
    if Width <=0:
        Width = 1
    for i in range(Width):
        AWGBwaveform.append(MaxV)
    AWGBwaveform = numpy.array(AWGBwaveform)
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
#
def AWGBMakeSine():
    global AWGBwaveform, AWGBSampleRate, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBperiodvalue
    global AWGBDutyCyclevalue, AWGBFreqvalue, duty2lab, AWGBgain, AWGBoffset, AWGBPhaseDelay, AWGBperiodvalue
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)

    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 10.0

    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
    Cycles = int(37500/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    RecLength = Cycles * AWGBperiodvalue
    AWGBwaveform = []
    AWGBwaveform = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    amplitude = (AWGBOffsetvalue-AWGBAmplvalue) / 2.0
    offset = (AWGBOffsetvalue+AWGBAmplvalue) / 2.0
    AWGBwaveform = (AWGBwaveform * amplitude) + offset # scale and offset the waveform
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    BAWGBPhaseDelay()
    duty2lab.config(text="%")
#
def AWGBMakeFourier():
    global AWGBwaveform, AWGBSampleRate, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength
    global AWGBDutyCyclevalue, AWGBFreqvalue, duty2lab, AWGBgain, AWGBoffset
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBDutyCycle(temp)
    
    Max_term = AWGBDutyCyclevalue*100
    AWGBwaveform = []
    AWGBwaveform = numpy.cos(numpy.linspace(0, 2*numpy.pi, AWGBSampleRate/AWGBFreqvalue)) # the fundamental
    k = 3
    while k <= Max_term:
        # Add odd harmonics up to max_term
        Harmonic = (math.sin(k*numpy.pi/2)/k)*(numpy.cos(numpy.linspace(0, k*2*numpy.pi, AWGBSampleRate/AWGBFreqvalue)))
        AWGBwaveform = AWGBwaveform + Harmonic
        k = k + 2 # skip even numbers
    amplitude = (AWGBOffsetvalue-AWGBAmplvalue) / 2.0
    offset = (AWGBOffsetvalue+AWGBAmplvalue) / 2.0
    AWGBwaveform = (AWGBwaveform * amplitude) + offset # scale and offset the waveform
    duty2lab.config(text="Harmonics")
#
def AWGBMakeSinc():
    global AWGBwaveform, AWGBSampleRate, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBperiodvalue
    global AWGBDutyCyclevalue, AWGBFreqvalue, duty2lab, AWGBgain, AWGBoffset, AWGBPhaseDelay, AWGBperiodvalue
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)

    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
    Cycles = AWGBDutyCyclevalue*100
    NCycles = -1 * Cycles
    AWGBwaveform = []
    AWGBwaveform = numpy.sinc(numpy.linspace(NCycles, Cycles, AWGBSampleRate/AWGBFreqvalue))
    amplitude = (AWGBOffsetvalue-AWGBAmplvalue) / 2.0
    offset = (AWGBOffsetvalue+AWGBAmplvalue) / -2.0
    AWGBwaveform = (AWGBwaveform * amplitude) + offset # scale and offset the waveform
    Cycles = int(37500/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    if Cycles > 1:
        Extend = int((Cycles-1.0)*AWGBperiodvalue/2.0)
        AWGBwaveform = numpy.pad(AWGBwaveform, (Extend,Extend), 'wrap')
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    BAWGBPhaseDelay()
    duty2lab.config(text="Cycles")
#
def AWGBMakeSSQ():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset, phaseblab, duty2lab

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
        
    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
    Cycles = int(37500/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1    
    MaxV = AWGBOffsetvalue
    MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*AWGBSampleRate/1000)
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBperiodvalue * (1.0-AWGBDutyCyclevalue))
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int((AWGBperiodvalue - PulseWidth - SlopeValue)/2.0)
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepAmp = (MaxV - MinV)/2.0
    StepOff = (MaxV + MinV)/2.0
    AWGBwaveform = StepAmp * (numpy.cos(numpy.linspace(0, 2*numpy.pi, SlopeValue*2))) + StepOff
    MidArray = numpy.ones(PulseWidth) * MinV
    AWGBwaveform = numpy.insert(AWGBwaveform, SlopeValue, MidArray)
    AWGBwaveform = numpy.pad(AWGBwaveform, (Remainder, Remainder), 'edge')
    if Cycles > 1:
        Extend = int((Cycles-1.0)*AWGBperiodvalue/2.0)
        AWGBwaveform = numpy.pad(AWGBwaveform, (Extend,Extend), 'wrap')
    # AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    duty2lab.config(text="%")
    phaseblab.config(text = "Rise Time")
#
def AWGBMakeSquare():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset, phaseblab, duty2lab
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
        
    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
    Cycles = int(37500/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    MaxV = AWGBOffsetvalue
    MinV = AWGBAmplvalue
    AWGBwaveform = []
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    for j in range(Cycles):
        for i in range(PulseWidth):
            AWGBwaveform.append(MaxV)
        for i in range(Remainder):
            AWGBwaveform.append(MinV)
    AWGBwaveform = numpy.array(AWGBwaveform)
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    BAWGBPhaseDelay()
    duty2lab.config(text="%")
#
def AWGBMakeTrapazoid():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset, phaseblab, duty2lab
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
        
    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
    Cycles = int(37500/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    MaxV = AWGBOffsetvalue
    MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*AWGBSampleRate/1000)
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth) - SlopeValue
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    for j in range(Cycles):
        SampleValue = MinV
        for i in range(SlopeValue):
            AWGBwaveform.append(SampleValue)
            SampleValue = SampleValue + StepValue
        for i in range(PulseWidth):
            AWGBwaveform.append(MaxV)
        for i in range(SlopeValue):
            AWGBwaveform.append(SampleValue)
            SampleValue = SampleValue - StepValue
        for i in range(Remainder):
            AWGBwaveform.append(MinV)
    AWGBwaveform = numpy.array(AWGBwaveform)
    # AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    duty2lab.config(text="%")
    phaseblab.config(text = "Rise Time")
#
#
def AWGBMakeRamp():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset, phaseblab, duty2lab
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
        
    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
    Cycles = int(37500/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    MaxV = AWGBOffsetvalue
    MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*AWGBSampleRate/1000) # convert mS to samples
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepValue = (MaxV - MinV) / SlopeValue
    for j in range(Cycles):
        SampleValue = MinV
        for i in range(SlopeValue):
            AWGBwaveform.append(SampleValue)
            SampleValue = SampleValue + StepValue
        for i in range(PulseWidth):
            AWGBwaveform.append(MaxV)
        for i in range(Remainder):
            AWGBwaveform.append(MinV)
    AWGBwaveform = numpy.array(AWGBwaveform)
    # AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    duty2lab.config(text="%")
    phaseblab.config(text = "Slope Time")
#
def AWGBMakeUpDownRamp():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset, duty2lab
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
    Cycles = int(37500/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    MaxV = AWGBOffsetvalue
    MinV = AWGBAmplvalue
    AWGBwaveform = []
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGBperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    UpStepValue = (MaxV - MinV) / PulseWidth
    DownStepValue = (MaxV - MinV) / Remainder
    SampleValue = MaxV # MinV
    for j in range(Cycles):
        SampleValue = MaxV # MinV
        for i in range(PulseWidth):
            AWGBwaveform.append(SampleValue)
            SampleValue = SampleValue - UpStepValue
        for i in range(Remainder):
            AWGBwaveform.append(SampleValue)
            SampleValue = SampleValue + DownStepValue
    AWGBwaveform = numpy.array(AWGBwaveform)
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    BAWGBPhaseDelay()
    duty2lab.config(text = "Symmetry")
#
def AWGBMakeTriangle():
    global AWGBDutyCycleEntry
    
    AWGBDutyCycleEntry.delete(0,"end")
    AWGBDutyCycleEntry.insert(0, 50)
    AWGBMakeUpDownRamp()
#
def AWGBMakeSawtooth():
    global AWGBDutyCycleEntry
    
    AWGBDutyCycleEntry.delete(0,"end")
    AWGBDutyCycleEntry.insert(0, 99)
    AWGBMakeUpDownRamp()
#
def AWGBMakeImpulse():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    MaxV = AWGBOffsetvalue
    MinV = AWGBAmplvalue
    MidV = (MinV+MaxV)/2
    AWGBwaveform = []
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue / 2.0)
    if AWGBPhaseDelay.get() == 0:
        DelayValue = int(AWGBperiodvalue*(AWGBPhasevalue/360.0))
    elif AWGBPhaseDelay.get() == 1:
        DelayValue = int(AWGBPhasevalue*100)
    for i in range(DelayValue-PulseWidth):
        AWGBwaveform.append(MidV)
    for i in range(PulseWidth):
        AWGBwaveform.append(MaxV)
    for i in range(PulseWidth):
        AWGBwaveform.append(MinV)
    DelayValue = int(AWGBperiodvalue-DelayValue)
    for i in range(DelayValue-PulseWidth):
        AWGBwaveform.append(MidV)
    AWGBwaveform = numpy.array(AWGBwaveform)
#
def AWGBMakeStair():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGBSampleRate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWGBgain, AWGBoffset, duty2lab
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGBSampleRate / 1000
        
    MaxV = AWGBOffsetvalue 
    MinV = AWGBAmplvalue
    AWGBwaveform = []
    Treads = int(AWGBDutyCyclevalue*100)
    if Treads < 2:
        Treads = 2
    TreadWidth = int(AWGBperiodvalue / Treads)
    TreadHight = (MaxV-MinV)/(Treads-1)
    for i in range(Treads):
        for j in range(TreadWidth):
            AWGBwaveform.append(MinV)
        MinV = MinV + TreadHight
#
    AWGBwaveform = numpy.array(AWGBwaveform)
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    BAWGBPhaseDelay()
    duty2lab.config(text = "Steps")
    
def AWGBMakeUUNoise():
    global AWGBwaveform, AWGBSampleRate, AWGBAmplvalue, AWGBOffsetvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue
    global AWGBgain, AWGBoffset
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    if AWGBAmplvalue > AWGBOffsetvalue:
        MinV = AWGBOffsetvalue
        MaxV = AWGBAmplvalue
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = numpy.random.uniform(MinV, MaxV, int(AWGBperiodvalue))
    
def AWGBMakeUGNoise():
    global AWGBwaveform, AWGBSampleRate, AWGBAmplvalue, AWGBOffsetvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue
    global AWGBgain, AWGBoffset
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
        
    if AWGBAmplvalue > AWGBOffsetvalue:
        MinV = AWGBOffsetvalue
        MaxV = AWGBAmplvalue 
    else:
        MaxV = AWGBOffsetvalue 
        MinV = AWGBAmplvalue
    AWGBwaveform = numpy.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGBperiodvalue))
#
def UpdateAWGB():
    global AWGBAmplvalue, AWGBOffsetvalue,  AWGAwaveform
    global AWGBFreqvalue, AWGBPhasevalue, AWGBPhaseDelay
    global AWGBDutyCyclevalue, FSweepMode, AWGBRepeatFlag, dac_b_pd
    global AWGBSampleRate, AWG2Offset, AWGBWave, AWGBMode, AWGBwaveform
    global ctx, ad5625, m2k_AWG2pd, m2k_fabric, Buff0, Buff1, m2k_dac_a, m2k_dac_b
    global AWGBMode, AWGBIOMode, AWGBModeLabel, DevID, HWRevOne
    global AWGBShape, AWGAbinform, AWGAgain, AWGBgain, AWGBbinform
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGBSampleRate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    if AWGBMode.get() == 0: # power up AWG 1
        m2k_AWG2pd.attrs["powerdown"].value = '0'
        AWG2Offset.attrs["powerdown"].value = '0'
        dac_b_pd.attrs["powerdown"].value = '0'
    elif AWGBMode.get() == 2: # Power down AWG 1
        AWG2Offset.attrs["powerdown"].value = '1'
        m2k_AWG2pd.attrs["powerdown"].value = '1'
        dac_b_pd.attrs["powerdown"].value = '1'
    if AWGBShape.get() == 0:
        label_txt = 'DC'
        AWGBMakeDC()
    if AWGBShape.get() == 1:
        label_txt = 'Sine'
        AWGBMakeSine()
    if AWGBShape.get() == 2:
        label_txt = 'Triangle'
        AWGBMakeTriangle()
    if AWGBShape.get() == 3:
        label_txt = 'Sawtooth'
        AWGBMakeSawtooth()
    if AWGBShape.get() == 4:
        label_txt = 'Square'
        AWGBMakeSquare()
    if AWGBShape.get() == 5:
        label_txt = "StairStep"
        AWGBMakeStair()
    if AWGBShape.get() == 9:
        label_txt = "Impulse"
        AWGBMakeImpulse()
    if AWGBShape.get() == 11:
        label_txt = "Trapezoid"
        AWGBMakeTrapazoid()
    if AWGBShape.get() == 15:
        label_txt = "SSQ Pulse"
        AWGBMakeSSQ()
    if AWGBShape.get() == 12:
        label_txt = "U-D Ramp"
        AWGBMakeUpDownRamp()
    if AWGBShape.get() == 17:
        label_txt = "Ramp"
        AWGBMakeRamp()
    if AWGBShape.get() == 14:
        label_txt = "Fourier Series"
        AWGBMakeFourier()
    if AWGBShape.get() == 16:
        label_txt = "Sin X/X"
        AWGBMakeSinc()
    if AWGBShape.get() == 7:
        label_txt = "UU Noise"
        AWGBMakeUUNoise()
    if AWGBShape.get() == 8:
        label_txt = "UG Noise"
        AWGBMakeUGNoise()
    if AWGBShape.get() == 10:
        label_txt = "Math"
        AWGBMakeMath()
    if AWGBShape.get() == 6:
        label_txt = "CSV File"
        AWGBReadFile()
    if AWGBShape.get() == 13:
        label_txt = "WAV File"
        AWGBReadWAV()
    label_txt = label_txt + " Shape"
    AWGBModeLabel.config(text = label_txt ) # change displayed value
#
    InvGain = -1.0 * AWGBgain
    AWGBbinform = AWGBwaveform * InvGain
    AWGBbinform = bytearray(numpy.array(AWGBbinform,dtype="int16"))
    AWGBLength.config(text = "L = " + str(int(len(AWGBbinform)/2))) # change displayed value
    m2k_dac_a.attrs["dma_sync"].value = '1' 
    m2k_dac_b.attrs["dma_sync"].value = '1'
    blenght = int(len(AWGBbinform)/2)
    if blenght < 10:
        blenght = 100
    try:
        Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
    except:
        del(Buff1) # delete old buffer and make a new one
        Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
    Buff1.write(AWGBbinform)
    Buff1.push()
    blenght = int(len(AWGAbinform)/2)
    if blenght > 10:
        try:
            Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
        except:
            del(Buff0) # delete old buffer and make a new one
            Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
        Buff0.write(AWGAbinform)
        Buff0.push()
    m2k_dac_a.attrs["dma_sync"].value = '0' # resyn AWG channels
    m2k_dac_b.attrs["dma_sync"].value = '0'
    #
def UpdateAWGBT(temp):
    UpdateAWGB()
                
def BAWGEnab():
    global AWGAMode, AWGBMode

    UpdateAWGA()
    UpdateAWGB()
#
# ======= Spectrum Analyzer functions ===========
#
def BSaveScreenSA():
    global CANVASwidthF, CANVASheightF, freqwindow
    global COLORtext
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")], parent=freqwindow)
    Orient = askyesno("Rotation","Save in Landscape (Yes) or Portrait (No):\n", parent=freqwindow)
    if MarkerNum > 0 or ColorMode.get() > 0:
        Freqca.postscript(file=filename, height=CANVASheightF, width=CANVASwidthF, colormode='color', rotate=Orient)
    else: # temp change text color to black
        COLORtext = "#000000"
        UpdateFreqScreen()
        # save postscript file
        Freqca.postscript(file=filename, height=CANVASheightF, width=CANVASwidthF, colormode='color', rotate=Orient)
        # 
        COLORtext = "#ffffff"
        UpdateFreqScreen()
#
def Bnot():
    print "Routine not made yet"

def BShowCurvesAllSA():
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P
    ShowC1_VdB.set(1)
    ShowC1_P.set(1)
    ShowC2_VdB.set(1)
    ShowC2_P.set(1)

def BShowCurvesNoneSA():
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P
    ShowC1_VdB.set(0)
    ShowC1_P.set(0)
    ShowC2_VdB.set(0)
    ShowC2_P.set(0)
    
def BNormalmode():
    global RUNstatus
    global FreqTraceMode

    FreqTraceMode.set(1)
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)
    
def BPeakholdmode():
    global RUNstatus
    global FreqTraceMode

    FreqTraceMode.set(2)
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)
    
def BAveragemode():
    global RUNstatus, TRACEaverage, FreqTraceMode, freqwindow

    FreqTraceMode.set(3)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)

def BResetFreqAvg():
    global FreqTraceMode, TRACEresetFreq

    if FreqTraceMode.get()==3:
        TRACEresetFreq = True
        
def BSTOREtraceSA():
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMathSA
    global T1Fline, T2Fline, T1FRline, T2FRline, TFRMline, TFMline
    global T1Pline, T2Pline, T1PRline, T2PRline
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    
    if ShowC1_VdB.get() == 1:
        T1FRline = T1Fline
        PeakxRA = PeakxA
        PeakyRA = PeakyA
        PeakdbRA = PeakdbA
        PeakfreqRA = PeakfreqA
    if ShowC2_VdB.get() == 1:
        T2FRline = T2Fline
        PeakxRB = PeakxB
        PeakyRB = PeakyB
        PeakdbRB = PeakdbB
        PeakfreqRB = PeakfreqB
    if ShowC1_P.get() == 1:
        T1PRline = T1Pline
    if ShowC2_P.get() == 1:
        T2PRline = T2Pline
    if ShowMathSA.get() > 0:
        TFRMline = TFMline
        PeakxRM = PeakxM
        PeakyRM = PeakyM
        PeakRMdb = PeakMdb
        PeakfreqRM = PeakfreqM

    UpdateFreqTrace()           # Always Update
#
def BSTOREtraceBP():
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMathBP
    global TAFline, TBFline, TAFRline, TBFRline, TBPRMline, TBPMline
    global TAPline, TBPline, TAPRline, TBPRline
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    
    if ShowCA_VdB.get() == 1:
        TAFRline = TAFline
        PeakxRA = PeakxA
        PeakyRA = PeakyA
        PeakdbRA = PeakdbA
        PeakfreqRA = PeakfreqA
    if ShowCB_VdB.get() == 1:
        TBFRline = TBFline
        PeakxRB = PeakxB
        PeakyRB = PeakyB
        PeakdbRB = PeakdbB
        PeakfreqRB = PeakfreqB
    if ShowCA_P.get() == 1:
        TAPRline = TAPline
    if ShowCB_P.get() == 1:
        TBPRline = TBPline
    if ShowMathBP.get() > 0:
        TBPRMline = TBPMline
        PeakxRM = PeakxM
        PeakyRM = PeakyM
        PeakRMdb = PeakMdb
        PeakfreqRM = PeakfreqM

    UpdateBodeTrace()           # Always Update
#
def BCSVfile(): # Store the trace as CSV file [frequency, magnitude or dB value]
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep, FBins, bodewindow
    global SAMPLErate, ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P
    
    # Set the TRACEsize variable
    if ShowCA_VdB.get() == 1:
        TRACEsize = len(FSweepAdB)     # Set the trace length
    elif ShowCA_VdB.get() == 1:
        TRACEsize = len(FSweepBdB)
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        return()
# ask if save as magnitude or dB
    dB = askyesno("Mag or dB: ","Save amplidude data as dB (Yes) or Mag (No):\n", parent=bodewindow)
# Yes 1 = dB, No 0 = Mag
    # Make the file name and open it
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
    filename = "Bode-" + tme
    filename = filename + ".csv"
    # open file to save data
    filename = asksaveasfilename(initialfile = filename, defaultextension = ".csv",
                                 filetypes=[("Comma Separated Values", "*.csv")], parent=bodewindow)
    DataFile = open(filename,'a')  # Open output file
    HeaderString = 'Frequency-#, '
    if ShowCA_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'C1-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'C1-Mag, '
    if ShowCB_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'C2-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'C2-Mag, '
    if ShowCA_P.get() == 1:
        HeaderString = HeaderString + 'Phase 1-2, '
    if ShowCB_P.get() == 1:
        HeaderString = HeaderString + 'Phase 2-1, '
    HeaderString = HeaderString + '\n'
    DataFile.write( HeaderString )   

    n = 0
    while n < len(FSweepAdB):
        F = FBins[FStep[n]] # look up frequency bin in list of bins
        txt = str(F)
        if ShowCA_VdB.get() == 1:
            if dB == 1:
                V = 10 * math.log10(float(FSweepAdB[n])) + 17  # Add 17 dB for max value of +10 dB
            else:
                V = 7.079458 * math.sqrt(float(FFTresultA[n]))   # scale to Vrms
                #V = 50.12 * float(FFSweepAdB[n])# scale to Vrms
            txt = txt + "," + str(V) 
        if ShowCB_VdB.get() == 1:
            if dB == 1:
                V = 10 * math.log10(float(FSweepBdB[n])) + 17  # Add 17 dB for max value of +10 dB
            else:
                V = 7.079458 * math.sqrt(float(FFTresultA[n]))   # scale to Vrms
                #V = 50.12 * float(FSweepBdB[n]) # scale to Vrms
            txt = txt  + "," + str(V)
        if ShowCA_P.get() == 1:
            RelPhase = FSweepAPh[n]#-FSweepBPh[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        if ShowCB_P.get() == 1:
            RelPhase = FSweepBPh[n]#-FSweepAPh[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        txt = txt + "\n"
        DataFile.write(txt)
        n = n + 1    

    DataFile.close()                           # Close the file

def BNumDiv():
    global Vdiv, freqwindow
    
    UpdateFreqTrace()

def BStartSA():
    global RUNstatus, PowerStatus, PwrBt, freqwindow
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMathSA, DevID, FWRevOne

    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    else:
        if ShowC1_VdB.get() == 0 and ShowC2_VdB.get() == 0 and ShowMathSA.get() == 0 and ShowC1_P.get() == 0 and ShowC2_P.get() == 0:
            showwarning("WARNING","Select at least one trace first",  parent=freqwindow)
            return()    
        if RUNstatus.get() == 0:
            RUNstatus.set(1)
#
    UpdateFreqAll()          # Always Update

def BStopSA():
    global RUNstatus
    
    if (RUNstatus.get() == 1):
        RUNstatus.set(0)
    elif (RUNstatus.get() == 2):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 3):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 4):
        RUNstatus.set(3)
    UpdateFreqAll()          # Always Update
    
def Blevel1():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() - 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def Blevel2():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() + 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def Blevel3():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() - 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def Blevel4():
    global DBlevel
    global RUNstatus

    DBlevel.set(DBlevel.get() + 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def BZeroStuff():
    global RUNstatus
    global ZEROstuffing, freqwindow, bodewindow
    
    if (RUNstatus.get() != 0):

        UpdateFreqScreen()          # Always Update    

def Bsamples1():
    global RUNstatus, SpectrumScreenStatus, IAScreenStatus
    global SMPfftpwrTwo, SMPfft, FFTwindow
    global TRACEresetFreq
    
    if FFTwindow.get() != 8:
        if (SMPfftpwrTwo.get() > 6):  # Min 64
            SMPfftpwrTwo.set(SMPfftpwrTwo.get() - 1)
            TRACEresetFreq = True   # Reset trace peak and trace average
            SMPfft = 2 ** int(SMPfftpwrTwo.get())

    if RUNstatus.get() == 0:      # Update if stopped
        if SpectrumScreenStatus.get() > 0:
            UpdateFreqScreen()
        if IAScreenStatus.get() > 0:
            UpdateIAScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)

def Bsamples2():
    global RUNstatus
    global SMPfftpwrTwo, SMPfft, FFTwindow
    global TRACEresetFreq
      
    if FFTwindow.get() != 8:
        if (SMPfftpwrTwo.get() < 16): # Max 65536
            SMPfftpwrTwo.set(SMPfftpwrTwo.get() + 1)
            TRACEresetFREQ = True   # Reset trace peak and trace average
            SMPfft = 2 ** int(SMPfftpwrTwo.get())

    if RUNstatus.get() == 0:      # Update if stopped
        if SpectrumScreenStatus.get() > 0:
            UpdateFreqScreen()
        if IAScreenStatus.get() > 0:
            UpdateIAScreen()
    if RUNstatus.get() == 2:      # Restart if running
        RUNstatus.set(4)

def BDBdiv1():
    global DBdivindex
    global RUNstatus
    
    if (DBdivindex.get() >= 1):
        DBdivindex.set(DBdivindex.get() - 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()

def BDBdiv2():
    global DBdivindex
    global DBdivlist
    global RUNstatus
    
    if (DBdivindex.get() < len(DBdivlist) - 1):
        DBdivindex.set(DBdivindex.get() + 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()
#Bode Plot controls
def BStartBP():
    global RUNstatus, LoopNum, PowerStatus, PwrBt, bodewindow
    global ShowCA_VdB, ShowCB_P, ShowCB_VdB, ShowCB_P, ShowMathBP, MinigenMode
    global FStep, FBins, NSteps, FSweepMode, HScaleBP, CutDC, AWGAMode, AWGAShape, AWGBMode, AWGBShape
    global BeginIndex, EndIndex
    global StartBodeEntry, StopBodeEntry, SweepStepBodeEntry, DevID, FWRevOne
    global HalfSAMPLErate, SAMPLErate, OldCH1Gain, OldCH2Gain, CH1GainSA, CH2GainSA

    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    else:
        if ShowCA_VdB.get() == 0 and ShowCB_VdB.get() == 0 and ShowMathBP.get() == 0:
            showwarning("WARNING","Select at least one trace first",  parent=bodewindow)
            return()    
        if CH1GainSA.get() == 0:
            m2k_adc0.attrs["gain"].value = 'high'
            ch1_multiplier = CH1_H_Gain
        else:
            m2k_adc0.attrs["gain"].value = 'low'
            ch1_multiplier = CH1_L_Gain
        if CH2GainSA.get() == 0:
            m2k_adc1.attrs["gain"].value = 'high'
            ch2_multiplier = CH2_H_Gain
        else:
            m2k_adc1.attrs["gain"].value = 'low'
            ch2_multiplier = CH2_L_Gain
        OldCH1Gain = CH1GainSA.get()
        OldCH2Gain = CH2GainSA.get()
        HalfSAMPLErate = SAMPLErate/2.0
        FBins = numpy.linspace(0, HalfSAMPLErate, num=16384)
#
        CutDC.set(1) # set to remove DC
        if FSweepMode.get() == 3:
            MinigenMode.set(0) # Set MiniGen shape to Sine
        try:
            NSteps.set(float(SweepStepBodeEntry.get()))
        except:
            SweepStepBodeEntry.delete(0,"end")
            SweepStepBodeEntry.insert(0, NSteps.get())
        try:
            EndFreq = float(StopBodeEntry.get())
        except:
            StopBodeEntry.delete(0,"end")
            StopBodeEntry.insert(0,10000)
            EndFreq = 10000
        try:
            BeginFreq = float(StartBodeEntry.get())
        except:
            StartBodeEntry.delete(0,"end")
            StartBodeEntry.insert(0,100)
            BeginFreq = 100
        if RUNstatus.get() == 0:
            RUNstatus.set(1)
            if FSweepMode.get() > 0:
                LoopNum.set(1)
                if FSweepMode.get() == 1: # set new CH-A frequency
                    AWGAFreqEntry.delete(0,END)
                    AWGAFreqEntry.insert(4, BeginFreq)
                    UpdateAWGA()
                if FSweepMode.get() == 2: # set new CH-B frequency
                    AWGBFreqEntry.delete(0,END)
                    AWGBFreqEntry.insert(4, BeginFreq)
                    UpdateAWGB()
                if NSteps.get() < 5:
                    NSteps.set(5)
                if HScaleBP.get() == 1:
                    LogFStop = math.log10(EndFreq) # EndIndex)
                    try:
                        LogFStart = math.log10(BeginFreq) # BeginIndex)
                    except:
                        LogFStart = 1.0
                    FStep = numpy.logspace(LogFStart, LogFStop, num=NSteps.get(), base=10.0)
                else:
                    FStep = numpy.linspace(BeginFreq, EndFreq, num=NSteps.get())
        # UpdateBodeAll()          # Always Update
#
def BStopBP():
    global RUNstatus
    
    if (RUNstatus.get() == 1):
        RUNstatus.set(0)
    elif (RUNstatus.get() == 2):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 3):
        RUNstatus.set(3)
    elif (RUNstatus.get() == 4):
        RUNstatus.set(3)
    UpdateBodeAll()          # Always Update
# 
def Blevel1BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() - 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def Blevel2BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() + 1)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def Blevel3BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() - 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def Blevel4BP():
    global DBlevelBP
    global RUNstatus

    DBlevelBP.set(DBlevelBP.get() + 10)
    
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def BDBdiv1BP():
    global DBdivindexBP
    global RUNstatus
    
    if (DBdivindexBP.get() >= 1):
        DBdivindexBP.set(DBdivindexBP.get() - 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()

def BDBdiv2BP():
    global DBdivindexBP
    global DBdivlist
    global RUNstatus
    
    if (DBdivindexBP.get() < len(DBdivlist) - 1):
        DBdivindexBP.set(DBdivindexBP.get() + 1)

    if RUNstatus.get() == 0:      # Update if stopped
        UpdateBodeTrace()
#
def BShowCurvesAllBP():
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P
    ShowCA_VdB.set(1)
    ShowCA_P.set(1)
    ShowCB_VdB.set(1)
    ShowCB_P.set(1)

def BShowCurvesNoneBP():
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P
    ShowCA_VdB.set(0)
    ShowCA_P.set(0)
    ShowCB_VdB.set(0)
    ShowCB_P.set(0)
# Bode Plot refresh
def UpdateBodeAll():        # Update Data, trace and screen
    global FFTBuffA, FFTBuffB
    global SMPfft
    
    # DoFFT()             # Fast Fourier transformation
    MakeBodeTrace()         # Update the traces
    UpdateBodeScreen()      # Update the screen 

def UpdateBodeTrace():      # Update trace and screen
    MakeBodeTrace()         # Update traces
    UpdateBodeScreen()      # Update the screen

def UpdateBodeScreen():     # Update screen with trace and text
    MakeBodeScreen()        # Update the screen    
#
# ============================= Freq Main routine ==========================================
def Analog_Freq_In():   # Read the audio from the stream and store the data into the arrays
    global ADsignal1, FFTBuffA, FFTBuffB, SMPfft
    global AWGSync, AWGAMode, AWGBMode, AWGAShape, AWGAIOMode, AWGBIOMode
    global AWGAFreqvalue, AWGBFreqvalue, FStepSync, FSweepSync
    global NSteps, LoopNum, FSweepMode, FStep, FBins
    global StartFreqEntry, StopFreqEntry, HoldOffentry, StartBodeEntry, StopBodeEntry
    global MaxSamples, OldShowSamples, OldCH1Gain, CH1GainSA, OldCH2Gain, CH2GainSA
    global RUNstatus, SingleShot, FSweepCont, SAMPLErate, OldSampleRate
    global AWGASampleRate, AWGBSampleRate, IAScreenStatus, SpectrumScreenStatus, BodeScreenStatus
    global OverRangeFlagA, OverRangeFlagB, BodeDisp, IADisp, FreqDisp, AWGAFreqEntry
    global DCA, DCB, InOffA, InGainA, InOffB, InGainB
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DigFiltA, DFiltACoef, DigFiltB, DFiltBCoef
    global BDSweepFile, FileSweepFreq, FileSweepAmpl, MinigenFout, MinigenScreenStatus
    global TimeBuffer, m2k_adc, SHOWsamples, ch1_multiplier, ch2_multiplier
    global m2k_adc4_trigger, m2k_adc5_trigger
    global CH1_H_Gain, CH1_L_Gain, CH2_H_Gain, CH2_L_Gain
    global CH1_H_Gain1K, CH1_L_Gain1K, CH2_H_Gain1K, CH2_L_Gain1K
    global CH1_H_Gain10K, CH1_L_Gain10K, CH2_H_Gain10K, CH2_L_Gain10K
    global CH1_H_Gain100K, CH1_L_Gain100K, CH2_H_Gain100K, CH2_L_Gain100K
    global CH1_H_Gain1M, CH1_L_Gain1M, CH2_H_Gain1M, CH2_L_Gain1M
    global CH1_H_Gain10M, CH1_L_Gain10M, CH2_H_Gain10M, CH2_L_Gain10M
    global CH1_H_Gain100M, CH1_L_Gain100M, CH2_H_Gain100M, CH2_L_Gain100M
    global ctx, logic, Dig0, Dig1
    
    OldShowSamples = SHOWsamples
    if FreqDisp.get() > 0:
        try:
            TryRate = 2*float(eval(StopFreqEntry.get()))
        except:
            TryRate = 100000
    elif FSweepMode.get() > 0 and BodeDisp.get() > 0: # Run Sweep Gen only if selected and Bode display is active
        if BDSweepFile.get() == 0:
            if LoopNum.get() <= len(FStep):
                try:
                    FregPoint = FStep[LoopNum.get()-1] # look up next frequency from list of bins
                except:
                    FregPoint = FBins[16383] # change this at some point
            else:
                FregPoint = FStep[0]
        else: # getting sweep freq and ampl from file
            if LoopNum.get() <= len(FileSweepFreq): #
                FreqIndex = int((FileSweepFreq[LoopNum.get()-1]*16384)/HalfSAMPLErate)
                FregPoint = FBins[FreqIndex] # look up next frequency from list of bins
                VRMSAmpl = 10**(FileSweepAmpl[LoopNum.get()-1]/20) # convert to V RMS 0 dBV = 1V RMS
            else:
                FregPoint = FBins[FileSweepFreq[0]]
                VRMSAmpl = 10**(FileSweepAmpl[0]/20) # convert to V RMS 0 dBV = 1V RMS
            VMax = 2.5 + (1.414*VRMSAmpl) # calculate positive peak assuming sine wave
            VMin = 2.5 - (1.414*VRMSAmpl) # calculate negative peak assuming sine wave
            if FSweepMode.get() == 1: # set new CH-A amplitude
                AWGAAmplEntry.delete(0,END)
                AWGAAmplEntry.insert(4, VMin)
                AWGAOffsetEntry.delete(0,END)
                AWGAOffsetEntry.insert(4, VMax)
            if FSweepMode.get() == 2: # set new CH-B amplitude
                AWGBAmplEntry.delete(0,END)
                AWGBAmplEntry.insert(4, VMin)
                AWGBOffsetEntry.delete(0,END)
                AWGBOffsetEntry.insert(4, VMax)
        if FSweepMode.get() == 1: # set new CH-A frequency
            AWGAFreqEntry.delete(0,END)
            AWGAFreqEntry.insert(4, FregPoint)
        if FSweepMode.get() == 2: # set new CH-B frequency
            AWGBFreqEntry.delete(0,END)
            AWGBFreqEntry.insert(4, FregPoint)
        if FSweepMode.get() == 3 and MinigenScreenStatus.get() > 0: # set new MiniGen frequency
            MinigenFout.delete(0,END)
            MinigenFout.insert(8, FregPoint)
            BSendMG()
        BAWGEnab()
        if FregPoint <= 1000.0:
            TryRate = 10000
        elif FregPoint > 1000.0 and FregPoint <= 10000.0:
            TryRate = 100000
        elif FregPoint > 10000.0 and FregPoint <= 100000.0:
            TryRate = 1000000
        elif FregPoint > 100000.0 and FregPoint <= 1000000.0:
            TryRate = 10000000
        elif FregPoint > 1000000.0 and FregPoint <= 10000000.0:
            TryRate = 100000000
        #
        if TryRate/FregPoint > 128: # was 16
            SMPfft = 16384
        elif TryRate/FregPoint > 64: # was 32
            SMPfft = 8192
        elif TryRate/FregPoint > 32: # was 64
            SMPfft = 4096
        else:
            SMPfft = 2048
        # time.sleep(0.2)
    elif IADisp.get() > 0:
        try:
            TryRate = 20*float(eval(AWGAFreqEntry.get()))
        except:
            TryRate = 100000
            AWGAFreqEntry.delete(0,END)
            AWGAFreqEntry.insert(0, 1000)
    #
    if TryRate <= 1000:
        NewSAMPLErate = 1000
        CH1_H_Gain = CH1_H_Gain1K
        CH1_L_Gain = CH1_L_Gain1K
        CH2_H_Gain = CH2_H_Gain1K
        CH2_L_Gain = CH2_L_Gain1K
    elif TryRate > 1000 and TryRate <= 10000:
        NewSAMPLErate = 10000
        CH1_H_Gain = CH1_H_Gain10K
        CH1_L_Gain = CH1_L_Gain10K
        CH2_H_Gain = CH2_H_Gain10K
        CH2_L_Gain = CH2_L_Gain10K
    elif TryRate > 10000 and TryRate <= 100000:
        NewSAMPLErate = 100000
        CH1_H_Gain = CH1_H_Gain100K
        CH1_L_Gain = CH1_L_Gain100K
        CH2_H_Gain = CH2_H_Gain100K
        CH2_L_Gain = CH2_L_Gain100K
    elif TryRate > 100000 and TryRate <= 1000000:
        NewSAMPLErate = 1000000
        CH1_H_Gain = CH1_H_Gain1M
        CH1_L_Gain = CH1_L_Gain1M
        CH2_H_Gain = CH2_H_Gain1M
        CH2_L_Gain = CH2_L_Gain1M 
    elif TryRate > 1000000 and TryRate <= 10000000:
        NewSAMPLErate = 10000000
        CH1_H_Gain = CH1_H_Gain10M
        CH1_L_Gain = CH1_L_Gain10M
        CH2_H_Gain = CH2_H_Gain10M
        CH2_L_Gain = CH2_L_Gain10M 
    elif TryRate > 10000000:
        NewSAMPLErate = 100000000
        CH1_H_Gain = CH1_H_Gain100M
        CH1_L_Gain = CH1_L_Gain100M
        CH2_H_Gain = CH2_H_Gain100M
        CH2_L_Gain = CH2_L_Gain100M 
    if NewSAMPLErate != SAMPLErate:
        SAMPLErate = NewSAMPLErate
        m2k_adc.attrs["oversampling_ratio"].value = str(OverSampleRate)
        m2k_adc.attrs["sampling_frequency"].value = str(SAMPLErate)
    # Do input probe Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
    try:
        InOffA = float(eval(CHAVOffsetEntry.get()))
    except:
        CHAVOffsetEntry.delete(0,END)
        CHAVOffsetEntry.insert(0, InOffA)
    try:
        InGainA = float(eval(CHAVGainEntry.get()))
    except:
        CHAVGainEntry.delete(0,END)
        CHAVGainEntry.insert(0, InGainA)
    try:
        InOffB = float(eval(CHBVOffsetEntry.get()))
    except:
        CHBVOffsetEntry.delete(0,END)
        CHBVOffsetEntry.insert(0, InOffB)
    try:
        InGainB = float(eval(CHBVGainEntry.get()))
    except:
        CHBVGainEntry.delete(0,END)
        CHBVGainEntry.insert(0, InGainB)
# Set input gain based on Vert scale /div
# get the vertical ranges
    try:
        CH1pdvRange = float(eval(CHAsb.get()))
    except:
        CHAsb.delete(0,END)
        CHAsb.insert(0, CH1vpdvRange)
    try:
        CH2pdvRange = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2vpdvRange)
    if OldCH1Gain != CH1GainSA.get():
        if CH1GainSA.get() == 0:
            m2k_adc0.attrs["gain"].value = 'high'
            ch1_multiplier = CH1_H_Gain
        else:
            m2k_adc0.attrs["gain"].value = 'low'
            ch1_multiplier = CH1_L_Gain
    if OldCH2Gain != CH2GainSA.get():
        if CH2GainSA.get() == 0:
            m2k_adc1.attrs["gain"].value = 'high'
            ch2_multiplier = CH2_H_Gain
        else:
            m2k_adc1.attrs["gain"].value = 'low'
            ch2_multiplier = CH2_L_Gain
    OldCH1Gain = CH1GainSA.get()
    OldCH2Gain = CH2GainSA.get()
    try:
        HoldOff = float(eval(HoldOffentry.get()))
        if HoldOff < 0:
            HoldOff = 0
            HoldOffentry.delete(0,END)
            HoldOffentry.insert(0, HoldOff)
    except:
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, HoldOff)
    # turn off triggering
    m2k_adc4_trigger.attrs["mode"].value = 'always'
    m2k_adc5_trigger.attrs["mode"].value = 'always'
    #
    INITIALIZEstart()
    # Starting acquisition
    # restart AWGs if indicated
    if BodeDisp.get() == 0: # make new noise waveforms each sweep
        if AWGAShape.get() == 7 and AWGAMode.get() == 0:
            UpdateAWGA()
        elif AWGAShape.get() == 8 and AWGAMode.get() == 0:
            UpdateAWGA()
        elif AWGBShape.get() == 7 and AWGBMode.get() == 0:
            UpdateAWGB()
        elif AWGBShape.get() == 8 and AWGBMode.get() == 0:
            UpdateAWGB()
    #
##    hldn = int(HoldOff * 100 )
##    if hldn > MaxSamples-SMPfft:
##        hldn = MaxSamples-SMPfft
##        HoldOffentry.delete(0,END)
##        HoldOffentry.insert(0, hldn/100)
##        if hldn < 128:
##            hldn = 128
    SHOWsamples = SMPfft # + hldn # get holf off extra samples
    if BodeDisp.get() > 0: # check if doing Bode Plot
        if FStepSync.get() == 1: # output low - high - low pulse on PIO-0
            Dig0.attrs["direction"].value = 'out'
            Dig0.attrs["raw"].value = '0'
            Dig0.attrs["raw"].value = '1'
            Dig0.attrs["raw"].value = '0'
        if FStepSync.get() == 2: # output high - low - high pulse on PIO-0
            Dig0.attrs["direction"].value = 'out'
            Dig0.attrs["raw"].value = '1'
            Dig0.attrs["raw"].value = '0'
            Dig0.attrs["raw"].value = '1'
        if LoopNum.get() == 1 and FSweepSync.get() == 1: # output low - high - low pulse on PIO-1
            Dig1.attrs["direction"].value = 'out'
            Dig1.attrs["raw"].value = '0'
            Dig1.attrs["raw"].value = '1'
            Dig1.attrs["raw"].value = '0'
        if LoopNum.get() == 1 and FSweepSync.get() == 2: # output high - low - high pulse on PIO-1
            Dig1.attrs["direction"].value = 'out'
            Dig1.attrs["raw"].value = '1'
            Dig1.attrs["raw"].value = '0'
            Dig1.attrs["raw"].value = '1'
##    try:
##        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
##    except:
    if OldShowSamples != SHOWsamples:
        del(TimeBuffer) # delete old buffer and make a new one
        TimeBuffer = iio.Buffer(m2k_adc, SHOWsamples, False)
        time.sleep(0.2)
        TimeBuffer.refill() # burn one buffer to remove possible bad data
        x = TimeBuffer.read()
        # print "Extra fill and read", len(x)
    TimeBuffer.refill() # fill the buffer
    x = TimeBuffer.read() # read the buffer
    ADsignal1 = []
    FFTBuffA = [] # Clear the FFTBuff array for trace A
    FFTBuffB = [] # Clear the FFTBuff array for trace B
    OverRangeFlagA = OverRangeFlagB = 0 # Clear over range flags
    for n in range (0, len(x), 2): # formated as hex unsigned 12 bits little-endian
        ADsignal1.append(struct.unpack_from("<h", x, n)[0])
    for n in range (0, len(ADsignal1), 2):
        VCH1 = float(ADsignal1[n])
        VAdata = (VCH1/2048.0)*ch1_multiplier # scale to volts
        FFTBuffA.append(VAdata)
        if CH1GainSA.get() == 0:
            if VAdata >= 2.9 or VAdata <= -2.9:
                OverRangeFlagA = 1
        VCH2 = float(ADsignal1[n+1])
        VBdata = (VCH2/2048.0)*ch2_multiplier # scale to volts
        FFTBuffB.append(VBdata)
        if CH2GainSA.get() == 0:
            if VBdata >= 2.9 or VBdata <= -2.9:
                OverRangeFlagB = 1
#
    FFTBuffA = numpy.array(FFTBuffA)
    FFTBuffB = numpy.array(FFTBuffB)
    FFTBuffA = (FFTBuffA - InOffA) * InGainA
    FFTBuffB = (FFTBuffB - InOffB) * InGainB
    DCA = numpy.average(FFTBuffA)
    DCB = numpy.average(FFTBuffB)
    if CutDC.get() == 1:
        FFTBuffA = FFTBuffA - DCA
        FFTBuffB = FFTBuffB - DCB
# check if digital filter box checked
    if DigFiltA.get() == 1:
        FFTBuffA = numpy.convolve(FFTBuffA, DFiltACoef)
    if DigFiltB.get() == 1:
        FFTBuffB = numpy.convolve(FFTBuffB, DFiltBCoef)
    DoFFT()
    if SpectrumScreenStatus.get() > 0 and FreqDisp.get() > 0:
        UpdateFreqAll()                         # Update spectrum Data, trace and screen
    if IAScreenStatus.get() > 0 and IADisp.get() > 0:
        UpdateIAAll()
    if BodeScreenStatus.get() > 0 and BodeDisp.get() > 0:
        UpdateBodeAll()
    if SingleShot.get() == 1: # Single shot sweep is on
        RUNstatus.set(0)
# RUNstatus = 3: Stop
# RUNstatus = 4: Stop and restart
    if (RUNstatus.get() == 3) or (RUNstatus.get() == 4):
        if RUNstatus.get() == 3:
            RUNstatus.set(0)                # Status is stopped 
        if RUNstatus.get() == 4:          
            RUNstatus.set(1)                # Status is (re)start
        if SpectrumScreenStatus.get() > 0 and FreqDisp.get() > 0:
            UpdateFreqScreen()                  # Freq UpdateScreen() call
        if IAScreenStatus.get() > 0 and IADisp.get() > 0:
            UpdateIAScreen()
    if FSweepMode.get() > 0 and BodeDisp.get() > 0: # Increment loop counter only if sleceted and Bode display is active
        LoopNum.set(LoopNum.get() + 1)
        if LoopNum.get() > NSteps.get():
            LoopNum.set(1)
            if FSweepCont.get() == 0:
                RUNstatus.set(0)

def UpdateFreqAll():        # Update Data, trace and screen
    global FFTBuffA, FFTBuffB
    global SMPfft

    if len(FFTBuffA) < SMPfft and len(FFTBuffB) < SMPfft:
        return
    
    # DoFFT()             # Fast Fourier transformation
    MakeFreqTrace()         # Update the traces
    UpdateFreqScreen()      # Update the screen 

def UpdateFreqTrace():      # Update trace and screen
    MakeFreqTrace()         # Update traces
    UpdateFreqScreen()      # Update the screen

def UpdateFreqScreen():     # Update screen with trace and text
    MakeFreqScreen()        # Update the screen    

def DoFFT():            # Fast Fourier transformation
    global FFTBuffA, FFTBuffB
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P
    global FFTmemoryA, FFTresultA
    global FFTmemoryB, FFTresultB
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh
    global PeakdbA, PeakdbB, PeakphaseA, PeakphaseB, PeakRelPhase
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global FFTwindowshape, FFTbandwidth
    global SAMPLErate, StartFreqEntry, StopFreqEntry, StartBodeEntry
    global SMPfft, LoopNum
    global STARTsample, STOPsample, Fsample
    global TRACEaverage, FreqTraceMode, FSweepMode
    global TRACEresetFreq, ZEROstuffing
    global SpectrumScreenStatus, IAScreenStatus, BodeScreenStatus

    # T1 = time.time()              # For time measurement of FFT routine
    REX = []
    PhaseA = []
    PhaseB = []
    # Convert list to numpy array REX for faster Numpy calculations
    # Take the first fft samples
    REX = numpy.array(FFTBuffA[:SMPfft])    # Make a numpy arry of the list

    # Set Analog level display value MAX value is 5 volts for ALM1000
    REX = REX / 5.0

    # Do the FFT window function 
    REX = REX * FFTwindowshape      # The windowing shape function only over the samples

    # Zero stuffing of array for better interpolation of peak level of signals
    ZEROstuffingvalue = int(2 ** ZEROstuffing.get())
    fftsamples = ZEROstuffingvalue * SMPfft      # Add zero's to the arrays

    # Save previous trace in memory for max or average trace
    FFTmemoryA = FFTresultA
    if FreqTraceMode.get() == 3:
        PhaseMemoryA = PhaseA

    # FFT with numpy 
    ALL = numpy.fft.fft(REX, n=fftsamples)  # Do FFT + zerostuffing till n=fftsamples with NUMPY  ALL = Real + Imaginary part
    PhaseA = numpy.angle(ALL, deg=True)     # calculate angle
    ALL = numpy.absolute(ALL)               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    ALL = ALL * ALL                         # Convert from Voltage to Power (P = (V*V) / R; R = 1)

    le = len(ALL)
    le = le / 2                             # Only half is used, other half is mirror
    ALL = ALL[:le]                          # So take only first half of the array
    PhaseA = PhaseA[:le]
    Totalcorr = float(ZEROstuffingvalue)/ fftsamples # For VOLTAGE!
    Totalcorr = Totalcorr * Totalcorr               # For POWER!
    FFTresultA = Totalcorr * ALL

    REX = []
    # Convert list to numpy array REX for faster Numpy calculations
    # Take the first fft samples
    REX = numpy.array(FFTBuffB[:SMPfft])    # Make a numpy arry of the list

    # Set level display value MAX value is 5 volts for ALM1000
    REX = REX / 5.0

    # Do the FFT window function
    REX = REX * FFTwindowshape      # The windowing shape function only over the samples

    # Zero stuffing of array for better interpolation of peak level of signals
    ZEROstuffingvalue = int(2 ** ZEROstuffing.get())
    fftsamples = ZEROstuffingvalue * SMPfft      # Add zero's to the arrays

    # Save previous trace in memory for max or average trace
    FFTmemoryB = FFTresultB
    if FreqTraceMode.get() == 3:
        PhaseMemoryB = PhaseB
    # FFT with numpy 
    ALL = numpy.fft.fft(REX, n=fftsamples)  # Do FFT + zerostuffing till n=fftsamples with NUMPY  ALL = Real + Imaginary part
    PhaseB = numpy.angle(ALL, deg=True)     # calculate angle
    ALL = numpy.absolute(ALL)               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!
    ALL = ALL * ALL                         # Convert from Voltage to Power (P = (U*U) / R; R = 1)

    le = len(ALL)
    le = le / 2                             # Only half is used, other half is mirror
    ALL = ALL[:le]                          # So take only first half of the array
    PhaseB = PhaseB[:le]
    Totalcorr = float(ZEROstuffingvalue)/ fftsamples # For VOLTAGE!
    Totalcorr = Totalcorr * Totalcorr               # For POWER!
    FFTresultB = Totalcorr * ALL
    TRACEsize = len(FFTresultB)
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)
    if SpectrumScreenStatus.get() > 0:
        try:
            StartFrequency = float(StartFreqEntry.get())
        except:
            StartFreqEntry.delete(0,"end")
            StartFreqEntry.insert(0,100)
            StartFrequency = 100
        STARTsample = StartFrequency / Fsample
    else:
        STARTsample = 0.0
    if LoopNum.get() == 1:
        PhaseMemoryB = PhaseB
        FSweepAdB = []
        FSweepBdB = []
        FSweepAPh = []
        FSweepBPh = []
    if FreqTraceMode.get() == 1:      # Normal mode 1, do not change
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1

    if FreqTraceMode.get() == 2 and TRACEresetFreq == False:  # Peak hold mode 2, change v to peak value
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryB[ptmax+i] = PhaseB[ptmax]
                i = i + 1
        try:
            FFTresultB = numpy.maximum(FFTresultB, FFTmemoryB)#
        except:
            donothing()
    if FreqTraceMode.get() == 3 and TRACEresetFreq == False:  # Average mode 3, add difference / TRACEaverage to v
        try:
            FFTresultB = FFTmemoryB + (FFTresultB - FFTmemoryB) / TRACEaverage.get()
            PhaseB = PhaseMemoryB +(PhaseB - PhaseMemoryB) / TRACEaverage.get()
        except:
            FFTmemoryB = FFTresultB
            PhaseMemoryB = PhaseB
# 
    TRACEsize = len(FFTresultA)
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)
    if SpectrumScreenStatus.get() > 0:
        STARTsample = StartFrequency / Fsample
    else:
        STARTsample = 0.0
    if LoopNum.get() == 1:
        PhaseMemoryA = PhaseA
    if FreqTraceMode.get() == 1:      # Normal mode 1, do not change
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1

    if FreqTraceMode.get() == 2 and TRACEresetFreq == False:  # Peak hold mode 2, change v to peak value
        if FSweepMode.get() == 1:
            ptmax = numpy.argmax(FFTresultA[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
        if FSweepMode.get() == 2:
            ptmax = numpy.argmax(FFTresultB[STARTsample::])
            if ptmax > STARTsample:
                STARTsample = ptmax
            i = 0
            while i < 6:
                PhaseMemoryA[ptmax+i] = PhaseA[ptmax]
                i = i + 1
#
        FFTresultA = numpy.maximum(FFTresultA, FFTmemoryA)
    if FreqTraceMode.get() == 3 and TRACEresetFreq == False:  # Average mode 3, add difference / TRACEaverage to v
        try:
            FFTresultA = FFTmemoryA + (FFTresultA - FFTmemoryA) / TRACEaverage.get()
            PhaseA = PhaseMemoryA +(PhaseA - PhaseMemoryA) / TRACEaverage.get()
        except:
            FFTmemoryA = FFTresultA
            PhaseMemoryA = PhaseA
#
    if FSweepMode.get() > 0 and BodeScreenStatus.get() > 0:
        FindFreqPeak()
        FSweepAdB.append(PeakdbA)
        FSweepBdB.append(PeakdbB)
        FSweepAPh.append(PeakphaseA)
        FSweepBPh.append(PeakphaseB)
##        FSweepAdB.append(numpy.amax(FFTresultA))
##        FSweepBdB.append(numpy.amax(FFTresultB))
##        FSweepAPh.append(PhaseA[numpy.argmax(FFTresultA)])
##        FSweepBPh.append(PhaseB[numpy.argmax(FFTresultB)])

    TRACEresetFreq = False          # Trace reset done

    # T2 = time.time()
    # print (T2 - T1)           # For time measurement of FFT routine

def MakeFreqTrace():        # Update the grid and trace
    global FFTmemoryA, FFTresultA
    global FFTmemoryB, FFTresultB
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMathSA
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM, PeakIndexA, PeakIndexB
    global PeakfreqA, PeakfreqB
    global DBdivindex   # Index value
    global DBdivlist    # dB per division list
    global DBlevel      # Reference level
    global GRHF          # Screenheight
    global GRWF          # Screenwidth
    global SAMPLErate, HScale, Fsample
    global StartFreqEntry, StopFreqEntry
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global FreqTraceMode, RelPhaseCorrection
    global T1Fline, T2Fline, TFMline, T1Pline, T2Pline
    global Vdiv         # Number of vertical divisions
    global X0LF          # Left top X value
    global Y0TF          # Left top Y value

    # Set the TRACEsize variable
    TRACEsize = 0
    try:
        StartFrequency = float(StartFreqEntry.get())
    except:
        StartFreqEntry.delete(0,"end")
        StartFreqEntry.insert(0,100)
        StartFrequency = 100
    try:
        StopFrequency = float(StopFreqEntry.get())
    except:
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,100)
        StopFrequency = 10000
    if ShowC1_VdB.get() == 1 or ShowMathSA.get() > 0:
        TRACEsize = len(FFTresultA)     # Set the trace length
    elif ShowC2_VdB.get() == 1 or ShowMathSA.get() > 0:
        TRACEsize = len(FFTresultB)
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        return()
    if FSweepMode.get() > 0 and LoopNum.get() == NSteps.get():
        PhaseA = PhaseMemoryA
        PhaseB = PhaseMemoryB
   # Vertical conversion factors (level dBs) and border limits
    Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()])     # Conversion factors, Yconv is the number of screenpoints per dB
    Yc = float(Y0TF) + Yconv * (DBlevel.get())  # Yc is the 0 dBm position, can be outside the screen!
    Ymin = Y0TF                  # Minimum position of screen grid (top)
    Ymax = Y0TF + GRHF            # Maximum position of screen grid (bottom)
    Yphconv = float(GRHF) / 360
    Yp = float(Y0TF) + Yphconv + 180
    # Horizontal conversion factors (frequency Hz) and border limits
    Fpixel = (StopFrequency - StartFrequency) / GRWF    # Frequency step per screen pixel
    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)       # Frequency step per sample   
    LogFStop = math.log10(StopFrequency)
    try:
        LogFStart = math.log10(StartFrequency)
    except:
        LogFStart = 0.0
    LogFpixel = (LogFStop - LogFStart) / GRWF
    STARTsample = StartFrequency / Fsample     # First sample in FFTresult[] that is used
    STARTsample = int(math.ceil(STARTsample))               # First within screen range

    STOPsample = StopFrequency / Fsample       # Last sample in FFTresult[] that is used
    STOPsample = int(math.floor(STOPsample))                # Last within screen range, math.floor actually not necessary, part of int

    MAXsample = TRACEsize                                   # Just an out of range check
    if STARTsample > (MAXsample - 1):
        STARTsample = MAXsample - 1

    if STOPsample > MAXsample:
        STOPsample = MAXsample

    T1Fline = []
    T2Fline = []
    T1Pline = []
    T2Pline = []
    TFMline = []
    n = STARTsample
    PeakdbA = -200
    PeakdbB = -200 # PeakdbB
    PeakMdb = -200
    while n <= STOPsample:
        F = n * Fsample
        if HScale.get() == 1:
            try:
                LogF = math.log10(F) # convet to log Freq
                x = X0LF + (LogF - LogFStart)/LogFpixel
            except:
                x = X0LF
        else:
            x = X0LF + (F - StartFrequency)  / Fpixel
        if ShowC1_VdB.get() == 1: 
            T1Fline.append(int(x + 0.5))
            try:
                dbA = (10 * math.log10(float(FFTresultA[n])) + 17)   # Convert power to DBs, except for log(0) error
                ya = Yc - Yconv * dbA  # Add 17 dB for max value of +10 dB ALSO in CSV file routine!
            except:
                ya = Ymax
                dbA = ya / (Yc - Yconv)
            if (ya < Ymin):
                ya = Ymin
            if (ya > Ymax):
                ya = Ymax
            if dbA > PeakdbA:
                PeakdbA = dbA
                PeakyA = int(ya + 0.5)
                PeakxA = int(x + 0.5)
                PeakfreqA = F
                PeakIndexA = n
            T1Fline.append(int(ya + 0.5))
        if ShowC2_VdB.get() == 1:
            T2Fline.append(int(x + 0.5))
            try:
                dbB = (10 * math.log10(float(FFTresultB[n])) + 17) # Add 17 dB for max value of +10 dB ALSO in CSV file routine!
                yb = Yc - Yconv * dbB 
            except:
                yb = Ymax
                dbB = yb / (Yc - Yconv)
            if (yb < Ymin):
                yb = Ymin
            if (yb > Ymax):
                yb = Ymax
            if dbB > PeakdbB:
                PeakdbB = dbB
                PeakyB = int(yb + 0.5)
                PeakxB = int(x + 0.5)
                PeakfreqB = F
                PeakIndexB = n
            T2Fline.append(int(yb + 0.5))
        if ShowC1_P.get() == 1:
            T1Pline.append(int(x + 0.5))
            if FSweepMode.get() > 0:
                RelPhase = PhaseMemoryA[n]-PhaseMemoryB[n]
            else:
                RelPhase = PhaseA[n]-PhaseB[n] - RelPhaseCorrection
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            ya = Yp - Yphconv * RelPhase
            T1Pline.append(int(ya + 0.5))
        if ShowC2_P.get() == 1:
            T2Pline.append(int(x + 0.5))
            if FSweepMode.get() > 0:
                RelPhase = PhaseMemoryB[n]-PhaseMemoryA[n]
            else:
                RelPhase = PhaseB[n]-PhaseA[n] - RelPhaseCorrection
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            ya = Yp - Yphconv * RelPhase
            T2Pline.append(int(ya + 0.5))
        if ShowMathSA.get() > 0:
            TFMline.append(int(x + 0.5))
            dbA = (10 * math.log10(float(FFTresultA[n])) + 17) # Convert power to DBs, except for log(0) error
            dbB = (10 * math.log10(float(FFTresultB[n])) + 17) # Add 17 dB for max value of +10 dB ALSO in CSV file routine!
            if ShowMathSA.get() == 1:
                MdB = dbA - dbB
            elif ShowMathSA.get() == 2:
                MdB = dbB - dbA
            yb = Yc - Yconv * MdB
            if (yb < Ymin):
                yb = Ymin
            if (yb > Ymax):
                yb = Ymax
            if MdB > PeakMdb:
                PeakMdb = MdB
                PeakyM = int(yb + 0.5)
                PeakxM = int(x + 0.5)
                PeakfreqM = F
            TFMline.append(int(yb + 0.5))
        n = n + 1               
# make Bode Plot Traces
def MakeBodeTrace():        # Update the grid and trace
    global FSweepAdB, FSweepBdB, FSweepAPh, FSweepBPh, FStep, FBins
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMathBP
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB, PeakRelPhase
    global PeakxM, PeakyM, PeakMdb, PeakfreqM, PeakphaseA, PeakphaseB
    global PeakfreqA, PeakfreqB
    global DBdivindexBP   # Index value
    global DBdivlist    # dB per division list
    global DBlevelBP      # Reference level
    global GRHBP          # Screenheight
    global GRWBP          # Screenwidth
    global SAMPLErate, HScaleBP, RUNstatus, HalfSAMPLErate
    global StartBodeEntry, StopBodeEntry, BeginIndex, EndIndex
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global FreqTraceMode, RelPhaseCorrection
    global TAFline, TBFline, TBPMline, TAPline, TBPline
    global Vdiv         # Number of vertical divisions
    global X0LBP        # Left top X value
    global Y0TBP        # Left top Y value

    HalfSAMPLErate = SAMPLErate/2
    # Set the TRACEsize variable
    TRACEsize = 0
    if ShowCA_VdB.get() == 1 or ShowMathBP.get() > 0:
        TRACEsize = len(FStep)     # Set the trace length
    elif ShowCB_VdB.get() == 1 or ShowMathBP.get() > 0:
        TRACEsize = len(FStep)
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        return()
    #
    try:
        EndFreq = float(StopBodeEntry.get())
    except:
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,10000)
        EndFreq = 10000
    try:
        BeginFreq = float(StartBodeEntry.get())
    except:
        StartBodeEntry.delete(0,"end")
        StartBodeEntry.insert(0,100)
        BeginFreq = 100
    if FSweepMode.get() > 0 and len(FSweepAdB) > 4:
        # Vertical conversion factors (level dBs) and border limits
        Yconv = float(GRHBP) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()])     # Conversion factors, Yconv is the number of screenpoints per dB
        Yc = float(Y0TBP) + Yconv * (DBlevelBP.get())  # Yc is the 0 dBm position, can be outside the screen!
        Ymin = Y0TBP                  # Minimum position of screen grid (top)
        Ymax = Y0TBP + GRHBP            # Maximum position of screen grid (bottom)
        Yphconv = float(GRHBP) / 360
        Yp = float(Y0TBP) + Yphconv + 180
        # Horizontal conversion factors (frequency Hz) and border limits
        Fpixel = (EndFreq - BeginFreq) / GRWBP    # Frequency step per screen pixel   
        LogFStop = math.log10(EndFreq)
        try:
            LogFStart = math.log10(BeginFreq)
        except:
            LogFStart = 0.0
        LogFpixel = (LogFStop - LogFStart) / GRWBP
        TAFline = []
        TBFline = []
        TAPline = []
        TBPline = []
        TBPMline = []
        PeakAmplA = -200
        PeakAmplB = -200
        PeakMdb = -200
        n = 0
        for n in range(len(FSweepAdB)): # while n < len(FStep):
            if n < len(FStep): # check if n has gone out off bounds because user did something dumb
                F = FStep[n] # look up frequency bin in list of bins
            else:
                F = FStep[0]
            if F >= BeginFreq and F <= EndFreq:
                if HScaleBP.get() == 1:
                    try:
                        LogF = math.log10(F) # convet to log Freq
                        x = X0LBP + (LogF - LogFStart)/LogFpixel
                    except:
                        x = X0LBP
                else:
                    x = X0LBP + (F - BeginFreq)  / Fpixel
                if ShowCA_VdB.get() == 1: 
                    TAFline.append(int(x + 0.5))
                    try:
                        dbA = FSweepAdB[n] 
                        ya = Yc - Yconv * dbA  
                    except:
                        ya = Ymax
                    if (ya < Ymin):
                        ya = Ymin
                    if (ya > Ymax):
                        ya = Ymax
                    if dbA > PeakAmplA:
                        PeakAmplA = dbA
                        PeakyA = int(ya + 0.5)
                        PeakxA = int(x + 0.5)
                        PeakfreqA = F
                    TAFline.append(int(ya + 0.5))
                if ShowCB_VdB.get() == 1:
                    TBFline.append(int(x + 0.5))
                    try:
                        dbB = FSweepBdB[n] # 
                        yb = Yc - Yconv * dbB 
                    except:
                        yb = Ymax
                    if (yb < Ymin):
                        yb = Ymin
                    if (yb > Ymax):
                        yb = Ymax
                    if dbB > PeakAmplB:
                        PeakAmplB = dbB
                        PeakyB = int(yb + 0.5)
                        PeakxB = int(x + 0.5)
                        PeakfreqB = F
                    TBFline.append(int(yb + 0.5))
                if ShowCA_P.get() == 1:
                    TAPline.append(int(x + 0.5))
                    RelPhase = FSweepAPh[n] - FSweepBPh[n] - RelPhaseCorrection
                    if RelPhase > 180:
                        RelPhase = RelPhase - 360
                    elif RelPhase < -180:
                        RelPhase = RelPhase + 360
                    ya = Yp - Yphconv * RelPhase
                    TAPline.append(int(ya + 0.5))
                if ShowCB_P.get() == 1:
                    TBPline.append(int(x + 0.5))
                    RelPhase = FSweepBPh[n] - FSweepAPh[n] - RelPhaseCorrection
                    if RelPhase > 180:
                        RelPhase = RelPhase - 360
                    elif RelPhase < -180:
                        RelPhase = RelPhase + 360
                    ya = Yp - Yphconv * RelPhase
                    TBPline.append(int(ya + 0.5))
                if ShowMathBP.get() > 0:
                    TBPMline.append(int(x + 0.5))
                    dbA = FSweepAdB[n] # 
                    dbB = FSweepBdB[n] # 
                    if ShowMathBP.get() == 1:
                        MdB = dbA - dbB
                    elif ShowMathBP.get() == 2:
                        MdB = dbB - dbA
                    yb = Yc - Yconv * MdB
                    if (yb < Ymin):
                        yb = Ymin
                    if (yb > Ymax):
                        yb = Ymax
                    if MdB > PeakMdb:
                        PeakMdb = MdB
                        PeakyM = int(yb + 0.5)
                        PeakxM = int(x + 0.5)
                        PeakfreqM = F
                    TBPMline.append(int(yb + 0.5))
#
def MakeBodeScreen():       # Update the screen with traces and text
    global CANVASheightBP, CANVASwidthBP, SmoothCurvesBP
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    global COLORgrid    # The colors
    global COLORsignalband, COLORtext
    global COLORtrace1, COLORtrace2
    global FSweepMode, LoopNum, MarkerFreqNum, TRACEwidth, GridWidth
    global DBdivindexBP   # Index value
    global DBdivlist    # dB per division list
    global DBlevelBP      # Reference level
    global FFTwindow, FFTbandwidth, ZEROstuffing, FFTwindowname
    global X0LBP          # Left top X value
    global Y0TBP          # Left top Y value
    global GRWBP          # Screenwidth
    global GRHBP          # Screenheight
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global SAMPLErate, SingleShot, HScaleBP
    global SMPfft       # number of FFT samples
    global StartBodeEntry, StopBodeEntry
    global ShowCA_P, ShowCB_P, ShowRA_VdB, ShowRB_VdB, ShowMarkerBP
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP
    global ShowMathBP, BodeDisp
    global ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global TAFline, TBFline, TAPline, TAFRline, TBFRline, TBPMline, TBPRMline
    global TAPRline, TBPRline
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv         # Number of vertical divisions

    # Delete all items on the screen
    de = Bodeca.find_enclosed( -1000, -1000, CANVASwidthBP+1000, CANVASheightBP+1000 )
    MarkerFreqNum = 0
    for n in de: 
        Bodeca.delete(n)
    try:
        EndFreq = float(StopBodeEntry.get())
    except:
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,10000)
        EndFreq = 10000
    try:
        BeginFreq = float(StartBodeEntry.get())
    except:
        StartBodeEntry.delete(0,"end")
        StartBodeEntry.insert(0,100)
        BeginFreq = 100
    # Draw horizontal grid lines
    i = 0
    x1 = X0LBP
    x2 = X0LBP + GRWBP
    while (i <= Vdiv.get()):
        y = Y0TBP + i * GRHBP/Vdiv.get()
        Dline = [x1,y,x2,y]
        if i == 0 or i == Vdiv.get():
            Bodeca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
        else:
            Bodeca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
        Vaxis_value = (DBlevelBP.get() - (i * DBdivlist[DBdivindexBP.get()]))
        Vaxis_label = str(Vaxis_value)
        Bodeca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
        if ShowCA_P.get() == 1 or ShowCB_P.get() == 1:
            Vaxis_value = ( 180 - ( i * (360 / Vdiv.get())))
            Vaxis_label = str(Vaxis_value)
            Bodeca.create_text(x2+3, y, text=Vaxis_label, fill=COLORtrace3, anchor="w", font=("arial", 8 ))
        i = i + 1
    # Draw vertical grid lines
    i = 0
    y1 = Y0TBP
    y2 = Y0TBP + GRHBP
    if HScaleBP.get() == 1:
        F = 1.0
        LogFStop = math.log10(EndFreq)
        try:
            LogFStart = math.log10(BeginFreq)
        except:
            LogFStart = 0.0
        LogFpixel = (LogFStop - LogFStart) / GRWBP
        # draw left and right edges
        while F <= EndFreq:
            if F >= BeginFreq:
                try:
                    LogF = math.log10(F) # convet to log Freq
                    x = X0LBP + (LogF - LogFStart)/LogFpixel
                except:
                    x = X0LBP
                Dline = [x,y1,x,y2]
                if F == 1 or F == 10 or F == 100 or F == 1000 or F == 10000 or F == 100000 or F == 1000000 or F == 10000000:
                    Bodeca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    if F >= 1000000:
                        axis_label = str(int(F/1000000)) + " MHz"
                    elif F >= 1000:
                        axis_label = str(int(F/1000)) + " KHz" 
                    else:
                        axis_label = str(F) + " Hz" 
                    Bodeca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
                else:
                    Bodeca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
                
            if F < 10:
                F = F + 1
            elif F < 100:
                F = F + 10
            elif F < 1000:
                F = F + 100
            elif F < 1000:
                F = F + 100
            elif F < 10000:
                F = F + 1000
            elif F < 100000:
                F = F + 10000
            elif F < 1000000:
                F = F + 100000
            elif F < 10000000:
                F = F + 1000000
    else:
        Freqdiv = (EndFreq - BeginFreq) / 10
        while (i < 11):
            x = X0LBP + i * GRWBP/10
            Dline = [x,y1,x,y2]
            if i == 0 or i == 10:
                Bodeca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                Bodeca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            axis_value = BeginFreq + (i * Freqdiv)
            if axis_value >= 1000000:
                axis_label = str(int(axis_value/1000000)) + " MHz"
            elif axis_value >= 1000:
                axis_label = str(int(axis_value/1000)) + " KHz" 
            else:
                axis_label = str(axis_value) + " Hz"
            Bodeca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
            i = i + 1
    # Draw X - Y cursors if needed
    if ShowBPCur.get() > 0:
        Dline = [BPCursor, Y0TBP, BPCursor, Y0TBP+GRHBP]
        Bodeca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScaleBP.get() == 1:
            LogFStop = math.log10(EndFreq)
            try:
                LogFStart = math.log10(BeginFreq)
            except:
                LogFStart = 0.0
            LogFpixel = (LogFStop - LogFStart) / GRWBP
            xfreq = 10**(((BPCursor-X0LF)*LogFpixel) + LogFStart)
        else:
            Fpixel = (EndFreq - BeginFreq) / GRWBP # Frequency step per screen pixel
            xfreq = ((BPCursor-X0LBP)*Fpixel)+BeginFreq
        XFString = ' {0:.2f} '.format(xfreq)
        V_label = XFString + " Hz"
        Bodeca.create_text(BPCursor+1, BdBCursor-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
#
    if ShowBdBCur.get() > 0:
        Dline = [X0LBP, BdBCursor, X0LBP+GRWBP, BdBCursor]
        Bodeca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        if ShowBdBCur.get() == 1: # Vertical conversion factors and border limits
            Yconv = float(GRHBP) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
            Yc = float(Y0TBP) + Yconv * (DBlevelBP.get()) # Yc is the 0 dBm position, can be outside the screen!
            yvdB = ((Yc-BdBCursor)/Yconv)
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " dBV"
        else:
            Yconv = float( GRHBP / 360.0 ) # pixels per degree
            Yc = float(Y0TBP + (GRHBP/2.0)) # Yc is the 0 degree position
            yvdB = ((Yc-BdBCursor)/Yconv)
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " deg"
        Bodeca.create_text(BPCursor+1, BdBCursor+5, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
    #
    SmoothBool = SmoothCurvesBP.get()
    # Draw traces
    if len(TAFline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHA
        if OverRangeFlagA == 1:
            Bodeca.create_line(TAFline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Bodeca.create_line(TAFline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            try:
                Peak_label = ' {0:.2f} '.format(PeakdbA) + ',' + ' {0:.1f} '.format(PeakfreqA)
                Bodeca.create_text(PeakxA, PeakyA, text=Peak_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
            except:
                donothing()
    if len(TBFline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHB
        if OverRangeFlagB == 1:
            Bodeca.create_line(TBFline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Bodeca.create_line(TBFline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            try:
                Peak_label = ' {0:.2f} '.format(PeakdbB) + ',' + ' {0:.1f} '.format(PeakfreqB)
                Bodeca.create_text(PeakxB, PeakyB, text=Peak_label, fill=COLORtrace2, anchor="w", font=("arial", 8 ))
            except:
                donothing()
    if len(TAPline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Bodeca.create_line(TAPline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TBPline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Bodeca.create_line(TBPline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowCA_RdB.get() == 1 and len(TAFRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TAFRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            try:
                Peak_label = ' {0:.2f} '.format(PeakdbRA) + ',' + ' {0:.1f} '.format(PeakfreqRA)
                Bodeca.create_text(PeakxRA, PeakyRA, text=Peak_label, fill=COLORtraceR1, anchor="e", font=("arial", 8 ))
            except:
                donothing()
    if ShowCB_RdB.get() == 1 and len(TBFRline) > 4:   # Write the ref trace B if active
        Bodeca.create_line(TBFRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            try:
                Peak_label = ' {0:.2f} '.format(PeakdbRB) + ',' + ' {0:.1f} '.format(PeakfreqRB)
                Freqca.create_text(PeakxRB, PeakyRB, text=Peak_label, fill=COLORtraceR2, anchor="w", font=("arial", 8 ))
            except:
                donothing()
    if ShowCA_RP.get() == 1 and len(TAPRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TAPRline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowCB_RP.get() == 1 and len(TBPRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TBPRline, fill=COLORtraceR4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMathBP.get() > 0 and len(TBPMline) > 4:   # Write the Math trace if active
        Bodeca.create_line(TBPMline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            try:
                Peak_label = ' {0:.2f} '.format(PeakMdb) + ',' + ' {0:.1f} '.format(PeakfreqM)
                Bodeca.create_text(PeakxM, PeakyM, text=Peak_label, fill=COLORtrace5, anchor="w", font=("arial", 8 ))
            except:
                donothing()
    if ShowRMathBP.get() == 1 and len(TBPRMline) > 4:   # Write the ref math trace if active
        Bodeca.create_line(TBPRMline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            try:
                Peak_label = ' {0:.2f} '.format(PeakRMdb) + ',' + ' {0:.1f} '.format(PeakfreqRM)
                Bodeca.create_text(PeakxRM, PeakyRM, text=Peak_label, fill=COLORtraceR5, anchor="w", font=("arial", 8 ))
            except:
                donothing()
    # General information on top of the grid
    if SAMPLErate >= 1000000:
        SR_string = str(int(SAMPLErate/1000000)) + " MSPS"
    else:
        SR_string = str(int(SAMPLErate/1000)) + " KSPS"
    txt = "    Sample rate: " + SR_string
    txt = txt + "    FFT samples: " + str(SMPfft)

    txt = txt + "   " + FFTwindowname
        
    x = X0LBP
    y = 12
    idTXT = Bodeca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

    # Start and stop frequency and dB/div and trace mode
    txt = str(BeginFreq) + " to " + str(EndFreq) + " Hz"
    txt = txt +  "  " + str(DBdivlist[DBdivindexBP.get()]) + " dB/div"
    txt = txt + "  Level: " + str(DBlevelBP.get()) + " dB "
    txt = txt + "  FFT Bandwidth =" + ' {0:.2f} '.format(FFTbandwidth)
    
    x = X0LBP
    y = Y0TBP+GRHBP+23
    idTXT = Bodeca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    
    if FreqTraceMode.get() == 1:
        txt ="Normal mode "

    if FreqTraceMode.get() == 2:
        txt = "Peak hold mode "
    
    if FreqTraceMode.get() == 3:
        txt = "Power average  mode (" + str(TRACEaverage.get()) + ") " 

    if ZEROstuffing.get() > 0:
        txt = txt + "Zero Stuffing = " + str(ZEROstuffing.get())
    # Runstatus and level information
    if (RUNstatus.get() == 0) and (SingleShot.get() == 0):
        txt = txt + "  Stopped "
    elif SingleShot.get() == 1:
        txt = txt + "  Single Shot Trace "
    else:
        if BodeDisp.get() == 1:
            txt = txt + "  Running "
        else:
            txt = txt + "  Display off "
    if FSweepMode.get() > 0:
        txt = txt + "  Freq Step = " + str(LoopNum.get())
    x = X0LBP
    y = Y0TBP+GRHBP+34
    IDtxt  = Bodeca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

# Impedance analyzer routines -----
def UpdateIAAll():        # Update Data, trace and screen
    global FFTBuffA, FFTBuffB
    global SMPfft

    if len(FFTBuffA) < SMPfft and len(FFTBuffB) < SMPfft:
        return
    UpdateIAScreen()      # Update the screen 

def UpdateIATrace():      # Update trace and screen
    UpdateIAScreen()      # Update the screen

def UpdateIAScreen():     # Update screen with trace and text
    MakeIAScreen()        # Update the screen
    root.update()       # Activate updated screens    
#
def DoImpedance():

# Input Variables
    global PeakdbA, PeakdbB, PeakRelPhase
    #(VZ/VA)from vector voltmeter 
    # global VVangle # angle in degrees between VZ and VA 
    global RsystemEntry # resistance of series resistor or power divider  
# Computed outputs 
    # global VVangleCosine # cosine of vector voltmeter angle 
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries # in ohms 
    global ImpedanceXseries # in ohms 
    # global temp # temporary variable
    
    DEG2RAD = (3.141592654 / 180.0)
    SMALL = 1E-20
    try:
        ResValue = float(RsystemEntry.get())
    except:
        ResValue = 1000.0
        
    VVvoltageRatio = math.pow(10,((PeakdbB-PeakdbA)/20)) # VZ/VA 
    VVangleCosine = math.cos(math.radians(PeakRelPhase))
    Temp1 = ResValue * VVvoltageRatio
    Temp2 = 1.0 + VVvoltageRatio**2 - (2.0 * VVvoltageRatio * VVangleCosine)
    if(Temp2 < SMALL):
        Temp2 = SMALL # This handles negative and too small positive
        
    Temp3 = math.sqrt(Temp2)  # VI/VA
    Temp4 = ResValue * (1-(VVvoltageRatio * VVangleCosine))

    ImpedanceMagnitude = (Temp1/Temp3) #  # Zx
    ImpedanceRseries = (Temp4/Temp2) - ResValue # Rx
    temp = ImpedanceMagnitude**2 - ImpedanceRseries**2
    if(temp < 0.0):
        temp = 0.0
    ImpedanceXseries = math.sqrt(temp) # Xx
    if(PeakRelPhase < 0.0):
        ImpedanceXseries = -ImpedanceXseries
    ImpedanceAngle = math.atan2(ImpedanceXseries, ImpedanceRseries) / DEG2RAD
#
def FindFreqPeak():        # Update the grid and trace
    global FFTmemoryA, FFTresultA
    global FFTmemoryB, FFTresultB
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB, PeakRelPhase
    global PeakxM, PeakyM, PeakMdb, PeakfreqM, PeakphaseA, PeakphaseB 
    global PeakfreqA, PeakfreqB
    global SAMPLErate
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global TRACEmode
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries # in ohms 
    global ImpedanceXseries # in ohms

    # Set the TRACEsize variable
    TRACEsize = len(FFTresultA)     # Set the trace length
    Fsample = float(SAMPLErate / 2.0) / (TRACEsize - 1)
    # Horizontal conversion factors (frequency Hz) and border limits
    STARTsample = 0     # First sample in FFTresult[] that is used
    STARTsample = int(math.ceil(STARTsample))               # First within screen range

    STOPsample = (SAMPLErate*0.5) / Fsample       # Last sample in FFTresult[] that is used
    STOPsample = int(math.floor(STOPsample))                # Last within screen range, math.floor actually not necessary, part of int
#
    MAXsample = TRACEsize                                   # Just an out of range check
    if STARTsample > (MAXsample - 1):
        STARTsample = MAXsample - 1

    if STOPsample > MAXsample:
        STOPsample = MAXsample

    n = STARTsample
    PeakfreqA = PeakfreqB = PeakfreqM = F = n * Fsample
    PeakphaseA = PhaseA[n]
    PeakphaseB = PhaseB[n]
    PeakSample = n
    PeakdbA = (10 * math.log10(float(FFTresultA[n])) + 17)
    PeakdbB = (10 * math.log10(float(FFTresultB[n])) + 17)
    PeakMdb = PeakdbA - PeakdbB
    
    while n <= STOPsample:
        F = n * Fsample
        try:
            dbA = (10 * math.log10(float(FFTresultA[n])) + 17)   # Convert power to DBs, except for log(0) error
        except:
            dbA = -200
        if dbA > PeakdbA:
            PeakdbA = dbA
            PeakfreqA = F
            PeakphaseA = PhaseA[n]
            PeakSample = n
        try:
            dbB = (10 * math.log10(float(FFTresultB[n])) + 17) # Add 17 dB for max value of +10 dB ALSO in CSV file routine! 
        except:
            dbB = -200
        if dbB > PeakdbB:
            PeakdbB = dbB
            PeakfreqB = F
            PeakphaseB = PhaseB[n]
        n = n + 1

    PeakRelPhase = PeakphaseB-PeakphaseA
    if PeakRelPhase > 180:
        PeakRelPhase = PeakRelPhase - 360
    elif PeakRelPhase < -180:
        PeakRelPhase = PeakRelPhase + 360
#
def MakeIAScreen():       # Update the screen with traces and text
    global CANVASheightIA, CANVASwidthIA, IAca
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    global PeakphaseA, PeakphaseB, PeakRelPhase, PhaseCalEntry, GainCorEntry, PhaseCorEntry, PhaseCorrection
    global COLORgrid    # The colors
    global COLORsignalband, COLORtext, COLORgrid
    global COLORtrace1, COLORtrace2, COLORtrace6
    global ResScale   # Ohms per div 
    global FFTwindow, FFTbandwidth, ZEROstuffing, FFTwindowname
    global X0LIA          # Left top X value
    global Y0TIA          # Left top Y value
    global GRWIA          # Screenwidth
    global GRHIA          # Screenheight
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global SAMPLErate, OverRangeFlagA, OverRangeFlagB
    global SMPfft       # number of FFT samples
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv         # Number of vertical divisions
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries # in ohms 
    global ImpedanceXseries # in ohms

    # find fundamental freqency / peak ampl and phase
    FindFreqPeak()
    try:
        GainCorrection = float(eval(GainCorEntry.get()))
    except:
        GainCorEntry.delete(0,END)
        GainCorEntry.insert(0, GainCorrection)
    try:
        PhaseCorrection = float(eval(PhaseCorEntry.get()))
    except:
        PhaseCorEntry.delete(0,END)
        PhaseCorEntry.insert(0, PhaseCorrection)
    PeakRelPhase = PeakRelPhase + PhaseCorrection
    PeakdbB = PeakdbB + GainCorrection
    DoImpedance()
    # Delete all items on the screen
    de = IAca.find_enclosed( -10000, -10000, CANVASwidthIA+10000, CANVASheightIA+10000 )    
    for n in de: 
        IAca.delete(n)
 
    # Draw circular grid lines
    i = 1
    xcenter = GRWIA/2
    ycenter = GRHIA/2 
    XRadius = (GRWIA-X0LIA)/11
    YRadius = (GRHIA-Y0TIA)/11
    if XRadius > YRadius: # best fit circular grid into the square space bounded by X Y window size
        Radius = YRadius
    else:
        Radius = XRadius
    OhmsperPixel = float(ResScale.get())/Radius
    TRadius = Radius * 5
    x1 = X0LIA
    x2 = X0LIA + GRWIA
    xright = 10 + xcenter + ( 5 * Radius )
    while (i <= 5):
        x0 = xcenter - ( i * Radius )
        x1 = xcenter + ( i * Radius )
        y0 = ycenter - ( i * Radius )
        y1 = ycenter + ( i * Radius )
        ResTxt = float(ResScale.get()) * i
        IAca.create_oval ( x0, y0, x1, y1, outline=COLORgrid, width=2)
        IAca.create_line(xcenter, y0, xright, y0, fill=COLORgrid, width=1, dash=(4,3))
        IAca.create_text(xright, y0, text=str(ResTxt), fill=COLORgrid, anchor="w", font=("arial", 10 ))
        # 
        i = i + 1
    IAca.create_line(xcenter, y0, xcenter, y1, fill=COLORgrid, width=2)
    IAca.create_line(x0, ycenter, x1, ycenter, fill=COLORgrid, width=2)
    RAngle = math.radians(45)
    y = TRadius*math.sin(RAngle)
    x = TRadius*math.cos(RAngle)
    IAca.create_line(xcenter-x, ycenter-y, xcenter+x, ycenter+y, fill=COLORgrid, width=2)
    IAca.create_line(xcenter+x, ycenter-y, xcenter-x, ycenter+y, fill=COLORgrid, width=2)
    IAca.create_text(x0, ycenter, text="180", fill=COLORgrid, anchor="e", font=("arial", 10 ))
    IAca.create_text(x1, ycenter, text="0.0", fill=COLORgrid, anchor="w", font=("arial", 10 ))
    IAca.create_text(xcenter, y0, text="90", fill=COLORgrid, anchor="s", font=("arial", 10 ))
    IAca.create_text(xcenter, y1, text="-90", fill=COLORgrid, anchor="n", font=("arial", 10 ))
    #
    IAca.create_text(xcenter-x, ycenter-y, text="135", fill=COLORgrid, anchor="se", font=("arial", 10 ))
    IAca.create_text(xcenter+x, ycenter-y, text="45", fill=COLORgrid, anchor="sw", font=("arial", 10 ))
    IAca.create_text(xcenter-x, ycenter+y, text="-135", fill=COLORgrid, anchor="ne", font=("arial", 10 ))
    IAca.create_text(xcenter+x, ycenter+y, text="-45", fill=COLORgrid, anchor="nw", font=("arial", 10 ))
    # Draw traces
    x1 = xcenter + ( ImpedanceRseries / OhmsperPixel )
    if x1 > 1500:
        x1 = xright
    elif x1 < -500:
        x1 = xcenter - xright
    IAca.create_line(xcenter, ycenter, x1, ycenter, fill=COLORtrace1, width=3)
    y1 = ycenter - ( ImpedanceXseries / OhmsperPixel )
    if y1 > 1500:
        y1 = xright
    elif y1 < -500:
        y1 = ycenter - xright
    xmag = x1
    ymag = y1
    IAca.create_line(xcenter, ycenter, xcenter, y1, fill=COLORtrace6, width=3)
    MagRadius = ImpedanceMagnitude / OhmsperPixel
    y1 = ycenter - MagRadius*math.sin(math.radians(ImpedanceAngle))
    if y1 > 1500:
        y1 = xright
    elif y1 < -500:
        y1 = ycenter - xright
    x1 = xcenter + MagRadius*math.cos(math.radians(ImpedanceAngle))
    if x1 > 1500:
        x1 = xright
    elif x1 < -500:
        x1 = xcenter - xright
    IAca.create_line(xcenter, ycenter, x1, y1, fill=COLORtrace2, width=3)

# display warning if input out of range
    if OverRangeFlagA == 1:
        x = X0LIA+GRWIA+10
        y = Y0TIA+GRHIA-40
        IAca.create_rectangle(x-6, y-6, x+6, y+6, fill="#ff0000")
        IAca.create_text (x+12, y, text="CHA Over Range", anchor=W, fill="#ff0000", font=("arial", 12 ))
    if OverRangeFlagB == 1:
        x = X0LIA+GRWIA+10
        y = Y0TIA+GRHIA-10
        IAca.create_rectangle(x-6, y-6, x+6, y+6, fill="#ff0000")
        IAca.create_text (x+12, y, text="CHB Over Range", anchor=W, fill="#ff0000", font=("arial", 12 ))
    # General information on top of the grid
    if SAMPLErate >= 1000000:
        SR_string = str(int(SAMPLErate/1000000)) + " MSPS"
    else:
        SR_string = str(int(SAMPLErate/1000)) + " KSPS"
    txt = "    Sample rate: " + SR_string
    txt = txt + "    FFT samples: " + str(SMPfft)

    txt = txt + "   " + FFTwindowname
        
    x = X0LIA
    y = 12
    idTXT = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    #
    x = X0LIA + GRWIA + 4
    y = 24
    txt = "Gain " + ' {0:.2f} '.format(PeakdbB-PeakdbA) + " dB" 
    TXT9  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = "Phase " + ' {0:.2f} '.format(PeakRelPhase) + " Degrees"
    TXT10  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    if PeakfreqA >= 1000000:
        txt = "Freq " + ' {0:.4f} '.format(PeakfreqA/1000000) + " MHz"
    elif PeakfreqA >= 1000:
        txt = "Freq " + ' {0:.4f} '.format(PeakfreqA/1000) + " KHz"
    else:
        txt = "Freq " + ' {0:.1f} '.format(PeakfreqA) + " Hertz"
    TXT11  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = "Impedance Magnitude"
    TXT1 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = ' {0:.1f} '.format(ImpedanceMagnitude)
    TXT2 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = "Impedance Angle" 
    TXT3 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = ' {0:.1f} '.format(ImpedanceAngle)
    TXT4 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = "Impedance R series"
    TXT5 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = ' {0:.1f} '.format(ImpedanceRseries)
    TXT6 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = "Impedance X series"
    TXT7 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
    y = y + 24
    txt = ' {0:.1f} '.format(ImpedanceXseries)
    TXT8 = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 14 ))
#
    if ImpedanceXseries < 0: # calculate series capacitance
        y = y + 24
        txt = "Series Capacitance"
        IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 12 ))
        try:
            Cseries = -1 / ( 2 * 3.14159 * PeakfreqA * ImpedanceXseries ) # in farads
        except:
            Cseries = 1.0
        Cseries = Cseries * 1E6
        y = y + 20
        if Cseries < 1:
            Cseries = Cseries * 1E3
            if Cseries < 1:
                Cseries = Cseries * 1E3
                txt = ' {0:.1f} '.format(Cseries) + "pF"
            else:
                txt = ' {0:.3f} '.format(Cseries) + "nF"
        else:
            txt = ' {0:.3f} '.format(Cseries) + "uF"
        IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 12 ))
        y = y + 20
        dissp = abs(ImpedanceRseries/ImpedanceXseries) * 100 # Dissipation factor is ratio of XR to XC in percent
        txt = 'D =  {0:.2f} '.format(dissp) + " %"
        IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 12 ))
    elif ImpedanceXseries > 0: # calculate series inductance
        y = y + 24
        txt = "Series Inductance"
        IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 12 ))
        try:
            Lseries = ImpedanceXseries / ( 2 * 3.14159 * PeakfreqA ) # in henry
        except:
            Lseries = 1000
        Lseries = Lseries * 1E3 # in millihenry
        y = y + 22
        if Lseries < 1:
            Lseries = Lseries * 1E3
            txt = ' {0:.2f} '.format(Lseries) + "uH"
        else:
            txt = ' {0:.2f} '.format(Lseries) + "mH"
        IAca.create_text(x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 12 ))
        y = y + 20
        qf = abs(ImpedanceXseries/ImpedanceRseries) * 100 # Quality Factor is ratio of XL to XR
        txt = 'Q =  {0:.2f} '.format(qf)
        IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext, font=("arial", 12 ))
    # Start and stop frequency and trace mode
    if SAMPLErate >= 2000000:
        BW_string = str(int(SAMPLErate*0.45/1000000)) + " MHz"
    else:
        BW_string = str(int(SAMPLErate*0.45/1000)) + " KHz"
    txt = "0.0 to " + BW_string
    txt = txt + "  FFT Bandwidth =" + ' {0:.2f} '.format(FFTbandwidth)
        
    x = X0LIA
    y = Y0TIA+GRHIA-13
    idTXT = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    txt = " "
    if FreqTraceMode.get() == 1:
        txt ="Normal mode "

    if FreqTraceMode.get() == 2:
        txt = "Peak hold mode "
    
    if FreqTraceMode.get() == 3:
        txt = "Power average  mode (" + str(TRACEaverage.get()) + ") " 

    if ZEROstuffing.get() > 0:
        txt = txt + "Zero Stuffing = " + str(ZEROstuffing.get())
    # Runstatus and level information
    if (RUNstatus.get() == 0):
        txt = txt + "  Stopped "
    else:
        txt = txt + "  Running "
    y = Y0TIA+GRHIA
    IDtxt  = IAca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
#
def IACaresize(event):
    global IAca, GRWIA, XOLIA, GRHIA, Y0TIA, CANVASwidthIA, CANVASheightIA
    
    CANVASwidthIA = event.width
    CANVASheightIA = event.height
    GRWIA = CANVASwidthIA - (2 * X0LIA) - 170 # new grid width
    GRHIA = CANVASheightIA - Y0TIA - 10     # new grid height
    UpdateIAAll()
#
# ================ Make IA Window ==========================
def MakeIAWindow():
    global iawindow, IAca, logo, IAScreenStatus, RsystemEntry, IADisp, AWGSync
    global COLORcanvas, CANVASwidthIA, CANVASheightIA, RevDate, AWGAMode, AWGAShape, AWGBMode
    global FFTwindow, CutDC, ColorMode, ResScale, GainCorEntry, PhaseCorEntry
    global CANVASwidthIA, GRWIA, X0LIA, CANVASheightIA, GRHIA, Y0TIA, CH1GainSA, CH2GainSA

    if IAScreenStatus.get() == 0:
        IAScreenStatus.set(1)
        IADisp.set(1)
        CutDC.set(1) # set to remove DC
        CANVASwidthIA = 170 + GRWIA + 2 * X0LIA     # The canvas width
        CANVASheightIA = GRHIA + Y0TIA + 10         # The canvas height
        iawindow = Toplevel()
        iawindow.title("Impedance Analyzer 2.0 " + RevDate)
        iawindow.protocol("WM_DELETE_WINDOW", DestroyIAScreen)
        frame2iar = Frame(iawindow, borderwidth=5, relief=RIDGE)
        frame2iar.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2ia = Frame(iawindow, borderwidth=5, relief=RIDGE)
        frame2ia.pack(side=TOP, expand=YES, fill=BOTH)

        IAca = Canvas(frame2ia, width=CANVASwidthIA, height=CANVASheightIA, background=COLORcanvas, cursor='cross')
        IAca.bind("<Configure>", IACaresize)
        IAca.bind("<Return>", DoNothing)
        IAca.pack(side=TOP, expand=YES, fill=BOTH)

        # menu buttons
        rsemenu = Frame( frame2iar )
        rsemenu.pack(side=TOP)
        rseb2 = Button(rsemenu, text="Stop", style="Stop.TButton", command=BStop)
        rseb2.pack(side=RIGHT)
        rseb3 = Button(rsemenu, text="Run", style="Run.TButton", command=BStart)
        rseb3.pack(side=RIGHT)
        #
        smpmenu = Frame( frame2iar )
        smpmenu.pack(side=TOP)
        smpb1 = Button(smpmenu, text="-Samples", style="W8.TButton", command=Bsamples1)
        smpb1.pack(side=LEFT)
        smpb2 = Button(smpmenu, text="+Samples", style="W8.TButton", command=Bsamples2)
        smpb2.pack(side=LEFT)
        #
        FFTwindmenu = Menubutton(frame2iar, text="FFTwindow", style="W11.TButton")
        FFTwindmenu.menu = Menu(FFTwindmenu, tearoff = 0 )
        FFTwindmenu["menu"]  = FFTwindmenu.menu
        FFTwindmenu.menu.add_radiobutton(label='Rectangular window (B=1)', variable=FFTwindow, value=0)
        FFTwindmenu.menu.add_radiobutton(label='Cosine window (B=1.24)', variable=FFTwindow, value=1)
        FFTwindmenu.menu.add_radiobutton(label='Triangular window (B=1.33)', variable=FFTwindow, value=2)
        FFTwindmenu.menu.add_radiobutton(label='Hann window (B=1.5)', variable=FFTwindow, value=3)
        FFTwindmenu.menu.add_radiobutton(label='Blackman window (B=1.73)', variable=FFTwindow, value=4)
        FFTwindmenu.menu.add_radiobutton(label='Nuttall window (B=2.02)', variable=FFTwindow, value=5)
        FFTwindmenu.menu.add_radiobutton(label='Flat top window (B=3.77)', variable=FFTwindow, value=6)
        FFTwindmenu.pack(side=TOP)
        # right side drop down menu buttons
        dropmenu = Frame( frame2iar )
        dropmenu.pack(side=TOP)
        # File menu 
        Filemenu = Menubutton(dropmenu, text="File", style="W5.TButton")
        Filemenu.menu = Menu(Filemenu, tearoff = 0 )
        Filemenu["menu"] = Filemenu.menu
        Filemenu.menu.add_command(label="Save Config", command=BSaveConfigIA)
        Filemenu.menu.add_command(label="Load Config", command=BLoadConfigIA)
        Filemenu.menu.add_command(label="Save V Cal", command=BSaveCal)
        Filemenu.menu.add_command(label="Load V Cal", command=BLoadCal)
        Filemenu.menu.add_command(label="Save Screen", command=BSaveScreenIA)
        Filemenu.menu.add_command(label="Help", command=BHelp)
        Filemenu.pack(side=LEFT, anchor=W)
        #
        Optionmenu = Menubutton(dropmenu, text="Options", style="W8.TButton")
        Optionmenu.menu = Menu(Optionmenu, tearoff = 0 )
        Optionmenu["menu"]  = Optionmenu.menu
        Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
        Optionmenu.menu.add_checkbutton(label='Cut-DC', variable=CutDC)
        Optionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
        Optionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
        Optionmenu.pack(side=LEFT, anchor=W)
        # Temp set source resistance to 1000
        rsystem = Frame( frame2iar )
        rsystem.pack(side=TOP)
        rsystemlab = Label(rsystem, text="Ext Res")
        rsystemlab.pack(side=LEFT, anchor=W)
        RsystemEntry = Entry(rsystem, width=7)
        RsystemEntry.bind('<MouseWheel>', onTextScroll)
        RsystemEntry.bind('<Key>', onTextKey)
        RsystemEntry.pack(side=LEFT, anchor=W)
        RsystemEntry.delete(0,"end")
        RsystemEntry.insert(4,1000)
        # Res Sacle Spinbox
        ressb = Frame( frame2iar )
        ressb.pack(side=TOP)
        reslab = Label(ressb, text="Ohms/div ")
        reslab.pack(side=LEFT)
        ResScale = Spinbox(ressb, width=7, values=ResScalediv)
        ResScale.bind('<MouseWheel>', onSpinBoxScroll)
        ResScale.pack(side=LEFT)
        ResScale.delete(0,"end")
        ResScale.insert(0,500)
        # V scale / gain
        ar1ialab = Label(frame2iar, text="CH1 Gain")
        ar1ialab.pack(side=TOP)
        AnaRange1ia = Frame( frame2iar )
        AnaRange1ia.pack(side=TOP)
        ar1ia = Radiobutton(AnaRange1ia, text="High", variable=CH1GainSA, value=0) #, command=UpdateFreqTrace )
        ar1ia.pack(side=LEFT)
        ar2ia = Radiobutton(AnaRange1ia, text="Low", variable=CH1GainSA, value=1) #, command=UpdateFreqTrace )
        ar2ia.pack(side=LEFT)
        ar2ialab = Label(frame2iar, text="CH2 Gain")
        ar2ialab.pack(side=TOP)
        AnaRange2ia = Frame( frame2iar )
        AnaRange2ia.pack(side=TOP)
        ar3ia = Radiobutton(AnaRange2ia, text="High", variable=CH2GainSA, value=0) #, command=UpdateFreqTrace )
        ar3ia.pack(side=LEFT)
        ar4ia = Radiobutton(AnaRange2ia, text="Low", variable=CH2GainSA, value=1) #, command=UpdateFreqTrace )
        ar4ia.pack(side=LEFT)
        #
        GainCor = Frame( frame2iar )
        GainCor.pack(side=TOP)
        GainCorlab = Label(GainCor, text="Gain Cor dB")
        GainCorlab.pack(side=LEFT, anchor=W)
        GainCorEntry = Entry(GainCor, width=7)
        GainCorEntry.bind('<MouseWheel>', onTextScroll)
        GainCorEntry.bind('<Key>', onTextKey)
        GainCorEntry.pack(side=LEFT, anchor=W)
        GainCorEntry.delete(0,"end")
        GainCorEntry.insert(4,0.0)
        #
        PhaseCor = Frame( frame2iar )
        PhaseCor.pack(side=TOP)
        PhaseCorlab = Label(PhaseCor, text="Phase Cor")
        PhaseCorlab.pack(side=LEFT, anchor=W)
        PhaseCorEntry = Entry(PhaseCor, width=7)
        PhaseCorEntry.bind('<MouseWheel>', onTextScroll)
        PhaseCorEntry.bind('<Key>', onTextKey)
        PhaseCorEntry.pack(side=LEFT, anchor=W)
        PhaseCorEntry.delete(0,"end")
        PhaseCorEntry.insert(4,0.0)
        
        dismiss1button = Button(frame2iar, text="Dismiss", style="W8.TButton", command=DestroyIAScreen)
        dismiss1button.pack(side=TOP)
        # add ADI logo Don't mess with bit map data!

        ADI1 = Label(frame2iar, image=logo, anchor= "sw", height=49, width=116, compound="top")
        ADI1.pack(side=TOP)
        IACheckBox()

def DestroyIAScreen():
    global iawindow, IAScreenStatus, IAca, IADisp
    
    IAScreenStatus.set(0)
    IADisp.set(0)
    IACheckBox()
    iawindow.destroy()
#
def STOREcsvfile():     # Store the trace as CSV file [frequency, magnitude or dB value]
    global FFTmemoryA, FFTresultA
    global FFTmemoryB, FFTresultB
    global PhaseA, PhaseB, freqwindow
    global SAMPLErate, ShowC1_VdB, ShowC2_VdB
    
    # Set the TRACEsize variable
    if ShowC1_VdB.get() == 1:
        TRACEsize = len(FFTresultA)     # Set the trace length
    elif ShowC2_VdB.get() == 1:
        TRACEsize = len(FFTresultB)
    if TRACEsize == 0:                  # If no trace, skip rest of this routine
        return()
# ask if save as magnitude or dB
    dB = askyesno("Mag or dB: ","Save amplidude data as dB (Yes) or Mag (No):\n", parent=freqwindow)
    # Make the file name and open it
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
    filename = "Spectrum-" + tme
    filename = filename + ".csv"
    # open file to save data
    filename = asksaveasfilename(initialfile = filename, defaultextension = ".csv",
                                 filetypes=[("Comma Separated Values", "*.csv")], parent=freqwindow)
    DataFile = open(filename,'a')  # Open output file
    HeaderString = 'Frequency-#, '
    if ShowC1_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'C1-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'C1-Mag, '
    if ShowC2_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'C2-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'C2-Mag, '
    if ShowC1_P.get() == 1:
        HeaderString = HeaderString + 'Phase 1-2, '
    if ShowC2_P.get() == 1:
        HeaderString = HeaderString + 'Phase 2-1, '
    HeaderString = HeaderString + '\n'
    DataFile.write( HeaderString )

    Fsample = float(SAMPLErate / 2) / (TRACEsize - 1)   # Frequency step per sample   

    n = 0
    while n < TRACEsize:
        F = n * Fsample
        txt = str(F)
        if ShowC1_VdB.get() == 1:
            if dB == 1:
                V = 10 * math.log10(float(FFTresultA[n])) + 17  # Add 17 dB for max value of +10 dB
            else:
                V = 7.079458 * math.sqrt(float(FFTresultA[n]))   # scale to Vrms
                #V = 50.12 * float(FFTresultA[n])# scale to Vrms
            txt = txt + "," + str(V) 
        if ShowC2_VdB.get() == 1:
            if dB == 1:
                V = 10 * math.log10(float(FFTresultB[n])) + 17  # Add 17 dB for max value of +10 dB
            else:
                V = 7.079458 * math.sqrt(float(FFTresultA[n]))   # scale to Vrms
                #V = 50.12 * float(FFTresultB[n]) # scale to Vrms
            txt = txt  + "," + str(V)
        if ShowC1_P.get() == 1:
            RelPhase = PhaseA[n]-PhaseB[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        if ShowC2_P.get() == 1:
            RelPhase = PhaseB[n]-PhaseA[n]
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            txt = txt + "," + str(RelPhase)
        txt = txt + "\n"
        DataFile.write(txt)
        n = n + 1    

    DataFile.close()                           # Close the file

def MakeFreqScreen():       # Update the screen with traces and text
    global CANVASheightF, CANVASwidthF, SmoothCurvesSA
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM, PeakIndexA, PeakIndexB, Fsample
    global COLORgrid    # The colors
    global COLORsignalband, COLORtext
    global COLORtrace1, COLORtrace2
    global FSweepMode, LoopNum, MarkerFreqNum, TRACEwidth, GridWidth
    global DBdivindex   # Index value
    global DBdivlist    # dB per division list
    global DBlevel      # Reference level
    global FFTwindow, FFTbandwidth, ZEROstuffing, FFTwindowname
    global X0LF          # Left top X value
    global Y0TF          # Left top Y value
    global GRWF          # Screenwidth
    global GRHF          # Screenheight
    global RUNstatus    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global SAMPLErate, SingleShot, HScale, HarmonicMarkers
    global SMPfft       # number of FFT samples
    global StartFreqEntry, StopFreqEntry
    global ShowC1_P, ShowC2_P, ShowRA_VdB, ShowRB_VdB, ShowMarker
    global ShowRA_P, ShowRB_P, ShowMathSA, FreqDisp
    global ShowFCur, ShowdBCur, FCursor, dBCursor
    global T1Fline, T2Fline, T1Pline, T1FRline, T2FRline, TFMline, TFRMline
    global T1PRline, T2PRline
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv         # Number of vertical divisions

    # Delete all items on the screen
    de = Freqca.find_enclosed( -1000, -1000, CANVASwidthF+1000, CANVASheightF+1000 )
    MarkerFreqNum = 0
    for n in de: 
        Freqca.delete(n)
    try:
        StartFrequency = float(StartFreqEntry.get())
    except:
        StartFreqEntry.delete(0,"end")
        StartFreqEntry.insert(0,100)
        StartFrequency = 100
    try:
        StopFrequency = float(StopFreqEntry.get())
    except:
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,100)
        StopFrequency = 10000
    # Draw horizontal grid lines
    i = 0
    x1 = X0LF
    x2 = X0LF + GRWF
    while (i <= Vdiv.get()):
        y = Y0TF + i * GRHF/Vdiv.get()
        Dline = [x1,y,x2,y]
        if i == 0 or i == Vdiv.get():
            Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
        else:
            Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
        Vaxis_value = (DBlevel.get() - (i * DBdivlist[DBdivindex.get()]))
        Vaxis_label = str(Vaxis_value)
        Freqca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
        if ShowC1_P.get() == 1 or ShowC2_P.get() == 1:
            Vaxis_value = ( 180 - ( i * (360 / Vdiv.get())))
            Vaxis_label = str(Vaxis_value)
            Freqca.create_text(x2+3, y, text=Vaxis_label, fill=COLORtrace3, anchor="w", font=("arial", 8 ))
        i = i + 1
    # Draw vertical grid lines
    i = 0
    y1 = Y0TF
    y2 = Y0TF + GRHF
    if HScale.get() == 1:
        F = 1.0
        LogFStop = math.log10(StopFrequency)
        try:
            LogFStart = math.log10(StartFrequency)
        except:
            LogFStart = 0.0
        LogFpixel = (LogFStop - LogFStart) / GRWF
        # draw left and right edges
        while F <= StopFrequency:
            if F >= StartFrequency:
                try:
                    LogF = math.log10(F) # convet to log Freq
                    x = X0LF + (LogF - LogFStart)/LogFpixel
                except:
                    x = X0LF
                Dline = [x,y1,x,y2]
                if F == 1 or F == 10 or F == 100 or F == 1000 or F == 10000 or F == 100000 or F == 1000000 or F == 10000000:
                    Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    if F >= 1000000:
                        axis_label = str(int(F/1000000)) + " MHz"
                    elif F >= 1000:
                        axis_label = str(int(F/1000)) + " KHz" 
                    else:
                        axis_label = str(F) + " Hz" 
                    Freqca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
                else:
                    Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
                
            if F < 10:
                F = F + 1
            elif F < 100:
                F = F + 10
            elif F < 1000:
                F = F + 100
            elif F < 1000:
                F = F + 100
            elif F < 10000:
                F = F + 1000
            elif F < 100000:
                F = F + 10000
            elif F < 1000000:
                F = F + 100000
            elif F < 10000000:
                F = F + 1000000
    else:
        Freqdiv = (StopFrequency - StartFrequency) / 10
        while (i < 11):
            x = X0LF + i * GRWF/10
            Dline = [x,y1,x,y2]
            if i == 0 or i == 10:
                Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            axis_value = (StartFrequency + (i * Freqdiv))
            if axis_value >= 1000000:
                axis_label = str(int(axis_value/1000000)) + " MHz"
            elif axis_value >= 1000:
                axis_label = str(int(axis_value/1000)) + " KHz" 
            else:
                axis_label = str(axis_value) + " Hz"
            Freqca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
            i = i + 1
    # Draw X - Y cursors if needed
    Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
    Yc = float(Y0TF) + Yconv * (DBlevel.get()) # Yc is the 0 dBm position, can be outside the screen!
    Fpixel = (StopFrequency - StartFrequency) / GRWF # Frequency step per screen pixel
    if ShowFCur.get() > 0:
        Dline = [FCursor, Y0TF, FCursor, Y0TF+GRHF]
        Freqca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScale.get() == 1:
            LogFStop = math.log10(StopFrequency)
            try:
                LogFStart = math.log10(StartFrequency)
            except:
                LogFStart = 0.0
            LogFpixel = (LogFStop - LogFStart) / GRWF
            xfreq = 10**(((FCursor-X0LF)*LogFpixel) + LogFStart)
        else:
            Fpixel = (StopFrequency - StartFrequency) / GRWF # Frequency step per screen pixel
            xfreq = ((FCursor-X0LF)*Fpixel)+StartFrequency
        XFString = ' {0:.2f} '.format(xfreq)
        V_label = XFString + " Hz"
        Freqca.create_text(FCursor+1, dBCursor-5, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
#
    if ShowdBCur.get() > 0:
        Dline = [X0LF, dBCursor, X0LF+GRWF, dBCursor]
        Freqca.create_line(Dline, dash=(3,4), fill=COLORtrigger, width=GridWidth.get())
        if ShowdBCur.get() == 1:# Vertical conversion factorsand border limits
            Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
            Yc = float(Y0TF) + Yconv * (DBlevel.get()) # Yc is the 0 dBm position, can be outside the screen!
            yvdB = ((Yc-dBCursor)/Yconv)
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " dBV"
        else:
            Yconv = float( GRHF / 360.0 ) # pixels per degree
            Yc = float(Y0TF + (GRHF/2.0)) # Yc is the 0 degree position
            yvdB = ((Yc-dBCursor)/Yconv)
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " deg"
        Freqca.create_text(FCursor+1, dBCursor+5, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
    #
    SmoothBool = SmoothCurvesSA.get()
    # Draw traces
    if len(T1Fline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CH1
        if OverRangeFlagA == 1:
            Freqca.create_line(T1Fline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Freqca.create_line(T1Fline, fill=COLORtrace1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() > 0:
            k = 1
            while k <= HarmonicMarkers.get():
                dbA = (10 * math.log10(float(FFTresultA[PeakIndexA*k])) + 17)
                FreqA = k*PeakIndexA*Fsample
                if ShowMarker.get() == 2 and k > 1:
                    Peak_label = ' {0:.2f} '.format(dbA - PeakdbA) + ',' + ' {0:.1f} '.format(FreqA - PeakfreqA)
                else:
                    Peak_label = ' {0:.2f} '.format(dbA) + ',' + ' {0:.1f} '.format(FreqA)
                if HScale.get() == 1:
                    try:
                        LogF = math.log10(FreqA) # convet to log Freq
                        xA = X0LF + int((LogF - LogFStart)/LogFpixel)
                    except:
                        xA = X0LF
                else:
                    xA = X0LF+int((FreqA - StartFrequency)/Fpixel)# +StartFrequency
                yA = Yc - Yconv * dbA
                Freqca.create_text(xA, yA, text=Peak_label, fill=COLORtrace1, anchor="s", font=("arial", 8 ))
                k = k + 1
    if len(T2Fline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CH2
        if OverRangeFlagB == 1:
            Freqca.create_line(T2Fline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Freqca.create_line(T2Fline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() > 0:
            k = 1
            while k <= HarmonicMarkers.get():
                dbB = (10 * math.log10(float(FFTresultB[PeakIndexB*k])) + 17)
                FreqB = k*PeakIndexB*Fsample
                if ShowMarker.get() == 2 and k > 1:
                    Peak_label = ' {0:.2f} '.format(dbB - PeakdbB) + ',' + ' {0:.1f} '.format(FreqB - PeakfreqB)
                else:
                    Peak_label = ' {0:.2f} '.format(dbB) + ',' + ' {0:.1f} '.format(FreqB)
                if HScale.get() == 1:
                    try:
                        LogF = math.log10(FreqB) # convet to log Freq
                        xB = X0LF + int((LogF - LogFStart)/LogFpixel)
                    except:
                        xB = X0LF
                else:
                    xB = X0LF+int((FreqB - StartFrequency)/Fpixel)# +StartFrequency
                yB = Yc - Yconv * dbB
                Freqca.create_text(xB, yB, text=Peak_label, fill=COLORtrace2, anchor="s", font=("arial", 8 ))
                k = k + 1
    if len(T1Pline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Freqca.create_line(T1Pline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(T2Pline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Freqca.create_line(T2Pline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRA_VdB.get() == 1 and len(T1FRline) > 4:   # Write the ref trace A if active
        Freqca.create_line(T1FRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRA) + ',' + ' {0:.1f} '.format(PeakfreqRA)
            Freqca.create_text(PeakxRA, PeakyRA, text=Peak_label, fill=COLORtraceR1, anchor="s", font=("arial", 8 ))
    if ShowRB_VdB.get() == 1 and len(T2FRline) > 4:   # Write the ref trace B if active
        Freqca.create_line(T2FRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRB) + ',' + ' {0:.1f} '.format(PeakfreqRB)
            Freqca.create_text(PeakxRB, PeakyRB, text=Peak_label, fill=COLORtraceR2, anchor="s", font=("arial", 8 ))
    if ShowRA_P.get() == 1 and len(T1PRline) > 4:   # Write the ref trace A if active
        Freqca.create_line(T1PRline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRB_P.get() == 1 and len(T2PRline) > 4:   # Write the ref trace A if active
        Freqca.create_line(T2PRline, fill=COLORtraceR4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMathSA.get() > 0 and len(TFMline) > 4:   # Write the Math trace if active
        Freqca.create_line(TFMline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() ==1:
            Peak_label = ' {0:.2f} '.format(PeakMdb) + ',' + ' {0:.1f} '.format(PeakfreqM)
            Freqca.create_text(PeakxM, PeakyM, text=Peak_label, fill=COLORtrace5, anchor="s", font=("arial", 8 ))
    if ShowRMath.get() == 1 and len(TFRMline) > 4:   # Write the ref math trace if active
        Freqca.create_line(TFRMline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarker.get() ==1:
            Peak_label = ' {0:.2f} '.format(PeakRMdb) + ',' + ' {0:.1f} '.format(PeakfreqRM)
            Freqca.create_text(PeakxRM, PeakyRM, text=Peak_label, fill=COLORtraceR5, anchor="s", font=("arial", 8 ))
    # General information on top of the grid
    if SAMPLErate >= 1000000:
        SR_string = str(int(SAMPLErate/1000000)) + " MSPS"
    else:
        SR_string = str(int(SAMPLErate/1000)) + " KSPS"
    txt = "    Sample rate: " + SR_string
    txt = txt + "    FFT samples: " + str(SMPfft)

    txt = txt + "   " + FFTwindowname
        
    x = X0LF
    y = 12
    idTXT = Freqca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

    # Start and stop frequency and dB/div and trace mode
    txt = str(StartFrequency) + " to " + str(StopFrequency) + " Hz"
    txt = txt +  "  " + str(DBdivlist[DBdivindex.get()]) + " dB/div"
    txt = txt + "  Level: " + str(DBlevel.get()) + " dB "
    if FFTwindow.get() < 7:
        txt = txt + "  FFT Bandwidth =" + ' {0:.2f} '.format(FFTbandwidth)
    else:
        txt = txt + "  FFT Bandwidth = ???" 
    
    x = X0LF
    y = Y0TF+GRHF+23
    idTXT = Freqca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    
    if FreqTraceMode.get() == 1:
        txt ="Normal mode "

    if FreqTraceMode.get() == 2:
        txt = "Peak hold mode "
    
    if FreqTraceMode.get() == 3:
        txt = "Power average  mode (" + str(TRACEaverage.get()) + ") " 

    if ZEROstuffing.get() > 0:
        txt = txt + "Zero Stuffing = " + str(ZEROstuffing.get())
    # Runstatus and level information
    if (RUNstatus.get() == 0) and (SingleShot.get() == 0):
        txt = txt + "  Stopped "
    elif SingleShot.get() == 1:
        txt = txt + "  Single Shot Trace "
    else:
        if FreqDisp.get() == 1:
            txt = txt + "  Running "
        else:
            txt = txt + "  Display off "
    x = X0LF
    y = Y0TF+GRHF+34
    IDtxt  = Freqca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)

def INITIALIZEstart():
    global SMPfft, FFTwindow
    global SMPfftpwrTwo, BodeDisp
    global TRACEresetFreq, FreqTraceMode, LoopNum, FSweepMode, FSweepCont

    # First some subroutines to set specific variables
    if BodeDisp.get() == 0:
        if FFTwindow.get() != 8:
            SMPfft = 2 ** int(SMPfftpwrTwo.get()) # Calculate the number of FFT samples from SMPfftpwrtwo

    CALCFFTwindowshape()
    if FreqTraceMode.get() == 1 and TRACEresetFreq == False:
        TRACEresetFreq = True               # Clear the memory for averaging or peak
    if FreqTraceMode.get() == 2 and LoopNum.get() == 1 and FSweepMode.get() > 0 and FSweepCont.get() == 0 and BodeDisp.get() >0:
        TRACEresetFreq = True               # Clear the memory for peak hold when using sweep generator

def CALCFFTwindowshape():           # Make the FFTwindowshape for the windowing function
    global FFTbandwidth             # The FFT bandwidth
    global FFTwindow                # Which FFT window number is selected
    global FFTwindowname            # The name of the FFT window function
    global FFTwindowshape           # The window shape
    global SAMPLErate               # The sample rate
    global SMPfft                   # Number of FFT samples
    global LastWindow, LastSMPfft
    
    if LastWindow == FFTwindow.get() and LastSMPfft == SMPfft:
        # recalculate window only if something changed
        return
    # FFTname and FFTbandwidth in milliHz
    FFTwindowname = "No such window"
    FFTbw = 0
    
    if FFTwindow.get() == 0:
        FFTwindowname = " Rectangular (no) window (B=1) "
        FFTbw = 1.0

    if FFTwindow.get() == 1:
        FFTwindowname = " Cosine window (B=1.24) "
        FFTbw = 1.24

    if FFTwindow.get() == 2:
        FFTwindowname = " Triangular window (B=1.33) "
        FFTbw = 1.33

    if FFTwindow.get() == 3:
        FFTwindowname = " Hann window (B=1.5) "
        FFTbw = 1.5

    if FFTwindow.get() == 4:
        FFTwindowname = " Blackman window (B=1.73) "
        FFTbw = 1.73

    if FFTwindow.get() == 5:
        FFTwindowname = " Nuttall window (B=2.02) "
        FFTbw = 2.02

    if FFTwindow.get() == 6:
        FFTwindowname = " Flat top window (B=3.77) "
        FFTbw = 3.77
        
    if FFTwindow.get() == 7:
        FFTwindowname = FFTUserWindowString
        FFTbw = 0.0
        try:
            FFTwindowshape = eval(FFTUserWindowString)
        except:
            FFTwindowshape = numpy.ones(SMPfft)         # Initialize with ones
    elif FFTwindow.get() == 8: # window shape array read from csv file
        FFTwindowname = "Window Shape From file"
        FFTbw = 0.0
    else:
        FFTbandwidth = int(FFTbw * SAMPLErate / float(SMPfft)) 
        # Calculate the shape
        FFTwindowshape = numpy.ones(SMPfft)         # Initialize with ones
        n = 0
        while n < SMPfft:
            # Cosine window function - medium-dynamic range B=1.24
            if FFTwindow.get() == 1:
                w = math.sin(math.pi * n / (SMPfft - 1))
                FFTwindowshape[n] = w * 1.571
            # Triangular non-zero endpoints - medium-dynamic range B=1.33
            if FFTwindow.get() == 2:
                w = (2.0 / SMPfft) * ((SMPfft/ 2.0) - abs(n - (SMPfft - 1) / 2.0))
                FFTwindowshape[n] = w * 2.0
            # Hann window function - medium-dynamic range B=1.5
            if FFTwindow.get() == 3:
                w = 0.5 - 0.5 * math.cos(2 * math.pi * n / (SMPfft - 1))
                FFTwindowshape[n] = w * 2.000
            # Blackman window, continuous first derivate function - medium-dynamic range B=1.73
            if FFTwindow.get() == 4:
                w = 0.42 - 0.5 * math.cos(2 * math.pi * n / (SMPfft - 1)) + 0.08 * math.cos(4 * math.pi * n / (SMPfft - 1))
                FFTwindowshape[n] = w * 2.381
            # Nuttall window, continuous first derivate function - high-dynamic range B=2.02
            if FFTwindow.get() == 5:
                w = 0.355768 - 0.487396 * math.cos(2 * math.pi * n / (SMPfft - 1)) + 0.144232 * math.cos(4 * math.pi * n / (SMPfft - 1))- 0.012604 * math.cos(6 * math.pi * n / (SMPfft - 1))
                FFTwindowshape[n] = w * 2.811
            # Flat top window, medium-dynamic range, extra wide bandwidth B=3.77
            if FFTwindow.get() == 6:
                w = 1.0 - 1.93 * math.cos(2 * math.pi * n / (SMPfft - 1)) + 1.29 * math.cos(4 * math.pi * n / (SMPfft - 1))- 0.388 * math.cos(6 * math.pi * n / (SMPfft - 1)) + 0.032 * math.cos(8 * math.pi * n / (SMPfft - 1))
                FFTwindowshape[n] = w * 1.000
            n = n + 1
    LastWindow = FFTwindow.get()
    LastSMPfft = SMPfft
    
def BUserFFTwindow():
    global FFTUserWindowString, freqwindow

    TempString = FFTUserWindowString
    FFTUserWindowString = askstring("User FFT Window", "Current User Window: " + FFTUserWindowString + "\n\nNew Window:\n", initialvalue=FFTUserWindowString, parent=freqwindow)
    if (FFTUserWindowString == None):         # If Cancel pressed, then None
        FFTUserWindowString = TempString

def BFileFFTwindow():
    global FFTwindowshape, SMPfft, LastSMPfft, FFTwindow, LastWindow

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=freqwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
        FFTwindowshape = []
        for row in csv_f:
            try:
                FFTwindowshape.append(float(row[0]))
            except:
                print 'skipping non-numeric row'
        FFTwindowshape = numpy.array(FFTwindowshape)
        CSVFile.close()
        SMPfft = len(FFTwindowshape)
        LastSMPfft = SMPfft
        LastWindow = FFTwindow.get()
        print SMPfft
    except:
        showwarning("WARNING","No such file found or wrong format!")
#
def onCanvasFreqRightClick(event):
    global ShowFCur, ShowdBCur, FCursor, dBCursor, RUNstatus, Freqca

    FCursor = event.x
    dBCursor = event.y
    if RUNstatus.get() == 0:
        UpdateFreqScreen()
    Freqca.bind_all('<MouseWheel>', onCanvasFreqClickScroll)
#
def onCanvasFreqClickScroll(event):
    global ShowFCur, ShowdBCur, FCursor, dBCursor, RUNstatus, Freqca
    if event.widget == Freqca:
        ShiftKeyDwn = event.state & 1
        if ShowFCur.get() > 0 and ShiftKeyDwn == 0:
            FCursor = FCursor + event.delta/100
        elif ShowdBCur.get() > 0 or ShiftKeyDwn == 1:
            dBCursor = dBCursor - event.delta/100
        if RUNstatus.get() == 0:
            UpdateFreqScreen()
# 
def onCanvasFreqLeftClick(event):
    global X0LF          # Left top X value 
    global Y0TF          # Left top Y value
    global GRWF          # Screenwidth
    global GRHF          # Screenheight
    global Freqca, MarkerLoc
    global COLORgrid, COLORtext, HScale, ShowC1_VdB, ShowC2_VdB
    global COLORtrace1, COLORtrace2, StartFreqEntry, StopFreqEntry
    global SAMPLErate, RUNstatus, COLORtext, MarkerFreqNum, PrevdBV, PrevF

    if (RUNstatus.get() == 0):
        MarkerFreqNum = MarkerFreqNum + 1
        COLORmarker = COLORgrid
        if ShowC1_VdB.get() == 1:
            COLORmarker = COLORtrace1
        elif ShowC2_VdB.get() == 1:
            COLORmarker = COLORtrace2
        try:
            StartFrequency = float(StartFreqEntry.get())
        except:
            StartFreqEntry.delete(0,"end")
            StartFreqEntry.insert(0,100)
            StartFrequency = 100
        try:
            StopFrequency = float(StopFreqEntry.get())
        except:
            StopFreqEntry.delete(0,"end")
            StopFreqEntry.insert(0,100)
            StopFrequency = 100
        # draw X at marker point and number
        Freqca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORmarker)
        Freqca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORmarker)
        Freqca.create_text(event.x+4, event.y, text=str(MarkerFreqNum), fill=COLORmarker, anchor="w", font=("arial", 8 ))
        # Vertical conversion factors (level dBs) and border limits
        Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
        Yc = float(Y0TF) + Yconv * (DBlevel.get()) # Yc is the 0 dBm position, can be outside the screen!
        Yphconv = float(GRHF) / 360
        Yp = float(Y0TF) + Yphconv + 180
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScale.get() == 1:
            LogFStop = math.log10(StopFrequency)
            try:
                LogFStart = math.log10(StartFrequency)
            except:
                LogFStart = 0.0
            LogFpixel = (LogFStop - LogFStart) / GRWF
            xfreq = 10**(((event.x-X0LF)*LogFpixel) + LogFStart)
        else:
            Fpixel = (StopFrequency - StartFrequency) / GRWF # Frequency step per screen pixel
            xfreq = ((event.x-X0LF)*Fpixel)+StartFrequency

        yvdB = ((Yc-event.y)/Yconv)
        VdBString = ' {0:.1f} '.format(yvdB)
        XFString = ' {0:.2f} '.format(xfreq)
        V_label = str(MarkerFreqNum) + " " + XFString + " Hz, " + VdBString + " dBV"
        if MarkerFreqNum > 1:
            DeltaV = ' {0:.3f} '.format(yvdB-PrevdBV)
            DeltaF = ' {0:.2f} '.format(xfreq-PrevF)
            V_label = V_label + " Delta " + DeltaF + " Hz, " + DeltaV + " dBV"
        x = X0LF + 5
        y = Y0TF + 3 + (MarkerFreqNum*10)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0LF + GRWF - 5
            y = Y0TF + 3 + (MarkerFreqNum*10)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0LF + 5
            y = Y0TF + GRHF + 3 - (MarkerFreqNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0LF + GRWF - 5
            y = Y0TF + GRHF + 3 - (MarkerFreqNum*10)
            Justify = 'e'
        Freqca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", 8 ))
        PrevdBV = yvdB
        PrevF = xfreq
#
def onCanvasSAOne(event):
    global ShowC1_VdB
    if ShowC1_VdB.get() == 0:
        ShowC1_VdB.set(1)
    else:
        ShowC1_VdB.set(0)
#
def onCanvasSATwo(event):
    global ShowC2_VdB
    if ShowC2_VdB.get() == 0:
        ShowC2_VdB.set(1)
    else:
        ShowC2_VdB.set(0)
# 
def onCanvasSAThree(event):
    global ShowC1_P
    if ShowC1_P.get() == 0:
        ShowC1_P.set(1)
    else:
        ShowC1_P.set(0)
#
def onCanvasSAFour(event):
    global ShowC2_P
    if ShowC2_P.get() == 0:
        ShowC2_P.set(1)
    else:
        ShowC2_P.set(0)
#
def onCanvasSAFive(event):
    global ShowMarker
    if ShowMarker.get() == 0:
        ShowMarker.set(1)
    else:
        ShowMarker.set(0)
#
def onCanvasSASix(event):
    global ShowRA_VdB
    if ShowRA_VdB.get() == 0:
        ShowRA_VdB.set(1)
    else:
        ShowRA_VdB.set(0)
# 
def onCanvasSASeven(event):
    global ShowRB_VdB
    if ShowRB_VdB.get() == 0:
        ShowRB_VdB.set(1)
    else:
        ShowRB_VdB.set(0)
#
def onCanvasSAEight(event):
    global ShowMathSA
    ShowMathSA.set(2)
#
def onCanvasSANine(event):
    global ShowMathSA
    ShowMathSA.set(1)
#
def onCanvasSAZero(event):
    global ShowMathSA
    ShowMathSA.set(0)
#
def onCanvasSASnap(event):
    BSTOREtraceSA()
#
def onCanvasSANormal(event):
    BNormalmode()
#
def onCanvasSAPeak(event):
    BPeakholdmode()

def onCanvasSAReset(event):
    BResetFreqAvg()
#
def onCanvasSAAverage(event):
    BAveragemode()
#
def onCanvasShowFcur(event):
    global ShowFCur
    if ShowFCur.get() == 0:
        ShowFCur.set(1)
    else:
        ShowFCur.set(0)
#
def onCanvasShowdBcur(event):
    global ShowdBCur
    if ShowdBCur.get() == 1:
        ShowdBCur.set(0)
    else:
        ShowdBCur.set(1)
#
def onCanvasShowPcur(event):
    global ShowdBCur
    if ShowdBCur.get() == 2:
        ShowdBCur.set(0)
    else:
        ShowdBCur.set(2)
#
def onCanvasBodeRightClick(event):
    global ShowBPCur, ShowBdBCur, BPCursor, BdBCursor, RUNstatus, Bodeca

    BPCursor = event.x
    BdBCursor = event.y
    if RUNstatus.get() == 0:
        UpdateBodeScreen()
    Bodeca.bind_all('<MouseWheel>', onCanvasBodeClickScroll)
#
def onCanvasBodeClickScroll(event):
    global ShowBPCur, ShowBdBCur, BPCursor, BdBCursor, RUNstatus, Bodeca
    if event.widget == Bodeca:
        ShiftKeyDwn = event.state & 1
        if ShowBPCur.get() > 0 and ShiftKeyDwn == 0:
            BPCursor = BPCursor + event.delta/100
        elif ShowBdBCur.get() > 0 or ShiftKeyDwn == 1:
            BdBCursor = BdBCursor - event.delta/100
        if RUNstatus.get() == 0:
            UpdateBodeScreen()
# 
def onCanvasBodeLeftClick(event):
    global X0LBP          # Left top X value 
    global Y0TBP         # Left top Y value
    global GRWBP          # Screenwidth
    global GRHBP          # Screenheight
    global Bodeca, MarkerLoc
    global COLORgrid, COLORtext, HScaleBP, ShowCA_VdB, ShowCB_VdB, DBdivindexBP
    global COLORtrace1, COLORtrace2, StartBodeEntry, StopBodeEntry, DBlevelBP
    global SAMPLErate, RUNstatus, COLORtext, MarkerFreqNum, PrevdBV, PrevF, Vdiv

    if (RUNstatus.get() == 0):
        MarkerFreqNum = MarkerFreqNum + 1
        COLORmarker = COLORgrid
        if ShowCA_VdB.get() == 1:
            COLORmarker = COLORtrace1
        elif ShowCB_VdB.get() == 1:
            COLORmarker = COLORtrace2
        try:
            EndFreq = float(StopBodeEntry.get())
        except:
            StopBodeEntry.delete(0,"end")
            StopBodeEntry.insert(0,10000)
            EndFreq = 10000
        try:
            BeginFreq = float(StartBodeEntry.get())
        except:
            StartBodeEntry.delete(0,"end")
            StartBodeEntry.insert(0,100)
            BeginFreq = 100
        # draw X at marker point and number
        Bodeca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORmarker)
        Bodeca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORmarker)
        Bodeca.create_text(event.x+4, event.y, text=str(MarkerFreqNum), fill=COLORmarker, anchor="w", font=("arial", 8 ))
        # Vertical conversion factors (level dBs) and border limits
        Yconv = float(GRHBP) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
        Yc = float(Y0TBP) + Yconv * (DBlevelBP.get()) # Yc is the 0 dBm position, can be outside the screen!
        Yphconv = float(GRHBP) / 360
        Yp = float(Y0TBP) + Yphconv + 180
        # Horizontal conversion factors (frequency Hz) and border limits
        if HScaleBP.get() == 1:
            LogFStop = math.log10(EndFreq)
            try:
                LogFStart = math.log10(BeginFreq)
            except:
                LogFStart = 0.0
            LogFpixel = (LogFStop - LogFStart) / GRWBP
            xfreq = 10**(((event.x-X0LBP)*LogFpixel) + LogFStart)
        else:
            Fpixel = (EndFreq - BeginFreq) / GRWBP # Frequency step per screen pixel
            xfreq = ((event.x-X0LBP)*Fpixel)+BeginFreq

        yvdB = ((Yc-event.y)/Yconv)
        VdBString = ' {0:.1f} '.format(yvdB)
        XFString = ' {0:.2f} '.format(xfreq)
        V_label = str(MarkerFreqNum) + " " + XFString + " Hz, " + VdBString + " dBV"
        if MarkerFreqNum > 1:
            DeltaV = ' {0:.3f} '.format(yvdB-PrevdBV)
            DeltaF = ' {0:.2f} '.format(xfreq-PrevF)
            V_label = V_label + " Delta " + DeltaF + " Hz, " + DeltaV + " dBV"
        x = X0LBP + 5
        y = Y0TBP + 3 + (MarkerFreqNum*10)
        Justify = 'w'
        if MarkerLoc == 'UR' or MarkerLoc == 'ur':
            x = X0LBP + GRWBP - 5
            y = Y0TBP + 3 + (MarkerFreqNum*10)
            Justify = 'e'
        if MarkerLoc == 'LL' or MarkerLoc == 'll':
            x = X0LBP + 5
            y = Y0TBP + GRHBP + 3 - (MarkerFreqNum*10)
            Justify = 'w'
        if MarkerLoc == 'LR' or MarkerLoc == 'lr':
            x = X0LBP + GRWBP - 5
            y = Y0TBP + GRHBP + 3 - (MarkerFreqNum*10)
            Justify = 'e'
        Bodeca.create_text(x, y, text=V_label, fill=COLORmarker, anchor=Justify, font=("arial", 8 ))
        PrevdBV = yvdB
        PrevF = xfreq
#
def onCanvasBdOne(event):
    global ShowCA_VdB
    if ShowCA_VdB.get() == 0:
        ShowCA_VdB.set(1)
    else:
        ShowCA_VdB.set(0)
#
def onCanvasBdTwo(event):
    global ShowCB_VdB
    if ShowCB_VdB.get() == 0:
        ShowCB_VdB.set(1)
    else:
        ShowCB_VdB.set(0)
# 
def onCanvasBdThree(event):
    global ShowCA_P
    if ShowCA_P.get() == 0:
        ShowCA_P.set(1)
    else:
        ShowCA_P.set(0)
#
def onCanvasBdFour(event):
    global ShowCB_P
    if ShowCB_P.get() == 0:
        ShowCB_P.set(1)
    else:
        ShowCB_P.set(0)
#
def onCanvasBdFive(event):
    global ShowMarkerBP
    if ShowMarkerBP.get() == 0:
        ShowMarkerBP.set(1)
    else:
        ShowMarkerBP.set(0)
#
def onCanvasBdSix(event):
    global ShowRA_VdB
    if ShowRA_VdB.get() == 0:
        ShowRA_VdB.set(1)
    else:
        ShowRA_VdB.set(0)
# 
def onCanvasBdSeven(event):
    global ShowRB_VdB
    if ShowRB_VdB.get() == 0:
        ShowRB_VdB.set(1)
    else:
        ShowRB_VdB.set(0)
#
def onCanvasBdEight(event):
    global ShowMathBP
    ShowMathBP.set(2)
#
def onCanvasBdNine(event):
    global ShowMathBP
    ShowMathBP.set(1)
#
def onCanvasBdZero(event):
    global ShowMathBP
    ShowMathBP.set(0)
#
def onCanvasBdSnap(event):
    BSTOREtraceBP()
#
def onCanvasShowBPcur(event):
    global ShowBPCur
    if ShowBPCur.get() == 0:
        ShowBPCur.set(1)
    else:
        ShowBPCur.set(0)
#
def onCanvasShowBdBcur(event):
    global ShowBdBCur
    if ShowBdBCur.get() == 1:
        ShowBdBCur.set(0)
    else:
        ShowBdBCur.set(1)
#
def onCanvasShowPdBcur(event):
    global ShowBdBCur
    if ShowBdBCur.get() == 2:
        ShowBdBCur.set(0)
    else:
        ShowBdBCur.set(2)
#
def onAWGAscroll(event):
    global AWGAShape
    onTextScroll(event)
    UpdateAWGA()
#
def onAWGBscroll(event):
    global AWGBShape
    onTextScroll(event)
    UpdateAWGB()
#
def onTextScroll(event):   # august 7
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    Pos = cursor_position
    OldVal = button.get() # get current entry string
    OldValfl = float(OldVal) # and its value
    Len = len(OldVal)
    Dot = OldVal.find (".")  # find decimal point position
    Decimals = Len - Dot - 1
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else :
        Step = 10**(Dot - Pos + 1)
    if event.delta > 0: # increment value
        NewVal = OldValfl + Step
    else: # decrement value
        NewVal = OldValfl - Step
    FormatStr = "{0:." + str(Decimals) + "f}"
    NewStr = FormatStr.format(NewVal)
    NewDot = NewStr.find (".") 
    NewPos = Pos + NewDot - Dot
    if Decimals == 0 :
        NewLen = len(NewStr)
        NewPos = Pos + NewLen - Len
    button.delete(0, END) # remove old entry
    button.insert(0, NewStr) # insert new entry
    button.icursor(NewPos) # resets the insertion cursor
#
def onAWGAkey(event):
    global AWGAShape
    onTextKey(event)
    UpdateAWGA()
#
def onAWGBkey(event):
    global AWGBShape
    onTextKey(event)
    UpdateAWGB()
#
def onTextKey(event):
    
    button = event.widget
    cursor_position = button.index(INSERT) # get current cursor position
    NewPos = cursor_position -1
    OldVal = button.get() # get current entry string
    OldDigit = OldVal[NewPos]
    if event.keycode == 38: # increment digit for up arrow key
        NewDigit = int(OldDigit) + 1
    elif event.keycode == 40: # decrement digit for down arrow
        NewDigit = int(OldDigit) - 1
    else:
        return
    if OldDigit == ".": # if cursor next to decimal point nop
        return
    if NewDigit > 9:
        NewDigit = 0
        button.delete(NewPos) # remove old digit
        button.insert(NewPos,NewDigit) # insert new digit
        NewPos = cursor_position-2
        if NewPos < 0:
            return
        CarryDigit = OldVal[NewPos]
        if CarryDigit == ".": # if carry is decimal point
            NewPos = cursor_position-3
            CarryDigit = OldVal[NewPos]
        NewDigit = int(CarryDigit) + 1
        if NewDigit > 9:
            NewDigit = 0
        button.delete(NewPos) # remove old digit
        button.insert(NewPos,NewDigit) # insert new digit
    elif NewDigit < 0:
        NewDigit = 9
        button.delete(NewPos) # remove old digit
        button.insert(NewPos,NewDigit) # insert new digit
        NewPos = cursor_position-2
        if NewPos < 0:
            return
        CarryDigit = OldVal[NewPos]
        if CarryDigit == ".": # if carry is decimal point
            NewPos = cursor_position-3
            CarryDigit = OldVal[NewPos]
        NewDigit = int(CarryDigit) - 1
        if NewDigit < 0:
            NewDigit = 9
        button.delete(NewPos) # remove old digit
        button.insert(NewPos,NewDigit) # insert new digit
    else:
        button.delete(NewPos) # remove old digit
        button.insert(NewPos,NewDigit) # insert new digit
#
def onSpinBoxScroll(event):
    if event.widget == ca:
        spbox = TMsb
    else:
        spbox = event.widget
    if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    else: # decrement digit
        spbox.invoke('buttondown')
#
# ================ Make awg sub window ==========================
def MakeAWGWindow():
    global AWGAMode, AWGAShape, awgwindow, AWGAPhaseDelay, AWGBPhaseDelay
    global AWGBMode, AWGBShape, AWGScreenStatus, AWGARepeatFlag, AWGBRepeatFlag
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGAPhaseEntry, AWGADutyCycleEntry
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBPhaseEntry, AWGBDutyCycleEntry
    global AWGALength, AWGBLength, RevDate, phasealab, phaseblab, AWGAModeLabel, AWGBModeLabel
    global duty1lab, duty2lab, phasealab, phaseblab, awgaph, awgadel, awgbph, awgbdel
    global AwgLayout
    
    if AWGScreenStatus.get() == 0:
        AWGScreenStatus.set(1)
        
        awgwindow = Toplevel()
        awgwindow.title("AWG 2.0 " + RevDate)
        awgwindow.resizable(FALSE,FALSE)
        awgwindow.geometry('+0+100')
        awgwindow.protocol("WM_DELETE_WINDOW", DestroyAWGScreen)
        #
        frame2 = LabelFrame(awgwindow, text="AWG W 1", style="A10R1.TLabelframe")
        frame3 = LabelFrame(awgwindow, text="AWG W 2", style="A10R2.TLabelframe")
        #
        if AwgLayout == "Horz":
            frame2.pack(side=LEFT, expand=1, fill=Y)
            frame3.pack(side=LEFT, expand=1, fill=X)
        else:
            frame2.pack(side=TOP, expand=1, fill=Y)
            frame3.pack(side=TOP, expand=1, fill=Y)
        # now AWG 1
        # AWG enable sub frame
        AWGAMode = IntVar(0)   # AWG 1 mode variable
        AWGAShape = IntVar(0)  # AWG 1 Wave shape variable
        AWGAMode.set(2)
        awg1eb = Frame( frame2 )
        awg1eb.pack(side=TOP)
        ModeAMenu = Menubutton(awg1eb, text="Mode", style="W5.TButton")
        ModeAMenu.menu = Menu(ModeAMenu, tearoff = 0 )
        ModeAMenu["menu"] = ModeAMenu.menu
        ModeAMenu.menu.add_command(label="-Mode-", command=donothing)
        ModeAMenu.menu.add_radiobutton(label="Enabled", variable=AWGAMode, value=0, command=UpdateAWGA)
        ModeAMenu.menu.add_radiobutton(label="Hi-Z", variable=AWGAMode, value=2, command=UpdateAWGA)
        ModeAMenu.pack(side=LEFT, anchor=W)
        ShapeAMenu = Menubutton(awg1eb, text="Shape", style="W5.TButton")
        ShapeAMenu.menu = Menu(ShapeAMenu, tearoff = 0 )
        ShapeAMenu["menu"] = ShapeAMenu.menu
        ShapeAMenu.menu.add_radiobutton(label="DC", variable=AWGAShape, value=0, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Sine", variable=AWGAShape, value=1, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Triangle", variable=AWGAShape, value=2, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Sawtooth", variable=AWGAShape, value=3, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Square", variable=AWGAShape, value=4, command=UpdateAWGA)
        ShapeAMenu.menu.add_separator()
        ShapeAMenu.menu.add_radiobutton(label="StairStep", variable=AWGAShape, value=5, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Impulse", variable=AWGAShape, value=9, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Trapezoid", variable=AWGAShape, value=11, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Ramp", variable=AWGAShape, value=17, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="SSQ Pulse", variable=AWGAShape, value=15, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="U-D Ramp", variable=AWGAShape, value=12, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Fourier Series", variable=AWGAShape, value=14, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Sin X/X", variable=AWGAShape, value=16, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="UU Noise", variable=AWGAShape, value=7, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="UG Noise", variable=AWGAShape, value=8, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Read CSV File", variable=AWGAShape, value=6, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Read WAV File", variable=AWGAShape, value=13, command=UpdateAWGA)
        ShapeAMenu.menu.add_radiobutton(label="Math", variable=AWGAShape, value=10, command=UpdateAWGA)
        ShapeAMenu.menu.add_command(label="AWG 1 Formula", command=AWGAEnterMath)
        ShapeAMenu.menu.add_command(label="Save CSV File", command=AWGAWriteFile)
        ShapeAMenu.pack(side=LEFT, anchor=W)
        #
        AWGAModeLabel = Label(frame2, text="AWG 1 Mode")
        AWGAModeLabel.pack(side=TOP)
        #
        awg1ampl = Frame( frame2 )
        awg1ampl.pack(side=TOP)
        AWGAAmplEntry = Entry(awg1ampl, width=5)
        AWGAAmplEntry.bind("<Return>", UpdateAWGAT)
        AWGAAmplEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAAmplEntry.bind('<Key>', onAWGAkey)
        AWGAAmplEntry.pack(side=LEFT, anchor=W)
        AWGAAmplEntry.delete(0,"end")
        AWGAAmplEntry.insert(0,0.0)
        amp1lab = Label(awg1ampl, text="Min Ch 1")
        amp1lab.pack(side=LEFT, anchor=W)
        #
        awg1off = Frame( frame2 )
        awg1off.pack(side=TOP)
        AWGAOffsetEntry = Entry(awg1off, width=5)
        AWGAOffsetEntry.bind("<Return>", UpdateAWGAT)
        AWGAOffsetEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAOffsetEntry.bind('<Key>', onAWGAkey)
        AWGAOffsetEntry.pack(side=LEFT, anchor=W)
        AWGAOffsetEntry.delete(0,"end")
        AWGAOffsetEntry.insert(0,0.0)
        off1lab = Label(awg1off, text="Max Ch 1")
        off1lab.pack(side=LEFT, anchor=W)
        # AWG Frequency sub frame
        awg1freq = Frame( frame2 )
        awg1freq.pack(side=TOP)
        AWGAFreqEntry = Entry(awg1freq, width=7)
        AWGAFreqEntry.bind("<Return>", UpdateAWGAT)
        AWGAFreqEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAFreqEntry.bind('<Key>', onAWGAkey)
        AWGAFreqEntry.pack(side=LEFT, anchor=W)
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,0.0)
        freq1lab = Label(awg1freq, text="Freq 1")
        freq1lab.pack(side=LEFT, anchor=W)
        # AWG Phase or delay select sub frame
        AWGAPhaseDelay = IntVar(0) # 
        awgadelay = Frame( frame2 )
        awgadelay.pack(side=TOP)
        awgaph = Radiobutton(awgadelay, text="Phase", style="WPhase.TRadiobutton", variable=AWGAPhaseDelay, value=0, command=BAWGAPhaseDelay)
        awgaph.pack(side=LEFT, anchor=W)
        awgadel = Radiobutton(awgadelay, text="Delay", style="GPhase.TRadiobutton", variable=AWGAPhaseDelay, value=1, command=BAWGAPhaseDelay)
        awgadel.pack(side=LEFT, anchor=W)
        # AWG Phase entry sub frame
        awg1phase = Frame( frame2 )
        awg1phase.pack(side=TOP)
        AWGAPhaseEntry = Entry(awg1phase, width=5)
        AWGAPhaseEntry.bind("<Return>", UpdateAWGAT)
        AWGAPhaseEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAPhaseEntry.bind('<Key>', onAWGAkey)
        AWGAPhaseEntry.pack(side=LEFT, anchor=W)
        AWGAPhaseEntry.delete(0,"end")
        AWGAPhaseEntry.insert(0,0)
        phasealab = Label(awg1phase, text="Deg")
        phasealab.pack(side=LEFT, anchor=W)
        # AWG duty cycle frame
        awg1dc = Frame( frame2 )
        awg1dc.pack(side=TOP)
        AWGADutyCycleEntry = Entry(awg1dc, width=5)
        AWGADutyCycleEntry.bind("<Return>", UpdateAWGAT)
        AWGADutyCycleEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGADutyCycleEntry.bind('<Key>', onAWGAkey)
        AWGADutyCycleEntry.pack(side=LEFT, anchor=W)
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0,50)
        duty1lab = Label(awg1dc, text="%")
        duty1lab.pack(side=LEFT, anchor=W)
        #
        AWGALength = Label(frame2, text="Length")
        AWGALength.pack(side=TOP)
        # now AWG 2 - AWG enable sub frame
        AWGBMode = IntVar(0)   # AWG 2 mode variable
        AWGBShape = IntVar(0)  # AWG 2 Wave shape variable
        AWGBMode.set(2)
        awg2eb = Frame( frame3 )
        awg2eb.pack(side=TOP)
        ModeBMenu = Menubutton(awg2eb, text="Mode", style="W5.TButton")
        ModeBMenu.menu = Menu(ModeBMenu, tearoff = 0 )
        ModeBMenu["menu"] = ModeBMenu.menu
        ModeBMenu.menu.add_command(label="-Mode-", command=donothing)
        ModeBMenu.menu.add_radiobutton(label="Enabled", variable=AWGBMode, value=0, command=UpdateAWGB)
        ModeBMenu.menu.add_radiobutton(label="Hi-Z", variable=AWGBMode, value=2, command=UpdateAWGB)
        ModeBMenu.pack(side=LEFT, anchor=W)
        ShapeBMenu = Menubutton(awg2eb, text="Shape", style="W5.TButton")
        ShapeBMenu.menu = Menu(ShapeBMenu, tearoff = 0 )
        ShapeBMenu["menu"] = ShapeBMenu.menu
        ShapeBMenu.menu.add_radiobutton(label="DC", variable=AWGBShape, value=0, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Sine", variable=AWGBShape, value=1, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Triangle", variable=AWGBShape, value=2, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Sawtooth", variable=AWGBShape, value=3, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Square", variable=AWGBShape, value=4, command=UpdateAWGB)
        ShapeBMenu.menu.add_separator()
        ShapeBMenu.menu.add_radiobutton(label="StairStep", variable=AWGBShape, value=5, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Impulse", variable=AWGBShape, value=9, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Trapezoid", variable=AWGBShape, value=11, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Ramp", variable=AWGBShape, value=17, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="SSQ Pulse", variable=AWGBShape, value=15, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="U-D Ramp", variable=AWGBShape, value=12, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Fourier Series", variable=AWGBShape, value=14, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Sin X/X", variable=AWGBShape, value=16, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="UU Noise", variable=AWGBShape, value=7, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="UG Noise", variable=AWGBShape, value=8, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Read CSV File", variable=AWGBShape, value=6, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Read WAV File", variable=AWGBShape, value=13, command=UpdateAWGB)
        ShapeBMenu.menu.add_radiobutton(label="Math", variable=AWGBShape, value=10, command=UpdateAWGB)
        ShapeBMenu.menu.add_command(label="AWG 2 Formula", command=AWGBEnterMath)
        ShapeBMenu.menu.add_command(label="Save CSV File", command=AWGBWriteFile)
        ShapeBMenu.pack(side=LEFT, anchor=W)
        #
        AWGBModeLabel = Label(frame3, text="AWG 2 Mode")
        AWGBModeLabel.pack(side=TOP)
        #
        awg2ampl = Frame( frame3 )
        awg2ampl.pack(side=TOP)
        AWGBAmplEntry = Entry(awg2ampl, width=5)
        AWGBAmplEntry.bind("<Return>", UpdateAWGBT)
        AWGBAmplEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBAmplEntry.bind('<Key>', onAWGBkey)
        AWGBAmplEntry.pack(side=LEFT, anchor=W)
        AWGBAmplEntry.delete(0,"end")
        AWGBAmplEntry.insert(0,0.0)
        amp2lab = Label(awg2ampl, text="Min Ch 2")
        amp2lab.pack(side=LEFT, anchor=W)
        #
        awg2off = Frame( frame3 )
        awg2off.pack(side=TOP)
        AWGBOffsetEntry = Entry(awg2off, width=5)
        AWGBOffsetEntry.bind("<Return>", UpdateAWGBT)
        AWGBOffsetEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBOffsetEntry.bind('<Key>', onAWGBkey)
        AWGBOffsetEntry.pack(side=LEFT, anchor=W)
        AWGBOffsetEntry.delete(0,"end")
        AWGBOffsetEntry.insert(0,0.0)
        off2lab = Label(awg2off, text="Max Ch 2")
        off2lab.pack(side=LEFT, anchor=W)
        # AWG Frequency sub frame
        awg2freq = Frame( frame3 )
        awg2freq.pack(side=TOP)
        AWGBFreqEntry = Entry(awg2freq, width=7)
        AWGBFreqEntry.bind("<Return>", UpdateAWGBT)
        AWGBFreqEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBFreqEntry.bind('<Key>', onAWGBkey)
        AWGBFreqEntry.pack(side=LEFT, anchor=W)
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,0.0)
        freq2lab = Label(awg2freq, text="Freq 2")
        freq2lab.pack(side=LEFT, anchor=W)
        # AWG Phase or delay select sub frame
        AWGBPhaseDelay = IntVar(0) # 
        awgbdelay = Frame( frame3 )
        awgbdelay.pack(side=TOP)
        awgbph = Radiobutton(awgbdelay, text="Phase", style="WPhase.TRadiobutton", variable=AWGBPhaseDelay, value=0, command=BAWGBPhaseDelay)
        awgbph.pack(side=LEFT, anchor=W)
        awgbdel = Radiobutton(awgbdelay, text="Delay", style="GPhase.TRadiobutton", variable=AWGBPhaseDelay, value=1, command=BAWGBPhaseDelay)
        awgbdel.pack(side=LEFT, anchor=W)
        # AWG Phase sub frame
        awg2phase = Frame( frame3 )
        awg2phase.pack(side=TOP)
        AWGBPhaseEntry = Entry(awg2phase, width=5)
        AWGBPhaseEntry.bind("<Return>", UpdateAWGBT)
        AWGBPhaseEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBPhaseEntry.bind('<Key>', onAWGBkey)
        AWGBPhaseEntry.pack(side=LEFT, anchor=W)
        AWGBPhaseEntry.delete(0,"end")
        AWGBPhaseEntry.insert(0,0)
        phaseblab = Label(awg2phase, text="Deg")
        phaseblab.pack(side=LEFT, anchor=W)
        # AWG duty cycle frame
        awg2dc = Frame( frame3 )
        awg2dc.pack(side=TOP)
        AWGBDutyCycleEntry = Entry(awg2dc, width=5)
        AWGBDutyCycleEntry.bind("<Return>", UpdateAWGBT)
        AWGBDutyCycleEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBDutyCycleEntry.bind('<Key>', onAWGBkey)
        AWGBDutyCycleEntry.pack(side=LEFT, anchor=W)
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0,50)
        duty2lab = Label(awg2dc, text="%")
        duty2lab.pack(side=LEFT, anchor=W)
        #
        AWGBLength = Label(frame3, text="Length")
        AWGBLength.pack(side=TOP)
        #
        dismissbutton = Button(frame3, text="Minimize", style="W8.TButton", command=DestroyAWGScreen)
        dismissbutton.pack(side=TOP)
    else:
        awgwindow.deiconify()
        
def DestroyAWGScreen():
    global awgwindow, AWGScreenStatus
    awgwindow.iconify()
    
# ===== Channel 2 Mux Mode sub Window =======
def MakeMuxModeWindow():
    global MuxScreenStatus, muxwindow, RevDate, DacScreenStatus, DigScreenStatus
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry, SyncButton
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxEnb, MuxSync, hipulseimg, lowpulseimg
    
    if MuxScreenStatus.get() == 0 and DacScreenStatus.get() == 0 and DigScreenStatus.get() == 0:
        MuxScreenStatus.set(1)
        
        muxwindow = Toplevel()
        muxwindow.title("CH-2 Mux 2.0 " + RevDate)
        muxwindow.resizable(FALSE,FALSE)
        muxwindow.protocol("WM_DELETE_WINDOW", DestroyMuxScreen)
        #
        frameM = LabelFrame(muxwindow, text="CH 2 Mux", style="A10B.TLabel")
        frameM.pack(side=LEFT, expand=1, fill=Y)
        # Voltage channel CH2-A
        frameA = Frame(frameM)
        frameA.pack(side=TOP)
        cba = Checkbutton(frameA, text='C2-A', variable=Show_CBA, command=UpdateTimeTrace)
        cba.pack(side=LEFT, anchor=W)
        CHB_Asb = Spinbox(frameA, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Asb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Asb.pack(side=LEFT)
        CHB_Asb.delete(0,"end")
        CHB_Asb.insert(0,0.5)
        #
        CHB_Alab = Label(frameA, text="C2-A V/Div",style="Rtrace2.TButton")
        CHB_Alab.pack(side=LEFT)
        CHB_APosEntry = Entry(frameA, width=5)
        CHB_APosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_APosEntry.bind('<Key>', onTextKey)
        CHB_APosEntry.pack(side=LEFT)
        CHB_APosEntry.delete(0,"end")
        CHB_APosEntry.insert(0,0.0)
        CHB_Aofflab = Label(frameA, text="C2-A Pos", style="Rtrace2.TButton")
        CHB_Aofflab.pack(side=LEFT)
        # Voltage channel CH2-B
        frameB = Frame(frameM)
        frameB.pack(side=TOP)
        cbb = Checkbutton(frameB, text='C2-B', variable=Show_CBB, command=UpdateTimeTrace)
        cbb.pack(side=LEFT, anchor=W)
        CHB_Bsb = Spinbox(frameB, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Bsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Bsb.pack(side=LEFT)
        CHB_Bsb.delete(0,"end")
        CHB_Bsb.insert(0,0.5)
        CHB_Blab = Label(frameB, text="C2-B V/Div", style="Rtrace6.TButton")
        CHB_Blab.pack(side=LEFT)
        CHB_BPosEntry = Entry(frameB, width=5)
        CHB_BPosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_BPosEntry.bind('<Key>', onTextKey)
        CHB_BPosEntry.pack(side=LEFT)
        CHB_BPosEntry.delete(0,"end")
        CHB_BPosEntry.insert(0,0.0)
        CHB_Bofflab = Label(frameB, text="C2-B Pos", style="Rtrace6.TButton")
        CHB_Bofflab.pack(side=LEFT)
        # Voltage channel CH2-C
        frameC = Frame(frameM)
        frameC.pack(side=TOP)
        cbc = Checkbutton(frameC, text='C2-C', variable=Show_CBC, command=UpdateTimeTrace)
        cbc.pack(side=LEFT, anchor=W)
        CHB_Csb = Spinbox(frameC, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Csb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Csb.pack(side=LEFT)
        CHB_Csb.delete(0,"end")
        CHB_Csb.insert(0,0.5)
        # 
        CHB_Clab = Label(frameC, text="C2-C V/Div", style="Rtrace7.TButton")
        CHB_Clab.pack(side=LEFT)
        CHB_CPosEntry = Entry(frameC, width=5)
        CHB_CPosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_CPosEntry.bind('<Key>', onTextKey)
        CHB_CPosEntry.pack(side=LEFT)
        CHB_CPosEntry.delete(0,"end")
        CHB_CPosEntry.insert(0,0.0)
        CHB_Cofflab = Label(frameC, text="C2 V Pos", style="Rtrace7.TButton")
        CHB_Cofflab.pack(side=LEFT)
        # Voltage channel CH2-D
        frameD = Frame(frameM)
        frameD.pack(side=TOP)
        cbd = Checkbutton(frameD, text='C2-D', variable=Show_CBD, command=UpdateTimeTrace)
        cbd.pack(side=LEFT, anchor=W)
        CHB_Dsb = Spinbox(frameD, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Dsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Dsb.pack(side=LEFT)
        CHB_Dsb.delete(0,"end")
        CHB_Dsb.insert(0,0.5)
        CHB_Dlab = Label(frameD, text="C2-D V/Div", style="Rtrace4.TButton")
        CHB_Dlab.pack(side=LEFT)
        CHB_DPosEntry = Entry(frameD, width=5)
        CHB_DPosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_DPosEntry.bind('<Key>', onTextKey)
        CHB_DPosEntry.pack(side=LEFT)
        CHB_DPosEntry.delete(0,"end")
        CHB_DPosEntry.insert(0,0.0)
        CHB_Dofflab = Label(frameD, text="C2-D Pos", style="Rtrace4.TButton")
        CHB_Dofflab.pack(side=LEFT)
        frameE = Frame(frameM)
        frameE.pack(side=TOP)
        MuxEnb = IntVar(0)
        MuxSync = IntVar(0)
        muxenab = Checkbutton(frameE, text="Mux-Enb", variable=MuxEnb)
        muxenab.pack(side=LEFT)
        SyncButton = Checkbutton(frameE, compound=TOP, image=hipulseimg, variable=MuxSync, command=SyncImage)
        SyncButton.pack(side=LEFT)
        dismissbutton = Button(frameE, text="Dismiss", style="W8.TButton", command=DestroyMuxScreen)
        dismissbutton.pack(side=LEFT)
#
def SyncImage():
    global MuxSync, hipulseimg, lowpulseimg, SyncButton

    if MuxSync.get() == 0:
        SyncButton.config(image=hipulseimg)
    else:
        SyncButton.config(image=lowpulseimg)
        
def DestroyMuxScreen():
    global muxwindow, MuxScreenStatus
    
    MuxScreenStatus.set(0)
    muxwindow.destroy()
#
def BodeCaresize(event):
    global Bodeca, GRWBP, XOLBP, GRHBP, Y0TBP, CANVASwidthBP, CANVASheightBP
    
    CANVASwidthBP = event.width
    CANVASheightBP = event.height
    GRWBP = CANVASwidthBP - (2 * X0LBP) # new grid width
    GRHBP = CANVASheightBP - 80     # new grid height
    UpdateBodeAll()
#
def BStepSync():
    global FStepSync, Dig0, logic, ctx
        
    if FStepSync.get() == 0:
        Dig0.attrs["direction"].value = 'in' # set PIO-0 to Z
    elif FStepSync.get() == 1:
        Dig0.attrs["direction"].value = 'out'
        Dig0.attrs["raw"].value = str(0) # set PIO-0 to 0
    elif FStepSync.get() == 2:
        Dig0.attrs["direction"].value = 'out'
        Dig0.attrs["raw"].value = str(1) # set PIO-0 to 1
#
def BSweepSync():
    global FSweepSync, Dig1, logic, ctx

    if FSweepSync.get() == 0:
        Dig1.attrs["direction"].value = 'in' # set PIO-1 to Z
    elif FSweepSync.get() == 1:
        Dig1.attrs["direction"].value = 'out'
        Dig1.attrs["raw"].value = str(0) # set PIO-1 to 0
    elif FSweepSync.get() == 2:
        Dig1.attrs["direction"].value = 'out'
        Dig1.attrs["raw"].value = str(1)  # set PIO-1 to 1
#
def BDSweepFromFile():
    global BDSweepFile, FileSweepFreq, FileSweepAmpl

    if BDSweepFile.get() > 0:
       # Read values from CVS file
        filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent = bodewindow)
        try:
            CSVFile = open(filename)
            csv_f = csv.reader(CSVFile)
            FileSweepFreq = []
            FileSweepAmpl = []
            for row in csv_f:
                try:
                    FileSweepFreq.append(float(row[0]))
                    FileSweepAmpl.append(float(row[1]))
                except:
                    print 'skipping non-numeric row'
            FileSweepFreq = numpy.array(FileSweepFreq)
            FileSweepAmpl = numpy.array(FileSweepAmpl)
            MaxAmpl = numpy.amax(FileSweepAmpl)
            NormAmpl = MaxAmpl
            s = askstring("Normalize Max Amplitude", "Max Amplitude = " + str(MaxAmpl) + "\n\n Enter New Max value:\n in dB", parent = bodewindow)
            if (s == None):         # If Cancel pressed, then None
                return()
            try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
                v = float(s)
            except:
                s = "error"

            if s != "error":
                NormAmpl = MaxAmpl - v
            else:
                NormAmpl = MaxAmpl
            FileSweepAmpl = FileSweepAmpl - NormAmpl # normalize max amplitude to requested dBV
            CSVFile.close()
            StopBodeEntry.delete(0,"end")
            StopBodeEntry.insert(0,FileSweepFreq[len(FileSweepFreq)-1])
            StartBodeEntry.delete(0,"end")
            StartBodeEntry.insert(0,FileSweepFreq[0])
            SweepStepBodeEntry.delete(0,"end")
            SweepStepBodeEntry.insert(0,len(FileSweepFreq))
        except:
            showwarning("WARNING","No such file found or wrong format!")
# 
# ========== Make Bode Plot Window =============
def MakeBodeWindow():
    global logo, SmoothCurvesBP, CutDC, SingleShotBP, bodewindow
    global CANVASwidthBP, CANVASheightBP, FFTwindow, CutDC, AWGAMode, AWGAShape, AWGBMode 
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMarkerBP, BodeDisp
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP, ShowMathBP, ShowRMathBP
    global BPSweepMode, BPSweepCont, Bodeca, BodeScreenStatus, RevDate, SweepStepBodeEntry
    global HScaleBP, StopBodeEntry, StartBodeEntry, ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global GRWBP, GRHBP, X0LBP, FStepSync, FSweepSync, BDSweepFile, MinigenScreenStatus
    global CH1GainSA, CH2GainSA
    
    if BodeScreenStatus.get() == 0:
        BodeScreenStatus.set(1)
        BodeDisp.set(1)
        CANVASwidthBP = GRWBP + 2 * X0LBP    # The Bode canvas width
        CANVASheightBP = GRHBP + 80         # The ode canvas height
        CutDC.set(1) # set to remove DC
        bodewindow = Toplevel()
        bodewindow.title("Bode Plotter 2.0 " + RevDate)
        bodewindow.protocol("WM_DELETE_WINDOW", DestroyBodeScreen)
        frame2bp = Frame(bodewindow, borderwidth=5, relief=RIDGE)
        frame2bp.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2b = Frame(bodewindow, borderwidth=5, relief=RIDGE)
        frame2b.pack(side=TOP, expand=YES, fill=BOTH)

        Bodeca = Canvas(frame2b, width=CANVASwidthBP, height=CANVASheightBP, background=COLORcanvas, cursor='cross')
        Bodeca.bind('<Configure>', BodeCaresize)
        Bodeca.bind('<1>', onCanvasBodeLeftClick)
        Bodeca.bind('<3>', onCanvasBodeRightClick)
        Bodeca.bind("<Up>", onCanvasUpArrow)
        Bodeca.bind("<Down>", onCanvasDownArrow)
        Bodeca.bind("<Left>", onCanvasLeftArrow)
        Bodeca.bind("<Right>", onCanvasRightArrow)
        Bodeca.bind("1", onCanvasBdOne)
        Bodeca.bind("2", onCanvasBdTwo)
        Bodeca.bind("3", onCanvasBdThree)
        Bodeca.bind("4", onCanvasBdFour)
        Bodeca.bind("5", onCanvasBdFive)
        Bodeca.bind("6", onCanvasBdSix)
        Bodeca.bind("7", onCanvasBdSeven)
        Bodeca.bind("8", onCanvasBdEight)
        Bodeca.bind("9", onCanvasBdNine)
        Bodeca.bind("0", onCanvasBdZero)
        Bodeca.bind("f", onCanvasShowBPcur)
        Bodeca.bind("d", onCanvasShowBdBcur)
        Bodeca.bind("h", onCanvasShowPdBcur)
        Bodeca.bind("s", onCanvasBdSnap)
        Bodeca.pack(side=TOP, expand=YES, fill=BOTH)
        # right side drop down menu buttons
        dropmenu = Frame( frame2bp )
        dropmenu.pack(side=TOP)
        # File menu
        Filemenu = Menubutton(dropmenu, text="File", style="W5.TButton")
        Filemenu.menu = Menu(Filemenu, tearoff = 0 )
        Filemenu["menu"] = Filemenu.menu
        Filemenu.menu.add_command(label="Save Config", command=BSaveConfigBP)
        Filemenu.menu.add_command(label="Load Config", command=BLoadConfigBP)
        Filemenu.menu.add_command(label="Save Screen", command=BSaveScreenBP)
        Filemenu.menu.add_command(label="Save Data", command=BCSVfile)
        Filemenu.pack(side=LEFT, anchor=W)
        #
        Optionmenu = Menubutton(dropmenu, text="Options", style="W8.TButton")
        Optionmenu.menu = Menu(Optionmenu, tearoff = 0 )
        Optionmenu["menu"]  = Optionmenu.menu
        Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
        Optionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurvesBP)
        Optionmenu.menu.add_checkbutton(label='Cut-DC', variable=CutDC)
        Optionmenu.menu.add_command(label="Store trace [s]", command=BSTOREtraceBP)
        Optionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
        Optionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
        Optionmenu.menu.add_command(label="-Step Sync Pulse-", command=donothing)
        Optionmenu.menu.add_radiobutton(label='None', variable=FStepSync, value=0, command=BStepSync)
        Optionmenu.menu.add_radiobutton(label='Rising', variable=FStepSync, value=1, command=BStepSync)
        Optionmenu.menu.add_radiobutton(label='Falling', variable=FStepSync, value=2, command=BStepSync)
        Optionmenu.menu.add_command(label="-Sweep Sync Pulse-", command=donothing)
        Optionmenu.menu.add_radiobutton(label='None', variable=FSweepSync, value=0, command=BSweepSync)
        Optionmenu.menu.add_radiobutton(label='Rising', variable=FSweepSync, value=1, command=BSweepSync)
        Optionmenu.menu.add_radiobutton(label='Falling', variable=FSweepSync, value=2, command=BSweepSync)
        Optionmenu.pack(side=LEFT, anchor=W)
        #
        RUNframe = Frame( frame2bp )
        RUNframe.pack(side=TOP)
        sbode = Button(RUNframe, text="Stop", style="Stop.TButton", command=BStopBP)
        sbode.pack(side=LEFT)
        rbode = Button(RUNframe, text="Run", style="Run.TButton", command=BStartBP)
        rbode.pack(side=LEFT)
        #
        dropmenu2 = Frame( frame2bp )
        dropmenu2.pack(side=TOP)
        FFTwindmenu = Menubutton(dropmenu2, text="FFTwindow", style="W11.TButton")
        FFTwindmenu.menu = Menu(FFTwindmenu, tearoff = 0 )
        FFTwindmenu["menu"]  = FFTwindmenu.menu
        FFTwindmenu.menu.add_radiobutton(label='Rectangular window (B=1)', variable=FFTwindow, value=0)
        FFTwindmenu.menu.add_radiobutton(label='Cosine window (B=1.24)', variable=FFTwindow, value=1)
        FFTwindmenu.menu.add_radiobutton(label='Triangular window (B=1.33)', variable=FFTwindow, value=2)
        FFTwindmenu.menu.add_radiobutton(label='Hann window (B=1.5)', variable=FFTwindow, value=3)
        FFTwindmenu.menu.add_radiobutton(label='Blackman window (B=1.73)', variable=FFTwindow, value=4)
        FFTwindmenu.menu.add_radiobutton(label='Nuttall window (B=2.02)', variable=FFTwindow, value=5)
        FFTwindmenu.menu.add_radiobutton(label='Flat top window (B=3.77)', variable=FFTwindow, value=6)
        FFTwindmenu.menu.add_radiobutton(label='User Defined window', variable=FFTwindow, value=7)
        FFTwindmenu.menu.add_command(label="Enter User function", command=BUserFFTwindow)
        FFTwindmenu.menu.add_radiobutton(label='FFT Window from file', variable=FFTwindow, value=8, command=BFileFFTwindow)
        FFTwindmenu.pack(side=LEFT)
        #
        Showmenu = Menubutton(dropmenu2, text="Curves", style="W7.TButton")
        Showmenu.menu = Menu(Showmenu, tearoff = 0 )
        Showmenu["menu"] = Showmenu.menu
        Showmenu.menu.add_command(label="-Show-", command=donothing)
        Showmenu.menu.add_command(label="All", command=BShowCurvesAllBP)
        Showmenu.menu.add_command(label="None", command=BShowCurvesNoneBP)
        Showmenu.menu.add_checkbutton(label='C1-dBV   [1]', variable=ShowCA_VdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='C2-dBV   [2]', variable=ShowCB_VdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Phase 1 - 2 [3]', variable=ShowCA_P, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Phase 2 - 1 [4]', variable=ShowCB_P, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Marker [5]', variable=ShowMarkerBP, command=UpdateBodeAll)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='Cursor Off', variable=ShowBdBCur, value=0)
        Showmenu.menu.add_radiobutton(label='dB Cursor   [d]', variable=ShowBdBCur, value=1)
        Showmenu.menu.add_radiobutton(label='Phase Cursor [h]', variable=ShowBdBCur, value=2)
        Showmenu.menu.add_checkbutton(label='Freq Cursor [f]', variable=ShowBPCur)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='None   [0]', variable=ShowMathBP, value=0, command=UpdateBodeAll)
        Showmenu.menu.add_radiobutton(label='C1-dB - C2-dB [9]', variable=ShowMathBP, value=1, command=UpdateBodeAll)
        Showmenu.menu.add_radiobutton(label='C2-dB - C1-dB [8]', variable=ShowMathBP, value=2, command=UpdateBodeAll)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_checkbutton(label='R1-dBV [6]', variable=ShowCA_RdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='R2-dBV [7]', variable=ShowCB_RdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='RPhase 1 - 2', variable=ShowCA_RP, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='RPhase 2 - 1', variable=ShowCB_RP, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Math', variable=ShowRMathBP, command=UpdateBodeAll)
        Showmenu.pack(side=LEFT)
        # Horz Scale        
        HScaleBP = IntVar(0)
        HScaleBP.set(1)
        HzScale = Frame( frame2bp )
        HzScale.pack(side=TOP)
        rb1 = Radiobutton(HzScale, text="Lin F", variable=HScaleBP, value=0, command=UpdateBodeTrace )
        rb1.pack(side=LEFT)
        rb2 = Radiobutton(HzScale, text="Log F", variable=HScaleBP, value=1, command=UpdateBodeTrace )
        rb2.pack(side=LEFT)
        # V scale / gain
        AnaRange1bp = Frame( frame2bp )
        AnaRange1bp.pack(side=TOP)
        ar1bplab = Label(AnaRange1bp, text="CH1 Gain")
        ar1bplab.pack(side=LEFT)
        ar1bp = Radiobutton(AnaRange1bp, text="High", variable=CH1GainSA, value=0)
        ar1bp.pack(side=LEFT)
        ar2bp = Radiobutton(AnaRange1bp, text="Low", variable=CH1GainSA, value=1)
        ar2bp.pack(side=LEFT)
        AnaRange2bp = Frame( frame2bp )
        AnaRange2bp.pack(side=TOP)
        ar2bplab = Label(AnaRange2bp, text="CH2 Gain")
        ar2bplab.pack(side=LEFT)
        ar3bp = Radiobutton(AnaRange2bp, text="High", variable=CH2GainSA, value=0)
        ar3bp.pack(side=LEFT)
        ar4bp = Radiobutton(AnaRange2bp, text="Low", variable=CH2GainSA, value=1)
        ar4bp.pack(side=LEFT)
        
        DBrange = Frame( frame2bp )
        DBrange.pack(side=TOP)
        bd3 = Button(DBrange, text="+dB/div", style="W8.TButton", command=BDBdiv2BP)
        bd3.pack(side=LEFT)
        bd4 = Button(DBrange, text="-dB/div", style="W8.TButton", command=BDBdiv1BP)
        bd4.pack(side=LEFT)

        LVBrange = Frame( frame2bp )
        LVBrange.pack(side=TOP)
        bd5 = Button(LVBrange, text="LVL+10", style="W8.TButton", command=Blevel4BP)
        bd5.pack(side=LEFT)
        bd6 = Button(LVBrange, text="LVL-10", style="W8.TButton", command=Blevel3BP)
        bd6.pack(side=LEFT)

        LVSrange = Frame( frame2bp )
        LVSrange.pack(side=TOP)
        bd7 = Button(LVSrange, text="LVL+1", style="W8.TButton", command=Blevel2BP)
        bd7.pack(side=LEFT)
        bd8 = Button(LVSrange, text="LVL-1", style="W8.TButton", command=Blevel1BP)
        bd8.pack(side=LEFT)
        # sweep generator mode menu buttons
        FSweepmenu = Label(frame2bp, text="-Sweep Gen-", style="A10B.TLabel")
        FSweepmenu.pack(side=TOP)
        
        Frange1 = Frame( frame2bp )
        Frange1.pack(side=TOP)
        startfreqlab = Label(Frange1, text="Startfreq")
        startfreqlab.pack(side=LEFT)
        StartBodeEntry = Entry(Frange1, width=8)
        StartBodeEntry.bind('<MouseWheel>', onTextScroll)
        StartBodeEntry.bind('<Key>', onTextKey)
        StartBodeEntry.pack(side=LEFT)
        StartBodeEntry.delete(0,"end")
        StartBodeEntry.insert(0,10)

        Frange2 = Frame( frame2bp )
        Frange2.pack(side=TOP)
        stopfreqlab = Label(Frange2, text="Stopfreq")
        stopfreqlab.pack(side=LEFT)
        StopBodeEntry = Entry(Frange2, width=8)
        StopBodeEntry.bind('<MouseWheel>', onTextScroll)
        StopBodeEntry.bind('<Key>', onTextKey)
        StopBodeEntry.pack(side=LEFT)
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,10000)
        
        sgrb1 = Radiobutton(frame2bp, text='None', variable=FSweepMode, value=0)
        sgrb1.pack(side=TOP)
        Frange4 = Frame( frame2bp )
        Frange4.pack(side=TOP)
        sgrb2 = Radiobutton(Frange4, text='CH-1', variable=FSweepMode, value=1)
        sgrb2.pack(side=LEFT)
        sgrb3 = Radiobutton(Frange4, text='CH-2', variable=FSweepMode, value=2)
        sgrb3.pack(side=LEFT)
        if MinigenScreenStatus.get() > 0:
            sgrb1 = Radiobutton(frame2bp, text='MinGen', variable=FSweepMode, value=3)
            sgrb1.pack(side=TOP)
        ffcb = Checkbutton(frame2bp, text='Sweep From File', variable=BDSweepFile, command=BDSweepFromFile)
        ffcb.pack(side=TOP)
        Frange3 = Frame( frame2bp )
        Frange3.pack(side=TOP)
        sweepsteplab = Label(Frange3, text="Sweep Steps")
        sweepsteplab.pack(side=LEFT)
        SweepStepBodeEntry = Entry(Frange3, width=5)
        SweepStepBodeEntry.bind('<MouseWheel>', onTextScroll)
        SweepStepBodeEntry.bind('<Key>', onTextKey)
        SweepStepBodeEntry.pack(side=LEFT)
        SweepStepBodeEntry.delete(0,"end")
        SweepStepBodeEntry.insert(0,100)
        
        sgrb5 = Radiobutton(frame2bp, text='Single', variable=FSweepCont, value=0)
        sgrb5.pack(side=TOP)
        sgrb6 = Radiobutton(frame2bp, text='Continuous', variable=FSweepCont, value=1)
        sgrb6.pack(side=TOP)
        
        bodismiss1button = Button(frame2bp, text="Dismiss", style="W8.TButton", command=DestroyBodeScreen)
        bodismiss1button.pack(side=TOP)
        
        ADI2 = Label(frame2bp, image=logo, anchor= "sw", height=49, width=116, compound="top")
        ADI2.pack(side=TOP)
        BodeCheckBox()
        if ShowBallonHelp > 0:
            sbode_tip = CreateToolTip(sbode, 'Stop acquiring data')
            rbode_tip = CreateToolTip(rbode, 'Start acquiring data')
            bd3_tip = CreateToolTip(bd3, 'Increase number of dB/Div')
            bd4_tip = CreateToolTip(bd4, 'Decrease number of dB/Div')
            bd5_tip = CreateToolTip(bd5, 'Increase Ref Level by 10 dB')
            bd6_tip = CreateToolTip(bd6, 'Decrease Ref Level by 10 dB')
            bd7_tip = CreateToolTip(bd7, 'Increase Ref Level by 1 dB')
            bd8_tip = CreateToolTip(bd8, 'Decrease Ref Level by 1 dB')
            bodismiss1button_tip = CreateToolTip(bodismiss1button, 'Dismiss Bode Plot window')

def DestroyBodeScreen():
    global bodewindow, BodeScreenStatus, ca, FSweepMode
    
    BodeScreenStatus.set(0)
    FSweepMode.set(0)
    BodeDisp.set(0)
    BodeCheckBox()
    bodewindow.destroy()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
def FreqCaresize(event):
    global Freqca, GRWF, XOLF, GRHF, Y0TF, CANVASwidthF, CANVASheightF
    
    CANVASwidthF = event.width
    CANVASheightF = event.height
    GRWF = CANVASwidthF - (2 * X0LF) # new grid width
    GRHF = CANVASheightF - 80     # new grid height
    UpdateFreqAll()
#
# ================ Make spectrum sub window ==========================
def MakeSpectrumWindow():
    global logo, SmoothCurvesSA, CutDC, SingleShot, FFTwindow, freqwindow, SmoothCurvesSA
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMarker, FreqDisp
    global ShowRA_VdB, ShowRA_P, ShowRB_VdB, ShowRB_P, ShowMathSA, ShowBallonHelp
    global ShowRMath, FSweepMode, FSweepCont, Freqca, SpectrumScreenStatus, RevDate
    global HScale, StopFreqEntry, StartFreqEntry, ShowFCur, ShowdBCur, FCursor, dBCursor
    global CANVASwidthF, GRWF, X0LF, CANVASheightF, GRHF
    global CH1GainSA, CH2GainSA
    
    if SpectrumScreenStatus.get() == 0:
        SpectrumScreenStatus.set(1)
        FreqDisp.set(1)
        CANVASwidthF = GRWF + 2 * X0LF     # The spectrum canvas width
        CANVASheightF = GRHF + 80         # The spectrum canvas height
        freqwindow = Toplevel()
        freqwindow.title("Spectrum Analyzer 2.0 " + RevDate)
        freqwindow.protocol("WM_DELETE_WINDOW", DestroySpectrumScreen)
        frame2fr = Frame(freqwindow, borderwidth=5, relief=RIDGE)
        frame2fr.pack(side=RIGHT, expand=NO, fill=BOTH)
        frame2f = Frame(freqwindow, borderwidth=5, relief=RIDGE)
        frame2f.pack(side=TOP, expand=YES, fill=BOTH)

        Freqca = Canvas(frame2f, width=CANVASwidthF, height=CANVASheightF, background=COLORcanvas, cursor='cross')
        Freqca.bind('<Configure>', FreqCaresize)
        Freqca.bind('<1>', onCanvasFreqLeftClick)
        Freqca.bind('<3>', onCanvasFreqRightClick)
        Freqca.bind("<Up>", onCanvasUpArrow)
        Freqca.bind("<Down>", onCanvasDownArrow)
        Freqca.bind("<Left>", onCanvasLeftArrow)
        Freqca.bind("<Right>", onCanvasRightArrow)
        Freqca.bind("1", onCanvasSAOne)
        Freqca.bind("2", onCanvasSATwo)
        Freqca.bind("3", onCanvasSAThree)
        Freqca.bind("4", onCanvasSAFour)
        Freqca.bind("5", onCanvasSAFive)
        Freqca.bind("6", onCanvasSASix)
        Freqca.bind("7", onCanvasSASeven)
        Freqca.bind("8", onCanvasSAEight)
        Freqca.bind("9", onCanvasSANine)
        Freqca.bind("0", onCanvasSAZero)
        Freqca.bind("a", onCanvasSAAverage)
        Freqca.bind("n", onCanvasSANormal)
        Freqca.bind("p", onCanvasSAPeak)
        Freqca.bind("r", onCanvasSAReset)
        Freqca.bind("f", onCanvasShowFcur)
        Freqca.bind("d", onCanvasShowdBcur)
        Freqca.bind("h", onCanvasShowPcur)
        Freqca.bind("s", onCanvasSASnap)
        Freqca.pack(side=TOP, expand=YES, fill=BOTH)
        # right side drop down menu buttons
        dropmenu = Frame( frame2fr )
        dropmenu.pack(side=TOP)
        # File menu
        Filemenu = Menubutton(dropmenu, text="File", style="W5.TButton")
        Filemenu.menu = Menu(Filemenu, tearoff = 0 )
        Filemenu["menu"] = Filemenu.menu
        Filemenu.menu.add_command(label="Save Config", command=BSaveConfigSA)
        Filemenu.menu.add_command(label="Load Config", command=BLoadConfigSA)
        Filemenu.menu.add_command(label="Save Screen", command=BSaveScreenSA)
        Filemenu.menu.add_command(label="Save Data", command=STOREcsvfile)
        Filemenu.pack(side=LEFT, anchor=W)
        #
        Optionmenu = Menubutton(dropmenu, text="Options", style="W8.TButton")
        Optionmenu.menu = Menu(Optionmenu, tearoff = 0 )
        Optionmenu["menu"]  = Optionmenu.menu
        Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
        Optionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurvesSA)
        Optionmenu.menu.add_checkbutton(label='Cut-DC', variable=CutDC)
        Optionmenu.menu.add_command(label="Store trace [s]", command=BSTOREtraceSA)
        Optionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
        Optionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
        Optionmenu.pack(side=LEFT, anchor=W)
        #
        RUNframe = Frame( frame2fr )
        RUNframe.pack(side=TOP)
        sb = Button(RUNframe, text="Stop", style="Stop.TButton", command=BStopSA)
        sb.pack(side=LEFT)
        rb = Button(RUNframe, text="Run", style="Run.TButton", command=BStartSA)
        rb.pack(side=LEFT)
        #
        SingleShot = IntVar(0) # variable for Single Shot sweeps
        Modeframe = Frame( frame2fr )
        Modeframe.pack(side=TOP)
        Modemenu = Menubutton(Modeframe, text="Mode", style="W5.TButton")
        Modemenu.menu = Menu(Modemenu, tearoff = 0 )
        Modemenu["menu"]  = Modemenu.menu
        Modemenu.menu.add_command(label="Normal mode [n]", command=BNormalmode)
        Modemenu.menu.add_command(label="Peak hold   [p]", command=BPeakholdmode)
        Modemenu.menu.add_command(label="Average   [a]", command=BAveragemode)
        Modemenu.menu.add_command(label="Reset Average [r]", command=BResetFreqAvg)
        Modemenu.menu.add_checkbutton(label='SingleShot', variable=SingleShot)
        Modemenu.pack(side=LEFT)
        #
        FFTwindmenu = Menubutton(Modeframe, text="FFTwindow", style="W11.TButton")
        FFTwindmenu.menu = Menu(FFTwindmenu, tearoff = 0 )
        FFTwindmenu["menu"]  = FFTwindmenu.menu
        FFTwindmenu.menu.add_radiobutton(label='Rectangular window (B=1)', variable=FFTwindow, value=0)
        FFTwindmenu.menu.add_radiobutton(label='Cosine window (B=1.24)', variable=FFTwindow, value=1)
        FFTwindmenu.menu.add_radiobutton(label='Triangular window (B=1.33)', variable=FFTwindow, value=2)
        FFTwindmenu.menu.add_radiobutton(label='Hann window (B=1.5)', variable=FFTwindow, value=3)
        FFTwindmenu.menu.add_radiobutton(label='Blackman window (B=1.73)', variable=FFTwindow, value=4)
        FFTwindmenu.menu.add_radiobutton(label='Nuttall window (B=2.02)', variable=FFTwindow, value=5)
        FFTwindmenu.menu.add_radiobutton(label='Flat top window (B=3.77)', variable=FFTwindow, value=6)
        FFTwindmenu.menu.add_radiobutton(label='User Defined window', variable=FFTwindow, value=7)
        FFTwindmenu.menu.add_command(label="Enter User function", command=BUserFFTwindow)
        FFTwindmenu.menu.add_radiobutton(label='FFT Window from file', variable=FFTwindow, value=8, command=BFileFFTwindow)
        FFTwindmenu.pack(side=LEFT)
        #
        SamplesMenu = Frame( frame2fr )
        SamplesMenu.pack(side=TOP)
        bless = Button(SamplesMenu, text="-Samples", style="W8.TButton", command=Bsamples1)
        bless.pack(side=LEFT)
        bmore = Button(SamplesMenu, text="+Samples", style="W8.TButton", command=Bsamples2)
        bmore.pack(side=LEFT)
        # Show channels menu
        ShowC1_VdB = IntVar(0)   # curves to display variables
        ShowC1_P = IntVar(0)
        ShowC2_VdB = IntVar(0)
        ShowC2_P = IntVar(0)
        ShowMarker = IntVar(0)
        ShowRA_VdB = IntVar(0)
        ShowRA_P = IntVar(0)
        ShowRB_VdB = IntVar(0)
        ShowRB_P = IntVar(0)
        ShowMathSA = IntVar(0)
        ShowRMath = IntVar(0)
        #
        Showmenu = Menubutton(frame2fr, text="Curves", style="W7.TButton")
        Showmenu.menu = Menu(Showmenu, tearoff = 0 )
        Showmenu["menu"] = Showmenu.menu
        Showmenu.menu.add_command(label="-Show-", command=donothing)
        Showmenu.menu.add_command(label="All", command=BShowCurvesAllSA)
        Showmenu.menu.add_command(label="None", command=BShowCurvesNoneSA)
        Showmenu.menu.add_checkbutton(label='C1-dBV   [1]', variable=ShowC1_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='C2-dBV   [2]', variable=ShowC2_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='Phase 1 - 2 [3]', variable=ShowC1_P, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='Phase 2 - 1 [4]', variable=ShowC2_P, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='Markers  Off', variable=ShowMarker, value=0, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='Markers  [5]', variable=ShowMarker, value=1, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='Delta Markers', variable=ShowMarker, value=2, command=UpdateFreqAll)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='Cursor Off', variable=ShowdBCur, value=0)
        Showmenu.menu.add_radiobutton(label='dB Cursor [d]', variable=ShowdBCur, value=1)
        Showmenu.menu.add_radiobutton(label='Phase Cursor [h]', variable=ShowdBCur, value=2)
        Showmenu.menu.add_checkbutton(label='Freq Cursor [f]', variable=ShowFCur)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='None   [0]', variable=ShowMathSA, value=0, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='C1-dB - C2-dB [9]', variable=ShowMathSA, value=1, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='C2-dB - C1-dB [8]', variable=ShowMathSA, value=2, command=UpdateFreqAll)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_checkbutton(label='R1-dBV [6]', variable=ShowRA_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='R2-dBV [7]', variable=ShowRB_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='RPhase 1 - 2', variable=ShowRA_P, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='RPhase 2 - 1', variable=ShowRB_P, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='Math', variable=ShowRMath, command=UpdateFreqAll)
        Showmenu.pack(side=TOP)
        # HScale
        Frange1 = Frame( frame2fr )
        Frange1.pack(side=TOP)
        startfreqlab = Label(Frange1, text="Startfreq")
        startfreqlab.pack(side=LEFT)
        StartFreqEntry = Entry(Frange1, width=8)
        StartFreqEntry.bind('<MouseWheel>', onTextScroll)
        StartFreqEntry.bind('<Key>', onTextKey)
        StartFreqEntry.pack(side=LEFT)
        StartFreqEntry.delete(0,"end")
        StartFreqEntry.insert(0,10)

        Frange2 = Frame( frame2fr )
        Frange2.pack(side=TOP)
        stopfreqlab = Label(Frange2, text="Stopfreq")
        stopfreqlab.pack(side=LEFT)
        StopFreqEntry = Entry(Frange2, width=8)
        StopFreqEntry.bind('<MouseWheel>', onTextScroll)
        StopFreqEntry.bind('<Key>', onTextKey)
        StopFreqEntry.pack(side=LEFT)
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,10000)
        
        HScale = IntVar(0)
        HScale.set(1)
        HzScale = Frame( frame2fr )
        HzScale.pack(side=TOP)
        rb1 = Radiobutton(HzScale, text="Lin F", variable=HScale, value=0, command=UpdateFreqTrace )
        rb1.pack(side=LEFT)
        rb2 = Radiobutton(HzScale, text="Log F", variable=HScale, value=1, command=UpdateFreqTrace )
        rb2.pack(side=LEFT)
        # V scale / gain
        ar1lab = Label(frame2fr, text="CH1 Gain")
        ar1lab.pack(side=TOP)
        AnaRange1 = Frame( frame2fr )
        AnaRange1.pack(side=TOP)
        ar1 = Radiobutton(AnaRange1, text="High", variable=CH1GainSA, value=0)
        ar1.pack(side=LEFT)
        ar2 = Radiobutton(AnaRange1, text="Low", variable=CH1GainSA, value=1)
        ar2.pack(side=LEFT)
        ar2lab = Label(frame2fr, text="CH2 Gain")
        ar2lab.pack(side=TOP)
        AnaRange2 = Frame( frame2fr )
        AnaRange2.pack(side=TOP)
        ar3 = Radiobutton(AnaRange2, text="High", variable=CH2GainSA, value=0)
        ar3.pack(side=LEFT)
        ar4 = Radiobutton(AnaRange2, text="Low", variable=CH2GainSA, value=1)
        ar4.pack(side=LEFT)
        
        DBrange = Frame( frame2fr )
        DBrange.pack(side=TOP)
        b3 = Button(DBrange, text="+dB/div", style="W8.TButton", command=BDBdiv2)
        b3.pack(side=LEFT)
        b4 = Button(DBrange, text="-dB/div", style="W8.TButton", command=BDBdiv1)
        b4.pack(side=LEFT)

        LVBrange = Frame( frame2fr )
        LVBrange.pack(side=TOP)
        b5 = Button(LVBrange, text="LVL+10", style="W8.TButton", command=Blevel4)
        b5.pack(side=LEFT)
        b6 = Button(LVBrange, text="LVL-10", style="W8.TButton", command=Blevel3)
        b6.pack(side=LEFT)

        LVSrange = Frame( frame2fr )
        LVSrange.pack(side=TOP)
        b7 = Button(LVSrange, text="LVL+1", style="W8.TButton", command=Blevel2)
        b7.pack(side=LEFT)
        b8 = Button(LVSrange, text="LVL-1", style="W8.TButton", command=Blevel1)
        b8.pack(side=LEFT)
        
        sadismiss1button = Button(frame2fr, text="Dismiss", style="W8.TButton", command=DestroySpectrumScreen)
        sadismiss1button.pack(side=TOP)
        
        ADI2 = Label(frame2fr, image=logo, anchor= "sw", compound="top") # , height=49, width=116
        ADI2.pack(side=TOP)
        FreqCheckBox()
        if ShowBallonHelp > 0:
            sb_tip = CreateToolTip(sb, 'Stop acquiring data')
            rb_tip = CreateToolTip(rb, 'Start acquiring data')
            bless_tip = CreateToolTip(bless, 'Decrease FFT samples')
            bmore_tip = CreateToolTip(bmore, 'Increase FFT samples')
            b3_tip = CreateToolTip(b3, 'Increase number of dB/Div')
            b4_tip = CreateToolTip(b4, 'Decrease number of dB/Div')
            b5_tip = CreateToolTip(b5, 'Increase Ref Level by 10 dB')
            b6_tip = CreateToolTip(b6, 'Decrease Ref Level by 10 dB')
            b7_tip = CreateToolTip(b7, 'Increase Ref Level by 1 dB')
            b8_tip = CreateToolTip(b8, 'Decrease Ref Level by 1 dB')
            sadismiss1button_tip = CreateToolTip(sadismiss1button, 'Dismiss Spectrum Analyzer window')
def DestroySpectrumScreen():
    global freqwindow, SpectrumScreenStatus, ca
    
    SpectrumScreenStatus.set(0)
    FreqDisp.set(0)
    FreqCheckBox()
    freqwindow.destroy()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
def XYcaresize(event):
    global XYca, GRWXY, XOLXY, GRHXY, Y0TXY, CANVASwidthXY, CANVASheightXY
    global YminXY, YmaxXY, XminXY, XmaxXY
    
    CANVASwidthXY = event.width
    CANVASheightXY = event.height
    GRWXY = CANVASwidthXY - 18 - X0LXY # new grid width
    GRHXY = CANVASheightXY - 80     # new grid height
    YminXY = Y0TXY                  # Minimum position of time grid (top)
    YmaxXY = Y0TXY + GRHXY            # Maximum position of time grid (bottom)
    XminXY = X0LXY                  # Minimum position of time grid (left)
    XmaxXY = X0LXY + GRWXY            # Maximum position of time grid (right)
    UpdateXYAll()
#    
# ================ Make spectrum sub window ==========================
def MakeXYWindow():
    global logo, CANVASwidthXY, CANVASheightXY, Xsignal, Ysignal, ShowRXY, ShowBallonHelp
    global XYScreenStatus, MarkerXYScale, XYca, xywindow, RevDate, XYDisp
    global CHAsbxy, CHBsbxy, CHAxylab, CHBxylab, CHAVPosEntryxy, CHBVPosEntryxy
    global CHAIsbxy, CHBIsbxy, CHAIPosEntryxy, CHBIPosEntryxy, ScreenXYrefresh
    global YminXY, Y0TXY, YmaxXY, GRHXY, XminXY, X0LXY, XmaxXY, X0LXY, GRWXY, CANVASwidthXY, CANVASheightXY
    global MC1sbxy, MC2sbxy, MC1VPosEntryxy, MC2VPosEntryxy, MC1labxy, MC2labxy
    
    if XYScreenStatus.get() == 0:
        XYScreenStatus.set(1)
        XYDisp.set(1)
        YminXY = Y0TXY                  # Minimum position of XY grid (top)
        YmaxXY = Y0TXY + GRHXY            # Maximum position of XY grid (bottom)
        XminXY = X0LXY                  # Minimum position of XY grid (left)
        XmaxXY = X0LXY + GRWXY            # Maximum position of XY grid (right)
        CANVASwidthXY = GRWXY + 18 + X0LXY     # The XY canvas width
        CANVASheightXY = GRHXY + 80         # The XY canvas height
        xywindow = Toplevel()
        xywindow.title("X-Y Plot 2.0 " + RevDate)
        xywindow.protocol("WM_DELETE_WINDOW", DestroyXYScreen)
        frame2xyr = Frame(xywindow, borderwidth=5, relief=RIDGE)
        frame2xyr.pack(side=RIGHT, expand=NO, fill=BOTH)
        frame2xy = Frame(xywindow, borderwidth=5, relief=RIDGE)
        frame2xy.pack(side=TOP, expand=YES, fill=BOTH)
        frame3xy = Frame(xywindow, borderwidth=5, relief=RIDGE)
        frame3xy.pack(side=TOP, expand=NO, fill=BOTH)
        frame4xy = Frame(xywindow, borderwidth=5, relief=RIDGE)
        frame4xy.pack(side=TOP, expand=NO, fill=BOTH)

        XYca = Canvas(frame2xy, width=CANVASwidthXY, height=CANVASheightXY, background=COLORcanvas, cursor='cross')
        XYca.bind('<Configure>', XYcaresize)
        XYca.bind('<1>', onCanvasXYLeftClick)
        XYca.bind('<3>', onCanvasXYRightClick)
        XYca.bind("<Motion>",onCanvasMouse_xy)
        XYca.bind("<Up>", onCanvasUpArrow)
        XYca.bind("<Down>", onCanvasDownArrow)
        XYca.bind("<Left>", onCanvasLeftArrow)
        XYca.bind("<Right>", onCanvasRightArrow)
        XYca.bind("a", onCanvasAverage)
        XYca.pack(side=TOP, fill=BOTH, expand=YES)
        #
        RUNframe = Frame( frame2xyr )
        RUNframe.pack(side=TOP)
        sb = Button(RUNframe, text="Stop", style="Stop.TButton", command=BStop)
        sb.pack(side=LEFT)
        rb = Button(RUNframe, text="Run", style="Run.TButton", command=BStart)
        rb.pack(side=LEFT)
        # Disply mode menu
        # X - Y mode signal select
        AxisLabX = Label(frame2xyr, text ="-X Axis-")
        AxisLabX.pack(side=TOP)
        chaxmenu = Frame( frame2xyr )
        chaxmenu.pack(side=TOP)
        rbx2 = Radiobutton(chaxmenu, text='C1-V', variable=Xsignal, value=1, command=UpdateXYTrace)
        rbx2.pack(side=LEFT, anchor=W)
        chbxmenu = Frame( frame2xyr )
        chbxmenu.pack(side=TOP)
        rbx4 = Radiobutton(chbxmenu, text='C2-V', variable=Xsignal, value=3, command=UpdateXYTrace)
        rbx4.pack(side=LEFT, anchor=W)
        rbx7 = Radiobutton(frame2xyr, text='Histogram C1-V', variable=Xsignal, value=6, command=BHistAsPercent)
        rbx7.pack(side=TOP)
        rbx8 = Radiobutton(frame2xyr, text='Histogram C2-V', variable=Xsignal, value=7, command=BHistAsPercent)
        rbx8.pack(side=TOP)
        rbx6 = Radiobutton(frame2xyr, text='Math', variable=Xsignal, value=5, command=UpdateXYTrace)
        rbx6.pack(side=TOP)
        xb1 = Button(frame2xyr, text="Enter X Formula", style="W16.TButton", command=BEnterMathXString)
        xb1.pack(side=TOP)
        #
        AxisLabY = Label(frame2xyr, text ="-Y Axis-")
        AxisLabY.pack(side=TOP)
        chaymenu = Frame( frame2xyr )
        chaymenu.pack(side=TOP)
        rby2 = Radiobutton(chaymenu, text='C1-V', variable=Ysignal, value=1, command=UpdateXYTrace)
        rby2.pack(side=LEFT, anchor=W)
        chbymenu = Frame( frame2xyr )
        chbymenu.pack(side=TOP)
        rby4 = Radiobutton(chbymenu, text='C2-V', variable=Ysignal, value=3, command=UpdateXYTrace)
        rby4.pack(side=LEFT, anchor=W)
        rby6 = Radiobutton(frame2xyr, text='Math',variable=Ysignal, value=5, command=UpdateXYTrace)
        rby6.pack(side=TOP)
        yb1 = Button(frame2xyr, text="Enter Y Formula", style="W16.TButton", command=BEnterMathYString)
        yb1.pack(side=TOP)
        # show cursor menu buttons
        cursormenu = Frame( frame2xyr )
        cursormenu.pack(side=TOP)
        cb1 = Checkbutton(cursormenu, text='X-Cur', variable=ShowXCur)
        cb1.pack(side=LEFT, anchor=W)
        cb2 = Checkbutton(cursormenu, text='Y-Cur', variable=ShowYCur)
        cb2.pack(side=LEFT, anchor=W)
        cb3 = Checkbutton(frame2xyr, text='RX-Y', variable=ShowRXY, command=UpdateXYTrace)
        cb3.pack(side=TOP)
        cb4 = Checkbutton(frame2xyr, text='Persistance', variable=ScreenXYrefresh, command=UpdateXYTrace)
        cb4.pack(side=TOP)
        #
        snapbutton = Button(frame2xyr, text="SnapShot", style="W8.TButton", command=BSnapShot)
        snapbutton.pack(side=TOP)
        savebutton = Button(frame2xyr, text="Save Screen", style="W11.TButton", command=BSaveScreenXY)
        savebutton.pack(side=TOP)
        dismissxybutton = Button(frame2xyr, text="Dismiss", style="W7.TButton", command=DestroyXYScreen)
        dismissxybutton.pack(side=TOP)
        ADI1xy = Label(frame2xyr, image=logo, anchor= "sw", compound="top") # , height=49, width=116
        ADI1xy.pack(side=TOP)
        # Bottom Buttons
        MarkerXYScale = IntVar(0)
        MarkerXYScale.set(1)
        # Voltage channel 1
        CHAsbxy = Spinbox(frame3xy, width=4, values=CHvpdiv)
        CHAsbxy.bind('<MouseWheel>', onSpinBoxScroll)
        CHAsbxy.pack(side=LEFT)
        CHAsbxy.delete(0,"end")
        CHAsbxy.insert(0,0.5)
        CHAxylab = Button(frame3xy, text="C1 V/Div", style="Rtrace1.TButton", command=SetXYScaleA)
        CHAxylab.pack(side=LEFT)

        CHAVPosEntryxy = Entry(frame3xy, width=5)
        CHAVPosEntryxy.bind('<MouseWheel>', onTextScroll)
        CHAVPosEntryxy.bind('<Key>', onTextKey)
        CHAVPosEntryxy.pack(side=LEFT)
        CHAVPosEntryxy.delete(0,"end")
        CHAVPosEntryxy.insert(0,2.5)
        CHAofflabxy = Button(frame3xy, text="C1 V Pos", style="Rtrace1.TButton", command=SetXYVAPoss)
        CHAofflabxy.pack(side=LEFT)
        # Math channel 1
        MC1sbxy = Spinbox(frame3xy, width=4, values=CHvpdiv) #, command=BCHBlevel)
        MC1sbxy.bind('<MouseWheel>', onSpinBoxScroll)
        MC1sbxy.pack(side=LEFT)
        MC1sbxy.delete(0,"end")
        MC1sbxy.insert(0,0.5)
        # 
        MC1labxy = Button(frame3xy, text="MC1 /Div", style="Strace5.TButton", command=SetXYScaleMC1)
        MC1labxy.pack(side=LEFT)
        MC1VPosEntryxy = Entry(frame3xy, width=5)
        MC1VPosEntryxy.bind("<Return>", BOffsetB)
        MC1VPosEntryxy.bind('<MouseWheel>', onTextScroll)
        MC1VPosEntryxy.bind('<Key>', onTextKey)
        MC1VPosEntryxy.pack(side=LEFT)
        MC1VPosEntryxy.delete(0,"end")
        MC1VPosEntryxy.insert(0,0.0)
        MC1offlabxy = Button(frame3xy, text="MC1 Pos", style="Rtrace5.TButton") #, command=SetXYMC1Poss)
        MC1offlabxy.pack(side=LEFT)
        # Voltage channel B
        CHBsbxy = Spinbox(frame4xy, width=4, values=CHvpdiv)
        CHBsbxy.bind('<MouseWheel>', onSpinBoxScroll)
        CHBsbxy.pack(side=LEFT)
        CHBsbxy.delete(0,"end")
        CHBsbxy.insert(0,0.5)
        #
        CHBxylab = Button(frame4xy, text="C2 V/Div", style="Strace2.TButton", command=SetXYScaleB)
        CHBxylab.pack(side=LEFT)
        CHBVPosEntryxy = Entry(frame4xy, width=5)
        CHBVPosEntryxy.bind('<MouseWheel>', onTextScroll)
        CHBVPosEntryxy.bind('<Key>', onTextKey)
        CHBVPosEntryxy.pack(side=LEFT)
        CHBVPosEntryxy.delete(0,"end")
        CHBVPosEntryxy.insert(0,2.5)
        CHBofflabxy = Button(frame4xy, text="C2 V Pos", style="Rtrace2.TButton", command=SetXYVBPoss)
        CHBofflabxy.pack(side=LEFT)
        # Math channel 2
        MC2sbxy = Spinbox(frame4xy, width=4, values=CHvpdiv) #, command=BCHBlevel)
        MC2sbxy.bind('<MouseWheel>', onSpinBoxScroll)
        MC2sbxy.pack(side=LEFT)
        MC2sbxy.delete(0,"end")
        MC2sbxy.insert(0,0.5)
        MC2labxy = Button(frame4xy, text="MC2 /Div", style="Strace7.TButton", command=SetXYScaleMC2)
        MC2labxy.pack(side=LEFT)
        MC2VPosEntryxy = Entry(frame4xy, width=5)
        MC2VPosEntryxy.bind("<Return>", BOffsetB)
        MC2VPosEntryxy.bind('<MouseWheel>', onTextScroll)
        MC2VPosEntryxy.bind('<Key>', onTextKey)
        MC2VPosEntryxy.pack(side=LEFT)
        MC2VPosEntryxy.delete(0,"end")
        MC2VPosEntryxy.insert(0,0.0)
        MC2offlabxy = Button(frame4xy, text="MC2 Pos", style="Rtrace7.TButton") # , command=SetXYMC1Poss)
        MC2offlabxy.pack(side=LEFT)
        #
        XYCheckBox()
        if ShowBallonHelp > 0:
            xb1_tip = CreateToolTip(xb1, 'Enter formula for X axis Math trace')
            yb1_tip = CreateToolTip(yb1, 'Enter formula for Y axis Math trace')
            snapbutton_tip = CreateToolTip(snapbutton, 'Take snap shot of current trace')
            savebutton_tip = CreateToolTip(savebutton, 'Save current trace to EPS file')
            dismissxybutton_tip = CreateToolTip(dismissxybutton, 'Diamiss X-Y plot window')
            CHAxylab_tip = CreateToolTip(CHAxylab, 'Select CH1-V vertical range/position axis to be used for markers and drawn color')
            CHBxylab_tip = CreateToolTip(CHBxylab, 'Select CH2-V vertical range/position axis to be used for markers and drawn color')
            CHAxyofflab_tip = CreateToolTip(CHAofflabxy, 'Set CH1-V position to DC average of signal')
            CHBxyofflab_tip = CreateToolTip(CHBofflabxy, 'Set CH2-V position to DC average of signal')

def DestroyXYScreen():
    global xywindow, XYScreenStatus, ca, XYDisp
    
    XYScreenStatus.set(0)
    XYDisp.set(0)
    XYCheckBox()
    xywindow.destroy()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
# Self Calibration procedure routine
#
def BSelfCalibration():
    SelfCalibration() # Run a sel calibration to start
    BAWGEnab() # restart AWGs
    
def SelfCalibration():
    global RevDate, FWRevOne, SAMPLErate, AWGASampleRate, dac_a_pd, dac_b_pd, m2k_AWG2pd
    global ctx, m2k_fabric, m2k_adc, adc0, adc1, TimeBuffer, Scope1Offset, Scope2Offset
    global AWGAgain, AWGAoffset, AWGBgain, AWGBoffset, ch1_multiplier, ch2_multiplier, AWG1Offset
    global AWGAgain7M, AWGAgain75M, AWGBgain7M, AWGBgain75M, m2k_fabric, m2k_AWG1pd, AWG2Offset
    global CH1hwOffset, CH2hwOffset, Buff0, Buff1, m2k_dac_a, m2k_dac_b, ad9963
    global CH1_H_Gain1K, CH1_L_Gain1K, CH2_H_Gain1K, CH2_L_Gain1K
    global CH1_H_Gain10K, CH1_L_Gain10K, CH2_H_Gain10K, CH2_L_Gain10K
    global CH1_H_Gain100K, CH1_L_Gain100K, CH2_H_Gain100K, CH2_L_Gain100K
    global CH1_H_Gain1M, CH1_L_Gain1M, CH2_H_Gain1M, CH2_L_Gain1M
    global CH1_H_Gain10M, CH1_L_Gain10M, CH2_H_Gain10M, CH2_L_Gain10M
    global CH1_H_Gain100M, CH1_L_Gain100M, CH2_H_Gain100M, CH2_L_Gain100M
    global Awg_divider, ADC_0_gain, ADC_1_gain, CH1PosFactor, CH2PosFactor
    global AWGAgain750K, AWGBgain750K, AWGAgain75K, AWGBgain75K

    # set awg sample rates
    print "Sarting Self Calibration"
    AWGASampleRate = AWGBSampleRate = 7500000
    m2k_dac_a.attrs["sampling_frequency"].value = str(AWGASampleRate)
    m2k_dac_b.attrs["sampling_frequency"].value = str(AWGBSampleRate)
    # print "I DAC 0x68 = ", ad9963.reg_read(0x68)
    # print "Q DAC 0x6B = ", ad9963.reg_read(0x6B)
    # print "I DAC 0x69 = ", ad9963.reg_read(0x69)
    # print "Q DAC 0x6C = ", ad9963.reg_read(0x6C)
    # print "I DAC 0x6A = ", ad9963.reg_read(0x6A)
    # print "Q DAC 0x6D = ", ad9963.reg_read(0x6D)
    ad9963.reg_write(0x68, 0x00) # 0x05)
    ad9963.reg_write(0x6B, 0x00) # 0x05)
    ad9963.reg_write(0x69, 0x00) # 0x1C) # IGAIN2 +-2.5%
    ad9963.reg_write(0x6C, 0x00) # 0x1C)
    # ad9963.reg_write(0x6A, 0x20) # IRSET +-20%
    # ad9963.reg_write(0x6D, 0x20)
    ad9963.reg_write(0x6A, 0x2A) # Decrease Rset values
    ad9963.reg_write(0x6D, 0x2A) # Increasing DAC output current
    # print "I DAC 0x6A = ", ad9963.reg_read(0x6A)
    # print "Q DAC 0x6D = ", ad9963.reg_read(0x6D)
    # power up AWG 1 and 2
    m2k_AWG1pd.attrs["powerdown"].value = '0'
    AWG1Offset.attrs["powerdown"].value = '0'
    dac_a_pd.attrs["powerdown"].value = '0'
    m2k_AWG2pd.attrs["powerdown"].value = '0'
    AWG2Offset.attrs["powerdown"].value = '0'
    dac_b_pd.attrs["powerdown"].value = '0'
    time.sleep(0.1)
# make a zero DC level waveform
    AWGAwaveform = []
    Width = 1000
    if Width <=0:
        Width = 1
    for i in range(Width):
        AWGAwaveform.append(0)
    #
    AWGAwaveform = bytearray(numpy.array(AWGAwaveform,dtype="int16"))
    m2k_dac_a.attrs["dma_sync"].value = '1' 
    m2k_dac_b.attrs["dma_sync"].value = '1'
    blenght = int(len(AWGAwaveform)/2)
    try:
        Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
    except:
        del(Buff0) # delete old buffer and make a new one
        Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
    Buff0.write(AWGAwaveform)
    Buff0.push()
    try:
        Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
    except:
        del(Buff1) # delete old buffer and make a new one
        Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
    Buff1.write(AWGAwaveform)
    Buff1.push()
    m2k_dac_a.attrs["dma_sync"].value = '0' # resyn AWG channels
    m2k_dac_b.attrs["dma_sync"].value = '0'
    time.sleep(0.1)
# define some harware constants
    if AWGAgain < 4000 or AWGAgain > 5000:
        AWGAgain = 4300 # 6100
    if AWGBgain < 4000 or AWGBgain > 5000:
        AWGBgain = 4300 # 6100
    Input_divider_h = 221.0/1041.0
    Input_divider_l = 20.9/1041.0
    Awg_divider = 1.0/9.0 # was 9.06
    ADC_Ref1 = 1.2/2.6
    ADC_Ref2 = 1.2/5.02
    High_Low_Ratio = 221.0/21.0
    # set sample rate to lowest value
    SAMPLErate = 1000
    m2k_adc.attrs["sampling_frequency"].value = str(SAMPLErate)
    adc0.enabled = True
    adc1.enabled = True
    try:
        TimeBuffer = iio.Buffer(m2k_adc, 256, False)
    except:
        del(TimeBuffer)
        TimeBuffer = iio.Buffer(m2k_adc, 256, False)
# First step is to measure scope offset DAC with input grounded
    Scope1Offset.attrs["raw"].value = str(CH1hwOffset) # set approx inital value
    Scope2Offset.attrs["raw"].value = str(CH2hwOffset)
    m2k_fabric.attrs["calibration_mode"].value = 'adc_gnd'
    time.sleep(0.2)
    TimeBuffer.refill()
    x = TimeBuffer.read()
    X = []
    for n in range (0, len(x), 2):
        X.append(struct.unpack_from("<h", x, n)[0])
    VCH1 = VCH2 = 0
    AvgCount = 0
    for n in range (126, len(X), 2):
        VCH1 = VCH1 + float(X[n])
        VCH2 = VCH2 + float(X[n+1])
        AvgCount = AvgCount + 1
    VCH1 = VCH1 / AvgCount
    VCH2 = VCH2 / AvgCount
    # print "Grounded VCH1 = ", VCH1, "VCH2 = ", VCH2
    CH1hwOffset = 2009 - int(VCH1/1.5)
    CH2hwOffset = 2009 - int(VCH2/1.5)
    Scope1Offset.attrs["raw"].value = str(CH1hwOffset) # set new value
    Scope2Offset.attrs["raw"].value = str(CH2hwOffset)
    # print "new scope offset ", CH1hwOffset, CH2hwOffset
# Now measure offset DAC gain
    HwOffset = 875 # approx number for 2.5 V shift in position high gain mode
    Scope1Offset.attrs["raw"].value = str(CH1hwOffset-HwOffset) # set new value
    Scope2Offset.attrs["raw"].value = str(CH2hwOffset-HwOffset)
    time.sleep(0.1)
    TimeBuffer.refill()
    x = TimeBuffer.read()
    X = []
    for n in range (0, len(x), 2):
        X.append(struct.unpack_from("<h", x, n)[0])
    VCH1 = VCH2 = 0
    AvgCount = 0
    for n in range (126, len(X), 2):
        VCH1 = VCH1 + float(X[n])
        VCH2 = VCH2 + float(X[n+1])
        AvgCount = AvgCount + 1
    CH1OffsetDACgain = VCH1 / AvgCount
    CH2OffsetDACgain = VCH2 / AvgCount
    Scope1Offset.attrs["raw"].value = str(CH1hwOffset) # reset back to new value
    Scope2Offset.attrs["raw"].value = str(CH2hwOffset)
# Secomd step is to measure first ADC reference voltage
    m2k_fabric.attrs["calibration_mode"].value = 'adc_ref1'
    time.sleep(0.2)
    TimeBuffer.refill()
    x = TimeBuffer.read()
    X = []
    for n in range (0, len(x), 2):
        X.append(struct.unpack_from("<h", x, n)[0])
    VCH1 = VCH2 = 0
    AvgCount = 1
    for n in range (126, len(X), 2):
        VCH1 = VCH1 + float(X[n])
        VCH2 = VCH2 + float(X[n+1])
        AvgCount = AvgCount + 1
    VCH1 = VCH1 / AvgCount
    VCH2 = VCH2 / AvgCount
    CH1_Ref1_cal_h = (ADC_Ref1*2048.0)/(VCH1*Input_divider_h)
    CH2_Ref1_cal_h = (ADC_Ref1*2048.0)/(VCH2*Input_divider_h)
    CH1_Ref1_cal_l = (ADC_Ref1*2048.0)/(VCH1*Input_divider_l)
    CH2_Ref1_cal_l = (ADC_Ref1*2048.0)/(VCH2*Input_divider_l)
    ADC_0_gain = (ADC_Ref1*2048.0)/(VCH1)
    ADC_1_gain = (ADC_Ref1*2048.0)/(VCH2)
    # print "ADC 0 gain = ", ADC_0_gain, "ADC 1 gain = ", ADC_1_gain
# Third step is to measure second ADC reference voltage
    m2k_fabric.attrs["calibration_mode"].value = 'adc_ref2'
    time.sleep(0.2)
    TimeBuffer.refill()
    x = TimeBuffer.read()
    X = []
    for n in range (0, len(x), 2):
        X.append(struct.unpack_from("<h", x, n)[0])
    VCH1 = VCH2 = 0
    AvgCount = 1
    for n in range (126, len(X), 2):
        VCH1 = VCH1 + float(X[n])
        VCH2 = VCH2 + float(X[n+1])
        AvgCount = AvgCount + 1
    VCH1 = VCH1 / AvgCount
    VCH2 = VCH2 / AvgCount
    # print "ADC Ref 2 VCH1 = ", VCH1, "VCH2 = ", VCH2
    CH1_Ref2_cal_h = (ADC_Ref2*2048.0)/(VCH1*Input_divider_h)
    CH2_Ref2_cal_h = (ADC_Ref2*2048.0)/(VCH2*Input_divider_h)
    CH1_Ref2_cal_l = (ADC_Ref2*2048.0)/(VCH1*Input_divider_l)
    CH2_Ref2_cal_l = (ADC_Ref2*2048.0)/(VCH2*Input_divider_l)
    
    CH1_H_Gain1K = (CH1_Ref1_cal_h+CH1_Ref2_cal_h)/2.0
    CH2_H_Gain1K = (CH2_Ref1_cal_h+CH2_Ref2_cal_h)/2.0
    CH1_L_Gain1K = (CH1_Ref1_cal_l+CH1_Ref2_cal_l)/2.0
    CH2_L_Gain1K = (CH2_Ref1_cal_l+CH2_Ref2_cal_l)/2.0
    #
    rx_filt_comp_table100M = 1.00
    rx_filt_comp_table10M = 1.05
    rx_filt_comp_table1M = 1.10
    rx_filt_comp_table100K = 1.15
    rx_filt_comp_table10K = 1.20
    rx_filt_comp_table1K = 1.26
    #
    CH1_H_Gain10K = CH1_H_Gain1K / rx_filt_comp_table10M
    CH2_H_Gain10K = CH2_H_Gain1K / rx_filt_comp_table10M
    CH1_L_Gain10K = CH1_L_Gain1K / rx_filt_comp_table10M
    CH2_L_Gain10K = CH2_L_Gain1K / rx_filt_comp_table10M

    CH1_H_Gain100K = CH1_H_Gain1K / rx_filt_comp_table1M
    CH2_H_Gain100K = CH2_H_Gain1K / rx_filt_comp_table1M
    CH1_L_Gain100K = CH1_L_Gain1K / rx_filt_comp_table1M
    CH2_L_Gain100K = CH2_L_Gain1K / rx_filt_comp_table1M

    CH1_H_Gain1M = CH1_H_Gain1K / rx_filt_comp_table100K
    CH2_H_Gain1M = CH2_H_Gain1K / rx_filt_comp_table100K
    CH1_L_Gain1M = CH1_L_Gain1K / rx_filt_comp_table100K
    CH2_L_Gain1M = CH2_L_Gain1K / rx_filt_comp_table100K

    CH1_H_Gain10M = CH1_H_Gain1K / rx_filt_comp_table10K
    CH2_H_Gain10M = CH2_H_Gain1K / rx_filt_comp_table10K
    CH1_L_Gain10M = CH1_L_Gain1K / rx_filt_comp_table10K
    CH2_L_Gain10M = CH2_L_Gain1K / rx_filt_comp_table10K

    CH1_H_Gain100M = CH1_H_Gain1K / rx_filt_comp_table1K
    CH2_H_Gain100M = CH2_H_Gain1K / rx_filt_comp_table1K
    CH1_L_Gain100M = CH1_L_Gain1K / rx_filt_comp_table1K
    CH2_L_Gain100M = CH2_L_Gain1K / rx_filt_comp_table1K

    ch1_multiplier = CH1_H_Gain1K
    ch2_multiplier = CH2_H_Gain1K
# calculate scope positon factors
    CH1PosFactor = -875/((CH1OffsetDACgain/2048.0)*ch1_multiplier)
    CH2PosFactor = -875/((CH2OffsetDACgain/2048.0)*ch2_multiplier)
    # print "CH1 pos = ", CH1PosFactor, "CH2 pos = ", CH2PosFactor
# calibrate AWG offsets
    AWG1Offset.attrs["raw"].value = str(AWGAoffset)
    AWG2Offset.attrs["raw"].value = str(AWGBoffset)
    m2k_fabric.attrs["calibration_mode"].value = 'dac'
# measure AWG offsets
    time.sleep(0.2)
    TimeBuffer.refill()
    x = TimeBuffer.read()
    X = []
    for n in range (0, len(x), 2):
        X.append(struct.unpack_from("<h", x, n)[0])
    VCH1 = VCH2 = 0
    AvgCount = 1
    for n in range (126, len(X), 2):
        VCH1 = VCH1 + float(X[n])
        VCH2 = VCH2 + float(X[n+1])
        AvgCount = AvgCount + 1
    VCH1 = VCH1 / AvgCount
    VCH2 = VCH2 / AvgCount
    # print "AWG zero VCH1 = ", VCH1, "VCH2 = ", VCH2
    AWGAoffset = AWGAoffset - int(VCH1/0.8)
    AWGBoffset = AWGBoffset - int(VCH2/0.8)
    AWG1Offset.attrs["raw"].value = str(AWGAoffset) # set new value
    AWG2Offset.attrs["raw"].value = str(AWGBoffset)
    # print "new awg offset ", AWGAoffset, AWGBoffset
# Remasure offset a second time
    time.sleep(0.1)
    TimeBuffer.refill()
    x = TimeBuffer.read()
    X = []
    for n in range (0, len(x), 2):
        X.append(struct.unpack_from("<h", x, n)[0])
    VCH1 = VCH2 = 0
    AvgCount = 1
    for n in range (126, len(X), 2):
        VCH1 = VCH1 + float(X[n])
        VCH2 = VCH2 + float(X[n+1])
        AvgCount = AvgCount + 1
    VCH1 = VCH1 / AvgCount
    VCH2 = VCH2 / AvgCount
    # print "AWG zero VCH1 = ", VCH1, "VCH2 = ", VCH2
    AWGAoffset = AWGAoffset - int(VCH1/1.0)
    AWGBoffset = AWGBoffset - int(VCH2/1.0)
    AWG1Offset.attrs["raw"].value = str(AWGAoffset) # set new value
    AWG2Offset.attrs["raw"].value = str(AWGBoffset)
    # print "new awg offset ", AWGAoffset, AWGBoffset
# make a 2.5 V DC level waveform
    MaxV = -16384 # 1/4 of range +/- 32768
    AWGAwaveform = []
    Width = 1000
    if Width <=0:
        Width = 1
    for i in range(Width):
        AWGAwaveform.append(MaxV)
    #
    AWGAwaveform = bytearray(numpy.array(AWGAwaveform,dtype="int16"))
    m2k_dac_a.attrs["dma_sync"].value = '1' 
    m2k_dac_b.attrs["dma_sync"].value = '1'
    blenght = int(len(AWGAwaveform)/2)
    try:
        Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
    except:
        del(Buff0) # delete old buffer and make a new one
        Buff0 = iio.Buffer(m2k_dac_a, blenght, True)
    Buff0.write(AWGAwaveform)
    Buff0.push()
    try:
        Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
    except:
        del(Buff1) # delete old buffer and make a new one
        Buff1 = iio.Buffer(m2k_dac_b, blenght, True)
    Buff1.write(AWGAwaveform)
    Buff1.push()
    m2k_dac_a.attrs["dma_sync"].value = '0' # resyn AWG channels
    m2k_dac_b.attrs["dma_sync"].value = '0'
    # measure gain
    TimeBuffer.refill()
    x = TimeBuffer.read()
    time.sleep(0.2)
    TimeBuffer.refill()
    x = TimeBuffer.read()
    X = []
    for n in range (0, len(x), 2):
        X.append(struct.unpack_from("<h", x, n)[0])
    VCH1 = VCH2 = 0
    AvgCount = 1
    for n in range (126, len(X), 2):
        VCH1 = VCH1 + float(X[n])
        VCH2 = VCH2 + float(X[n+1])
        AvgCount = AvgCount + 1
    VCH1 = VCH1 / AvgCount
    VCH2 = VCH2 / AvgCount
    # print "AWG avg VCH1 = ", VCH1, "VCH2 = ", VCH2
    # Calculate reading in volts
    Awg1Value = (VCH1)/(2048.0*Awg_divider)*ADC_0_gain
    Awg2Value = (VCH2)/(2048.0*Awg_divider)*ADC_1_gain # scale to volts
    # print "old awg gain ", AWGAgain, AWGBgain
    # print "AWG 2.5 VCH1 = ", Awg1Value, "VCH2 = ", Awg2Value
    AWGAgain = AWGAgain7M = (16384 / Awg1Value) #
    AWGBgain = AWGBgain7M = (16384 / Awg2Value) #
    # print "new awg gain ", AWGAgain7M, AWGBgain7M
    tx_filt_comp_table75m = 1.00
    tx_filt_comp_table7m = 1.525879
    tx_filt_comp_table750k = 1.164153
    tx_filt_comp_table75k = 1.776357
    tx_filt_comp_table7k = 1.355253
    tx_filt_comp_table750 = 1.033976
    #
    AWGAgain75M = AWGAgain7M * tx_filt_comp_table7m
    AWGBgain75M = AWGBgain7M * tx_filt_comp_table7m
    AWGAgain750K = AWGAgain75M / tx_filt_comp_table750k
    AWGBgain750K = AWGBgain75M / tx_filt_comp_table750k
    AWGAgain75K = AWGAgain75M / tx_filt_comp_table75k
    AWGBgain75K = AWGBgain75M / tx_filt_comp_table75k
    # turn off calibration mode
    # time.sleep(2)
    m2k_fabric.attrs["calibration_mode"].value = 'none'
    print "Completed Self Calibration."

def SaveCalibration():
    global DevID, AWGAoffset, AWGBoffset
    global AWGAgain7M, AWGAgain75M, AWGBgain7M, AWGBgain75M
    global AWGAgain750K, AWGBgain750K, AWGAgain75K, AWGBgain75K
    global CH1hwOffset, CH2hwOffset, CH1PosFactor, CH2PosFactor
    global CH1_H_Gain1K, CH1_L_Gain1K, CH2_H_Gain1K, CH2_L_Gain1K
    global CH1_H_Gain10K, CH1_L_Gain10K, CH2_H_Gain10K, CH2_L_Gain10K
    global CH1_H_Gain100K, CH1_L_Gain100K, CH2_H_Gain100K, CH2_L_Gain100K
    global CH1_H_Gain1M, CH1_L_Gain1M, CH2_H_Gain1M, CH2_L_Gain1M
    global CH1_H_Gain10M, CH1_L_Gain10M, CH2_H_Gain10M, CH2_L_Gain10M
    global CH1_H_Gain100M, CH1_L_Gain100M, CH2_H_Gain100M, CH2_L_Gain100M

    # Write cal factors to file
    devidstr = DevID[17:31]
    filename = devidstr + "_self.cal"
    CalFile = open(filename, "w")
    CalFile.write('global CH1hwOffset; CH1hwOffset = ' + str(CH1hwOffset) + '\n')
    CalFile.write('global CH2hwOffset; CH2hwOffset = ' + str(CH2hwOffset) + '\n')
    CalFile.write('global CH1PosFactor; CH1PosFactor = ' + str(CH1PosFactor) + '\n')
    CalFile.write('global CH2PosFactor; CH2PosFactor = ' + str(CH2PosFactor) + '\n')
    CalFile.write('global AWGAoffset; AWGAoffset = ' + str(AWGAoffset) + '\n')
    CalFile.write('global AWGBoffset; AWGBoffset = ' + str(AWGBoffset) + '\n')
    CalFile.write('global AWGAgain7M; AWGAgain7M = ' + str(AWGAgain7M) + '\n')
    CalFile.write('global AWGBgain7M; AWGBgain7M = ' + str(AWGBgain7M) + '\n')
    CalFile.write('global AWGAgain75M; AWGAgain75M = ' + str(AWGAgain75M) + '\n')
    CalFile.write('global AWGBgain75M; AWGBgain75M = ' + str(AWGBgain75M) + '\n')
    CalFile.write('global AWGAgain75K; AWGAgain75K = ' + str(AWGAgain75K) + '\n')
    CalFile.write('global AWGBgain75K; AWGBgain75K = ' + str(AWGBgain75K) + '\n')
    CalFile.write('global AWGAgain750K; AWGAgain750KM = ' + str(AWGAgain750K) + '\n')
    CalFile.write('global AWGBgain750K; AWGBgain750KM = ' + str(AWGBgain750K) + '\n')
    #
    CalFile.write('global CH1_H_Gain1K; CH1_H_Gain1K = ' + str(CH1_H_Gain1K) + '\n')
    CalFile.write('global CH2_H_Gain1K; CH2_H_Gain1K = ' + str(CH2_H_Gain1K) + '\n')
    CalFile.write('global CH1_L_Gain1K; CH1_L_Gain1K = ' + str(CH1_L_Gain1K) + '\n')
    CalFile.write('global CH2_L_Gain1K; CH2_L_Gain1K = ' + str(CH2_L_Gain1K) + '\n')
    #
    CalFile.write('global CH1_H_Gain10K; CH1_H_Gain10K = ' + str(CH1_H_Gain10K) + '\n')
    CalFile.write('global CH2_H_Gain10K; CH2_H_Gain10K = ' + str(CH2_H_Gain10K) + '\n')
    CalFile.write('global CH1_L_Gain10K; CH1_L_Gain10K = ' + str(CH1_L_Gain10K) + '\n')
    CalFile.write('global CH2_L_Gain10K; CH2_L_Gain10K = ' + str(CH2_L_Gain10K) + '\n')
    #
    CalFile.write('global CH1_H_Gain100K; CH1_H_Gain100K = ' + str(CH1_H_Gain100K) + '\n')
    CalFile.write('global CH2_H_Gain100K; CH2_H_Gain100K = ' + str(CH2_H_Gain100K) + '\n')
    CalFile.write('global CH1_L_Gain100K; CH1_L_Gain100K = ' + str(CH1_L_Gain100K) + '\n')
    CalFile.write('global CH2_L_Gain100K; CH2_L_Gain100K = ' + str(CH2_L_Gain100K) + '\n')
    #
    CalFile.write('global CH1_H_Gain1M; CH1_H_Gain1M = ' + str(CH1_H_Gain1M) + '\n')
    CalFile.write('global CH2_H_Gain1M; CH2_H_Gain1M = ' + str(CH2_H_Gain1M) + '\n')
    CalFile.write('global CH1_L_Gain1M; CH1_L_Gain1M = ' + str(CH1_L_Gain1M) + '\n')
    CalFile.write('global CH2_L_Gain1M; CH2_L_Gain1M = ' + str(CH2_L_Gain1M) + '\n')
    #
    CalFile.write('global CH1_H_Gain10M; CH1_H_Gain10M = ' + str(CH1_H_Gain10M) + '\n')
    CalFile.write('global CH2_H_Gain10M; CH2_H_Gain10M = ' + str(CH2_H_Gain10M) + '\n')
    CalFile.write('global CH1_L_Gain10M; CH1_L_Gain10M = ' + str(CH1_L_Gain10M) + '\n')
    CalFile.write('global CH2_L_Gain10M; CH2_L_Gain10M = ' + str(CH2_L_Gain10M) + '\n')
    #
    CalFile.write('global CH1_H_Gain100M; CH1_H_Gain100M = ' + str(CH1_H_Gain100M) + '\n')
    CalFile.write('global CH2_H_Gain100M; CH2_H_Gain100M = ' + str(CH2_H_Gain100M) + '\n')
    CalFile.write('global CH1_L_Gain100M; CH1_L_Gain100M = ' + str(CH1_L_Gain100M) + '\n')
    CalFile.write('global CH2_L_Gain100M; CH2_L_Gain100M = ' + str(CH2_L_Gain100M) + '\n')
    #
    CalFile.close()
#
def LoadCalibration():
    global DevID, AWGAoffset, AWGBoffset
    global AWGAgain7M, AWGAgain75M, AWGBgain7M, AWGBgain75M
    global AWGAgain750K, AWGBgain750K, AWGAgain75K, AWGBgain75K
    global CH1hwOffset, CH2hwOffset, CH1PosFactor, CH2PosFactor
    global CH1_H_Gain1K, CH1_L_Gain1K, CH2_H_Gain1K, CH2_L_Gain1K
    global CH1_H_Gain10K, CH1_L_Gain10K, CH2_H_Gain10K, CH2_L_Gain10K
    global CH1_H_Gain100K, CH1_L_Gain100K, CH2_H_Gain100K, CH2_L_Gain100K
    global CH1_H_Gain1M, CH1_L_Gain1M, CH2_H_Gain1M, CH2_L_Gain1M
    global CH1_H_Gain10M, CH1_L_Gain10M, CH2_H_Gain10M, CH2_L_Gain10M
    global CH1_H_Gain100M, CH1_L_Gain100M, CH2_H_Gain100M, CH2_L_Gain100M
    # Read cal factors from file
    devidstr = DevID[17:31]
    filename = devidstr + "_self.cal"
    try:
        CalFile = open(filename)
        for line in CalFile:
            try:
                exec( line.rstrip() )
            except:
                print "Skiping " + line.rstrip()
        CalFile.close()
    except:
        print "Cal file for this device not found"
#
# ========== MiniGen routines ==========
def SPIShiftOut(DValue):
    global Dig0, Dig1, Dig2, Dig3, logic, ctx
    
    Dig0.attrs["direction"].value = 'out'
    Dig1.attrs["direction"].value = 'out'
    Dig2.attrs["direction"].value = 'out'
    Dig3.attrs["direction"].value = 'out'
    binstr = bin(DValue)
    binlen = len(binstr)
    datastr = binstr[2:binlen]
    datalen = len(datastr)
    if datalen < 16:
       datastr = str.rjust(datastr , 16 , '0')
       datalen = len(datastr)
    i = 1
    Dig0.attrs["raw"].value = '0' # set PIO fsync to 0
    while i < datalen+1:
    #
        D1code = int(datastr[i-1])
        Dig1.attrs["raw"].value = str(D1code) # set PI1 data bit
        Dig3.attrs["raw"].value = '1' # set PI3 sclk to 1
        Dig3.attrs["raw"].value = '0' # set PI3 sclk to 0
        Dig3.attrs["raw"].value = '1' # set PI3 sclk to 1
        i = i + 1
    Dig0.attrs["raw"].value = '1' # set PIO fsync to 1
#
def BSendMG():
    global MinigenFclk, MinigenFout, MinigenMode
    global Two28

    DValue = 8192 + MinigenMode.get()
    SPIShiftOut(DValue)
    try:
        fout = float(eval(MinigenFout.get()))
    except:
        MinigenFout.delete(0,"end")
        MinigenFout.insert(0,100)
    try:
        mclk = float(eval(MinigenFclk.get()))*1000000 # convert from MHz to Hz
    except:
        MingenFclk.delete(0,"end")
        MinigenFclk.insert(0,16)
    Freg = int((fout*Two28)/mclk)
    Foutstr = bin(Freg)
    Foutlen = len(Foutstr)
    datastr = Foutstr[2:Foutlen]
    datalen = len(datastr)
    if datalen < 28:
       datastr = str.rjust(datastr , 28 , '0')
       datalen = len(datastr)
    Fmsb = '0b01' + datastr[0:14]
    Flsb = '0b01' + datastr[14:]
    FValue = int(eval(Flsb))
    SPIShiftOut(FValue)
    FValue = int(eval(Fmsb))
    SPIShiftOut(FValue)
    
def MakeMinigenWindow():
    global  RevDate, minigenwindow, MinigenMode, MinigenScreenStatus, MinigenFclk, MinigenFout

    if MinigenScreenStatus.get() == 0:
        MinigenScreenStatus.set(1)
        minigenwindow = Toplevel()
        minigenwindow.title("MiniGen 2.0 " + RevDate)
        minigenwindow.resizable(FALSE,FALSE)
        minigenwindow.protocol("WM_DELETE_WINDOW", DestroyMinigenScreen)
        # 
        MinigenMode = IntVar(0)
        mgb1 = Radiobutton(minigenwindow, text="Sine", variable=MinigenMode, value=0, command=BSendMG )
        mgb1.grid(row=1, column=0, sticky=W)
        mgb2 = Radiobutton(minigenwindow, text="Triangle", variable=MinigenMode, value=2, command=BSendMG )
        mgb2.grid(row=1, column=1, sticky=W)
        mgb3 = Radiobutton(minigenwindow, text="Square", variable=MinigenMode, value=40, command=BSendMG )
        mgb3.grid(row=2, column=0, sticky=W)
        mgb4 = Radiobutton(minigenwindow, text="Square/2", variable=MinigenMode, value=32, command=BSendMG )
        mgb4.grid(row=2, column=1, sticky=W)
        f0lab = Label(minigenwindow, text="Mclk in MHz")
        f0lab.grid(row=3, column=0, columnspan=1, sticky=W)
        MinigenFclk = Entry(minigenwindow, width=5)
        MinigenFclk.grid(row=3, column=1, sticky=W, padx=6)
        MinigenFclk.delete(0,"end")
        MinigenFclk.insert(0,16)
        f1lab = Label(minigenwindow, text="Output Freq, Hz")
        f1lab.grid(row=4, column=0, columnspan=1, sticky=W)
        MinigenFout = Entry(minigenwindow, width=8)
        MinigenFout.grid(row=4, column=1, sticky=W)
        MinigenFout.bind('<MouseWheel>', onMiniGenScroll)
        MinigenFout.delete(0,"end")
        MinigenFout.insert(0,100)
        bsn1 = Button(minigenwindow, text='UpDate', command=BSendMG)
        bsn1.grid(row=5, column=0, sticky=W, pady=4)
        dismissmgbutton = Button(minigenwindow, text="Dismiss", command=DestroyMinigenScreen)
        dismissmgbutton.grid(row=5, column=1, sticky=W, pady=4)
#
def DestroyMinigenScreen():
    global minigenwindow, MinigenScreenStatus
    
    MinigenScreenStatus.set(0)
    minigenwindow.destroy()
#
def onMiniGenScroll(event):
    # global ETSStatus, ETSDisp
    onTextScroll(event)
    BSendMG()
#
def DA1ShiftOut(D1Value, D2Value):
    global Dig0, Dig1, Dig2, Dig3, logic, ctx
    
    Dig0.attrs["direction"].value = 'out'
    Dig1.attrs["direction"].value = 'out'
    Dig2.attrs["direction"].value = 'out'
    Dig3.attrs["direction"].value = 'out'
    
    binstr = bin(D1Value)
    binlen = len(binstr)
    data1str = binstr[2:binlen]
    datalen = len(data1str)
    if datalen < 16:
       data1str = str.rjust(data1str , 16 , '0')
       datalen = len(data1str)
    #
    binstr = bin(D2Value)
    binlen = len(binstr)
    data2str = binstr[2:binlen]
    datalen = len(data2str)
    if datalen < 16:
       data2str = str.rjust(data2str , 16 , '0')
       datalen = len(data2str)
    # sync --> PIO 0
    # D0 --> PIO 1
    # D1 --> PIO 2
    # SCLK --> PIO 3
    i = 1
#
    Dig0.attrs["raw"].value = '0' # sync to 0
    while i < datalen+1:
    # sending 0x50 = set to 0, 0x51 = set to 1
        D1code = int(data1str[i-1])
        D2code = int(data2str[i-1])
        Dig1.attrs["raw"].value = str(D1code) # , 1, 0, 0, 0, 100) # data 0 bit
        Dig2.attrs["raw"].value = str(D2code) # , 2, 0, 0, 0, 100) # data 1 bit
        Dig3.attrs["raw"].value = '1' # set PI3 sclk to 1
        Dig3.attrs["raw"].value = '0' # set PI3 sclk to 0
        Dig3.attrs["raw"].value = '1' # set PI3 sclk to 1
        i = i + 1
    Dig0.attrs["raw"].value = '1' # sync to 1
#   
def BSendDA1():
    global DAC1Entry, DAC2Entry, DAC3Entry, DAC4Entry, REFEntry
    
    try:
        RefValue = float(eval(REFEntry.get()))
    except:
        RefValue = 3.3
    try:
        D1Value = float(eval(DAC1Entry.get()))
    except:
        D1Value = 0.0129
    D1Code = int((D1Value/RefValue)*255)
    if D1Code > 255:
        D1Code = 255
    D1Code = D1Code + 0x2000
    try:
        D2Value = float(eval(DAC2Entry.get()))
    except:
        D2Value = 0.0129
    D2Code = int((D2Value/RefValue)*255)
    if D2Code > 255:
        D2Code = 255
    D2Code = D2Code + 0x2400
    try:
        D3Value = float(eval(DAC3Entry.get()))
    except:
        D3Value = 0.0129
    D3Code = int((D3Value/RefValue)*255)
    if D3Code > 255:
        D3Code = 255
    D3Code = D3Code + 0x2000
    try:
        D4Value = float(eval(DAC4Entry.get()))
    except:
        D4Value = 0.0129
    D4Code = int((D4Value/RefValue)*255)
    if D4Code > 255:
        D4Code = 255
    D4Code = D4Code + 0x2400
    #
    DA1ShiftOut(D1Code, D3Code)
    DA1ShiftOut(D2Code, D4Code)

def MakeDA1Window():
    global da1window, DA1ScreenStatus, DAC1Entry, DAC2Entry, DAC3Entry, DAC4Entry
    global REFEntry, RevDate
    
    if DA1ScreenStatus.get() == 0:
        DA1ScreenStatus.set(1)
        da1window = Toplevel()
        da1window.title("DA1 PMOD 2.0 " + RevDate)
        da1window.resizable(FALSE,FALSE)
        da1window.protocol("WM_DELETE_WINDOW", DestroyDA1Screen)
#
        d1lab = Label(da1window, text="DAC A1 output")
        d1lab.grid(row=0, column=0, columnspan=1, sticky=W)
        DAC1Entry = Entry(da1window, width=5)
        DAC1Entry.grid(row=0, column=1, sticky=W)
        DAC1Entry.delete(0,"end")
        DAC1Entry.insert(0,0)
        d2lab = Label(da1window, text="DAC B1 output")
        d2lab.grid(row=1, column=0, columnspan=1, sticky=W)
        DAC2Entry = Entry(da1window, width=5)
        DAC2Entry.grid(row=1, column=1, sticky=W)
        DAC2Entry.delete(0,"end")
        DAC2Entry.insert(0,0)

        d3lab = Label(da1window, text="DAC A2 output")
        d3lab.grid(row=2, column=0, columnspan=1, sticky=W)
        DAC3Entry = Entry(da1window, width=5)
        DAC3Entry.grid(row=2, column=1, sticky=W)
        DAC3Entry.delete(0,"end")
        DAC3Entry.insert(0,0)

        d4lab = Label(da1window, text="DAC B2 output")
        d4lab.grid(row=3, column=0, columnspan=1, sticky=W)
        DAC4Entry = Entry(da1window, width=5)
        DAC4Entry.grid(row=3, column=1, sticky=W)
        DAC4Entry.delete(0,"end")
        DAC4Entry.insert(0,0)

        d5lab = Label(da1window, text="Reference V")
        d5lab.grid(row=4, column=0, columnspan=1, sticky=W)
        REFEntry = Entry(da1window, width=5)
        REFEntry.grid(row=4, column=1, sticky=W)
        REFEntry.delete(0,"end")
        REFEntry.insert(0,3.3)

        bsn1 = Button(da1window, text='UpDate', style="W7.TButton", command=BSendDA1)
        bsn1.grid(row=5, column=0, sticky=W)
        dismissdabutton = Button(da1window, text="Dismiss", style="W8.TButton", command=DestroyDA1Screen)
        dismissdabutton.grid(row=5, column=1, sticky=W, pady=4)

def DestroyDA1Screen():
    global da1window, DA1ScreenStatus
    
    DA1ScreenStatus.set(0)
    da1window.destroy()

def DigPotShiftOut(DValue):
    global Dig0, Dig1, Dig2, Dig3, logic, ctx, SingleDualPot

    Dig0.attrs["direction"].value = 'out'
    Dig1.attrs["direction"].value = 'out'
    Dig2.attrs["direction"].value = 'out'
    Dig3.attrs["direction"].value = 'out'

    binstr = bin(DValue)
    binlen = len(binstr)
    datastr = binstr[2:binlen]
    datalen = len(datastr)
    if SingleDualPot.get() == 0: # send 10 bits of data
        if datalen < 10:
           datastr = str.rjust(datastr , 10 , '0')
           datalen = len(datastr)
    if SingleDualPot.get() == 1: # send 8 bits of data
        if datalen < 8:
           datastr = str.rjust(datastr , 8 , '0')
           datalen = len(datastr)
    if SingleDualPot.get() == 2: # send 8 bits of data
        if datalen < 8:
           datastr = str.rjust(datastr , 8 , '0')
           datalen = len(datastr)
    i = 1
    Dig3.attrs["raw"].value = '0' # 3 # clock to 0
    Dig0.attrs["raw"].value = '0' # CS to 0
    while i < datalen+1:
    # CS --> PIO 0
    # D0 --> PIO 1
    # D1 --> PIO 2
    # SCLK --> PIO 3
        D1code = int(datastr[i-1])
        Dig1.attrs["raw"].value = str(D1code) # 1 # data bit
        Dig3.attrs["raw"].value = '1' # clock to 1
        Dig3.attrs["raw"].value = '0' # clock to 0
        i = i + 1
    Dig0.attrs["raw"].value = '1' # CS to 1
    #
def DigPotSend(Temp):
    global DigPot1, DigPot2, DigPot3, DigPot4, SendPot1, SendPot2, SendPot3, SendPot4
    global SingleDualPot
    
    if SingleDualPot.get() == 0 or SingleDualPot.get() == 1:
        NumTaps = 255
    if SingleDualPot.get() == 2:
        NumTaps = 63
    try:
        DValue1 = DigPot1.get()
        if DValue1 > NumTaps:
            DValue1 = NumTaps
    except:
        DValue1 = 0
    try:
        DValue2 = DigPot2.get()
        if DValue2 > NumTaps:
            DValue2 = NumTaps
    except:
        DValue2 = 0
    try:
        DValue3 = DigPot3.get()
        if DValue3 > NumTaps:
            DValue3 = NumTaps
    except:
        DValue3 = 0
    try:
        DValue4 = DigPot4.get()
        if DValue4 > NumTaps:
            DValue4 = NumTaps
    except:
        DValue4 = 0
    if SendPot1.get() > 0:
        DigPotShiftOut(DValue1)
    if SendPot2.get() > 0:
        DigPotShiftOut(DValue2+NumTaps+1)
    if SendPot3.get() > 0:
        DigPotShiftOut(DValue3+2*(NumTaps+1))
    if SendPot4.get() > 0:
        DigPotShiftOut(DValue4+3*(NumTaps+1))

def UpdatePotSlider():
    global SingleDualPot, DPotlabel, DigPot1, DigPot2, DigPot3, DigPot4

    if SingleDualPot.get() == 0 or SingleDualPot.get() == 1:
        DPotlabel.config(text="Enter number from 0 to 255")
        DigPot1.config(from_=0, to=255, length=256)
        DigPot2.config(from_=0, to=255, length=256)
        DigPot3.config(from_=0, to=255, length=256)
        DigPot4.config(from_=0, to=255, length=256)
    if SingleDualPot.get() == 2:
        DPotlabel.config(text="Enter number from 0 to 63")
        DigPot1.config(from_=0, to=63, length=64)
        DigPot2.config(from_=0, to=63, length=64)
        DigPot3.config(from_=0, to=63, length=64)
        DigPot4.config(from_=0, to=63, length=64)
    
def MakeDigPotWindow(): # set up for single, dual or quad, digital pots
    global digpotwindow, DigPotScreenStatus, DigPot1, DigPot2, DigPot3, DigPot4, RevDate
    global SendPot1, SendPot2, SendPot3, SendPot4, SingleDualPot
    global DPotlabel, DigPot1, DigPot2, DigPot3, DigPot4

    if DigPotScreenStatus.get() == 0:
        DigPotScreenStatus.set(1)
        digpotwindow = Toplevel()
        digpotwindow.title("Digital Potentiometer" + RevDate)
        digpotwindow.resizable(FALSE,FALSE)
        digpotwindow.protocol("WM_DELETE_WINDOW", DestroyDigPotScreen)
        #
        SendPot1 = IntVar(0)
        SendPot1.set(1)
        SendPot2 = IntVar(0)
        SendPot2.set(1)
        SendPot3 = IntVar(0)
        SendPot3.set(0)
        SendPot4 = IntVar(0)
        SendPot4.set(0)
        DPotlabel = Label(digpotwindow,text="Enter number from 0 to 255", style="A12B.TLabel")
        DPotlabel.grid(row=0, column=0, columnspan=3, sticky=W)
        
        SingleDualPot = IntVar(0)
        SingleDualPot.set(0)
        CompMenu = Menubutton(digpotwindow, text="Sel Comp.", style="W7.TButton")
        CompMenu.menu = Menu(CompMenu, tearoff = 0 )
        CompMenu["menu"] = CompMenu.menu
        CompMenu.menu.add_radiobutton(label="AD840X", variable=SingleDualPot, value=0, command=UpdatePotSlider)
        CompMenu.menu.add_radiobutton(label="AD5160", variable=SingleDualPot, value=1, command=UpdatePotSlider)
        CompMenu.menu.add_radiobutton(label="AD5203", variable=SingleDualPot, value=2, command=UpdatePotSlider)
        CompMenu.grid(row=1, column=0, columnspan=2, sticky=W)
        lab1 = Checkbutton(digpotwindow,text="Pot 1", variable=SendPot1)
        lab1.grid(row=2, column=0, sticky=W)
        DigPot1 = Scale(digpotwindow, from_=0, to=255, orient=HORIZONTAL, command=DigPotSend, length=256)
        DigPot1.grid(row=3, column=0, columnspan=3, sticky=W)
        lab2 = Checkbutton(digpotwindow,text="Pot 2", variable=SendPot2)
        lab2.grid(row=4, column=0, sticky=W)
        DigPot2 = Scale(digpotwindow, from_=0, to=255, orient=HORIZONTAL, command=DigPotSend, length=256)
        DigPot2.grid(row=5, column=0, columnspan=3, sticky=W)
        lab3 = Checkbutton(digpotwindow,text="Pot 3", variable=SendPot3)
        lab3.grid(row=6, column=0, sticky=W)
        DigPot3 = Scale(digpotwindow, from_=0, to=255, orient=HORIZONTAL, command=DigPotSend, length=256)
        DigPot3.grid(row=7, column=0, columnspan=3, sticky=W)
        lab4 = Checkbutton(digpotwindow,text="Pot 4", variable=SendPot4)
        lab4.grid(row=8, column=0, sticky=W)
        DigPot4 = Scale(digpotwindow, from_=0, to=255, orient=HORIZONTAL, command=DigPotSend, length=256)
        DigPot4.grid(row=9, column=0, columnspan=3, sticky=W)
        dismissdpbutton = Button(digpotwindow, text="Dismiss", style="W8.TButton", command=DestroyDigPotScreen)
        dismissdpbutton.grid(row=10, column=0, sticky=W, pady=4)

def DestroyDigPotScreen():
    global digpotwindow, DigPotScreenStatus
    
    DigPotScreenStatus.set(0)
    digpotwindow.destroy()

def BSendGS():
    global serialwindow, GenericSerialStatus, SCLKPort, SDATAPort, SLATCHPort, SLatchPhase
    global NumBitsEntry, DataBitsEntry, SerDirection
    global Dig0, Dig1, Dig2, Dig3, logic, ctx

    Dig0.attrs["direction"].value = 'out'
    Dig1.attrs["direction"].value = 'out'
    Dig2.attrs["direction"].value = 'out'
    Dig3.attrs["direction"].value = 'out'

    try:
        DValue = int(eval(DataBitsEntry.get()))
        if DValue < 0:
            DValue = 0
    except:
        DValue = 0
    try:
        NumBits = int(NumBitsEntry.get())
        if NumBits < 1:
            NumBits = 1
    except:
        NumBits = 8
    binstr = bin(DValue)
    binlen = len(binstr)
    datastr = binstr[2:binlen]
    datalen = len(datastr)
    if datalen < NumBits:
       datastr = str.rjust(datastr , NumBits , '0')
       datalen = len(datastr)
    if SLatchPhase.get() == 0:
        LatchInt = 0x50
        LatchEnd = 0x51
    else:
        LatchInt = 0x51
        LatchEnd = 0x50
    DevOne.ctrl_transfer(0x40, 0x50, SCLKPort.get(), 0, 0, 0, 100) # clock to 0
    DevOne.ctrl_transfer(0x40, LatchInt, SLATCHPort.get(), 0, 0, 0, 100) # CS to 0
    i = 1
    while i < datalen+1:
        if SerDirection.get() == 1: # for MSB first
            D1code = 0x50 + int(datastr[datalen-i]) # 0x50 = set to 0, 0x51 = set to 1
        else:
            D1code = 0x50 + int(datastr[i-1]) # for LSB first
        DevOne.ctrl_transfer(0x40, D1code, SDATAPort.get(), 0, 0, 0, 100) # data bit
        DevOne.ctrl_transfer(0x40, 0x51, SCLKPort.get(), 0, 0, 0, 100) # clock to 1
        DevOne.ctrl_transfer(0x40, 0x50, SCLKPort.get(), 0, 0, 0, 100) # clock to 0
        i = i + 1
    DevOne.ctrl_transfer(0x40, LatchEnd, SLATCHPort.get(), 0, 0, 0, 100) # CS to 1
    
def MakeGenericSerialWindow():
    global serialwindow, GenericSerialStatus, SCLKPort, SDATAPort, SLATCHPort, SLatchPhase
    global NumBitsEntry, DataBitsEntry, SerDirection

    if GenericSerialStatus.get() == 0:
        GenericSerialStatus.set(1)
        serialwindow = Toplevel()
        serialwindow.title("Generic Serial Output " + RevDate)
        serialwindow.resizable(FALSE,FALSE)
        serialwindow.protocol("WM_DELETE_WINDOW", DestroyGenericSerialScreen)
        #
        SCLKPort = IntVar(0)
        SCLKPort.set(3)
        SDATAPort = IntVar(0)
        SDATAPort.set(1)
        SLATCHPort = IntVar(0)
        SLatchPhase = IntVar(0)
        SerDirection = IntVar(0)
        label = Label(serialwindow,text="Enter number of Bits")
        label.grid(row=1, column=0, columnspan=2, sticky=W)
        NumBitsEntry = Entry(serialwindow, width=3)
        NumBitsEntry.grid(row=1, column=2, sticky=W)
        NumBitsEntry.delete(0,"end")
        NumBitsEntry.insert(0,8)
        #
        label2 = Label(serialwindow,text="Enter Data Word")
        label2.grid(row=2, column=0, columnspan=1, sticky=W)
        DataBitsEntry = Entry(serialwindow, width=10)
        DataBitsEntry.grid(row=2, column=1, columnspan=3, sticky=W)
        DataBitsEntry.delete(0,"end")
        DataBitsEntry.insert(0,0)
        #
        label3 = Label(serialwindow,text="SCLK PI/O Port ")
        label3.grid(row=3, column=0, columnspan=1, sticky=W)
        sclk1 = Radiobutton(serialwindow, text="0", variable=SCLKPort, value=0)
        sclk1.grid(row=3, column=1, sticky=W)
        sclk2 = Radiobutton(serialwindow, text="1", variable=SCLKPort, value=1)
        sclk2.grid(row=3, column=2, sticky=W)
        sclk3 = Radiobutton(serialwindow, text="2", variable=SCLKPort, value=2)
        sclk3.grid(row=3, column=3, sticky=W)
        sclk4 = Radiobutton(serialwindow, text="3", variable=SCLKPort, value=3)
        sclk4.grid(row=3, column=4, sticky=W)
        #
        label4 = Label(serialwindow,text="SData PI/O Port ")
        label4.grid(row=4, column=0, columnspan=1, sticky=W)
        sdat1 = Radiobutton(serialwindow, text="0", variable=SDATAPort, value=0)
        sdat1.grid(row=4, column=1, sticky=W)
        sdat2 = Radiobutton(serialwindow, text="1", variable=SDATAPort, value=1)
        sdat2.grid(row=4, column=2, sticky=W)
        sdat3 = Radiobutton(serialwindow, text="2", variable=SDATAPort, value=2)
        sdat3.grid(row=4, column=3, sticky=W)
        sdat4 = Radiobutton(serialwindow, text="3", variable=SDATAPort, value=3)
        sdat4.grid(row=4, column=4, sticky=W)
        #
        label5 = Label(serialwindow,text="Latch PI/O Port ")
        label5.grid(row=5, column=0, columnspan=1, sticky=W)
        slth1 = Radiobutton(serialwindow, text="0", variable=SLATCHPort, value=0)
        slth1.grid(row=5, column=1, sticky=W)
        slth2 = Radiobutton(serialwindow, text="1", variable=SLATCHPort, value=1)
        slth2.grid(row=5, column=2, sticky=W)
        slth3 = Radiobutton(serialwindow, text="2", variable=SLATCHPort, value=2)
        slth3.grid(row=5, column=3, sticky=W)
        slth4 = Radiobutton(serialwindow, text="3", variable=SLATCHPort, value=3)
        slth4.grid(row=5, column=4, sticky=W)
        #
        label6 = Label(serialwindow,text="Latch Phase ")
        label6.grid(row=6, column=0, columnspan=1, sticky=W)
        sph1 = Radiobutton(serialwindow, text="0", variable=SLatchPhase, value=0)
        sph1.grid(row=6, column=1, sticky=W)
        sph2 = Radiobutton(serialwindow, text="1", variable=SLatchPhase, value=1)
        sph2.grid(row=6, column=2, sticky=W)
        #
        sdir1 = Radiobutton(serialwindow, text="LSB First", variable=SerDirection, value=0 )
        sdir1.grid(row=7, column=0, sticky=W)
        sdir2 = Radiobutton(serialwindow, text="MSB First", variable=SerDirection, value=1 )
        sdir2.grid(row=7, column=1, columnspan=2, sticky=W)

        bsn1 = Button(serialwindow, text='Send', command=BSendGS)
        bsn1.grid(row=8, column=0, sticky=W)
        dismissgsbutton = Button(serialwindow, text="Dismiss", style="W8.TButton", command=DestroyGenericSerialScreen)
        dismissgsbutton.grid(row=8, column=1, columnspan=2, sticky=W, pady=4)
        
def DestroyGenericSerialScreen():
    global serialwindow, GenericSerialStatus
    
    GenericSerialStatus.set(0)
    serialwindow.destroy()
#
def MakeDBuff():
    global VBuffA, VBuffB, VFilterA, VFilterB

    VFilterA = VBuffA
    VFilterB = VBuffB
#
def MakeDigFiltWindow():
    global digfltwindow, DigFiltStatus, DigBuffA, DigBuffB 
    global DigFiltA, DigFiltB, DifFiltALength, DifFiltBLength, DifFiltAFile, DifFiltBFile

    if DigFiltStatus.get() == 0:
        DigFiltStatus.set(1)
        digfltwindow = Toplevel()
        digfltwindow.title("Digital Filter " + RevDate)
        digfltwindow.resizable(FALSE,FALSE)
        digfltwindow.protocol("WM_DELETE_WINDOW", DestroyDigFiltScreen)
        titlab = Label(digfltwindow,text="Apply Digital Filters ", style="A12B.TLabel")
        titlab.grid(row=0, column=0, sticky=W)
        lab1 = Checkbutton(digfltwindow,text="Filter CH 1", variable=DigFiltA)
        lab1.grid(row=1, column=0, sticky=W)
        labf1 = Checkbutton(digfltwindow,text="Enab Buffer", variable=DigBuffA, command=MakeDBuff)
        labf1.grid(row=2, column=0, sticky=W)
        DifFiltALength = Label(digfltwindow,text="Length = 0 ")
        DifFiltALength.grid(row=3, column=0, sticky=W)
        DifFiltAFile = Label(digfltwindow,text="File Name, none ")
        DifFiltAFile.grid(row=4, column=0, sticky=W)
        lab2 = Checkbutton(digfltwindow,text="Filter CH 2", variable=DigFiltB)
        lab2.grid(row=5, column=0, sticky=W)
        labf2 = Checkbutton(digfltwindow,text="Enab Buffer", variable=DigBuffB, command=MakeDBuff)
        labf2.grid(row=6, column=0, sticky=W)
        DifFiltBLength = Label(digfltwindow,text="Length = 0 ")
        DifFiltBLength.grid(row=7, column=0, sticky=W)
        DifFiltBFile = Label(digfltwindow,text="File Name, none ")
        DifFiltBFile.grid(row=8, column=0, sticky=W)
        cald = Button(digfltwindow, text='Load CH 1 Filter Coef', command=BLoadDFiltA)
        cald.grid(row=9, column=0, sticky=W)
        camath = Button(digfltwindow, text='CH 1 Filter formula', command=BDFiltAMath)
        camath.grid(row=10, column=0, sticky=W)
        cbld = Button(digfltwindow, text='Load CH 2 Filter Coef', command=BLoadDFiltB)
        cbld.grid(row=11, column=0, sticky=W)
        cbmath = Button(digfltwindow, text='CH 2 Filter formula', command=BDFiltBMath)
        cbmath.grid(row=12, column=0, sticky=W)
        #
        dismissdfbutton = Button(digfltwindow, text="Dismiss", style="W8.TButton", command=DestroyDigFiltScreen)
        dismissdfbutton.grid(row=13, column=0, columnspan=1, sticky=W, pady=4)

def DestroyDigFiltScreen():
    global digfltwindow, DigFiltStatus
    
    DigFiltStatus.set(0)
    digfltwindow.destroy()

def BLoadDFiltA():
    global DFiltACoef, digfltwindow, DifFiltALength, DifFiltAFile
# Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=digfltwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=digfltwindow)
        return
    DFiltACoef = []

    for row in csv_f:
        try:
            DFiltACoef.append(float(row[0]))
        except:
            print 'skipping non-numeric row'
    DFiltACoef = numpy.array(DFiltACoef)
    DifFiltALength.config(text = "Length = " + str(int(len(DFiltACoef)))) # change displayed length value
    DifFiltAFile.config(text = "File Name, " + os.path.basename(filename)) # change displayed file name
    CSVFile.close()
#
def BDFiltAMath():
    global DFiltACoef, digfltwindow, DifFiltALength, DifFiltAFile, DigFilterAString
    
    TempString = DigFilterAString
    DigFilterAString = askstring("CH 1 Filter Math Formula", "Current Formula: " + DigFilterAString + "\n\nNew Formula:\n", initialvalue=DigFilterAString, parent=digfltwindow)
    if (DigFilterAString == None):         # If Cancel pressed, then None
        DigFilterAString = TempString
        return
    DFiltACoef = eval(DigFilterAString)
    DFiltACoef = numpy.array(DFiltACoef)
    coefsum = numpy.sum(DFiltACoef)
    DFiltACoef = DFiltACoef / coefsum
    DifFiltALength.config(text = "Length = " + str(int(len(DFiltACoef)))) # change displayed length value
    DifFiltAFile.config(text = "Using Filter 1 formula" ) # change displayed file name
    
def BLoadDFiltB():
    global DFiltBCoef, digfltwindow, DifFiltBLength, DifFiltBFile

# Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=digfltwindow)
    try:
        CSVFile = open(filename)
        csv_f = csv.reader(CSVFile)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=digfltwindow)
        return
    DFiltBCoef = []

    for row in csv_f:
        try:
            DFiltBCoef.append(float(row[0]))
        except:
            print 'skipping non-numeric row'
    DFiltBCoef = numpy.array(DFiltBCoef)
    DifFiltBLength.config(text = "Length = " + str(int(len(DFiltBCoef)))) # change displayed length value
    DifFiltBFile.config(text = "File Name, " + os.path.basename(filename)) # change displayed file name
    CSVFile.close()
#
def BDFiltBMath():
    global DFiltBCoef, digfltwindow, DifFiltBLength, DifFiltBFile, DigFilterBString
    
    TempString = DigFilterBString
    DigFilterBString = askstring("CH 2 Filter Math Formula", "Current Formula: " + DigFilterBString + "\n\nNew Formula:\n", initialvalue=DigFilterBString, parent=digfltwindow)
    if (DigFilterBString == None):         # If Cancel pressed, then None
        DigFilterBString = TempString
        return
    DFiltBCoef = eval(DigFilterBString)
    DFiltBCoef = numpy.array(DFiltBCoef)
    coefsum = numpy.sum(DFiltBCoef)
    DFiltBCoef = DFiltBCoef / coefsum
    DifFiltBLength.config(text = "Length = " + str(int(len(DFiltBCoef)))) # change displayed length value
    DifFiltBFile.config(text = "Using Filter 2 formula" ) # change displayed file name
#
def MakeCommandScreen():
    global commandwindow, CommandStatus, ExecString, LastCommand, RevDate
    
    if CommandStatus.get() == 0:
        CommandStatus.set(1)
        commandwindow = Toplevel()
        commandwindow.title("Command Line " + RevDate)
        commandwindow.resizable(FALSE,FALSE)
        commandwindow.protocol("WM_DELETE_WINDOW", DestroyCommandScreen)
        toplab = Label(commandwindow,text="Command Line Interface ", style="A12B.TLabel")
        toplab.grid(row=0, column=0, columnspan=2, sticky=W)
        cl1 = Label(commandwindow,text="Last command:")
        cl1.grid(row=1, column=0, sticky=W)
        LastCommand = Label(commandwindow,text=" ")
        LastCommand.grid(row=2, column=0, columnspan=4, sticky=W)
        ExecString = Entry(commandwindow, width=40)
        ExecString.bind("<Return>", RExecuteFromString)
        ExecString.grid(row=3, column=0, columnspan=4, sticky=W)
        ExecString.delete(0,"end")
        ExecString.insert(0,"global ; ")
        executeclbutton = Button(commandwindow, text="Execute", style="W8.TButton", command=BExecuteFromString)
        executeclbutton.grid(row=4, column=0, sticky=W, pady=8)
        #
        cmddismissclbutton = Button(commandwindow, text="Dismiss", style="W8.TButton", command=DestroyCommandScreen)
        cmddismissclbutton.grid(row=4, column=1, sticky=W, pady=7)
        
def DestroyCommandScreen():
    global commandwindow, CommandStatus
    
    CommandStatus.set(0)
    commandwindow.destroy()

def RExecuteFromString(temp):

    BExecuteFromString()
    
def BExecuteFromString(): #
    global ExecString, LastCommand

    try:
        exec( ExecString.get() )
        LastCommand.config(text = ExecString.get() ) # change displayed last command
    except:
        LastCommand.config(text = "Syntax Error Encountered" ) # change displayed last command
        return()
#
def CAresize(event):
    global ca, GRW, XOL, GRH, Y0T, CANVASwidth, CANVASheight
    global Ymin, Ymax, Xmin, Xmax
    
    CANVASwidth = event.width
    CANVASheight = event.height
    GRW = CANVASwidth - (2 * X0L) # new grid width
    GRH = CANVASheight - 80     # new grid height
    Ymin = Y0T                  # Minimum position of time grid (top)
    Ymax = Y0T + GRH            # Maximum position of time grid (bottom)
    Xmin = X0L                  # Minimum position of time grid (left)
    Xmax = X0L + GRW            # Maximum position of time grid (right)
    UpdateTimeAll()
#
def UpdateMeasureScreen():
    global ChaLab1, ChaLab12, ChaLab3, ChaLab4, ChaLab5, ChaLab6
    global ChaValue1, ChaValue2, ChaValue3, ChaValue4, ChaValue5, ChaValue6
    global ChbLab1, ChbLab12, ChbLab3, ChbLab4, ChbLab5, ChbLab6
    global ChbValue1, ChbValue2, ChbValue3, ChbValue4, ChbValue5, ChbValue6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString1))
    ChaValue1.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString2))
    ChaValue2.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString3))
    ChaValue3.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString4))
    ChaValue4.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString5))
    ChaValue5.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChaMeasString6))
    ChaValue6.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString1))
    ChbValue1.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString2))
    ChbValue2.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString3))
    ChbValue3.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString4))
    ChbValue4.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString5))
    ChbValue5.config(text = ValueText)
    ValueText = ' {0:.4f} '.format(eval(ChbMeasString6))
    ChbValue6.config(text = ValueText)
#
def MakeMeasureScreen():
    global measurewindow, MeasureStatus
    global ChaLab1, ChaLab12, ChaLab3, ChaLab4, ChaLab5, ChaLab6
    global ChaValue1, ChaValue2, ChaValue3, ChaValue4, ChaValue5, ChaValue6
    global ChbLab1, ChbLab12, ChbLab3, ChbLab4, ChbLab5, ChbLab6
    global ChbValue1, ChbValue2, ChbValue3, ChbValue4, ChbValue5, ChbValue6
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    
    if MeasureStatus.get() == 0:
        MeasureStatus.set(1)
        measurewindow = Toplevel()
        measurewindow.title("Measurements " + RevDate)
        measurewindow.resizable(FALSE,FALSE)
        measurewindow.protocol("WM_DELETE_WINDOW", DestroyMeasureScreen)
        toplab = Label(measurewindow,text="Measurements ", style="A12B.TLabel")
        toplab.grid(row=0, column=0, columnspan=2, sticky=W)
        ChaLab1 = Label(measurewindow,text=ChaLableSrring1, style="A10B.TLabel")
        ChaLab1.grid(row=1, column=0, columnspan=1, sticky=W)
        ChaValue1 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue1.grid(row=1, column=1, columnspan=1, sticky=W)
        ChaLab2 = Label(measurewindow,text=ChaLableSrring2, style="A10B.TLabel")
        ChaLab2.grid(row=1, column=2, columnspan=1, sticky=W)
        ChaValue2 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue2.grid(row=1, column=3, columnspan=1, sticky=W)
        ChaLab3 = Label(measurewindow,text=ChaLableSrring3, style="A10B.TLabel")
        ChaLab3.grid(row=2, column=0, columnspan=1, sticky=W)
        ChaValue3 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue3.grid(row=2, column=1, columnspan=1, sticky=W)
        ChaLab4 = Label(measurewindow,text=ChaLableSrring4, style="A10B.TLabel")
        ChaLab4.grid(row=2, column=2, columnspan=1, sticky=W)
        ChaValue4 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue4.grid(row=2, column=3, columnspan=1, sticky=W)
        ChaLab5 = Label(measurewindow,text=ChaLableSrring5, style="A10B.TLabel")
        ChaLab5.grid(row=3, column=0, columnspan=1, sticky=W)
        ChaValue5 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue5.grid(row=3, column=1, columnspan=1, sticky=W)
        ChaLab6 = Label(measurewindow,text=ChaLableSrring6, style="A10B.TLabel")
        ChaLab6.grid(row=3, column=2, columnspan=1, sticky=W)
        ChaValue6 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChaValue6.grid(row=3, column=3, columnspan=1, sticky=W)
        #
        ChbLab1 = Label(measurewindow,text=ChbLableSrring1, style="A10B.TLabel")
        ChbLab1.grid(row=4, column=0, columnspan=1, sticky=W)
        ChbValue1 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue1.grid(row=4, column=1, columnspan=1, sticky=W)
        ChbLab2 = Label(measurewindow,text=ChbLableSrring2, style="A10B.TLabel")
        ChbLab2.grid(row=4, column=2, columnspan=1, sticky=W)
        ChbValue2 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue2.grid(row=4, column=3, columnspan=1, sticky=W)
        ChbLab3 = Label(measurewindow,text=ChbLableSrring3, style="A10B.TLabel")
        ChbLab3.grid(row=5, column=0, columnspan=1, sticky=W)
        ChbValue3 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue3.grid(row=5, column=1, columnspan=1, sticky=W)
        ChbLab4 = Label(measurewindow,text=ChbLableSrring4, style="A10B.TLabel")
        ChbLab4.grid(row=5, column=2, columnspan=1, sticky=W)
        ChbValue4 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue4.grid(row=5, column=3, columnspan=1, sticky=W)
        ChbLab5 = Label(measurewindow,text=ChbLableSrring5, style="A10B.TLabel")
        ChbLab5.grid(row=6, column=0, columnspan=1, sticky=W)
        ChbValue5 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue5.grid(row=6, column=1, columnspan=1, sticky=W)
        ChbLab6 = Label(measurewindow,text=ChbLableSrring6, style="A10B.TLabel")
        ChbLab6.grid(row=6, column=2, columnspan=1, sticky=W)
        ChbValue6 = Label(measurewindow,text="0.0000", style="A10B.TLabel")
        ChbValue6.grid(row=6, column=3, columnspan=1, sticky=W)
#
def DestroyMeasureScreen():
    global measurewindow, MeasureStatus
    
    MeasureStatus.set(0)
    measurewindow.destroy()
#
def MakeOhmWindow():
    global OhmDisp, OhmStatus, ohmwindow, RevDate, OhmA0, OhmRunStatus
    global CHATestVEntry, CHATestREntry
    
    if OhmStatus.get() == 0:
        OhmStatus.set(1)
        OhmDisp.set(1)
        ohmwindow = Toplevel()
        ohmwindow.title("DC Ohmmeter " + RevDate)
        ohmwindow.resizable(FALSE,FALSE)
        ohmwindow.protocol("WM_DELETE_WINDOW", DestroyOhmScreen)
        frame1 = Frame(ohmwindow, borderwidth=5, relief=RIDGE)
        frame1.grid(row=0, column=0, sticky=W)
        #
        buttons = Frame( frame1 )
        buttons.grid(row=0, column=0, sticky=W)
        rb1 = Radiobutton(buttons, text="Stop", style="Stop.TRadiobutton", variable=OhmRunStatus, value=0 )
        rb1.pack(side=LEFT)
        rb2 = Radiobutton(buttons, text="Run", style="Run.TRadiobutton", variable=OhmRunStatus, value=1 )
        rb2.pack(side=LEFT)
        #
        OhmA0 = Label(frame1, style="A16B.TLabel")
        OhmA0.grid(row=1, column=0, columnspan=2, sticky=W)
        OhmA0.config(text = "0.000 Ohms")
        #
        TestVA = Frame( frame1 )
        TestVA.grid(row=3, column=0, sticky=W)
        chatestvlab = Label(TestVA, text="Test Voltage", style="A10B.TLabel")
        chatestvlab.pack(side=LEFT)
        CHATestVEntry = Entry(TestVA, width=6) #
        CHATestVEntry.pack(side=LEFT)
        CHATestVEntry.bind('<MouseWheel>', onTextScroll)
        CHATestVEntry.delete(0,"end")
        CHATestVEntry.insert(0,5.0)
        #
        TestRA = Frame( frame1 )
        TestRA.grid(row=5, column=0, sticky=W)
        chatestrlab = Label(TestRA, text="Known Res", style="A10B.TLabel")
        chatestrlab.pack(side=LEFT)
        CHATestREntry = Entry(TestRA, width=6) #
        CHATestREntry.pack(side=LEFT)
        CHATestREntry.bind('<MouseWheel>', onTextScroll)
        CHATestREntry.delete(0,"end")
        CHATestREntry.insert(0,50.0)
        #
        ohmdismissclbutton = Button(frame1, text="Dismiss", style="W8.TButton", command=DestroyOhmScreen)
        ohmdismissclbutton.grid(row=6, column=0, sticky=W, pady=7)
        OhmCheckBox()
#
def DestroyOhmScreen():
    global ohmwindow, OhmStatus, OhmDisp
    
    OhmStatus.set(0)
    OhmDisp.set(0)
    OhmCheckBox()
    ohmwindow.destroy()
#
def BnegUS(temp):
    global negUSEntry, NegUS, ctx, ad5627

    SetNegUS()
#
def BplusUS(temp):
    global plusUSEntry, PlusUS, ctx, ad5627

    SetPosUS()
#
def BPlusOnOff():
    global PlusUSEnab, PlusUS, ctx, ad5627, plusUSlab

    if PlusUSEnab.get() > 0:
        PlusUS.attrs["powerdown"].value = '0' # power up positive user supply
        SetPosUS()
        plusUSlab.config( style="Enab.TCheckbutton")
    else:
        PlusUS.attrs["powerdown"].value = '1' # power down positive user supply
        plusUSlab.config( style="Disab.TCheckbutton")
#
def BNegOnOff():
    global NegUUEnab, NegUS, ctx, ad5627, negUSlab

    if NegUSEnab.get() > 0:
        NegUS.attrs["powerdown"].value = '0' # power up negative user supply
        SetNegUS()
        negUSlab.config( style="Enab.TCheckbutton")
    else:
        NegUS.attrs["powerdown"].value = '1' # power down negative user supply
        negUSlab.config( style="Disab.TCheckbutton")
#
def SetNegUS():
    global negUSEntry, NegUS, NegVolts, ctx, ad5627, NegUS_RB

    if NegUSEnab.get() > 0:
        NegUS.attrs["powerdown"].value = '0' # power up negative user supply
    else:
        NegUS.attrs["powerdown"].value = '1' # power down negative user supply
    try:
        NegVolts = float(negUSEntry.get())
        if NegVolts > 0 :
            NegVolts = 0.0
            negUSEntry.delete(0,END)
            negUSEntry.insert(0, NegVolts)
        if NegVolts < -5.0:
            NegVolts = -5.0
            negUSEntry.delete(0,END)
            negUSEntry.insert(0, NegVolts)
    except:
        negUSEntry.delete(0,END)
        negUSEntry.insert(0, NegVolts)
    data = abs(int(4095*NegVolts/6.14))
    NegUS.attrs["raw"].value = str(data) # set value to volts
# Read back scaled values for user power supplies seem to be 500 too big?
    negrb_val = float(NegUS_RB.attrs['scale'].value) * float(NegUS_RB.attrs['raw'].value)/495.5
    negrb_str = ' {0:.3f} '.format(negrb_val * -1)
    negUSrb.configure(text=negrb_str)
#
def SetPosUS():
    global plusUSEntry, PlusVolts, PlusUS, ctx, ad5627, PlusUS_RB, plusUSrb
    
    if PlusUSEnab.get() > 0:
        PlusUS.attrs["powerdown"].value = '0' # power up positive user supply
    else:
        PlusUS.attrs["powerdown"].value = '1'
    try:
        PlusVolts = float(plusUSEntry.get())
        if PlusVolts < 0 :
            PlusVolts = 0.0
            plusUSEntry.delete(0,END)
            plusUSEntry.insert(0, PlusVolts)
        if PlusVolts > 5.0:
            PlusVolts = 5.0
            plusUSEntry.delete(0,END)
            plusUSEntry.insert(0, PlusVolts)
    except:
        plusUSEntry.delete(0,END)
        plusUSEntry.insert(0, PlusVolts)
    data = abs(int(4095*PlusVolts/6.05))
    PlusUS.attrs["raw"].value = str(data) # set positve user supply voltage
# Read back scaled values for user power supplies seem to be 500 too big?
    posrb_val = float(PlusUS_RB.attrs['scale'].value) * float(PlusUS_RB.attrs['raw'].value)/498
    posrb_str = ' {0:.3f} '.format(posrb_val)
    plusUSrb.configure(text=posrb_str)
#)
def scrollPlusUS(temp):

    onTextScroll(temp)
    SetPosUS()
#
def scrollNegUS(temp):

    onTextScroll(temp)
    SetNegUS()
#
def Settingsscroll(event):
    onTextScroll(event)
    SettingsUpdate()
#
def MakeSettingsMenu():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, SettingsDisp, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon

    if SettingsStatus.get() == 0:
        Settingswindow = Toplevel()
        Settingswindow.title("Settings" + RevDate)
        Settingswindow.resizable(FALSE,FALSE)
        Settingswindow.protocol("WM_DELETE_WINDOW", DestroySettings)
        frame1 = Frame(Settingswindow, borderwidth=5, relief=RIDGE)
        frame1.grid(row=0, column=0, sticky=W)
        #
        zstlab = Label(frame1, text="FFT Zero Stuffing", style= "A10B.TLabel")
        zstlab.grid(row=0, column=0, sticky=W)
        zstMode = Frame( frame1 )
        zstMode.grid(row=0, column=1, sticky=W)
        ZSTuff = Entry(zstMode, width=4)
        ZSTuff.bind('<MouseWheel>', Settingsscroll)
        ZSTuff.bind('<Key>', onTextKey)
        ZSTuff.pack(side=RIGHT)
        ZSTuff.delete(0,"end")
        ZSTuff.insert(0,ZEROstuffing.get())
        #
        Avglab = Label(frame1, text="Number Traces to Average", style= "A10B.TLabel")
        Avglab.grid(row=1, column=0, sticky=W)
        AvgMode = Frame( frame1 )
        AvgMode.grid(row=1, column=1, sticky=W)
        TAvg = Entry(AvgMode, width=4)
        TAvg.bind('<MouseWheel>', Settingsscroll)
        TAvg.bind('<Key>', onTextKey)
        TAvg.pack(side=RIGHT)
        TAvg.delete(0,"end")
        TAvg.insert(0,TRACEaverage.get())
        #
        HarMlab = Label(frame1, text="Number of Harmonic Markers", style= "A10B.TLabel")
        HarMlab.grid(row=2, column=0, sticky=W)
        HarMMode = Frame( frame1 )
        HarMMode.grid(row=2, column=1, sticky=W)
        HarMon = Entry(HarMMode, width=4)
        HarMon.bind('<MouseWheel>', Settingsscroll)
        HarMon.bind('<Key>', onTextKey)
        HarMon.pack(side=RIGHT)
        HarMon.delete(0,"end")
        HarMon.insert(0,HarmonicMarkers.get())
        #
        Vdivlab = Label(frame1, text="Number Vertical Div (SA, Bode)", style= "A10B.TLabel")
        Vdivlab.grid(row=3, column=0, sticky=W)
        VdivMode = Frame( frame1 )
        VdivMode.grid(row=3, column=1, sticky=W)
        VDivE = Entry(VdivMode, width=4)
        VDivE.bind('<MouseWheel>', Settingsscroll)
        VDivE.bind('<Key>', onTextKey)
        VDivE.pack(side=RIGHT)
        VDivE.delete(0,"end")
        VDivE.insert(0,Vdiv.get())
        #
        Twdthlab = Label(frame1, text="Trace Width in Pixels", style= "A10B.TLabel")
        Twdthlab.grid(row=4, column=0, sticky=W)
        TwdthMode = Frame( frame1 )
        TwdthMode.grid(row=4, column=1, sticky=W)
        TwdthE = Entry(TwdthMode, width=4)
        TwdthE.bind('<MouseWheel>', Settingsscroll)
        TwdthE.bind('<Key>', onTextKey)
        TwdthE.pack(side=RIGHT)
        TwdthE.delete(0,"end")
        TwdthE.insert(0,TRACEwidth.get())
        #
        Gwdthlab = Label(frame1, text="Grid Width in Pixels", style= "A10B.TLabel")
        Gwdthlab.grid(row=5, column=0, sticky=W)
        GwdthMode = Frame( frame1 )
        GwdthMode.grid(row=5, column=1, sticky=W)
        GwdthE = Entry(GwdthMode, width=4)
        GwdthE.bind('<MouseWheel>', Settingsscroll)
        GwdthE.bind('<Key>', onTextKey)
        GwdthE.pack(side=RIGHT)
        GwdthE.delete(0,"end")
        GwdthE.insert(0,GridWidth.get())
        #
        Settingsdismissbutton = Button(frame1, text="Dismiss", style= "W8.TButton", command=DestroySettings)
        Settingsdismissbutton.grid(row=6, column=0, sticky=W, pady=7)
#
def SettingsUpdate():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, SettingsDisp, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon

    try:
        GW = int(eval(GwdthE.get()))
        if GW < 1:
            GW = 1
            GwdthE.delete(0,END)
            GwdthE.insert(0, int(GW))
        if GW > 5:
            GW = 5
            GwdthE.delete(0,END)
            GwdthE.insert(0, int(GW))
    except:
        GwdthE.delete(0,END)
        GwdthE.insert(0, GridWidth.get())
    GridWidth.set(GW)
    try:
        TW = int(eval(TwdthE.get()))
        if TW < 1:
            TW = 1
            TwdthE.delete(0,END)
            TwdthE.insert(0, int(TW))
        if TW > 5:
            TW = 5
            TwdthE.delete(0,END)
            TwdthE.insert(0, int(TW))
    except:
        TwdthE.delete(0,END)
        TwdthE.insert(0, TRACEwidth.get())
    TRACEwidth.set(TW)
 # Number of average sweeps for average mode
    try:
        TA = int(eval(TAvg.get()))
        if TA < 1:
            TA = 1
            TAvg.delete(0,END)
            TAvg.insert(0, int(TA))
        if TA > 16:
            TA = 16
            TAvg.delete(0,END)
            TAvg.insert(0, int(TA))
    except:
        TAvg.delete(0,END)
        TAvg.insert(0, TRACEaverage.get())
    TRACEaverage.set(TA)
    # Number of vertical divisions for spectrum / Bode
    try:
        VDv = int(eval(VDivE.get()))
        if VDv < 1:
            VDv = 1
            VDivE.delete(0,END)
            VDivE.insert(0, int(VDv))
        if VDv > 16:
            VDv = 16
            VDivE.delete(0,END)
            VDivE.insert(0, int(VDv))
    except:
        VDivE.delete(0,END)
        VDivE.insert(0, Vdiv.get())
    Vdiv.set(VDv)
    # number of Harmonic Markers in SA
    try:
        HM = int(eval(HarMon.get()))
        if HM < 1:
            HM = 1
            HarMon.delete(0,END)
            HarMon.insert(0, int(HM))
        if HM > 9:
            HM =9
            HarMon.delete(0,END)
            HarMon.insert(0, int(HM))
    except:
        HarMon.delete(0,END)
        HarMon.insert(0, HarmonicMarkers.get())
    HarmonicMarkers.set(HM)
 # The zero stuffing value is 2 ** ZERO stuffing, calculated on initialize
    try:
        ZST = int(eval(ZSTuff.get()))
        if ZST < 1:
            ZST = 1
            ZSTuff.delete(0,END)
            ZSTuff.insert(0, int(ZST))
        if ZST > 5:
            ZST = 5
            ZSTuff.delete(0,END)
            ZSTuff.insert(0, int(ZST))
    except:
        ZSTuff.delete(0,END)
        ZSTuff.insert(0, ZEROstuffing.get())
    ZEROstuffing.set(ZST)
#
def DestroySettings():
    global Settingswindow, SettingsStatus, SettingsDisp
    
    SettingsStatus.set(0)
    # SettingsDisp.set(0)
    Settingswindow.destroy()
#
def onCanvasMouse_xy(event):
    global MouseX, MouseY, MouseWidget

    MouseWidget = event.widget
    MouseX, MouseY = event.x, event.y
#
# ================ Make main Screen ==========================
TgInput = IntVar(0)   # Trigger Input variable
SingleShot = IntVar(0) # variable for Single Shot manual trigger
AutoLevel = IntVar(0) # variable for Auto Level trigger at mid point
TgEdge = IntVar(0)   # Trigger edge variable
# Show channels variables
ShowC1_V = IntVar(0)   # curves to display variables
ShowC2_V = IntVar(0)
ShowLoopBack = IntVar(0)
ShowRA_V = IntVar(0)
ShowRB_V = IntVar(0)
ShowMath = IntVar(0)
Show_MathX = IntVar(0)
Show_MathY = IntVar(0)
AutoCenterA = IntVar(0)
AutoCenterB = IntVar(0)
SmoothCurves = IntVar(0)
ZOHold = IntVar(0)
TRACEmodeTime = IntVar(0)
TRACEmodeTime.set(0)
ColorMode = IntVar(0)
MathTrace = IntVar(0)
# define vertical measurment variables
MeasDCV1 = IntVar(0)
MeasMinV1 = IntVar(0)
MeasMaxV1 = IntVar(0)
MeasMidV1 = IntVar(0)
MeasPPV1 = IntVar(0)
MeasRMSV1 = IntVar(0)
MeasRMSVA_B = IntVar(0)
MeasDiffAB = IntVar(0)
MeasDCV2 = IntVar(0)
MeasMinV2 = IntVar(0)
MeasMaxV2 = IntVar(0)
MeasMidV2 = IntVar(0)
MeasPPV2 = IntVar(0)
MeasRMSV2 = IntVar(0)
MeasDiffBA = IntVar(0)
MeasUserA = IntVar(0)
MeasAHW = IntVar(0)
MeasALW = IntVar(0)
MeasADCy = IntVar(0)
MeasAPER = IntVar(0)
MeasAFREQ = IntVar(0)
MeasBHW = IntVar(0)
MeasBLW = IntVar(0)
MeasBDCy = IntVar(0)
MeasBPER = IntVar(0)
MeasBFREQ = IntVar(0)
MeasPhase = IntVar(0)
MeasTopV1 = IntVar(0)
MeasBaseV1 = IntVar(0)
MeasTopV2 = IntVar(0)
MeasBaseV2 = IntVar(0)
MeasUserB = IntVar(0)
MeasDelay = IntVar(0)
TimeDisp = IntVar(0)
TimeDisp.set(1)
XYDisp = IntVar(0)
FreqDisp = IntVar(0)
BodeDisp = IntVar(0)
IADisp = IntVar(0)
OhmDisp = IntVar(0)
BodeScreenStatus = IntVar(0)
BodeScreenStatus.set(0)
DigScreenStatus = IntVar(0)
DigScreenStatus.set(0)
PatGenScreenStatus = IntVar(0)
PatGenScreenStatus.set(0)
MuxScreenStatus = IntVar(0)
MuxScreenStatus.set(0)
MinigenScreenStatus = IntVar(0)
MinigenScreenStatus.set(0)
DA1ScreenStatus = IntVar(0)
DA1ScreenStatus.set(0)
DigPotScreenStatus = IntVar(0)
DigPotScreenStatus.set(0)
GenericSerialStatus = IntVar(0)
GenericSerialStatus.set(0)
DigFiltStatus = IntVar(0)
DigFiltStatus.set(0)
CommandStatus = IntVar(0)
CommandStatus.set(0)
MeasureStatus = IntVar(0)
MeasureStatus.set(0)
MarkerScale = IntVar(0)
MarkerScale.set(1)
PlusUSEnab = IntVar(0)
NegUSEnab = IntVar(0)
SampleModeTime = IntVar(0)
SettingsStatus = IntVar(0)
#
frame2r = Frame(root, borderwidth=5, relief=RIDGE)
frame2r.pack(side=RIGHT, fill=BOTH, expand=NO)

frame1 = Frame(root, borderwidth=5, relief=RIDGE)
frame1.pack(side=TOP, fill=BOTH, expand=NO)

frame2 = Frame(root, borderwidth=5, relief=RIDGE)
frame2.pack(side=TOP, fill=BOTH, expand=YES)

frame3 = Frame(root, borderwidth=5, relief=RIDGE)
frame3.pack(side=TOP, fill=BOTH, expand=NO)
# define custom buttons
root.style.configure("W3.TButton", width=3, relief=RAISED)
root.style.configure("W4.TButton", width=4, relief=RAISED)
root.style.configure("W5.TButton", width=5, relief=RAISED)
root.style.configure("W7.TButton", width=7, relief=RAISED)
root.style.configure("W8.TButton", width=8, relief=RAISED)
root.style.configure("W11.TButton", width=11, relief=RAISED)
root.style.configure("W16.TButton", width=16, relief=RAISED)
root.style.configure("W17.TButton", width=17, relief=RAISED)
root.style.configure("Stop.TButton", background="red", width=4, relief=RAISED)
root.style.configure("Run.TButton", background="green", width=4, relief=RAISED)
root.style.configure("Pwr.TButton", background="green", width=7, relief=RAISED)
root.style.configure("RConn.TButton", background="red", width=5, relief=RAISED)
root.style.configure("GConn.TButton", background="green", width=5, relief=RAISED)
root.style.configure("Rtrace1.TButton", background=COLORtrace1, width=7, relief=RAISED)
root.style.configure("Strace1.TButton", background=COLORtrace1, width=7, relief=SUNKEN)
root.style.configure("Rtrace2.TButton", background=COLORtrace2, width=7, relief=RAISED)
root.style.configure("Strace2.TButton", background=COLORtrace2, width=7, relief=SUNKEN)
root.style.configure("Rtrace3.TButton", background=COLORtrace3, width=7, relief=RAISED)
root.style.configure("Strace3.TButton", background=COLORtrace3, width=7, relief=SUNKEN)
root.style.configure("Rtrace4.TButton", background=COLORtrace4, width=7, relief=RAISED)
root.style.configure("Strace4.TButton", background=COLORtrace4, width=7, relief=SUNKEN)
root.style.configure("Rtrace5.TButton", background=COLORtrace5, width=7, relief=RAISED)
root.style.configure("Strace5.TButton", background=COLORtrace5, width=7, relief=SUNKEN)
root.style.configure("Rtrace6.TButton", background=COLORtrace6, width=7, relief=RAISED)
root.style.configure("Strace6.TButton", background=COLORtrace6, width=7, relief=SUNKEN)
root.style.configure("Rtrace7.TButton", background=COLORtrace7, width=7, relief=RAISED)
root.style.configure("Strace7.TButton", background=COLORtrace7, width=7, relief=SUNKEN)
root.style.configure("A10R1.TLabelframe.Label", foreground=COLORtraceR1, font=('Arial', 10, 'bold'))
root.style.configure("A10R1.TLabelframe", borderwidth=5, relief=RIDGE)
root.style.configure("A10R2.TLabelframe.Label", foreground=COLORtraceR2, font=('Arial', 10, 'bold'))
root.style.configure("A10R2.TLabelframe", borderwidth=5, relief=RIDGE)
root.style.configure("A10B.TLabel", foreground=COLORcanvas, font="Arial 10 bold") # Black text
root.style.configure("A12B.TLabel", foreground=COLORcanvas, font="Arial 12 bold") # Black text
root.style.configure("A16B.TLabel", foreground=COLORcanvas, font="Arial 16 bold") # Black text
root.style.configure("Stop.TRadiobutton", background="red")
root.style.configure("Run.TRadiobutton", background="green")
root.style.configure("Disab.TCheckbutton", indicatorcolor="red")
root.style.configure("Enab.TCheckbutton", indicatorcolor="green")
root.style.configure("WPhase.TRadiobutton", width=5, background="white", indicatorcolor=("red", "green"))
root.style.configure("GPhase.TRadiobutton", width=5, background="gray", indicatorcolor=("red", "green"))
# create a pulldown menu
# Trigger signals
Triggermenu = Menubutton(frame1, text="Trigger", style="W7.TButton")
Triggermenu.menu = Menu(Triggermenu, tearoff = 0 )
Triggermenu["menu"]  = Triggermenu.menu
Triggermenu.menu.add_radiobutton(label='None', variable=TgInput, value=0)
Triggermenu.menu.add_radiobutton(label='C1-V', variable=TgInput, value=1)
Triggermenu.menu.add_radiobutton(label='C2-V', variable=TgInput, value=3)
Triggermenu.menu.add_checkbutton(label='Auto Level', variable=AutoLevel)
Triggermenu.menu.add_checkbutton(label='SingleShot', variable=SingleShot)
Triggermenu.pack(side=LEFT)
#
Edgemenu = Menubutton(frame1, text="Edge", style="W5.TButton")
Edgemenu.menu = Menu(Edgemenu, tearoff = 0 )
Edgemenu["menu"]  = Edgemenu.menu
Edgemenu.menu.add_radiobutton(label='Rising  [+]', variable=TgEdge, value=0)
Edgemenu.menu.add_radiobutton(label='Falling [-]', variable=TgEdge, value=1)
Edgemenu.pack(side=LEFT)
#
tlab = Label(frame1, text="Trig Level")
tlab.pack(side=LEFT)
TRIGGERentry = Entry(frame1, width=5)
TRIGGERentry.bind('<MouseWheel>', onTextScroll)
TRIGGERentry.bind("<Return>", BTriglevel)
TRIGGERentry.bind('<Key>', onTextKey)
TRIGGERentry.pack(side=LEFT)
TRIGGERentry.delete(0,"end")
TRIGGERentry.insert(0,0.0)
#
tgb = Button(frame1, text="50%", style="W4.TButton", command=BTrigger50p)
tgb.pack(side=LEFT)
#
hldlab = Button(frame1, text="Hold Off", style="W8.TButton", command=IncHoldOff)
hldlab.pack(side=LEFT)
HoldOffentry = Entry(frame1, width=4)
HoldOffentry.bind('<MouseWheel>', onTextScroll)
HoldOffentry.bind("<Return>", BHoldOff)
HoldOffentry.bind('<Key>', onTextKey)
HoldOffentry.pack(side=LEFT)
HoldOffentry.delete(0,"end")
HoldOffentry.insert(0,0.0)
#
hozlab = Button(frame1, text="Horz Pos", style="W8.TButton", command=SetTriggerPoss)
hozlab.pack(side=LEFT)
HozPossentry = Entry(frame1, width=8)
HozPossentry.bind('<MouseWheel>', onTextScroll)
HozPossentry.bind("<Return>", BHozPoss)
HozPossentry.bind('<Key>', onTextKey)
HozPossentry.pack(side=LEFT)
HozPossentry.delete(0,"end")
HozPossentry.insert(0,0.0)
#
bexit = Button(frame1, text="Exit", style="W4.TButton", command=Bcloseexit)
bexit.pack(side=RIGHT)
bstop = Button(frame1, text="Stop", style="Stop.TButton", command=BStop)
bstop.pack(side=RIGHT)
brun = Button(frame1, text="Run", style="Run.TButton", command=BStart)
brun.pack(side=RIGHT)
# Curves Menu
Showmenu = Menubutton(frame1, text="Curves", style="W7.TButton")
Showmenu.menu = Menu(Showmenu, tearoff = 0 )
Showmenu["menu"] = Showmenu.menu
Showmenu.menu.add_command(label="-Show-", foreground="blue", command=donothing)
Showmenu.menu.add_command(label="All", command=BShowCurvesAll)
Showmenu.menu.add_command(label="None", command=BShowCurvesNone)
Showmenu.menu.add_checkbutton(label='C1-V   [1]', variable=ShowC1_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='C2-V   [2]', variable=ShowC2_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='Loop Back [l]', variable=ShowLoopBack, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='Math-X [3]', variable=Show_MathX, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='Math-Y [4]', variable=Show_MathY, command=UpdateTimeTrace)
Showmenu.menu.add_command(label="-Auto Vert Center-", foreground="blue", command=donothing)
Showmenu.menu.add_checkbutton(label='C1-V', variable=AutoCenterA)
Showmenu.menu.add_checkbutton(label='C2-V', variable=AutoCenterB)
Showmenu.menu.add_separator()  
Showmenu.menu.add_checkbutton(label='R1-V', variable=ShowRA_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='R2-V', variable=ShowRB_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='RMath', variable=ShowMath, command=UpdateTimeTrace)
Showmenu.menu.add_separator()
Showmenu.menu.add_checkbutton(label='T Cursor [t]', variable=ShowTCur, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='V Cursor [v]', variable=ShowVCur, command=UpdateTimeTrace)
Showmenu.pack(side=RIGHT)
#
if ShowBallonHelp > 0:
    Triggermenu_tip = CreateToolTip(Triggermenu, 'Select trigger signal')
    Edgemenu_tip = CreateToolTip(Edgemenu, 'Select trigger edge')
    tgb_tip = CreateToolTip(tgb, 'Set trigger level to waveform mid point')
    hldlab_tip = CreateToolTip(hldlab, 'Increment Hold Off setting by one time division')
    hozlab_tip = CreateToolTip(hozlab, 'When triggering, set trigger point to center of screen')
    bexit_tip = CreateToolTip(bexit, 'Exit ALICE Desktop')
    bstop_tip = CreateToolTip(bstop, 'Stop acquiring data')
    brun_tip = CreateToolTip(brun, 'Start acquiring data')
    Showmenu_tip = CreateToolTip(Showmenu, 'Select which traces to display')
# Time per Div
TMsb = Spinbox(frame1, width=8, values= TMpdiv, command=BTime)
TMsb.bind('<MouseWheel>', onSpinBoxScroll)
TMsb.pack(side=RIGHT)
TMsb.delete(0,"end")
TMsb.insert(0,0.5)
TMlab = Label(frame1, text="Time mS/Div")
TMlab.pack(side=RIGHT)
#
ca = Canvas(frame2, width=CANVASwidth, height=CANVASheight, background=COLORcanvas, cursor='cross')
# add mouse left and right button click to canvas
ca.bind('<Configure>', CAresize)
ca.bind('<1>', onCanvasClickLeft)
ca.bind('<3>', onCanvasClickRight)
ca.bind("<Motion>",onCanvasMouse_xy)
ca.bind("<Up>", onCanvasUpArrow) # DoNothing)
ca.bind("<Down>", onCanvasDownArrow)
ca.bind("<Left>", onCanvasLeftArrow)
ca.bind("<Right>", onCanvasRightArrow)
ca.bind("1", onCanvasOne)
ca.bind("2", onCanvasTwo)
ca.bind("3", onCanvasThree)
ca.bind("4", onCanvasFour)
ca.bind("5", onCanvasFive)
ca.bind("6", onCanvasSix)
ca.bind("7", onCanvasSeven)
ca.bind("8", onCanvasEight)
ca.bind("9", onCanvasNine)
ca.bind("0", onCanvasZero)
ca.bind("a", onCanvasAverage)
ca.bind("l", onCanvasLoopBack)
ca.bind("t", onCanvasShowTcur)
ca.bind("v", onCanvasShowVcur)
ca.bind("s", onCanvasSnap)
ca.bind("+", onCanvasTrising)
ca.bind("-", onCanvasTfalling)
# ca.bind('<MouseWheel>', onCanvasClickScroll)
ca.pack(side=TOP, fill=BOTH, expand=YES)
MouseWidget = ca
# right side menu buttons
dropmenu = Frame( frame2r )
dropmenu.pack(side=TOP)
bcon = Button(dropmenu, text="Recon", style="RConn.TButton", command=ReConnectDevice)
bcon.pack(side=LEFT, anchor=W)
# File menu
Filemenu = Menubutton(dropmenu, text="File", style="W4.TButton")
Filemenu.menu = Menu(Filemenu, tearoff = 0 )
Filemenu["menu"] = Filemenu.menu
Filemenu.menu.add_command(label="Save Config", command=BSaveConfigTime)
Filemenu.menu.add_command(label="Load Config", command=BLoadConfigTime)
Filemenu.menu.add_command(label="Save Adj", command=BSaveCal)
Filemenu.menu.add_command(label="Load Adj", command=BLoadCal)
Filemenu.menu.add_command(label="Save Screen", command=BSaveScreen)
Filemenu.menu.add_command(label="Save To CSV", command=BSaveData)
Filemenu.menu.add_command(label="Load From CSV", command=BReadData)
Filemenu.menu.add_command(label="Help", command=BHelp)
Filemenu.menu.add_command(label="About", command=BAbout)
Filemenu.pack(side=LEFT, anchor=W)
# Options Menu
Optionmenu = Menubutton(dropmenu, text="Options", style="W7.TButton")
Optionmenu.menu = Menu(Optionmenu, tearoff = 0 )
Optionmenu["menu"] = Optionmenu.menu
Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
Optionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurves, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Z-O-Hold', variable=ZOHold, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Trace Avg [a]', variable=TRACEmodeTime)
# Optionmenu.menu.add_checkbutton(label='Sample Avg', variable=SampleModeTime)
# Optionmenu.menu.add_command(label="Num Sa Avg", command=BSampleAveragemode)
Optionmenu.menu.add_checkbutton(label='Persistance', variable=ScreenTrefresh)
Optionmenu.menu.add_command(label='Set Marker Location', command=BSetMarkerLocation)
Optionmenu.menu.add_command(label="SnapShot [s]", command=BSnapShot)
Optionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
Optionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
Optionmenu.menu.add_command(label="Run Self Cal", command=BSelfCalibration)
Optionmenu.menu.add_command(label="Save Cal file", command=SaveCalibration)
Optionmenu.menu.add_command(label="Load Cal file", command=LoadCalibration)
Optionmenu.pack(side=LEFT, anchor=W)
#
dropmenu2 = Frame( frame2r )
dropmenu2.pack(side=TOP)
# Math trace menu
MathMenu = Menubutton(dropmenu2, text="Math", style="W4.TButton")
MathMenu.menu = Menu(MathMenu, tearoff = 0 )
MathMenu["menu"] = MathMenu.menu
MathMenu.menu.add_radiobutton(label='none   [0]', variable=MathTrace, value=0, command=UpdateTimeTrace)
MathMenu.menu.add_radiobutton(label='C1V+C2V [5]', variable=MathTrace, value=1, command=UpdateTimeTrace)
MathMenu.menu.add_radiobutton(label='C1V-C2V [6]', variable=MathTrace, value=2, command=UpdateTimeTrace)
MathMenu.menu.add_radiobutton(label='C2V-C1V [7]', variable=MathTrace, value=3, command=UpdateTimeTrace)
MathMenu.menu.add_radiobutton(label='C2V/C1V [8]', variable=MathTrace, value=10, command=UpdateTimeTrace)
MathMenu.menu.add_radiobutton(label='Formula [9]', variable=MathTrace, value=12, command=UpdateTimeTrace)
MathMenu.menu.add_command(label="Enter Formula", command=BEnterMathString)
MathMenu.menu.add_command(label="Enter X Formula", command=BEnterMathXString)
MathMenu.menu.add_command(label="Enter Y Formula", command=BEnterMathYString)
MathMenu.pack(side=RIGHT, anchor=W)
# Measurments menu
measlab = Label(dropmenu2, text="Meas")
measlab.pack(side=LEFT, anchor=W)
MeasmenuA = Menubutton(dropmenu2, text="C1", style="W3.TButton")
MeasmenuA.menu = Menu(MeasmenuA, tearoff = 0 )
MeasmenuA["menu"] = MeasmenuA.menu
MeasmenuA.menu.add_command(label="-C1-V-", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=MeasDCV1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=MeasMinV1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=MeasMaxV1)
MeasmenuA.menu.add_checkbutton(label='Base', variable=MeasBaseV1)
MeasmenuA.menu.add_checkbutton(label='Top', variable=MeasTopV1)
MeasmenuA.menu.add_checkbutton(label='Mid', variable=MeasMidV1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=MeasPPV1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=MeasRMSV1)
MeasmenuA.menu.add_checkbutton(label='C1-C2', variable=MeasDiffAB)
MeasmenuA.menu.add_checkbutton(label='C1-C2 RMS', variable=MeasRMSVA_B)
MeasmenuA.menu.add_checkbutton(label='User', variable=MeasUserA, command=BUserAMeas)
MeasmenuA.menu.add_separator()
#
MeasmenuA.menu.add_command(label="C1-Time", command=donothing)
MeasmenuA.menu.add_checkbutton(label='H-Width', variable=MeasAHW)
MeasmenuA.menu.add_checkbutton(label='L-Width', variable=MeasALW)
MeasmenuA.menu.add_checkbutton(label='DutyCyle', variable=MeasADCy)
MeasmenuA.menu.add_checkbutton(label='Period', variable=MeasAPER)
MeasmenuA.menu.add_checkbutton(label='Freq', variable=MeasAFREQ)
MeasmenuA.menu.add_checkbutton(label='1-2 Phase', variable=MeasPhase)
#
MeasmenuA.pack(side=LEFT)
#
MeasmenuB = Menubutton(dropmenu2, text="C2", style="W3.TButton")
MeasmenuB.menu = Menu(MeasmenuB, tearoff = 0 )
MeasmenuB["menu"] = MeasmenuB.menu
MeasmenuB.menu.add_command(label="-C2-V-", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=MeasDCV2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=MeasMinV2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=MeasMaxV2)
MeasmenuB.menu.add_checkbutton(label='Base', variable=MeasBaseV2)
MeasmenuB.menu.add_checkbutton(label='Top', variable=MeasTopV2)
MeasmenuB.menu.add_checkbutton(label='Mid', variable=MeasMidV2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=MeasPPV2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=MeasRMSV2)
MeasmenuB.menu.add_checkbutton(label='C2-C1', variable=MeasDiffBA)
MeasmenuB.menu.add_checkbutton(label='User', variable=MeasUserB, command=BUserBMeas)
MeasmenuB.menu.add_separator()
#
MeasmenuB.menu.add_command(label="C2-Time", command=donothing)
MeasmenuB.menu.add_checkbutton(label='H-Width', variable=MeasBHW)
MeasmenuB.menu.add_checkbutton(label='L-Width', variable=MeasBLW)
MeasmenuB.menu.add_checkbutton(label='DutyCyle', variable=MeasBDCy)
MeasmenuB.menu.add_checkbutton(label='Period', variable=MeasBPER)
MeasmenuB.menu.add_checkbutton(label='Freq', variable=MeasBFREQ)
MeasmenuB.menu.add_checkbutton(label='2-1 Delay', variable=MeasDelay)
MeasmenuB.pack(side=LEFT)
#
BuildAWGScreen = Button(frame2r, text="AWG Window", style="W16.TButton", command=MakeAWGWindow)
BuildAWGScreen.pack(side=TOP)
# Mode selector
timebtn = Frame( frame2r )
timebtn.pack(side=TOP)
ckb1 = Checkbutton(timebtn, text="Enab", style="Disab.TCheckbutton", variable=TimeDisp, command=TimeCheckBox)
ckb1.pack(side=LEFT)
timelab = Label(timebtn, text="Time Plot")
timelab.pack(side=LEFT)
xybtn = Frame( frame2r )
xybtn.pack(side=TOP)
ckb2 = Checkbutton(xybtn, text="Enab", style="Disab.TCheckbutton", variable=XYDisp, command=XYCheckBox)
ckb2.pack(side=LEFT)
BuildXYScreen = Button(xybtn, text="X-Y Plot", style="W11.TButton", command=MakeXYWindow)
BuildXYScreen.pack(side=TOP)
#
freqbtn = Frame( frame2r )
freqbtn.pack(side=TOP)
ckb3 = Checkbutton(freqbtn, text="Enab", style="Disab.TCheckbutton", variable=FreqDisp, command=FreqCheckBox)
ckb3.pack(side=LEFT)
BuildSpectrumScreen = Button(freqbtn, text="Spectrum Plot", style="W11.TButton", command=MakeSpectrumWindow)
BuildSpectrumScreen.pack(side=LEFT)
#
bodebtn = Frame( frame2r )
bodebtn.pack(side=TOP)
ckb5 = Checkbutton(bodebtn, text="Enab", style="Disab.TCheckbutton", variable=BodeDisp, command=BodeCheckBox)
ckb5.pack(side=LEFT)
BuildBodeScreen = Button(bodebtn, text="Bode Plot", style="W11.TButton", command=MakeBodeWindow)
BuildBodeScreen.pack(side=LEFT)
#
impdbtn = Frame( frame2r )
impdbtn.pack(side=TOP)
ckb4 = Checkbutton(impdbtn, text="Enab", style="Disab.TCheckbutton", variable=IADisp, command=IACheckBox)
ckb4.pack(side=LEFT)
BuildIAScreen = Button(impdbtn, text="Impedance", style="W11.TButton", command=MakeIAWindow)
BuildIAScreen.pack(side=LEFT)
#
dcohmbtn = Frame( frame2r )
dcohmbtn.pack(side=TOP)
ckb6 = Checkbutton(dcohmbtn, text="Enab", style="Disab.TCheckbutton", variable=OhmDisp, command=OhmCheckBox)
ckb6.pack(side=LEFT)
BuildOhmScreen = Button(dcohmbtn, text="Ohmmeter", style="W11.TButton", command=MakeOhmWindow)
BuildOhmScreen.pack(side=LEFT)
if ShowBallonHelp > 0:
    BuildAWGScreen_tip = CreateToolTip(BuildAWGScreen, 'Surface AWG Controls window')
    BuildXYScreen_tip = CreateToolTip(BuildXYScreen, 'Open X vs Y plot window')
    BuildSpectrumScreen_tip = CreateToolTip(BuildSpectrumScreen, 'Open spectrum analyzer window')
    BuildBodeScreen_tip = CreateToolTip(BuildBodeScreen, 'Open Bode plot window')
    BuildIAScreen_tip = CreateToolTip(BuildIAScreen, 'Open Impedance analyzer window')
    BuildOhmScreen_tip = CreateToolTip(BuildOhmScreen, 'Open DC Ohmmeter window')
# Digital Input / Output Option screens
BuildDigScreen = Button(frame2r, text="Digital I/O Screen", style="W17.TButton", command=MakeDigScreen)
BuildDigScreen.pack(side=TOP)
# Digital Pattern Generator screen
BuildPatGenScreen = Button(frame2r, text="Dig Pat Gen Screen", style="W17.TButton", command=MakePatGenScreen)
BuildPatGenScreen.pack(side=TOP)
# Optional plugin cards
if EnableMuxMode > 0:
    BuildMuxScreen = Button(frame2r, text="Analog In Mux Screen", style="W17.TButton", command=MakeMuxModeWindow)
    BuildMuxScreen.pack(side=TOP)
if EnableMinigenMode > 0:
    BuildMinigenScreen = Button(frame2r, text="MiniGen Controls", style="W17.TButton", command=MakeMinigenWindow)
    BuildMinigenScreen.pack(side=TOP)
if EnablePmodDA1Mode > 0:
    BuildDA1Screen = Button(frame2r, text="PMOD DA1 Controls", style="W17.TButton", command=MakeDA1Window)
    BuildDA1Screen.pack(side=TOP)
if EnableDigPotMode >0:
    BuildDigPotScreen = Button(frame2r, text="Dig Pot Controls", style="W17.TButton", command=MakeDigPotWindow)
    BuildDigPotScreen.pack(side=TOP)
##if EnableGenericSerialMode >0:
##    GenericSerialScreen = Button(frame2r, text="Generic Serial Output", style="W17.TButton", command=MakeGenericSerialWindow)
##    GenericSerialScreen.pack(side=TOP)
if EnableDigitalFilter >0:
    DigFiltScreen = Button(frame2r, text="Digital Filter", style="W17.TButton", command=MakeDigFiltWindow)
    DigFiltScreen.pack(side=TOP)
if EnableCommandInterface > 0:
    CommandLineScreen = Button(frame2r, text="Command Interface", style="W17.TButton", command=MakeCommandScreen)
    CommandLineScreen.pack(side=TOP)
if EnableMeasureScreen > 0:
    MeasureScreen = Button(frame2r, text="Measure Screen", style="W17.TButton", command=MakeMeasureScreen)
    MeasureScreen.pack(side=TOP)
# User Power supply controls
userlab = Label(frame2r, text="External Power Supplies")
userlab.pack(side=TOP)
PlusUS = Frame( frame2r )
PlusUS.pack(side=TOP)
plusUSrb = Label(PlusUS, text="5.00")
plusUSrb.pack(side=RIGHT)
plusUSEntry = Entry(PlusUS, width=5)
plusUSEntry.bind("<Return>", BplusUS)
plusUSEntry.bind('<MouseWheel>', scrollPlusUS)
plusUSEntry.bind('<Key>', onTextKey)
plusUSEntry.pack(side=RIGHT)
plusUSEntry.delete(0,"end")
plusUSEntry.insert(0,5.0)
plusUSlab = Checkbutton(PlusUS, text="+V", style="Disab.TCheckbutton", variable=PlusUSEnab, command=BPlusOnOff)
plusUSlab.pack(side=RIGHT)
#
NegUS = Frame( frame2r )
NegUS.pack(side=TOP)
negUSrb = Label(NegUS, text=" -5.00")
negUSrb.pack(side=RIGHT)
negUSEntry = Entry(NegUS, width=5)
negUSEntry.bind("<Return>", BnegUS)
negUSEntry.bind('<MouseWheel>', scrollNegUS)
negUSEntry.bind('<Key>', onTextKey)
negUSEntry.pack(side=RIGHT)
negUSEntry.delete(0,"end")
negUSEntry.insert(0,-5.0)
negUSlab = Checkbutton(NegUS, text="-V", style="Disab.TCheckbutton", variable=NegUSEnab, command=BNegOnOff)
negUSlab.pack(side=RIGHT)
# input probe wigets
prlab = Label(frame2r, text="Adjust Gain / Offset")
prlab.pack(side=TOP)
# Input Probes sub frame 
ProbeA = Frame( frame2r )
ProbeA.pack(side=TOP)
gain1lab = Label(ProbeA, text="CH1")
gain1lab.pack(side=LEFT)
CHAVGainEntry = Entry(ProbeA, width=5)
CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
CHAVGainEntry.bind('<Key>', onTextKey)
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,1.0)
CHAVOffsetEntry = Entry(ProbeA, width=5)
CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAVOffsetEntry.bind('<Key>', onTextKey)
CHAVOffsetEntry.pack(side=LEFT)
CHAVOffsetEntry.delete(0,"end")
CHAVOffsetEntry.insert(0,0.0)
#
ProbeB = Frame( frame2r )
ProbeB.pack(side=TOP)
gain2lab = Label(ProbeB, text="CH2")
gain2lab.pack(side=LEFT)
CHBVGainEntry = Entry(ProbeB, width=5)
CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
CHBVGainEntry.bind('<Key>', onTextKey)
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,1.0)
CHBVOffsetEntry = Entry(ProbeB, width=5)
CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBVOffsetEntry.bind('<Key>', onTextKey)
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,0.0)
# add ADI logo Don't mess with this bit map data!
ADIlogo = """
R0lGODlhdAAxAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/
/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm
AABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/
MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm
ZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/
mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm
zGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/
/5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ
AJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA
M8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ
ZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A
mf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z
zP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///yH5BAEAABAALAAAAAB0ADEA
AAj/AP8JHEiwoMGDCBMqXMiwocOHEBlSS5WKIUWJfqj9S+XnokGPEUOKdEito0WNCC9OpEbtz7+V
HyuOnEnzI6yMEylWpNgx50aOGkt6LElUoB9VPFHyTAXrYipVNaOSTOWzEEuqA61SXTnxH06ZK7EK
5Ap2J9WdKKWqRVjyJ1c/1ZbqvPnyrKqS215mzEiwo8yfer22XUs4Zse9V31mPFuxbdKxjAU65Si5
8Vm+hTNXrvuWKFKdjs8WJEqR5V63bkP/1bx28E+rK28ihckRayHQnH/yVdUTMtB/1fywHj7TI0iR
x4krd7g0bcjSy6NLn069uvXr2LNr3/6Sip/vU777//EOXjx5P+G/nw/vnCA18gXFOy+JWfL31V6/
s001ZQqK8AdN1B8KJiVETX9TMIGggv0xmOCCEDbYX3sDoTdhXwi6199qFjJRUIMB3iEhgs7x56CC
wrH134r+tcjiiy7G+B+FL7nIYYsp1ojCX9SwuFqLBh343xQc+bGiUjhyhCNbLTbR4oBTODlkk09S
iQKNBz7Z139OotQjkQPxx2WO/3D5kZNUDDSRk8IJOUVabqoo45ww1tkijejt+N9fUM64kX9/GQne
lQMBWdCRGs6Yyp4FFYllhIVM6aCkCFL65kGAHshEjhZa2NiGAlWzJzUK8pngaAmSKVAh/fHWX0Rf
sv+oSnB01iprkIwOWKF//wzIEqBG8drrf4USS9CiYBYEy39/GCrQHzpZFWCVhOoFpZSVRkktheg1
MRaoXhGLbEaM9tpEinmiNGSj4CaaipNTqKltuaPBOF+ftt6JKgpUnGUoFcIaGR6wX371X4rOjnXw
R3tSYexLL+L37YgUmhjhgxSjijHGGln4rYMVoXdihr2eqiETdxhEooUUtuuevQEiayeL7eU5p3B5
ZmXjsHRWlLBAWgA7ULME/rPsqxjuOC2X/tE4VrfUztuef6oCKXDSRBb8MoBc6gSalD1BDVW4E5rW
osQQx+i0mgLbOd/CSWeJwtY7pvvhjLWmDWOOJc3/jHaWHDckd4TOsawxePEeuyGJ7O44opbWDukH
LB8hOGFtAcI4dkNEx7g5d+6xtBBLa8s7ZbUk/XF66aBLFau+D/GntntbwdQo6bXnHmTu83FFO+6k
wxm8QoAzyDrbI186UPIF/vk4in6UStA2DKaC4q4OKp98qsFmnPnsC21jM8zF3izZzB1RTRDRfrBa
dMl1alSrcPgOmVeQVpYuYNRSOtf/RFDbSaaCJzop9cVJFOkPzs6mF3iVjEheo0qzmvAHpcCtXuA7
iJjy5ZyE2Wwi9IpPub4ULzFlhIFP25P6DCKwzQlJVRML3EEstDFLOYdBH7qcyxQ3hUJIJkE7ORip
/5CmptJcEENMQNv3bkW7mc3pcz8bl8xilKN1ka0i7HMfDMsHo42wqIdiWVqlSmSlbGHLVwTRleII
tMFrccpPVnxXeGSnxH+csUk/tFJ96Aa7kuTLbWl82PnmKLn06OeHOxKTTExowoTgCD3i6UvbVqix
wMlue5i80PKIuKoN0VEhCJLd2KzHnushxJSjuySFXnewP3IwkIkrH0WYpRCBkewfWnSTc1TRyvfF
RwuqEtgqy3gt/hkTdXYUVl0cqEiFyE5ozlugL+GXpS32pwkdjNIqncjNWnXwYBZaEVSm+CIyQekv
jYTffaDkpjqpzpOym6a8HmepKk2KcAS5J+OcV0JDAIXJioPMEZQaxJd6Kkqfe1RTNxfquWNRBFo6
oV0qbvNQ6BQxjP/4TOGSpBSKUDQVEH2awHrTupKa9KQoTWl0AgIAOw==
"""
logo = PhotoImage(data=ADIlogo)
ADI1 = Label(frame2r, image=logo, anchor= "sw", compound="top") #, height=49, width=116
ADI1.pack(side=TOP)
# Bottom Buttons
# Voltage channel 1
CHAsb = Spinbox(frame3, width=4, values=CHvpdiv, command=BCHAlevel)
CHAsb.bind('<MouseWheel>', onSpinBoxScroll)
CHAsb.pack(side=LEFT)
CHAsb.delete(0,"end")
CHAsb.insert(0,0.5)
#
CHAlab = Button(frame3, text="C1 V/Div", style="Rtrace1.TButton", command=SetScaleA)
CHAlab.pack(side=LEFT)
CHAVPosEntry = Entry(frame3, width=5)
CHAVPosEntry.bind("<Return>", BOffsetA)
CHAVPosEntry.bind('<MouseWheel>', onTextScroll)
CHAVPosEntry.bind('<Key>', onTextKey)
CHAVPosEntry.pack(side=LEFT)
CHAVPosEntry.delete(0,"end")
CHAVPosEntry.insert(0,0.0)
CHAofflab = Button(frame3, text="C1 V Pos", style="Rtrace1.TButton", command=SetVAPoss)
CHAofflab.pack(side=LEFT)
# Voltage channel 2
CHBsb = Spinbox(frame3, width=4, values=CHvpdiv, command=BCHBlevel)
CHBsb.bind('<MouseWheel>', onSpinBoxScroll)
CHBsb.pack(side=LEFT)
CHBsb.delete(0,"end")
CHBsb.insert(0,0.5)
# 
CHBlab = Button(frame3, text="C2 V/Div", style="Strace2.TButton", command=SetScaleB)
CHBlab.pack(side=LEFT)
CHBVPosEntry = Entry(frame3, width=5)
CHBVPosEntry.bind("<Return>", BOffsetB)
CHBVPosEntry.bind('<MouseWheel>', onTextScroll)
CHBVPosEntry.bind('<Key>', onTextKey)
CHBVPosEntry.pack(side=LEFT)
CHBVPosEntry.delete(0,"end")
CHBVPosEntry.insert(0,0.0)
CHBofflab = Button(frame3, text="C2 V Pos", style="Rtrace2.TButton", command=SetVBPoss)
CHBofflab.pack(side=LEFT)
# Math channel 1
MC1sb = Spinbox(frame3, width=4, values=CHvpdiv)
MC1sb.bind('<MouseWheel>', onSpinBoxScroll)
MC1sb.pack(side=LEFT)
MC1sb.delete(0,"end")
MC1sb.insert(0,0.5)
# 
MC1lab = Button(frame3, text="MC1 /Div", style="Strace5.TButton", command=SetScaleMC1)
MC1lab.pack(side=LEFT)
MC1VPosEntry = Entry(frame3, width=5)
MC1VPosEntry.bind("<Return>", BOffsetB)
MC1VPosEntry.bind('<MouseWheel>', onTextScroll)
MC1VPosEntry.bind('<Key>', onTextKey)
MC1VPosEntry.pack(side=LEFT)
MC1VPosEntry.delete(0,"end")
MC1VPosEntry.insert(0,0.0)
MC1offlab = Button(frame3, text="MC1 Pos", style="Rtrace5.TButton" )
MC1offlab.pack(side=LEFT)
# Math channel 2
MC2sb = Spinbox(frame3, width=4, values=CHvpdiv)
MC2sb.bind('<MouseWheel>', onSpinBoxScroll)
MC2sb.pack(side=LEFT)
MC2sb.delete(0,"end")
MC2sb.insert(0,0.5)
# 
MC2lab = Button(frame3, text="MC2 /Div", style="Strace7.TButton", command=SetScaleMC2)
MC2lab.pack(side=LEFT)
MC2VPosEntry = Entry(frame3, width=5)
MC2VPosEntry.bind("<Return>", BOffsetB)
MC2VPosEntry.bind('<MouseWheel>', onTextScroll)
MC2VPosEntry.bind('<Key>', onTextKey)
MC2VPosEntry.pack(side=LEFT)
MC2VPosEntry.delete(0,"end")
MC2VPosEntry.insert(0,0.0)
MC2offlab = Button(frame3, text="MC2 Pos", style="Rtrace7.TButton")
MC2offlab.pack(side=LEFT)
#
if ShowBallonHelp > 0:
    CHAlab_tip = CreateToolTip(CHAlab, 'Select CH1-V vertical range/position axis to be used for markers and drawn color')
    CHBlab_tip = CreateToolTip(CHBlab, 'Select CH2-V vertical range/position axis to be used for markers and drawn color')
    CHAofflab_tip = CreateToolTip(CHAofflab, 'Set CH1-V position to DC average of signal')
    CHBofflab_tip = CreateToolTip(CHBofflab, 'Set CH2-V position to DC average of signal')
    plusUS_tip = CreateToolTip(plusUSlab, 'Toggle User power supply on / off')
    negUS_tip = CreateToolTip(negUSlab, 'Toggle User power supply on / off')
#
root.geometry('+300+0')
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
#===== Initalize device ======
if not numpy_found:
    root.update()
    showwarning("WARNING","Numpy not found!")
    root.destroy()
    exit()
if libiio_found:
    ConnectDevice() # find attached M2K
    MakeAWGWindow() # always build AWG window
    if DevID != "No Device":
        time.sleep(0.2)
        SelfCalibration() # Run a self calibration on start up
    BLoadConfig("alice-last-config.cfg") # load configuration from last session
# ================ Call main routine ===============================
    root.update() # Activate updated screens
    Analog_In() # Start sampling
else:
    root.update()
    showwarning("WARNING","Libiio not found!")
    root.destroy()
    exit()
