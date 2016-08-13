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
# Name:        test_ft_lacp_fallback_timeout_priority.py
#
# Objective:   Verify that when lacp fallback is in priority mode and partner
#              is not detected, the period during which the interface with the
#              highest priority forwards traffic is given by the fallback
#              timeout.
#
# Topology:    2 switches (DUT running Halon) connected by 2 interfaces
#              2 workstations connected by the 2 switches.
#
##########################################################################

from pytest import mark
from time import sleep
from lacp_lib import (
    associate_interface_to_lag,
    associate_vlan_to_l2_interface,
    associate_vlan_to_lag,
    check_connectivity_between_hosts,
    config_lacp_rate,
    create_lag,
    create_vlan,
    find_device_label,
    LOCAL_STATE,
    REMOTE_STATE,
    sw_wait_until_all_ready,
    sw_wait_until_any_ready,
    turn_on_interface,
    verify_actor_state,
    verify_lag_config,
    verify_state_sync_lag,
    verify_turn_on_interfaces
)

TOPOLOGY = """
# +-----------------+
# |                 |
# |  Workstation 1  |
# |                 |
# +-------+---------+
#         |
#         |
#   +-----+------+
#   |     3      |
#   |    sw1     |
#   |   1   2    |
#   +---+---+----+
#       |   |
#       |   |     LAG 1
#       |   |
#   +---+---+----+
#   |   1   2    |
#   |     sw2    |
#   |     3      |
#   +-----+------+
#         |
#         |
# +-------+---------+
# |                 |
# |  Workstation 2  |
# |                 |
# +-----------------+

# Nodes
[type=openswitch name="OpenSwitch 1"] sw1
[type=openswitch name="OpenSwitch 2"] sw2
[type=host name="Host src 1" image="gdanii/iperf:latest"] hs1
[type=host name="Host dst 2" image="gdanii/iperf:latest"] hs2

# Links
hs1:1 -- sw1:3
sw1:1 -- sw2:1
sw1:2 -- sw2:2
sw2:3 -- hs2:1
"""


hs1_ip_address = '10.0.10.1'
hs2_ip_address = '10.0.10.2'
# Ports for testing
test_port_tcp = 778
times_to_send = 10
# traffic counters
lag_intf_counter_b = {}
lag_intf_counter_a = {}


# This function verifies that only the interface enabled by fallback forwards
# traffic.
def verify_forwarded_traffic(hs1, hs2, sw, interfaces, intf_fallback):

    for intf in interfaces:
            intf_info = sw.libs.vtysh.show_interface(intf)
            lag_intf_counter_b[intf] = intf_info['tx_packets']

    for x in range(0, times_to_send):
         hs1.libs.iperf.client_start(hs2_ip_address, test_port_tcp, 1, 2, False)

    sleep(20)
    for intf in interfaces:
        intf_info = sw.libs.vtysh.show_interface(intf)
        lag_intf_counter_a[intf] = intf_info['tx_packets']
        delta_tx =\
            lag_intf_counter_a[intf] - lag_intf_counter_b[intf]
        if intf == intf_fallback:
            assert delta_tx > 0,\
            'Interface {intf_fallback} should have forwarded traffic.'\
            .format(**locals())
        else:
            assert delta_tx == 0,\
            'Interface {intf} should not have forwarded traffic.'\
            .format(**locals())


@mark.platform_incompatible(['docker'])
def test_lacp_fallback_timeout_priority(topology, step):
    """
    Case 1:
        Verify that when lacp fallback is in priority mode, partner
        is not detected, and all lag member interfaces have the same priority,
        the period during which the interface selected by fallback forwards
        traffic is given by the fallback timeout.
    Case 2:
        Verify that when lacp fallback is in priority mode, partner
        is not detected, and lag member interfaces have different priority,
        the period during which the interface with the highest priority
        forwards traffic is given by the fallback timeout.
    """
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    hs1 = topology.get('hs1')
    hs2 = topology.get('hs2')
    hs1_ip_address_with_mask = '10.0.10.1/24'
    hs2_ip_address_with_mask = '10.0.10.2/24'
    sw1_lag_id = '10'
    sw2_lag_id = '20'
    vlan_identifier = '8'
    number_pings = 5

    assert sw1 is not None
    assert sw2 is not None
    assert hs1 is not None
    assert hs2 is not None

    ports_sw1 = list()
    ports_sw2 = list()
    port_labels = ['1', '2', '3']

    step("Mapping interfaces")
    for port in port_labels:
        ports_sw1.append(sw1.ports[port])
        ports_sw2.append(sw2.ports[port])

    step("Sorting the port list")
    ports_sw1.sort()
    ports_sw2.sort()

    step("Turning on all interfaces used in this test")
    for port in ports_sw1:
        turn_on_interface(sw1, port)

    for port in ports_sw2:
        turn_on_interface(sw2, port)

    step("Validate interfaces are turned on")
    verify_turn_on_interfaces(sw1, ports_sw1)
    verify_turn_on_interfaces(sw2, ports_sw2)

    ###########################################################################
    #                     Topology configuraion
    ###########################################################################

    step("Assign an IP address on the same range to each workstation")
    hs1.libs.ip.interface('1', addr=hs1_ip_address_with_mask, up=True)
    hs2.libs.ip.interface('1', addr=hs2_ip_address_with_mask, up=True)

    step('Creating VLAN in both switches')
    create_vlan(sw1, vlan_identifier)
    create_vlan(sw2, vlan_identifier)

    step("Create LAG in both switches")
    create_lag(sw1, sw1_lag_id, 'active')
    create_lag(sw2, sw2_lag_id, 'active')
    config_lacp_rate(sw1, sw1_lag_id, True)
    config_lacp_rate(sw2, sw2_lag_id, True)

    step("Associate interfaces [1, 2] to LAG in both switches")
    for port in ports_sw1[0:2]:
        associate_interface_to_lag(sw1, port, sw1_lag_id)
    for port in ports_sw2[0:2]:
        associate_interface_to_lag(sw2, port, sw2_lag_id)

    step("Verify LAG configuration")
    verify_lag_config(sw1, sw1_lag_id, ports_sw1[0:2],
                      mode='active', heartbeat_rate='fast')
    verify_lag_config(sw2, sw2_lag_id, ports_sw2[0:2],
                      mode='active', heartbeat_rate='fast')

    step("Configure LAGs and workstations interfaces with same VLAN")
    associate_vlan_to_lag(sw1, vlan_identifier, sw1_lag_id)
    associate_vlan_to_lag(sw2, vlan_identifier, sw2_lag_id)
    associate_vlan_to_l2_interface(sw1, vlan_identifier, ports_sw1[2])
    associate_vlan_to_l2_interface(sw2, vlan_identifier, ports_sw2[2])

    step("Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[0:2], LOCAL_STATE, 'active')
    verify_state_sync_lag(sw1, ports_sw1[0:2], REMOTE_STATE, 'active')
    verify_state_sync_lag(sw2, ports_sw2[0:2], LOCAL_STATE, 'active')
    verify_state_sync_lag(sw2, ports_sw2[0:2], REMOTE_STATE, 'active')

    step("Ping workstation 2 from workstation 1 and viceversa")
    check_connectivity_between_hosts(hs1, hs1_ip_address, hs2, hs2_ip_address,
                                     number_pings, True)

    ###########################################################################
    #         Enabling LAG Fallback and setting timeout in both Switches
    ###########################################################################
    step('Enabling Fallback mode on LAG %s on Switch 1' % sw1_lag_id)
    with sw1.libs.vtysh.ConfigInterfaceLag(sw1_lag_id) as ctx:
        ctx.lacp_fallback()
        ctx.lacp_fallback_timeout(60)
    lacp_map = sw1.libs.vtysh.show_lacp_aggregates()
    assert lacp_map['lag' + sw1_lag_id]['fallback'] and \
        lacp_map['lag' + sw1_lag_id]['fallback_mode'] == 'priority' and \
        lacp_map['lag' + sw1_lag_id]['fallback_timeout'] == '60' ,\
        'Fallback should be enable in priority mode and timeout should be 60'

    step('Enabling Fallback mode on LAG %s on Switch 2' % sw2_lag_id)
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_fallback()
        ctx.lacp_fallback_timeout(60)
    lacp_map = sw2.libs.vtysh.show_lacp_aggregates()
    assert lacp_map['lag' + sw2_lag_id]['fallback'] and \
        lacp_map['lag' + sw2_lag_id]['fallback_mode'] == 'priority' and \
        lacp_map['lag' + sw2_lag_id]['fallback_timeout'] == '60' ,\
        'Fallback should be enable in priority mode and timeout should be 60'

    ###########################################################################
    #
    #                     Case 1: Interfaces with the same priority.
    #
    ###########################################################################
    ###########################################################################
    #                           Disabling LAG Switch 2
    ###########################################################################
    step('Change LAG mode on switch 2 to off')
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.no_lacp_mode_active()

    step('Validate interfaces state with fallback')
    intf_fallback = verify_actor_state('asfncde', [sw1], ports_sw1[0:2], any=True)

    step('Verify that during the fallback_timeout period, the interface ' +
         'forwards traffic')
    counter = 0
    hs2.libs.iperf.server_start(test_port_tcp, 20, False)
    while counter < 3:
        verify_forwarded_traffic(hs1, hs2, sw1, ports_sw1[0:2], intf_fallback)
        counter += 1
    time_remaining = 1
    while (time_remaining > 0):
        sleep(1)
        output = sw1.libs.vtysh.diag_dump_lacp_basic()
        time_remaining = output['State'][sw1_lag_id][intf_fallback]\
            ['timeout_remaining']

    step('Verify that after the fallback_timeout period, the interface does ' +
         'not forwards traffic')
    verify_forwarded_traffic(hs1, hs2, sw1, ports_sw1[0:2], None)

    ###########################################################################
    #                           Enabling LAG Switch 2
    ###########################################################################
    step('Change LAG mode on switch 2 to active')
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.lacp_mode_active()

    ###########################################################################
    #                       Verifying LAGs on both Switches
    ###########################################################################
    step('Verify interfaces are AFNCD on both switches')
    verify_actor_state('asfncd', [sw1], ports_sw1[0:2])
    verify_actor_state('asfncd', [sw2], ports_sw2[0:2])

    ###########################################################################
    #
    #                     Case 2: Interfaces with different priority.
    #
    ###########################################################################

    ###########################################################################
    #            Assign different priorities to the interfaces
    ###########################################################################
    with sw1.libs.vtysh.ConfigInterface(ports_sw1[0]) as ctx:
        ctx.lacp_port_priority(10)
    with sw1.libs.vtysh.ConfigInterface(ports_sw1[1]) as ctx:
        ctx.lacp_port_priority(2)
    ###########################################################################
    #                           Disabling LAG Switch 2
    ###########################################################################
    step('Change LAG mode on switch 2 to off')
    with sw2.libs.vtysh.ConfigInterfaceLag(sw2_lag_id) as ctx:
        ctx.no_lacp_mode_active()

    step('Validate interfaces state with fallback')
    intf_fallback = verify_actor_state('asfncde', [sw1], ports_sw1[0:2], any=True)

    assert intf_fallback == ports_sw1[1],\
        'Interface {ports_sw1[1]} should be enabled by fallback.'\
            .format(**locals())

    step('Verify that during the fallback_timeout period, the interface ' +
         'forwards traffic')
    counter = 0
    hs2.libs.iperf.server_start(test_port_tcp, 20, False)
    while counter < 2:
        verify_forwarded_traffic(hs1, hs2, sw1, ports_sw1[0:2], intf_fallback)
        counter += 1
    sleep(20)
    step('Verify that after the fallback_timeout period, the interface does ' +
         'not forwards traffic')
    verify_forwarded_traffic(hs1, hs2, sw1, ports_sw1[0:2], None)
