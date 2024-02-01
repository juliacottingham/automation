import sys
import tkinter
try:
    import matplotlib as mlt
    mlt.use('TKAgg')
    import matplotlib.pyplot as plt
except: 
    print('Please activate pmt_env virtual environment before running.')
    sys.exit()
import numpy as np
from picosdk.ps3000a import ps3000a as ps
import ctypes
import inspect
from operator import itemgetter
import time as t
from picosdk.functions import adc2mV, assert_pico_ok

#RUNS IN PMT_ENV! make sure to 'conda activate pmt_env' before running

#range in mV for each channel
a=100
b=50
c=200 
d=100

#1 is enabled, 0 is disabled, order is A, B, C, D
ch_enable=np.array([0, 0, 1, 0])

tr_ch='CH_C' #trigger channel (write as 'CH_letter')
th_v=-70 #threshold voltage in mV
tr_dir='rising' #trigger direction

sample_no=256 #no. of samples per waveform
pre_tr=0.09 #ratio of samples taken before trigger
sample_int=4 #sampling interval in ns
#mem_ratio=1 #number of segments to create out of all possible segments????
waveform_no=(10**6)+20 #NOTE: test how large this can be compared to maximum segments and then make a for-loop for taking more data than segments
downsampling='none'

default_int=4
default_ch='A'
default_coupling='AC'
default_range=100
default_dir='rising'
default_samp='none'

status={}
handle=ctypes.c_int16()

status=ps.ps3000aOpenUnit(ctypes.byref(handle), None)

print("Status: " + str(status)) 

if status!=0: 
    print('There was a problem connecting to the picoscope!! Try checking the USB connection')
    print('Also check if you have picoscope software open.')
    print('Or if anyone else is taking measurements remotely')
    sys.exit()
else: 
    print('Picoscope connected!') 

######################################################################


def mv2adc(mv, ch):
    """
    Takes voltage in mV and turns it into ADC
    Useful for setting trigger level
    """
    #find max adc
    max_adc=ctypes.c_int16()
    status=ps.ps3000aMaximumValue(handle, ctypes.byref(max_adc))
    
    assert_pico_ok(status)    
    max_mv=ch['range']
    max_adc=max_adc.value
    ret = (mv/max_mv)*max_adc
    return int(round(ret))

def adc2mv_2(adc, ch): 
    """
    Takes data in ADC and converts it to mV
    """

    max_adc=ctypes.c_int16()
    s=ps.ps3000aMaximumValue(handle, ctypes.byref(max_adc))
    assert_pico_ok(s)

    max_mv=float(ch['range'])
    max_adc=float(max_adc.value)
    adc=adc.astype('float')
    
    mv=(adc/max_adc)*max_mv
    return mv


def ch(string): 
    """
    Goes from channel in form "A" to form PS3000A_CHANNEL['PS3000A_CHANNEL_A']
    """
    if string=='E':
        channel=ps.PS3000A_CHANNEL['PS3000A_EXTERNAL']
    else:
        try:
            string2='PS3000A_CHANNEL_' + string.upper()
            channel=ps.PS3000A_CHANNEL[string2]
        except:
            print('Invalid channel name.')
            print('Defaulting to channel '+ default_ch)
            channel=ch(default_ch)
    return channel

def couple(string): 
    """
    Takes coupling from string form 'AC' or 'DC' to PS3000A_COUPLING['PS3000A_AC']
    
    """
    string2='PS3000A_' + string.upper()
    try: 
        ret=ps.PS3000A_COUPLING[string2]
    except: 
        print('Invalid coupling name! Try again, and use AC or DC')
        print('Defaulting to default coupling ' + default_coupling)
        ret=couple(default_coupling)
    return ret

def psrange(range0): 
    """
    Takes range of channel in mV and converts it to PS3000A_RANGE['PS3000A_20MV']
    """

    unit='MV'
    if range0>500:
        range0=range0/1000    
        unit='V'

    string2='PS3000A_' + str(range0) + unit.upper()
    try: 
        ret=ps.PS3000A_RANGE[string2]
    except: 
        print('Problem with range value! Next time use 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, or 200000 mV')
        print('Defaulting to ' + default_range)
        ret=psrange(default_range)
    return ret

def tdir(string): 
    """
    Formatting trigger direction into PS3000A_THRESHOLD_DIRECTION to input into triggering function
    """

    string2='PS3000A_' + string.upper()
    try:
        ret = ps.PS3000A_THRESHOLD_DIRECTION[string2]
    except: 
        print('Invalid trigger direction! Use rising, falling, rising_or_falling, above, or below')
        print('Defaulting to trigger direction ' + default_dir)
        ret=tdir(default_dir)
    return ret

def ch_no(): 
    """
    Returns the number of channels enabled
    """
    no=CH_A['enable']+CH_B['enable']+CH_C['enable']+CH_D['enable']
    return no

def valid_int():
    """
    returns minimum sampling interval allowed for number of channels enabled
    based on info from ps3000a user manual
    """
    no=ch_no()
    if no<2: 
        ret=1
    if no<3: 
        ret=2
    else: 
        ret=4
    return ret

def gettimebase(interval, sampleNo, segment): 
    
    """
    Gets timebase number for functions from a given interval in ns
    """
    
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

    s=ps.ps3000aGetTimebase2(handle, tbase, sampleNo, ctypes.byref(int2), 1, ctypes.byref(max_samples), segment)
    assert_pico_ok(s)
    print('Requested sampling interval: ' + str(interval) + ' ns.')
    print('Corresponding timebase: ' + str(timebase))
    print('Closest sampling interval found: ' + str(int2.value) + ' ns')
    print('This corresponds to a maximum sample count of ' + str(max_samples.value) + ' samples.')
    return timebase, int2.value

def samp_mode(string): 
    """
    Puts downsampling mode in a PS3000A_RATIO_MODE form to input into functions
    """

    string2= 'PS3000A_RATIO_MODE_' + string.upper()
    try: 
        ret=ps.PS3000A_RATIO_MODE[string2]
    except: 
        print(str(string) + ' is an invalid downsampling mode') 
        print('Defaulting to downsampling mode '+ default_samp) 
        ret=samp_mode(default_samp)
    return ret

def mem_segments(waveforms, samples): 
    
    if ch_no()==3:
        factor=4
        #according to user manual number of samples per segment should be divided by 4 for 3 channels
    else: 
        factor=ch_no()
    
    sample_no=samples*factor

    max_segments=ctypes.c_uint32()
    max_samples=ctypes.c_int32()

    s=ps.ps3000aGetMaxSegments(handle, ctypes.byref(max_segments))
    assert_pico_ok(s)

    if waveforms>max_segments.value: 
        guess=max_segments.value
    else: 
        guess=waveforms
    
    s=ps.ps3000aMemorySegments(handle, guess, ctypes.byref(max_samples))
    assert_pico_ok(s)

    while sample_no>max_samples.value: 
        
        guess=guess*(max_samples.value/sample_no)
        guess=int(guess)
        
        s=ps.ps3000aMemorySegments(handle, guess, ctypes.byref(max_samples))
        assert_pico_ok(s)
        
    
    print('Maximum memory segments is :' + str(max_segments.value))
    print('Memory segments allocated: ' + str(guess))
    print('Max samples allowed: ' + str(max_samples.value/ch_no()))
    print('No of waveforms :' + str(waveforms))
    
    
    if waveforms<guess: 
        print('Constrained to less buffers than waveforms! Program will run several blocks.')
        
    runblock_captures=np.full(int(waveforms/guess), guess)

    if waveforms%guess!=0:
        runblock_captures=np.append(runblock_captures, waveforms%guess)

    return runblock_captures


mode=samp_mode(downsampling)

#channel = {'ch': channel for func call, 'enable': 0 or 1, 'range': +-50mV, 'offset': analog offset}
e=5000 #range automatically set (cannot be changed)
CH_A={'ch': ch('A'), 'enable': ch_enable[0], 'type': couple('ac'),'range': a, 'psrange': psrange(a), 'offset': 0}
CH_B={'ch': ch('B'), 'enable': ch_enable[1], 'type': couple('ac'), 'range': b, 'psrange': psrange(b), 'offset': 0}
CH_C={'ch': ch('C'), 'enable': ch_enable[2], 'type': couple('ac'),'range': c, 'psrange': psrange(c), 'offset': 0}
CH_D={'ch': ch('D'), 'enable': ch_enable[3], 'type': couple('ac'), 'range': d, 'psrange': psrange(d), 'offset': 0}
CH_E={'ch': ch('E'), 'range': e}
CH_ALL=np.array([CH_A, CH_B, CH_C, CH_D])

param=['ch', 'enable', 'type', 'psrange', 'offset']

for c in CH_ALL: 
    s=ps.ps3000aSetChannel(handle, *itemgetter(*param)(c))
    assert_pico_ok(s)

#threshold voltage in adc
th_v_adc=mv2adc(th_v, locals()[tr_ch])
s=ps.ps3000aSetSimpleTrigger(handle, 1, locals()[tr_ch]['ch'], th_v_adc, tdir(tr_dir), 0, 1000)
assert_pico_ok(s)

block=mem_segments(waveform_no, sample_no) 
print(block)

data_adc=np.empty((waveform_no, ch_no(), sample_no), dtype=np.dtype('int16'))

#################################################################################################

(timebase, int2)=gettimebase(sample_int, sample_no, 0)

for no, capture in enumerate(block):

    s=ps.ps3000aSetNoOfCaptures(handle, capture) 
    assert_pico_ok(s)
    print('Number of captured waveforms set to ' + str(capture))

#empty array initialized to hold data
    #data_adc=np.empty((waveform_no, ch_no(), sample_no), dtype=np.dtype('int16'))
    
    offset=sum(block[0:no])

    for n in range(capture): 
        i=0
        for a, b in enumerate(ch_enable): 
            if b:
                mem=n
                s=ps.ps3000aSetDataBuffer(handle, a, data_adc[n+offset, i].ctypes.data, sample_no, mem, mode)
                assert_pico_ok(s)
                i=i+1

    before=round(sample_no*pre_tr)
    after=sample_no-before

    time=ctypes.c_uint32()

    s=ps.ps3000aRunBlock(handle, before, after, timebase, 1, ctypes.byref(time), 0, None, None)
    assert_pico_ok(s)

    print('Taking ' + str(capture) + ' captures.')
    print('Iteration ' + str(no+1) + ' out of ' + str(block.size))
    print('Samples per capture: ' + str(sample_no))
    print('Estimated time: ' + str(time.value) + ' ms.')
    print('Note: data taking usually takes longer than estimated time.')
    print("Remember that the trigger must be on in order to take data!!! If the trigger isn't on, this program will wait indefinitely for data!")

    ready=ctypes.c_int16(0)
    check=ctypes.c_int16(0)

    print('Taking data...')
    while ready.value==check.value:
        s=ps.ps3000aIsReady(handle, ctypes.byref(ready))
        assert_pico_ok(s)
    print('Data collection complete!')

    overflow=np.empty(mem, dtype=np.dtype('int16'))
    samp_no=ctypes.c_int16(sample_no)
    
    print('Retrieving data...')
    s=ps.ps3000aGetValuesBulk(handle, ctypes.byref(samp_no), 0, mem, 1, mode, overflow.ctypes.data)
    assert_pico_ok(s)
    print('Data retrieved successfully')

    #empty array for data in mV

print('For loop begins...')
data=np.empty(data_adc.shape, dtype='float32')
i=0
for x, y in enumerate(ch_enable):
    if y:
        data[:, i]=adc2mv_2(data_adc[:, i], CH_ALL[x])
        i=i+1
print('For loop ends')

del data_adc

print('Here is the status code: ' + str(status))

#times=np.empty(sample_no, dtype=np.dtype('int64'))
#time_unit=ctypes.c_char()

start_time=-before*int2
stop_time=after*int2

t=np.arange(start_time, stop_time, int2)
#t=t[np.newaxis, :, np.newaxis] 
#time=np.repeat(t_array, waveform_no, axis=2)


data=np.moveaxis(data, (0, 1, 2), (2, 0, 1))
#data=np.concatenate((t, data), axis=0)

print(data.shape)
#np.save('file.npy', data)


ps.ps3000aStop(handle)
ps.ps3000aCloseUnit(handle)

print('A graph should appear...')
plt.figure()
plt.title('Channel A')
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (mV)')
#plt.plot(data[0, :, 0], data[1, :, :])
#plt.plot(data[0, :, 0], data[2, :, :])
plt.plot(t, data[:, :, 0])

"""
plt.figure()
plt.title('Channel C')
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (mV)')
#plt.plot(data[0, :, 0], data[2, :, :])
plt.plot(t, data[:, :, 0])
"""
plt.show()


