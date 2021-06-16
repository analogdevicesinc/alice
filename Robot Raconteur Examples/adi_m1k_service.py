#!/usr/bin/env python
# for use with ADALM1000 (M1k) and pysmu
# edited June 2021 by D. Mercer
#import robotraconteur library
import RobotRaconteur as RR
RRN=RR.RobotRaconteurNode.s

import sys, time, threading, copy, traceback
import numpy as np
from pysmu import Session, LED, Mode, exceptions

class m1k(object):
    #initialization
    def __init__(self):
        #start session
        self.session = Session(ignore_dataflow=True, queue_size=100000)
        # queue size can be changed, set to 1 Sec of data at 100KSPS
        self.num_dev = self.session.scan() # get number of connected boards
        if self.num_dev == 0:
            print("No M1ks Found")
            sys.exit(1)
        # get first (only?) device
        self.device = self.session.devices[0]
        #define sample rate from default
        self.sample_rate = self.device.default_rate
        #define streaming sample size
        self.sample_size=1
        #initialize default mode to HI_Z
        self.device.channels['A'].mode = Mode.HI_Z
        self.device.channels['B'].mode = Mode.HI_Z
        self.CHA = self.device.channels['A']
        self.CHB = self.device.channels['B']
        #streaming parameters
        self._streaming = False
        self._lock = threading.RLock()
        # Mode List
        self.mode_dict = {'HI_Z': Mode.HI_Z,'HI_Z_SPLIT': Mode.HI_Z_SPLIT,'SVMI': Mode.SVMI,'SVMI_SPLIT':Mode.SVMI_SPLIT,'SIMV':Mode.SIMV,'SIMV_SPLIT':Mode.SIMV_SPLIT}
        # Digitsl port list
        self.port_dict = {'PIO_0': 28,'PIO_1': 29,'PIO_2': 47,'PIO_3': 3,'PIO_4': 4,'PIO_5': 5,'PIO_6': 6,'PIO_7': 7}
        # Analog termination states
        self.term_state_dict = {'OPEN': 0x51,'CLOSED': 0x50}
        self.read_samples = RRN.NewStructure("adi.pysmu.m1k.read_samples")
        self.sample = RRN.NewStructure("adi.pysmu.m1k.sample")
        #wave dict
        self.wavedict = {
        ('A','sine'): self.device.channels['A'].sine,
        ('A','triangle'): self.device.channels['A'].triangle,
        ('A','sawtooth'): self.device.channels['A'].sawtooth,
        ('A','stairstep'): self.device.channels['A'].stairstep,
        ('A','square'): self.device.channels['A'].square,
        ('B','sine'): self.device.channels['B'].sine,
        ('B','triangle'): self.device.channels['B'].triangle,
        ('B','sawtooth'): self.device.channels['B'].sawtooth,
        ('B','stairstep'): self.device.channels['B'].stairstep,
        ('B','square'): self.device.channels['B'].square
        }
        # avoid crashing flag
        self.need_streaming=False
        
    def setawgconstant(self, channel, val): # To set an AWG cahnnel as DC source
        # channel can be 'A' or 'B'
        # val can be 0 to 5.0 V for voltages or -0.2 to 0.2 A for current
        try:
            self.device.channels[channel].constant(val)
        except:
            traceback.print_exc()
        return
        
    def setmode(self, channel, mode): # To set the SMU channel mode
        
        if self._streaming:
            self.StopStreaming()
            self.need_streaming=True
        try:
            self.device.channels[channel].mode = self.mode_dict[mode]
        except:
            traceback.print_exc()
        return

    #set 3 leds on/off based on binary value (000~111)
    def setled(self,val):
        self.device.set_led(val)

    def StartStreaming(self):
        if (self._streaming):
            raise Exception("Already streaming")
        self._streaming=True
        t=threading.Thread(target=self.stream)
        t.start()

    #Stop the streaming thread
    def StopStreaming(self):
        #if (not self._streaming):
        #    raise Exception("Not streaming")
        self._streaming=False

    def stream(self):
        while self._streaming:
            with self._lock:
                try:
                    reading=self.device.get_samples(self.sample_size)
                    self.samples.OutValue=list(sum(sum(reading, ()),()))

                except exceptions.SessionError:
                    self.StopStreaming()
                    print("pysmu Session Error while streaming")
                    self.samples.OutValue=np.zeros(4*self.sample_size)
                    time.sleep(5)
                except:
                    traceback.print_exc()

    def StartSession(self):

        self.session.start(0)

    def FlushSession(self):
        
        self.session.flush()
        
    def FlushDevice(self):
        
        self.device.flush(-1, True)
        
    def IsContinuous(self):

        return self.session.continuous

    def EndSession(self):

        self.session.end()

    def CancelSession(self):

        self.session.cancel()

    def GetDeviceSerial(self): # return device serial number

        return self.device.serial

    def GetDeviceFirmware(self): # return device firmware revision

        return self.device.fwver

    def GetDeviceHardware(self): # return device hardware revision

        return self.device.hwver

    def GetDefaultRate(self): # return device default sample rate

        return self.device.default_rate

    def SetSampleRate(self, SAMPLErate): # set sample rate

        self.session.configure(sample_rate=SAMPLErate)
        
    def GetSampleRate(self): # set sample rate
        
        return self.session.sample_rate

    def read(self,number): # Note: uses Discontinuous mode See DiscRead
        ########read number of samples, return 1D list [A_voltage,A_current,B_voltage,B_current,A_voltage,....]
        reading=self.device.get_samples(number)
        self.read_samples.timestamp=time.time()
        self.read_samples.data=list(sum(sum(reading, ()),()))
        return self.read_samples
    
    def ContRead(self, number): # Use to read samples in Continuous mode
        sample_list=[]        

        for sample in self.session.read(number, -1, True)[0]: # , -1, True
            self.sample.A=sample[0]
            self.sample.B=sample[1]
            sample_list.append(copy.deepcopy(self.sample))
        return sample_list
        
    def DiscRead(self, number): # Use to read samples in Discontinuous mode
        sample_list=[]        

        for sample in self.session.get_samples(number)[0]: # , -1, True
            self.sample.A=sample[0]
            self.sample.B=sample[1]
            sample_list.append(copy.deepcopy(self.sample))
        return sample_list

    def write(self,channel, val): # Note this is a discontinuous mode
        try:
            if self._streaming:
                self.StopStreaming()
                self.device.channels[channel].write(list(val),True)
                time.sleep(0.5)
                self.StartStreaming()
            else:
                self.device.channels[channel].write(list(val),True)
        except exceptions.WriteTimeout:
            self.device.get_samples(self.session.queue_size)
            self.device.channels[channel].write(list(val),True)
        except:
            traceback.print_exc()
        return

    def setpio(self,port,val):
        # port can be 'PIO_0', 'PIO_1', 'PIO_2', 'PIO_3'
        if val:
            self.device.ctrl_transfer(0x40, 0x51, self.port_dict[port], 0, 0, 0, 100) # set to 1
        else:
            self.device.ctrl_transfer(0x40, 0x50, self.port_dict[port], 0, 0, 0, 100) # set to 0

    def SetADCMux(self, val):

        self.device.set_adc_mux(val)
        
    def SetCtrlTransfer(self, val1, val2): # simplified version passes only the values that can change
        #
        self.device.ctrl_transfer(0x40, val1, val2, 0, 0, 0, 100)

    # Returns Input port state as int
    def getpio(self,port):
        
        Dval = self.device.ctrl_transfer(0xc0, 0x91, self.port_dict[port], 0, 0, 1, 100)
        return int(Dval[0])

    def setchanterm(self, channel, term, state):
        # channel can be 'A' or 'B'
        # term can be 'GND' or '2p5'
        # state can be 'OPEN' or 'CLOSED'
        # example setchanterm('A', 'GND', 'OPEN')
        if channel == 'A' and term == '2p5': # set CHA 2.5 V switch
            self.device.ctrl_transfer(0x40, self.term_state_dict[state], 32, 0, 0, 0, 100)
        elif channel == 'A' and term == 'GND': # set CHA GND switch
            self.device.ctrl_transfer(0x40, self.term_state_dict[state], 33, 0, 0, 0, 100)
        #
        if channel == 'B' and term == '2p5': # set CHB 2.5 V switch
            self.device.ctrl_transfer(0x40, self.term_state_dict[state], 37, 0, 0, 0, 100)
        elif channel == 'B' and term == 'GND': # set CHB GND switch
            self.device.ctrl_transfer(0x40, self.term_state_dict[state], 38, 0, 0, 0, 100)

    def ArbitraryWave(self, channel, waveform, repeat): # wave data is a numpy array of floats

        self.device.channels[channel].arbitrary(waveform, repeat)

# Something not right with using libsmu built in wave shapes. Only Square wave shape works?
    def AwgWave(self, channel, wavename, value1, value2, periodvalue, delayvalue, dutycyclevalue=0.5):
        if wavename=="square":
            self.wavedict[(channel,wavename)](value1, value2, periodvalue, delayvalue, dutycyclevalue)
        else:
            self.wavedict[(channel,wavename)](value1, value2, periodvalue, delayvalue)

    def wave(self, channel, wavename, value1, value2, periodvalue, delayvalue, dutycyclevalue=0.5):
        try:
            if wavename=="square":
                self.wavedict[(channel,wavename)](value1, value2, periodvalue, delayvalue, 1.-dutycyclevalue)
            else:
                self.wavedict[(channel,wavename)](value1, value2, periodvalue, delayvalue)
            
            if self.need_streaming:
                self.StartStreaming()
                self.need_streaming=False
        except:
            traceback.print_exc()
        return
    
    def arbitrary(self,channel,waveform):
        
        self.device.channels[channel].arbitrary(waveform,True)
        if self.need_streaming:
            self.StartStreaming()
            self.need_streaming=False

def main():
    with RR.ServerNodeSetup("M1K_Service_Node", 11111) as node_setup:
        #Register the service type
        RRN.RegisterServiceTypeFromFile("adi.pysmu.m1k")

        m1k_obj=m1k()

        #Register the service with object m1k_obj
        RRN.RegisterService("m1k","adi.pysmu.m1k.m1k_obj",m1k_obj)

        #add ws origin
        node_setup.tcp_transport.AddWebSocketAllowedOrigin("http://localhost")
        node_setup.tcp_transport.AddWebSocketAllowedOrigin("https://hehonglu123.github.io")

        #Wait for program exit to quit
        input("Press enter to quit")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()

    except exceptions.SessionError:
        print("Session Error, restarting service")
        main()
    except:
        traceback.print_exc()
    
