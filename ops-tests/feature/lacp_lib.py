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
from time import sleep
from functools import wraps

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
            pass
        else:
            assert False, 'Invalid mode %s for LAG' % (lag_mode)
    lag_name = "lag" + lag_id
    output = sw.libs.vtysh.show_lacp_aggregates(lag_name)
    assert lag_mode == output[lag_name]['mode'],\
        "Unable to create and validate LAG"


def delete_lag(sw, lag_id):
    with sw.libs.vtysh.Configure() as ctx:
        ctx.no_interface_lag(lag_id)
    lag_name = "lag" + lag_id
    output = sw.libs.vtysh.show_lacp_aggregates()
    assert lag_name not in output,\
        "Unable to delete LAG"


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


def associate_vlan_to_lag(sw, vlan_id, lag_id, vlan_type='access'):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        ctx.no_routing()
        if vlan_type == 'access':
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


def validate_lag_state_sync(map_lacp, state, lacp_mode='active'):
    assert map_lacp[state][lacp_mode] is True,\
        "LAG state should be {}".format(lacp_mode)
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


def validate_lag_state_static(map_lacp, state):
    for key in map_lacp[state]:
        assert map_lacp[state][key] is False,\
            "LAG state for {} should be False".format(key)


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


def set_lag_rate(sw, lag_id, rate):
    with sw.libs.vtysh.ConfigInterfaceLag(lag_id) as ctx:
        if rate == 'fast':
            ctx.lacp_rate_fast()
        elif rate == 'slow':
            ctx.lacp_rate_slow()


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

    sleep(wait_time)

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


def associate_vlan_to_l2_interface(
    sw,
    vlan_id,
    interface,
    vlan_type='access'
):
    with sw.libs.vtysh.ConfigInterface(interface) as ctx:
        ctx.no_routing()
        if vlan_type == 'access':
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
        assert ping['received'] == 0,\
            'Ping between ' + s1_ip + ' and ' + s2_ip + ' success'

    ping = s2.libs.vtysh.ping_repetitions(s1_ip, ping_num)
    if success:
        assert ping['transmitted'] == ping['received'] == ping_num,\
            'Ping between ' + s2_ip + ' and ' + s1_ip + ' failed'
    else:
        assert ping['received'] == 0,\
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


def verify_lag_config(
    sw,
    lag_id,
    interfaces,
    heartbeat_rate='slow',
    fallback=False,
    hashing='l3-src-dst',
    mode='off'
):
    lag_name = 'lag{lag_id}'.format(**locals())
    lag_config = sw.libs.vtysh.show_lacp_aggregates(lag=lag_name)
    assert len(interfaces) == len(lag_config[lag_name]['interfaces']),\
        ' '.join(
        [
            "{} interfaces in LAG is different".format(
                len(lag_config[lag_name]['interfaces'])
            ),
            "than the expected number of {}".format(len(interfaces))
        ]
    )
    for interface in interfaces:
        assert interface in lag_config[lag_name]['interfaces'],\
            "Interface {} is not in LAG".format(interface)
    assert heartbeat_rate == lag_config[lag_name]['heartbeat_rate'],\
        "Heartbeat rate {} is not expected. Expected {}".format(
            lag_config[lag_name]['heartbeat_rate'],
            heartbeat_rate
    )
    assert fallback == lag_config[lag_name]['fallback'],\
        "Fallback setting of {} is not expected. Expected {}".format(
        lag_config[lag_name]['fallback'],
        fallback
    )
    assert hashing == lag_config[lag_name]['hash'],\
        "Hash setting of {} is not expected. Expected {}".format(
        lag_config[lag_name]['hash'],
        hashing
    )
    assert hashing == lag_config[lag_name]['hash'],\
        "LAG mode setting of {} is not expected. Expected {}".format(
        lag_config[lag_name]['mode'],
        mode
    )


def verify_vlan_full_state(sw, vlan_id, interfaces=None, status='up'):
    vlan_status = sw.libs.vtysh.show_vlan()
    vlan_str_id = str(vlan_id)
    assert vlan_str_id in vlan_status,\
        'VLAN not found, Expected: {}'.format(vlan_str_id)
    assert vlan_status[vlan_str_id]['status'] == status,\
        'Unexpected VLAN status, Expected: {}'.format(status)
    if interfaces is None:
        assert len(vlan_status[vlan_str_id]['ports']) == 0,\
            ''.join(['Unexpected number of interfaces in VLAN',
                     '{}, Expected: 0'.format(vlan_id)])
    else:
        assert len(vlan_status[vlan_str_id]['ports']) == len(interfaces),\
            'Unexpected number of interfaces in VLAN {}, Expected: {}'.format(
            vlan_id,
            len(interfaces)
        )
        for interface in interfaces:
            assert interface not in vlan_status[vlan_str_id],\
                'Interface not found in VLAN {}, Expected {}'.format(
                vlan_id,
                interface
            )


def verify_lag_interface_key(
    sw1_int_map_lacp,
    sw2_int_map_lacp=None,
    key='1',
    value_check=True,
    cross_check=False
):
    if cross_check and sw2_int_map_lacp is None:
        print(' '.join(
            ['validate_lag_interface_key skipped',
             'because of invalid settings']
        ))
        return
    if value_check is True:
        assert key == sw1_int_map_lacp['local_key'],\
            'Unexpected key value of {}, Expected {}'.format(
            sw1_int_map_lacp['local_key'],
            key
        )
    if cross_check is True:
        assert sw1_int_map_lacp['local_key'] ==\
            sw2_int_map_lacp['remote_key'],\
            'Remote key {} on partner does not match, Expected {}'.format(
            sw2_int_map_lacp['remote_key'],
            sw1_int_map_lacp['local_key']
        )


def verify_lag_interface_priority(
    sw1_int_map_lacp,
    sw2_int_map_lacp=None,
    priority='1',
    value_check=True,
    cross_check=False
):
    if cross_check and sw2_int_map_lacp is None:
        print(' '.join(
            ['validate_lag_interface_priority skipped',
             'because of invalid settings']
        ))
        return
    if value_check is True:
        assert priority == sw1_int_map_lacp['local_port_priority'],\
            'Unexpected priority value of {}, Expected {}'.format(
            sw1_int_map_lacp['local_port_priority'],
            priority
        )
    if cross_check is True:
        assert sw1_int_map_lacp['local_port_priority'] ==\
            sw2_int_map_lacp['remote_port_priority'],\
            ' '.join(
            [
                'Remote priority {} on partner does not match,'.format(
                    sw2_int_map_lacp['remote_port_priority']
                ),
                'Expected {}'.format(
                    sw1_int_map_lacp['local_port_priority'])
            ]
        )


def verify_lag_interface_id(
    sw1_int_map_lacp,
    sw2_int_map_lacp=None,
    id='1',
    value_check=True,
    cross_check=False
):
    if cross_check and sw2_int_map_lacp is None:
        print(' '.join(
            ['validate_lag_interface_id skipped',
             'because of invalid settings']
        ))
        return
    if value_check is True:
        assert id == sw1_int_map_lacp['local_port_id'],\
            'Unexpected key value of {}, Expected {}'.format(
            sw1_int_map_lacp['local_port_id'],
            id
        )
    if cross_check is True:
        assert sw1_int_map_lacp['local_port_id'] ==\
            sw2_int_map_lacp['remote_port_id'],\
            'Remote id {} on partner does not match, Expected {}'.format(
            sw2_int_map_lacp['remote_port_id'],
            sw1_int_map_lacp['local_port_id']
        )


def verify_lag_interface_system_id(
    sw1_int_map_lacp,
    sw2_int_map_lacp=None,
    system_id='00:00:00:00:00:00',
    value_check=True,
    cross_check=False
):
    if cross_check and sw2_int_map_lacp is None:
        print(' '.join(
            ['validate_lag_interface_system_id skipped',
             'because of invalid settings']
        ))
    if value_check is True:
        assert system_id ==\
            sw1_int_map_lacp['local_system_id'],\
            'Unexpected local system id {}, Expected: {}'.format(
                sw1_int_map_lacp['local_system_id'],
                system_id
            )
    if cross_check is True:
        assert sw1_int_map_lacp['local_system_id'] ==\
            sw2_int_map_lacp['remote_system_id'],\
            ' '.join(
            ['Remote system id',
             sw2_int_map_lacp['remote_system_id'],
             'on partner does not match local system id, Expected',
             sw1_int_map_lacp['local_system_id']]
        )


def verify_lag_interface_system_priority(
    sw1_int_map_lacp,
    sw2_int_map_lacp=None,
    system_priority='65534',
    value_check=True,
    cross_check=False
):
    if cross_check and sw2_int_map_lacp is None:
        print(' '.join(
            ['validate_lag_interface_system_priority skipped',
             'because of invalid settings']
        ))
    if value_check is True:
        assert system_priority ==\
            sw1_int_map_lacp['local_system_priority'],\
            'Unexpected local system priority {}, Expected: {}'.format(
                sw1_int_map_lacp['local_system_priority'],
                system_priority
            )
    if cross_check is True:
        assert sw1_int_map_lacp['local_system_priority'] ==\
            sw2_int_map_lacp['remote_system_priority'],\
            ' '.join(
            ['Remote system priority',
             sw2_int_map_lacp['remote_system_priority'],
             'on partner does not match local system priority, Expected',
             sw1_int_map_lacp['local_system_priority']]
        )


def verify_lag_interface_lag_id(map_lacp, lag_id='1'):
    assert map_lacp['lag_id'] == lag_id,\
        'Unexpected value for LAG id {}, Expected {}'.format(
        map_lacp['lag_id'],
        lag_id
    )


def retry_wrapper(
    init_msg,
    soft_err_msg,
    time_steps,
    timeout,
    err_condition=None
):
    if err_condition is None:
        err_condition = AssertionError

    def actual_retry_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(init_msg)
            cont = 0
            while cont <= timeout:
                try:
                    func(*args, **kwargs)
                    return
                except err_condition:
                    print(soft_err_msg)
                    if cont < timeout:
                        print('Waiting {} seconds to retry'.format(
                            time_steps
                        ))
                        sleep(time_steps)
                        cont += time_steps
                        continue
                    print('Retry time of {} seconds expired'.format(
                        timeout
                    ))
                    raise
        return wrapper
    return actual_retry_wrapper


def compare_lag_interface_basic_settings(
    lag_stats,
    lag_id,
    members,
    agg_key=1,
    mode='off'
):
    assert lag_stats['lag_name'] == 'lag{}'.format(lag_id),\
        'Unexpected LAG name, Expected lag{}'.format(lag_id)
    assert lag_stats['agg_key'] == agg_key,\
        'Unexpected LAG aggregation key {}, Expected {}'.format(
        lag_stats['agg_key'],
        agg_key
    )
    if mode == 'off':
        assert lag_stats['agg_mode'] is None,\
            'Found aggregate mode for static LAG in LAG statistics'
    else:
        assert lag_stats['agg_mode'] is not None,\
            'Could not find aggregate mode for static LAG in LAG statistics'
        assert mode == lag_stats['agg_mode'],\
            'Unexpected value for aggregate mode {}, Expected {}'.format(
            lag_stats['agg_mode'],
            mode
        )
    aggregated_interfaces = lag_stats['aggregated_interfaces'].strip(
    ).split(' ')
    if len(aggregated_interfaces) == 1 and aggregated_interfaces[0] == '':
        aggregated_interfaces = []
    assert len(members) == len(aggregated_interfaces),\
        'Unexpected number of aggregated interfaces, Expected {}'.format(
        len(members)
    )
    for member in members:
        assert member in aggregated_interfaces,\
            'Unable to find LAG member {} in LAG interface'.format(member)
