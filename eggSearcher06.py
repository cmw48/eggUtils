#!/usr/bin/python
#originally written for pyv2

import serial
import sys
import time
import serial.tools.list_ports

# declare once with bogus values
ser = serial.Serial()

def readserial(ser, numlines):
    readcount = 0
    readmore = True
    while readmore:
        rcv1 = ""
        rcv1 = ser.readline()
        words = rcv1.split()
        print rcv1
        print words
        readcount = readcount + 1
        if readcount > numlines:
            readcount = 0
            readmore = False
    return 'read in ' + str(numlines) + 'lines'

def rtcinit (ser):
    rtccmd= ['restore defaults\n', 'use ntp\n', 'tz_off -4\n', 'backup tz\n', 'ssid WickedDevice\n', 'pwd wildfire123\n', 'exit\n']
    ser.write('restore defaults\n')
    print 'restore defaults\n'
    time.sleep(2)
    ser.write('use ntp\n')
    print 'use ntp\n'
    time.sleep(2)
    ser.write('tz_off -4\n')
    print 'tz_off -4\n'
    time.sleep(2)
    ser.write('backup tz\n')
    print 'backup tz\n'
    time.sleep(2)
    ser.write('ssid WickedDevice\n')
    print 'ssid WickedDevice\n'
    time.sleep(2)
    ser.write('pwd wildfire123\n')
    print 'pwd wildfire123\n'
    time.sleep(2)
    ser.write('exit\n')
    print 'exit\n'
    time.sleep(2)

def main():

    print 'initializing...'
    serPort = ""
    totalPorts = 0
    count = 0
    eggComPort = ""
    eggCount = 0

    eggNotFound = True
    print 'Ready!'


    while eggNotFound:

        # Find Live Ports
        ports = list(serial.tools.list_ports.comports())
        totalPorts = len(ports)
        print "there are " + str(totalPorts) + " com ports available"

        for p in ports:
            print p # This causes each port's information to be printed out.
            # To search this p data, use p[2].

            if "FTDI" in p[2]:  # Looks for "FTDI" in P[2].
                print "there is an air quality egg on " + p[0]
                eggComPort = p[0]
                print "Found AQE on " + eggComPort
                eggNotFound = False
                #note- as soon as any egg is found, loop ends.
                eggCount = eggCount + 1

            if count == totalPorts-1:
                if eggNotFound:
                    print "egg not found!"
                    time.sleep(.5)
                else:
                    print "There were " + str(eggCount) + " eggs found."


                    #count = totalPorts  #kick out of this while loop and read ports again

                #sys.exit() # Terminates Script.
            #count = count + 1

        time.sleep(2)  # pause before looping again# check ports again in 5 seconds
    time.sleep(2)  # Gives user 5 seconds to view Port information -- can be   changed/removed.

    # Set Port
    ser = serial.Serial(eggComPort, 115200, timeout=30) # Put in your speed and timeout value.

    # This begins the opening and printout of data from the Arduino.

    ser.close()  # In case the port is already open this closes it.
    ser.open()   # Reopen the port.

    ser.flushInput()
    ser.flushOutput()
    print "connected to port " + eggComPort

    #CO2 egg has a 16 line header
    readserial(ser, 16)

    ser.write('aqe\n')

    readserial(ser, 102)



    print 'closing serial port...'
    ser.close()  # In case the port is already open this closes it.
    ser.open()   # Reopen the port.


    readserial(ser, 200)

if __name__ == "__main__":
    main()
