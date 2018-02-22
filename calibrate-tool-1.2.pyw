#!/usr/bin/python
# ADALM1000 calibration tool 1.2.py(w) (2-10-2018)
# For Python version > = 2.7.8
# With external module pysmu ( libsmu.rework >= 1.0 for ADALM1000 )
# optional split I/O modes for Rev F hardware supported
# Created by D Mercer ()
#
import math
import time
import csv
import wave
import os
import urllib2
import struct
import subprocess
from time import gmtime, strftime
import tkFont
from Tkinter import *
from ttk import *
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from tkSimpleDialog import askstring
from tkMessageBox import *
import webbrowser
try:
    from pysmu import *
    pysmu_found = True
except:
    pysmu_found = False
#
RevDate = "(10 Feb 2018)"
# samll bit map of ADI logo for window icon
TBicon = """
R0lGODlhIAAgAHAAACH5BAEAAAIALAAAAAAgACAAgQAAAP///wAAAAAAAAJJhI+py+0PYwtBWkDp
hTnv2XlfEobjUZZnmn4se72vJMtcbYN4ruz44uORgiodsfI4Im++2M5VW81OmBbVULxiRVrUsgsO
i8fUAgA7
"""

root=Tk()
root.title("ALM1000 Calibration tool 1.2 " + RevDate)
img = PhotoImage(data=TBicon)
root.call('wm', 'iconphoto', root._w, '-default', img)
#
#
root.style = Style()
#('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
try:
    root.style.theme_use(Style_String)
except:
    root.style.theme_use('default')
#
COLORcanvas = "#000000"   # 100% black
DevID = "m1k"
# set value for on board resistors and ext AD584 reference
OnBoardRes = 50.83
AD584act = 3.3
MaxSamples = 200000
#
root.style.configure("A12B.TLabel", foreground=COLORcanvas, font="Arial 12 bold") # Black text
root.style.configure("A16B.TLabel", foreground=COLORcanvas, font="Arial 16 bold") # Black text
#
def Bcloseexit():
    global session, CHA, CHB

    # Put channels in Hi-Z and exit
    try:
        CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
        CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
        CHA.constant(0.0)
        CHB.constant(0.0)
        if session.continuous:
            session.end()
    except:
        donothing()

    root.destroy()
    exit()
#
def MakeBoardScreen():
    global boardwindow, BoardStatus, session, devx, dev0, dev1, dev2
    global RevDate, BrdSel, FWRevOne, HWRevOne, FWRevTwo, HWRevTwo, WRevThree, HWRevThree
    
    if len(session.devices) > 1: # make screen only if more than one board present
        if BoardStatus.get() == 0:
            BoardStatus.set(1)
            boardwindow = Toplevel()
            boardwindow.title("Select Board " + RevDate)
            boardwindow.resizable(FALSE,FALSE)
            boardwindow.protocol("WM_DELETE_WINDOW", DestroyBoardScreen)
            toplab = Label(boardwindow,text="- Select ALM1000 -", style="A12B.TLabel")
            toplab.pack(side=TOP)
            for idx, devx in enumerate(session.devices):
                BrdText = "Board # " + str(idx)
                if idx == 0:
                    devx.set_led(0b010) # LED.green
                    FWRevOne = float(devx.fwver)
                    HWRevOne = devx.hwver
                    dev0 = session.devices[0]
                    brd = Radiobutton(boardwindow, text=BrdText, fg="green", variable=BrdSel, value=idx, command=SelectBoard)
                elif idx == 1:
                    devx.set_led(0b100) # LED.blue,
                    FWRevTwo = float(devx.fwver)
                    HWRevTwo = devx.hwver
                    dev1 = session.devices[1]
                    brd = Radiobutton(boardwindow, text=BrdText, fg="blue", variable=BrdSel, value=idx, command=SelectBoard)
                elif idx == 2:
                    devx.set_led(0b001) # LED.red,
                    FWRevThree = float(devx.fwver)
                    HWRevThree = devx.hwver
                    dev2 = session.devices[2]
                    brd = Radiobutton(boardwindow, text=BrdText, fg="red", variable=BrdSel, value=idx, command=SelectBoard)
                else:
                    dev3 = session.devices[3]
                    brd = Radiobutton(boardwindow, text=BrdText, variable=BrdSel, value=idx, command=SelectBoard)
                brd.pack(side=TOP)
    else:
        devx = session.devices[0]
        # devx.ignore_dataflow = True
        #devx.set_led(0b010) # LED.green
        FWRevOne = float(devx.fwver)
        HWRevOne = devx.hwver
        dev0 = session.devices[0]
#
def DestroyBoardScreen():
    global boardwindow, BoardStatus
    
    BoardStatus.set(0)
    boardwindow.destroy()
#
def ConnectDevice():
    global devx, dev0, dev1, dev2, session, BrdSel, CHA, CHB, DevID, MaxSamples
    global FWRevOne, HWRevOne, FWRevTwo, HWRevTwo, WRevThree, HWRevThree

    if DevID == "No Device" or DevID == "m1k":
        session = Session(ignore_dataflow=True, queue_size=MaxSamples)
        # session.add_all()
        if not session.devices:
            print 'No Device plugged IN!'
            DevID = "No Device"
            # bcon.configure(text="Recon", style="RConn.TButton") #, bg="red")
            return
        session.configure()
        MakeBoardScreen()
        SelectBoard()
        #bcon.configure(text="Conn", style="GConn.TButton")
#
def SelectBoard():
    global devx, dev0, dev1, dev2, session, BrdSel, CHA, CHB, DevID

    if BrdSel.get() == 0:
        try:
            session.remove(dev1)
        except:
            print "Skipping dev1"
        try:
            session.remove(dev2)
        except:
            print "Skipping dev2"
        session.add(dev0)
        devx = dev0
    if BrdSel.get() == 1:
        try:
            session.remove(dev0)
        except:
            print "Skipping dev0"
        try:
            session.remove(dev2)
        except:
            print "Skipping dev2"
        session.add(dev1)
        devx = dev1
    DevID = devx.serial
    print DevID
    print devx.fwver, devx.hwver
    print devx.default_rate
    CHA = devx.channels['A']    # Open CHA
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB = devx.channels['B']    # Open CHB
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
#
# Optional Calibration procedure routine
#
def SelfCalibration():
    global DevID, devx, CHA, CHB, RevDate, OnBoardRes, AD584act, FWRevOne
    global discontloop, contloop, session, COLORcanvas
    # global OnBoardResAgnd, OnBoardResA25, OnBoardResBgnd, OnBoardResB25
    # setup cal results window
    if FWRevOne < 2.06: # Check firmware revision level > 2.06
        showwarning("WARNING","Out of date Firmware Revision!")
        return
    # display wigets
    prlab = Label(root, text="Channel Gain / Offset calibration", style="A16B.TLabel")
    prlab.grid(row=0, column=0, columnspan=2, sticky=W)
    labelA0 = Label(root, style="A12B.TLabel")
    labelA0.grid(row=1, column=0, columnspan=2, sticky=W)
    labelA0.config(text = "CA gnd Volts")
    labelAMax = Label(root, style="A12B.TLabel")
    labelAMax.grid(row=2, column=0, columnspan=2, sticky=W)
    labelAMax.config(text = "CA 584 Volts")
    labelAMin = Label(root, style="A12B.TLabel")
    labelAMin.grid(row=3, column=0, columnspan=2, sticky=W)
    labelAMin.config(text = "CA 5V Src I ")
    labelB0 = Label(root, style="A12B.TLabel")
    labelB0.grid(row=4, column=0, columnspan=2, sticky=W)
    labelB0.config(text = "CA gnd Volts")
    labelBMax = Label(root, style="A12B.TLabel")
    labelBMax.grid(row=5, column=0, columnspan=2, sticky=W)
    labelBMax.config(text = "CB 584 Volts")
    labelBMin = Label(root, style="A12B.TLabel")
    labelBMin.grid(row=6, column=0, columnspan=2, sticky=W)
    labelBMin.config(text = "CB 5V Src I ")
    labelAB = Label(root, style="A12B.TLabel")
    labelAB.grid(row=7, column=0, columnspan=2, sticky=W)
    labelAB.config(text = "CA 0V Src I")
    labelBA = Label(root, style="A12B.TLabel")
    labelBA.grid(row=8, column=0, columnspan=2, sticky=W)
    labelBA.config(text = "CA 0V Src I")
    labelSIA0 = Label(root, style="A12B.TLabel")
    labelSIA0.grid(row=9, column=0, columnspan=2, sticky=W)
    labelSIA0.config(text = "CA 2.5 Src 0 I")
    labelSIA = Label(root, style="A12B.TLabel")
    labelSIA.grid(row=10, column=0, columnspan=2, sticky=W)
    labelSIA.config(text = "CA 50 Src 100 ")
    labelSIAN = Label(root, style="A12B.TLabel")
    labelSIAN.grid(row=11, column=0, columnspan=2, sticky=W)
    labelSIAN.config(text = "CA 50 Src -45")
    labelSIB0 = Label(root, style="A12B.TLabel")
    labelSIB0.grid(row=12, column=0, columnspan=2, sticky=W)
    labelSIB0.config(text = "CB 2.5 Src 0 I")
    labelSIB = Label(root, style="A12B.TLabel")
    labelSIB.grid(row=13, column=0, columnspan=2, sticky=W)
    labelSIB.config(text = "CB 50 Src 100 ")
    labelSIBN = Label(root, style="A12B.TLabel")
    labelSIBN.grid(row=14, column=0, columnspan=2, sticky=W)
    labelSIBN.config(text = "CB 50 Src -45")
    if session.continuous:
        session.end()
    # Setup ADAML1000
    if askyesno("Reset Calibration", "Do You Need To Reset Default Calibration?", parent=root):
        #print(devx.calibration)
        try:
            devx.write_calibration("calib_default.txt")
            #print "wrote calib_default.txt"
        except:
            filename = askopenfilename(defaultextension = ".txt", filetypes=[("Default Cal File", "*.txt")], parent=root)
            devx.write_calibration(filename)
        #print(devx.calibration)
    #
    devidstr = DevID[17:31]
    filename = "calib" + devidstr + ".txt"
    if os.path.isfile(filename):
        if askyesno("Calibration exists", 'A previous Calibration file exists./nDo you want to load that?', parent=root):
            devx.write_calibration(filename)
            #print "wrote old ", filename
            root.destroy()
            return
    #
    CalFile = open(filename, "w")
    #
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    devx.ctrl_transfer( 0x40, 0x50, 34, 0, 0, 0, 100) # close voltage sense loop just in case
    devx.ctrl_transfer( 0x40, 0x50, 39, 0, 0, 0, 100) # close voltage sense loop just in case
    ADsignal1 = []              # Ain signal array channel
    ADsignal1 = devx.get_samples(1010)
    # Pause whie user connects external voltage reference AD584
    BadData = 1
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    RequestVRef = askstring("External Reference", "Enter External Reference Voltage", initialvalue=AD584act, parent=root)
    try:
        AD584act = float(RequestVRef)*1.0
    except:
        AD584act = 3.3
    showinfo("CONNECT","Connect External Voltage to both CH-A and CH-B inputs.",  parent=root)
    while (BadData):       # loop till good reading
        # Get A  and B AD584 data
        CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
        CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
        ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
        CHA584Raw = CHB584Raw = 0.0 # initalize measurment variable
        # get_samples returns a list of values for voltage [0] and current [1]
        for index in range(1000): # calculate average
            CHA584Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
            CHB584Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage

        CHA584Raw = CHA584Raw / 1000.0 # calculate average
        CHB584Raw = CHB584Raw / 1000.0 # calculate average
        VString = "Extern A Volts " + ' {0:.4f} '.format(CHA584Raw) # format with 4 decimal places
        labelAMax.config(text = VString) # change displayed value
        VString = "Extern B Volts " + ' {0:.4f} '.format(CHB584Raw) # format with 4 decimal places
        labelBMax.config(text = VString) # change displayed value
        Lower = AD584act - 0.3
        Upper = AD584act + 0.3
        if CHA584Raw < Lower or CHA584Raw > Upper or CHB584Raw < Lower or CHB584Raw > Upper:
            if askyesno("CONNECT","Did not get good data from Ref V, check connections!\n Abort(Y) or Try again(N)", parent=root):
                CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
                CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
                contloop = 0
                discontloop = 1
                root.destroy()
                return
        else:
            BadData = 0
    #
    showinfo("DISCONNECT","Disconnect everything from CHA and CHB pins.", parent=root)
    CHAGndRaw = CHBGndRaw = CHAI0gRaw = CHBI0gRaw = 0.0 # initalize measurment variable
    # Get A GND and B GND data
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 33, 0, 0, 0, 100) # set GND switch to closed
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 38, 0, 0, 0, 100) # set CHB GND switch to closed
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHAGndRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBGndRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI0gRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI0gRaw += ADsignal1[index+10][1][1] # Sum for average CB current

    CHAGndRaw = CHAGndRaw / 1000.0 # calculate average
    CHAI0gRaw = CHAI0gRaw / 1000.0
    CHBGndRaw = CHBGndRaw / 1000.0 # calculate average
    CHBI0gRaw = CHBI0gRaw / 1000.0
    VString = "CA gnd Volts " + ' {0:.4f} '.format(CHAGndRaw) # format with 4 decimal places
    labelA0.config(text = VString) # change displayed value
    VString = "CB gnd Volts " + ' {0:.4f} '.format(CHBGndRaw) # format with 4 decimal places
    labelB0.config(text = VString) # change displayed value
    CHA2p5Raw = CHB2p5Raw = CHAI02p5Raw = CHBI02p5Raw = 0.0 # initalize measurment variable
    # Get A and B data for internal 2.5 rail
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHA2p5Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHB2p5Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI02p5Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI02p5Raw += ADsignal1[index+10][1][1] # Sum for average CB current
        
    CHA2p5Raw = CHA2p5Raw / 1000.0 # calculate average
    CHAI02p5Raw = CHAI02p5Raw / 1000.0
    CHB2p5Raw = CHB2p5Raw / 1000.0 # calculate average
    CHBI02p5Raw = CHBI02p5Raw / 1000.0
    # Get A force 0V and B force 0V data
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SVMI
    CHA.constant(0.0)
    CHB.mode = Mode.SVMI
    CHB.constant(0.0)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAF0vRaw = CHBF0vRaw = CHAI0F0Raw = CHBI0F0Raw = 0.0 # initalize measurment variable
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHAF0vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBF0vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI0F0Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI0F0Raw += ADsignal1[index+10][1][1] # Sum for average CB current
        
    CHAF0vRaw = CHAF0vRaw / 1000.0 # calculate average
    CHAI0F0Raw = CHAI0F0Raw / 1000.0
    CHBF0vRaw = CHBF0vRaw / 1000.0 # calculate average
    CHBI0F0Raw = CHBI0F0Raw / 1000.0
    # Get A force 2.5V and B force 2.5V data
    CHA.mode = Mode.SVMI
    CHA.constant(4.5)
    CHB.mode = Mode.SVMI
    CHB.constant(4.5)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAF25vRaw = CHAI0F25Raw = CHBF25vRaw = CHBI0F25Raw = 0.0 # initalize measurment variable
    # get_samples returns a list of values for voltage [0] and current [1]
    for index in range(1000): # calculate average
        CHAF25vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBF25vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAI0F25Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBI0F25Raw += ADsignal1[index+10][1][1] # Sum for average CB current
        
    CHAF25vRaw = CHAF25vRaw / 1000.0 # calculate average
    CHAI0F25Raw = CHAI0F25Raw / 1000.0
    CHBF25vRaw = CHBF25vRaw / 1000.0 # calculate average
    CHBI0F25Raw = CHBI0F25Raw / 1000.0
    #
    # Get A and B measure current data for int 50 res to gnd at 5V
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 33, 0, 0, 0, 100) # set CHA GND switch to closed
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x50, 38, 0, 0, 0, 100) # set CHB GND switch to closed
    CHA.mode = Mode.SVMI
    CHA.constant(5.0)
    CHB.mode = Mode.SVMI
    CHB.constant(5.0)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHASr5vRaw = CHAISr5vRaw = CHBSr5vRaw = CHBISr5vRaw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHASr5vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBSr5vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr5vRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr5vRaw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHASr5vRaw = CHASr5vRaw / 1000.0 # calculate average
    CHAISr5vRaw = CHAISr5vRaw / 1000.0
    CHBSr5vRaw = CHBSr5vRaw / 1000.0 # calculate average
    CHBISr5vRaw = CHBISr5vRaw / 1000.0
    VString = "CA 5V Src I " + ' {0:.4f} '.format(CHAISr5vRaw) # format with 4 decimal places
    labelAMin.config(text = VString) # change displayed value
    VString = "CB 5V Src I " + ' {0:.4f} '.format(CHBISr5vRaw) # format with 4 decimal places
    labelBMin.config(text = VString) # change displayed value
    # Get A and B measure current data for int 50 res to 2.5 V  at 0V
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SVMI
    CHA.constant(0.001)
    CHB.mode = Mode.SVMI
    CHB.constant(0.001)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHASr0vRaw = CHAISr0vRaw = CHBSr0vRaw = CHBISr0vRaw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHASr0vRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBSr0vRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr0vRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr0vRaw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHASr0vRaw = CHASr0vRaw / 1000.0 # calculate average
    CHAISr0vRaw = CHAISr0vRaw / 1000.0
    CHBSr0vRaw = CHBSr0vRaw / 1000.0 # calculate average
    CHBISr0vRaw = CHBISr0vRaw / 1000.0
    VString = "CA 0V Src I " + ' {0:.4f} '.format(CHAISr0vRaw) # format with 4 decimal places
    labelAB.config(text = VString) # change displayed value
    VString = "CB 0V Src I " + ' {0:.4f} '.format(CHBISr0vRaw) # format with 4 decimal places
    labelBA.config(text = VString) # change displayed value

    # Get A and B force 0.0 current data for int 50 res to 2.5 rail
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SIMV
    CHA.constant(0.0)
    CHB.mode = Mode.SIMV
    CHB.constant(0.0)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAVSr0iRaw = CHAISr0iRaw = CHBVSr0iRaw = CHBISr0iRaw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHAVSr0iRaw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBVSr0iRaw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr0iRaw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr0iRaw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHAVSr0iRaw = CHAVSr0iRaw / 1000.0 # calculate average
    CHAISr0iRaw = CHAISr0iRaw / 1000.0
    CHBVSr0iRaw = CHBVSr0iRaw / 1000.0 # calculate average
    CHBISr0iRaw = CHBISr0iRaw / 1000.0
    VString = "CA 2.5 Src 0 I" + ' {0:.4f} '.format(CHAISr0iRaw) # format with 4 decimal places
    labelSIA0.config(text = VString) # change displayed value
    VString = "CB 2.5 Src 0 I" + ' {0:.4f} '.format(CHBISr0iRaw) # format with 4 decimal places
    labelSIB0.config(text = VString) # change displayed value
    #
    # Get A and B force +0.45 current data for int 50 res to 2.5 V rail
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SIMV
    CHA.constant(0.045)
    CHB.mode = Mode.SIMV
    CHB.constant(0.045)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAVSr100Raw = CHAISr100Raw = CHBVSr100Raw = CHBISr100Raw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHAVSr100Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBVSr100Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISr100Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISr100Raw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHAVSr100Raw = CHAVSr100Raw / 1000.0 # calculate average
    CHAISr100Raw = CHAISr100Raw / 1000.0
    CHBVSr100Raw = CHBVSr100Raw / 1000.0 # calculate average
    CHBISr100Raw = CHBISr100Raw / 1000.0
    VString = "CA 50 Src +45 " + ' {0:.4f} '.format(CHAVSr100Raw) # format with 4 decimal places
    labelSIA.config(text = VString) # change displayed value
    VString = "CB 50 Src +45 " + ' {0:.4f} '.format(CHBVSr100Raw) # format with 4 decimal places
    labelSIB.config(text = VString) # change displayed value
    #
    # Get A and B force -0.045 current data for int 50 res to 2.5 V rail
    devx.ctrl_transfer(0x40, 0x50, 32, 0, 0, 0, 100) # set CHA 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set CHA GND switch to open
    devx.ctrl_transfer(0x40, 0x50, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to closed
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    CHA.mode = Mode.SIMV
    CHA.constant(-0.045)
    CHB.mode = Mode.SIMV
    CHB.constant(-0.045)
    ADsignal1 = devx.get_samples(1010) # get samples for dev channel A0 and B0
    CHAVSrN45Raw = CHAISrN45Raw = CHBVSrN45Raw = CHBISrN45Raw = 0.0 # initalize measurment variable
    for index in range(1000): # calculate average
        CHAVSrN45Raw += ADsignal1[index+10][0][0] # Sum for average CA voltage 
        CHBVSrN45Raw += ADsignal1[index+10][1][0] # Sum for average CB voltage
        CHAISrN45Raw += ADsignal1[index+10][0][1] # Sum for average CA current 
        CHBISrN45Raw += ADsignal1[index+10][1][1] # Sum for average CB current
                       
    CHAVSrN45Raw = CHAVSrN45Raw / 1000.0 # calculate average
    CHAISrN45Raw = CHAISrN45Raw / 1000.0
    CHBVSrN45Raw = CHBVSrN45Raw / 1000.0 # calculate average
    CHBISrN45Raw = CHBISrN45Raw / 1000.0
    VString = "CA 50 Src -45 " + ' {0:.4f} '.format(CHAVSrN45Raw) # format with 4 decimal places
    labelSIAN.config(text = VString) # change displayed value
    VString = "CB 50 Src -45 " + ' {0:.4f} '.format(CHBVSrN45Raw) # format with 4 decimal places
    labelSIBN.config(text = VString) # change displayed value
    # return all switches to open
    devx.ctrl_transfer(0x40, 0x51, 32, 0, 0, 0, 100) # set 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 33, 0, 0, 0, 100) # set GND switch to open
    devx.ctrl_transfer(0x40, 0x51, 37, 0, 0, 0, 100) # set CHB 2.5 V switch to open
    devx.ctrl_transfer(0x40, 0x51, 38, 0, 0, 0, 100) # set CHB GND switch to open
    # Caculate voltage gain errors
    # 
    CHAF25V = CHAF25vRaw * ( AD584act / CHA584Raw )
    CHBF25V = CHBF25vRaw * ( AD584act / CHB584Raw )
    #
    CHASr5v = CHASr5vRaw * ( AD584act / CHA584Raw ) # calculate actual voltage
    CHBSr5v = CHBSr5vRaw * ( AD584act / CHB584Raw ) # calculate actual voltage
    #
    CHA2p5 = CHA2p5Raw * ( AD584act / CHA584Raw )
    # print "calculated fixed 2.5 from CHA ", CHA2p5
    CHB2p5 = CHB2p5Raw * ( AD584act / CHB584Raw )
    # print "calculated fixed 2.5 from CHB ", CHB2p5
    # 
    CHAActSrI = CHASr5v / OnBoardRes # adjust resistor value to include switch ron
    CHBActSrI = CHBSr5v / OnBoardRes # adjust resistor value to include switch ron
    #
    CHAActSnkI = CHASr0vRaw - CHA2p5 / OnBoardRes # adjust resistor value to include switch ron
    CHBActSnkI = CHBSr0vRaw - CHB2p5 / OnBoardRes # adjust resistor value to include switch ron
    #
    CHASr0i = CHAVSr0iRaw * ( AD584act / CHA584Raw )
    CHASr0iAct = CHASr0i / OnBoardRes # adjust resistor value to include switch ron
    CHASr100 = CHAVSr100Raw * ( AD584act / CHA584Raw )
    CHASrI100Act = (CHASr100 - CHA2p5) / OnBoardRes # adjust resistor value to include switch ron
    CHASrN45 = CHAVSrN45Raw * ( AD584act / CHA584Raw )
    CHASrIN45Act = (CHASrN45 - CHA2p5) / OnBoardRes # adjust resistor value to include switch ron
    #
    CHBSr0i = CHBVSr0iRaw * ( AD584act / CHB584Raw )
    CHBSr0iAct = CHBSr0i / OnBoardRes # adjust resistor value to include switch ron
    CHBSr100 = CHBVSr100Raw * ( AD584act / CHB584Raw )
    CHBSrI100Act = (CHBSr100 - CHB2p5) / OnBoardRes # adjust resistor value to include switch ron
    CHBSrN45 = CHBVSrN45Raw * ( AD584act / CHB584Raw )
    CHBSrIN45Act = (CHBSrN45 - CHB2p5) / OnBoardRes # adjust resistor value to include switch ron
    # Write cal factors to file
    #
    CalFile.write('# Channel A, measure V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAGndRaw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(AD584act) + ', ' + '{0:.4f}'.format(CHA584Raw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel A, measure I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAI02p5Raw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(CHAActSrI) + ', ' + '{0:.4f}'.format(CHAISr5vRaw) + '>\n')
    # CalFile.write('<' + '{0:.4f}'.format(CHAISr0vRaw) + ', ' + '{0:.4f}'.format(CHAActSnkI) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(-CHAActSrI) + ', ' + '{0:.4f}'.format(-CHAISr5vRaw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel A, source V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAF0vRaw) + '>\n')
    CalFile.write('<4.5000, ' + '{0:.4f}'.format(CHAF25V) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel A, source I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHAISr0iRaw) + '>\n')
    CalFile.write('<0.045, ' + '{0:.4f}'.format(CHASrI100Act) + '>\n')
    CalFile.write('<-0.0450, ' + '{0:.4f}'.format(CHASrIN45Act) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B, measure V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBGndRaw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(AD584act) + ', ' + '{0:.4f}'.format(CHB584Raw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B, measure I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBI02p5Raw) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(CHBActSrI) + ', ' + '{0:.4f}'.format(CHBISr5vRaw) + '>\n')
    # CalFile.write('<' + '{0:.4f}'.format(CHBISr0vRaw) + ', ' + '{0:.4f}'.format(CHBActSnkI) + '>\n')
    CalFile.write('<' + '{0:.4f}'.format(-CHBActSrI) + ', ' + '{0:.4f}'.format(-CHBISr5vRaw) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B, source V\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBF0vRaw) + '>\n')
    CalFile.write('<4.5000, ' + '{0:.4f}'.format(CHAF25V) + '>\n')
    CalFile.write('<\>\n')
    CalFile.write('\n')
    #
    CalFile.write('# Channel B source I\n')
    CalFile.write('</>\n')
    CalFile.write('<0.0000, ' + '{0:.4f}'.format(CHBISr0iRaw) + '>\n')
    CalFile.write('<0.045, ' + '{0:.4f}'.format(CHBSrI100Act) + '>\n')
    CalFile.write('<-0.0450, ' + '{0:.4f}'.format(CHBSrIN45Act) + '>\n')
    CalFile.write('<\>\n')
    #
    CalFile.close()
    showinfo("Finish","Successfully measured cal factors!", parent=root)
    if askyesno("Write cal", "Write Cal Data to Board?",  parent=root):
        devx.write_calibration(filename)
        #print "wrote new " , filename
    #
    # session.end()
    CHA.mode = Mode.HI_Z # Put CHA in Hi Z mode
    CHB.mode = Mode.HI_Z # Put CHB in Hi Z mode
    contloop = 0
    discontloop = 1
    # session.cancel()
    root.destroy()
#
#
BrdSel = IntVar(0)
BoardStatus = IntVar(0)
root.protocol("WM_DELETE_WINDOW", Bcloseexit)
if pysmu_found:
    ConnectDevice()

# ================ Call main routine ===============================
    root.update()               # Activate updated screens
#
# Start sampling
    SelfCalibration()
    Bcloseexit()
else:
    root.update()
    showwarning("WARNING","Pysmu not found!")
    root.destroy()
    exit()
