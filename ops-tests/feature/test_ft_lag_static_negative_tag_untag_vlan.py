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

import re

TOPOLOGY = """
#
# +-------+
# |  sw1  |
# +-------+
#

# Nodes
[type=openswitch name="Switch 1"] sw1
"""


def get_interface_vlan(sw1, interface):
    # Recover vlan information from running config from specific VLAN
    # Variables
    overall_buffer = []
    buffer_string = ""
    command = ""

    ##########################################################################
    # Send Command
    ##########################################################################
    command = "show running-config"
    print("Show running config.*****" + command)
    overall_buffer = sw1.libs.vtysh.show_running_config()

    ###########################################################################
    # Exit for context and validet buffer with information
    ###########################################################################

    for cur_line in overall_buffer:
        buffer_string += str(cur_line)

    list_vlans = dict()
    list_vlans_result = list()
    data_interface_lag = re.split(r'' + str(interface), buffer_string)[0]
    list_vlans = re.findall(r'\s{4}(vlan.*)', data_interface_lag, re.MULTILINE)

    for current_vlan in list_vlans:
        vlan_pointer = dict()
        vlan_dist = re.match("vlan\s*(\w*)", current_vlan)
        if vlan_dist.group(1) == "access":
            vlan_temp = re.match("vlan\s*(\w*)\s*(\d*)", current_vlan)
            vlan_pointer['type'] = vlan_temp.group(1)
            vlan_pointer['id'] = vlan_temp.group(2)
        else:
            vlan_temp = re.match("vlan\s*(\w*)\s*(\w*)\s*(\d*)", current_vlan)
            vlan_pointer['type'] = vlan_temp.group(1)
            vlan_pointer['mode'] = vlan_temp.group(2)
            vlan_pointer['id'] = vlan_temp.group(3)

        list_vlans_result.append(vlan_pointer)
    return list_vlans_result


def test_ft_lag_static_negative_tag_untag_vlan(topology, step):
    sw1 = topology.get('sw1')
    lag_id = 100
    vlan_trunk_id = 950
    vlan_access_id = 900
    list_interfaces = ["1", "2", "3", "4"]  # Any interface to join the Lag

    assert sw1 is not None

    ##########################################################################
    # Step 1 - Create Lag
    ##########################################################################

    step("Test Create Lag")
    print("\n###############################################")
    print("# Step 1 - Create Lag ")
    print("###############################################")

    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_shutdown()

    ##########################################################################
    # Step 2 - Create vlans
    ##########################################################################

    step("Test Create Vlan")
    print("\n################################################")
    print("# Step 2 - Create vlans ")
    print("################################################")

    list_vlan = [vlan_access_id, vlan_trunk_id]

    for current_vlan in list_vlan:
        with sw1.libs.vtysh.ConfigVlan(current_vlan) as ctx:
            ctx.no_shutdown()

    ##########################################################################
    # Step 3 - Add ports to the Lag
    ##########################################################################

    step("Test Add Ports Lag")
    print("\n################################################")
    print("# Step 3 - Add ports to the Lag ")
    print("################################################")

    for current_interface in list_interfaces:
        with sw1.libs.vtysh.ConfigInterface(current_interface) as ctx:
            ctx.lag(lag_id)

    #######################################################################
    # Step 4 - Enable Interfaces
    ##########################################################################

    step("Test Enable Interface")
    print("\n###############################################")
    print("# Step 4 - Enable Interfaces ")
    print("###############################################")

    for current_interface in list_interfaces:
        with sw1.libs.vtysh.ConfigInterface(current_interface) as ctx:
            ctx.no_shutdown()

    ##########################################################################
    # Step 5 - Enable vlan access in Lag
    ##########################################################################

    step("Test Enable Vlan Trunk Lag")
    print("\n###############################################")
    print("# Step 5  - Enable vlan trunk in lag ")
    print("###############################################")

    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_routing()
        ctx.vlan_trunk_allowed(vlan_trunk_id)

    ##########################################################################
    # Step 6 - Validated access vlan show in lag 1
    ##########################################################################

    step("Test Validated Trunk Vlan Lag")
    print("\n###############################################")
    print("# Step 6 - Validated access vlan show in Lag ")
    print("###############################################")

    dev_ret_struct = get_interface_vlan(sw1, lag_id)

    if dev_ret_struct is None:
        print("No vlans assigned to the Lag")
    else:
        for current_vlan in dev_ret_struct:
            if current_vlan['type'] == "access":
                print("The vlan was misconfigured in the device")
                assert(False)

    ##########################################################################
    # Step 7 - Validated access vlan show in lag 1
    ##########################################################################

    step("Test Enable Vlan Access Lag")
    print("\n###############################################")
    print("# Step 7 - Enable vlan access in lag ")
    print("###############################################")

    with sw1.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        # ctx.no_routing()
        ctx.vlan_access(vlan_access_id)

    #######################################################################
    # Step 8 - Validated access vlan show in lag 1
    ##########################################################################

    step("Test Validated Access Vlan Lag")
    print("\n###############################################")
    print("# Step 8 - Validated access vlan show in Lag ")
    print("###############################################")

    dev_ret_struct = get_interface_vlan(sw1, lag_id)

    if dev_ret_struct is None:
        print("No vlans assigned to the Lag")
    else:
        for current_vlan in dev_ret_struct:
            if current_vlan['type'] == "trunk" or len(dev_ret_struct) > 1:
                print("The vlan was misconfigured in the device")
                assert(False)
