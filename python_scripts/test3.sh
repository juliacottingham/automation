
processed_data_folder="/home/labwork/autocontrol/output_files/sig_gen_test9/processed_data"
python_script="new_final10.py"
check_mode="1"

occupancy_arr="occupancy.npy"
fit_param_arr="fit_param.npy"


python3 -i $python_script $processed_data_folder $occupancy_arr $check_mode $fit_param_arr
