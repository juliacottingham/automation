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
except: 
    print('Please activate pmt_env.')
    sys.exit()

plt.ioff()

condition=0

path=sys.argv[1]
file=sys.argv[2]
check_mode=int(sys.argv[3])
#file_2='fit_param.npy'
file_2=sys.argv[4]

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
array2_set1=array2[setting2==1]
#array2_set1=array2[]

popt_num=int((array2_set1.shape[1]-1)/2)
sig_popt=array2_set1[:, (-popt_num):]

plt.figure()
plt.errorbar(set1[:, 0], set1[:, 2], yerr=set1[:, 5])
#times_time=np.array([t[11:20] for t in times])
plt.xticks(tick_index, times_array)
plt.title('Occupancy observed with run no. (setting 1)')
plt.xlabel('Time of measurement')
plt.ylabel('Signals per LED pulse observed')
plt.savefig(path + '/occupancy_variation.png')

plt.figure()
plt.errorbar(set1[:, 0], set1[:, 4], yerr=set1[:, 6])
plt.xticks(tick_index, times_array)
plt.title('Average PE observed with run no. (setting 1)')
plt.xlabel('Run no.')
plt.ylabel('Average PE')
plt.savefig(path + '/avg_pe_variation.png')


plt.figure()
plt.errorbar(array2_set1[:, 0], array2_set1[:, 5], yerr=sig_popt[:, 5])
plt.xticks(tick_index, times_array)
plt.title('Average PE determined through function fitting')
plt.xlabel('Time of measurement')
plt.ylabel('Average PE')
plt.savefig(path + '/avg_pe_fit.png')

plt.figure()
plt.errorbar(array2_set1[:, 0], array2_set1[:, 1], yerr=sig_popt[:, 1])
plt.xticks(tick_index, times_array)
plt.title('PE Charge determined through function fitting')
plt.xlabel('Time of measurement')
plt.ylabel('Signal Charge (pC)')
plt.savefig(path + '/pe_charge_fit.png')

#make plot for changes in arduino setting 

if check_mode==1: 
    plt.show(block=False)
