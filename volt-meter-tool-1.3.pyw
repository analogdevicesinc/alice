#!/usr/bin/python
# ADALM1000 DC Voltmeter Tool 1.3 7-17-2021
# For pysmu ( libsmu > = 1.0 )
#For Python version > = 2.7.8 and 3.7
import __future__
import os
import sys
if sys.version_info[0] == 2:
    print ("Python 2.x")
    import urllib2
    import tkFont
    from Tkinter import *
    from ttk import *
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
    from tkSimpleDialog import askstring
    from tkMessageBox import *
if sys.version_info[0] == 3:
    print ("Python 3.x")    
    import urllib.request, urllib.error, urllib.parse
    from tkinter.font import *
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import *
#
import time
import math
#
# check which operating system
import platform
#
try:
    from pysmu import *
    pysmu_found = True
except:
    pysmu_found = False
#
root = Tk()
RevDate = "17 July 2021)"
SWRev = "1.3 "
# small bit map of ADI logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root.title("ALM1000 Voltmeter " + SWRev + RevDate )
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
print("Windowing System is " + str(root.tk.call('tk', 'windowingsystem')))
#
InitFileName = "analog_meter_init.ini"
#
MouseFocus = 1
#
COLORcanvas = "#000000"   # 100% black
COLORgrid = "#808080"     # 50% Gray
COLORtrace1 = "#00ff00"   # 100% green
COLORtrace2 = "#ff8000"   # 100% orange
COLORtext = "#ffffff"     # 100% white
COLORdial = "#404040"     # 25% Gray
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
GUITheme = "Light"
ColorMode = IntVar(0)
# # Can be Light or Dark or Blue or LtBlue or Custom where:
FrameBG = "#d7d7d7" # Background color for frame
ButtonText = "#000000" # Button Text color
# Widget relief can be RAISED, GROOVE, RIDGE, and FLAT
ButRelief = RAISED
LabRelief = FLAT
FrameRefief = RIDGE
LocalLanguage = "English"
FontSize = 8
BorderSize = 1
GridWidth = IntVar(0)
GridWidth.set(2)
TRACEwidth = IntVar(0)
TRACEwidth.set(3)
MAScreenStatus = IntVar(0)
RUNstatus = IntVar(0)
# Analog Meter Variables
MGRW = 400                 # Width of the Analog Meter face 400 default
MGRH = 400                 # Height of the Analog Meter face 400 default
Mmin = 0.0                 # Meter Scale Min Value
Mmax = 5.0                 # Meter Scale Max Value
MajorDiv = 10              # Meter Scale number of div
MinorDiv = 5
DialSpan = 270             # Number of degrees for analog meter dial
MeterLabelText = "Volts"
InOffA = 0.0
InGainA = 1.0
InOffB = 0.0
InGainB = 1.0
#('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
# 'aqua' built-in native Mac OS X only; Native Mac OS X
windowingsystem = root.tk.call('tk', 'windowingsystem')
ScreenWidth = root.winfo_screenwidth()
ScreenHeight = root.winfo_screenheight()
# print(str(ScreenWidth) + "X" + str(ScreenHeight))
if (root.tk.call('tk', 'windowingsystem')=='aqua'):
    Style_String = 'aqua'
    # On Macs, allow the dock icon to deiconify.
    root.createcommand('::tk::mac::ReopenApplication', root.deiconify)
    root.createcommand('::tk::mac::Quit', root.destroy)# Bcloseexit)
    # On Macs, set up menu bar to be minimal.
    root.option_add('*tearOff', False)
    if sys.version_info[0] == 2:
        menubar = tKinter.Menu(root)
        appmenu = tKinter.Menu(menubar, name='apple')
    else:
        menubar = tkinter.Menu(root)
        appmenu = tkinter.Menu(menubar, name='apple')
    # menubar = tk.Menu(root)
    # appmenu = tk.Menu(menubar, name='apple')
    menubar.add_cascade(menu=appmenu)
    # appmenu.add_command(label='Exit', command=Bcloseexit)
    root['menu'] = menubar
else:
    Style_String = 'alt'
## Check if there is an analog_meter_init.ini file to read in
try:
    InitFile = open(InitFileName) # "analog_meter_init.ini"
    for line in InitFile:
        try:
            exec( line.rstrip(), globals(), globals())
            #exec( line.rstrip() )
        except:
            print("Skiping " + line.rstrip()) 
    InitFile.close()
except:
    print( "No Init File Read. " + InitFileName + " Not Found")
#
root.style = Style()
try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
if MouseFocus == 1:
    root.tk_focusFollowsMouse()
#
DevID = "m1k"
MXcenter = int(MGRW/2.0)   # Meter Center
MYcenter = int(MGRH/2.0)
MRadius = MXcenter - 50    # Meter Radius
#
if sys.version_info[0] == 2:
    default_font = tkFont.nametofont("TkDefaultFont")
if sys.version_info[0] == 3:
    default_font = tkinter.font.nametofont("TkDefaultFont")
default_font.configure(size=FontSize)
#
loopnum = 0
# define ADALM1000 interface
# define button actions
# Draw analog meter face
def Build_meter():
    global MXcenter, MYcenter, MRadius, MGRW, MGRH, MAScreenStatus
    global COLORtrace1, COLORtrace2, COLORtext, TRACEwidth, GridWidth, FontSize
    global COLORcanvas, COLORgrid, COLORdial, SWRev, RevDate, MAca, mawindow
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel
    global IndicatorA, IndicatorB, ValueDisA, ValueDisB, DialSpan
    global MeterMinEntry, MeterMaxEntry

    if MAScreenStatus.get() == 0:
        # Entry inputs for Meter Min and Max
        frame1 = Frame( root )
        frame1.grid(row=12, column=0, sticky=W)
        MeterMinEntry = Entry(frame1, width=5, cursor='double_arrow')
        #MeterMinEntry.bind("<Return>", BOffsetA)
        MeterMinEntry.bind('<MouseWheel>', onMeterMinMax)# with Windows OS
        MeterMinEntry.bind("<Button-4>", onMeterMinMax)# with Linux OS
        MeterMinEntry.bind("<Button-5>", onMeterMinMax)
        MeterMinEntry.bind('<Key>', onKeyMinMax)
        MeterMinEntry.pack(side=LEFT)
        MeterMinEntry.delete(0,"end")
        MeterMinEntry.insert(0,Mmin)
        MeterMinlab = Button(frame1, text="Meter Min", style="W9.TButton", command=donothing)# SetVAPoss)
        MeterMinlab.pack(side=LEFT)
        #
        frame2 = Frame( root )
        frame2.grid(row=12, column=0, sticky=W)
        MeterMaxEntry = Entry(frame1, width=5, cursor='double_arrow')
        #MeterMaxEntry.bind("<Return>", BOffsetA)
        MeterMaxEntry.bind('<MouseWheel>', onMeterMinMax)# with Windows OS
        MeterMaxEntry.bind("<Button-4>", onMeterMinMax)# with Linux OS
        MeterMaxEntry.bind("<Button-5>", onMeterMinMax)
        MeterMaxEntry.bind('<Key>', onKeyMinMax)
        MeterMaxEntry.pack(side=LEFT)
        MeterMaxEntry.delete(0,"end")
        MeterMaxEntry.insert(0,Mmax)
        MeterMaxlab = Button(frame1, text="Meter Max", style="W9.TButton", command=donothing)# SetVAPoss)
        MeterMaxlab.pack(side=LEFT)
        #
        root.update()
        #
        MAScreenStatus.set(1)
        mawindow = Toplevel()
        mawindow.title("Analog Meter " + SWRev + RevDate)
        mawindow.protocol("WM_DELETE_WINDOW", DestroyMAScreen)
    
        MAca = Canvas(mawindow, width=MGRW, height=MGRH, background=COLORcanvas)
        MAca.bind("<Configure>", MACaresize)
        MAca.pack(side=TOP, expand=YES, fill=BOTH)
# MAca.bind("<Return>", DoNothing)
        MAca.bind("<space>", onCanvasSpaceBar)
        if DialSpan > 359:
            DialSpan = 355
        DialStart = 360 - ((DialSpan-180)/2)
        DialCenter = 0.15 * MRadius
        MAca.create_arc(MXcenter-MRadius, MYcenter+MRadius, MXcenter+MRadius, MYcenter-MRadius, start=DialStart, extent=DialSpan, outline=COLORgrid, fill=COLORdial, width=GridWidth.get())
        MAca.create_arc(MXcenter-DialCenter, MYcenter+DialCenter, MXcenter+DialCenter, MYcenter-DialCenter, start=DialStart, extent=DialSpan, outline="blue", fill="blue", width=GridWidth.get())
        if Mmin >= Mmax:
            Mmax = Mmin + 0.1
            MeterMaxEntry.delete(0,END)
            MeterMaxEntry.insert(0, Mmax)
        MScale = Mmax - Mmin
        DialStart = 90 + (DialSpan/2)
        for tick in range(MajorDiv+1):
            TIradius = 1.1 * MRadius
            TOradius = 1.2 * MRadius
            Angle = DialStart - ((DialSpan*tick)/MajorDiv)
            NextAngle = DialStart - ((DialSpan*(tick+1))/MajorDiv)
            MinorTickStep = (Angle - NextAngle)/5.0
            RAngle = math.radians(Angle)
            y = MRadius*math.sin(RAngle)
            x = MRadius*math.cos(RAngle)
            yi = TIradius*math.sin(RAngle)
            xi = TIradius*math.cos(RAngle) 
            yt = TOradius*math.sin(RAngle)
            xt = TOradius*math.cos(RAngle)
            if Angle > 270:
                y = 0 - y
                yi = 0 - yi
                yt = 0 - yt
            #Draw Major Tick
            MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
            # Add Text Label
            Increment = MajorDiv/MScale
            axis_value = float((tick/Increment)+Mmin)
            axis_label = "{0: .2f}".format(axis_value)
            MAca.create_text(MXcenter+xt, MYcenter-yt, text = axis_label, fill=COLORtext, font=("arial", FontSize ))
            # Add minor Ticks
            TIradius = 1.05 * MRadius
            if tick < MajorDiv:
                for minor in range(MinorDiv-1):
                    MinorAngle = Angle-((minor+1)*MinorTickStep)
                    RAngle = math.radians(MinorAngle)
                    y = MRadius*math.sin(RAngle)
                    x = MRadius*math.cos(RAngle)
                    yi = TIradius*math.sin(RAngle)
                    xi = TIradius*math.cos(RAngle)
                    if MinorAngle > 270:
                        y = 0 - y
                        yi = 0 - yi
                    #Draw Minor Tick
                    MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())

        MeterLabel = MAca.create_text(MXcenter-MRadius/2,MYcenter+MRadius/2, text = MeterLabelText, fill=COLORtext, font=("arial", FontSize+4 ))
        
        IndicatorA = MAca.create_line(MXcenter, MYcenter, MXcenter+x, MYcenter-y, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
        IndicatorB = IndicatorA
        VString = ' CH-A {0:.4f} '.format(0.0) # format with 4 decimal places
        ValueDisA = MAca.create_text(MXcenter-MRadius,MYcenter+MRadius, text = VString, fill=COLORtrace1, font=("arial", FontSize+4 ))
        VString = ' CH-B {0:.4f} '.format(0.0) # format with 4 decimal places
        ValueDisB = MAca.create_text(MXcenter-MRadius,MYcenter+MRadius+FontSize+5, text = VString, fill=COLORtrace2, font=("arial", FontSize+4 ))
#
def DestroyMAScreen():
    global mawindow, MAScreenStatus #, MAca, MADisp

    MAScreenStatus.set(0)
    mawindow.destroy()
#
def Update_Analog_Meter(ValueA, ValueB):
    global MXcenter, MYcenter, MRadius, MAca, MGRW, MGRH
    global COLORtrace1, COLORtrace2, TRACEwidth, GridWidth, FontSize
    global Mmin, Mmax, MajorDiv, DialSpan, MeterMaxEntry
    global IndicatorA, IndicatorB, ValueDisA, ValueDisB
    
    if Mmin >= Mmax:
        Mmax = Mmin + 0.1
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    MScale = Mmax - Mmin
    DialStart = 90 + (DialSpan/2)
    Tradius = 1.0 * MRadius
    Angle = DialStart - ((DialSpan*(ValueA-Mmin))/MScale) # calculate angle of CHA indicator
    if Angle < 0.0:
        Angle = 360 - Angle
    RAngle = math.radians(Angle)
    ya = Tradius*math.sin(RAngle) # convert angle to x y position
    xa = Tradius*math.cos(RAngle)
    if Angle > 270:
        ya = 0 - ya
    Angle = DialStart - ((DialSpan*(ValueB-Mmin))/MScale) # calculate angle of CHB indicator
    if Angle < 0.0:
        Angle = 360 - Angle
    RAngle = math.radians(Angle)
    yb = Tradius*math.sin(RAngle) # convert angle to x y position
    xb = Tradius*math.cos(RAngle)
    if Angle > 270:
        yb = 0 - yb
    MAca.delete(IndicatorA) # remove old lines
    MAca.delete(IndicatorB)
    MAca.delete(ValueDisA)
    MAca.delete(ValueDisB)
    # make new lines
    IndicatorA = MAca.create_line(MXcenter, MYcenter, MXcenter+xa, MYcenter-ya, fill=COLORtrace1, arrow="last", width=TRACEwidth.get())
    IndicatorB = MAca.create_line(MXcenter, MYcenter, MXcenter+xb, MYcenter-yb, fill=COLORtrace2, arrow="last", width=TRACEwidth.get())
    VString = ' CH-A {0:.4f} '.format(ValueA) # format with 4 decimal places
    ValueDisA = MAca.create_text(FontSize+MXcenter-MRadius,MYcenter+MRadius, text = VString, fill=COLORtrace1, font=("arial", FontSize+4 ))
    VString = ' CH-B {0:.4f} '.format(ValueB) # format with 4 decimal places
    ValueDisB = MAca.create_text(FontSize+MXcenter-MRadius,MYcenter+MRadius+(FontSize*2), text = VString, fill=COLORtrace2, font=("arial", FontSize+4 ))
#
# Resize Analog Meter window
def MACaresize(event):
    global MAca, MGRW, MGRH, CANVASwidthMA, CANVASheightMA, FontSize
    global MXcenter, MYcenter, MRadius, COLORdial, MeterMinEntry, MeterMaxEntry
    global IndicatorA, IndicatorB, COLORtrace1, COLORtrace2, COLORtext, TRACEwidth, GridWidth
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel 
     
    CANVASwidthMA = event.width - 4
    CANVASheightMA = event.height - 4
    MGRW = CANVASwidthMA # 170 new grid width
    MGRH = CANVASheightMA  # 10 new grid height
    MXcenter = int(MGRW/2.0)   # Meter Center
    MYcenter = int(MGRH/2.0)
    MRadius = MXcenter - 50    # Meter Radius
    MakeMeterDial()
#
def MakeMeterDial():
    global MAca, MGRW, MGRH, CANVASwidthMA, CANVASheightMA, FontSize
    global MXcenter, MYcenter, MRadius, COLORdial, MeterMinEntry, MeterMaxEntry
    global IndicatorA, IndicatorB, COLORtrace1, COLORtrace2, COLORtext, TRACEwidth, GridWidth
    global Mmin, Mmax, MajorDiv, MinorDiv, MeterLabelText, MeterLabel, DialSpan
    
    # Re make meter dial
    MAca.delete(ALL) # remove all items
    if DialSpan > 359:
        DialSpan = 355
    DialStart = 360 - ((DialSpan-180)/2)
    DialCenter = 0.15 * MRadius
    MAca.create_arc(MXcenter-MRadius, MYcenter+MRadius, MXcenter+MRadius, MYcenter-MRadius, start=DialStart, extent=DialSpan, outline=COLORgrid, fill=COLORdial, width=GridWidth.get())
    MAca.create_arc(MXcenter-DialCenter, MYcenter+DialCenter, MXcenter+DialCenter, MYcenter-DialCenter, start=DialStart, extent=DialSpan, outline="blue", fill="blue", width=GridWidth.get())
#
    try:
        Mmin = float(eval(MeterMinEntry.get()))
    except:
        MeterMinEntry.delete(0,END)
        MeterMinEntry.insert(0, Mmin)
    try:
        Mmax = float(eval(MeterMaxEntry.get()))
    except:
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    if Mmin >= Mmax:
        Mmax = Mmin + 0.1
        MeterMaxEntry.delete(0,END)
        MeterMaxEntry.insert(0, Mmax)
    MScale = Mmax - Mmin
    DialStart = 90.0 + (DialSpan/2.0)
    for tick in range(MajorDiv+1):
        TIradius = 1.1 * MRadius
        TOradius = 1.2 * MRadius
        Angle = DialStart - ((DialSpan*tick)/MajorDiv)
        NextAngle = DialStart - ((DialSpan*(tick+1))/MajorDiv)
        MinorTickStep = (Angle - NextAngle)/5.0
        RAngle = math.radians(Angle)
        y = MRadius*math.sin(RAngle)
        x = MRadius*math.cos(RAngle)
        yi = TIradius*math.sin(RAngle)
        xi = TIradius*math.cos(RAngle) 
        yt = TOradius*math.sin(RAngle)
        xt = TOradius*math.cos(RAngle)
        if Angle > 270:
            y = 0 - y
            yi = 0 - yi
            yt = 0 - yt
        #Draw Major Tick
        MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
        # Add Text Label
        Increment = MajorDiv/MScale
        axis_value = float((tick/Increment)+Mmin)
        axis_label = "{0: .2f}".format(axis_value)
        MAca.create_text(MXcenter+xt, MYcenter-yt, text = axis_label, fill=COLORtext, font=("arial", FontSize ))
        # Add minor Ticks
        TIradius = 1.05 * MRadius
        if tick < MajorDiv:
            for minor in range(MinorDiv-1):
                MinorAngle = Angle-((minor+1)*MinorTickStep)
                RAngle = math.radians(MinorAngle)
                y = MRadius*math.sin(RAngle)
                x = MRadius*math.cos(RAngle)
                yi = TIradius*math.sin(RAngle)
                xi = TIradius*math.cos(RAngle)
                if MinorAngle > 270:
                    y = 0 - y
                    yi = 0 - yi
                #Draw Minor Tick
                MAca.create_line(MXcenter+x, MYcenter-y, MXcenter+xi, MYcenter-yi, fill=COLORgrid, width=GridWidth.get())
        MeterLabel = MAca.create_text(MXcenter, MYcenter+MRadius/2, text = MeterLabelText, fill=COLORtext, font=("arial", FontSize+4 ))
#
def Analog_in():
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global InOffA, InGainA, InOffB, InGainB, MADisp
    global session, DevID, devx, loopnum, session
    
    # Main loop
    while (True):
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
            if not session.continuous:
                session.flush()
                session.start(0)
                time.sleep(0.02)
            DCVA = DCVB = 0.0 # initalize measurment variable
            # Get A0 and B0 data
            ADsignal1 = devx.read(100, -1, True)
            # get_samples returns a list of values for voltage [0] and current [1]
            for index in range(90): # calculate average
                DCVA += ADsignal1[index+10][0][0] # Sum for average CA voltage 
                DCVB += ADsignal1[index+10][1][0] # Sum for average CB voltage

            DCVA = DCVA / 90.0 # calculate average
            DCVB = DCVB / 90.0 # calculate average
            DCVA = (DCVA - InOffA) * InGainA # adjust for external gain / offset
            DCVB = (DCVB - InOffB) * InGainB
            if DCVA > CHAMaxV:
                CHAMaxV = DCVA
            if DCVA < CHAMinV:
                CHAMinV = DCVA
            if DCVB > CHBMaxV:
                CHBMaxV = DCVB
            if DCVB < CHBMinV:
                CHBMinV = DCVB
            VAString = "CA Volts " + ' {0:.4f} '.format(DCVA) # format with 4 decimal places
            VBString = "CB Volts " + ' {0:.4f} '.format(DCVB) # format with 4 decimal places
            VABString = "CA-CB V " + ' {0:.4f} '.format(DCVA-DCVB) # format with 4 decimal places
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
            if MADisp.get() == 1:
                Update_Analog_Meter(DCVA, DCVB)
            #
#
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
# Use Arrow keys to inc dec entry values
def onTextKey(event):
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
    if platform.system() == "Windows":
        if event.keycode == 38: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 40: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Linux":
        if event.keycode == 111: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 116: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    elif platform.system() == "Darwin":
        if event.keycode == 0x7D: # increment digit for up arrow key
            NewVal = OldValfl + Step
        elif event.keycode == 0x7E: # decrement digit for down arrow
            NewVal = OldValfl - Step
        else:
            return
    else:
        return
#
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
def onMeterMinMax(event):
    onTextScroll(event)
    MakeMeterDial()
#
def onKeyMinMax(event):
    onTextKey(event)
    MakeMeterDial()
#
# Pause / start on space bar
def onCanvasSpaceBar(event):
    global RUNstatus, MAca

    if event.widget == MAca:
        if RUNstatus.get() == 0:
            RUNstatus.set(1)
        elif RUNstatus.get() > 0:
            RUNstatus.set(0)
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
## Nop
def donothing():
    global RUNstatus
## Another Nop
def DoNothing(event):
    global RUNstatus
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
            exec( line.rstrip(), globals(), globals())
            #exec( line.rstrip() )
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
#
def MACheckBox():
    global MADisp, ckb2
    if MADisp.get() == 1:
        ckb2.config(style="Enab.TCheckbutton")
    else:
        ckb2.config(style="Disab.TCheckbutton")
#
MADisp = IntVar(0)
# setup main window
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
root.minsize(200, 100)
#
if GUITheme == "Light": # Can be Light or Dark or Blue or LtBlue
    FrameBG = "#d7d7d7"
    ButtonText = "#000000"
elif GUITheme == "Dark":
    FrameBG = "#484848"
    ButtonText = "#ffffff"
elif GUITheme == "Blue":
    FrameBG = "#242468"
    ButtonText = "#d0d0ff"
elif GUITheme == "LtBlue":
    FrameBG = "#c0e8ff"
    ButtonText = "#000040"
EntryText = "#000000"
BoxColor = "#0000ff" # 100% blue
#
root.style.configure("TFrame", background=FrameBG, borderwidth=BorderSize)
root.style.configure("TLabelframe", background=FrameBG)
root.style.configure("TLabel", foreground=ButtonText, background=FrameBG, relief=LabRelief)
root.style.configure("TEntry", foreground=EntryText, background=FrameBG, relief=ButRelief) #cursor='sb_v_double_arrow'
root.style.configure("TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TRadiobutton", foreground=ButtonText, background=FrameBG, indicatorcolor=FrameBG)
root.style.configure("TButton", foreground=ButtonText, background=FrameBG, highlightcolor=FrameBG, relief=ButRelief)
# define custom buttons
root.style.configure("TSpinbox", arrowsize=13) # only changes things in Python 3
root.style.configure("W3.TButton", width=3, relief=ButRelief)
root.style.configure("W4.TButton", width=4, relief=ButRelief)
root.style.configure("W5.TButton", width=5, relief=ButRelief)
root.style.configure("W6.TButton", width=6, relief=ButRelief)
root.style.configure("W7.TButton", width=7, relief=ButRelief)
root.style.configure("W8.TButton", width=8, relief=ButRelief)
root.style.configure("W9.TButton", width=9, relief=ButRelief)
root.style.configure("W10.TButton", width=10, relief=ButRelief)
root.style.configure("W11.TButton", width=11, relief=ButRelief)
root.style.configure("W12.TButton", width=12, relief=ButRelief)
root.style.configure("W16.TButton", width=16, relief=ButRelief)
root.style.configure("W17.TButton", width=17, relief=ButRelief)
root.style.configure("Stop.TButton", background=ButtonRed, foreground="#000000", width=4, relief=ButRelief)
root.style.configure("Run.TButton", background=ButtonGreen, foreground="#000000", width=4, relief=ButRelief)
root.style.configure("Pwr.TButton", background=ButtonGreen, foreground="#000000", width=8, relief=ButRelief)
root.style.configure("PwrOff.TButton", background=ButtonRed, foreground="#000000", width=8, relief=ButRelief)
root.style.configure("RConn.TButton", background=ButtonRed, foreground="#000000", width=5, relief=ButRelief)
root.style.configure("GConn.TButton", background=ButtonGreen, foreground="#000000", width=5, relief=ButRelief)
root.style.configure("Rtrace1.TButton", background=COLORtrace1, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace1.TButton", background=COLORtrace1, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace1.TButton", background=COLORtrace1, foreground="#000000", relief=ButRelief)
root.style.configure("Rtrace2.TButton", background=COLORtrace2, foreground="#000000", width=7, relief=RAISED)
root.style.configure("Strace2.TButton", background=COLORtrace2, foreground="#000000", width=7, relief=SUNKEN)
root.style.configure("Ctrace2.TButton", background=COLORtrace2, foreground="#000000", relief=ButRelief)

root.style.configure("A10B.TLabel", foreground=ButtonText, font="Arial 10 bold") # Black text
root.style.configure("A10R.TLabel", foreground=ButtonRed, font="Arial 10 bold") # Red text
root.style.configure("A10G.TLabel", foreground=ButtonGreen, font="Arial 10 bold") # Red text
root.style.configure("A12B.TLabel", foreground=ButtonText, font="Arial 12 bold") # Black text
root.style.configure("A16B.TLabel", foreground=ButtonText, font="Arial 16 bold") # Black text
root.style.configure("Stop.TRadiobutton", background=ButtonRed, indicatorcolor=FrameBG)
root.style.configure("Run.TRadiobutton", background=ButtonGreen, indicatorcolor=FrameBG)
root.style.configure("Disab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonRed)
root.style.configure("Enab.TCheckbutton", foreground=ButtonText, background=FrameBG, indicatorcolor=ButtonGreen)
root.style.configure("Strace1.TCheckbutton", background=COLORtrace1, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("Strace2.TCheckbutton", background=COLORtrace2, foreground="#000000", indicatorcolor="#ffffff")
root.style.configure("WPhase.TRadiobutton", width=5, foreground="#000000", background="white", indicatorcolor=("red", "green"))
root.style.configure("GPhase.TRadiobutton", width=5, foreground="#000000", background="gray", indicatorcolor=("red", "green"))
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
rb1 = Radiobutton(buttons, text="Stop", style="Stop.TRadiobutton", variable=RUNstatus, value=0 )
rb1.pack(side=LEFT)
rb2 = Radiobutton(buttons, text="Run", style="Run.TRadiobutton", variable=RUNstatus, value=1 )
rb2.pack(side=LEFT)
resetb1 = Button(buttons, text='Reset Min/Max', command=BReset)
resetb1.pack(side=LEFT)
# Ebable Anaalog Meter Display
mabtn = Frame( root )
mabtn.grid(row=8, column=0, sticky=W)
ckb2 = Checkbutton(mabtn, text="Enab", style="Disab.TCheckbutton", variable=MADisp, command=MACheckBox)
ckb2.pack(side=LEFT)
BuildMAScreen = Button(mabtn, text="Analog Meter", style="W12.TButton", command=Build_meter)
BuildMAScreen.pack(side=TOP)
# input probe wigets
prlab = Label(root, text="Channel Gain / Offset Adjustment")
prlab.grid(row=9, column=0, sticky=W)
# Input Probes sub frame 
ProbeA = Frame( root )
ProbeA.grid(row=10, column=0, sticky=W)
gain1lab = Button(ProbeA, text="CA-V", width=4, style="Ctrace1.TButton", command=ReSetAGO) 
gain1lab.pack(side=LEFT,fill=X)
CHAVGainEntry = Entry(ProbeA, width=5, cursor='double_arrow')
CHAVGainEntry.bind('<Return>', onTextKey)
CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
CHAVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVGainEntry.bind("<Button-5>", onTextScroll)
CHAVGainEntry.bind('<Key>', onTextKey)
CHAVGainEntry.pack(side=LEFT)
CHAVGainEntry.delete(0,"end")
CHAVGainEntry.insert(0,InGainA)
CHAVOffsetEntry = Entry(ProbeA, width=5, cursor='double_arrow')
CHAVOffsetEntry.bind('<Return>', onTextKey)
CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHAVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHAVOffsetEntry.bind("<Button-5>", onTextScroll)
CHAVOffsetEntry.bind('<Key>', onTextKey)
CHAVOffsetEntry.pack(side=LEFT)
CHAVOffsetEntry.delete(0,"end")
CHAVOffsetEntry.insert(0,InOffA)
b1 = Button(ProbeA, text='Save', command=BSaveCal)
b1.pack(side=LEFT)
#
ProbeB = Frame( root )
ProbeB.grid(row=11, column=0, sticky=W)
gain2lab = Button(ProbeB, text="CB-V", width=4, style="Ctrace2.TButton", command=ReSetBGO) 
gain2lab.pack(side=LEFT,fill=X)
CHBVGainEntry = Entry(ProbeB, width=5, cursor='double_arrow')
CHBVGainEntry.bind('<Return>', onTextKey)
CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
CHBVGainEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVGainEntry.bind("<Button-5>", onTextScroll)
CHBVGainEntry.bind('<Key>', onTextKey)
CHBVGainEntry.pack(side=LEFT)
CHBVGainEntry.delete(0,"end")
CHBVGainEntry.insert(0,InGainB)
CHBVOffsetEntry = Entry(ProbeB, width=5, cursor='double_arrow')
CHBVOffsetEntry.bind('<Return>', onTextKey)
CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
CHBVOffsetEntry.bind("<Button-4>", onTextScroll)# with Linux OS
CHBVOffsetEntry.bind("<Button-5>", onTextScroll)
CHBVOffsetEntry.bind('<Key>', onTextKey)
CHBVOffsetEntry.pack(side=LEFT)
CHBVOffsetEntry.delete(0,"end")
CHBVOffsetEntry.insert(0,InOffB)
b2 = Button(ProbeB, text='Load', command=BLoadCal)
b2.pack(side=LEFT)
# Define Analog Meter display for two indicators
#Build_meter()

# connect ADAML1000
if pysmu_found:
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
else:
    root.update()
    showwarning("WARNING","Pysmu not found!")
    root.destroy()
    exit()
