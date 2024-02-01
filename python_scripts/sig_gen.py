#!/usr/bin/env python
#-*- coding:utf-8 –*-
#-----------------------------------------------------------------------------
# The short script is a example that open a socket, sends a query,
# print the return message and closes the socket.
#
#No warranties expressed or implied
#
#SIGLENT/JAC 05.2018
#
#-----------------------------------------------------------------------------
import socket # for sockets
import sys # for exit
import time # for sleep

try: 
    import psutil 

except: 
    raise RuntimeError("ACTIVATE PMT_ENV")
#-----------------------------------------------------------------------------

remote_ip = "172.16.175.154" # should match the instrument’s IP address
port = 5024 # the port number of the instrument service
#Port 5024 is valid for the following:
#SIGLENT SDS1202X-E, SDG2X Series, SDG6X Series
#SDM3055, SDM3045X, and SDM3065X 
#
#Port 5025 is valid for the following:
#SIGLENT SVA1000X series, SSA3000X Series, and SPD3303X/XE


amp=float(sys.argv[1]) 
wid=float(sys.argv[2])*(10**(-9))
freq=float(sys.argv[3])

f=open('do_not_delete.txt', 'w')

f.write("1")
f.close()
count = 0

def SocketConnect():
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print ('Failed to create socket.')
        sys.exit();
    try:
        #Connect to remote server
        s.connect((remote_ip , port))
    except socket.error:
        print('failed to connect to ip ' + remote_ip)
        print('Signal generator voltage NOT changed to ' + str(amp) + ' V.')
        print('Signal generator width NOT changed to ' + str(wid) + ' s.')
        print("Program exiting")
        
        f=open("do_not_delete.txt", "w")
        f.write("0")
        f.close()
    return s

def SocketQuery(Sock, cmd):
    try :
        #Send cmd string
        Sock.sendall(cmd)
        Sock.sendall(b'\n')
        time.sleep(1)
    except socket.error:
        print('failed to connect to ip ' + remote_ip)
        print('Signal generator voltage NOT changed to ' + str(amp) + ' V.')
        print('Signal generator width NOT changed to ' + str(wid) + ' s.')
        print("Program exiting")
        
        f=open("do_not_delete.txt", "w")
        f.write("0")
        f.close()
        #Send failed
        print ('Send failed')
        sys.exit()
    
    reply = Sock.recv(4096)
    return reply

def SocketSend(Sock, cmd):
    try:
        cmd = cmd + '\n'
        Sock.sendall(cmd.encode('latin1'))
        time.sleep(1)
    except socket.error:
        print('Send failed.')
        
        print('failed to connect to ip ' + remote_ip)
        print('Signal generator voltage NOT changed to ' + str(amp) + ' V.')
        print('Signal generator width NOT changed to ' + str(wid) + ' s.')
        print("Program exiting")
        
        f=open("do_not_delete.txt", "w")
        f.write("0")
        f.close()
 
        sys.exit()

def SocketClose(Sock):
    #close the socket
    Sock.close()
    time.sleep(1)

def main():
    global remote_ip
    global port
    global count
    global p
    # Body: send the SCPI commands *IDN? 10 times and print the return message
    s = SocketConnect()
    
    SocketSend(s, "C1:OUTP OFF,LOAD,50")
    string="C1:BSWV WVTP,PULSE,FRQ,%s,LLEV,0,HLEV,%s,WIDTH,%s" % (freq, amp, wid)
    print('Here is the command sent to the socket')
    print(string)
    SocketSend(s, string)
    #wait(1)
    #time.sleep(2)
    
    p=SocketQuery(s, b'C1:BSWV?')
    print('Here is the socket query\n')
    print(p)
    print('\n')
    
    SocketSend(s, "C1:OUTP ON,LOAD,50")
    """
    p=SocketQuery(s, b'C1:BSWV?')
    print('Here is the second socket query\n')
    print(p)
    print('\n')
    
    a=SocketQuery(s, b'SYST:COMM:LAN:MAC?')
    print('MAC address of signal generator: ')
    print(a)
    """
    index0=p.find(b'AMP,') + 4 
    index1=p.find(b',AMPVRMS,')

    current_amp=p[index0:index1].decode('latin1')

    index2=p.find(b'WIDTH,') + 6
    index3=p.find(b',RISE,')

    current_wid=p[index2:index3].decode('latin1')

    #add code which states the parameters of the signal generator
    print('Amplitude set to ' + current_amp)
    print('Width set to ' + current_wid + ' s.')

    """
    for i in range(10):
        qStr = SocketQuery(s, b'*IDN?')
        print (str(count) + ":: " + str(qStr))
        count = count + 1
    """


    SocketClose(s)
    print('Complete. Exiting program')
    sys.exit

if __name__ == '__main__':
    proc = main()
