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

"""OpenSwitch Test Suite for LAG with fallback."""

from lacp_lib import (
    associate_interface_to_lag,
    create_lag_active,
    set_lag_rate,
    turn_on_interface,
    verify_actor_state,
    verify_turn_on_interfaces
)

from pytest import fixture

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

sw1_lag_id = '100'
sw2_lag_id = '100'

port_labels = ['1', '2']


@fixture(scope='module')
def main_setup(request, topology):
    """Test Suite Common Topology."""
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    print('Verifying switches are not None')
    assert sw1 is not None
    assert sw2 is not None

    for port in port_labels:
        print('Turning On interface %s on Switch 1' % port)
        turn_on_interface(sw1, port)

    for port in port_labels:
        print('Turning On interface %s on Switch 2' % port)
        turn_on_interface(sw2, port)

    print('Verifying interfaces of Switch 1')
    verify_turn_on_interfaces(sw1, port_labels)

    print('Verifying interfaces of Switch 2')
    verify_turn_on_interfaces(sw2, port_labels)

    print('Creating LAG %s on Switch 1' % sw1_lag_id)
    create_lag_active(sw1, sw1_lag_id)

    print('Creating LAG %s on Switch 2' % sw2_lag_id)
    create_lag_active(sw2, sw2_lag_id)

    print('Setting LAG %s to "fast" on Switch 1' % sw1_lag_id)
    set_lag_rate(sw1, sw1_lag_id, 'fast')

    print('Setting LAG %s to "fast" on Switch 1' % sw1_lag_id)
    set_lag_rate(sw2, sw2_lag_id, 'fast')

    for port in port_labels:
        print('Associate interfaces %s to lag on Switch 1' % port)
        associate_interface_to_lag(sw1, port, sw1_lag_id)

        print('Associate interfaces %s to lag on Switch 2' % port)
        associate_interface_to_lag(sw2, port, sw2_lag_id)

    print('Verify interfaces are AFNCD on both switches')
    verify_actor_state('asfncd', [sw1, sw2], port_labels)


def test_lag_fallback(topology, main_setup, step):
    """Test Case: LAG fallback."""
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    step('Verifying switches are not None')
    assert sw1 is not None
    assert sw2 is not None

    ###########################################################################
    #
    #                           Disabling LAG Switch 2
    #
    ###########################################################################
    step('Change LAG mode on switch 2 to off')
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.no_lacp_mode_active()

    step('Verifying Switch 1 interfaces are AFOEX')
    verify_actor_state('asfoex', [sw1], port_labels)

    ###########################################################################
    #
    #                           Enabling LAG Switch 2
    #
    ###########################################################################
    step('Change LAG mode on switch 2 to active')
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_mode_active()

    ###########################################################################
    #
    #                     Enabling LAG Fallback both Switches
    #
    ###########################################################################
    step('Enabling Fallback mode on LAG %s on Switch 1' % sw1_lag_id)
    with sw1.libs.vtysh.ConfigInterfaceLag(sw1_lag_id) as ctx:
        ctx.lacp_fallback()

    step('Enabling Fallback mode on LAG %s on Switch 2' % sw2_lag_id)
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_fallback()

    ###########################################################################
    #
    #                           Disabling LAG Switch 2
    #
    ###########################################################################
    step('Change LAG mode on switch 2 to off')
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.no_lacp_mode_active()

    step('Validate interfaces state with fallback')
    intf_fallback = verify_actor_state('asfncd', [sw1], port_labels, any=True)

    step('Interface enabled found: %s' % intf_fallback)
    tmp = list(port_labels)
    tmp.remove(intf_fallback)

    step('Validate intefaces without fallback')
    verify_actor_state('asfoe', [sw1], tmp)

    ###########################################################################
    #
    #                           Enabling LAG Switch 2
    #
    ###########################################################################
    step('Change LAG mode on switch 2 to active')
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_mode_active()

    ###########################################################################
    #
    #                       Verifying LAGs on both Switches
    #
    ###########################################################################
    step('Verify interfaces are AFNCD on both switches')
    verify_actor_state('asfncd', [sw1, sw2], port_labels)
