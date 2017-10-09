#!/usr/bin/python
#originally written for pyv2

import serial
import sys
import time
import serial.tools.list_ports

def readserial(numlines):
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
        return 'read in ' + numlines + 'lines'



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
ser = serial.Serial(eggComPort, 115200, timeout=10) # Put in your speed and timeout value.

# This begins the opening and printout of data from the Arduino.

ser.close()  # In case the port is already open this closes it.
ser.open()   # Reopen the port.

ser.flushInput()
ser.flushOutput()
print "connected to port " + eggComPort

read16 = True
read102 = True
read200 = True
readcount = 0

#CO2 egg has a 16 line header
print readserial(16)


ser.write('aqe\n')


while read102:
  rcv1 = ""
  rcv1 = ser.readline()
  print rcv1
  readcount = readcount + 1
  if readcount > 102:
    readcount = 0
    read102 = False



#int1 = 0
#str1 = ""
#str2 = ""

#while int1==0:

#   if "\n" not in str1:        # concatinates string on one line till a line feed "\n"
#      str2 = ser.readline()    # is found, then prints the line.
#      str1 += str2
#   print(str1)
#   str1=""
#   time.sleep(.1)


ser.write('restore defaults\n')
time.sleep(2)
ser.write('use ntp\n')
time.sleep(2)
ser.write('tz_off -4\n')
time.sleep(2)
ser.write('backup tz\n')
time.sleep(2)
ser.write('ssid WickedDevice\n')
time.sleep(2)
ser.write('pwd wildfire123\n')
time.sleep(2)
ser.write('exit\n')
time.sleep(2)

print 'closing serial port...'
ser.close()  # In case the port is already open this closes it.
ser.open()   # Reopen the port.


while read200:
  rcv1 = ""
  rcv1 = ser.readline()
  print rcv1
  readcount = readcount + 1
  if readcount > 200:
    readcount = 0
    read200 = False



if __name__ == "__main__":
    main()
