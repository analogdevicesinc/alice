# ALICE

Active Learning Interface (for) Circuits (and) Electronics:

The ALICE Desktop software interface is a collection of software instruments written for use with the active learning hardware modules ADALM1000 (M1K) and ADALM2000 (M2K). Note: Source code for M2k is no longer being up dated and is likely non-functional.
### [ALICE 1.1 User Guide for M1K]:
### [ALICE 2.0 User Guide for M2K]:
[ALICE 1.1 User Guide for M1K]:https://wiki.analog.com/university/tools/m1k/alice/desk-top-users-guide
[ALICE 2.0 User Guide for M2K]:https://wiki.analog.com/university/tools/m2k/alice/users-guide-m2k

## Background:

Although the word ALICE can be spelled out from the title of this users guide, it is actually an allusion to 
the fantasy works of Lewis Carroll: 1865’s Alice’s Adventures in Wonderland and its 1871 sequel Through the 
Looking-Glass, and What Alice Found There. In these stories Alice explores a strange and wondrous world down 
a rabbit hole and on the other side of a mirror ( looking glass ).

Hopefully, through the use of this software along with the active learning hardware modules, Students 
can explore the strange and wondrous world of Circuits, Electronics and Electrical Engineering.

### Functions:

The ALICE Desktop software provides the following functions:

- Two Channel Oscilloscope for time domain display and analysis of voltage and current waveforms.
- Two Channel Arbitrary Waveform Generator (AWG) controls.
- X-Y display for plotting captured analog signal data as well as waveform histograms.
- Two Channel Spectrum Analyzer for frequency domain display and analysis of analog waveforms.
- Bode plotter and network analyzer with built-in sweep generator.
- Impedance Analyzer for analyzing complex RLC networks and as a RLC meter and Vector Voltmeter.
- DC Ohmmeter, measures unknown resistance with respect to known external resistor or known internal 50 ohms.
- M1K Board Self-Calibration using a known external reference such as an AD584 precision 2.5V reference from the ADALP2000 Analog Parts Kit

## Required files:

The ALICE Desktop programs are written in Python and if run from the source code requires version 2.7.8 or 
greater of Python be installed on the user’s computer. The program only imports modules generally included 
with standard Python installation packages.

### Windows:

Windows users who do not wish to install Python and the other required software packages can install the 
standalone executable under Releases.   

Run the alice-desktop-1.2-setup.exe or alice-desktop-2.0-setup.exe installer program. 
ALICE desktop opens and saves info and data to various files in the installation directory. Because of user 
permission issues with some installations of Windows you may need to install the software in a directory 
other than the default “Program Files”. C:\ALM Software\ would be a good second choice. The installer adds 
desktop icons for each tool in the suite. Alternatively, under the properties for the icons, you can change 
the directory the program(s) start in.

Or run ALICE Desktop from the Python 2.7 compatible source code with the following packages installed:

Python 2.7.11 (or higher, 32 bit version recommended)
numpy numerical package extension
libsmu/pysmu for M1K or libiio/iio.py for M2K
