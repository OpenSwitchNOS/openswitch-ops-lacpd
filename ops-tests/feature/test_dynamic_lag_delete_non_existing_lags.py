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
# Name:        DynamicLagDeleteNonExistingLags.py
#
# Description: Tests that a previously configured dynamic Link Aggregation does
#              not stop forwarding traffic when attempting to delete several
#              non-existent Link Aggregations with different names that may not
#              be supported
#
# Author:      Jose Hernandez
#
# Topology:  |Host| ----- |Switch| ---------------------- |Switch| ----- |Host|
#                                   (Dynamic LAG - 2 links)
#
# Success Criteria:  PASS -> Non-existent LAGs cannot be deleted and they
#                            don't affect the functioning LAG
#
#                    FAILED -> Functioning LAG configuration is changed or any
#                              of the non-existing LAGs don't produce errors
#                              when attempting to delete them
#
###############################################################################

# import pytest
from pytest import raises
from topology_lib_vtysh.exceptions import UnknownCommandException
from topology_lib_vtysh.exceptions import UnknownVtyshException

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
sw1:if02 -- sw2:if01
sw1:if03 -- sw2:if02
sw2:if03 -- h2:if01
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
def createlag(switch, lagid, configure, intarray, mode, switchid):
    if configure:
        with switch.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
            ctx.shutdown()

        addinterfacestolag(switch, 1, intarray)
        if mode != 'off' and switchid == 1:
            with switch.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
                ctx.lacp_mode_active()
        elif mode != 'off' and switchid == 2:
            with switch.libs.vtysh.ConfigInterfaceLag(lagid) as ctx:
                ctx.lacp_mode_passive()

        out = switch.libs.vtysh.show_lacp_aggregates()
        if out == {}:
            return False
        if out['lag1']['name'] != "lag" + str(lagid):
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


# Function to try and delete a non-existent LAG. It assumes there is only
# 1 other LAG and then matches the information present in DUT to verify it
# wasn't modified
def deletelagnegative(
        switch, lagid, goodlagid, goodlagmode, goodlaginterfaces,
        goodlaghash, goodlagfallback, goodlagfastflag):
    with switch.libs.vtysh.Configure() as ctx:
        ctx.no_interface_lag(lagid)

    out = switch.libs.vtysh.show_lacp_aggregates()
    if out['lag1'] == lagid:
        return False
    if out['lag1']['mode'] != goodlagmode:
        return False
    if out['lag1']['hash'] != goodlaghash:
        return False
    if out['lag1']['fallback'] != goodlagfallback:
        return False
    # if out['lag1']['lacpfastflag'] != goodlagfastflag:
    #     return False
    if len(out['lag1']['interfaces']) != len(goodlaginterfaces):
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
def pingbetweenworkstations(host1, host2, ipaddr, success, sw1, sw2):
    print("SHOW RUN SW1")
    sw1("show run")

    print("SHOW RUN SW2")
    sw2("show run")

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

    sw2p1 = sw2.ports['if01']
    sw2p2 = sw2.ports['if02']
    sw2p3 = sw2.ports['if03']

    print("Unconfigure workstations")
    print("Unconfiguring workstation 1")
    finalresult.append(configureworkstation(h1, h1p1, "140.1.1.10", "24",
                                            "140.1.1.255", False))
    print("Unconfiguring workstation 2")
    finalresult.append(configureworkstation(h2, h2p1, "140.1.1.11", "24",
                                            "140.1.1.255", False))

    print("Delete LAGs on DUTs")
    finalresult.append(createlag(sw1, '1', False, [], 'off', 1))
    finalresult.append(createlag(sw2, '1', False, [], 'off', 2))

    print("Disable interfaces on DUTs")
    print("Configuring switch dut01")
    finalresult.append(enabledutinterface(sw1, sw1p1, False))
    finalresult.append(enabledutinterface(sw1, sw1p2, False))
    finalresult.append(enabledutinterface(sw1, sw1p3, False))

    print("Configuring switch dut02")
    finalresult.append(enabledutinterface(sw2, sw2p1, False))
    finalresult.append(enabledutinterface(sw2, sw2p2, False))
    finalresult.append(enabledutinterface(sw2, sw2p3, False))

    print("Remove VLAN from DUTs")
    finalresult.append(configurevlan(sw1, 900, False))
    finalresult.append(configurevlan(sw2, 900, False))


def test_ft_dynamic_lag_delete_non_existing_lags(topology, step):
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

    sw2p1 = sw2.ports['if01']
    sw2p2 = sw2.ports['if02']
    sw2p3 = sw2.ports['if03']

    print("\n############################################")
    step("Create LAGs")
    print("############################################")
    assert(createlag(sw1, '1', True, [sw1p2, sw1p3], 'active', 1))
    assert(createlag(sw2, '1', True, [sw2p1, sw2p2], 'passive', 2))

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
    assert(addinterfacevlan(sw2, 900, True, sw2p3))
    assert(addinterfacevlan(sw2, 900, True, 'lag 1'))

    print("\n############################################")
    step("Enable switches interfaces")
    print("############################################")
    print("Configuring switch dut01")
    assert(enabledutinterface(sw1, sw1p1, True))
    assert(enabledutinterface(sw1, sw1p2, True))
    assert(enabledutinterface(sw1, sw1p3, True))

    print("Configuring switch dut02")
    assert(enabledutinterface(sw2, sw2p1, True))
    assert(enabledutinterface(sw2, sw2p2, True))
    assert(enabledutinterface(sw2, sw2p3, True))

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
    assert(pingbetweenworkstations(h1, h2, "140.1.1.11", True, sw1, sw2))

    print("\n############################################")
    step("Delete non-existent LAGs on both DUTs")
    print("############################################")
    print('Attemtpt to delete LAGs on dut01')
    print('With ID XX')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw1, 'XX', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID 0')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw1, '0', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID -1')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw1, '-1', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID 2000')
    with raises(UnknownVtyshException):
        assert(deletelagnegative(sw1, '2000', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID 2001')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw1, '2001', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID @%&$#()')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw1, '@%&$#()', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID 60000')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw1, '60000', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID 600')
    with raises(UnknownVtyshException):
        assert(deletelagnegative(sw1, '600', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))
    print('With ID 2')
    with raises(UnknownVtyshException):
        assert(deletelagnegative(sw1, '2', '1', 'active', [sw1p2, sw1p3],
                                 'l3-src-dst', False, False))

    print('Attemtpt to delete LAGs on dut01')
    print('With ID XX')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw2, 'xx', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID 0')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw2, '0', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID -1')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw2, '-1', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID 2000')
    with raises(UnknownVtyshException):
        assert(deletelagnegative(sw2, '2000', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID 2001')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw2, '2001', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID @%&$#()')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw2, '@%&$#()', '1', 'passive',
                                 [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID 60000')
    with raises(UnknownCommandException):
        assert(deletelagnegative(sw2, '60000', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID 600')
    with raises(UnknownVtyshException):
        assert(deletelagnegative(sw2, '600', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))
    print('With ID 2')
    with raises(UnknownVtyshException):
        assert(deletelagnegative(sw2, '2', '1', 'passive', [sw2p1, sw2p2],
                                 'l3-src-dst', False, False))

    print("\n############################################")
    step("Test ping between clients work")
    print("############################################")
    assert(pingbetweenworkstations(h1, h2, "140.1.1.11", True, sw1, sw2))

    clean_up_devices(sw1, sw2, h1, h2)
