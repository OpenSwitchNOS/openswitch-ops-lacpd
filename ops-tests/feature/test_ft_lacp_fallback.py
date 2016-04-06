# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

##########################################################################
# Name:      test_ft_lacp_fallback.py
#
# Objective: The purpose is to configured LAG to either disable all ports
#            or to fallback to active/backup (a single port forwarding and
#            the other blocking) when dynamic LACP is configured and the
#            LACP negotiation fail (due to the lack of an LACP partner).
#
# Topology:  2 switch (DUT running Halon)
#
##########################################################################

"""
OpenSwitch Test for LAG with fallback.
"""

import time
from lacp_lib import create_lag_active
from lacp_lib import associate_interface_to_lag
from lacp_lib import turn_on_interface
from lacp_lib import validate_lag_state_sync
from lacp_lib import LOCAL_STATE
from lacp_lib import REMOTE_STATE
from lacp_lib import validate_lag_name
from lacp_lib import validate_local_key
from lacp_lib import validate_remote_key
from lacp_lib import set_lag_rate
from lacp_lib import validate_lag_state_afoex
from lacp_lib import validate_lag_state_afncde
from lacp_lib import validate_lag_state_afoe
from lacp_lib import retry_validate_turn_on_interfaces

TOPOLOGY = """
#
#     +--------+  LAG  +--------+
#     |        <------->        |
#     |  ops1  <------->  ops2  |
#     |        |       |        |
#     +--------+       +--------+

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2

# Links
sw1:1 -- sw2:1
sw1:2 -- sw2:2
"""


def test_lag_fallback(topology):
    """
    Tests LAG fallback
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    sw1_lag_id = '100'
    sw2_lag_id = '100'
    assert sw1 is not None
    assert sw2 is not None

    p11 = sw1.ports['1']
    p12 = sw1.ports['2']
    p21 = sw2.ports['1']
    p22 = sw2.ports['2']

    print("Turning on all interfaces used in this test")
    ports_sw1 = [p11, p12]
    for port in ports_sw1:
        turn_on_interface(sw1, port)

    ports_sw2 = [p21, p22]
    for port in ports_sw2:
        turn_on_interface(sw2, port)

    print("Waiting for interfaces to turn on")

    retry_validate_turn_on_interfaces(sw1,
                                      ports_sw1,
                                      "Verify Interfaces are up in switch1",
                                      "Retry to make sure interfaces are up",
                                      10,
                                      40)
    retry_validate_turn_on_interfaces(sw2,
                                      ports_sw2,
                                      "Verify Interfaces are up in switch2",
                                      "Retry to make sure interfaces are up",
                                      10,
                                      40)

    # Create and configure lags
    create_lag_active(sw1, sw1_lag_id)
    create_lag_active(sw2, sw2_lag_id)

    set_lag_rate(sw1, sw1_lag_id, 'fast')
    set_lag_rate(sw2, sw2_lag_id, 'fast')

    print("Associate interfaces [1,2] to lag in both switches")
    associate_interface_to_lag(sw1, p11, sw1_lag_id)
    associate_interface_to_lag(sw1, p12, sw1_lag_id)
    associate_interface_to_lag(sw2, p21, sw2_lag_id)
    associate_interface_to_lag(sw2, p22, sw2_lag_id)

    cont = 0
    timeout = 60
    time_steps = 10
    print("Validate the LAG was created in both switches")
    while cont <= timeout:

        map_lacp_sw1 = sw1.libs.vtysh.show_lacp_interface(p11)
        map_lacp_sw2 = sw2.libs.vtysh.show_lacp_interface(p21)

        try:
            validate_lag_name(map_lacp_sw1, sw1_lag_id)
            validate_local_key(map_lacp_sw1, sw1_lag_id)
            validate_remote_key(map_lacp_sw1, sw2_lag_id)
            validate_lag_state_sync(map_lacp_sw1, LOCAL_STATE)
            validate_lag_state_sync(map_lacp_sw1, REMOTE_STATE)

            validate_lag_name(map_lacp_sw2, sw2_lag_id)
            validate_local_key(map_lacp_sw2, sw2_lag_id)
            validate_remote_key(map_lacp_sw2, sw1_lag_id)
            validate_lag_state_sync(map_lacp_sw2, LOCAL_STATE)
            validate_lag_state_sync(map_lacp_sw2, REMOTE_STATE)
            break
        except AssertionError:
            if cont < timeout:
                print("Waiting 10 seconds to retry")
                time.sleep(10)
                cont += time_steps
                continue
            print("Retry time of 10 seconds expired")
            raise

    # lacp fallback false as a default

    # Disable Interfaces from bond in switch 2.
    print("Change LAG mode on switch 2 to off")
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.no_lacp_mode_active()

    cont = 0
    print("Validate the interfaces are in LAG state AFOEX in switch 1")
    while cont <= timeout:
        map_lacp_sw1_p11 = sw1.libs.vtysh.show_lacp_interface(p11)
        map_lacp_sw1_p12 = sw1.libs.vtysh.show_lacp_interface(p12)

        try:
            validate_lag_state_afoex(map_lacp_sw1_p11, LOCAL_STATE)
            validate_lag_state_afoex(map_lacp_sw1_p12, LOCAL_STATE)
            break
        except AssertionError:
            if cont < timeout:
                print("Waiting 10 seconds to retry")
                time.sleep(10)
                cont += time_steps
                continue
            print("Retry time of 10 seconds expired")
            raise

    # Set lacp to "active"
    print("Change LAG mode on switch 2 to active")
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_mode_active()

    # lacp fallback true
    with sw1.libs.vtysh.ConfigInterfaceLag(sw1_lag_id) as ctx:
        ctx.lacp_fallback()
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_fallback()

    # Disable Interfaces from bond in switch 2.
    print("Change LAG mode on switch 2 to off")
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.no_lacp_mode_active()

    print("Validate interfaces state with fallback")
    cont = 0
    while cont <= timeout:
        map_lacp_sw1_p11 = sw1.libs.vtysh.show_lacp_interface(p11)
        map_lacp_sw1_p12 = sw1.libs.vtysh.show_lacp_interface(p12)

        try:
            success = False
            if ((validate_lag_state_afncde(map_lacp_sw1_p11,
                                           LOCAL_STATE) is True and
                 validate_lag_state_afoe(map_lacp_sw1_p12,
                                         LOCAL_STATE) is True) or
                (validate_lag_state_afoe(map_lacp_sw1_p11,
                                         LOCAL_STATE) is True and
                validate_lag_state_afncde(map_lacp_sw1_p12,
                                          LOCAL_STATE) is True)):
                success = True

            assert success is True,\
                "Interfaces don't have correct state with Fallback enabled"
            break
        except AssertionError:
            if cont < timeout:
                print("Waiting 10 seconds to retry")
                time.sleep(10)
                cont += time_steps
                continue
            print("Retry time of 10 seconds expired")
            raise

    # Set lacp to "active"
    print("Change LAG mode on switch 2 to active")
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_mode_active()

    print("Validate LAG state with interfaces in switch 1 and switch 2")
    cont = 0
    timeout = 40
    while cont <= timeout:
        map_lacp_sw1_p11 = sw1.libs.vtysh.show_lacp_interface(p11)
        map_lacp_sw1_p12 = sw1.libs.vtysh.show_lacp_interface(p12)
        map_lacp_sw2_p21 = sw2.libs.vtysh.show_lacp_interface(p21)
        map_lacp_sw2_p22 = sw2.libs.vtysh.show_lacp_interface(p22)

        try:
            validate_lag_state_sync(map_lacp_sw1_p11, LOCAL_STATE)
            validate_lag_state_sync(map_lacp_sw1_p12, LOCAL_STATE)

            validate_lag_state_sync(map_lacp_sw2_p21, LOCAL_STATE)
            validate_lag_state_sync(map_lacp_sw2_p22, LOCAL_STATE)
            break
        except AssertionError:
            if cont < timeout:
                print("Waiting 10 seconds to retry")
                time.sleep(10)
                cont += time_steps
                continue
            print("Retry time of 10 seconds expired")
            raise

    print("Test Fallback PASS.")