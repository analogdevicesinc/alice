#!/usr/bin/python
# ADALM1000 DC volt meter / source tool RR 6-6-2021
# For use with pysmu / libsmu.rework >= 1.0
# For Python version > 3.7
# RobotRaconteur requires Python > 3.7
import __future__
import os
import sys
from RobotRaconteur.Client import *

NetAddr = "localhost" # default network address string
InitFileName = "meter_source_init.ini"

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

# define button actions
loopnum = 0
RevDate = "6 June 2021)"
PIO_0 = 28
PIO_1 = 29
PIO_2 = 47
PIO_3 = 3
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
def EnabAwg():
    global InOffA, InGainA, InOffB, InGainB, CHAmode, CHBmode
    global chatestv, chbtestv, chatesti, chbtesti, AWGAIOMode, AWGBIOMode
    global session, DevID, devx, loopnum, CHAstatus, CHBstatus
    
    try:
        chatestv = float(eval(CHATestVEntry.get()))
        if chatestv >= 5.0:
            chatestv = 5.0
            CHATestVEntry.delete(0,END)
            CHATestVEntry.insert(0, chatestv)
        if chatestv <= 0.0:
            chatestv = 0.0
            CHATestVEntry.delete(0,END)
            CHATestVEntry.insert(0, chatestv)
    except:
        CHATestVEntry.delete(0,END)
        CHATestVEntry.insert(0, chatestv)
    try:
        chbtestv = float(eval(CHBTestVEntry.get()))
        if chbtestv >= 5.0:
            chbtestv = 5.0
            CHBTestVEntry.delete(0,END)
            CHBTestVEntry.insert(0, chbtestv)
        if chbtestv <= 0.0:
            chbtestv = 0.0
            CHBTestVEntry.delete(0,END)
            CHBTestVEntry.insert(0, chbtestv)
    except:
        CHBTestVEntry.delete(0,END)
        CHBTestVEntry.insert(0, chbtestv)
    try:
        chatesti = float(eval(CHATestIEntry.get()))
        if chatesti >= 200.0:
            chatesti = 200.0
            CHATestIEntry.delete(0,END)
            CHATestIEntry.insert(0, chatesti)
        if chatesti <= -200.0:
            chatesti = -200.0
            CHATestIEntry.delete(0,END)
            CHATestIEntry.insert(0, chatesti)
    except:
        CHATestIEntry.delete(0,END)
        CHATestIEntry.insert(0, chatesti)
    try:
        chbtesti = float(eval(CHBTestIEntry.get()))
        if chbtesti >= 200.0:
            chbtesti = 200.0
            CHBTestIEntry.delete(0,END)
            CHBTestIEntry.insert(0, chbtesti)
        if chbtesti <= -200.0:
            chbtesti = -200.0
            CHBTestIEntry.delete(0,END)
            CHBTestIEntry.insert(0, chbtesti)
    except:
        CHBTestIEntry.delete(0,END)
        CHBTestIEntry.insert(0, chbtesti)
    #
    if CHAstatus.get() == 0:
        if AWGAIOMode.get() == 0:
            m1k_obj.setmode('A','HI_Z')
            #CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
        else:
            #CHA.mode = Mode.HI_Z_SPLIT
            m1k_obj.setmode('A','HI_Z_SPLIT')
    else:
        if CHAmode.get() == 0:
            # Put CHA in SVMI mode
            if AWGAIOMode.get() == 0:
                m1k_obj.setmode('A','SVMI')
                #CHA.mode = Mode.SVMI # Put CHA in SVMI mode
            else:
                m1k_obj.setmode('A','SVMI_SPLIT')
                #CHA.mode = Mode.SVMI_SPLIT # Put CHA in SVMI split mode
            m1k_obj.setawgconstant('A', chatestv)
        else:
            # Put CHA in SIMV mode
            if AWGAIOMode.get() == 0:
                m1k_obj.setmode('A','SIMV')
                #CHA.mode = Mode.SIMV # Put CHA in SIMV mode
            else:
                m1k_obj.setmode('A','SIMV_SPLIT')
                #CHA.mode = Mode.SIMV_SPLIT # Put CHA in SIMV split mode
            m1k_obj.setawgconstant('A', chatesti/1000.0)
    if CHBstatus.get() == 0:
        if AWGBIOMode.get() == 0:
            m1k_obj.setmode('B','HI_Z')
            #CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
        else:
            m1k_obj.setmode('B','HI_Z_SPLIT')
            #CHB.mode = Mode.HI_Z_SPLIT
    else:
        if CHBmode.get() == 0:
            # Put CHB in SVMI mode
            if AWGBIOMode.get() == 0:
                m1k_obj.setmode('B','SVMI')
                #CHB.mode = Mode.SVMI # Put CHB in SVMI mode
            else:
                m1k_obj.setmode('B','SVMI_SPLIT')
                #CHB.mode = Mode.SVMI_SPLIT # Put CHB in SVMI split mode
            m1k_obj.setawgconstant('B', chbtestv)
        else:
            # Put CHB in SIMV mode
            if AWGBIOMode.get() == 0:
                m1k_obj.setmode('B','SIMV')
                #CHB.mode = Mode.SIMV # Put CHB in SIMV mode
            else:
                m1k_obj.setmode('B','SIMV_SPLIT')
                #CHB.mode = Mode.SIMV_SPLIT # Put CHB in SIMV split mode
            m1k_obj.setawgconstant('B', chbtesti/1000.0)
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
    
def Analog_in():
    # global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global InOffA, InGainA, InOffB, InGainB, labelAI, labelBI, labelAV, labelBV
    global session, DevID, devx, loopnum, labelAPW, labelBPW
    while (True):       # Main loop
        if RUNstatus.get() == 1:
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
            DCVA0 = DCVB0 = DCIA0 = DCIB0 = 0.0 # initalize measurment variable
            if m1k_obj.IsContinuous():
                samples = m1k_obj.ContRead(200)
                #time.sleep(0.01)
            for sample in samples: # calculate average
                DCVA0 += sample.A[0] # Sum for average CA voltage 
                DCVB0 += sample.B[0] # Sum for average CB voltage
                DCIA0 += sample.A[1] # Sum for average CA current 
                DCIB0 += sample.B[1] # Sum for average CB current

            DCVA0 = DCVA0 / 200.0 # calculate average
            DCVB0 = DCVB0 / 200.0 # calculate average
            DCIA0 = DCIA0 / 200.0 # calculate average
            DCIB0 = DCIB0 / 200.0 # calculate average
            DCVA0 = (DCVA0 - InOffA) * InGainA
            DCVB0 = (DCVB0 - InOffB) * InGainB
            DCIA0 = ((DCIA0*100.0) - CurOffA) * CurGainA
            DCIB0 = ((DCIB0*100.0) - CurOffB) * CurGainB
            VAString = "CA V " + ' {0:.4f} '.format(DCVA0) # format with 4 decimal places
            VBString = "CB V " + ' {0:.4f} '.format(DCVB0) # format with 4 decimal places
            labelAV.config(text = VAString) # change displayed value
            labelBV.config(text = VBString) # change displayed value
            VAString = "A-B V " + ' {0:.4f} '.format(DCVA0-DCVB0) # format with 4 decimal places
            VBString = "B-A V " + ' {0:.4f} '.format(DCVB0-DCVA0) # format with 4 decimal places
            labelADV.config(text = VAString) # change displayed value
            labelBDV.config(text = VBString) # change displayed value
            
            if CHAstatus.get() == 0:
                IAString = "CA mA ----"
                PAString = "CA mW ----"
            else:
                IAString = "CA mA " + ' {0:.2f} '.format(DCIA0)
                PAString = "CA mW " + ' {0:.2f} '.format(DCVA0*DCIA0)
            if CHBstatus.get() == 0:
                IBString = "CB mA ----"
                PBString = "CB mW ----"
            else:
                IBString = "CB mA " + ' {0:.2f} '.format(DCIB0)
                PBString = "CB mW " + ' {0:.2f} '.format(DCVB0*DCIB0)
            
            labelAI.config(text = IAString) # change displayed value
            labelAPW.config(text = PAString) # change displayed value
            labelBI.config(text = IBString) # change displayed value
            labelBPW.config(text = PBString) # change displayed value
#
            loopnum = loopnum + 1
    # Update tasks and screens by TKinter
        else:
            if loopnum > 0:
                m1k_obj.setmode('A','HI_Z')
                m1k_obj.setmode('B','HI_Z')
                loopnum = 0
                # session.cancel()
                if m1k_obj.IsContinuous():
                    m1k_obj.EndSession()
                    #print "Stoping Session"
        root.update_idletasks()
        root.update()            

def BSaveCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global CHATestVEntry, CHBTestVEntry, CHATestIEntry, CHBTestVEntry
    global AWGAIOMode, AWGBIOMode, CHAstatus, CHBstatus
    global DevID

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")])
    # open Config file for Write
    CalFile = open(filename, "w")
    #
    CalFile.write('CHAmode.set(' + str(CHAmode.get()) + ')\n')
    CalFile.write('CHBmode.set(' + str(CHBmode.get()) + ')\n')
    CalFile.write('AWGAIOMode.set(' + str(AWGAIOMode.get()) + ')\n')
    CalFile.write('AWGBIOMode.set(' + str(AWGBIOMode.get()) + ')\n')
    CalFile.write('CHAstatus.set(' + str(CHAstatus.get()) + ')\n')
    CalFile.write('CHBstatus.set(' + str(CHBstatus.get()) + ')\n')
    
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
    CalFile.write('CHATestVEntry.delete(0,END)\n')
    CalFile.write('CHATestVEntry.insert(4, ' + CHATestVEntry.get() + ')\n')
    CalFile.write('CHBTestVEntry.delete(0,END)\n')
    CalFile.write('CHBTestVEntry.insert(4, ' + CHBTestVEntry.get() + ')\n')
    CalFile.write('CHATestIEntry.delete(0,END)\n')
    CalFile.write('CHATestIEntry.insert(4, ' + CHATestIEntry.get() + ')\n')
    CalFile.write('CHBTestVEntry.delete(0,END)\n')
    CalFile.write('CHBTestVEntry.insert(4, ' + CHBTestVEntry.get() + ')\n')
    CalFile.close()

def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHBIGainEntry, CHAIOffsetEntry, CHBIOffsetEntry
    global CHATestVEntry, CHBTestVEntry, CHATestIEntry, CHBTestVEntry
    global SelCHA, SelCHB, AWGAIOMode, AWGBIOMode, CHAstatus, CHBstatus
    global DevID

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")])

    CalFile = open(filename)
    for line in CalFile:
        try:
            exec( line.rstrip() )
        except:
            print( "Skipping " + line.rstrip())
    CalFile.close()

def DestroyDigScreen():
    global win1, DigScreenStatus
    
    DigScreenStatus.set(0)
    win1.destroy()

def sel():
    global devx, DevID, DevOne
    global D0, D1, D2, D3, D4, D5, D6, D7
    global PIO_0, PIO_1, PIO_2, PIO_3
    global digin0, digin1, digin2, digin3, digin4, digin5, digin6, digin7
    # sending 0x50 = set to 0, 0x51 = set to 1
    if D0.get() > 0:
        m1k_obj.setpio('PIO_0', D0.get())
        if D0.get() == 0x50:
            digin0.configure(text="Low", bg="#00ff00")
        else:
            digin0.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_0')
        if Dval == 0:
            digin0.configure(text="Low", bg="#00ff00")
        else:
            digin0.configure(text="Hi", bg="#ff0000")
    if D1.get() > 0:
        m1k_obj.setpio('PIO_1', D1.get())
        if D1.get() == 0x50:
            digin1.configure(text="Low", bg="#00ff00")
        else:
            digin1.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_1')
        if Dval == 0:
            digin1.configure(text="Low", bg="#00ff00")
        else:
            digin1.configure(text="Hi", bg="#ff0000")
    if D2.get() > 0:
        m1k_obj.setpio('PIO_2', D2.get())
        if D2.get() == 0x50:
            digin2.configure(text="Low", bg="#00ff00")
        else:
            digin2.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_2')
        if Dval == 0:
            digin2.configure(text="Low", bg="#00ff00")
        else:
            digin2.configure(text="Hi", bg="#ff0000")
    if D3.get() > 0:
        m1k_obj.setpio('PIO_3', D3.get())
        if D3.get() == 0x50:
            digin3.configure(text="Low", bg="#00ff00")
        else:
            digin3.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_3')
        if Dval == 0:
            digin3.configure(text="Low", bg="#00ff00")
        else:
            digin3.configure(text="Hi", bg="#ff0000")
    if D4.get() > 0:
        m1k_obj.setpio('PIO_4', D4.get())
        if D4.get() == 0x50:
            digin4.configure(text="Low", bg="#00ff00")
        else:
            digin4.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_4')
        if Dval == 0:
            digin4.configure(text="Low", bg="#00ff00")
        else:
            digin4.configure(text="Hi", bg="#ff0000")
    if D5.get() > 0:
        m1k_obj.setpio('PIO_5', D5.get())
        if D5.get() == 0x50:
            digin5.configure(text="Low", bg="#00ff00")
        else:
            digin5.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_5')
        if Dval == 0:
            digin5.configure(text="Low", bg="#00ff00")
        else:
            digin5.configure(text="Hi", bg="#ff0000")
    if D6.get() > 0:
        m1k_obj.setpio('PIO_6', D6.get())
        if D6.get() == 0x50:
            digin6.configure(text="Low", bg="#00ff00")
        else:
            digin6.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_6')
        if Dval == 0:
            digin6.configure(text="Low", bg="#00ff00")
        else:
            digin6.configure(text="Hi", bg="#ff0000")
    if D7.get() > 0:
        m1k_obj.setpio('PIO_7', D7.get())
        if D7.get() == 0x50:
            digin7.configure(text="Low", bg="#00ff00")
        else:
            digin7.configure(text="Hi", bg="#ff0000")
    else:
        Dval = m1k_obj.getpio('PIO_7')
        if Dval == 0:
            digin7.configure(text="Low", bg="#00ff00")
        else:
            digin7.configure(text="Hi", bg="#ff0000")

def MakeDigScreen():
    global D0, D1, D2, D3, D4, D5, D6, D7
    global DigScreenStatus, win1
    global digin0, digin1, digin2, digin3, digin4, digin5, digin6, digin7
    # setup Dig output window
    if DigScreenStatus.get() == 0:
        DigScreenStatus.set(1)
        win1 = Toplevel()
        win1.title("Digital Controls")
        win1.resizable(FALSE,FALSE)

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
        digin0 = Label(win1, text="Low", bg = "#00ff00")
        digin0.grid(row=2, column=3, sticky=W)
        rb3 = Radiobutton(win1, text="D1-0", variable=D1, value=0x50, command=sel )
        rb3.grid(row=3, column=0, sticky=W)
        rb3z = Radiobutton(win1, text="D1-Z", variable=D1, value=0, command=sel )
        rb3z.grid(row=3, column=1, sticky=W)
        rb4 = Radiobutton(win1, text="D1-1", variable=D1, value=0x51, command=sel )
        rb4.grid(row=3, column=2, sticky=W)
        digin1 = Label(win1, text="Low", bg = "#00ff00")
        digin1.grid(row=3, column=3, sticky=W)
        rb5 = Radiobutton(win1, text="D2-0", variable=D2, value=0x50, command=sel )
        rb5.grid(row=4, column=0, sticky=W)
        rb5z = Radiobutton(win1, text="D2-Z", variable=D2, value=0, command=sel )
        rb5z.grid(row=4, column=1, sticky=W)
        rb6 = Radiobutton(win1, text="D2-1", variable=D2, value=0x51, command=sel )
        rb6.grid(row=4, column=2, sticky=W)
        digin2 = Label(win1, text="Low", bg = "#00ff00")
        digin2.grid(row=4, column=3, sticky=W)
        rb7 = Radiobutton(win1, text="D3-0", variable=D3, value=0x50, command=sel )
        rb7.grid(row=5, column=0, sticky=W)
        rb7z = Radiobutton(win1, text="D3-Z", variable=D3, value=0, command=sel )
        rb7z.grid(row=5, column=1, sticky=W)
        rb8 = Radiobutton(win1, text="D3-1", variable=D3, value=0x51, command=sel )
        rb8.grid(row=5, column=2, sticky=W)
        digin3 = Label(win1, text="Low", bg = "#00ff00")
        digin3.grid(row=5, column=3, sticky=W)
        rb9 = Radiobutton(win1, text="D4-0", variable=D4, value=0x50, command=sel )
        rb9.grid(row=6, column=0, sticky=W)
        rb9z = Radiobutton(win1, text="D4-Z", variable=D4, value=0, command=sel )
        rb9z.grid(row=6, column=1, sticky=W)
        rb10 = Radiobutton(win1, text="D4-1", variable=D4, value=0x51, command=sel )
        rb10.grid(row=6, column=2, sticky=W)
        digin4 = Label(win1, text="Low", bg = "#00ff00")
        digin4.grid(row=6, column=3, sticky=W)
        rb11 = Radiobutton(win1, text="D5-0", variable=D5, value=0x50, command=sel )
        rb11.grid(row=7, column=0, sticky=W)
        rb11z = Radiobutton(win1, text="D5-Z", variable=D5, value=0, command=sel )
        rb11z.grid(row=7, column=1, sticky=W)
        rb12 = Radiobutton(win1, text="D5-1", variable=D5, value=0x51, command=sel )
        rb12.grid(row=7, column=2, sticky=W)
        digin5 = Label(win1, text="Low", bg = "#00ff00")
        digin5.grid(row=7, column=3, sticky=W)
        rb13 = Radiobutton(win1, text="D6-0", variable=D6, value=0x50, command=sel )
        rb13.grid(row=8, column=0, sticky=W)
        rb13z = Radiobutton(win1, text="D6-Z", variable=D6, value=0, command=sel )
        rb13z.grid(row=8, column=1, sticky=W)
        rb13 = Radiobutton(win1, text="D6-1", variable=D6, value=0x51, command=sel )
        rb13.grid(row=8, column=2, sticky=W)
        digin6 = Label(win1, text="Low", bg = "#00ff00")
        digin6.grid(row=8, column=3, sticky=W)
        rb14 = Radiobutton(win1, text="D7-0", variable=D7, value=0x50, command=sel )
        rb14.grid(row=9, column=0, sticky=W)
        rb14z = Radiobutton(win1, text="D7-Z", variable=D7, value=0, command=sel )
        rb14z.grid(row=9, column=1, sticky=W)
        rb15 = Radiobutton(win1, text="D7-1", variable=D7, value=0x51, command=sel )
        rb15.grid(row=9, column=2, sticky=W)
        digin7 = Label(win1, text="Low", bg = "#00ff00")
        digin7.grid(row=9, column=3, sticky=W)

        dismissbutton = Button(win1, text="Dismiss", command=DestroyDigScreen)
        dismissbutton.grid(row=10, column=0, sticky=W)
#
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
    if SCLKPort.get() == 0:
        Sclk = 'PIO_0'
    elif SCLKPort.get() == 1:
        Sclk = 'PIO_1'
    elif SCLKPort.get() == 2:
        Sclk = 'PIO_3'
    elif SCLKPort.get() == 3:
        Sclk = 'PIO_3'
    if SLATCHPort.get() == 0:
        SLatch = 'PIO_0'
    elif SLATCHPort.get() == 1:
        SLatch = 'PIO_1'
    elif SLATCHPort.get() == 2:
        SLatch = 'PIO_3'
    elif SLATCHPort.get() == 3:
        SLatch = 'PIO_3'
    if SDATAPort.get() == 0:
        SData = 'PIO_0'
    elif SDATAPort.get() == 1:
        SData = 'PIO_1'
    elif SDATAPort.get() == 2:
        SData = 'PIO_3'
    elif SDATAPort.get() == 3:
        SData = 'PIO_3'
    m1k_obj.setpio(Sclk, ClockInt)
    m1k_obj.setpio(SLatch, LatchInt)
    i = 1
    while i < datalen+1:
        if SerDirection.get() == 1: # for MSB first
            D1code = 0x50 + int(datastr[datalen-i]) # 0x50 = set to 0, 0x51 = set to 1
        else:
            D1code = 0x50 + int(datastr[i-1]) # for LSB first
        m1k_obj.setpio(SData, D1code)
        m1k_obj.setpio(Sclk, ClockEnd)
        m1k_obj.setpio(Sclk, ClockInt)
        i = i + 1
    
    m1k_obj.setpio(Sclk, ClockEnd)
    m1k_obj.setpio(SLatch, LatchEnd)
    m1k_obj.setpio(SLatch, LatchInt)
    m1k_obj.setpio(SLatch, LatchEnd)
#
def MakeAD5626Window():
    global ad5626window, AD5626SerialStatus, SCLKPort, SDATAPort, SLATCHPort, SLatchPhase, SClockPhase
    global DigScreenStatus
    global AD5626Entry, SerDirection
    global PIO_0, PIO_1, PIO_2, PIO_3

    if DigScreenStatus.get() == 1:
        DigScreenStatus.set(0)
        DestroyDigScreen()
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
        bsn1 = Button(ad5626window, text='Send', command=BSendGS)
        bsn1.grid(row=5, column=0, sticky=W)
        dismissgsbutton = Button(ad5626window, text="Dismiss", command=DestroyAD5626Screen)
        dismissgsbutton.grid(row=5, column=1, columnspan=2, sticky=W, pady=4)
#
def onAD5626Scroll(event):
    onTextScroll(event)
    BSendGS()
    
def DestroyAD5626Screen():
    global ad5626window, AD5626SerialStatus
    
    AD5626SerialStatus.set(0)
    ad5626window.destroy()
#
def donothing():
    print( "doing nothing")
    
##def SelectBoard():
##    global devx, dev0, dev1, dev0, session, BrdSel, CHA, CHB
##
##    if RUNstatus.get() == 1:
##        BStop()
##    if BrdSel.get() == 0:
##        try:
##            session.remove(dev1)
##        except:
##            print( "Skipping dev1")
##        try:
##            session.remove(dev2)
##        except:
##            print( "Skipping dev2")
##        session.add(dev0)
##        devx = dev0
##    if BrdSel.get() == 1:
##        try:
##            session.remove(dev0)
##        except:
##            print( "Skipping dev0")
##        try:
##            session.remove(dev2)
##        except:
##            print( "Skipping dev2")
##        session.add(dev1)
##        devx = dev1
##    #devx = session.devices[BrdSel.get()]
##    DevID = devx.serial
##    print( DevID)
##    print( devx.fwver)
##    print( devx.hwver)
##    print( devx.default_rate)
##    CHA = devx.channels['A']    # Open CHA
##    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
##    CHB = devx.channels['B']    # Open CHB
##    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
##    #devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
##    #devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
##    session.add(devx)
##    #session.start(0)
#
def Bcloseexit():
    global RUNstatus, session, CHA, CHB, devx, AWG_2X
    
    RUNstatus.set(0)
    # BSaveConfig("alice-last-config.cfg")
    try:
        # Put channels in Hi-Z and exit
        m1k_obj.setmode('A','HI_Z')
        m1k_obj.setmode('B','HI_Z')
        #m1k_obj.setawgconstant('A', 0.0)
        #m1k_obj.setawgconstant('N', 0.0)
        m1k_obj.setled(1 % 8) # Set LED.red on the way out
        if m1k_obj.IsContinuous():
            m1k_obj.EndSession()
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
root.title("ALM1000 Meter-Source RR " + RevDate)
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
#
root.tk_focusFollowsMouse()
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
windowingsystem = root.tk.call('tk', 'windowingsystem')
# 'aqua' built-in native Mac OS X only; Native Mac OS X
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    Style_String = 'aqua'
    # On Macs, allow the dock icon to deiconify.
    root.createcommand('::tk::mac::ReopenApplication', root.deiconify)
    root.createcommand('::tk::mac::Quit', Bcloseexit)
    # On Macs, set up menu bar to be minimal.
    root.option_add('*tearOff', False)
    menubar = tk.Menu(root)
    appmenu = tk.Menu(menubar, name='apple')
    menubar.add_cascade(menu=appmenu)
    # appmenu.add_command(label='Exit', command=Bcloseexit)
    root['menu'] = menubar
else:
    Style_String = 'alt'
print("Windowing System is " + str(windowingsystem))
#root.style.configure("Stop.TRadiobutton", background="red")
#root.style.configure("Run.TRadiobutton", background="green")
RUNstatus = IntVar(0)
CHAstatus = IntVar(0)
CHBstatus = IntVar(0)
CHAmode = IntVar(0)
CHBmode = IntVar(0)
AWGAIOMode = IntVar(0)
AWGBIOMode = IntVar(0)
#
buttons = Frame( root )
buttons.grid(row=0, column=0, columnspan=4, sticky=W)
rb1 = Radiobutton(buttons, text="Stop", bg = "#ff0000", variable=RUNstatus, value=0, command=BStop )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", bg = "#00ff00", variable=RUNstatus, value=1, command=BStart )
rb2.pack(side=LEFT)
b3 = Button(buttons, text='Exit', command=Bcloseexit)
b3.pack(side=LEFT)
b1 = Button(buttons, text='Save Confg', command=BSaveCal)
b1.pack(side=LEFT)
b2 = Button(buttons, text='Load Confg', command=BLoadCal)
b2.pack(side=LEFT)
#
DigScreenStatus = IntVar(0)
AD5626SerialStatus = IntVar(0)
BuildDigScreen = Button(buttons, text="Digital Controls", width=13, command=MakeDigScreen)
BuildDigScreen.pack(side=LEFT)
AD5626SerialScreen = Button(buttons, text="AD5626 Output", width=13, command=MakeAD5626Window)
AD5626SerialScreen.pack(side=LEFT)
#
frame1 = Frame(root, borderwidth=5, relief=RIDGE)
frame1.grid(row=1, column=0, rowspan=2, sticky=W) # 
frame2 = Frame(root, borderwidth=5, relief=RIDGE)
frame2.grid(row=1, column=1, rowspan=2, sticky=W) # 
frame3 = Frame(root, borderwidth=5, relief=RIDGE)
frame3.grid(row=1, column=2, sticky=NW) # 
frame4 = Frame(root, borderwidth=5, relief=RIDGE)
frame4.grid(row=1, column=3, sticky=NW) # 
#
labelCA = Label(frame1, font = "Arial 16 bold")
labelCA.grid(row=0, column=0, columnspan=2, sticky=W)
labelCA.config(text = "CA Meter")

labelAV = Label(frame1, font = "Arial 16 bold")
labelAV.grid(row=1, column=0, columnspan=2, sticky=W)
labelAV.config(text = "CA-V 0.0000")

labelADV = Label(frame1, font = "Arial 16 bold")
labelADV.grid(row=2, column=0, columnspan=2, sticky=W)
labelADV.config(text = "A-B V 0.0000")

labelAI = Label(frame1, font = "Arial 16 bold")
labelAI.grid(row=3, column=0, columnspan=2, sticky=W)
labelAI.config(text = "CA-I 0.00")
# input probe wigets
calAlab = Label(frame1, text="CH A Gain/Offset calibration")
calAlab.grid(row=4, column=0, sticky=W)
# Input Probes sub frame 
ProbeAV = Frame( frame1 )
ProbeAV.grid(row=5, column=0, sticky=W)
gainavlab = Label(ProbeAV, text="VA")
gainavlab.pack(side=LEFT)
CHAVGainEntry = Entry(ProbeAV, width=6) #
CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
CHAVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVGainEntry.bind("<Button-5>", onTextScroll)
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,1.0)
CHAVOffsetEntry = Entry(ProbeAV, width=6) #
CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVOffsetEntry.bind("<Button-5>", onTextScroll)
CHAVOffsetEntry.pack(side=LEFT)
CHAVOffsetEntry.delete(0,"end")
CHAVOffsetEntry.insert(0,0.0)
#
ProbeAI = Frame( frame1 )
ProbeAI.grid(row=6, column=0, sticky=W)
gainailab = Label(ProbeAI, text=" IA ")
gainailab.pack(side=LEFT)
CHAIGainEntry = Entry(ProbeAI, width=6) #
CHAIGainEntry.bind('<MouseWheel>', onTextScroll)
CHAIGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAIGainEntry.bind("<Button-5>", onTextScroll)
CHAIGainEntry.pack(side=LEFT)
CHAIGainEntry.delete(0,"end")
CHAIGainEntry.insert(0,1.0)
CHAIOffsetEntry = Entry(ProbeAI, width=6)
CHAIOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAIOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAIOffsetEntry.bind("<Button-5>", onTextScroll)
CHAIOffsetEntry.pack(side=LEFT)
CHAIOffsetEntry.delete(0,"end")
CHAIOffsetEntry.insert(0,0.0)
#
labelCB = Label(frame2, font = "Arial 16 bold")
labelCB.grid(row=0, column=0, columnspan=2, sticky=W)
labelCB.config(text = "CB Meter")

labelBV = Label(frame2, font = "Arial 16 bold")
labelBV.grid(row=1, column=0, columnspan=2, sticky=W)
labelBV.config(text = "CB-V 0.0000")

labelBDV = Label(frame2, font = "Arial 16 bold")
labelBDV.grid(row=2, column=0, columnspan=2, sticky=W)
labelBDV.config(text = "B-A V 0.0000")

labelBI = Label(frame2, font = "Arial 16 bold")
labelBI.grid(row=3, column=0, columnspan=2, sticky=W)
labelBI.config(text = "CB-I 0.00")
# input probe wigets
calBlab = Label(frame2, text="CH B Gain/Offset calibration")
calBlab.grid(row=4, column=0, sticky=W)
#
ProbeBV = Frame( frame2 )
ProbeBV.grid(row=5, column=0, sticky=W)
gainbvlab = Label(ProbeBV, text="VB")
gainbvlab.pack(side=LEFT)
CHBVGainEntry = Entry(ProbeBV, width=6) #
CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
CHBVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVGainEntry.bind("<Button-5>", onTextScroll)
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,1.0)
CHBVOffsetEntry = Entry(ProbeBV, width=6) #
CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVOffsetEntry.bind("<Button-5>", onTextScroll)
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,0.0)
#
ProbeBI = Frame( frame2 )
ProbeBI.grid(row=6, column=0, sticky=W)
gainbilab = Label(ProbeBI, text=" IB ")
gainbilab.pack(side=LEFT)
CHBIGainEntry = Entry(ProbeBI, width=6) #
CHBIGainEntry.bind('<MouseWheel>', onTextScroll)
CHBIGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBIGainEntry.bind("<Button-5>", onTextScroll)
CHBIGainEntry.pack(side=LEFT)
CHBIGainEntry.delete(0,"end")
CHBIGainEntry.insert(0,1.0)
CHBIOffsetEntry = Entry(ProbeBI, width=6) #
CHBIOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBIOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBIOffsetEntry.bind("<Button-5>", onTextScroll)
CHBIOffsetEntry.pack(side=LEFT)
CHBIOffsetEntry.delete(0,"end")
CHBIOffsetEntry.insert(0,0.0)
#
labelAS = Label(frame3, font = "Arial 16 bold")
labelAS.grid(row=0, column=0, columnspan=2, sticky=W)
labelAS.config(text = "CA Source")

labelAPW = Label(frame3, font = "Arial 16 bold")
labelAPW.grid(row=1, column=0, columnspan=2, sticky=W)
labelAPW.config(text = "CA Power")

chaonbutton = Frame( frame3 )
chaonbutton.grid(row=2, column=0, columnspan=2, sticky=W)
rbaoff = Radiobutton(chaonbutton, text="CHA off", variable=CHAstatus, value=0, command=UpdateAwgCont )
rbaoff.pack(side=LEFT)
rbaon = Radiobutton(chaonbutton, text="CHA on", variable=CHAstatus, value=1, command=UpdateAwgCont )
rbaon.pack(side=LEFT)

chaivbutton = Frame( frame3 )
chaivbutton.grid(row=3, column=0, columnspan=2, sticky=W)
rbav = Radiobutton(chaivbutton, text="CHA V", variable=CHAmode, value=0, command=UpdateAwgCont )
rbav.pack(side=LEFT)
rbai = Radiobutton(chaivbutton, text="CHA I", variable=CHAmode, value=1, command=UpdateAwgCont )
rbai.pack(side=LEFT)

chaiomode = Checkbutton(frame3, text="Split I/O", variable=AWGAIOMode, command=EnabAwg)
chaiomode.grid(row=4, column=0, columnspan=2, sticky=W)

TestVA = Frame( frame3 )
TestVA.grid(row=5, column=0, sticky=W)
chatestvlab = Label(TestVA, text="CA-V")
chatestvlab.pack(side=LEFT)
CHATestVEntry = Entry(TestVA, width=6) #
CHATestVEntry.bind('<MouseWheel>', onAWGscroll)
CHATestVEntry.bind("<Button-4>", onAWGscroll)# with Linux OS
CHATestVEntry.bind("<Button-5>", onAWGscroll)
CHATestVEntry.pack(side=LEFT)
CHATestVEntry.delete(0,"end")
CHATestVEntry.insert(0,0.0)
chaunitsvlab = Label(TestVA, text="Volts")
chaunitsvlab.pack(side=LEFT)

TestIA = Frame( frame3 )
TestIA.grid(row=6, column=0, sticky=W)
chatestilab = Label(TestIA, text="CA-I")
chatestilab.pack(side=LEFT)
CHATestIEntry = Entry(TestIA, width=6) #
CHATestIEntry.bind('<MouseWheel>', onAWGscroll)
CHATestIEntry.bind("<Button-4>", onAWGscroll)# with Linux OS
CHATestIEntry.bind("<Button-5>", onAWGscroll)
CHATestIEntry.pack(side=LEFT)
CHATestIEntry.delete(0,"end")
CHATestIEntry.insert(0,0.0)
chaunitsilab = Label(TestIA, text="mAmps")
chaunitsilab.pack(side=LEFT)
#
labelBS = Label(frame4, font = "Arial 16 bold")
labelBS.grid(row=0, column=0, columnspan=2, sticky=W)
labelBS.config(text = "CB Source")

labelBPW = Label(frame4, font = "Arial 16 bold")
labelBPW.grid(row=1, column=0, columnspan=2, sticky=W)
labelBPW.config(text = "CB Power")

chbonbutton = Frame( frame4 )
chbonbutton.grid(row=2, column=0, columnspan=2, sticky=W)
rbboff = Radiobutton(chbonbutton, text="CHB off", variable=CHBstatus, value=0, command=UpdateAwgCont )
rbboff.pack(side=LEFT)
rbbon = Radiobutton(chbonbutton, text="CHB on", variable=CHBstatus, value=1, command=UpdateAwgCont )
rbbon.pack(side=LEFT)

chbivbutton = Frame( frame4 )
chbivbutton.grid(row=3, column=0, columnspan=2, sticky=W)
rbbv = Radiobutton(chbivbutton, text="CHB V", variable=CHBmode, value=0, command=UpdateAwgCont )
rbbv.pack(side=LEFT)
rbbi = Radiobutton(chbivbutton, text="CHB I", variable=CHBmode, value=1, command=UpdateAwgCont )
rbbi.pack(side=LEFT)

chbiomode = Checkbutton(frame4, text="Split I/O", variable=AWGBIOMode, command=EnabAwg)
chbiomode.grid(row=4, column=0, columnspan=2, sticky=W)

TestVB = Frame( frame4 )
TestVB.grid(row=5, column=0, sticky=W)
chbtestvlab = Label(TestVB, text="CB-V")
chbtestvlab.pack(side=LEFT)
CHBTestVEntry = Entry(TestVB, width=6) #
CHBTestVEntry.bind('<MouseWheel>', onAWGscroll)
CHBTestVEntry.bind("<Button-4>", onAWGscroll)# with Linux OS
CHBTestVEntry.bind("<Button-5>", onAWGscroll)
CHBTestVEntry.pack(side=LEFT)
CHBTestVEntry.delete(0,"end")
CHBTestVEntry.insert(0,0.0)
chbunitsvlab = Label(TestVB, text="Volts")
chbunitsvlab.pack(side=LEFT)

TestIB = Frame( frame4 )
TestIB.grid(row=6, column=0, sticky=W)
chbtestilab = Label(TestIB, text="CB-I")
chbtestilab.pack(side=LEFT)
CHBTestIEntry = Entry(TestIB, width=6) #
CHBTestIEntry.bind('<MouseWheel>', onAWGscroll)
CHBTestIEntry.bind("<Button-4>", onAWGscroll)# with Linux OS
CHBTestIEntry.bind("<Button-5>", onAWGscroll)
CHBTestIEntry.pack(side=LEFT)
CHBTestIEntry.delete(0,"end")
CHBTestIEntry.insert(0,0.0)
chbunitsilab = Label(TestIB, text="mAmps")
chbunitsilab.pack(side=LEFT)
# Setup ADAML1000
##session = Session(ignore_dataflow=True, queue_size=10000)
### session.add_all()
##if not session.devices:
##    print( 'no device found')
##    root.destroy()
##    exit()
### session.configure()

BrdSel = IntVar(0)
##Brds = Frame( root )
##Brds.grid(row=11, column=0, sticky=W)
##
##for idx, devx in enumerate(session.devices):
##    BrdText = "Board # " + str(idx)
##    if idx == 0:
##        #dev0 = devx
##        m1k_obj.setled(2 % 8)
##        #devx.set_led(0b010) # LED.green, 
##        brd = Radiobutton(Brds, text=BrdText, fg="green", variable=BrdSel, value=idx, command=SelectBoard)
##    elif idx == 1:
##        #dev1 = devx
##        m1k_obj.setled(4 % 8)
##        #devx.set_led(0b100) # LED.blue,
##        brd = Radiobutton(Brds, text=BrdText, fg="blue", variable=BrdSel, value=idx, command=SelectBoard)
##    elif idx == 2:
##        #dev2 = devx
##        #devx.set_led(0b001) # LED.red,
##        m1k_obj.setled(1 % 8)
##        brd = Radiobutton(Brds, text=BrdText, fg="red", variable=BrdSel, value=idx, command=SelectBoard)
##    else:  
##        brd = Radiobutton(Brds, text=BrdText, variable=BrdSel, value=idx, command=SelectBoard)
##    brd.pack(side=LEFT)

#
##Start Service and robot setup
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
m1k_obj.setmode('A','HI_Z_SPLIT')
m1k_obj.setmode('B','HI_Z_SPLIT')

ADsignal1 = []              # Ain signal array channel
m1k_obj.setled(2 % 8)
# start main loop
root.update()
# Start sampling
Analog_in()
#
