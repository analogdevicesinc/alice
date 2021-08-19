#!/usr/bin/python
# ADALM1000 Strip chart recorder tool (7-17-2021)
# For Python version > = 2.7.8 and 3.7
# With external module pysmu (libsmu > = 1.0 ADALM1000 )
# Created by D Mercer ()
#
import __future__
import os
import sys
if sys.version_info[0] == 2:
    print ("Python 2.x")
    from Tkinter import *
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
if sys.version_info[0] == 3:
    from tkinter import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    print ("Python 3.x")
import math, random, threading, time
from pysmu import *
from time import gmtime, strftime
# set up variables
InOffA = InOffB = 0.0
InGainA = InGainB = 1.0
CANVASwidth = 1000
CANVASheight = 400
COLORcanvas = "#000000"   # 100% black
COLORgrid = "#808080"     # 50% Gray
COLORzeroline = "#0000ff" # 100% blue
COLORtrace2 = "#00ff00"   # 100% green
COLORtrace1 = "#ff8000"   # 100% orange
CHAMaxV = 0.0
CHAMinV = 5.0
CHBMaxV = 0.0
CHBMinV = 5.0
BaseSampleRate = 100000
SampleRate = 50
SampRates = (50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000)
RunStatus = 0
SampleNum = 0
# Check if there is an stripchart_init.ini file to read in
try:
    InitFile = open("stripchart_init.ini")
    for line in InitFile:
        try:
            exec( line.rstrip(), globals(), globals())
            #exec( line.rstrip() )
        except:
            print( "Skiping " + line.rstrip())
    InitFile.close()
except:
    print( "No Init File Read")
#
class StripChart:
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global InOffA, InOffB, InGainA, InGainB, chalab, chblab, SampleNum
    global COLORcanvas, COLORgrid, COLORzeroline, COLORtrace1, COLORtrace2
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV, SampleDelayEntry
    global DCVA0, DCVB0, dlog, Dlog_open, Ztime, Run_For, RunForEntry
    
    def __init__(self, root):
        global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry, SampleDelayEntry
        global Run_For, RunForEntry
        self.gf = self.makeGraph(root)
        self.cf = self.makeControls(root)
        self.gf.pack()
        self.cf.pack()
        self.Reset()

    def makeGraph(self, frame):
        global CANVASwidth, CANVASheight, COLORcanvas
        global gf
        self.sw = CANVASwidth # default 1000
        self.h = CANVASheight # default 200
        self.top = 2
        gf = Canvas(frame, width=self.sw, height=self.h+10,
                    bg=COLORcanvas, bd=0, highlightthickness=0)
        gf.p = PhotoImage(width=2*self.sw, height=self.h)
        self.item = gf.create_image(0, self.top, image=gf.p, anchor=NW)
        return(gf)

    def makeControls(self, frame):
        global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry, SRateScale
        global NumGrid, SelCHA, SelCHB, dlog, Dlog_open, chalab, chblab, SampleDelayEntry
        global Run_For, RunForEntry
        global SampRates, InOffA, InOffB, InGainA, InGainB
        
        cf = Frame(frame, borderwidth=1, relief="raised")
        br = Button(cf, text="Run", bg="#00ff00", command=self.Run)
        br.grid(column=2, row=2)
        bs = Button(cf, text="Stop", bg="#ff0000",command=self.Stop)
        bs.grid(column=3, row=2)
        bt = Button(cf, text="Reset", bg='yellow', command=self.Reset)
        bt.grid(column=4, row=2)
        bexit = Button(cf, text="Exit", command=close_out)
        bexit.grid(column=5,row=2)
        bss = Button(cf, text="Save Screen", bg='cyan', command=BSaveScreen)
        bss.grid(column=6, row=2, columnspan=1)
        brf = Label(cf, text="Run For")
        brf.grid(column=7, row=2)
        Run_For = IntVar()
        Run_For.set(0)
        runfor = Checkbutton(cf, text="Samples", variable=Run_For)
        runfor.grid(column=8, row=2, columnspan=1)
        RunForEntry = Entry(cf, width=4)
        RunForEntry.bind('<MouseWheel>', onTextScroll)
        RunForEntry.grid(column=9,row=2)
        RunForEntry.delete(0,"end")
        RunForEntry.insert(0,100)
        
        sampdeylab = Label(cf, text="Delay")
        sampdeylab.grid(column=10,row=2)
        SampleDelayEntry = Entry(cf, width=4)
        SampleDelayEntry.bind('<MouseWheel>', onTextScroll)
        SampleDelayEntry.grid(column=11,row=2)
        SampleDelayEntry.delete(0,"end")
        SampleDelayEntry.insert(0,0.0)
        # Channel data displays
        chalab = Label(cf, text="CHA 0.000 V CHA Max 0.000 V CHA Min 0.000 V", font = "Arial 12 bold")
        chalab.grid(row=2, column=0, sticky=W)
        chblab = Label(cf, text="CHB 0.000 V CHB Max 0.000 V CHB Min 0.000 V", font = "Arial 12 bold")
        chblab.grid(row=3, column=0, sticky=W) 
        # input probe wigets
        prlab = Label(cf, text="Channel Gain / Offset calibration")
        prlab.grid(row=2, column=1, sticky=W)
        # Input Probes sub frame 
        ProbeA = Frame( cf )
        ProbeA.grid(row=3, column=1, columnspan=8, sticky=W)
        gain1lab = Label(ProbeA, text="CA")
        gain1lab.pack(side=LEFT)
        CHAVGainEntry = Entry(ProbeA, width=6) #
        CHAVGainEntry.bind('<MouseWheel>', onTextScroll)
        CHAVGainEntry.pack(side=LEFT)
        CHAVGainEntry.delete(0,"end")
        CHAVGainEntry.insert(0,InGainA)
        CHAVOffsetEntry = Entry(ProbeA, width=6) #
        CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
        CHAVOffsetEntry.pack(side=LEFT)
        CHAVOffsetEntry.delete(0,"end")
        CHAVOffsetEntry.insert(0,InOffA)
        #
        gain2lab = Label(ProbeA, text="CB")
        gain2lab.pack(side=LEFT)
        CHBVGainEntry = Entry(ProbeA, width=6) #
        CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
        CHBVGainEntry.pack(side=LEFT)
        CHBVGainEntry.delete(0,"end")
        CHBVGainEntry.insert(0,InGainB)
        CHBVOffsetEntry = Entry(ProbeA, width=6) #
        CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
        CHBVOffsetEntry.pack(side=LEFT)
        CHBVOffsetEntry.delete(0,"end")
        CHBVOffsetEntry.insert(0,InOffB)
        b1 = Button(ProbeA, text='Save', command=BSaveCal)
        b1.pack(side=LEFT)
        b2 = Button(ProbeA, text='Load', command=BLoadCal)
        b2.pack(side=LEFT)
        #
        SelCHA = IntVar(0)
        selcha = Checkbutton(cf, text="CH A", variable=SelCHA, command = self.ChangeGrid)
        selcha.grid(row=3, column=5, sticky=W)
        SelCHB = IntVar(0)
        selchb = Checkbutton(cf, text="CH B", variable=SelCHB, command = self.ChangeGrid)
        selchb.grid(row=3, column=6, sticky=W)
        NumGrid = IntVar(0)
        rb1 = Radiobutton(cf, text="1 Grid", variable=NumGrid, value=0, command = self.ChangeGrid )
        rb1.grid(row=3, column=7, sticky=W)
        rb2 = Radiobutton(cf, text="2 Grid", variable=NumGrid, value=1, command = self.ChangeGrid )
        rb2.grid(row=3, column=8, sticky=W)
        #
        SRateScale = Spinbox(cf, width=5, values=SampRates)
        SRateScale.bind('<MouseWheel>', onSpinBoxScroll)
        SRateScale.grid(row=3, column=9, sticky=W)
        #
        self.fps = Label(cf, text="0 Sps")
        self.fps.grid(row=3, column=10, columnspan=1)
        dlog = IntVar()
        dlog.set(0)
        Dlog_open = IntVar()
        Dlog_open.set(0)
        dlog1 = Checkbutton(cf, text="Data Log", variable=dlog)
        dlog1.grid(column=11, row=3, columnspan=1)
        #
        SelCHA.set(1)
        SelCHB.set(1)
        return(cf)

    def Run(self):
        global Ztime, Dlog_open, dlog, session
        global Run_For, RunForEntry, SampleNum
        
        self.go = 1
        for t in threading.enumerate():
            if t.name == "_gen_":
                print("already running")
                return
        threading.Thread(target=self.do_start, name="_gen_").start()
        if Dlog_open.get() == 1 and dlog.get() > 0:
            Ztime = time.time()
            SampleNum = 0.0
        elif Dlog_open.get() == 0 and dlog.get() > 0:
            open_out()
            Ztime = time.time()
        else:
            Dlog_open.set(0)

    def Stop(self):
        global Run_For, RunForEntry, session
        
        self.go = 0
        #for t in threading.enumerate():
            #print( t.name )
            #if t.name == "_gen_":
                #t.join()
##        if session.continuous:
##            print( "ending session")
##            session.end() # end continuous session mode
    def Reset(self):
        global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
        global InOffA, InGainA, InOffB, InGainB
        global COLORcanvas
        
        self.Stop()
        self.clearstrip(self.gf.p, COLORcanvas)
        CHAMaxV = (0.0 - InOffA) * InGainA
        CHAMinV = (5.0 - InOffA) * InGainA
        CHBMaxV = (0.0 - InOffB) * InGainB
        CHBMinV = (5.0 - InOffB) * InGainB

    def ChangeGrid(self):
        if self.go == 1:
            self.Reset()
            time.sleep(0.05)
            self.Run()

    def do_start(self):
        global DCVA0, DCVB0
        global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
        global COLORcanvas, COLORgrid, COLORzeroline, COLORtrace1, COLORtrace2
        global NumGrid, SelCHA, SelCHB, SampleRate
        global Run_For, RunForEntry
        
        t = 0
        y2 = 0
        tx = time.time()
        # add sample counter start here
        loop_end = int(eval(RunForEntry.get()))
        loop_count = 0
        if Run_For.get() == 0 and (loop_end <= loop_count):
            loop_end = loop_count + 1
        while self.go and (loop_count < loop_end): # loop forever or till sample count reached
            Analog_Strip_Chart()
            #
            if DCVB0 > 5.0:
                DCVB0 = 5.0
            if DCVA0 > 5.0:
                DCVA0 = 5.0
            if DCVB0 < 0.0:
                DCVB0 = 0.0
            if DCVA0 < 0.0:
                DCVA0 = 0.0
            if NumGrid.get() == 0: # both on one grid
                y1 = (DCVB0/6.25)-0.4 # scale / 0ffset 0 to 5 V to +/- 0.4
                y2 = (DCVA0/6.25)-0.4 # scale / 0ffset 0 to 5 V to +/- 0.4
                if SelCHA.get() and SelCHB.get():
                    self.scrollstrip(self.gf.p,
                       (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.5+y1,0.5+y2),
                       (COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORzeroline, COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORtrace1, COLORtrace2),
                         "" if t % SampleRate else "#088")
                elif SelCHA.get():
                    self.scrollstrip(self.gf.p,
                       (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.5+y2),
                       (COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORzeroline, COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORtrace2),
                         "" if t % SampleRate else "#088")
                elif SelCHB.get():
                    self.scrollstrip(self.gf.p,
                       (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.5+y1),
                       (COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORzeroline, COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORtrace1),
                         "" if t % SampleRate else "#088")
            else: # two grids
                y1 = (DCVB0/12.5)-0.2 # scale / 0ffset 0 to 5 V to +/- 0.2
                y2 = (DCVA0/12.5)-0.2 # scale / 0ffset 0 to 5 V to +/- 0.2
                if SelCHA.get() and SelCHB.get():
                    self.scrollstrip(self.gf.p,
                       (0.05,0.15,0.25,0.35,0.45,0.25+y1,0.55,0.65,0.75,0.85,0.95,0.75+y2),
                       (COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORtrace1,COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORtrace2),
                         "" if t % SampleRate else "#088")
                elif SelCHA.get():
                    self.scrollstrip(self.gf.p,
                       (0.05,0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.75+y2),
                       (COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORtrace2),
                         "" if t % SampleRate else "#088")
                elif SelCHB.get():
                    self.scrollstrip(self.gf.p,
                       (0.05,0.15,0.25,0.35,0.45,0.25+y1,0.55,0.65,0.75,0.85,0.95),
                       (COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORtrace1,COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid),
                         "" if t % SampleRate else "#088")
            t += 1
            try:
                RateScale = int(SRateScale.get())
            except:
                RateScale = 100
            if not t % RateScale:
                tx2 = time.time()
                SampleRate = int(RateScale/(tx2 - tx))
                self.fps.config(text='%d Sps' % SampleRate)
                tx = tx2
                SampleRate = RateScale
            if Run_For.get() == 1:
                loop_count = loop_count + 1
            else:
                loop_count = 0
            #time.sleep(0.075)

    def clearstrip(self, p, color):  # Fill strip with background color
        self.bg = color              # save background color for scroll
        self.data = None             # clear previous data
        self.x = 0
        p.tk.call(p, 'put', color, '-to', 0, 0, p['width'], p['height'])

    def scrollstrip(self, p, data, colors, bar=""):   # Scroll the strip, add new data
        self.x = (self.x + 1) % self.sw               # x = double buffer position
        bg = bar if bar else self.bg
        p.tk.call(p, 'put', bg, '-to', self.x, 0,
                  self.x+1, self.h)
        p.tk.call(p, 'put', bg, '-to', self.x+self.sw, 0,
                  self.x+self.sw+1, self.h)
        self.gf.coords(self.item, -1-self.x, self.top)  # scroll to just-written column
        if not self.data:
            self.data = data
        for d in range(len(data)):
            try:
                y0 = int((self.h-1) * (1.0-self.data[d]))   # plot all the data points
                y1 = int((self.h-1) * (1.0-data[d]))
                ya, yb = sorted((y0, y1))
                for y in range(ya, yb+1):                   # connect the dots
                    p.put(colors[d], (self.x,y))
                    p.put(colors[d], (self.x+self.sw,y))
            except:
                self.Stop()
                self.Reset()
        self.data = data            # save for next call
#
def onSpinBoxScroll(event):
    spbox = event.widget
    if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    else: # decrement digit
        spbox.invoke('buttondown')
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
def close_out():
    global DlogFile, Dlog_open, dlog, root, session, CHA, CHB
# close opened files by this process
    if session.continuous:
        CHA.mode = Mode.HI_Z
        CHB.mode = Mode.HI_Z
        CHA.constant(0.0)
        CHA.constant(0.0)
        time.sleep(0.01)
        # print "ending session"
        # session.end() # end continuous session mode
    try:
        DlogFile.close()
    except:
        Dlog_open.set(0)
    root.destroy()
    exit()
    
def open_out():
    global DlogFile, Dlog_open, dlog

    # open file for data logging
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
    filename = "StripChart-" + tme
    filename = filename + ".csv"
    try:
        DlogFile = open(filename, 'a')
    except:
        filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
        DlogFile = open(filename, 'a')
    DlogFile.write( 'Time, CA-V, CB-V \n' )
    Dlog_open.set(1)
    
def Analog_Strip_Chart():
    global DevID, CHA, CHB, devx, session, dlog, DlogFile, SampleNum
    global DCVA0, DCVB0, Ztime, SampleDelayEntry, ADsignal1
    global InOffA, InOffB, InGainA, InGainB, chalab, chblab
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV, SRateScale, BaseSampleRate
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    #
    if not session.continuous:
        session.flush()
        session.start(0)
        #print "starting session"
        time.sleep(0.05)
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
    NumSamples = int(BaseSampleRate/float(SRateScale.get()))
    if session.continuous:
        ADsignal1 = devx.read(NumSamples, -1, False) #True)
    #print len(ADsignal1)
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(NumSamples-10): # calculate average
        DCVA0 += ADsignal1[index][0][0] # Sum for average CA voltage 
        DCVB0 += ADsignal1[index][1][0] # Sum for average CB voltage
    DCVA0 = DCVA0/(NumSamples-10.0) # calculate average
    DCVB0 = DCVB0/(NumSamples-10.0) # calculate average
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
    try:
        chalab.config(text = "CHA " + '{0:.3f} '.format(DCVA0) + "V CHA Max " + '{0:.3f} '.format(CHAMaxV) + "V CHA Min " + '{0:.3f} '.format(CHAMinV) + "V")
        chblab.config(text = "CHB " + '{0:.3f} '.format(DCVB0) + "V CHB Max " + '{0:.3f} '.format(CHBMaxV) + "V CHB Min " + '{0:.3f} '.format(CHBMinV) + "V")
    except:
        time.sleep(float(SampleDelayEntry.get()))
    if dlog.get() > 0:
        #tstr1 = time.time()-Ztime
        SampleNum = SampleNum + (1.0/float(SRateScale.get()))
        DlogString = '{0:.4f}, '.format(SampleNum) + '{0:.4f}, '.format(DCVA0) + '{0:.4f} '.format(DCVB0) + " \n"
        DlogFile.write( DlogString )
    # wait for sample delsy time
    time.sleep(float(SampleDelayEntry.get()))
#
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
    global InOffA, InOffB, InGainA, InGainB

    devidstr = DevID[17:31]
    filename = devidstr + "_V.cal"
    CalFile = open(filename)
    for line in CalFile:
        try:
            exec( line.rstrip(), globals(), globals())
            #exec( line.rstrip() )
        except:
            print( "Skipping " + line.rstrip())
    CalFile.close()
    InOffA = float(eval(CHAVOffsetEntry.get()))
    InGainA = float(eval(CHAVGainEntry.get()))
    InOffB = float(eval(CHBVOffsetEntry.get()))
    InGainB = float(eval(CHBVGainEntry.get()))
#
def BSaveScreen():
    global CANVASwidth, CANVASheight
    global gf
    # ask for file name
    filename = asksaveasfilename(defaultextension = ".eps", filetypes=[("Encapsulated Postscript", "*.eps")])
    # next save postscript file
    gf.postscript(file=filename, height=CANVASheight, width=CANVASwidth, colormode='color')

    #
def main():
    global DevID, CHA, CHB, session, root, devx, ADsignal1
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    # setup main window
    TBicon = """
    R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
    hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
    i8fUAgA7
    """
    #
    root = Tk()
    root.title("ALICE 1.3 (17 July 2021): ALM1000 StripChart")
    img = PhotoImage(data=TBicon)
    root.call('wm', 'iconphoto', root._w, img)
    #
    # Setup ADAML1000
    session = Session(ignore_dataflow=True, queue_size=20000)
    # session = Session()
    session.add_all()
    if not session.devices:
        print( 'no device found')
        root.destroy()
        exit()
    session.configure()
    devx = session.devices[0]
    DevID = devx.serial
    print( DevID)
    print( devx.fwver)
    print( devx.hwver)
    print( devx.default_rate)
    CHA = devx.channels['A']    # Open CHA
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB = devx.channels['B']    # Open CHB
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    ADsignal1 = []              # Ain signal array channel
    CHAMaxV = -100.0
    CHAMinV = 100.0
    CHBMaxV = -100.0
    CHBMinV = 100.0
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    # start main loop
    app = StripChart(root)
    root.mainloop()

main()
