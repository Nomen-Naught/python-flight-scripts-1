# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2014 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.

"""
Simple example that connects to the first Crazyflie found, ramps up/down
the motors and disconnects.
"""

import time
import sys
from threading import Thread
import logging

sys.path.append("../lib")
import cflib  # noqa
from cflib.crazyflie import Crazyflie  # noqa

logging.basicConfig(level=logging.ERROR)


class MotorRampExample:
    """Example that connects to a Crazyflie and ramps the motors up/down and
    the disconnects"""

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print("Connecting to %s" % link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        Thread(target=self._ramp_motors).start()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print("Connection to %s failed: %s" % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print("Connection to %s lost: %s" % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print("Disconnected from %s" % link_uri)

    def take_off(self, roll, pitch, yawrate, thrust):
        x = 0
        while x <= 4:
            #take off loop
            x = x+1
            self._cf.commander.send_setpoint(roll, pitch, yawrate, 40000)
            time.sleep(0.1)
        return

    def hover(self, roll, pitch, yawrate, thrust):
        x = 0
        while x <= 15:
            #hover Loop
            x = x+1
            self._cf.commander.send_setpoint(roll, pitch, yawrate, 32000)
            time.sleep(0.1)
            self._cf.commander.send_setpoint(roll, pitch, yawrate, 35000)
            time.sleep(0.1)
        return
            
    def next_spot(self, roll, pitch, yawrate, thrust):
        x = 0
        while x <= 3:
            #forward loop
            x = x+1
            self._cf.commander.send_setpoint(roll, pitch , yawrate, 35000)
            time.sleep(0.1)
        #stop the quad from moving forward            
        pitch = -2
        self._cf.commander.send_setpoint(roll, pitch, yawrate, 40000)
        time.sleep(0.1)
        pitch = 3
        return

    def land(self, roll, pitch, yawrate, thrust):
        x = 0
        thrust1 = 33000
        while x <= 13:
            #landing loop
            x = x+1
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust1)
            time.sleep(0.1)
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust1)
            time.sleep(0.1)
            thrust1 = thrust1 - 100
        return

    def _ramp_motors(self):
        thrust_mult = 1
        thrust_step = 500
        thrust = 35000
        pitch = 3
        roll = 1
        yawrate = 0
        y = 0
        
        # Unlock startup thrust protection
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        time.sleep(0.1)

        self.take_off(roll, pitch, yawrate, thrust)
            
        self.hover(roll, pitch, yawrate, thrust)

        thrust = 33000
        self.land(roll, pitch, yawrate, thrust)
                      
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing

        time.sleep(0.1)
        self._cf.close_link()


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found
    print("Scanning interfaces for Crazyflies...")
    available = cflib.crtp.scan_interfaces()
    print("Crazyflies found:")
    for i in available:
        print(i[0])

    if len(available) > 0:
        le = MotorRampExample(available[0][0])
    else:
        print("No Crazyflies found, cannot run example")
