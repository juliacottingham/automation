import numpy as np
import matplotlib.pyplot as plt
from picosdk.ps3000a import ps3000a as ps
import ctypes
import sys 
import inspect
from operator import itemgetter
import time as t
from picosdk.functions import assert_pico_ok

a=(50, 'mV') #range value and unit for channel A
b=(50, 'mV')
c=(100, 'mV') 
d=(100, 'mV')
#NOTE MAYBE CHANGE THIS SO INSTEAD OF USING TUPLES WITH TEXT JUST PUT ALL VALUES IN MV

ch_enable=np.array([1, 0, 1, 0])

tr_ch='E' #trigger channel
th_v=70 #threshold voltage in mV
tr_dir='rising'

sample_no=256
pre_tr=0.09 #ratio of samples taken before trigger
sample_int=4 #sampling interval in ns
waveform_no=998 
mem_ratio=0.5 #number of segments to create out of all possible segments????

downsampling='none'

default_int=4

status={}
handle=ctypes.c_int16()

status=ps.ps3000aOpenUnit(ctypes.byref(handle), None)

print("Status: " + str(status)) 

if status!=0: 
    print('There was a problem connecting to the picoscope!! Try checking the USB connection')
    sys.exit()
else: 
    print('Picoscope connected!') 

def mv2adc(mv, max_mv):
    max_adc=ctypes.c_int16()
    status=ps.ps3000aMaximumValue(handle, ctypes.byref(max_adc))
    max_adc=max_adc.value
    ret = (mv/max_mv)*max_adc
    return int(round(ret))

def ch(string): 
    if string=='E':
        channel=ps.PS3000A_CHANNEL['PS3000A_EXTERNAL']
    else:
        try:
            string2='PS3000A_CHANNEL_' + string.upper()
            channel=ps.PS3000A_CHANNEL[string2]
        except:
            print('Invalid channel name. Try again, and use A, B, C, D, or E')
            sys.exit()
    return channel

def couple(string): 
    string2='PS3000A_' + string.upper()
    try: 
        ret=ps.PS3000A_COUPLING[string2]
    except: 
        print('Invalid coupling name! Try again, and use AC or DC')
        sys.exit()
    return ret

def psrange(range0, unit): 
    string2='PS3000A_' + str(range0) + unit.upper()
    try: 
        ret=ps.PS3000A_RANGE[string2]
    except: 
        print('Problem with range value! Try again.')
        sys.exit()
    return ret

def tdir(string): 
    string2='PS3000A_' + string.upper()
    try:
        ret = ps.PS3000A_THRESHOLD_DIRECTION[string2]
    except: 
        print('Invalid trigger direction! Use rising, falling, rising_or_falling, above, or below')
        sys.exit()
    return ret

def ch_no(): 
    no=CH_A['enable']+CH_B['enable']+CH_C['enable']+CH_D['enable']
    return no

def valid_int():
    #returns minimum sampling interval allowed for number of channels enabled
    no=ch_no()
    if no<2: 
        ret=1
    if no<3: 
        ret=2
    else: 
        ret=4
    return ret

def gettimebase(interval, sampleNo, segment): 
    
    i=int(interval)
    min_i=valid_int()
    
    if i<min_i:
        
        if i<0: 
            print('Sampling interval must be a positive number!')
        else: 
            print('With ' + str(ch_no()) + ' channels enabled, the minimum sampling rate is ' + str(min_i) + ' ns.')
            print('For lower sampling rates, disable more channels!')
        
        print('Defaulting to lowest possible sampling rate: ' +str(min_i) + ' ns.')
        i=min_i

    if i<6: 
        timebase=np.log2(i)
    else: 
        timebase= (i/8)+2
    
    timebase=round(timebase)
    timebase=int(timebase)

    int2=ctypes.c_float()
    max_samples=ctypes.c_int32()
    tbase=ctypes.c_uint32(timebase)

    ps.ps3000aGetTimebase2(handle, tbase, sampleNo, ctypes.byref(int2), 1, ctypes.byref(max_samples), segment)

    print('Requested sampling interval: ' + str(interval) + ' ns.')
    print('Corresponding timebase: ' + str(timebase))
    print('Closest sampling interval found: ' + str(int2.value) + ' ns')
    print('This corresponds to a maximum sample count of ' + str(max_samples.value) + ' samples.')
    return timebase, int2.value

def my_func(): 
    print('Hello world!')

def samp_mode(string): 
    string2= 'PS3000A_RATIO_MODE_' + string.upper()
    try: 
        ret=ps.PS3000A_RATIO_MODE[string2]
    except: 
        print(str(string) + ' is an invalid downsampling mode') 
        print('Defaulting to downsampling mode "none"') 
        ret=samp_mode('none')
    return ret

mode=samp_mode(downsampling)
#channel = {'ch': channel for func call, 'enable': 0 or 1, 'range': +-50mV, 'offset': analog offset}
e=(5000, 'mV') #range automatically set (cannot be changed)
CH_A={'ch': ch('A'), 'enable': ch_enable[0], 'type': couple('ac'),'range': a, 'psrange': psrange(*a), 'offset': 0}
CH_B={'ch': ch('B'), 'enable': ch_enable[1], 'type': couple('ac'), 'range': b, 'psrange': psrange(*b), 'offset': 0}
CH_C={'ch': ch('C'), 'enable': ch_enable[2], 'type': couple('ac'),'range': c, 'psrange': psrange(*c), 'offset': 0}
CH_D={'ch': ch('D'), 'enable': ch_enable[3], 'type': couple('ac'), 'range': d, 'psrange': psrange(*d), 'offset': 0}
CH_E={'ch': ch('E'), 'range': e}

param=['ch', 'enable', 'type', 'psrange', 'offset']
ps.ps3000aSetChannel(handle, *itemgetter(*param)(CH_A))
ps.ps3000aSetChannel(handle, *itemgetter(*param)(CH_B))
ps.ps3000aSetChannel(handle, *itemgetter(*param)(CH_C))
ps.ps3000aSetChannel(handle, *itemgetter(*param)(CH_D))

th_v_adc=mv2adc(th_v, CH_E['range'][0])
status=ps.ps3000aSetSimpleTrigger(handle, 1, ch('E'), th_v_adc, tdir(tr_dir), 0, 0)
assert_pico_ok(status)
print(status)
max_segment=ctypes.c_uint32()
max_samples0=ctypes.c_int32()
ps.ps3000aGetMaxSegments(handle, ctypes.byref(max_segment))
segments=ctypes.c_uint32(int(max_segment.value*mem_ratio))
ps.ps3000aMemorySegments(handle, segments, ctypes.byref(max_samples0))
max_per_ch=max_samples0.value/ch_no()

print('Maximum memory segments possible: ' + str(max_segment.value))
print('Memory segments actually created: ' + str(segments.value))
print('Maximum samples for each segment: ' + str(max_samples0.value))
print(str(ch_no()) + ' channels currently enabled.')
print('Samples per channel per segment: ' + str(max_per_ch))

#sample_int=input('Enter a sampling interval, and see if it works!')
(timebase, int2)=gettimebase(sample_int, sample_no, 0)

ps.ps3000aSetNoOfCaptures(handle, waveform_no) 
print('Number of captured waveforms set to ' + str(waveform_no))

#data=np.empty((waveform_no, ch_no(), sample_no), dtype=np.dtype('int16'))
data=np.empty((ch_no(), sample_no, waveform_no), dtype=np.dtype('int16'))
#data[:, :]=ctypes.c_int16()
#data_p=data.ctypes.data_as(ctypes.POINTER(ctypes.c_int16()))

for n in range(waveform_no): 
    i=0
    for a, b in enumerate(ch_enable): 
        if b:
            mem=n*ch_no()+i
            ps.ps3000aSetDataBuffer(handle, a, data[n, i].ctypes.data, sample_no, mem, mode)  
            i=i+1

before=round(sample_no*pre_tr)
after=sample_no-before
#param=ctypes.c_void_p()
time=ctypes.c_uint32()
#ps.ps3000aRunBlock(handle, before, after, timebase, 1, None, 0, my_func(), None)
ps.ps3000aRunBlock(handle, before, after, timebase, 1, ctypes.byref(time), 0, None, None)
print('Taking ' + str(waveform_no) + ' captures.')
print('Samples per capture: ' + str(sample_no))
print('Estimated time: ' + str(time.value) + ' ms.')

ready=ctypes.c_int16(0)
check=ctypes.c_int16(0)
while ready.value==check.value:
    ps.ps3000aIsReady(handle, ctypes.byref(ready))
    t.sleep(5.5)
    print(ready.value)
print('Data collection complete!')

overflow=np.empty(mem, dtype=np.dtype('int16'))
samp_no=ctypes.c_int16(sample_no)
ps.ps3000aGetValuesBulk(handle, ctypes.byref(samp_no), 0, mem, 1, mode, overflow.ctypes.data)

times=np.empty(mem, dtype=np.dtype('int64'))
time_unit=ctypes.c_char()

#ps.ps3000aGetValuesTriggerTimeOffsetBulk64(handle, times.ctypes.data, ctypes.byref(time_unit), 0, mem)

#print(times.shape) 
#print(time_unit)

start_time=-before*int2
stop_time=after*int2

t_array=np.arange(start_time, stop_time, int2)[:, np.newaxis] 
#time_array=np.repeat(t_array, waveform_no
time=np.repeat(t_array, waveform_no, axis=1)
print(time.shape)
print(data.shape)

