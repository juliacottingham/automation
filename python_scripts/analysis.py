import sys 
check_mode=int(sys.argv[2])
try:
    
    import matplotlib as mlt
    if check_mode:
        mlt.use('TkAgg') 
    else: 
        mlt.use('Agg')
    
    import matplotlib.pyplot as plt
    import os 
    
    import numpy as np
    import numpy.ma as ma
    import scipy.integrate as integral
    import scipy.optimize as op
    import scipy.constants as con
    import datetime
except: 
    print('Please activate pmt_env virtual environment before running')
    sys.exit()

#plt.ioff()
#NOTE TO SELF MAKE THESE VARIABLES EDITABLE IN THE RUN_AUTOCONTROL FILE
"""
t_int=[0, 100] #time interval for integration
v_th=-4 #in mV
width=7
bins=50
unit_factor=1/50
plotting_lim=50
num_pe=2
digits=2
font_size=6
"""
color_list=np.array(['blue', 'magenta', 'purple', 'green'])
#integrated charge of (mV*ns) divided by 50 ohm impedance for pC units

data_loc=sys.argv[1]
check_mode=int(sys.argv[2])
pmt_ch = int(sys.argv[3])
ch_enable=sys.argv[4:8]
setting=sys.argv[8]
analysis_path=sys.argv[9]

t_int=np.array(sys.argv[10:12]).astype(float)
v_th=float(sys.argv[12])
width=float(sys.argv[13])
bins=int(sys.argv[14])
unit_factor=float(sys.argv[15])
plotting_lim=int(sys.argv[16])
num_pe=int(sys.argv[17])
digits=int(sys.argv[18])
font_size=float(sys.argv[19])
signal_folder=sys.argv[20] 
charge_dist_folder=sys.argv[21]
file_name=sys.argv[22]
arduino_setting=int(sys.argv[23])
run_no=int(sys.argv[24])
occupancy_file=sys.argv[25]
current_time=sys.argv[26:]
fit_param_file='fit_param.npy'

print(data_loc)
print(check_mode)

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

    y[1:, :, x<0.03]=0
    return y 

def norm_tail_sum(x, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H): 
    k=norm_tail_seperate(x, pe_ch, pe_stdev, zero_ch, zero_stdev, avg_pe_fit, R, x0, H)
    return np.sum(k, axis=(0, 1))

data=np.load(data_loc + '.npy')
signal=np.stack([data[0], data[pmt_ch+1]], axis=0)
ch_no=data.shape[0]-1

waveform_no=signal.shape[2]
condition=((t_int[0] < signal[0]) & (signal[0]<t_int[1]))
condition=np.stack([condition, condition], axis=0)
mask1=np.logical_or(~np.isfinite(signal), ~condition) 

signal_ma=ma.array(signal, mask=mask1)
peak_index=signal_ma[1:].argmin(axis=1)

#grid probably unnecesssary?? only one dimension left after choosing peak
#nvm

grid=np.ix_(*[np.arange(s) for s in signal_ma.shape[-1:]])
peak_t=signal[(0, *((peak_index,) + grid))]
int_lim=[peak_t - width, peak_t + width]

condition2=((int_lim[0] < signal[0]) & (signal[0] < int_lim[1]))
condition2=np.stack([condition2, condition2], axis=0)

signal_int=ma.array(signal_ma, mask=~condition2)
charge=integral.trapezoid((-1)*signal_int[1], signal_int[0], axis=0)*unit_factor
charge.set_fill_value(0)


pmt_count=ma.sum((ma.min(signal_int[1], axis =0)) < v_th)

occupancy=pmt_count/waveform_no

print('Occupancy found to be ' + str(occupancy))

count, bin_lim = np.histogram(charge, bins)
width=bin_lim[1]-bin_lim[0]
bin_center=(bin_lim+(width/2))[:-1]

if occupancy == 1: 
    avg_pe_guess=3
else: 
    avg_pe_guess=-np.log(1-occupancy)

bin_center1=bin_center[bin_center>0.07]
count1=count[bin_center>0.07]

h_guess=sum(count)*width;

pe1=bin_center1[np.argmax(count1)]
pe0=bin_center[np.argmax(count)]

#bounds0=((0, max(charge)), (0, np.inf), (-1, max(charge)), (0, np.inf), (0, np.inf), (0, 1), (0, np.inf), (0, np.inf))
lower_bound=(0.05, width, -1, width/2, 0, 0, 0.01, 0.8*h_guess)
upper_bound=(1.5*pe1, max(charge)-min(charge), 0.3*pe1, max(charge)-min(charge), np.inf, 0.5, 10, 1.2*h_guess)
param0=(pe1, 1, pe0, 1, avg_pe_guess, 0.2, 0.1, h_guess)
try:
    popt, pcov = op.curve_fit(norm_tail_sum, bin_center, count, p0=param0, bounds=(lower_bound, upper_bound), maxfev=50000)
except: 
    popt, pcov = op.curve_fit(norm_tail_sum, bin_center, count, bounds=(lower_bound, upper_bound), maxfev=50000)
x=np.arange(bin_lim[0], bin_lim[-1], width/10)

sum_fit=norm_tail_sum(x, *popt)
part_of_fit = norm_tail_seperate(x, *popt)
#NOTE: add saving feature here 

     
title0='Oscilloscope Output'

if data.shape[2]>plotting_lim: 
    index=plotting_lim
    title0 += ' (first ' + str(plotting_lim) + ' waveforms)'
else:
    index=data.shape[2]

title0 += ' for setting ' + str(setting)

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
plt.savefig(analysis_path + '/' + signal_folder + '/' + file_name + '.png')

fig1, ax1= plt.subplots()
plt.hist(charge, bins=bins)
plt.plot(x, sum_fit, label='Fit Function')

for j in range(part_of_fit.shape[0]): 
    
    label1= str(j) + ' PE'
    
    for k in range(part_of_fit.shape[1]):
        
        if k==0: 
            label2= ' normal distribution' 
        else: 
            label2= ' tail'
        
        plt.plot(x, part_of_fit[j, k], label= label1+ label2)  

#plt.plot(x, norm_fit)
#plt.plot(x, tail_fit)
plt.title('Charge Distribution for Arduino Setting ' + str(setting))
plt.xlabel('Charge (pC)')
plt.ylabel('Counts')

param_text=mlt.offsetbox.AnchoredText('PE Charge= ' + str(sci(popt[0])) + '\n1PE Stdev= ' + str(sci(popt[1])) + '\n0PE Charge= ' + str(sci(popt[2])) + '\nZero Stdev= ' + str(sci(popt[3])) + '\nAverage PE= ' + str(sci(popt[4])) + '\nR= ' + str(sci(popt[5])) + '\nx0= ' + str(sci(popt[6])) + '\nIntegration Area= ' + str(sci(popt[7])), loc=1, prop=dict(fontsize=font_size))  
A

ax1.grid()
ax1.add_artist(param_text)
plt.tight_layout()
plt.savefig(analysis_path + '/' + charge_dist_folder + '/' + file_name + '.png')

gain=(popt[0]/con.e)*(10**(-12))
occupancy_fit=1-np.exp(-popt[4])

#time_array=np.array([str(run_no), current_time])
current_time0=" ".join(f for f in current_time)
occupancy_array=np.array([current_time0, run_no, arduino_setting, occupancy, waveform_no])[np.newaxis, :]
popt_array=np.array(popt)[np.newaxis, :]

if run_no != 1:
    occupancy_array2=np.load(analysis_path+ '/' + occupancy_file)
    popt_array2=np.load(analysis_path + '/' + occupancy_file)
    
    if occupancy_array2.shape[0] == run_no: 
        occupancy_array2[run_no-1, :] =occupancy_array
        occupancy_array=occupancy_array2
        
        popt_array2[run_no-1, :]=popt_array
        popt_array=popt_array2
    else:
        occupancy_array=np.concatenate([occupancy_array2, occupancy_array])
        popt_array=np.concatenate([popt_array2, popt_array])

np.save(analysis_path+'/'+occupancy_file, occupancy_array)
np.save(analysis_path + '/' + fit_param_file, popt_array)

#plt.show(block=False)

if check_mode:
    plt.show(block=False)
    print('Gain is calculated to be ' + str(sci(gain)))
    #print('Occupancy (from fit) is calculated to be ' + str(occupancy))

