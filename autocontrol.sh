#autocontrol.sh is called by run_autocontrol.sh, and it runs python programs to collect and save data based on the parameters there. It also creates a hierarchyof files where the data is saved.

#arguments passed from run_autocontrol.sh (see run_autocontrol.sh for more details)
args=( "$@" ) 
ch_enable=( "${args[@]:0:4}" )
scope_args=( "${args[@]:0:16}" )
folder_name="${args[16]}"
check_mode="${args[17]}"
pmt_ch="${args[18]}"
led_ch="${args[19]}"
freq="${args[20]}"
analysis_args=( "${args[@]:21:12}" )
iteration_var="${args[33]}"
pe_charge="${args[34]}"
std0_guess="${args[35]}"
std1_guess="${args[36]}"
std0_lim="${args[37]}"
std1_lim="${args[38]}"
pe0_lim="${args[39]}"
settings=( "${args[@]:40}" )

tr_v="${scope_args[14]}"
tr_dir="${scope_args[15]}"

#The last arguments are the arduino settings, 
length=$(expr "${#settings[@]} / 3" )
two_length=$(expr "${#settings[@]} / 3 * 2")
arduino_settings=( "${settings[@]:0:$length}" )
echo ${arduino_settings[@]}
#echo $two_length
#echo $length
amp=( "${settings[@]: $length:$length}" )
echo ${amp[@]}
wid=( "${settings[@]: $two_length:$length}" ) 
echo ${wid[@]}
main_dir=$(pwd)

arduino_dir="$main_dir/sketchbook" #this is where the Makefile is for the arduino program
data_dir="$main_dir/output_files" #this is where the folder of data is saved
scope_dir="$main_dir/python_scripts" #directory of python scripts

#for each folder in data_dir there is a raw_data_folder and a processed_data folder, each containing the raw and processed data, respectively
raw_data_folder="raw_data" 
processed_data_folder="processed_data" 
signal_folder="signal" #under processed_data_folder, contains pictures of the plotted signal from the oscilloscope
charge_dist_folder="charge_distribution" #under processed_data_folder, contains pictures of the charge distribution and the fit 

script_name="oscilloscope.py"         #controls oscilloscope
analysis_name="analysis.py" #runs analysis after each data collection
final_name="final.py"       #name of script that runs analysis after all data collection is completed 
sig_gen_name="sig_gen_on.py"        #name of script that turns on the signal generator, sets the load to 50 ohms, and sets the voltage amplitude of the pulse and the duration of the pulse
off_script="sig_gen_off.py"         #name of script that turns of signal generator

screen_name="arduino_screen"     #set in the Makefile under sketchbook (name of 'screen' instance where the program communicates with the Arduino)
log_name="arduino_log"           #can be changed in Makefile under sketchbook, log of screen input and output

occupancy_name="occupancy.npy"   #name of file containing occupancy array under processed_data_folder
param_name="fit_param.npy"       #contains all the fitted parameeters from the charge distribution and their uncertainties 
overflow_name="overflow.npy"     #has information on whether there was an overflow in any given waveform collected

get_dir(){
	
	#get_dir() looks to see if the directory that was input to run_autocontorl.sh already exists. if so, and if check_mode=1, the program prompts the user either to continue with this directory or choose another one. Sets up the directory hierachy (raw_data_folder and processed_data_folder under this directory

	dir_exists=0
	
	if [ -d "$data_dir/$folder_name" ]; then
		dir_exists=1
		continue_var=0
		if [ $check_mode = 1 ]; then
			echo "Folder $folder_name exists. Are you sure you want to continue saving data here?"
		 	read variable
		else 
			variable="y"
		fi
		
		while [ $continue_var = 0 ]; 
		
		do 
			
			if [ $variable = "y" ] || [ $variable  = "Y" ]; then 
					
				#continue_var=1
				break

			fi	

			if [ $variable = "n" ] || [ $variable = "N" ]; then 
				echo "Enter new folder name here:"
				read folder_name
				#continue_var=1
				get_dir
				break
					
			else 
				echo "Invalid input! type Y or N"
			fi
			
			read variable
		done			


	else 
		cd $data_dir 
		mkdir "$folder_name"
	
		cd $folder_name 
		mkdir $raw_data_folder
	        raw_data_dir="$data_dir/$folder_name/$raw_data_folder"	

	fi
	
	if [ -d "$data_dir/$folder_name/$raw_data_folder" ]; then
		echo "Found data folder..."
		raw_data_dir="$data_dir/$folder_name/$raw_data_folder"
	else 
		cd "$data_dir/$folder_name"
		mkdir $raw_data_folder
		raw_data_dir="$data_dir/$folder_name/$raw_data_folder"
	fi

	if [ -d "$data_dir/$folder_name/$processed_data_folder" ]; then 
		echo "Found processed data folder..."
		processed_data_dir="$data_dir/$folder_name/$processed_data_folder"
	else 
		cd "$data_dir/$folder_name"
		mkdir $processed_data_folder
		processed_data_dir="$data_dir/$folder_name/$processed_data_folder"
		cd $processed_data_dir
		mkdir $signal_folder 
		mkdir $charge_dist_folder
	fi


}

#activate pmt_env virtual environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate pmt_env

#set current setting of arduino to an arbitrary value until it is moved, when it will be known what it is 
current_setting=0
current_voltage=0
current_wid=0

arduino_start(){
	
	#Create a screen instance so that the setting of the Arduino can be changed and the serial output from the arduino can be read

	cd $arduino_dir
	
	if ls | grep $log_name; then 
		#clear log file so it won't contain anything from past runs
		rm $log_name
	fi
	
	#make the Makefile in $arduino_dir
	make upload monitor
	
	if screen -ls | grep $screen_name; then 	
		echo "Serial communication opened!"
		echo "Connection on screen named $screen_name"
	fi
	sleep 2
	
	screen -S $screen_name -X logfile flush 1
}

arduino_stop(){
	
	#move the arduino to setting 7 (this way if the arduino is unplugged after this program is run, it will not be too close to the edges of the track and fall off)
	arduino_set 7
	#get rid of screen
	screen -S $screen_name -X quit
        screen -wipe	
	cd $arduino_dir
	make clean
}

arduino_set(){
	#Input the arduino setting given as the first input after running the function, and then search the output from the Arduino for confirmation that this setting has actually been reached. Update $current_setting.
	
	setting=$1
	
	echo "Input setting is $setting"	

	if [ $current_setting != $setting ]; then
		
		screen -S $screen_name -X stuff $setting
		tail -n0 -f "$arduino_dir/$log_name" | sed '/'"$setting"' Finished/ q'
		current_setting=$setting
	fi	
}

sig_gen_set(){
	#Sets the amplitude (in V) and width (in ns) of the pulse

	set_amp=$1
	set_wid=$2
	
	if [ $current_voltage != $set_amp ] || [ $current_wid != $set_wid ]; then
		python3 "$scope_dir/$sig_gen_name" $set_amp $set_wid $freq
		current_voltage=$set_amp
		current_wid=$set_wid
	fi

}

get_data(){
	#Calls the python program that takes data from the oscilloscope. 

	if [ $check_mode == 1 ]; then 
		python3 -i "$scope_dir/$script_name" ${scope_args[@]} $file_path $overflow_path
	else
		python3 "$scope_dir/$script_name" ${scope_args[@]} $file_path $overflow_path
	fi
	
	if [ $check_mode == 1 ]; then
		
		#If it is check mode, after the graph is shown, there is an option to retake the data and rewrite the data currently displayed. Mostly used if I am adjusting the voltage to get a certain occupancy I want to measure at.
		echo "This is check mode"
		python3 -i "$scope_dir/$analysis_name" $file_path $check_mode $pmt_ch $led_ch ${ch_enable[@]} ${arduino_settings[i]} $analysis_path ${analysis_args[@]} $signal_folder $charge_dist_folder $file_name ${arduino_settings[$i]} $run_no $occupancy_name $param_name $current_voltage $current_wid $pe_charge $overflow_path $tr_dir $tr_v $std0_guess $std1_guess $std0_lim $std1_lim $pe0_lim $(date)
		
		echo 'Type r if you want to retake data, and c to continue' 
		
		while [ 0 = 0 ];
		do
			read retake_var 

			if [ $retake_var = "r" ]; then
			
				get_data
				break
			
			elif [ $retake_var = "c" ]; then 

				break
			else
				echo "Invalid input!! Type r or c"
			fi	

		done
	else 
		python3 "$scope_dir/$analysis_name" $file_path $check_mode $pmt_ch $led_ch ${ch_enable[@]} ${arduino_settings[i]} $analysis_path ${analysis_args[@]} $signal_folder $charge_dist_folder $file_name ${arduino_settings[$i]} $run_no $occupancy_name $param_name $current_voltage $current_wid $pe_charge $overflow_path $tr_dir $tr_v $std0_guess $std1_guess $std0_lim $std1_lim $pe0_lim $(date)
	fi
	
	#putting this here so that the graphs update as more data is taken
	if [ $check_mode == 1 ]; then 
		python3 -i "$scope_dir/$final_name" $processed_data_dir $occupancy_name $check_mode $param_name
	else 
		python3 "$scope_dir/$final_name" $processed_data_dir $occupancy_name $check_mode $param_name
fi

}

#set up directories for data
get_dir

#establish communication with arduino
arduino_start


#loop through each set of waveforms to take and save data

for n in $(seq 1 $iteration_var); do
	
	for i in ${!arduino_settings[@]}; do

		no_files=$(ls $raw_data_dir | wc -l)
		run_no=$(expr 1 + $no_files)
	
		file_name="arduino_${arduino_settings[$i]}_run_$run_no"
		file_path="$raw_data_dir/$file_name"
		overflow_path="$processed_data_dir/$overflow_name"
		analysis_path="$processed_data_dir"

		arduino_set ${arduino_settings[$i]}
		sig_gen_set ${amp[$i]} ${wid[$i]}

		sig_gen_val=$(<do_not_delete.txt)
		
		if [ $sig_gen_val == 0 ]; then
			
			arduino_stop
			echo "There has been an error with the signal generator!" 
			echo "Try turning it on and then off"

			echo "Data collection cancelled."
			
			
			exit 
		
		fi
		
		echo 'Now running data collection!!'

		get_data
		
	done	
done

arduino_stop

python3 "$scope_dir/$off_script"

#final analysis once all of the data is taken 

