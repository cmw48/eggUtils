import serial
import sys
import time
import serial.tools.list_ports

serPort = ""
totalPorts = 0
count = 0
eggComPort = ""
eggCount = 0

eggNotFound = True

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

        if "USB VID:PID" in p[2]:  # Looks for "PID" in P[2].
            print "LINUX! there is an air quality egg on " + p[0]
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

# This begins the opening and printout of data from the Adruino.

ser.close()  # In case the port is already open this closes it.
ser.open()   # Reopen the port.

ser.flushInput()
ser.flushOutput()
print "connected to port " + eggComPort

readten = True
readcount = 0

while readten:
  rcv1 = ""
  rcv1 = ser.readline()
  print rcv1
  readcount = readcount + 1
  if readcount > 10:
    readten = False
    
  
  
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

print 'serial closed'
ser.close()
