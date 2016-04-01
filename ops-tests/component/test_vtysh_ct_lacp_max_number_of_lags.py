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

TOPOLOGY = """
#
# +-------+
# |  sw1  |
# +-------+
#

# Nodes
[type=openswitch name="Switch 1"] sw1
"""


def test_lacp_max_number_lags(topology, step):
    sw1 = topology.get('sw1')

    assert sw1 is not None

    step('### Test max number of LAGs allowed ###')
    max_lag = 256
    sw1('configure terminal')

    # Create allowed LAGs
    for lag_num in range(1, max_lag + 1):
        sw1('interface lag %d' % lag_num)

    out = sw1('do show running-config')
    lines = out.split('\n')

    # Check if all LAGs were created
    total_lag = 0
    for line in lines:
        if 'interface lag ' in line:
            total_lag += 1

    assert total_lag is max_lag

    # Crate LAG 257
    out = sw1('interface lag %d' % (max_lag + 1))

    assert "Cannot create LAG interface." in out
