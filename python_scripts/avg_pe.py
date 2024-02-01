import numpy as np 
import tkinter
import sys
import os 
try: 
    import matplotlib as mlt 
    mlt.use('TkAgg') 
    import matplotlib.pyplot as plt 
except: 
    raise RuntimeError('PLEASE ACTIVATE PMT_ENV (CONDA VIRTUAL ENVIRONMENT) BEFORE RUNNING') 
    #sys.exit()

#array=np.load('/home/labwork/autocontrol/output_files/data_set_arduino_setting/processed_data/occupancy.npy')

#array=np.load('/home/labwork/autocontrol/output_files/azimuth1_test2/processed_data/occupancy.npy')
def my_function(path1, path2, title, condition, condition2):
    
    if condition:
        array=np.load(path1)[:, 1:].astype(float)
        time_day=np.load(path1)[:, 0]
    else: 
        array=np.load(path1)
    setting=array[:, 1]
    occupancy=array[:, 2:3]
    waveform_no=array[:, 3:]
    avg_pe=-np.log(1-occupancy)

    occupancy_err=np.sqrt(occupancy*(1-occupancy)/waveform_no)
    avg_pe_err=np.sqrt(occupancy/(waveform_no*(1-occupancy)))

    array=np.concatenate([array, avg_pe, occupancy_err, avg_pe_err], axis=1)
    if condition2:
        n=np.arange(0, array.shape[0]/2, 1).astype(int)
        set_1=array[2*n] 
        set_other=array[2*n+1] 
    else:
        set_1=array[setting==1]
        set_other=array[setting!=1]

    occupancy_ratio=set_other[:, 2]/set_1[:, 2]
    print(set_other[:, 2]) 
    print(set_1[:, 2])

    occupancy_ratio_err=occupancy_ratio*np.sqrt(((set_other[:, 5]/set_other[:,2])**2) + ((set_1[:, 5]/set_1[:,2])**2))
    avg_pe_ratio=set_other[:, 4]/set_1[:, 4]
    avg_pe_ratio_err=avg_pe_ratio*np.sqrt(((set_other[:, 6]/set_other[:, 4])**2) +((set_1[:, 6]/set_1[:, 4])**2))

###### This part is Kristi's data
    led_trigger=60*60
#path='/home/labwork/autocontrol/data_files/Azimuth2'
    path=path2
    #path='/home/labwork/autocontrol/data_files/Azimuth1'
    file_array=np.array(os.listdir(path)) 
    data_sets=np.empty(file_array.size, dtype=object)

    for f in range(len(file_array)): 
        data_sets[f]=np.loadtxt(path + '/' + file_array[f], skiprows=1)[:-1]
    #data_sets[f]=data_sets[f, :-1]

    array2=np.concatenate(data_sets, axis=0)

    occupancy2=array2[:, 3:]/led_trigger
    avg_pe2=-np.log(1-occupancy2)

    occupancy_err2=np.sqrt(occupancy2*(1-occupancy2)/led_trigger)
    avg_pe_err2=np.sqrt(occupancy2/(led_trigger*(1-occupancy2)))

    array2=np.concatenate([array2, avg_pe2, occupancy_err2, avg_pe_err2, occupancy2], axis=1) 
    n=np.arange(0, array2.shape[0]/2, 1).astype(int)
    set_1_2=array2[2*n] 
    set_other_2=array2[2*n+1] 
    
    occupancy_ratio2=set_other_2[:, 3]/set_1_2[:, 3]
    avg_pe_ratio2=set_other_2[:, 4]/set_1_2[:, 4] 
    
    #print(occupancy_ratio2.shape)
    #print(avg_pe_ratio2.shape)
    #print(occupancy_ratio2)
    #print(avg_pe_ratio2)

    occupancy_ratio_err2=occupancy_ratio2*np.sqrt(((set_other_2[:, 5]/set_other_2[:,7])**2) + ((set_1_2[:, 5]/set_1_2[:,7])**2))
    avg_pe_ratio_err2=avg_pe_ratio2*np.sqrt(((set_other_2[:, 6]/set_other_2[:, 4])**2) +((set_1_2[:, 6]/set_1_2[:, 4])**2))

    new_array=np.stack([set_other_2[:, 1], avg_pe_ratio2, avg_pe_ratio_err2, occupancy_ratio2, occupancy_ratio_err2]) 
    new_array=new_array[:, new_array[0, :].argsort()]

    grouped = np.split(new_array, np.unique(new_array[0, :], return_index=True)[1][1:], axis=1)

    setting=np.empty(len(grouped))
    averaged_pe=np.empty(len(grouped))
    averaged_occupancy=np.empty(len(grouped))
    averaged_occupancy_err=np.empty(len(grouped))
#no=np.empty(len(grouped))

    averaged_pe_err=np.empty(len(grouped))
    for g in range(len(grouped)):
        no=grouped[0][0].size
        setting[g]=grouped[g][0][0]
        averaged_pe[g]=np.average(grouped[g][1]) #averaged the avg PE ratio for multiple iterations of the same setting
        quadrature=map(lambda x: x*x, grouped[g][2])
        averaged_pe_err[g]=np.sqrt(sum(list(quadrature)))/no

        averaged_occupancy[g]=np.average(grouped[g][3])
        quadrature=map(lambda x: x*x, grouped[g][4])
        averaged_occupancy_err[g]=np.sqrt(sum(list(quadrature)))/no
    
    #print(setting.shape)
    #se=averaged_pe[setting!=1]/averaged_pe[setting==1]
    plt.figure()
    
    i=np.argsort(set_other[:,1])
    
    #sorted_setting=np.sort(set_other[:,1])
    plt.errorbar((set_other[:, 1][i]-1)*0.5, avg_pe_ratio[i], yerr=avg_pe_ratio_err[i], label='My Data')

    plt.errorbar((setting-1)*0.5, averaged_pe, yerr=averaged_pe_err, label="Kristi's Data")
    plt.grid()

    plt.title(title + ' Avg PE Data') 
    plt.xlabel('Distance from center of PMT (inches)') 
    plt.ylabel('Ratio of average PE per LED trigger to center of PMT') 
    plt.legend()
    
    plt.figure()

    plt.errorbar((set_other[:, 1][i]-1)*0.5, occupancy_ratio[i], yerr=occupancy_ratio_err[i], label='My Data')

    plt.errorbar((setting-1)*0.5, averaged_occupancy, yerr=averaged_occupancy_err, label="Kristi's Data")
    plt.grid()

    plt.title(title + ' Occupancy Data') 
    plt.xlabel('Distance from center of PMT (inches)') 
    plt.ylabel('Ratio of average PE per LED trigger to center of PMT') 
    plt.legend()

    plt.show(block=False)
    
path='/home/labwork/autocontrol/output_files'
path_2='/home/labwork/autocontrol/data_files'

path1=path + '/azimuth1_test2/processed_data/occupancy.npy'
path2=path_2 + '/Azimuth1'
my_function(path1, path2, 'Azimuth 1', False, False)

path1=path + '/data_set_arduino_setting/processed_data/occupancy.npy'
path2=path_2 + '/Azimuth2'
my_function(path1, path2, 'Azimuth 2', False, False)

#Azimuth 4 data not good (forgot to turn on the PMT voltage)
#path1=path+ '/azimuth4_take1/processed_data/occupancy.npy'
#path2=path_2 + '/Azimuth4' 
#my_function(path1, path2, 'Azimuth4')

path1=path + '/azimuth3_long_run/processed_data/occupancy.npy' 
path2=path_2+'/Azimuth3'
my_function(path1, path2, 'Azimuth 3', False, False)

path1 = path + '/azimuth3_long_run_2/processed_data/occupancy.npy' 
path2=path_2+ '/Azimuth3' 
my_function(path1, path2, 'Azimuth 3 Take 2', False, False)

path1 = path + '/azimuth3_long_run_3/processed_data/occupancy.npy' 
path2=path_2+ '/Azimuth3' 
my_function(path1, path2, 'Azimuth 3 Take 3', False, False)

path1 = path + '/azimuth2_long_run_2/processed_data/occupancy.npy' 
path2=path_2+ '/Azimuth2' 
my_function(path1, path2, 'Azimuth 2 Take 2', True, False)



