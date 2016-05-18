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

import pytest
from time import sleep
from ipdb import set_trace

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
    sw_wait_until_one_sm_ready,
    sw_wait_until_ready,
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
[type=openswitch name="switch 1"] sw1
[type=openswitch name="switch 2"] sw2

# Links
# 1 Gig ports
sw1:1 -- sw2:1
sw1:2 -- sw2:2
sw1:3 -- sw2:3
sw1:4 -- sw2:4
"""

# Interfaces from 1-2 are 1G ports.
sw_1g_intf_start = 1
sw_1g_intf_end = 3
n_1g_links = 2
port_labels_1g = ['1', '2', '3', '4']
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
    """Common tests configuration.

    This configuration will be applied for all Fallback test cases, enabled or
    not, and after each test case the configuration must remains the same to
    keep the atomicity of each test.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    for port in port_labels_1g:
        sw_1g_intf.append(sw1.ports[port])

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

    sw_wait_until_ready([sw1, sw2], sw_1g_intf)

    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], sw_1g_intf, active_ready)


def test_fallback_priority_mode(topology, step, main_setup):

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on both switches')
    set_port_parameter(sw1, test_lag, enable_fallback)
    set_port_parameter(sw2, test_lag, enable_fallback)

    set_trace()
