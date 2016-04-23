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
# Name:        test_lag_ct_bond_status.py
#
# Objective:   Verify lag bond status is properly updated according to the
#              status of the added interfaces.
#
# Topology:    2 switches (DUT running Halon) connected by 4 interfaces
#
#
##########################################################################

from lib_test import sw_set_intf_user_config
from lib_test import sw_create_bond
from lib_test import verify_intf_in_bond
from lib_test import verify_intf_not_in_bond
from lib_test import remove_intf_from_bond
from lib_test import verify_intf_bond_status
from lib_test import verify_port_bond_status


TOPOLOGY = """
#   +-----+------+
#   |            |
#   |    sw1     |
#   |            |
#   +--+-+--+-+--+
#      | |  | |
#      | |  | | LAG 1
#      | |  | |
#   +--+-+--+-+--+
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
sw1:4 -- sw2:4
"""


# Add a new Interface to the existing bond.
def add_intf_to_bond(sw, bond_name, intf_name):

    print("Adding interface %s to LAG %s \n" %
          (intf_name, bond_name))
    # Get the UUID of the interface that has to be added.
    c = ("get interface %s _uuid" % (str(intf_name)))

    intf_uuid = sw(c.format(**locals()), shell='vsctl').rstrip('\r\n')

    # Get the current list of Interfaces in the bond.
    c = ("get port %s interfaces" % (bond_name))
    out = sw(c.format(**locals()), shell='vsctl')
    intf_list = out.rstrip('\r\n').strip("[]").replace(" ", "").split(',')

    assert intf_uuid not in intf_list,\
        print("Interface %s is already part of %s \n" %
              (intf_name, bond_name))

    # Add the given intf_name's UUID to existing Interfaces.
    intf_list.append(intf_uuid)

    # Set the new Interface list in the bond.
    new_intf_str = "[%s]" % (",".join(intf_list))

    c = ("set port %s interfaces=%s" % (bond_name, new_intf_str))
    sw(c.format(**locals()), shell='vsctl')


# Add a list of Interfaces to the bond.
def add_intf_list_from_bond(sw, bond_name, intf_list):
    for intf in intf_list:
        add_intf_to_bond(sw, bond_name, intf)


def enable_intf_list(sw, intf_list):
    for intf in intf_list:
        sw_set_intf_user_config(sw, intf, ['admin=up'])


def disable_intf_list(sw, intf_list):
    for intf in intf_list:
        sw_set_intf_user_config(sw, intf, ['admin=down'])


def test_lag_bond_status(topology):
    """
        Verify correct LAG bond_status according to the status of member
        interfaces status.
    """
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    lag_name = 'lag1'

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

    ports_sw1 = [p11, p12, p13, p14]
    ports_sw2 = [p21, p22, p23, p24]

    print("Turning on all interfaces used in this test")
    enable_intf_list(sw1, ports_sw1)
    enable_intf_list(sw2, ports_sw2)

    print("Creating static lag with 4 interfaces")
    sw_create_bond(sw1, lag_name, ports_sw1)
    sw_create_bond(sw2, lag_name, ports_sw2)

    ###########################################################################
    # 1.  When all member interfaces have bond_status up
    ###########################################################################

    print("Verify that all the interfaces are added to LAG and that "
          "bond_status is up.")
    for intf in ports_sw1:
        verify_intf_in_bond(sw1, intf, "Expected interfaces "
                            "to be added to static lag")
        verify_intf_bond_status(sw1, intf, "up", "Expected interfaces "
                                "to have bond status UP")

    print("Verify LAG bond status is UP when all the member  interfaces "
          "have bond_status equal to UP")
    verify_port_bond_status(sw1, lag_name, "up", "Expected the LAG "
                            "to have bond status UP")

    ###########################################################################
    # 2.  When at least 1 member interface has bond_status up.
    ###########################################################################

    print("Turning off all interfaces of LAG but one")
    disable_intf_list(sw1, ports_sw1[1:4])

    print("Verify that off interfaces bond_status is down")
    for intf in ports_sw1[1:4]:
        verify_intf_bond_status(sw1, intf, "down", "Expected off interfaces "
                                "to have bond status DOWN")

    print("Verify that on interface bond_status is up")
    verify_intf_bond_status(sw1, ports_sw1[0], "up", "Expected on interface "
                            "to have bond status UP")

    print("Verify LAG bond status is UP when at least one member interface "
          "have bond_status equal to UP")
    verify_port_bond_status(sw1, lag_name, "up", "Expected the LAG "
                            "to have bond status UP")

    print("Turning back on interfaces")
    enable_intf_list(sw1, ports_sw1[1:4])

    ###########################################################################
    # 3.  Interfaces not member of LAG have bond_status equal to blocked
    ###########################################################################

    print("Remove interface from LAG")
    remove_intf_from_bond(sw1, lag_name, ports_sw1[0])

    print("Verify interface is not part of LAG and bond_status is blocked.")
    verify_intf_not_in_bond(sw1, ports_sw1[0],
                            "Expected the interfaces to be removed "
                            "from static lag")
    verify_intf_bond_status(sw1, ports_sw1[0], "blocked", "Interfaces expected"
                            " to have bond status BLOCKED")

    print("Add interface back to LAG")
    add_intf_to_bond(sw1, lag_name, ports_sw1[0])

    print("Verify interface is part of LAG and bond_status is up.")
    verify_intf_in_bond(sw1, ports_sw1[0], "Interfaces is not "
                        "added back to the trunk.")

    verify_intf_bond_status(sw1, ports_sw1[0], "up", "Expected interfaces "
                            "to have bond status UP")

    ###########################################################################
    # 4.  When all member interfaces have bond_status down
    ###########################################################################

    print("Turning off all interfaces used in this test")
    disable_intf_list(sw1, ports_sw1)

    print("Verify that interfaces are not added to LAG when they are disabled"
          "and interface bond status is set to down\n")
    for intf in ports_sw1:
        verify_intf_not_in_bond(sw1, intf, "Interfaces should not be part "
                                "of LAG when they are disabled.")

        verify_intf_bond_status(sw1, intf, "down", "Expected interfaces "
                                "to have bond status DOWN")

    print("Verify that when all interfaces have bond_status equal to down "
          "LAG bond_status is down")

    verify_port_bond_status(sw1, lag_name, "down", "Expected the LAG "
                            "to have bond status DOWN")

    print("Turning back on all interfaces used in this test")
    enable_intf_list(sw1, ports_sw1)

    ###########################################################################
    # 5. LAG with no member interfaces have bond_status equal to blocked
    ###########################################################################

    print("Remove all interfaces from LAG")
    for intf in ports_sw1:
        remove_intf_from_bond(sw1, lag_name, intf)

    print("Verify interface is not part of LAG and bond_status is blocked.")
    for intf in ports_sw1:
        verify_intf_not_in_bond(sw1, intf,
                                "Expected the interfaces to be removed "
                                "from static lag")
        verify_intf_bond_status(sw1, intf, "blocked", "Interfaces expected"
                                " to have bond status BLOCKED")

    print("Verify LAG bond status is BLOCKED when LAG has no interfaces")
    verify_port_bond_status(sw1, lag_name, "blocked", "Expected the LAG "
                            "to have bond status BLOCKED")
