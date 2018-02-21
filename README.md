# ALICE

Active Learning Interface (for) Circuits (and) Electronics M1K:

The ALICE Desktop software interface is written for use with the ADALM1000 (M1K) active learning kit hardware.

[ALICE 1.1 User Guide]:https://wiki.analog.com/university/tools/m1k/alice/desk-top-users-guide

If you are looking for ALICE for the ADALM2000 (M2K) look here. 

## Background:

Although the word ALICE can be spelled out from the title of this users guide, it is actually an allusion to 
the fantasy works of Lewis Carroll: 1865’s Alice’s Adventures in Wonderland and its 1871 sequel Through the 
Looking-Glass, and What Alice Found There. In these stories Alice explores a strange and wondrous world down 
a rabbit hole and on the other side of a mirror ( looking glass ).

Hopefully, through the use of this software along with the ADALM1000 active learning kit hardware, Students 
can explore the strange and wondrous world of Circuits, Electronics and Electrical Engineering.

### Functions:

The ALICE Desktop software provides the following functions:

- Two Channel Oscilloscope for time domain display and analysis of voltage and current waveforms.
- Two Channel Arbitrary Waveform Generator (AWG) controls.
- X-Y display for plotting captured voltage and current vs voltage and current data as well as voltage waveform histograms.
- Two Channel Spectrum Analyzer for frequency domain display and analysis of voltage waveforms.
- Bode plotter and network analyzer with built-in sweep generator.
- Impedance Analyzer for analyzing complex RLC networks and as a RLC meter and Vector Voltmeter.
- DC Ohmmeter, measures unknown resistance with respect to known external resistor or known internal 50 ohms.
- Board Self-Calibration using the AD584 precision 2.5V reference from the ADALP2000 Analog Parts Kit

## Required files:

The ALICE Desktop program is written in Python and if run from the source code requires version 2.7.8 or 
greater of Python be installed on the user’s computer. The program only imports modules generally included 
with standard Python installation packages.

### Windows:

Windows users who do not wish to install Python and the other required software packages can install the 
standalone executable under Releases.   

Extract the .exe setup file from the .zip archive. Run the alice-desktop-1.1-setup.exe installer program. 
ALICE desktop opens and saves info and data to various files in the installation directory. Because of user 
permission issues with some installations of Windows you may need to install the software in a directory 
other than the default “Program Files”. C:\ALM Software\ would be a good second choice. The installer adds 
desktop icons for each tool in the suite. Alternatively, under the properties for the icons, you can change 
the directory the program(s) start in.

Or run ALICE Desktop from the Python 2.7 compatible source code with the following packages installed:

Python 2.7.11 (or higher, 32 bit version recommended)
numpy numerical package extension
libsmu/pysmu

Note: For firmware versions greater than or equal to 2.08 you must run a version of ALICE desktop 1.1 dated on or after 10-4-2016

### Linux and OSX:

Most releases of the Linux operating system have Python included and many also include the numpy numerical 
package as well. Linux ( including Raspberry Pi ) and OSX users must manually compile libsmu/pysmu. 

Directions on how to manually install Numpy can be found here.

### Manually installing libsmu / pysmu and ALICE Desktop Python source
