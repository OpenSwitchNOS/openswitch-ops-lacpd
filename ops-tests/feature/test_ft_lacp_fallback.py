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
# Name:      test_lacpd_ft_lag_fallback.py
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
from lacp_lib import delete_lag
from lacp_lib import associate_interface_to_lag
from lacp_lib import turn_on_interface
from lacp_lib import turn_off_interface
from lacp_lib import validate_lag_state_out_of_sync
from lacp_lib import validate_lag_state_sync
from lacp_lib import LOCAL_STATE

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

    # Create and configure lags
    create_lag_active(sw1, sw1_lag_id)
    create_lag_active(sw2, sw2_lag_id)

    print("Associate interfaces [1,2] to lag in both switches")
    associate_interface_to_lag(sw1, p11, sw1_lag_id)
    associate_interface_to_lag(sw1, p12, sw1_lag_id)
    associate_interface_to_lag(sw2, p21, sw2_lag_id)
    associate_interface_to_lag(sw2, p22, sw2_lag_id)

    # Without this sleep time, we are validating temporary
    # states in state machines
    print("Waiting for LAG negotiations between switches")
    time.sleep(30)

    # lacp fallback false as a default

    # Disable Interfaces from bond in switch 2.
    print("Change LAG mode on switch 2 to off")
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.no_lacp_mode_active()

    # Without this sleep time, we are validating temporary
    # states in state machines
    print("Waiting for LAG negotiations between switches")
    time.sleep(30)

    print("Get information for LAG in interfaces in switch 1")
    map_lacp_sw1_p11 = sw1.libs.vtysh.show_lacp_interface(p11)
    map_lacp_sw1_p12 = sw1.libs.vtysh.show_lacp_interface(p12)

    print("Validate the interfaces off in switch 1")
    validate_lag_state_out_of_sync(map_lacp_sw1_p11, LOCAL_STATE)
    validate_lag_state_out_of_sync(map_lacp_sw1_p12, LOCAL_STATE)

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

    # Without this sleep time, we are validating temporary
    # states in state machines
    print("Waiting for LAG negotiations between switches")
    time.sleep(30)

    print("Validate the interface 1 in switch 1")
    validate_lag_state_sync(map_lacp_sw1_p11, LOCAL_STATE)

    # Add the Interface back into the LAG/Trunk.
    # Set lacp to "active"
    print("Change LAG mode on switch 2 to active")
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_mode_active()

    # Without this sleep time, we are validating temporary
    # states in state machines
    print("Waiting for LAG negotiations between switches")
    time.sleep(30)

    print("Validate the interfaces in switch 1")
    validate_lag_state_sync(map_lacp_sw1_p11, LOCAL_STATE)
    validate_lag_state_sync(map_lacp_sw1_p12, LOCAL_STATE)

    print("Cleaning configuration")
    for port in ports_sw1:
        turn_off_interface(sw1, port)

    for port in ports_sw2:
        turn_off_interface(sw2, port)

    delete_lag(sw1, sw1_lag_id)
    delete_lag(sw2, sw2_lag_id)
