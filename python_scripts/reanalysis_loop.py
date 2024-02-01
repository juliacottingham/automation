import subprocess
import numpy as np
import os

def run_cmd(cmd): 
    cmd=cmd.split(" ")
    out=subprocess.check_output(cmd)
    return out

raw_data_dir="/home/labwork/autocontrol/output_files/sig_gen_test5/raw_data/"

check_mode=1
pmt_ch=0
led_ch=2
ch_enable=np.array(["1", "0", "1", "0"])
setting=1
analysis_path="/home/labwork/autocontrol/output_files/sig_gen_test5/processed_data"
t_int=np.array(["-10", "50"])
led_t_int=np.array(["-5", "30"])
v_th=-3
int_width=14
bins=50
unit_factor=1/50
plotting_lim=50000
num_pe=5
digits=2
font_size=6
signal_folder="signal"
charge_dist_folder="charge_distribution"
arduino_setting=1
occupancy_file="occupancy2.npy"
fit_param_file="fit_param.npy"

v_set=5
wid=np.arange(5, 14.3, 0.1)

pe_charge=2.213
overflow_file=analysis_path + "/overflow.npy"
tr_dir='falling'
tr_v=1000

std0_guess=0.009
std1_guess=0.87
std0_lim=0.1
std1_lim=0.95
pe0_lim=0.5

#time=np.load(analysis_path+'/occupancy.npy')[:, 0]

max_runs=len(os.listdir(raw_data_dir))

#for i in range(max_runs): 
for i in np.array([22]):
    n=i+1
    run_no=n
    file_name="arduino_1_run_" + str(n)
    data_loc=raw_data_dir + file_name 
    wid_set=format(wid[i], '.' + str(digits) + 'E')
    #current_time=np.array(time[i].split(" "))
    print("analyzing file number " + str(run_no))
    try:
        out=subprocess.check_output(["python3", "-i", "sig_gen_analysis.py", data_loc, str(check_mode), str(pmt_ch), str(led_ch), *ch_enable, str(setting), analysis_path, *t_int, *led_t_int, str(v_th), str(int_width), str(bins), str(unit_factor), str(plotting_lim), str(num_pe), str(digits), str(font_size), signal_folder, charge_dist_folder, file_name, str(arduino_setting), str(run_no), occupancy_file, fit_param_file, str(v_set), str(wid_set), str(pe_charge), overflow_file, tr_dir, str(tr_v), str(std0_guess), str(std1_guess), str(std0_lim), str(std1_lim), str(pe0_lim), str(n)])
        print(out)
    except subprocess.CalledProcessError as e: 
        print(e.output)
    except: 
        print('there is an error!')
    

