import sys
check_mode=int(sys.argv[3])
try: 
    import matplotlib as mlt 
    if check_mode: 
        mlt.use('TkAgg')
    else: 
        mlt.use('Agg')
    import matplotlib.pyplot as plt 
    import numpy as np
    import numpy.ma as ma
    import pandas as pd 
    import datetime as dt
except: 
    print('Please activate pmt_env.')
    sys.exit()

plt.ioff()


def plotting_function(time_arr, temp_time_arr, data_arr, temp_arr, legend_item, ylabel, title, xlim): 
	fig, ax =plt.subplots()
	plt.plot(dt_array, data_arr)
	plt.legend([legend_item], loc=2)
	plt.title(title)
	ax2=ax.twinx()
	ax2.plot(temp_time_arr, temp_arr, color='orange')
	plt.legend(['Temperature'], loc=1)
	ax.set_ylabel(ylabel)
	ax2.set_ylabel('Temperature degrees Celsius')
	ax.set_xlim(xlim)

path=sys.argv[1]

#path='/home/labwork/autocontrol/output_files/led_v_curve12/processed_data'
file=sys.argv[2]

check_mode=int(sys.argv[3])
#file_2='fit_param.npy'
file_2=sys.argv[4]

times=np.load(path+ '/' + file)[:, 0]
array=np.load(path + '/' + file)[:, 1:].astype(float)
array2=np.load(path + '/' + file_2)

#v_array=np.concatenate([np.arange(8.8, 9.26, 0.02), np.arange(8.8, 9.26, 0.02)])
led_v_array=np.load(path + '/led_v.npy').astype(float)

dt_array=[]
for t in range(len(times)): 
    dt_array.append(dt.datetime.strptime(times[t], '%a %b %d %I:%M:%S %p EDT %Y'))

popt_num=int((array2.shape[1]-1)/2)
sig_popt=array2[:, (-popt_num):]


m=array[:, 2]!=1
sig_pe_o=np.empty(array.shape[0])
avg_pe=np.empty((array.shape[0], 2))

sig_pe_o[m]=np.sqrt(array[m, 2]/((1-array[m,2])*array[m, 3]))
sig_pe_o[~m]=np.inf

condition=sig_pe_o<sig_popt[:, 4]

avg_pe[condition, 0]=-np.log(1-array[condition,2])

avg_pe[condition, 1]=sig_pe_o[condition]

avg_pe[~condition, 0]=array2[~condition, 5]
avg_pe[~condition, 1]=sig_popt[~condition, 4] 


max_err=10

led_v_array2=led_v_array
sig_popt2=sig_popt
array2=array2[sig_popt[:, 4]<max_err]
led_v_array=led_v_array[sig_popt[:, 4]<max_err]
#led_v_array=led_v_array[sig_popt[:, 5]<0.1]
dt_array=np.array(dt_array)
#v_array=v_array[sig_popt[:, 5]<max_err]
sig_popt=sig_popt[sig_popt[:, 4]<max_err]
dt_array=dt_array[array2[:, 0].astype(int)-1]

#plotting_function(dt_array, time2, led_v_array[:, 1], temp, 'LED Charge', 'Average LED Charge (pC)', 'Average LED Charge (pC)', xlim) 

#plotting_function(dt_array, time2, led_v_array[:, 2], temp, 'LED Charge', 'Median LED Charge (pC)')

def plotting_function2(time, arr1, arr2, y_error, legend_arr, title, ylabel_arr): 
	
	fig, ax = plt.subplots()
	plt.plot(time, arr1)
	ax.legend([legend_arr[0]], loc=1)
	ax.set_ylabel(ylabel_arr[0])
	ax2=ax.twinx()
	ax2.errorbar(time, arr2, yerr=y_error, color='orange')
	ax2.set_ylabel(ylabel_arr[1])
	ax2.legend([legend_arr[1]], loc=2)
	plt.title(title)
	return fig, ax, ax2
"""
plotting_function2(dt_array2, led_v_array[:, 1], array2[:, 5], sig_popt[:, 5], ['LED Charge', 'Avg PE'], 'Average LED Charge (pC)', ['Average LED Charge (pC)', 'Average PE'])

plotting_function2(dt_array2, led_v_array[:, 2], array2[:, 5], sig_popt[:, 5], ['LED Charge', 'Avg PE'], 'Median LED Charge (pC)', ['Median LED Charge (pC)', 'Average PE'])

plotting_function2(dt_array2, led_v_array[:, 3], array2[:, 5], sig_popt[:, 5], ['LED Charge', 'Avg PE'], 'Standard Deviation LED Charge (pC)', ['Standard Deviation LED Charge (pC)', 'Average PE'])
fig, ax, ax2 = plotting_function2(dt_array2, led_v_array[:, 4], array2[:, 5], sig_popt[:, 5], ['LED Voltage', 'Avg PE'], 'Average LED Peak Voltage (V)', ['Average LED Voltage (V)', 'Average PE'])
ax.invert_yaxis()

plotting_function2(dt_array2, led_v_array[:, 5], array2[:, 5], sig_popt[:, 5], ['LED Pulse Duration', 'Avg PE'], 'Average LED Pulse Duration (ns)', ['Average LED Pulse Duration (ns)', 'Average PE'])
plotting_function2(dt_array2, led_v_array[:, 6], array2[:, 5], sig_popt[:, 5], ['LED Pulse Duration', 'Avg PE'], 'Median LED Pulse Duration (ns)', ['Median LED Pulse Duration (ns)', 'Average PE'])
plotting_function2(dt_array2, led_v_array[:, 7], array2[:, 5], sig_popt[:, 5], ['LED Pulse Duration', 'Avg PE'], 'Standard Deviation of LED Pulse Duration (ns)', ['Standard Deiviation of LED Pulse Duration (ns)', 'Average PE'])

plt.figure()
plt.plot(dt_array, led_v_array[:, 1])
plt.title('Average LED Charge (pC)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 2])
plt.title('Median LED Charge (pC)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
fig, ax2= plt.subplots()
plt.plot(dt_array, led_v_array[:, 3])
plt.title('Standard Deviation of  LED Charge (pC)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 4])
plt.title('Average LED Peak (V)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 5])
plt.title('Average LED Duration (ns)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 6])
plt.title('Median LED Duration (ns)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
plt.figure()
plt.plot(dt_array, led_v_array[:, 7])
plt.title('Standard Deviation of LED Duration (ns)')
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#
"""
def plotting_function1(led_v, title, xlabel, ylabel): 
    plt.figure()
    plt.plot(led_v_array[:, -2], led_v)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    
titles=['Average LED Charge', 'Median LED Charge', 'Standard Deviation of LED Charge', 'Average LED Peak', 'Average LED Duration', 'Median LED Duration', 'Standard Deviation of LED Duration']

ylabels=['Charge (pC)', 'Charge (pC)', 'Charge (pC)', 'Voltage (mV)', 'Duration (ns)', 'Duration (ns)', 'Duration (ns)']

for n in range(led_v_array.shape[1]-3): 
    plotting_function1(led_v_array[:, n+1], titles[n], 'Input voltage', ylabels[n])

"""
plt.figure()
plt.plot(led_v_array[:, -2], led_v_array[:, 0])
plt.ylabel('Average LED Charge (pC)')
plt.xlabel('Input voltage to signal generator')
plt.title('Input voltage to signal generator versus fraction of charge produced')
"""
#Fitted average PE against voltage input to signal generator (LOG)
fig, ax = plt.subplots()
plt.errorbar(led_v_array[:, -2], array2[:, 5], yerr=sig_popt[:, 4], linestyle='None', marker='.', color='orange')
ax.set_yscale("log")
plt.xlabel('Input voltage (V)')
plt.ylabel('Average PE')
plt.title('Light Level with Voltage')
plt.savefig(path + '/v_curve.png')

#Fitted average PE against measured voltage given to LED
fig, ax = plt.subplots()
plt.errorbar(led_v_array[:, 4], array2[:, 5], yerr=sig_popt[:, 4], linestyle='None', marker='.', color='orange')
ax.set_yscale("log")
plt.xlabel('Measured Voltage on CH C (mV)')
plt.ylabel('Average PE')
plt.title('Fitted light level with voltage')
plt.grid()
plt.savefig(path + '/v_curve_meas.png')

#Occupancy against voltage input to signal generator - note: no errorbars because they go to infinity at occupancy=1
plt.figure()
plt.errorbar(led_v_array2[m, -2], array[m, 2], linestyle='None', marker='o', color='purple')
plt.xlabel('Input voltage (V)')
plt.ylabel('Occupancy')
plt.title('Occupancy with input voltage')
plt.grid()
plt.savefig(path + '/occupancy_v_curve.png')

#Occupancy against measured voltage - same note
plt.figure()
plt.errorbar(led_v_array2[m, 4], array[m, 2], linestyle='None', marker='o', color='purple')
plt.xlabel('Measured voltage (mV)')
plt.ylabel('Occupancy')
plt.title('Occupancy with measured voltage')
plt.savefig(path + '/occupancy_v_curve_meas.png')

#Avg PE from occupancy against measured voltage 
fig, ax = plt.subplots()
plt.errorbar(led_v_array2[m, 4], -np.log(1-array[m, 2]), yerr=sig_pe_o[m], linestyle='None', marker='.')
plt.xlabel('Measured channel C voltage (mV)')
plt.ylabel('Avg PE (calculated from occupancy)')
plt.title('Avg PE with measured voltage')
ax.set_yscale("log")
plt.savefig(path + '/pe_from_occupancy_meas.png')

#Avg PE from occupancy against input voltage
fig, ax = plt.subplots()
plt.errorbar(led_v_array2[m, -2], -np.log(1-array[m, 2]), yerr=sig_pe_o[m], linestyle='None', marker='.')
plt.xlabel('Input voltage (V)')
plt.ylabel('Avg PE (calculated from occupancy)')
plt.title('Avg PE with input voltage')
ax.set_yscale("log")
plt.savefig(path + '/pe_from_occupancy.png')



fig, ax= plt.subplots()
plt.errorbar(led_v_array2[condition, -2], avg_pe[condition, 0], yerr=avg_pe[condition, 1], linestyle='None', marker='.', label='Estimated from Occupancy')
plt.errorbar(led_v_array2[~condition, -2], avg_pe[~condition, 0], yerr=avg_pe[~condition, 1], linestyle='None', marker='.', label='Estimated from Charge Distribution')
plt.xlabel('Input voltage (V)')
plt.ylabel('Avg PE')
plt.title('Light level with input voltage')
plt.legend()
plt.savefig(path + '/v_curve_new_method.png')

fig, ax = plt.subplots()
plt.errorbar(led_v_array2[condition, -2], avg_pe[condition, 0], yerr=avg_pe[condition, 1], linestyle='None', marker='.', label='Estimated from Occupancy')
plt.errorbar(led_v_array2[~condition, -2], avg_pe[~condition, 0], yerr=avg_pe[~condition, 1], linestyle='None', marker='.', label='Estimated from Charge Distribution')
plt.xlabel('Input voltage (V) ')
plt.ylabel('Avg PE')
plt.title('Light level with input voltage')
#ax.set_xscale("log")
ax.set_yscale("log")
plt.legend()
plt.savefig(path + '/v_curve_new_method_log.png')

fig, ax = plt.subplots()
plt.errorbar(led_v_array2[condition, 4], avg_pe[condition, 0], yerr=avg_pe[condition, 1], linestyle='None', marker='.', label='Estimated from Occupancy')
plt.errorbar(led_v_array2[~condition, 4], avg_pe[~condition, 0], yerr=avg_pe[~condition, 1], linestyle='None', marker='.', label='Estimated from Charge Distribution')
plt.xlabel('Measured peak voltage (mV)')
plt.ylabel('Avg PE')
plt.title('Light level with measured voltage')
#ax.set_xscale("log")
ax.set_yscale("log")
plt.legend()
plt.savefig(path + '/v_curve_new_method_log2.png')
"""
fig, ax = plt.subplots()
plt.errorbar(led_v_array2[:, 4], led_v_array[:, , yerr=avg_pe[condition, 1], linestyle='None', marker='.', label='Estimated from Occupancy')
plt.errorbar(led_v_array2[~condition, 4], avg_pe[~condition, 0], yerr=avg_pe[~condition, 1], linestyle='None', marker='.', label='Estimated from Charge Distribution')
plt.xlabel('Measured peak voltage (mV)')
plt.ylabel('Avg PE')
plt.title('Light level with measured voltage')
#ax.set_xscale("log")
ax.set_yscale("log")
plt.legend()
plt.savefig(path + '/v_curve_new_method_log2.png')
"""


if check_mode:
    plt.show(block=False)