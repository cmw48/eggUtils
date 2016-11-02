import serial
import sys
import time
import serial.tools.list_ports

serPort = ""
totalPorts = 0
count = 0
comportInteger = 0
comportnameStr = ""
comportnumberStr = ""
eggNotFound = True

while eggNotFound:

    # Find Live Ports
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print p # This causes each port's information to be printed out.
        # To search this p data, use p[2].
        totalPorts = len(p)
        print "there are " + str(totalPorts) + " com ports available"

   
        while count < totalPorts:   # Loop checks "COM0" to "COM254" for egg Port Info. 

          if "FTDI" in p[2]:  # Looks for "FTDI" in P[1].
            print "EEEEGGGG! on " + p[0]
            comportnumberStr = str() # Converts an Integer to a String, allowing:
            print comportnumberStr
            comportnameStr = p[0]
            #comportnameStr = "COM" + comportnumberStr # add the strings together.
            print "Found AQE on " + comportnameStr
            eggNotFound = False
            count = 255 # Causes loop to end.
            
            
          #if "FTDI" in p[2] and comportnameStr in p[1]: # Looks for "FTDI" and "COM#"
          #   print "Found AQE on " + comportnameStr
          #   count = 255 # Causes loop to end.

          if count == totalPorts-1:
             print "egg not found!"
             count = totalPorts  #kick out of this while loop and read ports again 
             time.sleep(.5)
             #sys.exit() # Terminates Script.
        count = count + 1

    time.sleep(2)  # pause before looping again# check ports again in 5 seconds
time.sleep(2)  # Gives user 5 seconds to view Port information -- can be   changed/removed.

# Set Port
ser = serial.Serial(comportnameStr, 115200, timeout=10) # Put in your speed and timeout value.

# This begins the opening and printout of data from the Adruino.

ser.close()  # In case the port is already open this closes it.
ser.open()   # Reopen the port.

ser.flushInput()
ser.flushOutput()
print "connected to port " + comportnameStr

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