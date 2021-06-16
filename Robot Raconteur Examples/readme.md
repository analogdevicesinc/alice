# ADI provided Robot Raconteur Server for M1K with Python 3 source examples from ALICE

Robot Raconteur is a communication framework for robotics and the Internet of Things, developed by Wason Technology, LLC
(https://www.robotraconteur.com/ and https://github.com/robotraconteur/robotraconteur-directory). The following Python 3 codes provides a way to access the M1k (ADALM1000) board through a Robot Raconteur server link.

## Prerequisites
* Python 3
* [RobotRaconteur](https://github.com/robotraconteur/robotraconteur/wiki/Download)
* [Python bindings](https://github.com/analogdevicesinc/libsmu) (python3.7)

For Windows, the python bindings can be installed along with libsmu [installer](https://github.com/analogdevicesinc/libsmu/releases/tag/v1.0.2)

## Usage:
First run `$ python adi_m1k_service.py` to start the RR server.

Then run whatever client program.

The following examples are offered as is and have not been fully tested. They all prompt for the address of the RR server such as localhost.
Certain parts of the standard pysmu functionality do not work consinstantly (i.e. as when used directly) with Robot Raconteur if at all. Your milage will vary.

## Examples:
`volt-meter-tool-rr.pyw`: Version of ALICE voltmeter tool

`dc-meter-source-tool-rr.pyw`: Version of ALICE DC Meter/Source tool

`ohm-meter-vdiv-rr.pyw`: Version of ALICE Ohmmeter tool

`alice-desktop-for-RR.pyw`: Version of ALICE Desktop

## Service Definition
```
service adi.pysmu.m1k

stdver 0.9

struct read_samples
	field double[] data
	field double timestamp
end

struct sample
	field double[] A
	field double[] B
end

object m1k_obj
	#M1K sample rate, fixed
	property int32 sample_rate	
	#change channel mode							
	function void setmode (string channel, string mode)
	#set led on/off		
	function void setled(int8 val)	
	#read from channel						
	function read_samples read(int16 number)	
	#write to channel				
	function void write(string channel, double[] val)	
	#set pio state		
	function void setpio(string port, int8 val)		
	#get pio state		
	function double getpio(string port)	
	#wire for streaming real-time values					
	wire double[] samples [readonly]	
	#start streaming function					
	function void StartStreaming()	
	#streaming parameters
	property int32 sample_size
	#stop streaming function		
	function void StopStreaming()		
	#set waveform for channel					
	function void wave(string channel, string wavename, double value1, double value2, double periodvalue, double delayvalue, double dutycyclevalue)
	function void AwgWave(string channel, string wavename, double value1, double value2, double periodvalue, double delayvalue, double dutycyclevalue)
	#set arbitrary waveform
	function void arbitrary(string channel, double[] waveform)
	#set arbitrary waveform with repeat flag
	function void ArbitraryWave(string channel, double[] waveform, int8 repeat)
	function sample{list} DiscRead(int16 number)
	function sample{list} ContRead(int16 number))
	function void setchanterm(string channel, string term, string state)
	function void setawgconstant(string channel, double vsl)
	function void SetCtrlTransfer(int8 val1, int8 val2)
	function void SetADCMux(int8 val)
	function void StartSession()
	function void FlushSession()
	function void FlushDevice()
	function void EndSession()
	function void CancelSession()
	function int8 IsContinuous()
	function string GetDeviceSerial()
	function string GetDeviceFirmware()
	function string GetDeviceHardware()
	function double GetDefaultRate()
	function double GetSampleRate()
	function void SetSampleRate(double SAMPLErate)
end

```


