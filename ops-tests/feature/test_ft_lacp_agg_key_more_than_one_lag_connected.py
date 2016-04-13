# (C) Copyright 2016 Hewlett Packard Enterprise Development LP
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

##########################################################################
# Name:        test_ft_lacp_aggregation_key.py
#
# Objective:   To verify the LACP aggregation key functionality in several
#              corner cases that take the interfaces to the expected state
#
# Topology:    2 switch (DUT running Halon)
#
##########################################################################


"""
OpenSwitch Test for LACP aggregation key functionality
"""

import time
from lacp_lib import create_lag_active
from lacp_lib import associate_interface_to_lag
from lacp_lib import turn_on_interface
from lacp_lib import validate_lag_state_sync
from lacp_lib import validate_lag_state_out_of_sync
from lacp_lib import validate_lag_state_afn
from lacp_lib import LOCAL_STATE
from lacp_lib import set_lacp_rate_fast
from lacp_lib import validate_turn_on_interfaces
from lacp_lib import parse_appctl_getlacpstate
from lacp_lib import parse_appctl_getlacpinterfaces
from lacp_lib import validate_appctl_lag_state_sync
from lacp_lib import validate_appctl_lag_state_out_sync
from lacp_lib import validate_appctl_lag_state_afn
from lacp_lib import validate_appctl_lacp_interfaces
from lacp_lib import APPCTL_LOCAL_STATE

TOPOLOGY = """
# +-------+     +-------+
# |  sw1  |-----|  sw2  |
# +-------+     +-------+

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2

# Links
sw1:1 -- sw2:1
sw1:2 -- sw2:2
sw1:3 -- sw2:3
sw1:4 -- sw2:4
sw1:5 -- sw2:6
sw1:6 -- sw2:7
sw1:7 -- sw2:5
"""


# Executes ovs-appctl command getlacpstate
def get_appctl_lacp_state(sw):
    c = "ovs-appctl -t ops-lacpd lacpd/getlacpstate"
    output = sw(c, shell='bash')
    return parse_appctl_getlacpstate(output + '\n')


# Executes ovs-appctl command getlacpinterfaces
def get_appctl_lacp_interfaces(sw):
    c = "ovs-appctl -t ops-lacpd lacpd/getlacpinterfaces"
    output = sw(c, shell='bash')
    return parse_appctl_getlacpinterfaces(output)


def test_lacp_agg_key_more_than_one_lag_connected(topology):
    """
    Case 2:
        Verify only interfaces associated with the same
        aggregation key get to Collecting/Distributing state
        Initial Topology:
            SW1>
                LAG150 -> Interfaces: 1,2,3,4
            SW2>
                LAG300 -> Interfaces: 1,2
                LAG400 -> Interfaces: 3,4
        Expected behaviour:
            Interfaces 1 and 2 in both switches get state Active, InSync,
            Collecting and Distributing. Interfaces 3 and 4 should get state
            Active, OutOfSync, Collecting and Distributing
    """
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    sw1_lag_id = '150'
    sw2_lag_id = '150'
    sw2_lag_id_2 = '400'

    assert sw1 is not None
    assert sw2 is not None

    p11 = sw1.ports['1']
    p12 = sw1.ports['2']
    p13 = sw1.ports['3']
    p14 = sw1.ports['4']
    p21 = sw2.ports['1']
    p22 = sw2.ports['2']
    p23 = sw2.ports['3']
    p24 = sw2.ports['4']

    print("Turning on all interfaces used in this test")
    ports_sw1 = [p11, p12, p13, p14]
    for port in ports_sw1:
        turn_on_interface(sw1, port)

    ports_sw2 = [p21, p22, p23, p24]
    for port in ports_sw2:
        turn_on_interface(sw2, port)

    time.sleep(40)
    validate_turn_on_interfaces(sw1, ports_sw1)
    validate_turn_on_interfaces(sw2, ports_sw2)

    print("Create LAG in both switches")
    create_lag_active(sw1, sw1_lag_id)
    create_lag_active(sw2, sw2_lag_id)
    create_lag_active(sw2, sw2_lag_id_2)
    set_lacp_rate_fast(sw1, sw1_lag_id)
    set_lacp_rate_fast(sw2, sw2_lag_id)
    set_lacp_rate_fast(sw2, sw2_lag_id_2)

    print("Associate interfaces to lag in both switches")
    for interface in ports_sw1:
        associate_interface_to_lag(sw1, interface, sw1_lag_id)

    for interface in ports_sw2[0:2]:
        associate_interface_to_lag(sw2, interface, sw2_lag_id)

    for interface in ports_sw2[2:4]:
        associate_interface_to_lag(sw2, interface, sw2_lag_id_2)

    # Without this sleep time, we are validating temporary
    # states in state machines
    print("Waiting for LAG negotations between switches")
    time.sleep(60)

    print("Get the configured interfaces for each LAG using appctl " +
          "getlacpinterfaces in both switches")
    sw1_lacp_interfaces = get_appctl_lacp_interfaces(sw1)
    sw2_lacp_interfaces = get_appctl_lacp_interfaces(sw2)
    validate_appctl_lacp_interfaces(sw1_lacp_interfaces, sw1_lag_id,
                                    [p11, p12, p13, p14], [p11, p12, p13, p14],
                                    [p11, p12])
    validate_appctl_lacp_interfaces(sw2_lacp_interfaces, sw2_lag_id,
                                    [p21, p22], [p21, p22], [p21, p22])
    validate_appctl_lacp_interfaces(sw2_lacp_interfaces, sw2_lag_id_2,
                                    [p23, p24], [p23, p24], [])

    print("Get information for LAG in interface 1 with both switches")
    map_lacp_sw1_p11 = sw1.libs.vtysh.show_lacp_interface(p11)
    map_lacp_sw1_p12 = sw1.libs.vtysh.show_lacp_interface(p12)
    map_lacp_sw1_p13 = sw1.libs.vtysh.show_lacp_interface(p13)
    map_lacp_sw1_p14 = sw1.libs.vtysh.show_lacp_interface(p14)
    map_lacp_sw2_p21 = sw2.libs.vtysh.show_lacp_interface(p21)
    map_lacp_sw2_p22 = sw2.libs.vtysh.show_lacp_interface(p22)
    map_lacp_sw2_p23 = sw2.libs.vtysh.show_lacp_interface(p23)
    map_lacp_sw2_p24 = sw2.libs.vtysh.show_lacp_interface(p24)

    print("Get the state of LAGs using appctl getlacpstate in both switches")
    sw1_lacp_state = get_appctl_lacp_state(sw1)
    sw2_lacp_state = get_appctl_lacp_state(sw2)
    map_appctl_lacp_sw1_p11 = sw1_lacp_state[str(sw1_lag_id)][int(p11)]
    map_appctl_lacp_sw1_p12 = sw1_lacp_state[str(sw1_lag_id)][int(p12)]
    map_appctl_lacp_sw1_p13 = sw1_lacp_state[str(sw1_lag_id)][int(p13)]
    map_appctl_lacp_sw1_p14 = sw1_lacp_state[str(sw1_lag_id)][int(p14)]
    map_appctl_lacp_sw2_p21 = sw2_lacp_state[str(sw2_lag_id)][int(p21)]
    map_appctl_lacp_sw2_p22 = sw2_lacp_state[str(sw2_lag_id)][int(p22)]
    map_appctl_lacp_sw2_p23 = sw2_lacp_state[str(sw2_lag_id_2)][int(p23)]
    map_appctl_lacp_sw2_p24 = sw2_lacp_state[str(sw2_lag_id_2)][int(p24)]

    print("Validate the LAG was created in both switches")
    validate_lag_state_sync(map_lacp_sw1_p11, LOCAL_STATE)
    validate_lag_state_sync(map_lacp_sw1_p12, LOCAL_STATE)
    validate_lag_state_out_of_sync(map_lacp_sw1_p13,
                                   LOCAL_STATE)
    validate_lag_state_out_of_sync(map_lacp_sw1_p14,
                                   LOCAL_STATE)

    validate_lag_state_sync(map_lacp_sw2_p21, LOCAL_STATE)
    validate_lag_state_sync(map_lacp_sw2_p22, LOCAL_STATE)
    validate_lag_state_afn(map_lacp_sw2_p23, LOCAL_STATE)
    validate_lag_state_afn(map_lacp_sw2_p24, LOCAL_STATE)

    # Validate appctl results
    validate_appctl_lag_state_sync(map_appctl_lacp_sw1_p11,
                                   APPCTL_LOCAL_STATE)
    validate_appctl_lag_state_sync(map_appctl_lacp_sw1_p12,
                                   APPCTL_LOCAL_STATE)
    validate_appctl_lag_state_out_sync(map_appctl_lacp_sw1_p13,
                                       APPCTL_LOCAL_STATE)
    validate_appctl_lag_state_out_sync(map_appctl_lacp_sw1_p14,
                                       APPCTL_LOCAL_STATE)

    validate_appctl_lag_state_sync(map_appctl_lacp_sw2_p21,
                                   APPCTL_LOCAL_STATE)
    validate_appctl_lag_state_sync(map_appctl_lacp_sw2_p22,
                                   APPCTL_LOCAL_STATE)
    validate_appctl_lag_state_afn(map_appctl_lacp_sw2_p23,
                                  APPCTL_LOCAL_STATE)
    validate_appctl_lag_state_afn(map_appctl_lacp_sw2_p24,
                                  APPCTL_LOCAL_STATE)
