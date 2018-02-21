#!/usr/bin/python
# ADALM1000 DC Voltmeter Tool 1.1 11-25-2016
# For pysmu ( libsmu > = 0.88 )
#For Python version > = 2.7.8
from Tkinter import *
import time
from pysmu import *
# define ADALM1000 interface
# define button actions
def Analog_in():
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global InOffA, InGainA, InOffB, InGainB
    
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
            DCVA0 = DCVB0 = 0.0 # initalize measurment variable
            # Get A0 and B0 data
            devx.ctrl_transfer(DevID, 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
            devx.ctrl_transfer(DevID, 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
            ADsignal1 = Both.get_samples(210) # get samples for both channel A0 and B0
            # get_samples returns a list of values for voltage [0] and current [1]
            for index in range(200): # calculate average
                DCVA0 += ADsignal1[0][index+10][0] # VAdata # Sum for average CA voltage 
                DCVB0 += ADsignal1[1][index+10][0] # VBdata # Sum for average CB voltage

            DCVA0 = DCVA0 / 200.0 # calculate average
            DCVB0 = DCVB0 / 200.0 # calculate average
            DCVA0 = (DCVA0 - InOffA) * InGainA
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
            time.sleep(0.05)
    # Update tasks and screens by TKinter
        root.update_idletasks()
        root.update()            

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
            print "Skipping " + line.rstrip()
    CalFile.close()
    
# setup main window
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""
root = Tk()
root.title("ALM1000 Voltmeter 1.1 (11-25-2016)")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, img)
root.minsize(250, 100)
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
rb1 = Radiobutton(buttons, text="Stop", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", variable=RUNstatus, value=1 )
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
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,1.0)
CHAVOffsetEntry = Entry(ProbeA, width=6) # 
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
CHBVGainEntry = Entry(ProbeB, width=6) # )
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,1.0)
CHBVOffsetEntry = Entry(ProbeB, width=6) # 
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,0.0)
b2 = Button(ProbeB, text='Load', command=BLoadCal)
b2.pack(side=LEFT)
# Setup ADAML1000
devx = Smu()
# devx.add_all()
DevID = devx.serials[0]
print DevID
CHA = devx.channels['A']    # Open CHA
CHA.set_mode('d')           # Put CHA in Hi Z mode
CHB = devx.channels['B']    # Open CHB
CHB.set_mode('d')           # Put CHB in Hi Z mode
Both = devx.devices[0]
ADsignal1 = []              # Ain signal array channel
CHAMaxV = 0.0
CHAMinV = 5.0
CHBMaxV = 0.0
CHBMinV = 5.0
# start main loop
root.update()
# Start sampling
Analog_in()
#
