ACKNOWLEDGEMENTS: I would like to give Kristi Engel credit for her .ino code file which this program runs to control the Arduino. Also the code to control the signal generator is adapted from an example program on the Siglent website.

WHAT THIS CODE DOES: 
- Changes the position of the Arduino on the track
- Changes the pulse amplitude, width, and frequency of the signal generator
- Collects measurements of voltage with time from the scope and saves these as .npy files 
- Counts the number of "hits" (where the voltage on the PMT channel goes below the threshold voltage)
- Integrates the signals on the PMT channel to get charge
- Fits the charge distribution to a Poisson PE distribution where each PE no. has a individual Gaussian charge distribution 
- Measures the "peak" voltage on the LED channel
- Estimates the duration between the times the voltage on the LED channel hits the threshold
- Integrates the voltage on the LED channel over the specified range.
- Produces (and saves) graphs of the signal trace, charge distribution of PMT, charge distribution of LED, distribution of other measurements of LED such as the peak and duration
- Saves data from each set of waveforms including the parameters from the PMT fit, uncertainty on these parameters, average/median/standard deviation of LED peak/duration/charge, and the time of data collection

SOME NOTES:
- Don't be alarmed by the reflection visible in channel C. Since the cable is properly terminated at the scope, the reflection does not affect the amount of light produced by the LED.
- If we end up getting a new signal generator, it might be handy to "reserve" an IP address for it, and then change the IP address in ~/autocontrol/python_scripts/sig_gen.py and sig_gen2.py to that IP address. If for some reason we get a different model of signal generator, it may be necesssary to change the port number in these two python scripts as well. There is some guidance in the comments of these scripts for which port number would be best for which model of Siglent signal generator.
- If the PMT (or HV on PMT) is changed, it will be necessary to change the $pe_charge variable in the run_autocontrol.sh file. If it is a new PMT, you can take several measurements at low-ish occupancies (<0.96), and the code will fit these. You can use the fitted values to determine what the new $pe_charge value should be. The fit will rely on the value of $pe_charge for occupanies >0.96. (Further explanation below under the heading FILE DIRECTORIES under subheading ~/autocontrol/output_files/{my file folder here}/charge_distribution)
- As of right now, the signal generator will randomly become unresponsive to button pressing, connecting over Ethernet, etc. When this code recognizes that that is happening, run_autocontrol.sh will just stop running. It will output a message in the log file, which is why it can be a good idea to periodically check on the log file or just leave it open using "tail -f"
-Once the code completes running, the arduino will be in setting 7. This is because Kristi had recommended avoiding leaving the Arduino in positions near the edge of the track, because it could fall off (unless I remember wrong). This means that if you want to take measurements through other means (ie. the application on the computer by the picoscope company), and you would prefer the arduino is at a different setting, follow the instructions below under heading 'Controlling Arduino Through Command Line' (or you could just use the Arduino IDE, either will work!) Remember to change the arduino setting back to 7 once you are finished.
-This code switches the load on the signal generator to 50 ohms. This may be important if you want to compare some data taken using this program to some taken by hand, because it would be best to have the load on the signal generator the same for both. (If I remember right, the default load on the signal generator is HiZ, so this could be easily overlooked, especially if the signal generator was turned off and then on again.) The load on the signal generator can be changed easily in the sig_gen.py file under python_scripts, or through pressing buttons on the signal generator.
-If you quit this program using 'Ctrl-C' or using the 'kill' command, it might be a good idea to run 'screen -X kill', and then 'screen -wipe', which are typically run at the end of the code. Otherwise, you will get some error messages when you run the code next time, but they will not actually interfere with the code.
-The fitting function is actually the integral of a continuous charge distribution (see slides that I sent to Jordan and Andy) over the bin sizes.
-For some of the old histograms of LED charge, the y axis is mistakenly labeled "Fractional Count", but is actually the "Count". This is fixed for future runs of the code.

A slighly redundant note that hopefully will make this documentation easier to understand: Each "run" is comprised of $waveform_no number of waveforms. Each waveform is a trigger on the oscilloscope. Each one of these waveforms has $sample_no number of samples. Each sample is a data point with a time, and a voltage for each of the enabled oscilloscope channels.

HOW TO USE:
Edit any of the data collection parameters you need/want to in run_autocontrol.sh. If you would like to run run_autocontrol.sh multiple times and have the data saved in the same folder, you can leave the folder name as the same (it will not overwrite previously existing data)

Make sure that the $wid, $amp, and $arduino_setting arrays are all the same length. Each index of these arrays will correspond to a run, which will need to have a pulse width, pulse amplitude, and arduino setting. $iteration_var is the number of times that the code will repeat these measurements. For example, if $iteration_var were 3, and $wid was ( 4 5 ), and amp was ( 1 2 ), and arduino setting was (7 8 ), the code will take a measurement at pulse width 4 ns, amplitude 1 V, and setting 7, and then a measurement at pulse width 5 ns, amplitude 2 V, and setting 8, and then a measurement at pulse width 4 ns, amplitude 2 V, and setting 7, and then a measurement at pulse width 5 ns, amplitude 2 V, and setting 8.

In general, be careful that changing certain properties of the pulse may influence the voltage range that you would want on the channel with the split LED signal, as well as the interval over which you would like the code to integrate the voltage signal. Properties of the signal pulse as well as the arduino setting may influence the light level of the LED, and then influence the number of PEs measured by the PMT, so you might have to then change the voltage range on the channel with the PMT, as well as the maximum number of PEs included in the summation for the charge distribution fit.
It can sometimes be a good idea to look at the log file after taking data, just becasue sometimes you might specify an invalid value for the voltage on the oscilloscope or on the signal generator, and the code will sometimes default to a different value. 

The valid voltage ranges for the oscilloscope are in the run_autocontrol.sh file. The signal generator has a maximum high level voltage of 5V when low level voltage is set to 0 V and the load is set to 50 ohms. (This means that valid values in the "$amp" array will include all numbers from 0 to 5). 
The arduino setting can be any whole number >= 1 and <=14. The distance from the center of the PMT to the LED is equal to 
(s-1)*0.5 inches
where s is the arduino setting.

PRODUCING YOUR OWN GRAPHS: 

If you are looking to make some graphs using the processed (or raw) data from a given run, edit the file ~/autocontrol/python_scripts/new_final10.py to produce the graphs that you want. 

If the data has already been taken, go use the file ~/autocontrol/python_scripts/test3.sh and change the names of the $processed_data_folder to match the processed_data folder for your data folder. ($check_mode=1 will allow you to view the graphs. If you are going to use $check_mode=1, and you are running the code remotely, make sure that X11 forwarding is working. If X11 forwarding won't work for whatever reason, then set $check_mode=0.)


SOME DEBUGGING STUFF:
-If the code stops running as a result of the signal generator not working, this is most likely solvable by turning the signal geneator off and then on, and then adjusting the parameters in run_autocontrol.sh so that you can take the remaining data. Leave the folder the same if you would like all of the data to be in the same folder (it will not rewrite the previous data). If this problem is not resolved by turning the signal generator off and then on, first make sure that the signal generator is connected to Ethernet. Then, check if the IP address on the signal generator matches the one in sig_gen.py and sig_gen2.py. Make sure that the port number in sig_gen.py and sig_gen2.py corresponds to the correct model of signal generator (this should be explained in the comments in sig_gen.py and sig_gen2.py). 
- If the code is just hanging when taking measurements, check the trigger level, since it is possible that the oscilloscope just isn't seeing any triggers with the trigger level specified.
- If all the fitted parameters from the charge distribution are NAN, that means that the fitter was unable to converge. The first thing to check if the fit is failing is most likely $num_pe in the run_autocontrol.sh file. The fit function involves a summation of the charge distribution of any given number n PEs. (Charge distribution of 0PEs would be a Gaussian centered roughly on 0, charge distribution of 1PE is a Gaussian with a tail centered on some non-zero charge, etc. and summing these all together makes the charge distribution.) The charge distributions of all charge distributions from 0 to $num_pe are summed to create this function, so if $num_pe is too low for the current light level, the fitter will be unable to work. You will want $num_pe to be higher than the average number of PEs for any given fit. Increasing $waveform_no can be useful in general and especially if the occupancy is very low. Changing the number of bins for the histogram can potentially change the fit, too. Make sure that $pmt_ch is set properly in the code as well.  
- Another note: getting fitted parameters from the charge distribution as NAN is sometimes OK. If you are measuring at very low occupancy, you will most likely get NAN parameters, which just means that estimating avg_pe using the charge distribution will not necessarily work well. Using occupancy can be a better method in this case. 
- If you accidentally delete a file in the raw_data directory, the code will probably get confused and begin to overwrite the last written file (It determines how many runs have been taken by the number of files in that directory, which also means that you will have issues with incorrect run numbers for each run if you add more files in the raw_data directory during or before running run_autocontrol.sh.
-If the code is taking a long time in between measurements, that may be a sign that it is having a hard time fitting the charge distribution. It might be worth looking at the charge distribution figures and seeing if the initial parameters are giving a reasonably close fit.  
-If you run the code from a different computer from the lab computer with $check_mode=1, you will receive an error if you do not have X-forwarding correctly set up. Either use $check_mode=0 when ssh-ing into the lab computer, or make sure that you have an X-forwarding client set up if you are not using a Linux computer. Make sure that the display number you use is 10 or higher. 

FILE DIRECTORIES: 

~/autocontrol/output_files:
All data is saved in output_files. There will be a folder corresponding to the folder name specified in the run_autocontrol.sh file, and inside that folder, there should be two directories, raw_data and processed_data. 

~/autocontrol/output_files/{my data folder here}/raw_data:
Inside raw_data, there will be a file for each set of waveforms. Each will be named "arduino_n_run_N.npy', where n corresponds to the arduino setting of the set of waveforms and N corresponds to the run number, which is basically a number that is is assigned from the number of sets of prior waveforms that were taken. (1 is the first set of waveforms taken, 2 is the second set of waveforms taken, etc.) Each one of these numpy files is a three-dimensional array. The organization of the numpy arrays is as follows: 

Dimension 0: 
Index 0: Time
Index 1-end: the channels that are enabled, in order. For example, if channel A and channel D were enabled (but channels B and C are not enabled), channel A would be index 1 since it is alphabetically first out of all the enabled channels, and channel D would be index 2 since it is alphabetically second out of all the enabled channels. The number of indicies in this dimension will depend on the number of enabled channels. 

Dimension 1: 
Each one of the indicies in this dimension will correspond to a number of a sample. For each waveform, there is a number of samples, at which the time relative to the trigger and the voltage is recorded. 

Dimension 2: 
The "number" of the waveform. For each run, there are a certain number of waveforms recorded. These are indexed chronologically. 

~/autocontrol/output_files/{my data folder here}/processed_data:
In the processed_data directory, there are several numpy files. One is named occupancy.npy. 

~/autocontrol/output_files/{my data folder here}/processed_data/occupancy.npy:
The information in occupancy.npy is as follows: 
Dimension 0: 
Each index in dimension 0 is an individual run (comprising several waveforms). 
Dimension 1: 
Index 0: Day/time at the beginning of the run
Index 1: Run number (starting at 1, corresponds to the number of runs taken before that given run
Index 2: Arduino setting
Index 3: Occupancy measured by counting the number of "hits" beneath a given voltage threshold (threshold set in run_autocontrol.sh)
Index 4: Number of waveforms in the run
Index 5: Number of times the voltage goes outside the oscilloscope voltage range (This feature is sort of iffy, and not very reliable, take it with a grain of salt...)
Index 6: Average integrated charge of PMT signal

~/autocontrol/output_files/{my data folder here}/processed_data/fit_param.npy:
Each of the values in fit_param.npy is from the fitter (except for the run number).
The information in fit_param.npy is as follows: 
Dimension 0: 
Each index in dimension 0 is an individual run (comprising several waveforms). 
Dimension 1:
Index 0: Run number 
Index 1: PE charge from fit (if the occupancy is high, or if the fit failed, this will be NAN)
Index 2: Standard deviation of the charge distribution of the 1 PE peak
Index 3: The charge of the 0PE peak (should be close to 0, but might be slightly offset.)
Index 4: The standard deviation of the charge distribution of the 0PE peak
Index 5: The average number of PEs from fit
Index 6: The ratio of exponential tail to Gaussian distribution for the charge distribution for >0PE, referred to as "R" (It may be helpful to refer to the slides that I sent to Jordan and Andy.)
Index 7: this is x0, which has been fitted by the fitter. It is a parameter that changes the length of the exponential tail(Here, it also may be helpful to refer to the slides that I sent to Jordan and Andy.)
Index 8: Uncertainty in PE charge from fit (index 1) (calculated from fitter)
Index 9: Uncertainty in 1 PE standard deviation (see index 2) (...)
Index 10: Uncertainty in charge of 0 PE peak (see index 3) (...)
Index 11: Uncertainty in 0PE standard deviation (see index 4) (...)
Index 12: Uncertainty in average number of PEs (see index 5) (...)
Index 13: Uncertainty in R (see index 6) (...)
Index 14: Uncertainty in x0 (see index 7) (...)

~/autocontrol/output_files/{my data folder here}/processed_data/led_v.npy:
The information in led_v.npy is as follows: 
Dimension 0: 
Each index is an individual run.
Dimension 1: 
Index 0: Average integrated LED charge (V)
Index 1: Median integrated LED charge (V)
Index 2: Standard deviation of integrated LED charge (V)
Index 3: Average LED peak (V)
Index 4: Average LED duration (ns)
Index 5: Median LED duration (ns)
Index 6: Standard deviation in LED duration (ns)
Index 7: The amplitude that the signal generator was set to (V)
Index 8: The pulse width that the signal geneartor was set to (ns)

~/autocontrol/output_files/{my data folder here}/processed_data/overflow.npy:
The information in overflow.npy is as follows: 
Dimension 0: 
Each index is an individual run (in chronological order).
Dimension 1: 
Each index is an individual waveform (in chronological order).

The value at any given point will be 0 if there is an overflow, and 1 if there is an overflow. I am not certain that this is very reliable. I think it sometimes says that there are overflows when there aren't. The documentation about the overflow array in the picoscope SDK guides feels very confusing to me, so there may be something wrong with the way that I am setting the overflow array in the script2.py file.


~/autocontrol/output_files/{my data folder here}/processed_data/signal:
In the processed_data directory, there is a directory called "signal". For each run, there is a .png file named the same way that the raw data files are. Each png file shows the signal trace of several waveforms. If the number of waveforms in a run exceeds the value of $plotting_lim in the run_autocontrol.sh file, there will be the first $plotting_lim number of waveforms plotted on top of each other. Otherwise, all the waveforms taken will be plotted on top of each other. For viewing a single signal trace, set $plotting_lim to 1 (or $waveform_no to 1). Unfortunately, plotting every individual signal trace in its own seperate saved graph might take up a lot of space (depending on the number of waveforms taken in a run). It is always possible to examine signal traces further by plotting the data in the files in the raw data directory. This code is in new_analysis5.py, and can always be modified further.  

~/autocontrol/output_files/{my data folder here}/processed_data/charge_distribution:
There is another directory called "charge_distribution". For each run, there is a .png file which is named the same way as the raw data files are. Each png file shows a charge distribution for each of the runs. The fitted charge distribution function is visible, as well as the charge distribution with the initial parameters (that is mainly there for debugging purposes). The charge distribution for certain individual numbers of PEs are also plotted. The individual PE charge distributions plotted vary based on the average PE. If the occupancy is low, the only individual charge distributions plotted might be for 0 through 5 PEs. If the average PE is close to 50, you will likely see the charge distribution for 45 through 55 PEs. However, the summed fitted function always includes all charge distributions from 0 to $num_pe, whether they are displayed on the graph or not. (It probably would be more computationally efficient if the code decided which charge distributions would be negligible based on the occupancy, instead of summing all from 0 to $num_pe.)
It's important to note that for high occupancies (>0.96), the fitter does not fit the 1 PE charge, and instead uses the value set in run_autocontrol.sh. This is because for high occupancies there is no 0PE peak that would anchor the charge of 1 PE, 2 PE, 3 PE with respect to one another, so allowing the fitter to determine the charge of 1 PE can cause issues. The box on the upper right shows values from the fit (as well as the number of bins used). If the occupancy is high, the value for PE charge will be set to the $pe_charge value in run_autocontrol.sh, and the uncertainty will display as NAN. 
In addition to the "arduino_n_run_N.png" files, there are several files named in this pattern "led_arduino_n_run_N.png". The n and N correspond to the same things they to in the naming pattern for the files named "arduino_n_run_N.png" (see the paragraph on the files in the "signal" folder.) These files have histograms of the integrated charge of the split LED signal. The channel with this signal can be specified in the $led_ch variable in the run_autocontrol.sh file. In the upper right, there is the average integrated charge, the median integrated charge, and the standard deviation of the charge. Unlike the histogram of the charge for the PMT signals, these parameters are not obtained through any kind of fit.

~/autocontrol/output_files/{my data folder here}/processed_data/led_duration:
There is another directory called "led_duration." (All these graphs follow the same naming convention as the ones in the "signal" folder) This directory has a series of figures that have the measured "duration" of the LED pulse versus the "waveform number". The waveform number corresponds to how many waveforms were taken before that waveform in the given run. The duration is the time length between when the pulse first reaches the trigger level going up and when it hits the trigger level going down. Duration is not the same measure as the width of the pulse listed on the oscilloscope, and it is definitely true that if you produce two different pulses with the same 'pulse width' but different amplitudes, the one with the greater amplitude will have a greater duration. This parameter was used to study a weird pattern where the pulse duration would sometimes go down with width (hopefully this is resolved by the time someone is reading this). These graphs will most likely appear as a series of horizontal lines, with about 0.1 ns in between each. Although the lowest time sampling interval the oscilloscope has is 2 ns, the code uses linear interpolation to estimate the duration. This is mainly done to avoid situations where there are so few samples that the code will see samples not along the pulse as being closer to the trigger level than samples along the pulse, leading to outlier points where the duration would be far off from what it really should be. (This may have something to do with the 2ns rise and fall time, meaning there are typically more samples at the top of the pulse and not on the pulse than there are in the transition upwards and downwards.) These graphs were produced to see if there was any transition in input duration, where it settled to a different value, although none was found. (It may have been better to have a graph of the cumulative average LED duration verus wavenumber, since it is difficult to tell exactly what is happening with so many points on top of one another.)

~/autocontrol/output_files/{my data folder here}/processed_data/led_duration_hist:
There is another directory called "led_duration_hist". (Again, each figure has the same naming convention as the ones in the signal folder.) This is a histogram of the measured LED duration values. You will notice a gap in between each of the histogram bars of about 0.1 ns (see previous paragraph for explanation). This is a better depiction of the ratio of LED durations found. It is a little clearer how many pulses correspond to any given LED duration, since a lot of points are overlapping in the graphs in "led_duration."

~/autocontrol/output_files/{my data folder here}/processed_data/led_peak:
There is another directory called "led_peak". (These graphs have the same naming convention as the ones in signal folder.) Each figure is a figure of the peak voltage measured on the split signal versus the waveform number, which just corresponds to the chronological order which the waveforms were taken. The peak voltage is just the maximum measured voltage on the channel $led_ch set in the run_autocontrol.sh file for each waveform. These graphs were made for a similar reason as the led_duration graphs, to see if anomalous signal geneator pulses slowly settled into a more normal shape. These graphs will also most likely appear as a series of straight horizontal lines, where the voltage in between each line is the resolution on the oscilloscope (which depends on the voltage range set).

~/autocontrol/output_files/{my data folder here}/processed_data/led_peak:
There is another directory called "led_peak_hist." (These graphs also have the same naming convention as the ones in the signal folder.) These figures are histograms of the LED peak voltage. See previous paragraphs for a bit more explanation on how LED peak voltage is calculated.

~/autocontrol/autocontrol_log:
Outside of the output_files folder, there is a folder called "autocontrol_log." This folder contains the log file for each run of this code. It can be worth it to check in on the code while it is running or afterwards by looking at the log file for your run of the code.

~/autocontrol/notes/notes0.txt:
This file contains notes on the optical density filter, HV voltage connected to the PMT, and any other notes on a given folder of data. The earliest data folders mentioned are likely on the blue Samsung 2TB hard drive in the lab, and may also be backed up to pa-pub.umd.edu. All of the earliest data folders are taken without a neutral density filter. I have used this file mainly to write about data that I have used for something, so some of the data that has not been used may not be included in this file.

~/autocontrol/notes/script_notes.txt:
This has some notes on the python code files. Most of the files mentioned are out-of-date.

~/autocontrol/notes/filter.txt: 
This is just a note to myself about how the naming for the optical density filters works.

~/autocontrol/python_scripts: 
This folder contains all of the python scripts including the ones that are out-of-date, as well as some files that are not python scripts. Some information on some of the out-of-date files may be found in ~/autocontrol/notes/script_notes.txt. To find out which of these scripts are being currently used for what, go to ~/autocontrol/autocontrol.sh and read the file names for that are set for $script_name, $analysis_name, $final_name, $sig_gen_name, and $off_script. The comments should describe what each of these files do. 
~/autocontrol/python_scripts/do_not_delete.txt is a file containing a zero or an one. Each time that the code to run the signal generator is used, this file is initialized to a 1, and it becomes a 0 if connecting to the signal generator fails. Once it turns to a 0, the code is stopped. Please do not delete this file.
To find more information on some of the files in this folder, read under the header "Re-running Analysis Scripts on Existing Data."

~/autocontrol/sketchbook: 
This directory contains all the files that are used to control the Arduino. Arduino.mk is the package that is used to compile and run Kristi's code (~/autocontrol/sketchbook/10-inch_Calibration_half-in.ino) outside of the Arduino IDE. For more information on controlling the Arduino, read under the header "Controlling Arduino Through Command Line/Arduino IDE." 
~/autocontrol/sketchbook/arduino_log is a logfile which has the output from the Arduino. This is wiped at the beginning of each new run of run_autocontrol.sh. 
~/autocontrol/sketchbook/libraries is a directory with Arduino libraries needed to compile Kristi's code. 
If the Arduino is for any reason replaced with a different Arduino with a different model, the BOARD_SUB and BOARD_TAG variables in ~/autocontrol/sketchbook/Makefile should be updated. This file also specifies the libraries used, and some options for the instance of screen that the serial communication with the Arduino occurs on.
~/autocontrol/sketchbook/libraries contains the Servo library, which is needed to run Kristi's code. 

~/autocontrol/data_files: 
This is a directory of data files that are not taken by this program. (For purposes of comparing my results to some of these files.
~/autocontrol/data_files/Azimuth{1, 2, 3, or 4} or raw_responses:
These are data files that Kristi took. The pulses were taken with a mercury switch at 60 Hz.

~/autocontrol/temperature
This is a directory with .xls files with temperature and humidity measurements verus time (taken with the Elitech temperature and humidity logger in the lab). There used to be some speculation that some specific issues with instability of the system (ie. measuring drastically different occupancies with the LED pulser set to the same voltage) was related to temperature. It turned out that it was not strongly correlated, and most likely related to the old mercury switch being used. 


CHECK_MODE VARIABLE IN RUN_AUTOCONTROL.SH FILE:
Check mode will cause the code to display graphs after every data collection "run" (each set of $waveform_no waveforms), as well as running almost all python scripts interactively. It requires constant intervention (manually closing the graphs and typing "exit()" to leave interactive mode so that the program can continue). It gives the user the option to retake data, which can be handy if you are messing with the equipment and just want to see if something changes the data, or if you are only observing the behavior of the runs, or sometimes if you are trying to debug the code, and you want to change different parts of the analysis script and rerun the whole thing and see if it works without having to save more data than you need to. It does have this bug where it often shows the user a set of graphs twice. 
An important note: if you are ssh-ing into juici and you want to run the code with check_mode=1, make sure that X11 forwarding works first using 'xeyes' or something. The code will just not work otherwise.
It's sort of clunky (there are a lot of graphs that appear on your screen), but sometimes handy, especially since I can access all the variables through interactive mode. 
It might be useful to note that the graphs that are displayed in check_mode can be just as easily monitored without check_mode by just using "feh" on the graphs in processed_data during data collection, since they are continuously updated while the data is being taken.


IF YOU HAVE ANY QUESTIONS: Please contact me at jcottin1@terpmail.umd.edu or julia.cottingham@comcast.net.




