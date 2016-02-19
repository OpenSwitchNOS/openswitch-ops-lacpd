# -*- coding: utf-8 -*-
#
# Copyright (C) 201 Hewlett Packard Enterprise Development LP
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
# Name:        CT_LAG_Dynamic_Linux_Bonding_Configuration.py
#
# Objective:   Verify Linux bonding is configured properly when LAG are
#              created and deleted, also when interfaces are added and
#              removed.
#
# Topology:    2 switches (DUT running Halon) connected by 3 interfaces
#
##########################################################################

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
"""


def create_lag_active(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_mode_active()


def create_lag_passive(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_mode_passive()


def delete_lag(sw, lag_id):
    with sw.libs.vtysh.Configure() as ctx:
        ctx.no_interface_lag(lag_id)


def associate_interface_to_lag(sw, interface, lag_id):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.lag(lag_id)


def remove_interface_from_lag(sw, interface, lag_id):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.no_lag(lag_id)


# Check if linux bond exists based on ifconfig output
def sw_is_linux_bond_created(sw, lag_id):
    bond_name = "lag" + lag_id
    assert not sw('ip netns exec swns bash'.format(**locals()),
                  shell='bash')

    cmd_output = sw('ifconfig'.format(**locals()),
                    shell='bash')
    lines = cmd_output.split('\n')
    for line in lines:
        if bond_name in line:
            return True
    return False


# Check if linux bond exists based on ifconfig output
def sw_is_interface_in_bond(sw, lag_id, intf_name):
    bond_name = "lag" + lag_id
    assert not sw('ip netns exec swns bash'.format(**locals()),
                  shell='bash')

    c = "cat /sys/class/net/" + bond_name + "/bonding/slaves"
    cmd_output = sw(c.format(**locals()), shell='bash')

    if intf_name in cmd_output:
            return True
    return False


def test_lag_linux_bond_configuration(topology):
    """
    Case 1:
        Verify Linux bonding drivers files are configured
        correctly when LAG is created/deleted and when
        interfaces are added/removed.
    """
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    sw1_lag_id = '1'
    sw2_lag_id = '2'

    assert sw1 is not None
    assert sw2 is not None

    p11 = sw1.ports['1']
    p12 = sw1.ports['2']
    p13 = sw1.ports['3']
    p21 = sw2.ports['1']
    p22 = sw2.ports['2']
    p23 = sw2.ports['3']

    ports_sw1 = [p11, p12, p13]
    ports_sw2 = [p21, p22, p23]

    # Create LAG in both switches
    create_lag_active(sw1, sw1_lag_id)
    create_lag_active(sw2, sw2_lag_id)

    # Verify if Linux bond has been created for each LAG
    assert sw_is_linux_bond_created(sw1, sw1_lag_id),\
        "Linux Bonding for LAG " + sw1_lag_id + " should be created"
    assert sw_is_linux_bond_created(sw2, sw2_lag_id),\
        "Linux Bonding for LAG " + sw2_lag_id + " should be created"

    # Add interfaces to each LAG
    for interface in ports_sw1:
        associate_interface_to_lag(sw1, interface, sw1_lag_id)
    for interface in ports_sw2:
        associate_interface_to_lag(sw2, interface, sw2_lag_id)

    # Verify the interfaces were added to the linux bond
    for interface in ports_sw1:
        assert sw_is_interface_in_bond(sw1, sw1_lag_id, interface),\
            "Interface " + interface + " should be part of bond " +\
            "for LAG " + sw1_lag_id
    for interface in ports_sw2:
        assert sw_is_interface_in_bond(sw2, sw2_lag_id, interface),\
            "Interface " + interface + " should be part of bond " +\
            "for LAG " + sw2_lag_id

    # Remove interfaces from each LAG
    remove_interface_from_lag(sw1, p11, sw1_lag_id)
    remove_interface_from_lag(sw2, p22, sw2_lag_id)

    # Verify the interface was removed from the linux bond
    assert not sw_is_interface_in_bond(sw1, sw1_lag_id, p11),\
        "Interface " + p11 + " should not be part of bond " +\
        "for LAG " + sw1_lag_id
    assert not sw_is_interface_in_bond(sw2, sw2_lag_id, p22),\
        "Interface " + p22 + " should not be part of bond " +\
        "for LAG " + sw2_lag_id

    ports_sw1 = [p12, p13]
    ports_sw2 = [p21, p23]

    # Verify the remaining interfaces are still in the linux bond
    for interface in ports_sw1:
        assert sw_is_interface_in_bond(sw1, sw1_lag_id, interface),\
            "Interface " + interface + " should be part of bond " +\
            "for LAG " + sw1_lag_id
    for interface in ports_sw2:
        assert sw_is_interface_in_bond(sw2, sw2_lag_id, interface),\
            "Interface " + interface + " should be part of bond " +\
            "for LAG " + sw2_lag_id

    # Delete LAG in both switches
    delete_lag(sw1, sw1_lag_id)
    delete_lag(sw2, sw2_lag_id)

    assert not sw_is_linux_bond_created(sw1, sw1_lag_id),\
        "Linux Bonding for LAG " + sw1_lag_id + " should be deleted"
    assert not sw_is_linux_bond_created(sw2, sw2_lag_id),\
        "Linux Bonding for LAG " + sw2_lag_id + " should be deleted"
