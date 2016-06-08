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
# Name:        test_lag_ct_bond_speed.py
#
# Objective:   Verify static lag bond speed is properly updated according
#              to the speed of the added interfaces.
#
# Topology:    2 switches (DUT running Halon) connected by 3 interfaces
#
#
##########################################################################
import pytest
from lib_test import (
    add_intf_to_bond,
    disable_intf_list,
    enable_intf_list,
    remove_all_intf_from_bond,
    set_port_parameter,
    sw_set_intf_pm_info,
    sw_create_bond,
    sw_wait_until_all_sm_ready,
    verify_interfaces_mac_uniqueness,
    verify_intf_in_bond,
    verify_intf_status,
    verify_port_bond_speed,
    verify_port_bond_speed_empty
)


TOPOLOGY = """
#   +-----+------+
#   |            |
#   |    sw1     |
#   |            |
#   +---+-+-+----+
#       | | |
#       | | | LAG 1
#       | | |
#   +---+-+-+----+
#   |            |
#   |     sw2    |
#   |            |
#   +-----+------+

# Nodes
[type=openswitch name="OpenSwitch 1"] sw1
[type=openswitch name="OpenSwitch 2"] sw2

# Links
sw1:1 -- sw2:1
sw1:2 -- sw2:2
sw1:3 -- sw2:3
"""

# Ports
port_labels = ['1', '2', '3']


###############################################################################
#
#                       ACTOR STATE STATE MACHINES VARIABLES
#
###############################################################################
sm_col_and_dist = '"Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,Dist:1,Def:0,Exp:0"'


@pytest.mark.skipif(True, reason="Skipping due to instability")
def test_lacp_bond_speed(topology, step):
    """
        Verify correct LAG bond_status:speed according to the speed of member
        interfaces status.
    """
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    lag_name = 'lag1'

    assert sw1 is not None
    assert sw2 is not None

    ports_sw1 = list()
    ports_sw2 = list()

    print("Mapping interfaces")
    for port in port_labels:
        ports_sw1.append(sw1.ports[port])
    for port in port_labels:
        ports_sw2.append(sw2.ports[port])

    step("Sorting the port list")
    ports_sw1.sort()
    ports_sw2.sort()

    p11 = ports_sw1[0]
    p12 = ports_sw1[1]
    p13 = ports_sw1[2]
    p21 = ports_sw2[0]
    p22 = ports_sw2[1]
    p33 = ports_sw2[2]

    step("Turning on all interfaces used in this test")
    enable_intf_list(sw1, ports_sw1)
    enable_intf_list(sw2, ports_sw2)

    step("Creating dynamic lag with 3 interfaces")
    sw_create_bond(sw1, lag_name, ports_sw1, lacp_mode='active')
    sw_create_bond(sw2, lag_name, ports_sw2, lacp_mode='active')

    step('Setting LAGs lacp rate as fast in switches')
    set_port_parameter(sw1, lag_name, ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, lag_name, ['other_config:lacp-time=fast'])

    for intf in ports_sw1:
        verify_intf_status(sw1, intf, "link_state", "up")
    for intf in ports_sw2:
        verify_intf_status(sw2, intf, "link_state", "up")

    verify_interfaces_mac_uniqueness([sw1,sw2], ['1'])

    step('Verify state machines from interfaces on Switch 1')
    sw_wait_until_all_sm_ready([sw1], ports_sw1, sm_col_and_dist)

    step('Verify state machines from interfaces on Switch 2')
    sw_wait_until_all_sm_ready([sw2], ports_sw2, sm_col_and_dist)

    ###########################################################################
    # 1.  When all member interfaces have the same speed.
    ###########################################################################

    intf_speed_1 = sw1('get interface ' + p11 + ' link_speed', shell='vsctl')
    intf_speed_2 = sw1('get interface ' + p12 + ' link_speed', shell='vsctl')
    intf_speed_3 = sw1('get interface ' + p13 + ' link_speed', shell='vsctl')
    assert intf_speed_1 == intf_speed_2 == intf_speed_3, 'The link_speed of' +\
        ' the 3 interfaces used in the test should be equal.'

    step("Verify LAG bond speed is equal to member interfaces speed")
    verify_port_bond_speed(sw1, lag_name, intf_speed_1, "Expected the LAG "
                            "bond_speed to be " + intf_speed_1)

    ###########################################################################
    # 2.  When member interfaces have different speed, bond_speed is equal to
    #     the speed of the first added interface
    ###########################################################################

    # Change speed in interface 3
    command = 'set interface ' + p13 + ' hw_intf_config:speeds="1000,10000" ' +\
              'hw_intf_info:max_speed="10000" hw_intf_info:speeds="1000,10000"'
    sw1(command, shell='vsctl')
    command = 'set interface ' + p13 + ' user_config:speeds="10000"'
    sw1(command, shell='vsctl')

    step("Verify LAG bond speed is equal to the first added interface speed")
    verify_port_bond_speed(sw1, lag_name, intf_speed_1, "Expected the LAG "
                            "bond_speed to be " + intf_speed_1)

    step("Remove all interfaces from LAG")
    remove_all_intf_from_bond(sw1, lag_name)

    step("Add interface 3 to LAG")
    add_intf_to_bond(sw1, lag_name, p13)
    verify_intf_in_bond(sw1, p13, "Expected interfaces "
                        "to be added to static lag")
    step("Add interface 2 to LAG")
    add_intf_to_bond(sw1, lag_name, p12)
    step("Add interface 1 to LAG")
    add_intf_to_bond(sw1, lag_name, p11)

    # Get the speed of interface 3
    intf_speed_3 = sw1('get interface ' + p13 + ' user_config:speeds', shell='vsctl')
    intf_speed_3 = intf_speed_3.strip('"') + '000000'

    step("Verify LAG bond speed is equal to the first added interface speed")
    verify_port_bond_speed(sw1, lag_name, intf_speed_3, "Expected the LAG "
                            "bond_speed to be " + intf_speed_3)

    step("Turning off interface 3")
    disable_intf_list(sw1, [p13])
    verify_intf_status(sw1, p13, "link_state", "down")

    # Get the speed of interface 1
    intf_speed_1 = sw1('get interface ' + p11 + ' link_speed', shell='vsctl')

    step("Verify LAG bond speed is equal to the first added interface speed")
    verify_port_bond_speed(sw1, lag_name, intf_speed_1, "Expected the LAG "
                            "bond_speed to be " + intf_speed_1)

    ###########################################################################
    # 4. When LAG has no member interfaces, bond_speed is empty
    ###########################################################################

    step("Remove all interfaces from LAG")
    remove_all_intf_from_bond(sw1, lag_name)

    step("Verify LAG bond speed is empty when LAG has no interfaces")
    verify_port_bond_speed_empty(sw1, lag_name, "Interface expected"
                                  " to have bond speed EMPTY")
