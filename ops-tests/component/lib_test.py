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

from time import sleep
import re

ovs_vsctl = "/usr/bin/ovs-vsctl "

header_length = 40

def print_header(msg):
    print('%s\n%s\n%s\n' % ('=' * header_length,
                            msg,
                            '=' * header_length))

# This method calls a function to retrieve data, then calls another function
# to compare the data to the expected value(s). If it fails, it sleeps for
# half a second, then retries, up to a specified retry limit (default 20 = 10
# seconds). It returns a tuple of the test status and the actual results.
def timed_compare(data_func, params, compare_func,
                  expected_results, retries=20):
    while retries != 0:
        actual_results = data_func(params)
        result = compare_func(actual_results, expected_results, retries == 1)
        if result is True:
            return True, actual_results
        sleep(0.5)
        retries -= 1
    return False, actual_results


# Set user_config for an Interface.
def sw_set_intf_user_config(sw, interface, config):
    c = ovs_vsctl + "set interface " + str(interface)
    for s in config:
        c += " user_config:" + s
    return sw(c, shell='bash')


# Clear user_config for an Interface.
def sw_clear_user_config(sw, interface):
    c = ovs_vsctl + "clear interface " + str(interface) + " user_config"
    return sw(c, shell='bash')


# Set pm_info for an Interface.
def sw_set_intf_pm_info(sw, interface, config):
    c = ovs_vsctl + "set interface " + str(interface)
    for s in config:
        c += " pm_info:" + s
    return sw(c, shell='bash')


def set_port_parameter(sw, port, config):
    """Configure parameters in 'config' from 'port' on 'sw'."""

    cmd = "%s set port %s %s" % (ovs_vsctl,
                                 str(port),
                                 ' '.join(map(str, config)))
    return sw(cmd, shell='bash')


def clear_port_parameter(sw, port, config):
    """Clears parameters in 'config' from 'port' on 'sw'."""

    cmd = "%s clear port %s %s" % (ovs_vsctl,
                                   str(port),
                                   ' '.join(map(str, config)))
    return sw(cmd, shell='bash')


def remove_port_parameter(sw, port, col, keys):
    """Removes 'keys' in 'col' section from 'port' on 'sw'."""

    cmd = "%s remove port %s %s %s" % (ovs_vsctl,
                                       port,
                                       col,
                                       ' '.join(map(str, keys)))

    return sw(cmd, shell='bash')


def set_intf_parameter(sw, intf, config):
    """Configure parameters in 'config' to 'intf' in 'sw'."""

    cmd = "%s set interface %s %s" % (ovs_vsctl,
                                      str(intf),
                                      ' '.join(map(str, config)))
    return sw(cmd, shell='bash')


def sw_get_intf_state(params):
    """Get the values of a set of columns from Interface table.

    This function returns a list of values if 2 or more
    fields are requested, and returns a single value (no list)
    if only 1 field is requested.
    """
    cmd = '%s get interface %s %s' % (ovs_vsctl,
                                      str(params[1]),
                                      ' '.join(map(str, params[2])))

    out = params[0](cmd, shell='bash').replace('"', '').splitlines()
    return out


def sw_get_port_state(params):
    """Retrive values from Port table using 'ovs-vsctl'."""
    cmd = '%s get port %s %s' % (ovs_vsctl,
                                 str(params[1],
                                 ' '.join(map(str, params[2]))))

    out = params[0](cmd, shell='bash').splitlines()
    if len(out) == 1:
        out = out[0]
    return out


def sw_create_bond(sw, bond_name, intf_list, lacp_mode="off"):
    """Create a bond/lag/trunk in the OVS-DB."""
    print("Creating LAG %s with interfaces: %s\n" % (bond_name,
                                                     str(intf_list)))

    cmd = '%s add-bond bridge_normal %s %s ' % (ovs_vsctl,
                                               bond_name,
                                               ' '.join(map(str, intf_list)))

    cmd += '-- set port %s lacp=%s hw_config:enable=true' % (bond_name,
                                                             lacp_mode)
    return sw(cmd, shell='bash')

def sw_delete_bond(sw, bond_name, intf_list):
    """Delete a bond/lag/trunk in the OVS-DB.

    This will remove the interfaces in 'intf_list' from 'bond_name' and then
    remove the 'bond_name'.
    """

    remove_intf_list_from_bond(sw, bond_name, intf_list)

    cmd = '%s del-port bridge_normal %s' % (ovs_vsctl, bond_name)

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


# Verify that an Interface is part of a bond.
def verify_intf_in_bond(sw, intf, msg):
    result = timed_compare(sw_get_intf_state,
                           (sw, intf, ['hw_bond_config:rx_enabled',
                            'hw_bond_config:tx_enabled']),
                           verify_compare_tuple, ['true', 'true'])
    assert result == (True, ["true", "true"]), msg


# Verify that an Interface is not part of any bond.
def verify_intf_not_in_bond(sw, intf, msg):
    result = timed_compare(sw_get_intf_state,
                           (sw, intf, ['hw_bond_config:rx_enabled',
                            'hw_bond_config:tx_enabled']),
                           verify_compare_tuple_negate, ['true', 'true'])
    assert result[0] is True and\
        result[1][0] is not 'true' and\
        result[1][1] is not 'true', msg


# Verify Interface status
def verify_intf_status(sw, intf, column_name, value, msg=''):
    result = timed_compare(sw_get_intf_state,
                           (sw, intf, [column_name]),
                           verify_compare_tuple, [value])
    assert result == (True, [value]), msg


def verify_intf_field_absent(sw, intf, field, msg):
    retries = 20
    while retries != 0:
        result = sw_get_intf_state((sw, intf, [field]))
        if "no key" in result[0]:
            return
        sleep(0.5)
        retries -= 1
    assert "no key" in result, msg


def remove_intf_from_bond(sw, bond_name, intf_name, fail=True):
    """Remove an Interface from a bond."""

    print("Removing interface " + intf_name + " from LAG " + bond_name + "\n")

    # Get the UUID of the Interface that has to be removed.
    cmd = "%s get interface %s _uuid" % (ovs_vsctl, str(intf_name))
    intf_uuid = sw(cmd, shell='bash').rstrip('\r\n')

    # Get the current list of Interfaces in the bond.
    cmd = "%s get port %s interfaces" % (ovs_vsctl, bond_name)
    out = sw(cmd, shell='bash')
    intf_list = out.rstrip('\r\n').strip("[]").replace(" ", "").split(',')

    assert intf_uuid in intf_list, "Unable to find the interface in the bond"

    # Remove the given intf_name's UUID from the bond's Interfaces.
    new_intf_list = [i for i in intf_list if i != intf_uuid]
    c = ovs_vsctl + "set port " + bond_name + " interfaces=" + new_intf_str
    out = sw(c, shell='bash')

    return out


def remove_intf_list_from_bond(sw, bond_name, intf_list):
    """Remove a list of Interfaces from the bond."""
    for intf in intf_list:
        remove_intf_from_bond(sw, bond_name, intf)


def sw_wait_until_all_sm_ready(sws, intfs, ready, max_retries=30):
    """Verify that all 'intfs' SM have status like 'ready'.

    We need to verify that all interfaces' State Machines have 'ready' within
    'ovs-vsctl' command output.

    The main structure is an array of arrays with the format of:
    [ [<switch>, <interfaces number>, <SM ready>], ...]

    'not_ready' will be all arrays that 'SM ready' is still False and needs to
    verify again.
    """
    all_intfs = []
    retries = 0

    for sw in sws:
        all_intfs += [[sw, intf, False] for intf in intfs]

    # All arrays shal be True
    while not all(intf[2] for intf in all_intfs):
        # Retrieve all arrays that have False
        not_ready = filter(lambda intf: not intf[2], all_intfs)

        assert retries is not max_retries, \
            "Exceeded max retries. SM never achieved status: %s" % ready

        for sm in not_ready:
            cmd = '%s get interface %s lacp_status:actor_state' % (ovs_vsctl,
                                                                   sm[1])

            """
            If you want to print the output remove or set 'silent' to False

            It was removed because of the frequency of 'ovs-vsctl' calls to
            validate SM status and constant prints will make test output
            ilegible
            """
            out = sm[0](cmd, shell='bash', silent=False)
            sm[2] = bool(re.match(ready, out))

            retries +=1

        sleep(1)
