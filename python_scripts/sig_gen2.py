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
        print ('failed to connect to ip ' + remote_ip)
        print('OPEN AUTOCONTROL/SIG_GEN.PY AND CHANGE IP ADDRESS OF SIGNAL GENERATOR')
    return s

def SocketQuery(Sock, cmd):
    try :
        #Send cmd string
        Sock.sendall(cmd)
        Sock.sendall(b'\n')
        time.sleep(1)
    except socket.error:
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
    
    SocketSend(s, "C1:OUTP OFF")
    
    SocketClose(s)
    print('Complete. Exiting program')
    sys.exit

if __name__ == '__main__':
    proc = main()
