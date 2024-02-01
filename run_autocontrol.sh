#run_autocontrol.sh 
#adjust the parameters below and run in order to get measurements

iteration_var=1            #number of times to iterate the set of measurements  

wid=( 10 )                 #array of pulse widths (ns)
amp=( 5 )                  #array of pulse amplitudes (V)
arduino_settings=( 1 )     #array of arduino settings (number from 1-14)

#wid=($(seq 5 9 0.1)) #sets the widths to a series of values from 5 to 9 ns, evenly spaced by 0.1 ns                                                                      
#amp=($(for i in $(seq ${#wid[@]}); do echo 3; done)) #keeps the amplitude at 3V               
#arduino_settings=($(for i in $(seq ${#wid[@]}); do echo 1; done)) #keeps the arduino set at 1 

check_mode=0               #normally 0, only use 1 for debugging (see README.md for more details)

folder_name='code_test2'   #folder name for saving data 
log_file='code_test2.txt'  #name of log file  

pmt_ch=0                   #0 is CH_A, 1 is CH_B, 2 is CH_C, 3 is CH_D
led_ch=2                   #channel w split signal from box

freq=100000                #Hz
waveform_no=50000          #number of waveforms for each arduino/signal generator setting
sample_no=200              #number of time/voltage measurements (samples) per waveform
sample_int=2               #time interval between each sample (ns)

tr_ch='CH_C'               #channel to trigger on
pre_tr=0.4                 #fraction of samples taken before the trigger
th_v=100                   #threshold voltage for triggering waveform in mV
tr_dir='falling'           #trigger direction for triggering waveform
downsampling='none'        #downsampling method for oscilloscope
ch_enable=(1 0 1 0)        # (ch A, ch B, ch C, ch D) 0 is disabled, 1 is enabled
mv_range=(100 50 500 2000) #voltage range for each channel (CH A, CH B, CH C, CH D)
                           #Valid voltage ranges: 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000 mV. 

t_int=( -20 50 )           #time window where PMT signals are "counted" towards occupancy (ns) 
led_t_int=( -20 10 )       #LED voltage is integrated over this time interval to get charge (ns)

v_th=-3                    #threshold for PMT signal to be counted (occupancy)
width=19                   #integration time for PMT signal (14ns before peak, 14ns after)
bins=50                    # no. of bins for histogram 
unit_factor=0.02           #(impedance in ohms)^(-1)
plotting_lim=50 	   #max no. of signal traces plotted on the same plot
num_pe=100                 #highest PE no. included in Poisson distribution 
digits=2                   #number of digits for numbers shown in figures
font_size=6                #font size on graph for fitted parameters of charge distribution

pe_charge=2.213            #pe charge in pc (see README for more info)

#--------------------------some initial parameters for charge distribution fit-----
std0_guess=0.009           #initial parameter for stdev of 0PE
std1_guess=0.87            #initial parameter for stdev of 1PE

#--------------------------upper bounds on parameters for charge distribution fit---
std0_lim=0.1               #upper limit for stdev of 0PE
std1_lim=0.95              #upper limit for stdev of 1PE
pe0_lim=0.5                #upper limit for charge of 1PE




if [ $check_mode == 1 ]; then
	./autocontrol.sh ${ch_enable[@]} ${mv_range[@]} $waveform_no $sample_no $sample_int $pre_tr $downsampling $tr_ch $th_v $tr_dir $folder_name $check_mode $pmt_ch $led_ch $freq ${t_int[@]} ${led_t_int[@]} $v_th $width $bins $unit_factor $plotting_lim $num_pe $digits $font_size $iteration_var $pe_charge $std0_guess $std1_guess $std0_lim $std1_lim $pe0_lim ${arduino_settings[@]} ${amp[@]} ${wid[@]}
else 	 
	./autocontrol.sh ${ch_enable[@]} ${mv_range[@]} $waveform_no $sample_no $sample_int $pre_tr $downsampling $tr_ch $th_v $tr_dir $folder_name $check_mode $pmt_ch $led_ch $freq ${t_int[@]} ${led_t_int[@]} $v_th $width $bins $unit_factor $plotting_lim $num_pe $digits $font_size $iteration_var $pe_charge $std0_guess $std1_guess $std0_lim $std1_lim $pe0_lim ${arduino_settings[@]} ${amp[@]} ${wid[@]} &>>"autocontrol_log/$log_file" &
fi

