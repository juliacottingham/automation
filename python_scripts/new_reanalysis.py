#this script analyzes any one numpy file of waveforms and determines occupancy from a threshold and from a charge distribution

import sys 

#determine check_mode first since that determines the matplotlib backend needed
check_mode=int(sys.argv[2])

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

color_list=np.array(['blue', 'magenta', 'purple', 'green'])

data_loc=sys.argv[1]
check_mode=int(sys.argv[2])
pmt_ch = int(sys.argv[3])
led_ch=int(sys.argv[4])
ch_enable=np.array(sys.argv[5:9]).astype(bool)
setting=sys.argv[9]
analysis_path=sys.argv[10]

t_int=np.array(sys.argv[11:13]).astype(float)
led_t_int=np.array(sys.argv[13:15]).astype(float)
v_th=float(sys.argv[15])
int_width=float(sys.argv[16])
bins=int(sys.argv[17])
unit_factor=float(sys.argv[18])
plotting_lim=int(sys.argv[19])
num_pe=int(sys.argv[20])
digits=int(sys.argv[21])
font_size=float(sys.argv[22])
signal_folder=sys.argv[23] 
charge_dist_folder=sys.argv[24]
file_name=sys.argv[25]
arduino_setting=int(sys.argv[26])
run_no=int(sys.argv[27])
occupancy_file=sys.argv[28]
fit_param_file=sys.argv[29]
v_set=sys.argv[30]
wid_set=sys.argv[31]
pe_charge=float(sys.argv[32])
overflow_file=sys.argv[33]

tr_dir=sys.argv[34]
tr_v=float(sys.argv[35])

std0_guess=float(sys.argv[36])
std1_guess=float(sys.argv[37])

std0_lim=float(sys.argv[38])
std1_lim=float(sys.argv[39])

pe0_lim=float(sys.argv[40])

current_time=sys.argv[41:]
#fit_param_file='fit_param.npy'

def sci(number): 
    ret=np.empty(number.shape, dtype='U100')
    iterate=np.ndindex(number.shape)

    for w in iterate: 
        if number[w]==np.nan: 
            ret[w]='NAN'
        else:
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

def norm_tail_int(x, width, avg, stdev, R, x0): 
    arr=np.array([erf(x, width, avg, stdev, R), exp_int(x, width, x0, R)])
    return arr

def norm_tail_int_seperate(x, width, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0):
    pe_arr=np.arange(0, num_pe+1, 1)
    r_arr=np.full(num_pe+1, R)
    r_arr[0]=0
    avg_arr=np.array([zero_ch, *(pe_ch*pe_arr[1:])])
    stdev_arr=np.array([zero_stdev, *(pe_stdev*np.sqrt(pe_arr[1:]))])
    area=poisson(avg_pe_fit, pe_arr)
    
    x_arr=np.expand_dims(x, axis=-1)

    y=norm_tail_int(x_arr, width, avg_arr, stdev_arr, r_arr, x0)*area
    y=np.moveaxis(y, (0, 1, 2), (1, 2, 0))
    
    #condition= ((zero_ch - zero_stdev) < x) & ( x< (zero_ch + zero_stdev))
    #y[0, :, condition]=(area[0]/(zero_stdev*2))
    #y[0, :, ~condition]=0
    #y[0]=np.choose(condition, [ area/(zero_stdev*2), 

    y[1:, :, x<0.2]=0
    return y 

def norm_tail_int_sum(x, width, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0): 
    k=norm_tail_int_seperate(x, width, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0)
    return np.sum(k, axis=(0, 1))

def alt_fit(x, avg_pe_fit, std): 
    R=1
    avg=pe_charge*avg_pe_fit
    return norm(x, avg, std, R)
   
data=np.load(data_loc + '.npy')

signal=np.stack([data[0], data[pmt_ch+1]], axis=0)
ch_no=data.shape[0]-1
ch=np.array([0, 1, 2, 3])
led_no=np.where(ch[ch_enable]==led_ch)[0][0] + 1
#print("Here is the index of led (should equal 3)!!")
#print(str(led_no))

waveform_no=signal.shape[2]
condition0=((t_int[0] < signal[0]) & (signal[0]<t_int[1]))

overflow_arr=np.load(overflow_file)[run_no-1]

overrange_count=np.sum(overflow_arr)
print("Overrange count: " + str(overrange_count))

signal[1, ~np.isfinite(signal[1])]=np.min(signal[1, np.isfinite(signal[1])])
signal[1, ~condition0]=0
peak_index=signal[1].argmin(axis=0)

if tr_dir=='falling':
    closest_index=np.argmin(np.abs(data[led_no][data[0, :, 0]<-4] - tr_v), axis=0)
else: 
    closest_index=np.argmin(np.abs(data[led_no][data[0, :, 0]>4] - tr_v), axis=0)
    closest_index=closest_index+data[led_no][data[0, :, 0]<4].shape[0]
grid2=np.ix_(*[np.arange(g) for g in data.shape[0:]])	
grid=np.ix_(*[np.arange(s) for s in signal.shape[-1:]])
closest_t=data[(0, *((closest_index,) + grid))]

if tr_dir=='falling':
    led_duration=-closest_t
    print('This is led duration!!!')
    print(led_duration)
else: 
    led_duration=closest_t

avg_led_duration=np.average(led_duration)
med_led_duration=np.median(led_duration)
std_led_duration=np.std(led_duration)

peak_t=signal[(0, *((peak_index,) + grid))]
int_lim=[peak_t - int_width, peak_t + int_width]

condition2=((int_lim[0] < signal[0]) & (signal[0] < int_lim[1]))
signal[1, ~condition2]=0

#condition3=((t_int2[0] < signal[0]) & (signal[0]<t_int2[1]))

condition3=((led_t_int[0] < signal[0]) & (signal[0]<led_t_int[1]))

led_v_integral=data[led_no]
#led_v_integral[~condition3[:, 0]] = 0


charge=integral.trapezoid((-1)*signal[1], signal[0], axis=0)*unit_factor
#charge.set_fill_value(0)

led_charge=integral.trapezoid(led_v_integral, signal[0], axis=0)*unit_factor
avg_led_charge=np.average(led_charge)
med_led_charge=np.median(led_charge)
std_led_charge=np.std(led_charge)

avg_led_peak= np.average(np.max(data[led_no], axis=0))

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

print('This is the occupancy: ' + str(sci(occupancy)))

if occupancy > 0.96: 
    avg_pe_guess=np.average(charge)/pe_charge
    high_occupancy=True
    print('High occupancy!!')
else: 
    avg_pe_guess=-np.log(1-occupancy)
    high_occupancy=False
    print('Not high occupancy!')

bin_center1=bin_center[bin_center>0.25]
count1=count[bin_center>0.25]

#h_guess=sum(count)*width;
h_guess=1
#pe1=bin_center1[np.argmax(count1)]

pe1=2.5
pe0=0
count=count/sum(count)
#bounds0=((0, max(charge)), (0, np.inf), (-1, max(charge)), (0, np.inf), (0, np.inf), (0, 1), (0, np.inf), (0, np.inf))
#lower_bound=np.array([0.05, width, -1, width/20, 0, 0, 0.01, 0.8*h_guess])
#upper_bound=np.array([1.5*pe1, max(charge)-min(charge), 0.3*pe1, max(charge)-min(charge), np.inf, 0.5, 10, 1.2*h_guess])
if high_occupancy: 
    
    int_func = lambda x, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0: norm_tail_int_sum(x, width/2, pe_charge, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0) 

    param0=np.array([std1_guess, pe0, std0_guess, avg_pe_guess, 0.2, 0.1])
    lower_bound=np.array([0, -pe0_lim, 0, -np.inf, 0, 0.04])
    upper_bound=np.array([std1_lim, pe0_lim, std0_lim, np.inf, 1, np.inf])


else:
    
    int_func = lambda x, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0: norm_tail_int_sum(x, width/2, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0) 
    param0=np.array([pe1, std1_guess, pe0, std0_guess, avg_pe_guess, 0.2, 0.1])
    
    lower_bound=np.array([0, 0, -pe0_lim, 0, -np.inf, 0, 0.04])
    upper_bound=np.array([3*pe1, std1_lim, pe0_lim, std0_lim, np.inf, 1, np.inf])


condition1=param0>lower_bound
condition2=param0<upper_bound

combined_condition=condition1 & condition2

param0=np.choose(combined_condition, [0.5, param0])


combined_condition=condition1 & condition2
#redo once param0 are assigned again. if statement below just in case bounds are changed so that 0.5 no longer works as a number safely within the bounds

fit_success=True

if np.all(combined_condition):
    try:    
        print('Fitting...')
        
        popt=np.full(param0.shape, np.nan)
        sig_popt=np.full(param0.shape, np.nan)
        #popt, pcov = op.curve_fit(int_func, bin_center, count, p0=param0, bounds=(lower_bound, upper_bound), maxfev=50000)
        #sig_popt=np.sqrt(np.diag(pcov))
        
    except:
        print('Failed.')
        fit_success=False
        popt=np.full(param0.shape, np.nan)
        sig_popt=np.full(param0.shape, np.nan)
else: 

    print('Fit failed.')
    fit_success=False
    popt=np.full(param0.shape, np.nan)
    sig_popt=np.full(param0.shape, np.nan)

if high_occupancy: 
    popt=np.insert(popt, [0], [pe_charge])
    param0=np.insert(param0, 0, pe_charge)
    sig_popt=np.insert(sig_popt, [0], [np.nan])


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
ax.legend(handle, label)
plt.savefig(analysis_path + '/' + signal_folder + '/' + file_name + '.png')

if fit_success:
    x=np.arange(bin_center[0], bin_center[-1], width/10)
    sum_fit=norm_tail_int_sum(bin_center, width/2, *popt)
    part_of_fit = norm_tail_int_seperate(bin_center, width/2, *popt)
    init_fit=norm_tail_int_sum(bin_center, width/2, *param0)

    fig1, ax1= plt.subplots()
    plt.stairs(count0/sum(count0), bin_lim)
    plt.plot(bin_center, sum_fit, label='Fit Function')
    plt.plot(bin_center, init_fit, label='Initial Fit Parameters')

    if part_of_fit.shape[0]>5: 
        n=5
    else: 
        n=part_of_fit.shape[0]

    if high_occupancy: 
        
        lower_lim0=0
        upper_lim0=part_of_fit.shape[0]

        lower_lim1=np.ceil(popt[4])-5
        upper_lim1=np.ceil(popt[4])+5
        
        if lower_lim1> lower_lim0: 
            lower_lim0=lower_lim1

        if upper_lim1< upper_lim0: 
            upper_lim0=upper_lim1
        
        iter_array=np.arange(lower_lim0, upper_lim0, 1).astype(int)

    else: 
        iter_array=range(n)

    for j in iter_array: 

        label1= str(j) + ' PE'

        for k in range(part_of_fit.shape[1]):

            if k==0: 
                label2= ' normal distribution' 
            else: 
                label2= ' tail'

            plt.plot(bin_center, part_of_fit[j, k], label= label1+ label2)  

    #plt.plot(x, norm_fit)
    #plt.plot(x, tail_fit)
    plt.title('Arduino Setting ' + str(arduino_setting) + ' LED Voltage ' + str(v_set) + ' Duration ' + str(wid_set) + ' ns')
    plt.xlabel('Charge (pC)')
    plt.ylabel('Normalized Counts')
    plt.legend(loc='lower right', fontsize=font_size)

    if high_occupancy: 
        param_text=mlt.offsetbox.AnchoredText('PE Charge= ' + str(sci(popt[0])) + ' (Unfitted)\n1PE Stdev= ' + str(sci(popt[1])) + ' +- ' + str(sci(sig_popt[1])) + '\n0PE Charge= ' + str(sci(popt[2])) + ' +- '+ str(sci(sig_popt[2])) + '\nZero Stdev= ' + str(sci(popt[3])) + ' +- ' + str(sci(sig_popt[3])) +  '\nAverage PE= ' + str(sci(popt[4])) + ' +- ' + str(sci(sig_popt[4])) + '\nR= ' + str(sci(popt[5])) + ' +- ' + str(sci(sig_popt[5])) + '\nx0= ' + str(sci(popt[6])) + ' +- ' + str(sci(sig_popt[6])) + '\nBins= ' + str(bins), loc=1, prop=dict(fontsize=font_size))  
    else:
        param_text=mlt.offsetbox.AnchoredText('PE Charge= ' + str(sci(popt[0])) +  ' +- '+ str(sci(sig_popt[0])) + '\n1PE Stdev= ' + str(sci(popt[1])) + ' +- ' + str(sci(sig_popt[1]))+ '\n0PE Charge= ' + str(sci(popt[2])) + ' +- '+ str(sci(sig_popt[2])) + '\nZero Stdev= ' + str(sci(popt[3])) + ' +- ' + str(sci(sig_popt[3])) +  '\nAverage PE= ' + str(sci(popt[4])) + ' +- ' + str(sci(sig_popt[4])) + '\nR= ' + str(sci(popt[5])) + ' +- ' + str(sci(sig_popt[5])) + '\nx0= ' + str(sci(popt[6])) + ' +- ' + str(sci(sig_popt[6])) + '\nBins= ' + str(bins), loc=1, prop=dict(fontsize=font_size))  
    
    ax1.grid()
    ax1.add_artist(param_text)
    plt.tight_layout()
    #plt.show()
    plt.savefig(analysis_path + '/' + charge_dist_folder + '/' + file_name + '.png')

fig, ax2 = plt.subplots()
plt.hist(led_charge, bins=40)
param_text2=mlt.offsetbox.AnchoredText('Mean Charge = ' + str(sci(avg_led_charge)) + '\nMedian Charge = ' + str(sci(med_led_charge)) + '\nStandard Deviation = ' + str(sci(std_led_charge)), loc=1, prop=dict(fontsize=font_size))
ax2.add_artist(param_text2)
plt.tight_layout()	
plt.title('LED Charge Distribution')
plt.xlabel('Charge (pC)')
plt.ylabel('Fractional Count')
plt.savefig(analysis_path + '/' + charge_dist_folder + '/led_' + file_name + '.png')

gain=(popt[0]/con.e)*(10**(-12))
occupancy_fit=1-np.exp(-popt[4])

gain=(popt[0]/con.e)*(10**(-12))
occupancy_fit=1-np.exp(-popt[4])

#time_array=np.array([str(run_no), current_time])
#current_time0=" ".join(f for f in current_time)
    #occupancy_array=np.array([current_time0, run_no, arduino_setting, occupancy, waveform_no])[np.newaxis, :]
#popt_array=np.array([run_no, *popt])[np.newaxis, :]

if high_occupancy: 
    popt[0]=np.nan
    sig_popt[0]=np.nan

current_time0=" ".join(f for f in current_time)
occupancy_array=np.array([current_time0, run_no, arduino_setting, occupancy, waveform_no, overrange_count, np.average(charge)])[np.newaxis, :]
popt_array=np.array([run_no, *popt, *sig_popt])[np.newaxis, :]
#sig_popt_array=np.array([run_no, *sig_popt])[np.newaxis, :]

led_v_array=np.array([run_no, avg_led_charge, med_led_charge, std_led_charge, avg_led_peak, avg_led_duration, med_led_duration, std_led_duration, v_set, wid_set])[np.newaxis, :]
if run_no != 1:

    occupancy_array2=np.load(analysis_path+ '/' + occupancy_file)
    popt_array2=np.load(analysis_path + '/' + fit_param_file)
    led_v_array2=np.load(analysis_path + '/' + 'led_v.npy')

    occupancy_array=np.concatenate([occupancy_array2, occupancy_array])
    popt_array=np.concatenate([popt_array2, popt_array])
    led_v_array=np.concatenate([led_v_array2, led_v_array])

np.save(analysis_path+'/'+occupancy_file, occupancy_array)
np.save(analysis_path + '/' + fit_param_file, popt_array)
np.save(analysis_path + '/'+ 'led_v.npy', led_v_array)
    
if check_mode:
    plt.show(block=False)
    #print('Gain is calculated to be ' + str(sci(gain)))
    print('Occupancy (from fit) is calculated to be ' + str(occupancy))

