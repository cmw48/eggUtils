import serial
import sys
import time
import datetime
import serial.tools.list_ports
import traceback
import logging


# declare once
ser = serial.Serial()

#declare pass fail conditions
fwver = '2.2.2'
fwsig = '310547 40166'
timezone = '-4.000000000'

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
        self.firstread = []
        self.macaddr = ''
        self.mqtthost = ''
        self.ssid = ''
        self.tempoff = 0.0
        self.humoff = 0.0
        self.allpass = False
        self.dlfile = ''
        self.data = []



    def introduce(self):
        logging.info ('eggserial {1}, eggtype {2}, firmware version {3}'.format(self, self.eggserial, self.eggtype, self.eggversion))

    def passeggtests(self):
        logging.info ('wdpass {1}, slotpass {2},  spipass {3}, sdpass {4}, sht25pass {5}, rtcpass {6}, esppass {7} '.format(self, self.wdpass, self.slotpass, self.spipass, self.sdpass, self.sht25pass, self.rtcpass, self.esppass))
        if self.wdpass and self.slotpass and self.spipass and self.sdpass and self.sht25pass and self.rtcpass and self.esppass:
            logging.info('PASSED all self tests')

    def rtctest(self):
        if self.ntpok:
            rtcmsg = "PASS - "
        else:
            rtcmsg = "FAIL - "
            rtcmsg = rtcmsg + "tz offset: " + str(self.tzoff) + "  NTP set: " + str(self.ntpok)
            logging.info (rtcmsg)

    def finaltest(self):
        logging.info (self.eggserial)
        logging.info (self.macaddr)
        logging.info (self.mqtthost)
        allpass = True
        if self.eggversion == fwver:
            logging.info ('PASS',)
        else:
            logging.error ('FAIL',)
            allpass = False
        logging.info ('Firmware version ' + self.eggversion)
        if self.rtcpass == True:
            rtcok = True
            if self.tzoff == timezone:
                logging.info ('PASS',)
            else:
                logging.error ('FAIL',)
                rtcok = False
            logging.info ('tz set to ' + self.tzoff)
            if self.ntpok == True:
                logging.info ('PASS - NTP time is correct')
            else:
                logging.info ('FAIL - NTP time differs from local time')
                rtcok = False
            if rtcok:
                logging.info ('PASS - real time clock set up and correct')
            else:
                logging.info ('FAIL - real time clock incorrect')
                allpass = False
        self.rtctest()

        if self.wdpass and self.slotpass and self.spipass and self.sdpass and self.sht25pass and self.rtcpass and self.esppass:
            logging.info ('PASS - all self tests okay')
        else:
            logging.info ('FAIL - self test failure, see below')
            allpass = False
        self.passeggtests()

        if (self.tempoff <> 0) and (self.humoff <> 0):
            print ('PASS - temp and humidity offsets are nonzero')
        else:
            print ('FAIL - temp and/or humidity offsets not entered')

thisEgg = Egg()
filelist = []
lastfile = 0
#myegg = Egg("egg0080huey")
#otheregg = Egg("egg0080louie")
#myegg.introduce()
#otheregg.introduce()

def parseEggData(thisEgg, words):
    ignoreline = False
    numwords = len(words)
    csvdate = ''
    #logging.debug ('debug! number of words ' + str(numwords))

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

            elif words[1] == "Getting":
                if words[2] == "NTP":
                    logging.debug ('debug: ntp test')
                    now = datetime.datetime.now()
                    timehack = now.strftime("%H:%M:%S")
                    ntptime = str(words[4])
                    logging.debug (timehack)
                    logging.debug (ntptime)
                    timehour = timehack[:2]
                    ntphour = ntptime[:2]
                    timemin = timehack[3:5]
                    ntpmin = ntptime[3:5]
                    logging.debug (timemin)
                    logging.debug (ntpmin)
                    if timehour == ntphour:
                        timediff = int(ntpmin)- int(timemin)
                        if abs(timediff) < 5:
                            logging.debug ('Debug!  time is within 5 mins of system time')
                            thisEgg.ntpok = True
                            thisEgg.rtctest()
                        else:
                            logging.debug ('Debug!  RTC time does not match system time')
                            thisEgg.rtctest()

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
                thisEgg.humoff = words[4]

            else:
                # don't set any eggvars
                pass
        except:
            logging.error (sys.exc_info()[0])
            logging.error (traceback.format_exc())

    elif numwords == 3:
        try:

            if words[1] == 'SHT25':
                if words[2]  == 'Initialization...OK.':
                    thisEgg.sht25pass = True

            elif words[1] == 'RTC':
                if words[2]  == 'Initialization...OK.':
                    thisEgg.rtcpass = True

            elif words[1] == 'ESP8266':
                if words[2]  == 'Initialization...OK.':
                    thisEgg.esppass = True

            elif words[0] == "csv:":
                # because this line is 3 words, it's a data row

                #print 'debug: csv!'
                rightnow = datetime.datetime.now()
                csvdate = rightnow.strftime("%m/%d/%y")
                logging.info (csvdate),
                logging.info (str(words[2]))
                #TODO: need a pass fail condition

            elif str(words[2]) == csvdate:
                firstread = { 'serial' : thisEgg.serial, 'time' : str(words[2]), 'temp' : str(words[3]), 'hum' : str(words[4])}
                print firstread
                thisEgg.firstread = firstread
                thisEgg.uploadok = True

            elif words[1] == 'Done':
                if words[2]  == 'downloading.':
                #    print 'Debug!  Download finished.'
                    return 'done'

            else:
                pass
                # do we care about any other two (three) word lines?
        except:
            print sys.exc_info()[0]
            print traceback.format_exc()

    elif numwords == 2:
        try:
            lenfirstword = len(words[0])
            filenametest = str(words[0])
            filenameext = filenametest[-4:]
            if filenameext == ".csv":
                filename = filenametest
                filedate = filenametest[:8]
                filelist.append(filename)
                thisEgg.downloadok = True
                lastfile = len(filelist)
                print 'DEBUG! ' + filename + " , " + filedate
                print 'DEBUG! ' + str(filelist)
                print 'DEBUG! ' + str(lastfile) + ' files found'
            elif words[0] == "csv:":
                logging.info ('writing offline data...')
                # because this line is 2 words, it's a HEADER row
                logging.info (str(words[2:]))
                print 'debug: header row!'
                #rightnow = datetime.datetime.now()
                #csvdate = rightnow.strftime("%m/%d/%y")
                logging.info (csvdate)
                logging.info (str(words[2]))
                #TODO: need a pass fail condition
            else:
                # any other 2 word combination we care about
                pass

        except:
            print sys.exc_info()[0]
            print traceback.format_exc()

    elif numwords <= 1:
        try:
            return 'suppress'

        except:
            print sys.exc_info()[0]
            print traceback.format_exc()

def readserial(ser, numlines):
    parsereturn = ''
    readcount = 0
    readmore = True
    while readmore:
        rcv1 = ""
        rcv1 = ser.readline()
        words = rcv1.split()
        parsereturn = parseEggData(thisEgg, words)
        if parsereturn == 'done':
            print 'Debug! early terminate for readlines'
            readmore = False
        #print rcv1
        #print '(' + str(readcount) + ') ' + str(words)
        #elif parsereturn == 'suppress':
        #   print '.',
        else:
            print '(' + str(readcount) + ') ' + rcv1
        readcount = readcount + 1
        if (readcount > numlines):
            readcount = 0
            readmore = False
            print 'finished reading...'
    print 'read in ' + str(numlines) + ' lines'

def cmd (ser, cmdlist):
    for cmd in cmdlist:
        ser.write(cmd)
        print cmd
        time.sleep(3)
    return 'command list processed...'

def main():

    #logging.basicConfig(filename='eggtest.log', level=logging.INFO)
    logging.basicConfig(filename='eggtest.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
    while True:
        logging.info('Started')


        logging.info ('initializing...')
        serPort = ""
        totalPorts = 0
        portcount = 0
        eggComPort = ""
        eggCount = 0
        processcmd = ""
        eggNotFound = True

        while eggNotFound:

            # Find Live Ports
            ports = list(serial.tools.list_ports.comports())
            totalPorts = len(ports)
            logging.debug ("there are " + str(totalPorts) + " com ports available")

            for p in ports:
                logging.debug (p)# This causes each port's information to be printed out.
                # To search this p data, use p[2].

                if "FTDI" in p[2]:  # Looks for "FTDI" in P[2].
                    logging.debug ("there is an air quality egg on " + p[0])
                    eggComPort = p[0]
                    logging.debug ("Found AQE on " + eggComPort)
                    eggNotFound = False
                    #note- as soon as any egg is found, loop ends.
                    eggCount = eggCount + 1

                if "USB VID:PID" in p[2]:  # Looks for "PID" in P[2].
                    logging.debug ("LINUX! there is an air quality egg on " + p[0])
                    eggComPort = p[0]
                    logging.debug ("Found AQE on " + eggComPort)
                    eggNotFound = False
                    #note- as soon as any egg is found, loop ends.
                    eggCount = eggCount + 1

                if portcount == totalPorts-1:
                    if eggNotFound:
                        logging.debug ("egg not found!")
                        time.sleep(.5)
                    else:
                        logging.debug ("There were " + str(eggCount) + " eggs found.")

                        #portcount = totalPorts  #kick out of this while loop and read ports again

                    #sys.exit() # Terminates Script.
                #portcount = portcount + 1

            time.sleep(2)  # pause before looping again-  check ports again in 2 seconds
        time.sleep(2)  # Gives user 2 seconds to view Port information

        # Set Port
        ser = serial.Serial(eggComPort, 115200, timeout=10) # Put in your speed and timeout value.
        ser.close()  # In case the port is already open this closes it.
        ser.open()   # Reopen the port.

        ser.flushInput()
        ser.flushOutput()
        logging.debug ("connected to port " + eggComPort)
        #CO2 egg has a 16 line header
        #readserial(ser, 16)

        #gas egg has a 21 line header
        #readserial(ser, 21)
        logging.info ("reading header...")
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


        processcmd = cmd(ser, ['restore defaults\n', 'use ntp\n', 'tz_off -4\n', 'backup tz\n', 'ssid WickedDevice\n', 'pwd wildfire123\n', 'exit\n'])
        #processcmd = cmd(ser, ['restore defaults\n', 'use ntp\n', 'tz_off -4\n', 'backup tz\n', 'ssid Acknet\n', 'pwd millicat75\n', 'exit\n'])
        time.sleep(4)
        print thisEgg.rtctest()
        logging.info ("setting NTP time...")
        #print 'bouncing serial port...'
        #ser.close()  # In case the port is already open this closes it.
        #ser.open()   # Reopen the port.
        logging.info ("restarting...")
        readserial(ser, 90)
        ser.close()  # In case the port is already open this closes it.
        ser.open()   # Reopen the port.

        logging.debug ("reconnecting to port " + eggComPort)
        time.sleep(3)


        logging.info('setting offline mode...')
        processcmd = cmd(ser, ['aqe\n'])
        time.sleep(4)
        processcmd = cmd(ser, ['restore defaults\n'])
        time.sleep(3)
        processcmd = cmd(ser, ['opmode offline\n', 'exit\n'])

        logging.info ("restarting...")
        ser.close()  # In case the port is already open this closes it.
        ser.open()   # Reopen the port.
        readserial(ser, 40)
        logging.info ("restarting...")
        ser.close()  # In case the port is already open this closes it.
        ser.open()   # Reopen the port.
        logging.debug ("reconnecting to port " + eggComPort)
        time.sleep(3)
        logging.info ("reading files on SD card...")
        processcmd = cmd(ser, ['aqe\n'])
        time.sleep(4)
        processcmd = cmd(ser, ['list files\n'])
        readserial(ser, 100)
        processcmd = cmd(ser, ['download ' + str(filelist[lastfile-1]) + '\n'])
        readserial(ser, 100)
        logging.debug ('Finished downloading...')
        processcmd = cmd(ser, ['download ' + str(filelist[lastfile]) + '\n'])
        thisEgg.finaltest()
        for csvfilename in filelist:
            processcmd = cmd(ser, ['delete ' + csvfilename + '\n'])
            time.sleep(2)
        logging.info('Finished')

        again = raw_input("press any key to test another egg... ")
        print ("here we go...")
        return

if __name__ == "__main__":
    main()
