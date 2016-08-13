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
# Name:        test_ft_lacp_fallback_vtysh.py
#
# Objective:   Verify lacp fallback cli commands set fallback mode and
#              timeout properly.
#
# Topology:    2 switches (DUT running Halon) connected by 2 interfaces
#
##########################################################################

from pytest import mark
from time import sleep
from lacp_lib import (
    associate_interface_to_lag,
    config_lacp_rate,
    create_lag,
    LOCAL_STATE,
    REMOTE_STATE,
    turn_on_interface,
    verify_lag_config,
    verify_state_sync_lag,
    verify_turn_on_interfaces
)

TOPOLOGY = """
#   +-----+------+
#   |            |
#   |    sw1     |
#   |   1   2    |
#   +---+---+----+
#       |   |
#       |   |     LAG 1
#       |   |
#   +---+---+----+
#   |   1   2    |
#   |    sw2     |
#   |            |
#   +-----+------+


# Nodes
[type=openswitch name="OpenSwitch 1"] sw1
[type=openswitch name="OpenSwitch 2"] sw2

# Links
sw1:1 -- sw2:1
sw1:2 -- sw2:2
"""


def test_lacp_fallback_vtysh(topology, step):
    """
    Case 1:
        Verify cli commands lacp fallback and lacp fallback timeout set values
        properly, using cli commands show lacp aggregates, show running-config
        and show running-config interface.
    """
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    sw1_lag_id = '10'
    sw2_lag_id = '20'
    vlan_identifier = '8'

    assert sw1 is not None
    assert sw2 is not None

    ports_sw1 = list()
    ports_sw2 = list()
    port_labels = ['1', '2']

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

    step("Create LAG in both switches")
    create_lag(sw1, sw1_lag_id, 'active')
    create_lag(sw2, sw2_lag_id, 'active')
    config_lacp_rate(sw1, sw1_lag_id, True)
    config_lacp_rate(sw2, sw2_lag_id, True)

    step("Associate interfaces [1, 2] to LAG in both switches")
    for port in ports_sw1:
        associate_interface_to_lag(sw1, port, sw1_lag_id)
    for port in ports_sw2:
        associate_interface_to_lag(sw2, port, sw2_lag_id)

    step("Verify LAG configuration")
    verify_lag_config(sw1, sw1_lag_id, ports_sw1[0:2],
                      mode='active', heartbeat_rate='fast')
    verify_lag_config(sw2, sw2_lag_id, ports_sw2[0:2],
                      mode='active', heartbeat_rate='fast')

    step("Verify if LAG is synchronized")
    verify_state_sync_lag(sw1, ports_sw1, LOCAL_STATE, 'active')
    verify_state_sync_lag(sw1, ports_sw1, REMOTE_STATE, 'active')
    verify_state_sync_lag(sw2, ports_sw2, LOCAL_STATE, 'active')
    verify_state_sync_lag(sw2, ports_sw2, REMOTE_STATE, 'active')

    ###########################################################################
    #                     Enabling LAG Fallback
    ###########################################################################
    step('Enabling Fallback mode on LAG %s on Switch 1' % sw1_lag_id)
    with sw1.libs.vtysh.ConfigInterfaceLag(sw1_lag_id) as ctx:
        ctx.lacp_fallback()

    ###########################################################################
    #               Verify fallback is enabled and mode is priority
    ###########################################################################
    step('Verify show lacp aggregates output')
    lacp_map = sw1.libs.vtysh.show_lacp_aggregates()
    assert lacp_map['lag' + sw1_lag_id]['fallback'] and \
        lacp_map['lag' + sw1_lag_id]['fallback_mode'] == 'priority',\
        'Fallback should be enable and in priority mode.'

    step('Verify show running-config ouput')
    lacp_map = sw1.libs.vtysh.show_running_config()
    assert lacp_map['interface']['lag'][sw1_lag_id]['lacp_fallback'],\
        'Fallback should be enable.'

    step('Verify show running-config interface output')
    lacp_map = sw1.libs.vtysh.show_running_config_interface('lag10')
    assert lacp_map['interface']['lag'][sw1_lag_id]['lacp_fallback'],\
        'Fallback should be enable.'

    ###########################################################################
    #                     Disabling LAG Fallback
    ###########################################################################
    step('Enabling Fallback mode on LAG %s on Switch 1' % sw1_lag_id)
    with sw1.libs.vtysh.ConfigInterfaceLag(sw1_lag_id) as ctx:
        ctx.no_lacp_fallback()

    ###########################################################################
    #               Verify fallback is disabled
    ###########################################################################
    step('Verify show lacp aggregates output')
    lacp_map = sw1.libs.vtysh.show_lacp_aggregates()
    assert lacp_map['lag' + sw1_lag_id]['fallback'] == False,\
        'Fallback should be disabled.'

    step('Verify show running-config ouput')
    lacp_map = sw1.libs.vtysh.show_running_config()
    assert 'lacp_fallback' not in lacp_map['interface']['lag'][sw1_lag_id],\
        'Fallback should be disabled.'

    step('Verify show running-config interface output')
    lacp_map = sw1.libs.vtysh.show_running_config_interface('lag10')
    assert 'lacp_fallback' not in lacp_map['interface']['lag'][sw1_lag_id],\
        'Fallback should be disabled.'

    ###########################################################################
    #                    Setting Fallback timeout
    ###########################################################################
    step('Setting fallback timeout to 60 on LAG %s on Switch 1' % sw1_lag_id)
    with sw1.libs.vtysh.ConfigInterfaceLag(sw1_lag_id) as ctx:
        ctx.lacp_fallback_timeout(60)

    ###########################################################################
    #               Verify fallback timeout is set to 60
    ###########################################################################
    step('Verify show lacp aggregates output')
    lacp_map = sw1.libs.vtysh.show_lacp_aggregates()
    assert lacp_map['lag' + sw1_lag_id]['fallback_timeout'] == '60' ,\
        'Fallback timeout should be 60'

    step('Verify show running-config ouput')
    output = sw1.libs.vtysh.show_running_config()
    lacp_map = output['interface']['lag'][sw1_lag_id]
    assert lacp_map['lacp_fallback_timeout'] == '60' ,\
        'Fallback timeout should be 60'

    step('Verify show running-config interface output')
    output = sw1.libs.vtysh.show_running_config_interface('lag10')
    lacp_map = output['interface']['lag'][sw1_lag_id]
    assert lacp_map['lacp_fallback_timeout'] == '60' ,\
        'Fallback timeout should be 60'

    ###########################################################################
    #                    Setting no fallback timeout
    ###########################################################################
    step('Setting fallback timeout to 60 on LAG %s on Switch 1' % sw1_lag_id)
    with sw1.libs.vtysh.ConfigInterfaceLag(sw1_lag_id) as ctx:
        ctx.no_lacp_fallback_timeout(60)

    ###########################################################################
    #               Verify fallback timeout is not set
    ###########################################################################
    step('Verify show lacp aggregates output')
    lacp_map = sw1.libs.vtysh.show_lacp_aggregates()
    assert lacp_map['lag' + sw1_lag_id]['fallback_timeout'] == '0' ,\
        'Fallback timeout should be 0'

    step('Verify show running-config ouput')
    output = sw1.libs.vtysh.show_running_config()
    lacp_map = output['interface']['lag'][sw1_lag_id]
    assert 'lacp_fallback_timeout' not in lacp_map ,\
        'Fallback timeout should not be set'

    step('Verify show running-config interface output')
    output = sw1.libs.vtysh.show_running_config_interface('lag10')
    lacp_map = output['interface']['lag'][sw1_lag_id]
    assert 'lacp_fallback_timeout' not in lacp_map ,\
        'Fallback timeout should not be set'
