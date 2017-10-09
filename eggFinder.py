import serial
import sys
import time
import serial.tools.list_ports

serPort = ""
count = 0
comportInteger = 0
comportnameStr = ""
comportnumberStr = ""

# Find Live Ports
ports = list(serial.tools.list_ports.comports())
for p in ports:
   print p # This causes each port's information to be printed out.
           # To search this p data, use p[2].



   while count < 255:   # Loop checks "COM0" to "COM254" for egg Port Info.

      if "FTDI" in p[2]:  # Looks for "FTDI" in P[1].
            print "EEEEGGGG! on " + p[0]
            comportnumberStr = str() # Converts an Integer to a String, allowing:
            print comportnumberStr
            comportnameStr = p[0]
            #comportnameStr = "COM" + comportnumberStr # add the strings together.
            print "Found AQE on " + comportnameStr
            count = 255 # Causes loop to end.


      #if "FTDI" in p[2] and comportnameStr in p[1]: # Looks for "FTDI" and "COM#"
      #   print "Found AQE on " + comportnameStr
      #   count = 255 # Causes loop to end.

      if count == 254:
         print "egg not found!"
         sys.exit() # Terminates Script.

      count = count + 1

time.sleep(5)  # Gives user 5 seconds to view Port information -- can be   changed/removed.

# Set Port
ser = serial.Serial(comportnameStr, 115200, timeout=10) # Put in your speed and timeout value.

# This begins the opening and printout of data from the Adruino.

ser.close()  # In case the port is already open this closes it.
ser.open()   # Reopen the port.

ser.flushInput()
ser.flushOutput()
print "connected to port " + comportnameStr

int1 = 0
rcv1 = ""

rcv1 = ser.readline()
print rcv1
str1 = ser.readline()
while int1==0:
   str1 = ser.readline()
   #if "\n" not in str1:        # concatenates string on one line till a line feed "\n"
   #    str2 = ser.readline()    # is found, then prints the line.
   #str1 += str2
   print(str1)
   str1=""
   time.sleep(.1)

#print 'serial closed'
#ser.close()
