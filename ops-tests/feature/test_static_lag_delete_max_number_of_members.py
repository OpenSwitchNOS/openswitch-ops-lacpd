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
# Name:        StaticLagDeleteMaxNumberOfMembers.py
#
# Description: Tests that a previously configured static Link Aggregation of 8
#              members can be deleted
#
# Author:      Jose Hernandez
#
# Topology:  |Host| ----- |Switch| ---------------------- |Switch| ----- |Host|
#                                   (Static LAG - 8 links)
#
# Success Criteria:  PASS -> LAGs are deleted when having 8 members
#
#                    FAILED -> LAGs cannot be deleted in the scenario
#                              mentioned in the pass criteria
#
###############################################################################

TOPOLOGY = """
#
# +-------+                                +-------+
# |       |     +-------+<-->+-------+     |       |
# |  hs1  <----->  sw1  |    |  sw2  <----->  hs3  |
# |       |     +-------+<-->+-------+     |       |
# +-------+                                +-------+
#

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2
[type=host name="host 1"] h1
[type=host name="host 2"] h2

# Links
sw1:if01 -- h1:if01
sw1:if02 -- sw2:if02
sw1:if03 -- sw2:if03
sw1:if04 -- sw2:if04
sw1:if05 -- sw2:if05
sw1:if06 -- sw2:if06
sw1:if07 -- sw2:if07
sw1:if08 -- sw2:if08
sw1:if09 -- sw2:if09
sw2:if01 -- h2:if01
"""


# Adds interfaces to LAG
def addinterfacestolag(switch, lagid, intarray):
    # Add interfaces
    for i in intarray:
        with switch.libs.vtysh.ConfigInterface(i) as ctx:
            ctx.lag(lagid)


# Enable/disable routing on interfaces so VLANs can be configured
def enableinterfacerouting(switch, interface, enable):
    # enter interface
    with switch.libs.vtysh.ConfigInterface(interface) as ctx:
        if enable:
            # configure interface
            ctx.routing()
        else:
            # configure interface
            ctx.no_routing()


# Enable/disable interface on DUT
def enabledutinterface(switch, interface, enable):
    if enable:
        with switch.libs.vtysh.ConfigInterface(interface) as ctx:
            ctx.no_shutdown()
    else:
        with switch.libs.vtysh.ConfigInterface(interface) as ctx:
            ctx.shutdown()
    return True


# Create/delete a LAG and add interfaces
def createlag(switch, lagid, configure, intarray, mode):
    if configure:
        with switch.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
            ctx.shutdown()

        addinterfacestolag(switch, 1, intarray)
        if mode != 'off':
            with switch.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
                ctx.lacp_mode_active()

        out = switch.libs.vtysh.show_lacp_aggregates()
        if out == {}:
            return False
        if len(out['lag1']['interfaces']) != len(intarray):
            return False
        if out['lag1']['mode'] != mode:
            return False
    else:
        with switch.libs.vtysh.Configure() as ctx:
            ctx.no_interface_lag(lagid)

        out = switch.libs.vtysh.show_lacp_aggregates()
        if out != {}:
            return False
    return True


# Add VLAN to interface
def addinterfacevlan(switch, vlanid, enable, interface):
    if enable:
        enableinterfacerouting(switch, interface, False)
        with switch.libs.vtysh.ConfigInterface(interface) as ctx:
            ctx.vlan_access(vlanid)
    else:
        with switch.libs.vtysh.ConfigInterface(interface) as ctx:
            ctx.no_vlan_access(vlanid)

        enableinterfacerouting(switch, interface, True)
    return True


# Configure/delete VLAN on switch
def configurevlan(switch, vlanid, enable):
    if enable:
        with switch.libs.vtysh.ConfigVlan(vlanid) as ctx:
            ctx.no_shutdown()
    else:
        with switch.libs.vtysh.Configure() as ctx:
            ctx.no_vlan(vlanid)
    return True


# Configure/unconfigure the IP address of a workstation
def configureworkstation(host, interface, ipaddr, netmask, broadcast, enable):
    if enable:
        host.libs.ip.interface("if01", addr="%s/%s" % (ipaddr, netmask),
                               up=True)
        cmdout = host("ifconfig {interface}".format(**locals()))
    else:
        host.libs.ip.remove_ip("if01", "%s/%s" % (ipaddr, netmask))
        cmdout = host("ifconfig {interface}".format(**locals()))
    return True


# Ping between workstation
def pingbetweenworkstations(host1, host2, ipaddr, success):
    if success:
        host1.libs.ping.ping(10, ipaddr)
    else:
        host1.libs.ping.ping(10, ipaddr)
    return True


# Clean up devices
def clean_up_devices(sw1, sw2, h1, h2):
    print("\n############################################")
    print("Device Cleanup - rolling back config")
    print("############################################")
    finalresult = []
    h1p1 = h1.ports['if01']
    h2p1 = h2.ports['if01']

    sw1p1 = sw1.ports['if01']
    sw1p2 = sw1.ports['if02']
    sw1p3 = sw1.ports['if03']
    sw1p4 = sw1.ports['if04']
    sw1p5 = sw1.ports['if05']
    sw1p6 = sw1.ports['if06']
    sw1p7 = sw1.ports['if07']
    sw1p8 = sw1.ports['if08']
    sw1p9 = sw1.ports['if09']

    sw2p1 = sw2.ports['if01']
    sw2p2 = sw2.ports['if02']
    sw2p3 = sw2.ports['if03']
    sw2p4 = sw2.ports['if04']
    sw2p5 = sw2.ports['if05']
    sw2p6 = sw2.ports['if06']
    sw2p7 = sw2.ports['if07']
    sw2p8 = sw2.ports['if08']
    sw2p9 = sw2.ports['if09']

    print("Unconfigure workstations")
    print("Unconfiguring workstation 1")
    finalresult.append(configureworkstation(h1, h1p1, "140.1.1.10", "24",
                                            "140.1.1.255", False))

    print("Unconfiguring workstation 2")
    finalresult.append(configureworkstation(h2, h2p1, "140.1.1.11", "24",
                                            "140.1.1.255", False))

    print("Disable interfaces on DUTs")
    print("Configuring switch dut01")
    finalresult.append(enabledutinterface(sw1, sw1p1, False))
    finalresult.append(enabledutinterface(sw1, sw1p2, False))
    finalresult.append(enabledutinterface(sw1, sw1p3, False))
    finalresult.append(enabledutinterface(sw1, sw1p4, False))
    finalresult.append(enabledutinterface(sw1, sw1p5, False))
    finalresult.append(enabledutinterface(sw1, sw1p6, False))
    finalresult.append(enabledutinterface(sw1, sw1p7, False))
    finalresult.append(enabledutinterface(sw1, sw1p8, False))
    finalresult.append(enabledutinterface(sw1, sw1p9, False))

    print("Configuring switch dut02")
    finalresult.append(enabledutinterface(sw2, sw2p1, False))
    finalresult.append(enabledutinterface(sw2, sw2p2, False))
    finalresult.append(enabledutinterface(sw2, sw2p3, False))
    finalresult.append(enabledutinterface(sw2, sw2p4, False))
    finalresult.append(enabledutinterface(sw2, sw2p5, False))
    finalresult.append(enabledutinterface(sw2, sw2p6, False))
    finalresult.append(enabledutinterface(sw2, sw2p7, False))
    finalresult.append(enabledutinterface(sw2, sw2p8, False))
    finalresult.append(enabledutinterface(sw2, sw2p9, False))

    print("Remove VLAN from DUTs")
    finalresult.append(configurevlan(sw1, 900, False))
    finalresult.append(configurevlan(sw2, 900, False))


def test_ft_static_lag_delete_max_number_of_members(topology, step):
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')
    h1 = topology.get('h1')
    h2 = topology.get('h2')

    assert sw1 is not None
    assert sw2 is not None
    assert h1 is not None
    assert h2 is not None

    h1p1 = h1.ports['if01']
    h2p1 = h2.ports['if01']

    sw1p1 = sw1.ports['if01']
    sw1p2 = sw1.ports['if02']
    sw1p3 = sw1.ports['if03']
    sw1p4 = sw1.ports['if04']
    sw1p5 = sw1.ports['if05']
    sw1p6 = sw1.ports['if06']
    sw1p7 = sw1.ports['if07']
    sw1p8 = sw1.ports['if08']
    sw1p9 = sw1.ports['if09']

    sw2p1 = sw2.ports['if01']
    sw2p2 = sw2.ports['if02']
    sw2p3 = sw2.ports['if03']
    sw2p4 = sw2.ports['if04']
    sw2p5 = sw2.ports['if05']
    sw2p6 = sw2.ports['if06']
    sw2p7 = sw2.ports['if07']
    sw2p8 = sw2.ports['if08']
    sw2p9 = sw2.ports['if09']

    print("\n############################################")
    step("Create LAGs")
    print("############################################")
    assert(createlag(sw1, '1', True, [sw1p2, sw1p3, sw1p4, sw1p5, sw1p6,
                     sw1p7, sw1p8, sw1p9], 'off'))
    assert(createlag(sw2, '1', True, [sw2p2, sw2p3, sw2p4, sw2p5, sw2p6,
                     sw2p7, sw2p8, sw2p9], 'off'))

    print("\n############################################")
    step("Configure VLANs on switches")
    print("############################################")
    # Switch 1
    print("Configure VLAN on dut01")
    assert(configurevlan(sw1, 900, True))
    assert(addinterfacevlan(sw1, 900, True, sw1p1))
    assert(addinterfacevlan(sw1, 900, True, 'lag 1'))
    print("Configure VLAN on dut02")
    assert(configurevlan(sw2, 900, True))
    assert(addinterfacevlan(sw2, 900, True, sw2p1))
    assert(addinterfacevlan(sw2, 900, True, 'lag 1'))

    print("\n############################################")
    step("Enable switches interfaces")
    print("############################################")
    print("Configuring switch dut01")
    assert(enabledutinterface(sw1, sw1p1, True))
    assert(enabledutinterface(sw1, sw1p2, True))
    assert(enabledutinterface(sw1, sw1p3, True))
    assert(enabledutinterface(sw1, sw1p4, True))
    assert(enabledutinterface(sw1, sw1p5, True))
    assert(enabledutinterface(sw1, sw1p6, True))
    assert(enabledutinterface(sw1, sw1p7, True))
    assert(enabledutinterface(sw1, sw1p8, True))
    assert(enabledutinterface(sw1, sw1p9, True))

    print("Configuring switch dut02")
    assert(enabledutinterface(sw2, sw2p1, True))
    assert(enabledutinterface(sw2, sw2p2, True))
    assert(enabledutinterface(sw2, sw2p3, True))
    assert(enabledutinterface(sw2, sw2p4, True))
    assert(enabledutinterface(sw2, sw2p5, True))
    assert(enabledutinterface(sw2, sw2p6, True))
    assert(enabledutinterface(sw2, sw2p7, True))
    assert(enabledutinterface(sw2, sw2p8, True))
    assert(enabledutinterface(sw2, sw2p9, True))

    print("\n############################################")
    step("Configure workstations")
    print("############################################")
    print("Configuring workstation 1")
    assert(configureworkstation(h1, h1p1, "140.1.1.10", "24",
                                "140.1.1.255", True))
    print("Configuring workstation 2")
    assert(configureworkstation(h2, h2p1, "140.1.1.11", "24",
                                "140.1.1.255", True))

    print("\n############################################")
    step("Test ping between clients work")
    print("############################################")
    assert(pingbetweenworkstations(h1, h2, "140.1.1.11", True))

    print("\n############################################")
    step("Delete LAGs")
    print("############################################")
    assert(createlag(sw1, '1', False, [], None))
    assert(createlag(sw2, '1', False, [], None))

    print("\n############################################")
    step("Test ping between clients does not work")
    print("############################################")
    assert(pingbetweenworkstations(h1, h2, "140.1.1.11", False))

    clean_up_devices(sw1, sw2, h1, h2)
