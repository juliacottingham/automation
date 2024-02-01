import tkinter
from picosdk.ps3000a import ps3000a as ps
import ctypes 
import numpy as np
import matplotlib as mlt
mlt.use('TkAgg')
import matplotlib.pyplot as plt

mem_ratio=0.5
ch_no=2

handle=ctypes.c_int16()
max_segment=ctypes.c_uint32()
max_samples0=ctypes.c_uint32()

ps.ps3000aOpenUnit(ctypes.byref(handle), None)
ps.ps3000aGetMaxSegments(handle, ctypes.byref(max_segment))

print('Maximum segments allowed is ' + str(max_segment))

ratio_arr=np.linspace(0.001, 1, 1000)
#seg_arr=np.empty(ratio_arr.shape)
seg_arr=ratio_arr*max_segment.value
sample_arr=np.empty(seg_arr.shape)

for x, y in enumerate(seg_arr):
    segments=ctypes.c_uint(int(y))
    ps.ps3000aMemorySegments(handle, segments, ctypes.byref(max_samples0))
    sample_arr[x]=max_samples0.value

np.save('segment.npy', seg_arr)
np.save('sample.npy', sample_arr)

plt.plot(seg_arr, sample_arr)
plt.show()
#print('Segments used ' +str(segments.value))
#print('Maximum number of samples ' + str(max_samples0.value))
#print('Which is ' + str(max_samples0.value/ch_no) + ' samples per channel')
"""
ranges=ctypes.c_int32()
length=ctypes.c_int32()
a=ps.ps3000aGetChannelInformation(handle, ps.PS3000A_CI_RANGES, 0, ctypes.byref(ranges), ctypes.byref(length), 0)

print(a)
#ps.ps3000aGetTimebase2
"""
