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


TOPOLOGY = """
# +-------+
# |  sw1  |
# +-------+

# Nodes
[type=openswitch name="Switch 1"] sw1
"""


ovs_vsctl_get_ip_cmd = "/usr/bin/ovs-vsctl get port {} ip4_address"
ovs_vsctl_get_ipv6_cmd = "/usr/bin/ovs-vsctl get port {} ip6_address"

first_interface = 'lag 100'
second_interface = 'lag 200'
third_interface = 'lag 300'


def vrf_add_delete(sw1, step):
    '''
        Test VRF add and delete validations
    '''
    step("VRF add/delete validations")
    # OPS_TODO: When multiple VRF support is added, change the script
    # to include required validations.
    sw1("configure terminal")
    # Checking VRF name more than 32 characters
    ret = sw1('vrf thisisavrfnamewhichismorethan32characters')
    assert 'Non-default VRFs not supported' in ret
    step('VRF name validation passed')
    # Adding another VRF
    ret = sw1('vrf thisisavrfnamewhichisexactly32c')
    assert 'Non-default VRFs not supported' in ret
    step('VRF add validation passed')
    # Adding default VRF
    ret = sw1('vrf vrf_default')
    assert 'Default VRF already exists.' in ret
    step('Default VRF add validation passed')
    # Deleting default VRF
    ret = sw1('no vrf vrf_default')
    assert 'Cannot delete default VRF.' in ret
    step('VRF delete validation passed')
    # Deleting VRF which does not exist
    ret = sw1('no vrf abcd')
    assert 'Non-default VRFs not supported' in ret
    step('VRF lookup validation passed')
    # Cleanup
    sw1('end')


def no_internal_vlan(sw1, step):
    '''
        Test LAG status for up/no internal vlan
    '''
    step("LAG status up/no_internal_vlan validations")
    # Configurig vlan range for a single vlan
    sw1("configure terminal")
    sw1("vlan internal range 1024 1026 ascending")
    sw1('interface {}'.format(first_interface))
    sw1('no routing')
    sw1('exit')
    sw1('interface {}'.format(second_interface))
    sw1('no routing')
    sw1('exit')
    sw1('interface {}'.format(third_interface))
    sw1('ip address 11.1.1.1/8')
    sw1('end')
    # Checking to see if up and no_internal_vlan cases are handled
    ret = sw1('show vlan internal')
    ret = ret.replace(' ', '')
    expected_output = '\t{}'.format(first_interface)
    assert expected_output not in ret


def lag_ip_verification(sw1, step):
    '''
        Test configuration of IP address for port
    '''
    step("Assign/remove IP address to/from interface")
    # Adding IP address to L2 interface
    sw1('configure terminal')
    sw1('interface {}'.format(first_interface))
    ret = sw1('ip address 10.0.20.2/24')
    expected_output = 'Interface lag100 is not L3.'
    assert expected_output in ret
    # Deleting IP address on an L3 interface which does not
    # have any IP address
    sw1('routing')
    ret = sw1('no ip address 10.0.30.2/24')
    expected_output = 'No IP address \
configured on interface {}'.format(first_interface)
    assert expected_output in ret
    # Configuring IP address on L3 interface
    sw1('ip address 10.0.20.2/24')
    # intf_cmd = OVS_VSCTL + 'get port ' + first_interface \
    #     + ' ip4_address'
    # ip = sw1(intf_cmd).strip()
    ip = sw1(ovs_vsctl_get_ip_cmd.format(first_interface), shell='bash')
    assert ip is '10.0.20.2/24'
    # Updating IP address on L3 interface
    sw1('ip address 10.0.20.3/24')
    # intf_cmd = OVS_VSCTL+ 'get port ' + first_interface \
    #     + ' ip4_address'
    # ip = sw1(intf_cmd).strip()
    ip = sw1(ovs_vsctl_get_ip_cmd.format(first_interface), shell='bash')
    assert ip is '10.0.20.3/24'
    # Remove IP address on L3 interface by giving an IP address
    # that is not present
    sw1("no ip address 10.0.20.4/24 secondary")
    ret = sw1("no ip address 10.0.30.2/24")
    assert "IP address 10.0.30.2/24 not found." in ret
    # Remove IP address from L3 interface by giving correct IP address
    ret = sw1("no ip address 10.0.20.3/24")
    # intf_cmd = OVS_VSCTL + "get port " + first_interface \
    #            + " ip4_address"
    # ip = sw1(intf_cmd).strip()
    ip = sw1(ovs_vsctl_get_ip_cmd.format(first_interface), shell='bash')
    assert ip is '[]'
    sw1('end')


def lag_ipv6_verification(sw1, step):
    '''
        Test configuration of IPv6 address for port
    '''
    step("Assign/remove IPv6 address to/from interface")
    # Adding IPv6 address to L2 interface
    sw1('configure terminal')
    sw1('interface {}'.format(first_interface))
    ret = sw1('ipv6 address 2002::1/128')
    expected_output = 'Interface lag100 is not L3.'
    assert expected_output in ret
    # Deleting IPv6 address on an L3 interface which does
    # not have any IPv6 address
    sw1('routing')
    ret = sw1('no ipv6 address 2002::1/128')
    expected_output = 'No IPv6 address configured on interface {} \
'.format(first_interface)
    assert expected_output in ret
    # Configuring IPv6 address on L3 interface
    sw1('ipv6 address 2002::1/128')
    # intf_cmd = OVS_VSCTL + 'get port ' + first_interface \
    #     + ' ip6_address'
    # ipv6 = sw1(intf_cmd).strip()
    ipv6 = sw1(ovs_vsctl_get_ipv6_cmd.format(first_interface), shell='bash')
    assert ipv6 is '2002::1/128'
    # Updating IPv6 address on L3 interface
    sw1('ipv6 address 2001::1/128')
    # intf_cmd = OVS_VSCTL + 'get port ' + first_interface \
    #     + ' ip6_address'
    # ipv6 = sw1(intf_cmd).strip()
    ipv6 = sw1(ovs_vsctl_get_ipv6_cmd.format(first_interface), shell='bash')
    assert ipv6 is '2001::1/128'
    # Remove IPv6 address from L3 interface by giving correct IP address
    ret = sw1("no ipv6 address 2001::1/128")
    # intf_cmd = OVS_VSCTL + "get port " + first_interface \
    #            + " ip4_address"
    # ip = sw1(intf_cmd).strip()
    ip = sw1(ovs_vsctl_get_ip_cmd.format(first_interface), shell='bash')
    assert ip is '[]'
    # Cleanup
    sw1('end')


def toggle_l2_l3(sw1, step):
    '''
        Test routing / no routing commands for port
    '''
    step("Testing routing/ no routing working")
    sw1('configure terminal')
    sw1('interface {}'.format(first_interface))
    sw1("routing")
    sw1("ipv6 address 2002::1/128")
    sw1("ip address 10.1.1.1/8")
    ret = sw1("do show vrf")
    expected_output = '\tlag100'
    assert expected_output in ret
    # Making L3 interface as L2
    sw1('no routing')
    ret = sw1('do show vrf')
    expected_output = '\tlag100'
    assert expected_output not in ret
    # intf_cmd = OVS_VSCTL + 'get port ' + first_interface \
    #     + ' ip4_address'
    # ip = sw1(intf_cmd).strip()
    ip = sw1(ovs_vsctl_get_ip_cmd.format(first_interface))
    assert ip is '[]'
    # Checking if IPv6 address removed
    # intf_cmd = OVS_VSCTL + 'get port ' + first_interface \
    #     + ' ip6_address'
    # ipv6 = sw1(intf_cmd).strip()
    ipv6 = sw1(ovs_vsctl_get_ipv6_cmd.format(first_interface))
    assert ipv6 is '[]'
    # Checking if no routing worked
    ret = sw1('ip address 10.1.1.1/8')
    expected_output = 'Interface lag100 is not L3.'
    assert expected_output in ret
    # Cleanup
    sw1('end')


def test_lacpd_ct_lag_l3_l2(topology, step):
    sw1 = topology.get("sw1")
    assert sw1 is not None
    vrf_add_delete(sw1, step)
    no_internal_vlan(sw1, step)
    lag_ip_verification(sw1, step)
    lag_ipv6_verification(sw1, step)
    toggle_l2_l3(sw1, step)
