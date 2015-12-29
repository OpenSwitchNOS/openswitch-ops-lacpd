#!/usr/bin/python
#
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
#

import os
import sys
import time
import subprocess
import pytest

from opsvsi.docker import *
from opsvsi.opsvsitest import *

from lib_test import timed_compare
from lib_test import sw_set_intf_user_config
from lib_test import sw_clear_user_config
from lib_test import sw_set_intf_pm_info
from lib_test import set_port_parameter
from lib_test import sw_get_intf_state
from lib_test import sw_get_port_state
from lib_test import sw_create_bond
from lib_test import verify_compare_value
from lib_test import verify_compare_tuple
from lib_test import verify_compare_tuple_negate
from lib_test import verify_compare_complex
from lib_test import verify_intf_in_bond
from lib_test import verify_intf_not_in_bond
from lib_test import verify_intf_status
from lib_test import verify_intf_field_absent
from lib_test import verify_intf_lacp_status

OVS_VSCTL = "/usr/bin/ovs-vsctl "

# Test case configuration.
DFLT_BRIDGE = "bridge_normal"

# Interfaces from 1-10 are 1G ports.
sw_to_host1 = 21
sw_to_host2 = 22

sw_1G_intf_start = 1
sw_1G_intf_end = 10
n_1G_links = 10
sw_1G_intf = [str(i) for i in irange(sw_1G_intf_start, sw_1G_intf_end)]

# Set open_vsw_lacp_config parameter(s)
def set_open_vsw_lacp_config(sw, config):
    c = OVS_VSCTL + "set system ."
    for s in config:
        c += " lacp_config:" + s
    debug(c)
    return sw.ovscmd(c)

def sys_open_vsw_lacp_config_clear(sw):
    c = OVS_VSCTL + "remove system . lacp_config lacp-system-id " + \
        "lacp_config lacp-system-priority"
    debug(c)
    sw.ovscmd(c)

# Set interface:other_config parameter(s)
def set_intf_other_config(sw, intf, config):
    c = OVS_VSCTL + "set interface " + str(intf)
    for s in config:
        c += ' other_config:%s' % s
    debug(c)
    return sw.ovscmd(c)

# Simulate the link state on an Interface
def simulate_link_state(sw, interface, link_state="up"):
    info("Setting the link state of interface " + interface + " to " + link_state + "\n")
    c = OVS_VSCTL + "set interface " + str(interface) + " link_state=" + link_state
    debug(c)
    return sw.ovscmd(c)

# Delete a bond/lag/trunk from OVS-DB.
def sw_delete_bond(sw, bond_name):
    info("Deleting the bond " + bond_name + "\n")
    c = OVS_VSCTL + "del-port bridge_normal " + bond_name
    debug(c)
    return sw.ovscmd(c)


# Add a new Interface to the existing bond.
def add_intf_to_bond(sw, bond_name, intf_name):

    info("Adding interface " + intf_name + " to LAG " + bond_name + "\n")

    # Get the UUID of the interface that has to be added.
    c = OVS_VSCTL + "get interface " + str(intf_name) + " _uuid"
    debug(c)
    intf_uuid = sw.ovscmd(c).rstrip('\r\n')

    # Get the current list of Interfaces in the bond.
    c = OVS_VSCTL + "get port " + bond_name + " interfaces"
    debug(c)
    out = sw.ovscmd(c)
    intf_list = out.rstrip('\r\n').strip("[]").replace(" ", "").split(',')

    if intf_uuid in intf_list:
        info("Interface " + intf_name + " is already part of " + bond_name + "\n")
        return

    # Add the given intf_name's UUID to existing Interfaces.
    intf_list.append(intf_uuid)

    # Set the new Interface list in the bond.
    new_intf_str = '[' + ",".join(intf_list) + ']'

    c = OVS_VSCTL + "set port " + bond_name + " interfaces=" + new_intf_str
    debug(c)
    return sw.ovscmd(c)


# Add a list of Interfaces to the bond.
def add_intf_list_from_bond(sw, bond_name, intf_list):
    for intf in intf_list:
        add_intf_to_bond(sw, bond_name, intf)


# Remove an Interface from a bond.
def remove_intf_from_bond(sw, bond_name, intf_name, fail=True):

    info("Removing interface " + intf_name + " from LAG " + bond_name + "\n")

    # Get the UUID of the Interface that has to be removed.
    c = OVS_VSCTL + "get interface " + str(intf_name) + " _uuid"
    debug(c)
    intf_uuid = sw.ovscmd(c).rstrip('\r\n')

    # Get the current list of Interfaces in the bond.
    c = OVS_VSCTL + "get port " + bond_name + " interfaces"
    debug(c)
    out = sw.ovscmd(c)
    intf_list = out.rstrip('\r\n').strip("[]").replace(" ", "").split(',')

    if intf_uuid not in intf_list:
        assert fail == True, "Unable to find the interface in the bond"
        return

    # Remove the given intf_name's UUID from the bond's Interfaces.
    new_intf_list = [i for i in intf_list if i != intf_uuid]

    # Set the new Interface list in the bond.
    new_intf_str = '[' + ",".join(new_intf_list) + ']'

    c = OVS_VSCTL + "set port " + bond_name + " interfaces=" + new_intf_str
    debug(c)
    out = sw.ovscmd(c)

    return out

# Remove a list of Interfaces from the bond.
def remove_intf_list_from_bond(sw, bond_name, intf_list):
    for intf in intf_list:
        remove_intf_from_bond(sw, bond_name, intf)

def verify_port_lacp_status(sw, lag, value, msg=''):
    result = timed_compare(sw_get_port_state,
                           (sw, lag, ["lacp_status"]),
                           verify_compare_value, value)
    assert result == (True, value), msg

def lacpd_switch_pre_setup(sw):

    for intf in irange(sw_1G_intf_start, sw_1G_intf_end):
        sw_set_intf_pm_info(sw, intf, ('connector="SFP_RJ45"',
                                       'connector_status=supported',
                                       'max_speed="1000"',
                                       'supported_speeds="1000"'))

# Create a topology with two switches, and 10 ports connected
# to each other.
class myDualSwitchTopo( Topo ):
    """Dual switch topology with ten ports connected to them
       H1[h1-eth0]<--->[1]S1[2-10]<--->[2-10]S2[1]<--->[h2-eth0]H2
    """

    def build(self, hsts=2, sws=2, n_links=10, **_opts):
        self.hsts = hsts
        self.sws = sws

        "Add the hosts to the topology."
        for h in irange(1, hsts):
            host = self.addHost('h%s' % h)

        "Add the switches to the topology."
        for s in irange(1, sws):
            switch = self.addSwitch('s%s' %s)

        "Add the links between the hosts and switches."
        self.addLink('h1', 's1', port1=1, port2=sw_to_host1)
        self.addLink('h2', 's2', port1=1, port2=sw_to_host2)

        "Add the links between the switches."
        for one_g_intf in irange(sw_1G_intf_start, sw_1G_intf_end):
            self.addLink('s1', 's2', port1=one_g_intf, port2=one_g_intf)

class lacp_fallbackTest(OpsVsiTest):

    def setupNet(self):

        # Create a topology with two VsiOpenSwitch switches,
        # and a host connected to each switch.
        host_opts = self.getHostOpts()
        switch_opts = self.getSwitchOpts()
        lacpd_topo = myDualSwitchTopo(sws=2, hopts=host_opts,
                                      sopts=switch_opts)

        self.net = Mininet(lacpd_topo, switch=VsiOpenSwitch,
                           host=Host, link=OpsVsiLink,
                           controller=None, build=True)


    # Simulate valid pluggable modules in all the modules.
    def test_pre_setup(self):
        s1 = self.net.switches[0]
        s2 = self.net.switches[1]

        lacpd_switch_pre_setup(s1)
        lacpd_switch_pre_setup(s2)


    # Clear the user_config of all the Interfaces.
    # Reset the pm_info to default values.
    def test_post_cleanup(self):
        s1 = self.net.switches[0]
        s2 = self.net.switches[1]

        for intf in irange(sw_1G_intf_start, sw_1G_intf_end):
            sw_clear_user_config(s1, intf)
            sw_clear_user_config(s2, intf)
            sw_set_intf_pm_info(s1, intf, ('connector=absent',
                                           'connector_status=unsupported'))
            sw_set_intf_pm_info(s2, intf, ('connector=absent',
                                           'connector_status=unsupported'))


    # Enable all the Interfaces used in the test.
    def enable_all_intf(self):
        s1 = self.net.switches[0]
        s2 = self.net.switches[1]

        for intf in irange(sw_1G_intf_start, sw_1G_intf_end):
            sw_set_intf_user_config(s1, intf, ['admin=up'])
            sw_set_intf_user_config(s2, intf, ['admin=up'])


    def dynamic_lag_config(self):

        info("\n============= lacpd user config"
             " (dynamic LAG) tests =============\n")
        s1 = self.net.switches[0]
        s2 = self.net.switches[1]

        system_mac = {}
        system_mac[1] = s1.ovscmd("ovs-vsctl get system . "
                                  "system_mac").rstrip('\r\n')
        system_mac[2] = s2.ovscmd("ovs-vsctl get system . "
                                  "system_mac").rstrip('\r\n')
        system_prio = {}
        system_prio[1] = "65534"
        system_prio[2] = "65534"

        # Enable all the interfaces under test.
        self.test_pre_setup()

        info("Test base mac address\n")
        for intf in sw_1G_intf[0:2]:
            sw_set_intf_user_config(s1, intf, ['admin=up'])
            sw_set_intf_user_config(s2, intf, ['admin=up'])

        sw_create_bond(s1, "lag0", sw_1G_intf[0:2], lacp_mode="active")
        sw_create_bond(s2, "lag0", sw_1G_intf[0:2], lacp_mode="active")

        for intf in sw_1G_intf[0:2]:
            verify_intf_lacp_status(s1,
                    intf,
                    { "actor_system_id" : system_prio[1] +
                      "," + system_mac[1],
                      "partner_state" :
                      "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                      "Dist:1,Def:0,Exp:0",
                      "partner_system_id" :
                      system_prio[2] + "," + system_mac[2] },
                    "s1:" + intf)

            verify_intf_lacp_status(s2,
                    intf,
                    { "actor_system_id" : system_prio[2] +
                      "," + system_mac[2],
                      "partner_state" :
                      "Activ:1,TmOut:1,Aggr:1,Sync:1,Col:1,"
                      "Dist:1,Def:0,Exp:0",
                      "partner_system_id" :
                      system_prio[1] + "," + system_mac[1] },
                    "s1:" + intf)

        # Test lacp down

        info("\n############### Test Case 1 - Verify lacp negotiation"
             " fails ###############\n")
        info("#######################################################"
             "####################\n")

        # Create two dynamic LAG with two ports each.
        # the current schema doesn't allow creating a bond
        # with less than two ports. Once that is changed
        # we should modify the test case.
        sw_create_bond(s1, "lag0", sw_1G_intf[0:2], lacp_mode="active")
        sw_create_bond(s2, "lag0", sw_1G_intf[0:2], lacp_mode="active")

        set_port_parameter(s1, "lag0", ['other_config:lacp-time=fast'])
        set_port_parameter(s2, "lag0", ['other_config:lacp-time=fast'])

        # Enable both the interfaces.
        for intf in sw_1G_intf[0:2]:
            sw_set_intf_user_config(s1, intf, ['admin=up'])
            sw_set_intf_user_config(s2, intf, ['admin=up'])

        # Verify that all the interfaces are linked up
        for intf in sw_1G_intf[0:2]:
            verify_intf_status(s1, intf, "link_state", "up")
            verify_intf_status(s2, intf, "link_state", "up")
            verify_intf_status(s1, intf, "link_speed", "1000000000")
            verify_intf_status(s2, intf, "link_speed", "1000000000")

        for intf in sw_1G_intf[0:2]:
            verify_intf_in_bond(s1, intf, "Interfaces are expected to be "
                                          "part of dynamic LAG when "
                                          "both the switches are in "
                                          "active mode on switch1")
            verify_intf_in_bond(s2, intf, "Interfaces are expected to be "
                                          "part of dynamic LAG when "
                                          "both the switches are in "
                                          "active mode on switch1")

        # Set lacp to "off"
        set_port_parameter(s1, "lag0" , [ 'lacp=off'])

        verify_intf_field_absent(s1, intf, 'lacp_status:actor_state',
                                 "lacp status should be empty")

        info("lacp fallback true \n")
        set_port_parameter(s1, "lag0", ['other_config:lacp-fallback=true'])
        set_port_parameter(s2, "lag0", ['other_config:lacp-fallback=true'])

        info("Verify interface lacp_status\n")
        # interfaces must be down due to lacp = off
        for intf in sw_1G_intf[0:2]:
            if intf == "1":
                info("Verifying interface 1 is up \n")
                verify_intf_in_bond(s2, intf, "One Interface must be up")
            if intf != "1":
                info("Verifying rest of interfaces are down \n")
                verify_intf_not_in_bond(s2, intf,
                                        "Rest of interfaces must be down")

        # Set lacp to "active"
        info("\n############# LACP back to active \n")
        set_port_parameter(s1, "lag0" , [ 'lacp=active'])

        info("Verify interface lacp_status\n")
        # interfaces must be up when lacp is back to active
        for intf in sw_1G_intf[0:2]:
            info("Verifying all interfaces are up \n")
            verify_intf_in_bond(s2, intf, "All Interfaces must be up")

        info("lacp fallback false \n\n")
        set_port_parameter(s1, "lag0", ['other_config:lacp-fallback=false'])
        set_port_parameter(s2, "lag0", ['other_config:lacp-fallback=false'])

        # Set lacp to "off"
        set_port_parameter(s1, "lag0" , [ 'lacp=off'])

        time.sleep(4)

        info("############# Verify interface lacp_status ############# \n")
        info("############  LACP off and fallback = false ############ \n")
        # interfaces must be down due to lacp = off
        for intf in sw_1G_intf[0:2]:
            info("Verifying all interfaces are down \n")
            verify_intf_not_in_bond(s2, intf,
                                    "All interfaces must be down")

class Test_lacpd:

    def setup(self):
        pass

    def teardown(self):
        pass

    def setup_class(cls):
        # Create the Mininet topology based on Mininet.
        Test_lacpd.test = lacp_fallbackTest()

        # Stop PMD. This tests manually sets lot of DB elements
        # that 'pmd' is responsible for. To avoid any cross
        # interaction disable 'pmd'
        Test_lacpd.test.net.switches[0].cmd("/bin/systemctl stop pmd")
        Test_lacpd.test.net.switches[1].cmd("/bin/systemctl stop pmd")

    def teardown_class(cls):
        Test_lacpd.test.net.switches[0].cmd("/bin/systemctl start pmd")
        Test_lacpd.test.net.switches[1].cmd("/bin/systemctl start pmd")

        # Stop the Docker containers, and
        # mininet topology
        Test_lacpd.test.net.stop()

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def __del__(self):
        del self.test

    # Set fallback(lacp) daemon tests.

    def test_lacpd_dynamic_lag_config(self):
        self.test.dynamic_lag_config()
    #   CLI(self.test.net)