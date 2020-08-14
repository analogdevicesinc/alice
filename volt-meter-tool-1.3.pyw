#!/usr/bin/python
# ADALM1000 DC Voltmeter Tool 1.3 8-4-2020
# For pysmu ( libsmu > = 1.0 )
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
# define ADALM1000 interface
# define button actions
loopnum = 0
def Analog_in():
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global InOffA, InGainA, InOffB, InGainB
    global session, DevID, devx, loopnum, session
    
    while (True):       # Main loop
        if (RUNstatus.get() == 1):
            #
            if not session.continuous:
                session.flush()
                session.start(0)
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
            DCVA0 = DCVB0 = 0.0 # initalize measurment variable
            #
            # Get A0 and B0 data
            time.sleep(0.1)
            ADsignal1 = devx.read(4096, -1, True)
            if len(ADsignal1) < 512:
                print (len(ADsignal1))
                print (loopnum)
            else:
            # get_samples returns a list of values for voltage [0] and current [1]
                for index in range(200): # calculate average
                    DCVA0 += ADsignal1[index+10][0][0] # Sum for average CA voltage 
                    DCVB0 += ADsignal1[index+10][1][0] # Sum for average CB voltage

                DCVA0 = DCVA0 / 200.0 # calculate average
                DCVB0 = DCVB0 / 200.0 # calculate average
                DCVA0 = (DCVA0 - InOffA) * InGainA # adjust for external gain / offset
                DCVB0 = (DCVB0 - InOffB) * InGainB
                if DCVA0 > CHAMaxV:
                    CHAMaxV = DCVA0
                if DCVA0 < CHAMinV:
                    CHAMinV = DCVA0
                if DCVB0 > CHBMaxV:
                    CHBMaxV = DCVB0
                if DCVB0 < CHBMinV:
                    CHBMinV = DCVB0
                VAString = "CA Volts " + ' {0:.4f} '.format(DCVA0) # format with 4 decimal places
                VBString = "CB Volts " + ' {0:.4f} '.format(DCVB0) # format with 4 decimal places
                VABString = "CA-CB V " + ' {0:.4f} '.format(DCVA0-DCVB0) # format with 4 decimal places
                labelA0.config(text = VAString) # change displayed value
                labelB0.config(text = VBString) # change displayed value
                labelAB.config(text = VABString) # change displayed value
                VAString = "CA Max Volts " + ' {0:.4f} '.format(CHAMaxV) # format with 4 decimal places
                VBString = "CB Max Volts " + ' {0:.4f} '.format(CHBMaxV) # format with 4 decimal places
                labelAMax.config(text = VAString) # change displayed value
                labelBMax.config(text = VBString) # change displayed value
                VAString = "CA Min Volts " + ' {0:.4f} '.format(CHAMinV) # format with 4 decimal places
                VBString = "CB Min Volts " + ' {0:.4f} '.format(CHBMinV) # format with 4 decimal places
                labelAMin.config(text = VAString) # change displayed value
                labelBMin.config(text = VBString) # change displayed value
    #
            # time.sleep(0.1)
            loopnum = loopnum + 1
    # Update tasks and screens by TKinter
        else:
            if loopnum > 0:
                loopnum = 0
                if session.continuous:
                    session.end()
                    #print "Stoping Session"

        root.update_idletasks()
        root.update()            
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
def BReset():
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global InOffA, InGainA, InOffB, InGainB

    CHAMaxV = (0.0 - InOffA) * InGainA
    CHAMinV = (5.0 - InOffA) * InGainA
    CHBMaxV = (0.0 - InOffB) * InGainB
    CHBMinV = (5.0 - InOffB) * InGainB
    
def BSaveCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global DevID

    devidstr = DevID[17:31]
    filename = devidstr + "_V.cal"
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
    filename = devidstr + "_V.cal"
    CalFile = open(filename)
    for line in CalFile:
        try:
            exec( line.rstrip() )
        except:
            print ("Skipping " + line.rstrip())
    CalFile.close()
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
# setup main window
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""
root = Tk()
root.title("ALM1000 Voltmeter 1.3 (14 Aug 2018)")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, img)
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
root.minsize(200, 100)
#
labelA0 = Label(root, font = "Arial 16 bold")
labelA0.grid(row=0, column=0, columnspan=2, sticky=W)
labelA0.config(text = "CA Volts 0.0000")
labelAMax = Label(root, font = "Arial 12 bold")
labelAMax.grid(row=1, column=0, columnspan=2, sticky=W)
labelAMax.config(text = "CA Max Volts 0.0000")
labelAMin = Label(root, font = "Arial 12 bold")
labelAMin.grid(row=2, column=0, columnspan=2, sticky=W)
labelAMin.config(text = "CA Min Volts 0.0000")
labelB0 = Label(root, font = "Arial 16 bold")
labelB0.grid(row=3, column=0, columnspan=2, sticky=W)
labelB0.config(text = "CB Volts 0.0000")
labelBMax = Label(root, font = "Arial 12 bold")
labelBMax.grid(row=4, column=0, columnspan=2, sticky=W)
labelBMax.config(text = "CB Max Volts 0.0000")
labelBMin = Label(root, font = "Arial 12 bold")
labelBMin.grid(row=5, column=0, columnspan=2, sticky=W)
labelBMin.config(text = "CB Min Volts 0.0000")
labelAB = Label(root, font = "Arial 16 bold")
labelAB.grid(row=6, column=0, columnspan=2, sticky=W)
labelAB.config(text = "CA-CB V 0.0000")
#
RUNstatus = IntVar(0)
buttons = Frame( root )
buttons.grid(row=7, column=0, sticky=W)
rb1 = Radiobutton(buttons, text="Stop", bg = "#ff0000", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", bg = "#00ff00", variable=RUNstatus, value=1 )
rb2.pack(side=LEFT)
resetb1 = Button(buttons, text='Reset Min/Max', command=BReset)
resetb1.pack(side=LEFT)
# input probe wigets
prlab = Label(root, text="Channel Gain / Offset calibration")
prlab.grid(row=8, column=0, sticky=W)
# Input Probes sub frame 
ProbeA = Frame( root )
ProbeA.grid(row=9, column=0, sticky=W)
gain1lab = Label(ProbeA, text="CA")
gain1lab.pack(side=LEFT)
CHAVGainEntry = Entry(ProbeA, width=6) #
CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
CHAVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVGainEntry.bind("<Button-5>", onTextScroll)
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,1.0)
CHAVOffsetEntry = Entry(ProbeA, width=6) #
CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVOffsetEntry.bind("<Button-5>", onTextScroll)
CHAVOffsetEntry.pack(side=LEFT)
CHAVOffsetEntry.delete(0,"end")
CHAVOffsetEntry.insert(0,0.0)
b1 = Button(ProbeA, text='Save', command=BSaveCal)
b1.pack(side=LEFT)
#
ProbeB = Frame( root )
ProbeB.grid(row=10, column=0, sticky=W)
gain2lab = Label(ProbeB, text="CB")
gain2lab.pack(side=LEFT)
CHBVGainEntry = Entry(ProbeB, width=6) #
CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
CHBVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVGainEntry.bind("<Button-5>", onTextScroll)
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,1.0)
CHBVOffsetEntry = Entry(ProbeB, width=6) #
CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVOffsetEntry.bind("<Button-5>", onTextScroll)
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,0.0)
b2 = Button(ProbeB, text='Load', command=BLoadCal)
b2.pack(side=LEFT)
# Setup ADAML1000
session = Session(ignore_dataflow=True, queue_size=10000)
#session.add_all()
if not session.devices:
    print ('no device found')
    root.destroy()
    exit()
#session.configure()
print (session.queue_size)
devx = session.devices[0]
# devx.ignore_dataflow = True
DevID = devx.serial
print(DevID)
print(devx.fwver)
print(devx.hwver)
print(devx.default_rate)
CHA = devx.channels['A']    # Open CHA
CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
CHB = devx.channels['B']    # Open CHB
CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
devx.set_led(0b010) # LED.green,
ADsignal1 = []              # Ain signal array channel
CHAMaxV = -100.0
CHAMinV = 100.0
CHBMaxV = -100.0
CHBMinV = 100.0
devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
# start main loop
# session.start(0)
root.update()
# Start sampling
Analog_in()
#
