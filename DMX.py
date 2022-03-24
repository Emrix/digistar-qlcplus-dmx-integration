#################################################################
#    DMX.py
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
# Install websockets via pip
# Add the DMX.py script to $Content/User/Python


# The following are digistar commands
# To import the script into the Python Environment in Digistar, enter the following command.  You should see "DMX Imported" when successful
# py com "import DMX"

# To begin the communication with QLC+, make sure QLC+ is opened on the computer, and type in the following.
# py com "DMX.Begin('ws://localhost:9999/qlcplusWS')"
# You should see "Started DMX" if it was successful. This URL can be changed to be the computer or port number that QLC+ is running on, if not localhost:9999

# The commands used are directly taken from the QLC+ API, and prepended with "DMX " to signal to the python program that it is a lighting command
# See https://www.qlcplus.org/Test_Web_API.html for more information about the API
# To change a specific channel, type in "CH|channelNumber|channelValue".
# py control "DMX CH|1|2"

# To change a specific widget in QLC+, type in "widgetID|widgetValue".
# For instance, if I had a button widget configured on QLC+ whose ID was 1, I would "click" that button by sending the following command
# py control "DMX 1|255"

# To end the communication with QLC+, you may either issue a fadestopreset command, or send an "end" control message like so:
# py control "end"

# ---Known bugs---
# Sending commands too fast via Digistar will not update QLC+ in a timely manner.  The use of widgets are recommended.
# There is no graceful handling of strings that do not comply with the QLC+ API
# If there is a fadestopreset, lighting will break.  But that's an easy fix.
# Right now, it's not possible to receive information back from QLC+ (for querying widget IDs and such.)

#################################################################

import asyncio, Ds, websockets, time
print('DMX Imported')

class C_DMX:
    def __init__(self):
        print('Started DMX')
        self.eStart = 0
        self.eFinish = 1
        self.nState = self.eStart
        self.timPrev = 0.0
        # self.nShowClockAttrRef = Ds.AllocObjectAttrRef('show', 'time')
        # self.nTextDisplayAttrRef = Ds.AllocObjectAttrRef('timeCode', 'text')

    def Run(self, address):
        while self.nState != self.eFinish:
            sCommand = Ds.GetCommand();  # check for [py control "end"]
            if sCommand != '':
                print(sCommand)
                if sCommand == 'end' or sCommand == 'fadestopreset':
                    print('ending')
                    self.nState = self.eFinish
                elif sCommand.startswith("DMX"):
                    asyncio.run(self.Update(sCommand,address))  # call update function to update lights
                else:
                    print(round(time.time() * 1000))
            time.sleep(1)  # sleep 1/2 second (modify for different update rate)
        return

    async def Update(self, sCommand, address):
        async with websockets.connect(address) as websocket:
            print("Connecting to " + address)
            # await websocket.send("Digistar!")
            # await websocket.recv()
            await websocket.send(sCommand[4:])
            await websocket.close()
            # await websocket.recv()
        return

def Begin(address):
   s = C_DMX()
   s.Run(address)
   print('Stopped DMX')
   del s
   return
