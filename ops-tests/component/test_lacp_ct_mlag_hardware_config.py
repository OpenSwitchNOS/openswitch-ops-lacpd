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
# Name:        test_lacp_ct_mlag_hardware_config.py
#
# Objective:   Verify lacp bond status is properly updated according to the
#              status of the interface when interface is Mlag.
#              RX enable/TX enable are not updated by lacp
#
# Topology:    2 switches (DUT running Halon) connected by 2 interfaces
#
#
##########################################################################

from lib_test import (
    enable_intf_list,
    disable_intf_list,
    set_port_parameter,
    sw_create_bond,
    sw_wait_until_all_sm_ready,
    verify_intf_bond_status,
    verify_intf_in_bond,
    verify_intf_status,
    verify_port_bond_status,
    verify_intf_bond_status_down
)


TOPOLOGY = """
#   +-----+------+
#   |            |
#   |    sw1     |
#   |            |
#   +--+----+----+
#      |    |
#      |    |   LAG 1
#      |    |
#   +--+----+----+
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
"""


###############################################################################
#
#                       ACTOR STATE STATE MACHINES VARIABLES
#
###############################################################################
sm_col_and_dist = '"Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,Dist:1,Def:0,Exp:0"'


def test_lacp_bond_status(topology, step):
    """
        Verify correct LACP bond_status according to the status of member
        interfaces status.
    """
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    lag_name = 'lag1'

    assert sw1 is not None
    assert sw2 is not None

    p11 = sw1.ports['1']
    p12 = sw1.ports['2']
    p21 = sw2.ports['1']
    p22 = sw2.ports['2']

    ports_sw1 = [p11, p12]
    ports_sw2 = [p21, p22]

    step("Turning on all interfaces used in this test")
    enable_intf_list(sw1, ports_sw1)
    enable_intf_list(sw2, ports_sw2)

    step("Creating dynamic lag with 4 interfaces")
    sw_create_bond(sw1, lag_name, ports_sw1, lacp_mode='active')
    sw_create_bond(sw2, lag_name, ports_sw2, lacp_mode='active')

    step("Turning on all the interfaces used in this test")
    for intf in ports_sw1:
        verify_intf_status(sw1, intf, "link_state", "up")
    for intf in ports_sw2:
        verify_intf_status(sw2, intf, "link_state", "up")

    step('Setting LAGs lacp rate as fast in switches')
    set_port_parameter(sw1, lag_name, ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, lag_name, ['other_config:lacp-time=fast'])

    step('Verify state machines from interfaces on Switch 1')
    sw_wait_until_all_sm_ready([sw1], ports_sw1, sm_col_and_dist)
    step('Verify state machines from interfaces on Switch 1')
    sw_wait_until_all_sm_ready([sw1], ports_sw1, sm_col_and_dist)
    step('Verify state machines from interfaces on Switch 1')
    sw_wait_until_all_sm_ready([sw1], ports_sw1, sm_col_and_dist)

    step('Verify state machines from interfaces on Switch 2')
    sw_wait_until_all_sm_ready([sw2], ports_sw2, sm_col_and_dist)

    ###########################################################################
    # 1.  When all member interfaces have bond_status up.
    ###########################################################################

    step("Verify that all the interfaces are added to LAG and that "
         "bond_status is up.")

    for intf in ports_sw1:
        verify_intf_in_bond(sw1, intf, "Expected interfaces "
                            "to be added to static lag")

        verify_intf_bond_status(sw1, intf, "state", "Expected interfaces "
                                "to have bond status UP")

    step("Verify LAG bond status is UP when all the member  interfaces "
         "have bond_status equal to UP")
    verify_port_bond_status(sw1, lag_name, "state", "Expected the LAG "
                            "to have bond status UP")

    ###########################################################################
    # 2.  Set mclag_status values
    ###########################################################################

    step('Setting MLAG state = true')
    set_port_parameter(sw1, lag_name, ['other_config:mclag_enabled=true'])
    set_port_parameter(sw2, lag_name, ['other_config:mclag_enabled=true'])

    print("Set mclag_status: actor_system_id and port_id")
    count = 0
    actor_system_id = ["00:06:00:02:82:1f:60:4a", "00:06:00:02:82:1f:60:4b"]
    port_id = ["12", "13"]

    for intf in ports_sw1:
        c = "ovs-vsctl set interface " + str(intf) +\
             " mclag_status:actor_system_id=" + actor_system_id[count] +\
             " mclag_status:actor_port_id=" + port_id[count] +\
             " mclag_status:actor_key=\"60:00\" "
        count += 1
        print(c)
        output = sw1(c, shell='bash')

        assert output == "", ("Error changing MLAG settings for interface %s"
                              "returned %s" % (intf, output))

    ###########################################################################
    # 3.  Verify Bond Status change, RX/TX enable didnt change
    ###########################################################################

    print(" Verify Bond Status change, RX/TX enable didnt change")

    disable_intf_list(sw2, ports_sw2)

    verify_intf_bond_status_down(sw1, intf, "state", "Expected interfaces "
                                 "to have bond status DOWN")
    for intf in ports_sw1:
        verify_intf_in_bond(sw1, intf, "Expected interfaces "
                            "to be added to static lag")
