#################################################################
#    DMX.py v2.0
#
# Digistar control of QLC+, and theatre lighting 
# 
# Created: 2/26/2022
# Created by Matt Ricks (mricks1@alpinedistrict.org)

# QLC+ is a free and cross-platform software to control DMX or analog lighting systems like moving heads, dimmers, scanners etc.
# https://www.qlcplus.org created by Heikki Junnila & Massimo Callegari

# QLC+ can be controlled via websockets.  Digistar is able to run a Python environment, enabling the use of websockets.
# This project combines both, in order to allow Digistar to control DMX lighting systems without the need for a "Black Box"

# This has been tested with the following versions:
# Windows 10.0.19044
# Python 3.8.0
# Digistar 7.22.02
# Websockets 10.0
# QLC+ 4.12.4

# ---Digistar Setup---
# Follow the steps in the Digistar User's Guide in the following path:
# Scripting Reference / Python Scripting / Setup Python to Run on Digistar
# Make sure Python is enabled on startup

# ---QLC+ Setup---
# Follow these steps taken from https://www.qlcplus.org/docs/html_en_EN/commandlineparameters.html
# 1. Create a shortcut of qlcplus.exe (usually located in C:\QLC+) on your desktop.
# 2. Right click on the shortcut and select "Properties".
# 3. In the "Target" field you will see something like "C:\QLC+\qlcplus.exe".
# 4. There you can add "-w" as the command line parameter. This enables websockets on QLC+ on the default port 9999

# ---Python Setup---
# Install websocket-client via pip
# Add the DMX.py script to $Content/User/Python
# Set the "websocketURL" variable equal to the websocket URL for QLC+
# Set the "updateTime" variable equal to whatever update time you need.  This will poll Digistar for any new messages
# (For "updateTime" The time is in millisecs.  A lower number is a faster, but can take more processing)


# The following are digistar commands
# To import the script into the Python Environment in Digistar, enter the following command.  You should see "DMX Imported" when successful
# py com "import DMX"
# You can put this in the startup.ds script if that floats your boat

# The commands used are directly taken from the QLC+ API, and prepended with "DMX " to signal to the python program that it is a lighting command
# See https://www.qlcplus.org/Test_Web_API.html for more information about the API
# To change a specific channel, type in "CH|channelNumber|channelValue".
# py control "DMX CH|1|2"

# To change a specific widget in QLC+, type in "widgetID|widgetValue".
# For instance, if I had a button widget configured on QLC+ whose ID was 1, I would "click" that button by sending the following command
# py control "DMX 1|255"
# if you'd like to send more than one command to QLC+, then you can chain together strings with \n like the following
# which will set widget 1 to 255, and widget 2 to 100 (note that the "DMX " string is used only at the very beginning)
# py control "DMX 1|255\n2|100"

# To end the communication with QLC+, you may either issue a fadestopreset command, or send an "end" control message like so:
# py control "end"
# Note: Fadestopreset is commented out in this code, so that this script will persist.  The only way to end it is with "end"

# ---Known bugs---
# There is no graceful handling of strings that do not comply with the QLC+ API

#################################################################

websocketURL = "ws://localhost:9999/qlcplusWS" 
updateTime = 250

import websocket
import time

def getDSMessage(ws):
    stopDMX = False
    while True:
        if stopDMX:
            print("stopping")
            ws.keep_running = False
            ws.close()
            break;
        time.sleep(updateTime/1000)
        sCommand = Ds.GetCommand();
        if sCommand != '':
            # if sCommand.startswith('fadestopreset'):
            #     stopDMX = True
            #     print('Stopping DMX Processing due to fadestopreset')
            if sCommand.startswith("DMX"):
                print(sCommand)
                if sCommand.startswith("DMX end"):
                    stopDMX = True
                    print('Stopping DMX Processing due to end command')
                sCommand = sCommand.replace("\\n",'\n')
                sCommand = sCommand[4:]
                print(sCommand)

                lines = sCommand.split("\n")
                for line in lines:
                    print(line)
                    ws.send(line)

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### QLC+ closed connection ###")

def on_open(ws):
    print("### Opened connection with QLC+ ###")
    getDSMessage(ws)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(websocketURL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(reconnect=5) # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly