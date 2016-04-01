# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

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


def test_lacp_cli(topology, step):
    sw1 = topology.get('sw1')

    assert sw1 is not None

    step('### Test to create LAG Port ###')
    sw1('configure terminal')
    sw1('interface lag 1')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert "lag1" in out

    step('### Test Show lacp aggregates command ###')
    sw1('interface lag 2')
    out = sw1('do show lacp aggregates')

    assert "lag2" in out

    step('### Test to delete LAG port ###')
    sw1('interface lag 3')
    sw1('exit')
    sw1('interface 10')
    sw1('lag 3')
    sw1('exit')
    sw1('no interface lag 3')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert "lag3" not in out

    out = sw1('do show running')

    assert "lag3" not in out

    step('### Test to add interfaces to LAG ports ###')
    sw1('interface 1')
    sw1('lag 1')
    sw1('interface 2')
    sw1('lag 1')
    sw1('interface 3')
    sw1('lag 2')
    sw1('interface 4')
    sw1('lag 2')
    out = sw1('do show lacp aggregates')

    assert "Aggregated-interfaces" in out and '3' in out and '4' in out

    step('### Test global LACP commands ###')
    sw1('lacp system-priority 999')
    out = sw1('ovs-vsctl list system', shell='bash')

    assert 'lacp-system-priority="999"' in out

    step('### Test LAG Load balancing for L2, L2+VID, L3 and L4 ###')
    sw1('interface lag 1')
    sw1('hash l2-src-dst')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert 'bond_mode="l2-src-dst"' in out

    out = sw1('do show running-config')

    assert 'hash l2-src-dst' in out

    out = sw1('do show running interface lag1')

    assert 'hash l2-src-dst' in out

    out = sw1('do show lacp aggregates')

    assert re.search("(Hash\s+: l2-src-dst)", out) is not None

    sw1('interface lag 1')
    sw1('hash l2vid-src-dst')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert 'bond_mode="l2vid-src-dst"' in out

    out = sw1('do show running-config')

    assert 'hash l2vid-src-dst' in out

    out = sw1('do show running interface lag1')

    assert 'hash l2vid-src-dst' in out

    out = sw1('do show lacp aggregates')

    assert re.search("(Hash\s+: l2vid-src-dst)", out) is not None

    sw1('interface lag 1')
    sw1('hash l3-src-dst')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert 'bond_mode=' not in out

    out = sw1('do show running-config')

    assert "hash l3-src-dst" not in out

    out = sw1('do show running interface lag1')

    assert "hash l3-src-dst" not in out

    out = sw1('do show lacp aggregates')

    assert re.search("(Hash\s+: l3-src-dst)", out) is not None

    sw1('interface lag 1')
    sw1('hash l4-src-dst')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert 'bond_mode="l4-src-dst"' in out

    out = sw1('do show running-config')

    assert "hash l4-src-dst" in out

    out = sw1('do show running interface lag1')

    assert "hash l4-src-dst" in out

    out = sw1('do show lacp aggregates')

    assert re.search("(Hash\s+: l4-src-dst)", out) is not None

    step('### Test LAG context commands ###')
    sw1('interface lag 1')
    sw1('lacp mode active')
    sw1('lacp fallback')
    sw1('hash l2-src-dst')
    sw1('lacp rate fast')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert re.search("(lacp * : active)", out) is not None and \
        'lacp-fallback-ab="true"' in out and \
        'bond_mode="l2-src-dst"' in out and \
        'lacp-time=fast' in out

    # Test "no" forms of commands
    sw1('no lacp mode active')
    sw1('no lacp fallback')
    sw1('no lacp rate fast')
    out = sw1('ovs-vsctl list port', shell='bash')

    assert re.search("(lacp * : active)", out) is None and \
        'lacp-fallback-ab' not in out and \
        'lacp-time' not in out

    step('### Test lacp port-id commands ###')
    test_interface = 1
    test_port_id = 999
    test_commands = ["no lacp port-id",
                     "no lacp port-id %s" % test_port_id]

    # Configure port-id
    sw1("interface %s" % test_interface)

    for command in test_commands:
        sw1('lacp port-id %s' % test_port_id)

        # Verify if lacp port-id was modified within DB
        out = sw1('ovs-vsctl list interface %s' % test_interface, shell='bash')

        assert 'other_config' in out and \
            'lacp-port-id="%s"' % test_port_id in out

        sw1(command)

        # Validate if lacp port-id was removed from DB
        out = sw1('ovs-vsctl list interface %s' % test_interface, shell='bash')

        assert 'other_config' in out and \
            'lacp-port-id="%s"' % test_port_id not in out

    # Check that command fails when port-id does not exist
    out = sw1(test_commands[0])

    assert "Command failed" not in out

    out = sw1(test_commands[1])

    assert "Command failed" in out

    step('### Test interface set port-priority command ###')
    test_interface = 1
    test_port_priority = 111
    test_commands = ["no lacp port-priority",
                     "no lacp port-priority %s" % test_port_priority]

    sw1("interface 1")

    for command in test_commands:
        sw1('lacp port-priority %s' % test_port_priority)

        out = sw1('ovs-vsctl list interface %s' % test_interface, shell='bash')

        assert 'other_config' in out and \
            'lacp-port-priority="%s"' % test_port_priority in out

        sw1(command)

        out = sw1('ovs-vsctl list interface %s' % test_interface, shell='bash')

        assert 'other_config' in out and \
            'lacp-port-priority="%s"' % test_port_priority not in out

    # Check that command fails when port-id does not exist
    out = sw1(test_commands[0])

    assert "Command failed" not in out

    out = sw1(test_commands[1])

    assert "Command failed" in out

    step('### Test show interface lag brief command ###')
    # Configure lag with undefined mode
    sw1("interface lag 3")

    # Configure lag in passive mode
    sw1("interface lag 4")
    sw1('lacp mode passive')

    # Configure lag in active mode
    sw1("interface lag 5")
    sw1('lacp mode active')

    # Verify show interface brief shows the lags created before
    out = sw1('do show interface brief')

    assert re.search("(lag3[\s-]+auto)", out) is not None and \
        re.search("(lag4[\s-]+passive[\s-]+auto)", out) is not None and \
        re.search("(lag5[\s-]+active[\s-]+auto)", out) is not None

    # Verify show interface lag4 brief shows only lag 4
    out = sw1('do show interface lag4 brief')

    assert re.search("(lag4[\s-]+passive[\s-]+auto)", out) is not None and \
        'lag1' not in out and 'lag2' not in out and \
        'lag3' not in out and 'lag5' not in out

    step('### Test show interface lag transceiver command ###')
    out = sw1('do show interface lag5 transceiver')

    assert 'Invalid switch interface ID.' in out

    step('### Test show interface lag command ###')
    # Verify 'show interface lag1' shows correct  information about lag1
    out = sw1("do show interface lag1")

    assert "Aggregate-name lag1" in out and \
        "Aggregated-interfaces : " in out and \
        "Aggregate mode : off" in out and \
        "Speed 0 Mb/s" in out and \
        "Aggregation-key : 1" in out

    # Verify 'show interface lag4' shows correct  information about lag4
    out = sw1("do show interface lag4")

    assert "Aggregate-name lag4" in out and \
        "Aggregated-interfaces : " in out and \
        "Aggregate mode : passive" in out and \
        "Speed 0 Mb/s" in out

    # Verify 'show interface lag5' shows correct  information about lag5
    out = sw1("do show interface lag5")

    assert "Aggregate-name lag5" in out and \
        "Aggregated-interfaces : " in out and \
        "Aggregate mode : active" in out and \
        "Speed 0 Mb/s" in out

    out = sw1("do show lacp interface")

    assert "Actor details of all interfaces:" in out and \
        re.search(
            "(Intf Aggregate Port\s+Port\s+Key\s+"
            "State\s+System-id\s+System\s+Aggr)",
            out) is not None and \
        re.search("(name\s+id\s+Priority\s+Priority Key)", out) \
        is not None and \
        "Partner details of all interfaces:" in out and \
        re.search("(1\s+lag1)", out) is not None and \
        re.search("(2\s+lag1)", out) is not None and \
        re.search("(3\s+lag2)", out) is not None and \
        re.search("(4\s+lag2)", out) is not None
