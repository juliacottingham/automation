import sys
check_mode=1
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

my_table=pd.read_excel('/home/labwork/autocontrol/temperature/temp3.xls', skiprows=28, usecols=[0, 1, 2, 3])

init_col=np.array([*my_table.keys()])
final_col=np.array(["No.", "Time", "Temp", "Humidity"])
mapping_dict=dict(zip(init_col, final_col))

#my_table=my_table.rename(columns={0: "No.", 1: "Time", 2: "Temperature", 3: "Humidity"}) 

my_table=my_table.rename(columns=mapping_dict) 

#start_idx=int(my_table["No."][my_table["Time"]=="2023-05-26 11:26:18"]) -1
#end_idx=int(my_table["No."][my_table["Time"]=="2023-05-26 16:05:18"]) -1
start_idx=0
end_idx=len(my_table["No."])

plt.figure() 

plt.plot(my_table["Time"][start_idx:end_idx], my_table["Temp"][start_idx:end_idx])
plt.title("Temperature over Time") 
plt.ylabel("Temperature in Celsius")
plt.xlabel("Time")
plt.show(block=False)
condition=0
path='/home/labwork/autocontrol/output_files/azimuth3_long_term_run10/processed_data'
file='occupancy.npy'
check_mode=1
file_2='fit_param.npy'

#path=sys.argv[1]
#file=sys.argv[2]
#check_mode=int(sys.argv[3])
#file_2='fit_param.npy'
#file_2=sys.argv[4]

times=np.load(path+ '/' + file)[:, 0]
array=np.load(path + '/' + file)[:, 1:].astype(float)
array2=np.load(path + '/' + file_2)

array[array[:, 2]==1, 3]=0.999


run=array[:, 0]
setting=array[:, 1]
occupancy=array[:, 2:3]
waveform_no=array[:, 3:]

avg_pe=-np.log(1-occupancy)

occupancy_err=np.sqrt(occupancy*(1-occupancy)/waveform_no)
avg_pe_err=np.sqrt(occupancy/(waveform_no*(1-occupancy)))

array=np.concatenate([array, occupancy, occupancy_err, avg_pe_err], axis=1)

#array2_set1=array2[setting==1]

interval=15;
#my_time2=np.empty(end_idx-start_idx)

time2=[]
temp=my_table["Temp"][start_idx:end_idx]

for t in np.arange(start_idx, end_idx): 
    time=my_table["Time"][t]
    time2.append(dt.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))

"""
for r in np.arange(start_idx, end_idx):
    y=my_table["Times"][r]
    my_time2[r]=y[-8:]
    
    hour=int(my_time2[r][:2])
    
    if hour==0:
        my_time2[r][:2]='12' 
        my_time2[r]=my_time2[r]+ ' AM '
    
    else if hour > 12: 
        new_hour= hour - 12
        if new_hour <10: 
            my_time2[r][:2]= '0' + str(new_hour)
        else: 
            my_time2[r][:2]= str(new_hour)
        my_time2[r] = my_time[r] + ' PM '
    
    else: 
        my_time2[r] = my_time[r] + ' AM '
"""
dt_array=[]
for t in range(len(times)): 
    dt_array.append(dt.datetime.strptime(times[t], '%a %b %d %I:%M:%S %p EDT %Y'))


t_index=range(len(times))
my_times=np.array([t[11:23] for t in times])
my_day=np.array([t[0:3] for t in times])
my_date=np.array([t[4:10] + t[-5:] for t in times])
tick_index=[]
times_array=[]
day_array=[]
for t in range(len(t_index)): 
    if t%interval ==0:
        tick_index.append(t_index[t])
        times_array.append(my_times[t] + '\n' + my_day[t] + '\n' + my_date[t])
        day_array.append(my_day[t])
set1=array[setting==1]
#make plot for changes in arduino setting 1 occupancy 
index=np.argsort(array2[:, 0])
array2=array2[index]
if condition: 
    setting2=np.insert(setting, 68, 1)
else: 
    setting2=setting


#tick_index2=np.arange(0, array2.shape[0], 1)
#times_array2=np.insert(times_array, 67, '')
#array2_set1=array2[setting2==1]
array2_set1=array2
#dt_array2=dt_array[
#array2_set1=array2[]

popt_num=int((array2_set1.shape[1]-1)/2)
sig_popt=array2_set1[:, (-popt_num):]
array2_set1=array2_set1[sig_popt[:, 5] <0.1]
sig_popt=sig_popt[sig_popt[:, 5]<0.1]

dt_array=np.array(dt_array)
dt_array2=dt_array[array2_set1[:, 0].astype(int)-1]

#
xlim=[dt_array[0], dt_array[-1]]

#plt.figure()
fig, ax=plt.subplots()
ax.errorbar(dt_array, set1[:, 2], yerr=set1[:, 5])
#times_time=np.array([t[11:20] for t in times])
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
#plt.xticks(tick_index, times_array)
ax.set_title('Occupancy observed with run no. (setting 1)')
ax.set_xlabel('Time of measurement')
ax.set_ylabel('Signals per LED pulse observed')
ax2.set_ylabel('Temperature degrees Celsius')
ax.legend(['Occupancy'], loc=1)
ax2.legend(['Temperature'], loc=2)
ax.set_xlim(xlim)
plt.savefig(path + '/occupancy_variation.png')


fig, ax=plt.subplots()
#plt.figure()
ax.errorbar(dt_array, set1[:, 4], yerr=set1[:, 6])
#plt.xticks(tick_index, times_array)
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
ax.set_title('Average PE observed with run no. (setting 1)')
ax.set_xlabel('Run no.')
ax.set_ylabel('Average PE')
ax2.set_ylabel('Temperature in degrees Celsius')
ax.legend(['Avg PE'], loc=1)
ax2.legend(['Temperature'], loc=2)

ax.set_xlim(xlim)
plt.savefig(path + '/avg_pe_variation.png')


#plt.figure()
fig, ax=plt.subplots()
ax.errorbar(dt_array2, array2_set1[:, 5], yerr=sig_popt[:, 5])
#plt.xticks(tick_index, times_array)
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
ax.set_title('Average PE determined through function fitting')
ax.set_xlabel('Time of measurement')
ax.set_ylabel('Average PE')
ax2.set_ylabel('Temperature (in degrees Celsius)')
ax.legend(['Avg PE'], loc=1)
ax2.legend(['Temperature'], loc=2)
ax.set_xlim(xlim)
plt.savefig(path + '/avg_pe_fit.png')

occupancy_fit=1-np.exp(-array2_set1[:, 5])
occupancy_sigma=sig_popt[:, 5]*(np.exp(-array2_set1[:, 5]))
fig, ax=plt.subplots()
ax.errorbar(dt_array2, occupancy_fit, yerr=occupancy_sigma)
#plt.xticks(tick_index, times_array)
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
ax.set_title('Occupancy determined through function fitting')
ax.set_xlabel('Time of measurement')
ax.set_ylabel('Occupancy')
ax2.set_ylabel('Temperature (in degrees Celsius)')
ax.legend(['Occupancy'], loc=1)
ax2.legend(['Temperature'], loc=2)
ax.set_xlim(xlim)
plt.savefig(path + '/occupancy_fit.png')




#plt.figure()
fig, ax=plt.subplots()
ax.errorbar(dt_array2, array2_set1[:, 1], yerr=sig_popt[:, 1])
#plt.xticks(tick_index, times_array)
ax2=ax.twinx()
ax2.plot(time2, my_table["Temp"][start_idx:end_idx], color='orange')
ax.set_title('PE Charge determined through function fitting')
ax.set_xlabel('Time of measurement')
ax.set_ylabel('Signal Charge (pC)')
ax2.set_ylabel('Temperature in degrees Celsius')
ax.legend(['Avg PE'], loc=1)
ax2.legend(['Temperature'], loc=0)
ax.set_xlim(xlim)
plt.savefig(path + '/pe_charge_fit.png')

#make plot for changes in arduino setting 

if check_mode==1: 
    plt.show(block=False)
