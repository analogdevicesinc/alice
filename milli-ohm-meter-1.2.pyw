#!/usr/bin/python
# ADALM1000 Milli Ohmmeter Tool 1.2 6-10-2018
# For pysmu ( libsmu.rework > = 1.0 )
#For Python version > = 2.7.8
from Tkinter import *
import time
from pysmu import *
# define button actions
loopnum = 0
#
def Analog_in():
    global InOffA, InGainA, InOffB, InGainB
    global session, DevID, devx, loopnum
    global CHAI_autozero, CHBV_autozero, labelA0, labelA1

    while (True):       # Main loop
        if (RUNstatus.get() == 1):
            #
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
                CHAtesti = float(eval(CHATestVEntry.get()))
                if CHAtesti > 200.0:
                    CHAtesti = 200.0
                    CHATestVEntry.delete(0,END)
                    CHATestVEntry.insert(0, CHAtesti)
            except:
                CHATestVEntry.delete(0,END)
                CHATestVEntry.insert(0, CHAtesti)
            # 
            DCVA0 = DCVB0 = DCIA0 = DCIB0 = 0.0 # initalize measurment variable
            RIN = 1000000 # nominal ALM1000 input resistance is 1 Mohm
            # Get A0 and B0 data
            devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
            #
            if CHAI_autozero.get() == 1 or CHBV_autozero.get() == 1:
                CHA.mode = Mode.SIMV # Put CHA in Hi Z mode
                CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
                CHA.constant(0.0)
                time.sleep(0.05)
                #
                ADsignal1 = devx.get_samples(1024) # get samples for both channel A0 and B0
                # get_samples returns a list of values for voltage [0] and current [1]
                for index in range(1000): # calculate average 
                    DCVB0 += ADsignal1[index+10][1][0] # VBdata # Sum for average CB voltage
                    DCIA0 += ADsignal1[index+10][0][1] # Sum for average CA current 
                #
                DCVB0 = DCVB0 / 1000.0 # calculate average
                DCIA0 = DCIA0 / 1000.0 # calculate average
                if CHAI_autozero.get() == 1:
                    String = ' {0:.3f} '.format(DCIA0*1000)
                    CHAIOffsetEntry.delete(0,END)
                    CHAIOffsetEntry.insert(0, String) # change to mA
                if CHBV_autozero.get() == 1:
                    String = ' {0:.3f} '.format(DCVB0)
                    CHBVOffsetEntry.delete(0,END)
                    CHBVOffsetEntry.insert(0, String)
            #
            time.sleep(0.05)
            CHA.mode = Mode.SIMV # Put CHA in SVMI mode
            CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
            CHA.constant(CHAtesti/1000.0)
            time.sleep(0.1)
            #
            ADsignal1 = devx.get_samples(1024) # get samples for both channel A0 and B0
            # get_samples returns a list of values for voltage [0] and current [1]
            for index in range(1000): # calculate average
                DCVB0 += ADsignal1[index+10][1][0] # VBdata # Sum for average CB voltage
                DCIA0 += ADsignal1[index+10][0][1] # Sum for average CA current  

            DCVB0 = DCVB0 / 1000.0 # calculate average
            DCIA0 = DCIA0 / 1000.0 # calculate average
            #
            DCVB0 = (DCVB0 - InOffB) * InGainB
            DCIA0 = ((DCIA0*1000) - CurOffA) * CurGainA
            #
            DCR = (DCVB0/(20*DCIA0/1000))
            DCR = abs(DCR)
            if DCR > 1:
                String = ' {0:.3f} '.format(DCR) + "Ohms " # format with 3 decimal places
            else:
                String = ' {0:.1f} '.format(DCR*1000) + "mOhms "# multiply by 1000 and format with 1 decimal places
            labelA0.config(text = String) # change displayed value
            String = "IA = " + ' {0:.2f} '.format(DCIA0) + " mA, VB = " + ' {0:.3f} '.format(DCVB0) + " V"
            if DCVB0 > 4.85:
                labelAI.config(fg= "red", text = String) # change displayed value / color
            else:
                labelAI.config(fg= "black", text = String) # change displayed value / color
#
            #time.sleep(0.1)
            loopnum = loopnum + 1
            devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
# Update tasks and screens by TKinter
        else:
            if loopnum > 0:
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
    filename = devidstr + "_MO.cal"
    CalFile = open(filename, "w")
    #
    CalFile.write('CHBVGainEntry.delete(0,END)\n')
    CalFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
    CalFile.write('CHBVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')
    #
    CalFile.write('CHAIGainEntry.delete(0,END)\n')
    CalFile.write('CHAIGainEntry.insert(4, ' + CHAIGainEntry.get() + ')\n')
    CalFile.write('CHAIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAIOffsetEntry.insert(4, ' + CHAIOffsetEntry.get() + ')\n')
    #
    CalFile.close()

def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global DevID

    devidstr = DevID[17:31]
    filename = devidstr + "_MO.cal" # first try reading from Milli Ohmmeter tool cal file
    try:
        CalFile = open(filename)
        for line in CalFile:
            try:
                exec( line.rstrip() )
            except:
                print "Skipping " + line.rstrip()
        CalFile.close()
    except:
        filename = devidstr + "_V.cal" # else try reading from Voltmeter tool cal file
        try:
            CalFile = open(filename)
            for line in CalFile:
                try:
                    exec( line.rstrip() )
                except:
                    print "Skipping " + line.rstrip()
            CalFile.close()
        except:
            print "Cal file(s) for this device not found"
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
def Clear_Auto_Zero():

    CHAIOffsetEntry.delete(0,END)
    CHAIOffsetEntry.insert(0, 0.0) # change to mA
    CHBVOffsetEntry.delete(0,END)
    CHBVOffsetEntry.insert(0, 0.0)
    
# setup main window
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root = Tk()
root.title("ALM1000 Milli-Ohmmeter 1.2 (6-10-2018)")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, img)
root.tk_focusFollowsMouse()
root.minsize(175, 100)
#
RUNstatus = IntVar(0)
CHAI_autozero = IntVar()
CHBV_autozero = IntVar()
#
buttons = Frame( root )
buttons.grid(row=0, column=0, sticky=W)
rb1 = Radiobutton(buttons, text="Stop", bg = "RED", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", bg = "GREEN", variable=RUNstatus, value=1 )
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
labelA0.config(text = "0.000 Ohms")

labelAI = Label(frame1, font = "Arial 12 bold")
labelAI.grid(row=1, column=0, columnspan=2, sticky=W)
labelAI.config(text = "IA = 0.00 mA, VB = 0.000 V")
#
TestVA = Frame( frame1 )
TestVA.grid(row=2, column=0, sticky=W)
chatestvlab = Label(TestVA, text="CA test I")
chatestvlab.pack(side=LEFT)
CHATestVEntry = Entry(TestVA, width=6) #
CHATestVEntry.bind('<MouseWheel>', onTextScroll)
CHATestVEntry.pack(side=LEFT)
CHATestVEntry.delete(0,"end")
CHATestVEntry.insert(0,150.0)
# input probe wigets
calAlab = Label(frame1, text="Channel A Gain / Offset calibration")
calAlab.grid(row=3, column=0, sticky=W)
#
chaiaz = Checkbutton(frame1, text="Auto Zero CA-I", variable=CHAI_autozero)
chaiaz.grid(row=4, column=0, sticky=W)
# Input Probes sub frame 
ProbeAI = Frame( frame1 )
ProbeAI.grid(row=5, column=0, sticky=W)
gainailab = Label(ProbeAI, text=" IA ")
gainailab.pack(side=LEFT)
CHAIGainEntry = Entry(ProbeAI, width=6) #
CHAIGainEntry.bind('<MouseWheel>', onTextScroll)
CHAIGainEntry.pack(side=LEFT)
CHAIGainEntry.delete(0,"end")
CHAIGainEntry.insert(0,1.0)
CHAIOffsetEntry = Entry(ProbeAI, width=6) #
CHAIOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAIOffsetEntry.pack(side=LEFT)
CHAIOffsetEntry.delete(0,"end")
CHAIOffsetEntry.insert(0,0.0)
# input probe wigets
calBlab = Label(frame1, text="Channel B Gain / Offset calibration")
calBlab.grid(row=6, column=0, sticky=W)
#
chbvaz = Checkbutton(frame1, text="Auto Zero CB-V", variable=CHBV_autozero)
chbvaz.grid(row=7, column=0, sticky=W)
#
ProbeBV = Frame( frame1 )
ProbeBV.grid(row=8, column=0, sticky=W)
gainbvlab = Label(ProbeBV, text="VB")
gainbvlab.pack(side=LEFT)
CHBVGainEntry = Entry(ProbeBV, width=6) #
CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,1.0)
CHBVOffsetEntry = Entry(ProbeBV, width=6) #
CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,0.0)
#
cb1 = Button(frame1, text='Clear Offsets', command=Clear_Auto_Zero)
cb1.grid(row=9, column=0, sticky=W)
#
try:
    schem = PhotoImage(file="ad8210-sch.gif")
    SCHEM = Label(root, image=schem, anchor= "sw", compound="bottom", height=110, width=315)
    SCHEM.grid(row=2, column=0, sticky=W)
except:
    SCHEM = Label(root, text="AD8210 Schematic goes here.")
    SCHEM.grid(row=2, column=0, sticky=W)
# Setup ADAML1000
session = Session(ignore_dataflow=True, queue_size=2000)
session.add_all()
if not session.devices:
    print 'no device found'
    root.destroy()
    exit()
session.configure()
devx = session.devices[0]
devx.set_led(0b010) # LED.green
DevID = devx.serial
print DevID
print devx.fwver
print devx.hwver
print devx.default_rate
CHA = devx.channels['A']    # Open CHA
CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
CHB = devx.channels['B']    # Open CHB
CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
ADsignal1 = []              # Ain signal array channel
devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
# start main loop
root.update()
# Start sampling
Analog_in()
#
