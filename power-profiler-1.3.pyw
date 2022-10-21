#!/usr/bin/python
# ADALM1000 power profiler tool (9-20-2022)
# For Python version > = 2.7.8 and 3.7
# With external module pysmu (libsmu > = 1.0 ADALM1000 )
# Created by D Mercer ()
#
import struct
import subprocess
import __future__
import os
import sys
if sys.version_info[0] == 2:
    print ("Python 2.x")
    from Tkinter import *
    import tkFont
    from ttk import *
    from tkFileDialog import askopenfilename
    from tkFileDialog import asksaveasfilename
    from tkSimpleDialog import askstring
    from tkMessageBox import *
if sys.version_info[0] == 3:
    from tkinter import *
    from tkinter.font import *
    from tkinter.ttk import *
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import asksaveasfilename
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import *
    print ("Python 3.x")
import math, random, threading, time
from pysmu import *
from time import gmtime, strftime
# Check to see if user passed init file name on command line
if len(sys.argv) > 1:
    InitFileName = str(sys.argv[1])
    print( 'Init file name: ' + InitFileName )
else:
    InitFileName = "profiler_init.ini"
#
RevDate = "(20 Sept 2022)"
MouseFocus = 1
# Colors that can be modified
COLORframes = "#000080"   # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORcanvas = "#000000"   # 100% black
COLORgrid = "#808080"     # 50% Gray
COLORzeroline = "#0000ff" # 100% blue
COLORtrace1 = "#00ff00"   # 100% green
COLORtrace2 = "#ff8000"   # 100% orange
COLORtrace3 = "#00ffff"   # 100% cyan
COLORtrace4 = "#ffff00"   # 100% yellow
COLORtrace5 = "#ff00ff"   # 100% magenta
COLORtrace6 = "#C80000"   # 90% red
COLORtrace7 = "#8080ff"   # 100% purple
COLORtraceR1 = "#008000"   # 50% green
COLORtraceR2 = "#905000"   # 50% orange
COLORtraceR3 = "#008080"   # 50% cyan
COLORtraceR4 = "#808000"   # 50% yellow
COLORtraceR5 = "#800080"   # 50% magenta
COLORtraceR6 = "#800000"   # 80% red
COLORtraceR7 = "#4040a0"  # 80% purple
COLORtext = "#ffffff"     # 100% white
COLORtrigger = "#ff0000"  # 100% red
COLORsignalband = "#ff0000" # 100% red
# set up variables
ButtonGreen = "#00ff00"   # 100% green
ButtonRed = "#ff0000" # 100% red
GUITheme = "Light"
ButtonOrder = 0
SBoxarrow = 11
Closed = 0

# # Can be Light or Dark or Blue or LtBlue or Custom where:
FrameBG = "#d7d7d7" # Background color for frame
ButtonText = "#000000" # Button Text color
# Widget relief can be RAISED, GROOVE, RIDGE, and FLAT
ButRelief = RAISED
LabRelief = FLAT
FrameRefief = RIDGE
InOffA = InOffB = 0.0
InGainA = InGainB = 1.0
CANVASwidth = 1000
CANVASheight = 400
CHAMaxV = 0.0
CHAMinV = 5.0
CHBMaxV = 0.0
CHBMinV = 5.0
BaseSampleRate = 100000
SampleRate = 50
SampRates = (10, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 450, 500)
RunStatus = 0
## Vertical Sensitivity list in v/div
CHvpdiv = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
## Vertical Sensitivity list in mA/div or mW/Div
CHipdiv = (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0)
##
# Check if there is an init.ini file to read in
# Check if there is an alice_init.ini file to read in
try:
    import alice
    import pathlib
# pathlib only available as standard in Python 3.4 and higher. For Python 2.7 must manually install package
    path = pathlib.Path(alice.__file__).parent.absolute()
    filename = os.path.join(path, "resources", InitFileName) # "datalogger_init.ini"
    InitFile = open(filename)
    for line in InitFile:
        try:
            exec( line.rstrip(), globals(), globals())
            #exec( line.rstrip() )
        except:
            print("Skiping " + line.rstrip()) 
    InitFile.close()
except:
    try:
        InitFile = open(InitFileName) # "datalogger_init.ini"
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
# samll bit map of ADI logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root = Tk()
root.title("ALICE 1.3 " + RevDate + ": ALM1000 Power Profiler")
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
#root.call('wm', 'iconphoto', root._w, img)
#
root.geometry('+300+0')

root.style = Style()
#('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
if MouseFocus == 1:
    root.tk_focusFollowsMouse()
# define custom buttons
root.style.configure("W3.TButton", width=3, relief=ButRelief)
root.style.configure("W4.TButton", width=4, relief=ButRelief)
root.style.configure("W5.TButton", width=5, relief=ButRelief)
root.style.configure("W7.TButton", width=7, relief=ButRelief)
root.style.configure("W8.TButton", width=8, relief=ButRelief)
root.style.configure("W9.TButton", width=9, relief=ButRelief)
root.style.configure("W10.TButton", width=10, relief=ButRelief)
root.style.configure("W11.TButton", width=11, relief=ButRelief)
root.style.configure("W16.TButton", width=16, relief=ButRelief)
root.style.configure("W17.TButton", width=17, relief=ButRelief)
root.style.configure("Stop.TButton", background="#ff0000", width=4, relief=ButRelief)
root.style.configure("Run.TButton", background="#00ff00", width=4, relief=ButRelief)
root.style.configure("Reset.TButton", background="#ffff00", width=5, relief=ButRelief)
root.style.configure("Pwr.TButton", background="#00ff00", width=7, relief=ButRelief)
root.style.configure("PwrOff.TButton", background="#ff0000", width=7, relief=ButRelief)
root.style.configure("RConn.TButton", background="#ff0000", width=5, relief=ButRelief)
root.style.configure("GConn.TButton", background="#00ff00", width=5, relief=ButRelief)
root.style.configure("Rtrace1.TButton", background=COLORtrace1, width=7, relief=RAISED)
root.style.configure("Strace1.TButton", background=COLORtrace1, width=7, relief=SUNKEN)
root.style.configure("Rtrace2.TButton", background=COLORtrace2, width=7, relief=RAISED)
root.style.configure("Strace2.TButton", background=COLORtrace2, width=7, relief=SUNKEN)
root.style.configure("Rtrace3.TButton", background=COLORtrace3, width=7, relief=RAISED)
root.style.configure("Strace3.TButton", background=COLORtrace3, width=7, relief=SUNKEN)
root.style.configure("Rtrace4.TButton", background=COLORtrace4, width=7, relief=RAISED)
root.style.configure("Strace4.TButton", background=COLORtrace4, width=7, relief=SUNKEN)
root.style.configure("Rtrace5.TButton", background=COLORtrace5, width=7, relief=RAISED)
root.style.configure("Strace5.TButton", background=COLORtrace5, width=7, relief=SUNKEN)
root.style.configure("Rtrace6.TButton", background=COLORtrace6, width=7, relief=RAISED)
root.style.configure("Strace6.TButton", background=COLORtrace6, width=7, relief=SUNKEN)
root.style.configure("Rtrace7.TButton", background=COLORtrace7, width=7, relief=RAISED)
root.style.configure("Strace7.TButton", background=COLORtrace7, width=7, relief=SUNKEN)
root.style.configure("RGray.TButton", background="#808080", width=7, relief=RAISED)
root.style.configure("SGray.TButton", background="#808080", width=7, relief=SUNKEN)
root.style.configure("A10R1.TLabelframe.Label", foreground=COLORtraceR1, font=('Arial', 10, 'bold'))
root.style.configure("A10R1.TLabelframe", borderwidth=5, relief=RIDGE)
root.style.configure("A10R2.TLabelframe.Label", foreground=COLORtraceR2, font=('Arial', 10, 'bold'))
root.style.configure("A10R2.TLabelframe", borderwidth=5, relief=RIDGE)
root.style.configure("A10B.TLabel", foreground=COLORcanvas, font="Arial 10 bold") # Black text
root.style.configure("A10R.TLabel", foreground="#ff0000", font="Arial 10 bold") # Red text
root.style.configure("A10G.TLabel", foreground="#00ff00", font="Arial 10 bold") # Red text
root.style.configure("A12B.TLabel", foreground=COLORcanvas, font="Arial 12 bold") # Black text
root.style.configure("A16B.TLabel", foreground=COLORcanvas, font="Arial 16 bold") # Black text
root.style.configure("Stop.TRadiobutton", background="#ff0000")
root.style.configure("Run.TRadiobutton", background="#00ff00")
root.style.configure("Disab.TCheckbutton", indicatorcolor="#ff0000")
root.style.configure("Enab.TCheckbutton", indicatorcolor="#00ff00")
root.style.configure("WPhase.TRadiobutton", width=5, background="white", indicatorcolor=("red", "green"))
root.style.configure("GPhase.TRadiobutton", width=5, background="gray", indicatorcolor=("red", "green"))
#
ColorMode = IntVar(0)
RUNstatus = IntVar(0)
CHAstatus = IntVar(0)
CHBstatus = IntVar(0)
CHAmode = IntVar(0)
CHBmode = IntVar(0)
AWGAIOMode = IntVar(0)
AWGBIOMode = IntVar(0)
MSScreenStatus = IntVar(0)
#
class StripChart:
    global InOffA, InOffB, InGainA, InGainB, chalab, chblab
    global COLORcanvas, COLORgrid, COLORzeroline, COLORtrace1, COLORtrace2
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV, SampleDelayEntry
    global DCVA0, DCVB0, DCIA0, DCIB0, dlog, Dlog_open, Ztime, Run_For, RunForEntry
    global RUNstatus, CHAstatus, CHBstatus, CHAmode, CHBmode, AWGAIOMode, AWGBIOMode
    global MSScreenStatus, mswindow, RevDate
    global CHAVGainEntry, CHAVOffsetEntry, CHBVGainEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHAIOffsetEntry, CHBIGainEntry, CHBIOffsetEntry
    global labelAI, labelBI, labelAV, labelBV, labelAPW, labelBPW
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV, Sglobal, RateScale
    global CHAsb, CHAIsb, CHAPwsb, CHBsb, CHBIsb, CHBPwsb, CHAPosEntry, CHBPosEntry
    
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
        global Run_For, RunForEntry, cf, CHAsb, CHAIsb, CHAPwsb, CHBsb, CHBIsb, CHBPwsb
        global CHAPosEntry, CHBPosEntry
        global SampRates, InOffA, InOffB, InGainA, InGainB
        
        cf = Frame(frame, borderwidth=1, relief="raised")
        # trace selecters
        SelCHA = IntVar(0)
        lcha = Button(cf, text="CH A", style="Rtrace1.TButton")
        lcha.grid(row=2, column=0, sticky=W)
        selchao = Radiobutton(cf, text="Off", variable=SelCHA, value=0, command = self.ChangeGrid)
        selchao.grid(row=2, column=1, sticky=W)
        selchav = Radiobutton(cf, text="V ", variable=SelCHA, value=1, command = self.ChangeGrid)
        selchav.grid(row=2, column=2, sticky=W)
        selchai = Radiobutton(cf, text="I ", variable=SelCHA, value=2, command = self.ChangeGrid)
        selchai.grid(row=2, column=3, sticky=W)
        selchap = Radiobutton(cf, text="Pw  ", variable=SelCHA, value=3, command = self.ChangeGrid)
        selchap.grid(row=2, column=4, sticky=W)
        SelCHB = IntVar(0)
        lchb = Button(cf, text="CH B", style="Rtrace2.TButton")
        lchb.grid(row=3, column=0, sticky=W)
        selchbo = Radiobutton(cf, text="Off", variable=SelCHB, value=0, command = self.ChangeGrid)
        selchbo.grid(row=3, column=1, sticky=W)
        selchbv = Radiobutton(cf, text="V ", variable=SelCHB, value=1, command = self.ChangeGrid)
        selchbv.grid(row=3, column=2, sticky=W)
        selchbi = Radiobutton(cf, text="I ", variable=SelCHB, value=2, command = self.ChangeGrid)
        selchbi.grid(row=3, column=3, sticky=W)
        selchbp = Radiobutton(cf, text="Pw ", variable=SelCHB, value=3, command = self.ChangeGrid)
        selchbp.grid(row=3, column=4, sticky=W)
        NumGrid = IntVar(0)
        rb1 = Radiobutton(cf, text="1 Grid ", variable=NumGrid, value=0, command = self.ChangeGrid )
        rb1.grid(row=2, column=5, sticky=W)
        rb2 = Radiobutton(cf, text="2 Grid ", variable=NumGrid, value=1, command = self.ChangeGrid )
        rb2.grid(row=3, column=5, sticky=W)
        # Input ranges sub frame
        #
        RangeA = Frame( cf )
        RangeA.grid(row=2, column=6, columnspan=1, sticky=W)
        
        # Voltage ranges
        CHAsb = Spinbox(RangeA, width=4, values=CHvpdiv)#, command=BCHAlevel)
        CHAsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHAsb.pack(side=LEFT)
        CHAsb.delete(0,"end")
        CHAsb.insert(0,0.5)
        CHAlab = Button(RangeA, text="V/Div", style="Rtrace1.TButton")#, command=SetScaleA)
        CHAlab.pack(side=LEFT)
        # Current ranges
        CHAIsb = Spinbox(RangeA, width=5, values=CHipdiv)#, command=BCHAIlevel)
        CHAIsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHAIsb.pack(side=LEFT)
        CHAIsb.delete(0,"end")
        CHAIsb.insert(0,50.0)
        CHAIlab = Button(RangeA, text="mA/Div", style="Strace3.TButton")#, command=SetScaleIA)
        CHAIlab.pack(side=LEFT)
        # Power ranges
        CHAPwsb = Spinbox(RangeA, width=5, values=CHipdiv)#, command=BCHAIlevel)
        CHAPwsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHAPwsb.pack(side=LEFT)
        CHAPwsb.delete(0,"end")
        CHAPwsb.insert(0,50.0)
        CHAPwlab = Button(RangeA, text="mW/Div", style="Strace5.TButton")#, command=SetScaleIA)
        CHAPwlab.pack(side=LEFT)
        
        CHAPosEntry = Entry(RangeA, width=5) #
        CHAPosEntry.bind('<MouseWheel>', onTextScroll)
        CHAPosEntry.pack(side=LEFT)
        CHAPosEntry.delete(0,"end")
        CHAPosEntry.insert(0,InOffA)
        CHAPoslab = Button(RangeA, text="Poss", style="Strace1.TButton")#, command=SetScaleIA)
        CHAPoslab.pack(side=LEFT)
        # CH B
        RangeB = Frame( cf )
        RangeB.grid(row=3, column=6, columnspan=1, sticky=W)
        # Voltage ranges
        CHBsb = Spinbox(RangeB, width=4, values=CHvpdiv)#, command=BCHAlevel)
        CHBsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHBsb.pack(side=LEFT)
        CHBsb.delete(0,"end")
        CHBsb.insert(0,0.5)
        CHBlab = Button(RangeB, text="V/Div", style="Rtrace2.TButton")#, command=SetScaleA)
        CHBlab.pack(side=LEFT)
        # Current ranges
        CHBIsb = Spinbox(RangeB, width=5, values=CHipdiv)#, command=BCHAIlevel)
        CHBIsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHBIsb.pack(side=LEFT)
        CHBIsb.delete(0,"end")
        CHBIsb.insert(0,50.0)
        CHBIlab = Button(RangeB, text="mA/Div", style="Strace4.TButton")#, command=SetScaleIA)
        CHBIlab.pack(side=LEFT)
        # Power ranges
        CHBPwsb = Spinbox(RangeB, width=5, values=CHipdiv)#, command=BCHAIlevel)
        CHBPwsb.bind('<MouseWheel>', onSpinBoxScroll)
        CHBPwsb.pack(side=LEFT)
        CHBPwsb.delete(0,"end")
        CHBPwsb.insert(0,50.0)
        CHBPwlab = Button(RangeB, text="mW/Div", style="Strace7.TButton")#, command=SetScaleIA)
        CHBPwlab.pack(side=LEFT)

        CHBPosEntry = Entry(RangeB, width=5) #
        CHBPosEntry.bind('<MouseWheel>', onTextScroll)
        CHBPosEntry.pack(side=LEFT)
        CHBPosEntry.delete(0,"end")
        CHBPosEntry.insert(0,InOffA)
        CHBPoslab = Button(RangeB, text="Poss", style="Strace2.TButton")#, command=SetScaleIA)
        CHBPoslab.pack(side=LEFT)
        #
        gap1 = Label(cf, text="   ")
        gap1.grid(column=8, row=2)
        br = Button(cf, text="Run", style="Run.TButton", command=self.Run)
        br.grid(column=9, row=2)
        bs = Button(cf, text="Stop", style="Stop.TButton",command=self.Stop)
        bs.grid(column=10, row=2)
        brf = Label(cf, text="Run For")
        brf.grid(column=11, row=2)
        Run_For = IntVar()
        Run_For.set(0)
        runfor = Checkbutton(cf, text="Samples", variable=Run_For)
        runfor.grid(column=12, row=2, columnspan=1)
        RunForEntry = Entry(cf, width=4)
        RunForEntry.bind('<MouseWheel>', onTextScroll)
        RunForEntry.grid(column=13,row=2)
        RunForEntry.delete(0,"end")
        RunForEntry.insert(0,100)
        
        sampdeylab = Label(cf, text="Delay")
        sampdeylab.grid(column=14,row=2)
        SampleDelayEntry = Entry(cf, width=4)
        SampleDelayEntry.bind('<MouseWheel>', onTextScroll)
        SampleDelayEntry.grid(column=15,row=2)
        SampleDelayEntry.delete(0,"end")
        SampleDelayEntry.insert(0,0.0)
        #
        bexit = Button(cf, text="Exit", style="W4.TButton", command=Bcloseexit)
        bexit.grid(column=10,row=3)
        bt = Button(cf, text="Reset", style="Reset.TButton", command=self.Reset)
        bt.grid(column=11, row=3)
        bss = Button(cf, text="Save Screen", command=BSaveScreen)
        bss.grid(column=12, row=3, columnspan=1)
        #
        SRateScale = Spinbox(cf, width=5, values=SampRates)
        SRateScale.bind('<MouseWheel>', onSpinBoxScroll)
        SRateScale.grid(row=3, column=13, sticky=W)
        SRateScale.delete(0,END)
        SRateScale.insert(0, 50)
        #
        self.fps = Label(cf, text="0 Sps")
        self.fps.grid(row=3, column=14, columnspan=1)
        dlog = IntVar()
        dlog.set(0)
        Dlog_open = IntVar()
        Dlog_open.set(0)
        dlog1 = Checkbutton(cf, text="Log to file", variable=dlog, command = Dloger_on_off)
        dlog1.grid(row=3, column=15, columnspan=1)
        #
        #SelCHA.set(1)
        #SelCHB.set(1)
        MakeMeterSourceWindow()
        return(cf)

    def Run(self):
        global Ztime, Dlog_open, dlog, session
        global Run_For, RunForEntry

        RUNstatus.set(1)
        if not session.continuous:
            #print "Run Is Not Continuous? ", session.continuous
            session.start(0)
            UpdateAwgCont()
            #time.sleep(0.02)
            
        else:
            #print "Run Is Continuous? ", session.continuous
            UpdateAwgCont()
            session.flush()
            #time.sleep(0.02)
            #print "Starting continuous mode"
        
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
        global Run_For, RunForEntry
        
        self.go = 0
##        for t in threading.enumerate():
##            if t.name == "_gen_":
##                t.join()
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
#
    def Reset(self):
        global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
        global CHAMaxI, CHAMinI, CHBMaxI, CHBMinI
        global COLORcanvas
        
        self.Stop()
        self.clearstrip(self.gf.p, COLORcanvas)
        CHAMaxV = 0.0
        CHAMinV = 0.0
        CHBMaxV = 0.0
        CHBMinV = 0.0
        CHAMaxI = 0.0
        CHAMinI = 0.0
        CHBMaxI = 0.0
        CHBMinI = 0.0

    def ChangeGrid(self):
        if self.go == 1:
            self.Reset()
            time.sleep(0.05)
            self.Run()

    def do_start(self):
        global DCVA0, DCVB0, DCIA0, DCIB0
        global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
        global COLORcanvas, COLORgrid, COLORzeroline, COLORtrace1, COLORtrace2
        global NumGrid, SelCHA, SelCHB, SampleRate, SRateScale
        global Run_For, RunForEntry # , CHAoffsetEntry, CHArangeEntry, CHBoffsetEntry, CHBrangeEntry
        global CHAoffset, CHArange, CHBoffset, CHBrange
        global CHAsb, CHAIsb, CHAPwsb, CHBsb, CHBIsb, CHBPwsb, CHAPosEntry, CHBPosEntry
        
        t = 0
        y2 = 0
        tx = time.time()
        # add sample counter start here
        loop_end = int(eval(RunForEntry.get()))
        loop_count = 0
        if Run_For.get() == 0 and (loop_end <= loop_count):
            loop_end = loop_count + 1
        while self.go and (loop_count < loop_end): # loop forever or till sample count reached
            Analog_in()
            #
            try:
                CHAPos = float(eval(CHAPosEntry.get()))
            except:
                CHAPosEntry.delete(0,END)
                CHAPosEntry.insert(0, CHAPos)
            try:
                CHBPos = float(eval(CHBPosEntry.get()))
            except:
                CHBPosEntry.delete(0,END)
                CHBPosEntry.insert(0, CHBPos)
            #
            try:
                CHArange = 0.5/float(CHAsb.get())
            except:
                CHArange = 1.0
            try:
                CHAIrange = 0.5/float(CHAIsb.get())
            except:
                CHAIrange = 1.0
            try:
                CHAPwrange = 0.5/float(CHAPwsb.get())
            except:
                CHAPwrange = 1.0
            if CHArange == 0:
                CHArange = 0.00001
            if SelCHA.get() > 0:
                VA0 = (DCVA0-CHAPos)*CHArange
                IA0 = (DCIA0-CHAPos)*CHAIrange
                PwA0 = ((DCVA0*DCIA0)-CHAPos)*CHAPwrange
                if VA0 > 5.0:
                    VA0 = 5.0
                if VA0 < 0.0:
                    VA0 = 0.0
                if IA0 > 5.0:
                    IA0 = 5.0
                if IA0 < 0.0:
                    IA0 = 0.0
                if PwA0 > 5.0:
                    PwA0 = 5.0
                if PwA0 < 0.0:
                    PwA0 = 0.0
            try:
                CHBrange = 0.5/float(CHBsb.get())
            except:
                CHBrange = 1.0
            try:
                CHBIrange = 0.5/float(CHBIsb.get())
            except:
                CHBIrange = 1.0
            try:
                CHBPwrange = 0.5/float(CHBPwsb.get())
            except:
                CHBPwrange = 1.0
            if CHBrange == 0:
                CHBrange = 0.00001
            if SelCHB.get() > 0:
                VB0 = (DCVB0-CHBPos)*CHBrange
                IB0 = (DCIB0-CHBPos)*CHBIrange
                PwB0 = ((DCVB0*DCIB0)-CHBPos)*CHBPwrange
                if VB0 > 5.0:
                    VB0 = 5.0
                if VB0 < 0.0:
                    VB0 = 0.0
                if IB0 > 5.0:
                    IB0 = 5.0
                if IB0 < 0.0:
                    IB0 = 0.0
                if PwB0 > 5.0:
                    PwB0 = 5.0
                if PwB0 < 0.0:
                    PwB0 = 0.0
            if NumGrid.get() == 0: # both on one grid
                if SelCHA.get() == 1: # plot VA
                    y1 = (VA0/5.0)-0.5 # scale / 0ffset 0 to 5 V to +/- 0.4
                    COLORtraceA = COLORtrace1
                elif SelCHA.get() == 2: # plot IA
                    y1 = (IA0/5.0)-0.5 # scale / 0ffset -200 to 200 to +/- 0.4
                    COLORtraceA = COLORtrace3
                elif SelCHA.get() == 3: # plot PwA
                    y1 = (PwA0/5.0)-0.5 # scale / 0ffset -200 to 200 to +/- 0.4
                    COLORtraceA = COLORtrace5
                if SelCHB.get() == 1: # plot VB
                    y2 = (VB0/5.0)-0.5 # scale / 0ffset 0 to 5 V to +/- 0.4
                    COLORtraceB = COLORtrace2
                elif SelCHB.get() == 2: # plot IB
                    y2 = (IB0/5.0)-0.5 # scale / 0ffset -200 to 200 V to +/- 0.4
                    COLORtraceB = COLORtrace4
                elif SelCHB.get() == 3: # plot PwB
                    y2 = (PwB0/5.0)-0.5 # scale / 0ffset -200 to 200 V to +/- 0.4
                    COLORtraceB = COLORtrace7
                #
                if SelCHA.get() > 0 and SelCHB.get() > 0:
                    self.scrollstrip(self.gf.p,
                       (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.5+y1,0.5+y2),
                       (COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORzeroline, COLORgrid, COLORgrid, COLORgrid,
                        COLORgrid, COLORgrid, COLORtraceA, COLORtraceB), "" if t % SampleRate else "#088")
                elif SelCHB.get() > 0:
                    self.scrollstrip(self.gf.p,
                       (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.5+y2),
                       (COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORzeroline, COLORgrid, COLORgrid, COLORgrid,
                        COLORgrid, COLORgrid, COLORtraceB), "" if t % SampleRate else "#088")
                elif SelCHA.get() > 0:
                    self.scrollstrip(self.gf.p,
                       (0.0, 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0, 0.5+y1),
                       (COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORgrid, COLORzeroline, COLORgrid, COLORgrid, COLORgrid,
                        COLORgrid, COLORgrid, COLORtraceA), "" if t % SampleRate else "#088")
            else: # two grids
                if SelCHA.get() == 1: # plot VA
                    y1 = (VA0/10.0)-0.25 # scale / 0ffset 0 to 5 V to +/- 0.2
                    COLORtraceA = COLORtrace1
                elif SelCHA.get() == 2: # plot IA
                    y1 = (IA0/10.0)-0.25 # scale / 0ffset -200 to 200 to +/- 0.2
                    COLORtraceA = COLORtrace3
                elif SelCHA.get() == 3: # plot PwA
                    y1 = (PwA0/10.0)-0.25 # scale / 0ffset -200 to 200 to +/- 0.2
                    COLORtraceA = COLORtrace5
                if SelCHB.get() == 1: # plot VB
                    y2 = (VB0/10.0)-0.25 # scale / 0ffset 0 to 5 V to +/- 0.2
                    COLORtraceB = COLORtrace2
                elif SelCHB.get() == 2: # plot IB
                    y2 = (IB0/10.0)-0.25 # scale / 0ffset -200 to 200 V to +/- 0.2
                    COLORtraceB = COLORtrace4
                elif SelCHB.get() == 3: # plot PwB
                    y2 = (PwB0/10.0)-0.25 # scale / 0ffset -200 to 200 V to +/- 0.2
                    COLORtraceB = COLORtrace7
                #
                if SelCHA.get()>0 and SelCHB.get()>0:
                    self.scrollstrip(self.gf.p,
                       (0.0,0.05,0.15,0.25,0.35,0.45,0.5,0.25+y1,0.55,0.65,0.75,0.85,0.95,1.0,0.75+y2),
                       (COLORgrid,COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORgrid,COLORtraceA,
                        COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORgrid,COLORtraceB), "" if t % SampleRate else "#088")
                elif SelCHB.get()>0:
                    self.scrollstrip(self.gf.p,
                       (0.0,0.05,0.15,0.25,0.35,0.45,0.50,0.55,0.65,0.75,0.85,0.95,1.0,0.75+y2),
                       (COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORgrid,
                        COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORtraceB), "" if t % SampleRate else "#088")
                elif SelCHA.get()>0:
                    self.scrollstrip(self.gf.p,
                       (0.0,0.05,0.15,0.25,0.35,0.45,0.5,0.25+y1,0.55,0.65,0.75,0.85,0.95,1.0),
                       (COLORgrid,COLORgrid,COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORtraceA,
                        COLORgrid,COLORgrid,COLORzeroline,COLORgrid,COLORgrid,COLORgrid), "" if t % SampleRate else "#088")
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
            if loop_count == loop_end:
                self.Stop()
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
    if sys.version_info[0] == 3: # Spin Boxes do this automatically in Python 3 apparently
        return
    if event.delta > 0: # increment digit
        spbox.invoke('buttonup')
    else: # decrement digit
        spbox.invoke('buttondown')
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
    NewVal = OldValfl
    if Dot == -1 : # no point
        Decimals = 0             
        Step = 10**(Len - Pos)
    elif Pos <= Dot : # no point left of position
        Step = 10**(Dot - Pos)
    else:
        Step = 10**(Dot - Pos + 1)
    # respond to Linux or Windows wheel event
    if event.num == 5 or event.delta < 0:
        NewVal = OldValfl - Step
    if event.num == 4 or event.delta > 0:
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
    devx.set_led(0b001) # Set LED.red on the way out
    root.destroy()
    exit()

def Dloger_on_off(): # Toggle dlogger flag
    global DlogFile, Dlog_open, dlog

    if dlog.get() == 1:
        open_out()
        print("Opening Dlog file")
    else:
        close_out()
        print("Closing Dlog file")
        
def close_out():
    global DlogFile, Dlog_open, dlog

    if Dlog_open.get() == 1:
        try:
            DlogFile.close()
            print("Closing Dlog file")
        except:
            Dlog_open.set(0)
    else:
        Dlog_open.set(0)
def open_out():
    global DlogFile, Dlog_open, dlog

    # open file for data logging
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())      # The time
    filename = "DataLogger-" + tme
    filename = filename + ".csv"
    try:
        DlogFile = open(filename, 'a')
    except:
        filename = asksaveasfilename(defaultextension = ".csv", filetypes=[("Comma Separated Values", "*.csv")])
        DlogFile = open(filename, 'a')
    DlogFile.write( 'Time, CA-V, CB-V, CA-I, CB-I \n' )
    Dlog_open.set(1)
    
def Analog_in():
    global DevID, CHA, CHB, devx, session, dlog, DlogFile
    global DCVA0, DCVB0, DCIA0, DCIB0, Ztime, SampleDelayEntry, ADsignal1
    global InOffA, InOffB, InGainA, InGainB, chalab, chblab
    global labelAMaxI, labelBMaxI
    global labelAI, labelBI, labelAV, labelBV, labelAPW, labelBPW
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global CHAMaxI, CHAMinI, CHBMaxI, CHBMinI, SRateScale, BaseSampleRate
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHAIOffsetEntry, CHBIGainEntry, CHBIOffsetEntry
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
    # Get A0 and B0 data
    NumSamples = int(BaseSampleRate/float(SRateScale.get()))
    if session.continuous:
        ADsignal1 = devx.read(NumSamples, -1, False) #True)
    #print len(ADsignal1)
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(NumSamples-10): # calculate average
        DCVA0 += ADsignal1[index][0][0] # Sum for average CA voltage 
        DCVB0 += ADsignal1[index][1][0] # Sum for average CB voltage
        DCIA0 += ADsignal1[index+10][0][1] # Sum for average CA current 
        DCIB0 += ADsignal1[index+10][1][1] # Sum for average CB current
    DCVA0 = DCVA0/(NumSamples-10.0) # calculate average
    DCVB0 = DCVB0/(NumSamples-10.0) # calculate average
    DCIA0 = DCIA0/(NumSamples-10.0) # calculate average
    DCIB0 = DCIB0/(NumSamples-10.0) # calculate average
    DCVA0 = (DCVA0 - InOffA) * InGainA
    DCVB0 = (DCVB0 - InOffB) * InGainB
    DCIA0 = ((DCIA0*1000.0) - CurOffA) * CurGainA
    DCIB0 = ((DCIB0*1000.0) - CurOffB) * CurGainB
    #
    if DCVA0 > CHAMaxV:
        CHAMaxV = DCVA0
    if DCVA0 < CHAMinV:
        CHAMinV = DCVA0
    if DCVB0 > CHBMaxV:
        CHBMaxV = DCVB0
    if DCVB0 < CHBMinV:
        CHBMinV = DCVB0
    if DCIA0 > CHAMaxI:
        CHAMaxI = DCIA0
    if DCIA0 < CHAMinI:
        CHAMinI = DCIA0
    if DCIB0 > CHBMaxI:
        CHBMaxI = DCIB0
    if DCIB0 < CHBMinI:
        CHBMinI = DCIB0
    try:
        VAString = "CA V " + ' {0:.4f} '.format(DCVA0) # format with 4 decimal places
        VBString = "CB V " + ' {0:.4f} '.format(DCVB0) # format with 4 decimal places
        labelAV.config(text = VAString) # change displayed value
        labelBV.config(text = VBString) # change displayed value
        if CHAstatus.get() == 0:
            IAString = "CA mA ----"
            PAString = "CA mW ----"
            AMaxIString = "Max I ----"
        else:
            IAString = "CA mA " + ' {0:.2f} '.format(DCIA0)
            PAString = "CA mW " + ' {0:.2f} '.format(DCVA0*DCIA0)
            AMaxIString = "Max I " + ' {0:.2f} '.format(CHAMaxI) # format with 2 decimal places
        if CHBstatus.get() == 0:
            IBString = "CB mA ----"
            PBString = "CB mW ----"
            BMaxIString = "Max I ----"
        else:
            IBString = "CB mA " + ' {0:.2f} '.format(DCIB0)
            PBString = "CB mW " + ' {0:.2f} '.format(DCVB0*DCIB0)
            BMaxIString = "Max I " + ' {0:.2f} '.format(CHBMaxI) # format with 2 decimal places
        labelAI.config(text = IAString) # change displayed value
        labelAPW.config(text = PAString) # change displayed value
        labelBI.config(text = IBString) # change displayed value
        labelBPW.config(text = PBString) # change displayed value
        labelAMaxI.config(text = AMaxIString) # change displayed value
        labelBMaxI.config(text = BMaxIString) # change displayed value
    except:
        donothing()
    if dlog.get() > 0:
        tstr1 = time.time()-Ztime
        DlogString = '{0:.3f}, '.format(tstr1) + '{0:.3f}, '.format(DCVA0) + '{0:.3f}, '.format(DCVB0) + '{0:.3f}, '.format(DCIA0) + '{0:.3f} '.format(DCIB0) + " \n"
        DlogFile.write( DlogString )
    # wait for sample delay time
    time.sleep(float(SampleDelayEntry.get()))
#
def donothing():
    time.sleep(0.001)
    
def BSaveCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHAIOffsetEntry, CHBIGainEntry, CHBIOffsetEntry
    global CHAsb, CHAIsb, CHAPwsb, CHBsb, CHBIsb, CHBPwsb, CHAPosEntry, CHBPosEntry
    global NumGrid, SelCHA, SelCHB, AWGAIOMode, AWGBIOMode, CHAstatus, CHBstatus
    global CHATestVEntry, CHBTestVEntry, CHATestIEntry, CHBTestVEntry, CHAmode, CHBmode 
    global Run_For, RunForEntry, CHAoffsetEntry, CHArangeEntry, CHBoffsetEntry, CHBrangeEntry
    global DevID, SampleDelayEntry, SRateScale, dlog, mswindow, CANVASwidth, CANVASheight

    filename = asksaveasfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")])
    # open Config file for Write
    CalFile = open(filename, "w")
    # Save Window placements
    CalFile.write("root.geometry('+" + str(root.winfo_x()) + '+' + str(root.winfo_y()) + "')\n")
    CalFile.write("mswindow.geometry('+" + str(mswindow.winfo_x()) + '+' + str(mswindow.winfo_y()) + "')\n")
    CalFile.write('CANVASwidth = ' + str(CANVASwidth) + '\n')
    CalFile.write('CANVASheight = ' + str(CANVASheight) + '\n')
    #
    CalFile.write('NumGrid.set(' + str(NumGrid.get()) + ')\n')
    CalFile.write('SelCHA.set(' + str(SelCHA.get()) + ')\n')
    CalFile.write('SelCHB.set(' + str(SelCHB.get()) + ')\n')
    CalFile.write('CHAmode.set(' + str(CHAmode.get()) + ')\n')
    CalFile.write('CHBmode.set(' + str(CHBmode.get()) + ')\n')
    CalFile.write('AWGAIOMode.set(' + str(AWGAIOMode.get()) + ')\n')
    CalFile.write('AWGBIOMode.set(' + str(AWGBIOMode.get()) + ')\n')
    CalFile.write('CHAstatus.set(' + str(CHAstatus.get()) + ')\n')
    CalFile.write('CHBstatus.set(' + str(CHBstatus.get()) + ')\n')
    CalFile.write('Run_For.set(' + str(Run_For.get()) + ')\n')
    CalFile.write('dlog.set(' + str(dlog.get()) + ')\n')
    
    CalFile.write('CHAVGainEntry.delete(0,END)\n')
    CalFile.write('CHAVGainEntry.insert(4, ' + CHAVGainEntry.get() + ')\n')
    CalFile.write('CHBVGainEntry.delete(0,END)\n')
    CalFile.write('CHBVGainEntry.insert(4, ' + CHBVGainEntry.get() + ')\n')
    CalFile.write('CHAVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAVOffsetEntry.insert(4, ' + CHAVOffsetEntry.get() + ')\n')
    CalFile.write('CHBVOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBVOffsetEntry.insert(4, ' + CHBVOffsetEntry.get() + ')\n')

    CalFile.write('CHAIGainEntry.delete(0,END)\n')
    CalFile.write('CHAIGainEntry.insert(4, ' + CHAIGainEntry.get() + ')\n')
    CalFile.write('CHBIGainEntry.delete(0,END)\n')
    CalFile.write('CHBIGainEntry.insert(4, ' + CHBIGainEntry.get() + ')\n')
    CalFile.write('CHAIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHAIOffsetEntry.insert(4, ' + CHAIOffsetEntry.get() + ')\n')
    CalFile.write('CHBIOffsetEntry.delete(0,END)\n')
    CalFile.write('CHBIOffsetEntry.insert(4, ' + CHBIOffsetEntry.get() + ')\n')
    
    CalFile.write('CHATestVEntry.delete(0,END)\n')
    CalFile.write('CHATestVEntry.insert(4, ' + CHATestVEntry.get() + ')\n')
    CalFile.write('CHBTestVEntry.delete(0,END)\n')
    CalFile.write('CHBTestVEntry.insert(4, ' + CHBTestVEntry.get() + ')\n')
    CalFile.write('CHATestIEntry.delete(0,END)\n')
    CalFile.write('CHATestIEntry.insert(4, ' + CHATestIEntry.get() + ')\n')
    CalFile.write('CHBTestVEntry.delete(0,END)\n')
    CalFile.write('CHBTestVEntry.insert(4, ' + CHBTestVEntry.get() + ')\n')

    CalFile.write('CHAPosEntry.delete(0,END)\n')
    CalFile.write('CHAPosEntry.insert(4, ' + CHAPosEntry.get() + ')\n')
    CalFile.write('CHAsb.delete(0,END)\n')
    CalFile.write('CHAsb.insert(4, ' + CHAsb.get() + ')\n')
    CalFile.write('CHAIsb.delete(0,END)\n')
    CalFile.write('CHAIsb.insert(4, ' + CHAIsb.get() + ')\n')
    CalFile.write('CHAPwsb.delete(0,END)\n')
    CalFile.write('CHAPwsb.insert(4, ' + CHAPwsb.get() + ')\n')
    #
    CalFile.write('CHBPosEntry.delete(0,END)\n')
    CalFile.write('CHBPosEntry.insert(4, ' + CHBPosEntry.get() + ')\n')
    CalFile.write('CHBsb.delete(0,END)\n')
    CalFile.write('CHBsb.insert(4, ' + CHBsb.get() + ')\n')
    CalFile.write('CHBIsb.delete(0,END)\n')
    CalFile.write('CHBIsb.insert(4, ' + CHBIsb.get() + ')\n')
    CalFile.write('CHBPwsb.delete(0,END)\n')
    CalFile.write('CHBPwsb.insert(4, ' + CHBPwsb.get() + ')\n')
    
    CalFile.write('RunForEntry.delete(0,END)\n')
    CalFile.write('RunForEntry.insert(4, ' + RunForEntry.get() + ')\n')
    CalFile.write('SampleDelayEntry.delete(0,END)\n')
    CalFile.write('SampleDelayEntry.insert(4, ' + SampleDelayEntry.get() + ')\n')
    CalFile.write('SRateScale.delete(0,END)\n')
    CalFile.write('SRateScale.insert(0, ' + SRateScale.get() + ')\n')
    #
    CalFile.close()

def BLoadCal():
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHAIOffsetEntry, CHBIGainEntry, CHBIOffsetEntry
    global CHAsb, CHAIsb, CHAPwsb, CHBsb, CHBIsb, CHBPwsb, CHAPosEntry, CHBPosEntry
    global NumGrid, SelCHA, SelCHB, AWGAIOMode, AWGBIOMode, CHAstatus, CHBstatus
    global CHATestVEntry, CHBTestVEntry, CHATestIEntry, CHBTestVEntry
    global Run_For, RunForEntry, CHAoffsetEntry, CHArangeEntry, CHBoffsetEntry, CHBrangeEntry
    global DevID, SampleDelayEntry, SRateScale, mswindow, CANVASwidth, CANVASheight
    global InOffA, InOffB, InGainA, InGainB, CHAmode, CHBmode

    filename = askopenfilename(defaultextension = ".cfg", filetypes=[("Config files", "*.cfg")])
    
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
def EnabAwg():
    global InOffA, InGainA, InOffB, InGainB, CHAmode, CHBmode
    global chatestv, chbtestv, chatesti, chbtesti, AWGAIOMode, AWGBIOMode
    global session, DevID, devx, loopnum, CHAstatus, CHBstatus
    global CHATestVEntry, CHBTestVEntry, CHATestIEntry, CHBTestVEntry
    
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
            #print "About to chang awg and Stopping continuous mode"
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
def DestroyMeterSourceScreen():
    global mswindow, MSScreenStatus
    
    MSScreenStatus.set(0)
    mswindow.destroy()
#
def MakeMeterSourceWindow():
    global RUNstatus, CHAstatus, CHBstatus, CHAmode, CHBmode, AWGAIOMode, AWGBIOMode
    global MSScreenStatus, mswindow, RevDate
    global CHAVGainEntry, CHAVOffsetEntry, CHBVGainEntry, CHBVOffsetEntry
    global CHAIGainEntry, CHAIOffsetEntry, CHBIGainEntry, CHBIOffsetEntry
    global CHATestVEntry, CHATestIEntry, CHBTestVEntry, CHBTestIEntry
    global labelAI, labelBI, labelAV, labelBV, labelAPW, labelBPW
    global labelAMaxI, labelBMaxI, mswindow
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV, Sglobal, RateScale
    global CHAMaxI, CHAMinI, CHBMaxI, CHBMinI

    if MSScreenStatus.get() == 0:
        MSScreenStatus.set(1)
        #
        mswindow = Toplevel()
        mswindow.title("Power Profiler 1.3 " + RevDate)
        mswindow.resizable(FALSE,FALSE)
        mswindow.protocol("WM_DELETE_WINDOW", DestroyMeterSourceScreen)
        #
        msbuttons = Frame( mswindow )
        msbuttons.grid(row=0, column=0, columnspan=4, sticky=W)
        msb1 = Button(msbuttons, text='Save Config', command=BSaveCal)
        msb1.pack(side=LEFT)
        msb2 = Button(msbuttons, text='Load Config', command=BLoadCal)
        msb2.pack(side=LEFT)
        #
        frame1 = Frame(mswindow, borderwidth=5, relief=RIDGE)
        frame1.grid(row=1, column=0, rowspan=2, sticky=W) # 
        frame2 = Frame(mswindow, borderwidth=5, relief=RIDGE)
        frame2.grid(row=1, column=1, rowspan=2, sticky=W) # 
        frame3 = Frame(mswindow, borderwidth=5, relief=RIDGE)
        frame3.grid(row=1, column=2, sticky=NW) # 
        frame4 = Frame(mswindow, borderwidth=5, relief=RIDGE)
        frame4.grid(row=1, column=3, sticky=NW) # 
        #
        labelCA = Label(frame1, font = "Arial 16 bold")
        labelCA.grid(row=0, column=0, columnspan=2, sticky=W)
        labelCA.config(text = "CA Meter")

        labelAV = Label(frame1, font = "Arial 16 bold")
        labelAV.grid(row=1, column=0, columnspan=2, sticky=W)
        labelAV.config(text = "CA-V 0.0000")

        labelAI = Label(frame1, font = "Arial 16 bold")
        labelAI.grid(row=2, column=0, columnspan=2, sticky=W)
        labelAI.config(text = "CA-I 0.00")

        labelAMaxI = Label(frame1, font = "Arial 16 bold")
        labelAMaxI.grid(row=3, column=0, columnspan=2, sticky=W)
        labelAMaxI.config(text = "Max I 0.00")
        
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

        labelBI = Label(frame2, font = "Arial 16 bold")
        labelBI.grid(row=2, column=0, columnspan=2, sticky=W)
        labelBI.config(text = "CB-I 0.00")

        labelBMaxI = Label(frame2, font = "Arial 16 bold")
        labelBMaxI.grid(row=3, column=0, columnspan=2, sticky=W)
        labelBMaxI.config(text = "Max I 0.00")
        
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
#
def main():
    global DevID, CHA, CHB, session, root, devx, ADsignal1
    global CHAVGainEntry, CHBVGainEntry, CHAVOffsetEntry, CHBVOffsetEntry
    global CHAMaxV, CHAMinV, CHBMaxV, CHBMinV
    global CHAMaxI, CHAMinI, CHBMaxI, CHBMinI
    
    # setup main window
    root.protocol("WM_DELETE_WINDOW", Bcloseexit)
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
    devx.set_led(0b010) # LED.green
    ADsignal1 = []              # Ain signal array channel
    CHAMaxV = -100.0
    CHAMinV = 100.0
    CHBMaxV = -100.0
    CHBMinV = 100.0
    CHAMaxI = -200.0
    CHAMinI = 200.0
    CHBMaxI = -200.0
    CHBMinI = 200.0
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    #root.update()
    
    # start main loop
    app = StripChart(root)
    
    root.mainloop()

main()
