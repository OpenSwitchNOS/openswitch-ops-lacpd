# -*- coding: utf-8 -*-
# (C) Copyright 2015 Hewlett Packard Enterprise Development LP
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
###############################################################################
#
# No description or steps defined on original test case.
# Ported by:   Mauricio Fonseca
# Condition to pass -> Both duts are able to enable lldp and see each other as
#                      as neighbors. Both duts disable lldp and are capable to
#                      to unconfigure properly
#              fail -> Not able to enable lldp and see its neighbor. Not able
#                      to disable and unconfigure lldp properly
#
###############################################################################

"""
OpenSwitch Test for vlan related configurations.
"""

# from pytest import mark
from time import sleep

TOPOLOGY = """
# +------+     +-------+     +--------+     +-------+
# |  hs1 <----->  ops1  <----->  ops2 <----->  hs3  |
# +------+     +--- ---+     +---- ---+     +-------+
#                  |              |
#                  |              |
#              +--- ---+      +--- ---+
#              |  hs2  |      |  hs4  |
#              +-------+      +-------+

# Nodes
[type=openswitch name="OpenSwitch 1"] ops1
[type=openswitch name="OpenSwitch 2"] ops2
[type=host name="Host 1"] hs1
[type=host name="Host 2"] hs2
[type=host name="Host 3"] hs3
[type=host name="Host 4"] hs4

# Links
ops1:IF01 -- ops2:IF01
ops1:IF02 -- ops2:IF02
ops1:IF03 -- hs1:IF01
ops1:IF04 -- hs2:IF01
ops2:IF03 -- hs3:IF01
ops2:IF04 -- hs4:IF01
"""


# @mark.test_id(15308)
def test_ft_lag_dynamic_tagged_vlans(topology):
    # Test variables
    lagid = 100
    l2ipaddress = ["10.2.2.100", "10.2.2.101", "10.2.2.102", "10.2.2.103"]
    vlanl2id = ["900", "950"]

    ops1 = topology.get('ops1')
    ops2 = topology.get('ops2')
    hs1 = topology.get('hs1')
    hs2 = topology.get('hs2')
    hs3 = topology.get('hs3')
    hs4 = topology.get('hs4')

    assert ops1 is not None
    assert ops2 is not None
    assert hs1 is not None
    assert hs2 is not None
    assert hs3 is not None
    assert hs4 is not None

    print("Step 1- Configure, enable lag in switch 1 and switch 2")
    with ops1.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
        ctx.lacp_mode_active()
    with ops2.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
        ctx.lacp_mode_active()

    print("Step 2- Configure vlan in switch 1 and switch 2")
    for vlan in vlanl2id:
        with ops1.libs.vtysh.ConfigVlan(vlan) as ctx:
            ctx.no_shutdown()
        with ops2.libs.vtysh.ConfigVlan(vlan) as ctx:
            ctx.no_shutdown()

    print("Step 3- Configure vlan in interface switch 1 and switch 2")
    with ops1.libs.vtysh.ConfigInterface("IF03") as ctx:
        ctx.no_routing()
        ctx.vlan_access(vlanl2id[0])
    with ops1.libs.vtysh.ConfigInterface("IF04") as ctx:
        ctx.no_routing()
        ctx.vlan_access(vlanl2id[1])
    with ops2.libs.vtysh.ConfigInterface("IF03") as ctx:
        ctx.no_routing()
        ctx.vlan_access(vlanl2id[0])
    with ops2.libs.vtysh.ConfigInterface("IF04") as ctx:
        ctx.no_routing()
        ctx.vlan_access(vlanl2id[1])
    with ops1.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
        ctx.no_routing()
        for vlan in vlanl2id:
            ctx.vlan_trunk_allowed(vlan)
    with ops2.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
        ctx.no_routing()
        for vlan in vlanl2id:
            ctx.vlan_trunk_allowed(vlan)

    print("Step 4- Configure lagId in interface switch 1 and switch 2")
    with ops1.libs.vtysh.ConfigInterface("IF01") as ctx:
        # ctx.no_routing()
        ctx.lag(lagid)
    with ops1.libs.vtysh.ConfigInterface("IF02") as ctx:
        # ctx.no_routing()
        ctx.lag(lagid)
    with ops2.libs.vtysh.ConfigInterface("IF01") as ctx:
        # ctx.no_routing()
        ctx.lag(lagid)
    with ops2.libs.vtysh.ConfigInterface("IF02") as ctx:
        # ctx.no_routing()
        ctx.lag(lagid)

    print("Step 5- Configure workstations")
    hs1.libs.ip.interface('IF01', addr=l2ipaddress[0] + "/24", up=True)
    hs2.libs.ip.interface('IF01', addr=l2ipaddress[1] + "/24", up=True)
    hs3.libs.ip.interface('IF01', addr=l2ipaddress[2] + "/24", up=True)
    hs4.libs.ip.interface('IF01', addr=l2ipaddress[3] + "/24", up=True)

    print("Step 6- Enable all switch 1 and switch 2 interfaces")
    with ops1.libs.vtysh.ConfigInterface('IF01') as ctx:
        ctx.no_shutdown()
    with ops1.libs.vtysh.ConfigInterface('IF02') as ctx:
        ctx.no_shutdown()
    with ops1.libs.vtysh.ConfigInterface('IF03') as ctx:
        ctx.no_shutdown()
    with ops1.libs.vtysh.ConfigInterface('IF04') as ctx:
        ctx.no_shutdown()
    with ops2.libs.vtysh.ConfigInterface('IF01') as ctx:
        ctx.no_shutdown()
    with ops2.libs.vtysh.ConfigInterface('IF02') as ctx:
        ctx.no_shutdown()
    with ops2.libs.vtysh.ConfigInterface('IF03') as ctx:
        ctx.no_shutdown()
    with ops2.libs.vtysh.ConfigInterface('IF04') as ctx:
        ctx.no_shutdown()

    sleep(5)

    print("Step 7- Send traffic between clients")

    ping = hs1.libs.ping.ping(5, l2ipaddress[2])
    print("Packets sent:\t" + str(ping['transmitted']))
    print("Packets received:\t" + str(ping['received']))
    print("Packets loss:\t" + str(ping['errors']))
    assert ping['errors'] == 0

    ping = hs1.libs.ping.ping(5, l2ipaddress[3])
    print("Packets sent:\t" + str(ping['transmitted']))
    print("Packets received:\t" + str(ping['received']))
    print("Packets loss:\t" + str(ping['errors']))

    ping = hs2.libs.ping.ping(5, l2ipaddress[3])
    print("Packets sent:\t" + str(ping['transmitted']))
    print("Packets received:\t" + str(ping['received']))
    print("Packets loss:\t" + str(ping['errors']))
    assert ping['errors'] == 0

    ping = hs2.libs.ping.ping(5, l2ipaddress[2])
    print("Packets sent:\t" + str(ping['transmitted']))
    print("Packets received:\t" + str(ping['received']))
    print("Packets loss:\t" + str(ping['errors']))
