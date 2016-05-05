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
# Name         test_ft_lag_dynamic_minimum_members.py
#
# Objective:   Verify that a dynamic LAG of 2 members or less can be deleted.
#
# Topology:    |Host| ----- |Switch| ------------------ |Switch| ----- |Host|
#                                   (Dynamic LAG - 2 links)
#
# Success Criteria:  PASS ->  LAGs can be recreated and deleted without errors.
#                             Workstations can communicate when a LAG is
#                             created with at least one interface.
#                             Workstations cannot communicate when LAGs are
#                             deleted or the LAG has no interfaces associated.
#
#                    FAILED -> LAGs cannot be created or deleted or there
#                              are errors when doing so.
#                              Workstations cannot communicate when a LAG
#                              is created with at least 1 interface.
#                              Workstations can communicate after deleting
#                              a LAG or when the LAG has no associated
#                              interfaces.
###############################################################################

from lacp_lib import turn_on_interface
from lacp_lib import create_lag
from lacp_lib import associate_interface_to_lag
from lacp_lib import associate_vlan_to_l2_interface
from lacp_lib import associate_vlan_to_lag
from lacp_lib import create_vlan
from lacp_lib import check_connectivity_between_hosts
from lacp_lib import delete_lag
from lacp_lib import verify_turn_on_interfaces
from lacp_lib import verify_lag_config
from lacp_lib import LOCAL_STATE
from lacp_lib import REMOTE_STATE
from lacp_lib import verify_state_sync_lag

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
# |  sw1  3----------------------------3  sw2  |
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
sw2:1 -- hs2:1
"""


def test_dynamic_minimum_members(topology):

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    hs1 = topology.get('hs1')
    hs2 = topology.get('hs2')

    assert sw1 is not None
    assert sw2 is not None
    assert hs1 is not None
    assert hs2 is not None

    p11h = sw1.ports['1']
    p12 = sw1.ports['2']
    p13 = sw1.ports['3']
    p21h = sw2.ports['1']
    p22 = sw2.ports['2']
    p23 = sw2.ports['3']

    ports_sw1 = [p11h, p12, p13]
    ports_sw2 = [p21h, p22, p23]

    lag_id = '1'
    vlan_id = '900'
    mode_active = 'active'
    mode_passive = 'passive'

    print("#### Turning on interfaces in sw1 ###")
    for port in ports_sw1:
        turn_on_interface(sw1, port)

    print("#### Turning on interfaces in sw2 ###")
    for port in ports_sw2:
        turn_on_interface(sw2, port)

    print("#### Validate interfaces are turn on ####")
    verify_turn_on_interfaces(sw1, ports_sw1)
    verify_turn_on_interfaces(sw2, ports_sw2)

    print("##### Create LAGs ####")
    create_lag(sw1, lag_id, mode_active)
    create_lag(sw2, lag_id, mode_passive)

    print("#### Associate Interfaces to LAG ####")
    for intf in ports_sw1[1:3]:
        associate_interface_to_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:3]:
        associate_interface_to_lag(sw2, intf, lag_id)

    print("#### Verify LAG configuration ####")
    verify_lag_config(sw1, lag_id, ports_sw1[1:3], mode=mode_active)
    verify_lag_config(sw2, lag_id, ports_sw2[1:3], mode=mode_passive)

    print("#### Configure VLANs on switches ####")
    create_vlan(sw1, vlan_id)
    create_vlan(sw2, vlan_id)

    associate_vlan_to_l2_interface(sw1, vlan_id, p11h)
    associate_vlan_to_lag(sw1, vlan_id, lag_id)

    associate_vlan_to_l2_interface(sw2, vlan_id, p21h)
    associate_vlan_to_lag(sw2, vlan_id, lag_id)

    print("#### Configure workstations ####")
    hs1.libs.ip.interface('1', addr='140.1.1.10/24', up=True)
    hs2.libs.ip.interface('1', addr='140.1.1.11/24', up=True)

    print("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1[1:3], LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, ports_sw1[1:3], REMOTE_STATE, mode_passive)

    print("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    print("### Delete LAGs ###")
    delete_lag(sw1, lag_id)
    delete_lag(sw2, lag_id)

    print("#### Negative test ping between clients ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, False)

    print("##### Create LAGs ####")
    create_lag(sw1, lag_id, mode_active)
    create_lag(sw2, lag_id, mode_passive)

    print("#### Associate Interface to LAG ####")
    associate_interface_to_lag(sw1, p12, lag_id)
    associate_interface_to_lag(sw2, p22, lag_id)

    print("#### Verify LAG configuration ####")
    verify_lag_config(sw1, lag_id, p12, mode=mode_active)
    verify_lag_config(sw2, lag_id, p22, mode=mode_passive)

    print("### Associate Vlan to LAG")
    associate_vlan_to_lag(sw1, vlan_id, lag_id)
    associate_vlan_to_lag(sw2, vlan_id, lag_id)

    print("### Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, p12, LOCAL_STATE, mode_active)
    verify_state_sync_lag(sw1, p12, REMOTE_STATE, mode_passive)

    print("#### Test ping between clients ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    print("### Delete LAGs ###")
    delete_lag(sw1, lag_id)
    delete_lag(sw2, lag_id)

    print("#### Negative test ping between clients ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, False)

    print("##### Create LAGs ####")
    create_lag(sw1, lag_id, mode_active)
    create_lag(sw2, lag_id, mode_passive)

    print("### Delete LAGs ###")
    delete_lag(sw1, lag_id)
    delete_lag(sw2, lag_id)
