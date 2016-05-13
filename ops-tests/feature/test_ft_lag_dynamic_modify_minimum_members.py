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

###############################################################################
# Name         test_ft_lag_dynamic_modify_minimum_members.py
#
# Objective:   Verify that it is possible to modify the lower limits of a LAG.
#
# Description: Tests that a previously configured dynamic link aggregation
#              can be modified to have between zero and two members.
#
# Topology:    |Host| ----- |Switch| ------------------ |Switch| ----- |Host|
#                                   (Dynamic LAG - 2 links)
#
# Success Criteria:  PASS -> Number of interfaces on the LAGs are modified
#                            Workstations cannot communicate with at least
#                            one LAG interface still active.
#
#                    FAILED -> Number of interfaces on the LAGs cannot be
#                              modified.
#                              Workstations cannot communicate with at least
#                              1 interface on each LAG or they can communicate
#                              when there are no interfaces on the LAGs.
###############################################################################

from lacp_lib import (
    associate_interface_to_lag,
    associate_vlan_to_l2_interface,
    associate_vlan_to_lag,
    check_connectivity_between_hosts,
    create_lag,
    create_vlan,
    LOCAL_STATE,
    REMOTE_STATE,
    remove_interface_from_lag,
    turn_on_interface,
    validate_interface_not_in_lag,
    verify_lag_config,
    verify_state_sync_lag,
    verify_turn_on_interfaces
)

TOPOLOGY = """

# +-------+                            +-------+
# |       |                            |       |
# |  hs1  |                            |  hs2  |
# |       |                            |       |
# +---1---+                            +---1---+
#     |                                    |
#     |                                    |
#     |                                    |
#     |                                    |
# +---1---+                            +---1---+
# |       |                            |       |
# |       2----------------------------2       |
# |  sw1  4----------------------------4  sw2  |
# |       |                            |       |
# +-------+                            +-------+



# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2
[type=host name="Host 1"] hs1
[type=host name="Host 2"] hs2

# Links
sw1:1 -- hs1:1
sw1:2 -- sw2:2
sw1:3 -- sw2:3
sw1:4 -- sw2:4
sw2:1 -- hs2:1
"""


def test_dynamic_modify_minimum_members(topology, step):

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    hs1 = topology.get('hs1')
    hs2 = topology.get('hs2')

    assert sw1 is not None
    assert sw2 is not None
    assert hs1 is not None
    assert hs2 is not None

    ports_sw1 = list()
    ports_sw2 = list()
    port_labels = ['1', '2', '3', '4']

    lag_id = '1'
    vlan_id = '900'
    mode_active = 'active'
    mode_passive = 'passive'

    step("### Mapping interfaces ###")
    for port in port_labels:
        ports_sw1.append(sw1.ports[port])
        ports_sw2.append(sw2.ports[port])

    step("#### Turning on interfaces in sw1 ###")
    for port in ports_sw1:
        turn_on_interface(sw1, port)

    step("#### Turning on interfaces in sw2 ###")
    for port in ports_sw2:
        turn_on_interface(sw2, port)

    step("#### Validate interfaces are turn on ####")
    verify_turn_on_interfaces(sw1, ports_sw1)
    verify_turn_on_interfaces(sw2, ports_sw2)

    step("##### Create LAGs ####")
    create_lag(sw1, lag_id, mode_active)
    create_lag(sw2, lag_id, mode_passive)

    step("#### Associate Interfaces to LAG ####")
    for intf in ports_sw1[1:4]:
        associate_interface_to_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:4]:
        associate_interface_to_lag(sw2, intf, lag_id)

    step("#### Verify LAG configuration ####")
    verify_lag_config(sw1, lag_id, ports_sw1[1:4], mode=mode_active)
    verify_lag_config(sw2, lag_id, ports_sw2[1:4], mode=mode_passive)

    step("#### Configure VLANs on switches ####")
    create_vlan(sw1, vlan_id)
    create_vlan(sw2, vlan_id)

    associate_vlan_to_l2_interface(sw1, vlan_id, ports_sw1[0])
    associate_vlan_to_lag(sw1, vlan_id, lag_id)

    associate_vlan_to_l2_interface(sw2, vlan_id, ports_sw2[0])
    associate_vlan_to_lag(sw2, vlan_id, lag_id)

    step("#### Configure workstations ####")
    hs1.libs.ip.interface('1', addr='140.1.1.10/24', up=True)
    hs2.libs.ip.interface('1', addr='140.1.1.11/24', up=True)

    step("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[1:4], LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, ports_sw1[1:4], REMOTE_STATE, mode_passive)

    step("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    step("### Remove one interface from each LAG ###")
    remove_interface_from_lag(sw1, ports_sw1[1], lag_id)
    remove_interface_from_lag(sw2, ports_sw2[1], lag_id)

    step("### Validate if the interface was removed of LAG ###")
    validate_interface_not_in_lag(sw1, ports_sw1[1], lag_id)
    validate_interface_not_in_lag(sw2, ports_sw2[1], lag_id)

    step("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[2:4], LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, ports_sw1[2:4], REMOTE_STATE, mode_passive)

    step("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    step("### Turning on interface ###")
    turn_on_interface(sw1, ports_sw1[1])
    turn_on_interface(sw2, ports_sw2[1])

    step("### Validate interface is turn on ###")
    verify_turn_on_interfaces(sw1, ports_sw1[1])
    verify_turn_on_interfaces(sw2, ports_sw2[1])

    step("### Add back the interface ###")
    associate_interface_to_lag(sw1, ports_sw1[1], lag_id)
    associate_interface_to_lag(sw2, ports_sw2[1], lag_id)

    step("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[1:4], LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, ports_sw1[1:4], REMOTE_STATE, mode_passive)

    step("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    step("### Remove all the interfaces from the LAGs ###")
    for intf in ports_sw1[1:4]:
        remove_interface_from_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:4]:
        remove_interface_from_lag(sw2, intf, lag_id)

    step("### Verify if the interfaces were removed from the LAGs ###")
    for intf in ports_sw1[1:4]:
        validate_interface_not_in_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:4]:
        validate_interface_not_in_lag(sw2, intf, lag_id)

    step("#### Negative test ping between clients ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, False)

    step("#### Turning on interfaces in sw1 ###")
    for port in ports_sw1[1:4]:
        turn_on_interface(sw1, port)

    step("#### Turning on interfaces in sw2 ###")
    for port in ports_sw2[1:4]:
        turn_on_interface(sw2, port)

    step("#### Validate interfaces are turn on ####")
    verify_turn_on_interfaces(sw1, ports_sw1)
    verify_turn_on_interfaces(sw2, ports_sw2)

    step("#### Associate Interfaces to LAG ####")
    for intf in ports_sw1[1:4]:
        associate_interface_to_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:4]:
        associate_interface_to_lag(sw2, intf, lag_id)

    step("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[1:4], LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, ports_sw1[1:4], REMOTE_STATE, mode_passive)

    step("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    step("### Remove two the interfaces from the LAGs ###")
    for intf in ports_sw1[1:3]:
        remove_interface_from_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:3]:
        remove_interface_from_lag(sw2, intf, lag_id)

    step("### Verify if the interfaces were removed from the LAGs ###")
    for intf in ports_sw1[1:3]:
        validate_interface_not_in_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:3]:
        validate_interface_not_in_lag(sw2, intf, lag_id)

    step("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[3], LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, ports_sw1[3], REMOTE_STATE, mode_passive)

    step("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    step("#### Turning on interfaces in sw1 ###")
    for port in ports_sw1[1:3]:
        turn_on_interface(sw1, port)

    step("#### Turning on interfaces in sw2 ###")
    for port in ports_sw2[1:3]:
        turn_on_interface(sw2, port)

    step("#### Validate interfaces are turn on ####")
    verify_turn_on_interfaces(sw1, ports_sw1)
    verify_turn_on_interfaces(sw2, ports_sw2)

    step("### Add back the interface ###")
    for intf in ports_sw1[1:3]:
        associate_interface_to_lag(sw1, intf, lag_id)

    for intf in ports_sw1[1:3]:
        associate_interface_to_lag(sw2, intf, lag_id)

    step("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[1:4], LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, ports_sw1[1:4], REMOTE_STATE, mode_passive)

    step("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)
