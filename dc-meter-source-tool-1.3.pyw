#!/usr/bin/python
# ADALM1000 DC volt meter / source tool 11-14-2022
# For use with pysmu / libsmu.rework >= 1.0
# For Python version > = 2.7.8 and 3.7
import __future__
import os
import sys
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
import math
from pysmu import *
#
root = Tk()
RevDate = "14 Nov 2022)"
SWRev = "1.3 "
# small bit map of ADI logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root.title("ALM1000 Meter-Source 1.3 " + RevDate)
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
#
root.tk_focusFollowsMouse()
#
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
# define button actions
RUNstatus = IntVar(0)
CHAstatus = IntVar(0)
CHBstatus = IntVar(0)
CHAmode = IntVar(0)
CHBmode = IntVar(0)
AWGAIOMode = IntVar(0)
AWGBIOMode = IntVar(0)
loopnum = 0
PIO_0 = 28
PIO_1 = 29
PIO_2 = 47
PIO_3 = 3
#
FontSize = 8
COLORwhite = "#ffffff" # 100% white
COLORblack = "#000000" # 100% black
#
#
RDX0L = 20  # Left top X value of Res Div Schem
RDY0T = 20  # Left top Y value of Res Div Schem
RDGRW = 530 - ( RDX0L + 230 ) # Width of the Res Div Schem
RDGRH = 275 - ( 2 * RDY0T )   # Height of the Res Div Schem
R1 = StringVar()  
R2 = StringVar()
Voff = StringVar()
VR2 = StringVar()
ResDivStatus = IntVar(0)
ResDivDisp = IntVar(0)
Rint = 1000000.0 # 1 Meg Ohm M1k internal resistor to ground
RDeffective = Rint
RDGain = 1.0
RDOffset = 0.0
CHAIleak = 0.0 # 400E-9 # Channel A leakage current
CHBIleak = 0.0 # 400E-9 # Channel B leakage current
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
            CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
        else:
            CHA.mode = Mode.HI_Z_SPLIT
    else:
        if CHAmode.get() == 0:
            # Put CHA in SVMI mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.SVMI # Put CHA in SVMI mode
            else:
                CHA.mode = Mode.SVMI_SPLIT # Put CHA in SVMI split mode
            CHA.constant(chatestv)
        else:
            # Put CHA in SIMV mode
            if AWGAIOMode.get() == 0:
                CHA.mode = Mode.SIMV # Put CHA in SIMV mode
            else:
                CHA.mode = Mode.SIMV_SPLIT # Put CHA in SIMV split mode
            CHA.constant(chatesti/1000.0)
    if CHBstatus.get() == 0:
        if AWGBIOMode.get() == 0:
            CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
        else:
            CHB.mode = Mode.HI_Z_SPLIT
    else:
        if CHBmode.get() == 0:
            # Put CHB in SVMI mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.SVMI # Put CHB in SVMI mode
            else:
                CHB.mode = Mode.SVMI_SPLIT # Put CHB in SVMI split mode
            CHB.constant(chbtestv)
        else:
            # Put CHB in SIMV mode
            if AWGBIOMode.get() == 0:
                CHB.mode = Mode.SIMV # Put CHB in SIMV mode
            else:
                CHB.mode = Mode.SIMV_SPLIT # Put CHB in SIMV split mode
            CHB.constant(chbtesti/1000.0)
#
def UpdateAwgCont():
    global session, CHA, CHB, RUNstatus
    # if running and in continuous streaming mode temp stop, flush buffer and restart to change AWG settings
    if RUNstatus.get() == 1:
        if session.continuous:
            #print "About to change awg and Stopping continuous mode"
            session.end()
            #time.sleep(0.02) # wait awhile here for some reason
            #print session.continuous
            if not session.continuous:
                EnabAwg() # set-up new AWG settings
                #print "Just changed awg and Starting continuous mode"
                #time.sleep(0.02)
                session.start(0)
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
    if not session.continuous:
        #print "Run Is Not Continuous? ", session.continuous
        #session.flush()
        session.start(0)
        UpdateAwgCont()
        #time.sleep(0.02)
        
    else:
        #print "Run Is Continuous? ", session.continuous
        UpdateAwgCont()
        session.flush()
        #time.sleep(0.02)
        #print "Starting continuous mode"
    
#
def BStop():
    global RUNstatus, session, CHA, CHB
    
    RUNstatus.set(0)
    # print "Stoping continuous mode"
    # session.cancel() # cancel continuous session mode while paused
    if session.continuous:
        #print "Is Continuous? ", session.continuous
        session.end()
        #time.sleep(0.02)
        CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
        CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
        CHA.constant(0.0)
        CHB.constant(0.0)
        session.flush()
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
            if session.continuous:
                ADsignal1 = devx.read(2000, -1, True)
                #time.sleep(0.01)
            if len(ADsignal1) > 1010:
                for index in range(1000): # calculate average
                    DCVA0 += ADsignal1[index+10][0][0] # VAdata # Sum for average CA voltage 
                    DCVB0 += ADsignal1[index+10][1][0] # VBdata # Sum for average CB voltage
                    DCIA0 += ADsignal1[index+10][0][1] # Sum for average CA current 
                    DCIB0 += ADsignal1[index+10][1][1] # Sum for average CB current

            DCVA0 = DCVA0 / 1000.0 # calculate average
            DCVB0 = DCVB0 / 1000.0 # calculate average
            DCIA0 = DCIA0 / 1000.0 # calculate average
            DCIB0 = DCIB0 / 1000.0 # calculate average
            DCVA0 = (DCVA0 - InOffA) * InGainA
            DCVB0 = (DCVB0 - InOffB) * InGainB
            DCIA0 = ((DCIA0*1000.0) - CurOffA) * CurGainA
            DCIB0 = ((DCIB0*1000.0) - CurOffB) * CurGainB
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
            if idx == 0:
                time.sleep(0.1)
            loopnum = loopnum + 1
    # Update tasks and screens by TKinter
        else:
            time.sleep(0.05) # add small sleep time while not running to reduce CPU usage
            if loopnum > 0:
                CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
                CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
                loopnum = 0
                # session.cancel()
                if session.continuous:
                    session.end()
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
            exec( line.rstrip(), globals(), globals())
            #exec( line.rstrip() )
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
        devx.ctrl_transfer( 0x40, D0.get(), PIO_0, 0, 0, 0, 100) # set PIO 0
        if D0.get() == 0x50:
            digin0.configure(text="Low", bg="#00ff00")
        else:
            digin0.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_0, 0, 0, 1, 100)
        if Dval[0] == 0:
            digin0.configure(text="Low", bg="#00ff00")
        else:
            digin0.configure(text="Hi", bg="#ff0000")
    if D1.get() > 0:
        devx.ctrl_transfer( 0x40, D1.get(), PIO_1, 0, 0, 0, 100) # set PIO 1
        if D1.get() == 0x50:
            digin1.configure(text="Low", bg="#00ff00")
        else:
            digin1.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_1, 0, 0, 1, 100)
        if Dval[0] == 0:
            digin1.configure(text="Low", bg="#00ff00")
        else:
            digin1.configure(text="Hi", bg="#ff0000")
    if D2.get() > 0:
        devx.ctrl_transfer( 0x40, D2.get(), PIO_2, 0, 0, 0, 100) # set PIO 2
        if D2.get() == 0x50:
            digin2.configure(text="Low", bg="#00ff00")
        else:
            digin2.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_2, 0, 0, 1, 100)
        if Dval[0] == 0:
            digin2.configure(text="Low", bg="#00ff00")
        else:
            digin2.configure(text="Hi", bg="#ff0000")
    if D3.get() > 0:
        devx.ctrl_transfer( 0x40, D3.get(), PIO_3, 0, 0, 0, 100) # set PIO 3
        if D3.get() == 0x50:
            digin3.configure(text="Low", bg="#00ff00")
        else:
            digin3.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, PIO_3, 0, 0, 1, 100)
        if Dval[0] == 0:
            digin3.configure(text="Low", bg="#00ff00")
        else:
            digin3.configure(text="Hi", bg="#ff0000")
    if D4.get() > 0:
        devx.ctrl_transfer( 0x40, D4.get(), 4, 0, 0, 0, 100) # set PIO 4
        if D4.get() == 0x50:
            digin4.configure(text="Low", bg="#00ff00")
        else:
            digin4.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 4, 0, 0, 1, 100)
        if Dval[0] == 0:
            digin4.configure(text="Low", bg="#00ff00")
        else:
            digin4.configure(text="Hi", bg="#ff0000")
    if D5.get() > 0:
        devx.ctrl_transfer( 0x40, D5.get(), 5, 0, 0, 0, 100) # set PIO 5
        if D5.get() == 0x50:
            digin5.configure(text="Low", bg="#00ff00")
        else:
            digin5.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 5, 0, 0, 1, 100)
        if Dval[0] == 0:
            digin5.configure(text="Low", bg="#00ff00")
        else:
            digin5.configure(text="Hi", bg="#ff0000")
    if D6.get() > 0:
        devx.ctrl_transfer( 0x40, D6.get(), 6, 0, 0, 0, 100) # set PIO 6
        if D6.get() == 0x50:
            digin6.configure(text="Low", bg="#00ff00")
        else:
            digin6.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 6, 0, 0, 1, 100)
        if Dval[0] == 0:
            digin6.configure(text="Low", bg="#00ff00")
        else:
            digin6.configure(text="Hi", bg="#ff0000")
    if D7.get() > 0:
        devx.ctrl_transfer( 0x40, D7.get(), 7, 0, 0, 0, 100) # set PIO 7
        if D7.get() == 0x50:
            digin7.configure(text="Low", bg="#00ff00")
        else:
            digin7.configure(text="Hi", bg="#ff0000")
    else:
        Dval = devx.ctrl_transfer( 0xc0, 0x91, 7, 0, 0, 1, 100)
        if Dval[0] == 0:
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
    
def SelectBoard():
    global devx, dev0, dev1, dev0, session, BrdSel, CHA, CHB

    if RUNstatus.get() == 1:
        BStop()
    if BrdSel.get() == 0:
        try:
            session.remove(dev1)
        except:
            print( "Skipping dev1")
        try:
            session.remove(dev2)
        except:
            print( "Skipping dev2")
        session.add(dev0)
        devx = dev0
    if BrdSel.get() == 1:
        try:
            session.remove(dev0)
        except:
            print( "Skipping dev0")
        try:
            session.remove(dev2)
        except:
            print( "Skipping dev2")
        session.add(dev1)
        devx = dev1
    #devx = session.devices[BrdSel.get()]
    DevID = devx.serial
    print( DevID)
    print( devx.fwver)
    print( devx.hwver)
    print( devx.default_rate)
    CHA = devx.channels['A']    # Open CHA
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB = devx.channels['B']    # Open CHB
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    session.add(devx)
    #session.start(0)
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
def ReSetAGO():
    global CHAVGainEntry, CHAVOffsetEntry

    CHAVGainEntry.delete(0,"end")
    CHAVGainEntry.insert(0,1.0)
    CHAVOffsetEntry.delete(0,"end")
    CHAVOffsetEntry.insert(0,0.0)
#
def ReSetBGO():
    global CHBVGainEntry, CHBVOffsetEntry

    CHBVGainEntry.delete(0,"end")
    CHBVGainEntry.insert(0,1.0)
    CHBVOffsetEntry.delete(0,"end")
    CHBVOffsetEntry.insert(0,0.0)
#
# Converts User input string with "M" or "k" to floating point number
# So calculations can be done on the user inputs
def UnitConvert(Value):
    
    Value = Value.upper()
    if 'K' in Value:
        Value = str.strip(Value,'K') #
        Value = float(Value) * math.pow(10,3)
    elif 'M' in Value:
        Value = str.strip(Value,'M') #
        Value = float(Value) * math.pow(10,6)
    else:
        Value = float(Value)
    return Value
#
# Calculate resistor divider gain and offset voltage
def RDbutton(): 
    global Rint, RDX0L, display9, display8, Voff, R1, R2, resdivwindow
    global RDGain, RDOffset, RDeffective
    #
    try:
        X = UnitConvert(Voff.get())
        Y = UnitConvert(R1.get())
        Z = UnitConvert(R2.get())
        ZE = (Z * Rint) / (Z + Rint)
        YE = (Y * Rint) / (Y + Rint)
        RDGain =  (Y + ZE) / ZE
        RDOffset = (X * YE)/(YE + Z)
        RDeffective = (Y * ZE) / (Y + ZE)
    except:
        RDOffset = None
        RDGain = None
        X = None
        Y = None
        Z = None

    if ((RDOffset is None) or (X is None) or (Y is None) or (Z is None) or (RDGain is None)):
        display = Label(resdivwindow, text="Calculation Error", foreground = "Red").place(x = RDX0L+80, y = 260)
    else:
        display = Label(resdivwindow, text="Calculation Successful", foreground = "Dark Green").place(x = RDX0L+80, y = 260)
        display9.config(text="%f Offset" %RDOffset)
        display8.config(text="%f Gain" %RDGain)		
#
# Draw a resistor shape at location
def DrawRes(X, Y): 
    global Sche, COLORblack

    ResW = 10
    Sche.create_line(X, Y, X, Y+20, fill=COLORblack, width=3)
    Sche.create_line(X, Y+20, X+ResW, Y+25, fill=COLORblack, width=3)
    Sche.create_line(X+ResW, Y+25, X-ResW, Y+35, fill=COLORblack, width=3)
    Sche.create_line(X-ResW, Y+35, X+ResW, Y+45, fill=COLORblack, width=3)
    Sche.create_line(X+ResW, Y+45, X-ResW, Y+55, fill=COLORblack, width=3)
    Sche.create_line(X-ResW, Y+55, X, Y+60, fill=COLORblack, width=3)
    Sche.create_line(X, Y+60, X, Y+80, fill=COLORblack, width=3)
#
def RDSetAGO():
    global CHAVGainEntry, CHAVOffsetEntry
    global RDGain, RDOffset, CHAIleak, RDeffective

    DivOffset = RDOffset + (CHAIleak * RDeffective)
    Gain_str = '{0:.3f}'.format(RDGain)
    Voff_str = '{0:.3f}'.format(DivOffset)
    CHAVGainEntry.delete(0,"end")
    CHAVGainEntry.insert(0,Gain_str)
    CHAVOffsetEntry.delete(0,"end")
    CHAVOffsetEntry.insert(0,Voff_str)
#
def RDSetBGO():
    global CHBVGainEntry, CHBVOffsetEntry
    global RDGain, RDOffset, CHBIleak, RDeffective

    DivOffset = RDOffset + (CHBIleak * RDeffective)
    Gain_str = '{0:.3f}'.format(RDGain)
    Voff_str = '{0:.3f}'.format(DivOffset)
    CHBVGainEntry.delete(0,"end")
    CHBVGainEntry.insert(0,Gain_str)
    CHBVOffsetEntry.delete(0,"end")
    CHBVOffsetEntry.insert(0,Voff_str)
#
#
def MakeResDivWindow():
    global SWRev, RevDate, ResDivStatus, ResDivDisp, R1, R2, Voff, COLORblack, COLORwhite
    global display8, display9, Sche, resdivwindow, RDGRW, RDGRH, RDY0T, RDX0L
    
    if ResDivStatus.get() == 0:
        ResDivStatus.set(1)
        ResDivDisp.set(1)
        resdivwindow = Toplevel()
        resdivwindow.title("Input Resistor Divider " + SWRev + RevDate)
        resdivwindow.resizable(FALSE,FALSE)
        resdivwindow.protocol("WM_DELETE_WINDOW", DestroyResDivScreen)
        resdivwindow.geometry("530x310")
# from here down we build GUI
        Font_tuple = ("Comic Sans MS", 10, "bold")
        #
        display = Label(resdivwindow, text="M1k Input Resistor Divider", foreground= "Blue",font = Font_tuple)
        display.place(x = RDX0L, y = RDY0T)
        
        display1 = Label(resdivwindow, text="Resistor - R1")
        display1.place(x = RDX0L, y = 60)
        display2 = Entry(resdivwindow,textvariable=R1)
        display2.place(x = RDX0L+80, y = 60)
        
        display3 = Label(resdivwindow, text="Resistor - R2")
        display3.place(x = RDX0L, y = 100)
        display4 = Entry(resdivwindow,textvariable=R2)
        display4.place(x = RDX0L+80, y = 100)
        
        display5 = Label(resdivwindow, text="Offset Voltage")
        display5.place(x = RDX0L, y = 140)
        display6 = Entry(resdivwindow,textvariable=Voff)
        display6.place(x = RDX0L+80, y = 140)
        
        display7 = Label(resdivwindow, text="Divider Offset")
        display7.place(x = RDX0L, y = 180)
        
        display9 = Label(resdivwindow, text="To be calculated", foreground = "Blue")
        display9.place(x = RDX0L+80, y = 180)

        display10 = Label(resdivwindow, text="Divider Gain")
        display10.place(x = RDX0L, y = 220)
        
        display8 = Label(resdivwindow, text="To be calculated", foreground = "Blue")
        display8.place(x = RDX0L+80, y = 220)
        
        Calbutton = Button(resdivwindow, text = "Calculate", command=RDbutton)
        Calbutton.place(x = RDX0L, y = 260)
        
        ResDivdismissbutton = Button(resdivwindow, text="Dismiss", command=DestroyResDivScreen)
        ResDivdismissbutton.place(x = 230, y = 260)

        ResDivCHAsetbutton = Button(resdivwindow, text="Set CH A", command=RDSetAGO)
        ResDivCHAsetbutton.place(x = 330, y = 260)

        ResDivCHBsetbutton = Button(resdivwindow, text="Set CH B", command=RDSetBGO)
        ResDivCHBsetbutton.place(x = 430, y = 260)
        
        Sche = Canvas(resdivwindow, width=RDGRW, height=RDGRH, background=COLORwhite)
        Sche.place(x = 230, y = RDY0T) #
        
        # Draw Schematic
        DrawRes(115, 40)
        Sche.create_text(140, 80, text = "R1", fill=COLORblack, font=("arial", FontSize+4 ))
        DrawRes(115, 120)
        Sche.create_text(140, 160, text = "R2", fill=COLORblack, font=("arial", FontSize+4 ))
        DrawRes(190, 120)
        Sche.create_text(220, 160, text = "Rint", fill=COLORblack, font=("arial", FontSize+4 ))
        Sche.create_text(225, 180, text = "1 Meg", fill=COLORblack, font=("arial", FontSize+4 ))
        Sche.create_line(70, 40, 115, 40, fill=COLORblack, width=3)
        Sche.create_line(70, 200, 115, 200, fill=COLORblack, width=3)
        Sche.create_line(115, 120, 235, 120, fill=COLORblack, width=3)
        Sche.create_line(175, 200, 205, 200, fill=COLORblack, width=3)
        Sche.create_line(175, 200, 190, 220, fill=COLORblack, width=3)
        Sche.create_line(205, 200, 190, 220, fill=COLORblack, width=3)
        Sche.create_rectangle(40, 30, 70, 50, width=3) #
        Sche.create_text(45, 15, text = "V Input", fill=COLORblack, font=("arial", FontSize+4 ))
        Sche.create_rectangle(40, 190, 70, 210, width=3) #
        Sche.create_text(47, 175, text = "V Offset", fill=COLORblack, font=("arial", FontSize+4 ))
        Sche.create_rectangle(235, 110, 265, 130, width=3) #
        Sche.create_text(235, 95, text = "M1k Input", fill=COLORblack, font=("arial", FontSize+4 ))
#
def DestroyResDivScreen():
    global resdivwindow, ResDivStatus, ResDivDisp
    
    ResDivStatus.set(0)
    ResDivDisp.set(0)
    resdivwindow.destroy()
#
# setup main window
#
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
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
calAlab = Button(frame1, text="Adjust CH A Gain/Offset", command=MakeResDivWindow)
calAlab.grid(row=4, column=0, sticky=W)
# Input Probes sub frame 
ProbeAV = Frame( frame1 )
ProbeAV.grid(row=5, column=0, sticky=W)
gainavlab = Button(ProbeAV, text="VA", command=ReSetAGO)
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
gainailab = Button(ProbeAI, text=" IA")
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
calBlab = Button(frame2, text="Adjust CH B Gain/Offset", command=MakeResDivWindow)
calBlab.grid(row=4, column=0, sticky=W)
#
ProbeBV = Frame( frame2 )
ProbeBV.grid(row=5, column=0, sticky=W)
gainbvlab = Button(ProbeBV, text="VB", command=ReSetBGO) 
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
gainbilab = Button(ProbeBI, text=" IB")
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
session = Session(ignore_dataflow=True, queue_size=10000)
# session.add_all()
if not session.devices:
    print( 'no device found')
    root.destroy()
    exit()
# session.configure()

BrdSel = IntVar(0)
Brds = Frame( root )
Brds.grid(row=11, column=0, sticky=W)

for idx, devx in enumerate(session.devices):
    BrdText = "Board # " + str(idx)
    if idx == 0:
        dev0 = devx
        devx.set_led(0b010) # LED.green, 
        brd = Radiobutton(Brds, text=BrdText, fg="green", variable=BrdSel, value=idx, command=SelectBoard)
    elif idx == 1:
        dev1 = devx
        devx.set_led(0b100) # LED.blue,
        brd = Radiobutton(Brds, text=BrdText, fg="blue", variable=BrdSel, value=idx, command=SelectBoard)
    elif idx == 2:
        dev2 = devx
        devx.set_led(0b001) # LED.red, 
        brd = Radiobutton(Brds, text=BrdText, fg="red", variable=BrdSel, value=idx, command=SelectBoard)
    else:  
        brd = Radiobutton(Brds, text=BrdText, variable=BrdSel, value=idx, command=SelectBoard)
    brd.pack(side=LEFT)

SelectBoard()

ADsignal1 = []              # Ain signal array channel

# start main loop
root.update()
# Start sampling
Analog_in()
#
