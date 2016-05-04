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

##########################################################################
# Name:        test_lacpd_ct_vtysh_fallback.py
#
# Objective:   Verify functionality for lacp fallback mode and timeout CLI
#              commands
#
# Topology:    1 switch (DUT running OpenSwitch)
#
##########################################################################
import topology_lib_vtysh
from lib_test import (
    verify_port_fallback_mode,
    verify_port_fallback_timeout
)


TOPOLOGY = """
#
#
# +-------+
# |       |
# |  sw1  |
# |       |
# +-------+
#

# Nodes
[type=openswitch name="Switch 1"] sw1

# Links
"""


def test_lacp_fallback_vtysh(topology, step):
    sw1 = topology.get('sw1')

    assert sw1 is not None
    lag_id = '1'
    lag_name = 'lag1'
    mode_empty_state = 'ovs-vsctl: no key lacp_fallback_mode in Port ' +\
                       'record ' + lag_name + ' column other_config'
    timeout_empty_state = 'ovs-vsctl: no key lacp_fallback_timeout in ' +\
                          'Port record ' + lag_name + ' column other_config'

    step("Configure LAG in switch")
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_mode_active()

    ###########################################################################
    #                         LACP FALLBACK MODE                              #
    ###########################################################################

    step('Verify initial fallback mode is empty')
    verify_port_fallback_mode(sw1, lag_name, mode_empty_state,
                              'lacp_fallback_mode expected to be EMPTY')

    step('Configure lacp_fallback_mode as all_active')
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_fallback_mode_all_active()
    step('Verify fallback mode is all_active')
    verify_port_fallback_mode(sw1, lag_name, 'all_active',
                              'lacp_fallback_mode expected to be ALL_ACTIVE')

    step('Configure lacp_fallback_mode as priority')
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_fallback_mode_priority()
    step('Verify fallback mode is empty')
    verify_port_fallback_mode(sw1, lag_name, mode_empty_state,
                              'lacp_fallback_mode expected to be EMPTY')

    step('Configure lacp_fallback_mode as all_active')
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_fallback_mode_all_active()
    step('Verify fallback mode is all_active')
    verify_port_fallback_mode(sw1, lag_name, 'all_active',
                              'lacp_fallback_mode expected to be ALL_ACTIVE')

    step('Configure lacp_fallback_mode as no all_active')
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_lacp_fallback_mode_all_active()
    step('Verify fallback mode is empty')
    verify_port_fallback_mode(sw1, lag_name, mode_empty_state,
                              'lacp_fallback_mode expected to be EMPTY')

    ###########################################################################
    #                         LACP FALLBACK TIMEOUT                           #
    ###########################################################################

    step('Verify initial fallback_timeout is empty')
    verify_port_fallback_timeout(sw1, lag_name, timeout_empty_state,
                                 'lacp_fallback_timeout expected to be EMPTY')

    step('Configure lacp_fallback_timeout to 900')
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_fallback_timeout(900)
    step('Verify fallback_timeout is 900')
    verify_port_fallback_timeout(sw1, lag_name, '900',
                                 'lacp_fallback_timeout expected to be 900')

    step('Configure lacp_fallback_timeout to 1')
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_fallback_timeout(1)
    step('Verify fallback_timeout is 1')
    verify_port_fallback_timeout(sw1, lag_name, '1',
                                 'lacp_fallback_timeout expected to be 1')

    step('Configure no lacp_fallback_timeout with invalid value 2')
    success = False
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        try:
            ctx.no_lacp_fallback_timeout(2)
        except topology_lib_vtysh.exceptions.TcamResourcesException:
            success = True
    assert success, ('no lacp_fallback_timeout(2) expected to raise ' +
                     'exception ' +
                     str(topology_lib_vtysh.exceptions.TcamResourcesException))
    step('Verify fallback_timeout is still 1')
    verify_port_fallback_timeout(sw1, lag_name, '1',
                                 'lacp_fallback_timeout expected to be 1')

    step('Configure no lacp_fallback_timeout with invalid value 901')
    success = False
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        try:
            ctx.no_lacp_fallback_timeout(901)
        except topology_lib_vtysh.exceptions.UnknownCommandException:
            success = True
    assert success, ('no lacp_fallback_timeout(901) expected to raise ' +
                     'exception ' +
                     str(topology_lib_vtysh.exceptions.UnknownCommandException)
                     )
    step('Verify fallback_timeout is still 1')
    verify_port_fallback_timeout(sw1, lag_name, '1',
                                 'lacp_fallback_timeout expected to be 1')

    step('Configure no lacp_fallback_timeout with invalid value 0')
    success = False
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        try:
            ctx.no_lacp_fallback_timeout(0)
        except topology_lib_vtysh.exceptions.UnknownCommandException:
            success = True
    assert success, ('no lacp_fallback_timeout(0) expected to raise ' +
                     'exception ' +
                     str(topology_lib_vtysh.exceptions.UnknownCommandException)
                     )
    step('Verify fallback_timeout is still 1')
    verify_port_fallback_timeout(sw1, lag_name, '1',
                                 'lacp_fallback_timeout expected to be 1')

    step('Configure lacp_fallback_timeout to 0')
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_lacp_fallback_timeout(1)
    step('Verify fallback_timeout is empty')
    verify_port_fallback_timeout(sw1, lag_name, timeout_empty_state,
                                 'lacp_fallback_timeout expected to be EMPTY')

    step('Configure lacp_fallback_timeout to invalid value 901')
    success = False
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        try:
            ctx.lacp_fallback_timeout(901)
        except topology_lib_vtysh.exceptions.UnknownCommandException:
            success = True
    assert success, ('lacp_fallback_timeout(901) expected to raise ' +
                     'exception ' +
                     str(topology_lib_vtysh.exceptions.UnknownCommandException)
                     )
    step('Verify fallback_timeout is empty')
    verify_port_fallback_timeout(sw1, lag_name, timeout_empty_state,
                                 'lacp_fallback_timeout expected to be EMPTY')

    step('Configure lacp_fallback_timeout to invalid value 0')
    success = False
    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        try:
            ctx.lacp_fallback_timeout(0)
        except topology_lib_vtysh.exceptions.UnknownCommandException:
            success = True
    assert success, ('lacp_fallback_timeout(0) expected to raise ' +
                     'exception ' +
                     str(topology_lib_vtysh.exceptions.UnknownCommandException)
                     )
    step('Verify fallback_timeout is empty')
    verify_port_fallback_timeout(sw1, lag_name, timeout_empty_state,
                                 'lacp_fallback_timeout expected to be EMPTY')
