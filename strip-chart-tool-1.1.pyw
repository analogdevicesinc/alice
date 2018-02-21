#!/usr/bin/python
# ADALM1000 Strip chart recorder tool (11-28-2017)
# For Python version > = 2.7.8
# With external module pysmu (libsmu > = 0.88 ADALM1000 )
# Created by D Mercer ()
#
from Tkinter import *
import math, random, threading, time
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from pysmu import *
from time import gmtime, strftime
# set up variables
InOffA = InOffB = 0.0
InGainA = InGainB = 1.0
CANVASwidth = 1000
CANVASheight = 200
CHAMaxV = 0.0
CHAMinV = 5.0
CHBMaxV = 0.0
CHBMinV = 5.0
SampleRate = 45

#
class StripChart:
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global InOffA, InOffB, InGainA, InGainB, chalab, chblab
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV, SampleDelayEntry
    global DCVA0, DCVB0, dlog, Dlog_open, Ztime
    
    def __init__(self, root):
        global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry, SampleDelayEntry
        self.gf = self.makeGraph(root)
        self.cf = self.makeControls(root)
        self.gf.pack()
        self.cf.pack()
        self.Reset()

    def makeGraph(self, frame):
        global CANVASwidth, CANVASheight
        global gf
        self.sw = CANVASwidth # default 1000
        self.h = CANVASheight # default 200
        self.top = 2
        gf = Canvas(frame, width=self.sw, height=self.h+10,
                    bg="#000", bd=0, highlightthickness=0)
        gf.p = PhotoImage(width=2*self.sw, height=self.h)
        self.item = gf.create_image(0, self.top, image=gf.p, anchor=NW)
        return(gf)

    def makeControls(self, frame):
        global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
        global NumGrid, SelCHA, SelCHB, dlog, Dlog_open, chalab, chblab, SampleDelayEntry
        
        cf = Frame(frame, borderwidth=1, relief="raised")
        br = Button(cf, text="Run", command=self.Run)
        br.grid(column=2, row=2)
        bs = Button(cf, text="Stop", command=self.Stop)
        bs.grid(column=4, row=2)
        bt = Button(cf, text="Reset", command=self.Reset)
        bt.grid(column=6, row=2)
        bss = Button(cf, text="Save Screen", command=BSaveScreen)
        bss.grid(column=8, row=2, columnspan=2)
        dlog = IntVar()
        dlog.set(0)
        Dlog_open = IntVar()
        Dlog_open.set(0)
        dlog1 = Checkbutton(cf, text="Start Data Log", variable=dlog)
        dlog1.grid(column=10, row=2, columnspan=2)
        sampdeylab = Label(cf, text="Sample delay")
        sampdeylab.grid(column=12,row=2)
        SampleDelayEntry = Entry(cf, width=4)
        SampleDelayEntry.grid(column=13,row=2)
        SampleDelayEntry.delete(0,"end")
        SampleDelayEntry.insert(0,0.0)
        bexit = Button(cf, text="Exit", command=close_out)
        bexit.grid(column=14,row=2)
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
        CHAVGainEntry.insert(0,1.0)
        CHAVOffsetEntry = Entry(ProbeA, width=6) #
        CHAVOffsetEntry.bind('<MouseWheel>', onTextScroll)
        CHAVOffsetEntry.pack(side=LEFT)
        CHAVOffsetEntry.delete(0,"end")
        CHAVOffsetEntry.insert(0,0.0)
        #
        gain2lab = Label(ProbeA, text="CB")
        gain2lab.pack(side=LEFT)
        CHBVGainEntry = Entry(ProbeA, width=6) #
        CHBVGainEntry.bind('<MouseWheel>', onTextScroll)
        CHBVGainEntry.pack(side=LEFT)
        CHBVGainEntry.delete(0,"end")
        CHBVGainEntry.insert(0,1.0)
        CHBVOffsetEntry = Entry(ProbeA, width=6) #
        CHBVOffsetEntry.bind('<MouseWheel>', onTextScroll)
        CHBVOffsetEntry.pack(side=LEFT)
        CHBVOffsetEntry.delete(0,"end")
        CHBVOffsetEntry.insert(0,0.0)
        b1 = Button(ProbeA, text='Save', command=BSaveCal)
        b1.pack(side=LEFT)
        b2 = Button(ProbeA, text='Load', command=BLoadCal)
        b2.pack(side=LEFT)
        #
        SelCHA = IntVar(0)
        selcha = Checkbutton(cf, text="CH A", variable=SelCHA)
        selcha.grid(row=3, column=9, sticky=W)
        SelCHB = IntVar(0)
        selchb = Checkbutton(cf, text="CH B", variable=SelCHB)
        selchb.grid(row=3, column=10, sticky=W)
        NumGrid = IntVar(0)
        rb1 = Radiobutton(cf, text="1 Grid", variable=NumGrid, value=0 )
        rb1.grid(row=3, column=11, sticky=W)
        rb2 = Radiobutton(cf, text="2 Grid", variable=NumGrid, value=1 )
        rb2.grid(row=3, column=12, sticky=W)
        #
        self.fps = Label(cf, text="0 Sps")
        self.fps.grid(row=3, column=13, columnspan=1)
        return(cf)

    def Run(self):
        global Ztime, Dlog_open, dlog
        self.go = 1
        for t in threading.enumerate():
            if t.name == "_gen_":
                print("already running")
                return
        threading.Thread(target=self.do_start, name="_gen_").start()
        if Dlog_open.get() == 1 and dlog.get() > 0:
            Ztime = time.time()
        elif Dlog_open.get() == 0 and dlog.get() > 0:
            open_out()
            Ztime = time.time()
        else:
            Dlog_open.set(0)

    def Stop(self):
        self.go = 0
        for t in threading.enumerate():
            if t.name == "_gen_":
                t.join()

    def Reset(self):
        global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
        global InOffA, InGainA, InOffB, InGainB
        
        self.Stop()
        self.clearstrip(self.gf.p, '#000')
        CHAMaxV = (0.0 - InOffA) * InGainA
        CHAMinV = (5.0 - InOffA) * InGainA
        CHBMaxV = (0.0 - InOffB) * InGainB
        CHBMinV = (5.0 - InOffB) * InGainB

    def do_start(self):
        global DCVA0, DCVB0
        global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
        global NumGrid, SelCHA, SelCHB, SampleRate
        
        t = 0
        y2 = 0
        tx = time.time()
        while self.go:
            Analog_in()
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
                       ('#808080','#808080','#808080','#808080','#0000D0','#808080','#808080','#808000','#808080','#00ff00','#ff8000'),
                         "" if t % SampleRate else "#088")
                elif SelCHA.get():
                    self.scrollstrip(self.gf.p,
                       (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.5+y2),
                       ('#808080','#808080','#808080','#808080','#0000D0','#808080','#808080','#808000','#808080','#ff8000'),
                         "" if t % SampleRate else "#088")
                elif SelCHB.get():
                    self.scrollstrip(self.gf.p,
                       (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.5+y1),
                       ('#808080','#808080','#808080','#808080','#0000D0','#808080','#808080','#808000','#808080','#00ff00'),
                         "" if t % SampleRate else "#088")
            else: # two grids
                y1 = (DCVB0/12.5)-0.2 # scale / 0ffset 0 to 5 V to +/- 0.2
                y2 = (DCVA0/12.5)-0.2 # scale / 0ffset 0 to 5 V to +/- 0.2
                if SelCHA.get() and SelCHB.get():
                    self.scrollstrip(self.gf.p,
                       (0.05,0.15,0.25,0.35,0.45,0.25+y1,0.55,0.65,0.75,0.85,0.95,0.75+y2),
                       ('#008000','#008000','#008000','#008000','#008000','#00ff00','#804000','#804000','#804000','#804000','#804000','#ff8000'),
                         "" if t % SampleRate else "#088")
                elif SelCHA.get():
                    self.scrollstrip(self.gf.p,
                       (0.05,0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.75+y2),
                       ('#008000','#008000','#008000','#008000','#008000','#804000','#804000','#804000','#804000','#804000','#ff8000'),
                         "" if t % SampleRate else "#088")
                elif SelCHB.get():
                    self.scrollstrip(self.gf.p,
                       (0.05,0.15,0.25,0.35,0.45,0.25+y1,0.55,0.65,0.75,0.85,0.95),
                       ('#008000','#008000','#008000','#008000','#008000','#00ff00','#804000','#804000','#804000','#804000','#804000'),
                         "" if t % SampleRate else "#088")
            t += 1
            if not t % 200:
                tx2 = time.time()
                SampleRate = int(200/(tx2 - tx))
                self.fps.config(text='%d Sps' % SampleRate)
                tx = tx2
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
            y0 = int((self.h-1) * (1.0-self.data[d]))   # plot all the data points
            y1 = int((self.h-1) * (1.0-data[d]))
            ya, yb = sorted((y0, y1))
            for y in range(ya, yb+1):                   # connect the dots
                p.put(colors[d], (self.x,y))
                p.put(colors[d], (self.x+self.sw,y))
        self.data = data            # save for next call
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
    global DlogFile, Dlog_open, dlog, root
# close opened files by this process
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
    
def Analog_in():
    global DevID, CHA, CHB, Both, dlog, DlogFile
    global DCVA0, DCVB0, Ztime, SampleDelayEntry
    global InOffA, InOffB, InGainA, InGainB, chalab, chblab
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
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
    ADsignal1 = Both.get_samples(20) # get samples for both channel A0 and B0
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(10): # calculate average
        DCVA0 += ADsignal1[0][index+10][0] # VAdata # Sum for average CA voltage 
        DCVB0 += ADsignal1[1][index+10][0] # VBdata # Sum for average CB voltage

    DCVA0 = DCVA0 / 10.0 # calculate average
    DCVB0 = DCVB0 / 10.0 # calculate average
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
        tstr1 = time.time()-Ztime
        DlogString = '{0:.3f}, '.format(tstr1) + '{0:.3f}, '.format(DCVA0) + '{0:.3f} '.format(DCVB0) + " \n"
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
            exec( line.rstrip() )
        except:
            print "Skipping " + line.rstrip()
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
    global DevID, CHA, CHB, Both, root
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    # setup main window
    TBicon = """
    R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
    hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
    i8fUAgA7
    """
    #
    root = Tk()
    root.title("ALICE 1.1 (11-28-2017): ALM1000 StripChart")
    img = PhotoImage(data=TBicon)
    root.call('wm', 'iconphoto', root._w, img)
    #
    # Setup ADAML1000
    devx = Smu()
    DevID = devx.serials[0]
    print DevID
    CHA = devx.channels['A']    # Open CHA
    CHA.set_mode('d')           # Put CHA in Hi Z mode
    CHB = devx.channels['B']    # Open CHB
    CHB.set_mode('d')           # Put CHB in Hi Z mode
    Both = devx.devices[0]
    devx.ctrl_transfer(DevID, 0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(DevID, 0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    ADsignal1 = []              # Ain signal array channel
    # start main loop
    app = StripChart(root)
    root.mainloop()

main()
