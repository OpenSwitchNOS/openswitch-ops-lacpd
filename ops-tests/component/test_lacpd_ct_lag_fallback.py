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

from lib_test import sw_set_intf_user_config
from lib_test import sw_clear_user_config
from lib_test import set_port_parameter
from lib_test import sw_set_intf_pm_info
from lib_test import sw_create_bond
from lib_test import verify_intf_in_bond
from lib_test import verify_intf_not_in_bond
from lib_test import verify_intf_status

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
sw1:if01 -- sw2:if01
sw1:if02 -- sw2:if02
"""

# Interfaces from 1-10 are 1G ports.
sw_1g_intf_start = 1
sw_1g_intf_end = 3
n_1g_links = 2
# sw_1g_intf = [str(i) for i in range(sw_1g_intf_start, sw_1g_intf_end)]
port_labels_1g = ['if01', 'if02']
sw_1g_intf = []


def lacpd_switch_pre_setup(sw):
    for intf in range(sw_1g_intf_start, sw_1g_intf_end):
        sw_set_intf_pm_info(sw, intf, ('connector="SFP_RJ45"',
                                       'connector_status=supported',
                                       'max_speed="1000"',
                                       'supported_speeds="1000"'))


@pytest.fixture(scope="module")
def main_setup(request, topology):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    sw1("/bin/systemctl stop pmd", shell='bash')
    sw2("/bin/systemctl stop pmd", shell='bash')

    global sw_1g_intf
    for lbl in port_labels_1g:
        sw_1g_intf.append(sw1.ports[lbl])

    def cleanup():
        sw1("/bin/systemctl start pmd", shell='bash')
        sw2("/bin/systemctl start pmd", shell='bash')

    request.addfinalizer(cleanup)


# Simulate valid pluggable modules in all the modules.
@pytest.fixture()
def setup(request, topology):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print('Simulate valid pluggable modules in all the modules.')
    lacpd_switch_pre_setup(sw1)
    lacpd_switch_pre_setup(sw2)

    def cleanup():
        print('Clear the user_config of all the Interfaces.\n'
              'Reset the pm_info to default values.')
        for intf in range(sw_1g_intf_start, sw_1g_intf_end):
            sw_clear_user_config(sw1, intf)
            sw_clear_user_config(sw2, intf)
            sw_set_intf_pm_info(sw1, intf, ('connector=absent',
                                'connector_status=unsupported'))
            sw_set_intf_pm_info(sw2, intf, ('connector=absent',
                                'connector_status=unsupported'))

    request.addfinalizer(cleanup)


@pytest.mark.skipif(True, reason="Test case was disable for owners.")
def test_lacpd_fallback_dynamic_lag_config(topology, step, main_setup, setup):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    print("\n============= lacpd user config"
          " (dynamic LAG) tests =============\n")

    system_mac = {}
    system_mac[1] = sw1("ovs-vsctl get system . system_mac",
                        shell='bash').rstrip('\r\n')
    system_mac[2] = sw2("ovs-vsctl get system . system_mac",
                        shell='bash').rstrip('\r\n')
    system_prio = {}
    system_prio[1] = "65534"
    system_prio[2] = "65534"

    # Test lacp down
    print("\n############### Test Case 1 - Verify lacp negotiation"
          " fails ###############\n")
    print("#######################################################"
          "####################\n")

    # Create two dynamic LAG with two ports each.
    sw_create_bond(sw1, "lag0", sw_1g_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag0", sw_1g_intf[0:2], lacp_mode="active")

    set_port_parameter(sw1, "lag0", ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, "lag0", ['other_config:lacp-time=fast'])

    # Enable both the interfaces.
    for intf in sw_1g_intf[0:2]:
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])

    # Verify that all the interfaces are linked up
    print("\n### Verify that all the interfaces are linked up ###\n")
    for intf in sw_1g_intf[0:2]:
        verify_intf_status(sw1, intf, "link_state", "up")
        verify_intf_status(sw2, intf, "link_state", "up")
        verify_intf_status(sw1, intf, "link_speed", "1000000000")
        verify_intf_status(sw2, intf, "link_speed", "1000000000")

    for intf in sw_1g_intf[0:2]:
        verify_intf_in_bond(sw1, intf, "Interfaces are expected to be "
                                       "part of dynamic LAG when "
                                       "both the switches are in "
                                       "active mode on switch1")
        verify_intf_in_bond(sw2, intf, "Interfaces are expected to be "
                                       "part of dynamic LAG when "
                                       "both the switches are in "
                                       "active mode on switch2")

    # Set lacp fail
    print("lacp fallback true \n")
    set_port_parameter(sw1, "lag0", ['other_config:lacp-fallback-ab=true'])
    set_port_parameter(sw2, "lag0", ['other_config:lacp-fallback-ab=true'])

    # Disable Interfaces from bond in switch 2.
    # Verify that hw_bond_config:{rx_enabled="false", tx_enabled="false"}
    # Set lacp to "off"
    set_port_parameter(sw2, "lag0", ['lacp=off'])

    print("Verify that interfaces were disabled from LAG"
          " when RX/TX are set to false.\n")

    # interfaces must be down due to partner missing
    print("\n### interfaces must be down due to partner missing ###\n")
    for intf in sw_1g_intf[0:2]:
        if intf == "1":
            print("Verifying interface 1 is up \n")
            verify_intf_in_bond(sw1, intf, "One Interface must be up")
        if intf != "1":
            print("Verifying rest of interfaces are down \n")
            verify_intf_not_in_bond(sw1, intf,
                                    "Rest of interfaces must be down")

    # Add the Interface back into the LAG/Trunk.
    # Set lacp to "active"
    print("\n############# LACP back to active \n")
    set_port_parameter(sw2, "lag0", ['lacp=active'])

    print("Verify interface lacp_status\n")
    # interfaces must be up when lag is back to active
    for intf in sw_1g_intf[0:2]:
        print("Verifying all interfaces are up \n")
        verify_intf_in_bond(sw1, intf, "All Interfaces must be up")

    print("lacp fallback false \n\n")
    set_port_parameter(sw1, "lag0", ['other_config:lacp-fallback-ab=false'])
    set_port_parameter(sw2, "lag0", ['other_config:lacp-fallback-ab=false'])

    # interfaces back to out of bond to lag failure

    # Set lacp to "off"
    set_port_parameter(sw2, "lag0", ['lacp=off'])

    sleep(4)

    print("############# Verify interface lacp_status ############# \n")
    print("##########  LACP failed and fallback = false ########### \n")
    # interfaces must be down due to partner missing.
    for intf in sw_1g_intf[0:2]:
        print("Verifying all interfaces are down \n")
        verify_intf_not_in_bond(sw1, intf,
                                "All interfaces must be down")
