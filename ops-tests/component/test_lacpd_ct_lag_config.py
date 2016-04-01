# Copyright (C) 2015 Hewlett-Packard Development Company, L.P.
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

from time import sleep
import pytest

from lib_test import sw_set_intf_user_config
from lib_test import sw_clear_user_config
from lib_test import sw_set_intf_pm_info
from lib_test import set_port_parameter
from lib_test import sw_get_intf_state
from lib_test import sw_get_port_state
from lib_test import sw_create_bond
from lib_test import verify_intf_in_bond
from lib_test import verify_intf_not_in_bond
from lib_test import verify_intf_status
from lib_test import timed_compare
from lib_test import remove_intf_from_bond
from lib_test import remove_intf_list_from_bond


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
sw1:if03 -- sw2:if03
sw1:if04 -- sw2:if04
sw1:if05 -- sw2:if05
sw1:if06 -- sw2:if06
sw1:if07 -- sw2:if07
sw1:if08 -- sw2:if08
sw1:if09 -- sw2:if09
sw1:if10 -- sw2:if10
# 10 Gig ports
sw1:if11 -- sw2:if11
sw1:if12 -- sw2:if12
sw1:if13 -- sw2:if13
sw1:if14 -- sw2:if14
sw1:if15 -- sw2:if15
sw1:if16 -- sw2:if16
sw1:if17 -- sw2:if17
sw1:if18 -- sw2:if18
sw1:if19 -- sw2:if19
sw1:if20 -- sw2:if20
# 40 Gig ports
sw1:if49 -- sw2:if49
sw1:if50 -- sw2:if50
sw1:if51 -- sw2:if51
sw1:if52 -- sw2:if52
sw1:if53 -- sw2:if53
sw1:if54 -- sw2:if54
"""


ovs_vsctl = "/usr/bin/ovs-vsctl "

# Interfaces from 1-10 are 1G ports.
# Interfaces from 11-20 are 10G ports.
# Interfaces from 49-54 are 40G ports.
sw_to_host1 = 21
sw_to_host2 = 22

sw_1g_intf_start = 1
sw_1g_intf_end = 10
n_1g_links = 10
# sw_1g_intf = [str(i) for i in range(sw_1g_intf_start, sw_1g_intf_end)]
port_labels_1G = ['if01', 'if02', 'if03', 'if04', 'if05', 'if06', 'if07', 'if08', 'if09', 'if10']  # noqa
sw_1g_intf = []

sw_10g_intf_start = 11
sw_10g_intf_end = 20
n_10g_link2 = 10
# sw_10g_intf = [str(i) for i in range(sw_10g_intf_start, sw_10g_intf_end)]
port_labels_10G = ['if11', 'if12', 'if13', 'if14', 'if15', 'if16', 'if17', 'if18', 'if19', 'if20']  # noqa
sw_10g_intf = []

sw_40g_intf_start = 49
sw_40g_intf_end = 55
n_40g_link2 = 6
# sw_40g_intf = [str(i) for i in range(sw_40g_intf_start, sw_40g_intf_end)]
port_labels_40G = ['if49', 'if50', 'if51', 'if52', 'if53', 'if54']
sw_40g_intf = []


# Set open_vsw_lacp_config parameter(s)
def set_open_vsw_lacp_config(sw, config):
    c = ovs_vsctl + "set system ."
    for s in config:
        c += " lacp_config:" + s
    return sw(c, shell='bash')


def sys_open_vsw_lacp_config_clear(sw):
    c = ovs_vsctl + "remove system . lacp_config lacp-system-id " + \
        "lacp_config lacp-system-priority"
    sw(c, shell='bash')


# Set interface:other_config parameter(s)
def set_intf_other_config(sw, intf, config):
    c = ovs_vsctl + "set interface " + str(intf)
    for s in config:
        c += ' other_config:%s' % s
    return sw(c, shell='bash')


# Get interface:other_config parameter(s)
def get_intf_other_config(sw, intf, params):
    c = ovs_vsctl + "get interface " + str(intf)
    for f in params:
        c += ' other_config:%s' % f
    out = sw(c, shell='bash').splitlines()
    if len(out) == 1:
        out = out[0]
    return out


# Delete interface other config parameter(s)
def del_intf_other_config(sw, intf, params):
    c = ovs_vsctl + "remove interface " + str(intf)
    for f in params:
        c += ' other_config %s' % f
    return sw(c, shell='bash')


# Simulate the link state on an Interface
def simulate_link_state(sw, interface, link_state="up"):
    print("Setting the link state of interface " + interface +
          " to " + link_state + "\n")
    c = ovs_vsctl + "set interface " + str(interface) +\
        " link_state=" + link_state
    return sw(c, shell='bash')


# Delete a bond/lag/trunk from OVS-DB.
def sw_delete_bond(sw, bond_name):
    print("Deleting the bond " + bond_name + "\n")
    c = ovs_vsctl + "del-port bridge_normal " + bond_name
    return sw(c, shell='bash')


# Add a new Interface to the existing bond.
def add_intf_to_bond(sw, bond_name, intf_name):
    print("Adding interface " + intf_name + " to LAG " + bond_name + "\n")

    # Get the UUID of the interface that has to be added.
    c = ovs_vsctl + "get interface " + str(intf_name) + " _uuid"
    intf_uuid = sw(c, shell='bash').rstrip('\r\n')

    # Get the current list of Interfaces in the bond.
    c = ovs_vsctl + "get port " + bond_name + " interfaces"
    out = sw(c, shell='bash')
    intf_list = out.rstrip('\r\n').strip("[]").replace(" ", "").split(',')
    intf_uuid = intf_uuid.strip("[]").replace(" ", "").replace("'", "").split('\n')  # noqa
    if intf_uuid in intf_list:
        print("Interface " + intf_name + " is already part of " +
              bond_name + "\n")
        return

    new_intf_str = []
    for i in intf_list:
        if ']' in i:
            i = i.replace(']', '').split('\n')
            i = i[0]
        new_intf_str.append(i)

    # Add the given intf_name's UUID to existing Interfaces.
    new_intf_str.append(intf_uuid[0])

    # Set the new Interface list in the bond.
    new_intf_str = '[' + ",".join(new_intf_str) + ']'

    c = ovs_vsctl + "set port " + bond_name + " interfaces=" + new_intf_str
    return sw(c, shell='bash')


# Add a list of Interfaces to the bond.
def add_intf_list_from_bond(sw, bond_name, intf_list):
    for intf in intf_list:
        add_intf_to_bond(sw, bond_name, intf)


def verify_compare_value(actual, expected, final):
    if actual != expected:
        return False
    return True


def verify_compare_tuple(actual, expected, final):
    if len(actual) != len(expected):
        return False
    if actual != expected:
        return False
    return True


def verify_compare_tuple_negate(actual, expected, final):
    if len(actual) != len(expected):
        return False
    for i in range(0, len(expected)):
        if actual[i] == expected[i]:
            return False
    return True


def verify_compare_complex(actual, expected, final):
    attrs = []
    for attr in expected:
        attrs.append(attr)
    if len(actual) != len(expected):
        return False
    for i in range(0, len(attrs)):
        if actual[i] != expected[attrs[i]]:
            return False
    return True


def verify_intf_field_absent(sw, intf, field, msg):
    retries = 20
    while retries != 0:
        result = sw_get_intf_state((sw, intf, [field]))
        if "no key" in result[0]:
            return
        sleep(0.5)
        retries -= 1
    assert "no key" in result, msg


def verify_intf_lacp_status(sw, intf, verify_values, context=''):
    request = []
    attrs = []
    for attr in verify_values:
        request.append('lacp_status:' + attr)
        attrs.append(attr)
    result = timed_compare(sw_get_intf_state,
                           (sw, intf, request),
                           verify_compare_complex, verify_values)
    field_vals = result[1]
    for i in range(0, len(attrs)):
        verify_values[attrs[i]].replace('"', '')
        assert field_vals[i] == verify_values[attrs[i]], context +\
            ": invalid value for " + attrs[i] + ", expected " +\
            verify_values[attrs[i]] + ", got " + field_vals[i]


def verify_port_lacp_status(sw, lag, value, msg=''):
    result = timed_compare(sw_get_port_state,
                           (sw, lag, ["lacp_status"]),
                           verify_compare_value, value)
    assert result == (True, value), msg


def lacpd_switch_pre_setup(sw):
    for intf in range(sw_1g_intf_start, sw_1g_intf_end):
        if intf > 9:
            port = "if"
        else:
            port = "if0"
        # port = intf > 9 ? "if" : "if0"
        port = "{}{}".format(port, intf)
        sw_set_intf_pm_info(sw, sw.ports[port], ('connector="SFP_RJ45"',
                                                 'connector_status=supported',
                                                 'max_speed="1000"',
                                                 'supported_speeds="1000"'))

    for intf in range(sw_10g_intf_start, sw_10g_intf_end):
        if intf > 9:
            port = "if"
        else:
            port = "if0"
        # port = intf > 9 ? "if" : "if0"
        port = "{}{}".format(port, intf)
        sw_set_intf_pm_info(sw, sw.ports[port], ('connector=SFP_SR',
                                                 'connector_status=supported',
                                                 'max_speed="10000"',
                                                 'supported_speeds="10000"'))

    for intf in range(sw_40g_intf_start, sw_40g_intf_end):
        if intf > 9:
            port = "if"
        else:
            port = "if0"
        # port = intf > 9 ? "if" : "if0"
        port = "{}{}".format(port, intf)
        sw_set_intf_pm_info(sw, sw.ports[port], ('connector=QSFP_SR4',
                                                 'connector_status=supported',
                                                 'max_speed="40000"',
                                                 'supported_speeds="40000, \
                                                 10000"'))


@pytest.fixture(scope="module")
def main_setup(request, topology):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    sw1("/bin/systemctl stop pmd", shell='bash')
    sw2("/bin/systemctl stop pmd", shell='bash')

    global sw_1g_intf, sw_10g_intf_end, sw_40g_intf, port_labels_1G, port_labels_10G, port_labels_40G  # noqa
    for lbl in port_labels_1G:
        sw_1g_intf.append(sw1.ports[lbl])
    for lbl in port_labels_10G:
        sw_10g_intf.append(sw1.ports[lbl])
    for lbl in port_labels_40G:
        sw_40g_intf.append(sw1.ports[lbl])

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
        for intf in range(1, 54):
            sw_clear_user_config(sw1, intf)
            sw_clear_user_config(sw2, intf)
            sw_set_intf_pm_info(sw1, intf, ('connector=absent',
                                'connector_status=unsupported'))
            sw_set_intf_pm_info(sw2, intf, ('connector=absent',
                                'connector_status=unsupported'))

    request.addfinalizer(cleanup)


# Enable all the Interfaces used in the test.
def enable_all_intf(sw1, sw2):
    for intf in range(1, 54):
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])


def test_lacpd_lag_static_config(topology, step, main_setup, setup):
    print("\n============= lacpd user config "
          "(static LAG) tests =============\n")
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    # Setup valid pluggable modules.
    step("Setting up valid pluggable modules in all the Interfaces.\n")

    # Create a Staic lag of 'eight' ports of each speed type
    sw_create_bond(sw1, "lag0", sw_1g_intf[0:8])
    sw_create_bond(sw1, "lag1", sw_10g_intf[0:8])
    sw_create_bond(sw1, "lag2", sw_40g_intf[0:8])

    # When Interfaces are not enabled, they shouldn't be added to LAG.
    step("Verify that interfaces are not added to LAG "
         "when they are disabled.\n")
    for intf in sw_1g_intf[0:8] + sw_10g_intf[0:8] + sw_40g_intf[0:8]:
        verify_intf_not_in_bond(sw1, intf, "Interfaces should not be part "
                                "of LAG when they are disabled.")

    step("Enabling all the interfaces.\n")
    enable_all_intf(sw1, sw2)

    # Verify that hw_bond_config:{rx_enabled="true", tx_enabled="true"}
    # In static LAG, Interfaces should be added to LAG,
    # even though ports are not added to LAG on S2.
    step("Verify that all the interfaces are added to LAG.\n")

    for intf in sw_1g_intf[0:8]:
        verify_intf_in_bond(sw1, intf, "Expected the 1G interfaces "
                            "to be added to static lag")

    for intf in sw_10g_intf[0:8]:
        verify_intf_in_bond(sw1, intf, "Expected the 10G interfaces "
                            "to be added to static lag")

    for intf in sw_40g_intf[0:8]:
        verify_intf_in_bond(sw1, intf, "Expected the 40G interfaces "
                            "to be added to static lag")

    # Remove an Interface from bond.
    # Verify that hw_bond_config:{rx_enabled="false", tx_enabled="false"}
    remove_intf_from_bond(sw1, "lag0", sw_1g_intf[0])

    step("Verify that RX/TX is set to false when it is removed from LAG.\n")
    verify_intf_not_in_bond(sw1, sw_1g_intf[0],
                            "Expected the interfaces to be removed "
                            "from static lag")

    # Add the Interface back into the LAG/Trunk.
    add_intf_to_bond(sw1, "lag0", sw_1g_intf[0])

    # Verify that Interface is added back to LAG/Trunk
    step("Verify that RX/TX is set to true when it is added to LAG.\n")
    verify_intf_in_bond(sw1, sw_1g_intf[0], "Interfaces is not "
                        "added back to the trunk.")

    # In case of static LAGs we need a minimum of two Interfaces.
    # Remove all Interfaces except two.
    remove_intf_list_from_bond(sw1, "lag0", sw_1g_intf[2:8])

    step("Verify that a LAG can exist with two interfaces.\n")
    for intf in sw_1g_intf[0:2]:
        verify_intf_in_bond(sw1, intf, "Expected a static trunk "
                            "of two interfaces.")

    for intf in sw_1g_intf[2:8]:
        verify_intf_not_in_bond(sw1, intf, "Expected interfaces "
                                "to be removed from the LAG.")

    # OPS_TODO: If we remove one more Interface,
    # how will we know if the LAG has suddenly become PORT

    # Disable one of the Interfaces, then it should be
    # removed from the LAG.
    step("Verify that a interface is removed "
         "from LAG when it is disabled.\n")
    sw_set_intf_user_config(sw1, sw_10g_intf[0], ['admin=down'])
    verify_intf_not_in_bond(sw1, sw_10g_intf[0],
                            "Disabled interface is not removed "
                            "from the LAG.")

    # Enable the Interface back, then it should be added back
    step("Verify that a interface is added back to LAG "
         "when it is re-enabled.\n")
    sw_set_intf_user_config(sw1, sw_10g_intf[0], ['admin=up'])
    verify_intf_in_bond(sw1, sw_10g_intf[0],
                        "Re-enabled interface is not added "
                        "back to the trunk.")

    # OPS_TODO: Enhance VSI to simulate link up/down.
    # Looks like we need ovs-appctl mechanism to simulate link down,
    # otherwise switchd is always re-setting the link.
    # simulate_link_state(s1, sw_10G_intf[0], 'down')
    # verify_intf_not_in_bond(s1, sw_10G_intf[0], \
    #                         "Link down interface is not removed "
    #                         "from the trunk.")

    # simulate_link_state(s1, sw_10G_intf[0], 'up')
    # verify_intf_in_bond(s1, sw_10G_intf[0], \
    #                     "Interface is not added back when it is "
    #                     "linked up")

    sw_delete_bond(sw1, "lag0")
    sw_delete_bond(sw1, "lag1")
    sw_delete_bond(sw1, "lag2")


def test_lacpd_lag_static_negative_tests(topology, step, main_setup, setup):
    step("\n============= lacpd user config "
         "(static LAG negative) tests =============\n")
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    # Setup valid pluggable modules.
    sw_set_intf_user_config(sw1, sw_1g_intf[0], ['admin=up'])
    sw_set_intf_user_config(sw1, sw_1g_intf[1], ['admin=up'])

    sw_set_intf_user_config(sw1, sw_10g_intf[0], ['admin=up'])
    sw_set_intf_user_config(sw1, sw_10g_intf[1], ['admin=up'])

    # Create a static LAG with Interfaces of multiple speeds.
    sw_create_bond(sw1, "lag0", sw_1g_intf[0:2])
    add_intf_list_from_bond(sw1, "lag0", sw_10g_intf[0:2])

    # When Interfaces with different speeds are added,
    # then the first interface is choosen as base, and
    # then only those interfaces of the same speed are added to LAG

    step("Verify that interfaces with matching speeds "
         "are enabled in LAG.\n")
    for intf in sw_1g_intf[0:2]:
        verify_intf_in_bond(sw1, intf, "Expected the 1G "
                            "interfaces to be added to LAG ")

    step("Verify that interfaces with "
         "non-matching speeds are disabled in LAG.\n")
    for intf in sw_10g_intf[0:2]:
        verify_intf_not_in_bond(sw1, intf, "Expected the 10G interfaces "
                                "not added to LAG "
                                "when there is speed mismatch")

    # When both the 1G interfaces are disabled/down,
    # then we should add the 10G interfaces to LAG.
    step("Verify interfaces join LAG when speed "
         "matching block is removed.\n")
    remove_intf_list_from_bond(sw1, "lag0", sw_1g_intf[0:2])

    for intf in sw_10g_intf[0:2]:
        verify_intf_in_bond(sw1, intf,
                            "Interface should be added "
                            "to bond after others are deleted.")

    sw_delete_bond(sw1, "lag0")


def test_lacpd_lag_dynamic_config(topology, step, main_setup, setup):  # noqa
    step("\n============= lacpd user config "
         "(dynamic LAG) tests =============\n")
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert sw1 is not None
    assert sw2 is not None

    # These lines are helpful to debug errors with the daemon
    # during the tests execution
    # s1.ovscmd("ovs-appctl -t ops-lacpd vlog/set dbg")
    # s2.ovscmd("ovs-appctl -t ops-lacpd vlog/set dbg")

    system_mac = {}
    system_mac[1] = sw1("ovs-vsctl get system . "
                        "system_mac", shell='bash').rstrip('\r\n')
    system_mac[2] = sw2("ovs-vsctl get system . "
                        "system_mac", shell='bash').rstrip('\r\n')
    system_prio = {}
    system_prio[1] = "65534"
    system_prio[2] = "65534"

    base_mac = {}
    base_mac[1] = "70:72:11:11:11:d4"
    base_mac[2] = "70:72:22:22:22:d4"

    change_mac = "aa:bb:cc:dd:ee:ff"
    change_prio = "555"
    invalid_mac = "aa:bb:cc:dd:ee:fg"

    alt_mac = "70:72:33:33:33:d4"
    alt_prio = "99"

    base_prio = "100"
    port_mac = "70:72:44:44:44:d4"
    port_prio = "88"

    # Enable all the interfaces under test.
    step("Test base mac address\n")
    for intf in sw_1g_intf[0:2]:
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])

    sw_create_bond(sw1, "lag0", sw_1g_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag0", sw_1g_intf[0:2], lacp_mode="active")

    for intf in sw_1g_intf[0:2]:
        set_intf_other_config(sw1, intf, ['lacp-aggregation-key=1'])
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=1'])

    for intf in sw_1g_intf[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                {"actor_system_id": system_prio[1] +
                                 "," + system_mac[1].replace('"', ''),
                                 "partner_state":
                                 "Activ:1,TmOut:0,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": system_prio[2] +
                                 "," + system_mac[2].replace('"', '')},
                                "s1:" + intf)

        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_system_id": system_prio[2] +
                                 "," + system_mac[2].replace('"', ''),
                                 "partner_state":
                                 "Activ:1,TmOut:0,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id":
                                 system_prio[1] + "," +
                                 system_mac[1].replace('"', '')},
                                "s1:" + intf)

    # Test lacp-time
    step("Verify port:other_config:lacp-time.\n")
    # Verify default lacp-time is "slow"
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_state":
                             "Activ:1,TmOut:0,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "actor_system_id": system_prio[1] +
                             "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:0,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0"},
                            "s1:" + intf)

    succes = False
    out = sw1('show lacp aggregates')
    lines = out.split('\n')
    for line in lines:
        if 'Heartbeat rate' and 'slow' in line:
            succes = True
    assert succes is True

    # Set lacp-time back to "fast"
    set_port_parameter(sw1, "lag0", ['other_config:lacp-time=fast'])
    set_port_parameter(sw1, "lag1", ['other_config:lacp-time=fast'])
    set_port_parameter(sw1, "lag2", ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, "lag0", ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, "lag1", ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, "lag2", ['other_config:lacp-time=fast'])

    # Verify "timeout" is now "fast"
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "actor_system_id": system_prio[1] +
                             "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0"},
                            "s1:" + intf)

    succes = False
    out = sw1('show lacp aggregates')
    lines = out.split('\n')
    for line in lines:
        if 'Heartbeat rate' and 'fast' in line:
            succes = True
    assert succes is True

    step("Override system parameters\n")
    # Change the LACP system ID on the switches.
    sw1("ovs-vsctl set system . lacp_config:lacp-system-id='" +
        base_mac[1] + "' lacp_config:lacp-system-priority=" +
        base_prio, shell='bash')
    sw2("ovs-vsctl set system . lacp_config:lacp-system-id='" +
        base_mac[2] + "' lacp_config:lacp-system-priority=" +
        base_prio, shell='bash')

    for intf in sw_1g_intf[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                {"actor_system_id": base_prio +
                                 "," + base_mac[1],
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": base_prio +
                                 "," + base_mac[2]},
                                "s1:" + intf)

        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_system_id": base_prio +
                                 "," + base_mac[2],
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": base_prio +
                                 "," + base_mac[1]},
                                "s1:" + intf)
    step("Override port parameters\n")
    sw1("ovs-vsctl set port lag0 other_config:lacp-system-id='" +
        port_mac + "' other_config:lacp-system-priority=" +
        port_prio, shell='bash')

    for intf in sw_1g_intf[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                {"actor_system_id": port_prio +
                                 "," + port_mac,
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": base_prio +
                                 "," + base_mac[2]},
                                "s1:" + intf)

        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_system_id":
                                 base_prio + "," + base_mac[2],
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": port_prio +
                                 "," + port_mac},
                                "s1:" + intf)

    step("Delete and recreate lag\n")
    # delete and recreate lag
    sw1("ovs-vsctl del-port lag0", shell='bash')
    sw2("ovs-vsctl del-port lag0", shell='bash')

    for intf in sw_1g_intf[0:2]:
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])

    sw_create_bond(sw1, "lag0", sw_1g_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag0", sw_1g_intf[0:2], lacp_mode="active")

    for intf in sw_1g_intf[0:2]:
        set_intf_other_config(sw1, intf, ['lacp-aggregation-key=1'])
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=1'])

    step("Verify system override still in effect\n")
    for intf in sw_1g_intf[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                {"actor_system_id": base_prio +
                                 "," + base_mac[1],
                                 "partner_state":
                                 "Activ:1,TmOut:0,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": base_prio +
                                 "," + base_mac[2]},
                                "s1:" + intf)

        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_system_id": base_prio +
                                 "," + base_mac[2],
                                 "partner_state":
                                 "Activ:1,TmOut:0,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": base_prio +
                                 "," + base_mac[1]},
                                "s1:" + intf)

    # finish testing
    sw1("ovs-vsctl del-port lag0", shell='bash')
    sw2("ovs-vsctl del-port lag0", shell='bash')

    # Create two dynamic LAG with two interfaces each.
    # the current schema doesn't allow creating a bond
    # with less than two interfaces. Once that is changed
    # we should modify the test case.
    step("Creating dynamic lag with two interfaces\n")
    sw_create_bond(sw1, "lag0", sw_1g_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag0", sw_1g_intf[0:2], lacp_mode="active")

    set_port_parameter(sw1, "lag0", ['other_config:lacp-time=fast'])
    set_port_parameter(sw2, "lag0", ['other_config:lacp-time=fast'])

    # Enable both interfaces.
    for intf in sw_1g_intf[0:2]:
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])

    # Verify that all the interfaces are linked up
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
                            "active mode on switch1")

    # Test system:lacp_config:{lacp-system-id,lacp-system-priority}
    intf = sw_1g_intf[0]

    # Set sys_id and sys_pri
    set_open_vsw_lacp_config(sw1, ['lacp-system-id=' +
                             change_mac, 'lacp-system-priority=' +
                             change_prio])

    step("Verify system:lacp_config:lacp-system-id "
         "and lacp-system-priority.\n")
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_system_id": change_prio +
                             "," + change_mac},
                            "s1:" + intf)

    # Clear sys_id and sys_pri, verify that values go back to default
    sys_open_vsw_lacp_config_clear(sw1)

    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_system_id":
                             system_prio[1] + "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "partner_system_id": base_prio +
                             "," + base_mac[2]},
                            "s1:" + intf)

    # Attempt to set invalid sys_id and invalid sys_pri
    step("Verify invalid system-id and system-priority are rejected\n")
    set_open_vsw_lacp_config(sw1, ['lacp-system-id=' + invalid_mac])
    set_open_vsw_lacp_config(sw1, ['lacp-system-priority=99999'])

    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "actor_system_id": system_prio[1] +
                             "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "partner_system_id": base_prio +
                             "," + base_mac[2]},
                            "s1:" + intf)

    # Test port:lacp
    # Set lacp to "passive"
    set_port_parameter(sw1, "lag0", ['lacp=passive'])

    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_state":
                             "Activ:0,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "actor_system_id": system_prio[1] +
                             "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "partner_system_id": base_prio +
                             "," + base_mac[2]},
                            "s1:" + intf)

    # Set lacp to "off"
    set_port_parameter(sw1, "lag0", ['lacp=off'])

    verify_intf_field_absent(sw1, intf,
                             'lacp_status:actor_state',
                             "lacp status should be empty")

    # Set lacp to "active"
    set_port_parameter(sw1, "lag0", ['lacp=active'])

    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "actor_system_id": system_prio[1] +
                             "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "partner_system_id": base_prio +
                             "," + base_mac[2]},
                            "s1:" + intf)

    # Test lacp-time
    step("Verify port:other_config:lacp-time.\n")
    # Set lacp-time to "slow"
    set_port_parameter(sw1, "lag0", ['other_config:lacp-time=slow'])

    # Verify "timeout" is now "slow"
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_state":
                             "Activ:1,TmOut:0,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "actor_system_id": system_prio[1] +
                             "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "partner_system_id": base_prio +
                             "," + base_mac[2]},
                            "s1:" + intf)

    # Set lacp-time back to "fast"
    set_port_parameter(sw1, "lag0", ['other_config:lacp-time=fast'])

    # Verify "timeout" is now "fast"
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "actor_system_id": system_prio[1] +
                             "," + system_mac[1],
                             "partner_state":
                             "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                             "Dist:1,Def:0,Exp:0",
                             "partner_system_id": base_prio +
                             "," + base_mac[2]},
                            "s1:" + intf)

    # Test interface:other_config:{lacp-port-id,lacp-port-priority}

    # Changing aggregation key on interface for s1
    # This will take out the interface from the lag0
    step("Validate aggregation key functionality\n")
    set_intf_other_config(sw1, intf, ['lacp-aggregation-key=2'])

    # First validate if the interface change the aggregation key correctly
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_key": "2"},
                            "s1:" + intf)

    # Verifying the interface is not part of any LAG anymore
    verify_intf_not_in_bond(sw1, intf, "Interfaces should not be part of "
                            "the dynamic LAG when aggregation key "
                            "is changed")

    # Get the interface back to the LAG
    set_intf_other_config(sw1, intf, ['lacp-aggregation-key=1'])
    verify_intf_in_bond(sw1, intf, "Interface should get part of "
                        "the dynamic LAG when aggregation key is changed")

    # Test interface:other_config:{lacp-port-id,lacp-port-priority}
    step("Test interface other_config values for lacp-port-id and "
         "lacp-port-priority")
    # save original values
    original_pri_info = sw_get_intf_state((sw1, intf,
                                          ['lacp_status:'
                                           'actor_port_id']))[0]
    # Set port_id, port_priority, and aggregation-key
    set_intf_other_config(sw1, intf,
                          ['lacp-port-id=222',
                           'lacp-port-priority=123'])

    # Get the new values
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_port_id": "123,222"},
                            "s1:" + intf)

    # Set invalid port_id and port_priority
    set_intf_other_config(sw1, intf,
                          ['lacp-port-id=-1',
                           'lacp-port-priority=-1'])

    # Get the new values
    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_port_id": original_pri_info},
                            "s1:" + intf)

    set_intf_other_config(sw1, intf,
                          ['lacp-port-id=65536',
                           'lacp-port-priority=65536'])

    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_port_id": original_pri_info},
                            "s1:" + intf)

    step("Clear lacp-port-id and lacp-port-priority\n")
    sw1("ovs-vsctl remove interface " + intf +
        " other_config lacp-port-id", shell='bash')
    sw1("ovs-vsctl remove interface " + intf +
        " other_config lacp-port-priority", shell='bash')

    verify_intf_lacp_status(sw1,
                            intf,
                            {"actor_port_id": original_pri_info},
                            "s1:" + intf)

    step("Verify port lacp_status\n")
    # verify lag status
    verify_port_lacp_status(sw1,
                            "lag0",
                            '{bond_speed="1000", bond_status=ok}',
                            'Port lacp_status is expected to be '
                            'bond_speed=1000, '
                            'bond_status=ok')
    verify_port_lacp_status(sw2,
                            "lag0",
                            '{bond_speed="1000", bond_status=ok}',
                            'Port lacp_status is expected to be '
                            'bond_speed=1000, '
                            'bond_status=ok')

    step("Verify interface lacp_status\n")
    for intf in sw_1g_intf[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                {"actor_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "actor_system_id": system_prio[1] +
                                 "," + system_mac[1],
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": base_prio +
                                 "," + base_mac[2]},
                                "s1:" + intf)
        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "actor_system_id": base_prio +
                                 "," + base_mac[2],
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                                 "Dist:1,Def:0,Exp:0",
                                 "partner_system_id": system_prio[1] +
                                 "," + system_mac[1]},
                                "s2:" + intf)

    step("Verify dynamic update of system-level override\n")
    sw1("ovs-vsctl set system . lacp_config:lacp-system-id='" + alt_mac +
        "' lacp_config:lacp-system-priority=" + alt_prio, shell='bash')

    for intf in sw_1g_intf[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                {"actor_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:0,Col:0,"
                                 "Dist:0,Def:0,Exp:0",
                                 "actor_system_id": alt_prio +
                                 "," + alt_mac,
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:0,Col:0,"
                                 "Dist:0,Def:0,Exp:0",
                                 "partner_system_id": base_prio +
                                 "," + base_mac[2]},
                                "s1:" + intf)
        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:0,Col:0,"
                                 "Dist:0,Def:0,Exp:0",
                                 "actor_system_id": base_prio +
                                 "," + base_mac[2],
                                 "partner_state":
                                 "Activ:1,TmOut:1,Aggr:1,Sync:0,Col:0,"
                                 "Dist:0,Def:0,Exp:0",
                                 "partner_system_id": alt_prio +
                                 "," + alt_mac},
                                "s2:" + intf)

    step("Verify dynamic update of port-level override\n")
    sw_create_bond(sw2, "lag1", sw_1g_intf[4:6], lacp_mode="active")

    for intf in sw_1g_intf[4:6]:
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])

    for intf in sw_1g_intf[4:6]:
        set_intf_other_config(sw1, intf, ['lacp-aggregation-key=2'])
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=2'])

    for intf in sw_1g_intf[4:6]:
        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_system_id": base_prio +
                                 "," + base_mac[2]}, "s2:" + intf)

    step("Verify isolation of port-level override\n")
    # change just lag0
    sw2("ovs-vsctl set port lag0 other_config:lacp-system-id='" + port_mac +
        "' other_config:lacp-system-priority=" + port_prio, shell='bash')

    # verify that lag0 changed
    for intf in sw_1g_intf[0:2]:
        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_system_id": port_prio +
                                 "," + port_mac}, "s2:" + intf)

    # verify that lag1 did not change
    for intf in sw_1g_intf[4:6]:
        verify_intf_lacp_status(sw2,
                                intf,
                                {"actor_system_id": base_prio +
                                 "," + base_mac[2]}, "s2:" + intf)

    step("Verify port-level override applied to newly added interfaces\n")
    # add an interface to lag0
    add_intf_to_bond(sw2, "lag0", sw_1g_intf[2])
    sw_set_intf_user_config(sw2, sw_1g_intf[2], ['admin=up'])

    # verify that new interface has picked up correct information
    verify_intf_lacp_status(sw2,
                            sw_1g_intf[2],
                            {"actor_system_id": port_prio +
                             "," + port_mac}, "s2:" + sw_1g_intf[2])

    step("Verify clearing port-level override\n")
    # clear port-level settings
    sw2("ovs-vsctl remove port lag0 other_config lacp-system-id "
        "other_config lacp-system-priority", shell='bash')

    # verify that lag0 changed back to system values
    for intf in sw_1g_intf[0:3]:
        verify_intf_lacp_status(sw2, intf,
                                {"actor_system_id": base_prio + "," +
                                 base_mac[2]}, "s2:" + intf)
