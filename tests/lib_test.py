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
#

import pytest
from opstestfw import *
from opstestfw.switch.CLI import *
from opstestfw.host import *
import re
import pexpect
import random
import time
from math import ceil
from math import floor
from datetime import timedelta


def expecting(expectHndl, command):
    '''
    Wraps the process of sending a command to a device CLI and expecting
    an output as long as the CLI always has a '#' character on the prompt

    Args:
        expectHndl (object): pexpect handler
        command (str): Command to be sent through pexpect handler

    Returns:
        bool: True if received prompt, False if timeouts after 20 seconds
    '''
    expectHndl.sendline(command)
    if expectHndl.expect(['#', pexpect.TIMEOUT], timeout=20) != 0:
        LogOutput(
            'error',
            'Timeout while waiting for output of command: %s' % command)
        return False
    return True


def switchTcpdumpInterfaces(deviceObj):
    '''
    Obtains the equivalent names of active interfaces for use with tcpdump

    Mainly used by lagVerifyTrafficFlow

    Args:
        deviceObj (Switch): Switch with active interfaces

    Returns:
        bool, dict: True and dictionary of with keys being the real interfaces
            of switch and the values what tcpdump understands. True and None
            otherwise
    '''

    expectHndl = deviceObj.expectHndl

    res = {}
    if not expecting(expectHndl, 'sudo tcpdump -D'):
        return False, None
    for result in re.findall(r'(\d+)[.](\d+)', expectHndl.before):
        res[result[1]] = result[0]
    return True, res


def deviceStartWiresharkCap(device, deviceLink, filter=None):
    '''
    Initiates a tcpdump capture on a device link on the background
    The capture output is sent to a temporal file

    Mainly used by lagVerifyTrafficFlow

    Args:
        device (Device): Device on which a capture is started
        deviceLink (str): Interface on device to start capture
            Note this is the interface name tcpdump understands
            See switchTcpdumpInterfaces function for more information
        filter (str, optional): Filter for tcpdump to use

    Returns:
        int: Returns process ID of capture on device.
            None if not able to get it
    '''
    expectHndl = device.expectHndl
    command = 'tcpdump -i %s' % deviceLink
    if filter:
        command += ' %s' % filter
    command += ' 1>/tmp/cap%s.test 2>&1 &' % deviceLink
    expecting(expectHndl, command)
    res = re.search(r'\[\d+\] (\d+)', expectHndl.before)
    if res:
        return int(res.group(1))
    else:
        return None


def deviceStopWiresharkCap(device,
                           processId,
                           deviceLink,
                           filter=None,
                           filteresSwitch=None):
    '''
    Stops tcpdump capture on device and reads obtained information
    from temporal file

    Mainly used by lagVerifyTrafficFlow

    Args:
        device (Device): Device on which a capture was started
        processId (int): Process number of capture on device's system
        deviceLink (str): Interface on device in whcih capture was started
            Note this is the interface name tcpdump understands
            See switchTcpdumpInterfaces function for more information
        filter (str, optional): Filter expression to look for desired packets
            in capture
        filteresSwitch (str, optional): Second filter expression

    Returns:
        dict: Dictionary with parsed information
            filtered (int): Number of filtered packets if a filter was
                defined in deviceStartWiresharkCap
            total (int): Total number of packets capture
            filtered_matches (int, optional): Number of packets matching
                filter argument
            filtered_matches2 (int, optional): Number of packets matching
                filteresSwitch argument
            raw (str): Raw output obtained from capture
    '''
    expectHndl = device.expectHndl
    expecting(expectHndl, 'kill %d' % int(processId))
    time.sleep(1)
    for i in xrange(0, 2):
        expecting(expectHndl, '')
    expecting(expectHndl, 'cat /tmp/cap%s.test' % deviceLink)
    res = {}

    try:
        match = re.search(
            r'(\d+) packets received by filter', expectHndl.before)
        if match:
            res['filtered'] = match.group(1)
        else:
            res['filtered'] = 0
        match = re.search(r'(\d+) packets captured', expectHndl.before)
        if match:
            res['total'] = match.group(1)
        else:
            res['total'] = 0
        if filter:
            match = re.findall(filter, expectHndl.before)
            if match:
                res['filtered_matches'] = len(match)
            else:
                res['filtered_matches'] = 0
        if filteresSwitch:
            match = re.findall(filteresSwitch, expectHndl.before)
            if match:
                res['filtered_matches2'] = len(match)
            else:
                res['filtered_matches2'] = 0
        res['raw'] = expectHndl.before
    except Exception as e:
        LogOutput('error',
                  'Error while deciphering packets ' +
                  'obtained by Wireshark for device %s' %
                  str(device.device))
        LogOutput('error', 'Exception:\n%s' % e)
        return None
    return res


def deviceObtainActiveMacAddresses(device, links):
    '''
    Creates a list with all the MAC addresses used by a devices in
    the links of interest

    Since the device can either be a switch or a workstation, it is
    up to the user of this function to handle device contexts correctly

    Args:
        device (object): Device to which the MAC addresses will be obtained
        links (list[str]): List of links as defined in topology (ie: lnk01)
            that belong to the device

    Returns:
        list[str]: List of MAC address on all devices' links of interest
    '''
    macList = []
    expectHndl = device.expectHndl
    expecting(expectHndl, 'ifconfig')
    for link in links:
        try:
            macList.append(
                re.search(r'%s.*?(\w{2}'
                          % device.linkPortMapping[link] +
                          r':\w{2}:\w{2}' +
                          r':\w{2}:\w{2}:\w{2})',
                          expectHndl.before).group(1).upper())
        except AttributeError:
            return None
    return macList


def swtichGetIntoVtyshOrSwns(device, enter=True):
    '''
    Normalizes device prompt so it can be handled by standard framework
    functions or enters switch bash context

    Mainly used by lagVerifyTrafficFlow

    Args:
        device (dict): Information of device
        enter (bool, optional): Controls whether the function attempts
            to normalize the device prompt or get to switch bash context

    Returns:
        bool: True if managed to get into VTYSH or into switch bash
            context, False otherwise
    '''

    expectHndl = device.expectHndl

    if enter:
        if not expecting(expectHndl, 'exit'):
            LogOutput(
                'error', 'Could not return to VTYSH on device %s' %
                device.device)
            return False
        if not expecting(expectHndl, 'vtysh'):
            LogOutput(
                'error', 'Could not return to VTYSH on device %s' %
                device.device)
            device.deviceContext = 'linux'
            return False
    else:
        if device.deviceContext != 'vtyShell':
            retStruct = device.VtyshShell(enter=True)
            if retStruct.returnCode() != 0:
                LogOutput('error', 'Could not enter vtysh on device %s' %
                          device.device)
                return False
        if not expecting(expectHndl, 'exit'):
            LogOutput('error', 'Could not exit vtysh context on device' +
                      ' %s' % device.device)
            return False
        if not expecting(expectHndl, 'ip netns exec swns bash'):
            LogOutput('error', 'Could not enter switch bash context on' +
                      ' device %s' % device.device)
            device.deviceContext = 'linux'
            return False
    return True

def lagCheckOwnership(dut, lagId, interfaces, dutCheckNumberMatch=True):
    '''
    Verifies if a group of interfaces are part of a LAG. Optionally the
    function also verify if there are more or less links in the LAG than
    passed as argument

    Args:
        dut (object): Device to test
        lagId (str): Name of LAG as in OVS. Eg: lag1
        interfaces (list[str]): List of interfaces part of the LAG
        dutCheckNumberMatch (bool, optional): When True, the function
            verifies if the number of interfaces is exactly as reported
            by OVS before proceeding to verify if the interfaces themselves
            are indeed part of the LAG. Otherwise the function only verifies
            if the interfaces are part of the LAG

    Returns:
        bool: True if all the interfaces are part of the LAG, False otherwise

    '''
    if not expecting(dut.expectHndl, 'ovs-vsctl get port %s' % lagId +
                     ' interfaces'):
        LogOutput('error', 'Could not get the interfaces in %s' %
                  str(lagIg) + ' on device %s' % dut.device)
        return False

    if re.search(r'no row "%s"' % lagId, dut.expectHndl.before):
        LogOutput('error', '%s does not exist' % lagId)
        return False

    lagUuidInterfaces = re.search(r'\[(.*)\]',
                                  dut.expectHndl.before).group(1)
    lagUuidInterfaces = lagUuidInterfaces.split(', ')

    if (dutCheckNumberMatch and len(lagUuidInterfaces) != len(interfaces)
            and lagUuidInterfaces[0] != ''):
        LogOutput('error', 'The number of interfaces in %s on ' % lagId +
                  'device %s is different from the number of interfaces to' %
                  dut.device + ' evaluate')
        LogOutput('error', 'Expected interfaces: %d' % len(lagUuidInterfaces))
        LogOutput('error', 'Interfaces to evaluate: %d' % len(interfaces))
        return False

    for interface in interfaces:
        if not expecting(dut.expectHndl, 'ovs-vsctl get interface %s' %
                         interface + ' _uuid'):
            LogOutput('error', 'Could not obtain interface %s' % interface +
                      ' information on device %s' % dut.device)
            return False
        interfaceUuid = re.search(
            r'(([a-z0-9]+-?){5})\r', dut.expectHndl.before).group(1)
        if interfaceUuid not in lagUuidInterfaces:
            LogOutput('error', 'Interface %s is not present' % interface +
                      ' on %s on device %s' % (lagId, dut.device))
            return False
    LogOutput('debug', '%d interfaces have been ' % len(interfaces) +
              'accounted for in %s as expected' % lagId)
    return True


def lagCheckLACPStatus(dut01, interfaceLag):

    # Recover LACP information from OVS from specific LAG

    # Variables
    overallBuffer = []
    bufferString = ""
    command = ""
    returnCode = 0

    if dut01 is None:
        LogOutput('error', "Need to pass switch dut01 to this routine")
        returnCls = returnStruct(returnCode=1)
        return returnCls

    # Get into vtyshelll
    returnStructure = dut01.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    ###########################################################################
    # Exit vtysh context and validate buffer with information
    ###########################################################################

    value = expecting(dut01.expectHndl, 'exit')
    dut01.deviceContext = 'linux'
    overallBuffer.append(dut01.expectHndl.before)
    if not value:
        LogOutput('error', 'Unable to exit vtysh context')
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    command = "ovs-vsctl list port " + str(interfaceLag)
    LogOutput('info', "Show LACP status " + command)
    returnDevInt = dut01.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])

    if retCode != 0:
        LogOutput('error', "Failed to get information ." + command)

    ###########################################################################
    # Analyze obtained information
    ###########################################################################

    for curLine in overallBuffer:
        bufferString += str(curLine)
    lacpStatus = dict()
    lacpElements = re.search(
        r'lacp_status\s*:\s*{bond_speed="(\d*)",\s*bond_status=' +
        '(\w*)(,\s*bond_status_reason=".*")?}', bufferString)

    lacpStatus['bond_speed'] = lacpElements.group(1)
    lacpStatus['bond_status'] = lacpElements.group(2)
    if lacpElements.group(3):
        lacpStatus['bond_reason'] = re.search(
            r'="(.*)"', lacpElements.group(3)).group(1)
    else:
        lacpStatus['bond_reason'] = None

    return lacpStatus


def lagCheckLACPInterfaceStatus(dut01, interface):

    # Recover vlan information from running config from specific VLAN
    # Variables
    overallBuffer = []
    bufferString = ""
    command = ""
    returnCode = 0

    if dut01 is None:
        LogOutput('error', "Need to pass switch dut01 to this routine")
        returnCls = returnStruct(returnCode=1)
        return returnCls

    # Get into vtyshelll
    returnStructure = dut01.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    ###########################################################################
    # Exit vtysh and obtain information
    ###########################################################################
    value = expecting(dut01.expectHndl, 'exit')
    dut01.deviceContext = 'linux'
    overallBuffer.append(dut01.expectHndl.before)
    if not value:
        LogOutput('error', 'Unable to exit vtysh context')
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=1, buffer=bufferString)
        return returnCls

    command = "ovs-vsctl list interface " + str(interface)
    LogOutput('info', "Show LACP status in interface" + command)
    returnDevInt = dut01.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])

    if retCode != 0:
        LogOutput('error', "Failed to get information ." + command)

    ###########################################################################
    # Validate buffer with information
    ###########################################################################

    for curLine in overallBuffer:
        bufferString += str(curLine)

    lacpInterfaceStatus = dict()
    lacpInterfaceElements = re.search(
        r'lacp_current\s*:\s(.*?)\r', bufferString)

    lacpInterfaceStatus['lacp_current'] = lacpInterfaceElements.group(1)

    lacpInterfaceElements = re.search(
        r'actor_key="(\d*)"\s*', bufferString)
    lacpInterfaceStatus['actor_key'] = lacpInterfaceElements.group(1)

    lacpInterfaceElements = re.search(
        r'actor_port_id="(\d*,\d*)"', bufferString)
    lacpInterfaceStatus['actor_port_id'] = lacpInterfaceElements.group(1)

    lacpInterfaceElements = re.search(
        r'actor_state="Activ:(\d*),TmOut:(\d*),Aggr:(\d*),Sync:(\d*),' +
        'Col:(\d*),Dist:(\d*),Def:(\d*),Exp:(\d*)"', bufferString)

    actorFlags = dict()
    actorFlags['Activ'] = lacpInterfaceElements.group(1)
    actorFlags['TmOut'] = lacpInterfaceElements.group(2)
    actorFlags['Aggr'] = lacpInterfaceElements.group(3)
    actorFlags['Sync'] = lacpInterfaceElements.group(4)
    actorFlags['Col'] = lacpInterfaceElements.group(5)
    actorFlags['Dist'] = lacpInterfaceElements.group(6)
    actorFlags['Def'] = lacpInterfaceElements.group(7)
    actorFlags['Exp'] = lacpInterfaceElements.group(8)

    lacpInterfaceStatus['actor_state'] = actorFlags

    lacpInterfaceElements = re.search(
        r'actor_system_id="(\d*,.{2}:.{2}:.{2}:.{2}:.{2}:.{2})"', bufferString)
    lacpInterfaceStatus['actor_system_id'] = lacpInterfaceElements.group(1)

    lacpInterfaceElements = re.search(
        r'partner_key="(\d*)"\s*', bufferString)
    lacpInterfaceStatus['partner_key'] = lacpInterfaceElements.group(1)

    lacpInterfaceElements = re.search(
        r'partner_port_id="(\d*,\d*)"', bufferString)
    lacpInterfaceStatus['partner_port_id'] = lacpInterfaceElements.group(1)

    lacpInterfaceElements = re.search(
        r'partner_state="Activ:(\d*),TmOut:(\d*),Aggr:(\d*),Sync:(\d*),' +
        'Col:(\d*),Dist:(\d*),Def:(\d*),Exp:(\d*)"', bufferString)

    partnerFlags = dict()
    partnerFlags['Activ'] = lacpInterfaceElements.group(1)
    partnerFlags['TmOut'] = lacpInterfaceElements.group(2)
    partnerFlags['Aggr'] = lacpInterfaceElements.group(3)
    partnerFlags['Sync'] = lacpInterfaceElements.group(4)
    partnerFlags['Col'] = lacpInterfaceElements.group(5)
    partnerFlags['Dist'] = lacpInterfaceElements.group(6)
    partnerFlags['Def'] = lacpInterfaceElements.group(7)
    partnerFlags['Exp'] = lacpInterfaceElements.group(8)

    lacpInterfaceStatus['partner_state'] = partnerFlags

    lacpInterfaceElements = re.search(
        r'partner_system_id="(\d*,.{2}:.{2}:.{2}:.{2}:.{2}:.{2})"',
        bufferString)
    lacpInterfaceStatus['partner_system_id'] = lacpInterfaceElements.group(1)

    return lacpInterfaceStatus


# Verify LACP status & flagging


def lagVerifyLACPStatusAndFlags(dut01,
                                dut02,
                                lacpActive,
                                lagLinks,
                                lag01,
                                lag02,
                                status='ok',
                                dut01Flags={'Activ': '1',
                                            'TmOut': '1',
                                            'Aggr': '1',
                                            'Sync': '1',
                                            'Col': '1',
                                            'Dist': '1',
                                            'Def': '0',
                                            'Exp': '0'},
                                dut02Flags={'Activ': '1',
                                            'TmOut': '1',
                                            'Aggr': '1',
                                            'Sync': '1',
                                            'Col': '1',
                                            'Dist': '1',
                                            'Def': '0',
                                            'Exp': '0'},
                                dut01LnksKeys=None, dut02LnksKeys=None,
                                dut01PortIds=None, dut02PortIds=None,
                                dut01LnkPriorities=None,
                                dut02LnkPriorities=None,
                                dut01LACPCurrentVals=None,
                                dut02LACPCurrentVals=None,
                                dut01LnkCheckNumberMatch=True,
                                dut02LnkCheckNumberMatch=True):
    '''
    Validates the LACP configuration is established on both ends of a LAG

    Args:
        dut01 (object): First member of LAG
        dut02 (object): Second member of LAG
        lacpActive (bool): Flag indicating if LAG is using LACP or not
        lagLinks (list[str]): List of links in the topology which are part
            of the LAG
        lag01 (str): Name of LAG in first switch
        lag02 (str): Name of LAG in second switch
        status (str, optional): Expected status of LAG in both switches
            Default: ok
        dut01Flags (ditc[str]): Dictionary containing the LACP flags which
            are expected the first switch to be advertising to its partner
        dut02Flags (ditc[str]): Dictionary containing the LACP flags which
            are expected the second switch to be advertising to its partner
        dut01LnksKeys (list[str]): List of keys the ports members of a LAG
            are expected to have. There should be 1 per port in LAG. If a
            value in the list is None, the key 1 is utilized
            Default: None
        dut02LnksKeys (list[str], optional): List of keys the ports members
            of a LAG are expected to have. There should be 1 per port in
            LAG. If a value in the list is None, the key 1 is utilized
            Default: None
        dut01PortIds (list[str], optional): List of port IDs used by the ports
            members of the LAG. There should be 1 per port in LAG. If a value
            in the list is None, it is not checked
            Default: None
        dut02PortIds (list[str], optional): List of port IDs used by the ports
            members of the LAG. There should be 1 per port in LAG. If a value
            in the list is None, it is not checked
            Default: None
        dut01LnkPriorities (list[str], optional): List of port priorities used
            by members of LAG. There should be 1 per port in LAG. If a value
            in the list is None, the priority by default is 1
            Default: None
        dut01LnkPriorities (list[str], optional): List of port priorities used
            by members of LAG. There should be 1 per port in LAG. If a value
            in the list is None, the priority by default is 1
            Default: None
        dut01LACPCurrentVals (list[str], optional): List of current status of
            LACP on each interface. There should be 1 per port in LAG. If a
            value in the list is None, the default value is true
            Default: None
        dut02LACPCurrentVals (list[str], optional): List of current status of
            LACP on each interface. There should be 1 per port in LAG. If a
            value in the list is None, the default value is true
            Default: None
        dut01LnkCheckNumberMatch (bool, optional): If True, the function will
            check if the number of links inserted into the function for dut01
            is the total number configured on the LAG. Otherwise, the function
            will only check if the links passed are part of the LAG
        dut02LnkCheckNumberMatch (bool, optional): If True, the function will
            check if the number of links inserted into the function for dut02
            is the total number configured on the LAG. Otherwise, the function
            will only check if the links passed are part of the LAG

        Returns:
            bool: True if information matches, False otherwise
    '''
    # variable initialization
    dut01LACPStatus = {}
    dut02LACPStatus = {}
    dut01LACPInterfacesStatus = []
    dut02LACPInterfacesStatus = []
    duts = [{'dut': dut01, 'lag': lag01, 'lacp_status': dut01LACPStatus,
             'lacp_interfaces': dut01LACPInterfacesStatus,
             'flags': dut01Flags, 'keys': dut01LnksKeys, 'ids': dut01PortIds,
             'priorities': dut01LnkPriorities,
             'lacp_currents': dut01LACPCurrentVals,
             'check_lnk_numbers': dut01LnkCheckNumberMatch},
            {'dut': dut02, 'lag': lag02, 'lacp_status': dut02LACPStatus,
             'lacp_interfaces': dut02LACPInterfacesStatus,
             'flags': dut02Flags, 'keys': dut02LnksKeys, 'ids': dut02PortIds,
             'priorities': dut02LnkPriorities,
             'lacp_currents': dut02LACPCurrentVals,
             'check_lnk_numbers': dut02LnkCheckNumberMatch}]

    '''
    Attempt to retrieve LACP information
    It should fail when LACP is disabled and succeed otherwise
    '''

    LogOutput('info', 'Verify ownership of LAGs on interfaces')
    for dut in duts:
        LogOutput('info', 'Device: %s....' % dut['dut'].device)
        interfaces = [dut['dut'].linkPortMapping[interface] for interface
                      in lagLinks]
        if not lagCheckOwnership(dut['dut'], dut['lag'], interfaces,
                                 dutCheckNumberMatch=dut['check_lnk_numbers']):
            return False
    LogOutput('info', 'All member interfaces correctly accounted')
    LogOutput(
        'info', 'Attempt to retrieve LACP information for all switches ' +
        'interfaces')
    for dut in duts:
        LogOutput('info', 'Device: %s....' % dut['dut'].device)
        try:
            dut['lacp_status'] = lagCheckLACPStatus(dut['dut'], dut['lag'])
            if not lacpActive:
                LogOutput('error', 'LACP status information detected on ' +
                          'device %s with LACP disabled' % dut['dut'].device)
                return False
        except AttributeError as e:
            # Validation in case the LAG has no interfaces yet
            if len(lagLinks) == 0:
                dut['lacp_status'] = None
                LogOutput('debug', 'No links are present yes on %s and it ' %
                          dut['lag'] + 'is not possible to get its ' +
                          'information even if it is dynamic or static')
                continue
            # Normal validation
            if lacpActive:
                LogOutput('error', 'Could not verify LACP status for LAG' +
                          ' %s in device %s' %
                          (dut['lag'], dut['dut'].device))
                LogOutput('debug', 'Exception: %s' % str(e))
                return False
        for lagLink in lagLinks:
            try:
                stat = lagCheckLACPInterfaceStatus(dut['dut'],
                                                   dut['dut'].linkPortMapping
                                                   [lagLink])
                if not lacpActive:
                    LogOutput('error', 'Obtained LACP status on interface ' +
                              '%s from device %s when LACP is disabled' %
                              (dut['dut'].linkPortMapping[lagLink],
                               dut['dut'].device))
                    return False
                dut['lacp_interfaces'].append(stat)
            except AttributeError as e:
                if lacpActive:
                    LogOutput('error', 'Could not verify LACP interface ' +
                              'status for LAG %s interface %s in device %s' %
                              (dut['lag'],
                               dut['dut'].linkPortMapping[lagLink],
                               dut['dut'].device))
                    LogOutput('debug', 'Exception: %s' % str(e))
                    return False

# If LACP is not active and we got here, there is nothing else to do
    if not lacpActive:
        LogOutput('info', 'No LACP information obtained as expected from' +
                  ' static LAGs')
        return True

# Validate LACP is up and information is consistent between partners

    LogOutput('info', 'Analyze obtained LACP information')
    for i, dut in enumerate(duts, 0):
        LogOutput('info', 'Device: %s....' % dut['dut'].device)
        # Validate LAG LACP status
        if dut['lacp_status'] and dut['lacp_status']['bond_status'] != status:
            LogOutput('error', 'Unexpected LACP status for device ' +
                      '%s: %s  %s' % (dut['dut'].device,
                                      dut['lacp_status'],
                                  dut['lacp_status']['bond_status']))
            LogOutput('error', 'Expected: %s' % status)
            return False
# If there are no interfaces on LAG, there is nothing to gain
# past this point
        if len(lagLinks) == 0:
            continue
        if i == 0:
            otherDut = duts[1]
        else:
            otherDut = duts[0]

# Get current system-id
        retStruct = lagpGlobalSystemShow(deviceObj=dut['dut'])
        if retStruct.returnCode() != 0:
            LogOutput('error', 'Could not obtain system-id for ' +
                      'verification on device %s' % dut['dut'].device)
            return False

        expectedSystemId = retStruct.valueGet()
        expectedSystemId['System-id'] = expectedSystemId['System-id'].lower()

        # Validate LACP information

        for k, (ints1, ints2) in enumerate(zip(dut['lacp_interfaces'],
                                               otherDut['lacp_interfaces']),
                                           0):
            # Validate system id locally
            id = re.search(
                r'\d+,(([0-9a-fA-F]{1,2}:?){6})',
                ints1['actor_system_id']).group(1)
            if (id != expectedSystemId['System-id']):
                LogOutput('error', 'System-id of device does not match ' +
                          'expected value')
                LogOutput('error', 'Expected: %s' %
                          expectedSystemId['System-id'])
                LogOutput('error', 'Actual: %s' % ints1['actor_system_id'])
                return False

            # Validate system id is correctly sent
            id2 = re.search(
                r'\d+,(([0-9a-fA-F]{1,2}:?){6})',
                ints2['partner_system_id']).group(1)
            if id != id2:
                LogOutput('error', 'Actor system-id does not match value sent')
                LogOutput('error', 'Device: %s' % dut['dut'].device)
                LogOutput('error', 'System-id: %s' % id)
                LogOutput('error', 'System-id sent: %s' % id2)
                return False

            # Validate system priority locally
            id = re.search(
                r'(\d+),([0-9a-fA-F]{1,2}:?){6}',
                ints1['actor_system_id']).group(1)
            if (id != str(expectedSystemId['System-priority'])):
                LogOutput('error', 'System-priority of device does not ' +
                          'match expected value')
                LogOutput('error', 'Expected: %s' %
                          str(expectedSystemId['System-priority']))
                LogOutput('error', 'Actual: %s' % ints1['actor_system_id'])
                return False

            # Validate system priority is correctly sent
            id2 = re.search(
                r'(\d+),([0-9a-fA-F]{1,2}:?){6}',
                ints2['partner_system_id']).group(1)
            if id != id2:
                LogOutput(
                    'error', 'Actor system-priority does not match ' +
                    'value sent')
                LogOutput('error', 'Device: %s' % dut['dut'].device)
                LogOutput('error', 'System-priority: %s' % id)
                LogOutput('error', 'System-priority sent: %s' % id2)
                return False

            # Validate locally the port-id

            id = re.search(r'\d+,(\d+)', ints1['actor_port_id']).group(1)
            if dut['ids'] and dut['ids'][k]:
                expected = dut['ids'][k]
            else:
                expected = id

            if expected != id:
                LogOutput('error', 'Actor port id on device ' +
                          '%s does not match expected' %
                          dut['dut'].device)
                LogOutput('error', 'Expected: %s' % expected)
                LogOutput('error', 'Actual: %s' % id)
                return False

            # Validate the port-id is passed to other device
            id2 = re.search(r'\d+,(\d+)', ints2['partner_port_id']).group(1)
            if id != id2:
                LogOutput('error', 'Actor port-id does not match value sent')
                LogOutput('error', 'Device: %s' % dut['dut'].device)
                LogOutput('error', 'Port-id: %s' % id)
                LogOutput('error', 'Port-id sent: %s' % id2)
                return False

            # Validate locally the port priority
            if dut['priorities'] and dut['priorities'][k]:
                expected = dut['priorities'][k]
            else:
                expected = 1

            priority = re.search(r'(\d+),\d+',
                                 ints1['actor_port_id']).group(1)
            if str(expected) != priority:
                LogOutput('error', 'Actor port priority on device ' +
                          '%s does not match expected' % dut['dut'].device)
                LogOutput('error', 'Expected: %s' % expected)
                LogOutput('error', 'Actual: %s' % priority)
                return False

            # Validate the port-priority is passed to other device
            priority2 = re.search(
                r'(\d+),\d+', ints2['partner_port_id']).group(1)
            if priority != priority2:
                LogOutput('error', 'Actor port-priority does not match ' +
                          'value sent')
                LogOutput('error', 'Device: %s' % dut['dut'].device)
                LogOutput('error', 'Port-priority: %s' % priority)
                LogOutput('error', 'Port-priority sent: %s' % priority2)
                return False

            # Validate locally the key
            if dut['keys'] and dut['keys'][k]:
                expected = dut['keys'][k]
            else:
                expected = 1

            if str(expected) != ints1['actor_key']:
                LogOutput('error', 'Actor key on device ' +
                          '%s does not match expected' % dut['dut'].device)
                LogOutput('error', 'Expected: %s' % expected)
                LogOutput('error', 'Actual: %s' % ints1['actor_key'])
                return False

            # Validate the key is passed to other device
            if ints1['actor_key'] != ints2['partner_key']:
                LogOutput('error', 'Actor key does not match ' +
                          'value sent')
                LogOutput('error', 'Device: %s' % dut['dut'].device)
                LogOutput('error', 'Key: %s' % ints1['actor_key'])
                LogOutput('error', 'Key sent: %s' % ints2['partner_key'])
                return False

            # Validate locally the lacp_current flag
            if dut['lacp_currents'] and dut['lacp_currents'][k]:
                expected = dut['lacp_currents'][k]
            else:
                expected = 'true'

            if expected != ints1['lacp_current']:
                LogOutput('error', 'Actor lacp_current flag on device ' +
                          '%s does not match expected' % dut['dut'].device)
                LogOutput('error', 'Expected: %s' % expected)
                LogOutput('error', 'Actual: %s' % ints1['lacp_current'])
                return False

            # Validate LACP interface status flags
            for key in ints1['actor_state']:
                if ints1['actor_state'][key] != dut['flags'][key]:
                    LogOutput('error', 'Unexpected LACP flag information')
                    LogOutput('error', 'Flag: %s' % key)
                    LogOutput('error', 'Device: %s' % dut['dut'].device)
                    LogOutput('error', 'Local status: %s' %
                              ints1['actor_state'][key])
                    LogOutput('error', 'Expected local status: %s' %
                              dut['flags'][key])
                    return False
                if ints1['actor_state'][key] != ints2['partner_state'][key]:
                    LogOutput('error', 'Difference in LACP information ' +
                              'betweeen partners')
                    LogOutput('error', 'Flag: %s' % key)
                    LogOutput('error', 'Device: %s' % dut['dut'].device)
                    LogOutput('error', 'Partner device: %s' %
                              otherDut['dut'].device)
                    LogOutput('error', 'Local status: %s' %
                              ints1['actor_state'][key])
                    LogOutput('error', 'Partner status: %s' %
                              ints2['partner_state'][key])
                    return False
    LogOutput('info', 'Finished analyzing LACP information with no ' +
              'unexpected results')
    return True


def lagVerifyConfig(
        deviceObj,
        lagId,
        interfaces=[],
        lacpMode='off',
        fallbackFlag=False,
        hashType='l3-src-dst',
        lacpFastFlag=True):
    '''
    Parse a LAG for configuration settings

    Args:
        deviceObj (PSwitch,VSwitch): Device from which configuration is
            verified
        lagId (str): LAG identifier
        interfaces (list[str], optional): A list of interfaces to
            verify if present (default: empty list)
        lacpMode (str, optional): LACP mode (default: off)
        fallbackFlag (bool, optional): Status of fallback flag
            (default: False)
        hashType (str, optional): Hashing algorithm employed
            (default: l3-src-dst)
        lacpFastFlag (bool, optional): Flag indicating if LAG uses fast
            heartbeat (detault: False)

    Returns:
        bool: True if configuration matches, False otherwise
    '''
    if not deviceObj or not lagId:
        LogOutput('error', "The device and LAG ID must be specified")
        return False
    LogOutput('debug', "Verifying LAG %s configuration..." % str(lagId))

    baseLag = {
        "interfaces": interfaces,
        "lacpMode": lacpMode,
        "fallbackFlag": fallbackFlag,
        "hashType": hashType,
        "lacpFastFlag": lacpFastFlag}
    otherConfigAttributes = {'lacp-fallback-ab': {'attr': 'fallbackFlag',
                                                  'value': False,
                                                  'meanings': {'true': True,
                                                               'false': False}
                                                  },
                             'bond_mode': {'attr': 'hashType', 'value':
                                           'l3-src-dst', 'meanings': None},
                             'lacp-time': {'attr': 'lacpFastFlag', 'value':
                                           True, 'meanings': {'fast': True,
                                                              'slow': False}}}

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        return False
    value = expecting(deviceObj.expectHndl, 'exit')
    deviceObj.deviceContext = 'linux'
    if not value:
        LogOutput('error', 'Unable to exit vtysh context')
        return False
    # Get information
    command = 'ovs-vsctl list port lag%s' % str(lagId)
    if not expecting(deviceObj.expectHndl, command):
        LogOutput('error', 'Unable to retrieve LAG %s information' %
                  str(lagId))
        return False

    # Name
    res = re.findall(r'name\s+?: "(lag%s+?)"' % str(lagId),
                     deviceObj.expectHndl.before)
    if len(res) == 0:
        LogOutput('error', 'Could not retrieve LAG %s information' %
                  str(lagId))
        return False
    # lacpMode
    res = re.findall(r'lacp\s+?: (active|passive|off|\[\])',
                     deviceObj.expectHndl.before)
    if len(res) == 0:
        LogOutput('error', 'Could not retrieve LACP mode')
        return False
    if res[0] == '[]':
        res[0] = 'off'
    if res[0] != baseLag['lacpMode']:
        LogOutput(
            'error',
            "Failure verifying LAG %s configuration " % str(lagId) +
            "configuration on attribute lacpMode")
        LogOutput(
            'error', "Found: %s - Expected: %s" %
            (res[0], baseLag['lacpMode']))
        return False

# Other attributes except interfaces
    res = re.findall(r'other_config\s+: {(.*?)}', deviceObj.expectHndl.before)
    if len(res) == 0:
        LogOutput('error', 'Could not retrieve fallback, hash and rate')
        return False
    if res[0] != '':
        text = re.sub(r'"', '', res[0])
        textList = text.split(', ')
        for element in textList:
            values = element.split('=')
            if otherConfigAttributes[values[0]]['meanings']:
                otherConfigAttributes[values[0]]['value'] =\
                    otherConfigAttributes[values[0]]['meanings'][values[1]]
            else:
                otherConfigAttributes[values[0]]['value'] = values[1]
    for key in otherConfigAttributes:
        if baseLag[otherConfigAttributes[key]['attr']] !=\
                otherConfigAttributes[key]['value']:
            LogOutput(
                'error',
                "Failure verifying LAG %s configuration " % str(lagId) +
                "configuration on attribute %s" %
                otherConfigAttributes[key]['attr'])
            LogOutput(
                'error', "Found: %s - Expected: %s" %
                (otherConfigAttributes[key]['value'],
                 str(baseLag[otherConfigAttributes[key]['attr']])))
            return False
# Interfaces
    if not lagCheckOwnership(deviceObj, 'lag%s' % str(lagId), interfaces):
        return False

    LogOutput(
        'info',
        "Verification of LAG %s configuration passed" % str(lagId))
    return True

# Parses the output of "show run" and verify that the config is empty.
# Returns True if the configuration is empty, False otherwise


def validateEmptyConfig(devices):
    for dev in devices:
        output = showRun(deviceObj=dev).buffer()
        ret_expression = re.search(
            r'Current configuration:\s*!\s*!\s*!\s*(.*)\s*exit',
            output,
            re.DOTALL
        )
        if ret_expression.group(1) != "":
            return False
    return True

# Reboots switch


def switchReboot(deviceObj):
    if not validateEmptyConfig([deviceObj]):
        # Reboot switch
        LogOutput('info', "Reboot switch " + deviceObj.device)
        deviceObj.Reboot()
    if not validateEmptyConfig([deviceObj]):
        return False
    return True


def interfaceEnableRouting(deviceObj, int, enable):
    # Enable/disable routing on interfaces so VLANs can be configured
    overallBuffer = []
    returnStructure = deviceObj.VtyshShell(enter=True)
    overallBuffer.append(returnStructure.buffer())
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    # enter interface
    command = "interface %s\r" % str(int)
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to configure interface " +
                  str(int) + " on device " + deviceObj.device)
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=retCode, buffer=bufferString)
        return returnCls
    else:
        LogOutput('debug', "Entered interface " +
                  str(int) + " on device " + deviceObj.device)
    if enable:
        # configure interface
        command = "routing"
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to enable routing on interface " +
                      str(int) + " on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = returnStruct(returnCode=retCode, buffer=bufferString)
            return returnCls
        else:
            LogOutput('info', "Enabled routing on interface " +
                      str(int) + " on device " + deviceObj.device)
    else:
        # configure interface
        command = "no routing"
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to disable routing on interface " +
                      str(int) + " on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = returnStruct(returnCode=retCode, buffer=bufferString)
            return returnCls
        else:
            LogOutput('info', "Disabled routing on interface " +
                      str(int) + " on device " + deviceObj.device)
        # exit
    command = "exit"
    returnDevInt = deviceObj.DeviceInteract(command=command)
    retCode = returnDevInt['returnCode']
    overallBuffer.append(returnDevInt['buffer'])
    if retCode != 0:
        LogOutput('error', "Failed to exit configure interface " +
                  str(int) + " on device " + deviceObj.device)
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=retCode, buffer=bufferString)
        return returnCls
    else:
        LogOutput('debug', "Exited configure interface " +
                  str(int) + " on device " + deviceObj.device)
    # Get out of config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    # Get out of vtysh
    returnStructure = deviceObj.VtyshShell(enter=False)
    overallBuffer.append(returnStructure.buffer())
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    # Return
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
    return returnCls

# Enable/disable interface on DUT


def interfaceGetStatus(dev, interface):
    # Gets the status of a switch interface
    output = showInterface(deviceObj=dev, interface=interface).buffer()
    ret_expression = re.search(
        r'Interface [\d-]+? is (down|up)',
        output
    )
    if ret_expression.group(1) == "up":
        LogOutput('info',"Interface %s is up" % str(interface))
        return True
    LogOutput('info',"Interface %s is down" % str(interface))
    return False


def switchEnableInterface(deviceObj, int, enable):
    # Enables/disables a switch interface and verifies if correctly configured
    if enable:
        retStruct = InterfaceEnable(
            deviceObj=deviceObj, enable=enable, interface=int)
        if not retStruct.returnCode() == 0:
            LogOutput(
                'error', "Failed to enable " + deviceObj.device +
                " interface " + int)
            return False
        else:
            LogOutput(
                'info', "Enabled " + deviceObj.device + " interface " + int)
    else:
        retStruct = InterfaceEnable(
            deviceObj=deviceObj, enable=enable, interface=int)
        if retStruct.returnCode() != 0:
            LogOutput(
                'error', "Failed to disable " + deviceObj.device +
                " interface " + int)
            return False
        else:
            LogOutput(
                'info', "Disabled " + deviceObj.device + " interface " + int)

    return True


def lagAddInterfaces(deviceObj, lagId, intArray):
    # Adds interfaces to LAG
    overallBuffer = []
    returnStructure = deviceObj.VtyshShell(enter=True)
    overallBuffer.append(returnStructure.buffer())
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    # Get into config context
    returnStructure = deviceObj.ConfigVtyShell(enter=True)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls

    # Add interfaces
    for i in intArray:
        command = "interface %s\r" % str(i)
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to configure interface " +
                      str(i) + " on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = returnStruct(returnCode=retCode, buffer=bufferString)
            return returnCls
        else:
            LogOutput(
                'debug', "Entered interface " + str(i) + " on device " +
                deviceObj.device)

        command = "lag %s" % str(lagId)
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to add interface " + str(i) +
                      " to LAG" + str(lagId) + " on device " +
                      deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = returnStruct(returnCode=retCode,
                                     buffer=bufferString)
            return returnCls
        else:
            LogOutput('info', "Added interface " + str(i) +
                      " to LAG" + str(lagId) + " on device " +
                      deviceObj.device)

        command = "exit"
        returnDevInt = deviceObj.DeviceInteract(command=command)
        retCode = returnDevInt['returnCode']
        overallBuffer.append(returnDevInt['buffer'])
        if retCode != 0:
            LogOutput('error', "Failed to exit configuration of interface " +
                      str(i) + " on device " + deviceObj.device)
            bufferString = ""
            for curLine in overallBuffer:
                bufferString += str(curLine)
            returnCls = returnStruct(returnCode=retCode, buffer=bufferString)
            return returnCls
        else:
            LogOutput('debug', "Exited configuration of interface " +
                      str(i) + " on device " + deviceObj.device)

    # Get out of config context
    returnStructure = deviceObj.ConfigVtyShell(enter=False)
    returnCode = returnStructure.returnCode()
    overallBuffer.append(returnStructure.buffer())
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh config prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    # Exit vtysh
    returnStructure = deviceObj.VtyshShell(enter=False)
    overallBuffer.append(returnStructure.buffer())
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to exit vtysh prompt")
        bufferString = ""
        for curLine in overallBuffer:
            bufferString += str(curLine)
        returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
        return returnCls
    bufferString = ""
    for curLine in overallBuffer:
        bufferString += str(curLine)
    returnCls = returnStruct(returnCode=returnCode, buffer=bufferString)
    return returnCls


def lagCreate(deviceObj, lagId, configure, intArray, mode):
    # Creates LAG and adds interfaces
    if configure:
        retStruct = lagCreation(
            deviceObj=deviceObj, lagId=str(lagId), configFlag=True)
        if retStruct.returnCode() != 0:
            LogOutput('error', "Failed to create LAG1 on " + deviceObj.device)
            return False
        else:
            LogOutput(
                'info', "Created LAG" + str(lagId) + " on " +
                deviceObj.device)
        retStruct = lagAddInterfaces(deviceObj, lagId, intArray)
        if retStruct.returnCode() != 0:
            return False
        if mode != 'off':
            retStruct = lagMode(
                lagId=str(lagId), deviceObj=deviceObj, lacpMode=mode)
            if retStruct.returnCode() != 0:
                return False
        if not lagVerifyConfig(deviceObj, lagId, intArray, mode):
            LogOutput('error',
                      'Failed to create a LAG with intended configuration')
            return False

    else:
        retStruct = lagCreation(
            deviceObj=deviceObj, lagId=str(lagId), configFlag=False)
        if retStruct.returnCode() != 0:
            LogOutput('error', "Failed to delete LAG1 on " + deviceObj.device)
            return False
        else:
            LogOutput(
                'info', "Deleted LAG" + str(lagId) + " on " + deviceObj.device)
        retStruct = lacpAggregatesShow(deviceObj=deviceObj)
        if len(retStruct.dataKeys()) != 0:
            if retStruct.valueGet(key=str(lagId)) is not None:
                LogOutput(
                    'error', "The LAG was not deleted from configuration")
                return False
    return True

# Add VLAN to interface


def vlanVerifyPorts(dut, vlanID, port):
    # Verify if port is part of a VLAN
    assigned = False
    helper = re.search('lag ', port)
    if helper:
        port = port.replace(' ', '')
    returnCLS = ShowVlan(deviceObj=dut)
    output = returnCLS.buffer()
    output = re.search(r'\r\n(%d .+?)\r' % vlanID, output)
    if not output:
        LogOutput('error', 'Could not find VLAN %d to which ' % vlanID +
                  'ports could be assigned')
        return False
    output = output.group(1)
    helper = ''
    helperList = []
    count = 0
    foundLetter = False
    for i in xrange(len(output) - 1, 0, -1):
        if not foundLetter:
            if output[i] != ' ':
                foundLetter = True
                continue
        else:
            if output[i] == ' ':
                count += 1
                if count > 1:
                    helper = output[i + 2:]
                    helperList = helper.split(', ')
                    break
            else:
                count = 0
    if port in helperList:
        assigned = True
        LogOutput('info', 'Found interface %s in VLAN %d' %
                  (port, vlanID))
    else:
        LogOutput('error', 'Could not find interface %s in VLAN %d' %
                  (port, vlanID))
    return assigned


def vlanAddInterface(deviceObj, vlanId, enable, int):
    # Verify a port has been assigned to a vlan

    if enable:
        retStruct = interfaceEnableRouting(deviceObj, int, False)
        if retStruct.returnCode() != 0:
            return False
        retStruct = AddPortToVlan(deviceObj=deviceObj, vlanId=vlanId,
                                  interface=int, access=True)
        if not (retStruct.returnCode() == 0 and
                vlanVerifyPorts(deviceObj, vlanId, int)):
            LogOutput(
                'error', "Failed to add VLAN " + str(vlanId) +
                " to interface " + int)
            return False
        else:
            LogOutput('info', "Added VLAN " + str(vlanId) +
                      " to interface " + int)
    else:
        retStruct = AddPortToVlan(deviceObj=deviceObj, vlanId=vlanId,
                                  interface=int, config=False, access=True)

        if not (retStruct.returnCode() == 0 and
                not vlanVerifyPorts(deviceObj, vlanId, int)):
            LogOutput(
                'error', "Failed to delete VLAN " + str(vlanId) +
                " to interface " + int)
            return False
        else:
            LogOutput('info', "Delete VLAN " + str(vlanId) +
                      " to interface " + int)
        retStruct = interfaceEnableRouting(deviceObj, int, True)
        if retStruct.returnCode() != 0:
            return False
    return True


def vlanVerify(dut, pVlan):
    ''' Verify a vlan exist on VLAN table.

    Args:
         dut (obj) : device under test
         pVlan (str) : vlan name to verify

    '''
    LogOutput('info', "Validating VLAN")
    cont = 0
    devRetStruct = ShowVlan(deviceObj=dut)
    returnData = devRetStruct.buffer()
    vlans = re.findall('[vV][lL][aA][nN]([0-9]+)\s', returnData)
    for vlan in vlans:
        if vlan == str(pVlan):
            cont = cont + 1
    if cont == 1:
        return 0
    else:
        return 1


def vlanConfigure(deviceObj, vlanId, enable):
    # Configure/delete VLAN on switch

    if enable:
        LogOutput('debug', "Configuring VLAN " + str(vlanId) +
                  " on device " + deviceObj.device)
        retStruct = AddVlan(deviceObj=deviceObj, vlanId=vlanId)
        if retStruct.returnCode() != 0 or vlanVerify(deviceObj, vlanId) != 0:
            LogOutput('error', "Failed to create VLAN " +
                      str(vlanId) + " on device " + deviceObj.device)
            return False
        else:
            LogOutput(
                'info', "Created VLAN " + str(vlanId) + " on device " +
                deviceObj.device)
        retStruct = VlanStatus(deviceObj=deviceObj, vlanId=vlanId,
                               status=True)
        if retStruct.returnCode() != 0:
            LogOutput('error', "Failed to enable VLAN " +
                      str(vlanId) + " on device " + deviceObj.device)
            return False
        else:
            LogOutput(
                'info', "Enabled VLAN " + str(vlanId) + " on device " +
                deviceObj.device)
    else:
        LogOutput('debug', "Deleting VLAN " + str(vlanId) +
                  " on device " + deviceObj.device)
        retStruct = AddVlan(deviceObj=deviceObj, vlanId=vlanId,
                            config=False)
        if retStruct.returnCode() != 0 or vlanVerify(deviceObj, vlanId) != 1:
            LogOutput('error', "Failed to delete VLAN " +
                      str(vlanId) + " on device " + deviceObj.device)
            return False
        else:
            LogOutput(
                'info', "Deleted VLAN " + str(vlanId) + " on device " +
                deviceObj.device)
    return True


def workstationConfigure(deviceObj, int, ipAddr, netMask, broadcast, enable):
    # Configure/unconfigure the IP address of a workstation
    if enable:
        retStruct = deviceObj.NetworkConfig(ipAddr=ipAddr,
                                            netMask=netMask,
                                            broadcast=broadcast,
                                            interface=int, configFlag=True)
        if retStruct.returnCode() != 0:
            LogOutput(
                'error', "Failed to configure IP on workstation " +
                deviceObj.device)
            return False
        cmdOut = deviceObj.cmd("ifconfig " + int)
        LogOutput('info', "Ifconfig info for workstation " +
                  deviceObj.device + ":\n" + cmdOut)
    else:
        retStruct = deviceObj.NetworkConfig(ipAddr=ipAddr,
                                            netMask=netMask,
                                            broadcast=broadcast,
                                            interface=int, configFlag=False)
        if retStruct.returnCode() != 0:
            LogOutput(
                'error', "Failed to unconfigure IP on workstation " +
                deviceObj.device)
            return False
        cmdOut = deviceObj.cmd("ifconfig " + int)
        LogOutput('info', "Ifconfig info for workstation " +
                  deviceObj.device + ":\n" + cmdOut)
    return True


def lagAddInterface(deviceObj, lagId, int, config):
    # Adds/removes interfaces from LAG
    if config:
        LogOutput('info', "Adding interface " + str(int) +
                  " to LAG" + lagId + " on device " + deviceObj.device)
    else:
        LogOutput('info', "Removing interface " + str(int) +
                  " to LAG" + lagId + " on device " + deviceObj.device)
    returnStruct = InterfaceLagIdConfig(
        deviceObj=deviceObj, interface=int, lagId=lagId, enable=config)
    if returnStruct.returnCode() != 0:
        if config:
            LogOutput('error', 'Failed to add interface to LAG')
        else:
            LogOutput('error', 'Failed to remove interface from LAG')
        return False
    return True


def lagVerifyNumber(dutObj, expectedNumber):
    '''
    Verifies the number of LAGs in a switch is the same as expected

    Params:
        dutObj (object): Switch reference
        expectedNumber (int): Number of expected LAGs in configuration

    Returns:
        bool: True if the number of LAGs is as expected, False otherwise
    '''
    LogOutput('info', 'Verifying number of LAGs in device %s...' %
              dutObj.device)
    retStruct = lacpAggregatesShow(deviceObj=dutObj)
    if retStruct.returnCode() != 0:
        LogOutput('error', 'Could not obtain information on number of LAGs')
        return False
    if len(retStruct.valueGet().keys()) != expectedNumber:
        LogOutput('error', 'Different number of LAGs in config')
        LogOutput('error', 'Expected: %d - Actual: %d' %
                  (expectedNumber, len(retStruct.valueGet().keys())))
        return False
    LogOutput('info', 'As expected')
    return True


def lagChangeLACPRate(deviceObj, lagId, lacpFastFlag=True, config=True):
    '''
    Changes LACP rate of LAG directly on OVS

    Args:
        deviceObj (object): Device on which change is made
        lagId (str): Number of LAG in configuration, this change
            is to make it similar to library function once
            pending defect is fixed
        lacpFastFlag (bool, optional): True indicates the rate will
            be set to fast, False is for slow
        config (bool, optional): True indicates lacp-rate will be configured,
            False is for wiping lacp-rate from OVS

    Returns:
        bool: True if successful, False otherwise
    '''

    # Variable declaration
    lacpRate = {'lacp-time': 'lacp-time',
                'values': {True: 'fast', False: 'slow'}}

    # If deviceObj or lagId are not defined, return error
    if not deviceObj or not lagId:
        LogOutput('error', "The device and LAG ID must be specified")
        return False
    LogOutput('debug', "Verifying LAG %s configuration..." % str(lagId))

    # Get into vtyshelll
    returnStructure = deviceObj.VtyshShell(enter=True)
    returnCode = returnStructure.returnCode()
    if returnCode != 0:
        LogOutput('error', "Failed to get vtysh prompt")
        return False
    # Get into linux context
    value = expecting(deviceObj.expectHndl, 'exit')
    deviceObj.deviceContext = 'linux'
    if not value:
        LogOutput('error', 'Unable to exit vtysh context')
        return False

    # Get current LAG information
    command = 'ovs-vsctl get port lag%s other_config' % str(lagId)
    if not expecting(deviceObj.expectHndl, command):
        LogOutput('error', 'Unable to retrieve LAG %s information' %
                  str(lagId))
        return False
    # If LAG is not present, return error
    if re.search(r'no row "lag%s"' % str(lagId), deviceObj.expectHndl.before):
        LogOutput('error', 'LAG %s does not exist' % str(lagId))
        return False

    # Separate information
    res = re.findall(r'[{ ](.+?=.+?)[},]',
                     deviceObj.expectHndl.before)

    # Look for pre-existing LACP rate
    for i, value in enumerate(res, 0):
        if (len(re.findall(lacpRate['lacp-time'], value) > 0)):
            if config:
                text = value.split('=')
                text[1] = lacpRate['values'][lacpFastFlag]
                text = '='.join(text)
                res[i] = text
            else:
                res.remove(value)
            break
    if config:
        # If no pre-existing information exists, fill it
        if len(res) == 0:
            res.append('='.join([lacpRate['lacp-time'],
                                 lacpRate['values'][lacpFastFlag]]))

    command = ('ovs-vsctl set port lag%s other_config={%s}' %
               (str(lagId), ', '.join(res)))
    if not expecting(deviceObj.expectHndl, command):
        LogOutput('error', 'Unable to configure LAG %s' % str(lagId))
        return False
    return True


def lacpCaptureFormat(capText):
    '''
    Format output of tcpdump capture into usable information
    The text that matches is the output from: tcpdump -i <INTERFACE> -v -e
    when observing LACP messages

    Args:
        capText (str): Text which is to be formatted

    Returns:
        list[dict(str)]: Dictionary with LACP information for each packet
            None if it cannot format the data
    '''
    def flagParse(flagText):
        retDict = {'Activ': '0', 'TmOut': '0', 'Aggr': '0', 'Sync': '0',
                   'Col': '0', 'Dist': '0', 'Def': '0', 'Exp': '0'}
        parseDict = {'Activ': 'Activ', 'Time': 'TmOut', 'Aggr': 'Aggr',
                     'Sync': 'Sync', 'Col': 'Col', 'Dist': 'Dist',
                     'Def': 'Def', 'Exp': 'Exp'}
        for key in parseDict.keys():
            if re.search(key, flagText):
                retDict[parseDict[key]] = '1'
        return retDict
    finalResult = None
    hoursSum = [0, 0]
    if capText is None:
        LogOutput('error', 'To format LACP capture please use a no None ' +
                  'type object')
        return None

    formatExpr = (r'(\d+?) packets received by filter')

    formatRes = re.findall(formatExpr, str(capText), re.DOTALL)
    if len(formatRes) == 0:
        LogOutput('error', 'Could not format LACP capture information')
        return None
    finalResult = int(formatRes[0])
    return finalResult
