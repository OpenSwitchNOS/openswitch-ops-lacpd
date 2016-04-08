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

import ipdb
import pytest
from time import sleep

from lib_test import (
    clear_port_parameter,
    print_header,
    remove_port_parameter,
    sw_set_intf_user_config,
    sw_clear_user_config,
    set_intf_parameter,
    set_port_parameter,
    sw_set_intf_pm_info,
    sw_create_bond,
    sw_wait_until_all_sm_ready,
    verify_intf_in_bond,
    verify_intf_not_in_bond,
    verify_intf_status
)

TOPOLOGY = """
#
# +-------+     +-------+
# |  sw1  <----->  sw2  |
# +-------+     +-------+
#

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2

# Links
# 1 Gig ports
sw1:1 -- sw2:1
sw1:2 -- sw2:2
"""

# Interfaces from 1-2 are 1G ports.
sw_1g_intf_start = 1
sw_1g_intf_end = 3
n_1g_links = 2
port_labels_1g = ['1', '2']
sw_1g_intf = []

test_lag = 'lag1'

###############################################################################
#
#                       ACTOR STATE STATE MACHINES VARIABLES
#
###############################################################################
# Everything is working and 'Collecting and Distributing'
active_ready = '"Activ:1,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:0,Exp:0"'
# No fallback enabled, interface is 'dead'
active_no_fallback = '"Activ:1,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:1"'
# Fallback enabled, in 'Defaulted' but 'Collecting and Distributing'
active_fallback = '"Activ:1,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:1,Exp:0"'
# Interface from same LAG with Fallback enabled but not assign to 'listen'
active_other_intf = '"Activ:1,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:0"'

passive_ready = '"Activ:0,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:0,Exp:0"'
# No fallback enabled, interface is 'dead'
passive_no_fallback = '"Activ:0,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:1"'
# Fallback enabled, in 'Defaulted' but 'Collecting and Distributing'
passive_fallback = '"Activ:0,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:1,Exp:0"'
# Interface from same LAG with Fallback enabled but not assign to 'listen'
passive_other_intf = '"Activ:0,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:0"'

###############################################################################
#
#                           TEST TOGGLE VARIABLES
#
###############################################################################
disable_admin = ['admin=down']
enable_admin = ['admin=up']

disable_lag = ['lacp=off']
active_lag = ['lacp=active']
passive_lag = ['lacp=passive']

fallback_key = 'lacp-fallback-ab'
other_config_key = 'other_config'
enable_fallback = ['%s:%s="true"' % (other_config_key, fallback_key)]
disable_fallback = ['%s:%s="false"' % (other_config_key, fallback_key)]


@pytest.fixture(scope='module')
def main_setup(request, topology):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    for port in port_labels_1g:
        sw_1g_intf.append(sw1.ports[port])


@pytest.fixture()
def setup(request, topology):
    """Simulate valid pluggable modules in all the modules."""
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    # Create two dynamic LAG with two ports each.
    sw_create_bond(sw1, test_lag, sw_1g_intf, lacp_mode='active')
    sw_create_bond(sw2, test_lag, sw_1g_intf, lacp_mode='active')

    set_port_parameter(sw1, test_lag, ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, test_lag, ['other_config:lacp-time=fast'])

    # Enable both the interfaces.
    for intf in sw_1g_intf:
        set_intf_parameter(sw1, intf, ['user_config:admin=up',
                                       'other_config:lacp-aggregation-key=1'])
        set_intf_parameter(sw2, intf, ['user_config:admin=up',
                                       'other_config:lacp-aggregation-key=1'])

    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)


##############################################################################
#
#                           FALLBACK DISABLED TESTS
#
##############################################################################
def test_nf_toggle_admin_flag(topology, step, main_setup, setup):
    """Toggle 'admin' flag.

    To disable LAG 1 on both switches, 'admin' flag will be toggled between
    'up' and 'down'.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback disabled, toggle "admin" flag')

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_admin)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, enable_admin)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_admin)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, enable_admin)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)


def test_nf_toggle_lacp_flag_active(topology, step, main_setup, setup):
    """Toggle 'lacp' flag to 'active'.

    To disable LAG 1 on both switches, 'lacp' flag will be toggled between
    '[]' and 'active'.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback disabled, toggle "lacp" flag to active')

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)


def test_nf_toggle_lacp_flag_passive(topology, step, main_setup, setup):
    """Toggle 'lacp' flag to 'passive'.

    To disable LAG 1 on both switches, 'lacp' flag will be toggled between
    '[]' and 'passive'.

    Note: Both switches cannot be in the same state of 'passive' or
    connectivity will be lost.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback disabled, toggle "lacp" flag to passive')

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Setting SW2 LAG to "passive"')
    set_port_parameter(sw2, test_lag, passive_lag)
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, passive_no_fallback)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from SW1 are "active"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, active_ready)
    print('Verify all interface SM from SW2 are "passive"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, passive_ready)

    print('Setting SW2 LAG to "active"')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Setting SW1 LAG to "passive"')
    set_port_parameter(sw1, test_lag, passive_lag)
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, passive_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from SW1 are "passive"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, passive_ready)
    print('Verify all interface SM from SW2 are "active"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, active_ready)

    print('Setting SW1 LAG to "active"')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)


def test_nf_false_flag_toggle_admin_flag(topology, step, main_setup, setup):
    """Toggle 'admin' flag with 'false' flag.

    The source code must handle also the possibility to retrieve from OVSDB the
    'lacp-fallback-ab' flag with 'false' even when by default the flag is not
    present.

    To disable LAG 1 on both switches, 'admin' flag will be toggled between
    'up' and 'down'.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback disabled with false flag, toggle "admin" flag')

    print('Setting "lacp-fallback-ab" flag into OVSDB')
    set_port_parameter(sw1, test_lag, disable_fallback)
    set_port_parameter(sw2, test_lag, disable_fallback)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_admin)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, enable_admin)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    #######################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_admin)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, enable_admin)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])


def test_nf_false_flag_toggle_lacp_active(topology, step, main_setup, setup):
    """Toggle 'lacp' flag to 'active' with 'false' flag.

    The source code must handle also the possibility to retrieve from OVSDB the
    'lacp-fallback-ab' flag with 'false' even when by default the flag is not
    present.

    To disable LAG 1 on both switches, 'lacp' flag will be toggled between
    '[]' and 'active'.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback disabled with false flag, toggle "lacp" flag to '
                 'active')

    print('Setting "lacp-fallback-ab" flag into OVSDB')
    set_port_parameter(sw1, test_lag, disable_fallback)
    set_port_parameter(sw2, test_lag, disable_fallback)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    #######################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, active_no_fallback)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])


def test_nf_false_flag_toggle_lacp_passive(topology, step, main_setup, setup):
    """Toggle 'lacp' flag to 'passive' with 'false' flag.

    The source code must handle also the possibility to retrieve from OVSDB the
    'lacp-fallback-ab' flag with 'false' even when by default the flag is not
    present.

    To disable LAG 1 on both switches, 'lacp' flag will be toggled between
    '[]' and 'passive'.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback disabled with false flag, toggle "lacp" flag to '
                 'passive')

    print('Setting "lacp-fallback-ab" flag into OVSDB')
    set_port_parameter(sw1, test_lag, disable_fallback)
    set_port_parameter(sw2, test_lag, disable_fallback)

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Setting SW2 LAG to "passive"')
    set_port_parameter(sw2, test_lag, passive_lag)
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, passive_no_fallback)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from SW1 are "active"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, active_ready)
    print('Verify all interface SM from SW2 are "passive"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, passive_ready)

    print('Setting SW2 LAG to "active"')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Setting SW1 LAG to "passive"')
    set_port_parameter(sw1, test_lag, passive_lag)
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, passive_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from SW1 are "passive"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, passive_ready)
    print('Verify all interface SM from SW2 are "active"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, active_ready)

    print('Setting SW1 LAG to "active"')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])



##############################################################################
#
#                           FALLBACK ENABLED TESTS
#
##############################################################################
"""FALLBACK TESTS ARE DISABLED.

There's a bug with fallback (>.<)

After you enabled fallback on both switches, LAG 1 from switch 1 will be
disabled and then evaluated and enabled again. After LAG 1 from switch 2 is
disabled, actor_state of switch 1 displays info like there's no fallback
enabled and no interface remains as Collecting and Distributing.
"""

def disabled_test_fb_toggle_admin_flag(topology, step, main_setup, setup):
    """Toggle 'admin' flag.

    To disable LAG 1 on both switches, 'admin' flag will be toggled between
    'up' and 'down'.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback enabled, toggle "admin" flag')

    print('Enabling Fallback on both switches')
    set_port_parameter(sw1, test_lag, enable_fallback)
    set_port_parameter(sw2, test_lag, enable_fallback)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_admin)
    print('Verify that interface 1 is "Collecting, Distributing and '
          'Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[0], active_fallback)
    print('Verify that interface 2 is only "Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[1:], active_other_intf)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, enable_admin)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw1, test_lag, disable_admin)
    print('Verify that interface 1 is "Collecting, Distributing and '
          'Defaulted" on sw2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[0], active_fallback)
    print('Verify that interface 2 is only "Defaulted" on sw2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[1:], active_other_intf)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw1, test_lag, enable_admin)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])


def disabled_test_fb_toggle_lacp_flag_active(topology, step, main_setup, setup):

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback enabled, toggle "lacp" flag to active')

    print('Enabling Fallback on both switches')
    set_port_parameter(sw1, test_lag, enable_fallback)
    set_port_parameter(sw2, test_lag, enable_fallback)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)
    print('Verify that interface 1 is "Collecting, Distributing and '
          'Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[0], active_fallback)
    print('Verify that interface 2 is only "Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf[1:], active_other_intf)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)
    print('Verify that interface 1 is "Collecting, Distributing and '
          'Defaulted" on sw2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[0], active_fallback)
    print('Verify that interface 2 is only "Defaulted" on sw2')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf[1:], active_other_intf)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, as_sm_state_ready)

    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])


def disabled_test_fb_toggle_lacp_flag_passive(topology, step, main_setup, setup):
    """Toggle 'lacp' flag to 'passive'.

    To disable LAG 1 on both switches, 'lacp' flag will be toggled between
    '[]' and 'passive'.

    Note: Both switches cannot be in the same state of 'passive' or
    connectivity will be lost.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Fallback enabled, toggle "lacp" flag to passive')

    print('Enabling Fallback on both switches')
    set_port_parameter(sw1, test_lag, enable_fallback)
    set_port_parameter(sw2, test_lag, enable_fallback)

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Setting SW2 LAG to "passive"')
    set_port_parameter(sw2, test_lag, passive_lag)
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, passive_fallback)

    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from SW1 are "active"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, active_ready)
    print('Verify all interface SM from SW2 are "passive"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, passive_ready)

    print('Setting SW2 LAG to "active"')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Setting SW1 LAG to "passive"')
    set_port_parameter(sw1, test_lag, passive_lag)
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)
    print('Verify that all SW1 SMs are in "Defaulted and Expired"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, passive_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interface SM from SW1 are "passive"')
    sw_wait_until_all_sm_ready([sw1], sw_1g_intf, passive_ready)
    print('Verify all interface SM from SW2 are "active"')
    sw_wait_until_all_sm_ready([sw2], sw_1g_intf, active_ready)

    print('Setting SW1 LAG to "active"')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify all interface SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)

    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])