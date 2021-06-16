#!/usr/bin/python
# ADALM1000 DC Ohmmeter Tool RR 6-6-2021
# For pysmu ( libsmu.rework > = 1.0 )
# For Python version > 3.7
# RobotRaconteur requires Python > 3.7 
import __future__
import os
import sys
from RobotRaconteur.Client import *

NetAddr = "localhost" # default network address string
InitFileName = "ohm_eter_init.ini"

if sys.version_info[0] == 2:
    print ("Python 2.x")
    from Tkinter import *
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
    from tkSimpleDialog import askstring
    from tkMessageBox import *
if sys.version_info[0] == 3:
    from tkinter import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    from tkinter.simpledialog import askstring
    print ("Python 3.x")
import time
#
## Check if there is an analog_meter_init.ini file to read in
try:
    InitFile = open(InitFileName) # "analog_meter_init.ini"
    for line in InitFile:
        try:
            exec( line.rstrip() )
        except:
            print("Skiping " + line.rstrip()) 
    InitFile.close()
except:
    print( "No Init File Read. " + InitFileName + " Not Found")
#
# define button actions
loopnum = 0
RevDate = "6 June 2021)"

def EnabAwg():
    global chatestv, CHATestVEntry
    try:
        chatestv = float(eval(CHATestVEntry.get()))
        if chatestv > 5.0:
            chatestv = 5.0
            CHATestVEntry.delete(0,END)
            CHATestVEntry.insert(0, chatestv)
    except:
        CHATestVEntry.delete(0,END)
        CHATestVEntry.insert(0, chatestv)
    #
    if RMode.get() == 0:
        m1k_obj.setchanterm('B', 'GND', 'OPEN') # set CHB GND switch to open
    else:
        m1k_obj.setchanterm('B', 'GND', 'CLOSED') # set CHB GND switch to closed
    #
    m1k_obj.setawgconstant('A', chatestv)
    m1k_obj.setmode('A', 'SVMI')
    m1k_obj.setmode('B', 'HI_Z')
    
def Analog_in():
    # global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global InOffA, InGainA, InOffB, InGainB
    global session, DevID, devx, loopnum
    global RMode, Diodelabel, labelA0, labelA1

    while (True):       # Main loop
        if (RUNstatus.get() == 1):
            #
            #print "entered loop with RUNstatus.get() == 1"
            if not m1k_obj.IsContinuous():
                m1k_obj.FlushSession()
                m1k_obj.StartSession()
                #print "starting session inside analog in"
                time.sleep(0.02)
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
                CurOffA = float(eval(CHAIOffsetEntry.get()))
            except:
                CHAIOffsetEntry.delete(0,END)
                CHAIOffsetEntry.insert(0, CurOffA)
            try:
                CurGainA = float(eval(CHAIGainEntry.get()))
            except:
                CHAIGainEntry.delete(0,END)
                CHAIGainEntry.insert(0, CurGainA)
            try:
                CurOffB = float(eval(CHBIOffsetEntry.get()))
            except:
                CHBIOffsetEntry.delete(0,END)
                CHBIOffsetEntry.insert(0, CurOffB)
            try:
                CurGainB = float(eval(CHBIGainEntry.get()))
            except:
                CHBIGainEntry.delete(0,END)
                CHBIGainEntry.insert(0, CurGainB)
            #
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
            
            if RMode.get() == 0:
                m1k_obj.setchanterm('B', 'GND', 'OPEN') # set CHB GND switch to open
            else:
                m1k_obj.setchanterm('B', 'GND', 'CLOSED') # set CHB GND switch to closed
            #
            if m1k_obj.IsContinuous():
                samples = m1k_obj.ContRead(200)
            # get_samples returns a list of values for voltage [0] and current [1]
            for sample in samples: # calculate average
                DCVA0 += sample.A[0] # VAdata # Sum for average CA voltage 
                DCVB0 += sample.B[0] # VBdata # Sum for average CB voltage
                DCIA0 += sample.A[1] # Sum for average CA current 
                DCIB0 += sample.B[1] # Sum for average CB current 

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
                String = "Forward Voltage " + ' {0:.3f} '.format(DCVB0) + " V"
            else: # use internal 50 ohm resistor
                DCR = chatestr * ((DCVA0-DCVB0)/DCVB0)
                String = "Forward Voltage " + ' {0:.3f} '.format(DCVA0-DCVB0) + " V"
            Diodelabel.config(text = String) # change displayed value
            DCR = abs(DCR)
            if DCR < 1000:
                String = "Ohms " + ' {0:.2f} '.format(DCR) # format with 2 decimal places
            else:
                String = "KOhms " + ' {0:.3f} '.format(DCR/1000) # divide by 1000 and format with 3 decimal places
            labelA0.config(text = String) # change displayed value
            String = "Meas " + ' {0:.2f} '.format(DCIA0) + " mA " + ' {0:.2f} '.format(DCVA0) + " V"
            labelAI.config(text = String) # change displayed value
#
            #time.sleep(0.1)
            loopnum = loopnum + 1
            # m1k_obj.setchanterm('B', 'GND', 'OPEN') # set CHB GND switch to open
# Update tasks and screens by TKinter
        else:
            if loopnum > 0:
                # print "stop"
                # session.end()
                m1k_obj.setmode('A','HI_Z') # Put CHA in Hi Z mode
                m1k_obj.setmode('B','HI_Z') # Put CHB in Hi Z mode
                loopnum = 0
#
        root.update_idletasks()
        root.update()            

## Nop
def donothing():
    global RUNstatus
## Another Nop
def DoNothing(event):
    global RUNstatus
#
def BSaveCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
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
    CalFile.write('CHAIGainEntry.delete(0,END)\n')
    CalFile.write('CHAIGainEntry.insert(4, ' + CHAIGainEntry.get() + ')\n')
    CalFile.write('CHBIGainEntry.delete(0,END)\n')
    CalFile.write('CHBIGainEntry.insert(4, ' + CHBIGainEntry.get() + ')\n')
    CalFile.write('CHAIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAIOffsetEntry.insert(4, ' + CHAIOffsetEntry.get() + ')\n')
    CalFile.write('CHBIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBIOffsetEntry.insert(4, ' + CHBIOffsetEntry.get() + ')\n')
    #
    CalFile.close()

def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global DevID

    devidstr = DevID[17:31]
    filename = devidstr + "_O.cal" # first try reading from Ohmmeter tool cal file
    try:
        CalFile = open(filename)
        for line in CalFile:
            try:
                exec( line.rstrip() )
            except:
                print( "Skipping " + line.rstrip())
        CalFile.close()
    except:
        filename = devidstr + "_V.cal" # else try reading from Voltmeter tool cal file
        try:
            CalFile = open(filename)
            for line in CalFile:
                try:
                    exec( line.rstrip() )
                except:
                    print( "Skipping " + line.rstrip())
            CalFile.close()
        except:
            print( "Cal file(s) for this device not found")
#
def onTextScroll(event):   # Use mouse wheel to scroll entry values, august 7
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
    else:
        Step = 10**(Dot - Pos + 1)
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta == -120:
        NewVal = OldValfl - Step
    if event.num == 4 or event.delta == 120:
        NewVal = OldValfl + Step
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
def UpdateAwgCont():
    global RUNstatus
    # if running and in continuous streaming mode temp stop, flush buffer and restart to change AWG settings
    if RUNstatus.get() == 1:
        if m1k_obj.IsContinuous():
            #print "About to change awg and Stopping continuous mode"
            m1k_obj.EndSession()
            #time.sleep(0.02) # wait awhile here for some reason
            #print session.continuous
            if not m1k_obj.IsContinuous():
                EnabAwg() # set-up new AWG settings
                #print "Just changed awg and Starting continuous mode"
                #time.sleep(0.02)
                m1k_obj.StartSession()
                #time.sleep(0.02)
    #else:
        #EnabAwg() # set-up new AWG settings
#
def onAWGscroll(event):
    
    onTextScroll(event)
    UpdateAwgCont()
#
#
def BStart():
    global RUNstatus, devx, DevID, FWRevOne, session, chatestv

    time.sleep(0.01)
    RUNstatus.set(1)
    if not m1k_obj.IsContinuous():
        #print "Run Is Not Continuous? ", session.continuous
        m1k_obj.FlushSession()
        m1k_obj.StartSession()
        UpdateAwgCont()
        #time.sleep(0.02)
        
    else:
        #print "Run Is Continuous? ", session.continuous
        UpdateAwgCont()
        m1k_obj.FlushSession()
        #time.sleep(0.02)
        #print "Starting continuous mode"
    
#
def BStop():
    global RUNstatus, session, CHA, CHB
    
    RUNstatus.set(0)
    # print "Stoping continuous mode"
    # session.cancel() # cancel continuous session mode while paused
    if m1k_obj.IsContinuous():
        # print ("Is Continuous? ", m1k_obj.IsContinuous())
        #time.sleep(0.02)
        m1k_obj.setmode('A','HI_Z_SPLIT')
        m1k_obj.setmode('B','HI_Z_SPLIT')
        m1k_obj.setawgconstant('A', 0.0)
        m1k_obj.setawgconstant('B', 0.0)
        #time.sleep(0.01)
        #print "Stoping continuous mode"
        #print "Is Continuous? ", session.continuous
    #else:
        #session.cancel()
    
def Bcloseexit():
    global RUNstatus
    
    RUNstatus.set(0)
    # BSaveConfig("alice-last-config.cfg")
    try:
        # Put channels in Hi-Z and exit
        m1k_obj.setmode('A','HI_Z')
        m1k_obj.setmode('B','HI_Z')

        m1k_obj.setled(1 % 8)
        if m1k_obj.IsContinuous():
            m1k_obj.EndSession()
    except:
        donothing()

    root.destroy()
    exit()
#
# setup main window
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root = Tk()
root.title("ALM1000 Ohmmeter V Div RR " + RevDate)
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, img)
root.tk_focusFollowsMouse()
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
root.minsize(175, 100)
#
RUNstatus = IntVar(0)
buttons = Frame( root )
buttons.grid(row=0, column=0, sticky=W)
rb1 = Radiobutton(buttons, text="Stop", bg = "#ff0000", variable=RUNstatus, value=0, command=BStop )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", bg = "#00ff00", variable=RUNstatus, value=1, command=BStart )
rb2.pack(side=LEFT)
b1 = Button(buttons, text='Save', command=BSaveCal)
b1.pack(side=LEFT)
b2 = Button(buttons, text='Load', command=BLoadCal)
b2.pack(side=LEFT)
#
frame1 = Frame(root, borderwidth=5, relief=RIDGE)
frame1.grid(row=1, column=0, sticky=W) # 
#
labelA0 = Label(frame1, font = "Arial 16 bold")
labelA0.grid(row=0, column=0, columnspan=2, sticky=W)
labelA0.config(text = "Ohms 0.0000")

labelAI = Label(frame1, font = "Arial 12 bold")
labelAI.grid(row=1, column=0, columnspan=2, sticky=W)
labelAI.config(text = "CA-I 0.0000")
#
Diodelabel = Label(frame1, font = "Arial 12 bold")
Diodelabel.grid(row=2, column=0, columnspan=2, sticky=W)
Diodelabel.config(text = "Forward Voltage")
#
TestVA = Frame( frame1 )
TestVA.grid(row=3, column=0, sticky=W)
chatestvlab = Label(TestVA, text="CA test V")
chatestvlab.pack(side=LEFT)
CHATestVEntry = Entry(TestVA, width=6) #
CHATestVEntry.bind('<MouseWheel>', onAWGscroll)
CHATestVEntry.bind("<Button-4>", onAWGscroll)# with Linux OS
CHATestVEntry.bind("<Button-5>", onAWGscroll)
CHATestVEntry.pack(side=LEFT)
CHATestVEntry.delete(0,"end")
CHATestVEntry.insert(0,5.0)
#
RMode = IntVar(0)
TestMode = Frame( frame1 )
TestMode.grid(row=4, column=0, sticky=W)
modelab = Label(TestMode, text="Res ", font = "Arial 10 bold")
modelab.pack(side=LEFT)
rm3 = Radiobutton(TestMode, text="Ext", variable=RMode, value=0)
rm3.pack(side=LEFT)
rm4 = Radiobutton(TestMode, text="Int", variable=RMode, value=1)
rm4.pack(side=LEFT)
RMode.set(1)
#
TestRA = Frame( frame1 )
TestRA.grid(row=5, column=0, sticky=W)
chatestrlab = Label(TestRA, text="CA test R")
chatestrlab.pack(side=LEFT)
CHATestREntry = Entry(TestRA, width=6) #
CHATestREntry.bind('<MouseWheel>', onTextScroll)
CHATestREntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHATestREntry.bind("<Button-5>", onTextScroll)
CHATestREntry.pack(side=LEFT)
CHATestREntry.delete(0,"end")
CHATestREntry.insert(0,50.0)
# input probe wigets
calAlab = Label(frame1, text="Channel A Gain / Offset calibration")
calAlab.grid(row=6, column=0, sticky=W)
# Input Probes sub frame 
ProbeAV = Frame( frame1 )
ProbeAV.grid(row=7, column=0, sticky=W)
gainavlab = Label(ProbeAV, text="VA")
gainavlab.pack(side=LEFT)
CHAVGainEntry = Entry(ProbeAV, width=6) #
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,1.0)
CHAVOffsetEntry = Entry(ProbeAV, width=6) # 
CHAVOffsetEntry.pack(side=LEFT)
CHAVOffsetEntry.delete(0,"end")
CHAVOffsetEntry.insert(0,0.0)
#
ProbeAI = Frame( frame1 )
ProbeAI.grid(row=8, column=0, sticky=W)
gainailab = Label(ProbeAI, text=" IA ")
gainailab.pack(side=LEFT)
CHAIGainEntry = Entry(ProbeAI, width=6) #
CHAIGainEntry.pack(side=LEFT)
CHAIGainEntry.delete(0,"end")
CHAIGainEntry.insert(0,1.0)
CHAIOffsetEntry = Entry(ProbeAI, width=6) # 
CHAIOffsetEntry.pack(side=LEFT)
CHAIOffsetEntry.delete(0,"end")
CHAIOffsetEntry.insert(0,0.0)
# input probe wigets
calBlab = Label(frame1, text="Channel B Gain / Offset calibration")
calBlab.grid(row=9, column=0, sticky=W)
#
ProbeBV = Frame( frame1 )
ProbeBV.grid(row=10, column=0, sticky=W)
gainbvlab = Label(ProbeBV, text="VB")
gainbvlab.pack(side=LEFT)
CHBVGainEntry = Entry(ProbeBV, width=6) # )
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,1.0)
CHBVOffsetEntry = Entry(ProbeBV, width=6) # 
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,0.0)
#
ProbeBI = Frame( frame1 )
ProbeBI.grid(row=11, column=0, sticky=W)
gainbilab = Label(ProbeBI, text=" IB ")
gainbilab.pack(side=LEFT)
CHBIGainEntry = Entry(ProbeBI, width=6) # )
CHBIGainEntry.pack(side=LEFT)
CHBIGainEntry.delete(0,"end")
CHBIGainEntry.insert(0,1.0)
CHBIOffsetEntry = Entry(ProbeBI, width=6) # 
CHBIOffsetEntry.pack(side=LEFT)
CHBIOffsetEntry.delete(0,"end")
CHBIOffsetEntry.insert(0,0.0)
# Setup ADAML1000
# Start Service and robot setup
Connected = 0
while not Connected:
    try:
        NetAddr = askstring("Enter Network Address:", "Enter Network Address:\n", initialvalue=NetAddr)
        url='rr+tcp://' + NetAddr + ':11111?service=m1k'
        m1k_obj = RRN.ConnectService(url)
        Connected = 1
    except:
        if askyesno("WARNING","Network Address / Service was not found!\n Try Again?\n"):
            Connected = 0
        else:
            Connected = 1
            Bcloseexit()
#
#url='rr+tcp://localhost:11111?service=m1k'
#m1k_obj = RRN.ConnectService(url)
#
DevID = m1k_obj.GetDeviceSerial()
print( DevID )
print( m1k_obj.GetDeviceFirmware())
print( m1k_obj.GetDeviceHardware())
print( m1k_obj.GetDefaultRate())
#
m1k_obj.setled(2 % 8) # LED.green
#
m1k_obj.setmode('A','HI_Z_SPLIT')
m1k_obj.setmode('B','HI_Z_SPLIT')
#
m1k_obj.setchanterm('B', '2p5', 'OPEN') # set CHB 2.5 V switch to open
m1k_obj.setchanterm('B', 'GND', 'OPEN') # set CHB GND switch to open

# start main loop
root.update()
# Start sampling
Analog_in()
#
