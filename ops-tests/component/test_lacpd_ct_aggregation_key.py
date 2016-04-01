# -*- coding: utf-8 -*-

# (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
# GNU Zebra is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any
# later version.
#
# GNU Zebra is distributed in the hope that it will be useful, but
# WITHoutput ANY WARRANTY; withoutput even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Zebra; see the file COPYING.  If not, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.


# Topology definition. the topology contains two back to back switches
# having four links between them.

from time import sleep
from pytest import fixture

TOPOLOGY = """
# +-------+        +-------+
# |  sw1  <1:----:1>  sw2  |
# |  sw1  <2:----:2>  sw2  |
# |  sw1  <3:----:3>  sw2  |
# |  sw1  <4:----:4>  sw2  |
# |  sw1  <5:----:6>  sw2  |
# |  sw1  <6:----:7>  sw2  |
# |  sw1  <7:----:5>  sw2  |
# +-------+        +-------+

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2

# Links
sw1:if01 -- sw2:if01
sw1:if02 -- sw2:if02
sw1:if03 -- sw2:if03
sw1:if04 -- sw2:if04
sw1:if05 -- sw2:if06
sw1:if06 -- sw2:if07
sw1:if07 -- sw2:if05
"""

ovs_vsctl = "/usr/bin/ovs-vsctl "
sw_intf_start = 1
sw_intf_end = 4
sw_intf = [i for i in range(sw_intf_start, sw_intf_end + 1)]
# sw_intf_str = map(lambda x: str(x), sw_intf)
sw_intf_str = [str(i) for i in range(sw_intf_start, sw_intf_end + 1)]
sw1_crossed_over_intf = [5, 6, 7]
sw1_crossed_over_intf_str = ["5", "6", "7"]
sw2_crossed_over_intf = [6, 7, 5]
sw2_crossed_over_intf_str = ["6", "7", "5"]
sw_all_intf_start = 1
sw_all_intf_end = 7
sw_all_intf = [str(i) for i in range(sw_all_intf_start, sw_all_intf_end + 1)]
sw_intf_not_connected = [8, 9, 10]
# switches = []


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


def sw_get_intf_state(params):
    c = "{} get interface {}".format(ovs_vsctl, params[1])
    for f in params[2]:
        c = "{} {}".format(c, f)
    out = params[0](c, shell='bash').splitlines()
    return out


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


# Set pm_info for an Interface.
def sw_set_intf_pm_info(sw, interface, config):
    c = "{} set interface {}".format(ovs_vsctl, interface)
    for s in config:
        c = "{} pm_info:{}".format(c, s)
    return sw(c, shell='bash')


def lacpd_switch_pre_setup(sw):
    for intf in range(sw_all_intf_start, sw_all_intf_end + 1):
        sw_set_intf_pm_info(sw, intf, ('connector="SFP_RJ45"',
                                       'connector_status=supported',
                                       'max_speed="1000"',
                                       'supported_speeds="1000"'))


# Set user_config for an Interface.
def sw_set_intf_user_config(sw, interface, config):
    c = "{} {} {}".format(ovs_vsctl, "set interface", interface)
    for s in config:
        c = "{} user_config:{}".format(c, s)
    return sw(c, shell='bash')


# Create a bond/lag/trunk in the OVS-DB.
def sw_create_bond(sw1, bond_name, intf_list, lacp_mode="off"):
    print("Creating lag {} with interfaces:{}".format(bond_name,
                                                      str(intf_list)))
    c = "{}add-bond bridge_normal {} {}".format(ovs_vsctl, bond_name,
                                                " ".join(map(str, intf_list)))
    c = "{} -- set port {} lacp={}".format(c, bond_name, lacp_mode)
    return sw1(c, shell='bash')


# Set interface:other_config parameter(s)
def set_intf_other_config(sw, intf, config):
    c = "{} set interface {}".format(ovs_vsctl, intf)
    for s in config:
        c = "{} other_config:{}".format(c, s)
    return sw(c, shell='bash')


def verify_intf_lacp_status(sw, intf, verify_values, context=''):
    request = []
    attrs = []
    for attr in verify_values:
        request.append('lacp_status:{}'.format(attr))
        attrs.append(attr)
    result = timed_compare(sw_get_intf_state,
                           (sw, intf, request),
                           verify_compare_complex, verify_values)
    field_vals = result[1]
    for i in range(0, len(attrs)):
        assert field_vals[i] == verify_values[attrs[i]]


# Creating lacp state values
# Default values are with a Lag forming correctly
def create_lacp_state(actor_sync="1", actor_col="1", actor_dist="1",
                      partner_sync="1", partner_col="1", partner_dist="1"):
    verify = {}
    template = '"Activ:1,TmOut:0,Aggr:1,Sync:{},Col:{},Dist:{},Def:0,Exp:0"'
    verify["actor_state"] = template.format(actor_sync, actor_col, actor_dist)
    verify["partner_state"] = template.format(partner_sync, partner_col,
                                              partner_dist)
    return verify


def pre_setup(sw1, sw2):
    lacpd_switch_pre_setup(sw1)
    lacpd_switch_pre_setup(sw2)


def enable_all_intf(sw1, sw2):
    for intf in range(sw_all_intf_start, sw_all_intf_end + 1):
        sw_set_intf_user_config(sw1, intf, ['admin=up'])
        sw_set_intf_user_config(sw2, intf, ['admin=up'])


@fixture(scope="module")
def main_setup(request, topology):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    assert sw1 is not None
    assert sw2 is not None
    sw1("/bin/systemctl stop pmd", shell='bash')
    sw2("/bin/systemctl stop pmd", shell='bash')

    def cleanup():
        sw1("/bin/systemctl start pmd", shell='bash')
        sw2("/bin/systemctl start pmd", shell='bash')

    request.addfinalizer(cleanup)


@fixture()
def setup(topology):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    assert sw1 is not None
    assert sw2 is not None
    pre_setup(sw1, sw2)
    enable_all_intf(sw1, sw2)


def test_lacpd_ct_aggregation_key_lag_created_with_only_one_lag(topology,
                                                                main_setup,
                                                                setup):
    # TOPOLOGY
    # -----------------------
    # Switch 1
    #   lag 100:
    #       Interface 1
    #       Interface 2
    #
    # Switch 2
    #   lag 100:
    #       Interface 1
    #       Interface 2
    # pre_setup()
    # enable_all_intf()
    sw1 = topology.get("sw1")
    assert sw1 is not None
    sw2 = topology.get("sw2")
    assert sw2 is not None
    sw_create_bond(sw1, "lag100", sw_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag100", sw_intf[0:2], lacp_mode="active")
    for intf in sw_intf[0:2]:
        set_intf_other_config(sw1, intf, ['lacp-aggregation-key=100'])
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=100'])
    sleep(30)
    for intf in sw_intf_str[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(),
                                "sw2:{}".format(intf))
    sw1("ovs-vsctl del-port lag100", shell='bash')
    # TOPOLOGY
    # -----------------------
    # Switch 1
    #   lag 200:
    #       Interface 1
    #       Interface 8
    #   lag 100:
    #       Interface 2
    #       Interface 9
    #
    # Switch 2
    #   lag 100:
    #       Interface 1
    #       Interface 2
    sw_create_bond(sw1, "lag200", [sw_intf[0], sw_intf_not_connected[0]],
                   lacp_mode="active")
    set_intf_other_config(sw1, sw_intf[0], ['lacp-aggregation-key=200'])
    set_intf_other_config(sw1, sw_intf_not_connected[0],
                          ['lacp-aggregation-key=200'])
    sw_create_bond(sw1, "lag100", [sw_intf[1], sw_intf_not_connected[1]],
                   lacp_mode="active")
    set_intf_other_config(sw1, sw_intf[1], ['lacp-aggregation-key=100'])
    set_intf_other_config(sw1, sw_intf_not_connected[1],
                          ['lacp-aggregation-key=100'])
    sleep(10)
    verify_intf_lacp_status(sw1,
                            sw_intf[0],
                            create_lacp_state(actor_col="0",
                                              actor_dist="0",
                                              partner_sync="0",
                                              partner_col="0",
                                              partner_dist="0"),
                            "sw1:{}".format(sw_intf_str[0]))
    verify_intf_lacp_status(sw2,
                            sw_intf[0],
                            create_lacp_state(actor_sync="0",
                                              actor_col="0",
                                              actor_dist="0",
                                              partner_col="0",
                                              partner_dist="0"),
                            "sw2:{}".format(sw_intf_str[0]))
    # Cleaning configuration
    sw1("ovs-vsctl del-port lag100", shell='bash')
    sw1("ovs-vsctl del-port lag200", shell='bash')
    sw2("ovs-vsctl del-port lag100", shell='bash')


def test_lacpd_ct_aggregation_key_lag_with_cross_links(topology, main_setup,
                                                       setup):
    # pre_setup()
    # enable_all_intf()
    # TOPOLOGY
    # -----------------------
    # Switch 1
    #   lag 50:
    #       Interface 1
    #       Interface 2
    #       Interface 3
    #       Interface 4
    #
    # Switch 2
    #   lag 50:
    #       Interface 1
    #       Interface 2
    #   lag 60:
    #       Interface 3
    #       Interface 4
    sw1 = topology.get("sw1")
    assert sw1 is not None
    sw2 = topology.get("sw2")
    assert sw2 is not None
    sw_create_bond(sw1, "lag50", sw_intf[0:4], lacp_mode="active")
    sw_create_bond(sw2, "lag50", sw_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag60", sw_intf[2:4], lacp_mode="active")
    for intf in sw_intf[0:4]:
        set_intf_other_config(sw1, intf, ['lacp-aggregation-key=50'])
    for intf in sw_intf[0:2]:
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=50'])
    for intf in sw_intf[2:4]:
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=60'])
    sleep(30)
    for intf in sw_intf_str[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(),
                                "sw2:{}".format(intf))
    for intf in sw_intf_str[2:4]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(actor_sync="0",
                                                  actor_col="0",
                                                  actor_dist="0",
                                                  partner_col="0",
                                                  partner_dist="0"),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(actor_col="0",
                                                  actor_dist="0",
                                                  partner_sync="0",
                                                  partner_col="0",
                                                  partner_dist="0"),
                                "sw2:{}".format(intf))
    # Cleaning the configuration
    sw1("ovs-vsctl del-port lag50", shell='bash')
    sw2("ovs-vsctl del-port lag50", shell='bash')
    sw2("ovs-vsctl del-port lag60", shell='bash')


def test_lacpd_ct_aggregation_key_lag_with_differet_keys(topology,
                                                         main_setup, setup):
    # pre_setup()
    # enable_all_intf()
    # TOPOLOGY
    # -----------------------
    # Switch 1
    #   lag 150:
    #       Interface 5
    #       Interface 1
    #   lag 250:
    #       Interface 6
    #       Interface 2
    #   lag 350:
    #       Interface 7
    #       Interface 3
    #
    # Switch 2
    #   lag 150:
    #       Interface 6
    #       Interface 1
    #   lag 250:
    #       Interface 7
    #       Interface 2
    #   lag 350:
    #       Interface 5
    #       Interface 3
    sw1 = topology.get("sw1")
    assert sw1 is not None
    sw2 = topology.get("sw2")
    assert sw2 is not None
    sw_create_bond(sw1, "lag150", [5, 1], lacp_mode="active")
    sw_create_bond(sw1, "lag250", [6, 2], lacp_mode="active")
    sw_create_bond(sw1, "lag350", [7, 3], lacp_mode="active")
    sw_create_bond(sw2, "lag150", [6, 1], lacp_mode="active")
    sw_create_bond(sw2, "lag250", [7, 2], lacp_mode="active")
    sw_create_bond(sw2, "lag350", [5, 3], lacp_mode="active")
    set_intf_other_config(sw1, 5, ['lacp-aggregation-key=150'])
    set_intf_other_config(sw1, 1, ['lacp-aggregation-key=150'])
    set_intf_other_config(sw2, 6, ['lacp-aggregation-key=150'])
    set_intf_other_config(sw2, 1, ['lacp-aggregation-key=150'])
    set_intf_other_config(sw1, 6, ['lacp-aggregation-key=250'])
    set_intf_other_config(sw1, 2, ['lacp-aggregation-key=250'])
    set_intf_other_config(sw2, 7, ['lacp-aggregation-key=250'])
    set_intf_other_config(sw2, 2, ['lacp-aggregation-key=250'])
    set_intf_other_config(sw1, 7, ['lacp-aggregation-key=350'])
    set_intf_other_config(sw1, 3, ['lacp-aggregation-key=350'])
    set_intf_other_config(sw2, 5, ['lacp-aggregation-key=350'])
    set_intf_other_config(sw2, 3, ['lacp-aggregation-key=350'])
    sleep(30)
    for intf in sw_all_intf[0:3]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(),
                                "sw2:{}".format(intf))
    for intf in sw1_crossed_over_intf_str[0:3]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(),
                                "sw2:{}".format(intf))
    sw1("ovs-vsctl del-port lag150", shell='bash')
    sw1("ovs-vsctl del-port lag250", shell='bash')
    sw1("ovs-vsctl del-port lag350", shell='bash')
    sw2("ovs-vsctl del-port lag150", shell='bash')
    sw2("ovs-vsctl del-port lag250", shell='bash')
    sw2("ovs-vsctl del-port lag350", shell='bash')


def test_lacpd_ct_aggregation_key_lag_with_system_n_port_priority(topology,
                                                                  main_setup,
                                                                  setup):
    # TOPOLOGY
    # -----------------------
    # Switch 1
    #   lag 100:
    #       Interface 1
    #       Interface 2
    #
    # Switch 2
    #   lag 200:
    #       Interface 1
    #       Interface 2
    # pre_setup()
    # enable_all_intf()
    sw1 = topology.get("sw1")
    assert sw1 is not None
    sw2 = topology.get("sw2")
    assert sw2 is not None
    sw_create_bond(sw1, "lag100", sw_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag200", sw_intf[0:2], lacp_mode="active")
    for intf in sw_intf[0:2]:
        set_intf_other_config(sw1, intf, ['lacp-aggregation-key=100'])
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=200'])
    sleep(30)
    for intf in sw_intf_str[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(),
                                "sw2:{}".format(intf))
    sw1("ovs-vsctl del-port lag100", shell='bash')
    sw2("ovs-vsctl del-port lag200", shell='bash')


def test_lacpd_ct_aggregation_key_case5(topology, main_setup, setup):
    # pre_setup()
    # enable_all_intf()
    # TOPOLOGY
    # -----------------------
    # Switch 1 (System Priority 200)
    #   lag 50:
    #       Interface 1 (Port Priority = 100)
    #       Interface 2 (Port Priority = 100)
    #       Interface 3 (Port Priority = 100)
    #       Interface 4 (Port Priority = 100)
    #
    # Switch 2 (System Priority 1)
    #   lag 50:
    #       Interface 1 (Port Priority = 100)
    #       Interface 2 (Port Priority = 100)
    #   lag 60:
    #       Interface 3 (Port Priority = 1)
    #       Interface 4 (Port Priority = 1)
    sw1 = topology.get("sw1")
    assert sw1 is not None
    sw2 = topology.get("sw2")
    assert sw2 is not None
    sw1("ovs-vsctl set system . "
        " lacp_config:lacp-system-priority=200", shell='bash')
    sw2("ovs-vsctl set system . "
        " lacp_config:lacp-system-priority=1", shell='bash')
    sw_create_bond(sw1, "lag50", sw_intf[0:4], lacp_mode="active")
    sw_create_bond(sw2, "lag50", sw_intf[0:2], lacp_mode="active")
    sw_create_bond(sw2, "lag60", sw_intf[2:4], lacp_mode="active")
    for intf in sw_intf[0:4]:
        set_intf_other_config(sw1, intf, ['lacp-aggregation-key=50'])
        set_intf_other_config(sw1, intf, ['lacp-port-priority=100'])
    for intf in sw_intf[0:2]:
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=50'])
        set_intf_other_config(sw2, intf, ['lacp-port-priority=100'])
    for intf in sw_intf[2:4]:
        set_intf_other_config(sw2, intf, ['lacp-aggregation-key=60'])
        set_intf_other_config(sw2, intf, ['lacp-port-priority=1'])
    sleep(30)
    for intf in sw_intf_str[0:2]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(actor_sync="0",
                                                  actor_col="0",
                                                  actor_dist="0",
                                                  partner_col="0",
                                                  partner_dist="0"),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(actor_col="0",
                                                  actor_dist="0",
                                                  partner_sync="0",
                                                  partner_col="0",
                                                  partner_dist="0"),
                                "sw2:{}".format(intf))
    for intf in sw_intf_str[2:4]:
        verify_intf_lacp_status(sw1,
                                intf,
                                create_lacp_state(),
                                "sw1:{}".format(intf))
        verify_intf_lacp_status(sw2,
                                intf,
                                create_lacp_state(),
                                "sw2:{}".format(intf))
    sw1("ovs-vsctl del-port lag50", shell='bash')
    sw2("ovs-vsctl del-port lag50", shell='bash')
    sw2("ovs-vsctl del-port lag60", shell='bash')
