import serial
import sys
import time
import datetime
import serial.tools.list_ports

# declare once
ser = serial.Serial()

class Egg:

    def __init__(self):
        self.eggserial = ''
        self.eggtype = ''
        self.eggversion = ''
        self.tzoff = ''
        self.wdpass = False
        self.slotpass = False
        self.spipass = False
        self.sdpass = False
        self.sht25pass = False
        self.rtcpass = False
        self.esppass = False
        self.firmsig = ''
        self.ntpok = False


    def introduce(self):
        print('eggserial {1}, eggtype {2}, firmware version {3}'.format(self, self.eggserial, self.eggtype, self.eggversion))

    def passeggtests(self):
        print('wdpass {1}, slotpass {2},  spipass {3}, sdpass {4}, sht25pass {5}, rtcpass {6}, esppass {7} '.format(self, self.wdpass, self.slotpass, self.spipass, self.sdpass, self.sht25pass, self.rtcpass, self.esppass))

    def rtctest(self):
        print('tzoff {1}, ntpok {2} '.format(self, self.tzoff, self.ntpok))


thisEgg = Egg()
#myegg = Egg("egg0080huey")
#otheregg = Egg("egg0080louie")
#myegg.introduce()
#otheregg.introduce()

def parseEggData(thisEgg, words):
    ignoreline = False
    numwords = len(words)
    if numwords > 3:
        try:
            if words[1] == "CO2":
                thisEgg.eggtype = 'CO2'

            elif words[1] == "SO2":
                thisEgg.eggtype = 'SO2O3'

            elif words[1] == "NO2":
                thisEgg.eggtype = 'NO2CO'

            elif words[1] == "Firmware":
                thisEgg.eggversion = words[3]

            elif words[1] == 'Serial':
                thisEgg.eggserial = words[3]

            elif words[1] == "TZ":
                thisEgg.tzoff = words[3]

            elif words[1] == "Tiny":
                if words[3]  == 'Initialization...OK.':
                    thisEgg.wdpass = True

            elif words[1] == "Slot":
                if words[4]  == 'Initialization...OK.':
                    thisEgg.slotpass = True

            elif words[1] == 'SPI':
                if words[3]  == 'Initialization...OK.':
                    thisEgg.spipass = True

            elif words[1] == "SD":
                if words[3]  == 'Initialization...OK.':
                    thisEgg.sdpass = True

            elif words[1] == "SHT25":
                if words[2]  == 'Initialization...OK.':
                    thisEgg.sht25pass = True

            elif words[1] == 'RTC':
                if words[2]  == 'Initialization...OK.':
                    thisEgg.rtcpass = True

            elif words[1] == "ESP8266":
                if words[3]  == 'Initialization...OK.':
                    thisEgg.esppass = True

            elif words[1] == "Getting":
                if words[2] == "NTP":
                    print 'debug: ntp test'
                    now = datetime.datetime.now()
                    timehack = now.strftime("%H:%M:%S")
                    ntptime = str(words[4])
                    print timehack
                    print ntptime
                    timehour = timehack[:2]
                    ntphour = ntptime[:2]
                    timemin = timehack[3:5]
                    ntpmin = ntptime[3:5]
                    print timemin
                    print ntpmin
                    if timehour == ntphour:
                        timediff = int(ntpmin)- int(timemin)
                        if abs(timediff) < 5:
                            thisEgg.ntpok = True

            elif words[1] == "Current":
                firmwaresig = str(words[4]) + str(words[5])
                thisEgg.firmsig = firmwaresig

            elif words[0] == "MAC":
                thisEgg.macaddr = words[2]

            elif words[0] == "MQTT":
                if words[1] == "Server":
                    thisEgg.mqtthost = words[2]

            elif words[0] == "Temperature":
                thisEgg.tempoff = words[4]

            elif words[0] == "Humidity":
                thisEgg.tempoff = words[4]

            elif words[0] == "csv:":
                print 'debug: csv!'
                now = datetime.datetime.now()
                csvdate = now.strftime("%m/%d/%y")
                print csvdate
                print str(words[2])
                if str(words[2]) == csvdate:
                    print (str(words[2]) + ', ' + str(words[3]) + ', ' + str(words[4]))
            else:
                # don't set any eggvars
                pass

        except:
            pass
            print sys.exc_info()[0]


def readserial(ser, numlines):
    readcount = 0
    readmore = True
    while readmore:
        rcv1 = ""
        rcv1 = ser.readline()
        words = rcv1.split()
        parseEggData(thisEgg, words)
        #print rcv1
        print '(' + str(readcount) + ') ' + str(words)
        readcount = readcount + 1
        if readcount > numlines:
            readcount = 0
            readmore = False
            print 'finished reading...'
    print 'read in ' + str(numlines) + ' lines'

def cmd (ser, cmdlist):
    for cmd in cmdlist:
        ser.write(cmd)
        print cmd
        time.sleep(2)
    return 'command list processed...'

def main():

    print 'initializing...'
    serPort = ""
    totalPorts = 0
    count = 0
    eggComPort = ""
    eggCount = 0
    processcmd = ""
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

        time.sleep(2)  # pause before looping again-  check ports again in 2 seconds
    time.sleep(2)  # Gives user 2 seconds to view Port information

    # Set Port
    ser = serial.Serial(eggComPort, 115200, timeout=10) # Put in your speed and timeout value.
    ser.close()  # In case the port is already open this closes it.
    ser.open()   # Reopen the port.

    ser.flushInput()
    ser.flushOutput()
    print "connected to port " + eggComPort
    #CO2 egg has a 16 line header
    #readserial(ser, 16)

    #gas egg has a 21 line header
    #readserial(ser, 21)

    #get just enough of header to determine egg type
    readserial(ser, 6)
    #thisEgg.introduce()
    if thisEgg.eggtype == 'CO2':
        #immediately read 10 more lines
        readserial(ser, 10)
    else:
        #gas egg, immediately read 15 more lines
        readserial(ser, 13)

    processcmd = cmd(ser, ['aqe\n'])
    time.sleep(15)


    if thisEgg.eggtype == 'CO2':
        #immediately read 10 more lines
        readserial(ser, 75)
    else:
        #gas egg, immediately read 15 more lines
        readserial(ser, 99)

    # CO2 egg displays 75 lines after AQE
    #readserial(ser, 75)

    # gas egg displays 99 lines after AQE
    #readserial(ser, 99)
    time.sleep(5)

    thisEgg.passeggtests()
    thisEgg.rtctest()

    processcmd = cmd(ser, ['restore defaults\n', 'use ntp\n', 'tz_off -4\n', 'backup tz\n', 'ssid WickedDevice\n', 'pwd wildfire123\n', 'exit\n'])
    #processcmd = cmd(ser, ['restore defaults\n', 'use ntp\n', 'tz_off -4\n', 'backup tz\n', 'ssid Acknet\n', 'pwd millicat75\n', 'exit\n'])

    #print 'bouncing serial port...'
    #ser.close()  # In case the port is already open this closes it.
    #ser.open()   # Reopen the port.

    readserial(ser, 300)

if __name__ == "__main__":
    main()
