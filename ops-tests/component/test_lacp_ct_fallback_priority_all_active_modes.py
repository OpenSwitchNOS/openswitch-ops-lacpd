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
from lib_test import (
    clear_port_parameter,
    print_header,
    remove_intf_parameter,
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
    verify_intf_status,
    verify_interfaces_mac_uniqueness
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
sw1:1 -- sw2:1
sw1:2 -- sw2:2
sw1:3 -- sw2:3
sw1:4 -- sw2:4
"""

sw_intf_start = 0
sw_intf_end = 4
intf_labels = ['1', '2', '3', '4']
test_lag = 'lag1'

###############################################################################
#
#                       ACTOR STATE STATE MACHINES VARIABLES
#
###############################################################################
# Everything is working and 'Collecting and Distributing'
active_ready = '"Activ:1,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:0,Exp:0"'
# No fallback enabled, interface is 'dead'
active_no_fallback = '"Activ:1,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:0"'
# Fallback enabled, in 'Defaulted' but 'Collecting and Distributing'
active_fallback = '"Activ:1,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:1,Exp:0"'
# Interface from same LAG with Fallback enabled but not assign to 'listen'
active_other_intf = '"Activ:1,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:0"'

passive_ready = '"Activ:0,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:0,Exp:0"'
# No fallback enabled, interface is 'dead'
passive_no_fallback = '"Activ:0,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:0"'
# Fallback enabled, in 'Defaulted' but 'Collecting and Distributing'
passive_fallback = '"Activ:0,TmOut:\d,Aggr:1,Sync:1,Col:1,Dist:1,Def:1,Exp:0"'
# Interface from same LAG with Fallback enabled but not assign to 'listen'
passive_other_intf = '"Activ:0,TmOut:\d,Aggr:1,Sync:0,Col:0,Dist:0,Def:1,Exp:0"'

###############################################################################
#
#                           TEST TOGGLE VARIABLES
#
###############################################################################
disable_lag = ['lacp=off']
active_lag = ['lacp=active']
passive_lag = ['lacp=passive']

fallback_key = 'lacp-fallback-ab'
other_config_key = 'other_config'
port_priority_key = 'lacp-port-priority'
fallback_mode_key = 'lacp_fallback_mode'
fallback_timeout_key = 'lacp_fallback_timeout'
priority_mode_key = 'priority'
all_active_mode_key = 'all_active'
fallback_timeout_time = 20

enable_fallback = ['%s:%s="true"' % (other_config_key, fallback_key)]
disable_fallback = ['%s:%s="false"' % (other_config_key, fallback_key)]

enable_fallback_priority = ['%s:%s=%s' %
                            (other_config_key,
                             fallback_mode_key,
                             priority_mode_key)]
enable_fallback_all_active = ['%s:%s=%s' %
                              (other_config_key,
                               fallback_mode_key,
                               all_active_mode_key)]
lacp_intf_priority = '%s:%s' % (other_config_key, port_priority_key)
enable_fallback_timeout = ['%s:%s=%d' %
                           (other_config_key,
                            fallback_timeout_key,
                            fallback_timeout_time)]
enable_fallback_timeout_zero = ['%s:%s=%d' %
                                (other_config_key,
                                 fallback_timeout_key,
                                 0)]

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

    # Create two dynamic LAG with two ports each.
    sw_create_bond(sw1, test_lag, intf_labels, lacp_mode='active')
    sw_create_bond(sw2, test_lag, intf_labels, lacp_mode='active')

    set_port_parameter(sw1, test_lag, ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, test_lag, ['other_config:lacp-time=fast'])

    # Enable both the interfaces.
    for intf in intf_labels:
        set_intf_parameter(sw1, intf, ['user_config:admin=up',
                                       'other_config:lacp-aggregation-key=1'])
        set_intf_parameter(sw2, intf, ['user_config:admin=up',
                                       'other_config:lacp-aggregation-key=1'])

    mac_addr_sw1 = sw1.libs.vtysh.show_interface(1)['mac_address']
    mac_addr_sw2 = sw2.libs.vtysh.show_interface(1)['mac_address']
    assert mac_addr_sw1 != mac_addr_sw2,\
        'Mac address of interfaces in sw1 is equal to mac address of ' +\
        'interfaces in sw2. This is a test framework problem. Dynamic ' +\
        'LAGs cannot work properly under this condition. Refer to Taiga ' +\
        'issue #1251.'

    sw_wait_until_ready([sw1, sw2], intf_labels)

    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


##############################################################################
#
#                           FALLBACK PRIORITY TESTS
#
##############################################################################
@pytest.mark.skipif(True, reason="Skipping because instable enviroment")
def test_fallback_priority(topology, step, main_setup):
    """Enable Fallback mode priority

    The interface with higher priority must be in Defaulted and in
    'Collecting and Distributing' when fallback is active and the fallback
    mode is 'priority'
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Enable Fallback mode priority')

    ##########################################################################
    # Setting port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[0]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=1'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=2'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=4'])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback priority mode' flag
    ##########################################################################
    print('Enabling Fallback priority mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_priority)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    ##########################################################################
    # Verify fallback priority mode functionality
    ##########################################################################
    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    print('Setting interface 1 to a lower lacp port priority on sw1')
    print('interface with higher priority is 2 now')
    set_intf_parameter(sw1, higher_prio_intf, [lacp_intf_priority + '=5'])
    higher_prio_intf = intf_labels[1]
    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


@pytest.mark.skipif(True, reason="Skipping because all active is not ready")
def test_fallback_mode_priority_to_all_active(topology, step, main_setup):
    """Change fallback mode priority to all active mode

    The interface with higher priority must be in Defaulted and in
    'Collecting and Distributing' when fallback is active and the fallback
    mode is 'priority'. When the mode is change to all active, all interfaces
    must be in Defaulted and in 'Collecting and Distributing'
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Change fallback mode priority to the mode all active')

    ##########################################################################
    # Setting port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[3]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=4'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=2'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=1'])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback priority mode' flag
    ##########################################################################
    print('Enabling Fallback priority mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_priority)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    ##########################################################################
    # Verify fallback priority mode can change to all_active mode
    ##########################################################################
    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    print('Setting fallback mode to all active on sw1')
    set_port_parameter(sw1, test_lag, enable_fallback_all_active)

    print('Verify that all interfaces of LAG 1 are in '
          '"Collecting, Distributing and Defaulted" on sw1')

    sw_wait_until_all_sm_ready([sw1],
                               intf_labels,
                               active_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


# @pytest.mark.skipif(True, reason="Skipping because instable enviroment")
def test_fallback_mode_priority_with_timeout(topology, step, main_setup):
    """Enable Fallback mode priority with timeout

    The interface with higher priority must be in Defaulted and in
    'Collecting and Distributing' when fallback is active and the fallback
    mode is 'priority'. When the fallback timeout is set to 20 seconds, the
    interfaces should remain in fallback, after the 20 seconds all interfaces
    must not be in fallback anymore
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Enable Fallback mode priority with timeout')

    ##########################################################################
    # Setting port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[2]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=4'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=1'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=2'])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Set fallback timeout to 20 seconds
    ##########################################################################
    print('Enabling Fallback timeout 20 seconds on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_timeout)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback priority mode' flag
    ##########################################################################
    print('Enabling Fallback priority mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_priority)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    from pytest import set_trace
    set_trace()
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    print('Wait 10 seconds, fallback should be still active')
    sleep(10)

    ##########################################################################
    # Verify fallback priority with timeout
    ##########################################################################
    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    print('Wait 15 seconds, fallback should not be active')
    sleep(15)

    print('Verify that interfaces are "Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], intf_labels, active_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp_fallback_timeout" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_timeout_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


@pytest.mark.skipif(True, reason="Skipping because instable enviroment")
def test_fallback_mode_priority_with_timeout_zero(topology, step, main_setup):
    """Enable Fallback mode priority with timeout zero

    The interface with higher priority must be in Defaulted and in
    'Collecting and Distributing' when fallback is active and the fallback
    mode is 'priority'. When the fallback timeout is set to 0, the interface
    with higher priority should be in fallback all the time
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Enable Fallback mode priority with timeout zero')

    ##########################################################################
    # Setting port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[1]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=1'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=4'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=2'])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Set fallback timeout to 0 seconds
    ##########################################################################
    print('Enabling Fallback timeout zero on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_timeout_zero)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback priority mode' flag
    ##########################################################################
    print('Enabling Fallback priority mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_priority)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    print('Wait 10 seconds, fallback should be still active')
    sleep(10)

    ##########################################################################
    # Verify fallback priority with timeout zero
    ##########################################################################
    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp_fallback_timeout" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_timeout_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


@pytest.mark.skipif(True, reason="Skipping because instable enviroment")
def test_fallback_priority_toggle_lacp_mode(topology, step, main_setup):
    """Enable Fallback mode priority toggle lacp mode

    If in switch 1 and 2, the lacp mode is set to 'off' and then to 'on' the
    interface with higher priority must be in Defaulted and in'Collecting and
    Distributing' when fallback is active and the fallback mode is 'priority'.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Enable Fallback mode priority toggle lacp mode')

    ##########################################################################
    # Setting port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[0]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=1'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=2'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=4'])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Add 'fallback priority mode' flag
    ##########################################################################
    print('Enabling Fallback priority mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_priority)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw1 and sw2
    ##########################################################################
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    ##########################################################################
    # Verify fallback priority mode functionality
    ##########################################################################
    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    ##########################################################################
    # LAG 1 disabled on sw1
    ##########################################################################
    print('Shutting down LAG1 on sw1')
    set_port_parameter(sw1, test_lag, disable_lag)

    ##########################################################################
    # Setting different port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[3]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=4'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=2'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=1'])
    sleep(5)
    ##########################################################################
    # Verify fallback priority mode functionality when changing lacp mode
    ##########################################################################
    print('Enabling LAG1 on sw1')
    set_port_parameter(sw1, test_lag, active_lag)
    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


##############################################################################
#
#                           FALLBACK ALL ACTIVE TESTS SKIPPED UNTIL
#                           THE MODE IS COMPLETE
#
##############################################################################
@pytest.mark.skipif(True, reason="Skipping because all active is not ready")
def test_fallback_mode_all_active(topology, step, main_setup):
    """Enable Fallback mode all active

    When the mode is all active all interfaces in the LAG must be in
    'Collecting and Distributing' and in Defaulted, changes in lacp
    port priority should not affect this.
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Enable Fallback mode all active')

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)

    ##########################################################################
    # Add 'fallback all active mode' flag
    ##########################################################################
    print('Enabling Fallback all active mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_all_active)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    ##########################################################################
    # Verify fallback all active mode
    ##########################################################################
    print('Verify that all interfaces are Collecting, Distributing and '
          'Defaulted on sw1')
    sw_wait_until_all_sm_ready([sw1], intf_labels, active_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


@pytest.mark.skipif(True, reason="Skipping because all active is not ready")
def test_fallback_mode_all_active_to_priority(topology, step, main_setup):
    """Change fallback mode all active to priority mode

    When the fallback mode is all active, all interfaces in the LAG must be
    'Collecting and Distributing', when the fallaback mode is changed to
    priority the interface with higher priority must be in Defaulted and in
    'Collecting and Distributing'. When the mode is changed to all active,
    all interfaces must be in Defaulted and in 'Collecting and Distributing'
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Change fallback mode all active to priority mode')

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)

    ##########################################################################
    # Add 'fallback priority mode' flag
    ##########################################################################
    print('Enabling Fallback all active mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_all_active)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    ##########################################################################
    # Verify fallback all active mode can change to priority mode
    ##########################################################################
    print('Verify that all interfaces of LAG 1 are in '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1],
                               intf_labels,
                               active_fallback)

    ##########################################################################
    # Setting port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[0]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=1'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=2'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=4'])

    print('Enabling Fallback priority mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_priority)

    print('Verify that interface with higher priority is '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_one_sm_ready([sw1],
                               [higher_prio_intf],
                               active_fallback)

    print('Verify that other interfaces are "Defaulted" on sw1')
    tmp = list(intf_labels)
    tmp.remove(higher_prio_intf)
    sw_wait_until_all_sm_ready([sw1], tmp, active_other_intf)

    print('Setting fallback mode to all active on sw1')
    set_port_parameter(sw1, test_lag, enable_fallback_all_active)

    print('Verify that all interfaces of LAG 1 are in '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1],
                               intf_labels,
                               active_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


@pytest.mark.skipif(True, reason="Skipping because all active is not ready")
def test_fallback_mode_all_active_with_timeout(topology, step, main_setup):
    """Enable Fallback mode all active with timeout

    When the fallback mode is all active and fallback is active, all
    interfaces in the LAG must be 'Collecting, Distributing and Defaulted'.
    When the fallback timeout is set to 20 seconds, the interfaces should
    remain in fallback, after the 20 seconds all interfaces must not be in
    fallback anymore
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Enable Fallback mode all active with timeout')

    ##########################################################################
    # Setting port priorities
    ##########################################################################
    print('Setting interface lacp port priorities on sw1')
    higher_prio_intf = intf_labels[2]
    set_intf_parameter(sw1, intf_labels[0], [lacp_intf_priority + '=3'])
    set_intf_parameter(sw1, intf_labels[1], [lacp_intf_priority + '=4'])
    set_intf_parameter(sw1, intf_labels[2], [lacp_intf_priority + '=1'])
    set_intf_parameter(sw1, intf_labels[3], [lacp_intf_priority + '=2'])

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)

    ##########################################################################
    # Set fallback timeout to 20 seconds
    ##########################################################################
    print('Enabling Fallback timeout 20 seconds on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_timeout)

    ##########################################################################
    # Add 'fallback all active mode' flag
    ##########################################################################
    print('Enabling Fallback all active mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_all_active)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    print('Wait 10 seconds, fallback should be still active')
    sleep(10)

    ##########################################################################
    # Verify fallback all active with timeout
    ##########################################################################
    print('Verify that all interfaces of LAG 1 are in '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], intf_labels, active_fallback)

    print('Wait 15 seconds, fallback should not be active')
    sleep(15)

    print('Verify that interfaces are "Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], intf_labels, active_no_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp_fallback_timeout" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_timeout_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)


@pytest.mark.skipif(True, reason="Skipping because all active is not ready")
def test_fallback_mode_all_active_with_timeout_zero(topology, step, main_setup):
    """Enable Fallback mode all active with timeout zero

    When the fallback mode is all active and fallback is active, all
    interfaces in LAG must be 'Collecting, Distributing and Defaulted'.
    When the fallback timeout is set to 0, the interfaces should be in
    fallback all the time
    """

    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print_header('Enable Fallback mode all active with timeout zero')

    ##########################################################################
    # Add 'fallback' flag
    ##########################################################################
    print('Enabling Fallback on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback)

    ##########################################################################
    # Set fallback timeout to 0 seconds
    ##########################################################################
    print('Enabling Fallback timeout zero on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_timeout_zero)

    ##########################################################################
    # Add 'fallback all active mode' flag
    ##########################################################################
    print('Enabling Fallback all active mode on switch 1')
    set_port_parameter(sw1, test_lag, enable_fallback_priority)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # LAG 1 disabled on sw2
    ##########################################################################
    print('Shutting down LAG1 on sw2')
    set_port_parameter(sw2, test_lag, disable_lag)

    print('Wait 10 seconds, fallback should be still active')
    sleep(10)

    ##########################################################################
    # Verify fallback priority with timeout zero
    ##########################################################################
    print('Verify that all interfaces of LAG 1 are in '
          '"Collecting, Distributing and Defaulted" on sw1')
    sw_wait_until_all_sm_ready([sw1], intf_labels, active_fallback)

    print('Enabling LAG1 on sw2')
    set_port_parameter(sw2, test_lag, active_lag)
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)

    ##########################################################################
    # Remove added flags
    ##########################################################################
    print('Clearing "lacp-fallback-ab" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key, [fallback_key])
    remove_port_parameter(sw2, test_lag, other_config_key, [fallback_key])
    print('Clearing "lacp_fallback_mode" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_mode_key])
    print('Clearing "lacp_fallback_timeout" flag from OVSDB')
    remove_port_parameter(sw1, test_lag, other_config_key,
                          [fallback_timeout_key])
    print('Clearing "lacp-port-priority" flag from OVSDB')
    for intf in intf_labels:
        remove_intf_parameter(sw1, intf, other_config_key,
                              [port_priority_key])
    print('Verify all interfaces SM from both switches are working')
    sw_wait_until_all_sm_ready([sw1, sw2], intf_labels, active_ready)
