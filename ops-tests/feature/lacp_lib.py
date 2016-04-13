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

##########################################################################
# Name:        lacp_lib.py
#
# Objective:   Library for all utils function used across all LACP tests
#
# Topology:    N/A
#
##########################################################################

"""
OpenSwitch Test Library for LACP
"""

# from pytest import set_trace
import re
import time

APPCTL_LOCAL_STATE = 'actor_oper_port_state'
APPCTL_REMOTE_STATE = 'partner_oper_port_state'
LOCAL_STATE = 'local_state'
REMOTE_STATE = 'remote_state'
ACTOR = 'Actor'
PARTNER = 'Partner'
LACP_PROTOCOL = '0x8809'
LACP_MAC_HEADER = '01:80:c2:00:00:02'


def create_lag_active(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_mode_active()


def create_lag_passive(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_mode_passive()


def lag_no_routing(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_routing()


def create_lag(sw, lag_id, lag_mode):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        if(lag_mode == 'active'):
            ctx.lacp_mode_active()
        elif(lag_mode == 'passive'):
            ctx.lacp_mode_passive()
        elif(lag_mode == 'off'):
            ctx.routing()
        else:
            assert False, 'Invalid mode %s for LAG' % (lag_mode)
    lag_name = "lag" + lag_id
    output = sw.libs.vtysh.show_lacp_aggregates(lag_name)
    assert lag_mode == output[lag_name]['mode'],\
        "Unable to create and validate LAG"


def delete_lag(sw, lag_id):
    with sw.libs.vtysh.Configure() as ctx:
        ctx.no_interface_lag(lag_id)


def associate_interface_to_lag(sw, interface, lag_id):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.lag(lag_id)
    lag_name = "lag" + lag_id
    output = sw.libs.vtysh.show_lacp_aggregates(lag_name)
    assert interface in output[lag_name]['interfaces'],\
        "Unable to associate interface to lag"


def remove_interface_from_lag(sw, interface, lag_id):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.no_lag(lag_id)
    lag_name = "lag" + lag_id
    output = sw.libs.vtysh.show_lacp_aggregates(lag_name)
    assert interface not in output[lag_name]['interfaces'],\
        "Unable to remove interface from lag"


def disassociate_interface_to_lag(sw, interface, lag_id):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.no_lag(lag_id)


def associate_vlan_to_lag(sw, vlan_id, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_routing()
        ctx.vlan_access(vlan_id)
    output = sw.libs.vtysh.show_vlan(vlan_id)
    lag_name = 'lag' + lag_id
    assert lag_name in output[vlan_id]['ports'],\
        "Vlan was not properly associated to lag"


def turn_on_interface(sw, interface):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.no_shutdown()


def turn_off_interface(sw, interface):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.shutdown()


def validate_turn_on_interfaces(sw, interfaces):
    for intf in interfaces:
        output = sw.libs.vtysh.show_interface(intf)
        assert output['interface_state'] == 'up',\
            "Interface state for " + intf + " is down"


def validate_turn_off_interfaces(sw, interfaces):
    for intf in interfaces:
        output = sw.libs.vtysh.show_interface(intf)
        assert output['interface_state'] == 'down',\
            "Interface state for " + intf + "is up"


def validate_local_key(map_lacp, lag_id):
    assert map_lacp['local_key'] == lag_id,\
        "Actor Key is not the same as the LAG ID"


def validate_remote_key(map_lacp, lag_id):
    assert map_lacp['remote_key'] == lag_id,\
        "Partner Key is not the same as the LAG ID"


def validate_lag_name(map_lacp, lag_id):
    assert map_lacp['lag_id'] == lag_id,\
        "LAG ID should be " + lag_id


def validate_lag_state_sync(map_lacp, state):
    assert map_lacp[state]['active'] is True,\
        "LAG state should be active"
    assert map_lacp[state]['aggregable'] is True,\
        "LAG state should have aggregable enabled"
    assert map_lacp[state]['in_sync'] is True,\
        "LAG state should be In Sync"
    assert map_lacp[state]['collecting'] is True,\
        "LAG state should be in collecting"
    assert map_lacp[state]['distributing'] is True,\
        "LAG state should be in distributing"


def validate_lag_state_out_of_sync(map_lacp, state):
    assert map_lacp[state]['active'] is True,\
        "LAG state should be active"
    assert map_lacp[state]['in_sync'] is False,\
        "LAG state should be out of sync"
    assert map_lacp[state]['aggregable'] is True,\
        "LAG state should have aggregable enabled"
    assert map_lacp[state]['collecting'] is False,\
        "LAG state should not be in collecting"
    assert map_lacp[state]['distributing'] is False,\
        "LAG state should not be in distributing"
    assert map_lacp[state]['out_sync'] is True,\
        "LAG state should not be out of sync"


def validate_lag_state_afn(map_lacp, state):
    assert map_lacp[state]['active'] is True,\
        "LAG state should be active"
    assert map_lacp[state]['aggregable'] is True,\
        "LAG state should have aggregable enabled"
    assert map_lacp[state]['in_sync'] is True,\
        "LAG state should be In Sync"
    assert map_lacp[state]['collecting'] is False,\
        "LAG state should not be in collecting"
    assert map_lacp[state]['distributing'] is False,\
        "LAG state should not be in distributing"


def validate_lag_state_default_neighbor(map_lacp, state):
    assert map_lacp[state]['neighbor_state'] is True,\
        "LAG state should have default neighbor state"


def set_lag_lb_hash(sw, lag_id, lb_hash):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        if lb_hash == 'l2-src-dst':
            ctx.hash_l2_src_dst()
        elif lb_hash == 'l3-src-dst':
            ctx.hash_l3_src_dst()
        elif lb_hash == 'l4-src-dst':
            ctx.hash_l4_src_dst()


def check_lag_lb_hash(sw, lag_id, lb_hash):
    lag_info = sw.libs.vtysh.show_lacp_aggregates()
    assert lag_info['lag' + lag_id]['hash'] == lb_hash


def get_device_mac_address(sw, interface):
    cmd_output = sw('ifconfig'.format(**locals()),
                    shell='bash_swns')
    mac_re = (r'' + interface + '\s*Link\sencap:Ethernet\s*HWaddr\s'
              r'(?P<mac_address>([0-9A-Fa-f]{2}[:-]){5}'
              r'[0-9A-Fa-f]{2})')

    re_result = re.search(mac_re, cmd_output)
    assert re_result

    result = re_result.groupdict()
    print(result)

    return result['mac_address']


def tcpdump_capture_interface(sw, interface_id, wait_time):
    cmd_output = sw('tcpdump -D'.format(**locals()),
                    shell='bash_swns')
    interface_re = (r'(?P<linux_interface>\d)\.' + interface_id +
                    r'\s[\[Up, Running\]]')
    re_result = re.search(interface_re, cmd_output)
    assert re_result
    result = re_result.groupdict()

    sw('tcpdump -ni ' + result['linux_interface'] +
        ' -e ether proto ' + LACP_PROTOCOL + ' -vv'
        '> /tmp/interface.cap 2>&1 &'.format(**locals()),
        shell='bash_swns')

    time.sleep(wait_time)

    sw('killall tcpdump'.format(**locals()),
        shell='bash_swns')

    capture = sw('cat /tmp/interface.cap'.format(**locals()),
                 shell='bash_swns')

    sw('rm /tmp/interface.cap'.format(**locals()),
       shell='bash_swns')

    return capture


def get_info_from_packet_capture(capture, switch_side, sw_mac):
    packet_re = (r'[\s \S]*' + sw_mac.lower() + '\s\>\s' + LACP_MAC_HEADER +
                 r'\,[\s \S]*'
                 r'' + switch_side + '\sInformation\sTLV\s\(0x\d*\)'
                 r'\,\slength\s\d*\s*'
                 r'System\s(?P<system_id>([0-9A-Fa-f]{2}[:-]){5}'
                 r'[0-9A-Fa-f]{2})\,\s'
                 r'System\sPriority\s(?P<system_priority>\d*)\,\s'
                 r'Key\s(?P<key>\d*)\,\s'
                 r'Port\s(?P<port_id>\d*)\,\s'
                 r'Port\sPriority\s(?P<port_priority>\d*)')

    re_result = re.search(packet_re, capture)
    assert re_result

    result = re_result.groupdict()

    return result


def tcpdump_capture_interface_start(sw, interface_id):
    cmd_output = sw('tcpdump -D'.format(**locals()),
                    shell='bash_swns')
    interface_re = (r'(?P<linux_interface>\d)\.' + interface_id +
                    r'\s[\[Up, Running\]]')
    re_result = re.search(interface_re, cmd_output)
    assert re_result
    result = re_result.groupdict()

    cmd_output = sw(
        'tcpdump -ni ' + result['linux_interface'] +
        ' -e ether proto ' + LACP_PROTOCOL + ' -vv'
        '> /tmp/ops_{interface_id}.cap 2>&1 &'.format(**locals()),
        shell='bash_swns'
    )

    res = re.compile(r'\[\d+\] (\d+)')
    res_pid = res.findall(cmd_output)

    if len(res_pid) == 1:
        tcpdump_pid = int(res_pid[0])
    else:
        tcpdump_pid = -1

    return tcpdump_pid


def tcpdump_capture_interface_stop(sw, interface_id, tcpdump_pid):
    sw('kill {tcpdump_pid}'.format(**locals()),
        shell='bash_swns')

    capture = sw('cat /tmp/ops_{interface_id}.cap'.format(**locals()),
                 shell='bash_swns')

    sw('rm /tmp/ops_{interface_id}.cap'.format(**locals()),
       shell='bash_swns')

    return capture


def get_counters_from_packet_capture(capture):
    tcp_counters = {}

    packet_re = (r'(\d+) (\S+) (received|captured|dropped)')
    res = re.compile(packet_re)
    re_result = res.findall(capture)

    for x in re_result:
        tcp_counters[x[2]] = int(x[0])

    return tcp_counters


def set_debug(sw):
    sw('ovs-appctl -t ops-lacpd vlog/set dbg'.format(**locals()),
       shell='bash')


def create_vlan(sw, vlan_id):
    with sw.libs.vtysh.ConfigVlan(vlan_id) as ctx:
        ctx.no_shutdown()


def validate_vlan_state(sw, vlan_id, state):
    output = sw.libs.vtysh.show_vlan(vlan_id)
    assert output[vlan_id]['status'] == state,\
        'Vlan is not in ' + state + ' state'


def delete_vlan(sw, vlan):
    with sw.libs.vtysh.Configure() as ctx:
        ctx.no_vlan(vlan)
    output = sw.libs.vtysh.show_vlan()
    for vlan_index in output:
        assert vlan != output[vlan_index]['vlan_id'],\
            'Vlan was not deleted'


def associate_vlan_to_l2_interface(sw, vlan_id, interface):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.no_routing()
        ctx.vlan_access(vlan_id)
    output = sw.libs.vtysh.show_vlan(vlan_id)
    assert interface in output[vlan_id]['ports'],\
        'Vlan was not properly associated with Interface'


def check_connectivity_between_hosts(h1, h1_ip, h2, h2_ip,
                                     ping_num=5, success=True):
    ping = h1.libs.ping.ping(ping_num, h2_ip)
    if success:
        # Assuming it is OK to lose 1 packet
        assert ping['transmitted'] == ping_num <= ping['received'] + 1,\
            'Ping between ' + h1_ip + ' and ' + h2_ip + ' failed'
    else:
        assert ping['received'] == 0,\
            'Ping between ' + h1_ip + ' and ' + h2_ip + ' success'

    ping = h2.libs.ping.ping(ping_num, h1_ip)
    if success:
        # Assuming it is OK to lose 1 packet
        assert ping['transmitted'] == ping_num <= ping['received'] + 1,\
            'Ping between ' + h2_ip + ' and ' + h1_ip + ' failed'
    else:
        assert ping['received'] == 0,\
            'Ping between ' + h2_ip + ' and ' + h1_ip + ' success'


def check_connectivity_between_switches(s1, s1_ip, s2, s2_ip,
                                        ping_num=5, success=True):
    ping = s1.libs.vtysh.ping_repetitions(s2_ip, ping_num)
    if success:
        assert ping['transmitted'] == ping['received'] == ping_num,\
            'Ping between ' + s1_ip + ' and ' + s2_ip + ' failed'
    else:
        assert 'Network is unreachable' is not ping, \
            'Ping between ' + s1_ip + ' and ' + s2_ip + ' success'

    ping = s2.libs.vtysh.ping_repetitions(s1_ip, ping_num)
    if success:
        assert ping['transmitted'] == ping['received'] == ping_num,\
            'Ping between ' + s2_ip + ' and ' + s1_ip + ' failed'
    else:
        assert 'Network is unreachable' is not ping,\
            'Ping between ' + s2_ip + ' and ' + s1_ip + ' success'


def validate_interface_not_in_lag(sw, interface, lag_id):
    output = sw.libs.vtysh.show_lacp_interface(interface)
    print("Came back from show lacp interface")
    assert output['lag_id'] == "",\
        "Unable to associate interface to lag"


def is_interface_up(sw, interface):
    interface_status = sw('show interface {interface}'.format(**locals()))
    lines = interface_status.split('\n')
    for line in lines:
        if "Admin state" in line and "up" in line:
            return True
    return False


def is_interface_down(sw, interface):
    interface_status = sw('show interface {interface}'.format(**locals()))
    lines = interface_status.split('\n')
    for line in lines:
        if "Admin state" in line and "up" not in line:
            return True
    return False


def lag_shutdown(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.shutdown()


def lag_no_shutdown(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_shutdown()


def assign_ip_to_lag(sw, lag_id, ip_address, ip_address_mask):
    ip_address_complete = ip_address + "/" + ip_address_mask
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.routing()
        ctx.ip_address(ip_address_complete)


def config_lacp_rate(sw, lag_id, lacp_rate_fast=False):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        if lacp_rate_fast:
            ctx.lacp_rate_fast()
        else:
            ctx.no_lacp_rate_fast()


def set_lacp_rate_fast(sw, lag_id):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.lacp_rate_fast()


def validate_appctl_lag_state_sync(map_appctl_lacpstate, state):
    assert map_appctl_lacpstate[state]['lacp_activity'] == 1,\
        "Appctl LAG state should be active"
    assert map_appctl_lacpstate[state]['time_out'] == 1,\
        "Appctl LAG state should have short timeout"
    assert map_appctl_lacpstate[state]['aggregation'] == 1,\
        "Appctl LAG state should have aggregable enabled"
    assert map_appctl_lacpstate[state]['sync'] == 1,\
        "Appctl LAG state should be In Sync"
    assert map_appctl_lacpstate[state]['collecting'] == 1,\
        "Appctl LAG state should be in collecting"
    assert map_appctl_lacpstate[state]['distributing'] == 1,\
        "Appctl LAG state should be in distributing"


def validate_appctl_lag_state_out_sync(map_appctl_lacpstate, state):
    assert map_appctl_lacpstate[state]['lacp_activity'] == 1,\
        "Appctl LAG state should be active"
    assert map_appctl_lacpstate[state]['sync'] == 0,\
        "Appctl LAG state should be out of sync"
    assert map_appctl_lacpstate[state]['aggregation'] == 1,\
        "Appctl LAG state should have aggregable enabled"
    assert map_appctl_lacpstate[state]['collecting'] == 0,\
        "Appctl LAG state should not be in collecting"
    assert map_appctl_lacpstate[state]['distributing'] == 0,\
        "Appctl LAG state should not be in distributing"


def validate_appctl_lag_state_afn(map_appctl_lacpstate, state):
    assert map_appctl_lacpstate[state]['lacp_activity'] == 1,\
        "Appctl LAG state should be active"
    assert map_appctl_lacpstate[state]['time_out'] == 1,\
        "Appctl LAG state should have short timeout"
    assert map_appctl_lacpstate[state]['aggregation'] == 1,\
        "Appctl LAG state should have aggregable enabled"
    assert map_appctl_lacpstate[state]['sync'] == 1,\
        "Appctl LAG state should be In Sync"
    assert map_appctl_lacpstate[state]['collecting'] == 0,\
        "Appctl LAG state should not be in collecting"
    assert map_appctl_lacpstate[state]['distributing'] == 0,\
        "Appctl LAG state should not be in distributing"


def validate_appctl_lacp_interfaces(appctl_output, lag_id, expected_configured,
                                    expected_eligible, expected_participant):
    for interface in expected_configured:
        assert interface in appctl_output[lag_id]['configured_interfaces'],\
            ('Interface %s is not in configured interfaces for LAG %s'
             % (interface, lag_id))
    for interface in appctl_output[lag_id]['configured_interfaces']:
        assert interface in expected_configured,\
            ('Interface %s should not be in configured interfaces for LAG %s'
             % (interface, lag_id))
    for interface in expected_eligible:
        assert interface in appctl_output[lag_id]['eligible_interfaces'],\
            ('Interface %s is not in eligible interfaces for LAG %s'
             % (interface, lag_id))
    for interface in appctl_output[lag_id]['eligible_interfaces']:
        assert interface in expected_eligible,\
            ('Interface %s should not be in eligible interfaces for LAG %s'
             % (interface, lag_id))
    for interface in expected_participant:
        assert interface in appctl_output[lag_id]['participant_interfaces'],\
            ('Interface %s is not in participant interfaces for LAG %s'
             % (interface, lag_id))
    for interface in appctl_output[lag_id]['participant_interfaces']:
        assert interface in expected_participant,\
            ('Interface %s should not be in participant interfaces for LAG %s'
             % (interface, lag_id))


def parse_appctl_getlacpcounters(raw_result):
    """
    Parse the 'ovs-appctl -t ops-lacpd lacpd/getlacpcounters' command raw
    output.

    :param str raw_result: vtysh raw result string.
    :rtype: dict
    :return: The parsed result of the getlacpcounters in a dictionary of the
             form:

     ::

         {
            'lag':
                {'interface':
                    {'lacp_pdus_sent': 0,
                    'marker_response_pdus_sent': 0,
                    'lacp_pdus_received' : 0,
                    'marker_pdus_received' : 0},
                'interface':
                    {'lacp_pdus_sent': 0,
                    'marker_response_pdus_sent': 0,
                    'lacp_pdus_received' : 0,
                    'marker_pdus_received' : 0},
                }
        }
    """

    getlacpcounters_re = (
        r'Interface: (?P<interface>\d+)\s*'
        r'lacp_pdus_sent: (?P<lacp_pdus_sent>\d+)\s*'
        r'marker_response_pdus_sent: (?P<marker_response_pdus_sent>\d+)\s*'
        r'lacp_pdus_received: (?P<lacp_pdus_received>\d+)\s*'
        r'marker_pdus_received: (?P<marker_pdus_received>\d+)\s*'
    )

    result = {}
    result_interface = {}

    lag_block = raw_result.split('LAG lag')
    for block in lag_block:
        lag_id = block.split(':\n')[0]
        if lag_id:
            for re_partial in re.finditer(getlacpcounters_re, block):
                interface = re_partial.groupdict()
                interface_number = interface['interface']
                del interface['interface']
                for key, value in interface.items():
                    if value is None:
                        interface[key] = 0
                    elif value.isdigit():
                        interface[key] = int(value)
                result_interface[interface_number] = interface
            result[lag_id] = result_interface
            result_interface = {}
    return result


def parse_appctl_getlacpstate(raw_result):
    """
    Parse the 'ovs-appctl -t ops-lacpd lacpd/getlacpstate' command raw
    output.

    :param str raw_result: vtysh raw result string.
    :rtype: dict
    :return: The parsed result of the getlacpstate in a dictionary of the
             form:
     ::
         {
            'lag':
                {'interface':
                    { 'actor_oper_port_state':
                        {'lacp_activity': 0,
                        'time_out': 0,
                        'aggregation' : 0,
                        'sync' : 0
                        'collecting': 0,
                        'distributing' : 0,
                        'defaulted' : 0,
                        'expired' : 0},
                    'partner_oper_port_state':
                        {'lacp_activity': 0,
                        'time_out': 0,
                        'aggregation' : 0,
                        'sync' : 0
                        'collecting': 0,
                        'distributing' : 0,
                        'defaulted' : 0,
                        'expired' : 0},
                    'lacp_control':
                        {'begin': 0,
                        'actor_churn': 0,
                        'partner_churn' : 0,
                        'ready_n' : 0
                        'selected': 0,
                        'port_moved' : 0,
                        'ntt' : 0,
                        'port_enabled' : 0},
                    }
                }
        }
    """

    getlacpstate_actor_re = (
        r'Interface: (?P<interface>\d+)\s*'
        r'actor_oper_port_state\s*'
        r'lacp_activity:(?P<a_lacp_activity>\S+) time_out:(?P<a_time_out>' +
        '\S+) aggregation:(?P<a_aggregation>\S+) sync:(?P<a_sync>\S+) ' +
        'collecting:(?P<a_collecting>\S+) distributing:(?P<a_distributing>' +
        '\S+) defaulted:(?P<a_defaulted>\S+) expired:(?P<a_expired>\S+)\s+'
        r'partner_oper_port_state\s*'
        r'lacp_activity:(?P<p_lacp_activity>\S+) time_out:(?P<p_time_out>' +
        '\S+) aggregation:(?P<p_aggregation>\S+) sync:(?P<p_sync>\S+) ' +
        'collecting:(?P<p_collecting>\S+) distributing:(?P<p_distributing>' +
        '\S+) defaulted:(?P<p_defaulted>\S+) expired:(?P<p_expired>\S+)\s+'
        r'lacp_control\s*'
        r'begin:(?P<begin>\S+) actor_churn:(?P<actor_churn>\S+) ' +
        'partner_churn:(?P<partner_churn>\S+) ready_n:(?P<ready_n>\S+) ' +
        'selected:(?P<selected>\S+) port_moved:(?P<port_moved>\S+) ' +
        'ntt:(?P<ntt>\S+) port_enabled:(?P<port_enabled>\S+)\s'
    )
    actor_data_keys = ['a_lacp_activity', 'a_time_out', 'a_aggregation',
                       'a_sync', 'a_collecting', 'a_distributing',
                       'a_defaulted', 'a_expired']
    partner_data_keys = ['p_lacp_activity', 'p_time_out', 'p_aggregation',
                         'p_sync', 'p_collecting', 'p_distributing',
                         'p_defaulted', 'p_expired']
    lacp_control_keys = ['begin', 'actor_churn', 'partner_churn', 'ready_n',
                         'selected', 'port_moved', 'ntt', 'port_enabled']
    result = {}
    actor_dict = {}
    partner_dict = {}
    lacp_control_dict = {}
    interface_data_dict = {}
    interface_dict = {}

    lag_block = raw_result.split('LAG lag')
    for block in lag_block:
        lag_id = block.split(':\n')[0]
        if lag_id:
            for re_partial in re.finditer(getlacpstate_actor_re, block):
                interface_data = re_partial.groupdict()
                for key, value in interface_data.items():
                    if value.isdigit():
                        interface_data[key] = int(value)
                for key_actor, key_partner, key_lacp_control in\
                        zip(actor_data_keys, partner_data_keys,
                            lacp_control_keys):
                        actor_dict[key_actor[2:]] = interface_data[key_actor]
                        partner_dict[key_partner[2:]] =\
                            interface_data[key_partner]
                        lacp_control_dict[key_lacp_control] =\
                            interface_data[key_lacp_control]
                interface_data_dict['actor_oper_port_state'] = actor_dict
                interface_data_dict['partner_oper_port_state'] = partner_dict
                interface_data_dict['lacp_control'] = lacp_control_dict
                actor_dict = {}
                partner_dict = {}
                lacp_control_dict = {}
                interface_dict[interface_data['interface']] =\
                    interface_data_dict
                interface_data_dict = {}
            result[lag_id] = interface_dict
            interface_dict = {}
    return result


def parse_appctl_getlacpinterfaces(raw_result):
    """
    Parse the 'ovs-appctl -t ops-lacpd lacpd/getlacpinterfaces' command raw
    output.

    :param str raw_result: vtysh raw result string.
    :rtype: dict
    :return: The parsed result of the getlacpinterfaces in a dictionary of the
             form:
     ::
         {
            'lag':
                {'configured_members': [1, 2],
                 'eligible_members': [1, 2],
                 'participant_members': [1, 2],
                }
        }
    """

    getlacpcounters_re = (
        r'Port lag(?P<lag_number>\d+):\s*'
        r'configured_members\s+:[ ]?(?P<configured_interfaces>[\w \-]*)\s*'
        r'eligible_members\s+:[ ]?(?P<eligible_interfaces>[\w \-]*)\s*'
        r'participant_members\s+:[ ]?(?P<participant_interfaces>[\w \-]*)\s*'
    )

    result = {}

    for re_partial in re.finditer(getlacpcounters_re, raw_result):
        lag = re_partial.groupdict()
        lag_id = lag['lag_number']
        del lag['lag_number']
        lag['configured_interfaces'] = lag['configured_interfaces'].split()
        lag['eligible_interfaces'] = lag['eligible_interfaces'].split()
        lag['participant_interfaces'] = lag['participant_interfaces'].split()
        result[lag_id] = lag
    return result
