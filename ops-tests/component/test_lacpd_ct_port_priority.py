# Copyright (C) 2016 Hewlett-Packard Development Company, L.P.
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

"""Port Priority Test Suite.

Name:        test_lacpd_ct_port_priority.py

Objective:   Verify test cases for port priority functionality

Topology:    2 switch (DUT running OpenSwitch)

"""

from lib_test import (
    print_header,
    remove_intf_parameter,
    set_port_parameter,
    sw_clear_user_config,
    sw_create_bond,
    sw_delete_lag,
    sw_set_intf_other_config,
    sw_set_intf_user_config,
    sw_wait_until_all_sm_ready
)

import pytest


TOPOLOGY = """
#
# +-------+     +-------+
# |       <----->       |
# |       |     |       |
# |       <----->       |
# |       |     |       |
# | sw1   <----->  sw2  |
# |       |     |       |
# |       <----->       |
# |       |     |       |
# |       <----->       |
# +-------+     +-------+

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2

# Links
# 1 Gig ports
sw1:if01 -- sw2:if01
sw1:if02 -- sw2:if02
sw1:if03 -- sw2:if03
sw1:if04 -- sw2:if04
sw1:if05 -- sw2:if05
"""


sw_1g_intf_start = 1
sw_1g_intf_end = 5
port_labels_1G = ['if01', 'if02', 'if03', 'if04', 'if05']
sw_1g_intf = []

sm_col_and_dist = '"Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,Dist:1,Def:0,Exp:0"'
sm_in_sync = '"Activ:1,TmOut:1,Aggr:1,Sync:1,Col:0,Dist:0,Def:0,Exp:0"'
sm_out_sync = '"Activ:1,TmOut:1,Aggr:1,Sync:0,Col:0,Dist:0,Def:0,Exp:0"'


@pytest.fixture(scope='module')
def main_setup(request, topology):
    """Test Suit Setup."""
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    global sw_1g_intf, port_labels_1G
    for lbl in port_labels_1G:
        sw_1g_intf.append(sw1.ports[lbl])


@pytest.fixture()
def setup(request, topology):
    """Test Case Setup."""
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    def cleanup():
        print('Clear the user_config of all the Interfaces.\n'
              'Reset the pm_info to default values.')
        for intf in range(sw_1g_intf_start, sw_1g_intf_end):
            sw_clear_user_config(sw1, intf)
            sw_clear_user_config(sw2, intf)

    request.addfinalizer(cleanup)


def test_lacpd_lag_dynamic_port_priority(topology, step, main_setup, setup):
    """Dynamic Port Priority Test Case.

    Test the port priority functionality of LACP by setting a lower priority to
    an interface and allowing other interfaces with higher priority to join the
    corresponding LAGs.
    Two switches are connected with five interfaces using 2 LAGs in active
    mode.

    In switch 1, LAG 1 is formed with interfaces 1 and 2, LAG 2 is formed with
    interfaces 3, 4 and 5
    In switch 2, LAG 1 is formed with interfaces 1, 2 and 3, LAG 2 is formed
    with interfaces 4 and 5
    """
    print_header('lacpd dynamic LAG port priority test')
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    # Enable all the interfaces under test.
    step('Enabling interfaces [1, 2, 3, 4, 5] in all switches\n')
    for intf in sw_1g_intf[0:5]:
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])

    step('Creating active LAGs in switches\n')
    sw_create_bond(sw1, 'lag1', sw_1g_intf[0:2], lacp_mode='active')
    sw_create_bond(sw1, 'lag2', sw_1g_intf[2:5], lacp_mode='active')
    sw_create_bond(sw2, 'lag1', sw_1g_intf[0:3], lacp_mode='active')
    sw_create_bond(sw2, 'lag2', sw_1g_intf[3:5], lacp_mode='active')

    step('Setting LAGs lacp rate as fast in switches\n')
    set_port_parameter(sw1, 'lag1', ['other_config:lacp-time=fast'])
    set_port_parameter(sw1, 'lag2', ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, 'lag1', ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, 'lag2', ['other_config:lacp-time=fast'])

    """
    Every interface have the default port priority
    Switch 1:
        Interface 1 must be ASFNCD
        Interface 2 must be ASFNCD
        Interface 3 must be ASFN
        Interface 4 must be ASFO
        Interface 5 must be ASFO
    Switch 2:
        Interface 1 must be ASFNCD
        Interface 2 must be ASFNCD
        Interface 3 must be ASFO
        Interface 4 must be ASFN
        Interface 5 must be ASFN
    """
    step('Verify state machines on all switches\n')
    step('Verify LAG 1 on switch 1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[0:2], sm_col_and_dist)

    step('Verify LAG 2 on switch 1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[2], sm_in_sync)
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[3:5], sm_out_sync)

    step('Verify LAG 1 on switch 2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[0:2], sm_col_and_dist)
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[2], sm_out_sync)

    step('Verify LAG 2 on switch 2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[3:5], sm_in_sync)

    step('Setting port priorities\n')
    sw_set_intf_other_config(sw1, '1', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw1, '2', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw1, '3', ['lacp-port-priority=200'])
    sw_set_intf_other_config(sw1, '4', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw1, '5', ['lacp-port-priority=100'])

    sw_set_intf_other_config(sw2, '1', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw2, '2', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw2, '3', ['lacp-port-priority=200'])
    sw_set_intf_other_config(sw2, '4', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw2, '5', ['lacp-port-priority=100'])

    """
    Interface 3 has the lower priority, this allows other interfaces to
    agreggate to the LAGs
    Switch 1:
        Interface 1 must be ASFNCD
        Interface 2 must be ASFNCD
        Interface 3 must be ASFO
        Interface 4 must be ASFNCD
        Interface 5 must be ASFNCD
    Switch 2:
        Interface 1 must be ASFNCD
        Interface 2 must be ASFNCD
        Interface 3 must be ASFO
        Interface 4 must be ASFNCD
        Interface 5 must be ASFNCD
    """
    step('Verify state machines on all switches\n')

    tmp = list(sw_1g_intf)
    tmp.remove(sw_1g_intf[2])

    step('Verify LAG 1 on switch 1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[0:2], sm_col_and_dist)

    step('Verify LAG 2 on switch 1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[2], sm_out_sync)
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[3:5], sm_col_and_dist)

    step('Verify LAG 1 on switch 2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[0:2], sm_col_and_dist)
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[2], sm_out_sync)

    step('Verify LAG 2 on switch 2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[3:5], sm_col_and_dist)

    # Cleanup
    for intf in sw_1g_intf[0:5]:
        remove_intf_parameter(sw1,
                              intf,
                              'other_config',
                              ['lacp-port-priority'])

        remove_intf_parameter(sw1,
                              intf,
                              'other_config',
                              ['lacp-port-priority'])

    sw_delete_lag(sw1, 'lag1')
    sw_delete_lag(sw1, 'lag2')
    sw_delete_lag(sw2, 'lag1')
    sw_delete_lag(sw2, 'lag2')


def test_lacpd_lag_dynamic_partner_priority(topology, step, main_setup, setup):
    """Dynamic Partner Priority Test Case.

    Test the port priority functionality of LACP by testing the partner port
    priority. If two interfaces have the same port priority, the decision is
    made using the partner port priority.

    Two switches are connected with 4 interfaces
    In switch 1, LAG 1 is formed with interfaces 1 to 4.
    In switch 2, LAG 1 is formed with interfaces 1 and 2, LAG 2 is formed with
    interfaces 3 and 4
    """
    print_header('lacpd dynamic LAG partner priority test')
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    # Enable all the interfaces under test.
    step('Enabling interfaces [1, 2, 3, 4] in all switches\n')
    for intf in sw_1g_intf[0:4]:
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])

    step('Creating active LAGs in switches\n')
    sw_create_bond(sw1, 'lag1', sw_1g_intf[0:4], lacp_mode='active')
    sw_create_bond(sw2, 'lag1', sw_1g_intf[0:2], lacp_mode='active')
    sw_create_bond(sw2, 'lag2', sw_1g_intf[2:4], lacp_mode='active')

    step('Setting LAGs lacp rate as fast in switches\n')
    set_port_parameter(sw1, 'lag1', ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, 'lag1', ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, 'lag2', ['other_config:lacp-time=fast'])

    step('Setting port priorities\n')
    sw_set_intf_other_config(sw1, '1', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw1, '2', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw1, '3', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw1, '4', ['lacp-port-priority=100'])

    sw_set_intf_other_config(sw2, '1', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw2, '2', ['lacp-port-priority=100'])
    sw_set_intf_other_config(sw2, '3', ['lacp-port-priority=1'])
    sw_set_intf_other_config(sw2, '4', ['lacp-port-priority=1'])

    """
    Interface 3 and 4 in switch 2 have the higher priority, LAG 1 in switch 1
    will connect to the LAG 2 because the partner has higher priority

    Switch 1:
        Interface 1 must be ASFO
        Interface 2 must be ASFO
        Interface 3 must be ASFNCD
        Interface 4 must be ASFNCD
    Switch 2:
        Interface 1 must be ASFN
        Interface 2 must be ASFN
        Interface 3 must be ASFNCD
        Interface 4 must be ASFNCD
    """
    step('Verify state machines in all switches\n')
    step('Verify LAG 1 on switch 1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[0:2], sm_out_sync)
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[2:4], sm_col_and_dist)

    step('Verify LAG 1 on switch 2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[0:2], sm_in_sync)

    step('Verify LAG 1 on switch 2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[2:4], sm_col_and_dist)

    # Cleanup
    for intf in sw_1g_intf[0:4]:
        remove_intf_parameter(sw1,
                              intf,
                              'other_config',
                              ['lacp-port-priority'])

        remove_intf_parameter(sw2,
                              intf,
                              'other_config',
                              ['lacp-port-priority'])

    sw_delete_lag(sw1, 'lag1')
    sw_delete_lag(sw2, 'lag1')
    sw_delete_lag(sw2, 'lag2')
