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
# Name         test_ft_lag_dynamic_maximum_member.py
#
# Objective:   Verify that a dynamic LAG that contains 8 members can be deleted
#
# Topology:    |Host| ----- |Switch| ------------------ |Switch| ----- |Host|
#                                   (Dynamic LAG - 8 links)
#
# Success Criteria:  PASS -> LAGs can be created and deleted without errors
#                            Workstations can communicate when LAGs are created
#                            Workstations cannot communicate when LAGs
#                            are deleted.
#
#                    FAILED -> LAGs cannot be created or deleted or there
#                              are errors when doing so.
#                              Workstations cannot communicate when the
#                              LAGs are created.
#                              Workstations can communicate after deleting
#                              the LAGs.
#
###############################################################################

from time import sleep
from lacp_lib import turn_on_interface
from lacp_lib import validate_turn_on_interfaces
from lacp_lib import create_lag_active
from lacp_lib import create_lag_passive
from lacp_lib import associate_interface_to_lag
from lacp_lib import associate_vlan_to_l2_interface
from lacp_lib import associate_vlan_to_lag
from lacp_lib import create_vlan
from lacp_lib import check_connectivity_between_hosts
from lacp_lib import delete_lag

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
# |  sw1  9----------------------------9  sw2  |
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
sw1:5 -- sw2:5
sw1:6 -- sw2:6
sw1:7 -- sw2:7
sw1:8 -- sw2:8
sw1:9 -- sw2:9
sw2:1 -- hs2:1
"""


def test_dynamic_maximum_members(topology):

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
    p14 = sw1.ports['4']
    p15 = sw1.ports['5']
    p16 = sw1.ports['6']
    p17 = sw1.ports['7']
    p18 = sw1.ports['8']
    p19 = sw1.ports['9']
    p21h = sw2.ports['1']
    p22 = sw2.ports['2']
    p23 = sw2.ports['3']
    p24 = sw2.ports['4']
    p25 = sw2.ports['5']
    p26 = sw2.ports['6']
    p27 = sw2.ports['7']
    p28 = sw2.ports['8']
    p29 = sw2.ports['9']

    ports_sw1 = [p11h, p12, p13, p14, p15, p16, p17, p18, p19]
    ports_sw2 = [p21h, p22, p23, p24, p25, p26, p27, p28, p29]

    lag_id = '1'
    vlan_id = '900'

    print("#### Turning on interfaces in sw1 ###")
    for port in ports_sw1:
        turn_on_interface(sw1, port)

    print("#### Turning on interfaces in sw2 ###")
    for port in ports_sw2:
        turn_on_interface(sw2, port)

    print("#### Wait for interfaces to turn on ####")
    sleep(60)

    print("#### Validate interfaces are turn on ####")
    validate_turn_on_interfaces(sw1, ports_sw1)
    validate_turn_on_interfaces(sw2, ports_sw2)

    print("##### Create LAGs ####")
    create_lag_active(sw1, lag_id)
    create_lag_passive(sw2, lag_id)

    print("#### Associate Interfaces to LAG ####")
    for intf in ports_sw1[1:9]:
        associate_interface_to_lag(sw1, intf, lag_id)

    for intf in ports_sw2[1:9]:
        associate_interface_to_lag(sw2, intf, lag_id)

    print("#### Wait for LAG negotiation ####")
    sleep(40)

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

    print("#### Waiting for vlan and interface configuration ####")
    sleep(100)
    print("#### Test ping between clients work ####")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, True)

    print("#### Delete LAG ####")
    delete_lag(sw1, lag_id)
    delete_lag(sw2, lag_id)

    print("#### Negative Test ping between clients ###")
    check_connectivity_between_hosts(hs1, '140.1.1.10', hs2, '140.1.1.11',
                                     5, False)
