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
# Name:        StaticLagConvertToDynamic.py
#
# Description: Tests that a previously configured static Link Aggregation can
#              be converted to a dynamic one
#
# Author:      Jose Hernandez
#
# Topology:  |Host| ----- |Switch| ---------------------- |Switch| ----- |Host|
#                                   (Static LAG - 2 links)
#
# Success Criteria:  PASS -> LAGs is converted from static to dynamic
#
#                    FAILED -> LAG cannot be converted from static to dynamic
#
###############################################################################

from time import sleep
from lacp_lib import create_lag
from lacp_lib import turn_on_interface
from lacp_lib import validate_turn_on_interfaces
from lacp_lib import associate_interface_to_lag
from lacp_lib import verify_lag_config
from lacp_lib import create_vlan
from lacp_lib import verify_vlan_full_state
from lacp_lib import verify_lag_static_empty_values
from lacp_lib import verify_lag_state_cross_interface
from lacp_lib import check_connectivity_between_hosts
from lacp_lib import create_lag_passive
from lacp_lib import create_lag_active

TOPOLOGY = """
#            +-----------------+
#            |                 |
#            |      Host 1     |
#            |                 |
#            +-----------------+
#                     |
#                     |
#     +-------------------------------+
#     |                               |
#     |                               |
#     |            Switch 1           |
#     |                               |
#     +-------------------------------+
#          |         |        |
#          |         |        |
#          |         |        |
#     +-------------------------------+
#     |                               |
#     |                               |
#     |            Switch 2           |
#     |                               |
#     +-------------------------------+
#                     |
#                     |
#            +-----------------+
#            |                 |
#            |     Host 2      |
#            |                 |
#            +-----------------+

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2
[type=host name="Host 1"] hs1
[type=host name="Host 2"] hs2

# Links

sw1:1 -- hs1:1
sw2:1 -- hs2:1
sw1:2 -- sw2:2
sw1:3 -- sw2:3
sw1:4 -- sw2:4
"""

# Global variables
SW_LBL_PORTS = ['1', '2', '3', '4']
LAG_ID = '1'
LAG_VLAN = 900
NETWORK = '10.90.0.'
NETMASK = '24'
NUMBER_PINGS = 5


def verify_lacp_state(
    sw1,
    sw2,
    sw1_lacp_mode='off',
    sw2_lacp_mode='active',
):
    sw1_lacp_config = sw1.libs.vtysh.show_lacp_configuration()
    sw2_lacp_config = sw2.libs.vtysh.show_lacp_configuration()
    print('Verify LACP state on LAG members')
    for port in SW_LBL_PORTS[1:]:
        sw1_lacp_state = sw1.libs.vtysh.show_lacp_interface(port)
        sw2_lacp_state = sw2.libs.vtysh.show_lacp_interface(port)
        if sw1_lacp_mode == 'off':
            verify_lag_static_empty_values(sw1_lacp_state)
            verify_lag_static_empty_values(sw2_lacp_state)
        else:
            verify_lag_state_cross_interface(
                sw1_lacp_state,
                sw2_lacp_state,
                sw1_lacp_config,
                sw2_lacp_config,
                sw1_int_lacp_mode=sw1_lacp_mode,
                sw2_int_lacp_mode=sw2_lacp_mode
            )


def enable_switches_interfaces(sw_list, step):
    step('STEP: Enable switches interfaces')
    for sw in sw_list:
        for port in SW_LBL_PORTS:
            turn_on_interface(sw, port)
#     print('Waiting 15 seconds to ensure interfaces are turned on')
#     sleep(15)
#     for sw in sw_list:
#         validate_turn_on_interfaces(sw, SW_LBL_PORTS)


def configure_lags(sw_list, sw_real_ports, step):
    step('STEP: Create LAGs')
    for sw in sw_list:
        create_lag(sw, LAG_ID, 'off')
        # Set LACP rate to fast
        with sw.libs.vtysh.ConfigInterfaceLag(LAG_ID) as ctx:
            ctx.lacp_rate_fast()
        for port in sw_real_ports[sw][1:]:
            associate_interface_to_lag(sw, port, LAG_ID)
        verify_lag_config(
            sw,
            LAG_ID,
            sw_real_ports[sw][1:],
            heartbeat_rate='fast'
        )
        # verify_lacp_state(sw1, sw2, sw1_lacp_mode='off', sw2_lacp_mode='off')


def configure_vlans(sw_list, sw_real_ports, step):
    step('STEP: Configure VLANs on devices')
    for sw in sw_list:
        # Create VLAN
        create_vlan(sw, LAG_VLAN)
        # Associate VLAN to LAG
        with sw.libs.vtysh.ConfigInterfaceLag(LAG_ID) as ctx:
            ctx.no_routing()
            ctx.vlan_access(LAG_VLAN)
        # Associate VLAN to host interface
        with sw.libs.vtysh.ConfigInterface(SW_LBL_PORTS[0]) as ctx:
            ctx.no_routing()
            ctx.vlan_access(LAG_VLAN)
        # Verify VLAN configuration was successfully applied
        verify_vlan_full_state(
            sw,
            LAG_VLAN, interfaces=[
                sw_real_ports[sw][0],
                'lag{}'.format(LAG_ID)
            ]
        )


def verify_interfaces_status(sw_list, step):
    step('STEP: Validate devices interfaces are on')
    print('Wait 15 seconds for interfaces to be on')
    sleep(15)
    for sw in sw_list:
        validate_turn_on_interfaces(sw, SW_LBL_PORTS)


def configure_workstations(hs_list, step):
    step('STEP: Configure workstations')
    for hs_num, hs in enumerate(hs_list):
        hs.libs.ip.interface(
            SW_LBL_PORTS[0],
            addr='{}{}/{}'.format(NETWORK, hs_num + 1, NETMASK),
            up=True
        )


def validate_connectivity(hs_list, step):
    step('STEP: Check workstations connectivity')
    # Ping between workstations should succeed
    check_connectivity_between_hosts(
        hs_list[0],
        '{}{}'.format(NETWORK, 1),
        hs_list[1],
        '{}{}'.format(NETWORK, 2),
        NUMBER_PINGS,
        True
    )


def change_lacp_mode(sw_list, sw_real_ports, step):
    step('STEP: Change LAGs to dynamic')
    create_lag_active(sw_list[0], LAG_ID)
    create_lag_passive(sw_list[1], LAG_ID)
    # Verify configuration was successfully applied
    for sw, mode in zip(sw_list, ['active', 'passive']):
        verify_lag_config(
            sw,
            LAG_ID,
            sw_real_ports[sw][1:],
            heartbeat_rate='fast',
            mode=mode
        )
    # Sleep 5 seconds to make sure negotiation took place
    sleep(5)
    # Verify LACP status on both devices
    verify_lacp_state(
        sw_list[0],
        sw_list[1],
        sw1_lacp_mode='active',
        sw2_lacp_mode='passive'
    )


def test_ft_lag_convert_to_lacp(topology, step):
    hs1 = topology.get('hs1')
    hs2 = topology.get('hs2')
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert hs1 is not None, 'hs1 was not initialized'
    assert hs2 is not None, 'hs2 was not initialized'
    assert sw1 is not None, 'sw1 was not initialized'
    assert sw2 is not None, 'sw2 was not initialized'

    sw_real_ports = {
        sw1: [sw1.ports[port] for port in SW_LBL_PORTS],
        sw2: [sw2.ports[port] for port in SW_LBL_PORTS]
    }

    # Enable switches interfaces
    enable_switches_interfaces([sw1, sw2], step)

    # Configure static LAGs with members
    configure_lags([sw1, sw2], sw_real_ports, step)

    # Add VLAN configuration to LAGs and workstation interfaces
    configure_vlans([sw1, sw2], sw_real_ports, step)

    # Validate interfaces are on
    verify_interfaces_status([sw1, sw2], step)

    # Configure workstations
    configure_workstations([hs1, hs2], step)

    # Validate workstations can communicate
    validate_connectivity([hs1, hs2], step)

    # Change LACP mode on LAGs from static to dynamic
    change_lacp_mode([sw1, sw2], sw_real_ports, step)

    # Validate workstations can communicate
    validate_connectivity([hs1, hs2], step)
