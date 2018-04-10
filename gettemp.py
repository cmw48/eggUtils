#!/usr/bin/python
# but not that python, use Anaconda
#
# Copyright (c) 2016 Chris Westling <cmwestling@gmail.com>
# All Rights Reserved
#
# includes the Paho Python MQTT client - find resources at
#     http://www.eclipse.org/paho/
#

# This code is to non-invasively automate the Thermotron temp chamber

#TODO userio to enter an egg serial before each run
#TODO implement raspi

import paho.mqtt.client as paho
import json
import datetime
import time
import sys
import getopt
from pyfirmata import Arduino, util


try:
    board = Arduino('/dev/ttyUSB0', baudrate = 9600)
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
except ValueError:
    print "Could not convert data to an integer."
except:
    print "Unexpected errorC:", sys.exc_info()[0]


#declare a global list of temps
recent_temps=[]
temp_record=[]
deltas=[]


# why does this need to be here instead of in main?
global startblvrun
global M
global msgCount
msgCount = 0

class MQTT_Message:

    def __init__(self):
        self.values = []      # creates a new list of values for each message
        self.tempc = 0

    def getmessage(self, msg_json):
        try:

            self.values = msg_json
            #print(self.values)
            #self.tempc = self.values['raw-instant-value']
            self.tempc = self.values['converted-value']
            self.serialnum = self.values['serial-number']

        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected errorC:", sys.exc_info()[0]


# squawk when subscribe to egg topic is successful
def on_subscribe(client, userdata, mid, granted_qos):
    #print("Subscribed: "+str(mid)+" "+str(granted_qos))
    pass
    #print("gathering data... ready in 10")

# do something as each message is received
# TODO: break all the workywork out of this function and just return the message to the main code
# should this be a Message object?  (it's not really pervasive...)
def on_message(client, userdata, msg):
#pin assignments
# pin 0 is rx , pin 1 is tx
# pin 2 is HIGH when machine is under test
# pin 3 is HIGH when we are heating
# pin 4 is HIGH when we are stable
# pin 5 is HIGH when we enable temp servo control
# pin 6 is HIGH is the flickRGB i/o pin
# pin 7 is HIGH when we enable the COOL/OFF/HEAT servo


    try:
        global isStable
        global startStable
        global stopStable
        global startUnstable
        global stopUnstable
        global stableSince
        global msgCount
        global M
        global lastMessageTimeStamp

        #print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        #samplePayload m = {"serial-number":"egg008028c05e9b0152","converted-value":25.96,"converted-units":"degC","raw-value":25.96,"raw-instant-value":25.96,"raw-units":"degC","sensor-part-number":"SHT25"}
        parsed_msg = json.loads(msg.payload)
        M.getmessage(parsed_msg)
        msgCount = msgCount + 1
        lastMessageTimeStamp = time.time()

        converted_value_temp = (parsed_msg['converted-value'])
        temp_record.append([converted_value_temp, time.time()])
        recent_temps.append(converted_value_temp)

        #raw_instant_temp = (parsed_msg['raw-instant-value'])
        #temp_record.append([raw_instant_temp, time.time()])
        #recent_temps.append(raw_instant_temp)

        # review recent temps and report
        templistlen = len(recent_temps)
        if templistlen <= 10:
          #once we are warmed up, this condition won't be met and this code will not run
          #use this spot to initialize local variables until we get threading working
          # set servopower flag to on
          #board.digital[5].write(1)
          startStable = time.time()
          stopUnstable = time.time()
          stopStable = time.time()
          startUnstable = time.time()
          isStable = False
          #print (str(11-templistlen)+"...")
          # fill up deltaslist
          deltas.append(templistlen)
        elif templistlen > 10 :
          # set servopower flag to off
          #board.digital[5].write(0)

          for x in range (0, 10):
            deltas[x]=(recent_temps[x] - recent_temps[x+1])
          # print(deltas)
          # print(sum(deltas))
          #f.write(str(sum(deltas)))
          #json.dump(recent_temps[10], f)
          recent_temps.pop(0)
          #print(recent_temps[9])
          #print(temp_record)
          tempmsg = ""
          if abs(sum(deltas)) == 0 :
            if isStable :
              tempmsg = (str(recent_temps[9]) + " ...STABLE... " + str(sum(deltas)) + "   " + time.ctime(int(time.time())))
              #board.digital[4].write(1)
            else:
              isStable = True
              #board.digital[4].write(1)
              tempmsg = (str(recent_temps[9]) + "STABILITY LOCK" + str(sum(deltas)) + "   " + time.ctime(int(time.time())))
              startStable = time.time()
              stopUnstable = time.time()
          elif 0 < abs(sum(deltas)) <= 0.05:
            tempmsg = (str(recent_temps[9]) +"  ..stable..  " + str(sum(deltas)) + "   " + time.ctime(int(time.time())))
          elif  0.05 < abs(sum(deltas)) <= 0.1:
            tempmsg = (str(recent_temps[9]) +"   .nominal.  "  + str(sum(deltas)) + "   " + time.ctime(int(time.time())))
          elif 0.1 < abs(sum(deltas)) <= .3:
            if isStable :
              isStable = False
              #board.digital[4].write(0)
              stopStable = time.time()
              startUnstable = time.time()
              tempmsg = (str(recent_temps[9]) + "**NOT STABLE**" + str(sum(deltas)) + "   " + time.ctime(int(time.time())))
            else:
              tempmsg = (str(recent_temps[9]) + "--UNSTABLE-- " + str(sum(deltas)) + "   " + time.ctime(int(time.time())))
          else:
            tempmsg = (str(recent_temps[9]) +" change/slope " + str(sum(deltas)) + "   " + time.ctime(int(time.time())))
            #print(isStable)
          if isStable:
            #board.wickedstepper.step(1)
            stableSince = time.time()-startStable
            print(tempmsg + " stable for the past " + (time.strftime("%H:%M:%S", time.gmtime(stableSince))))
          else:
            #board.wickedstepper.step(-1)
            print(tempmsg + " elapsed... " + (time.strftime("%H:%M:%S", time.gmtime(time.time()-startUnstable))))
          #TODO add blinkrate based on how large sumdeltas error is?
          if (sum(deltas)) > 0:
            # cooling
            #board.digital[3].write(0)
            print "cooling..."
          else:
            # heating
            #board.digital[3].write(1)
            print "heating..."

        else:
          print("templist error, this should never happen.")
    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ValueError:
      print "Could not convert data to an integer."
    except:
      print "Unexpected error:", sys.exc_info()[0]
      #raise

def getEggList(eggseriallist):
    print("processing %d eggs" % len(eggseriallist))
    return eggseriallist

def main(argv):

    debug = False
    #host = "mqtt.opensensors.io"
    #host = "192.168.1.31"
    host = "mqtt.wickeddevice.com"
    client_id = 2940
    keepalive = 60
    port = 1883
    #password = "mXtsGZB5"
    password = "westling123"
    topic = "/orgs/wd/aqe/temperature"
    # eggserial = "egg00802e077f880112"
    eggserial = "egg00802294f10b0142"
    # eggserial = "egg00802fbeaf1b0130"
    listofeggs = ['egg00802e651c1b0130']
    username = "chris"
    #username = "wickeddevice"
    verbose = False


    try:
        opts, args = getopt.getopt(argv, "dh:i:k:p:P:t:e:l:u:v", ["debug", "id", "keepalive", "port", "password", "topic", "eggserial", "eggseriallist", "username", "verbose"])
    except getopt.GetoptError as s:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-i", "--id"):
            client_id = arg
        elif opt in ("-k", "--keepalive"):
            keepalive = int(arg)
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-P", "--password"):
            password = arg
        elif opt in ("-t", "--topic"):
            topic = arg
            print(topic)
        elif opt in ("-e", "--eggserial"):
            eggserial = arg
            print(eggserial)
        elif opt in ("-l", "--eggseriallist"):
            listofeggs = arg
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-v", "--verbose"):
            verbose = True

    if topic == None:
        print("You must provide a topic to clear.\n")
        print_usage()
        sys.exit(2)

    global board
    global M
    global lastMessageTimeStamp
    eggtempdict = {}
    ##MAIN EXECUTION STARTS HERE##
    # TODO: consider this should be a "main" function or __init__ or what the heck?
    eggseriallist = getEggList(listofeggs)
    M = MQTT_Message()
    print("Here we go! Press CTRL+C to exit")
    # reset timers and counts
    prevelapsedruntime = "00:00:00"
    timeSinceLastMessage = time.time()
    lastMessageTimeStamp = time.time()
    prevmsgCount = 0

    try:
        # change power flag to on
        #board.digital[2].write(1)
        print("test running.\n")
        #board.digital[5].write(1)
        #start temp chamber run clock and set blvrun flag
        blvrun = 1
        startblvrun = time.time()
        #assume room temp 25-27c
        #io for data (what needs to be saved?)
        f = open('workfile', 'w')

        client = paho.Client(client_id="2940")
        client.on_subscribe = on_subscribe

        client.username_pw_set(username, password)
        client.connect(host)
        #client.connect("192.168.1.31")
        for eggserial in eggseriallist:
            print("subscribing to temp messages for " + eggserial)
            client.subscribe("/orgs/wd/aqe/temperature/" + eggserial, qos=0)

        # message loop should be one of these (first two down't work for what we want)
        #client.loop_read()
        #client.loop_forever()
        client.loop_start()

        while blvrun:
            #get one message (and do a buncha stuff in that function)
            client.on_message = on_message

            # advance counts and clocks
            elapsedruntime = (time.strftime("%H:%M:%S", time.gmtime(time.time() - startblvrun)))
            timeSinceLastMessage = (time.strftime("%H:%M:%S", time.gmtime(time.time() - lastMessageTimeStamp)))

            # only print time string when it changes (each second)
            if elapsedruntime == prevelapsedruntime:
                sys.stdout.write(" %s  -  %s of %s    last: %s   run: %s \r" % (str(M.tempc),str(msgCount),str(len(eggseriallist)),timeSinceLastMessage,elapsedruntime))
                sys.stdout.flush()
            else:
                if M.tempc != 0:
                    #sys.stdout.write("str(M.tempc) + "  " + str(msgCount) + " of " + str(len(eggseriallist)) + " last: " + timeSinceLastMessage + " run: " + elapsedruntime + "\r")
                    #sys.stdout.write(" %s  -  %s of %s    last: %s   run: %s \r" % (str(M.tempc),str(msgCount),str(len(eggseriallist)),timeSinceLastMessage,elapsedruntime))
                    #sys.stdout.flush()


                    # write/overwrite temp to dict for that serial
                    eggtempdict[M.serialnum] = M.tempc
                if len(eggtempdict) == len(eggseriallist):
                    print(str(len(eggtempdict)) + "-" + str(len(eggseriallist)) + ' - dict is full')
                    blvrun = False
                    #print (eggtempdict)
                    #return eggtempdict

            prevelapsedruntime = elapsedruntime
            # reset message flag


            if (time.time() - lastMessageTimeStamp) < 90 :
                pass
            else:
                print("reconnecting...")
                client.unsubscribe("/orgs/wd/aqe/temperature/" + eggserial)
                client.connect(host)
                #client.connect("192.168.1.31")
                client.subscribe("/orgs/wd/aqe/temperature/" + eggserial, qos=0)
                lastMessageTimeStamp = time.time()
        print ("DONE - ")
        for k, v in eggtempdict.items():
            print(k, v)
        return eggtempdict
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        # change power flag to off
        # change arduino LED to green
        #board.digital[5].write(0)
        #board.digital[4].write(0)
        #board.digital[2].write(0)
        client.loop_stop()
        client.unsubscribe("/orgs/wd/aqe/temperature/" + eggserial)
        json.dump(temp_record, f)
        f.close()


if __name__ == "__main__":
    main(sys.argv[1:])
