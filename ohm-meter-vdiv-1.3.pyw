#!/usr/bin/python
# ADALM1000 DC Ohmmeter Tool 1.3 8-4-2020
# For pysmu ( libsmu.rework > = 1.0 )
#For Python version > = 2.7.8 and 3.7
import __future__
import os
import sys
if sys.version_info[0] == 2:
    print ("Python 2.x")
    from Tkinter import *
if sys.version_info[0] == 3:
    from tkinter import *
    print ("Python 3.x")
import time
from pysmu import *
# define button actions
loopnum = 0
def Analog_in():
    # global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global InOffA, InGainA, InOffB, InGainB
    global session, DevID, devx, loopnum
    global RMode, Diodelabel, labelA0, labelA1

    while (True):       # Main loop
        if (RUNstatus.get() == 1):
            #
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
                devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
            else:
                devx.ctrl_transfer(0x40, 0x50, 38, 0, 0, 0, 100) # set CHB GND switch to closed
            #
            CHA.mode = Mode.SVMI # Put CHA in SVMI mode
            CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
            CHA.constant(chatestv)
            # print chatestv
            # session.start(512)
            # session.flush()
            time.sleep(0.1)
            #session.start(512)
            #
            ADsignal1 = devx.get_samples(512) # get samples for both channel A0 and B0
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
            devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
# Update tasks and screens by TKinter
        else:
            if loopnum > 0:
                # print "stop"
                # session.end()
                CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
                CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
                loopnum = 0
        root.update_idletasks()
        root.update()            
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
def Bcloseexit():
    global RUNstatus, session, CHA, CHB, devx, AWG_2X
    
    RUNstatus.set(0)
    # BSaveConfig("alice-last-config.cfg")
    try:
        # Put channels in Hi-Z and exit
        CHA.mode = Mode.HI_Z_SPLIT # Put CHA in Hi Z split mode
        CHB.mode = Mode.HI_Z_SPLIT # Put CHB in Hi Z split mode
        devx.set_adc_mux(0) # set ADC mux conf to default
        CHA.constant(0.0)
        CHB.constant(0.0)
        devx.set_led(0b001) # Set LED.red on the way out
        if session.continuous:
            session.end()
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
root.title("ALM1000 Ohmmeter V Div 1.3 (14 Aug 2020)")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, img)
root.tk_focusFollowsMouse()
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
root.minsize(175, 100)
#
RUNstatus = IntVar(0)
buttons = Frame( root )
buttons.grid(row=0, column=0, sticky=W)
rb1 = Radiobutton(buttons, text="Stop", bg = "#ff0000", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", bg = "#00ff00", variable=RUNstatus, value=1 )
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
CHATestVEntry.bind('<MouseWheel>', onTextScroll)
CHATestVEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHATestVEntry.bind("<Button-5>", onTextScroll)
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
session = Session(ignore_dataflow=True, queue_size=2000)
session.add_all()
if not session.devices:
    print( 'no device found')
    root.destroy()
    exit()
session.configure()
devx = session.devices[0]
devx.set_led(0b010) # LED.green
DevID = devx.serial
print( DevID)
print( devx.fwver)
print( devx.hwver)
print( devx.default_rate)
CHA = devx.channels['A']    # Open CHA
CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
CHB = devx.channels['B']    # Open CHB
CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
devx.set_led(0b010) # LED.green,
ADsignal1 = []              # Ain signal array channel
devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
#session.start(0)
#session.run(512)
# start main loop
root.update()
# Start sampling
Analog_in()
#
