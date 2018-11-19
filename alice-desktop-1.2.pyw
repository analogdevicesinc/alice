#!/usr/bin/python
# ADALM1000 alice-desktop 1.2.py(w) (11-19-2018)
# For Python version > = 2.7.8
# With external module pysmu ( libsmu.rework >= 1.0 for ADALM1000 )
# optional split I/O modes for Rev F hardware supported
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
    from pysmu import *
    pysmu_found = True
except:
    pysmu_found = False
#
RevDate = "(19 Nov 2018)"
Version_url = 'https://github.com/analogdevicesinc/alice/releases/download/1.2.1/alice-desktop-1.2-setup.exe'
# samll bit map of ADI logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root=Tk()
root.title("ALICE DeskTop 1.2 " + RevDate + ": ALM1000 Oscilloscope")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
# Window graph area Values that can be modified
GRW = 720                   # Width of the time grid 720 default
GRH = 390                   # Height of the time grid 390 default
X0L = 55                    # Left top X value of time grid
Y0T = 25                    # Left top Y value of time grid
#
GRWF = 720                  # Width of the spectrum grid 720 default
GRHF = 390                  # Height of the spectrum grid 390 default
X0LF = 37                   # Left top X value of spectrum grid
Y0TF = 25                   # Left top Y value of spectrum grid
#
GRWBP = 720                  # Width of the Bode Plot grid 720 default
GRHBP = 390                  # Height of the Bode Plot grid 390 default
X0LBP = 37                   # Left top X value of Bode Plot grid
Y0TBP = 25                   # Left top Y value of Bode Plot grid
#
GRWXY = 420                  # Width of the XY grid 420 default
GRHXY = 390                  # Height of the XY grid 390 default
X0LXY = 37                   # Left top X value of XY grid
Y0TXY = 25                   # Left top Y value of XY grid
#
GRWIA = 400                  # Width of the grid 400 default
GRHIA = 400                  # Height of the grid 400 default
X0LIA = 37                    # Left top X value of grid
Y0TIA = 25                    # Left top Y value of grid
MouseX = MouseY = -10
MouseCAV = MouseCAI = MouseCBV = MouseCBI = MouseMuxA = MouseMuxB = MouseMuxC = MouseMuxD = -10
# Colors that can be modified
COLORframes = "#000080"   # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
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
COLORtraceR5 = "#800080"   # 50% magenta
COLORtraceR6 = "#800000"   # 80% red
COLORtraceR7 = "#4040a0"  # 80% purple
COLORtext = "#ffffff"     # 100% white
COLORtrigger = "#ff0000"  # 100% red
COLORsignalband = "#ff0000" # 100% red
# set value for on board resistors and ext AD584 reference
OnBoardRes = 50.83
AD584act = 2.5
# Set sample buffer size
HoldOff = 0.0
AWGSAMPLErate = 100000         # Sample rate of the AWG channels
SAMPLErate = AWGSAMPLErate # Scope sample rate can be decimated
MinSamples = 2000
MaxSamples = 200000
# set initial trigger conditions
TRIGGERlevel = 2.5          # Triggerlevel in volts
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
MathAxis = "V-A"
MathXAxis = "V-A"
MathYAxis = "V-B"
AWGAMathString = "(VBuffA + VBuffB)/2"
AWGBMathString = "(VBuffA + VBuffB)/2"
FFTUserWindowString = "numpy.kaiser(SMPfft, 14) * 3"
DigFilterAString = "numpy.sinc(numpy.linspace(-1, 1, 91))"
DigFilterBString = "numpy.sinc(numpy.linspace(-1, 1, 91))"
ChaMeasString1 = "DCV1"
ChaMeasString2 = "DCI1"
ChaMeasString3 = "SV1"
ChaMeasString4 = "MaxV1-MinV1"
ChaMeasString5 = "MaxI1-MinI1"
ChaMeasString6 = "math.sqrt(SV1**2 - DCV1**2)"
ChbMeasString1 = "DCV2"
ChbMeasString2 = "DCI2"
ChbMeasString3 = "SV2"
ChbMeasString4 = "MaxV2-MinV2"
ChbMeasString5 = "MaxI2-MinI2"
ChbMeasString6 = "math.sqrt(SV2**2 - DCV2**2)"
ChaLableSrring1 = "CHA-DCV "
ChaLableSrring2 = "CHA-DCI "
ChaLableSrring3 = "CHA-TRMS "
ChaLableSrring4 = "CHA-VP-P "
ChaLableSrring5 = "CHA-IP-P "
ChaLableSrring6 = "CHA-ACRMS "
ChbLableSrring1 = "CHB-DCV "
ChbLableSrring2 = "CHB-DCI "
ChbLableSrring3 = "CHB-TRMS "
ChbLableSrring4 = "CHB-VP-P "
ChbLableSrring5 = "CHB-IP-P "
ChbLableSrring6 = "CHB-ACRMS "
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
AWG_Amp_Mode = IntVar(0)
AWG_Amp_Mode.set(0) # 0 = Min/Max mode, 1 = Amp/Offset
#
ZEROstuffing = IntVar(0) # The zero stuffing value is 2 ** ZERO stuffing, calculated on initialize
ZEROstuffing.set(1)
FFTwindow = IntVar(0)   # FFT window function variable
FFTwindow.set(5)        # FFTwindow 0=None (rectangular B=1), 1=Cosine (B=1.24), 2=Triangular non-zero endpoints (B=1.33),
                        # 3=Hann (B=1.5), 4=Blackman (B=1.73), 5=Nuttall (B=2.02), 6=Flat top (B=3.77)
RelPhaseCorrection = 15 # Relative Phase error seems to be a random number each time board is powered up
RelPhaseCenter = IntVar(0)
RelPhaseCenter.set(0) # Center line value for phase plots
EnableCommandInterface = 0
EnableMuxMode = 1
EnableMinigenMode = 0
EnablePmodDA1Mode = 0
EnableDigPotMode = 0
EnableGenericSerialMode = 0
EnableAD5626SerialMode = 0
EnableDigitalFilter = 0
EnableMeasureScreen = 0
EnableETSScreen = 0
AllowFlashFirmware = 0
MouseFocus = 1
HistAsPercent = 0
ShowBallonHelp = 0
contloop = 0
discontloop = 0
AwgLayout = "Horz"
Style_String = 'alt'
MarkerLoc = 'UL' # can be UL, UR, LL or LR
CHA_TC1 = DoubleVar(0)
CHA_TC1.set(1)
CHA_TC2 = DoubleVar(0)
CHA_TC2.set(1)
CHB_TC1 = DoubleVar(0)
CHB_TC1.set(1)
CHB_TC2 = DoubleVar(0)
CHB_TC2.set(1)
CHA_A1 = DoubleVar(0)
CHA_A1.set(1)
CHA_A2 = DoubleVar(0)
CHA_A2.set(1)
CHB_A1 = DoubleVar(0)
CHB_A1.set(1)
CHB_A2 = DoubleVar(0)
CHB_A2.set(1)
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
DevID = "m1k"
# Vertical Sensitivity list in v/div
CHvpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
# Vertical Sensitivity list in mA/div
CHipdiv = (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)
# Time list in ms/div
TMpdiv = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0)
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
Reset_Freq = 300
#
DCV1 = DCV2 = MinV1 = MaxV1 = MinV2 = MaxV2 = MidV1 = PPV1 = MidV2 = PPV2 = SV1 = SI1 = 0
# Analog Mux channel measurement variables
DCVMuxA = MinVMuxA = MaxVMuxA = MidVMuxA = PPVMuxA = SVMuxA = 0
DCVMuxB = MinVMuxB = MaxVMuxB = MidVMuxB = PPVMuxB = SVMuxB = 0
DCVMuxC = MinVMuxC = MaxVMuxC = MidVMuxC = PPVMuxC = SVMuxC = 0
DCVMuxD = MinVMuxD = MaxVMuxD = MidVMuxD = PPVMuxD = SVMuxD = 0
DCI1 = DCI2 = MinI1 = MaxI1 = MinI2 = MaxI2 = MidI1 = PPI1 = MidI2 = PPI2 = SV2 = SI2 = 0
CHAperiod = CHAfreq = CHBperiod = CHBfreq = 0
# Calibration coefficients
CHAVGain = CHBVGain = 1.0
CHAVOffset = CHBVOffset = 0.0
# Initialisation of general variables
CHAOffset = CHBOffset = CHBAOffset = CHBBOffset = CHBCOffset = CHBDOffset = 2.5
CHAIOffset = CHBIOffset = InOffA = InGainA = InOffB = InGainB = 0.0
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
IBuffA = []
IBuffB = []
VBuffMA = []
VBuffMB = []
VBuffMC = []
VBuffMD = []
VmemoryMuxA = []
VmemoryMuxB = []
VmemoryMuxC = []
VmemoryMuxD = []
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

ETSStatus = IntVar(0)
ETSDisp = IntVar(0)
ETSDir = IntVar(0)
#
AWGAwaveform = []
AWGBwaveform = []
VmemoryA = numpy.ones(1)       # The memory for averaging
VmemoryB = numpy.ones(1)
ImemoryA = numpy.ones(1)       # The memory for averaging
ImemoryB = numpy.ones(1)
TRACEresetTime = True           # True for first new trace, false for averageing
TRACEresetFreq = True           # True for first new trace, false for averageing
AWGScreenStatus = IntVar(0)

T1Vline = []                # Voltage Trace line channel A
T2Vline = []                # Voltage Trace line channel B
T1Iline = []                # Current Trace line channel A
T2Iline = []                # Current Trace line channel B
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
T1VRline = []               # V reference Trace line channel A
T2VRline = []               # V reference Trace line channel B
T1IRline = []               # I reference Trace line channel A
T2IRline = []               # I reference Trace line channel B
TMRline = []                # Math reference Trace line
Triggerline = []            # Triggerline
Triggersymbol = []          # Trigger symbol
SHOWsamples = 2000          # Number of samples on the screen   
SCstart = 0                 # Start sample of the trace
HozPoss = 0.0
Is_Triggered = 0
#
TRACES = 1                  # Number of traces 1 or 2
TRACESread = 0              # Number of traces that have been read from ALM
ScreenTrefresh = IntVar(0)
ScreenXYrefresh = IntVar(0)
#
ZEROstuffing = IntVar(0) # The zero stuffing value is 2 ** ZERO stuffing, calculated on initialize
ZEROstuffing.set(1)
NSteps = IntVar(0)  # number of frequency sweep steps
NSteps.set(128)
LoopNum = IntVar(0)
LoopNum.set(1)
LastWindow = -1
LastSMPfft = 0
FBins = numpy.linspace(0, 50000, num=16384)
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
MathScreenStatus = IntVar(0)
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
PIO_0 = 28
PIO_1 = 29
PIO_2 = 47
PIO_3 = 3
#PIO_0 = 0
#PIO_1 = 1
#PIO_2 = 2
#PIO_3 = 3
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
    global TgInput, TgEdge, SingleShot, AutoLevel
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, Ysignal, AutoCenterA, AutoCenterB
    global CHAsb, CHAIsb, CHBsb, CHBIsb, HScale, FreqTraceMode
    global CHAsbxy, CHAIsbxy, CHBsbxy, CHBIsbxy, HoldOffentry
    global CHAVPosEntryxy, CHBVPosEntryxy, CHAIPosEntryxy, CHBIPosEntryxy
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I, MathTrace, MathXUnits, MathYUnits
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGATerm, AWGAMode, AWGARepeatFlag, AWGBRepeatFlag
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBPhaseEntry, AWGBShape, AWGBTerm, AWGBMode, AWGSync, AWGAIOMode, AWGBIOMode
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1, MeasDCI1, MeasMinI1
    global MeasMaxI1, MeasMidI1, MeasPPI1, MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2
    global MeasPPV2, MeasDCI2, MeasMinI2, MeasMaxI2, MeasMidI2, MeasPPI2, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasRMSI1, MeasRMSI2, MeasPhase
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC, DacScreenStatus, DigScreenStatus
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global SMPfftpwrTwo, SMPfft, StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, XYScreenStatus, IAScreenStatus, SpectrumScreenStatus
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry, AWGAPhaseDelay, AWGBPhaseDelay
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasDelay
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxScreenStatus, MuxEnb
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry, muxwindow
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry, HozPossentry
    global SmoothCurvesBP, SingleShotBP, bodewindow, AWG_Amp_Mode
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMarkerBP, BodeDisp
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP, ShowMathBP, ShowRMathBP
    global BPSweepMode, BPSweepCont, BodeScreenStatus, RevDate, SweepStepBodeEntry
    global HScaleBP, StopBodeEntry, StartBodeEntry, ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global MathAxis, MathXAxis, MathYAxis, Show_MathX, Show_MathY, MathScreenStatus, MathWindow
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2, RelPhaseCenter
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    
    # open Config file for Write
    ConfgFile = open(filename, "w")
    # Save Window placements
    ConfgFile.write("root.geometry('+" + str(root.winfo_x()) + '+' + str(root.winfo_y()) + "')\n")
    ConfgFile.write("awgwindow.geometry('+" + str(awgwindow.winfo_x()) + '+' + str(awgwindow.winfo_y()) + "')\n")
    ConfgFile.write('global GRW; GRW = ' + str(GRW) + '\n')
    ConfgFile.write('global GRH; GRH = ' + str(GRH) + '\n')
    # Windows configuration
    if MathScreenStatus.get() > 0:
        ConfgFile.write('NewEnterMathControls()\n')
        ConfgFile.write("MathWindow.geometry('+" + str(MathWindow.winfo_x()) + '+' + str(MathWindow.winfo_y()) + "')\n")
    else:
        ConfgFile.write('DestroyMathScreen()\n')
    if XYScreenStatus.get() > 0:
        ConfgFile.write('global GRWXY; GRWXY = ' + str(GRWXY) + '\n')
        ConfgFile.write('global GRHXY; GRHXY = ' + str(GRHXY) + '\n')
        ConfgFile.write('MakeXYWindow()\n')
        ConfgFile.write("xywindow.geometry('+" + str(xywindow.winfo_x()) + '+' + str(xywindow.winfo_y()) + "')\n")
        ConfgFile.write('CHAsbxy.delete(0,END)\n')
        ConfgFile.write('CHAsbxy.insert(0, ' + CHAsbxy.get() + ')\n')
        ConfgFile.write('CHAIsbxy.delete(0,END)\n')
        ConfgFile.write('CHAIsbxy.insert(0, ' + CHAIsbxy.get() + ')\n')
        ConfgFile.write('CHAVPosEntryxy.delete(0,END)\n')
        ConfgFile.write('CHAVPosEntryxy.insert(4, ' + CHAVPosEntryxy.get() + ')\n')
        ConfgFile.write('CHAIPosEntryxy.delete(0,END)\n')
        ConfgFile.write('CHAIPosEntryxy.insert(4, ' + CHAIPosEntryxy.get() + ')\n')
        ConfgFile.write('CHBsbxy.delete(0,END)\n')
        ConfgFile.write('CHBsbxy.insert(0, ' + CHBsbxy.get() + ')\n')
        ConfgFile.write('CHBIsbxy.delete(0,END)\n')
        ConfgFile.write('CHBIsbxy.insert(0, ' + CHBIsbxy.get() + ')\n')
        ConfgFile.write('CHBVPosEntryxy.delete(0,END)\n')
        ConfgFile.write('CHBVPosEntryxy.insert(4, ' + CHBVPosEntryxy.get() + ')\n')
        ConfgFile.write('CHBIPosEntryxy.delete(0,END)\n')
        ConfgFile.write('CHBIPosEntryxy.insert(4, ' + CHBIPosEntryxy.get() + ')\n')
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
        ConfgFile.write('RelPhaseCenter.set(' + str(RelPhaseCenter.get()) + ')\n')
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
    if DacScreenStatus.get() > 0:
        ConfgFile.write('MakeDacScreen()\n')
        ConfgFile.write("win1.geometry('+" + str(win1.winfo_x()) + '+' + str(win1.winfo_y()) + "')\n")
    else:
        ConfgFile.write('DestroyDacScreen()\n')
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
        ConfgFile.write('MuxEnb.set(' + str(MuxEnb.get()) + ')\n')
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
        ConfgFile.write('RelPhaseCenter.set(' + str(RelPhaseCenter.get()) + ')\n')
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
        ConfgFile.write('DestroyMeasuewScreen()\n')
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
    if ETSStatus.get() == 1: #
        ConfgFile.write('MakeETSWindow()\n')
        ConfgFile.write("etswindow.geometry('+" + str(etswindow.winfo_x()) + '+' + str(etswindow.winfo_y()) + "')\n")
        ConfgFile.write('ETSDisp.set(' + str(ETSDisp.get()) + ')\n')
        ConfgFile.write('ETSDir.set(' + str(ETSDir.get()) + ')\n')
        ConfgFile.write('FminEntry.delete(0,END)\n')
        ConfgFile.write('FminEntry.insert(6, ' + FminEntry.get() + ')\n')
        ConfgFile.write('DivXEntry.delete(0,END)\n')
        ConfgFile.write('DivXEntry.insert(4, ' + DivXEntry.get() + ')\n')
        ConfgFile.write('ETSts.delete(0,END)\n')
        ConfgFile.write('ETSts.insert(4, ' + ETSts.get() + ')\n')
    else:
        ConfgFile.write('DestroyETSScreen()\n')
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
    ConfgFile.write('ShowC1_I.set(' + str(ShowC1_I.get()) + ')\n')
    ConfgFile.write('ShowC2_V.set(' + str(ShowC2_V.get()) + ')\n')
    ConfgFile.write('ShowC2_I.set(' + str(ShowC2_I.get()) + ')\n')
    ConfgFile.write('Show_MathX.set(' + str(Show_MathX.get()) + ')\n')
    ConfgFile.write('Show_MathY.set(' + str(Show_MathY.get()) + ')\n')
    ConfgFile.write('AutoCenterA.set(' + str(AutoCenterA.get()) + ')\n')
    ConfgFile.write('AutoCenterB.set(' + str(AutoCenterB.get()) + ')\n')
    ConfgFile.write('TRACEmodeTime.set(' + str(TRACEmodeTime.get()) + ')\n')
    #
    ConfgFile.write('CHAVPosEntry.delete(0,END)\n')
    ConfgFile.write('CHAVPosEntry.insert(4, ' + CHAVPosEntry.get() + ')\n')
    ConfgFile.write('CHAIPosEntry.delete(0,END)\n')
    ConfgFile.write('CHAIPosEntry.insert(4, ' + CHAIPosEntry.get() + ')\n')
    ConfgFile.write('CHAsb.delete(0,END)\n')
    ConfgFile.write('CHAsb.insert(0, ' + CHAsb.get() + ')\n')
    ConfgFile.write('CHAIsb.delete(0,END)\n')
    ConfgFile.write('CHAIsb.insert(0, ' + CHAIsb.get() + ')\n')
    #
    ConfgFile.write('CHBVPosEntry.delete(0,END)\n')
    ConfgFile.write('CHBVPosEntry.insert(4, ' + CHBVPosEntry.get() + ')\n')
    ConfgFile.write('CHBIPosEntry.delete(0,END)\n')
    ConfgFile.write('CHBIPosEntry.insert(4, ' + CHBIPosEntry.get() + ')\n')
    ConfgFile.write('CHBsb.delete(0,END)\n')
    ConfgFile.write('CHBsb.insert(0, ' + CHBsb.get() + ')\n')
    ConfgFile.write('CHBIsb.delete(0,END)\n')
    ConfgFile.write('CHBIsb.insert(0, ' + CHBIsb.get() + ')\n')
    # AWG stuff
    ConfgFile.write('AWG_Amp_Mode.set('+ str(AWG_Amp_Mode.get()) + ')\n')
    ConfgFile.write('AWGAMode.set('+ str(AWGAMode.get()) + ')\n')
    ConfgFile.write('AWGAIOMode.set('+ str(AWGAIOMode.get()) + ')\n')
    ConfgFile.write('AWGATerm.set('+ str(AWGATerm.get()) + ')\n')
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
    ConfgFile.write('AWGARepeatFlag.set(' + str(AWGARepeatFlag.get()) + ')\n')
    #
    ConfgFile.write('AWGBMode.set('+ str(AWGBMode.get()) + ')\n')
    ConfgFile.write('AWGBIOMode.set('+ str(AWGBIOMode.get()) + ')\n')
    ConfgFile.write('AWGBTerm.set('+ str(AWGBTerm.get()) + ')\n')
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
    ConfgFile.write('AWGBRepeatFlag.set(' + str(AWGBRepeatFlag.get()) + ')\n')
    #
    ConfgFile.write('AWGSync.set(' + str(AWGSync.get()) + ')\n')
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
    ConfgFile.write('MeasDCI1.set(' + str(MeasDCI1.get()) + ')\n')
    ConfgFile.write('MeasMinI1.set(' + str(MeasMinI1.get()) + ')\n')
    ConfgFile.write('MeasMaxI1.set(' + str(MeasMaxI1.get()) + ')\n')
    ConfgFile.write('MeasMidI1.set(' + str(MeasMidI1.get()) + ')\n')
    ConfgFile.write('MeasPPI1.set(' + str(MeasPPI1.get()) + ')\n')
    ConfgFile.write('MeasRMSI1.set(' + str(MeasRMSI1.get()) + ')\n')
    ConfgFile.write('MeasDiffAB.set(' + str(MeasDiffAB.get()) + ')\n')
    ConfgFile.write('MeasDCV2.set(' + str(MeasDCV2.get()) + ')\n')
    ConfgFile.write('MeasMinV2.set(' + str(MeasMinV2.get()) + ')\n')
    ConfgFile.write('MeasMaxV2.set(' + str(MeasMaxV2.get()) + ')\n')
    ConfgFile.write('MeasBaseV2.set(' + str(MeasBaseV2.get()) + ')\n')
    ConfgFile.write('MeasTopV2.set(' + str(MeasTopV2.get()) + ')\n')
    ConfgFile.write('MeasMidV2.set(' + str(MeasMidV2.get()) + ')\n')
    ConfgFile.write('MeasPPV2.set(' + str(MeasPPV2.get()) + ')\n')
    ConfgFile.write('MeasRMSV2.set(' + str(MeasRMSV2.get()) + ')\n')
    ConfgFile.write('MeasDCI2.set(' + str(MeasDCI2.get()) + ')\n')
    ConfgFile.write('MeasMinI2.set(' + str(MeasMinI2.get()) + ')\n')
    ConfgFile.write('MeasMaxI2.set(' + str(MeasMaxI2.get()) + ')\n')
    ConfgFile.write('MeasMidI2.set(' + str(MeasMidI2.get()) + ')\n')
    ConfgFile.write('MeasPPI2.set(' + str(MeasPPI2.get()) + ')\n')
    ConfgFile.write('MeasRMSI2.set(' + str(MeasRMSI2.get()) + ')\n')
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
    #
    ConfgFile.write('CHAIGainEntry.delete(0,END)\n')
    ConfgFile.write('CHAIGainEntry.insert(4, ' + CHAIGainEntry.get() + ')\n')
    ConfgFile.write('CHBIGainEntry.delete(0,END)\n')
    ConfgFile.write('CHBIGainEntry.insert(4, ' + CHBIGainEntry.get() + ')\n')
    ConfgFile.write('CHAIOffsetEntry.delete(0,END)\n')
    ConfgFile.write('CHAIOffsetEntry.insert(4, ' + CHAIOffsetEntry.get() + ')\n')
    ConfgFile.write('CHBIOffsetEntry.delete(0,END)\n')
    ConfgFile.write('CHBIOffsetEntry.insert(4, ' + CHBIOffsetEntry.get() + ')\n')
    # Save strings
    ConfgFile.write('global MathString; MathString = "' + MathString + '"\n')
    ConfgFile.write('global MathXString; MathXString = "' + MathXString + '"\n')
    ConfgFile.write('global MathYString; MathYString = "' + MathYString + '"\n')
    ConfgFile.write('global UserAString; UserAString = "' + UserAString + '"\n')
    ConfgFile.write('global MathXUnits; MathXSUnits = "' + MathXUnits + '"\n')
    ConfgFile.write('global MathYUnits; MathYUnits = "' + MathYUnits + '"\n')
    ConfgFile.write('global UserALabel; UserALabel = "' + UserALabel + '"\n')
    ConfgFile.write('global UserBString; UserBString = "' + UserBString + '"\n')
    ConfgFile.write('global UserBLabel; UserBLabel = "' + UserBLabel + '"\n')
    ConfgFile.write('global MathAxis; MathAxis = "' + MathAxis + '"\n')
    ConfgFile.write('global MathXAxis; MathXAxis = "' + MathXAxis + '"\n')
    ConfgFile.write('global MathYAxis; MathYAxis = "' + MathYAxis + '"\n')
    ConfgFile.write('global AWGAMathString; AWGAMathString = "' + AWGAMathString + '"\n')
    ConfgFile.write('global AWGBMathString; AWGBMathString = "' + AWGBMathString + '"\n')
    ConfgFile.write('global FFTUserWindowString; FFTUserWindowString= "' +  FFTUserWindowString + '"\n')
    ConfgFile.write('global DigFilterAString; DigFilterAString = "' + DigFilterAString + '"\n')
    ConfgFile.write('global DigFilterBString; DigFilterBString = "' + DigFilterBString + '"\n')
    # save channel AC frequency compensation settings
    try:
        CHA_TC1.set(float(cha_TC1Entry.get()))
        CHA_TC2.set(float(cha_TC2Entry.get()))
        CHB_TC1.set(float(chb_TC1Entry.get()))
        CHB_TC2.set(float(chb_TC2Entry.get()))
        CHA_A1.set(float(cha_A1Entry.get()))
        CHA_A2.set(float(cha_A2Entry.get()))
        CHB_A1.set(float(chb_A1Entry.get()))
        CHB_A2.set(float(chb_A2Entry.get()))
    except:
        donothing()   
    ConfgFile.write('CHA_RC_HP.set(' + str(CHA_RC_HP.get()) + ')\n')
    ConfgFile.write('CHB_RC_HP.set(' + str(CHB_RC_HP.get()) + ')\n')
    ConfgFile.write('CHA_TC1.set(' + str(CHA_TC1.get()) + ')\n')
    ConfgFile.write('CHA_TC2.set(' + str(CHA_TC2.get()) + ')\n')
    ConfgFile.write('CHB_TC1.set(' + str(CHB_TC1.get()) + ')\n')
    ConfgFile.write('CHB_TC2.set(' + str(CHB_TC2.get()) + ')\n')
    ConfgFile.write('CHA_A1.set(' + str(CHA_A1.get()) + ')\n')
    ConfgFile.write('CHA_A2.set(' + str(CHA_A2.get()) + ')\n')
    ConfgFile.write('CHB_A1.set(' + str(CHB_A1.get()) + ')\n')
    ConfgFile.write('CHB_A2.set(' + str(CHB_A2.get()) + ')\n')
    ConfgFile.write('cha_TC1Entry.delete(0,END)\n')
    ConfgFile.write('cha_TC1Entry.insert(4, ' + str(CHA_TC1.get()) + ')\n')
    ConfgFile.write('cha_TC2Entry.delete(0,END)\n')
    ConfgFile.write('cha_TC2Entry.insert(4, ' + str(CHA_TC2.get()) + ')\n')
    ConfgFile.write('chb_TC1Entry.delete(0,END)\n')
    ConfgFile.write('chb_TC1Entry.insert(4, ' + str(CHB_TC1.get()) + ')\n')
    ConfgFile.write('chb_TC2Entry.delete(0,END)\n')
    ConfgFile.write('chb_TC2Entry.insert(4, ' + str(CHB_TC2.get()) + ')\n')
    ConfgFile.write('cha_A1Entry.delete(0,END)\n')
    ConfgFile.write('cha_A1Entry.insert(4, ' + str(CHA_A1.get()) + ')\n')
    ConfgFile.write('cha_A2Entry.delete(0,END)\n')
    ConfgFile.write('cha_A2Entry.insert(4, ' + str(CHA_A2.get()) + ')\n')
    ConfgFile.write('chb_A1Entry.delete(0,END)\n')
    ConfgFile.write('chb_A1Entry.insert(4, ' + str(CHB_A1.get()) + ')\n')
    ConfgFile.write('chb_A2Entry.delete(0,END)\n')
    ConfgFile.write('chb_A2Entry.insert(4, ' + str(CHB_A2.get()) + ')\n')

    # extra Spectrum stuff
    if SpectrumScreenStatus.get() > 0 or IAScreenStatus.get() > 0 or BodeScreenStatus.get() > 0:
        ConfgFile.write('SMPfftpwrTwo.set(' + str(SMPfftpwrTwo.get()) + ')\n')
        ConfgFile.write('FFTwindow.set(' + str(FFTwindow.get()) + ')\n')
        ConfgFile.write('ZEROstuffing.set(' + str(ZEROstuffing.get()) + ')\n')
        ConfgFile.write('Vdiv.set(' + str(Vdiv.get()) + ')\n')
        #
        ConfgFile.write('DBdivindex.set(' + str(DBdivindex.get()) + ')\n')
        ConfgFile.write('DBlevel.set(' + str(DBlevel.get()) + ')\n')
        # ConfgFile.write('TRACEaverage.set(' + str(TRACEaverage.get()) + ')\n')
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
    global TgInput, TgEdge, SingleShot, AutoLevel
    global root, freqwindow, awgwindow, iawindow, xywindow, win1, win2
    global TRIGGERentry, TMsb, Xsignal, Ysignal, AutoCenterA, AutoCenterB
    global CHAsb, CHAIsb, CHBsb, CHBIsb, HScale, FreqTraceMode
    global CHAsbxy, CHAIsbxy, CHBsbxy, CHBIsbxy, HoldOffentry
    global CHAVPosEntryxy, CHBVPosEntryxy, CHAIPosEntryxy, CHBIPosEntryxy
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I, MathTrace, MathXUnits, MathYUnits
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry, HozPossentry
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGADutyCycleEntry
    global AWGAPhaseEntry, AWGAShape, AWGATerm, AWGAMode, AWGARepeatFlag, AWGBRepeatFlag
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBDutyCycleEntry
    global AWGBPhaseEntry, AWGBShape, AWGBTerm, AWGBMode, AWGSync, AWGAIOMode, AWGBIOMode
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1, MeasDCI1, MeasMinI1
    global MeasMaxI1, MeasMidI1, MeasPPI1, MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2
    global MeasPPV2, MeasDCI2, MeasMinI2, MeasMaxI2, MeasMidI2, MeasPPI2, MeasDiffAB, MeasDiffBA
    global MeasRMSV1, MeasRMSV2, MeasRMSI1, MeasRMSI2, MeasPhase, MeasDelay
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, CutDC, AWG_Amp_Mode
    global FFTwindow, DBdivindex, DBlevel, TRACEmodeTime, TRACEaverage, Vdiv
    global SMPfftpwrTwo, SMPfft, StartFreqEntry, StopFreqEntry, ZEROstuffing
    global TimeDisp, XYDisp, FreqDisp, IADisp, AWGAPhaseDelay, AWGBPhaseDelay
    global RsystemEntry, ResScale, GainCorEntry, PhaseCorEntry
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxScreenStatus, MuxEnb
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry, muxwindow
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global MathString, MathXString, MathYString, UserAString, UserALabel, UserBString, UserBLabel
    global MathAxis, MathXAxis, MathYAxis, Show_MathX, Show_MathY, MathScreenStatus, MathWindow
    global AWGAMathString, AWGBMathString, FFTUserWindowString, DigFilterAString, DigFilterBString
    global GRWF, GRHF, GRWBP, GRHBP, GRWXY, GRHXY, GRWIA, GRHIA, MeasureStatus
    global ChaLableSrring1, ChaLableSrring2, ChaLableSrring3, ChaLableSrring4, ChaLableSrring5, ChaLableSrring6
    global ChbLableSrring1, ChbLableSrring2, ChbLableSrring3, ChbLableSrring4, ChbLableSrring5, ChbLableSrring6
    global ChaMeasString1, ChaMeasString2, ChaMeasString3, ChaMeasString4, ChaMeasString5, ChaMeasString6
    global ChbMeasString1, ChbMeasString2, ChbMeasString3, ChbMeasString4, ChbMeasString5, ChbMeasString6
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2, RelPhaseCenter
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    
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
            BAWGAModeLabel()
            BAWGBModeLabel()
            BAWGAPhaseDelay()
            BAWGBPhaseDelay()
        TimeCheckBox()
        XYCheckBox()
        FreqCheckBox()
        BodeCheckBox()
        IACheckBox()
        OhmCheckBox()
#
        time.sleep(0.05)
        if AWGAShape.get()==9:
            AWGAMakeImpulse()
        elif AWGAShape.get()==11:
            AWGAMakeTrapazoid()
        elif AWGAShape.get()==15:
            AWGAMakeSSQ()
        elif AWGAShape.get()==16:
            AWGAMakeRamp()
        elif AWGAShape.get()==17:
            AWGAMakePWMSine()
        elif AWGAShape.get()==18:
            AWGAMakeBodeSine()
        elif AWGAShape.get()==12:
            AWGAMakeUpDownRamp()
        elif AWGAShape.get()==14:
            AWGAMakeFourier()
        elif AWGAShape.get()==7:
            AWGAMakeUUNoise()
        elif AWGAShape.get()==8:
            AWGAMakeUGNoise()
#
        if AWGBShape.get()==9:
            AWGBMakeImpulse()
        elif AWGBShape.get()==11:
            AWGBMakeTrapazoid()
        elif AWGBShape.get()==15:
            AWGBMakeSSQ()
        elif AWGBShape.get()==16:
            AWGBMakeRamp()
        elif AWGBShape.get()==17:
            AWGBMakePWMSine()
        elif AWGBShape.get()==18:
            AWGBMakeBodeSine()
        elif AWGBShape.get()==12:
            AWGBMakeUpDownRamp()
        elif AWGBShape.get()==14:
            AWGBMakeFourier()
        elif AWGBShape.get()==7:
            AWGBMakeUUNoise()
        elif AWGBShape.get()==8:
            AWGBMakeUGNoise()
        else:
            UpdateAwgCont()
        time.sleep(0.05)
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
    else:    # temp chnage text corlor to black
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
    global VBuffA, VBuffB, IBuffA, IBuffB, SAMPLErate

    # open file to save data
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
    DataFile = open(filename, 'w')
    DataFile.write( 'Sample-#, CA-V, CA-I, CB-V, CB-I \n' )
    for index in range(len(VBuffA)):
        TimePnt = float((index+0.0)/SAMPLErate)
        DataFile.write( str(TimePnt) + ', ' + str(VBuffA[index]) + ', ' + str(IBuffA[index]) + ', '
                        + str(VBuffB[index]) + ', ' + str(IBuffB[index]) + '\n')
    DataFile.close()
#
def BSaveChannelData():
    global SAMPLErate, VBuffA, VBuffB, IBuffA, IBuffB

    # ask user for channel to save
    Channel = askstring("Choose Channel", "CA-V, CB-V, CA-I or CB-I\n\nChannel:\n", initialvalue="CA-V")
    if (Channel == None):         # If Cancel pressed, then None
        return
    # open file to save data
    filename = asksaveasfilename(defaultextension = ".txt", filetypes=[("Text Columns", "*.txt")])
    DataFile = open(filename, 'w')
    for index in range(len(VBuffA)):
        TimePnt = float((index+0.0)/SAMPLErate)
        if Channel == "CA-V":
            DataFile.write( str(TimePnt) + ', ' + str(VBuffA[index]) + '\n')
        elif Channel == "CA-I":
            DataFile.write( str(TimePnt) + ', ' + str(IBuffA[index]) + '\n')
        elif Channel == "CB-V":
            DataFile.write( str(TimePnt) + ', ' + str(VBuffB[index]) + '\n')
        elif Channel == "CB-I":
            DataFile.write( str(TimePnt) + ', ' + str(IBuffB[index]) + '\n')
    DataFile.close()
#
def BReadData():
    global VBuffA, VBuffB, IBuffA, IBuffB, SHOWsamples

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")])
    try:
        CSVFile = open(filename)
        dialect = csv.Sniffer().sniff(CSVFile.read(2048))
        CSVFile.seek(0)
        csv_f = csv.reader(CSVFile, dialect)
        VBuffA = []
        VBuffB = []
        IBuffA = []
        IBuffB = []
        SHOWsamples = 0
        for row in csv_f:
            try:
                VBuffA.append(float(row[1]))
                IBuffA.append(float(row[2]))
                VBuffB.append(float(row[3]))
                IBuffB.append(float(row[4]))
                SHOWsamples = SHOWsamples + 1
            except:
                print 'skipping non-numeric row'
        VBuffA = numpy.array(VBuffA)
        IBuffA = numpy.array(IBuffA)
        VBuffB = numpy.array(VBuffB)
        IBuffB = numpy.array(IBuffB)
        CSVFile.close()
        UpdateTimeTrace()
    except:
        showwarning("WARNING","No such file found or wrong format!")
#
def BHelp():
    # open a URL, in this case, the ALICE desk-top-users-guide
    url = "https://wiki.analog.com/university/tools/m1k/alice/desk-top-users-guide"
    webbrowser.open(url,new=2)

def BAbout():
    global RevDate, FWRevOne, HWRevOne, DevID, Version_url
    # show info on software / firmware / hardware
    try:
        u = urllib2.urlopen(Version_url)
        meta = u.info()
        time_string = str(meta.getheaders("Last-Modified"))
    except:
        time_string = "Unavailable"
    print time_string
    showinfo("About ALICE", "ALICE DeskTop 1.2 " + RevDate + "\n" +
             "Latest Version: " + time_string[7:18] + "\n" +
             "ADALM1000 Hardware Rev " + str(HWRevOne) + "\n" +
             "Firmware Rev " + str(FWRevOne) + "\n" +
             "Board Serial Number " + DevID + "\n" +
             "Software is provided as is without any Warranty")
    
def BSnapShot():
    global T1Vline, T2Vline, T1Iline, T2Iline
    global TXYline, Tmathline, TMRline, TXYRline
    global T1VRline, T2VRline, T1IRline, T2IRline, TMCVline, TMDVline
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I, ShowMath, MathTrace
    global MuxScreenStatus, TMCRline, TMBRline, TMAVline, TMBVline, TMCVline, TMDVline
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxEnb

    if ShowC1_V.get() == 1:
        T1VRline = T1Vline               # V reference Trace line channel A
    if ShowC2_V.get() == 1:
        T2VRline = T2Vline               # V reference Trace line channel B
    if ShowC1_I.get() == 1:
        T1IRline = T1Iline               # I reference Trace line channel A
    if ShowC2_I.get() == 1:
        T2IRline = T2Iline               # I reference Trace line channel B
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
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global DevID
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry

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
    CalFile.write('CHAIGainEntry.delete(0,END)\n')
    CalFile.write('CHAIGainEntry.insert(4, ' + CHAIGainEntry.get() + ')\n')
    CalFile.write('CHBIGainEntry.delete(0,END)\n')
    CalFile.write('CHBIGainEntry.insert(4, ' + CHBIGainEntry.get() + ')\n')
    CalFile.write('CHAIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAIOffsetEntry.insert(4, ' + CHAIOffsetEntry.get() + ')\n')
    CalFile.write('CHBIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBIOffsetEntry.insert(4, ' + CHBIOffsetEntry.get() + ')\n')
    #
    # save channel AC frequency compensation settings
    try:
        CHA_TC1.set(float(cha_TC1Entry.get()))
        CHA_TC2.set(float(cha_TC2Entry.get()))
        CHB_TC1.set(float(chb_TC1Entry.get()))
        CHB_TC2.set(float(chb_TC2Entry.get()))
        CHA_A1.set(float(cha_A1Entry.get()))
        CHA_A2.set(float(cha_A2Entry.get()))
        CHB_A1.set(float(chb_A1Entry.get()))
        CHB_A2.set(float(chb_A2Entry.get()))
    except:
        donothing()   
    CalFile.write('CHA_RC_HP.set(' + str(CHA_RC_HP.get()) + ')\n')
    CalFile.write('CHB_RC_HP.set(' + str(CHB_RC_HP.get()) + ')\n')
    CalFile.write('CHA_TC1.set(' + str(CHA_TC1.get()) + ')\n')
    CalFile.write('CHA_TC2.set(' + str(CHA_TC2.get()) + ')\n')
    CalFile.write('CHB_TC1.set(' + str(CHB_TC1.get()) + ')\n')
    CalFile.write('CHB_TC2.set(' + str(CHB_TC2.get()) + ')\n')
    CalFile.write('CHA_A1.set(' + str(CHA_A1.get()) + ')\n')
    CalFile.write('CHA_A2.set(' + str(CHA_A2.get()) + ')\n')
    CalFile.write('CHB_A1.set(' + str(CHB_A1.get()) + ')\n')
    CalFile.write('CHB_A2.set(' + str(CHB_A2.get()) + ')\n')
    CalFile.write('cha_TC1Entry.delete(0,END)\n')
    CalFile.write('cha_TC1Entry.insert(4, ' + str(CHA_TC1.get()) + ')\n')
    CalFile.write('cha_TC2Entry.delete(0,END)\n')
    CalFile.write('cha_TC2Entry.insert(4, ' + str(CHA_TC2.get()) + ')\n')
    CalFile.write('chb_TC1Entry.delete(0,END)\n')
    CalFile.write('chb_TC1Entry.insert(4, ' + str(CHB_TC1.get()) + ')\n')
    CalFile.write('chb_TC2Entry.delete(0,END)\n')
    CalFile.write('chb_TC2Entry.insert(4, ' + str(CHB_TC2.get()) + ')\n')
    CalFile.write('cha_A1Entry.delete(0,END)\n')
    CalFile.write('cha_A1Entry.insert(4, ' + str(CHA_A1.get()) + ')\n')
    CalFile.write('cha_A2Entry.delete(0,END)\n')
    CalFile.write('cha_A2Entry.insert(4, ' + str(CHA_A2.get()) + ')\n')
    CalFile.write('chb_A1Entry.delete(0,END)\n')
    CalFile.write('chb_A1Entry.insert(4, ' + str(CHB_A1.get()) + ')\n')
    CalFile.write('chb_A2Entry.delete(0,END)\n')
    CalFile.write('chb_A2Entry.insert(4, ' + str(CHB_A2.get()) + ')\n')

    CalFile.close()

def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global DevID
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry

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
def NewEnterMathControls():
    global RUNstatus, MathScreenStatus, MathWindow
    global MathString, MathUnits, MathXString, MathXUnits, MathYString, MathYUnits
    global MathAxis, MathXAxis, MathYAxis, MathTrace
    global formentry, unitsentry, axisentry, xformentry, xunitsentry, xaxisentry, yformentry, yunitsentry, yaxisentry
    global formlab, xformlab, yformlab
    
    if MathScreenStatus.get() == 0:
        MathScreenStatus.set(1)
        #
        MathWindow = Toplevel()
        MathWindow.title("Math Formula " + RevDate)
        MathWindow.resizable(FALSE,FALSE)
        MathWindow.protocol("WM_DELETE_WINDOW", DestroyMathScreen)
        frame1 = LabelFrame(MathWindow, text="Built-in Exp", style="A10R1.TLabelframe")
        frame2 = LabelFrame(MathWindow, text="Math Trace", style="A10R1.TLabelframe")
        frame3 = LabelFrame(MathWindow, text="X Math Trace", style="A10R1.TLabelframe")
        frame4 = LabelFrame(MathWindow, text="Y Math Trace", style="A10R1.TLabelframe")
        # frame1.grid(row=0, column=0, sticky=W)
        #
        frame1.grid(row = 0, column=0, rowspan=3, sticky=W)
        frame2.grid(row = 0, column=1, sticky=W)
        frame3.grid(row = 1, column=1, sticky=W)
        frame4.grid(row = 2, column=1, sticky=W)
        #
        # Built in functions
        # 
        rb1 = Radiobutton(frame1, text='none', variable=MathTrace, value=0, command=UpdateTimeTrace)
        rb1.grid(row=0, column=0, sticky=W)
        rb2 = Radiobutton(frame1, text='CAV+CBV', variable=MathTrace, value=1, command=UpdateTimeTrace)
        rb2.grid(row=1, column=0, sticky=W)
        rb3 = Radiobutton(frame1, text='CAV-CBV', variable=MathTrace, value=2, command=UpdateTimeTrace)
        rb3.grid(row=2, column=0, sticky=W)
        rb4 = Radiobutton(frame1, text='CBV-CAV', variable=MathTrace, value=3, command=UpdateTimeTrace)
        rb4.grid(row=3, column=0, sticky=W)
        rb5 = Radiobutton(frame1, text='CAI-CBI', variable=MathTrace, value=8, command=UpdateTimeTrace)
        rb5.grid(row=4, column=0, sticky=W)
        rb6 = Radiobutton(frame1, text='CBI-CAI', variable=MathTrace, value=9, command=UpdateTimeTrace)
        rb6.grid(row=5, column=0, sticky=W)
        rb7 = Radiobutton(frame1, text='CAV*CAI', variable=MathTrace, value=4, command=UpdateTimeTrace)
        rb7.grid(row=6, column=0, sticky=W)
        rb8 = Radiobutton(frame1, text='CBV*CBI', variable=MathTrace, value=5, command=UpdateTimeTrace)
        rb8.grid(row=7, column=0, sticky=W)
        rb9 = Radiobutton(frame1, text='CAV/CAI', variable=MathTrace, value=6, command=UpdateTimeTrace)
        rb9.grid(row=8, column=0, sticky=W)
        rb10 = Radiobutton(frame1, text='CBV/CBI', variable=MathTrace, value=7, command=UpdateTimeTrace)
        rb10.grid(row=9, column=0, sticky=W)
        rb11 = Radiobutton(frame1, text='CBV/CAV', variable=MathTrace, value=10, command=UpdateTimeTrace)
        rb11.grid(row=10, column=0, sticky=W)
        rb12 = Radiobutton(frame1, text='CBI/CAI', variable=MathTrace, value=11, command=UpdateTimeTrace)
        rb12.grid(row=11, column=0, sticky=W)
        rb13 = Radiobutton(frame1, text='Formula', variable=MathTrace, value=12, command=UpdateTimeTrace)
        rb13.grid(row=12, column=0, sticky=W)
        # 
        # Math trace formula sub frame2
        #
        sframe2a = Frame( frame2 )
        sframe2a.pack(side=TOP)
        formlab = Label(sframe2a, text="Formula ", style= "A10B.TLabel")
        formlab.grid(row=0, column=0, sticky=W)
        formlab.pack(side=LEFT)
        formentry = Entry(sframe2a, width=23)
        formentry.grid(row=0, column=1, sticky=W)
        formentry.pack(side=LEFT)
        formentry.delete(0,"end")
        formentry.insert(0,MathString)
        sframe2b = Frame( frame2 )
        sframe2b.pack(side=TOP)
        unitslab = Label(sframe2b, text="Units ", style= "A10B.TLabel")
        unitslab.grid(row=0, column=0, sticky=W)
        unitslab.pack(side=LEFT)
        unitsentry = Entry(sframe2b, width=6)
        unitsentry.grid(row=0, column=1, sticky=W)
        unitsentry.pack(side=LEFT)
        unitsentry.delete(0,"end")
        unitsentry.insert(0,MathUnits)
        checkbt = Button(sframe2b, text="Check", command=CheckMathString )
        checkbt.grid(row=0, column=2, sticky=W)
        checkbt.pack(side=LEFT)
        sframe2c = Frame( frame2 )
        sframe2c.pack(side=TOP)
        axislab = Label(sframe2c, text="Axis ", style= "A10B.TLabel")
        axislab.grid(row=0, column=0, sticky=W)
        axislab.pack(side=LEFT)
        axisentry = Entry(sframe2c, width=3)
        axisentry.grid(row=0, column=1, sticky=W)
        axisentry.pack(side=LEFT)
        axisentry.delete(0,"end")
        axisentry.insert(0,MathAxis)
        applybt = Button(sframe2c, text="Apply", command=ApplyMathString )
        applybt.grid(row=0, column=2, sticky=W)
        applybt.pack(side=LEFT)
        # 
        # X Math trace formula sub frame3
        #
        sframe3a = Frame( frame3 )
        sframe3a.pack(side=TOP)
        xformlab = Label(sframe3a, text=" X Formula ", style= "A10B.TLabel")
        xformlab.grid(row=0, column=0, sticky=W)
        xformlab.pack(side=LEFT)
        xformentry = Entry(sframe3a, width=20)
        xformentry.grid(row=0, column=1, sticky=W)
        xformentry.pack(side=LEFT)
        xformentry.delete(0,"end")
        xformentry.insert(0, MathXString)
        sframe3b = Frame( frame3 )
        sframe3b.pack(side=TOP)
        xunitslab = Label(sframe3b, text="X Units ", style= "A10B.TLabel")
        xunitslab.grid(row=0, column=0, sticky=W)
        xunitslab.pack(side=LEFT)
        xunitsentry = Entry(sframe3b, width=6)
        xunitsentry.grid(row=0, column=1, sticky=W)
        xunitsentry.pack(side=LEFT)
        xunitsentry.delete(0,"end")
        xunitsentry.insert(0, MathXUnits)
        xcheckbt = Button(sframe3b, text="Check", command=CheckMathXString )
        xcheckbt.grid(row=0, column=2, sticky=W)
        xcheckbt.pack(side=LEFT)
        sframe3c = Frame( frame3 )
        sframe3c.pack(side=TOP)
        xaxislab = Label(sframe3c, text="X Axis ", style= "A10B.TLabel")
        xaxislab.grid(row=0, column=0, sticky=W)
        xaxislab.pack(side=LEFT)
        xaxisentry = Entry(sframe3c, width=3)
        xaxisentry.grid(row=0, column=1, sticky=W)
        xaxisentry.pack(side=LEFT)
        xaxisentry.delete(0,"end")
        xaxisentry.insert(0, MathXAxis)
        xapplybt = Button(sframe3c, text="Apply", command=ApplyMathXString )
        xapplybt.grid(row=0, column=3, sticky=W)
        xapplybt.pack(side=LEFT)
        # 
        # Math trace formula sub frame4
        #
        sframe4a = Frame( frame4 )
        sframe4a.pack(side=TOP)
        yformlab = Label(sframe4a, text="Y Formula ", style= "A10B.TLabel")
        yformlab.grid(row=0, column=0, sticky=W)
        yformlab.pack(side=LEFT)
        yformentry = Entry(sframe4a, width=20)
        yformentry.grid(row=0, column=1, sticky=W)
        yformentry.pack(side=LEFT)
        yformentry.delete(0,"end")
        yformentry.insert(0,MathYString)
        sframe4b = Frame( frame4 )
        sframe4b.pack(side=TOP)
        yunitslab = Label(sframe4b, text="Y Units ", style= "A10B.TLabel")
        yunitslab.grid(row=0, column=0, sticky=W)
        yunitslab.pack(side=LEFT)
        yunitsentry = Entry(sframe4b, width=6)
        yunitsentry.grid(row=0, column=1, sticky=W)
        yunitsentry.pack(side=LEFT)
        yunitsentry.delete(0,"end")
        yunitsentry.insert(0,MathYUnits)
        ycheckbt = Button(sframe4b, text="Check", command=CheckMathYString )
        ycheckbt.grid(row=0, column=2, sticky=W)
        ycheckbt.pack(side=LEFT)
        sframe4c = Frame( frame4 )
        sframe4c.pack(side=TOP)
        yaxislab = Label(sframe4c, text="Y Axis ", style= "A10B.TLabel")
        yaxislab.grid(row=0, column=0, sticky=W)
        yaxislab.pack(side=LEFT)
        yaxisentry = Entry(sframe4c, width=3)
        yaxisentry.grid(row=0, column=1, sticky=W)
        yaxisentry.pack(side=LEFT)
        yaxisentry.delete(0,"end")
        yaxisentry.insert(0,MathYAxis)
        yapplybt = Button(sframe4c, text="Apply", command=ApplyMathYString )
        yapplybt.grid(row=0, column=3, sticky=W)
        yapplybt.pack(side=LEFT)

        dismissbutton = Button(MathWindow, text="Dismiss", command=DestroyMathScreen)
        dismissbutton.grid(row=3, column=0, sticky=W)
        
    if RUNstatus.get() > 0:
        UpdateTimeTrace()
#
def DestroyMathScreen():
    global MathScreenStatus, MathWindow
    
    if MathScreenStatus.get() == 1:
        MathScreenStatus.set(0)
        MathWindow.destroy()

def CheckMathString():
    global MathString, formentry, MathUnits, unitsentry, MathAxis, axisentry, formlab
    global VBuffA, VBuffB, IBuffA, IBuffB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global Show_MathX, Show_MathY
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2

    t = 0
    TempString = formentry.get()
    try:
        MathResult = eval(TempString)
        formlab.configure(text="Formula ", style= "A10G.TLabel")
    except:
        formlab.configure(text="Formula ", style= "A10R.TLabel")

def CheckMathXString():
    global MathXString, xformentry, MathXUnits, xunitsentry, MathXAxis, xaxisentry, xformlab
    global VBuffA, VBuffB, IBuffA, IBuffB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global Show_MathX, Show_MathY
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2

    t = 0
    TempString = xformentry.get()
    try:
        MathResult = eval(TempString)
        xformlab.configure(text="X Formula ", style= "A10G.TLabel")
    except:
        xformlab.configure(text="X Formula ", style= "A10R.TLabel")

def CheckMathYString():
    global MathYString, yformentry, MathYUnits, yunitsentry, MathYAxis, yaxisentry, yformlab
    global VBuffA, VBuffB, IBuffA, IBuffB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global Show_MathX, Show_MathY
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2

    t = 0
    TempString = yformentry.get()
    try:
        MathResult = eval(TempString)
        yformlab.configure(text="Y Formula ", style= "A10G.TLabel")
    except:
        yformlab.configure(text="Y Formula ", style= "A10R.TLabel")

    
def ApplyMathString():
    global MathString, formentry, MathUnits, unitsentry, MathAxis, axisentry

    MathString = formentry.get()
    MathUnits = unitsentry.get()
    MathAxis = axisentry.get()

def ApplyMathXString():
    global MathXString, xformentry, MathXUnits, xunitsentry, MathXAxis, xaxisentry

    MathXString = xformentry.get()
    MathXUnits = xunitsentry.get()
    MathXAxis = xaxisentry.get()

def ApplyMathYString():
    global MathYString, yformentry, MathYUnits, yunitsentry, MathYAxis, yaxisentry

    MathYString = yformentry.get()
    MathYUnits = yunitsentry.get()
    MathYAxis = yaxisentry.get()
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
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I
    ShowC1_V.set(1)
    ShowC1_I.set(1)
    ShowC2_V.set(1)
    ShowC2_I.set(1)
    UpdateTimeTrace()

def BShowCurvesNone():
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I
    ShowC1_V.set(0)
    ShowC1_I.set(0)
    ShowC2_V.set(0)
    ShowC2_I.set(0)
    UpdateTimeTrace()
    
def BTriggerEdge():
    global TgEdge
                                       
# TRIGCOND trigcondRisingPositive = 0
# TRIGCOND trigcondFallingNegative = 1

def BTrigger50p():
    global TgInput, TRIGGERlevel, TRIGGERentry
    global MaxV1, MinV1, MaxV2, MinV2
    global MaxI1, MinI1, MaxI2, MinI2
    # set new trigger level to mid point of waveform    
    MidV1 = (MaxV1+MinV1)/2
    MidV2 = (MaxV2+MinV2)/2
    MidI1 = (MaxI1+MinI1)/2
    MidI2 = (MaxI2+MinI2)/2
    if (TgInput.get() == 0):
        DCString = "0.0"
    elif (TgInput.get() == 1 ):
        DCString = ' {0:.2f} '.format(MidV1)
    elif (TgInput.get() == 2 ):
        DCString = ' {0:.2f} '.format(MidI1)
    elif (TgInput.get() == 3 ):
        DCString = ' {0:.2f} '.format(MidV2)
    elif (TgInput.get() == 4 ):
        DCString = ' {0:.2f} '.format(MidI2)

    TRIGGERlevel = eval(DCString)
    TRIGGERentry.delete(0,END)
    TRIGGERentry.insert(4, DCString)
    
    UpdateTimeTrace()           # Always Update
    
def BTriggerMode(): # place holder for future hardware triggering if implemented
    global TgInput

#    if (TgInput.get() == 0):
        # no trigger
#    elif (TgInput.get() == 1):
        # trigger source set to detector of analog in channels
        # auto trigger timeout value
#    elif (TgInput.get() == 2):
        # trigger source set to detector of analog in channels
        # 0 disables auto trigger
        
def BTriglevel(event):
    global TRIGGERlevel, TRIGGERentry

    # evalute entry string to a numerical value
    try:
        TRIGGERlevel = float(eval(TRIGGERentry.get()))
    except:
        TRIGGERentry.delete(0,END)
        TRIGGERentry.insert(0, TRIGGERlevel)
    # set new trigger level
    
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
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
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
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
    if TgInput.get() == 0:
        HoldOff = HoldOff + TIMEdiv
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, HoldOff)
# Analog Mux buttons
def SetMuxAPoss():
    global CHB_APosEntry, DCVMuxA
    
    CHB_APosEntry.delete(0,"end")
    CHB_APosEntry.insert(0, ' {0:.2f} '.format(DCVMuxA))
#
def SetMuxBPoss():
    global CHB_BPosEntry, DCVMuxB
    
    CHB_BPosEntry.delete(0,"end")
    CHB_BPosEntry.insert(0, ' {0:.2f} '.format(DCVMuxB))
#
def SetMuxCPoss():
    global CHB_CPosEntry, DCVMuxC
    
    CHB_CPosEntry.delete(0,"end")
    CHB_CPosEntry.insert(0, ' {0:.2f} '.format(DCVMuxC))
#
def SetMuxDPoss():
    global CHD_BPosEntry, DCVMuxD
    
    CHB_DPosEntry.delete(0,"end")
    CHB_DPosEntry.insert(0, ' {0:.2f} '.format(DCVMuxD))
#
def SetScaleMuxA():
    global MarkerScale, CHB_Alab, CHB_Blab, CHB_Clab, CHB_Dlab

    if MarkerScale.get() != 1:
        MarkerScale.set(5)
        CHB_Alab.config(style="Rtrace2.TButton")
        CHB_Blab.config(style="Strace6.TButton")
        CHB_Clab.config(style="Strace7.TButton")
        CHB_Dlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)
#
def SetScaleMuxB():
    global MarkerScale, CHB_Alab, CHB_Blab, CHB_Clab, CHB_Dlab

    if MarkerScale.get() != 1:
        MarkerScale.set(6)
        CHB_Alab.config(style="Strace2.TButton")
        CHB_Blab.config(style="Rtrace6.TButton")
        CHB_Clab.config(style="Strace7.TButton")
        CHB_Dlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)
#
def SetScaleMuxC():
    global MarkerScale, CHB_Alab, CHB_Blab, CHB_Clab, CHB_Dlab

    if MarkerScale.get() != 1:
        MarkerScale.set(7)
        CHB_Alab.config(style="Strace2.TButton")
        CHB_Blab.config(style="Strace6.TButton")
        CHB_Clab.config(style="Rtrace7.TButton")
        CHB_Dlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)
#
def SetScaleMuxD():
    global MarkerScale, CHB_Alab, CHB_Blab, CHB_Clab, CHB_Dlab

    if MarkerScale.get() != 1:
        MarkerScale.set(8)
        CHB_Alab.config(style="Strace2.TButton")
        CHB_Blab.config(style="Strace6.TButton")
        CHB_Clab.config(style="Strace7.TButton")
        CHB_Dlab.config(style="Rtrace4.TButton")
    else:
        MarkerScale.set(0)
#
def SetVAPoss():
    global CHAVPosEntry, DCV1
    
    CHAVPosEntry.delete(0,"end")
    CHAVPosEntry.insert(0, ' {0:.2f} '.format(DCV1))
#
def SetVBPoss():
    global CHBVPosEntry, DCV2
    
    CHBVPosEntry.delete(0,"end")
    CHBVPosEntry.insert(0, ' {0:.2f} '.format(DCV2))
#
def SetIAPoss():
    global CHAIPosEntry, DCI1
    
    CHAIPosEntry.delete(0,"end")
    CHAIPosEntry.insert(0, ' {0:.2f} '.format(DCI1))
#
def SetIBPoss():
    global CHBIPosEntry, DCI2
    
    CHBIPosEntry.delete(0,"end")
    CHBIPosEntry.insert(0, ' {0:.2f} '.format(DCI2))
#
def SetXYVAPoss():
    global CHAVPosEntryxy, DCV1
    
    CHAVPosEntryxy.delete(0,"end")
    CHAVPosEntryxy.insert(0, ' {0:.2f} '.format(DCV1))
#
def SetXYVBPoss():
    global CHBVPosEntryxy, DCV2
    
    CHBVPosEntryxy.delete(0,"end")
    CHBVPosEntryxy.insert(0, ' {0:.2f} '.format(DCV2))
#
def SetXYIAPoss():
    global CHAIPosEntryxy, DCI1
    
    CHAIPosEntryxy.delete(0,"end")
    CHAIPosEntryxy.insert(0, ' {0:.2f} '.format(DCI1))
#
def SetXYIBPoss():
    global CHBIPosEntryxy, DCI2
    
    CHBIPosEntryxy.delete(0,"end")
    CHBIPosEntryxy.insert(0, ' {0:.2f} '.format(DCI2))
    
def Bcloseexit():
    global RUNstatus, session, CHA, CHB
    
    RUNstatus.set(0)
    BSaveConfig("alice-last-config.cfg")
    # Put channels in Hi-Z and exit
    try:
        CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        CHA.constant(0.0)
        CHB.constant(0.0)
        if session.continuous:
            session.end()
    except:
        donothing()

    root.destroy()
    exit()

def BStart():
    global RUNstatus, PowerStatus, devx, PwrBt, DevID, FWRevOne, session, AWGSync
    global contloop, discontloop
    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    elif FWRevOne == 0.0:
        showwarning("WARNING","Out of data Firmware!")
    else:
        if PowerStatus == 0:
            PowerStatus = 1
            PwrBt.config(style="Pwr.TButton",text="PWR-On")
            devx.ctrl_transfer( 0x40, 0x51, 49, 0, 0, 0, 100) # turn on analog power
        if (RUNstatus.get() == 0):
            RUNstatus.set(1)
            if AWGSync.get() == 0: # running in continuous mode
                
                # print "number streaming ", session.active_devices
                time.sleep(0.01)
                if not session.continuous:
                    session.flush()
                    session.start(0)
                    time.sleep(0.01)
                    # print "From Start session(0)"
                contloop = 1
                discontloop = 0
                time.sleep(0.01)
                # print "Starting continuous mode"
                BAWGEnab()
            else:
                contloop = 0
                discontloop = 1
                if session.continuous:
                    session.end() # end continuous session mode
                    
    # UpdateTimeScreen()          # Always Update

def BStop():
    global RUNstatus, TimeDisp, XYDisp, FreqDisp, IADisp, session, AWGSync
    global CHA, CHB, contloop, discontloop
    
    if (RUNstatus.get() == 1):
        RUNstatus.set(0)
        CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        if AWGSync.get() == 0: # running in continuous mode
            CHA.constant(0.0)
            CHB.constant(0.0)
            # print "Stoping continuous mode"
            # session.cancel() # cancel continuous session mode while paused
            if session.continuous:
                #print "Is Continuous? ", session.continuous
                session.end()
                #time.sleep(0.02)
                #print "Is Continuous? ", session.continuous
        else:
            contloop = 0
            discontloop = 1
            session.cancel()
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
    global RUNstatus, PowerStatus, devx, PwrBt

    if (RUNstatus.get() == 1):
        BStop()
    if PowerStatus == 1:
        PowerStatus = 0
        PwrBt.config(style="PwrOff.TButton",text="PWR-Off")
        devx.ctrl_transfer( 0x40, 0x50, 49, 0, 0, 0, 100) # turn off analog power
    else:
        PowerStatus = 1
        PwrBt.config(style="Pwr.TButton",text="PWR-On")
        devx.ctrl_transfer( 0x40, 0x51, 49, 0, 0, 0, 100) # turn on analog power
    
def BTime():
    global TIMEdiv, TMsb, RUNstatus

    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    # BAWGEnab()
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

def BCHAIlevel():
    global CHAIsb
    
    try:
        CH1ipdvLevel = float(eval(CHAIsb.get()))
    except:
        CHAIsb.delete(0,END)
        CHAIsb.insert(0, CH1ipdvLevel)
    UpdateTimeTrace()           # Always Update

def BCHBlevel():
    global CHBsb
    
    try:
        CH2vpdvLevel = float(eval(CHBsb.get()))
    except:
        CHBsb.delete(0,END)
        CHBsb.insert(0, CH2vpdvLevel)
    UpdateTimeTrace()           # Always Update    

def BCHBIlevel():
    global CHBIsb
    
    try:
        CH2ipdvLevel = float(eval(CHBIsb.get()))
    except:
        CHBIsb.delete(0,END)
        CHBIsb.insert(0, CH2ipdvLevel)
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

def BIOffsetA(event):
    global CHAIOffset, CHAIPosEntry

    try:
        CHAIOffset = float(eval(CHAIPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHAIPosEntry.delete(0,END)
        CHAIPosEntry.insert(0, CHAIOffset)
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

def BIOffsetB(event):
    global CHBIOffset, CHBIPosEntry

    try:
        CHBIOffset = float(eval(CHBIPosEntry.get())) # evalute entry string to a numerical value
    except:
        CHBIPosEntry.delete(0,END)
        CHBIPosEntry.insert(0, CHBIOffset)
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
    global BodeDisp, ckb5, AWGSync
    if BodeDisp.get() == 1:
        AWGSync.set(1)
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
def ETSCheckBox():
    global ETSDisp, enb1
    if ETSDisp.get() == 1:
        enb1.config(style="Enab.TCheckbutton")
    else:
        try:
            enb1.config(style="Disab.TCheckbutton")
        except:
            donothing()
# ========================= Main routine ====================================
def Analog_In():
    global RUNstatus, SingleShot, TimeDisp, XYDisp, FreqDisp, SpectrumScreenStatus, HWRevOne
    global IADisp, IAScreenStatus, CutDC, DevOne, AWGBMode, MuxEnb, BodeScreenStatus, BodeDisp
    global MuxScreenStatus, VBuffA, VBuffB, VBuffMA, VBuffMB, VBuffMC, VBuffMD, MuxSync, AWGBIOMode
    global VmemoryMuxA, VmemoryMuxB, VmemoryMuxC, VmemoryMuxD
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, ShowC1_V, ShowC2_V, ShowC2_I, SMPfft
    global PIO_0, PIO_1, PIO_2, PIO_3
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global SV1, SI1, SV2, SI2, SVA_B
    # Analog Mux channel measurement variables
    global TRACEresetTime, TRACEmodeTime, DualMuxMode
    global DCVMuxA, MinVMuxA, MaxVMuxA, MidVMuxA, PPVMuxA, SVMuxA
    global DCVMuxB, MinVMuxB, MaxVMuxB, MidVMuxB, PPVMuxB, SVMuxB
    global DCVMuxC, MinVMuxC, MaxVMuxC, MidVMuxC, PPVMuxC, SVMuxC
    global DCVMuxD, MinVMuxD, MaxVMuxD, MidVMuxD, PPVMuxD, SVMuxD
    
    while (True):       # Main loop
        # RUNstatus = 1 : Open Acquisition
        if (RUNstatus.get() == 1) or (RUNstatus.get() == 2):
            if TimeDisp.get() > 0 or XYDisp.get() > 0:
                if MuxScreenStatus.get() == 0:
                    Analog_Time_In()
                else:
                    AWGSync.set(1) # force discontinuous mode
                    if DualMuxMode.get() == 1: # force split I/O mode if dual mux mode set
                        AWGAIOMode.set(1)
                        AWGBIOMode.set(1)
                        ShowC1_V.set(0) # force A voltage trace off
                    ShowC2_V.set(0) # force B voltage trace off
                    if HWRevOne == "D" :
                        # force channel B to always be in High-Z mode for Rev D hardware or if not in split I/O mode
                        AWGBMode.set(2)
                        if AWGBIOMode.get() == 0: # if not in split I/O mode
                            ShowC2_I.set(0) # no need to show CH-B current
                    if MuxEnb.get() == 1:
                        PIO2 = 0x51
                    else:
                        PIO2 = 0x50
                    if MuxSync.get() == 0:
                        PIO3 = 0x51
                        PIO3x = 0x50
                    else:
                        PIO3 = 0x50
                        PIO3x = 0x51
                    if TRACEmodeTime.get() == 0 and TRACEresetTime == False:
                        TRACEresetTime = True               # Clear the memory for averaging
                    elif TRACEmodeTime.get() == 1:
                        if TRACEresetTime == True:
                            TRACEresetTime = False
                    # Save previous trace in memory for average trace
                        VmemoryMuxA = VBuffMA
                        VmemoryMuxB = VBuffMB
                        VmemoryMuxC = VBuffMC
                        ImemoryMuxD = VBuffMD
                    if Show_CBD.get() == 1:
                        if DualMuxMode.get() == 1:
                            devx.ctrl_transfer(0x40, 0x50, PIO_0, 0, 0, 0, 100) # set PIO 0 to 0
                            devx.ctrl_transfer(0x40, 0x50, PIO_1, 0, 0, 0, 100) # set PIO 1 to 0
                        else:
                            devx.ctrl_transfer(0x40, 0x51, PIO_0, 0, 0, 0, 100) # set PIO 0 to 1
                            devx.ctrl_transfer(0x40, 0x51, PIO_1, 0, 0, 0, 100) # set PIO 1 to 1
                        devx.ctrl_transfer(0x40, PIO2, PIO_2, 0, 0, 0, 100) # set PIO 2 to 0
                        devx.ctrl_transfer(0x40, PIO3, PIO_3, 0, 0, 0, 100) # set PIO 3 to sync pulse for sweep start
                        time.sleep(0.002)
                        devx.ctrl_transfer(0x40, PIO3x, PIO_3, 0, 0, 0, 100) # set PIO 3 to return value
                        Analog_Time_In()
                        if DualMuxMode.get() == 1:
                            DCVMuxD = DCV1
                            MinVMuxD = MinV1
                            MaxVMuxD = MaxV1
                            MidVMuxD = (MaxV1+MinV1)/2.0
                            PPVMuxD = MaxV1-MinV1
                            SVMuxD = SV1
                            VBuffMD = VBuffA
                        else:
                            VBuffMD = VBuffB
                            DCVMuxD = DCV2
                            MinVMuxD = MinV2
                            MaxVMuxD = MaxV2
                            MidVMuxD = (MaxV2+MinV2)/2.0
                            PPVMuxD = MaxV2-MinV2
                            SVMuxD = SV2
                        # Average mode 1, add difference / TRACEaverage to arrayif :
                        if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
                            try:
                                VBuffMD = VmemoryMuxD + (VBuffMD - VmemoryMuxD) / TRACEaverage.get()
                            except:
                            # buffer size mismatch so reset memory buffers
                                VmemoryMuxD = VBuffMD
                    if Show_CBC.get() == 1:
                        if DualMuxMode.get() == 1:
                            devx.ctrl_transfer(0x40, 0x51, PIO_0, 0, 0, 0, 100) # set PIO 0 to 1
                            devx.ctrl_transfer(0x40, 0x50, PIO_1, 0, 0, 0, 100) # set PIO 1 to 0
                        else:
                            devx.ctrl_transfer(0x40, 0x50, PIO_0, 0, 0, 0, 100) # set PIO 0 to 0
                            devx.ctrl_transfer(0x40, 0x51, PIO_1, 0, 0, 0, 100) # set PIO 1 to 1
                        devx.ctrl_transfer(0x40, PIO2, PIO_2, 0, 0, 0, 100) # set PIO 2 to 0
                        devx.ctrl_transfer(0x40, PIO3, PIO_3, 0, 0, 0, 100) # set PIO 3 to sync pulse for sweep start
                        time.sleep(0.002)
                        devx.ctrl_transfer(0x40, PIO3x, PIO_3, 0, 0, 0, 100) # set PIO 3 to return value
                        Analog_Time_In()
                        DCVMuxC = DCV2
                        MinVMuxC = MinV2
                        MaxVMuxC = MaxV2
                        MidVMuxC = (MaxV2+MinV2)/2.0
                        PPVMuxC = MaxV2-MinV2
                        SVMuxC = SV2
                        if DualMuxMode.get() == 1:
                            DCVMuxC = DCV1
                            MinVMuxC = MinV1
                            MaxVMuxC = MaxV1
                            MidVMuxC = (MaxV1+MinV1)/2.0
                            PPVMuxC = MaxV1-MinV1
                            SVMuxC = SV1
                            VBuffMC = VBuffA
                        else:
                            VBuffMC = VBuffB
                            DCVMuxC = DCV2
                            MinVMuxC = MinV2
                            MaxVMuxC = MaxV2
                            MidVMuxC = (MaxV2+MinV2)/2.0
                            PPVMuxC = MaxV2-MinV2
                            SVMuxC = SV2
                        # Average mode 1, add difference / TRACEaverage to arrayif :
                        if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
                            try:
                                VBuffMC = VmemoryMuxC + (VBuffMC - VmemoryMuxC) / TRACEaverage.get()
                            except:
                            # buffer size mismatch so reset memory buffers
                                VmemoryMuxC = VBuffMC
                    if Show_CBB.get() == 1:
                        devx.ctrl_transfer(0x40, 0x51, PIO_0, 0, 0, 0, 100) # set PIO 0 to 1
                        devx.ctrl_transfer(0x40, 0x50, PIO_1, 0, 0, 0, 100) # set PIO 1 to 0
                        devx.ctrl_transfer(0x40, PIO2, PIO_2, 0, 0, 0, 100) # set PIO 2 to 0
                        devx.ctrl_transfer(0x40, PIO3, PIO_3, 0, 0, 0, 100) # set PIO 3 to sync pulse for sweep start
                        time.sleep(0.002)
                        devx.ctrl_transfer(0x40, PIO3x, 3, 0, 0, 0, 100) # set PIO 3 to return value
                        Analog_Time_In()
                        DCVMuxB = DCV2
                        MinVMuxB = MinV2
                        MaxVMuxB = MaxV2
                        MidVMuxB = (MaxV2+MinV2)/2.0
                        PPVMuxB = MaxV2-MinV2
                        SVMuxB = SV2
                        VBuffMB = VBuffB
                        # Average mode 1, add difference / TRACEaverage to arrayif :
                        if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
                            try:
                                VBuffMB = VmemoryMuxB + (VBuffMB - VmemoryMuxB) / TRACEaverage.get()
                            except:
                            # buffer size mismatch so reset memory buffers
                                VmemoryMuxB = VBuffMB
                    if Show_CBA.get() == 1 or ShowC1_V.get() == 1:
                        devx.ctrl_transfer(0x40, 0x50, PIO_0, 0, 0, 0, 100) # set PIO 0 to 0
                        devx.ctrl_transfer(0x40, 0x50, PIO_1, 0, 0, 0, 100) # set PIO 1 to 0
                        devx.ctrl_transfer(0x40, PIO2, PIO_2, 0, 0, 0, 100) # set PIO 2 to 0
                        devx.ctrl_transfer(0x40, PIO3, PIO_3, 0, 0, 0, 100) # set PIO 3 to 1 sync pulse for sweep start
                        time.sleep(0.002)
                        devx.ctrl_transfer(0x40, PIO3x, PIO_3, 0, 0, 0, 100) # set PIO 3 to return value
                        Analog_Time_In()
                        DCVMuxA = DCV2
                        MinVMuxA = MinV2
                        MaxVMuxA = MaxV2
                        MidVMuxA = (MaxV2+MinV2)/2.0
                        PPVMuxA = MaxV2-MinV2
                        SVMuxA = SV2
                        VBuffMA = VBuffB
                        # Average mode 1, add difference / TRACEaverage to arrayif :
                        if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
                            try:
                                VBuffMA = VmemoryMuxA + (VBuffMA - VmemoryMuxA) / TRACEaverage.get()
                            except:
                            # buffer size mismatch so reset memory buffers
                                VmemoryMuxA = VBuffMA
            if (FreqDisp.get() > 0 and SpectrumScreenStatus.get() == 1) or (IADisp.get() > 0 and IAScreenStatus.get() == 1) or (BodeDisp.get() > 0 and BodeScreenStatus.get() == 1):
                if IADisp.get() > 0 or BodeDisp.get() > 0:
                    CutDC.set(1) # remove DC portion of waveform
                    AWGSync.set(1) # Impedance analyzer and Bode plotter must be run in discontinuous mode
                if BodeDisp.get() > 0:
                    if LoopNum.get() <= len(FStep):
                        if FStep[LoopNum.get()-1] < 16:
                            SMPfft = 16384
                        elif FStep[LoopNum.get()-1] < 32:
                            SMPfft = 8192
                        elif FStep[LoopNum.get()-1] < 64:
                            SMPfft = 4096
                        else:
                            SMPfft = 4096
                Analog_Freq_In()
        elif OhmRunStatus.get() == 1 and OhmDisp.get() == 1:
            Ohm_Analog_In()
        root.update_idletasks()
        root.update()
#
def Ohm_Analog_In():
    global RMode, CHATestVEntry, CHATestREntry, CHA, CHB, devx, OhmA0, OhmA1

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
    try:
        CurOffA = float(CHAIOffsetEntry.get())
    except:
        CurOffA = 0.0
    try:
        CurOffB = float(CHBIOffsetEntry.get())
    except:
        CurOffB = 0.0
    try:
        CurGainA = float(CHAIGainEntry.get())
    except:
        CurGainA = 1.0
    try:
        CurGainB = float(CHBIGainEntry.get())
    except:
        CurGainB = 1.0
    try:
        chatestv = float(eval(CHATestVEntry.get()))
        if chatestv > 5.0:
            chatestv = 5.0
            CHATestVEntry.delete(0,END)
            CHATestVEntry.insert(0, chatestv)
    except:
        CHATestVEntry.delete(0,END)
        CHATestVEntry.insert(0, chatestv)
    try:
        chatestr = float(eval(CHATestREntry.get()))
    except:
        CHATestREntry.delete(0,END)
        CHATestREntry.insert(0, chatestr)
    # 
    DCVA0 = DCVB0 = DCIA0 = DCIB0 = 0.0 # initalize measurment variable
    RIN = 1000000 # nominal ALM1000 input resistance is 1 Mohm
    # Get A0 and B0 data
    CHA.mode = Mode.SVMI
    CHB.mode = Mode.HI_Z
    CHA.constant(chatestv)
    if RMode.get() == 0:
        devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    else:
        devx.ctrl_transfer(0x40, 0x50, 38, 0, 0, 0, 100) # set CHB GND switch to closed
    ADsignal1 = devx.get_samples(210) # get samples for both channel A0 and B0
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(200): # calculate average
        DCVA0 += ADsignal1[index+10][0][0] # VAdata # Sum for average CA voltage 
        DCVB0 += ADsignal1[index+10][1][0] # VBdata # Sum for average CB voltage
        DCIA0 += ADsignal1[index+10][0][1] # Sum for average CA current 
        DCIB0 += ADsignal1[index+10][1][1] # Sum for average CB current 

    DCVA0 = DCVA0 / 200.0 # calculate average
    DCVB0 = DCVB0 / 200.0 # calculate average
    DCIA0 = DCIA0 / 200.0 # calculate average
    DCIB0 = DCIB0 / 200.0 # calculate average
    DCVA0 = (DCVA0 - InOffA) * InGainA
    DCVB0 = (DCVB0 - InOffB) * InGainB
    DCIA0 = ((DCIA0*1000) - CurOffA) * CurGainA
    DCIB0 = ((DCIB0*1000) - CurOffB) * CurGainB
    if RMode.get() == 0: # external resistor
        DCM = chatestr * (DCVB0/(DCVA0-DCVB0))
        DCR = (DCM * RIN) / (RIN - DCM) # correct for channel B input resistance
    else: # use internal 50 ohm resistor
        DCR = chatestr * ((DCVA0-DCVB0)/DCVB0)
    if DCR < 1000:
        OhmString = '{0:.2f} '.format(DCR) + "Ohms "# format with 2 decimal places
    else:
        OhmString = '{0:.3f} '.format(DCR/1000) + "KOhms " # divide by 1000 and format with 3 decimal places
    IAString = "Meas " + ' {0:.2f} '.format(DCIA0) + " mA " + ' {0:.2f} '.format(DCVA0) + " V"
    OhmA0.config(text = OhmString) # change displayed value
    OhmA1.config(text = IAString) # change displayed value
#
    time.sleep(0.1)
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
#        
def Analog_Time_In():   # Read the analog data and store the data into the arrays
    global ADsignal1, VBuffA, VBuffB, IBuffA, IBuffB, VFilterA, VFilterB
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB, VmemoryMuxA, VmemoryMuxB, VmemoryMuxC, VmemoryMuxD
    global AWGSync, AWGAMode, AWGBMode, TMsb, HoldOff, HoldOffentry, HozPoss, HozPossentry
    global AWGAIOMode, AWGBIOMode, DecimateOption, DualMuxMode
    global TRACEresetTime, TRACEmodeTime, TRACEaverage, TRIGGERsample, TgInput
    global CHA, CHB, session, devx, discontloop, contloop
    global TRACES, TRACESread, TRACEsize
    global RUNstatus, SingleShot, TimeDisp, XYDisp, FreqDisp
    global TIMEdiv1x, TIMEdiv, hldn
    global SAMPLErate, SHOWsamples, MinSamples, MaxSamples, AWGSAMPLErate
    global TRACErefresh, AWGScreenStatus, XYScreenStatus, MeasureStatus
    global SCREENrefresh, DCrefresh
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global SV1, SI1, SV2, SI2, SVA_B
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global InOffA, InGainA, InOffB, InGainB
    global DigFiltA, DigFiltB, DFiltACoef, DFiltBCoef, DigBuffA, DigBuffB
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global VAets, VBets, Samples_Cycle, MulX, ETSDisp, ETSDir, ETSts, Fmin, FminE, eqivsamplerate
    global DivXEntry, FOffEntry, FminDisp, FOff, DivX, FminEntry, FBase, MaxETSrecord
 
    # get time scale
    try:
        TIMEdiv = eval(TMsb.get())
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
    #
    if TRACEmodeTime.get() == 0 and TRACEresetTime == False:
        TRACEresetTime = True               # Clear the memory for averaging
    elif TRACEmodeTime.get() == 1:
        if TRACEresetTime == True:
            TRACEresetTime = False
        # Save previous trace in memory for average trace
        VmemoryA = VBuffA
        VmemoryB = VBuffB
        ImemoryA = IBuffA
        ImemoryB = IBuffB

# Do input divider Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
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
    try:
        CurOffA = float(CHAIOffsetEntry.get()) #/1000.0 # convert to Amps # leave in mA
    except:
        CurOffA = 0.0
    try:
        CurOffB = float(CHBIOffsetEntry.get())#/1000.0 # convert to Amps
    except:
        CurOffB = 0.0
    try:
        CurGainA = float(CHAIGainEntry.get())
    except:
        CurGainA = 1.0
    try:
        CurGainB = float(CHBIGainEntry.get())
    except:
        CurGainB = 1.0
#
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

    hldn = int(HoldOff * AWGSAMPLErate/1000 )
    hozpos = int(HozPoss * AWGSAMPLErate/1000 )
    if hozpos < 0:
        hozpos = 0
    twoscreens = int(AWGSAMPLErate * 20.0 * TIMEdiv / 1000.0) # number of samples to acquire, 2 screen widths
    onescreen = int(twoscreens/2)
    if hldn+hozpos > MaxSamples-twoscreens:
        hldn = MaxSamples-twoscreens-hozpos
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, hldn*1000/AWGSAMPLErate)
    if ETSDisp.get() > 0:
        if TIMEdiv > 0.2:
            MaxETSrecord = int(AWGSAMPLErate * 10 * TIMEdiv / 1000.0)
        else:
            MaxETSrecord = int(AWGSAMPLErate * 20 * TIMEdiv / 1000.0)
        if (MaxETSrecord*100) > MaxSamples:
            MaxETSrecord = MaxSamples / 100
        try:
            DivX = float(eval(DivXEntry.get()))
            if DivX < 2:
                DivX = 2
            if DivX > 75:
                DivX = 75
                DivXEntry.delete(0,END)
                DivXEntry.insert(0, DivX)
        except:
            DivXEntry.delete(0,END)
            DivXEntry.insert(0, DivX)
        FOff = 25
        MulX = (DivX*SAMPLErate)/(100*FOff)
        while MulX > MaxETSrecord:
            FOff = FOff + 5
            MulX = (DivX*SAMPLErate)/(100*FOff)
        FOff = 0 - FOff
        SRstring = "Rec Len Mul = "  + str(MulX) + " samples"
        MulXEntry.config(text = SRstring) # change displayed value
        SRstring = "Offset = "  + str(FOff) + " samples"
        FOffEntry.config(text = SRstring) # change displayed value
        SHOWsamples = int(MulX * 100)
    else:
        SHOWsamples = twoscreens + hldn + hozpos
        if SHOWsamples > MaxSamples: # or a Max of 100,000 samples
            SHOWsamples = MaxSamples
        if SHOWsamples < MinSamples: # or a Min of 1000 samples
            SHOWsamples = MinSamples
    if hozpos >= 0:
        TRIGGERsample = hldn
    else:
        TRIGGERsample = abs(hozpos)
    TRIGGERsample = TRIGGERsample + hozpos #
# Starting acquisition
    if AWGScreenStatus.get() == 1: # don't try to start AWG is AWG screen is closed
        if AWGSync.get() > 0: # awg syn flag set so run in discontinuous mode
            if discontloop > 0:
                session.flush()
            else:
                discontloop = 1
            time.sleep(0.01)
            # print "just before awg enable"
            BAWGEnab()
            # print "just before get samples"
            ADsignal1 = devx.get_samples(SHOWsamples) # get samples for both channel A and B
            # waite to finish then return to open termination
            devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
            devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
            # time.sleep(1000.0/SHOWsamples)
        else: # running in continuous mode
            if session.continuous:
                ADsignal1 = devx.read(SHOWsamples, -1, True) # get samples for both channel A and B
    #
    else:
        # session.flush()
        ADsignal1 = devx.get_samples(SHOWsamples) # , True) # get samples for both channel A and B
        # time.sleep(0.01)
        # waite to finish then return to open termination
        devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
        devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    VBuffA = [] # Clear the V Buff array for trace A
    IBuffA = [] # Clear the I Buff array for trace A
    VBuffB = [] # Clear the V Buff array for trace B
    IBuffB = [] # Clear the I Buff array for trace B
    increment = 1
    SAMPLErate = AWGSAMPLErate
    if SHOWsamples >= 20000 and DecimateOption.get() > 0:
        increment = 2
        SAMPLErate = int(AWGSAMPLErate/increment)
    if SHOWsamples >= 40000 and DecimateOption.get() > 0:
        increment = 4
        SAMPLErate = int(AWGSAMPLErate/increment)
    index = 0
    if SHOWsamples != len(ADsignal1):
        SHOWsamples = len(ADsignal1)
    while index < SHOWsamples: # build arrays and decimate if needed
        VBuffA.append(ADsignal1[index][0][0])
        IBuffA.append(ADsignal1[index][0][1])
        VBuffB.append(ADsignal1[index][1][0])
        IBuffB.append(ADsignal1[index][1][1])
        index = index + increment
#
    SHOWsamples = len(VBuffA)
    VBuffA = numpy.array(VBuffA)
    VBuffB = numpy.array(VBuffB)
    IBuffA = numpy.array(IBuffA) * 1000 # convert to mA
    IBuffB = numpy.array(IBuffB) * 1000 # convert to mA
    VBuffA = (VBuffA - InOffA) * InGainA
    IBuffA = (IBuffA - CurOffA) * CurGainA
    VBuffB = (VBuffB - InOffB) * InGainB
    IBuffB = (IBuffB - CurOffB) * CurGainB
    TRACESread = 2
# temp ETS calculations
    if ETSDisp.get() > 0:
        baseFreq = SAMPLErate/DivX
        #
        VAets = []
        VBets = []
        IAets = []
        IBets = []
        index = 0
        try:
            FMul = float(eval(FminEntry.get()))
            if FMul < 1:
                FMul = 1
                FminEntry.delete(0,END)
                FminEntry.insert(0, int(FMul))
            if FMul > 75:
                FMul = 75
                FminEntry.delete(0,END)
                FminEntry.insert(0, int(FMul))
        except:
            FminEntry.delete(0,END)
            FminEntry.insert(0, int(FMul))
        Fmin = baseFreq * FMul
        FminE = float(SAMPLErate + FOff)
        Samples_Cycle = SAMPLErate/FminE # calculate number of samples per cycle
        # length of record set my Multiplcation factor
        tot_cycles = int((MulX*100)/Samples_Cycle)
        tot_cycles = tot_cycles + 0.1 # number of cycles in record length
        if tot_cycles > SHOWsamples:
            tot_cycles = SHOWsamples-1
        #
        SRstring = "Multiplied Freq = "  + ' {0:.1f} '.format(Fmin) + " Hz"
        #
        FminDisp.config(text = SRstring) # change displayed value
        #
        SRstring = "Base Frequency = "  + ' {0:.2f} '.format(baseFreq) + " Hz"
        eqivsamplerate.config(text = SRstring) # change displayed value
        # now sort RT data into ETS sample buffers
        while index < SHOWsamples:
            Ipart, Dpart = divmod( index*Samples_Cycle, 1)
            IndexValue = int(tot_cycles * Dpart)
            if IndexValue > SHOWsamples:
                IndexValue = SHOWsamples-1
            if IndexValue > tot_cycles:
                IndexValue = tot_cycles
            if ETSDir.get() == 0:
                VAets.append(VBuffA[IndexValue])
                VBets.append(VBuffB[IndexValue])
                IAets.append(IBuffA[IndexValue])
                IBets.append(IBuffB[IndexValue])
            else:
                VAets.append(VBuffA[tot_cycles-IndexValue])
                VBets.append(VBuffB[tot_cycles-IndexValue])
                IAets.append(IBuffA[tot_cycles-IndexValue])
                IBets.append(IBuffB[tot_cycles-IndexValue])
            index = index + 1
        SHiftFact = 5
        TimeCorrection = int(SHiftFact ) # correct for 5 uSec CHB time offset
        VBuffA = VAets
        VBuffB = VBets
        IBuffA = IAets
        IBuffB = IBets
        VBuffA = numpy.array(VBuffA)
        VBuffB = numpy.array(VBuffB)
        IBuffA = numpy.array(IBuffA)
        IBuffB = numpy.array(IBuffB)
        try:
            TimeCorrection = int(float(eval(ETSts.get())) * TimeCorrection)
        except:
            TimeCorrection = SHiftFact
        if ETSDir.get() == 0:
            VBuffB = numpy.roll(VBuffB, TimeCorrection)
            IBuffB = numpy.roll(IBuffB, TimeCorrection)
        else:
            VBuffB = numpy.roll(VBuffB, TimeCorrection)
            IBuffB = numpy.roll(IBuffB, TimeCorrection)
        SHOWsamples = twoscreens + hldn + hozpos
# Check if Input channel RC high pass compensation checked
    if CHA_RC_HP.get() == 1:
        try:
            TC1A = float(cha_TC1Entry.get())
            if TC1A < 0:
                TC1A = 0
                cha_TC1Entry.delete(0,END)
                cha_TC1Entry.insert(0, TC1A)
        except:
            TC1A = CHA_TC1.get()
        try:
            TC2A = float(cha_TC2Entry.get())
            if TC2A < 0:
                TC2A = 0
                cha_TC2Entry.delete(0,END)
                cha_TC2Entry.insert(0, TC2A)
        except:
            TC2A = CHA_TC2.get()
        #
        try:
            Gain1A = float(cha_A1Entry.get())
            if Gain1A < 0:
                Gain1A = 1
                cha_A1Entry.delete(0,END)
                cha_A1Entry.insert(0, Gain1A)
        except:
            Gain1A = CHA_A1.get()
        try:
            Gain2A = float(cha_A2Entry.get())
            if Gain2A < 0:
                Gain2A = 0
                cha_A2Entry.delete(0,END)
                cha_A2Entry.insert(0, Gain2A)
        except:
            Gain2A = CHA_A2.get()
        #
        VBuffA = Digital_RC_High_Pass( VBuffA, TC1A, Gain1A )
        VBuffA = Digital_RC_High_Pass( VBuffA, TC2A, Gain2A )
    if CHB_RC_HP.get() == 1:
        try:
            TC1B = float(chb_TC1Entry.get())
            if TC1B < 0:
                TC1B = 0
                chb_TC1Entry.delete(0, END)
                chb_TC1Entry.insert(0, TC1B)
        except:
            TC1B = CHB_TC1.get()
        try:
            TC2B = float(chb_TC2Entry.get())
            if TC2B < 0:
                TC2B = 0
                chb_TC2Entry.delete(0, END)
                chb_TC2Entry.insert(0, TC2B)
        except:
            TC2B = CHB_TC2.get()
        #
        try:
            Gain1B = float(chb_A1Entry.get())
            if Gain1B < 0:
                Gain1B = 1
                chb_A1Entry.delete(0,END)
                chb_A1Entry.insert(0, Gain1B)
        except:
            Gain1B = CHB_A1.get()
        try:
            Gain2B = float(chb_A2Entry.get())
            if Gain2B < 0:
                Gain2B = 0
                chb_A2Entry.delete(0,END)
                chb_A2Entry.insert(0, Gain2B)
        except:
            Gain2B = CHB_A2.get()
        #
        VBuffB = Digital_RC_High_Pass( VBuffB, TC1B, Gain1B )
        VBuffB = Digital_RC_High_Pass( VBuffB, TC2B, Gain2B )
# check if digital filter box checked
    if DigFiltA.get() == 1:
        if len(DFiltACoef) > 1:
            VBuffA = numpy.convolve(VBuffA, DFiltACoef)
    if DigFiltB.get() == 1:
        if len(DFiltBCoef) > 1:
            VBuffB = numpy.convolve(VBuffB, DFiltBCoef)
# Find trigger sample point if necessary
    LShift = 0
    if TgInput.get() == 1:
        FindTriggerSample(VBuffA)
    if TgInput.get() == 2:
        FindTriggerSample(IBuffA)
    if TgInput.get() == 3:
        FindTriggerSample(VBuffB)
    if TgInput.get() == 4:
        FindTriggerSample(IBuffB)
    if TRACEmodeTime.get() == 1 and TRACEresetTime == False:
        # Average mode 1, add difference / TRACEaverage to array
        if TgInput.get() > 0: # if triggering left shift all arrays such that trigger point is at index 0
            LShift = 0 - TRIGGERsample
            VBuffA = numpy.roll(VBuffA, LShift)
            VBuffB = numpy.roll(VBuffB, LShift)
            IBuffA = numpy.roll(IBuffA, LShift)
            IBuffB = numpy.roll(IBuffB, LShift)
            TRIGGERsample = hozpos # set trigger sample to index 0 offset by horizontal position
        try:
            if DualMuxMode.get() == 0 and MuxScreenStatus.get() == 0: # average A voltage data only if not in dual split I/O Mux Mode
                VBuffA = VmemoryA + (VBuffA - VmemoryA) / TRACEaverage.get()
            IBuffA = ImemoryA + (IBuffA - ImemoryA) / TRACEaverage.get()
            if MuxScreenStatus.get() == 0: # average B voltage data only if not in Mux Mode
                VBuffB = VmemoryB + (VBuffB - VmemoryB) / TRACEaverage.get()
            IBuffB = ImemoryB + (IBuffB - ImemoryB) / TRACEaverage.get()
        except:
            # buffer size mismatch so reset memory buffers
            VmemoryA = VBuffA
            if MuxScreenStatus.get() == 0: # average B voltage data only if not in Mux Mode
                VmemoryB = VBuffB
            ImemoryA = IBuffA
            ImemoryB = IBuffB
# DC value = average of the data record
    if CHA_RC_HP.get() == 1 or CHB_RC_HP.get() == 1:
        Endsample = hldn+onescreen # average over only one screen's worth of samples
    else:
        Endsample = SHOWsamples - 10 # average over all samples
    DCV1 = numpy.mean(VBuffA[hldn:Endsample])
    DCV2 = numpy.mean(VBuffB[hldn:Endsample])
    # convert current values to mA
    DCI1 = numpy.mean(IBuffA[hldn:Endsample])
    DCI2 = numpy.mean(IBuffB[hldn:Endsample])
# find min and max values
    MinV1 = numpy.amin(VBuffA[hldn:Endsample])
    MaxV1 = numpy.amax(VBuffA[hldn:Endsample])
    MinV2 = numpy.amin(VBuffB[hldn:Endsample])
    MaxV2 = numpy.amax(VBuffB[hldn:Endsample])
    MinI1 = numpy.amin(IBuffA[hldn:Endsample])
    MaxI1 = numpy.amax(IBuffA[hldn:Endsample])
    MinI2 = numpy.amin(IBuffB[hldn:Endsample])
    MaxI2 = numpy.amax(IBuffB[hldn:Endsample])
# RMS value = square root of average of the data record squared
    SV1 = numpy.sqrt(numpy.mean(numpy.square(VBuffA[hldn:Endsample])))
    SI1 = numpy.sqrt(numpy.mean(numpy.square(IBuffA[hldn:Endsample])))
    SV2 = numpy.sqrt(numpy.mean(numpy.square(VBuffB[hldn:Endsample])))
    SI2 = numpy.sqrt(numpy.mean(numpy.square(IBuffB[hldn:Endsample])))
    SVA_B = numpy.sqrt(numpy.mean(numpy.square(VBuffA[hldn:Endsample]-VBuffB[hldn:Endsample])))
#
    if TimeDisp.get() > 0:
        UpdateTimeAll()         # Update Data, trace and time screen
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
# High Pass y[n] = alpha * (y[n-1] + x[n] - x[n-1])
#  Low Pass y[n] = y[n-1] + (alpha * ((x[n] - x[n-1]))
#  All Pass y[n] = alpha * y[n-1] - alpha * (x[n] + x[n-1])
#  All Pass y[n] = alpha * (y[n-1] - x[n] - x[n-1])
def Digital_RC_High_Pass( InBuff, TC1, Gain ): # TC1 is in micro seconds
    global SAMPLErate
    
    OutBuff = []
    n = len(InBuff)
    Delta = 1.0/SAMPLErate
    TC = TC1 * 1.0E-6
    Alpha = TC / (TC + Delta)
    OutBuff.append(InBuff[1]-InBuff[0]) # set inital sample to derivative (difference of first two samples)
    i = 1
    while i < n:
        OutBuff.append( Alpha * (OutBuff[i-1] + InBuff[i] - InBuff[i-1]) )
        i += 1
    OutBuff = numpy.array(OutBuff)
    OutBuff = InBuff + (OutBuff * Gain)
    return OutBuff
#
def Digital_RC_Low_Pass( InBuff, TC1, Gain ): # TC1 is in micro seconds
    global SAMPLErate
    
    OutBuff = []
    n = len(InBuff)
    Delta = 1.0/SAMPLErate
    TC = TC1 * 1.0E-6
    Alpha = Delta / (TC + Delta)
    i = 1
    OutBuff.append(Alpha*InBuff[0])
    while i < n:
        OutBuff.append( OutBuff[i-1] + (Alpha * (InBuff[i] - InBuff[i-1])) )
        i += 1
    OutBuff = numpy.array(OutBuff)
    OutBuff = (OutBuff * Gain)
    return OutBuff
#
def Analog_Freq_In():   # Read from the stream and store the data into the arrays
    global ADsignal1, FFTBuffA, FFTBuffB, SMPfft
    global AWGSync, AWGAMode, AWGBMode, AWGAShape, AWGAIOMode, AWGBIOMode
    global AWGAFreqvalue, AWGBFreqvalue, FStepSync, FSweepSync
    global NSteps, LoopNum, FSweepMode, FStep, FBins
    global StartFreqEntry, StopFreqEntry, HoldOffentry
    global session, CHA, CHB, devx, MaxSamples, discontloop
    global RUNstatus, SingleShot, FSweepCont
    global AWGSAMPLErate, IAScreenStatus, SpectrumScreenStatus, BodeScreenStatus
    global OverRangeFlagA, OverRangeFlagB, BodeDisp, FreqDisp, IADisp
    global DCA, DCB, InOffA, InGainA, InOffB, InGainB
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DigFiltA, DFiltACoef, DigFiltB, DFiltBCoef
    global BDSweepFile, FileSweepFreq, FileSweepAmpl
    global PIO_0, PIO_1, PIO_2, PIO_3
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    global Reset_Freq, AWGAFreqEntry, AWGBFreqEntry
    
    # Do input divider Calibration CH1VGain, CH2VGain, CH1VOffset, CH2VOffset
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
    INITIALIZEstart()
    # Starting acquisition This is a HACK to get around non-continous AWG mode!
    # restart AWGs if indicated
    if BodeDisp.get() == 0: # make new noise waveforms each sweep
        if AWGAShape.get() == 7 and AWGAMode.get() == 0:
            AWGAMakeUUNoise()
        elif AWGAShape.get() == 8 and AWGAMode.get() == 0:
            AWGAMakeUGNoise()
        elif AWGBShape.get() == 7 and AWGBMode.get() == 0:
            AWGBMakeUUNoise()
        elif AWGBShape.get() == 8 and AWGBMode.get() == 0:
            AWGBMakeUGNoise()
    if FSweepMode.get() > 0 and BodeDisp.get() > 0: # Run Sweep Gen only if sleceted and Bode display is active
        if BDSweepFile.get() == 0:
            if LoopNum.get() <= len(FStep):
                FregPoint = FBins[int(FStep[LoopNum.get()-1])] # look up next frequency from list of bins
            else:
                FregPoint = FBins[FStep[0]]
        else:
            if LoopNum.get() <= len(FileSweepFreq): #
                FreqIndex = int((FileSweepFreq[LoopNum.get()-1]*16384)/50000)
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
            AWGAMakeBodeSine()
        if FSweepMode.get() == 2: # set new CH-B frequency
            AWGBFreqEntry.delete(0,END)
            AWGBFreqEntry.insert(4, FregPoint)
            AWGBMakeBodeSine()
    if AWGSync.get() > 0:
        if IAScreenStatus.get() > 0:
            AWGBMode.set(2)
        # BAWGEnab()
#
    hldn = int(HoldOff * 100 )
    if hldn > MaxSamples-SMPfft:
        hldn = MaxSamples-SMPfft
        HoldOffentry.delete(0,END)
        HoldOffentry.insert(0, hldn/100)
        if hldn < 128:
            hldn = 128
    SHOWsamples = SMPfft + hldn # get holf off extra samples
    if BodeDisp.get() > 0: # check if doing Bode Plot
        if FStepSync.get() == 1: # output low - high - low pulse on PIO-0
            devx.ctrl_transfer( 0x40, 0x50, PIO_0, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x51, PIO_0, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x50, PIO_0, 0, 0, 0, 100)
        if FStepSync.get() == 2: # output high - low - high pulse on PIO-0
            devx.ctrl_transfer( 0x40, 0x51, PIO_0, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x50, PIO_0, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x51, PIO_0, 0, 0, 0, 100)
        if LoopNum.get() == 1 and FSweepSync.get() == 1: # output low - high - low pulse on PIO-1
            devx.ctrl_transfer( 0x40, 0x50, PIO_1, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x51, PIO_1, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x50, PIO_1, 0, 0, 0, 100)
        if LoopNum.get() == 1 and FSweepSync.get() == 2: # output high - low - high pulse on PIO-1
            devx.ctrl_transfer( 0x40, 0x51, PIO_1, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x50, PIO_1, 0, 0, 0, 100)
            devx.ctrl_transfer( 0x40, 0x51, PIO_1, 0, 0, 0, 100)
    if AWGScreenStatus.get() == 1: # don't try to start AWG is AWG screen is closed
        if IAScreenStatus.get() > 0:
            AWGBMode.set(2)
        if AWGSync.get() > 0: # awg syn flag set so run in discontinuous mode
            if discontloop > 0:
                session.flush()
            else:
                discontloop = 1
            BAWGEnab()
            try:
                ADsignal1 = devx.get_samples(SHOWsamples) # get samples for both channel A and B
            except:
                donothing()
            # waite to finish then return to open termination
            devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
            devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
            devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
        else: # running in continuous mode
            ADsignal1 = devx.read(SHOWsamples, -1, True) # get samples for both channel A and B
    #
    else:
        if session.continuous:
            ADsignal1 = devx.read(SHOWsamples, -1, True)
        # ADsignal1 = devx.get_samples(SHOWsamples) # get samples for both channel A and B
        devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
        devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    FFTBuffA = [] # Clear the FFTBuff array for trace A
    FFTBuffB = [] # Clear the FFTBuff array for trace B
    OverRangeFlagA = OverRangeFlagB = 0 # Clear over range flags
    index = hldn-1 # skip first hldn samples
    if SHOWsamples != len(ADsignal1):
        SHOWsamples = len(ADsignal1)
    while index < SHOWsamples:
        VAdata = ADsignal1[index][0][0] 
        FFTBuffA.append(VAdata)
        VBdata = ADsignal1[index][1][0] 
        FFTBuffB.append(VBdata)
        if VAdata >= 5.0 or VAdata <= 0.0:
            OverRangeFlagA = 1

        if VBdata >= 5.0 or VBdata <= 0.0:
            OverRangeFlagB = 1
        index = index + 1

    FFTBuffA = numpy.array(FFTBuffA)
    FFTBuffB = numpy.array(FFTBuffB)
    FFTBuffA = (FFTBuffA - InOffA) * InGainA
    FFTBuffB = (FFTBuffB - InOffB) * InGainB
    DCA = numpy.average(FFTBuffA)
    DCB = numpy.average(FFTBuffB)
    if CutDC.get() == 1:
        FFTBuffA = FFTBuffA - DCA
        FFTBuffB = FFTBuffB - DCB
# Check if Input channel RC high pass compensation checked cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    if CHA_RC_HP.get() == 1:
        try:
            TC1A = float(cha_TC1Entry.get())
            if TC1A < 0:
                TC1A = 0
                cha_TC1Entry.delete(0,END)
                cha_TC1Entry.insert(0, TC1A)
        except:
            TC1A = CHA_TC1.get()
            #cha_TC1Entry.delete(0,END)
            #cha_TC1Entry.insert(0, CHA_TC1.get())
        try:
            TC2A = float(cha_TC2Entry.get())
            if TC2A < 0:
                TC2A = 0
                cha_TC2Entry.delete(0,END)
                cha_TC2Entry.insert(0, TC2A)
        except:
            TC2A = CHA_TC2.get()
            #cha_TC2Entry.delete(0,END)
            #cha_TC2Entry.insert(0, CHA_TC2.get())
        #
        try:
            Gain1A = float(cha_A1Entry.get())
            #CHA_A1.set(Gain1A)
            if Gain1A < 0:
                Gain1A = 1
                cha_A1Entry.delete(0,END)
                cha_A1Entry.insert(0, Gain1A)
        except:
            Gain1A = CHA_A1.get()
            #cha_A1Entry.delete(0,END)
            #cha_A1Entry.insert(0, CHA_A1.get())
        try:
            Gain2A = float(cha_A2Entry.get())
            #CHA_A2.set(int(Gain2A))
            if Gain2A < 0:
                Gain2A = 0
                cha_A2Entry.delete(0,END)
                cha_A2Entry.insert(0, Gain2A)
        except:
            Gain2A = CHA_A2.get()
            #cha_A2Entry.delete(0,END)
            #cha_A2Entry.insert(0, CHA_A2.get())
        #
        FFTBuffA = Digital_RC_High_Pass( FFTBuffA, TC1A, Gain1A )
        FFTBuffA = Digital_RC_High_Pass( FFTBuffA, TC2A, Gain2A )
    if CHB_RC_HP.get() == 1:
        try:
            TC1B = float(chb_TC1Entry.get())
            if TC1B < 0:
                TC1B = 0
                chb_TC1Entry.delete(0, END)
                chb_TC1Entry.insert(0, TC1B)
        except:
            TC1B = CHB_TC1.get()
            #chb_TC1Entry.delete(0,END)
            #chb_TC1Entry.insert(0, CHB_TC1.get())
        try:
            TC2B = float(chb_TC2Entry.get())
            if TC2B < 0:
                TC2B = 0
                chb_TC2Entry.delete(0, END)
                chb_TC2Entry.insert(0, TC2B)
        except:
            TC2B = CHB_TC2.get()
            #chb_TC2Entry.delete(0,END)
            #chb_TC2Entry.insert(0, CHB_TC2.get())
        #
        try:
            Gain1B = float(chb_A1Entry.get())
            if Gain1B < 0:
                Gain1B = 1
                chb_A1Entry.delete(0,END)
                chb_A1Entry.insert(0, Gain1B)
        except:
            Gain1B = CHB_A1.get()
            #chb_A1Entry.delete(0,END)
            #chb_A1Entry.insert(0, CHB_A1.get())
        try:
            Gain2B = float(chb_A2Entry.get())
            if Gain2B < 0:
                Gain2B = 0
                chb_A2Entry.delete(0,END)
                chb_A2Entry.insert(0, Gain2B)
        except:
            Gain2B = CHB_A2.get()
            #chb_A2Entry.delete(0,END)
            #chb_A2Entry.insert(0, CHB_A2.get())
        #
        FFTBuffB = Digital_RC_High_Pass( FFTBuffB, TC1B, Gain1B )
        FFTBuffB = Digital_RC_High_Pass( FFTBuffB, TC2B, Gain2B )
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
            if FSweepMode.get() == 1:
                AWGAFreqEntry.delete(0,"end")
                AWGAFreqEntry.insert(0, Reset_Freq)
            if FSweepMode.get() == 2:
                AWGBFreqEntry.delete(0,"end")
                AWGBFreqEntry.insert(0, Reset_Freq)
#
            LoopNum.set(1)
            if FSweepCont.get() == 0:
                RUNstatus.set(0)
#
def MakeHistogram():
    global VBuffA, VBuffB, IBuffA, IBuffB, HBuffA, HBuffB
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I, Xsignal
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
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
    global VBuffA, VBuffB, IBuffA, IBuffB
    global SHOWsamples, SAMPLErate, CHAperiod, CHAfreq, CHBperiod, CHBfreq
    global CHAHW, CHALW, CHADCy, CHBHW, CHBLW, CHBDCy, ShowC1_V, ShowC2_V
    global CHABphase, CHBADelayR1, CHBADelayR2, CHBADelayF
    
    anr1 = bnr1 = 0
    anf1 = bnf1 = 1
    anr2 = bnr2 = 2
    
# search channel A
    if ShowC1_V.get() == 1:
        MidV1 = (MaxV1+MinV1)/2
        Arising = [i for (i, val) in enumerate(VBuffA) if val >= MidV1 and VBuffA[i-1] < MidV1]
        Afalling = [i for (i, val) in enumerate(VBuffA) if val <= MidV1 and VBuffA[i-1] > MidV1]
        AIrising = [i - (VBuffA[i] - MidV1)/(VBuffA[i] - VBuffA[i-1]) for i in Arising]
        AIfalling = [i - (MidV1 - VBuffA[i])/(VBuffA[i-1] - VBuffA[i]) for i in Afalling]
        
        CHAfreq = SAMPLErate / numpy.mean(numpy.diff(AIrising))
        CHAperiod = (numpy.mean(numpy.diff(AIrising)) * 1000.0) / SAMPLErate # time in mSec
        if len(Arising) > 0 or len(Afalling) > 0:
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
# search channel B
    if ShowC2_V.get() == 1:
        MidV2 = (MaxV2+MinV2)/2
        Brising = [i for (i, val) in enumerate(VBuffB) if val >= MidV2 and VBuffB[i-1] < MidV2]
        Bfalling = [i for (i, val) in enumerate(VBuffB) if val <= MidV2 and VBuffB[i-1] > MidV2]
        BIrising = [i - (VBuffB[i] - MidV2)/(VBuffB[i] - VBuffB[i-1]) for i in Brising]
        BIfalling = [i - (MidV2 - VBuffB[i])/(VBuffB[i-1] - VBuffB[i]) for i in Bfalling]
        
        CHBfreq = SAMPLErate / numpy.mean(numpy.diff(BIrising))
        CHBperiod = (numpy.mean(numpy.diff(BIrising)) * 1000.0) / SAMPLErate # time in mSec
        if len(Brising) > 0 or len(Bfalling) > 0:
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
def FindTriggerSample(TrgBuff): # find trigger time sample point of passed waveform array
    global AutoLevel, TgInput, TRIGGERlevel, TRIGGERentry, DX, SAMPLErate, Is_Triggered
    global HoldOffentry, HozPossentry, TRIGGERsample, TRACEsize, HozPoss, hozpos
    
    # Set the TRACEsize variable
    TRACEsize = SHOWsamples               # Set the trace length
    DX = 0
    Is_Triggered = 0
    try:
        TrgMin = numpy.amin(TrgBuff)
    except:
        TrgMin = 0.0
    try:
        TrgMax = numpy.amax(TrgBuff)
    except:
        TrgMax = 0.0
# Find trigger sample
    try:
        if AutoLevel.get() == 1:
            TRIGGERlevel = (TrgMin + TrgMax)/2
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
    n = TRIGGERsample
    TRIGGERlevel2 = 0.99 * TRIGGERlevel # Hysteresis to avoid triggering on noise
    if TRIGGERlevel2 < TrgMin:
        TRIGGERlevel2 = TrgMin
    if TRIGGERlevel2 > TrgMax:
        TRIGGERlevel2 = TrgMax
    ChInput = TrgBuff[int(n)]
    Prev = ChInput
    while ( ChInput >= TRIGGERlevel2) and n < Nmax:
        n = n + 1
        ChInput = TrgBuff[int(n)]
    while (ChInput <= TRIGGERlevel) and n < Nmax:
        Prev = ChInput
        n = n + 1
        ChInput = TrgBuff[int(n)]
    DY = ChInput - Prev
    if DY != 0.0:
        DX = (TRIGGERlevel - Prev)/DY # calculate interpolated trigger point
    else:
        DX = 0
    if TgEdge.get() == 1:
        TRIGGERlevel2 = 1.01 * TRIGGERlevel
        if TRIGGERlevel2 < TrgMin:
            TRIGGERlevel2 = TrgMin
        if TRIGGERlevel2 > TrgMax:
            TRIGGERlevel2 = TrgMax
        ChInput = TrgBuff[int(n)]
        Prev = ChInput
        while (ChInput <= TRIGGERlevel2) and n < Nmax:
            n = n + 1
            ChInput = TrgBuff[int(n)]
        while (ChInput >= TRIGGERlevel) and n < Nmax:
            Prev = ChInput
            n = n + 1
            ChInput = TrgBuff[int(n)]
        DY = Prev - ChInput
        try:
            DX = (Prev - TRIGGERlevel)/DY # calculate interpolated trigger point
        except:
            DX = 0
    
# check to insure trigger point is in bounds                
    if n < Nmax:
        TRIGGERsample = n - 1
        Is_Triggered = 1
    elif n > Nmax: # Didn't find edge in first 2/3 of data set
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
def DestroyDigScreen():
    global win2, DigScreenStatus
    
    DigScreenStatus.set(0)
    win2.destroy()

def sel():
    global devx, DevID
    global D0, D1, D2, D3, D4, D5, D6, D7
    global PIO_0, PIO_1, PIO_2, PIO_3
    # sending 0x50 = set to 0, 0x51 = set to 1
    if D0.get() > 0:
        devx.ctrl_transfer( 0x40, D0.get(), PIO_0, 0, 0, 0, 100) # set PIO 0
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_0, 0, 0, 1, 100)
    if D1.get() > 0:
        devx.ctrl_transfer( 0x40, D1.get(), PIO_1, 0, 0, 0, 100) # set PIO 1
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_1, 0, 0, 1, 100)
    if D2.get() > 0:
        devx.ctrl_transfer( 0x40, D2.get(), PIO_2, 0, 0, 0, 100) # set PIO 2
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_2, 0, 0, 1, 100)
    if D3.get() > 0:
        devx.ctrl_transfer( 0x40, D3.get(), PIO_3, 0, 0, 0, 100) # set PIO 3
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_3, 0, 0, 1, 100)
    if D4.get() > 0:
        devx.ctrl_transfer( 0x40, D4.get(), 4, 0, 0, 0, 100) # set PIO 4
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100)
    if D5.get() > 0:
        devx.ctrl_transfer( 0x40, D5.get(), 5, 0, 0, 0, 100) # set PIO 5
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100)
    if D6.get() > 0:
        devx.ctrl_transfer( 0x40, D6.get(), 6, 0, 0, 0, 100) # set PIO 6
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100)
    if D7.get() > 0:
        devx.ctrl_transfer( 0x40, D7.get(), 7, 0, 0, 0, 100) # set PIO 7
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100)

def MakeDigScreen():
    global D0, D1, D2, D3, D4, D5, D6, D7
    global PIO_0, PIO_1, PIO_2, PIO_3
    global DigScreenStatus, DacScreenStatus, win2, MuxScreenStatus
    # setup Dig output window
    if DigScreenStatus.get() == 0 and DacScreenStatus.get() == 0 and MuxScreenStatus.get() == 0:
        DigScreenStatus.set(1)
        win2 = Toplevel()
        win2.title("Dig Out")
        win2.resizable(FALSE,FALSE)
        win2.protocol("WM_DELETE_WINDOW", DestroyDigScreen)
        rb1 = Radiobutton(win2, text="D0-0", variable=D0, value=0x50, command=sel )
        rb1.grid(row=2, column=0, sticky=W)
        rb0z = Radiobutton(win2, text="D0-Z", variable=D0, value=0, command=sel )
        rb0z.grid(row=2, column=1, sticky=W)
        rb2 = Radiobutton(win2, text="D0-1", variable=D0, value=0x51, command=sel )
        rb2.grid(row=2, column=2, sticky=W)
        rb3 = Radiobutton(win2, text="D1-0", variable=D1, value=0x50, command=sel )
        rb3.grid(row=3, column=0, sticky=W)
        rb3z = Radiobutton(win2, text="D1-Z", variable=D1, value=0, command=sel )
        rb3z.grid(row=3, column=1, sticky=W)
        rb4 = Radiobutton(win2, text="D1-1", variable=D1, value=0x51, command=sel )
        rb4.grid(row=3, column=2, sticky=W)
        rb5 = Radiobutton(win2, text="D2-0", variable=D2, value=0x50, command=sel )
        rb5.grid(row=4, column=0, sticky=W)
        rb5z = Radiobutton(win2, text="D2-Z", variable=D2, value=0, command=sel )
        rb5z.grid(row=4, column=1, sticky=W)
        rb6 = Radiobutton(win2, text="D2-1", variable=D2, value=0x51, command=sel )
        rb6.grid(row=4, column=2, sticky=W)
        rb7 = Radiobutton(win2, text="D3-0", variable=D3, value=0x50, command=sel )
        rb7.grid(row=5, column=0, sticky=W)
        rb7z = Radiobutton(win2, text="D3-Z", variable=D3, value=0, command=sel )
        rb7z.grid(row=5, column=1, sticky=W)
        rb8 = Radiobutton(win2, text="D3-1", variable=D3, value=0x51, command=sel )
        rb8.grid(row=5, column=2, sticky=W)
        rb9 = Radiobutton(win2, text="D4-0", variable=D4, value=0x50, command=sel )
        rb9.grid(row=6, column=0, sticky=W)
        rb9z = Radiobutton(win2, text="D4-Z", variable=D4, value=0, command=sel )
        rb9z.grid(row=6, column=1, sticky=W)
        rb10 = Radiobutton(win2, text="D4-1", variable=D4, value=0x51, command=sel )
        rb10.grid(row=6, column=2, sticky=W)
        rb11 = Radiobutton(win2, text="D5-0", variable=D5, value=0x50, command=sel )
        rb11.grid(row=7, column=0, sticky=W)
        rb11z = Radiobutton(win2, text="D5-Z", variable=D5, value=0, command=sel )
        rb11z.grid(row=7, column=1, sticky=W)
        rb12 = Radiobutton(win2, text="D5-1", variable=D5, value=0x51, command=sel )
        rb12.grid(row=7, column=2, sticky=W)
        rb13 = Radiobutton(win2, text="D6-0", variable=D6, value=0x50, command=sel )
        rb13.grid(row=8, column=0, sticky=W)
        rb13z = Radiobutton(win2, text="D6-Z", variable=D6, value=0, command=sel )
        rb13z.grid(row=8, column=1, sticky=W)
        rb13 = Radiobutton(win2, text="D6-1", variable=D6, value=0x51, command=sel )
        rb13.grid(row=8, column=2, sticky=W)
        rb14 = Radiobutton(win2, text="D7-0", variable=D7, value=0x50, command=sel )
        rb14.grid(row=9, column=0, sticky=W)
        rb14z = Radiobutton(win2, text="D7-Z", variable=D7, value=0, command=sel )
        rb14z.grid(row=9, column=1, sticky=W)
        rb15 = Radiobutton(win2, text="D7-1", variable=D7, value=0x51, command=sel )
        rb15.grid(row=9, column=2, sticky=W)

        dismissbutton = Button(win2, text="Dismiss", command=DestroyDigScreen)
        dismissbutton.grid(row=10, column=0, sticky=W)
#
def DestroyDacScreen():
    global win1, DacScreenStatus
    
    DacScreenStatus.set(0)
    win1.destroy()

def sel0(temp):
    global devx, DevID
    global PIO_0, PIO_1, PIO_2, PIO_3
    global DAC0
    # sending 0x50 = set to 0, 0x51 = set to 1
    if DAC0.get() == 1:
        devx.ctrl_transfer( 0x40, 0x50, PIO_0, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x50, 4, 0, 0, 0, 100) # set PIO 4 0
    elif DAC0.get() == 4:
        devx.ctrl_transfer( 0x40, 0x50, PIO_0, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x51, 4, 0, 0, 0, 100) # set PIO 4 1
    elif DAC0.get() == 2:
        devx.ctrl_transfer( 0x40, 0x50, PIO_0, 0, 0, 0, 100) # set PIO 0 0
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC0.get() == 3:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 0, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x50, 4, 0, 0, 0, 100) # set PIO 4
    elif DAC0.get() == 5:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_0, 0, 0, 1, 100) # set PIO 0 Z
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC0.get() == 7:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_0, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x51, 4, 0, 0, 0, 100) # set PIO 4 1
    elif DAC0.get() == 8:
        devx.ctrl_transfer( 0x40, 0x51, PIO_0, 0, 0, 0, 100) # set PIO 0 1
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC0.get() == 6:
        devx.ctrl_transfer( 0x40, 0x51, PIO_0, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x50, 4, 0, 0, 0, 100) # set PIO 4
    elif DAC0.get() == 9:
        devx.ctrl_transfer( 0x40, 0x51, PIO_0, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x51, 4, 0, 0, 0, 100) # set PIO 4

def sel1(temp):
    global devx, DevID
    global PIO_0, PIO_1, PIO_2, PIO_3
    global DAC1
    # sending 0x50 = set to 0, 0x51 = set to 1
    if DAC1.get() == 1:
        devx.ctrl_transfer( 0x40, 0x50, PIO_1, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x50, 5, 0, 0, 0, 100) # set PIO 4 0
    elif DAC1.get() == 4:
        devx.ctrl_transfer( 0x40, 0x50, PIO_1, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x51, 5, 0, 0, 0, 100) # set PIO 4 1
    elif DAC1.get() == 2:
        devx.ctrl_transfer( 0x40, 0x50, PIO_1, 0, 0, 0, 100) # set PIO 0 0
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC1.get() == 3:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_1, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x50, 5, 0, 0, 0, 100) # set PIO 4
    elif DAC1.get() == 5:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_1, 0, 0, 1, 100) # set PIO 0 Z
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC1.get() == 7:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_1, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x51, 5, 0, 0, 0, 100) # set PIO 4 1
    elif DAC1.get() == 8:
        devx.ctrl_transfer( 0x40, 0x51, PIO_1, 0, 0, 0, 100) # set PIO 0 1
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC1.get() == 6:
        devx.ctrl_transfer( 0x40, 0x51, PIO_1, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x50, 5, 0, 0, 0, 100) # set PIO 4
    elif DAC1.get() == 9:
        devx.ctrl_transfer( 0x40, 0x51, PIO_1, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x51, 5, 0, 0, 0, 100) # set PIO 4

def sel2(temp):
    global devx, DevID
    global PIO_0, PIO_1, PIO_2, PIO_3
    global DAC2
    # sending 0x50 = set to 0, 0x51 = set to 1
    if DAC2.get() == 1:
        devx.ctrl_transfer( 0x40, 0x50, PIO_2, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x50, 6, 0, 0, 0, 100) # set PIO 4 0
    elif DAC2.get() == 4:
        devx.ctrl_transfer( 0x40, 0x50, PIO_2, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x51, 6, 0, 0, 0, 100) # set PIO 4 1
    elif DAC2.get() == 2:
        devx.ctrl_transfer( 0x40, 0x50, PIO_2, 0, 0, 0, 100) # set PIO 0 0
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC2.get() == 3:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_2, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x50, 6, 0, 0, 0, 100) # set PIO 4
    elif DAC2.get() == 5:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_2, 0, 0, 1, 100) # set PIO 0 Z
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC2.get() == 7:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_2, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x51, 6, 0, 0, 0, 100) # set PIO 4 1
    elif DAC2.get() == 8:
        devx.ctrl_transfer( 0x40, 0x51, PIO_2, 0, 0, 0, 100) # set PIO 0 1
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC2.get() == 6:
        devx.ctrl_transfer( 0x40, 0x51, PIO_2, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x50, 6, 0, 0, 0, 100) # set PIO 4
    elif DAC2.get() == 9:
        devx.ctrl_transfer( 0x40, 0x51, PIO_2, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x51, 6, 0, 0, 0, 100) # set PIO 4

def sel3(temp):
    global devx, DevID
    global PIO_0, PIO_1, PIO_2, PIO_3
    global DAC3
    # sending 0x50 = set to 0, 0x51 = set to 1
    if DAC3.get() == 1:
        devx.ctrl_transfer( 0x40, 0x50, PIO_3, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x50, 7, 0, 0, 0, 100) # set PIO 4 0
    elif DAC3.get() == 4:
        devx.ctrl_transfer( 0x40, 0x50, PIO_3, 0, 0, 0, 100) # set PIO 0 0
        devx.ctrl_transfer( 0x40, 0x51, 7, 0, 0, 0, 100) # set PIO 4 1
    elif DAC3.get() == 2:
        devx.ctrl_transfer( 0x40, 0x50, PIO_3, 0, 0, 0, 100) # set PIO 0 0
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC3.get() == 3:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_3, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x50, 7, 0, 0, 0, 100) # set PIO 4
    elif DAC3.get() == 5:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_3, 0, 0, 1, 100) # set PIO 0 Z
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC3.get() == 7:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_3, 0, 0, 1, 100) # set PIO 0 Z
        devx.ctrl_transfer( 0x40, 0x51, 7, 0, 0, 0, 100) # set PIO 4 1
    elif DAC3.get() == 8:
        devx.ctrl_transfer( 0x40, 0x51, PIO_3, 0, 0, 0, 100) # set PIO 0 1
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100) # set PIO 4 Z
    elif DAC3.get() == 6:
        devx.ctrl_transfer( 0x40, 0x51, PIO_3, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x50, 7, 0, 0, 0, 100) # set PIO 4
    elif DAC3.get() == 9:
        devx.ctrl_transfer( 0x40, 0x51, PIO_3, 0, 0, 0, 100) # set PIO 0
        devx.ctrl_transfer( 0x40, 0x51, 7, 0, 0, 0, 100) # set PIO 4
                
def MakeDacScreen():
    global DAC0, DAC1, DAC2, DAC3
    global DacScreenStatus, DigScreenStatus, win1, MuxScreenStatus
    # setup Dig output window
    if DacScreenStatus.get() == 0 and DigScreenStatus.get() == 0 and MuxScreenStatus.get() == 0:
        DacScreenStatus.set(1)
        win1 = Toplevel()
        win1.title("DAC Out")
        win1.resizable(FALSE,FALSE)
        win1.protocol("WM_DELETE_WINDOW", DestroyDacScreen)
        DAC0 = Scale(win1, from_=9, to=1, orient=VERTICAL, command=sel0, length=90)
        DAC0.grid(row=0, column=0, sticky=W)
        DAC1 = Scale(win1, from_=9, to=1, orient=VERTICAL, command=sel1, length=90)
        DAC1.grid(row=0, column=1, sticky=W)
        DAC2 = Scale(win1, from_=9, to=1, orient=VERTICAL, command=sel2, length=90)
        DAC2.grid(row=0, column=2, sticky=W)
        DAC3 = Scale(win1, from_=9, to=1, orient=VERTICAL, command=sel3, length=90)
        DAC3.grid(row=0, column=3, sticky=W)        

        dismissbutton = Button(win1, text="Dismiss", command=DestroyDacScreen)
        dismissbutton.grid(row=1, column=0, columnspan=2, sticky=W)
#
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
    global VBuffA, VBuffB, IBuffA, IBuffB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD, MuxScreenStatus
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global VmemoryMuxA, VmemoryMuxB, VmemoryMuxC, VmemoryMuxD
    global FFTBuffA, FFTBuffB, FFTwindowshape
    global T1Vline, T2Vline, T1Iline, T2Iline
    global TMAVline, TMBVline, TMCVline, TMDVline
    global Tmathline, TMXline, TMYline
    global MathString, MathAxis, MathXString, MathYString, MathXAxis, MathYAxis
    global Triggerline, Triggersymbol, TgInput, TgEdge, HoldOff, HoldOffentry
    global X0L, Y0T, GRW, GRH, MouseX, MouseY, MouseCAV, MouseCAI, MouseCBV, MouseCBI
    global MouseMuxA, MouseMuxB, MouseMuxC, MouseMuxD
    global Ymin, Ymax, Xmin, Xmax
    global SHOWsamples, ZOHold, AWGBMode
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD
    global Show_MathX, Show_MathY
    global TRACES, TRACESread, RUNstatus
    global AutoCenterA, AutoCenterB
    global CHAsb, CHBsb, CHAOffset, CHBOffset, CHAIsb, CHBIsb, CHAIOffset, CHBIOffset
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate, SCstart
    global TRIGGERsample, TRACEsize, DX
    global TRIGGERlevel, TRIGGERentry, AutoLevel
    global InOffA, InGainA, InOffB, InGainB
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHAVPosEntry, CHBIPosEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
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
    Ymin = Y0T                  # Minimum position of time grid (top)
    Ymax = Y0T + GRH            # Maximum position of time grid (bottom)
    Xmin = X0L                  # Minimum position of time grid (left)
    Xmax = X0L + GRW            # Maximum position of time grid (right)
    # get time scale
    try:
        TIMEdiv = float(eval(TMsb.get()))
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    # prevent divide by zero error
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.01
    # Check for Auto Centering
    if AutoCenterA.get() > 0:
        CHAOffset = DCV1
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, ' {0:.2f} '.format(CHAOffset))
    if AutoCenterB.get() > 0:
        CHBOffset = DCV2
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, ' {0:.2f} '.format(CHBOffset))
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
        CH1IpdvRange = float(eval(CHAIsb.get()))
    except:
        CHAIsb.delete(0,END)
        CHAIsb.insert(0, CH1IpdvRange)
    try:
        CH2IpdvRange = float(eval(CHBIsb.get()))
    except:
        CHBIsb.delete(0,END)
        CHBIsb.insert(0, CH2IpdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntry.get()))
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    try:
        CHAIOffset = float(eval(CHAIPosEntry.get()))
    except:
        CHAIPosEntry.delete(0,END)
        CHAIPosEntry.insert(0, CHAIOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntry.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    try:
        CHBIOffset = float(eval(CHBIPosEntry.get()))
    except:
        CHBIPosEntry.delete(0,END)
        CHBIPosEntry.insert(0, CHBIOffset)
    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    if CH1IpdvRange < 0.1:
        CH1IpdvRange = 0.1
    if CH2IpdvRange < 0.1:
        CH2IpdvRange = 0.1
#
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
    hldn = int(HoldOff * AWGSAMPLErate/1000 )
    hozpos = int(HozPoss * AWGSAMPLErate/1000 )
    if hozpos < 0:
        hozpos = 0        
    #  drawing the traces 
    if TRACEsize == 0:                          # If no trace, skip rest of this routine
        T1Vline = []                            # Trace line channel A V
        T2Vline = []                            # Trace line channel B V
        T1Iline = []
        T2Iline = []
        TMAVline = []                   # V Trace line Mux channel A
        TMBVline = []                   # V Trace line Mux channel B
        TMCVline = []                   # V Trace line Mux channel C
        TMDVline = []                   # V Trace line Mux channel D
        Tmathline = []                  # math trce line
        return() 

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
        CurOffA = float(CHAIOffsetEntry.get()) # leave in mA
    except:
        CurOffA = 0.0
    try:
        CurOffB = float(CHBIOffsetEntry.get()) # leave in mA
    except:
        CurOffB = 0.0
    try:
        CurGainA = float(CHAIGainEntry.get())
    except:
        CurGainA = 1.0
    try:
        CurGainB = float(CHBIGainEntry.get())
    except:
        CurGainB = 1.0

    # set and/or corrected for in range
    if TgInput.get() > 0:
        SCmin = int(-1 * TRIGGERsample)
        SCmax = int(TRACEsize - TRIGGERsample - 20)
    else:
        SCmin = hldn
        SCmax = TRACEsize
    if SCstart < SCmin:             # No reading before start of array
        SCstart = SCmin
    if SCstart  > SCmax:            # No reading after end of array
        SCstart = SCmax

    # Make Trace lines etc.

    Yconv1 = float(GRH/10.0) / CH1pdvRange    # Vertical Conversion factors from samples to screen points
    Yconv2 = float(GRH/10.0) / CH2pdvRange
    YIconv1 = float(GRH/10.0) / CH1IpdvRange
    YIconv2 = float(GRH/10.0) / CH2IpdvRange
    Xconv1 = float(GRW/10.0) / CH1pdvRange    # Horizontal Conversion factors from samples to screen points
    Xconv2 = float(GRW/10.0) / CH2pdvRange
    XIconv1 = float(GRW/10.0) / CH1IpdvRange
    XIconv2 = float(GRW/10.0) / CH2IpdvRange
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
    if MathAxis == "V-A":
        YconvM = Yconv1
        CHMOffset = CHAOffset
    elif MathAxis == "V-B":
        YconvM = Yconv2
        CHMOffset = CHBOffset
    elif MathAxis == "I-A":
        YconvM = YIconv1
        CHMOffset = CHAIOffset
    elif MathAxis == "I-B":
        YconvM = YIconv2
        CHMOffset = CHBIOffset
    else:
        YconvM = Yconv1
        CHMOffset = CHAOffset
# include ploting X and Y math formulas vs time
    if MathYAxis == "V-A":
        YconvMxy = Yconv1
        CHMYOffset = CHAOffset
    elif MathYAxis == "V-B":
        YconvMxy = Yconv2
        CHMYOffset = CHBOffset
    elif MathYAxis == "I-A":
        YconvMxy = YIconv1
        CHMYOffset = CHAIOffset
    elif MathYAxis == "I-B":
        YconvMxy = YIconv2
        CHMYOffset = CHBIOffset
    else:
        YconvMxy = Yconv1
        CHMYOffset = CHAOffset
    if MathXAxis == "V-A":
        XconvMxy = Yconv1
        CHMXOffset = CHAOffset
    elif MathXAxis == "V-B":
        XconvMxy = Yconv2
        CHMXOffset = CHBOffset
    elif MathYAxis == "I-A":
        XconvMxy = YIconv1
        CHMXOffset = CHAIOffset
    elif MathXAxis == "I-B":
        XconvMxy = YIconv2
        CHMXOffset = CHBIOffset
    else:
        XconvMxy = Yconv1
        CHMXOffset = CHAOffset
    c1 = GRH / 2.0 + Y0T    # fixed correction channel A
    c2 = GRH / 2.0 + Y0T    # fixed correction channel B
 
    DISsamples = SAMPLErate * 10.0 * TIMEdiv / 1000.0 # number of samples to display
    T1Vline = []                    # V Trace line channel A
    T2Vline = []                    # V Trace line channel B
    T1Iline = []                    # I Trace line channel A
    T2Iline = []                    # I Trace line channel B
    TMAVline = []                   # V Trace line Mux channel A
    TMBVline = []                   # V Trace line Mux channel B
    TMCVline = []                   # V Trace line Mux channel C
    TMDVline = []                   # V Trace line Mux channel D
    Tmathline = []                  # math trce line
    TMXline = []                    # X math Trace line
    TMYline = []                    # Y math Trace line
    if len(VBuffA) < 4 and len(VBuffB) < 4 and len(IBuffA) < 4 and len(IBuffB) < 4:
        return
    t = int(SCstart + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
    if t < 0:
        t = 0
    x = 0                           # Horizontal screen pixel
#
    ypv1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
    ypi1 = int(c1 - YIconv1 * (IBuffA[t] - CHAIOffset))
    ypv2 = int(c2 - Yconv2 * (VBuffB[t] - CHBOffset))
    ypi2 = int(c1 - YIconv2 * (IBuffB[t] - CHBIOffset))
#
    if (DISsamples <= GRW):
        Xstep = GRW / DISsamples
        if AWGBMode.get() == 2:
            xa = int(Xstep/-2) - int(Xstep*DX)
        else:
            xa = 0 - int(Xstep*DX)       # adjust start pixel for interpolated trigger point
        x = 0 - int(Xstep*DX)
        Tstep = 1
        x1 = 0                      # x position of trace line
        xa1 = 0
        y1 = 0.0                    # y position of trace line
        ypv1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
        ytemp = IBuffA[t]
        ypi1 = int(c1 - YIconv1 * (ytemp - CHAIOffset))
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
        ytemp = IBuffB[t]
        ypi2 = int(c1 - YIconv2 * (ytemp - CHBIOffset))
        ypm = ypmx = ypmy = GRH / 2.0 + Y0T
        if TgInput.get() == 0:
            Xlimit = GRW
        else:
            Xlimit = GRW+Xstep
        while x <= Xlimit:
            if t < TRACEsize:
                xa1 = xa + X0L
                x1 = x + X0L
                y1 = int(c1 - Yconv1 * (VBuffA[t] - CHAOffset))
                ytemp = IBuffA[t]
                yi1 = int(c1 - YIconv1 * (ytemp - CHAIOffset))
                
                if y1 < Ymin: # clip waveform if going off grid
                    y1 = Ymin
                if y1 > Ymax:
                    y1 = Ymax
                if yi1 < Ymin:
                    yi1 = Ymin
                if yi1 > Ymax:
                    yi1 = Ymax
                if ShowC1_V.get() == 1 :
                    if ZOHold.get() == 1:
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(ypv1))
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(y1))
                    else:    
                        T1Vline.append(int(xa1))
                        T1Vline.append(int(y1))
                    ypv1 = y1
                if ShowC1_I.get() == 1:
                    if ZOHold.get() == 1:
                        T1Iline.append(int(xa1))
                        T1Iline.append(int(ypi1))
                        T1Iline.append(int(xa1))
                        T1Iline.append(int(yi1))
                    else:
                        T1Iline.append(int(xa1))
                        T1Iline.append(int(yi1))
                    ypi1 = yi1
                        
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
                    if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                        MouseMuxA = ypvma
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
                    if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                        MouseMuxB = ypvmb
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
                    if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                        MouseMuxC = ypvmc
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
                    if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                        MouseMuxD = ypvmd
                if ShowC2_I.get() == 1:
                    
                    ytemp = IBuffB[t]
                    yi1 = int(c1 - YIconv2 * (ytemp - CHBIOffset))
                    if yi1 < Ymin:
                        yi1 = Ymin
                    if yi1 > Ymax:
                        yi1 = Ymax
                    if (ZOHold.get() == 1):
                        T2Iline.append(int(x1))
                        T2Iline.append(int(ypi2))
                        T2Iline.append(int(x1))
                        T2Iline.append(int(yi1))
                    else:
                        T2Iline.append(int(x1))
                        T2Iline.append(int(yi1))
                    ypi2 = yi1
                if MathTrace.get() > 0:
                    if MathTrace.get() == 1: # plot sum of CA-V and CB-V
                        y1 = int(c1 - Yconv1 * (VBuffA[t] + VBuffB[t] - CHAOffset))

                    elif MathTrace.get() == 2: # plot difference of CA-V and CB-V 
                        y1 = int(c1 - Yconv1 * (VBuffA[t] - VBuffB[t] - CHAOffset))

                    elif MathTrace.get() == 3: # plot difference of CB-V and CA-V 
                        y1 = int(c2 - Yconv2 * (VBuffB[t] - VBuffA[t] - CHBOffset))

                    elif MathTrace.get() == 4: # plot product of CA-V and CA-I
                        Ypower = VBuffA[t] * IBuffA[t] # mAmps * Volts = mWatts
                        ytemp = YIconv1 * (Ypower - CHAIOffset)
                        y1 = int(c1 - ytemp)

                    elif MathTrace.get() == 5: # plot product of CB-V and CB-I
                        Ypower = VBuffB[t] * IBuffB[t] # mAmps * Volts = mWatts
                        ytemp = YIconv2 * (Ypower - CHBIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 6: # plot ratio of CA-V and CA-I
                        Yohms = VBuffA[t] / (IBuffA[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv1 * (Yohms - CHAIOffset)
                        y1 = int(c1 - ytemp)

                    elif MathTrace.get() == 7: # plot ratio of CB-V and CB-I
                        Yohms = VBuffB[t] / (IBuffB[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv2 * (Yohms - CHBIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 8: # plot difference of CA-I and CB-I
                        Ydif = (IBuffA[t] - IBuffB[t])#  in mA
                        ytemp = YIconv1 * (Ydif - CHAIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 9: # plot difference of CB-I and CA-I
                        Ydif =  (IBuffB[t] - IBuffA[t]) #  in mA
                        ytemp = YIconv2 * (Ydif - CHBIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 10: # plot ratio of CB-V and CA-V
                        try:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / VBuffA[t]) - CHBOffset)) #  voltage gain A to B
                        except:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / 0.000001) - CHBOffset))

                    elif MathTrace.get() == 11: # plot ratio of CB-I and CA-I
                        try:
                            Y1 = (IBuffB[t] / IBuffA[t])  # current gain A to B
                        except:
                            Y1 = (IBuffB[t] / 0.000001)
                        ytemp = YIconv2 * (Y1 - CHBIOffset)
                        y1 = int(c2 - ytemp)
                        
                    elif MathTrace.get() == 12: # plot from equation string
                        # MathString = "(VBuffA[t]+ VBuffB[t] - CHAOffset)"
                        try:
                            MathResult = eval(MathString)
                            MathResult = MathResult - CHMOffset
                            y1 = int(c1 - YconvM * MathResult)
                        except:
                            RUNstatus.set(0)
                            x = Xlimit + 1 # exit loop
                        
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
                        MathResult = MathResult - CHMXOffset
                        y1 = int(c1 - XconvMxy * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = Xlimit + 1 # exit loop
                        
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
                        MathResult = MathResult - CHMYOffset
                        y1 = int(c1 - YconvMxy * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = Xlimit + 1 # exit loop
                        
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
            # remember trace verticle pixel at X mouse location
            if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                MouseCAV = ypv1
                MouseCAI = ypi1
                MouseCBV = ypv2
                MouseCBI = ypi2
            t = int(t + Tstep)
            x = x + Xstep
            xa = xa + Xstep
            
    if (DISsamples > GRW): # if the number of samples is larger than the grid width need to ship over samples
        Xstep = 1
        Tstep = DISsamples / GRW      # number of samples to skip per grid pixel
        x1 = 0.0                          # x position of trace line
        ylo = 0.0                       # ymin position of trace 1 line
        yhi = 0.0                       # ymax position of trace 1 line

        t = int(SCstart + TRIGGERsample) # - (TriggerPos * SAMPLErate) # t = Start sample in trace
        if t < 0:
            t = 0
        x = 0               # Horizontal screen pixel
        ft = t              # time point with fractions
        while (x <= GRW):
            if (t < TRACEsize):
                x1 = x + X0L
                ylo = VBuffA[t] - CHAOffset
                ilo = IBuffA[t] - CHAIOffset
                yhi = ylo
                ihi = ilo
                n = t
                while n < (t + Tstep) and n < TRACEsize:
                    if ( ShowC1_V.get() == 1 ):
                        v = VBuffA[t] - CHAOffset
                        if v < ylo:
                            ylo = v
                        if v > yhi:
                            yhi = v
                    if ( ShowC1_I.get() == 1 ):
                        i = IBuffA[t] - CHAIOffset
                        if i < ilo:
                            ilo = i
                        if i > ihi:
                            ihi = i
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
                    ypv1 = ylo
                if ( ShowC1_I.get() == 1 ):    
                    ilo = int(c1 - YIconv1 * ilo)
                    ihi = int(c1 - YIconv1 * ihi)
                    if (ilo < Ymin):
                        ilo = Ymin
                    if (ilo > Ymax):
                        ilo = Ymax
                    if (ihi < Ymin):
                        ihi = Ymin
                    if (ihi > Ymax):
                        ihi = Ymax
                    T1Iline.append(int(x1))
                    T1Iline.append(int(ilo))        
                    T1Iline.append(int(x1))
                    T1Iline.append(int(ihi))
                    ypi1 = ilo
                ylo = VBuffB[t] - CHBOffset
                ilo = IBuffB[t] - CHBIOffset
                yhi = ylo
                ihi = ilo
                n = t
                if MuxScreenStatus.get() == 0:
                    while n < (t + Tstep) and n < TRACEsize:
                        if ( ShowC2_V.get() == 1 ):
                            v = VBuffB[t] - CHBOffset
                            if v < ylo:
                                ylo = v
                            if v > yhi:
                                yhi = v
                        if ( ShowC2_I.get() == 1 ):
                            i = IBuffB[t] - CHBIOffset
                            if i < ilo:
                                ilo = i
                            if i > ihi:
                                ihi = i
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
                        ypv2 = ylo
                    if ( ShowC2_I.get() == 1 ):
                        ilo = int(c2 - YIconv2 * ilo)
                        ihi = int(c2 - YIconv2 * ihi)
                        if (ilo < Ymin):
                            ilo = Ymin
                        if (ilo > Ymax):
                            ilo = Ymax
                        if (ihi < Ymin):
                            ihi = Ymin
                        if (ihi > Ymax):
                            ihi = Ymax
                        T2Iline.append(int(x1))
                        T2Iline.append(int(ilo))        
                        T2Iline.append(int(x1))
                        T2Iline.append(int(ihi))
                        ypi2 = ilo
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
                        if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                            MouseMuxA = ylo
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
                        if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                            MouseMuxB = ylo
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
                        if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                            MouseMuxC = ylo
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
                        if (MouseX - X0L) > (x - Xstep) and (MouseX - X0L) < (x + Xstep):
                            MouseMuxD = ylo
                    if ( ShowC2_I.get() == 1 ):
                        while n < (t + Tstep) and n < TRACEsize:
                            i = IBuffB[t] - CHBIOffset
                            if i < ilo:
                                ilo = i
                            if i > ihi:
                                ihi = i
                            n = n + 1
                        ilo = int(c2 - YIconv2 * ilo)
                        ihi = int(c2 - YIconv2 * ihi)
                        if (ilo < Ymin):
                            ilo = Ymin
                        if (ilo > Ymax):
                            ilo = Ymax
                        if (ihi < Ymin):
                            ihi = Ymin
                        if (ihi > Ymax):
                            ihi = Ymax
                        T2Iline.append(int(x1))
                        T2Iline.append(int(ilo))        
                        T2Iline.append(int(x1))
                        T2Iline.append(int(ihi))
                if MathTrace.get() > 0:
                    if MathTrace.get() == 1: # plot sum of CA-V and CB-V
                        y1 = int(c1 - Yconv1 * (VBuffA[t] + VBuffB[t] - CHAOffset))

                    elif MathTrace.get() == 2: # plot difference of CA-V and CB-V 
                        y1 = int(c1 - Yconv1 * (VBuffA[t] - VBuffB[t] - CHAOffset))

                    elif MathTrace.get() == 3: # plot difference of CB-V and CA-V 
                        y1 = int(c2 - Yconv2 * (VBuffB[t] - VBuffA[t] - CHBOffset))

                    elif MathTrace.get() == 4: # plot product of CA-V and CA-I
                        Ypower = VBuffA[t] * IBuffA[t] # mAmps * Volts = mWatts
                        ytemp = YIconv1 * (Ypower - CHAIOffset)
                        y1 = int(c1 - ytemp)                                            

                    elif MathTrace.get() == 5: # plot product of CB-V and CB-I
                        Ypower = VBuffB[t] * IBuffB[t] # mAmps * Volts = mWatts
                        ytemp = YIconv2 * (Ypower - CHBIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 6: # plot ratio of CA-V and CA-I
                        Yohms = VBuffA[t] / (IBuffA[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv1 * (Yohms- CHAIOffset)
                        y1 = int(c1 - ytemp)

                    elif MathTrace.get() == 7: # plot ratio of CB-V and CB-I
                        Yohms = VBuffB[t] / (IBuffB[t] / 1000.0) #  Volts / Amps = ohms
                        ytemp = YIconv2 * (Yohms - CHBIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 8: # plot difference of CA-I and CB-I
                        Ydif = (IBuffA[t] - IBuffB[t]) #  in mA
                        ytemp = YIconv1 * (Ydif - CHAIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 9: # plot difference of CB-I and CA-I
                        Ydif = (IBuffB[t] - IBuffA[t])  # in mA
                        ytemp = YIconv2 * (Ydif - CHBIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 10: # plot ratio of CB-V and CA-V
                        try:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / VBuffA[t]) - CHBOffset)) #  voltage gain A to B
                        except:
                            y1 = int(c1 - Yconv2 * ((VBuffB[t] / 0.000001) - CHBOffset))
                    elif MathTrace.get() == 11: # plot ratio of CB-I and CA-I
                        try:
                            Y1 = (IBuffB[t] / IBuffA[t]) # current gain A to B
                        except:
                            Y1 = (IBuffB[t] / 0.000001)
                        ytemp = YIconv2 * (Y1 - CHBIOffset)
                        y1 = int(c2 - ytemp)

                    elif MathTrace.get() == 12: # plot from equation string
                        # MathString = "(VBuffA[t]+ VBuffB[t] - CHAOffset)"
                        try:
                            MathResult = eval(MathString)
                            MathResult = MathResult - CHMOffset
                            y1 = int(c1 - YconvM * MathResult)
                        except:
                            RUNstatus.set(0)
                            x = GRW + 1
                        
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
                        MathResult = MathResult - CHMXOffset
                        y1 = int(c1 - XconvMxy * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = GRW + 1
                        
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
                        MathResult = MathResult - CHMYOffset
                        y1 = int(c1 - YconvMxy * MathResult)
                    except:
                        RUNstatus.set(0)
                        x = GRW + 1
                        
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
            if (MouseX - X0L) > (x - 1) and (MouseX - X0L) < (x + 1):
                MouseCAV = ypv1
                MouseCAI = ypi1
                MouseCBV = ypv2
                MouseCBI = ypi2
            t = int(ft)
            x = x + Xstep

    # Make trigger triangle pointer
    Triggerline = []                # Trigger pointer
    Triggersymbol = []                # Trigger symbol
    if TgInput.get() > 0:
        if TgInput.get() == 1 : # triggering on CA-V
            x1 = X0L
            ytemp = Yconv1 * (float(TRIGGERlevel)-CHAOffset) # / InGainA
            y1 = int(c1 - ytemp)
        elif TgInput.get() == 2:  # triggering on CA-I
            x1 = X0L+GRW
            y1 = int(c1 - YIconv1 * (float(TRIGGERlevel) - CHAIOffset))
        elif TgInput.get() == 3:  # triggering on CB-V
            x1 = X0L
            ytemp = Yconv2 * (float(TRIGGERlevel)-CHBOffset) # / InGainB         
            y1 = int(c2 - ytemp)
        elif TgInput.get() == 4: # triggering on CB-I
            x1 = X0L+GRW
            y1 = int(c2 - YIconv2 * (float(TRIGGERlevel) - CHBIOffset))
            
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
    global VBuffA, VBuffB, IBuffA, IBuffB
    global VmemoryA, VmemoryB, ImemoryA, ImemoryB
    global TXYline, MathXString, MathYString, MathXAxis, MathYAxis
    global HoldOff, HoldOffentry
    global X0LXY, Y0TXY, GRWXY, GRHXY
    global YminXY, YmaxXY, XminXY, XmaxXY
    global SHOWsamples, ZOHold, AWGBMode
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I
    global TRACES, TRACESread, RUNstatus
    global Xsignal, Ysignal
    global CHAsbxy, CHBsbxy, CHAOffset, CHBOffset, CHAIsbxy, CHBIsbxy, CHAIOffset, CHBIOffset
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate
    global SCstart, MathString
    global TRIGGERsample, TRACEsize, DX
    global TRIGGERlevel, TRIGGERentry, AutoLevel
    global InOffA, InGainA, InOffB, InGainB
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntryxy, CHAIPosEntryxy, CHAVPosEntryxy, CHBIPosEntryxy
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global HozPoss, HozPossentry

    # Set the TRACEsize variable
    if len(VBuffA) < 100:
        return
    TRACEsize = SHOWsamples               # Set the trace length
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
        CH1IpdvRange = float(eval(CHAIsbxy.get()))
    except:
        CHAIsbxy.delete(0,END)
        CHAIsbxy.insert(0, CH1IpdvRange)
    try:
        CH2IpdvRange = float(eval(CHBIsbxy.get()))
    except:
        CHBIsbxy.delete(0,END)
        CHBIsbxy.insert(0, CH2IpdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntryxy.get()))
    except:
        CHAVPosEntryxy.delete(0,END)
        CHAVPosEntryxy.insert(0, CHAOffset)
    try:
        CHAIOffset = float(eval(CHAIPosEntryxy.get()))
    except:
        CHAIPosEntryxy.delete(0,END)
        CHAIPosEntryxy.insert(0, CHAIOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntryxy.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    try:
        CHBIOffset = float(eval(CHBIPosEntryxy.get()))
    except:
        CHBIPosEntryxy.delete(0,END)
        CHBIPosEntryxy.insert(0, CHBIOffset)
    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    if CH1IpdvRange < 0.1:
        CH1IpdvRange = 0.1
    if CH2IpdvRange < 0.1:
        CH2IpdvRange = 0.1
    #
    Yconv1 = float(GRHXY/10.0) / CH1pdvRange    # Vertical Conversion factors from samples to screen points
    Yconv2 = float(GRHXY/10.0) / CH2pdvRange
    YIconv1 = float(GRHXY/10.0) / CH1IpdvRange
    YIconv2 = float(GRHXY/10.0) / CH2IpdvRange
    Xconv1 = float(GRWXY/10.0) / CH1pdvRange    # Horizontal Conversion factors from samples to screen points
    Xconv2 = float(GRWXY/10.0) / CH2pdvRange
    XIconv1 = float(GRWXY/10.0) / CH1IpdvRange
    XIconv2 = float(GRWXY/10.0) / CH2IpdvRange

    if MathYAxis == "V-A":
        YconvMxy = Yconv1
        CHMYOffset = CHAOffset
    elif MathYAxis == "V-B":
        YconvMxy = Yconv2
        CHMYOffset = CHBOffset
    elif MathYAxis == "I-A":
        YconvMxy = YIconv1
        CHMYOffset = CHAIOffset
    elif MathYAxis == "I-B":
        YconvMxy = YIconv2
        CHMYOffset = CHBIOffset
    else:
        YconvMxy = Yconv1
        CHMYOffset = CHAOffset
    if MathXAxis == "V-A":
        XconvMxy = Xconv1
        CHMXOffset = CHAOffset
    elif MathXAxis == "V-B":
        XconvMxy = Xconv2
        CHMXOffset = CHBOffset
    elif MathYAxis == "I-A":
        XconvMxy = XIconv1
        CHMXOffset = CHAIOffset
    elif MathXAxis == "I-B":
        XconvMxy = XIconv2
        CHMXOffset = CHBIOffset
    else:
        XconvMxy = Xconv1
        CHMXOffset = CHAOffset
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
            if ( MathTrace.get() == 2): # plot difference of CA-V and CB-V
                ylo = VBuffB[t] - CHBOffset
                ylo = int(c1 - Yconv2 * ylo)
                xlo = VBuffA[t] - VBuffB[t] - CHAOffset
                xlo = int(c2 + Xconv1 * xlo)
        elif (Xsignal.get() == 5 and Ysignal.get() == 4): # mode CBI/Math
            if ( MathTrace.get() == 2): # plot difference of CA-V and CB-V
                ylo = (IBuffB[t]) - CHBIOffset
                ylo = int(c1 - YIconv2 * ylo)
                xlo = VBuffA[t] - VBuffB[t] - CHAOffset
                xlo = int(c2 + Xconv1 * xlo)
        elif (Xsignal.get() == 5 and Ysignal.get() == 2): # mode CAI/Math
            if MathTrace.get() == 3: # plot difference of CB-V and CA-V
                ylo = (IBuffA[t]) - CHAIOffset
                ylo = int(c1 - YIconv1 * ylo)
                xlo = VBuffB[t] - VBuffA[t] - CHBOffset
                xlo = int(c2 + Xconv2 * xlo)
        elif (Xsignal.get() == 3 and Ysignal.get() == 5): # mode Math/CBV
            if MathTrace.get() == 2: # plot difference of CA-V and CB-V
                ylo = VBuffA[t] - VBuffB[t] - CHAOffset
                ylo = int(c1 - Yconv1 * ylo)
                xlo = VBuffB[t] - CHBOffset
                xlo = int(c2 + Xconv2 * xlo)
        elif (Xsignal.get() == 5 and Ysignal.get() == 1): # mode CAV/Math
            if MathTrace.get() == 3: # plot difference of CB-V and CA-V
                ylo = VBuffA[t] - CHAOffset
                ylo = int(c1 - Yconv1 * ylo)
                xlo = VBuffB[t] - VBuffA[t] - CHBOffset
                xlo = int(c2 + Xconv2 * xlo)
        elif (Xsignal.get() == 1 and Ysignal.get() == 5): # mode Math/CAV
            if MathTrace.get() == 3: # plot difference of CB-V and CA-V
                ylo = VBuffB[t] - VBuffA[t] - CHBOffset
                ylo = int(c1 - Yconv2 * ylo)
                xlo = VBuffA[t] - CHAOffset
                xlo = int(c2 + Xconv1 * xlo)
        elif (Xsignal.get() == 1 and Ysignal.get() == 2): # mode CAI/CAV
            ylo = (IBuffA[t]) - CHAIOffset
            xlo = VBuffA[t] - CHAOffset
            ylo = int(c1 - YIconv1 * ylo)
            xlo = int(c2 + Xconv1 * xlo)
        elif (Xsignal.get() == 3 and Ysignal.get() == 2): # mode CAI/CBV
            ylo = (IBuffA[t]) - CHAIOffset
            xlo = VBuffB[t] - CHBOffset
            ylo = int(c1 - YIconv1 * ylo)
            xlo = int(c2 + Xconv2 * xlo)
        elif (Xsignal.get() == 2 and Ysignal.get() == 1): # mode CAV/CAI
            ylo = VBuffA[t] - CHAOffset
            xlo = (IBuffA[t]) - CHAIOffset
            ylo = int(c1 - Yconv1 * ylo)
            xlo = int(c2 + XIconv1 * xlo)
        elif (Xsignal.get() == 2 and Ysignal.get() == 3): # mode CBV/CAI
            ylo = VBuffB[t] - CHBOffset
            xlo = (IBuffA[t]) - CHAIOffset
            ylo = int(c1 - Yconv2 * ylo)
            xlo = int(c2 + XIconv1 * xlo)
        elif (Xsignal.get() == 3 and Ysignal.get() == 4): # mode CBI/CBV
            ylo = (IBuffB[t]) - CHBIOffset
            xlo = VBuffB[t] - CHBOffset
            ylo = int(c1 - YIconv2 * ylo)
            xlo = int(c2 + Xconv2 * xlo)
        elif (Xsignal.get() == 4 and Ysignal.get() == 3): # mode CBV/CBI
            ylo = VBuffB[t] - CHBOffset
            xlo = (IBuffB[t]) - CHBIOffset
            ylo = int(c1 - Yconv2 * ylo)
            xlo = int(c2 + XIconv2 * xlo)
        elif (Xsignal.get() == 4 and Ysignal.get() == 2): # mode CAI/CBI
            ylo = (IBuffA[t]) - CHAIOffset
            xlo = (IBuffB[t]) - CHBIOffset
            ylo = int(c1 - YIconv1 * ylo)
            xlo = int(c2 + XIconv2 * xlo)
        elif (Xsignal.get() == 2 and Ysignal.get() == 4): # mode CBI/CAI
            ylo = (IBuffB[t]) - CHBIOffset
            xlo = (IBuffA[t]) - CHAIOffset
            ylo = int(c1 - YIconv2 * ylo)
            xlo = int(c2 + XIconv1 * xlo)
        elif (Xsignal.get() == 1 and Ysignal.get() == 4): # mode CBI/CAV
            ylo = (IBuffB[t]) - CHBIOffset
            xlo = VBuffA[t] - CHAOffset
            ylo = int(c1 - YIconv2 * ylo)
            xlo = int(c2 + Xconv1 * xlo)
        elif (Xsignal.get() == 5 and Ysignal.get() == 5): # mode MathYString/MathXString
            try:
                MathResult = eval(MathYString)
                MathResult = MathResult - CHMYOffset
                ylo = int(c1 - YconvMxy * MathResult)
            except:
                RUNstatus.set(0)
            try:
                MathResult = eval(MathXString)
                MathResult = MathResult - CHMXOffset
                xlo = int(c2 + XconvMxy * MathResult)
            except:
                RUNstatus.set(0)
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
    global T1Vline, T2Vline, T1Iline, T2Iline, TXYline # active trave lines
    global TMXline, TMYline
    global T1VRline, T2VRline, T1IRline, T2IRline # reference trace lines
    global Triggerline, Triggersymbol, Tmathline, TMRline, TXYRline
    global VBuffA, VBuffB, IBuffA, IBuffB
    global VBuffMA, VBuffMB, VBuffMC, VBuffMD, MuxScreenStatus
    global TMAVline, TMBVline, TMCVline, TMDVline, TMCRline, TMBRline
    global VmemoryA, VmemoryB, VmemoryA, ImemoryB
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global GRW          # Screenwidth
    global GRH          # Screenheight
    global MouseX, MouseY, MouseWidget, MouseCAV, MouseCAI, MouseCBV, MouseCBI
    global MouseMuxA, MouseMuxB, MouseMuxC, MouseMuxD
    global Ymin, Ymax
    global ShowXCur, ShowYCur, TCursor, VCursor
    global SHOWsamples  # Number of samples in data record
    global ShowC1_V, ShowC1_I, ShowC2_V, ShowC2_I, ShowRXY, Show_MathX, Show_MathY
    global ShowRA_V, ShowRA_I, ShowRB_V, ShowRB_I, ShowMath
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MathUnits, MathXUnits, MathYUnits
    global Xsignal, Ysignal, MathTrace, MathAxis, MathXAxis, MathYAxis
    global RUNstatus, SingleShot    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global CHAsb        # spinbox Index for channel 1 V
    global CHBsb        # spinbox Index for channel 2 V
    global CHAOffset    # Offset value for channel 1 V
    global CHBOffset    # Offset value for channel 2 V
    global CHAIsb       # spinbox Index for channel 1 I
    global CHBIsb       # spinbox Index for channel 2 I
    global CHAIOffset   # Offset value for channel 1 I
    global CHBIOffset   # Offset value for channel 2 I     
    global TMpdiv       # Array with time / div values in ms
    global TMsb         # Time per div spin box variable
    global TIMEdiv      # current spin box value
    global SAMPLErate, contloop, discontloop
    global TRIGGERsample, TRIGGERlevel, HoldOff, HoldOffentry, TgInput
    global COLORgrid, COLORzeroline, COLORtext, COLORtrigger, COLORtrace7, COLORtraceR7 # The colors
    global COLORtrace1, COLORtrace2, COLORtrace3, COLORtrace4, COLORtrace5, COLORtrace6
    global COLORtraceR1, COLORtraceR2, COLORtraceR3, COLORtraceR4, COLORtraceR5, COLORtraceR6
    global CANVASwidth, CANVASheight
    global TRACErefresh, TRACEmode, TRACEwidth, GridWidth
    global ScreenTrefresh, SmoothCurves, Is_Triggered
    global DCV1, DCV2, MinV1, MaxV1, MinV2, MaxV2, CHAHW, CHALW, CHADCy, CHAperiod, CHAfreq
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2, CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
        # Analog Mux channel measurement variables
    global DCVMuxA, MinVMuxA, MaxVMuxA, MidVMuxA, PPVMuxA, SVMuxA
    global DCVMuxB, MinVMuxB, MaxVMuxB, MidVMuxB, PPVMuxB, SVMuxB
    global DCVMuxC, MinVMuxC, MaxVMuxC, MidVMuxC, PPVMuxC, SVMuxC
    global DCVMuxD, MinVMuxD, MaxVMuxD, MidVMuxD, PPVMuxD, SVMuxD
    global SV1, SI1, SV2, SI2, CHABphase, SVA_B
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCI1, MeasMinI1, MeasMaxI1, MeasMidI1, MeasPPI1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasDCI2, MeasMinI2, MeasMaxI2, MeasMidI2, MeasPPI2
    global MeasRMSV1, MeasRMSI1, MeasRMSV2, MeasRMSI2, MeasPhase, MeasRMSVA_B
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global AWGAShape, AWGBShape, MeasDiffAB, MeasDiffBA 
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHAVPosEntry, CHBIPosEntry
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
    global DacScreenStatus, DigScreenStatus
    global D0, D1, D2, D3, D4, D5, D6, D7
    global DevID, devx, MarkerNum, MarkerScale
    global HozPoss, HozPossentry
    global VABase, VATop, VBBase, VBTop, UserALabel, UserAString, UserBLabel, UserBString
    global MeasTopV1, MeasBaseV1, MeasTopV2, MeasBaseV2, MeasUserA, MeasUserB
    global CHBADelayR1, CHBADelayR2, CHBADelayF, MeasDelay
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
    # get time scale
    try:
        TIMEdiv = eval(TMsb.get())
    except:
        TIMEdiv = 0.5
        TMsb.delete(0,"end")
        TMsb.insert(0,TIMEdiv)
    if TIMEdiv < 0.0002:
        TIMEdiv = 0.1
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
        CH1IpdvRange = float(eval(CHAIsb.get()))
    except:
        CHAIsb.delete(0,END)
        CHAIsb.insert(0, CH1IpdvRange)
    try:
        CH2IpdvRange = float(eval(CHBIsb.get()))
    except:
        CHBIsb.delete(0,END)
        CHBIsb.insert(0, CH2IpdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntry.get()))
    except:
        CHAVPosEntry.delete(0,END)
        CHAVPosEntry.insert(0, CHAOffset)
    try:
        CHAIOffset = float(eval(CHAIPosEntry.get()))
    except:
        CHAIPosEntry.delete(0,END)
        CHAIPosEntry.insert(0, CHAIOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntry.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    try:
        CHBIOffset = float(eval(CHBIPosEntry.get()))
    except:
        CHBIPosEntry.delete(0,END)
        CHBIPosEntry.insert(0, CHBIOffset)
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
    if CH1IpdvRange < 0.1:
        CH1IpdvRange = 0.1
    if CH2IpdvRange < 0.1:
        CH2IpdvRange = 0.1
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
        MathFlag1 = (MathAxis == "V-A" and MathTrace.get() == 12) or (MathXAxis == "V-A" and Show_MathX.get() == 1) or (MathYAxis == "V-A" and Show_MathY.get() == 1)
        MathFlag2 = (MathAxis == "V-B" and MathTrace.get() == 12) or (MathXAxis == "V-B" and Show_MathX.get() == 1) or (MathYAxis == "V-B" and Show_MathY.get() == 1)
        MathFlag3 = (MathAxis == "I-A" and MathTrace.get() == 12) or (MathXAxis == "I-A" and Show_MathX.get() == 1) or (MathYAxis == "I-A" and Show_MathY.get() == 1)
        MathFlag4 = (MathAxis == "I-B" and MathTrace.get() == 12) or (MathXAxis == "I-B" and Show_MathX.get() == 1) or (MathYAxis == "I-B" and Show_MathY.get() == 1)
        # vertical scale text labels
        if (ShowC1_V.get() == 1 or MathTrace.get() == 1 or MathTrace.get() == 2 or MathFlag1):
            ca.create_text(x1-2, 12, text="CA-V", fill=COLORtrace1, anchor="e", font=("arial", 7 ))
        if (ShowC1_I.get() == 1 or MathTrace.get() == 4 or MathTrace.get() == 6 or MathTrace.get() == 8 or MathFlag3):
            ca.create_text(x2+2, 12, text="CA-I", fill=COLORtrace3, anchor="w", font=("arial", 7 ))
        if (ShowC2_V.get() == 1 or MathTrace.get() == 3 or MathTrace.get() == 10 or MathFlag2):
            ca.create_text(x1-26, 12, text="CB-V", fill=COLORtrace2, anchor="e", font=("arial", 7 ))
        if (ShowC2_I.get() == 1 or MathTrace.get() == 5 or MathTrace.get() == 7 or MathTrace.get() == 9 or MathTrace.get() == 11 or MathFlag4):
            ca.create_text(x2+28, 12, text="CB-I", fill=COLORtrace4, anchor="w", font=("arial", 7 ))
        #
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

            if (ShowC1_V.get() == 1 or MathTrace.get() == 1 or MathTrace.get() == 2 or MathFlag1):
                Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                # Vaxis_label = ' {0:.2f} '.format(Vaxis_value)
                Vaxis_label = str(Vaxis_value)
                ca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
                
            if (ShowC1_I.get() == 1 or MathTrace.get() == 4 or MathTrace.get() == 6 or MathTrace.get() == 8 or MathFlag3):
                Iaxis_value = 1.0 * (((5-i) * CH1IpdvRange ) + CHAIOffset)
                Iaxis_label = str(Iaxis_value)
                ca.create_text(x2+2, y, text=Iaxis_label, fill=COLORtrace3, anchor="w", font=("arial", 8 ))
                
            if (ShowC2_V.get() == 1 or MathTrace.get() == 3 or MathTrace.get() == 10 or MathFlag2):
                Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                Vaxis_label = str(Vaxis_value)
                ca.create_text(x1-26, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", 8 ))
                
            if (ShowC2_I.get() == 1 or MathTrace.get() == 5 or MathTrace.get() == 7 or MathTrace.get() == 9 or MathTrace.get() == 11 or MathFlag4):
                Iaxis_value = 1.0 * (((5-i) * CH2IpdvRange ) + CHBIOffset)
                Iaxis_label = str(Iaxis_value)
                ca.create_text(x2+28, y, text=Iaxis_label, fill=COLORtrace4, anchor="w", font=("arial", 8 ))
            if MuxScreenStatus.get() == 1:
                if Show_CBA.get() == 1: 
                    Vaxis_value = (((5-i) * CHMApdvRange ) + CHBAOffset)
                    Vaxis_label = str(Vaxis_value)
                    ca.create_text(x1-26, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", 8 ))
                if Show_CBB.get() == 1: 
                    Iaxis_value = 1.0 * (((5-i) * CHMBpdvRange ) + CHBBOffset)
                    Iaxis_label = str(Iaxis_value)
                    ca.create_text(x2+2, y, text=Iaxis_label, fill=COLORtrace6, anchor="w", font=("arial", 8 ))
                if Show_CBC.get() == 1:
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
                    axis_value = ((i * vx)+ vt) / 1000.0
                    axis_label = str(int(axis_value)) + " S"
                if vx < 1000 and vx >= 1:
                    axis_value = (i * vx) + vt
                    axis_label = str(int(axis_value)) + " mS"
                if vx < 1:
                    axis_value = ((i * vx) + vt) * 1000.0
                    axis_label = str(int(axis_value)) + " uS"
                ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
            else:
                ca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                if vx >= 1000:
                    axis_value = ((i * vx)+ vt) / 1000.0
                    axis_label = str(int(axis_value)) + " S"
                if vx < 1000 and vx >= 1:
                    axis_value = (i * vx) + vt
                    axis_label = str(int(axis_value)) + " mS"
                if vx < 1:
                    axis_value = ((i * vx) + vt) * 1000.0
                    axis_label = str(int(axis_value)) + " uS"
                ca.create_text(x, y2+3, text=axis_label, fill=COLORgrid, anchor="n", font=("arial", 8 ))
                        
            i = i + 1
    # Write the trigger line if available
    if len(Triggerline) > 2:                    # Avoid writing lines with 1 coordinate
        ca.create_polygon(Triggerline, outline=COLORtrigger, fill=COLORtrigger, width=1)
        ca.create_line(Triggersymbol, fill=COLORtrigger, width=GridWidth.get())
        if TgInput.get() == 1:
            TgLabel = "CA-V"
        if TgInput.get() == 2:
            TgLabel = "CA-I"
        if TgInput.get() == 3:
            TgLabel = "CB-V"
        if TgInput.get() == 4:
            TgLabel = "CB-I"
        if Is_Triggered == 1:
            TgLabel = TgLabel + " Triggered"
        else:
            TgLabel = TgLabel + " Not Triggered"
        x = X0L + (GRW/2) + 12
        ca.create_text(x, Ymin-8, text=TgLabel, fill=COLORtrigger, anchor="w", font=("arial", 8 ))
    # Draw T - V Cursor lines if required
    if MarkerScale.get() == 0:
        Yconv1 = float(GRH/10.0) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORmarker = COLORtrace1
        Units = " V"
    if MarkerScale.get() == 1:
        MouseY = MouseCAV
        Yconv1 = float(GRH/10.0) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORmarker = COLORtrace1
        Units = " V"
    if MarkerScale.get() == 2:
        MouseY = MouseCBV
        Yconv1 = float(GRH/10.0) / CH2pdvRange
        Yoffset1 = CHBOffset
        COLORmarker = COLORtrace2
        Units = " V"
    if MarkerScale.get() == 3:
        MouseY = MouseCAI
        Yconv1 = float(GRH/10.0) / CH1IpdvRange
        Yoffset1 = CHAIOffset
        COLORmarker = COLORtrace3
        Units = " mA"
    if MarkerScale.get() == 4:
        MouseY = MouseCBI
        Yconv1 = float(GRH/10.0) / CH2IpdvRange
        Yoffset1 = CHBIOffset
        COLORmarker = COLORtrace4
        Units = " mA"
    # Aanalog Mux settings
    if MarkerScale.get() == 5:
        MouseY = MouseMuxA
        Yconv1 = float(GRH/10.0) / CHMApdvRange
        Yoffset1 = CHBAOffset
        COLORmarker = COLORtrace2
        Units = " V"
    if MarkerScale.get() == 6:
        MouseY = MouseMuxB
        Yconv1 = float(GRH/10.0) / CHMBpdvRange
        Yoffset1 = CHBBOffset
        COLORmarker = COLORtrace6
        Units = " V"
    if MarkerScale.get() == 7:
        MouseY = MouseMuxC
        Yconv1 = float(GRH/10.0) / CHMCpdvRange
        Yoffset1 = CHBCOffset
        COLORmarker = COLORtrace7
        Units = " V"
    if MarkerScale.get() == 8:
        MouseY = MouseMuxD
        Yconv1 = float(GRH/10.0) / CHMDpdvRange
        Yoffset1 = CHBDOffset
        COLORmarker = COLORtrace4
        Units = " V"
#
    if ShowTCur.get() > 0:
        Dline = [TCursor, Y0T, TCursor, Y0T+GRH]
        ca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
        DISsamples = (10.0 * TIMEdiv) # grid width in time 
        Tstep = DISsamples / GRW # time in mS per pixel
        Tpoint = ((TCursor-X0L) * Tstep) + vt
        if TIMEdiv < 0.1:
            TString = ' {0:.3f} '.format(Tpoint)
        else:
            TString = ' {0:.2f} '.format(Tpoint)
        V_label = TString + " mS"
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
            if TIMEdiv < 0.1:
                TString = ' {0:.3f} '.format(Tpoint)
            else:
                TString = ' {0:.2f} '.format(Tpoint)
            V_label = TString + " mS"
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
    if len(T1Iline) > 4: # Avoid writing lines with 1 coordinate
        ca.create_line(T1Iline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())   # Write the current trace 1
    if len(T2Vline) > 4: # Write the trace 2 if active
        ca.create_line(T2Vline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(T2Iline) > 4:
        ca.create_line(T2Iline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(Tmathline) > 4 and MathTrace.get() > 0: # Write Math tace if active
        ca.create_line(Tmathline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TMXline) > 4 : # Write X Math tace if active
        ca.create_line(TMXline, fill=COLORtrace6, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
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
        if ShowRB_I.get() == 1 and len(TMCRline) > 4:
            ca.create_line(TMCRline, fill=COLORtraceR7, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRA_V.get() == 1 and len(T1VRline) > 4:
        ca.create_line(T1VRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRA_I.get() == 1 and len(T1IRline) > 4:
        ca.create_line(T1IRline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRB_V.get() == 1 and len(T2VRline) > 4:
        ca.create_line(T2VRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowRB_I.get() == 1 and len(T2IRline) > 4:
        ca.create_line(T2IRline, fill=COLORtraceR4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMath.get() == 1 and len(TMRline) > 4:
        ca.create_line(TMRline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())

    # General information on top of the grid
    # Sweep information
    if contloop == 1:
        sttxt = "Running Continuous"
    else:
        sttxt = "Running Discontinuous"
    if TRACEmodeTime.get() == 1:
        sttxt = sttxt + " Averaging"
    if SingleShot.get() == 1:
        sttxt = "Single Shot"
    if (RUNstatus.get() == 0) or (RUNstatus.get() == 3):
        sttxt = "Stopped"
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
    txt = "Device ID " + DevID[17:31] + " Sample rate: " + str(SAMPLErate) + " " + sttxt
    x = X0L+2
    y = 12
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    # digital I/O indicators
    x2 = X0L + GRW
    BoxColor = "#808080"   # gray
    if DacScreenStatus.get() == 0 and (DigScreenStatus.get() == 1 or MuxScreenStatus.get() == 1):
        if D0.get() == 0 and D4.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-12, 6, x2, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-12, 6, x2, 18, fill="yellow")
        if D1.get() == 0 and D5.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-26, 6, x2-14, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-26, 6, x2-14, 18, fill="yellow")
        if D2.get() == 0 and D6.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-40, 6, x2-28, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-40, 6, x2-28, 18, fill="yellow")
        if D3.get() == 0 and D7.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
                BoxColor = "#ff0000"   # 100% red
            ca.create_rectangle(x2-54, 6, x2-42, 18, fill=BoxColor)
        else:
            ca.create_rectangle(x2-54, 6, x2-42, 18, fill="yellow")
        ca.create_text(x2-56, 12, text="Digital Inputs", anchor=E, fill=COLORtext)
    # Time sweep information and view at information
    vx = TIMEdiv
    if vx >= 1000:
        txt = str(int(vx/1000.0)) + " S/div"
    if vx < 1000 and vx >= 1:
        txt = str(int(vx)) + " mS/div"
    if vx < 1:
        txt = str(int(vx * 1000.0)) + " uS/div"

    txt = txt + "  "
    #
    txt = txt + "View at "
    if abs(vt) >= 1000:
        txt = txt + str(vt / 1000.0) + " S "
    if abs(vt) < 1000 and abs(vt) >= 1:
        txt = txt + str(vt) + " mS "
    if abs(vt) < 1:
        txt = txt + str(vt * 1000.0) + " uS "
    # print period and frequency of displayed channels
    if ShowC1_V.get() == 1 or ShowC2_V.get() == 1:
        FindRisingEdge()
        if ShowC1_V.get() == 1:
            if MeasAHW.get() == 1:
                txt = txt + " CA Hi Width = "
                V1String = ' {0:.2f} '.format(CHAHW)
                txt = txt + str(V1String) + " mS "
            if MeasALW.get() == 1:
                txt = txt + " CA Lo Width = "
                V1String = ' {0:.2f} '.format(CHALW)
                txt = txt + str(V1String) + " mS "
            if MeasADCy.get() == 1:
                txt = txt + " CA DutyCycle = "
                V1String = ' {0:.1f} '.format(CHADCy)
                txt = txt + str(V1String) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " CA Period = "
                V1String = ' {0:.2f} '.format(CHAperiod)
                txt = txt + str(V1String) + " mS "
            if MeasAFREQ.get() == 1:
                txt = txt + " CA Freq = "
                V1String = ' {0:.1f} '.format(CHAfreq)
                txt = txt + str(V1String) + " Hz "
        if ShowC2_V.get() == 1:
            if MeasBHW.get() == 1:
                txt = txt + " CB Hi Width = "
                V1String = ' {0:.2f} '.format(CHBHW)
                txt = txt + str(V1String) + " mS "
            if MeasBLW.get() == 1:
                txt = txt + " CB Lo Width = "
                V1String = ' {0:.2f} '.format(CHBLW)
                txt = txt + str(V1String) + " mS "
            if MeasBDCy.get() == 1:
                txt = txt + " CB DutyCycle = "
                V1String = ' {0:.1f} '.format(CHBDCy)
                txt = txt + str(V1String) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " CB Period = "
                V1String = ' {0:.2f} '.format(CHBperiod)
                txt = txt + str(V1String) + " mS "
            if MeasBFREQ.get() == 1:
                txt = txt + " CB Freq = "
                V1String = ' {0:.1f} '.format(CHBfreq)
                txt = txt + str(V1String) + " Hz "
        if MeasPhase.get() == 1:
            txt = txt + " CA-B Phase = "
            V1String = ' {0:.1f} '.format(CHABphase)
            txt = txt + str(V1String) + " deg "
        if MeasDelay.get() == 1:
            txt = txt + " CB-A Delay = "
            V1String = ' {0:.2f} '.format(CHBADelayR1)
            txt = txt + str(V1String) + " mS "    
         
    x = X0L
    y = Y0T+GRH+20
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    if MeasTopV1.get() == 1 or MeasBaseV1.get() == 1 or MeasTopV2.get() == 1 or MeasBaseV2.get() == 1:
        MakeHistogram()
    txt = " "
    if ShowC1_V.get() == 1:
    # Channel A information
        txt = "CHA: "
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
            MidV1 = (MaxV1+MinV1)/2.0
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
            txt = txt +  " A-B RMS = " + V1String
        if MeasDiffAB.get() == 1:
            V1String = ' {0:.4f} '.format(DCV1-DCV2)
            txt = txt +  " CA-CB = " + V1String
        if MeasUserA.get() == 1:
            try:
                TempValue = eval(UserAString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserALabel + " = " + V1String
    if (ShowC1_I.get() == 1 and ShowC1_V.get() == 0):
        txt = "CHA: "
        txt = txt + str(CH1IpdvRange) + " mA/div"
    elif (ShowC1_I.get() == 1 and ShowC1_V.get() == 1):
        txt = txt + "CHA: "
        txt = txt + str(CH1IpdvRange) + " mA/div"
    if ShowC1_I.get() == 1:
        if MeasDCI1.get() == 1:
            V1String = ' {0:.2f} '.format(DCI1)
            txt = txt + " AvgI = " + V1String
            if AWGAShape.get() == 0: # if this is a DC measurement calc resistance
                try:
                    Resvalue = (DCV1/DCI1)*1000
                    R1String = ' {0:.1f} '.format(Resvalue)
                    txt = txt + " Res = " + R1String
                except:
                    txt = txt + " Res = OverRange" 
        if MeasMaxI1.get() == 1:
            V1String = ' {0:.2f} '.format(MaxI1)
            txt = txt +  " MaxI = " + V1String
        if MeasMinI1.get() == 1:
            V1String = ' {0:.2f} '.format(MinI1)
            txt = txt +  " MinI = " + V1String
        if MeasMidI1.get() == 1:
            MidI1 = (MaxI1+MinI1)/2.0
            V1String = ' {0:.2f} '.format(MidI1)
            txt = txt +  " MidV = " + V1String
        if MeasPPI1.get() == 1:
            PPI1 = MaxI1-MinI1
            V1String = ' {0:.2f} '.format(PPI1)
            txt = txt +  " P-PI = " + V1String
        if MeasRMSI1.get() == 1:
            V1String = ' {0:.4f} '.format(SI1)
            txt = txt +  " RMS = " + V1String
        
    x = X0L
    y = Y0T+GRH+32
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    txt= " "
    # Channel B information
    if MuxScreenStatus.get() == 1:
        txt = "CHB-Mux: "
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String
    if ShowC2_V.get() == 1:
        txt = "CHB: "
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
            MidV2 = (MaxV2+MinV2)/2.0
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
            txt = txt +  " CB-CA = " + V1String
        if MeasUserB.get() == 1:
            try:
                TempValue = eval(UserBString)
                V1String = ' {0:.4f} '.format(TempValue)
            except:
                V1String = "####"
            txt = txt +  UserBLabel + " = " + V1String
    if (ShowC2_I.get() == 1 and ShowC2_V.get() == 0):
        txt = "CHB: "
        txt = txt + str(CH2IpdvRange) + " mA/div"
    elif (ShowC2_I.get() == 1 and ShowC2_V.get() == 1):
        txt = txt + "CHB: "
        txt = txt + str(CH2IpdvRange) + " mA/div"
    if ShowC2_I.get() == 1:
        if MeasDCI2.get() == 1:
            V1String = ' {0:.2f} '.format(DCI2)
            txt = txt + " AvgI = " + V1String
            if AWGBShape.get() == 0: # if this is a DC measurement calc resistance
                try:
                    Resvalue = (DCV2/DCI2)*1000
                    R1String = ' {0:.1f} '.format(Resvalue)
                    txt = txt + " Res = " + R1String
                except:
                    txt = txt + " Res = OverRange" 
        if MeasMaxI2.get() == 1:
            V1String = ' {0:.2f} '.format(MaxI2)
            txt = txt +  " MaxI = " + V1String
        if MeasMinI2.get() == 1:
            V1String = ' {0:.2f} '.format(MinI2)
            txt = txt +  " MinI = " + V1String
        if MeasMidI2.get() == 1:
            MidI2 = (MaxI2+MinI2)/2.0
            V1String = ' {0:.2f} '.format(MidI2)
            txt = txt +  " MidV = " + V1String
        if MeasPPI2.get() == 1:
            PPI2 = MaxI2-MinI2
            V1String = ' {0:.2f} '.format(PPI2)
            txt = txt +  " P-PI = " + V1String
        if MeasRMSI2.get() == 1:
            V1String = ' {0:.4f} '.format(SI2)
            txt = txt +  " RMS = " + V1String
            
    x = X0L
    y = Y0T+GRH+44
    ca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
#
def MakeXYScreen():
    global TXYline # active trave lines
    global Tmathline, TMRline, TXYRline
    global X0LXY         # Left top X value
    global Y0TXY          # Left top Y value
    global GRWXY          # Screenwidth
    global GRHXY          # Screenheight
    global Ymin, Ymax, XYca, MouseX, MouseY, MouseWidget
    global ShowXCur, ShowYCur, XCursor, YCursor
    global SHOWsamples  # Number of samples in data record
    global ShowRXY, ShowMath, MathUnits, MathXUnits, MathYUnits
    global Xsignal, Ysignal, MathXAxis, MathYAxis
    global RUNstatus, SingleShot    # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
    global CHAsbxy        # spinbox Index for channel 1 V
    global CHBsbxy        # spinbox Index for channel 2 V
    global CHAOffset    # Offset value for channel 1 V
    global CHBOffset    # Offset value for channel 2 V
    global CHAIsbxy       # spinbox Index for channel 1 I
    global CHBIsbxy       # spinbox Index for channel 2 I
    global CHAIOffset   # Offset value for channel 1 I
    global CHBIOffset   # Offset value for channel 2 I     
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
    global DCI1, DCI2, MinI1, MaxI1, MinI2, MaxI2, CHBHW, CHBLW, CHBDCy, CHBperiod, CHBfreq
    global SV1, SI1, SV2, SI2, CHABphase
    global MeasDCV1, MeasMinV1, MeasMaxV1, MeasMidV1, MeasPPV1
    global MeasDCI1, MeasMinI1, MeasMaxI1, MeasMidI1, MeasPPI1
    global MeasDCV2, MeasMinV2, MeasMaxV2, MeasMidV2, MeasPPV2
    global MeasDCI2, MeasMinI2, MeasMaxI2, MeasMidI2, MeasPPI2
    global MeasRMSV1, MeasRMSI1, MeasRMSV2, MeasRMSI2, MeasPhase
    global MeasAHW, MeasALW, MeasADCy, MeasAPER, MeasAFREQ
    global MeasBHW, MeasBLW, MeasBDCy, MeasBPER, MeasBFREQ
    global AWGAShape, AWGBShape
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAVPosEntry, CHAIPosEntry, CHAVPosEntry, CHBIPosEntry
    global CH1pdvRange, CHAOffset, CH2pdvRange, CHBOffset
    global DacScreenStatus, DigScreenStatus
    global D0, D1, D2, D3, D4, D5, D6, D7
    global DevID, devx, MarkerNum, MarkerScale
    global HozPoss, HozPossentry
    global HistAsPercent, VBuffA, VBuffB, HBuffA, HBuffB
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
        CH1IpdvRange = float(eval(CHAIsbxy.get()))
    except:
        CHAIsbxy.delete(0,END)
        CHAIsbxy.insert(0, CH1IpdvRange)
    try:
        CH2IpdvRange = float(eval(CHBIsbxy.get()))
    except:
        CHBIsbxy.delete(0,END)
        CHBIsbxy.insert(0, CH2IpdvRange)
    # get the vertical offsets
    try:
        CHAOffset = float(eval(CHAVPosEntryxy.get()))
    except:
        CHAVPosEntryxy.delete(0,END)
        CHAVPosEntryxy.insert(0, CHAOffset)
    try:
        CHAIOffset = float(eval(CHAIPosEntryxy.get()))
    except:
        CHAIPosEntryxy.delete(0,END)
        CHAIPosEntryxy.insert(0, CHAIOffset)
    try:
        CHBOffset = float(eval(CHBVPosEntryxy.get()))
    except:
        CHBVPosEntry.delete(0,END)
        CHBVPosEntry.insert(0, CHBOffset)
    try:
        CHBIOffset = float(eval(CHBIPosEntryxy.get()))
    except:
        CHBIPosEntryxy.delete(0,END)
        CHBIPosEntryxy.insert(0, CHBIOffset)
    # prevent divide by zero error
    if CH1pdvRange < 0.001:
        CH1pdvRange = 0.001
    if CH2pdvRange < 0.001:
        CH2pdvRange = 0.001
    if CH1IpdvRange < 0.05:
        CH1IpdvRange = 0.05
    if CH2IpdvRange < 0.05:
        CH2IpdvRange = 0.05
    # If drawing histograms adjust offset based on range such that bottom grid is zero
    if  Xsignal.get() == 6:
        CHAIOffset = 5 * CH1IpdvRange
    if  Xsignal.get() == 7:
        CHBIOffset = 5 * CH2IpdvRange
    if ScreenXYrefresh.get() == 0:
        # Delete all items on the screen
        de = XYca.find_enclosed( -1000, -1000, CANVASwidthXY+1000, CANVASheightXY+1000)
        MarkerNum = 0
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
                    while (l < 5):
                        Dline = [x1+k*mg_siz+l*mg_inc,y-5,x1+k*mg_siz+l*mg_inc,y+5]
                        XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
            else:
                XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            if Ysignal.get() == 2 or Xsignal.get() == 6:
                Iaxis_value = 1.0 * (((5-i) * CH1IpdvRange ) + CHAIOffset)
                Iaxis_label = str(Iaxis_value)
                XYca.create_text(x1-3, y, text=Iaxis_label, fill=COLORtrace3, anchor="e", font=("arial", 8 ))
            elif Ysignal.get() == 4 or Xsignal.get() == 7:
                Iaxis_value = 1.0 * (((5-i) * CH2IpdvRange ) + CHBIOffset)
                Iaxis_label = str(Iaxis_value)
                XYca.create_text(x1-3, y, text=Iaxis_label, fill=COLORtrace4, anchor="e", font=("arial", 8 ))
            elif Ysignal.get() == 1:
                Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                Vaxis_label = str(Vaxis_value)
                XYca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
            elif Ysignal.get() == 3:
                Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                Vaxis_label = str(Vaxis_value)
                XYca.create_text(x1-3, y, text=Vaxis_label, fill=COLORtrace2, anchor="e", font=("arial", 8 ))
            elif Ysignal.get() == 5:
                TempCOLOR = COLORtrace5
                if MathTrace.get() == 2:
                    Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                elif MathTrace.get() == 3:
                    Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                else:
                    if MathYAxis == "V-A":
                        Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                        TempCOLOR = COLORtrace1
                    elif MathYAxis == "V-B":
                        Vaxis_value = (((5-i) * CH2pdvRange ) + CHBOffset)
                        TempCOLOR = COLORtrace2
                    elif MathYAxis == "I-A":
                        Vaxis_value = 1.0 * (((5-i) * CH1IpdvRange ) + CHAIOffset)
                        TempCOLOR = COLORtrace3
                    elif MathYAxis == "I-B":
                        Vaxis_value = 1.0 * (((5-i) * CH2IpdvRange ) + CHBIOffset)
                        TempCOLOR = COLORtrace4
                    else:
                        Vaxis_value = (((5-i) * CH1pdvRange ) + CHAOffset)
                Vaxis_label = str(Vaxis_value)
                XYca.create_text(x1-3, y, text=Vaxis_label, fill=TempCOLOR, anchor="e", font=("arial", 8 ))
            i = i + 1
        # Draw vertical grid lines
        i = 0
        y1 = Y0TXY
        y2 = Y0TXY + GRHXY
        mg_siz = GRHXY/10.0
        mg_inc = mg_siz/5.0
        # 
        while (i < 11):
            x = X0LXY + i * GRWXY/10.0
            Dline = [x,y1,x,y2]
            if (i == 5):
                XYca.create_line(Dline, fill=COLORzeroline, width=GridWidth.get())   # Blue vertical line at center of grid
                k = 0
                while (k < 10):
                    l = 1
                    while (l < 5):
                        Dline = [x-5,y1+k*mg_siz+l*mg_inc,x+5,y1+k*mg_siz+l*mg_inc]
                        XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                        l = l + 1
                    k = k + 1
                if Xsignal.get() == 1 or Xsignal.get() == 6: # 
                    Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 3 or Xsignal.get() == 7:
                    Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 2:
                    Iaxis_value = 1.0 * (((i-5) * CH1IpdvRange ) + CHAIOffset)
                    Iaxis_label = str(Iaxis_value)
                    XYca.create_text(x, y2+3, text=Iaxis_label, fill=COLORtrace3, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 4:
                    Iaxis_value = 1.0 * (((i-5) * CH2IpdvRange ) + CHBIOffset)
                    Iaxis_label = str(Iaxis_value)
                    XYca.create_text(x, y2+3, text=Iaxis_label, fill=COLORtrace4, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 5:
                    TempCOLOR = COLORtrace5
                    if MathTrace.get() == 2:
                        Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    elif MathTrace.get() == 3:
                        Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    else:
                        if MathXAxis == "V-A":
                            Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                            TempCOLOR = COLORtrace1
                        elif MathXAxis == "V-B":
                            Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                            TempCOLOR = COLORtrace2
                        elif MathXAxis == "I-A":
                            Vaxis_value = 1.0 * (((i-5) * CH1IpdvRange ) + CHAIOffset)
                            TempCOLOR = COLORtrace3
                        elif MathXAxis == "I-B":
                            Vaxis_value = 1.0 * (((i-5) * CH2IpdvRange ) + CHBIOffset)
                            TempCOLOR = COLORtrace4
                        else:
                            Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                            TempCOLOR = COLORtrace5
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=TempCOLOR, anchor="n", font=("arial", 8 ))
            else:
                XYca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                if Xsignal.get() == 1 or Xsignal.get() == 6:
                    Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace1, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 3 or Xsignal.get() == 7:
                    Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=COLORtrace2, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 2:
                    Iaxis_value = 1.0 * (((i-5) * CH1IpdvRange ) + CHAIOffset)
                    Iaxis_label = str(Iaxis_value)
                    XYca.create_text(x, y2+3, text=Iaxis_label, fill=COLORtrace3, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 4:
                    Iaxis_value = 1.0 * (((i-5) * CH2IpdvRange ) + CHBIOffset)
                    Iaxis_label = str(Iaxis_value)
                    XYca.create_text(x, y2+3, text=Iaxis_label, fill=COLORtrace4, anchor="n", font=("arial", 8 ))
                elif Xsignal.get() == 5:
                    TempCOLOR = COLORtrace5
                    if MathTrace.get() == 2:
                        Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    elif MathTrace.get() == 3:
                        Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                    else:
                        if MathXAxis == "V-A":
                            Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                            TempCOLOR = COLORtrace1
                        elif MathXAxis == "V-B":
                            Vaxis_value = (((i-5) * CH2pdvRange ) + CHBOffset)
                            TempCOLOR = COLORtrace2
                        elif MathXAxis == "I-A":
                            Vaxis_value = 1.0 * (((i-5) * CH1IpdvRange ) + CHAIOffset)
                            TempCOLOR = COLORtrace3
                        elif MathXAxis == "I-B":
                            Vaxis_value = 1.0 * (((i-5) * CH2IpdvRange ) + CHBIOffset)
                            TempCOLOR = COLORtrace4
                        else:
                            Vaxis_value = (((i-5) * CH1pdvRange ) + CHAOffset)
                    Vaxis_label = str(Vaxis_value)
                    XYca.create_text(x, y2+3, text=Vaxis_label, fill=TempCOLOR, anchor="n", font=("arial", 8 ))
            i = i + 1
# Draw traces
    if len(TXYline) > 4:                    # Avoid writing lines with 1 coordinate
        if  Xsignal.get() == 1:
            XYca.create_line(TXYline, fill=COLORtrace1, width=TRACEwidth.get())
        elif  Xsignal.get() == 2:
            XYca.create_line(TXYline, fill=COLORtrace3, width=TRACEwidth.get())
        elif  Xsignal.get() == 3:
            XYca.create_line(TXYline, fill=COLORtrace2, width=TRACEwidth.get())
        elif  Xsignal.get() == 4:
            XYca.create_line(TXYline, fill=COLORtrace4, width=TRACEwidth.get())
        elif  Xsignal.get() == 5 or Ysignal.get() == 5:
            XYca.create_line(TXYline, fill=COLORtrace5, width=TRACEwidth.get())
    if len(TXYRline) > 4 and ShowRXY.get() == 1:
        XYca.create_line(TXYRline, fill=COLORtraceR1, width=TRACEwidth.get())
# Draw Histogram Traces
    if  Xsignal.get() == 6:
        MakeHistogram()
        b = 0
        Yconv1 = float(GRHXY/10.0) / CH1IpdvRange
        Xconv1 = float(GRWXY/10.0) / CH1pdvRange
        y1 = Y0TXY + GRHXY
        # print Yconv1, y1
        c2 = GRWXY / 2.0 + X0LXY   # Hor correction factor
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
        Yconv1 = float(GRHXY/10.0) / CH2IpdvRange
        Xconv1 = float(GRWXY/10.0) / CH2pdvRange
        y1 = Y0TXY + GRHXY
        c2 = GRWXY / 2.0 + X0LXY   # Hor correction factor
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
        X_label = " V"
    if Xsignal.get() == 2:
        Xconv1 = float(GRWXY/10) / CH1IpdvRange
        Xoffset1 = CHAIOffset
        COLORXmarker = COLORtrace3
        X_label = " mA"
    if Xsignal.get() == 3 or Xsignal.get() == 7:
        Xconv1 = float(GRWXY/10) / CH2pdvRange
        Xoffset1 = CHBOffset
        COLORXmarker = COLORtrace2
        X_label = " V"
    if Xsignal.get() == 4:
        Xconv1 = float(GRWXY/10) / CH2IpdvRange
        Xoffset1 = CHBIOffset
        COLORmarker = COLORtrace4
        X_label = " mA"
    if Xsignal.get() == 5:
        X_label = MathXUnits
        if MathXAxis == "V-A":
            Xconv1 = float(GRWXY/10) / CH1pdvRange
            Xoffset1 = CHAOffset
            COLORXmarker = COLORtrace1
        elif MathXAxis == "V-B":
            Xconv1 = float(GRWXY/10) / CH2pdvRange
            Xoffset1 = CHBOffset
            COLORXmarker = COLORtrace2
        elif MathXAxis == "I-A":
            Xconv1 = float(GRWXY/10) / CH1IpdvRange
            Xoffset1 = CHAIOffset
            COLORXmarker = COLORtrace3
        elif MathXAxis == "I-B":
            Xconv1 = float(GRWXY/10) / CH2IpdvRange
            Xoffset1 = CHBIOffset
            COLORXmarker = COLORtrace4
        else:
            Xconv1 = float(GRWXY/10) / CH1pdvRange
            Xoffset1 = CHAOffset
            COLORXmarker = COLORtrace1
#
    if Ysignal.get() == 1 or Ysignal.get() == 6:
        Yconv1 = float(GRHXY/10.0) / CH1pdvRange
        Yoffset1 = CHAOffset
        COLORYmarker = COLORtrace1
        Y_label = " V"
    if Ysignal.get() == 2:
        Yconv1 = float(GRHXY/10.0) / CH1IpdvRange
        Yoffset1 = CHAIOffset
        COLORYmarker = COLORtrace3
        Y_label = " mA"
    if Ysignal.get() == 3 or Ysignal.get() == 7:
        Yconv1 = float(GRHXY/10.0) / CH2pdvRange
        Yoffset1 = CHBOffset
        COLORYmarker = COLORtrace2
        Y_label = " V"
    if Ysignal.get() == 4:
        Yconv1 = float(GRHXY/10.0) / CH2IpdvRange
        Yoffset1 = CHBIOffset
        COLORYmarker = COLORtrace4
        Y_label = " mA"
    if Ysignal.get() == 5:
        Y_label = MathYUnits
        if MathYAxis == "V-A":
            Yconv1 = float(GRHXY/10.0) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORYmarker = COLORtrace1
        elif MathYAxis == "V-B":
            Yconv1 = float(GRHXY/10.0) / CH2pdvRange
            Yoffset1 = CHBOffset
            COLORYmarker = COLORtrace2
        elif MathYAxis == "I-A":
            Yconv1 = float(GRHXY/10.0) / CH1IpdvRange
            Yoffset1 = CHAIOffset
            COLORYmarker = COLORtrace3
        elif MathYAxis == "I-B":
            Yconv1 = float(GRHXY/10.0) / CH2IpdvRange
            Yoffset1 = CHBIOffset
            COLORYmarker = COLORtrace4
        else:
            Yconv1 = float(GRHXY/10.0) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORYmarker = COLORtrace1
    if ShowXCur.get() > 0:
        Dline = [XCursor, Y0TXY, XCursor, Y0TXY+GRHXY]
        XYca.create_line(Dline, dash=(4,3), fill=COLORXmarker, width=GridWidth.get())
        c1 = GRWXY / 2.0 + X0LXY    # fixed X correction 
        xvolts = Xoffset1 - ((c1-XCursor)/Xconv1)
        XString = ' {0:.3f} '.format(xvolts)
        V_label = XString + X_label
        XYca.create_text(XCursor+1, YCursor-5, text=V_label, fill=COLORXmarker, anchor="w", font=("arial", 8 ))
    if ShowYCur.get() > 0:
        Dline = [X0LXY, YCursor, X0LXY+GRWXY, YCursor]
        XYca.create_line(Dline, dash=(4,3), fill=COLORYmarker, width=GridWidth.get())
        c1 = GRHXY / 2.0 + Y0TXY    # fixed Y correction 
        yvolts = ((YCursor-c1)/Yconv1) - Yoffset1
        V1String = ' {0:.3f} '.format(-yvolts)
        V_label = V1String + Y_label
        XYca.create_text(XCursor+1, YCursor+5, text=V_label, fill=COLORYmarker, anchor="w", font=("arial", 8 ))
    if ShowXCur.get() == 0 and ShowYCur.get() == 0 and MouseWidget == XYca:
        if MouseX > X0LXY and MouseX < X0LXY+GRWXY and MouseY > Y0TXY and MouseY < Y0TXY+GRHXY:
            Dline = [MouseX, Y0TXY, MouseX, Y0TXY+GRHXY]
            XYca.create_line(Dline, dash=(4,3), fill=COLORXmarker, width=GridWidth.get())
            c1 = GRWXY / 2.0 + X0LXY    # fixed X correction 
            xvolts = Xoffset1 - ((c1-XCursor)/Xconv1)
            XString = ' {0:.3f} '.format(xvolts)
            V_label = XString + X_label
            XYca.create_text(MouseX+1, MouseY-5, text=V_label, fill=COLORXmarker, anchor="w", font=("arial", 8 ))
            Dline = [X0LXY, MouseY, X0LXY+GRWXY, MouseY]
            XYca.create_line(Dline, dash=(4,3), fill=COLORYmarker, width=GridWidth.get())
            c1 = GRHXY / 2 + Y0TXY    # fixed Y correction 
            yvolts = ((MouseY-c1)/Yconv1) - Yoffset1
            V1String = ' {0:.3f} '.format(-yvolts)
            V_label = V1String + Y_label
            XYca.create_text(MouseX+1, MouseY+5, text=V_label, fill=COLORYmarker, anchor="w", font=("arial", 8 ))
#
# General information on top of the grid
# Sweep information
    sttxt = "Running"
    if TRACEmodeTime.get() == 1:
        sttxt = sttxt + " Averaging"
    if SingleShot.get() == 1:
        sttxt = "Single Shot"
    if (RUNstatus.get() == 0) or (RUNstatus.get() == 3):
        sttxt = "Stopped"
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
    txt = "Device ID " + DevID[17:31] + " Sample rate: " + str(SAMPLErate) + " " + sttxt
    x = X0LXY
    y = 12
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    # digital I/O indicators
    x2 = X0LXY + GRWXY
    BoxColor = "#808080"   # gray
    if DacScreenStatus.get() == 0 and DigScreenStatus.get() == 1 :
        if D0.get() == 0 and D4.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
                BoxColor = "#ff0000"   # 100% red
            XYca.create_rectangle(x2-12, 6, x2, 18, fill=BoxColor)
        else:
            XYca.create_rectangle(x2-12, 6, x2, 18, fill="yellow")
        if D1.get() == 0 and D5.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
                BoxColor = "#ff0000"   # 100% red
            XYca.create_rectangle(x2-26, 6, x2-14, 18, fill=BoxColor)
        else:
            XYca.create_rectangle(x2-26, 6, x2-14, 18, fill="yellow")
        if D2.get() == 0 and D6.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
                BoxColor = "#ff0000"   # 100% red
            XYca.create_rectangle(x2-40, 6, x2-28, 18, fill=BoxColor)
        else:
            XYca.create_rectangle(x2-40, 6, x2-28, 18, fill="yellow")
        if D3.get() == 0 and D7.get() == 0:
            Dval = devx.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100)
            if Dval[0] == 1:
                BoxColor = "#00ff00"   # 100% green
            elif Dval[0] == 0:
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
                txt = txt + " CA Hi Width = "
                V1String = ' {0:.2f} '.format(CHAHW)
                txt = txt + str(V1String) + " mS "
            if MeasALW.get() == 1:
                txt = txt + " CA Lo Width = "
                V1String = ' {0:.2f} '.format(CHALW)
                txt = txt + str(V1String) + " mS "
            if MeasADCy.get() == 1:
                txt = txt + " CA DutyCycle = "
                V1String = ' {0:.1f} '.format(CHADCy)
                txt = txt + str(V1String) + " % "
            if MeasAPER.get() == 1:
                txt = txt + " CA Period = "
                V1String = ' {0:.2f} '.format(CHAperiod)
                txt = txt + str(V1String) + " mS "
            if MeasAFREQ.get() == 1:
                txt = txt + " CA Freq = "
                V1String = ' {0:.1f} '.format(CHAfreq)
                txt = txt + str(V1String) + " Hz "
        if Xsignal.get() == 3:
            if MeasBHW.get() == 1:
                txt = txt + " CB Hi Width = "
                V1String = ' {0:.2f} '.format(CHBHW)
                txt = txt + str(V1String) + " mS "
            if MeasBLW.get() == 1:
                txt = txt + " CB Lo Width = "
                V1String = ' {0:.2f} '.format(CHBLW)
                txt = txt + str(V1String) + " mS "
            if MeasBDCy.get() == 1:
                txt = txt + " CB DutyCycle = "
                V1String = ' {0:.1f} '.format(CHBDCy)
                txt = txt + str(V1String) + " % "
            if MeasBPER.get() == 1:
                txt = txt + " CB Period = "
                V1String = ' {0:.2f} '.format(CHBperiod)
                txt = txt + str(V1String) + " mS "
            if MeasBFREQ.get() == 1:
                txt = txt + " CB Freq = "
                V1String = ' {0:.1f} '.format(CHBfreq)
                txt = txt + str(V1String) + " Hz "
        if MeasPhase.get() == 1:
            txt = txt + " CA-B Phase = "
            V1String = ' {0:.1f} '.format(CHABphase)
            txt = txt + str(V1String) + " deg "
            
    x = X0LXY
    y = Y0TXY+GRHXY+20
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    txt = " "
    if Xsignal.get() == 1 or Ysignal.get() == 1 or Xsignal.get() == 6:
    # Channel A information
        txt = "CHA: "
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
    if Xsignal.get() == 2:
        txt = "CHA: "
        txt = txt + str(CH1IpdvRange) + " mA/div"
    elif (Xsignal.get() == 2):
        txt = txt + "CHA: "
        txt = txt + str(CH1IpdvRange) + " mA/div"
    if Xsignal.get() == 2 or Ysignal.get() == 2:
        if MeasDCI1.get() == 1:
            V1String = ' {0:.2f} '.format(DCI1)
            txt = txt + " AvgI = " + V1String
            if AWGAShape.get() == 0: # if this is a DC measurement calc resistance
                try:
                    Resvalue = (DCV1/DCI1)*1000
                    R1String = ' {0:.1f} '.format(Resvalue)
                    txt = txt + " Res = " + R1String
                except:
                    txt = txt + " Res = OverRange" 
        if MeasMaxI1.get() == 1:
            V1String = ' {0:.2f} '.format(MaxI1)
            txt = txt +  " MaxI = " + V1String
        if MeasMinI1.get() == 1:
            V1String = ' {0:.2f} '.format(MinI1)
            txt = txt +  " MinI = " + V1String
        if MeasMidI1.get() == 1:
            MidI1 = (MaxI1+MinI1)/2
            V1String = ' {0:.2f} '.format(MidI1)
            txt = txt +  " MidV = " + V1String
        if MeasPPI1.get() == 1:
            PPI1 = MaxI1-MinI1
            V1String = ' {0:.2f} '.format(PPI1)
            txt = txt +  " P-PI = " + V1String
        if MeasRMSI1.get() == 1:
            V1String = ' {0:.4f} '.format(SI1)
            txt = txt +  " RMS = " + V1String
        
    x = X0LXY
    y = Y0TXY+GRHXY+32
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
    txt= " "
    # Channel B information
    if Xsignal.get() == 3 or Ysignal.get() == 3 or Xsignal.get() == 7:
        txt = "CHB: "
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
    if Xsignal.get() == 4:
        txt = "CHB: "
        txt = txt + str(CH2IpdvRange) + " mA/div"
    elif Xsignal.get() == 4:
        txt = txt + "CHB: "
        txt = txt + str(CH2IpdvRange) + " mA/div"
    if Xsignal.get() == 4 or Ysignal.get() == 4:
        if MeasDCI2.get() == 1:
            V1String = ' {0:.2f} '.format(DCI2)
            txt = txt + " AvgI = " + V1String
            if AWGBShape.get() == 0: # if this is a DC measurement calc resistance
                try:
                    Resvalue = (DCV2/DCI2)*1000
                    R1String = ' {0:.1f} '.format(Resvalue)
                    txt = txt + " Res = " + R1String
                except:
                    txt = txt + " Res = OverRange" 
        if MeasMaxI2.get() == 1:
            V1String = ' {0:.2f} '.format(MaxI2)
            txt = txt +  " MaxI = " + V1String
        if MeasMinI2.get() == 1:
            V1String = ' {0:.2f} '.format(MinI2)
            txt = txt +  " MinI = " + V1String
        if MeasMidI2.get() == 1:
            MidI2 = (MaxI2+MinI2)/2
            V1String = ' {0:.2f} '.format(MidI2)
            txt = txt +  " MidV = " + V1String
        if MeasPPI2.get() == 1:
            PPI2 = MaxI2-MinI2
            V1String = ' {0:.2f} '.format(PPI2)
            txt = txt +  " P-PI = " + V1String
        if MeasRMSI2.get() == 1:
            V1String = ' {0:.4f} '.format(SI2)
            txt = txt +  " RMS = " + V1String
            
    x = X0LXY
    y = Y0TXY+GRHXY+44
    XYca.create_text(x, y, text=txt, anchor=W, fill=COLORtext)
#
def SetScaleA():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 1:
        MarkerScale.set(1)
        CHAlab.config(style="Rtrace1.TButton")
        CHBlab.config(style="Strace2.TButton")
        CHAIlab.config(style="Strace3.TButton")
        CHBIlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)
#
def SetScaleIA():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 3:
        MarkerScale.set(3)
        CHAlab.config(style="Strace1.TButton")
        CHBlab.config(style="Strace2.TButton")
        CHAIlab.config(style="Rtrace3.TButton")
        CHBIlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)

def SetScaleB():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 2:
        MarkerScale.set(2)
        CHAlab.config(style="Strace1.TButton")
        CHBlab.config(style="Rtrace2.TButton")
        CHAIlab.config(style="Strace3.TButton")
        CHBIlab.config(style="Strace4.TButton")
    else:
        MarkerScale.set(0)

def SetScaleIB():
    global MarkerScale, CHAlab, CHBlab, CHAIlab, CHBIlab

    if MarkerScale.get() != 3:
        MarkerScale.set(4)
        CHAlab.config(style="Strace1.TButton")
        CHBlab.config(style="Strace2.TButton")
        CHAIlab.config(style="Strace3.TButton")
        CHBIlab.config(style="Rtrace4.TButton")
    else:
        MarkerScale.set(0)
#
def SetXYScaleA():
    global MarkerXYScale, CHAxylab, CHBxylab

    MarkerXYScale.set(1)
    CHAxylab.config(style="Rtrace1.TButton")
    CHBxylab.config(style="Strace2.TButton")

def SetXYScaleB():
    global MarkerXYScale, CHAxylab, CHBxylab

    MarkerXYScale.set(2)
    CHBxylab.config(style="Rtrace2.TButton")
    CHAxylab.config(style="Strace1.TButton")       
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

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and shift_key == 0:
            VCursor = VCursor - 1
        elif ShowVCur.get() > 0 and shift_key == 1:
            VCursor = VCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowYCur.get() > 0 and shift_key == 0:
                YCursor = YCursor - 1
            elif ShowYCur.get() > 0 and shift_key == 1:
                YCursor = YCursor - 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowdBCur.get() > 0 and shift_key == 0:
                dBCursor = dBCursor - 1
            elif ShowdBCur.get() > 0 and shift_key == 1:
                dBCursor = dBCursor - 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBdBCur.get() > 0 and shift_key == 0:
                BdBCursor = BdBCursor - 1
            elif ShowBdBCur.get() > 0 and shift_key == 1:
                BdBCursor = BdBCursor - 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasDownArrow(event):
    global ShowVCur, VCursor, YCursor, dBCursor, BdBCursor, RUNstatus, ca, XYca, Freqca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowVCur.get() > 0 and shift_key == 0:
            VCursor = VCursor + 1
        elif ShowVCur.get() > 0 and shift_key == 1:
            VCursor = VCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowYCur.get() > 0 and shift_key == 0:
                YCursor = YCursor + 1
            elif ShowYCur.get() > 0 and shift_key == 1:
                YCursor = YCursor + 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowdBCur.get() > 0 and shift_key == 0:
                dBCursor = dBCursor + 1
            elif ShowdBCur.get() > 0 and shift_key == 1:
                dBCursor = dBCursor + 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBdBCur.get() > 0 and shift_key == 0:
                BdBCursor = BdBCursor + 1
            elif ShowBdBCur.get() > 0 and shift_key == 1:
                BdBCursor = BdBCursor + 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasLeftArrow(event):
    global ShowTCur, TCursor, XCursor, FCursor, BPCursor, RUNstatus, ca, XYca, Freqca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and shift_key == 0:
            TCursor = TCursor - 1
        elif ShowTCur.get() > 0 and shift_key == 1:
            TCursor = TCursor - 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowXCur.get() > 0 and shift_key == 0:
                XCursor = XCursor - 1
            elif ShowXCur.get() > 0 and shift_key == 1:
                XCursor = XCursor - 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowFCur.get() > 0 and shift_key == 0:
                FCursor = FCursor - 1
            elif ShowFCur.get() > 0 and shift_key == 1:
                FCursor = FCursor - 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBPCur.get() > 0 and shift_key == 0:
                BPCursor = BPCursor - 1
            elif ShowBPCur.get() > 0 and shift_key == 1:
                BPCursor = BPCursor - 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasRightArrow(event):
    global ShowTCur, TCursor, XCursor, FCursor, BPCursor, RUNstatus, ca, XYca, Freqca

    shift_key = event.state & 1
    if event.widget == ca:
        if ShowTCur.get() > 0 and shift_key == 0:
            TCursor = TCursor + 1
        elif ShowTCur.get() > 0 and shift_key == 1:
            TCursor = TCursor + 5
        if RUNstatus.get() == 0:
            UpdateTimeScreen()
    try:
        if event.widget == XYca:
            if ShowXCur.get() > 0 and shift_key == 0:
                XCursor = XCursor + 1
            elif ShowXCur.get() > 0 and shift_key == 1:
                XCursor = XCursor + 5
            if RUNstatus.get() == 0:
                UpdateXYScreen()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if ShowFCur.get() > 0 and shift_key == 0:
                FCursor = FCursor + 1
            elif ShowFCur.get() > 0 and shift_key == 1:
                FCursor = FCursor + 5
            if RUNstatus.get() == 0:
                UpdateFreqScreen()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if ShowBPCur.get() > 0 and shift_key == 0:
                BPCursor = BPCursor + 1
            elif ShowBPCur.get() > 0 and shift_key == 1:
                BPCursor = BPCursor + 5
            if RUNstatus.get() == 0:
                UpdateBodeScreen()
    except:
        donothing()
#
def onCanvasSpaceBar(event):
    global RUNstatus, ca, XYca, Freqca, Bodeca, IAca

    if event.widget == ca:
        if RUNstatus.get() == 0:
            BStart()
        elif RUNstatus.get() > 0:
            BStop()
    try:
        if event.widget == XYca:
            if RUNstatus.get() == 0:
                BStart()
            elif RUNstatus.get() > 0:
                BStop()
    except:
        donothing()
    try:
        if event.widget == IAca:
            if RUNstatus.get() == 0:
                BStart()
            elif RUNstatus.get() > 0:
                BStop()
    except:
        donothing()
    try:
        if event.widget == Freqca:
            if RUNstatus.get() == 0:
                BStartSA()
            elif RUNstatus.get() > 0:
                BStopSA()
    except:
        donothing()
    try:
        if event.widget == Bodeca:
            if RUNstatus.get() == 0:
                BStartBP()
            elif RUNstatus.get() > 0:
                BStopBP()
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
    global TMsb, CHAsb, CHBsb, CHAIsb, CHBIsb, MarkerScale
    global CHAVPosEntry, CHAIPosEntry, CHBVPosEntry, CHBIPosEntry
    global SAMPLErate, RUNstatus, MarkerNum, PrevV, PrevT
    global COLORtrace1, COLORtrace2, MathUnits, MathXUnits, MathYUnits
    global CH1pdvRange, CH2pdvRange, CH1IpdvRange, CH2IpdvRange
    global CHAOffset, CHAIOffset, CHBOffset, CHBIOffset
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry
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
        if TIMEdiv < 0.0002:
            TIMEdiv = 0.01
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
            CH1IpdvRange = float(eval(CHAIsb.get()))
        except:
            CHAIsb.delete(0,END)
            CHAIsb.insert(0, CH1IpdvRange)
        try:
            CH2IpdvRange = float(eval(CHBIsb.get()))
        except:
            CHBIsb.delete(0,END)
            CHBIsb.insert(0, CH2IpdvRange)
        # get the vertical offsets
        try:
            CHAOffset = float(eval(CHAVPosEntry.get()))
        except:
            CHAVPosEntry.delete(0,END)
            CHAVPosEntry.insert(0, CHAOffset)
        try:
            CHAIOffset = float(eval(CHAIPosEntry.get()))
        except:
            CHAIPosEntry.delete(0,END)
            CHAIPosEntry.insert(0, CHAIOffset)
        try:
            CHBOffset = float(eval(CHBVPosEntry.get()))
        except:
            CHBVPosEntry.delete(0,END)
            CHBVPosEntry.insert(0, CHBOffset)
        try:
            CHBIOffset = float(eval(CHBIPosEntry.get()))
        except:
            CHBIPosEntry.delete(0,END)
            CHBIPosEntry.insert(0, CHBIOffset)
        # prevent divide by zero error
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
        if CH2pdvRange < 0.001:
            CH2pdvRange = 0.001
        if CH1IpdvRange < 1.0:
            CH1IpdvRange = 1.0
        if CH2IpdvRange < 1.0:
            CH2IpdvRange = 1.0
        try:
            HoldOff = float(eval(HoldOffentry.get()))
            if HoldOff < 0:
                HoldOff = 0
        except:
            HoldOffentry.delete(0,END)
            HoldOffentry.insert(0, HoldOff)
#
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
        Yoffset1 = CHAOffset
        if MarkerScale.get() == 1:
            Yconv1 = float(GRH/10.0) / CH1pdvRange
            Yoffset1 = CHAOffset
            COLORmarker = COLORtrace1
            Units = " V"
        if MarkerScale.get() == 2:
            Yconv1 = float(GRH/10.0) / CH2pdvRange
            Yoffset1 = CHBOffset
            COLORmarker = COLORtrace2
            Units = " V"
        if MarkerScale.get() == 3:
            Yconv1 = float(GRH/10.0) / CH1IpdvRange
            Yoffset1 = CHAIOffset
            COLORmarker = COLORtrace3
            Units = " mA"
        if MarkerScale.get() == 4:
            Yconv1 = float(GRH/10.0) / CH2IpdvRange
            Yoffset1 = CHBIOffset
            COLORmarker = COLORtrace4
            Units = " mA"
        # Aanalog Mux settings
        if MarkerScale.get() == 5:
            Yconv1 = float(GRH/10.0) / CHMApdvRange
            Yoffset1 = CHBAOffset
            COLORmarker = COLORtrace2
            Units = " V"
        if MarkerScale.get() == 6:
            Yconv1 = float(GRH/10.0) / CHMBpdvRange
            Yoffset1 = CHBBOffset
            COLORmarker = COLORtrace6
            Units = " V"
        if MarkerScale.get() == 7:
            Yconv1 = float(GRH/10.0) / CHMCpdvRange
            Yoffset1 = CHBCOffset
            COLORmarker = COLORtrace7
            Units = " V"
        if MarkerScale.get() == 8:
            Yconv1 = float(GRH/10.0) / CHMDpdvRange
            Yoffset1 = CHBDOffset
            COLORmarker = COLORtrace4
            Units = " V"
    #
        c1 = GRH / 2.0 + Y0T    # fixed correction channel A
        xc1 = GRW / 2.0 + X0L
        c2 = GRH / 2.0 + Y0T    # fixed correction channel B
        # draw X at marker point and number
        ca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORtext)
        ca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORtext)
        DISsamples = (10.0 * TIMEdiv) # grid width in time 
        Tstep = DISsamples / GRW # time in mS per pixel
        Tpoint = ((event.x-X0L) * Tstep) + HoldOff
        TString = ' {0:.2f} '.format(Tpoint)
        yvolts = ((event.y-c1)/Yconv1) - Yoffset1
        if MarkerScale.get() == 1 or MarkerScale.get() == 2:
            V1String = ' {0:.3f} '.format(-yvolts)
        else:
            V1String = ' {0:.1f} '.format(-yvolts)
        V_label = str(MarkerNum) + " " + TString + " mS, " + V1String
        V_label = V_label + Units
        if MarkerNum > 1:
            if MarkerScale.get() == 1 or MarkerScale.get() == 2:
                DeltaV = ' {0:.3f} '.format(PrevV-yvolts)
            else:
                DeltaV = ' {0:.1f} '.format(PrevV-yvolts)
            DeltaT = ' {0:.3f} '.format(Tpoint-PrevT)
            V_label = V_label + " Delta " + DeltaT + " mS, " + DeltaV
            V_label = V_label + Units
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
        ca.create_text(event.x+4, event.y, text=str(MarkerNum), fill=COLORtext, anchor=Justify, font=("arial", 8 ))
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
    global ShowC1_I

    if ShowC1_I.get() == 0:
        ShowC1_I.set(1)
    else:
        ShowC1_I.set(0)
#
def onCanvasFour(event):
    global ShowC2_I

    if ShowC2_I.get() == 0:
        ShowC2_I.set(1)
    else:
        ShowC2_I.set(0)
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
    global ShowXCur, ShowYCur, XCursor, YCursor, RUNstatus
    if event.widget == XYca:
        if ShowXCur.get() > 0 or ShowYCur.get() > 0: # move cursors if shown
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
    global XYca
    global HoldOffentry, Xsignal, Ysignal, COLORgrid, COLORtext
    global TMsb, CHAsbxy, CHBsbxy, CHAIsbxy, CHBIsbxy, MarkerScale
    global CHAVPosEntryxy, CHAIPosEntryxy, CHBVPosEntryxy, CHBIPosEntryxy
    global SAMPLErate, RUNstatus, MarkerNum, PrevX, PrevY
    global COLORtrace1, COLORtrace2, MathUnits, MathXUnits, MathYUnits
    global CH1pdvRange, CH2pdvRange, CH1IpdvRange, CH2IpdvRange
    global CHAOffset, CHAIOffset, CHBOffset, CHBIOffset
    # add markers only if stopped
    # 
    if (RUNstatus.get() == 0):
        MarkerNum = MarkerNum + 1
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
            CH1IpdvRange = float(eval(CHAIsbxy.get()))
        except:
            CHAIsbxy.delete(0,END)
            CHAIsbxy.insert(0, CH1IpdvRange)
        try:
            CH2IpdvRange = float(eval(CHBIsbxy.get()))
        except:
            CHBIsbxy.delete(0,END)
            CHBIsbxy.insert(0, CH2IpdvRange)
        # get the vertical offsets
        try:
            CHAOffset = float(eval(CHAVPosEntryxy.get()))
        except:
            CHAVPosEntryxy.delete(0,END)
            CHAVPosEntryxy.insert(0, CHAOffset)
        try:
            CHAIOffset = float(eval(CHAIPosEntryxy.get()))
        except:
            CHAIPosEntryxy.delete(0,END)
            CHAIPosEntryxy.insert(0, CHAIOffset)
        try:
            CHBOffset = float(eval(CHBVPosEntryxy.get()))
        except:
            CHBVPosEntryxy.delete(0,END)
            CHBVPosEntryxy.insert(0, CHBOffset)
        try:
            CHBIOffset = float(eval(CHBIPosEntryxy.get()))
        except:
            CHBIPosEntryxy.delete(0,END)
            CHBIPosEntryxy.insert(0, CHBIOffset)
        # prevent divide by zero error
        if CH1pdvRange < 0.001:
            CH1pdvRange = 0.001
        if CH2pdvRange < 0.001:
            CH2pdvRange = 0.001
        if CH1IpdvRange < 1.0:
            CH1IpdvRange = 1.0
        if CH2IpdvRange < 1.0:
            CH2IpdvRange = 1.0
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
        Yconv2 = float(GRHXY/10) / CH2pdvRange
        Xconv2 = float(GRWXY/10) / CH2pdvRange
        # YIconv1 = float(GRH/10) / CH1IpdvRange
        # YIconv2 = float(GRH/10) / CH2IpdvRange
        COLORmarker = COLORtext
        Yoffset1 = CHAOffset
        c1 = GRHXY / 2 + Y0TXY    # fixed correction channel A
        xc1 = GRWXY / 2 + X0LXY
        c2 = GRHXY / 2 + Y0TXY    # fixed correction channel B
        # draw X at marker point and number
        XYca.create_line(event.x-4, event.y-4,event.x+4, event.y+5, fill=COLORtext)
        XYca.create_line(event.x+4, event.y-4,event.x-4, event.y+5, fill=COLORtext)
        XYca.create_text(event.x+4, event.y, text=str(MarkerNum), fill=COLORtext, anchor="w", font=("arial", 8 ))
        if (Xsignal.get()==1 or Xsignal.get()==5) and (Ysignal.get()==3 or Ysignal.get()==5):
            yvolts = ((event.y-c2)/Yconv2) - CHBOffset
            xvolts = ((xc1-event.x)/Xconv1) - CHAOffset
            VyString = ' {0:.3f} '.format(-yvolts)
            VxString = ' {0:.3f} '.format(-xvolts)
            V_label = str(MarkerNum) + " " + VxString + " V, " + VyString + " V"
            if MarkerNum > 1:
                DeltaY = ' {0:.3f} '.format(PrevY-yvolts)
                DeltaX = ' {0:.3f} '.format(PrevX-xvolts)
                V_label = V_label + " Delta " + DeltaX + " V, " + DeltaY + " V"
            x = X0LXY + 5
            y = Y0TXY + 3 + (MarkerNum*10)
            XYca.create_text(x, y, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
            PrevY = yvolts
            PrevX = xvolts
        elif (Xsignal.get()==3 or Xsignal.get()==5) and (Ysignal.get()==1 or Ysignal.get()==5):
            yvolts = ((event.y-c1)/Yconv1) - CHAOffset
            xvolts = ((xc1-event.x)/Xconv2) - CHBOffset
            VyString = ' {0:.3f} '.format(-yvolts)
            VxString = ' {0:.3f} '.format(-xvolts)
            V_label = str(MarkerNum) + " " + VxString + " V, " + VyString + " V"
            if MarkerNum > 1:
                DeltaY = ' {0:.3f} '.format(PrevY-yvolts)
                DeltaX = ' {0:.3f} '.format(PrevX-xvolts)
                V_label = V_label + " Delta " + DeltaX + " V, " + DeltaY + " V"
            x = X0LXY + 5
            y = Y0TXY + 3 + (MarkerNum*10)
            XYca.create_text(x, y, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
            PrevY = yvolts
            PrevX = xvolts               
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
#
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
    print len(frames)
    frames = ''.join(frames)
    print len(frames)
    for x in xrange(0, repeat):
        print x
        wavfile.writeframes(frames)
    wavfile.close()
    
# =========== Awg functions ==================
def BAWGAAmpl(temp):
    global AWGAAmplEntry, AWGAAmplvalue, AWGAMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    try:
        AWGAAmplvalue = float(eval(AWGAAmplEntry.get()))
    except:
        AWGAAmplEntry.delete(0,"end")
        AWGAAmplEntry.insert(0, AWGAAmplvalue)
    #
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            if AWGAAmplvalue > 5.00:
                AWGAAmplvalue = 5.00
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
            if AWGAAmplvalue < 0.00:
                AWGAAmplvalue = 0.00
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
    elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            if AWGAAmplvalue > 2.5:
                AWGAAmplvalue = 2.5
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
            if AWGAAmplvalue < -2.50:
                AWGAAmplvalue = -2.50
                AWGAAmplEntry.delete(0,"end")
                AWGAAmplEntry.insert(0, AWGAAmplvalue)
    if AWGAMode.get() == 1: # Source current measure voltage mode
        if AWGAAmplvalue > 200.00:
            AWGAAmplvalue = 200.00
            AWGAAmplEntry.delete(0,"end")
            AWGAAmplEntry.insert(0, AWGAAmplvalue)
        if AWGAAmplvalue < -200.00:
            AWGAAmplvalue = -200.00
            AWGAAmplEntry.delete(0,"end")
            AWGAAmplEntry.insert(0, AWGAAmplvalue)
#
def BAWGAOffset(temp):
    global AWGAOffsetEntry, AWGAOffsetvalue, AWGAMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    try:
        AWGAOffsetvalue = float(eval(AWGAOffsetEntry.get()))
    except:
        AWGAOffsetEntry.delete(0,"end")
        AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
    if AWGAMode.get() == 0: # Source Voltage measure current mode
        if AWGAOffsetvalue > 5.00:
            AWGAOffsetvalue = 5.00
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
        if AWGAOffsetvalue < 0.00:
            AWGAOffsetvalue = 0.00
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
    if AWGAMode.get() == 1: # Source current measure voltage mode
        if AWGAOffsetvalue > 200.00:
            AWGAOffsetvalue = 200.00
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
        if AWGAOffsetvalue < -200.00:
            AWGAOffsetvalue = -200.00
            AWGAOffsetEntry.delete(0,"end")
            AWGAOffsetEntry.insert(0, AWGAOffsetvalue)
#
def BAWGAFreq(temp):
    global AWGAFreqEntry, AWGAFreqvalue

    try:
        AWGAFreqvalue = float(eval(AWGAFreqEntry.get()))
    except:
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)

    if AWGAFreqvalue > 25000: # max freq is 20KHz
        AWGAFreqvalue = 25000
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    if AWGAFreqvalue < 0: # Set negative frequency entry to 0
        AWGAFreqvalue = 0
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, AWGAFreqvalue)
    #UpdateAWGA()

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
    global AWGADutyCycleEntry, AWGADutyCyclevalue

    try:
        AWGADutyCyclevalue = float(eval(AWGADutyCycleEntry.get()))/100
    except:
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)

    if AWGADutyCyclevalue > 1: # max duty cycle is 100%
        AWGADutyCyclevalue = 1
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue*100)
    if AWGADutyCyclevalue < 0: # min duty cycle is 0%
        AWGADutyCyclevalue = 0
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0, AWGADutyCyclevalue)
    #UpdateAWGA()

def BAWGAShape():
    global AWGAShape, AWGAWave, phasealab, duty1lab

    if AWGAShape.get() == 0:
        AWGAWave = 'dc'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 1:
        AWGAWave = 'sine'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 2:
        AWGAWave = 'triangle'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 3:
        AWGAWave = 'sawtooth'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 4:
        AWGAWave = 'square'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() == 5:
        AWGAWave = 'stairstep'
        duty1lab.config(text="%")
        BAWGAPhaseDelay()
    if AWGAShape.get() > 5:
        AWGAWave = 'arbitrary'
    # UpdateAWGA()

def AWGAReadFile():
    global AWGAwaveform, AWGALength, awgwindow

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    try:
        CSVFile = open(filename)
        # dialect = csv.Sniffer().sniff(CSVFile.read(128))
        CSVFile.seek(0)
        #csv_f = csv.reader(CSVFile, dialect)
        csv_f = csv.reader(CSVFile, csv.excel)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
    # print csv_f.dialect
    AWGAwaveform = []
    ColumnNum = 0
    ColumnSel = 0
    RowNum = 0
    for row in csv_f:
        # print 'found row = ', row
        if len(row) > 1 and ColumnSel == 0:
            RequestColumn = askstring("Which Column?", "File contains 1 to " + str(len(row)) + " columns\n\nEnter column number to import:\n", initialvalue=1, parent=awgwindow)
            ColumnNum = int(RequestColumn) - 1
            ColumnLen = str(len(row))
            ColumnSel = 1
        try:
            colnum = 0
            for col in row:
                if colnum == ColumnNum:
                    AWGAwaveform.append(float(col))
                colnum += 1
        except:
            print 'skipping non-numeric row', RowNum
        RowNum += 1
    AWGAwaveform = numpy.array(AWGAwaveform)
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    CSVFile.close()
    UpdateAwgCont()

def AWGAReadWAV():
    global AWGAwaveform, AWGALength, AWGAShape, awgwindow, AWGBwaveform, AWGBLength, AWGBShape

# Read values from WAV file
    filename = askopenfilename(defaultextension = ".wav", filetypes=[("WAV files", "*.wav")], parent=awgwindow)
    try:
        spf = wave.open(filename,'r')
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
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
            AWGAwaveform.append((Stereo[n] * 2.5 / 32768) + 2.5)
            n = n + 1
            AWGBwaveform.append((Stereo[n] * 2.5 / 32768) + 2.5)
            n = n + 1
        AWGAwaveform = numpy.array(AWGAwaveform)
        AWGBwaveform = numpy.array(AWGBwaveform)
        AWGALength.config(text = "L = " + str(len(AWGAwaveform))) # change displayed value
        AWGBLength.config(text = "L = " + str(len(AWGBwaveform))) # change displayed value
        AWGBShape.set(AWGAShape.get())
    else:
    #Extract Raw Audio from Wav File
        signal = spf.readframes(Length)
        WAVsignal = numpy.fromstring(signal, 'Int16') # convert strings to Int
        # offset and scale for 0 5 V range
        AWGAwaveform = (WAVsignal * 2.5 / 32768) + 2.5
        AWGAwaveform = numpy.array(AWGAwaveform)
        AWGALength.config(text = "L = " + str(len(AWGAwaveform))) # change displayed value
    spf.close()
    UpdateAwgCont()

def AWGAWriteFile():
    global AWGAwaveform, AWGALength, awgwindow
    
    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    numpy.savetxt(filename, AWGAwaveform, delimiter=",", fmt='%2.4f')
    
def AWGAMakeMath():
    global AWGAwaveform, AWGSAMPLErate, VBuffA, VBuffB, IBuffA, IBuffB
    global AWGBwaveform, VmemoryA, VmemoryB, ImemoryA, ImemoryB, AWGAMathString
    global FFTBuffA, FFTBuffB, FFTwindowshape, AWGALength, awgwindow
    global DFiltACoef, DFiltBCoef

    TempString = AWGAMathString
    AWGAMathString = askstring("AWG A Math Formula", "Current Formula: " + AWGAMathString + "\n\nNew Formula:\n", initialvalue=AWGAMathString, parent=awgwindow)
    if (AWGAMathString == None):         # If Cancel pressed, then None
        AWGAMathString = TempString
        return
    AWGAwaveform = eval(AWGAMathString)
    AWGAwaveform = numpy.array(AWGAwaveform)
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
#
def AWGAMakeBodeSine():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAperiodvalue
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWGAgain, AWGAoffset, AWGAPhaseDelay, AWGAMode
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)

    if AWGAFreqvalue < 10.0: # if frequency is less than 10 Hz use libsmu sine function
        AWGAShape.set(1)
        BAWGAShape()
        UpdateAwgCont()
        return

    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 10.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * AWGSAMPLErate / 1000
    Cycles = int(32768/AWGAperiodvalue)
    if Cycles < 1:
        Cycles = 1
    RecLength = Cycles * AWGAperiodvalue
    AWGAwaveform = []
    AWGAwaveform = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    if AWGAMode.get() == 1: # convert to mA
        amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / -2000.0
        offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2000.0
    else:
        amplitude = (AWGAOffsetvalue-AWGAAmplvalue) / -2.0
        offset = (AWGAOffsetvalue+AWGAAmplvalue) / 2.0
    AWGAwaveform = (AWGAwaveform * amplitude) + offset # scale and offset the waveform
    AWGAwaveform = numpy.roll(AWGAwaveform, int(AWGAdelayvalue))
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    BAWGAPhaseDelay()
    duty1lab.config(text="%")
    UpdateAwgCont()
#
def AWGAMakePWMSine():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)

    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    
    PulseWidth = int(AWGADutyCyclevalue*100)
    PulseSamples = int(AWGAperiodvalue/PulseWidth)
    AWGAwaveform = []
    for i in range(PulseSamples): #(i = 0; i < cPulse; i++)
        v = round(PulseWidth/2*(1+numpy.sin(i*2*numpy.pi/PulseSamples)))
    # print(v)
        for j in range(PulseWidth): #(j = 0; j < cLength; j++)
            if j >= v:
                AWGAwaveform.append(MaxV) # j>=v?1:0
            else:
                AWGAwaveform.append(MinV) # j>=v?1:0
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
#
def AWGAMakeFourier():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGALength
    global AWGADutyCyclevalue, AWGAFreqvalue, duty1lab, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGADutyCycle(temp)
    
    Max_term = int(AWGADutyCyclevalue*100)
    AWGAwaveform = []
    AWGAwaveform = numpy.cos(numpy.linspace(0, 2*numpy.pi, AWGSAMPLErate/AWGAFreqvalue)) # the fundamental
    k = 3
    while k <= Max_term:
        # Add odd harmonics up to max_term
        Harmonic = (math.sin(k*numpy.pi/2.0)/k)*(numpy.cos(numpy.linspace(0, k*2*numpy.pi, AWGSAMPLErate/AWGAFreqvalue)))
        AWGAwaveform = AWGAwaveform + Harmonic
        k = k + 2 # skip even numbers
    if AWG_Amp_Mode.get() == 0:
        amplitude = (AWGAOffsetvalue-AWGAAmplvalue)/2.0
        offset = (AWGAOffsetvalue+AWGAAmplvalue)/2.0
    else:
        amplitude = AWGAAmplvalue
        offset = AWGAOffsetvalue
    AWGAwaveform = (AWGAwaveform * amplitude) + offset # scale and offset the waveform
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="Harmonics")
    UpdateAwgCont()
#
def AWGAMakeSSQ():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*100)
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
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
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="%")
    phasealab.config(text = "Rise Time")
    UpdateAwgCont()
#
def AWGAMakeTrapazoid():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*100) # convert mS to samples
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
    StepValue = (MaxV - MinV) / SlopeValue
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
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="%")
    phasealab.config(text = "Rise Time")
    UpdateAwgCont()
#
def AWGAMakeRamp():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, phasealab, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    SlopeValue = int(AWGAPhasevalue*100) # convert mS to samples
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
    StepValue = (MaxV - MinV) / SlopeValue
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGAwaveform.append(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGAwaveform.append(MaxV)
    for i in range(Remainder):
        AWGAwaveform.append(MinV)
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    duty1lab.config(text="%")
    phasealab.config(text = "Slope Time")
    UpdateAwgCont()
#
def AWGAMakeUpDownRamp():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, duty1lab
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int(AWGAperiodvalue - PulseWidth)
    if Remainder <= 0:
        Remainder = 1
    UpStepValue = (MaxV - MinV) / PulseWidth
    DownStepValue = (MaxV - MinV) / Remainder
    SampleValue = MinV
    for i in range(PulseWidth):
        AWGAwaveform.append(SampleValue)
        SampleValue = SampleValue + UpStepValue
    for i in range(Remainder):
        AWGAwaveform.append(SampleValue)
        SampleValue = SampleValue - DownStepValue
    AWGAwaveform = numpy.roll(AWGAwaveform, int(AWGAPhasevalue*100))
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    BAWGAPhaseDelay()
    duty1lab.config(text = "Symmetry")
    UpdateAwgCont()
#
def AWGAMakeImpulse():
    global AWGAwaveform, AWGAAmplvalue, AWGAOffsetvalue, AWGALength, AWGAPhaseDelay, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global AWGAFreqvalue, AWGAperiodvalue, AWGSAMPLErate, AWGADutyCyclevalue, AWGAPhasevalue

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        MaxV = AWGAOffsetvalue
        MinV = AWGAAmplvalue
    AWGAwaveform = []
    PulseWidth = int(AWGAperiodvalue * AWGADutyCyclevalue / 2.0)
    if AWGAPhaseDelay.get() == 0:
        DelayValue = int(AWGAperiodvalue*(AWGAPhasevalue/360))
    elif AWGAPhaseDelay.get() == 1:
        DelayValue = int(AWGAPhasevalue*100)
    for i in range(DelayValue-PulseWidth):
        AWGAwaveform.append((MinV+MaxV)/2.0)
    for i in range(PulseWidth):
        AWGAwaveform.append(MaxV)
    for i in range(PulseWidth):
        AWGAwaveform.append(MinV)
    DelayValue = int(AWGAperiodvalue-DelayValue)
    for i in range(DelayValue-PulseWidth):
        AWGAwaveform.append((MinV+MaxV)/2.0)
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGAMakeUUNoise():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        if AWGAAmplvalue > AWGAOffsetvalue:
            MinV = AWGAOffsetvalue
            MaxV = AWGAAmplvalue
        else:
            MaxV = AWGAOffsetvalue
            MinV = AWGAAmplvalue
    AWGAwaveform = []
    AWGAwaveform = numpy.random.uniform(MinV, MaxV, int(AWGAperiodvalue))
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGAMakeUGNoise():
    global AWGAwaveform, AWGSAMPLErate, AWGAAmplvalue, AWGAOffsetvalue, AWGAFreqvalue
    global AWGALength, AWGAperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
        MinV = (AWGAOffsetvalue-AWGAAmplvalue)
    else:
        if AWGAAmplvalue > AWGAOffsetvalue:
            MinV = AWGAOffsetvalue
            MaxV = AWGAAmplvalue
        else:
            MaxV = AWGAOffsetvalue
            MinV = AWGAAmplvalue
    AWGAwaveform = []
    AWGAwaveform = numpy.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGAperiodvalue))
    AWGALength.config(text = "L = " + str(int(len(AWGAwaveform)))) # change displayed value
    UpdateAwgCont()
    
def BAWGAModeLabel():
    global AWGAMode, AWGAIOMode, AWGAModeLabel, DevID, session, devx, DevOne, CHA, HWRevOne
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    if AWGAMode.get() == 0: # Source Voltage measure current mode
        label_txt = "SVMI"
    elif AWGAMode.get() == 1: # Source current measure voltage mode
        label_txt = "SIMV"
    elif AWGAMode.get() == 2: # High impedance mode
        label_txt = "Hi-Z" 
    if AWGAIOMode.get() > 0: # Split Input / Output mode
        if HWRevOne == "D":
            if AWGAMode.get() == 0:
                AWGAMode.set(1)
                CHA.set_mode('i') # channel must be in source current mode for rev D boards
                label_txt = "SIMV"
        label_txt = label_txt + " Split I/O"
    label_txt = label_txt + " Mode"
    AWGAModeLabel.config(text = label_txt ) # change displayed value
    UpdateAwgCont()

def UpdateAWGA():
    global AWGAAmplvalue, AWGAOffsetvalue
    global AWGAFreqvalue, AWGAPhasevalue, AWGAPhaseDelay
    global AWGADutyCyclevalue, FSweepMode, AWGARepeatFlag, AWGSync
    global AWGAWave, AWGAMode, AWGATerm, AWGAwaveform, AWGAIOMode
    global CHA, AWGSAMPLErate, DevID, devx, HWRevOne, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global amp1lab, off1lab
    
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    BAWGAShape()

    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode, 1 = Amp/Offset
        amp1lab.config(text = "Min Ch A" ) # change displayed value
        off1lab.config(text = "Max Ch A" ) # change displayed value
    else:
        amp1lab.config(text = "Amp Ch A" )
        off1lab.config(text = "Off Ch A" )
        
    if AWGAFreqvalue > 0.0:
        AWGAperiodvalue = AWGSAMPLErate/AWGAFreqvalue
    else:
        AWGAperiodvalue = 0.0

    if AWGAPhaseDelay.get() == 0:
        if AWGAWave == 'square':
            AWGAPhasevalue = AWGAPhasevalue + 270.0
            if AWGAPhasevalue > 359:
                AWGAPhasevalue = AWGAPhasevalue - 360
        if AWGAPhasevalue > 0:
            AWGAdelayvalue = AWGAperiodvalue * AWGAPhasevalue / 360.0
        else:
            AWGAdelayvalue = 0.0
    elif AWGAPhaseDelay.get() == 1:
        AWGAdelayvalue = AWGAPhasevalue * 100

    if AWGATerm.get() == 0: # Open termination
        devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    elif AWGATerm.get() == 1: # 50 Ohm termination to GND
        devx.ctrl_transfer( 0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x50, 33, 0, 0, 0, 100) # set GND switch to closed
    elif AWGATerm.get() == 2: # 50 Ohm termination to +2.5 Volts
        devx.ctrl_transfer( 0x40, 0x50, 32, 0, 0, 0, 100) # set 2.5 V switch to closed
        devx.ctrl_transfer( 0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
        
    if AWGAWave == 'dc':
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.SVMI # Put CHA in SVMI mode
            else:
                CHA.mode = Mode.SVMI_SPLIT # Put CHA in SVMI split mode
            CHA.constant(AWGAOffsetvalue)
            # 
        if AWGAMode.get() == 1: # Source current measure voltage mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.SIMV # Put CHA in SIMV mode
            else:
                CHA.mode = Mode.SIMV_SPLIT # Put CHA in SIMV split mode
            CHA.constant(AWGAOffsetvalue/1000)
            #
        if AWGAMode.get() == 2: # High impedance mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
            else:
                CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
#
        if AWGAIOMode.get() > 0: # Split Input / Output mode
            if HWRevOne == "D":
                AWGAMode.set(1)
                CHA.mode = Mode.SIMV_SPLIT # channel must be in source current mode
#
    else:
        if AWGAMode.get() == 0: # Source Voltage measure current mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.SVMI # Put CHA in SVMI mode
            else:
                CHA.mode = Mode.SVMI_SPLIT # Put CHA in SVMI split mode
        if AWGAMode.get() == 1: # Source current measure voltage mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.SIMV # Put CHA in SIMV mode
            else:
                CHA.mode = Mode.SIMV_SPLIT # Put CHA in SIMV split mode
            AWGAOffsetvalue = AWGAOffsetvalue/1000
            AWGAAmplvalue = AWGAAmplvalue/1000
        if AWGAMode.get() == 2: # High impedance mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
            else:
                CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
            # CHA.constant(0.0)
        else:
            if AWG_Amp_Mode.get() == 1:
                MaxV = (AWGAOffsetvalue+AWGAAmplvalue)
                MinV = (AWGAOffsetvalue-AWGAAmplvalue)
            else:
                MaxV = AWGAOffsetvalue
                MinV = AWGAAmplvalue
            try:
                if AWGAWave == 'sine':
                    CHA.sine(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'triangle':
                    CHA.triangle(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'sawtooth':
                    CHA.sawtooth(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'square':
                    CHA.square(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue, AWGADutyCyclevalue)
                elif AWGAWave == 'stairstep':
                    CHA.stairstep(MaxV, MinV, AWGAperiodvalue, AWGAdelayvalue)
                elif AWGAWave == 'arbitrary':
                    if AWGSync.get() == 0:
                        AWGARepeatFlag.set(1)
                    CHA.arbitrary(AWGAwaveform, AWGARepeatFlag.get()) # set repeat flag
            except:
                    donothing()
        if AWGAIOMode.get() > 0: # Split Input / Output mode
            if HWRevOne == "D":
                AWGAMode.set(1)
                CHA.mode = Mode.SIMV_SPLIT # channel must be in source current mode
# AWG B functions 
def BAWGBAmpl(temp):
    global AWGBAmplEntry, AWGBAmplvalue, AWGBMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    try:
        AWGBAmplvalue = float(eval(AWGBAmplEntry.get()))
        if AWGBMode.get() == 0: # Source Voltage measure current mode
            if AWG_Amp_Mode.get() == 0: # 0 = Min/Max
                if AWGBAmplvalue > 5.00:
                    AWGBAmplvalue = 5.00
                    AWGBAmplEntry.delete(0,"end")
                    AWGBAmplEntry.insert(0, AWGBAmplvalue)
                if AWGBAmplvalue < 0.00:
                    AWGBAmplvalue = 0.00
                    AWGBAmplEntry.delete(0,"end")
                    AWGBAmplEntry.insert(0, AWGBAmplvalue)
            elif AWG_Amp_Mode.get() == 1: # 1 = Amp/Offset
                if AWGBAmplvalue > 2.5:
                    AWGBAmplvalue = 2.5
                    AWGBAmplEntry.delete(0,"end")
                    AWGBAmplEntry.insert(0, AWGBAmplvalue)
                if AWGBAmplvalue < -2.50:
                    AWGBAmplvalue = -2.50
                    AWGBAmplEntry.delete(0,"end")
                    AWGBAmplEntry.insert(0, AWGBAmplvalue)
        elif AWGBMode.get() == 1: # Source current measure voltage mode
            if AWGBAmplvalue > 200.00:
                AWGBAmplvalue = 200.00
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
            if AWGBAmplvalue < -200.00:
                AWGBAmplvalue = -200.00
                AWGBAmplEntry.delete(0,"end")
                AWGBAmplEntry.insert(0, AWGBAmplvalue)
    except:
        AWGBAmplEntry.delete(0,"end")
        AWGBAmplEntry.insert(0, AWGBAmplvalue)
#
def BAWGBOffset(temp):
    global AWGBOffsetEntry, AWGBOffsetvalue, AWGBMode, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    try:
        AWGBOffsetvalue = float(eval(AWGBOffsetEntry.get()))
        if AWGBMode.get() == 0: # Source Voltage measure current mode
            if AWGBOffsetvalue > 5.00:
                AWGBOffsetvalue = 5.00
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            if AWGBOffsetvalue < 0.00:
                AWGBOffsetvalue = 0.00
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
        elif AWGBMode.get() == 1: # Source current measure voltage mode
            if AWGBOffsetvalue > 200.00:
                AWGBOffsetvalue = 200.00
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
            if AWGBOffsetvalue < -200.00:
                AWGBOffsetvalue = -200.00
                AWGBOffsetEntry.delete(0,"end")
                AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
    except:
        AWGBOffsetEntry.delete(0,"end")
        AWGBOffsetEntry.insert(0, AWGBOffsetvalue)
#
def BAWGBFreq(temp):
    global AWGBFreqEntry, AWGBFreqvalue

    try:
        AWGBFreqvalue = float(eval(AWGBFreqEntry.get()))
    except:
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)

    if AWGBFreqvalue > 25000: # max freq is 20KHz
        AWGBFreqvalue = 25000
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    if AWGBFreqvalue < 0: # Set negative frequency entry to 0
        AWGBFreqvalue = 0
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, AWGBFreqvalue)
    # UpdateAWGB()

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
    global AWGBDutyCycleEntry, AWGBDutyCyclevalue

    try:
        AWGBDutyCyclevalue = float(eval(AWGBDutyCycleEntry.get()))/100
    except:
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)

    if AWGBDutyCyclevalue > 1: # max duty cycle is 100%
        AWGBDutyCyclevalue = 1
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue*100)
    if AWGBDutyCyclevalue < 0: # min duty cycle is 0%
        AWGBDutyCyclevalue = 0
        AWGBDutyCycleEntry.delete(0,"end")
        AWGBDutyCycleEntry.insert(0, AWGBDutyCyclevalue)
    # UpdateAWGB()
    
def BAWGBShape():
    global AWGBShape, AWGBWave, duty2lab
    
    if AWGBShape.get() == 0:
        AWGBWave = 'dc'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 1:
        AWGBWave = 'sine'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 2:
        AWGBWave = 'triangle'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 3:
        AWGBWave = 'sawtooth'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 4:
        AWGBWave = 'square'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() == 5:
        AWGBWave = 'stairstep'
        duty2lab.config(text="%")
        BAWGBPhaseDelay()
    if AWGBShape.get() > 5:
        AWGBWave = 'arbitrary'
    # UpdateAWGB()

def AWGBReadFile():
    global AWGBwaveform, AWGBLength, awgwindow

    # Read values from CVS file
    filename = askopenfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    try:
        CSVFile = open(filename)
        # dialect = csv.Sniffer().sniff(CSVFile.read(128), delimiters=None)
        CSVFile.seek(0)
        #csv_f = csv.reader(CSVFile, dialect)
        csv_f = csv.reader(CSVFile, csv.excel)
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
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
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    CSVFile.close()
    UpdateAwgCont()

def AWGBReadWAV():
    global AWGBwaveform, AWGBLength, awgwindow

# Read values from WAV file
    filename = askopenfilename(defaultextension = ".wav", filetypes=[("WAV files", "*.wav")], parent=awgwindow)
    try:
        spf = wave.open(filename,'r')
    except:
        showwarning("WARNING","No such file found or wrong format!", parent=awgwindow)
    AWGBwaveform = []
    #If Stereo
    if spf.getnchannels() == 2:
        showwarning("WARNING","Only mono files supported!", parent=awgwindow)
        return()
    #Extract Raw Audio from Wav File
    Length = spf.getnframes()
    if Length > 90000: # limit to first 90K samples
        Length = 90000
    signal = spf.readframes(Length)
    WAVsignal = numpy.fromstring(signal, 'Int16') # convert strings to Int
    # offset and scale for 0 5 V range
    AWGBwaveform = (WAVsignal * 2.5 / 32768) + 2.5
    AWGBwaveform = numpy.array(AWGBwaveform)
    AWGBLength.config(text = "L = " + str(len(AWGBwaveform))) # change displayed value
    spf.close()
    UpdateAwgCont()

def AWGBWriteFile():
    global AWGBwaveform, AWGBLength, awgwindow

    filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("CSV files", "*.csv")], parent=awgwindow)
    numpy.savetxt(filename, AWGBwaveform, delimiter=",", fmt='%2.4f')
    
def AWGBMakeMath():
    global AWGAwaveform, AWGSAMPLErate, VBuffA, VBuffB, IBuffA, IBuffB
    global AWGBwaveform, VmemoryA, VmemoryB, ImemoryA, ImemoryB, AWGBMathString
    global FFTBuffA, FFTBuffB, FFTwindowshape, AWGBLength, awgwindow
    global DFiltACoef, DFiltBCoef

    TempString = AWGBMathString
    AWGBMathString = askstring("AWG B Math Formula", "Current Formula: " + AWGBMathString + "\n\nNew Formula:\n", initialvalue=AWGBMathString, parent=awgwindow)
    if (AWGBMathString == None):         # If Cancel pressed, then None
        AWGBMathString = TempString
        return
    AWGBwaveform = eval(AWGBMathString)
    AWGBwaveform = numpy.array(AWGBwaveform)
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()
#
def AWGBMakeFourier():
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBFreqvalue, awgwindow
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    
    Max_termStr = askstring("AWG B Fourier", "\nEnter Max Harmonic:\n", parent=awgwindow)
    if (Max_termStr == None):         # If Cancel pressed, then None
        return
    Max_term = int(Max_termStr)
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)

    AWGBwaveform = []
    AWGBwaveform = numpy.cos(numpy.linspace(0, 2*numpy.pi, AWGSAMPLErate/AWGBFreqvalue)) # the fundamental
    k = 3
    while k <= Max_term:
        # Add odd harmonics up to max_term
        Harmonic = (math.sin(k*numpy.pi/2)/k)*(numpy.cos(numpy.linspace(0, k*2*numpy.pi, AWGSAMPLErate/AWGBFreqvalue)))
        AWGBwaveform = AWGBwaveform + Harmonic
        k = k + 2 # skip even numbers
    if AWG_Amp_Mode.get() == 0:
        amplitude = (AWGBOffsetvalue-AWGBAmplvalue)/2
        offset = (AWGBOffsetvalue+AWGBAmplvalue)/2
    else:
        amplitude = AWGBAmplvalue
        offset = AWGBOffsetvalue
    AWGBwaveform = (AWGBwaveform * amplitude) + offset # scale and offset the waveform
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="Harmonics")
    UpdateAwgCont()
#
def AWGBMakeBodeSine():
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBperiodvalue
    global AWGBDutyCyclevalue, AWGBFreqvalue, duty2lab, AWGBgain, AWGBoffset, AWGBPhaseDelay, AWGBMode
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)

    if AWGBFreqvalue < 10.0: # if frequency is less than 10 Hz use libsmu sine function
        AWGBShape.set(1)
        BAWGBShape()
        UpdateAwgCont()
        return

    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 10.0

    if AWGBPhaseDelay.get() == 0:
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * AWGSAMPLErate / 1000
    Cycles = int(32768/AWGBperiodvalue)
    if Cycles < 1:
        Cycles = 1
    RecLength = Cycles * AWGBperiodvalue
    AWGBwaveform = []
    AWGBwaveform = numpy.cos(numpy.linspace(0, 2*Cycles*numpy.pi, RecLength))
    if AWGBMode.get() == 1: # convert to mA
        amplitude = (AWGBOffsetvalue-AWGBAmplvalue) / -2000.0
        offset = (AWGBOffsetvalue+AWGBAmplvalue) / 2000.0
    else:
        amplitude = (AWGBOffsetvalue-AWGBAmplvalue) / -2.0
        offset = (AWGBOffsetvalue+AWGBAmplvalue) / 2.0
    AWGBwaveform = (AWGBwaveform * amplitude) + offset # scale and offset the waveform
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBdelayvalue))
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    BAWGBPhaseDelay()
    duty2lab.config(text="%")
    UpdateAwgCont()
#
def AWGBMakePWMSine():
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength
    global AWGBDutyCyclevalue, AWGBFreqvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)

    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    
    PulseWidth = int(AWGBDutyCyclevalue*100)
    PulseSamples = int(AWGBperiodvalue/PulseWidth)
    AWGBwaveform = []
    for i in range(PulseSamples): #(i = 0; i < cPulse; i++)
        v = round(PulseWidth/2*(1+numpy.sin(i*2*numpy.pi/PulseSamples)))
    # print(v)
        for j in range(PulseWidth): #(j = 0; j < cLength; j++)
            if j >= v:
                AWGBwaveform.append(MaxV) # j>=v?1:0
            else:
                AWGBwaveform.append(MinV) # j>=v?1:0
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()
#
def AWGBMakeSSQ():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    
    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*100)
    if SlopeValue <= 0:
        SlopeValue = 1
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue)
    if PulseWidth <=0:
        PulseWidth = 1
    Remainder = int((AWGBperiodvalue - PulseWidth - SlopeValue)/2)
    if Remainder <= 0:
        Remainder = 1
    PulseWidth = PulseWidth - SlopeValue
    if PulseWidth <=0:
        PulseWidth = 1
    StepAmp = (MaxV - MinV)/2
    StepOff = (MaxV + MinV)/2
    AWGBwaveform = StepAmp * (numpy.cos(numpy.linspace(0, 2*numpy.pi, SlopeValue*2))) + StepOff
    MidArray = numpy.ones(PulseWidth) * MinV
    AWGBwaveform = numpy.insert(AWGBwaveform, SlopeValue, MidArray)
    AWGBwaveform = numpy.pad(AWGBwaveform, (Remainder, Remainder), 'edge')
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="%")
    phaseblab.config(text = "Rise Time")
    UpdateAwgCont()
#    
def AWGBMakeTrapazoid():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*100)
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
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="%")
    phaseblab.config(text = "Rise Time")
    UpdateAwgCont()
#
def AWGBMakeRamp():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    SlopeValue = int(AWGBPhasevalue*100)
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
    SampleValue = MinV
    for i in range(SlopeValue):
        AWGBwaveform.append(SampleValue)
        SampleValue = SampleValue + StepValue
    for i in range(PulseWidth):
        AWGBwaveform.append(MaxV)
    for i in range(Remainder):
        AWGBwaveform.append(MinV)
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    duty2lab.config(text="%")
    phaseblab.config(text = "Slope Time")
    UpdateAwgCont()
#
def AWGBMakeUpDownRamp():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    else:
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
    SampleValue = MinV
    for i in range(PulseWidth):
        AWGBwaveform.append(SampleValue)
        SampleValue = SampleValue + UpStepValue
    for i in range(Remainder):
        AWGBwaveform.append(SampleValue)
        SampleValue = SampleValue - DownStepValue
    AWGBwaveform = numpy.roll(AWGBwaveform, int(AWGBPhasevalue*100))
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    BAWGBPhaseDelay()
    duty2lab.config(text = "Symmetry")
    UpdateAwgCont()
#
def AWGBMakeImpulse():
    global AWGBwaveform, AWGBAmplvalue, AWGBOffsetvalue, AWGBLength, AWGBPhaseDelay
    global AWGBFreqvalue, AWGBperiodvalue, AWGSAMPLErate, AWGBDutyCyclevalue, AWGBPhasevalue
    global AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    MaxV = AWGBOffsetvalue
    MinV = AWGBAmplvalue
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    AWGBwaveform = []
    PulseWidth = int(AWGBperiodvalue * AWGBDutyCyclevalue / 2)
    if AWGBPhaseDelay.get() == 0:
        DelayValue = int(AWGBperiodvalue*(AWGBPhasevalue/360))
    elif AWGBPhaseDelay.get() == 1:
        DelayValue = int(AWGBPhasevalue*100)
    for i in range(DelayValue-PulseWidth):
        AWGBwaveform.append((MinV+MaxV)/2)
    for i in range(PulseWidth):
        AWGBwaveform.append(MaxV)
    for i in range(PulseWidth):
        AWGBwaveform.append(MinV)
    DelayValue = int(AWGBperiodvalue-DelayValue)
    for i in range(DelayValue-PulseWidth):
        AWGBwaveform.append((MinV+MaxV)/2)
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()

def AWGBMakeUUNoise():
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0

    if AWGBAmplvalue > AWGBOffsetvalue:
        MinV = AWGBOffsetvalue
        MaxV = AWGBAmplvalue
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    AWGBwaveform = []
    AWGBwaveform = numpy.random.uniform(MinV, MaxV, int(AWGBperiodvalue))
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()
    
def AWGBMakeUGNoise():
    global AWGBwaveform, AWGSAMPLErate, AWGBAmplvalue, AWGBOffsetvalue, AWGBFreqvalue
    global AWGBLength, AWGBperiodvalue, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset

    temp = 0
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
    if AWGBAmplvalue > AWGBOffsetvalue:
        MinV = AWGBOffsetvalue
        MaxV = AWGBAmplvalue
    else:
        MaxV = AWGBOffsetvalue
        MinV = AWGBAmplvalue
    if AWG_Amp_Mode.get() == 1:
        MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
        MinV = (AWGBOffsetvalue-AWGBAmplvalue)
    AWGBwaveform = []
    AWGBwaveform = numpy.random.normal((MinV+MaxV)/2, (MaxV-MinV)/3, int(AWGBperiodvalue))
    AWGBLength.config(text = "L = " + str(int(len(AWGBwaveform)))) # change displayed value
    UpdateAwgCont()

def BAWGBModeLabel():
    global AWGBMode, AWGBIOMode, AWGBModeLabel, DevID, devx, DevOne, CHB, HWRevOne

    if AWGBMode.get() == 0: # Source Voltage measure current mode
        label_txt = "SVMI"
    elif AWGBMode.get() == 1: # Source current measure voltage mode
        label_txt = "SIMV"
    elif AWGBMode.get() == 2: # High impedance mode
        label_txt = "Hi-Z" 
    if AWGBIOMode.get() > 0: # Split Input / Output mode
        if HWRevOne == "D":
            if AWGBMode.get() == 0:
                AWGBMode.set(1)
                CHB.set_mode('i') # channel must be in source current mode for rev D boards
                label_txt = "SIMV"
        label_txt = label_txt + " Split I/O"
    label_txt = label_txt + " Mode"
    AWGBModeLabel.config(text = label_txt ) # change displayed value
    UpdateAwgCont()
    
def UpdateAWGB():
    global AWGBAmplvalue, AWGBOffsetvalue
    global AWGBFreqvalue, AWGBPhasevalue, AWGBPhaseDelay
    global AWGBDutyCyclevalue, FSweepMode, AWGBRepeatFlag, AWGSync
    global AWGBWave, AWGBMode, AWGBTerm, AWGBwaveform, AWGBIOMode
    global CHB, AWGSAMPLErate, DevID, devx, HWRevOne
    global amp2lab, off2lab, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    
    if AWG_Amp_Mode.get() == 0: # 0 = Min/Max mode, 1 = Amp/Offset
        amp2lab.config(text = "Min Ch B" ) # change displayed value
        off2lab.config(text = "Max Ch B" ) # change displayed value
    else:
        amp2lab.config(text = "Amp Ch B" )
        off2lab.config(text = "Off Ch B" )
        
    if AWGBFreqvalue > 0.0:
        AWGBperiodvalue = AWGSAMPLErate/AWGBFreqvalue
    else:
        AWGBperiodvalue = 0.0
#
    if AWGBPhaseDelay.get() == 0:
        if AWGBWave == 'square':
            AWGBPhasevalue = AWGBPhasevalue + 270.0
            if AWGBPhasevalue > 359:
                AWGBPhasevalue = AWGBPhasevalue - 360
        if AWGBPhasevalue > 0:
            AWGBdelayvalue = AWGBperiodvalue * AWGBPhasevalue / 360.0
        else:
            AWGBdelayvalue = 0.0
    elif AWGBPhaseDelay.get() == 1:
        AWGBdelayvalue = AWGBPhasevalue * 100
#        
    if AWGBTerm.get() == 0: # Open termination
        devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
    elif AWGBTerm.get() == 1: # 50 Ohm termination to GND
        devx.ctrl_transfer( 0x40, 0x51, 37, 0, 0, 0, 100) # set 2.5 V switch to open
        devx.ctrl_transfer( 0x40, 0x50, 38, 0, 0, 0, 100) # set GND switch to closed
    elif AWGBTerm.get() == 2: # 50 Ohm termination to +2.5 Volts
        devx.ctrl_transfer( 0x40, 0x50, 37, 0, 0, 0, 100) # set 2.5 V switch to closed
        devx.ctrl_transfer( 0x40, 0x51, 38, 0, 0, 0, 100) # set GND switch to open
        
    if AWGBWave == 'dc':
        if AWGBMode.get() == 0: # Source Voltage measure current mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.SVMI # Put CHB in SVMI mode
            else:
                CHB.mode = Mode.SVMI_SPLIT # Put CHB in SVMI split mode
            CHB.constant(AWGBOffsetvalue)
        if AWGBMode.get() == 1: # Source current measure Voltage mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.SIMV # Put CHB in SIMV mode
            else:
                CHB.mode = Mode.SIMV_SPLIT # Put CHB in SIMV split mode
            CHB.constant(AWGBOffsetvalue/1000)
        if AWGBMode.get() == 2: # Hi impedance mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
            else:
                CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
#
        if AWGBIOMode.get() > 0: # Split Input / Output mode
            if HWRevOne == "D":
                AWGBMode.set(1)
                CHB.mode = Mode.SIMV_SPLIT # channel must be in source current mode
#
    else:
        if AWGBMode.get() == 0: # Source Voltage measure current mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.SVMI # Put CHB in SVMI mode
            else:
                CHB.mode = Mode.SVMI_SPLIT # Put CHB in SVMI split mode
        if AWGBMode.get() == 1: # Source current measure Voltage mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.SIMV # Put CHB in SIMV mode
            else:
                CHB.mode = Mode.SIMV_SPLIT # Put CHB in SIMV split mode
            AWGBOffsetvalue = AWGBOffsetvalue/1000
            AWGBAmplvalue = AWGBAmplvalue/1000
        if AWGBMode.get() == 2: # Hi impedance mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
            else:
                CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        else:
            if AWG_Amp_Mode.get() == 1:
                MaxV = (AWGBOffsetvalue+AWGBAmplvalue)
                MinV = (AWGBOffsetvalue-AWGBAmplvalue)
            else:
                MaxV = AWGBOffsetvalue
                MinV = AWGBAmplvalue
            try: # keep going even if low level library returns an error
                if AWGBWave == 'sine':
                    CHB.sine(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'triangle':
                    CHB.triangle(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'sawtooth':
                    CHB.sawtooth(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'square':
                    CHB.square(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue, AWGBDutyCyclevalue)
                elif AWGBWave == 'stairstep':
                    CHB.stairstep(MaxV, MinV, AWGBperiodvalue, AWGBdelayvalue)
                elif AWGBWave == 'arbitrary':
                    if AWGSync.get() == 0:
                        AWGBRepeatFlag.set(1)
                    CHB.arbitrary(AWGBwaveform, AWGBRepeatFlag.get()) # set repeat flag
            except:
                    donothing()
        if AWGBIOMode.get() > 0: # Split Input / Output mode
            if HWRevOne == "D":
                AWGBMode.set(1)
                CHB.mode = Mode.SIMV_SPLIT # channel must be in source current mode
#
def UpdateAwgCont():
    global session, CHA, CHB, AWGSync
    # if running and in continuous streaming mode temp stop, flush buffer and restart to change AWG settings
    if (RUNstatus.get() == 1) and AWGSync.get() == 0:
        if session.continuous:
            # time.sleep(0.2)
            session.end()
            #time.sleep(0.01) # wait awhile here for some reason
            BAWGEnab() # set-up new AWG settings
            time.sleep(0.01) # wait awhile here for some reason
            #session.flush()
            session.start(0)
            #time.sleep(0.01) # wait awhile here for some reason
#
def UpdateAwgContRet(temp):
    UpdateAwgCont()
    
def BAWGEnab():
    global AWGAMode, AWGBMode, AWGSync
    global CHA, CHB, discontloop, contloop, session

    # Stream = False
    # print "Updateing AWGs"
    temp = 0
    BAWGAAmpl(temp)
    BAWGAOffset(temp)
    BAWGAFreq(temp)
    BAWGAPhase(temp)
    BAWGADutyCycle(temp)
    BAWGAShape()
    BAWGBAmpl(temp)
    BAWGBOffset(temp)
    BAWGBFreq(temp)
    BAWGBPhase(temp)
    BAWGBDutyCycle(temp)
    BAWGBShape()
    UpdateAWGA()
    UpdateAWGB()
            
def BAWGSync():
    global RUNstatus, AWGSync, session, CHA, CHB

    if (RUNstatus.get() == 1): # do this only if running
        if AWGSync.get() == 0:
            #UpdateAwgCont()
            session.flush()
            CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
            CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z mode
            BAWGEnab()
            session.start(0)
            time.sleep(0.02) # wait awhile here for some reason
        elif session.continuous:
            session.end()
            session.flush()
            CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z mode
            CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z mode

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
            HeaderString = HeaderString + 'CA-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CA-Mag, '
    if ShowCB_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'CB-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CB-Mag, '
    if ShowCA_P.get() == 1:
        HeaderString = HeaderString + 'Phase A-B, '
    if ShowCB_P.get() == 1:
        HeaderString = HeaderString + 'Phase B-A, '
    HeaderString = HeaderString + '\n'
    DataFile.write( HeaderString )   

    n = 0
    while n < len(FSweepAdB):
        F = FBins[FStep[n]] # look up frequency bin in list of bins
        txt = str(F)
        if ShowCA_VdB.get() == 1:
            V = 10 * math.log10(float(FSweepAdB[n])) + 17  # Add 17 dB for max value of +10 dB
            if dB == 0:
                V = 10.0**(V/20.0)
            txt = txt + "," + str(V) 
        if ShowCB_VdB.get() == 1:
            V = 10 * math.log10(float(FSweepBdB[n])) + 17  # Add 17 dB for max value of +10 dB
            if dB == 0:
                V = 10.0**(V/20.0)
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
    
    s = askstring("Vert Divisions", "Value: " + str(Vdiv.get()) + "\n\nNew value:\n(4-20)", parent=freqwindow)

    if (s == None): # If Cancel pressed, then None
        return()

    try:        # Error if for example no numeric characters or OK pressed without input (s = "")
        vs = int(s)
    except:
        s = "error"
        vs = 10

    if s != "error":
        Vdiv.set(vs)

    if Vdiv.get() < 4:
        Vdiv.set(4)

    if Vdiv.get() > 20:
        Vdiv.set(20)
    UpdateFreqTrace()

def BStartSA():
    global RUNstatus, PowerStatus, devx, PwrBt, freqwindow, session, AWGSync, contloop, discontloop
    global ShowC1_VdB, ShowC1_P, ShowC2_VdB, ShowC2_P, ShowMathSA, DevID, FWRevOne

    #AWGSync.set(0) # always run in continuous mode
    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    elif FWRevOne == 0.0:
        showwarning("WARNING","Out of data Firmware!")
    else:
        if PowerStatus == 0:
            PowerStatus = 1
            PwrBt.config(style="Pwr.TButton",text="PWR-On")
            devx.ctrl_transfer( 0x40, 0x51, 49, 0, 0, 0, 100) # turn on analog power

        if ShowC1_VdB.get() == 0 and ShowC2_VdB.get() == 0 and ShowMathSA.get() == 0 and ShowC1_P.get() == 0 and ShowC2_P.get() == 0:
            showwarning("WARNING","Select at least one trace first",  parent=freqwindow)
            return()    
        if RUNstatus.get() == 0:
            RUNstatus.set(1)
            if AWGSync.get() == 0: # running in continuous mode
                # print "number streaming ", session.active_devices
                if contloop == 0 or session.active_devices < 1:
                    session.start(0)
                    contloop = 1
                    discontloop = 0
                BAWGEnab()
                
            else:
                session.cancel() # cancel continuous session mode
                contloop = 0
                discontloop = 1
#
    UpdateFreqAll()          # Always Update

def BStopSA():
    global RUNstatus, session, AWGSync

    if (RUNstatus.get() == 1):
        RUNstatus.set(0)
        CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        if AWGSync.get() == 0: # running in continuous mode
            CHA.constant(0.0)
            CHB.constant(0.0)
            # print "Stoping continuous mode"
            # session.cancel() # cancel continuous session mode while paused
            if session.continuous:
                # print "Stoping Is Continuous? ", session.continuous
                # session.end()
                time.sleep(0.02)
                #print "Is Continuous? ", session.continuous
        else:
            contloop = 0
            discontloop = 1
            session.cancel()
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
    global RUNstatus, AWGSAMPLErate
    global ZEROstuffing, freqwindow, bodewindow
    
    if (RUNstatus.get() != 0):
        try:
            showwarning("WARNING","Stop sweep first", parent=freqwindow)
            return()
        except:
            try:
                showwarning("WARNING","Stop sweep first", parent=bodewindow)
                return()
            except:
                return()
    
    try:
        s = askstring("Zero stuffing","For better interpolation of levels between frequency samples.\nBut increases processing time!\n\nValue: "
                  + str(ZEROstuffing.get()) + "\n\nNew value:\n(0-5, 0 is no zero stuffing)", parent=freqwindow)
    except:
        try:
            s = askstring("Zero stuffing","For better interpolation of levels between frequency samples.\nBut increases processing time!\n\nValue: "
                  + str(ZEROstuffing.get()) + "\n\nNew value:\n(0-5, 0 is no zero stuffing)", parent=bodewindow)
        except:
            return()
    if (s == None):         # If Cancel pressed, then None
        return()

    try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
        v = int(s)
    except:
        s = "error"

    if s != "error":
        if v < 0:
            v = 0
        if v > 5:
            v = 5
        ZEROstuffing.set(v)

    # UpdateFreqScreen()          # Always Update    

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
    global RUNstatus, LoopNum, PowerStatus, devx, PwrBt, bodewindow, session, AWGSync
    global ShowCA_VdB, ShowCB_P, ShowCB_VdB, ShowCB_P, ShowMathBP, contloop, discontloop
    global FStep, NSteps, FSweepMode, HScaleBP, CutDC, AWGAMode, AWGAShape, AWGBMode, AWGBShape
    global StartBodeEntry, StopBodeEntry, SweepStepBodeEntry, DevID, FWRevOne
    global AWGAFreqEntry, AWGBFreqEntry, Reset_Freq

    if DevID == "No Device":
        showwarning("WARNING","No Device Plugged In!")
    elif FWRevOne == 0.0:
        showwarning("WARNING","Out of data Firmware!")
    else:
        if PowerStatus == 0:
            PowerStatus = 1
            PwrBt.config(style="Pwr.TButton",text="PWR-On")
            devx.ctrl_transfer( 0x40, 0x51, 49, 0, 0, 0, 100) # turn on analog power

        if ShowCA_VdB.get() == 0 and ShowCB_VdB.get() == 0 and ShowMathBP.get() == 0:
            showwarning("WARNING","Select at least one trace first",  parent=bodewindow)
            return()    
        CutDC.set(1) # set to remove DC
        if FSweepMode.get() == 1:    
            AWGAMode.set(0) # Set AWG A to SVMI
            AWGAShape.set(18) # Set Shape to Sine
            AWGBMode.set(2) # Set AWG B to Hi-Z
            Reset_Freq = AWGAFreqEntry.get()
        if FSweepMode.get() == 2:    
            AWGBMode.set(0) # Set AWG B to SVMI
            AWGBShape.set(18) # Set Shape to Sine
            AWGAMode.set(2) # Set AWG A to Hi-Z
            Reset_Freq = AWGBFreqEntry.get()
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
            if AWGSync.get() == 0: # running in continuous mode
                if contloop == 0:
                    #print "number streaming ", session.active_devices
                    if session.active_devices < 1:
                        session.start(0)
                    contloop = 1
                    discontloop = 0
                BAWGEnab()
                #print "Starting continuous mode"
            else:
                session.cancel() # cancel continuous session mode
            if FSweepMode.get() > 0:
                LoopNum.set(1)
                BeginIndex = int((BeginFreq/50000)*16384)
                EndIndex = int((EndFreq/50000)*16384)
                if NSteps.get() < 5:
                    NSteps.set(5)
                if HScaleBP.get() == 1:
                    LogFStop = math.log10(EndIndex)
                    try:
                        LogFStart = math.log10(BeginIndex)
                    except:
                        LogFStart = 1.0
                    FStep = numpy.logspace(LogFStart, LogFStop, num=NSteps.get(), base=10.0)
                else:
                    FStep = numpy.linspace(BeginIndex, EndIndex, num=NSteps.get())
        #
        # UpdateBodeAll()          # Always Update
#
def BStopBP():
    global RUNstatus, session, AWGSync, FSweepMode, AWGAFreqEntry, AWGBFreqEntry, Reset_Freq
    
    if FSweepMode.get() == 1:
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0, Reset_Freq)
    if FSweepMode.get() == 2:
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0, Reset_Freq)
#
    if (RUNstatus.get() == 1):
        RUNstatus.set(0)
        if AWGSync.get() == 0: # running in continuous mode
            session.cancel() # cancel continuous session mode while paused
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
def BSweepsteps():
    global RUNstatus, freqwindow
    global NSteps, LoopNum
    
    s = askstring("Number of frequency steps: ","Value: " + str(NSteps.get()) + " \n\nNew value:\n", parent=freqwindow)
    
    if (s == None):         # If Cancel pressed, then None
        return()

    try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
        v = int(s)
    except:
        s = "error"

    if s != "error":
        NSteps.set(v)

    if NSteps.get() <= 0:
        NSteps.set(5)
    if NSteps.get() > 1000:
        NSteps.set(1000)
    if RUNstatus.get() == 0:      # Update if stopped
        UpdateFreqTrace()
    if RUNstatus.get() == 2:      # Restart loop count if running
        LoopNum.set(1)
        
# ============================================ Freq Main routine ====================================================

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
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global FFTwindowshape, FFTbandwidth
    global AWGSAMPLErate, StartFreqEntry, StopFreqEntry, StartBodeEntry
    global SMPfft, LoopNum
    global STARTsample, STOPsample
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
    REX = REX * FFTwindowshape[:len(REX)]      # The windowing shape function only over the samples

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
    Fsample = float(AWGSAMPLErate / 2) / (TRACEsize - 1)
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
        if len(FFTresultB) == len(FFTmemoryB):
            FFTresultB = numpy.maximum(FFTresultB, FFTmemoryB)#
    if FreqTraceMode.get() == 3 and TRACEresetFreq == False:  # Average mode 3, add difference / TRACEaverage to v
        try:
            FFTresultB = FFTmemoryB + (FFTresultB - FFTmemoryB) / TRACEaverage.get()
            PhaseB = PhaseMemoryB +(PhaseB - PhaseMemoryB) / TRACEaverage.get()
        except:
            FFTmemoryB = FFTresultB
            PhaseMemoryB = PhaseB
# 
    TRACEsize = len(FFTresultA)
    Fsample = float(AWGSAMPLErate / 2) / (TRACEsize - 1)
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
        if len(FFTresultA) == len(FFTmemoryA):
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

        FSweepAdB.append(numpy.amax(FFTresultA))
        FSweepBdB.append(numpy.amax(FFTresultB))
        FSweepAPh.append(PhaseA[numpy.argmax(FFTresultA)])
        FSweepBPh.append(PhaseB[numpy.argmax(FFTresultB)])

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
    global AWGSAMPLErate, HScale, Fsample
    global StartFreqEntry, StopFreqEntry, PhCenFreqEntry, RelPhaseCenter
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global FreqTraceMode
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
        StopFreqEntry.insert(0,10000)
        StopFrequency = 10000
    if StartFrequency > StopFrequency :
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,50000)
        StopFrequency = 50000
    if StopFrequency < StartFrequency :
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,50000)
        StopFrequency = 50000
    try:
        Phasecenter = int(PhCenFreqEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenFreqEntry.delete(0,"end")
        PhCenFreqEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
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
    Fsample = float(AWGSAMPLErate / 2) / (TRACEsize - 1)       # Frequency step per sample   
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
    PeakIndexA = PeakIndexB = n
    PeakdbA = PeakdbB = PeakMdb = -200 # PeakdbB
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
                RelPhase = PhaseA[n]-PhaseB[n]
            RelPhase = RelPhase - Phasecenter
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            PhErr = 0.0018 * n * Fsample # calculate pahse error due half sample period offset
            RelPhase = RelPhase + PhErr - 12
            ya = Yp - Yphconv * RelPhase
            T1Pline.append(int(ya + 0.5))
        if ShowC2_P.get() == 1:
            T2Pline.append(int(x + 0.5))
            if FSweepMode.get() > 0:
                RelPhase = PhaseMemoryB[n]-PhaseMemoryA[n]
            else:
                RelPhase = PhaseB[n]-PhaseA[n]
            RelPhase = RelPhase - Phasecenter
            if RelPhase > 180:
                RelPhase = RelPhase - 360
            elif RelPhase < -180:
                RelPhase = RelPhase + 360
            PhErr = 0.0018 * n * Fsample # calculate pahse error due half sample period offset
            RelPhase = RelPhase - PhErr - 12
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
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB
    global DBdivindexBP   # Index value
    global DBdivlist    # dB per division list
    global DBlevelBP      # Reference level
    global GRHBP          # Screenheight
    global GRWBP          # Screenwidth
    global AWGSAMPLErate, HScaleBP, RUNstatus
    global StartBodeEntry, StopBodeEntry
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global FreqTraceMode, RelPhaseCenter, PhCenBodeEntry
    global TAFline, TBFline, TBPMline, TAPline, TBPline
    global Vdiv         # Number of vertical divisions
    global X0LBP        # Left top X value
    global Y0TBP        # Left top Y value

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
    try:
        Phasecenter = int(PhCenBodeEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenBodeEntry.delete(0,"end")
        PhCenBodeEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
    BeginIndex = int((BeginFreq/50000)*16384)
    EndIndex = int((EndFreq/50000)*16384)
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
        PeakdbA = -200
        PeakdbB = -200
        PeakMdb = -200
        n = 0
        for n in range(len(FSweepAdB)): # while n < len(FStep):
            if n < len(FStep): # check if n has gone out off bounds because user did something dumb
                F = FBins[int(FStep[n])] # look up frequency bin in list of bins
            else:
                F = FBins[int(FStep[0])]
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
                        dbA = (10 * math.log10(float(FSweepAdB[n])) + 17)   # Convert power to DBs, except for log(0) error
                        ya = Yc - Yconv * dbA  # Add 17 dB for max value of +10 dB ALSO in CSV file routine!
                    except:
                        ya = Ymax
                    if (ya < Ymin):
                        ya = Ymin
                    if (ya > Ymax):
                        ya = Ymax
                    if dbA > PeakdbA:
                        PeakdbA = dbA
                        PeakyA = int(ya + 0.5)
                        PeakxA = int(x + 0.5)
                        PeakfreqA = F
                    TAFline.append(int(ya + 0.5))
                if ShowCB_VdB.get() == 1:
                    TBFline.append(int(x + 0.5))
                    try:
                        dbB = (10 * math.log10(float(FSweepBdB[n])) + 17) # Add 17 dB for max value of +10 dB ALSO in CSV file routine!
                        yb = Yc - Yconv * dbB 
                    except:
                        yb = Ymax
                    if (yb < Ymin):
                        yb = Ymin
                    if (yb > Ymax):
                        yb = Ymax
                    if dbB > PeakdbB:
                        PeakdbB = dbB
                        PeakyB = int(yb + 0.5)
                        PeakxB = int(x + 0.5)
                        PeakfreqB = F
                    TBFline.append(int(yb + 0.5))
                if ShowCA_P.get() == 1:
                    TAPline.append(int(x + 0.5))
                    RelPhase = FSweepAPh[n] - FSweepBPh[n]
                    RelPhase = RelPhase - Phasecenter
                    if RelPhase > 180:
                        RelPhase = RelPhase - 360
                    elif RelPhase < -180:
                        RelPhase = RelPhase + 360
                    PhErr = 0.0018 * F # calculate phase error due half sample period offset
                    RelPhase = RelPhase + PhErr - 12
                    ya = Yp - Yphconv * RelPhase
                    TAPline.append(int(ya + 0.5))
                if ShowCB_P.get() == 1:
                    TBPline.append(int(x + 0.5))
                    RelPhase = FSweepBPh[n] - FSweepAPh[n]
                    RelPhase = RelPhase - Phasecenter
                    if RelPhase > 180:
                        RelPhase = RelPhase - 360
                    elif RelPhase < -180:
                        RelPhase = RelPhase + 360
                    PhErr = 0.0018 * F # calculate phase error due half sample period offset
                    RelPhase = RelPhase - PhErr - 12
                    ya = Yp - Yphconv * RelPhase
                    TBPline.append(int(ya + 0.5))
                if ShowMathBP.get() > 0:
                    TBPMline.append(int(x + 0.5))
                    dbA = (10 * math.log10(float(FSweepAdB[n])) + 17) # Convert power to DBs, except for log(0) error
                    dbB = (10 * math.log10(float(FSweepBdB[n])) + 17) # Add 17 dB for max value of +10 dB ALSO in CSV file routine!
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
    global AWGSAMPLErate, SingleShot, HScaleBP
    global SMPfft       # number of FFT samples
    global StartBodeEntry, StopBodeEntry
    global ShowCA_P, ShowCB_P, ShowRA_VdB, ShowRB_VdB, ShowMarkerBP
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP
    global ShowMathBP, BodeDisp, RelPhaseCenter, PhCenBodeEntry
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
    try:
        Phasecenter = int(PhCenBodeEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenBodeEntry.delete(0,"end")
        PhCenBodeEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
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
            Vaxis_value = Vaxis_value + Phasecenter
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
                if F == 1 or F == 10 or F == 100 or F == 1000 or F == 10000:
                    Bodeca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    axis_label = str(F)
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
            axis_label = str(axis_value)
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
        if ShowBdBCur.get() == 1:
            # Vertical conversion factors (level dBs) and border limits
            Yconv = float(GRHBP) / (Vdiv.get() * DBdivlist[DBdivindexBP.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
            Yc = float(Y0TBP) + Yconv * (DBlevelBP.get()) # Yc is the 0 dBm position, can be outside the screen!
            yvdB = ((Yc-BdBCursor)/Yconv)
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " dBV"
        else:
            # Vertical conversion factors (level degrees) and border limits
            Yconv = float(GRHBP) / 360.0 # Conversion factors, Yconv is the number of screenpoints per degree
            Yc = float(Y0TBP)  # Yc is the 180 degree position
            yvdB = 180 + ((Yc-BdBCursor)/Yconv) + Phasecenter
            VdBString = ' {0:.1f} '.format(yvdB)
            V_label = VdBString + " Deg"
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
            Peak_label = ' {0:.2f} '.format(PeakdbA) + ',' + ' {0:.1f} '.format(PeakfreqA)
            Bodeca.create_text(PeakxA, PeakyA, text=Peak_label, fill=COLORtrace1, anchor="e", font=("arial", 8 ))
    if len(TBFline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHB
        if OverRangeFlagB == 1:
            Bodeca.create_line(TBFline, fill=COLORsignalband, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        else:
            Bodeca.create_line(TBFline, fill=COLORtrace2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbB) + ',' + ' {0:.1f} '.format(PeakfreqB)
            Bodeca.create_text(PeakxB, PeakyB, text=Peak_label, fill=COLORtrace2, anchor="w", font=("arial", 8 ))
    if len(TAPline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Bodeca.create_line(TAPline, fill=COLORtrace3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if len(TBPline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the phase trace A-B 
        Bodeca.create_line(TBPline, fill=COLORtrace4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowCA_RdB.get() == 1 and len(TAFRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TAFRline, fill=COLORtraceR1, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRA) + ',' + ' {0:.1f} '.format(PeakfreqRA)
            Bodeca.create_text(PeakxRA, PeakyRA, text=Peak_label, fill=COLORtraceR1, anchor="e", font=("arial", 8 ))
    if ShowCB_RdB.get() == 1 and len(TBFRline) > 4:   # Write the ref trace B if active
        Bodeca.create_line(TBFRline, fill=COLORtraceR2, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakdbRB) + ',' + ' {0:.1f} '.format(PeakfreqRB)
            Freqca.create_text(PeakxRB, PeakyRB, text=Peak_label, fill=COLORtraceR2, anchor="w", font=("arial", 8 ))
    if ShowCA_RP.get() == 1 and len(TAPRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TAPRline, fill=COLORtraceR3, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowCB_RP.get() == 1 and len(TBPRline) > 4:   # Write the ref trace A if active
        Bodeca.create_line(TBPRline, fill=COLORtraceR4, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
    if ShowMathBP.get() > 0 and len(TBPMline) > 4:   # Write the Math trace if active
        Bodeca.create_line(TBPMline, fill=COLORtrace5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakMdb) + ',' + ' {0:.1f} '.format(PeakfreqM)
            Bodeca.create_text(PeakxM, PeakyM, text=Peak_label, fill=COLORtrace5, anchor="w", font=("arial", 8 ))
    if ShowRMathBP.get() == 1 and len(TBPRMline) > 4:   # Write the ref math trace if active
        Bodeca.create_line(TBPRMline, fill=COLORtraceR5, smooth=SmoothBool, splinestep=5, width=TRACEwidth.get())
        if ShowMarkerBP.get() == 1:
            Peak_label = ' {0:.2f} '.format(PeakRMdb) + ',' + ' {0:.1f} '.format(PeakfreqRM)
            Bodeca.create_text(PeakxRM, PeakyRM, text=Peak_label, fill=COLORtraceR5, anchor="w", font=("arial", 8 ))
    # General information on top of the grid

    txt = "    Sample rate: " + str(AWGSAMPLErate)
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
    
    MakeIATrace()         # Update the traces
    UpdateIAScreen()      # Update the screen 

def UpdateIATrace():      # Update trace and screen
    MakeIATrace()         # Update traces
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
def MakeIATrace():        # Update the grid and trace
    global FFTmemoryA, FFTresultA
    global FFTmemoryB, FFTresultB
    global PhaseA, PhaseB, PhaseMemoryA, PhaseMemoryB
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB, PeakRelPhase
    global PeakxM, PeakyM, PeakMdb, PeakfreqM, PeakphaseA, PeakphaseB 
    global PeakfreqA, PeakfreqB, GainCorEntry, PhaseCorEntry, PhaseCorrection
    global DBdivindex   # Index value
    global DBdivlist    # dB per division list
    global DBlevel      # Reference level
    global GRHIA          # Screenheight
    global GRWIA          # Screenwidth
    global AWGSAMPLErate
    global STARTsample, STOPsample, LoopNum, FSweepMode
    global TRACEmode
    global T1Vline, T2Vline, TMline, T1Pline, T2Pline
    global Vdiv         # Number of vertical divisions
    global X0LIA          # Left top X value
    global Y0TIA          # Left top Y value 
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries # in ohms 
    global ImpedanceXseries # in ohms

    # Set the TRACEsize variable
    TRACEsize = len(FFTresultA)     # Set the trace length
    Fsample = float(AWGSAMPLErate / 2) / (TRACEsize - 1)
    # Horizontal conversion factors (frequency Hz) and border limits
    STARTsample = 0     # First sample in FFTresult[] that is used
    STARTsample = int(math.ceil(STARTsample))               # First within screen range

    STOPsample = 45000 / Fsample       # Last sample in FFTresult[] that is used
    STOPsample = int(math.floor(STOPsample))                # Last within screen range, math.floor actually not necessary, part of int
#
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

        RelPhase = PhaseA[n]-PhaseB[n]
        if RelPhase > 180:
            RelPhase = RelPhase - 360
        elif RelPhase < -180:
            RelPhase = RelPhase + 360
        PhErr = 0.0018 * n * Fsample # calculate pahse error due half sample period offset
        RelPhase = RelPhase + PhErr - 12
        n = n + 1

    PeakRelPhase = PeakphaseB-PeakphaseA
    if PeakRelPhase > 180:
        PeakRelPhase = PeakRelPhase - 360
    elif PeakRelPhase < -180:
        PeakRelPhase = PeakRelPhase + 360
    PhErr = 0.0018 * PeakSample * Fsample # calculate pahse error due half sample period offset
    PeakRelPhase = PeakRelPhase + PhaseCorrection - PhErr # - 12
    PeakdbB = PeakdbB + GainCorrection
    DoImpedance()

def MakeIAScreen():       # Update the screen with traces and text
    global CANVASheightIA, CANVASwidthIA, IAca
    global PeakxA, PeakyA, PeakxB, PeakyB, PeakdbA, PeakdbB
    global PeakxM, PeakyM, PeakMdb, PeakfreqM
    global PeakfreqA, PeakfreqB, PeakfreqRA, PeakfreqRB
    global PeakxRA, PeakyRA, PeakxRB, PeakyRB, PeakdbRA, PeakdbRB
    global PeakxRM, PeakyRM, PeakRMdb, PeakfreqRM
    global PeakphaseA, PeakphaseB, PeakRelPhase, PhaseCalEntry
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
    global AWGSAMPLErate, OverRangeFlagA, OverRangeFlagB
    global SMPfft       # number of FFT samples
    global TRACEaverage # Number of traces for averageing
    global FreqTraceMode    # 1 normal 2 max 3 average
    global Vdiv         # Number of vertical divisions
    global ImpedanceMagnitude # in ohms 
    global ImpedanceAngle # in degrees 
    global ImpedanceRseries # in ohms 
    global ImpedanceXseries # in ohms

    # Delete all items on the screen
    de = IAca.find_enclosed( -10000, -10000, CANVASwidthIA+10000, CANVASheightIA+10000 )    
    for n in de: 
        IAca.delete(n)
 
    # Draw circular grid lines
    i = 1
    xcenter = GRWIA/2
    ycenter = GRHIA/2 
    Radius = (GRWIA-X0LIA)/11
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

    txt = "    Sample rate: " + str(AWGSAMPLErate)
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
        Cseries = -1 / ( 2 * 3.14159 * PeakfreqA * ImpedanceXseries ) # in farads
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
        Lseries = ImpedanceXseries / ( 2 * 3.14159 * PeakfreqA ) # in henry
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
    txt = "0.0 to 45000 Hz"
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
    global CANVASwidthIA, GRWIA, X0LIA, CANVASheightIA, GRHIA, Y0TIA

    if IAScreenStatus.get() == 0:
        IAScreenStatus.set(1)
        IADisp.set(1)
        IACheckBox()
        CutDC.set(1) # set to remove DC
        CANVASwidthIA = 170 + GRWIA + 2 * X0LIA     # The canvas width
        CANVASheightIA = GRHIA + Y0TIA + 10         # The canvas height
        AWGAMode.set(0) # Set AWG A to SVMI
        AWGAShape.set(1) # Set Shape to Sine
        AWGBMode.set(2) # Set AWG B to Hi-Z
        AWGSync.set(1) # Set AWGs to run
        iawindow = Toplevel()
        iawindow.title("Impedance Analyzer 1.2 " + RevDate)
        iawindow.protocol("WM_DELETE_WINDOW", DestroyIAScreen)
        frame2iar = Frame(iawindow, borderwidth=5, relief=RIDGE)
        frame2iar.pack(side=RIGHT, expand=NO, fill=BOTH)

        frame2ia = Frame(iawindow, borderwidth=5, relief=RIDGE)
        frame2ia.pack(side=TOP, expand=YES, fill=BOTH)

        IAca = Canvas(frame2ia, width=CANVASwidthIA, height=CANVASheightIA, background=COLORcanvas, cursor='cross')
        IAca.bind("<Configure>", IACaresize)
        IAca.bind("<Return>", DoNothing)
        IAca.bind("<space>", onCanvasSpaceBar)
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
        # add ADI logo 
        ADI1 = Label(frame2iar, image=logo, anchor= "sw", compound="top") #  height=49, width=116,
        ADI1.pack(side=TOP)

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
    global AWGSAMPLErate, ShowC1_VdB, ShowC2_VdB
    
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
            HeaderString = HeaderString + 'CA-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CA-Mag, '
    if ShowC2_VdB.get() == 1:
        if dB == 1:
            HeaderString = HeaderString + 'CB-dB, '
        if dB == 0:
            HeaderString = HeaderString + 'CB-Mag, '
    if ShowC1_P.get() == 1:
        HeaderString = HeaderString + 'Phase A-B, '
    if ShowC2_P.get() == 1:
        HeaderString = HeaderString + 'Phase B-A, '
    HeaderString = HeaderString + '\n'
    DataFile.write( HeaderString )

    Fsample = float(AWGSAMPLErate / 2) / (TRACEsize - 1)   # Frequency step per sample   

    n = 0
    while n < TRACEsize:
        F = n * Fsample
        txt = str(F)
        if ShowC1_VdB.get() == 1:
            V = 10 * math.log10(float(FFTresultA[n])) + 17  # Add 17 dB for max value of +10 dB
            if dB == 0:
                V = 10.0**(V/20.0)
            txt = txt + "," + str(V) 
        if ShowC2_VdB.get() == 1:
            V = 10 * math.log10(float(FFTresultB[n])) + 17  # Add 17 dB for max value of +10 dB
            if dB == 0:
                V = 10.0**(V/20.0)
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
    global AWGSAMPLErate, SingleShot, HScale, HarmonicMarkers
    global SMPfft       # number of FFT samples
    global StartFreqEntry, StopFreqEntry, PhCenFreqEntry, RelPhaseCenter
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
        StopFrequency = 100
    try:
        Phasecenter = int(PhCenFreqEntry.get())
        RelPhaseCenter.set(Phasecenter)
    except:
        PhCenFreqEntry.delete(0,"end")
        PhCenFreqEntry.insert(0,0)
        RelPhaseCenter.set(0)
        Phasecenter = 0
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
            Vaxis_value = Vaxis_value + Phasecenter
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
                if F == 1 or F == 10 or F == 100 or F == 1000 or F == 10000:
                    Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
                    axis_label = str(F)
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
    else:
        Freqdiv = (StopFrequency - StartFrequency) / 10
        while (i < 11):
            x = X0LF + i * GRWF/10.0
            Dline = [x,y1,x,y2]
            if i == 0 or i == 10:
                Freqca.create_line(Dline, fill=COLORgrid, width=GridWidth.get())
            else:
                Freqca.create_line(Dline, dash=(4,3), fill=COLORgrid, width=GridWidth.get())
            axis_value = (StartFrequency + (i * Freqdiv))
            axis_label = str(axis_value)
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
        # Vertical conversion factors (level dBs) and border limits
        Yconv = float(GRHF) / (Vdiv.get() * DBdivlist[DBdivindex.get()]) # Conversion factors, Yconv is the number of screenpoints per dB
        Yc = float(Y0TF) + Yconv * (DBlevel.get()) # Yc is the 0 dBm position, can be outside the screen!
        yvdB = ((Yc-dBCursor)/Yconv)
        VdBString = ' {0:.1f} '.format(yvdB)
        V_label = VdBString + " dBV"
        Freqca.create_text(FCursor+1, dBCursor+5, text=V_label, fill=COLORtext, anchor="w", font=("arial", 8 ))
    #
    SmoothBool = SmoothCurvesSA.get()
    # Draw traces
    if len(T1Fline) > 4:    # Avoid writing lines with 1 coordinate
        # Write the trace CHA
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
        # Write the trace CHB
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

    txt = "    Sample rate: " + str(AWGSAMPLErate)
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
    global AWGSAMPLErate               # The sample rate
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
            print "Filling FFT window with Ones"
    elif FFTwindow.get() == 8: # window shape array read from csv file
        FFTwindowname = "Window Shape From file"
        FFTbw = 0.0
    else:
        FFTbandwidth = int(FFTbw * AWGSAMPLErate / float(SMPfft)) 
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
    global AWGSAMPLErate, RUNstatus, COLORtext, MarkerFreqNum, PrevdBV, PrevF

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
    global ShowBPCur, ShowBdBCur, BPCursor, BdBCursor, RUNstatus

    # print event.state
    shift_key = event.state & 1
    if ShowBPCur.get() > 0 and shift_key == 0:
        BPCursor = BPCursor + event.delta/100
    elif ShowBdBCur.get() > 0 or shift_key == 1:
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
    global AWGSAMPLErate, RUNstatus, COLORtext, MarkerFreqNum, PrevdBV, PrevF, Vdiv

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
    time.sleep(0.05)
    if AWGAShape.get()==9:
        AWGAMakeImpulse()
    elif AWGAShape.get()==11:
        AWGAMakeTrapazoid()
    elif AWGAShape.get()==15:
        AWGAMakeSSQ()
    elif AWGAShape.get()==16:
        AWGAMakeRamp()
    elif AWGAShape.get()==17:
        AWGAMakePWMSine()
    elif AWGAShape.get()==18:
        AWGAMakeBodeSine()
    elif AWGAShape.get()==12:
        AWGAMakeUpDownRamp()
    elif AWGAShape.get()==14:
        AWGAMakeFourier()
    elif AWGAShape.get()==7:
        AWGAMakeUUNoise()
    elif AWGAShape.get()==8:
        AWGAMakeUGNoise()
    else:
        UpdateAwgCont()
    time.sleep(0.05)
#
def onAWGBscroll(event):
    global AWGBShape
    
    onTextScroll(event)
    time.sleep(0.05)
    if AWGBShape.get()==9:
        AWGBMakeImpulse()
    elif AWGBShape.get()==11:
        AWGBMakeTrapazoid()
    elif AWGBShape.get()==15:
        AWGBMakeSSQ()
    elif AWGBShape.get()==16:
        AWGBMakeRamp()
    elif AWGBShape.get()==17:
        AWGBMakePWMSine()
    elif AWGBShape.get()==18:
        AWGBMakeBodeSine()
    elif AWGBShape.get()==12:
        AWGBMakeUpDownRamp()
    elif AWGBShape.get()==14:
        AWGBMakeFourier()
    elif AWGBShape.get()==7:
        AWGBMakeUUNoise()
    elif AWGBShape.get()==8:
        AWGBMakeUGNoise()
    else:
        UpdateAwgCont()
    time.sleep(0.05)
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
    if AWGAShape.get()==9:
        AWGAMakeImpulse()
    elif AWGAShape.get()==11:
        AWGAMakeTrapazoid()
    elif AWGAShape.get()==15:
        AWGAMakeSSQ()
    elif AWGAShape.get()==16:
        AWGAMakeRamp()
    elif AWGAShape.get()==12:
        AWGAMakeUpDownRamp()
    elif AWGAShape.get()==14:
        AWGAMakeFourier()
    elif AWGAShape.get()==7:
        AWGAMakeUUNoise()
    elif AWGAShape.get()==8:
        AWGAMakeUGNoise()
#
def onAWGBkey(event):
    global AWGBShape
    
    onTextKey(event)
    if AWGBShape.get()==9:
        AWGBMakeImpulse()
    elif AWGBShape.get()==11:
        AWGBMakeTrapazoid()
    elif AWGBShape.get()==15:
        AWGBMakeSSQ()
    elif AWGBShape.get()==16:
        AWGBMakeRamp()
    elif AWGBShape.get()==12:
        AWGBMakeUpDownRamp()
    elif AWGBShape.get()==14:
        AWGBMakeFourier()
    elif AWGBShape.get()==7:
        AWGBMakeUUNoise()
    elif AWGBShape.get()==8:
        AWGBMakeUGNoise()
#
def onTextKeyAWG(event):
    onTextKey(event)
    UpdateAwgCont()
    
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
    spbox = event.widget
    if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    else: # decrement digit
        spbox.invoke('buttondown')
#
# ================ Make awg sub window ==========================
def MakeAWGWindow():
    global AWGAMode, AWGATerm, AWGAShape, AWGSync, awgwindow, AWGAPhaseDelay, AWGBPhaseDelay
    global AWGBMode, AWGBTerm, AWGBShape, AWGScreenStatus, AWGARepeatFlag, AWGBRepeatFlag
    global AWGAAmplEntry, AWGAOffsetEntry, AWGAFreqEntry, AWGAPhaseEntry, AWGADutyCycleEntry
    global AWGBAmplEntry, AWGBOffsetEntry, AWGBFreqEntry, AWGBPhaseEntry, AWGBDutyCycleEntry
    global AWGALength, AWGBLength, RevDate, phasealab, phaseblab, AWGAModeLabel, AWGBModeLabel
    global AWGAIOMode, AWGBIOMode, duty1lab, duty2lab, awgaph, awgadel, awgbph, awgbdel
    global AwgLayout, AWG_Amp_Mode # 0 = Min/Max mode, 1 = Amp/Offset
    global amp1lab, amp2lab, off1lab, off2lab, Reset_Freq
    
    if AWGScreenStatus.get() == 0:
        AWGScreenStatus.set(1)
        
        awgwindow = Toplevel()
        awgwindow.title("AWG 1.2 " + RevDate)
        awgwindow.resizable(FALSE,FALSE)
        awgwindow.geometry('+0+100')
        awgwindow.protocol("WM_DELETE_WINDOW", DestroyAWGScreen)
        #
        frame2 = LabelFrame(awgwindow, text="AWG CH A", style="A10R1.TLabelframe")
        frame3 = LabelFrame(awgwindow, text="AWG CH B", style="A10R2.TLabelframe")
        #
        if AwgLayout == "Horz":
            frame2.pack(side=LEFT, expand=1, fill=X)
            frame3.pack(side=LEFT, expand=1, fill=X)
        else:
            frame2.pack(side=TOP, expand=1, fill=Y)
            frame3.pack(side=TOP, expand=1, fill=Y)
        # now AWG A
        # AWG enable sub frame
        AWGAMode = IntVar(0)   # AWG A mode variable
        AWGAIOMode = IntVar(0)   # AWG A Split I/O mode variable
        AWGATerm = IntVar(0)   # AWG A termination variable
        AWGAShape = IntVar(0)  # AWG A Wave shape variable
        AWGARepeatFlag = IntVar(0) # AWG A Arb shape repeat flag
        AWGAMode.set(2)
        awg1eb = Frame( frame2 )
        awg1eb.pack(side=TOP)
        ModeAMenu = Menubutton(awg1eb, text="Mode", style="W5.TButton")
        ModeAMenu.menu = Menu(ModeAMenu, tearoff = 0 )
        ModeAMenu["menu"] = ModeAMenu.menu
        ModeAMenu.menu.add_command(label="-Mode-", command=donothing)
        ModeAMenu.menu.add_radiobutton(label="SVMI", variable=AWGAMode, value=0, command=BAWGAModeLabel)
        ModeAMenu.menu.add_radiobutton(label="SIMV", variable=AWGAMode, value=1, command=BAWGAModeLabel)
        ModeAMenu.menu.add_radiobutton(label="Hi-Z", variable=AWGAMode, value=2, command=BAWGAModeLabel)
        ModeAMenu.menu.add_checkbutton(label="Split I/O", variable=AWGAIOMode, command=BAWGAModeLabel)
        ModeAMenu.menu.add_separator()
        ModeAMenu.menu.add_command(label="-Term-", command=donothing)
        ModeAMenu.menu.add_radiobutton(label="Open", variable=AWGATerm, value=0)
        ModeAMenu.menu.add_radiobutton(label="To GND", variable=AWGATerm, value=1)
        ModeAMenu.menu.add_radiobutton(label="To 2.5V", variable=AWGATerm, value=2)
        ModeAMenu.pack(side=LEFT, anchor=W)
        ShapeAMenu = Menubutton(awg1eb, text="Shape", style="W5.TButton")
        ShapeAMenu.menu = Menu(ShapeAMenu, tearoff = 0 )
        ShapeAMenu["menu"] = ShapeAMenu.menu
        ShapeAMenu.menu.add_radiobutton(label="DC", variable=AWGAShape, value=0, command=UpdateAwgCont)
        ShapeAMenu.menu.add_radiobutton(label="Sine", variable=AWGAShape, value=18, command=AWGAMakeBodeSine)# command=UpdateAwgCont)
        ShapeAMenu.menu.add_radiobutton(label="Triangle", variable=AWGAShape, value=2, command=UpdateAwgCont)
        ShapeAMenu.menu.add_radiobutton(label="Sawtooth", variable=AWGAShape, value=3, command=UpdateAwgCont)
        ShapeAMenu.menu.add_radiobutton(label="Square", variable=AWGAShape, value=4, command=UpdateAwgCont)
        ShapeAMenu.menu.add_radiobutton(label="StairStep", variable=AWGAShape, value=5, command=UpdateAwgCont)
        ShapeAMenu.menu.add_separator()
        ShapeAMenu.menu.add_radiobutton(label="Impulse", variable=AWGAShape, value=9, command=AWGAMakeImpulse)
        ShapeAMenu.menu.add_radiobutton(label="Trapezoid", variable=AWGAShape, value=11, command=AWGAMakeTrapazoid)
        ShapeAMenu.menu.add_radiobutton(label="Ramp", variable=AWGAShape, value=16, command=AWGAMakeRamp)
        ShapeAMenu.menu.add_radiobutton(label="SSQ Pulse", variable=AWGAShape, value=15, command=AWGAMakeSSQ)
        ShapeAMenu.menu.add_radiobutton(label="U-D Ramp", variable=AWGAShape, value=12, command=AWGAMakeUpDownRamp)
        ShapeAMenu.menu.add_radiobutton(label="Fourier Series", variable=AWGAShape, value=14, command=AWGAMakeFourier)
        ShapeAMenu.menu.add_radiobutton(label="PWM Sine", variable=AWGAShape, value=17, command=AWGAMakePWMSine)
        # ShapeAMenu.menu.add_radiobutton(label="Bode Sine", variable=AWGAShape, value=18, command=AWGAMakeBodeSine)
        ShapeAMenu.menu.add_radiobutton(label="UU Noise", variable=AWGAShape, value=7, command=AWGAMakeUUNoise)
        ShapeAMenu.menu.add_radiobutton(label="UG Noise", variable=AWGAShape, value=8, command=AWGAMakeUGNoise)
        ShapeAMenu.menu.add_radiobutton(label="Math", variable=AWGAShape, value=10, command=AWGAMakeMath)
        ShapeAMenu.menu.add_radiobutton(label="Read CSV File", variable=AWGAShape, value=6, command=AWGAReadFile)
        ShapeAMenu.menu.add_radiobutton(label="Read WAV File", variable=AWGAShape, value=13, command=AWGAReadWAV)
        ShapeAMenu.menu.add_command(label="Save CSV File", command=AWGAWriteFile)
        ShapeAMenu.menu.add_checkbutton(label='Repeat', variable=AWGARepeatFlag)
        ShapeAMenu.pack(side=LEFT, anchor=W)
        #
        AWGAModeLabel = Label(frame2, text="AWG A Mode")
        AWGAModeLabel.pack(side=TOP)
        #
        awg1ampl = Frame( frame2 )
        awg1ampl.pack(side=TOP)
        AWGAAmplEntry = Entry(awg1ampl, width=5)
        AWGAAmplEntry.bind("<Return>", UpdateAwgContRet)
        AWGAAmplEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAAmplEntry.bind('<Key>', onTextKeyAWG)
        AWGAAmplEntry.pack(side=LEFT, anchor=W)
        AWGAAmplEntry.delete(0,"end")
        AWGAAmplEntry.insert(0,0.0)
        amp1lab = Label(awg1ampl) #, text="Min Ch A")
        amp1lab.pack(side=LEFT, anchor=W)
        #
        awg1off = Frame( frame2 )
        awg1off.pack(side=TOP)
        AWGAOffsetEntry = Entry(awg1off, width=5)
        AWGAOffsetEntry.bind("<Return>", UpdateAwgContRet)
        AWGAOffsetEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAOffsetEntry.bind('<Key>', onTextKeyAWG)
        AWGAOffsetEntry.pack(side=LEFT, anchor=W)
        AWGAOffsetEntry.delete(0,"end")
        AWGAOffsetEntry.insert(0,0.0)
        off1lab = Label(awg1off) #, text="Max Ch A")
        off1lab.pack(side=LEFT, anchor=W)
        if AWG_Amp_Mode.get() == 0:
            amp1lab.config(text = "Min Ch A" ) # change displayed value
            off1lab.config(text = "Max Ch A" ) # change displayed value
        else:
            amp1lab.config(text = "Amp Ch A" )
            off1lab.config(text = "Off Ch A" )
        # AWG Frequency sub frame
        awg1freq = Frame( frame2 )
        awg1freq.pack(side=TOP)
        AWGAFreqEntry = Entry(awg1freq, width=7)
        AWGAFreqEntry.bind("<Return>", UpdateAwgContRet)
        AWGAFreqEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAFreqEntry.bind('<Key>', onTextKeyAWG)
        AWGAFreqEntry.pack(side=LEFT, anchor=W)
        AWGAFreqEntry.delete(0,"end")
        AWGAFreqEntry.insert(0,100.0)
        freq1lab = Label(awg1freq, text="Freq Ch A")
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
        AWGAPhaseEntry.bind("<Return>", UpdateAwgContRet)
        AWGAPhaseEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGAPhaseEntry.bind('<Key>', onTextKeyAWG)
        AWGAPhaseEntry.pack(side=LEFT, anchor=W)
        AWGAPhaseEntry.delete(0,"end")
        AWGAPhaseEntry.insert(0,0)
        phasealab = Label(awg1phase, text="Deg")
        phasealab.pack(side=LEFT, anchor=W)
        # AWG duty cycle frame
        awg1dc = Frame( frame2 )
        awg1dc.pack(side=TOP)
        AWGADutyCycleEntry = Entry(awg1dc, width=5)
        AWGADutyCycleEntry.bind("<Return>", UpdateAwgContRet)
        AWGADutyCycleEntry.bind('<MouseWheel>', onAWGAscroll)
        AWGADutyCycleEntry.bind('<Key>', onTextKeyAWG)
        AWGADutyCycleEntry.pack(side=LEFT, anchor=W)
        AWGADutyCycleEntry.delete(0,"end")
        AWGADutyCycleEntry.insert(0,50)
        duty1lab = Label(awg1dc, text="%")
        duty1lab.pack(side=LEFT, anchor=W)
        #
        AWGALength = Label(frame2, text="Length")
        AWGALength.pack(side=TOP)
        #
        AWGSync = IntVar(0) # Sync start both AWG channels
        AWGSync.set(1)
        awgsync = Checkbutton(frame2, text="Sync AWG", variable=AWGSync, command=BAWGSync)
        awgsync.pack(side=TOP)
        # now AWG B
        # AWG enable sub frame
        AWGBMode = IntVar(0)   # AWG B mode variable
        AWGBIOMode = IntVar(0)   # AWG B Split I/O mode variable
        AWGBTerm = IntVar(0)   # AWG B termination variable
        AWGBShape = IntVar(0)  # AWG B Wave shape variable
        AWGBRepeatFlag = IntVar(0) # AWG B Arb shape repeat flag
        AWGBMode.set(2)
        awg2eb = Frame( frame3 )
        awg2eb.pack(side=TOP)
        ModeBMenu = Menubutton(awg2eb, text="Mode", style="W5.TButton")
        ModeBMenu.menu = Menu(ModeBMenu, tearoff = 0 )
        ModeBMenu["menu"] = ModeBMenu.menu
        ModeBMenu.menu.add_command(label="-Mode-", command=donothing)
        ModeBMenu.menu.add_radiobutton(label="SVMI", variable=AWGBMode, value=0, command=BAWGBModeLabel)
        ModeBMenu.menu.add_radiobutton(label="SIMV", variable=AWGBMode, value=1, command=BAWGBModeLabel)
        ModeBMenu.menu.add_radiobutton(label="Hi-Z", variable=AWGBMode, value=2, command=BAWGBModeLabel)
        ModeBMenu.menu.add_checkbutton(label="Split I/O", variable=AWGBIOMode, command=BAWGBModeLabel)
        ModeBMenu.menu.add_separator()
        ModeBMenu.menu.add_command(label="-Term-", command=donothing)
        ModeBMenu.menu.add_radiobutton(label="Open", variable=AWGBTerm, value=0)
        ModeBMenu.menu.add_radiobutton(label="To GND", variable=AWGBTerm, value=1)
        ModeBMenu.menu.add_radiobutton(label="To 2.5V", variable=AWGBTerm, value=2)
        ModeBMenu.pack(side=LEFT, anchor=W)
        ShapeBMenu = Menubutton(awg2eb, text="Shape", style="W5.TButton")
        ShapeBMenu.menu = Menu(ShapeBMenu, tearoff = 0 )
        ShapeBMenu["menu"] = ShapeBMenu.menu
        ShapeBMenu.menu.add_radiobutton(label="DC", variable=AWGBShape, value=0, command=UpdateAwgCont)
        ShapeBMenu.menu.add_radiobutton(label="Sine", variable=AWGBShape, value=18, command=AWGBMakeBodeSine)# command=UpdateAwgCont)
        ShapeBMenu.menu.add_radiobutton(label="Triangle", variable=AWGBShape, value=2, command=UpdateAwgCont)
        ShapeBMenu.menu.add_radiobutton(label="Sawtooth", variable=AWGBShape, value=3, command=UpdateAwgCont)
        ShapeBMenu.menu.add_radiobutton(label="Square", variable=AWGBShape, value=4, command=UpdateAwgCont)
        ShapeBMenu.menu.add_radiobutton(label="StairStep", variable=AWGBShape, value=5, command=UpdateAwgCont)
        ShapeBMenu.menu.add_separator()
        ShapeBMenu.menu.add_radiobutton(label="Impulse", variable=AWGBShape, value=9, command=AWGBMakeImpulse)
        ShapeBMenu.menu.add_radiobutton(label="Trapezoid", variable=AWGBShape, value=11, command=AWGBMakeTrapazoid)
        ShapeBMenu.menu.add_radiobutton(label="Ramp", variable=AWGBShape, value=16, command=AWGBMakeRamp)
        ShapeBMenu.menu.add_radiobutton(label="SSQ Pulse", variable=AWGBShape, value=15, command=AWGBMakeSSQ)
        ShapeBMenu.menu.add_radiobutton(label="U-D Ramp", variable=AWGBShape, value=12, command=AWGBMakeUpDownRamp)
        ShapeBMenu.menu.add_radiobutton(label="Fourier Series", variable=AWGBShape, value=14, command=AWGBMakeFourier)
        ShapeBMenu.menu.add_radiobutton(label="PWM Sine", variable=AWGBShape, value=17, command=AWGBMakePWMSine)
        ShapeBMenu.menu.add_radiobutton(label="UU Noise", variable=AWGBShape, value=7, command=AWGBMakeUUNoise)
        ShapeBMenu.menu.add_radiobutton(label="UG Noise", variable=AWGBShape, value=8, command=AWGBMakeUGNoise)
        ShapeBMenu.menu.add_radiobutton(label="Math", variable=AWGBShape, value=10, command=AWGBMakeMath)
        ShapeBMenu.menu.add_radiobutton(label="Read CSV File", variable=AWGBShape, value=6, command=AWGBReadFile)
        ShapeBMenu.menu.add_radiobutton(label="Read WAV File", variable=AWGBShape, value=13, command=AWGBReadWAV)
        ShapeBMenu.menu.add_command(label="Save CSV File", command=AWGBWriteFile)
        ShapeBMenu.menu.add_checkbutton(label='Repeat', variable=AWGBRepeatFlag)
        ShapeBMenu.pack(side=LEFT, anchor=W)
        #
        AWGBModeLabel = Label(frame3, text="AWG A Mode")
        AWGBModeLabel.pack(side=TOP)
        #
        awg2ampl = Frame( frame3 )
        awg2ampl.pack(side=TOP)
        AWGBAmplEntry = Entry(awg2ampl, width=5)
        AWGBAmplEntry.bind("<Return>", UpdateAwgContRet)
        AWGBAmplEntry.bind('<MouseWheel>', onAWGBscroll) # 
        AWGBAmplEntry.bind('<Key>', onTextKeyAWG)
        AWGBAmplEntry.pack(side=LEFT, anchor=W)
        AWGBAmplEntry.delete(0,"end")
        AWGBAmplEntry.insert(0,0.0)
        amp2lab = Label(awg2ampl) #, text="Min Ch B")
        amp2lab.pack(side=LEFT, anchor=W)
        #
        awg2off = Frame( frame3 )
        awg2off.pack(side=TOP)
        AWGBOffsetEntry = Entry(awg2off, width=5)
        AWGBOffsetEntry.bind("<Return>", UpdateAwgContRet)
        AWGBOffsetEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBOffsetEntry.bind('<Key>', onTextKeyAWG)
        AWGBOffsetEntry.pack(side=LEFT, anchor=W)
        AWGBOffsetEntry.delete(0,"end")
        AWGBOffsetEntry.insert(0,0.0)
        off2lab = Label(awg2off) #, text="Max Ch B")
        off2lab.pack(side=LEFT, anchor=W)
        if AWG_Amp_Mode.get() == 0:
            amp2lab.config(text = "Min Ch B" ) # change displayed value
            off2lab.config(text = "Max Ch B" ) # change displayed value
        else:
            amp2lab.config(text = "Amp Ch B" )
            off2lab.config(text = "Off Ch B" )
        # AWG Frequency sub frame
        awg2freq = Frame( frame3 )
        awg2freq.pack(side=TOP)
        AWGBFreqEntry = Entry(awg2freq, width=7)
        AWGBFreqEntry.bind("<Return>", UpdateAwgContRet)
        AWGBFreqEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBFreqEntry.bind('<Key>', onTextKeyAWG)
        AWGBFreqEntry.pack(side=LEFT, anchor=W)
        AWGBFreqEntry.delete(0,"end")
        AWGBFreqEntry.insert(0,100.0)
        freq2lab = Label(awg2freq, text="Freq Ch B")
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
        AWGBPhaseEntry.bind("<Return>", UpdateAwgContRet)
        AWGBPhaseEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBPhaseEntry.bind('<Key>', onTextKeyAWG)
        AWGBPhaseEntry.pack(side=LEFT, anchor=W)
        AWGBPhaseEntry.delete(0,"end")
        AWGBPhaseEntry.insert(0,0)
        phaseblab = Label(awg2phase, text="Deg")
        phaseblab.pack(side=LEFT, anchor=W)
        # AWG duty cycle frame
        awg2dc = Frame( frame3 )
        awg2dc.pack(side=TOP)
        AWGBDutyCycleEntry = Entry(awg2dc, width=5)
        AWGBDutyCycleEntry.bind("<Return>", UpdateAwgContRet)
        AWGBDutyCycleEntry.bind('<MouseWheel>', onAWGBscroll)
        AWGBDutyCycleEntry.bind('<Key>', onTextKeyAWG)
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
    
    # AWGScreenStatus.set(0)
    awgwindow.iconify()
# ===== Channel B Mux Mode sub Window =======
def MakeMuxModeWindow():
    global MuxScreenStatus, muxwindow, RevDate, DacScreenStatus, DigScreenStatus
    global CHB_Asb, CHB_APosEntry, CHB_Bsb, CHB_BPosEntry
    global CHB_Csb, CHB_CPosEntry, CHB_Dsb, CHB_DPosEntry, SyncButton
    global CHB_Alab, CHB_Blab, CHB_Clab, CHB_Dlab, CHBlab, CHBofflab
    global CHB_Cofflab, CHB_Dofflab
    global Show_CBA, Show_CBB, Show_CBC, Show_CBD, MuxEnb, MuxSync, hipulseimg, lowpulseimg, DualMuxMode
    
    if MuxScreenStatus.get() == 0 and DacScreenStatus.get() == 0 and DigScreenStatus.get() == 0:
        MuxScreenStatus.set(1)
        #
        AWGSync.set(1) # force discontinuous mode
        BAWGEnab() # update AWG settings
        #
        muxwindow = Toplevel()
        muxwindow.title("CH-B Mux 1.2 " + RevDate)
        muxwindow.resizable(FALSE,FALSE)
        muxwindow.protocol("WM_DELETE_WINDOW", DestroyMuxScreen)
        #
        frameM = LabelFrame(muxwindow, text="CH B Mux", style="A10B.TLabel") #, font="Arial 10 bold", borderwidth=5, relief=RIDGE)
        frameM.pack(side=LEFT, expand=1, fill=Y)
        #
        # Voltage channel CHB-A
        frameA = Frame(frameM)
        frameA.pack(side=TOP)
        cba = Checkbutton(frameA, text='CB-A', variable=Show_CBA, command=UpdateTimeTrace)
        cba.pack(side=LEFT, anchor=W)
        CHB_Asb = Spinbox(frameA, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Asb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Asb.pack(side=LEFT)
        CHB_Asb.delete(0,"end")
        CHB_Asb.insert(0,0.5)
        #
        CHB_Alab = Button(frameA, text="CB-A V/Div", style="Rtrace2.TButton", command=SetScaleMuxA)
        CHB_Alab.pack(side=LEFT)
        CHB_APosEntry = Entry(frameA, width=5)
        CHB_APosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_APosEntry.bind('<Key>', onTextKey)
        CHB_APosEntry.pack(side=LEFT)
        CHB_APosEntry.delete(0,"end")
        CHB_APosEntry.insert(0,2.5)
        CHB_Aofflab = Button(frameA, text="CB-A Pos", style="Rtrace2.TButton", command=SetMuxAPoss)
        CHB_Aofflab.pack(side=LEFT)
        # Voltage channel CHB-B
        frameB = Frame(frameM)
        frameB.pack(side=TOP)
        cbb = Checkbutton(frameB, text='CB-B', variable=Show_CBB, command=UpdateTimeTrace)
        cbb.pack(side=LEFT, anchor=W)
        CHB_Bsb = Spinbox(frameB, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Bsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Bsb.pack(side=LEFT)
        CHB_Bsb.delete(0,"end")
        CHB_Bsb.insert(0,0.5)
        CHB_Blab = Button(frameB, text="CB-B V/Div", style="Rtrace6.TButton", command=SetScaleMuxB)
        CHB_Blab.pack(side=LEFT)
        CHB_BPosEntry = Entry(frameB, width=5)
        CHB_BPosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_BPosEntry.bind('<Key>', onTextKey)
        CHB_BPosEntry.pack(side=LEFT)
        CHB_BPosEntry.delete(0,"end")
        CHB_BPosEntry.insert(0,2.5)
        CHB_Bofflab = Button(frameB, text="CB-B Pos", style="Rtrace6.TButton", command=SetMuxBPoss)
        CHB_Bofflab.pack(side=LEFT)
        # Voltage channel B-C
        frameC = Frame(frameM)
        frameC.pack(side=TOP)
        cbc = Checkbutton(frameC, text='CB-C', variable=Show_CBC, command=UpdateTimeTrace)
        cbc.pack(side=LEFT, anchor=W)
        CHB_Csb = Spinbox(frameC, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Csb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Csb.pack(side=LEFT)
        CHB_Csb.delete(0,"end")
        CHB_Csb.insert(0,0.5)
        # 
        CHB_Clab = Button(frameC, text="CB-C V/Div", style="Rtrace7.TButton", command=SetScaleMuxC)
        CHB_Clab.pack(side=LEFT)
        CHB_CPosEntry = Entry(frameC, width=5)
        CHB_CPosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_CPosEntry.bind('<Key>', onTextKey)
        CHB_CPosEntry.pack(side=LEFT)
        CHB_CPosEntry.delete(0,"end")
        CHB_CPosEntry.insert(0,2.5)
        CHB_Cofflab = Button(frameC, text="CB-C Pos", style="Rtrace7.TButton", command=SetMuxCPoss)
        CHB_Cofflab.pack(side=LEFT)
        # Voltage channel B-D
        frameD = Frame(frameM)
        frameD.pack(side=TOP)
        cbd = Checkbutton(frameD, text='CB-D', variable=Show_CBD, command=UpdateTimeTrace)
        cbd.pack(side=LEFT, anchor=W)
        CHB_Dsb = Spinbox(frameD, width=4, values=CHvpdiv, command=UpdateTimeTrace)
        CHB_Dsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHB_Dsb.pack(side=LEFT)
        CHB_Dsb.delete(0,"end")
        CHB_Dsb.insert(0,0.5)
        CHB_Dlab = Button(frameD, text="CB-D V/Div", style="Rtrace4.TButton", command=SetScaleMuxD)
        CHB_Dlab.pack(side=LEFT)
        CHB_DPosEntry = Entry(frameD, width=5)
        CHB_DPosEntry.bind('<MouseWheel>', onTextScroll)
        CHB_DPosEntry.bind('<Key>', onTextKey)
        CHB_DPosEntry.pack(side=LEFT)
        CHB_DPosEntry.delete(0,"end")
        CHB_DPosEntry.insert(0,2.5)
        CHB_Dofflab = Button(frameD, text="CB-D Pos", style="Rtrace4.TButton", command=SetMuxDPoss)
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
        frameF = Frame(frameM)
        frameF.pack(side=TOP)
        dmx = Checkbutton(frameF, text='Dual Mux Split I/O mode', variable=DualMuxMode, command=SetDualMuxMode)
        dmx.pack(side=LEFT)
        # Gray out main Channel B controls
        CHBlab.config(style="SGray.TButton")
        CHBofflab.config(style="SGray.TButton")
#
def SetDualMuxMode():
    global AWGAIOMode, AWGBIOMode, ShowC1_V, DualMuxMode, CHAlab, CHAofflab
    global CHB_Clab, CHB_Dlab, CHB_Cofflab, CHB_Dofflab

    if DualMuxMode.get() == 1:
        AWGAIOMode.set(1) # force awg A split I/O mode
        AWGBIOMode.set(1) # force awg A split I/O mode
        ShowC1_V.set(0) # force A voltage trace off
        CHB_Clab.config(text="CA-C V/Div")
        CHB_Dlab.config(text="CA-D V/Div")
        CHB_Cofflab.config(text="CA-C Pos")
        CHB_Dofflab.config(text="CA-D Pos")
        BAWGEnab() # update AWG settings
        # Gray out main Channel A controls
        CHAlab.config(style="SGray.TButton")
        CHAofflab.config(style="SGray.TButton")
    else:
        ShowC1_V.set(1) # force A voltage trace on
        CHB_Clab.config(text="CB-C V/Div")
        CHB_Dlab.config(text="CB-D V/Div")
        CHB_Cofflab.config(text="CB-C Pos")
        CHB_Dofflab.config(text="CB-D Pos")
        # Reset main Channel A control colors
        CHAlab.config(style="Rtrace1.TButton")
        CHAofflab.config(style="Rtrace1.TButton")
#
def SyncImage():
    global MuxSync, hipulseimg, lowpulseimg, SyncButton

    if MuxSync.get() == 0:
        SyncButton.config(image=hipulseimg)
    else:
        SyncButton.config(image=lowpulseimg)
        
def DestroyMuxScreen():
    global muxwindow, MuxScreenStatus, CHAlab, CHAofflab, CHBlab, CHBofflab
    
    MuxScreenStatus.set(0)
    # Reset main Channel B control colors
    CHBlab.config(style="Rtrace2.TButton")
    CHBofflab.config(style="Rtrace2.TButton")
    CHAlab.config(style="Rtrace1.TButton")
    CHAofflab.config(style="Rtrace1.TButton")
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
    global FStepSync, DevOne

    if FStepSync.get() == 0:
        Tval = devx.ctrl_transfer( 0xc0, 0x91, 0, 0, 0, 1, 100) # set PIO-0 to Z
    elif FStepSync.get() == 1:
        devx.ctrl_transfer( 0x40, 0x50, 0, 0, 0, 0, 100) # set PIO-0 to 0
    elif FStepSync.get() == 2:
        devx.ctrl_transfer( 0x40, 0x51, 0, 0, 0, 0, 100)  # set PIO-0 to 1
#
def BSweepSync():
    global FSweepSync, DevOne

    if FSweepSync.get() == 0:
        Tval = devx.ctrl_transfer( 0xc0, 0x91, 1, 0, 0, 1, 100) # set PIO-1 to Z
    elif FSweepSync.get() == 1:
        devx.ctrl_transfer( 0x40, 0x50, 1, 0, 0, 0, 100) # set PIO-1 to 0
    elif FSweepSync.get() == 2:
        devx.ctrl_transfer( 0x40, 0x51, 1, 0, 0, 0, 100)  # set PIO-1 to 1
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
            s = askstring("Normalize Max Amplitude", "Max Amplitude = " + str(MaxAmpl) + "\n\n Enter New Max value:\n in dB")
            if (s == None):         # If Cancel pressed, then None
                return()
            try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
                v = int(s)
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
    global ShowCA_VdB, ShowCA_P, ShowCB_VdB, ShowCB_P, ShowMarkerBP, BodeDisp, RelPhaseCenter
    global ShowCA_RdB, ShowCA_RP, ShowCB_RdB, ShowCB_RP, ShowMathBP, ShowRMathBP, PhCenBodeEntry
    global BPSweepMode, BPSweepCont, Bodeca, BodeScreenStatus, RevDate, SweepStepBodeEntry
    global HScaleBP, StopBodeEntry, StartBodeEntry, ShowBPCur, ShowBdBCur, BPCursor, BdBCursor
    global GRWBP, GRHBP, X0LBP, FStepSync, FSweepSync, BDSweepFile, MinigenScreenStatus
    
    if BodeScreenStatus.get() == 0:
        BodeScreenStatus.set(1)
        BodeDisp.set(1)
        BodeCheckBox()
        CANVASwidthBP = GRWBP + 2 * X0LBP    # The Bode canvas width
        CANVASheightBP = GRHBP + 80         # The ode canvas height
        CutDC.set(1) # set to remove DC
        AWGAMode.set(0) # Set AWG A to SVMI
        AWGAShape.set(1) # Set Shape to Sine
        AWGBMode.set(2) # Set AWG B to Hi-Z
        bodewindow = Toplevel()
        bodewindow.title("Bode Plotter 1.2 " + RevDate)
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
        Bodeca.bind("<space>", onCanvasSpaceBar)
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
        FFTwindmenu = Menubutton(frame2bp, text="FFTwindow", style="W11.TButton")
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
        FFTwindmenu.pack(side=TOP)
        # Show channels menu
        Showmenu = Menubutton(frame2bp, text="Curves", style="W7.TButton")
        Showmenu.menu = Menu(Showmenu, tearoff = 0 )
        Showmenu["menu"] = Showmenu.menu
        Showmenu.menu.add_command(label="-Show-", command=donothing)
        Showmenu.menu.add_command(label="All", command=BShowCurvesAllBP)
        Showmenu.menu.add_command(label="None", command=BShowCurvesNoneBP)
        Showmenu.menu.add_checkbutton(label='CA-dBV   [1]', variable=ShowCA_VdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='CB-dBV   [2]', variable=ShowCB_VdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Phase A-B [3]', variable=ShowCA_P, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Phase B-A [4]', variable=ShowCB_P, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Marker   [5]', variable=ShowMarkerBP, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Freq Cursor', variable=ShowBPCur)
        Showmenu.menu.add_checkbutton(label='dB Cursor', variable=ShowBdBCur)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='Cursor Off', variable=ShowBdBCur, value=0)
        Showmenu.menu.add_radiobutton(label='dB Cursor [d]', variable=ShowBdBCur, value=1)
        Showmenu.menu.add_radiobutton(label='Phase Cursor [h]', variable=ShowBdBCur, value=2)
        Showmenu.menu.add_checkbutton(label='Freq Cursor [f]', variable=ShowBPCur)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='None [0]', variable=ShowMathBP, value=0, command=UpdateBodeAll)
        Showmenu.menu.add_radiobutton(label='CA-dB - CB-dB [9]', variable=ShowMathBP, value=1, command=UpdateBodeAll)
        Showmenu.menu.add_radiobutton(label='CB-dB - CA-dB [8]', variable=ShowMathBP, value=2, command=UpdateBodeAll)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_checkbutton(label='RA-dBV [6]', variable=ShowCA_RdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='RB-dBV [7]', variable=ShowCB_RdB, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='RPhase A-B', variable=ShowCA_RP, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='RPhase B-A', variable=ShowCB_RP, command=UpdateBodeAll)
        Showmenu.menu.add_checkbutton(label='Math', variable=ShowRMathBP, command=UpdateBodeAll)
        Showmenu.pack(side=TOP)
        # Horz Scale        
        HScaleBP = IntVar(0)
        HScaleBP.set(1)
        HzScale = Frame( frame2bp )
        HzScale.pack(side=TOP)
        rb1 = Radiobutton(HzScale, text="Lin F", variable=HScaleBP, value=0, command=UpdateBodeTrace )
        rb1.pack(side=LEFT)
        rb2 = Radiobutton(HzScale, text="Log F", variable=HScaleBP, value=1, command=UpdateBodeTrace )
        rb2.pack(side=LEFT)
        
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

        PhaseCenter = Frame( frame2bp )
        PhaseCenter.pack(side=TOP)
        PhCenlab = Label(PhaseCenter, text="Center Phase on")
        PhCenlab.pack(side=LEFT)
        PhCenBodeEntry = Entry(PhaseCenter, width=5)
        PhCenBodeEntry.bind('<MouseWheel>', onTextScroll)
        PhCenBodeEntry.bind('<Key>', onTextKey)
        PhCenBodeEntry.pack(side=LEFT)
        PhCenBodeEntry.delete(0,"end")
        PhCenBodeEntry.insert(0,RelPhaseCenter.get())
        # sweep generator mode menu buttons
        FSweepmenu = Label(frame2bp, text="-Sweep Gen-", style="A10B.TLabel")
        FSweepmenu.pack(side=TOP)
        
        Frange1 = Frame( frame2bp )
        Frange1.pack(side=TOP)
        startfreqlab = Label(Frange1, text="Startfreq")
        startfreqlab.pack(side=LEFT)
        StartBodeEntry = Entry(Frange1, width=5)
        StartBodeEntry.bind('<MouseWheel>', onTextScroll)
        StartBodeEntry.bind('<Key>', onTextKey)
        StartBodeEntry.pack(side=LEFT)
        StartBodeEntry.delete(0,"end")
        StartBodeEntry.insert(0,10)

        Frange2 = Frame( frame2bp )
        Frange2.pack(side=TOP)
        stopfreqlab = Label(Frange2, text="Stopfreq")
        stopfreqlab.pack(side=LEFT)
        StopBodeEntry = Entry(Frange2, width=5)
        StopBodeEntry.bind('<MouseWheel>', onTextScroll)
        StopBodeEntry.bind('<Key>', onTextKey)
        StopBodeEntry.pack(side=LEFT)
        StopBodeEntry.delete(0,"end")
        StopBodeEntry.insert(0,10000)
        
        sgrb1 = Radiobutton(frame2bp, text='None', variable=FSweepMode, value=0)
        sgrb1.pack(side=TOP)
        Frange4 = Frame( frame2bp )
        Frange4.pack(side=TOP)
        sgrb2 = Radiobutton(Frange4, text='CH-A', variable=FSweepMode, value=1)
        sgrb2.pack(side=LEFT)
        sgrb3 = Radiobutton(Frange4, text='CH-B', variable=FSweepMode, value=2)
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
        
        ADI2 = Label(frame2bp, image=logo, anchor= "sw", compound="top") #, height=49, width=116
        ADI2.pack(side=TOP)
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
#
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
    global ShowRA_VdB, ShowRA_P, ShowRB_VdB, ShowRB_P, ShowMathSA
    global ShowRMath, FSweepMode, FSweepCont, Freqca, SpectrumScreenStatus, RevDate
    global HScale, StopFreqEntry, StartFreqEntry, ShowFCur, ShowdBCur, FCursor, dBCursor
    global CANVASwidthF, GRWF, X0LF, CANVASheightF, GRHF, PhCenFreqEntry, RelPhaseCenter
    
    if SpectrumScreenStatus.get() == 0:
        SpectrumScreenStatus.set(1)
        FreqDisp.set(1)
        FreqCheckBox()
        CANVASwidthF = GRWF + 2 * X0LF     # The spectrum canvas width
        CANVASheightF = GRHF + 80         # The spectrum canvas height
        freqwindow = Toplevel()
        freqwindow.title("Spectrum Analyzer 1.2 " + RevDate)
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
        Freqca.bind("<space>", onCanvasSpaceBar)
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
        Modemenu.menu.add_command(label="Average     [a]", command=BAveragemode)
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
        #
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
        Showmenu.menu.add_checkbutton(label='CA-dBV   [1]', variable=ShowC1_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='CB-dBV   [2]', variable=ShowC2_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='Phase A-B [3]', variable=ShowC1_P, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='Phase B-A [4]', variable=ShowC2_P, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='Markers  Off', variable=ShowMarker, value=0, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='Markers  [5]', variable=ShowMarker, value=1, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='Delta Markers', variable=ShowMarker, value=2, command=UpdateFreqAll)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='Cursor Off', variable=ShowdBCur, value=0)
        Showmenu.menu.add_radiobutton(label='dB Cursor   [d]', variable=ShowdBCur, value=1)
        Showmenu.menu.add_radiobutton(label='Phase Cursor [h]', variable=ShowdBCur, value=2)
        Showmenu.menu.add_checkbutton(label='Freq Cursor [f]', variable=ShowFCur)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_radiobutton(label='None  [0]', variable=ShowMathSA, value=0, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='CA-dB - CB-dB [9]', variable=ShowMathSA, value=1, command=UpdateFreqAll)
        Showmenu.menu.add_radiobutton(label='CB-dB - CA-dB [8]', variable=ShowMathSA, value=2, command=UpdateFreqAll)
        Showmenu.menu.add_separator()
        Showmenu.menu.add_checkbutton(label='RA-dBV  [6]', variable=ShowRA_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='RB-dBV  [7]', variable=ShowRB_VdB, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='RPhase A-B', variable=ShowRA_P, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='RPhase B-A', variable=ShowRB_P, command=UpdateFreqAll)
        Showmenu.menu.add_checkbutton(label='Math', variable=ShowRMath, command=UpdateFreqAll)
        Showmenu.pack(side=TOP)
        # HScale
        Frange1 = Frame( frame2fr )
        Frange1.pack(side=TOP)
        startfreqlab = Label(Frange1, text="Startfreq")
        startfreqlab.pack(side=LEFT)
        StartFreqEntry = Entry(Frange1, width=5)
        StartFreqEntry.bind('<MouseWheel>', onTextScroll)
        StartFreqEntry.bind('<Key>', onTextKey)
        StartFreqEntry.pack(side=LEFT)
        StartFreqEntry.delete(0,"end")
        StartFreqEntry.insert(0,10)

        Frange2 = Frame( frame2fr )
        Frange2.pack(side=TOP)
        stopfreqlab = Label(Frange2, text="Stopfreq")
        stopfreqlab.pack(side=LEFT)
        StopFreqEntry = Entry(Frange2, width=5)
        StopFreqEntry.bind('<MouseWheel>', onTextScroll)
        StopFreqEntry.bind('<Key>', onTextKey)
        StopFreqEntry.pack(side=LEFT)
        StopFreqEntry.delete(0,"end")
        StopFreqEntry.insert(0,10000)
        
        HScale = IntVar(0)
        HzScale = Frame( frame2fr )
        HzScale.pack(side=TOP)
        rb1 = Radiobutton(HzScale, text="Lin F", variable=HScale, value=0, command=UpdateFreqTrace )
        rb1.pack(side=LEFT)
        rb2 = Radiobutton(HzScale, text="Log F", variable=HScale, value=1, command=UpdateFreqTrace )
        rb2.pack(side=LEFT)
        #
        PhaseCenter = Frame( frame2fr )
        PhaseCenter.pack(side=TOP)
        PhCenlab = Label(PhaseCenter, text="Center Phase on")
        PhCenlab.pack(side=LEFT)
        PhCenFreqEntry = Entry(PhaseCenter, width=5)
        PhCenFreqEntry.bind('<MouseWheel>', onTextScroll)
        PhCenFreqEntry.bind('<Key>', onTextKey)
        PhCenFreqEntry.pack(side=LEFT)
        PhCenFreqEntry.delete(0,"end")
        PhCenFreqEntry.insert(0,RelPhaseCenter.get())
        #
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
        
        ADI2 = Label(frame2fr, image=logo, anchor= "sw", compound="top") #, height=49, width=116
        ADI2.pack(side=TOP)
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
    global logo, CANVASwidthXY, CANVASheightXY, Xsignal, Ysignal, ShowRXY
    global XYScreenStatus, MarkerXYScale, XYca, xywindow, RevDate, XYDisp
    global CHAsbxy, CHBsbxy, CHAxylab, CHBxylab, CHAVPosEntryxy, CHBVPosEntryxy
    global CHAIsbxy, CHBIsbxy, CHAIPosEntryxy, CHBIPosEntryxy, ScreenXYrefresh
    global YminXY, Y0TXY, YmaxXY, GRHXY, XminXY, X0LXY, XmaxXY, X0LXY, GRWXY, CANVASwidthXY, CANVASheightXY
    
    if XYScreenStatus.get() == 0:
        XYScreenStatus.set(1)
        XYDisp.set(1)
        XYCheckBox()
        YminXY = Y0TXY                  # Minimum position of XY grid (top)
        YmaxXY = Y0TXY + GRHXY            # Maximum position of XY grid (bottom)
        XminXY = X0LXY                  # Minimum position of XY grid (left)
        XmaxXY = X0LXY + GRWXY            # Maximum position of XY grid (right)
        CANVASwidthXY = GRWXY + 18 + X0LXY     # The XY canvas width
        CANVASheightXY = GRHXY + 80         # The XY canvas height
        xywindow = Toplevel()
        xywindow.title("X-Y Plot 1.2 " + RevDate)
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
        XYca.bind('<MouseWheel>', onCanvasXYScrollClick)
        XYca.bind("<Up>", onCanvasUpArrow)
        XYca.bind("<Down>", onCanvasDownArrow)
        XYca.bind("<Left>", onCanvasLeftArrow)
        XYca.bind("<Right>", onCanvasRightArrow)
        XYca.bind("<space>", onCanvasSpaceBar)
        XYca.bind("a", onCanvasAverage)
        XYca.pack(side=TOP, fill=BOTH, expand=YES)
        #
        RUNframe = Frame( frame2xyr )
        RUNframe.pack(side=TOP)
        sbxy = Button(RUNframe, text="Stop", style="Stop.TButton", command=BStop)
        sbxy.pack(side=LEFT)
        rbxy = Button(RUNframe, text="Run", style="Run.TButton", command=BStart)
        rbxy.pack(side=LEFT)
        # Open Math trace menu
        mathbt = Button(frame2xyr, text="Math", style="W4.TButton", command = NewEnterMathControls)
        mathbt.pack(side=TOP) #, anchor=W)
        # Disply mode menu
        # X - Y mode signal select
        AxisLabX = Label(frame2xyr, text ="-X Axis-", style="A10R1.TLabelframe.Label")
        AxisLabX.pack(side=TOP)
        chaxmenu = Frame( frame2xyr )
        chaxmenu.pack(side=TOP)
        rbx2 = Radiobutton(chaxmenu, text='CA-V', variable=Xsignal, value=1, command=UpdateXYTrace)
        rbx2.pack(side=LEFT, anchor=W)
        rbx3 = Radiobutton(chaxmenu, text='CA-I', variable=Xsignal, value=2, command=UpdateXYTrace)
        rbx3.pack(side=LEFT, anchor=W)
        chbxmenu = Frame( frame2xyr )
        chbxmenu.pack(side=TOP)
        rbx4 = Radiobutton(chbxmenu, text='CB-V', variable=Xsignal, value=3, command=UpdateXYTrace)
        rbx4.pack(side=LEFT, anchor=W)
        rbx5 = Radiobutton(chbxmenu, text='CB-I', variable=Xsignal, value=4, command=UpdateXYTrace)
        rbx5.pack(side=LEFT, anchor=W)
        rbx7 = Radiobutton(frame2xyr, text='Histogram CA-V', variable=Xsignal, value=6, command=BHistAsPercent)
        rbx7.pack(side=TOP)
        rbx8 = Radiobutton(frame2xyr, text='Histogram CB-V', variable=Xsignal, value=7, command=BHistAsPercent)
        rbx8.pack(side=TOP)
        rbx6 = Radiobutton(frame2xyr, text='Math', variable=Xsignal, value=5, command=UpdateXYTrace)
        rbx6.pack(side=TOP)
        #
        AxisLabY = Label(frame2xyr, text ="-Y Axis-", style="A10R2.TLabelframe.Label")
        AxisLabY.pack(side=TOP)
        chaymenu = Frame( frame2xyr )
        chaymenu.pack(side=TOP)
        rby2 = Radiobutton(chaymenu, text='CA-V', variable=Ysignal, value=1, command=UpdateXYTrace)
        rby2.pack(side=LEFT, anchor=W)
        rby3 = Radiobutton(chaymenu, text='CA-I', variable=Ysignal, value=2, command=UpdateXYTrace)
        rby3.pack(side=LEFT, anchor=W)
        chbymenu = Frame( frame2xyr )
        chbymenu.pack(side=TOP)
        rby4 = Radiobutton(chbymenu, text='CB-V', variable=Ysignal, value=3, command=UpdateXYTrace)
        rby4.pack(side=LEFT, anchor=W)
        rby5 = Radiobutton(chbymenu, text='CB-I', variable=Ysignal, value=4, command=UpdateXYTrace)
        rby5.pack(side=LEFT, anchor=W)
        rby6 = Radiobutton(frame2xyr, text='Math', variable=Ysignal, value=5, command=UpdateXYTrace)
        rby6.pack(side=TOP)
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
        snapbutton = Button(frame2xyr, style="W8.TButton", text="SnapShot", command=BSnapShot)
        snapbutton.pack(side=TOP)
        savebutton = Button(frame2xyr, style="W11.TButton", text="Save Screen", command=BSaveScreenXY)
        savebutton.pack(side=TOP)
        dismissxybutton = Button(frame2xyr, style="W7.TButton", text="Dismiss", command=DestroyXYScreen)
        dismissxybutton.pack(side=TOP)
        ADI1xy = Label(frame2xyr, image=logo, anchor= "sw", compound="top") # , height=49, width=116
        ADI1xy.pack(side=TOP)

        # Bottom Buttons
        MarkerXYScale = IntVar(0)
        MarkerXYScale.set(1)
        # Voltage channel A
        CHAsbxy = Spinbox(frame3xy, width=4, values=CHvpdiv)
        CHAsbxy.bind('<MouseWheel>', onSpinBoxScroll)
        CHAsbxy.pack(side=LEFT)
        CHAsbxy.delete(0,"end")
        CHAsbxy.insert(0,0.5)
        CHAxylab = Button(frame3xy, text="CA V/Div", style="Rtrace1.TButton", command=SetXYScaleA)
        CHAxylab.pack(side=LEFT)

        CHAVPosEntryxy = Entry(frame3xy, width=5)
        CHAVPosEntryxy.bind('<MouseWheel>', onTextScroll)
        CHAVPosEntryxy.bind('<Key>', onTextKey)
        CHAVPosEntryxy.pack(side=LEFT)
        CHAVPosEntryxy.delete(0,"end")
        CHAVPosEntryxy.insert(0,2.5)
        CHAofflabxy = Button(frame3xy, text="CA V Pos", style="Rtrace1.TButton", command=SetXYVAPoss)
        CHAofflabxy.pack(side=LEFT)
        # Current channel A
        CHAIsbxy = Spinbox(frame3xy, width=4, values=CHipdiv)
        CHAIsbxy.bind('<MouseWheel>', onSpinBoxScroll)
        CHAIsbxy.pack(side=LEFT)
        CHAIsbxy.delete(0,"end")
        CHAIsbxy.insert(0,50.0)
        CHAIlabxy = Label(frame3xy, text="CA mA/Div", style="Strace3.TButton")
        CHAIlabxy.pack(side=LEFT)

        CHAIPosEntryxy = Entry(frame3xy, width=5)
        CHAIPosEntryxy.bind('<MouseWheel>', onTextScroll)
        CHAIPosEntryxy.bind('<Key>', onTextKey)
        CHAIPosEntryxy.pack(side=LEFT)
        CHAIPosEntryxy.delete(0,"end")
        CHAIPosEntryxy.insert(0,0.0)
        CHAIofflabxy = Button(frame3xy, text="CA I Pos", style="Rtrace3.TButton", command=SetXYIAPoss)
        CHAIofflabxy.pack(side=LEFT)
        # Voltage channel B
        CHBsbxy = Spinbox(frame4xy, width=4, values=CHvpdiv)
        CHBsbxy.bind('<MouseWheel>', onSpinBoxScroll)
        CHBsbxy.pack(side=LEFT)
        CHBsbxy.delete(0,"end")
        CHBsbxy.insert(0,0.5)
        #
        CHBxylab = Button(frame4xy, text="CB V/Div", style="Strace2.TButton", command=SetXYScaleB)
        CHBxylab.pack(side=LEFT)

        CHBVPosEntryxy = Entry(frame4xy, width=5)
        CHBVPosEntryxy.bind('<MouseWheel>', onTextScroll)
        CHBVPosEntryxy.bind('<Key>', onTextKey)
        CHBVPosEntryxy.pack(side=LEFT)
        CHBVPosEntryxy.delete(0,"end")
        CHBVPosEntryxy.insert(0,2.5)
        CHBofflabxy = Button(frame4xy, text="CB V Pos", style="Rtrace2.TButton", command=SetXYVBPoss)
        CHBofflabxy.pack(side=LEFT)
        # Current channel B
        CHBIsbxy = Spinbox(frame4xy, width=4, values=CHipdiv) #
        CHBIsbxy.bind('<MouseWheel>', onSpinBoxScroll)
        CHBIsbxy.pack(side=LEFT)
        CHBIsbxy.delete(0,"end")
        CHBIsbxy.insert(0,50.0)
        CHBIlabxy = Label(frame4xy, text="CB mA/Div", style="Strace4.TButton")
        CHBIlabxy.pack(side=LEFT)

        CHBIPosEntryxy = Entry(frame4xy, width=5)
        CHBIPosEntryxy.bind('<MouseWheel>', onTextScroll)
        CHBIPosEntryxy.bind('<Key>', onTextKey)
        CHBIPosEntryxy.pack(side=LEFT)
        CHBIPosEntryxy.delete(0,"end")
        CHBIPosEntryxy.insert(0,0.0)
        CHBIofflabxy = Button(frame4xy, text="CB I Pos", style="Rtrace4.TButton", command=SetXYIBPoss)
        CHBIofflabxy.pack(side=LEFT)
        #
        if ShowBallonHelp > 0:
            #xb1_tip = CreateToolTip(xb1, 'Enter formula for X axis Math trace')
            #xb2_tip = CreateToolTip(xb2, 'Enter which axis controls to use for X axis Math trace')
            #yb1_tip = CreateToolTip(yb1, 'Enter formula for Y axis Math trace')
            #yb2_tip = CreateToolTip(yb2, 'Enter which axis controls to use for Y axis Math trace')
            math_tip = CreateToolTip(mathbt, 'Open Math window')
            bsxy_tip = CreateToolTip(sbxy, 'Stop acquiring data')
            brxy_tip = CreateToolTip(rbxy, 'Start acquiring data')
            snapbutton_tip = CreateToolTip(snapbutton, 'Take snap shot of current trace')
            savebutton_tip = CreateToolTip(savebutton, 'Save current trace to EPS file')
            dismissxybutton_tip = CreateToolTip(dismissxybutton, 'Diamiss X-Y plot window')
            CHAxylab_tip = CreateToolTip(CHAxylab, 'Select CHA-V vertical range/position axis to be used for markers and drawn color')
            CHBxylab_tip = CreateToolTip(CHBxylab, 'Select CHB-V vertical range/position axis to be used for markers and drawn color')
            CHAxyofflab_tip = CreateToolTip(CHAofflabxy, 'Set CHA-V position to DC average of signal')
            CHBxyofflab_tip = CreateToolTip(CHBofflabxy, 'Set CHB-V position to DC average of signal')
            CHAIxyofflab_tip = CreateToolTip(CHAIofflabxy, 'Set CHA-I position to DC average of signal')
            CHBIxyofflab_tip = CreateToolTip(CHBIofflabxy, 'Set CHB-I position to DC average of signal')

def DestroyXYScreen():
    global xywindow, XYScreenStatus, ca, XYDisp
    
    XYScreenStatus.set(0)
    XYDisp.set(0)
    XYCheckBox()
    xywindow.destroy()
    ca.bind_all('<MouseWheel>', onCanvasClickScroll)
#
# Optional Calibration procedure routine
#
def SelfCalibration():
    global DevID, devx, CHA, CHB, RevDate, OnBoardRes, AD584act, FWRevOne
    global discontloop, contloop, session
    # global OnBoardResAgnd, OnBoardResA25, OnBoardResBgnd, OnBoardResB25
    # setup cal results window
    if FWRevOne < 2.06: # Check firmware revision level > 2.06
        showwarning("WARNING","Out of date Firmware Revision!")
        return
    calwindow = Toplevel()
    calwindow.title("ALM1000 Calibration tool 1.2 " + RevDate)
    # display wigets
    prlab = Label(calwindow, text="Channel Gain / Offset calibration")
    prlab.grid(row=0, column=0, columnspan=2, sticky=W)
    labelA0 = Label(calwindow, style="A12B.TLabel")
    labelA0.grid(row=1, column=0, columnspan=2, sticky=W)
    labelA0.config(text = "CA gnd Volts")
    labelAMax = Label(calwindow, style="A12B.TLabel")
    labelAMax.grid(row=2, column=0, columnspan=2, sticky=W)
    labelAMax.config(text = "CA 584 Volts")
    labelAMin = Label(calwindow, style="A12B.TLabel")
    labelAMin.grid(row=3, column=0, columnspan=2, sticky=W)
    labelAMin.config(text = "CA 5V Src I ")
    labelB0 = Label(calwindow, style="A12B.TLabel")
    labelB0.grid(row=4, column=0, columnspan=2, sticky=W)
    labelB0.config(text = "CA gnd Volts")
    labelBMax = Label(calwindow, style="A12B.TLabel")
    labelBMax.grid(row=5, column=0, columnspan=2, sticky=W)
    labelBMax.config(text = "CB 584 Volts")
    labelBMin = Label(calwindow, style="A12B.TLabel")
    labelBMin.grid(row=6, column=0, columnspan=2, sticky=W)
    labelBMin.config(text = "CB 5V Src I ")
    labelAB = Label(calwindow, style="A12B.TLabel")
    labelAB.grid(row=7, column=0, columnspan=2, sticky=W)
    labelAB.config(text = "CA 0V Src I")
    labelBA = Label(calwindow, style="A12B.TLabel")
    labelBA.grid(row=8, column=0, columnspan=2, sticky=W)
    labelBA.config(text = "CA 0V Src I")
    labelSIA0 = Label(calwindow, style="A12B.TLabel")
    labelSIA0.grid(row=9, column=0, columnspan=2, sticky=W)
    labelSIA0.config(text = "CA 2.5 Src 0 I")
    labelSIA = Label(calwindow, style="A12B.TLabel")
    labelSIA.grid(row=10, column=0, columnspan=2, sticky=W)
    labelSIA.config(text = "CA 50 Src 100 ")
    labelSIAN = Label(calwindow, style="A12B.TLabel")
    labelSIAN.grid(row=11, column=0, columnspan=2, sticky=W)
    labelSIAN.config(text = "CA 50 Src -45")
    labelSIB0 = Label(calwindow, style="A12B.TLabel")
    labelSIB0.grid(row=12, column=0, columnspan=2, sticky=W)
    labelSIB0.config(text = "CB 2.5 Src 0 I")
    labelSIB = Label(calwindow, style="A12B.TLabel")
    labelSIB.grid(row=13, column=0, columnspan=2, sticky=W)
    labelSIB.config(text = "CB 50 Src 100 ")
    labelSIBN = Label(calwindow, style="A12B.TLabel")
    labelSIBN.grid(row=14, column=0, columnspan=2, sticky=W)
    labelSIBN.config(text = "CB 50 Src -45")
    if session.continuous:
        session.end()
    # Setup ADAML1000
    if askyesno("Reset Calibration", "Do You Need To Reset Default Calibration?", parent=calwindow):
        #print(devx.calibration)
        try:
            devx.write_calibration("calib_default.txt")
            #print "wrote calib_default.txt"
        except:
            filename = askopenfilename(defaultextension = ".txt", filetypes=[("Default Cal File", "*.txt")], parent=calwindow)
            devx.write_calibration(filename)
        #print(devx.calibration)
    #
    devidstr = DevID[17:31]
    filename = "calib" + devidstr + ".txt"
    if os.path.isfile(filename):
        if askyesno("Calibration exists", "A previous Calibration file exists. /n Do you want to load that?", parent=calwindow):
            devx.write_calibration(filename)
            #print "wrote old ", filename
            calwindow.destroy()
            return
    #
    CalFile = open(filename, "w")
    #
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    devx.ctrl_transfer( 0x40, 0x50, 34, 0, 0, 0, 100) # close voltage sense loop just in case
    devx.ctrl_transfer( 0x40, 0x50, 39, 0, 0, 0, 100) # close voltage sense loop just in case
    ADsignal1 = []              # Ain signal array channel
    ADsignal1 = devx.get_samples(1010)
    # Pause whie user connects external voltage reference AD584
    BadData = 1
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    RequestVRef = askstring("External Reference", "Enter External Reference Voltage", initialvalue=AD584act, parent=root)
    try:
        AD584act = float(RequestVRef)*1.0
    except:
        AD584act = 3.3
    showinfo("CONNECT","Connect External Voltage to both CHA and CHB inputs.",  parent=calwindow)
    while (BadData):       # loop till good reading
        # Get A  and B AD584 data
        CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
        CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
        ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
        CHA584Raw = CHB584Raw = 0.0 # initalize measurment variable
        # get_samples returns a list of values for voltage [0] and current [1]
        for index in range(1000): # calculate average
            CHA584Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
            CHB584Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage

        CHA584Raw = CHA584Raw / 1000.0 # calculate average
        CHB584Raw = CHB584Raw / 1000.0 # calculate average
        VString = "Extern A Volts " + ' {0:.4f} '.format(CHA584Raw) # format with 4 decimal places
        labelAMax.config(text = VString) # change displayed value
        VString = "Extern B Volts " + ' {0:.4f} '.format(CHB584Raw) # format with 4 decimal places
        labelBMax.config(text = VString) # change displayed value
        Lower = AD584act - 0.3
        Upper = AD584act + 0.3
        if CHA584Raw < Lower or CHA584Raw > Upper or CHB584Raw < Lower or CHB584Raw > Upper:
            if askyesno("CONNECT","Did not get good data from Ref V check connections!\n Abort(Y) or Try again(N)", parent=calwindow):
                CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
                CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
                contloop = 0
                discontloop = 1
                calwindow.destroy()
                return
        else:
            BadData = 0
    #
    showinfo("DISCONNECT","Disconnect everything from CHA and CHB pins.", parent=calwindow)
    CHAGndRaw = CHBGndRaw = CHAI0gRaw = CHBI0gRaw = 0.0 # initalize measurment variable
    # Get A GND and B GND data
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 33, 0, 0, 0, 100) # set GND switch to closed
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 38, 0, 0, 0, 100) # set CHB GND switch to closed
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHAGndRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBGndRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI0gRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI0gRaw += ADsignal1[index+10][1][1] # Sum for average CB current

    CHAGndRaw = CHAGndRaw / 1000.0 # calculate average
    CHAI0gRaw = CHAI0gRaw / 1000.0
    CHBGndRaw = CHBGndRaw / 1000.0 # calculate average
    CHBI0gRaw = CHBI0gRaw / 1000.0
    VString = "CA gnd Volts " + ' {0:.4f} '.format(CHAGndRaw) # format with 4 decimal places
    labelA0.config(text = VString) # change displayed value
    VString = "CB gnd Volts " + ' {0:.4f} '.format(CHBGndRaw) # format with 4 decimal places
    labelB0.config(text = VString) # change displayed value
    CHA2p5Raw = CHB2p5Raw = CHAI02p5Raw = CHBI02p5Raw = 0.0 # initalize measurment variable
    # Get A and B data for internal 2.5 rail
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHA2p5Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHB2p5Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI02p5Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI02p5Raw += ADsignal1[index+10][1][1] # Sum for average CB current
        
    CHA2p5Raw = CHA2p5Raw / 1000.0 # calculate average
    CHAI02p5Raw = CHAI02p5Raw / 1000.0
    CHB2p5Raw = CHB2p5Raw / 1000.0 # calculate average
    CHBI02p5Raw = CHBI02p5Raw / 1000.0
    # Get A force 0V and B force 0V data
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SVMI
    CHA.constant(0.0)
    CHB.mode = Mode.SVMI
    CHB.constant(0.0)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAF0vRaw = CHBF0vRaw = CHAI0F0Raw = CHBI0F0Raw = 0.0 # initalize measurment variable
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHAF0vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBF0vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI0F0Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI0F0Raw += ADsignal1[index+10][1][1] # Sum for average CB current
        
    CHAF0vRaw = CHAF0vRaw / 1000.0 # calculate average
    CHAI0F0Raw = CHAI0F0Raw / 1000.0
    CHBF0vRaw = CHBF0vRaw / 1000.0 # calculate average
    CHBI0F0Raw = CHBI0F0Raw / 1000.0
    # Get A force 2.5V and B force 2.5V data
    CHA.mode = Mode.SVMI
    CHA.constant(4.5)
    CHB.mode = Mode.SVMI
    CHB.constant(4.5)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAF25vRaw = CHAI0F25Raw = CHBF25vRaw = CHBI0F25Raw = 0.0 # initalize measurment variable
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHAF25vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBF25vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI0F25Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI0F25Raw += ADsignal1[index+10][1][1] # Sum for average CB current
        
    CHAF25vRaw = CHAF25vRaw / 1000.0 # calculate average
    CHAI0F25Raw = CHAI0F25Raw / 1000.0
    CHBF25vRaw = CHBF25vRaw / 1000.0 # calculate average
    CHBI0F25Raw = CHBI0F25Raw / 1000.0
    #
    # Get A and B measure current data for int 50 res to gnd at 5V
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 33, 0, 0, 0, 100) # set CHA GND switch to closed
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 38, 0, 0, 0, 100) # set CHB GND switch to closed
    CHA.mode = Mode.SVMI
    CHA.constant(5.0)
    CHB.mode = Mode.SVMI
    CHB.constant(5.0)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHASr5vRaw = CHAISr5vRaw = CHBSr5vRaw = CHBISr5vRaw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHASr5vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBSr5vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr5vRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr5vRaw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHASr5vRaw = CHASr5vRaw / 1000.0 # calculate average
    CHAISr5vRaw = CHAISr5vRaw / 1000.0
    CHBSr5vRaw = CHBSr5vRaw / 1000.0 # calculate average
    CHBISr5vRaw = CHBISr5vRaw / 1000.0
    VString = "CA 5V Src I " + ' {0:.4f} '.format(CHAISr5vRaw) # format with 4 decimal places
    labelAMin.config(text = VString) # change displayed value
    VString = "CB 5V Src I " + ' {0:.4f} '.format(CHBISr5vRaw) # format with 4 decimal places
    labelBMin.config(text = VString) # change displayed value
    # Get A and B measure current data for int 50 res to 2.5 V  at 0V
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SVMI
    CHA.constant(0.001)
    CHB.mode = Mode.SVMI
    CHB.constant(0.001)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHASr0vRaw = CHAISr0vRaw = CHBSr0vRaw = CHBISr0vRaw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHASr0vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBSr0vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr0vRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr0vRaw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHASr0vRaw = CHASr0vRaw / 1000.0 # calculate average
    CHAISr0vRaw = CHAISr0vRaw / 1000.0
    CHBSr0vRaw = CHBSr0vRaw / 1000.0 # calculate average
    CHBISr0vRaw = CHBISr0vRaw / 1000.0
    VString = "CA 0V Src I " + ' {0:.4f} '.format(CHAISr0vRaw) # format with 4 decimal places
    labelAB.config(text = VString) # change displayed value
    VString = "CB 0V Src I " + ' {0:.4f} '.format(CHBISr0vRaw) # format with 4 decimal places
    labelBA.config(text = VString) # change displayed value

    # Get A and B force 0.0 current data for int 50 res to 2.5 rail
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SIMV
    CHA.constant(0.0)
    CHB.mode = Mode.SIMV
    CHB.constant(0.0)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAVSr0iRaw = CHAISr0iRaw = CHBVSr0iRaw = CHBISr0iRaw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHAVSr0iRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBVSr0iRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr0iRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr0iRaw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHAVSr0iRaw = CHAVSr0iRaw / 1000.0 # calculate average
    CHAISr0iRaw = CHAISr0iRaw / 1000.0
    CHBVSr0iRaw = CHBVSr0iRaw / 1000.0 # calculate average
    CHBISr0iRaw = CHBISr0iRaw / 1000.0
    VString = "CA 2.5 Src 0 I" + ' {0:.4f} '.format(CHAISr0iRaw) # format with 4 decimal places
    labelSIA0.config(text = VString) # change displayed value
    VString = "CB 2.5 Src 0 I" + ' {0:.4f} '.format(CHBISr0iRaw) # format with 4 decimal places
    labelSIB0.config(text = VString) # change displayed value
    #
    # Get A and B force +0.45 current data for int 50 res to 2.5 V rail
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SIMV
    CHA.constant(0.045)
    CHB.mode = Mode.SIMV
    CHB.constant(0.045)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAVSr100Raw = CHAISr100Raw = CHBVSr100Raw = CHBISr100Raw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHAVSr100Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBVSr100Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr100Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr100Raw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHAVSr100Raw = CHAVSr100Raw / 1000.0 # calculate average
    CHAISr100Raw = CHAISr100Raw / 1000.0
    CHBVSr100Raw = CHBVSr100Raw / 1000.0 # calculate average
    CHBISr100Raw = CHBISr100Raw / 1000.0
    VString = "CA 50 Src +45 " + ' {0:.4f} '.format(CHAVSr100Raw) # format with 4 decimal places
    labelSIA.config(text = VString) # change displayed value
    VString = "CB 50 Src +45 " + ' {0:.4f} '.format(CHBVSr100Raw) # format with 4 decimal places
    labelSIB.config(text = VString) # change displayed value
    #
    # Get A and B force -0.045 current data for int 50 res to 2.5 V rail
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SIMV
    CHA.constant(-0.045)
    CHB.mode = Mode.SIMV
    CHB.constant(-0.045)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAVSrN45Raw = CHAISrN45Raw = CHBVSrN45Raw = CHBISrN45Raw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHAVSrN45Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBVSrN45Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISrN45Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISrN45Raw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHAVSrN45Raw = CHAVSrN45Raw / 1000.0 # calculate average
    CHAISrN45Raw = CHAISrN45Raw / 1000.0
    CHBVSrN45Raw = CHBVSrN45Raw / 1000.0 # calculate average
    CHBISrN45Raw = CHBISrN45Raw / 1000.0
    VString = "CA 50 Src -45 " + ' {0:.4f} '.format(CHAVSrN45Raw) # format with 4 decimal places
    labelSIAN.config(text = VString) # change displayed value
    VString = "CB 50 Src -45 " + ' {0:.4f} '.format(CHBVSrN45Raw) # format with 4 decimal places
    labelSIBN.config(text = VString) # change displayed value
    # return all switches to open
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    # Caculate voltage gain errors
    # 
    CHAF25V = CHAF25vRaw * ( AD584act / CHA584Raw )
    CHBF25V = CHBF25vRaw * ( AD584act / CHB584Raw )
    #
    CHASr5v = CHASr5vRaw * ( AD584act / CHA584Raw ) # calculate actual voltage
    CHBSr5v = CHBSr5vRaw * ( AD584act / CHB584Raw ) # calculate actual voltage
    #
    CHA2p5 = CHA2p5Raw * ( AD584act / CHA584Raw )
    # print "calculated fixed 2.5 from CHA ", CHA2p5
    CHB2p5 = CHB2p5Raw * ( AD584act / CHB584Raw )
    # print "calculated fixed 2.5 from CHB ", CHB2p5
    # 
    CHAActSrI = CHASr5v / OnBoardRes # adjust resistor value to include switch ron
    CHBActSrI = CHBSr5v / OnBoardRes # adjust resistor value to include switch ron
    #
    CHAActSnkI = CHASr0vRaw - CHA2p5 / OnBoardRes # adjust resistor value to include switch ron
    CHBActSnkI = CHBSr0vRaw - CHB2p5 / OnBoardRes # adjust resistor value to include switch ron
    #
    CHASr0i = CHAVSr0iRaw * ( AD584act / CHA584Raw )
    CHASr0iAct = CHASr0i / OnBoardRes # adjust resistor value to include switch ron
    CHASr100 = CHAVSr100Raw * ( AD584act / CHA584Raw )
    CHASrI100Act = (CHASr100 - CHA2p5) / OnBoardRes # adjust resistor value to include switch ron
    CHASrN45 = CHAVSrN45Raw * ( AD584act / CHA584Raw )
    CHASrIN45Act = (CHASrN45 - CHA2p5) / OnBoardRes # adjust resistor value to include switch ron
    #
    CHBSr0i = CHBVSr0iRaw * ( AD584act / CHB584Raw )
    CHBSr0iAct = CHBSr0i / OnBoardRes # adjust resistor value to include switch ron
    CHBSr100 = CHBVSr100Raw * ( AD584act / CHB584Raw )
    CHBSrI100Act = (CHBSr100 - CHB2p5) / OnBoardRes # adjust resistor value to include switch ron
    CHBSrN45 = CHBVSrN45Raw * ( AD584act / CHB584Raw )
    CHBSrIN45Act = (CHBSrN45 - CHB2p5) / OnBoardRes # adjust resistor value to include switch ron
    # Write cal factors to file
    #
    CalFile.write('# Channel A, measure V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAGndRaw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(AD584act) + ', ' + '{0:.4f}'.format(CHA584Raw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel A, measure I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAI02p5Raw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(CHAActSrI) + ', ' + '{0:.4f}'.format(CHAISr5vRaw) + '>\n')
    # CalFile.write('<' + '{0:.4f}'.format(CHAISr0vRaw) + ', ' + '{0:.4f}'.format(CHAActSnkI) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(-CHAActSrI) + ', ' + '{0:.4f}'.format(-CHAISr5vRaw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel A, source V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAF0vRaw) + '>\n')
    CalFile.write('<4.5000, ' + '{0:.4f}'.format(CHAF25V) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel A, source I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAISr0iRaw) + '>\n')
    CalFile.write('<0.045, ' + '{0:.4f}'.format(CHASrI100Act) + '>\n')
    CalFile.write('<-0.0450, ' + '{0:.4f}'.format(CHASrIN45Act) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B, measure V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBGndRaw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(AD584act) + ', ' + '{0:.4f}'.format(CHB584Raw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B, measure I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBI02p5Raw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(CHBActSrI) + ', ' + '{0:.4f}'.format(CHBISr5vRaw) + '>\n')
    # CalFile.write('<' + '{0:.4f}'.format(CHBISr0vRaw) + ', ' + '{0:.4f}'.format(CHBActSnkI) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(-CHBActSrI) + ', ' + '{0:.4f}'.format(-CHBISr5vRaw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B, source V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBF0vRaw) + '>\n')
    CalFile.write('<4.5000, ' + '{0:.4f}'.format(CHAF25V) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B source I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBISr0iRaw) + '>\n')
    CalFile.write('<0.045, ' + '{0:.4f}'.format(CHBSrI100Act) + '>\n')
    CalFile.write('<-0.0450, ' + '{0:.4f}'.format(CHBSrIN45Act) + '>\n')
    CalFile.write('<\>\n')
    #
    CalFile.close()
    showinfo("Finish","Successfully measured cal factors!", parent=calwindow)
    if askyesno("Write cal", "Write Cal Data to Board?",  parent=calwindow):
        devx.write_calibration(filename)
        #print "wrote new " , filename
    #
    # session.end()
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
    contloop = 0
    discontloop = 1
    # session.cancel()
    calwindow.destroy()
## ========== MiniGen routines ==========
def SPIShiftOut(DValue):
    global devx, PIO_0, PIO_1, PIO_2, PIO_3
    
    binstr = bin(DValue)
    binlen = len(binstr)
    datastr = binstr[2:binlen]
    datalen = len(datastr)
    if datalen < 16:
       datastr = str.rjust(datastr , 16 , '0')
       datalen = len(datastr)
    i = 1
    devx.ctrl_transfer(0x40, 0x50, PIO_0, 0, 0, 0, 100) # fsync to 0
    while i < datalen+1:
    # sending 0x50 = set to 0, 0x51 = set to 1
        D1code = 0x50 + int(datastr[i-1])
        devx.ctrl_transfer(0x40, D1code, PIO_1, 0, 0, 0, 100) # data bit
        devx.ctrl_transfer(0x40, 0x51, PIO_3, 0, 0, 0, 100) # sclk to 1
        devx.ctrl_transfer(0x40, 0x50, PIO_3, 0, 0, 0, 100) # sclk to 0
        devx.ctrl_transfer(0x40, 0x51, PIO_3, 0, 0, 0, 100) # sclk to 1
        i = i + 1
    devx.ctrl_transfer(0x40, 0x51, PIO_0, 0, 0, 0, 100) # fsync to 1
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
        minigenwindow.title("MiniGen 1.2 " + RevDate)
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
        f1lab = Label(minigenwindow, text="Output Freq")
        f1lab.grid(row=4, column=0, columnspan=1, sticky=W)
        MinigenFout = Entry(minigenwindow, width=8)
        MinigenFout.bind('<MouseWheel>', onMiniGenScroll)
        MinigenFout.grid(row=4, column=1, sticky=W)
        MinigenFout.delete(0,"end")
        MinigenFout.insert(0,100)
        bsn1 = Button(minigenwindow, text='UpDate', style="W7.TButton", command=BSendMG)
        bsn1.grid(row=5, column=0, sticky=W, pady=4)
        dismissmgbutton = Button(minigenwindow, text="Dismiss", style="W8.TButton", command=DestroyMinigenScreen)
        dismissmgbutton.grid(row=5, column=1, sticky=W, pady=4)
#
def DestroyMinigenScreen():
    global minigenwindow, MinigenScreenStatus
    
    MinigenScreenStatus.set(0)
    minigenwindow.destroy()
#
def onMiniGenScroll(event):
    global ETSStatus, ETSDisp
    
    onTextScroll(event)
    BSendMG()
##    if ETSStatus.get() > 0 and ETSDisp.get() > 0:
##        MGLoad()
def DA1ShiftOut(D1Value, D2Value):
    global devx
    global PIO_0, PIO_1, PIO_2, PIO_3
    
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
    devx.ctrl_transfer(0x40, 0x50, 0, 0, 0, 0, 100) # sync to 0
    while i < datalen+1:
    # sending 0x50 = set to 0, 0x51 = set to 1
        D1code = 0x50 + int(data1str[i-1])
        D2code = 0x50 + int(data2str[i-1])
        devx.ctrl_transfer(0x40, D1code, PIO_1, 0, 0, 0, 100) # data 0 bit
        devx.ctrl_transfer(0x40, D2code, PIO_2, 0, 0, 0, 100) # data 1 bit
        devx.ctrl_transfer(0x40, 0x51, PIO_3, 0, 0, 0, 100) # sclk to 1
        devx.ctrl_transfer(0x40, 0x50, PIO_3, 0, 0, 0, 100) # sclk to 0
        devx.ctrl_transfer(0x40, 0x51, PIO_3, 0, 0, 0, 100) # sclk to 1
        i = i + 1
    devx.ctrl_transfer(0x40, 0x51, PIO_0, 0, 0, 0, 100) # sync to 1
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
        da1window.title("DA1 PMOD 1.2 " + RevDate)
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
    global devx, SingleDualPot
    global PIO_0, PIO_1, PIO_2, PIO_3

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
    devx.ctrl_transfer(0x40, 0x50, PIO_3, 0, 0, 0, 100) # clock to 0
    devx.ctrl_transfer(0x40, 0x50, PIO_0, 0, 0, 0, 100) # CS to 0
    while i < datalen+1:
    # CS --> PIO 0
    # D0 --> PIO 1
    # D1 --> PIO 2
    # SCLK --> PIO 3
        D1code = 0x50 + int(datastr[i-1])
        devx.ctrl_transfer(0x40, D1code, PIO_1, 0, 0, 0, 100) # data bit
        devx.ctrl_transfer(0x40, 0x51, PIO_3, 0, 0, 0, 100) # clock to 1
        devx.ctrl_transfer(0x40, 0x50, PIO_3, 0, 0, 0, 100) # clock to 0
        i = i + 1
    devx.ctrl_transfer(0x40, 0x51, 0, 0, 0, 0, 100) # CS to 1
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
        digpotwindow.title("Digital Potentiometer 1.2 " + RevDate)
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
        CompMenu = Menubutton(digpotwindow, text="Sel Comp.", style="W8.TButton")
        CompMenu.menu = Menu(CompMenu, tearoff = 0 )
        CompMenu["menu"] = CompMenu.menu
        CompMenu.menu.add_radiobutton(label="AD840X", variable=SingleDualPot, value=0, command=UpdatePotSlider)
        CompMenu.menu.add_radiobutton(label="AD5160", variable=SingleDualPot, value=1, command=UpdatePotSlider)
        CompMenu.menu.add_radiobutton(label="AD5203", variable=SingleDualPot, value=2, command=UpdatePotSlider)
        CompMenu.grid(row=1, column=0, columnspan=2, sticky=W)
        lab1 = Checkbutton(digpotwindow,text="Pot 1", pady=0, variable=SendPot1)
        lab1.grid(row=2, column=0, sticky=W)
        DigPot1 = Scale(digpotwindow, from_=0, to=255, orient=HORIZONTAL, command=DigPotSend, length=256)
        DigPot1.grid(row=3, column=0, columnspan=3, sticky=W)
        lab2 = Checkbutton(digpotwindow,text="Pot 2", pady=0, variable=SendPot2)
        lab2.grid(row=4, column=0, sticky=W)
        DigPot2 = Scale(digpotwindow, from_=0, to=255, orient=HORIZONTAL, command=DigPotSend, length=256)
        DigPot2.grid(row=5, column=0, columnspan=3, sticky=W)
        lab3 = Checkbutton(digpotwindow,text="Pot 3", pady=0, variable=SendPot3)
        lab3.grid(row=6, column=0, sticky=W)
        DigPot3 = Scale(digpotwindow, from_=0, to=255, orient=HORIZONTAL, command=DigPotSend, length=256)
        DigPot3.grid(row=7, column=0, columnspan=3, sticky=W)
        lab4 = Checkbutton(digpotwindow,text="Pot 4", pady=0, variable=SendPot4)
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
    global serialwindow, GenericSerialStatus, SCLKPort, SDATAPort, SLATCHPort, SLatchPhase, SClockPhase
    global NumBitsEntry, DataBitsEntry, devx, SerDirection, DValue, NumBits, AD5626SerialStatus, AD5626Entry

    if AD5626SerialStatus.get() == 0:
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
    else:
        try:
            DValue = int(eval(AD5626Entry.get())*1000)
            if DValue < 0:
                DValue = 0
                AD5626Entry.delete(0,"end")
                AD5626Entry.insert(0,'0.000')
            if DValue > 4095:
                DValue = 4095
                AD5626Entry.delete(0,"end")
                AD5626Entry.insert(0,DValue/1000.0)
        except:
            DValue = 0
            AD5626Entry.delete(0,"end")
            AD5626Entry.insert(0,'0.000')
        NumBits = 12
    # print DValue
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
    if AD5626SerialStatus.get() > 0:
        LatchInt = 0x51
        LatchEnd = 0x50
    if SClockPhase.get() == 0:
        ClockInt = 0x50
        ClockEnd = 0x51
    else:
        ClockInt = 0x51
        ClockEnd = 0x50
    devx.ctrl_transfer(0x40, ClockInt, SCLKPort.get(), 0, 0, 0, 100) # clock to start value
    devx.ctrl_transfer(0x40, LatchInt, SLATCHPort.get(), 0, 0, 0, 100) # CS to start value
    i = 1
    while i < datalen+1:
        if SerDirection.get() == 1: # for MSB first
            D1code = 0x50 + int(datastr[datalen-i]) # 0x50 = set to 0, 0x51 = set to 1
        else:
            D1code = 0x50 + int(datastr[i-1]) # for LSB first
        devx.ctrl_transfer(0x40, D1code, SDATAPort.get(), 0, 0, 0, 100) # data bit
        devx.ctrl_transfer(0x40, ClockEnd, SCLKPort.get(), 0, 0, 0, 100) # clock to end value
        devx.ctrl_transfer(0x40, ClockInt, SCLKPort.get(), 0, 0, 0, 100) # clock to start value
        i = i + 1
    devx.ctrl_transfer(0x40, ClockEnd, SCLKPort.get(), 0, 0, 0, 100) # clock to end value
    devx.ctrl_transfer(0x40, LatchEnd, SLATCHPort.get(), 0, 0, 0, 100) # CS to end value
    devx.ctrl_transfer(0x40, LatchInt, SLATCHPort.get(), 0, 0, 0, 100) # CS to start value
    devx.ctrl_transfer(0x40, LatchEnd, SLATCHPort.get(), 0, 0, 0, 100) # CS to end value
#
def MakeAD5626Window():
    global ad5626window, AD5626SerialStatus, SCLKPort, SDATAPort, SLATCHPort, SLatchPhase, SClockPhase
    global GenericSerialStatus
    global AD5626Entry, SerDirection
    global PIO_0, PIO_1, PIO_2, PIO_3

    if GenericSerialStatus.get() == 1:
        GenericSerialStatus.set(0)
        DestroyGenericSerialScreen()
    if AD5626SerialStatus.get() == 0:
        AD5626SerialStatus.set(1)
        ad5626window = Toplevel()
        ad5626window.title("AD5626 Output 1.2" + RevDate)
        ad5626window.resizable(FALSE,FALSE)
        ad5626window.protocol("WM_DELETE_WINDOW", DestroyAD5626Screen)
        #
        SCLKPort = IntVar(0)
        SCLKPort.set(PIO_2)
        SDATAPort = IntVar(0)
        SDATAPort.set(PIO_1)
        SLATCHPort = IntVar(0)
        SLATCHPort.set(PIO_0)
        SLatchPhase = IntVar(0)
        SLatchPhase.set(0)
        SClockPhase = IntVar(0)
        SClockPhase.set(1)
        SerDirection = IntVar(0)
        SerDirection.set(0)
        #
        label2 = Label(ad5626window,text="Enter Output Volts")
        label2.grid(row=1, column=0, columnspan=1, sticky=W)
        AD5626Entry = Entry(ad5626window, width=10)
        AD5626Entry.bind('<MouseWheel>', onAD5626Scroll)
        AD5626Entry.grid(row=1, column=1, columnspan=3, sticky=W)
        AD5626Entry.delete(0,"end")
        AD5626Entry.insert(0,'0.000')
        #
        label3 = Label(ad5626window,text="SCLK PI/O Port ")
        label3.grid(row=2, column=0, columnspan=1, sticky=W)
        sclk1 = Radiobutton(ad5626window, text="0", variable=SCLKPort, value=PIO_0)
        sclk1.grid(row=2, column=1, sticky=W)
        sclk2 = Radiobutton(ad5626window, text="1", variable=SCLKPort, value=PIO_1)
        sclk2.grid(row=2, column=2, sticky=W)
        sclk3 = Radiobutton(ad5626window, text="2", variable=SCLKPort, value=PIO_2)
        sclk3.grid(row=2, column=3, sticky=W)
        sclk4 = Radiobutton(ad5626window, text="3", variable=SCLKPort, value=PIO_3)
        sclk4.grid(row=2, column=4, sticky=W)
        #
        label4 = Label(ad5626window,text="SData PI/O Port ")
        label4.grid(row=3, column=0, columnspan=1, sticky=W)
        sdat1 = Radiobutton(ad5626window, text="0", variable=SDATAPort, value=PIO_0)
        sdat1.grid(row=3, column=1, sticky=W)
        sdat2 = Radiobutton(ad5626window, text="1", variable=SDATAPort, value=PIO_1)
        sdat2.grid(row=3, column=2, sticky=W)
        sdat3 = Radiobutton(ad5626window, text="2", variable=SDATAPort, value=PIO_2)
        sdat3.grid(row=3, column=3, sticky=W)
        sdat4 = Radiobutton(ad5626window, text="3", variable=SDATAPort, value=PIO_3)
        sdat4.grid(row=3, column=4, sticky=W)
        #
        label5 = Label(ad5626window,text="Latch PI/O Port ")
        label5.grid(row=4, column=0, columnspan=1, sticky=W)
        slth1 = Radiobutton(ad5626window, text="0", variable=SLATCHPort, value=PIO_0)
        slth1.grid(row=4, column=1, sticky=W)
        slth2 = Radiobutton(ad5626window, text="1", variable=SLATCHPort, value=PIO_1)
        slth2.grid(row=4, column=2, sticky=W)
        slth3 = Radiobutton(ad5626window, text="2", variable=SLATCHPort, value=PIO_2)
        slth3.grid(row=4, column=3, sticky=W)
        slth4 = Radiobutton(ad5626window, text="3", variable=SLATCHPort, value=PIO_3)
        slth4.grid(row=4, column=4, sticky=W)
        #
        bsn1 = Button(ad5626window, text='Send', style="W5.TButton", command=BSendGS)
        bsn1.grid(row=5, column=0, sticky=W)
        dismissgsbutton = Button(ad5626window, text="Dismiss", style="W8.TButton", command=DestroyAD5626Screen)
        dismissgsbutton.grid(row=5, column=1, columnspan=2, sticky=W, pady=4)
#
def onAD5626Scroll(event):
    onTextScroll(event)
    BSendGS()
    
def DestroyAD5626Screen():
    global ad5626window, AD5626SerialStatus
    
    AD5626SerialStatus.set(0)
    ad5626window.destroy()
        
def MakeGenericSerialWindow():
    global serialwindow, GenericSerialStatus, SCLKPort, SDATAPort, SLATCHPort, SLatchPhase, SClockPhase
    global NumBitsEntry, DataBitsEntry, SerDirection
    global PIO_0, PIO_1, PIO_2, PIO_3

    if GenericSerialStatus.get() == 0:
        GenericSerialStatus.set(1)
        serialwindow = Toplevel()
        serialwindow.title("Generic Serial Output 1.2" + RevDate)
        serialwindow.resizable(FALSE,FALSE)
        serialwindow.protocol("WM_DELETE_WINDOW", DestroyGenericSerialScreen)
        #
        SCLKPort = IntVar(0)
        SCLKPort.set(PIO_2)
        SDATAPort = IntVar(0)
        SDATAPort.set(PIO_1)
        SLATCHPort = IntVar(0)
        SLATCHPort.set(PIO_0)
        SLatchPhase = IntVar(0)
        SClockPhase = IntVar(0)
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
        sclk1 = Radiobutton(serialwindow, text="0", variable=SCLKPort, value=PIO_0)
        sclk1.grid(row=3, column=1, sticky=W)
        sclk2 = Radiobutton(serialwindow, text="1", variable=SCLKPort, value=PIO_1)
        sclk2.grid(row=3, column=2, sticky=W)
        sclk3 = Radiobutton(serialwindow, text="2", variable=SCLKPort, value=PIO_2)
        sclk3.grid(row=3, column=3, sticky=W)
        sclk4 = Radiobutton(serialwindow, text="3", variable=SCLKPort, value=PIO_3)
        sclk4.grid(row=3, column=4, sticky=W)
        #
        label4 = Label(serialwindow,text="SData PI/O Port ")
        label4.grid(row=4, column=0, columnspan=1, sticky=W)
        sdat1 = Radiobutton(serialwindow, text="0", variable=SDATAPort, value=PIO_0)
        sdat1.grid(row=4, column=1, sticky=W)
        sdat2 = Radiobutton(serialwindow, text="1", variable=SDATAPort, value=PIO_1)
        sdat2.grid(row=4, column=2, sticky=W)
        sdat3 = Radiobutton(serialwindow, text="2", variable=SDATAPort, value=PIO_2)
        sdat3.grid(row=4, column=3, sticky=W)
        sdat4 = Radiobutton(serialwindow, text="3", variable=SDATAPort, value=PIO_3)
        sdat4.grid(row=4, column=4, sticky=W)
        #
        label5 = Label(serialwindow,text="Latch PI/O Port ")
        label5.grid(row=5, column=0, columnspan=1, sticky=W)
        slth1 = Radiobutton(serialwindow, text="0", variable=SLATCHPort, value=PIO_0)
        slth1.grid(row=5, column=1, sticky=W)
        slth2 = Radiobutton(serialwindow, text="1", variable=SLATCHPort, value=PIO_1)
        slth2.grid(row=5, column=2, sticky=W)
        slth3 = Radiobutton(serialwindow, text="2", variable=SLATCHPort, value=PIO_2)
        slth3.grid(row=5, column=3, sticky=W)
        slth4 = Radiobutton(serialwindow, text="3", variable=SLATCHPort, value=PIO_3)
        slth4.grid(row=5, column=4, sticky=W)
        #
        label6 = Label(serialwindow,text="Latch Phase ")
        label6.grid(row=6, column=0, columnspan=1, sticky=W)
        sph1 = Radiobutton(serialwindow, text="0", variable=SLatchPhase, value=0)
        sph1.grid(row=6, column=1, sticky=W)
        sph2 = Radiobutton(serialwindow, text="1", variable=SLatchPhase, value=1)
        sph2.grid(row=6, column=2, sticky=W)
        #
        label7 = Label(serialwindow,text="Clock Phase ")
        label7.grid(row=7, column=0, columnspan=1, sticky=W)
        sph7 = Radiobutton(serialwindow, text="0", variable=SClockPhase, value=0)
        sph7.grid(row=7, column=1, sticky=W)
        sph8 = Radiobutton(serialwindow, text="1", variable=SClockPhase, value=1)
        sph8.grid(row=7, column=2, sticky=W)
        #
        sdir1 = Radiobutton(serialwindow, text="LSB First", variable=SerDirection, value=0 )
        sdir1.grid(row=8, column=0, sticky=W)
        sdir2 = Radiobutton(serialwindow, text="MSB First", variable=SerDirection, value=1 )
        sdir2.grid(row=8, column=1, columnspan=2, sticky=W)

        bsn1 = Button(serialwindow, text='Send', style="W5.TButton", command=BSendGS)
        bsn1.grid(row=9, column=0, sticky=W)
        dismissgsbutton = Button(serialwindow, text="Dismiss", style="W8.TButton", command=DestroyGenericSerialScreen)
        dismissgsbutton.grid(row=9, column=1, columnspan=2, sticky=W, pady=4)
        
def DestroyGenericSerialScreen():
    global serialwindow, GenericSerialStatus
    
    GenericSerialStatus.set(0)
    serialwindow.destroy()

def MakeDigFiltWindow():
    global digfltwindow, DigFiltStatus
    global DigFiltA, DigFiltB, DifFiltALength, DifFiltBLength, DifFiltAFile, DifFiltBFile

    if DigFiltStatus.get() == 0:
        DigFiltStatus.set(1)
        digfltwindow = Toplevel()
        digfltwindow.title("Digital Filter 1.2 " + RevDate)
        digfltwindow.resizable(FALSE,FALSE)
        digfltwindow.protocol("WM_DELETE_WINDOW", DestroyDigFiltScreen)
        titlab = Label(digfltwindow,text="Apply Digital Filters ", style="A12B.TLabel")
        titlab.grid(row=0, column=0, sticky=W)
        lab1 = Checkbutton(digfltwindow,text="Filter CH A", variable=DigFiltA)
        lab1.grid(row=1, column=0, sticky=W)
        DifFiltALength = Label(digfltwindow,text="Length = 0 ")
        DifFiltALength.grid(row=2, column=0, sticky=W)
        DifFiltAFile = Label(digfltwindow,text="File Name, none ")
        DifFiltAFile.grid(row=3, column=0, sticky=W)
        lab2 = Checkbutton(digfltwindow,text="Filter CH B", variable=DigFiltB)
        lab2.grid(row=4, column=0, sticky=W)
        DifFiltBLength = Label(digfltwindow,text="Length = 0 ")
        DifFiltBLength.grid(row=5, column=0, sticky=W)
        DifFiltBFile = Label(digfltwindow,text="File Name, none ")
        DifFiltBFile.grid(row=6, column=0, sticky=W)
        cald = Button(digfltwindow, text='Load CH A Filter Coef', command=BLoadDFiltA)
        cald.grid(row=7, column=0, sticky=W)
        camath = Button(digfltwindow, text='CH A Filter formula', command=BDFiltAMath)
        camath.grid(row=8, column=0, sticky=W)
        cbld = Button(digfltwindow, text='Load CH B Filter Coef', command=BLoadDFiltB)
        cbld.grid(row=9, column=0, sticky=W)
        cbmath = Button(digfltwindow, text='CH B Filter formula', command=BDFiltBMath)
        cbmath.grid(row=10, column=0, sticky=W)
        #
        dismissdfbutton = Button(digfltwindow, text="Dismiss", style="W8.TButton", command=DestroyDigFiltScreen)
        dismissdfbutton.grid(row=11, column=0, columnspan=1, sticky=W, pady=4)

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
    DigFilterAString = askstring("CH A Filter Math Formula", "Current Formula: " + DigFilterAString + "\n\nNew Formula:\n", initialvalue=DigFilterAString, parent=digfltwindow)
    if (DigFilterAString == None):         # If Cancel pressed, then None
        DigFilterAString = TempString
        return
    DFiltACoef = eval(DigFilterAString)
    DFiltACoef = numpy.array(DFiltACoef)
    coefsum = numpy.sum(DFiltACoef)
    DFiltACoef = DFiltACoef / coefsum
    DifFiltALength.config(text = "Length = " + str(int(len(DFiltACoef)))) # change displayed length value
    DifFiltAFile.config(text = "Using Filter A formula" ) # change displayed file name
    
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
    DigFilterBString = askstring("CH B Filter Math Formula", "Current Formula: " + DigFilterBString + "\n\nNew Formula:\n", initialvalue=DigFilterBString, parent=digfltwindow)
    if (DigFilterBString == None):         # If Cancel pressed, then None
        DigFilterBString = TempString
        return
    DFiltBCoef = eval(DigFilterBString)
    DFiltBCoef = numpy.array(DFiltBCoef)
    coefsum = numpy.sum(DFiltBCoef)
    DFiltBCoef = DFiltBCoef / coefsum
    DifFiltBLength.config(text = "Length = " + str(int(len(DFiltBCoef)))) # change displayed length value
    DifFiltBFile.config(text = "Using Filter B formula" ) # change displayed file name
#
def MakeCommandScreen():
    global commandwindow, CommandStatus, ExecString, LastCommand, RevDate
    
    if CommandStatus.get() == 0:
        CommandStatus.set(1)
        commandwindow = Toplevel()
        commandwindow.title("Command Line 1.2 " + RevDate)
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
        dismissclbutton = Button(commandwindow, text="Dismiss", style="W8.TButton", command=DestroyCommandScreen)
        dismissclbutton.grid(row=4, column=1, sticky=W, pady=7)
        
def DestroyCommandScreen():
    global commandwindow, CommandStatus
    
    CommandStatus.set(0)
    commandwindow.destroy()

def RExecuteFromString(temp):

    BExecuteFromString()
    
def BExecuteFromString(): # global VBuffA,AWGAwaveform;VBuffA=AWGAwaveform
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
def MakeBoardScreen():
    global boardwindow, BoardStatus, session, devx, dev0, dev1, dev2
    global RevDate, BrdSel, FWRevOne, HWRevOne, FWRevTwo, HWRevTwo, WRevThree, HWRevThree
    
    if len(session.devices) > 1: # make screen only if more than one board present
        if BoardStatus.get() == 0:
            BoardStatus.set(1)
            boardwindow = Toplevel()
            boardwindow.title("Select Board " + RevDate)
            boardwindow.resizable(FALSE,FALSE)
            boardwindow.protocol("WM_DELETE_WINDOW", DestroyBoardScreen)
            toplab = Label(boardwindow,text="- Select ALM1000 -", style="A12B.TLabel")
            toplab.pack(side=TOP)
            for idx, devx in enumerate(session.devices):
                BrdText = "Board # " + str(idx)
                if idx == 0:
                    devx.set_led(0b010) # LED.green
                    FWRevOne = float(devx.fwver)
                    HWRevOne = devx.hwver
                    dev0 = session.devices[0]
                    brd = Radiobutton(boardwindow, text=BrdText, fg="green", variable=BrdSel, value=idx, command=SelectBoard)
                elif idx == 1:
                    devx.set_led(0b100) # LED.blue,
                    FWRevTwo = float(devx.fwver)
                    HWRevTwo = devx.hwver
                    dev1 = session.devices[1]
                    brd = Radiobutton(boardwindow, text=BrdText, fg="blue", variable=BrdSel, value=idx, command=SelectBoard)
                elif idx == 2:
                    devx.set_led(0b001) # LED.red,
                    FWRevThree = float(devx.fwver)
                    HWRevThree = devx.hwver
                    dev2 = session.devices[2]
                    brd = Radiobutton(boardwindow, text=BrdText, fg="red", variable=BrdSel, value=idx, command=SelectBoard)
                else:
                    dev3 = session.devices[3]
                    brd = Radiobutton(boardwindow, text=BrdText, variable=BrdSel, value=idx, command=SelectBoard)
                brd.pack(side=TOP)
    else:
        devx = session.devices[0]
        # devx.ignore_dataflow = True
        #devx.set_led(0b010) # LED.green
        try:
            FWRevOne = float(devx.fwver)
            HWRevOne = devx.hwver
        except:
            FWRevOne = "Before 2.06"
            HWRevOne = "?"
        dev0 = session.devices[0]
#
def DestroyBoardScreen():
    global boardwindow, BoardStatus
    
    BoardStatus.set(0)
    boardwindow.destroy()
#
def ConnectDevice():
    global devx, dev0, dev1, dev2, session, BrdSel, CHA, CHB, DevID, MaxSamples, AWGSAMPLErate
    global bcon, FWRevOne, HWRevOne, FWRevTwo, HWRevTwo, WRevThree, HWRevThree, SAMPLErate

    if DevID == "No Device" or DevID == "m1k":
        SAMPLErate = AWGSAMPLErate # Scope sample rate
        #print("Request sample rate: " + str(SAMPLErate))
        session = Session(ignore_dataflow=True, sample_rate=SAMPLErate, queue_size=MaxSamples)
        # session.add_all()
        if not session.devices:
            print 'No Device plugged IN!'
            DevID = "No Device"
            bcon.configure(text="Recon", style="RConn.TButton")
            return
        session.configure(sample_rate=SAMPLErate)
        #print("Session sample rate: " + str(session.sample_rate))
        MakeBoardScreen()
        SelectBoard()
        bcon.configure(text="Conn", style="GConn.TButton")
        session.start(0)
#
def SelectBoard():
    global devx, dev0, dev1, dev2, session, BrdSel, CHA, CHB, DevID
    global PIO_0, PIO_1, PIO_2, PIO_3

    if BrdSel.get() == 0:
        try:
            session.remove(dev1)
        except:
            print "Skipping dev1"
        try:
            session.remove(dev2)
        except:
            print "Skipping dev2"
        session.add(dev0)
        devx = dev0
    if BrdSel.get() == 1:
        try:
            session.remove(dev0)
        except:
            print "Skipping dev0"
        try:
            session.remove(dev2)
        except:
            print "Skipping dev2"
        session.add(dev1)
        devx = dev1
    DevID = devx.serial
    print DevID
    print devx.fwver, devx.hwver
    print("Session sample rate: " + str(session.sample_rate))
    CHA = devx.channels['A']    # Open CHA
    CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
    CHB = devx.channels['B']    # Open CHB
    CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
    if devx.hwver == "F":
        print "Rev F Board I/O ports set"
        PIO_0 = 28
        PIO_1 = 29
        PIO_2 = 47
        PIO_3 = 3
    else:
        PIO_0 = 0
        PIO_1 = 1
        PIO_2 = 2
        PIO_3 = 3
#
def SetSampleRate():
    global SAMPLErate, AWGSAMPLErate, session, ETSStatus, etssrlab

    # ask user for channel to save
    BStop() # Force Stop loop if running
    TempRate = askstring("Set Sample Rate", "Current Sample Rate:\n", initialvalue=SAMPLErate)
    if (TempRate == None):         # If Cancel pressed, then None
        return
    try:
        NewRate = int(TempRate)
        if NewRate <= 100000: # rate has to be less than or equal to 100,000
            AWGSAMPLErate = NewRate
        else:
            AWGSAMPLErate = 100000
        SAMPLErate = AWGSAMPLErate # Scope sample rate
    except:
        donothing()
    session.configure(sample_rate=SAMPLErate)
    if ETSStatus.get() > 0:
        SRstring = "RT Sample Rate = " + str(SAMPLErate)
        etssrlab.config(text=SRstring)
        ETSUpdate()
#
def UpdateFirmware():
    global devx, dev0, dev1, dev2, session, BrdSel, CHA, CHB, DevID, MaxSamples
    global bcon, FWRevOne, HWRevOne, FWRevTwo, HWRevTwo, WRevThree, HWRevThree

    RUNstatus.set(0)
    if askyesno("Update current firmware","Flash new firmware to current device:\n(Yes) or (No)?"):
        filename = askopenfilename(defaultextension = ".bin", filetypes=[("Binary", "*.bin")])
        print filename
        #print DevID
        #print FWRevOne, HWRevOne # devx.fwver, devx.hwver
        try:
            print "Cancel current session."
            session.cancel()
            print session.cancelled
            session.end()
            print "Waiting 5..."
            time.sleep(5)
            print "Put board in Samba mode and flash firmware."
            session.flash_firmware(filename)
        except:
            if askyesno("Flash Failed", "Failed to update firmware.\n Try again?"):
                try:
                    session.flash_firmware(filename)
                except:
                    showwarning("Flash Failed","Failed to update firmware.")
            else:
                return
        showwarning("Complete","Flash Firmware Complete: \n Un-plug board to cycle power.")
        print "doing session add all..."
        session = Session(ignore_dataflow=True, sample_rate=SAMPLErate, queue_size=MaxSamples)
        #session.scan()
        session.add_all()
        print session.devices
        time.sleep(5)
        print "trying to reconnect device..."
        ConnectDevice()
#
def MakeOhmWindow():
    global OhmDisp, OhmStatus, ohmwindow, RevDate, RMode, OhmA0, OhmA1, OhmRunStatus
    global CHATestVEntry, CHATestREntry
    
    if OhmStatus.get() == 0:
        OhmStatus.set(1)
        OhmDisp.set(1)
        OhmCheckBox()
        ohmwindow = Toplevel()
        ohmwindow.title("DC Ohmmeter 1.2" + RevDate)
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
        OhmA0 = Label(frame1, style="A16B.TLabel") # , font = "Arial 16 bold")
        OhmA0.grid(row=1, column=0, columnspan=2, sticky=W)
        OhmA0.config(text = "0.000 Ohms")

        OhmA1 = Label(frame1, style="A12B.TLabel") #, font = "Arial 12 bold")
        OhmA1.grid(row=2, column=0, columnspan=2, sticky=W)
        OhmA1.config(text = "Meas 0.00 mA 0.00 V")
        #
        TestVA = Frame( frame1 )
        TestVA.grid(row=3, column=0, sticky=W)
        chatestvlab = Label(TestVA, text="Test Voltage", style="A10B.TLabel") #, font = "Arial 10 bold")
        chatestvlab.pack(side=LEFT)
        CHATestVEntry = Entry(TestVA, width=6) #
        CHATestVEntry.pack(side=LEFT)
        CHATestVEntry.bind('<MouseWheel>', onTextScroll)
        CHATestVEntry.delete(0,"end")
        CHATestVEntry.insert(0,5.0)
        #
        RMode = IntVar(0)
        RMode.set(1)
        TestMode = Frame( frame1 )
        TestMode.grid(row=4, column=0, sticky=W)
        modelab = Label(TestMode, text="Known Res", style="A10B.TLabel") #, font = "Arial 10 bold")
        modelab.pack(side=LEFT)
        rm3 = Radiobutton(TestMode, text="Ext", variable=RMode, value=0)
        rm3.pack(side=LEFT)
        rm4 = Radiobutton(TestMode, text="Int", variable=RMode, value=1)
        rm4.pack(side=LEFT)
        #
        TestRA = Frame( frame1 )
        TestRA.grid(row=5, column=0, sticky=W)
        chatestrlab = Label(TestRA, text="Known Res", style="A10B.TLabel") #, font = "Arial 10 bold")
        chatestrlab.pack(side=LEFT)
        CHATestREntry = Entry(TestRA, width=6) #
        CHATestREntry.pack(side=LEFT)
        CHATestREntry.bind('<MouseWheel>', onTextScroll)
        CHATestREntry.delete(0,"end")
        CHATestREntry.insert(0,50.0)
        #
        ohmdismissclbutton = Button(frame1, text="Dismiss", style="W8.TButton", command=DestroyOhmScreen)
        ohmdismissclbutton.grid(row=6, column=0, sticky=W, pady=7)
#
def DestroyOhmScreen():
    global ohmwindow, OhmStatus, OhmDisp
    
    OhmStatus.set(0)
    OhmDisp.set(0)
    OhmCheckBox()
    ohmwindow.destroy()
#
def MakeETSWindow():
    global FminEntry, MulXEntry, etswindow, ETSStatus, ETSDisp, ETSDir, ETSts, eqivsamplerate
    global SAMPLErate, DivXEntry, FOffEntry, FminDisp, enb1, etssrlab

    #
    if ETSStatus.get() == 0:
        BaseFreq = (-10, -15, -20, -25, -30, -35, -40, -45, -50, -60, -70, -80, -90, -100)
        ETSStatus.set(1)
        ETSDisp.set(0)
        etswindow = Toplevel()
        etswindow.title("ETS Controls 1.2" + RevDate)
        etswindow.resizable(FALSE,FALSE)
        etswindow.protocol("WM_DELETE_WINDOW", DestroyETSScreen)
        frame1 = Frame(etswindow, borderwidth=5, relief=RIDGE)
        frame1.grid(row=0, column=0, sticky=W)
        # Sampling controls Widgets
        SRstring = "RT Sample Rate = " + str(SAMPLErate)
        etssrlab = Label(frame1, text=SRstring, style= "A10B.TLabel")
        etssrlab.grid(row=1, column=0, sticky=W)
        etssrbutton = Button(frame1, text="Set RT Sample Rate", command=SetSampleRate) #, style= "W8.TButton"
        etssrbutton.grid(row=2, column=0, sticky=W, pady=7)
        enb1 = Checkbutton(frame1,text="Enable ETS", variable=ETSDisp, command=ETSCheckBox)
        enb1.grid(row=3, column=0, sticky=W)
        #
        Divx = Frame( frame1 )
        Divx.grid(row=4, column=0, sticky=W)
        DivXEntry = Entry(Divx, width=6)
        DivXEntry.bind('<MouseWheel>', ETSscroll)
        DivXEntry.pack(side=RIGHT)
        DivXEntry.delete(0,"end")
        DivXEntry.insert(0,1)
        divxlab = Label( Divx, text = "Divide Factor")
        divxlab.pack(side=RIGHT)
        #
        FOffEntry = Label(frame1, text="Samples")
        FOffEntry.grid(row=5, column=0, sticky=W)
        MulXEntry = Label( frame1, text = "Rec Len Mul")
        MulXEntry.grid(row=6, column=0, sticky=W)
        #
        eqivsamplerate = Label(frame1, text="MHz", style= "A10B.TLabel")
        eqivsamplerate.grid(row=7, column=0, sticky=W)
        #
        FConv = Frame( frame1 )
        FConv.grid(row=8, column=0, sticky=W)
        FminEntry = Entry(FConv, width=3)
        FminEntry.bind('<MouseWheel>', ETSscroll)
        FminEntry.pack(side=RIGHT)
        FminEntry.delete(0,"end")
        FminEntry.insert(0,7)
        fminlab = Label( FConv, text = "Freq Multiplier")
        fminlab.pack(side=RIGHT)
        #
        FminDisp = Label(frame1, text="32768 Hz", style= "A10B.TLabel")
        FminDisp.grid(row=9, column=0, sticky=W)
        #
        mgloadbutton = Button(frame1, text="Load to MinGen", command=MGLoad)
        mgloadbutton.grid(row=10, column=0, sticky=W)
        #
        dirlab = Label(frame1, text="Sample Data Order", style= "A10B.TLabel")
        dirlab.grid(row=11, column=0, sticky=W)
        DataMode = Frame( frame1 )
        DataMode.grid(row=12, column=0, sticky=W)
        dm3 = Radiobutton(DataMode, text="Forward", variable=ETSDir, value=0)
        dm3.pack(side=LEFT)
        dm4 = Radiobutton(DataMode, text="Reverse", variable=ETSDir, value=1)
        dm4.pack(side=LEFT)
        tclab = Label(frame1, text="CH B Time Shift", style= "A10B.TLabel")
        tclab.grid(row=13, column=0, sticky=W)
        TSMode = Frame( frame1 )
        TSMode.grid(row=14, column=0, sticky=W)
        ETSts = Entry(TSMode, width=6)
        ETSts.bind('<MouseWheel>', ETSscroll)
        ETSts.pack(side=RIGHT)
        ETSts.delete(0,"end")
        ETSts.insert(0,1)
        ETStslab = Label( TSMode, text = "Factor")
        ETStslab.pack(side=RIGHT)
        #
        etsdismissclbutton = Button(frame1, text="Dismiss", style= "W8.TButton", command=DestroyETSScreen)
        etsdismissclbutton.grid(row=15, column=0, sticky=W, pady=7)
        ETSDisp.set(0)
        ETSCheckBox()
#
def DestroyETSScreen():
    global etswindow, ETSStatus, ETSDisp
    
    ETSStatus.set(0)
    ETSDisp.set(0)
    ETSCheckBox()
    etswindow.destroy()
#
def MGLoad():
    global MinigenFout, Fmin, ETSDir

    MinigenFout.delete(0,"end")
    if ETSDir.get() == 0:
        MinigenFout.insert(0,Fmin+20)
    else:
        MinigenFout.insert(0,Fmin-20)
    BSendMG()
#
def ETSscroll(event):
    onTextScroll(event)
    ETSUpdate()
#
def ETSUpdate():
    global FminEntry, MulXEntry, ETSStatus, ETSDisp, ETSDir, ETSts, eqivsamplerate, MaxETSrecord
    global SAMPLErate, DivXEntry, FOffEntry, FminDisp, DivX, FOff, MulX, Fmin, FMul, AWGSAMPLErate, TIMEdiv

    if TIMEdiv > 0.2:
        MaxETSrecord = int(AWGSAMPLErate * 10 * TIMEdiv / 1000.0)
    else:
        MaxETSrecord = int(AWGSAMPLErate * 20 * TIMEdiv / 1000.0)
    if (MaxETSrecord*100) > MaxSamples:
        MaxETSrecord = MaxSamples / 100
    try:
        DivX = float(eval(DivXEntry.get()))
        if DivX < 2:
            DivX = 2
        if DivX > 75:
            DivX = 75
            DivXEntry.delete(0,END)
            DivXEntry.insert(0, DivX)
    except:
        DivXEntry.delete(0,END)
        DivXEntry.insert(0, DivX)
    FOff = 25
    MulX = (DivX*SAMPLErate)/(100*FOff)
    while MulX > MaxETSrecord:
        FOff = FOff + 5
        MulX = (DivX*SAMPLErate)/(100*FOff)
    FOff = 0 - FOff
    SRstring = "Rec Len Mul = "  + str(MulX) + " samples"
    MulXEntry.config(text = SRstring) # change displayed value
    SRstring = "Offset = "  + str(FOff) + " samples"
    FOffEntry.config(text = SRstring) # change displayed value
    baseFreq = SAMPLErate/DivX
    try:
        FMul = float(eval(FminEntry.get()))
        if FMul < 1:
            FMul = 1
            FminEntry.delete(0,END)
            FminEntry.insert(0, int(FMul))
        if FMul > 75:
            FMul = 75
            FminEntry.delete(0,END)
            FminEntry.insert(0, int(FMul))
    except:
        FminEntry.delete(0,END)
        FminEntry.insert(0, int(FMul))
    Fmin = baseFreq * FMul
    SRstring = "Multiplied Freq = "  + ' {0:.1f} '.format(Fmin) + " Hz"
    FminDisp.config(text = SRstring) # change displayed value
    SRstring = "Base Frequency = "  + ' {0:.2f} '.format(baseFreq) + " Hz"
    eqivsamplerate.config(text = SRstring) # change displayed value
#
def Settingsscroll(event):
    onTextScroll(event)
    SettingsUpdate()
#
def MakeSettingsMenu():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, SettingsDisp, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon
    global AWG_Amp_Mode
    global CHA_RC_HP, CHB_RC_HP, CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry

    if SettingsStatus.get() == 0:
        Settingswindow = Toplevel()
        Settingswindow.title("Settings " + RevDate)
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
        AwgAmplrb1 = Radiobutton(frame1, text="AWG Min/Max", variable=AWG_Amp_Mode, value=0, command=UpdateAWGWin)
        AwgAmplrb1.grid(row=6, column=0, sticky=W)
        AwgAmplrb2 = Radiobutton(frame1, text="AWG Amp/Off", variable=AWG_Amp_Mode, value=1, command=UpdateAWGWin)
        AwgAmplrb2.grid(row=6, column=1, sticky=W)
        #
        cha_Rcomplab = Label(frame1, text="CHA Comp, TC1 in uSec, A1", style= "A10B.TLabel") # in micro seconds
        cha_Rcomplab.grid(row=7, column=0, sticky=W)
        cha_RcomplabMode = Frame( frame1 )
        cha_RcomplabMode.grid(row=7, column=1, sticky=W)
        cha_TC1Entry = Entry(cha_RcomplabMode, width=4)
        cha_TC1Entry.bind('<MouseWheel>', Settingsscroll)
        cha_TC1Entry.bind('<Key>', onTextKey)
        cha_TC1Entry.pack(side=LEFT)
        cha_TC1Entry.delete(0,"end")
        cha_TC1Entry.insert(0,CHA_TC1.get())
        cha_A1Entry = Entry(cha_RcomplabMode, width=4)
        cha_A1Entry.bind('<MouseWheel>', Settingsscroll)
        cha_A1Entry.bind('<Key>', onTextKey)
        cha_A1Entry.pack(side=LEFT)
        cha_A1Entry.delete(0,"end")
        cha_A1Entry.insert(0,CHA_A1.get())
        #
        cha_Ccomplab = Label(frame1, text="CHA Comp, TC2 in uSec, A2", style= "A10B.TLabel") # in micro seconds
        cha_Ccomplab.grid(row=8, column=0, sticky=W)
        cha_CcomplabMode = Frame( frame1 )
        cha_CcomplabMode.grid(row=8, column=1, sticky=W)
        cha_TC2Entry = Entry(cha_CcomplabMode, width=4)
        cha_TC2Entry.bind('<MouseWheel>', Settingsscroll)
        cha_TC2Entry.bind('<Key>', onTextKey)
        cha_TC2Entry.pack(side=LEFT)
        cha_TC2Entry.delete(0,"end")
        cha_TC2Entry.insert(0,CHA_TC2.get())
        cha_A2Entry = Entry(cha_CcomplabMode, width=4)
        cha_A2Entry.bind('<MouseWheel>', Settingsscroll)
        cha_A2Entry.bind('<Key>', onTextKey)
        cha_A2Entry.pack(side=LEFT)
        cha_A2Entry.delete(0,"end")
        cha_A2Entry.insert(0,CHA_A2.get())
        #
        chb_Rcomplab = Label(frame1, text="CHB Comp, TC1 in uSec, A1", style= "A10B.TLabel") # in micro seconds
        chb_Rcomplab.grid(row=9, column=0, sticky=W)
        chb_RcomplabMode = Frame( frame1 )
        chb_RcomplabMode.grid(row=9, column=1, sticky=W)
        chb_TC1Entry = Entry(chb_RcomplabMode, width=4)
        chb_TC1Entry.bind('<MouseWheel>', Settingsscroll)
        chb_TC1Entry.bind('<Key>', onTextKey)
        chb_TC1Entry.pack(side=LEFT)
        chb_TC1Entry.delete(0,"end")
        chb_TC1Entry.insert(0,CHB_TC1.get())
        chb_A1Entry = Entry(chb_RcomplabMode, width=4)
        chb_A1Entry.bind('<MouseWheel>', Settingsscroll)
        chb_A1Entry.bind('<Key>', onTextKey)
        chb_A1Entry.pack(side=LEFT)
        chb_A1Entry.delete(0,"end")
        chb_A1Entry.insert(0,CHB_A1.get())
        #
        chb_Ccomplab = Label(frame1, text="CHB Comp, TC2 in uSec, A2", style= "A10B.TLabel") # in micro seconds
        chb_Ccomplab.grid(row=10, column=0, sticky=W)
        chb_CcomplabMode = Frame( frame1 )
        chb_CcomplabMode.grid(row=10, column=1, sticky=W)
        chb_TC2Entry = Entry(chb_CcomplabMode, width=4)
        chb_TC2Entry.bind('<MouseWheel>', Settingsscroll)
        chb_TC2Entry.bind('<Key>', onTextKey)
        chb_TC2Entry.pack(side=LEFT)
        chb_TC2Entry.delete(0,"end")
        chb_TC2Entry.insert(0,CHB_TC2.get())
        chb_A2Entry = Entry(chb_CcomplabMode, width=4)
        chb_A2Entry.bind('<MouseWheel>', Settingsscroll)
        chb_A2Entry.bind('<Key>', onTextKey)
        chb_A2Entry.pack(side=LEFT)
        chb_A2Entry.delete(0,"end")
        chb_A2Entry.insert(0,CHB_A2.get())
        #
        Settingsdismissbutton = Button(frame1, text="Dismiss", style= "W8.TButton", command=DestroySettings)
        Settingsdismissbutton.grid(row=11, column=0, sticky=W, pady=7)
#
def UpdateAWGWin():

    UpdateAWGA()
    UpdateAWGB()
    
def SettingsUpdate():
    global GridWidth, TRACEwidth, TRACEaverage, Vdiv, HarmonicMarkers, ZEROstuffing, RevDate
    global Settingswindow, SettingsStatus, SettingsDisp, ZSTuff, TAvg, VDivE, TwdthE, GwdthE, HarMon
    global CHA_TC1, CHA_TC2, CHB_TC1, CHB_TC2
    global CHA_A1, CHA_A2, CHB_A1, CHB_A2
    global cha_TC1Entry, cha_TC2Entry, chb_TC1Entry, chb_TC2Entry
    global cha_A1Entry, cha_A2Entry, chb_A1Entry, chb_A2Entry
    
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
    try:
        TC1A = float(cha_TC1Entry.get())
        CHA_TC1.set(TC1A)
        if TC1A < 0:
            TC1A = 0
            cha_TC1Entry.delete(0,END)
            cha_TC1Entry.insert(0, TC1A)
    except:
        cha_TC1Entry.delete(0,END)
        cha_TC1Entry.insert(0, CHA_TC1.get())
    try:
        TC2A = float(cha_TC2Entry.get())
        CHA_TC2.set(TC2A)
        if TC2A < 0:
            TC2A = 0
            cha_TC2Entry.delete(0,END)
            cha_TC2Entry.insert(0, TC2A)
    except:
        cha_TC2Entry.delete(0,END)
        cha_TC2Entry.insert(0, CHA_TC2.get())
    #
    try:
        Gain1A = float(cha_A1Entry.get())
        CHA_A1.set(Gain1A)
        if Gain1A < 0:
            Gain1A = 1
            cha_A1Entry.delete(0,END)
            cha_A1Entry.insert(0, Gain1A)
    except:
        cha_A1Entry.delete(0,END)
        cha_A1Entry.insert(0, CHA_A1.get())
    try:
        Gain2A = float(cha_A2Entry.get())
        CHA_A2.set(Gain2A)
        if Gain2A < 0:
            Gain2A = 0
            cha_A2Entry.delete(0,END)
            cha_A2Entry.insert(0, Gain2A)
    except:
        cha_A2Entry.delete(0,END)
        cha_A2Entry.insert(0, CHA_A2.get())
    #
    try:
        TC1B = float(chb_TC1Entry.get())
        CHB_TC1.set(TC1B)
        if TC1B < 0:
            TC1B = 0
            chb_TC1Entry.delete(0, END)
            chb_TC1Entry.insert(0, TC1B)
    except:
        chb_TC1Entry.delete(0,END)
        chb_TC1Entry.insert(0, CHB_TC1.get())
    try:
        TC2B = float(chb_TC2Entry.get())
        CHB_TC2.set(TC2B)
        if TC2B < 0:
            TC2B = 0
            chb_TC2Entry.delete(0, END)
            chb_TC2Entry.insert(0, TC2B)
    except:
        chb_TC2Entry.delete(0,END)
        chb_TC2Entry.insert(0, CHB_TC2.get())
    #
    try:
        Gain1B = float(chb_A1Entry.get())
        CHB_A1.set(Gain1B)
        if Gain1B < 0:
            Gain1B = 1
            chb_A1Entry.delete(0,END)
            chb_A1Entry.insert(0, Gain1B)
    except:
        chb_A1Entry.delete(0,END)
        chb_A1Entry.insert(0, CHB_A1.get())
    try:
        Gain2B = float(chb_A2Entry.get())
        CHB_A2.set(Gain2B)
        if Gain2B < 0:
            Gain2B = 0
            chb_A2Entry.delete(0,END)
            chb_A2Entry.insert(0, Gain2B)
    except:
        chb_A2Entry.delete(0,END)
        chb_A2Entry.insert(0, CHB_A2.get())
    #
def DestroySettings():
    global Settingswindow, SettingsStatus, SettingsDisp
    
    SettingsStatus.set(0)
    SettingsUpdate()
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
ShowC1_V = IntVar(0)   # curves to display variables
TgEdge = IntVar(0)   # Trigger edge variable
# Show channels variables
ShowC1_V = IntVar(0)   # curves to display variables
ShowC1_I = IntVar(0)
ShowC2_V = IntVar(0)
ShowC2_I = IntVar(0)
ShowAV_I = IntVar(0)
ShowBV_I = IntVar(0)
ShowRA_V = IntVar(0)
ShowRA_I = IntVar(0)
ShowRB_V = IntVar(0)
ShowRB_I = IntVar(0)
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
DecimateOption = IntVar(0)
MathTrace = IntVar(0)
# define vertical measurment variables
MeasDCV1 = IntVar(0)
MeasMinV1 = IntVar(0)
MeasMaxV1 = IntVar(0)
MeasMidV1 = IntVar(0)
MeasPPV1 = IntVar(0)
MeasRMSV1 = IntVar(0)
MeasRMSVA_B = IntVar(0)
MeasDCI1 = IntVar(0)
MeasMinI1 = IntVar(0)
MeasMaxI1 = IntVar(0)
MeasMidI1 = IntVar(0)
MeasPPI1 = IntVar(0)
MeasRMSI1 = IntVar(0)
MeasDiffAB = IntVar(0)
MeasDCV2 = IntVar(0)
MeasMinV2 = IntVar(0)
MeasMaxV2 = IntVar(0)
MeasMidV2 = IntVar(0)
MeasPPV2 = IntVar(0)
MeasRMSV2 = IntVar(0)
MeasDCI2 = IntVar(0)
MeasMinI2 = IntVar(0)
MeasMaxI2 = IntVar(0)
MeasMidI2 = IntVar(0)
MeasPPI2 = IntVar(0)
MeasRMSI2 = IntVar(0)
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
DacScreenStatus = IntVar(0)
DacScreenStatus.set(0)
MuxScreenStatus = IntVar(0)
MuxScreenStatus.set(0)
DualMuxMode = IntVar(0)
MinigenScreenStatus = IntVar(0)
MinigenScreenStatus.set(0)
DA1ScreenStatus = IntVar(0)
DA1ScreenStatus.set(0)
DigPotScreenStatus = IntVar(0)
DigPotScreenStatus.set(0)
GenericSerialStatus = IntVar(0)
GenericSerialStatus.set(0)
AD5626SerialStatus = IntVar(0)
AD5626SerialStatus.set(0)
DigFiltStatus = IntVar(0)
DigFiltStatus.set(0)
CommandStatus = IntVar(0)
CommandStatus.set(0)
MeasureStatus = IntVar(0)
MeasureStatus.set(0)
MarkerScale = IntVar(0)
MarkerScale.set(1)
SettingsStatus = IntVar(0)
CHA_RC_HP = IntVar(0)
CHB_RC_HP = IntVar(0)
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
root.style.configure("PwrOff.TButton", background="red", width=7, relief=RAISED)
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
root.style.configure("Rtrace6.TButton", background=COLORtrace6, width=7, relief=RAISED)
root.style.configure("Strace6.TButton", background=COLORtrace6, width=7, relief=SUNKEN)
root.style.configure("Rtrace7.TButton", background=COLORtrace7, width=7, relief=RAISED)
root.style.configure("Strace7.TButton", background=COLORtrace7, width=7, relief=SUNKEN)
root.style.configure("RGray.TButton", background="#808080", width=7, relief=RAISED)
root.style.configure("SGray.TButton", background="#808080", width=7, relief=SUNKEN)
root.style.configure("A10R1.TLabelframe.Label", foreground=COLORtraceR1, font=('Arial', 10, 'bold'))
root.style.configure("A10R1.TLabelframe", borderwidth=5, relief=RIDGE)
root.style.configure("A10R2.TLabelframe.Label", foreground=COLORtraceR2, font=('Arial', 10, 'bold'))
root.style.configure("A10R2.TLabelframe", borderwidth=5, relief=RIDGE)
root.style.configure("A10B.TLabel", foreground=COLORcanvas, font="Arial 10 bold") # Black text
root.style.configure("A10R.TLabel", foreground="red", font="Arial 10 bold") # Red text
root.style.configure("A10G.TLabel", foreground="green", font="Arial 10 bold") # Red text
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
Triggermenu.menu.add_radiobutton(label='CA-V', variable=TgInput, value=1)
Triggermenu.menu.add_radiobutton(label='CA-I', variable=TgInput, value=2)
Triggermenu.menu.add_radiobutton(label='CB-V', variable=TgInput, value=3)
Triggermenu.menu.add_radiobutton(label='CB-I', variable=TgInput, value=4)
Triggermenu.menu.add_checkbutton(label='Auto Level', variable=AutoLevel)
Triggermenu.menu.add_checkbutton(label='SingleShot', variable=SingleShot)
Triggermenu.pack(side=LEFT)
#
Edgemenu = Menubutton(frame1, text="Edge", style="W5.TButton")
Edgemenu.menu = Menu(Edgemenu, tearoff = 0 )
Edgemenu["menu"]  = Edgemenu.menu
Edgemenu.menu.add_radiobutton(label='Rising [+]', variable=TgEdge, value=0)
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
HozPossentry = Entry(frame1, width=4)
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
PwrBt = Button(frame1, text="PWR-ON", style="Pwr.TButton", command=BPower)
PwrBt.pack(side=RIGHT)
# Curves Menu
Showmenu = Menubutton(frame1, text="Curves", style="W7.TButton")
Showmenu.menu = Menu(Showmenu, tearoff = 0 )
Showmenu["menu"] = Showmenu.menu
Showmenu.menu.add_command(label="-Show-", foreground="blue", command=donothing)
Showmenu.menu.add_command(label="All", command=BShowCurvesAll)
Showmenu.menu.add_command(label="None", command=BShowCurvesNone)
Showmenu.menu.add_checkbutton(label='CA-V [1]', variable=ShowC1_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='CA-I [3]', variable=ShowC1_I, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='CB-V [2]', variable=ShowC2_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='CB-I [4]', variable=ShowC2_I, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='Math-X', variable=Show_MathX, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='Math-Y', variable=Show_MathY, command=UpdateTimeTrace)
Showmenu.menu.add_command(label="-Auto Vert Center-", foreground="blue", command=donothing)
Showmenu.menu.add_checkbutton(label='CA-V', variable=AutoCenterA)
Showmenu.menu.add_checkbutton(label='CB-V', variable=AutoCenterB)
Showmenu.menu.add_command(label="-Input HP Comp-", foreground="blue", command=donothing)
Showmenu.menu.add_checkbutton(label='CA-V', variable=CHA_RC_HP)
Showmenu.menu.add_checkbutton(label='CB-V', variable=CHB_RC_HP)
Showmenu.menu.add_separator()  
Showmenu.menu.add_checkbutton(label='RA-V', variable=ShowRA_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='RA-I', variable=ShowRA_I, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='RB-V', variable=ShowRB_V, command=UpdateTimeTrace)
Showmenu.menu.add_checkbutton(label='RB-I', variable=ShowRB_I, command=UpdateTimeTrace)
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
    pwrbt_tip = CreateToolTip(PwrBt, 'Toggle ext power supply')
    Showmenu_tip = CreateToolTip(Showmenu, 'Select which traces to display')
# Time per Div
TMsb = Spinbox(frame1, width=5, values= TMpdiv, command=BTime)
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
ca.bind("<space>", onCanvasSpaceBar)
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
bcon = Button(dropmenu, text="Recon", style="RConn.TButton", command=ConnectDevice)
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
Filemenu.menu.add_command(label="Save PWL Data", command=BSaveChannelData)
Filemenu.menu.add_command(label="Help", command=BHelp)
Filemenu.menu.add_command(label="About", command=BAbout)
Filemenu.pack(side=LEFT, anchor=W)
# Options Menu
Optionmenu = Menubutton(dropmenu, text="Options", style="W7.TButton")
Optionmenu.menu = Menu(Optionmenu, tearoff = 0 )
Optionmenu["menu"]  = Optionmenu.menu
Optionmenu.menu.add_command(label='Change Settings', command=MakeSettingsMenu)
Optionmenu.menu.add_command(label='Set Sample Rate', command=SetSampleRate)
Optionmenu.menu.add_checkbutton(label='Smooth', variable=SmoothCurves, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Z-O-Hold', variable=ZOHold, command=UpdateTimeTrace)
Optionmenu.menu.add_checkbutton(label='Decimate', variable=DecimateOption)
Optionmenu.menu.add_checkbutton(label='Trace Avg [a]', variable=TRACEmodeTime)
Optionmenu.menu.add_checkbutton(label='Persistance', variable=ScreenTrefresh)
Optionmenu.menu.add_command(label='Set Marker Location', command=BSetMarkerLocation)
Optionmenu.menu.add_command(label="SnapShot [s]", command=BSnapShot)
Optionmenu.menu.add_radiobutton(label='Black BG', variable=ColorMode, value=0, command=BgColor)
Optionmenu.menu.add_radiobutton(label='White BG', variable=ColorMode, value=1, command=BgColor)
Optionmenu.menu.add_command(label="Run Self Cal", command=SelfCalibration)
if AllowFlashFirmware == 1:
    Optionmenu.menu.add_command(label="Update Firmware", command=UpdateFirmware)
Optionmenu.pack(side=LEFT, anchor=W)
#
dropmenu2 = Frame( frame2r )
dropmenu2.pack(side=TOP)
# Open Math trace menu
mathbt = Button(dropmenu2, text="Math", style="W4.TButton", command = NewEnterMathControls)
mathbt.pack(side=RIGHT, anchor=W)
# Measurments menu
measlab = Label(dropmenu2, text="Meas")
measlab.pack(side=LEFT, anchor=W)
MeasmenuA = Menubutton(dropmenu2, text="CA", style="W3.TButton")
MeasmenuA.menu = Menu(MeasmenuA, tearoff = 0 )
MeasmenuA["menu"]  = MeasmenuA.menu
MeasmenuA.menu.add_command(label="-CA-V-", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=MeasDCV1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=MeasMinV1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=MeasMaxV1)
MeasmenuA.menu.add_checkbutton(label='Base', variable=MeasBaseV1)
MeasmenuA.menu.add_checkbutton(label='Top', variable=MeasTopV1)
MeasmenuA.menu.add_checkbutton(label='Mid', variable=MeasMidV1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=MeasPPV1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=MeasRMSV1)
MeasmenuA.menu.add_checkbutton(label='CA-CB', variable=MeasDiffAB)
MeasmenuA.menu.add_checkbutton(label='CA-CB RMS', variable=MeasRMSVA_B)
MeasmenuA.menu.add_checkbutton(label='User', variable=MeasUserA, command=BUserAMeas)
MeasmenuA.menu.add_separator()
#
MeasmenuA.menu.add_command(label="-CA-I-", command=donothing)
MeasmenuA.menu.add_checkbutton(label='Avg', variable=MeasDCI1)
MeasmenuA.menu.add_checkbutton(label='Min', variable=MeasMinI1)
MeasmenuA.menu.add_checkbutton(label='Max', variable=MeasMaxI1)
MeasmenuA.menu.add_checkbutton(label='Mid', variable=MeasMidI1)
MeasmenuA.menu.add_checkbutton(label='P-P', variable=MeasPPI1)
MeasmenuA.menu.add_checkbutton(label='RMS', variable=MeasRMSI1)
MeasmenuA.menu.add_separator()
#
MeasmenuA.menu.add_command(label="CA-Time", command=donothing)
MeasmenuA.menu.add_checkbutton(label='H-Width', variable=MeasAHW)
MeasmenuA.menu.add_checkbutton(label='L-Width', variable=MeasALW)
MeasmenuA.menu.add_checkbutton(label='DutyCyle', variable=MeasADCy)
MeasmenuA.menu.add_checkbutton(label='Period', variable=MeasAPER)
MeasmenuA.menu.add_checkbutton(label='Freq', variable=MeasAFREQ)
MeasmenuA.menu.add_checkbutton(label='A-B Phase', variable=MeasPhase)
#
MeasmenuA.pack(side=LEFT)
#
MeasmenuB = Menubutton(dropmenu2, text="CB", style="W3.TButton")
MeasmenuB.menu = Menu(MeasmenuB, tearoff = 0 )
MeasmenuB["menu"]  = MeasmenuB.menu
MeasmenuB.menu.add_command(label="-CB-V-", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=MeasDCV2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=MeasMinV2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=MeasMaxV2)
MeasmenuB.menu.add_checkbutton(label='Base', variable=MeasBaseV2)
MeasmenuB.menu.add_checkbutton(label='Top', variable=MeasTopV2)
MeasmenuB.menu.add_checkbutton(label='Mid', variable=MeasMidV2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=MeasPPV2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=MeasRMSV2)
MeasmenuB.menu.add_checkbutton(label='CB-CA', variable=MeasDiffBA)
MeasmenuB.menu.add_checkbutton(label='User', variable=MeasUserB, command=BUserBMeas)
MeasmenuB.menu.add_separator()
#
MeasmenuB.menu.add_command(label="-CB-I-", command=donothing)
MeasmenuB.menu.add_checkbutton(label='Avg', variable=MeasDCI2)
MeasmenuB.menu.add_checkbutton(label='Min', variable=MeasMinI2)
MeasmenuB.menu.add_checkbutton(label='Max', variable=MeasMaxI2)
MeasmenuB.menu.add_checkbutton(label='Mid', variable=MeasMidI2)
MeasmenuB.menu.add_checkbutton(label='P-P', variable=MeasPPI2)
MeasmenuB.menu.add_checkbutton(label='RMS', variable=MeasRMSI2)
MeasmenuB.menu.add_separator()
#
MeasmenuB.menu.add_command(label="CB-Time", command=donothing)
MeasmenuB.menu.add_checkbutton(label='H-Width', variable=MeasBHW)
MeasmenuB.menu.add_checkbutton(label='L-Width', variable=MeasBLW)
MeasmenuB.menu.add_checkbutton(label='DutyCyle', variable=MeasBDCy)
MeasmenuB.menu.add_checkbutton(label='Period', variable=MeasBPER)
MeasmenuB.menu.add_checkbutton(label='Freq', variable=MeasBFREQ)
MeasmenuB.menu.add_checkbutton(label='B-A Delay', variable=MeasDelay)
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
    math_tip = CreateToolTip(mathbt, 'Open Math window')
    BuildAWGScreen_tip = CreateToolTip(BuildAWGScreen, 'Surface AWG Controls window')
    BuildXYScreen_tip = CreateToolTip(BuildXYScreen, 'Open X vs Y plot window')
    BuildSpectrumScreen_tip = CreateToolTip(BuildSpectrumScreen, 'Open spectrum analyzer window')
    BuildBodeScreen_tip = CreateToolTip(BuildBodeScreen, 'Open Bode plot window')
    BuildIAScreen_tip = CreateToolTip(BuildIAScreen, 'Open Impedance analyzer window')
    BuildOhmScreen_tip = CreateToolTip(BuildOhmScreen, 'Open DC Ohmmeter window')
# Digital Input / Output Option screens
DigScreenStatus = IntVar(0)
DigScreenStatus.set(0)
BuildDigScreen = Button(frame2r, text="Digital I/O Screen", style="W17.TButton", command=MakeDigScreen)
BuildDigScreen.pack(side=TOP)
#
BuildDacScreen = Button(frame2r, text="PIO-DAC Screen", style="W17.TButton", command=MakeDacScreen)
BuildDacScreen.pack(side=TOP)
# Optional plugin cards
if EnableMuxMode > 0:
    BuildMuxScreen = Button(frame2r, text="Analog In Mux Screen", style="W17.TButton", command=MakeMuxModeWindow)
    BuildMuxScreen.pack(side=TOP)
if EnableMinigenMode > 0:
    BuildMinigenScreen = Button(frame2r, text="MiniGen Screen", style="W17.TButton", command=MakeMinigenWindow)
    BuildMinigenScreen.pack(side=TOP)
if EnablePmodDA1Mode > 0:
    BuildDA1Screen = Button(frame2r, text="PMOD DA1 Screen", style="W17.TButton", command=MakeDA1Window)
    BuildDA1Screen.pack(side=TOP)
if EnableDigPotMode >0:
    BuildDigPotScreen = Button(frame2r, text="Dig Pot Screen", style="W17.TButton", command=MakeDigPotWindow)
    BuildDigPotScreen.pack(side=TOP)
if EnableGenericSerialMode >0:
    GenericSerialScreen = Button(frame2r, text="Generic Serial Output", style="W17.TButton", command=MakeGenericSerialWindow)
    GenericSerialScreen.pack(side=TOP)
if EnableAD5626SerialMode >0:
    AD5626SerialScreen = Button(frame2r, text="AD5626 Output", style="W17.TButton", command=MakeAD5626Window)
    AD5626SerialScreen.pack(side=TOP)
if EnableDigitalFilter >0:
    DigFiltScreen = Button(frame2r, text="Digital Filter", style="W17.TButton", command=MakeDigFiltWindow)
    DigFiltScreen.pack(side=TOP)
if EnableCommandInterface > 0:
    CommandLineScreen = Button(frame2r, text="Command Interface", style="W17.TButton", command=MakeCommandScreen)
    CommandLineScreen.pack(side=TOP)
if EnableMeasureScreen > 0:
    MeasureScreen = Button(frame2r, text="Measure Screen", style="W17.TButton", command=MakeMeasureScreen)
    MeasureScreen.pack(side=TOP)
if EnableETSScreen > 0:
    ETSScreen = Button(frame2r, text="ETS Controls", style="W17.TButton", command=MakeETSWindow)
    ETSScreen.pack(side=TOP)
# input probe wigets
prlab = Label(frame2r, text="Adjust Gain / Offset")
prlab.pack(side=TOP)
# Input Probes sub frame 
ProbeA = Frame( frame2r )
ProbeA.pack(side=TOP)
gain1lab = Label(ProbeA, text="CA-V")
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
gain2lab = Label(ProbeB, text="CB-V")
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
#
ProbeAI = Frame( frame2r )
ProbeAI.pack(side=TOP)
gainailab = Label(ProbeAI, text="CA-I")
gainailab.pack(side=LEFT)
CHAIGainEntry = Entry(ProbeAI, width=5)
CHAIGainEntry.bind('<MouseWheel>', onTextScroll)
CHAIGainEntry.bind('<Key>', onTextKey)
CHAIGainEntry.pack(side=LEFT)
CHAIGainEntry.delete(0,"end")
CHAIGainEntry.insert(0,1.0)
CHAIOffsetEntry = Entry(ProbeAI, width=5)
CHAIOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAIOffsetEntry.bind('<Key>', onTextKey)
CHAIOffsetEntry.pack(side=LEFT)
CHAIOffsetEntry.delete(0,"end")
CHAIOffsetEntry.insert(0,0.0)
#
ProbeBI = Frame( frame2r )
ProbeBI.pack(side=TOP)
gainbilab = Label(ProbeBI, text="CB-I")
gainbilab.pack(side=LEFT)
CHBIGainEntry = Entry(ProbeBI, width=5)
CHBIGainEntry.bind('<MouseWheel>', onTextScroll)
CHBIGainEntry.bind('<Key>', onTextKey)
CHBIGainEntry.pack(side=LEFT)
CHBIGainEntry.delete(0,"end")
CHBIGainEntry.insert(0,1.0)
CHBIOffsetEntry = Entry(ProbeBI, width=5)
CHBIOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBIOffsetEntry.bind('<Key>', onTextKey)
CHBIOffsetEntry.pack(side=LEFT)
CHBIOffsetEntry.delete(0,"end")
CHBIOffsetEntry.insert(0,0.0)
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
ADI1 = Label(frame2r, image=logo, anchor= "sw", compound="top") # , height=49, width=116
ADI1.pack(side=TOP)

# Bottom Buttons
# Voltage channel A
CHAsb = Spinbox(frame3, width=4, values=CHvpdiv, command=BCHAlevel)
CHAsb.bind('<MouseWheel>', onSpinBoxScroll)
CHAsb.pack(side=LEFT)
CHAsb.delete(0,"end")
CHAsb.insert(0,0.5)
#
CHAlab = Button(frame3, text="CA V/Div", style="Rtrace1.TButton", command=SetScaleA)
CHAlab.pack(side=LEFT)

CHAVPosEntry = Entry(frame3, width=5)
CHAVPosEntry.bind("<Return>", BOffsetA)
CHAVPosEntry.bind('<MouseWheel>', onTextScroll)
CHAVPosEntry.bind('<Key>', onTextKey)
CHAVPosEntry.pack(side=LEFT)
CHAVPosEntry.delete(0,"end")
CHAVPosEntry.insert(0,2.5)
CHAofflab = Button(frame3, text="CA V Pos", style="Rtrace1.TButton", command=SetVAPoss)
CHAofflab.pack(side=LEFT)
# Current channel A
CHAIsb = Spinbox(frame3, width=4, values=CHipdiv, command=BCHAIlevel)
CHAIsb.bind('<MouseWheel>', onSpinBoxScroll)
CHAIsb.pack(side=LEFT)
CHAIsb.delete(0,"end")
CHAIsb.insert(0,50.0)
CHAIlab = Button(frame3, text="CA mA/Div", style="Strace3.TButton", command=SetScaleIA)
CHAIlab.pack(side=LEFT)

CHAIPosEntry = Entry(frame3, width=5)
CHAIPosEntry.bind("<Return>", BIOffsetA)
CHAIPosEntry.bind('<MouseWheel>', onTextScroll)
CHAIPosEntry.bind('<Key>', onTextKey)
CHAIPosEntry.pack(side=LEFT)
CHAIPosEntry.delete(0,"end")
CHAIPosEntry.insert(0,0.0)
CHAIofflab = Button(frame3, text="CA I Pos", style="Rtrace3.TButton", command=SetIAPoss)
CHAIofflab.pack(side=LEFT)
# Voltage channel B
CHBsb = Spinbox(frame3, width=4, values=CHvpdiv, command=BCHBlevel)
CHBsb.bind('<MouseWheel>', onSpinBoxScroll)
CHBsb.pack(side=LEFT)
CHBsb.delete(0,"end")
CHBsb.insert(0,0.5)
#
CHBlab = Button(frame3, text="CB V/Div", style="Strace2.TButton", command=SetScaleB)
CHBlab.pack(side=LEFT)

CHBVPosEntry = Entry(frame3, width=5)
CHBVPosEntry.bind("<Return>", BOffsetB)
CHBVPosEntry.bind('<MouseWheel>', onTextScroll)
CHBVPosEntry.bind('<Key>', onTextKey)
CHBVPosEntry.pack(side=LEFT)
CHBVPosEntry.delete(0,"end")
CHBVPosEntry.insert(0,2.5)
CHBofflab = Button(frame3, text="CB V Pos", style="Rtrace2.TButton", command=SetVBPoss)
CHBofflab.pack(side=LEFT)
# Current channel B
CHBIsb = Spinbox(frame3, width=4, values=CHipdiv, command=BCHBIlevel)
CHBIsb.bind('<MouseWheel>', onSpinBoxScroll)
CHBIsb.pack(side=LEFT)
CHBIsb.delete(0,"end")
CHBIsb.insert(0,50.0)
CHBIlab = Button(frame3, text="CB mA/Div", style="Strace4.TButton", command=SetScaleIB)
CHBIlab.pack(side=LEFT)

CHBIPosEntry = Entry(frame3, width=5)
CHBIPosEntry.bind("<Return>", BIOffsetB)
CHBIPosEntry.bind('<MouseWheel>', onTextScroll)
CHBIPosEntry.bind('<Key>', onTextKey)
CHBIPosEntry.pack(side=LEFT)
CHBIPosEntry.delete(0,"end")
CHBIPosEntry.insert(0,0.0)
CHBIofflab = Button(frame3, text="CB I Pos", style="Rtrace4.TButton", command=SetIBPoss)
CHBIofflab.pack(side=LEFT)
#
if ShowBallonHelp > 0:
    CHAlab_tip = CreateToolTip(CHAlab, 'Select CHA-V vertical range/position axis to be used for markers and drawn color')
    CHBlab_tip = CreateToolTip(CHBlab, 'Select CHB-V vertical range/position axis to be used for markers and drawn color')
    CHAIlab_tip = CreateToolTip(CHAIlab, 'Select CHA-I vertical range/position axis to be used for markers and drawn color')
    CHBIlab_tip = CreateToolTip(CHBIlab, 'Select CHB-I vertical range/position axis to be used for markers and drawn color')
    CHAofflab_tip = CreateToolTip(CHAofflab, 'Set CHA-V position to DC average of signal')
    CHBofflab_tip = CreateToolTip(CHBofflab, 'Set CHB-V position to DC average of signal')
    CHAIofflab_tip = CreateToolTip(CHAIofflab, 'Set CHA-I position to DC average of signal')
    CHBIofflab_tip = CreateToolTip(CHBIofflab, 'Set CHB-I position to DC average of signal')
#
root.geometry('+300+0')
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
#===== Initalize device ======
if not numpy_found:
    root.update()
    showwarning("WARNING","Numpy not found!")
    root.destroy()
    exit()
#
BrdSel = IntVar(0)
BoardStatus = IntVar(0)
if pysmu_found:
    ConnectDevice()
    #session.hotplug_attach(ConnectDevice)
    #session.hotplug_detach(ConnectDevice)
    MakeAWGWindow() # always build AWG window
    BLoadConfig("alice-last-config.cfg") # load configuration from last session
# ================ Call main routine ===============================
    root.update()               # Activate updated screens
#
# Start sampling
    Analog_In()
else:
    root.update()
    showwarning("WARNING","Pysmu not found!")
    root.destroy()
    exit()

