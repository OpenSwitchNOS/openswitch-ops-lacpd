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
# Name:        test_ft_lacp_statistics_change_members.py
#
# Description: Tests that a configured dynamic Link Aggregation statistics
#              change when its members are removed or added to match the
#              current set of interfaces in the aggregation
#
# Author:      Jose Hernandez
#
# Topology:  |Host| ----- |Switch| ---------------------- |Switch| ----- |Host|
#                                        (3 links)
#
# Success Criteria:  PASS -> Statistics are accurate and represent the sum of
#                            all current members
#
#                    FAILED -> Information from the statistics does not
#                              represent the sum of each individual current
#                              member
#
###############################################################################

from time import sleep
from lacp_lib import create_lag
from lacp_lib import turn_on_interface
from lacp_lib import validate_turn_on_interfaces
from lacp_lib import associate_interface_to_lag
from lacp_lib import verify_lag_config
from lacp_lib import create_vlan
from lacp_lib import verify_vlan_full_state
from lacp_lib import check_connectivity_between_hosts
from lacp_lib import set_lag_rate
from lacp_lib import associate_vlan_to_l2_interface
from lacp_lib import retry_wrapper
from lacp_lib import remove_interface_from_lag
from lacp_lib import compare_lag_interface_basic_settings
from re import search
from re import DOTALL

TOPOLOGY = """
#            +-----------------+
#            |                 |
#            |      Host 1     |
#            |                 |
#            +-----------------+
#                     |
#                     |
#     +-------------------------------+
#     |                               |
#     |                               |
#     |            Switch 1           |
#     |                               |
#     +-------------------------------+
#          |         |        |
#          |         |        |
#          |         |        |
#     +-------------------------------+
#     |                               |
#     |                               |
#     |            Switch 2           |
#     |                               |
#     +-------------------------------+
#                     |
#                     |
#            +-----------------+
#            |                 |
#            |     Host 2      |
#            |                 |
#            +-----------------+

# Nodes
[type=openswitch name="Switch 1"] sw1
[type=openswitch name="Switch 2"] sw2
[type=host name="Host 1" image="openswitch/ubuntutest:latest"] hs1
[type=host name="Host 2" image="openswitch/ubuntutest:latest"] hs2

# Links

sw1:1 -- hs1:1
sw2:1 -- hs2:1
sw1:2 -- sw2:2
sw1:3 -- sw2:3
sw1:4 -- sw2:4
"""

# Global variables
SW_LBL_PORTS = ['1', '2', '3', '4']
LAG_ID = '1'
NETWORK = '10.90'
NETMASK = '24'
NUMBER_PINGS = 5
BASE_IPERF_PORT = 5000
IPERF_BW = '10m'
SW_COUNTERS_DELAY = 20
IPERF_INSTANCE_ID = 1
DATAGRAMS_PER_SEC = 850
DATAGRAM_SIZE_BYTES = 1470
IPERF_SRV_FILE = '/tmp/iperf_server-{}.log'.format(IPERF_INSTANCE_ID)
IPERF_CLIENT_FILE = '/tmp/iperf_client-{}.log'.format(IPERF_INSTANCE_ID)
ERROR_TOLERANCE = 0.01
VLANS_IDS = [900, 901, 902]
VLANS = {}
VLANS[VLANS_IDS[0]] = {'network': '0', 'member_id': 1, 'time_tx': 10}
VLANS[VLANS_IDS[1]] = {'network': '1', 'member_id': 2, 'time_tx': 15}
VLANS[VLANS_IDS[2]] = {'network': '2', 'member_id': 3, 'time_tx': 20}


@retry_wrapper(
    'Ensure iperf is turned on',
    'iperf is not yet ready',
    5,
    10)
def assert_udp_iperf_started(hs, file):
    # FIX ME
    res = hs('cat {}'.format(file))
    # END OF FIX ME
    search_res = search(r'-+.*UDP buffer size.*-+', res, DOTALL)
    assert search_res is not None, 'Could not get iperf start information'


@retry_wrapper(
    'Ensure iperf server finished',
    'iperf server is not yet finished',
    5,
    10)
def assert_iperf_srv_finished_traffic(hs, file, time):
    # FIX ME
    res = hs('cat {}'.format(file))
    # END OF FIX ME

    search_res = search(
        r'0\.0-{}\.0 sec\s+.*\(.*\)'.format(time),
        res
    )
    assert search_res is not None, 'Could not get iperf finish information'


def assert_verify_iperf_traffic_received_mbytes(
    iperf_output,
    datagram_size_bytes,
    datagram_speed,
    time,
    error=ERROR_TOLERANCE
):
    measure_unit = 'MBytes'
    assert len(iperf_output['traffic']) != 0,\
        'No iperf traffic information found'
    # Verify iperf traffic summary matches expected value
    last_val = iperf_output['traffic'][
        str(len(iperf_output['traffic']) - 1)
    ]['transfer']
    last_val = last_val.split(' ')
    assert measure_unit == last_val[1],\
        ' '.join([
            'Unit of measure for iperf traffic not',
            'as expected, Expected {}'.format(measure_unit)
        ])
    # get expected value in bytes
    expected_last_val = datagram_size_bytes * datagram_speed * time
    # convert to Megabytes
    expected_last_val = expected_last_val / 1024 / 1024
    # round to 1 decimal
    expected_last_val = round(expected_last_val, 1)
    compare_values(float(last_val[0]), expected_last_val, error)


@retry_wrapper(
    'Ensure interfaces are turned on',
    'Interfaces not yet ready',
    5,
    60)
def assert_retry_check_interfaces_on(sw_list):
    for sw in sw_list:
        validate_turn_on_interfaces(sw, SW_LBL_PORTS)


@retry_wrapper(
    'Obtain interfaces information and verify their consistency',
    'Information provided by counters is not yet reliable',
    5,
    SW_COUNTERS_DELAY)
def assert_get_and_compare_sw_stats(sw_list, sw_stats):
    print('Get statistics from switches')
    for sw in sw_list:
        sw_stats[sw] = {}
        for port in SW_LBL_PORTS:
            sw_stats[sw][port] = sw.libs.vtysh.show_interface(port)
    print('Verify obtained information is consistent')
    print('Compare counters between siwtches')
    compare_switches_counters(sw_list, sw_stats)


def compare_values(value1, value2, error=ERROR_TOLERANCE):
    value2_max = value2 * (1 + error)
    value2_min = value2 * (1 - error)
    assert value1 <= value2_max, ' '.join(
        ['Value of {} is more than {}'.format(value1, error * 100),
         'percent higher than {}'.format(value2)]
    )
    assert value1 >= value2_min, ' '.join(
        ['Value of {} is more than {}'.format(value1, error * 100),
         'percent lower than {}'.format(value2)]
    )


def compare_switches_counters(sw_list, stats):
    # Verify switches counters match
    for port in SW_LBL_PORTS:
        print('Compare port {} between switches'.format(port))
        print('rx from sw1 vs tx from sw2')
        compare_values(
            int(stats[sw_list[0]][port]['{}_packets'.format('rx')]),
            int(stats[sw_list[1]][port]['{}_packets'.format('tx')])
        )
        print('tx from sw1 vs rx from sw2')
        compare_values(
            int(stats[sw_list[0]][port]['{}_packets'.format('tx')]),
            int(stats[sw_list[1]][port]['{}_packets'.format('rx')])
        )


def compare_lag_to_switches_counters(sw_stats, lag_stats, ports):
    for param in [
        'rx_bytes',
        'rx_packets',
        'rx_crc_fcs',
        'rx_dropped',
        'rx_error',
        'tx_packets',
        'tx_bytes',
        'tx_collisions',
        'tx_dropped',
        'tx_errors',
        'speed'
    ]:
        total = 0
        for port in ports:
            total += int(sw_stats[port][param])
        print('Verifying LAG interface value for {}'.format(param))
        compare_values(int(lag_stats[param]), total)
    for port in ports:
        assert lag_stats['speed_unit'] == sw_stats[port]['speed_unit'],\
            'Unexpected change in speed unit {}, Expected {}'.format(
            lag_stats['speed_unit'],
            sw_stats[port]['speed_unit']
        )


def change_member_states(sw, sw_real_ports, before_state, new_state):
    for i, port in enumerate(sw_real_ports[sw][1:]):
        if before_state[i] == new_state[i]:
            continue
        elif before_state[i] is False and new_state[i] is True:
            associate_interface_to_lag(sw, port, LAG_ID)
        else:
            remove_interface_from_lag(sw, port, LAG_ID)
    lag_members = [port for port, state in zip(
        sw_real_ports[sw][1:],
        new_state
    ) if state is True]
    verify_lag_config(
        sw,
        LAG_ID,
        lag_members,
        heartbeat_rate='fast',
        mode='active'
    )
    return lag_members


def step_enable_switches_interfaces(sw_list, step):
    step('Enable switches interfaces')
    for sw in sw_list:
        for port in SW_LBL_PORTS:
            turn_on_interface(sw, port)
    # Verify interfaces are indeed on
    assert_retry_check_interfaces_on(sw_list)


def step_configure_vlans(sw_list, sw_real_ports, step):
    step('Configure VLANs on devices')
    for sw in sw_list:
        for vlan in VLANS_IDS:
            print('VLAN {}'.format(vlan))
            # Create VLAN
            create_vlan(sw, str(vlan))

            if vlan == VLANS_IDS[0]:
                # Associate VLAN to interfaces
                associate_vlan_to_l2_interface(
                    sw,
                    str(vlan),
                    sw_real_ports[sw][VLANS[vlan]['member_id']]
                )
                associate_vlan_to_l2_interface(
                    sw,
                    str(vlan),
                    sw_real_ports[sw][0]
                )
                # Verify VLAN configuration was successfully applied
                verify_vlan_full_state(
                    sw,
                    vlan, interfaces=[
                        sw_real_ports[sw][0],
                        sw_real_ports[sw][VLANS[vlan]['member_id']]
                    ]
                )
            else:
                # Associate VLAN to interfaces
                associate_vlan_to_l2_interface(
                    sw,
                    str(vlan),
                    sw_real_ports[sw][VLANS[vlan]['member_id']]
                )
                # Verify VLAN configuration was successfully applied
                verify_vlan_full_state(
                    sw,
                    vlan, interfaces=[
                        sw_real_ports[sw][VLANS[vlan]['member_id']]
                    ]
                )


def step_configure_lag(sw, step):
    step('Create LAG on sw1')
    create_lag(sw, LAG_ID, 'active')
    # Set LACP rate to fast
    set_lag_rate(sw, LAG_ID, 'fast')
    verify_lag_config(
        sw,
        LAG_ID,
        [],
        heartbeat_rate='fast',
        mode='active'
    )


def step_change_lag_members(sw, sw_real_ports, step):
    step('Change members of LAGs and compare LAG ports statistics match')
    lag_member_states = [
        [False, False, False],
        [False, False, True],
        [False, True, False],
        [False, True, True],
        [True, False, False],
        [True, False, True],
        [True, True, False],
        [True, True, True],
        [False, False, False]
    ]
    print('Verify information with no members')
    lag_int_stat = sw.libs.vtysh.show_interface('lag{}'.format(LAG_ID))
    compare_lag_interface_basic_settings(
        lag_int_stat,
        LAG_ID,
        [],
        mode='active'
    )
    compare_lag_to_switches_counters({}, lag_int_stat, [])
    for i in range(1, len(lag_member_states)):
        print('Changing members')
        current_lag_members = change_member_states(
            sw,
            sw_real_ports,
            lag_member_states[i - 1],
            lag_member_states[i]
        )
        print('Changed members of LAG to: {}'.format(current_lag_members))
        int_stats = {}
        for port in current_lag_members:
            int_stats[port] = sw.libs.vtysh.show_interface(port)
        print('Verify LAG statistics information')
        lag_int_stat = sw.libs.vtysh.show_interface('lag{}'.format(LAG_ID))
        compare_lag_interface_basic_settings(
            lag_int_stat,
            LAG_ID,
            current_lag_members,
            mode='active'
        )
        compare_lag_to_switches_counters(
            int_stats,
            lag_int_stat,
            current_lag_members
        )


def step_configure_workstations(hs_list, vlan_id, step):
    step('Configure workstations')
    for hs_num, hs in enumerate(hs_list):
        hs.libs.ip.interface(
            SW_LBL_PORTS[0],
            addr='{}.{}.{}/{}'.format(
                NETWORK,
                VLANS[vlan_id]['network'],
                hs_num + 1, NETMASK
            ),
            up=True
        )


def step_change_host_int_to_vlan(sw_list, sw_real_ports, vlan_id, step):
    for sw in sw_list:
        # Associate VLAN to host interface
        associate_vlan_to_l2_interface(
            sw,
            str(vlan_id),
            sw_real_ports[sw][0]
        )
        # Verify VLAN configuration was successfully applied
        verify_vlan_full_state(
            sw,
            vlan_id, interfaces=[
                sw_real_ports[sw][0],
                sw_real_ports[sw][VLANS[vlan_id]['member_id']]
            ]
        )


def step_transmit_iperf_traffic(sw_list, hs_list, vlan_id, step):
    sw_stats_after = {}
    step('Transmit iperf traffic between devices')
    print('Start iperf servers')
    for i, hs in enumerate(hs_list):
        hs.libs.iperf.server_start(BASE_IPERF_PORT + i, udp=True)
        # Verify iperf server has started
        assert_udp_iperf_started(hs, IPERF_SRV_FILE)
    print('Start traffic transmission')
    for hs, other_base in zip(hs_list, [2, 1]):
        hs.libs.iperf.client_start(
            '{}.{}.{}'.format(NETWORK, VLANS[vlan_id]['network'], other_base),
            BASE_IPERF_PORT + other_base - 1,
            time=VLANS[vlan_id]['time_tx'],
            udp=True,
            bandwidth=IPERF_BW
        )
        # Verify iperf client has started
        assert_udp_iperf_started(hs, IPERF_CLIENT_FILE)
    print('Wait for traffic to finish in {} seconds'.format(
        VLANS[vlan_id]['time_tx']
    ))
    sleep(VLANS[vlan_id]['time_tx'])
    print('Stop iperf')
    for hs in hs_list:
        srv_res = hs.libs.iperf.server_stop()
        hs.libs.iperf.client_stop()
        # Verify traffic was received by server
        assert_verify_iperf_traffic_received_mbytes(
            srv_res,
            DATAGRAM_SIZE_BYTES,
            DATAGRAMS_PER_SEC,
            VLANS[vlan_id]['time_tx']
        )

    assert_get_and_compare_sw_stats(sw_list, sw_stats_after)


def step_validate_connectivity(hs_list, vlan_id, wait, step):
    step('Check workstations connectivity')
    if wait is False:
        check_connectivity_between_hosts(
            hs_list[0],
            '{}.{}.{}'.format(NETWORK, VLANS[vlan_id]['network'], 1),
            hs_list[1],
            '{}.{}.{}'.format(NETWORK, VLANS[vlan_id]['network'], 2),
            NUMBER_PINGS,
            True
        )
    else:
        check_func = retry_wrapper(
            'Verifying workstations connectivity',
            'Configuration not yet applied',
            5,
            SW_COUNTERS_DELAY
        )(check_connectivity_between_hosts)
        check_func(
            hs_list[0],
            '{}.{}.{}'.format(NETWORK, VLANS[vlan_id]['network'], 1),
            hs_list[1],
            '{}.{}.{}'.format(NETWORK, VLANS[vlan_id]['network'], 2),
            NUMBER_PINGS,
            True
        )


def test_ft_lacp_statistics_change_members(topology, step):
    hs1 = topology.get('hs1')
    hs2 = topology.get('hs2')
    sw1 = topology.get('sw1')
    sw2 = topology.get('sw2')

    assert hs1 is not None, 'hs1 was not initialized'
    assert hs2 is not None, 'hs2 was not initialized'
    assert sw1 is not None, 'sw1 was not initialized'
    assert sw2 is not None, 'sw2 was not initialized'

    sw_real_ports = {
        sw1: [sw1.ports[port] for port in SW_LBL_PORTS],
        sw2: [sw2.ports[port] for port in SW_LBL_PORTS]
    }

    # Enable switches interfaces
    step_enable_switches_interfaces([sw1, sw2], step)

    # Add VLAN configuration to interconnection and workstation interfaces
    step_configure_vlans([sw1, sw2], sw_real_ports, step)

    # Configure workstations first VLAN
    step_configure_workstations([hs1, hs2], VLANS_IDS[0], step)

    # Validate workstations can communicate
    step_validate_connectivity([hs1, hs2], VLANS_IDS[0], True, step)

    # Transmit iperf traffic
    step_transmit_iperf_traffic([sw1, sw2], [hs1, hs2], VLANS_IDS[0], step)

    # Change host interfaces to second VLAN
    step_change_host_int_to_vlan(
        [sw1, sw2],
        sw_real_ports,
        VLANS_IDS[1],
        step
    )

    # Change workstations configuration
    step_configure_workstations([hs1, hs2], VLANS_IDS[1], step)

    # Validate workstations can communicate
    step_validate_connectivity([hs1, hs2], VLANS_IDS[1], True, step)

    # Transmit iperf traffic
    step_transmit_iperf_traffic([sw1, sw2], [hs1, hs2], VLANS_IDS[1], step)

    # Change host interfaces to third VLAN
    step_change_host_int_to_vlan(
        [sw1, sw2],
        sw_real_ports,
        VLANS_IDS[2],
        step
    )

    # Change workstations configuration
    step_configure_workstations([hs1, hs2], VLANS_IDS[2], step)

    # Validate workstations can communicate
    step_validate_connectivity([hs1, hs2], VLANS_IDS[2], True, step)

    # Transmit iperf traffic
    step_transmit_iperf_traffic([sw1, sw2], [hs1, hs2], VLANS_IDS[2], step)

    # Configure dynamic LAGs with no members on 1 switch
    step_configure_lag(sw1, step)

    # Modify configuration of interfaces in LAG and verify
    step_change_lag_members(sw1, sw_real_ports, step)
