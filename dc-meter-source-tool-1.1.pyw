#!/usr/bin/python
# ADALM1000 DC volt meter / source tool 12-2-2016
# For use with pysmu / libsmu >= 0.88
# For Python version > = 2.7.8
from Tkinter import *
import time
from pysmu import *
# define button actions
def Analog_in():
    global DevOne

    while (True):       # Main loop
        if RUNstatus.get() == 1:
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
            except:
                CHATestVEntry.delete(0,END)
                CHATestVEntry.insert(0, chatestv)
            try:
                chbtestv = float(eval(CHBTestVEntry.get()))
            except:
                CHBTestVEntry.delete(0,END)
                CHBTestVEntry.insert(0, chbtestv)
            try:
                chatesti = float(eval(CHATestIEntry.get()))/1000
            except:
                CHATestIEntry.delete(0,END)
                CHATestIEntry.insert(0, chatesti*1000)
            try:
                chbtesti = float(eval(CHBTestIEntry.get()))/1000
            except:
                CHBTestIEntry.delete(0,END)
                CHBTestIEntry.insert(0, chbtesti*1000)
            # 
            DCVA0 = DCVB0 = DCIA0 = DCIB0 = 0.0 # initalize measurment variable
            # Get A0 and B0 data
            if CHAstatus.get() == 0:
                CHA.set_mode('d')
            else:
                if CHAmode.get() == 0:
                    CHA.set_mode('v')
                    CHA.constant(chatestv)
                else:
                    CHA.set_mode('i')
                    CHA.constant(chatesti)
            if CHBstatus.get() == 0:
                CHB.set_mode('d')
            else:
                if CHBmode.get() == 0:
                    CHB.set_mode('v')
                    CHB.constant(chbtestv)
                else:
                    CHB.set_mode('i')
                    CHB.constant(chbtesti)
            DevOne.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
            DevOne.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
            ADsignal1 = DevOne.get_samples(210) # get samples for both channel A0 and B0
            # get_samples returns a list of values for voltage [0] and current [1]
            for index in range(200): # calculate average
                DCVA0 += ADsignal1[0][index+10][0] # VAdata # Sum for average CA voltage 
                DCVB0 += ADsignal1[1][index+10][0] # VBdata # Sum for average CB voltage
                DCIA0 += ADsignal1[0][index+10][1] # Sum for average CA current 
                DCIB0 += ADsignal1[1][index+10][1] # Sum for average CB current

            DCVA0 = DCVA0 / 200.0 # calculate average
            DCVB0 = DCVB0 / 200.0 # calculate average
            DCIA0 = DCIA0 / 200.0 # calculate average
            DCIB0 = DCIB0 / 200.0 # calculate average
            DCVA0 = (DCVA0 - InOffA) * InGainA
            DCVB0 = (DCVB0 - InOffB) * InGainB
            DCIA0 = ((DCIA0*1000) - CurOffA) * CurGainA
            DCIB0 = ((DCIB0*1000) - CurOffB) * CurGainB
            VAString = "CA V " + ' {0:.4f} '.format(DCVA0) # format with 4 decimal places
            VBString = "CB V " + ' {0:.4f} '.format(DCVB0) # format with 4 decimal places
            labelA0.config(text = VAString) # change displayed value
            labelB0.config(text = VBString) # change displayed value
            if CHAstatus.get() == 0:
                IAString = "CA mA ----"
            else:
                IAString = "CA mA " + ' {0:.2f} '.format(DCIA0)
            if CHBstatus.get() == 0:
                IBString = "CB mA ----"
            else:
                IBString = "CB mA " + ' {0:.2f} '.format(DCIB0)
            
            labelAI.config(text = IAString) # change displayed value
            labelBI.config(text = IBString) # change displayed value

#
            time.sleep(0.2)
    # Update tasks and screens by TKinter
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

def DestroyDigScreen():
    global win1, DigScreenStatus
    
    DigScreenStatus.set(0)
    win1.destroy()

def sel():
    global devx, DevID, DevOne
    global D0, D1, D2, D3, D4, D5, D6, D7
    # sending 0x50 = set to 0, 0x51 = set to 1
    if D0.get() > 0:
        DevOne.ctrl_transfer( 0x40, D0.get(), 0, 0, 0, 0, 100) # set PIO 0
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 0, 0, 0, 1, 100)
    if D1.get() > 0:
        DevOne.ctrl_transfer( 0x40, D1.get(), 1, 0, 0, 0, 100) # set PIO 1
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 1, 0, 0, 1, 100)
    if D2.get() > 0:
        DevOne.ctrl_transfer( 0x40, D2.get(), 2, 0, 0, 0, 100) # set PIO 2
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 2, 0, 0, 1, 100)
    if D3.get() > 0:
        DevOne.ctrl_transfer( 0x40, D3.get(), 3, 0, 0, 0, 100) # set PIO 3
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 3, 0, 0, 1, 100)
    if D4.get() > 0:
        DevOne.ctrl_transfer( 0x40, D4.get(), 4, 0, 0, 0, 100) # set PIO 4
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100)
    if D5.get() > 0:
        DevOne.ctrl_transfer( 0x40, D5.get(), 5, 0, 0, 0, 100) # set PIO 5
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100)
    if D6.get() > 0:
        DevOne.ctrl_transfer( 0x40, D6.get(), 6, 0, 0, 0, 100) # set PIO 6
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100)
    if D7.get() > 0:
        DevOne.ctrl_transfer( 0x40, D7.get(), 7, 0, 0, 0, 100) # set PIO 7
    else:
        Dval = DevOne.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100)

def MakeDigScreen():
    global D0, D1, D2, D3, D4, D5, D6, D7
    global DigScreenStatus, win1
    # setup Dig output window
    if DigScreenStatus.get() == 0:
        DigScreenStatus.set(1)
        win1 = Toplevel()
        win1.title("Dig Out")

        D0 = IntVar(0)
        D1 = IntVar(0)
        D2 = IntVar(0)
        D3 = IntVar(0)
        D4 = IntVar(0)
        D5 = IntVar(0)
        D6 = IntVar(0)
        D7 = IntVar(0)
        rb1 = Radiobutton(win1, text="D0-0", variable=D0, value=0x50, command=sel )
        rb1.grid(row=2, column=0, sticky=W)
        rb0z = Radiobutton(win1, text="D0-Z", variable=D0, value=0, command=sel )
        rb0z.grid(row=2, column=1, sticky=W)
        rb2 = Radiobutton(win1, text="D0-1", variable=D0, value=0x51, command=sel )
        rb2.grid(row=2, column=2, sticky=W)
        rb3 = Radiobutton(win1, text="D1-0", variable=D1, value=0x50, command=sel )
        rb3.grid(row=3, column=0, sticky=W)
        rb3z = Radiobutton(win1, text="D1-Z", variable=D1, value=0, command=sel )
        rb3z.grid(row=3, column=1, sticky=W)
        rb4 = Radiobutton(win1, text="D1-1", variable=D1, value=0x51, command=sel )
        rb4.grid(row=3, column=2, sticky=W)
        rb5 = Radiobutton(win1, text="D2-0", variable=D2, value=0x50, command=sel )
        rb5.grid(row=4, column=0, sticky=W)
        rb5z = Radiobutton(win1, text="D2-Z", variable=D2, value=0, command=sel )
        rb5z.grid(row=4, column=1, sticky=W)
        rb6 = Radiobutton(win1, text="D2-1", variable=D2, value=0x51, command=sel )
        rb6.grid(row=4, column=2, sticky=W)
        rb7 = Radiobutton(win1, text="D3-0", variable=D3, value=0x50, command=sel )
        rb7.grid(row=5, column=0, sticky=W)
        rb7z = Radiobutton(win1, text="D3-Z", variable=D3, value=0, command=sel )
        rb7z.grid(row=5, column=1, sticky=W)
        rb8 = Radiobutton(win1, text="D3-1", variable=D3, value=0x51, command=sel )
        rb8.grid(row=5, column=2, sticky=W)
        rb9 = Radiobutton(win1, text="D4-0", variable=D4, value=0x50, command=sel )
        rb9.grid(row=6, column=0, sticky=W)
        rb9z = Radiobutton(win1, text="D4-Z", variable=D4, value=0, command=sel )
        rb9z.grid(row=6, column=1, sticky=W)
        rb10 = Radiobutton(win1, text="D4-1", variable=D4, value=0x51, command=sel )
        rb10.grid(row=6, column=2, sticky=W)
        rb11 = Radiobutton(win1, text="D5-0", variable=D5, value=0x50, command=sel )
        rb11.grid(row=7, column=0, sticky=W)
        rb11z = Radiobutton(win1, text="D5-Z", variable=D5, value=0, command=sel )
        rb11z.grid(row=7, column=1, sticky=W)
        rb12 = Radiobutton(win1, text="D5-1", variable=D5, value=0x51, command=sel )
        rb12.grid(row=7, column=2, sticky=W)
        rb13 = Radiobutton(win1, text="D6-0", variable=D6, value=0x50, command=sel )
        rb13.grid(row=8, column=0, sticky=W)
        rb13z = Radiobutton(win1, text="D6-Z", variable=D6, value=0, command=sel )
        rb13z.grid(row=8, column=1, sticky=W)
        rb13 = Radiobutton(win1, text="D6-1", variable=D6, value=0x51, command=sel )
        rb13.grid(row=8, column=2, sticky=W)
        rb14 = Radiobutton(win1, text="D7-0", variable=D7, value=0x50, command=sel )
        rb14.grid(row=9, column=0, sticky=W)
        rb14z = Radiobutton(win1, text="D7-Z", variable=D7, value=0, command=sel )
        rb14z.grid(row=9, column=1, sticky=W)
        rb15 = Radiobutton(win1, text="D7-1", variable=D7, value=0x51, command=sel )
        rb15.grid(row=9, column=2, sticky=W)

        dismissbutton = Button(win1, text="Dismiss", command=DestroyDigScreen)
        dismissbutton.grid(row=10, column=0, sticky=W)
        
# setup main window
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root = Tk()
root.title("ALM1000 Meter-Source 1.1 (12-2-2016)")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, img)
#
RUNstatus = IntVar(0)
CHAstatus = IntVar(0)
CHBstatus = IntVar(0)
CHAmode = IntVar(0)
CHBmode = IntVar(0)
#
buttons = Frame( root )
buttons.grid(row=0, column=0, columnspan=2, sticky=W)
rb1 = Radiobutton(buttons, text="Stop", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", variable=RUNstatus, value=1 )
rb2.pack(side=LEFT)
b1 = Button(buttons, text='Save', command=BSaveCal)
b1.pack(side=LEFT)
b2 = Button(buttons, text='Load', command=BLoadCal)
b2.pack(side=LEFT)
#
frame1 = Frame(root, borderwidth=5, relief=RIDGE)
frame1.grid(row=1, column=0, rowspan=2, sticky=W) # 
frame2 = Frame(root, borderwidth=5, relief=RIDGE)
frame2.grid(row=1, column=1, rowspan=2, sticky=W) # 
frame3 = Frame(root, borderwidth=5, relief=RIDGE)
frame3.grid(row=1, column=2, sticky=W) # 
frame4 = Frame(root, borderwidth=5, relief=RIDGE)
frame4.grid(row=1, column=3, sticky=W) # 
#
labelAV = Label(frame1, font = "Arial 16 bold")
labelAV.grid(row=0, column=0, columnspan=2, sticky=W)
labelAV.config(text = "CA Meter")

labelA0 = Label(frame1, font = "Arial 16 bold")
labelA0.grid(row=1, column=0, columnspan=2, sticky=W)
labelA0.config(text = "CA-V 0.0000")

labelAI = Label(frame1, font = "Arial 16 bold")
labelAI.grid(row=2, column=0, columnspan=2, sticky=W)
labelAI.config(text = "CA-I 0.00")
# input probe wigets
calAlab = Label(frame1, text="CH A Gain/Offset calibration")
calAlab.grid(row=3, column=0, sticky=W)
# Input Probes sub frame 
ProbeAV = Frame( frame1 )
ProbeAV.grid(row=4, column=0, sticky=W)
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
ProbeAI.grid(row=5, column=0, sticky=W)
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
#
labelAV = Label(frame2, font = "Arial 16 bold")
labelAV.grid(row=0, column=0, columnspan=2, sticky=W)
labelAV.config(text = "CB Meter")

labelB0 = Label(frame2, font = "Arial 16 bold")
labelB0.grid(row=1, column=0, columnspan=2, sticky=W)
labelB0.config(text = "CB-V 0.0000")

labelBI = Label(frame2, font = "Arial 16 bold")
labelBI.grid(row=2, column=0, columnspan=2, sticky=W)
labelBI.config(text = "CB-I 0.00")
# input probe wigets
calBlab = Label(frame2, text="CH B Gain/Offset calibration")
calBlab.grid(row=3, column=0, sticky=W)
#
ProbeBV = Frame( frame2 )
ProbeBV.grid(row=4, column=0, sticky=W)
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
ProbeBI = Frame( frame2 )
ProbeBI.grid(row=5, column=0, sticky=W)
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
#
labelAS = Label(frame3, font = "Arial 16 bold")
labelAS.grid(row=0, column=0, columnspan=2, sticky=W)
labelAS.config(text = "CA Source")

chaonbutton = Frame( frame3 )
chaonbutton.grid(row=1, column=0, columnspan=2, sticky=W)
rbaoff = Radiobutton(chaonbutton, text="CHA off", variable=CHAstatus, value=0 )
rbaoff.pack(side=LEFT)
rbaon = Radiobutton(chaonbutton, text="CHA on", variable=CHAstatus, value=1 )
rbaon.pack(side=LEFT)

chaivbutton = Frame( frame3 )
chaivbutton.grid(row=2, column=0, columnspan=2, sticky=W)
rbav = Radiobutton(chaivbutton, text="CHA V", variable=CHAmode, value=0 )
rbav.pack(side=LEFT)
rbai = Radiobutton(chaivbutton, text="CHA I", variable=CHAmode, value=1 )
rbai.pack(side=LEFT)

TestVA = Frame( frame3 )
TestVA.grid(row=3, column=0, sticky=W)
chatestvlab = Label(TestVA, text="CA-V")
chatestvlab.pack(side=LEFT)
CHATestVEntry = Entry(TestVA, width=6) #
CHATestVEntry.pack(side=LEFT)
CHATestVEntry.delete(0,"end")
CHATestVEntry.insert(0,0.0)

TestIA = Frame( frame3 )
TestIA.grid(row=4, column=0, sticky=W)
chatestilab = Label(TestIA, text="CA-I")
chatestilab.pack(side=LEFT)
CHATestIEntry = Entry(TestIA, width=6) #
CHATestIEntry.pack(side=LEFT)
CHATestIEntry.delete(0,"end")
CHATestIEntry.insert(0,0.0)
#
labelBS = Label(frame4, font = "Arial 16 bold")
labelBS.grid(row=0, column=0, columnspan=2, sticky=W)
labelBS.config(text = "CB Source")

chbonbutton = Frame( frame4 )
chbonbutton.grid(row=1, column=0, columnspan=2, sticky=W)
rbboff = Radiobutton(chbonbutton, text="CHB off", variable=CHBstatus, value=0 )
rbboff.pack(side=LEFT)
rbbon = Radiobutton(chbonbutton, text="CHB on", variable=CHBstatus, value=1 )
rbbon.pack(side=LEFT)

chbivbutton = Frame( frame4 )
chbivbutton.grid(row=2, column=0, columnspan=2, sticky=W)
rbbv = Radiobutton(chbivbutton, text="CHB V", variable=CHBmode, value=0 )
rbbv.pack(side=LEFT)
rbbi = Radiobutton(chbivbutton, text="CHB I", variable=CHBmode, value=1 )
rbbi.pack(side=LEFT)

TestVB = Frame( frame4 )
TestVB.grid(row=3, column=0, sticky=W)
chbtestvlab = Label(TestVB, text="CB-V")
chbtestvlab.pack(side=LEFT)
CHBTestVEntry = Entry(TestVB, width=6) #
CHBTestVEntry.pack(side=LEFT)
CHBTestVEntry.delete(0,"end")
CHBTestVEntry.insert(0,0.0)

TestIB = Frame( frame4 )
TestIB.grid(row=4, column=0, sticky=W)
chbtestilab = Label(TestIB, text="CB-I")
chbtestilab.pack(side=LEFT)
CHBTestIEntry = Entry(TestIB, width=6) #
CHBTestIEntry.pack(side=LEFT)
CHBTestIEntry.delete(0,"end")
CHBTestIEntry.insert(0,0.0)
#
DigScreenStatus = IntVar(0)
BuildDigScreen = Button(root, text="Dig Out Screen", width=13, command=MakeDigScreen)
BuildDigScreen.grid(row=2, column=2, columnspan=2, sticky=W)
#
# Setup ADAML1000
devx = Smu()
DevID = devx.serials[0]
print DevID
CHA = devx.channels['A']    # Open CHA
CHA.set_mode('d')           # Put CHA in Hi Z mode
CHB = devx.channels['B']    # Open CHB
CHB.set_mode('d')           # Put CHB in Hi Z mode
DevOne = devx.devices[0]
ADsignal1 = []              # Ain signal array channel
# start main loop
root.update()
# Start sampling
Analog_in()
#
