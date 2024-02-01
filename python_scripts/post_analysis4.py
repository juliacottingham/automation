import sys 
check_mode=0
try:
    
    import matplotlib as mlt
    if check_mode:
        mlt.use('TkAgg') 
    else: 
        mlt.use('Agg')
    
    import matplotlib.pyplot as plt
    import os 
    import re
    import numpy as np
    import numpy.ma as ma
    import scipy.integrate as integral
    import scipy.optimize as op
    import scipy.constants as con
    import scipy.special as special
    import datetime
except: 
    print('Please activate pmt_env virtual environment before running')
    sys.exit()

#plt.ioff()
#NOTE TO SELF MAKE THESE VARIABLES EDITABLE IN THE RUN_AUTOCONTROL FILE
color_list=np.array(['blue', 'magenta', 'purple', 'green'])
#integrated charge of (mV*ns) divided by 50 ohm impedance for pC units


data_dir='/home/labwork/autocontrol/output_files/led_v_curve5/raw_data'
check_mode=0
pmt_ch = 0
led_ch= 2
ch_enable=np.array([True, False, True, False])
#setting=sys.argv[8]
analysis_path='/home/labwork/autocontrol/output_files/led_v_curve5/processed_data'

t_int=np.array([0,50])
t_int2=np.array([-50, 10])
v_th=-4
int_width=20
bins=50
unit_factor=1/50
plotting_lim=20
num_pe=150
digits=2
font_size=6
signal_folder='signal' 
charge_dist_folder='charge_distribution'
led_ch=2
fit_param_file='fit_param.npy'

def sci(number): 
    ret=np.empty(number.shape, dtype='U100')
    iterate=np.ndindex(number.shape)

    for w in iterate: 
        ret[w]=str(format(number[w], '.' + str(digits) + 'E'))
    return ret 

def poisson(avg, num): 
    return np.array([((avg**n)*np.exp(-avg)/np.math.factorial(n)) for n in num])

def norm(x, avg, stdev, R): 
    return (1/(stdev*np.sqrt(2*con.pi)))*np.exp((-0.5)*(((x-avg)/stdev)**2))*(1-R)

def tail(x, x0, R): 
    return (R/x0)*(np.exp(-x/x0))

def norm_tail(x, avg, stdev, h, R, x0): 
    arr=np.array([norm(x, avg, stdev, R), tail(x, x0, R)])*h
    return arr 

def erf(x, width, avg, stdev, R): 
    
    t_f=((x+width-avg)/(np.sqrt(2)*stdev))
    
    t_i=(x-width-avg)/(np.sqrt(2)*stdev)

    erf_val=special.erf(t_f)-special.erf(t_i)

    return (1-R)*erf_val/2

def exp_int(x, width, x0, R): 

    exp_f=np.exp(-(x-width)/x0)

    exp_i=np.exp(-(x+width)/x0)

    return R*(exp_f-exp_i)

def norm_tail_int(x, width, avg, stdev, h, R, x0): 
    arr=np.array([erf(x, width, avg, stdev, R), exp_int(x, width, x0, R)])*h
    return arr

def norm_tail_int_seperate(x, width, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H):
    pe_arr=np.arange(0, num_pe+1, 1)
    r_arr=np.full(num_pe+1, R)
    r_arr[0]=0
    avg_arr=np.array([zero_ch, *(pe_ch*pe_arr[1:])])
    stdev_arr=np.array([zero_stdev, *(pe_stdev*np.sqrt(pe_arr[1:]))])
    area=poisson(avg_pe_fit, pe_arr)*H
    
    x_arr=np.expand_dims(x, axis=-1)

    y=norm_tail_int(x_arr, width, avg_arr, stdev_arr, area, r_arr, x0)
    y=np.moveaxis(y, (0, 1, 2), (1, 2, 0))
    
    #condition= ((zero_ch - zero_stdev) < x) & ( x< (zero_ch + zero_stdev))
    #y[0, :, condition]=(area[0]/(zero_stdev*2))
    #y[0, :, ~condition]=0
    #y[0]=np.choose(condition, [ area/(zero_stdev*2), 

    y[1:, :, x<0.2]=0
    return y 

def norm_tail_int_sum(x, width, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H): 
    k=norm_tail_int_seperate(x, width, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H)
    return np.sum(k, axis=(0, 1))


def norm_tail_seperate(x, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H):
    pe_arr=np.arange(0, num_pe+1, 1)
    r_arr=np.full(num_pe+1, R)
    r_arr[0]=0
    avg_arr=np.array([zero_ch, *(pe_ch*pe_arr[1:])])
    stdev_arr=np.array([zero_stdev, *(pe_stdev*np.sqrt(pe_arr[1:]))])
    area=poisson(avg_pe_fit, pe_arr)*H
    
    x_arr=np.expand_dims(x, axis=-1)
    
    y=norm_tail(x_arr, avg_arr, stdev_arr, area, r_arr, x0)
    y=np.moveaxis(y, (0, 1, 2), (1, 2, 0))
    
    condition= ((zero_ch - zero_stdev) < x) & ( x< (zero_ch + zero_stdev))
    y[0, :, condition]=(area[0]/(zero_stdev*2))
    y[0, :, ~condition]=0
    #y[0]=np.choose(condition, [ area/(zero_stdev*2), 

    y[1:, :, x<0.2]=0
    return y 


def norm_tail_sum(x, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H): 
    k=norm_tail_seperate(x, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H)
    return np.sum(k, axis=(0, 1))

#data_list=os.listdir(data_dir)

bin_factor=1

ch=np.array([0, 1, 2, 3])
led_no=np.where(ch[ch_enable]==led_ch)[0][0]+1

bin_init=len(os.listdir(data_dir))
bin_final=int(bin_init/bin_factor)


for e in range(bin_final):
    #data_loc_list=os.listdir(data_dir)[e*bin_factor:(e+1)*bin_factor]
    

    data_loc_list=np.empty(bin_factor)
    data_list=np.empty(bin_factor, dtype=object)
    run_no_list=np.empty(bin_factor, dtype=int)
    for z in range(bin_factor): 
        run_no_list[z]=int(e*bin_factor + 1+ z)
        data_loc='arduino_1_run_' + str(run_no_list[z]) + '.npy'
        #b=re.sub(r'^arduino_', '', data_loc)
        #c=re.sub(r'_run\w+\.npy', '', b)

        #d=re.sub(r'^\w+\_run_', '', b)
        #f=re.sub(r'.npy', '', d)

        print(data_loc)
    
        #run_no_list[z]=int(f)
        #print(run_no)
        #index=run_no%(arduino_setting_arr.size)
        data_list[z]=np.load(data_dir +'/' + data_loc)
        arduino_setting=1
        #NOTE: will not work if the arduino setting changes
    
    run_no=int(np.average(run_no_list))
    print(run_no)
    print(arduino_setting)
    data=np.concatenate(data_list, axis=2)
    signal=np.stack([data[0], data[pmt_ch+1]], axis=0)

    #np.random.shuffle(data_list)

    ch_no=data.shape[0]-1

    waveform_no=signal.shape[2]
    condition0=((t_int[0] < signal[0]) & (signal[0]<t_int[1]))
    
    signal[1, ~np.isfinite(signal[1])]=np.min(signal[1, np.isfinite(signal[1])])
    signal[1, ~condition0]=0
    peak_index=signal[1].argmin(axis=0)
    
    closest_index=np.argmin(np.abs(data[led_no][data[0, :, 0]<-20] -1500), axis=0)
    grid2=np.ix_(*[np.arange(g) for g in data.shape[0:]])	
    grid=np.ix_(*[np.arange(s) for s in signal.shape[-1:]])
    closest_t=data[(0, *((closest_index,) + grid))]
    led_duration=-closest_t
    avg_led_duration=np.average(led_duration)
    med_led_duration=np.median(led_duration)
    std_led_duration=np.std(led_duration)

    peak_t=signal[(0, *((peak_index,) + grid))]
    int_lim=[peak_t - int_width, peak_t + int_width]

    condition2=((int_lim[0] < signal[0]) & (signal[0] < int_lim[1]))
    #condition2=np.stack([condition2, condition2], axis=0)

    #signal_int=ma.array(signal_ma, mask=~condition2)
    #signal_int[condition2]=0
    #signal_int[~condition2]=signal_ma.data[~condition2
    #signal_int_arr=np.empty(signal_int.shape)
    #signal_int_arr[~signal_int.mask]=signal_int.data[~signal_int.mask]
    #signal_int_arr[signal_int.mask]=0
    
    signal[1, ~condition2]=0
    	
    condition3=((t_int2[0] < signal[0]) & (signal[0]<t_int2[1]))
    led_v_integral=data[led_no]
    led_v_integral[~condition3[:, 0]] = 0
    
    
    charge=integral.trapezoid((-1)*signal[1], signal[0], axis=0)*unit_factor
    #charge.set_fill_value(0)
  
    led_charge=integral.trapezoid(led_v_integral, signal[0], axis=0)*unit_factor
    avg_led_charge=np.average(led_charge)
    med_led_charge=np.median(led_charge)
    std_led_charge=np.std(led_charge)
    
    avg_led_peak= np.average(np.max(data[led_no], axis=0))
   
    #diff_arr=np.abs(data[led_no]+70) 
    #i=np.argmin(diff_arr, axis=0)[0]    
    
    #start_time=data[0][condition4][0]
    pmt_count=np.sum((np.min(signal[1], axis =0)) < v_th)

    occupancy=pmt_count/waveform_no

    print('Occupancy found to be ' + str(occupancy))

    count0, bin_lim = np.histogram(charge, bins)
    width=bin_lim[1]-bin_lim[0]
    
    bin_center0=(bin_lim+(width/2))[:-1]
    
    hist_range_fraction=(bin_center0[-1]-bin_center0[0])*0.1

    new_bins=int(0.1*bins)

    bin_center=np.arange(bin_center0[0]-new_bins*width, bin_center0[-1] + new_bins*width, width)

    count=np.zeros(bin_center.shape)
    count[(bin_center>bin_lim[0]) & (bin_center<bin_lim[-1])]=count0
    
    """
    if occupancy == 1: 
        avg_pe_guess=3
    else: 
        
        avg_pe_guess=-np.log(1-occupancy)
    """
    pe0=0
    pe1=2.65
    avg_pe_guess=np.average(charge)/pe1
    
    bin_center1=bin_center[bin_center>0.25]
    count1=count[bin_center>0.25]

    #h_guess=sum(count)*width;
    h_guess=1
    #pe1=bin_center1[np.argmax(count1)]
    #pe0=bin_center[np.argmax(count)]
    count=count/sum(count)
    #bounds0=((0, max(charge)), (0, np.inf), (-1, max(charge)), (0, np.inf), (0, np.inf), (0, 1), (0, np.inf), (0, np.inf))
    #lower_bound=np.array([0.05, width, -1, width/20, 0, 0, 0.01, 0.8*h_guess])
    #upper_bound=np.array([1.5*pe1, max(charge)-min(charge), 0.3*pe1, max(charge)-min(charge), np.inf, 0.5, 10, 1.2*h_guess])
    lower_bound=np.array([0.75*pe1, 0, -0.5, 0, -np.inf, 0.001, 0.1, 0])
    upper_bound=np.array([1.25*pe1, np.inf, 0.5, 0.5, np.inf, 0.9, 10, np.inf])
    param0=np.array([pe1, 0.9, pe0, 0.12, avg_pe_guess, 0.01, 2.3, h_guess])

   
    #def norm_tail_int_sum(x, width, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H): 
    int_func = lambda x, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H: norm_tail_int_sum(x, width/2, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H) 
    
    popt, pcov = op.curve_fit(int_func, bin_center, count, p0=param0, bounds=(lower_bound, upper_bound), loss='soft_l1', maxfev=50000)
    sig_popt=np.sqrt(np.diag(pcov))
    #overall_num=bin_lim[-1]-bin_lim[0]
    #x=np.arange(bin_lim[0] - 0.1*overall_num, bin_lim[-1] + 0.1*overall_num, width/10)

    x=np.arange(bin_center[0], bin_center[-1], width/10)
    sum_fit=norm_tail_int_sum(bin_center, width/2, *popt)
    part_of_fit = norm_tail_int_seperate(bin_center, width/2, *popt)
    init_fit=norm_tail_int_sum(bin_center, width/2, *param0)
    

    
    title0='Oscilloscope Output'

    if data.shape[2]>plotting_lim: 
        index=plotting_lim
        title0 += ' (first ' + str(plotting_lim) + ' waveforms)'
    else:
        index=data.shape[2]

    
    title0 += ' for setting ' + str(arduino_setting)

    fig, ax = plt.subplots()
    handle=np.empty(ch_no, dtype='object')
    label=np.full(ch_no, 'Channel ', dtype='U100') 

    n=0
    for y in range(len(ch_enable)):
        if int(ch_enable[y]):
            i=y+1
            label0=chr(ord('@') + i)
            if y == pmt_ch: 

                label0 += ' (PMT signal)'

            label[n]+=label0
            handle0 = ax.plot(data[0, :, 0], data[n+1, :, :index], color=color_list[n])
            handle[n] = handle0[0]
            n=n+1

    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Voltage (mV)')
    ax.set_title(title0)
        #plt.legend()
    ax.legend(handle, label)
    #plt.savefig(analysis_path + '/' + signal_folder + '/' + file_name + '.png')
    
    fig1, ax1= plt.subplots()
    plt.stairs(count0/sum(count0), bin_lim)
    plt.plot(bin_center, sum_fit, label='Fit Function')
    plt.plot(bin_center, init_fit, label='Initial Fit Parameters')

    for j in range(part_of_fit.shape[0]): 
        
        label1= str(j) + ' PE'

        for k in range(part_of_fit.shape[1]):

            if k==0: 
                label2= ' normal distribution' 
            else: 
                label2= ' tail'

            
            plt.plot(bin_center, part_of_fit[j, k], label= label1+ label2)  

    #plt.plot(x, norm_fit)
    #plt.plot(x, tail_fit)
    plt.title('Charge Distribution for Arduino Runs' + str(run_no_list[0]) + '-' + str(run_no_list[-1]))
    plt.xlabel('Charge (pC)')
    plt.ylabel('Counts')
    #plt.legend(loc='lower right', fontsize=font_size)
    
    
    param_text=mlt.offsetbox.AnchoredText('PE Charge= ' + str(sci(popt[0])) + '\n1PE Stdev= ' + str(sci(popt[1])) + '\n0PE Charge= ' + str(sci(popt[2])) + '\nZero Stdev= ' + str(sci(popt[3])) + '\nAverage PE= ' + str(sci(popt[4])) + '\nR= ' + str(sci(popt[5])) + '\nx0= ' + str(sci(popt[6])) + '\nIntegration Area= ' + str(sci(popt[7])) + '\nBins= ' + str(bins), loc=1, prop=dict(fontsize=font_size))  


    ax1.grid()
    ax1.add_artist(param_text)
    plt.tight_layout()
    #plt.show()
    plt.savefig(analysis_path + '/' + charge_dist_folder + '/arduino_1_sets' + str(run_no_list[0]) + '-' + str(run_no_list[-1]) + '.png')
    
    fig2, ax2 = plt.subplots()
    plt.hist(led_charge, bins=40) 
    

    param_text2=mlt.offsetbox.AnchoredText('Mean Charge = ' + str(sci(avg_led_charge)) + '\nMedian Charge = ' + str(sci(med_led_charge)) + '\nStandard Deviation = ' + str(sci(std_led_charge)), loc=1, prop=dict(fontsize=font_size))
    ax2.add_artist(param_text2)
    plt.tight_layout()	
    plt.title('LED Charge Distribution')
    plt.xlabel('Charge (pC)')
    plt.ylabel('Fractional Count')
    plt.savefig(analysis_path + '/' + charge_dist_folder + '/' + 'led_1_' + str(run_no_list[0]) + '-' + str(run_no_list[-1]) + '.png')
    gain=(popt[0]/con.e)*(10**(-12))
    occupancy_fit=1-np.exp(-popt[4])

    #time_array=np.array([str(run_no), current_time])
    #current_time0=" ".join(f for f in current_time)
    #occupancy_array=np.array([current_time0, run_no, arduino_setting, occupancy, waveform_no])[np.newaxis, :]
    popt_array=np.array([run_no, *popt, *sig_popt])[np.newaxis, :]
    led_v_array=np.array([run_no, avg_led_charge, med_led_charge, std_led_charge, avg_led_peak, avg_led_duration, med_led_duration, std_led_duration])[np.newaxis, :]
    if e != 0:
        #occupancy_array2=np.load(analysis_path+ '/' + occupancy_file)
        popt_array2=np.load(analysis_path + '/' + fit_param_file)
        led_v_array2=np.load(analysis_path + '/led_v.npy')
        
        #if popt_array2.shape[0] == run_no: 
            #occupancy_array2[run_no-1, :] =occupancy_array
            #occupancy_array=occupancy_array2

            #popt_array2[run_no-1, :]=popt_array
            #popt_array=popt_array2
       
            #else:
            #occupancy_array=np.concatenate([occupancy_array2, occupancy_array])
        
        popt_array=np.concatenate([popt_array2, popt_array])
        led_v_array=np.concatenate([led_v_array2, led_v_array])
    #np.save(analysis_path+'/'+occupancy_file, occupancy_array)
    np.save(analysis_path + '/' + fit_param_file, popt_array)
    np.save(analysis_path + '/led_v.npy', led_v_array)
    #plt.show()
        
    if check_mode:
        print('Average PE found: ')
        print(sci(popt[4]))
        print('+-')
        print(sci(sig_popt[4]))
        print('Calculated occupancy from that') 
        print(sci(occupancy_fit))
        print('Uncertainty in calculated occupancy')
        print(sci(np.exp(-popt[4])*sig_popt[4]))
        #print('Gain is calculated to be ' + str(sci(gain)))
        #print('Occupancy (from fit) is calculated to be ' + str(occupancy))

        plt.show()
