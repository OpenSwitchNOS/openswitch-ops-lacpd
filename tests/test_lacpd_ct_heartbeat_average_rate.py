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
###############################################################################
# Name:        test_lacp_ct_heartbeat_average_rate.py
#
# Description: Tests LACP heartbeat average rate (slow/fast)
#
# Author(s):      Jose Hernandez, Agustin Meneses, Vladimir Vargas
#
# Topology:  |Host| ----- |Switch| ---------------------- |Switch| ----- |Host|
#                                   (LAG - 2 links)
#
# Success Criteria:  PASS -> Get correct LACP heartbeat average rate
#
#                    FAILED -> LACP heartbeat average rate too slow or
#                              too fast according to lacp_timeout
#
###############################################################################

import pytest
from opstestfw import *
from opstestfw.switch.CLI import *
from opstestfw.host import *
from lib_test import lagVerifyLACPStatusAndFlags
from lib_test import lagVerifyConfig
from lib_test import switchEnableInterface
from lib_test import lagCreate
from lib_test import vlanAddInterface
from lib_test import vlanConfigure
from lib_test import workstationConfigure
from lib_test import switchReboot
from lib_test import lagVerifyNumber
from lib_test import interfaceEnableRouting

from lib_test import lagChangeLACPRate
from lib_test import lacpCaptureFormat
from lib_test import swtichGetIntoVtyshOrSwns
from lib_test import switchTcpdumpInterfaces
from lib_test import deviceStartWiresharkCap
from lib_test import deviceStopWiresharkCap
from lib_test import deviceObtainActiveMacAddresses
from time import sleep

topoDict = {"topoExecution": 3000,
            "topoTarget": "dut01 dut02",
            "topoDevices": "dut01 dut02 wrkston01 wrkston02",
            "topoLinks": "lnk01:dut01:wrkston01,\
                          lnk02:dut01:dut02,\
                          lnk03:dut01:dut02,\
                          lnk04:dut02:wrkston02",
            "topoFilters": "dut01:system-category:switch,\
                            dut02:system-category:switch,\
                            wrkston01:system-category:workstation,\
                            wrkston02:system-category:workstation,\
                            wrkston01:docker-image: openswitch/ubuntutest,\
                            wrkston02:docker-image: openswitch/ubuntutest"}


def trafficCaptureStart(deviceObj, interfaces):
    tcpdumpInts = None
    macInts = None
    procs = None
    if not swtichGetIntoVtyshOrSwns(deviceObj, enter=False):
        LogOutput('error', 'Could not enter into linux switching context')
        return None, None, None
    res = switchTcpdumpInterfaces(deviceObj)
    if not res[0]:
        swtichGetIntoVtyshOrSwns(deviceObj)
        LogOutput('Could not obtain information on the interfaces for ' +
                  'tcpdump on device %s' % deviceObj.device)
        return None, None, None
    tcpdumpInts = res[1]
    macInts = deviceObtainActiveMacAddresses(deviceObj, interfaces)
    procs = []
    interfaces = [deviceObj.linkPortMapping[link] for link in interfaces]
    for interface, macAddr in zip(interfaces, macInts):
        procs.append(deviceStartWiresharkCap(deviceObj,
                                             tcpdumpInts[interface],
                                             '-vv -e ether src %s' %
                                             macAddr.lower()))
    if None in procs:
        swtichGetIntoVtyshOrSwns(deviceObj)
        LogOutput('error', 'Could not start traffic captures on device %s' %
                  deviceObj.device)
        return None, None, None
    return procs, tcpdumpInts, macInts


def trafficCaptureStop(deviceObj, interfaces, tcpdumpInts, processesIds):
    LogOutput('info', 'Obtaining results...')
    res = []
    interfaces = [deviceObj.linkPortMapping[link] for link in interfaces]
    for proc, interface in zip(processesIds, interfaces):
        res.append(deviceStopWiresharkCap(deviceObj, proc,
                                          tcpdumpInts[interface])) #'eth0'))
    if None in res:
        swtichGetIntoVtyshOrSwns(deviceObj)
        LogOutput('error', 'Could not stop traffic captures on device %s' %
                  deviceObj.device)
        return None
    if not swtichGetIntoVtyshOrSwns(deviceObj):
        LogOutput('error', 'Could not return to normal device context')
        return None
    return res

def lagLACPTimeCheckAverage(deviceObj, interfaces, fastHeartbeat):
    heartbeat = 0
    waitTime = 0
    tcpdumpInts = None
    macInts = None
    procs = None
    if fastHeartbeat:
        heartbeat = 1
        waitTime = 5
    else:
        heartbeat = 30
        waitTime = 90
    procs, tcpdumpInts, macInts =\
    trafficCaptureStart(deviceObj, interfaces)
    if not (procs and tcpdumpInts and macInts):
        return False
    LogOutput('info', 'Waiting %d seconds to let LACP traffic flow...' %
              waitTime)
    sleep(waitTime)
    res = trafficCaptureStop(deviceObj, interfaces, tcpdumpInts, procs)
    if not res:
        return False
    LogOutput('info', 'Analyzing results ...')
    for interface, formattedResult in zip(interfaces,
                                          (lacpCaptureFormat(val)
                                           for val in res)):
        if not formattedResult:
            return False

        avg = waitTime / formattedResult
        if avg < (heartbeat - 1):
            LogOutput('error', 'LACP hearbteat average rate is too slow ' +
                      'on interface %s' % interface)
            LogOutput('error', 'Expected: %d - Found: %.2f' %
                      (heartbeat, avg))
            return False
        if avg > (heartbeat + 1):
            LogOutput('error', 'LACP hearbteat average rate is too fast ' +
                      'on interface %s' % interface)
            LogOutput('error', 'Expected: %d - Found: %.2f' %
                      (heartbeat, avg))
            return False
    LogOutput('info', 'LACP heartbeat rate is as expected')
    return True


def clean_up_devices(dut01Obj, dut02Obj, wrkston01Obj, wrkston02Obj):
    # Clean up devices
    LogOutput('info', "\n############################################")
    LogOutput('info', "Device Cleanup - rolling back config")
    LogOutput('info', "############################################")
    finalResult = []
    dut01 = {'obj': dut01Obj, 'links': ['lnk01', 'lnk02', 'lnk03'],
             'wrkston_links': ['lnk01']}
    dut02 = {'obj': dut02Obj, 'links': ['lnk02', 'lnk03', 'lnk04'],
             'wrkston_links': ['lnk04']}

    LogOutput('info', "Unconfigure workstations")
    LogOutput('info', "Unconfiguring workstation 1")
    finalResult.append(workstationConfigure(
        wrkston01Obj,
        wrkston01Obj.linkPortMapping['lnk01'], "140.1.1.10",
        "255.255.255.0", "140.1.1.255", False))
    LogOutput('info', "Unconfiguring workstation 2")
    finalResult.append(workstationConfigure(
        wrkston02Obj,
        wrkston02Obj.linkPortMapping['lnk04'], "140.1.1.11",
        "255.255.255.0", "140.1.1.255", False))

    LogOutput('info', "Enable routing on DUTs workstations links")
    for dut in [dut01, dut02]:
        LogOutput('info', "Configuring switch %s" % dut['obj'].device)
        for link in dut['wrkston_links']:
            finalResult.append(interfaceEnableRouting(dut['obj'],
                                                      dut['obj'].
                                                      linkPortMapping[link],
                                                      True))

    LogOutput('info', "Disable interfaces on DUTs")
    for dut in [dut01, dut02]:
        LogOutput('info', "Configuring switch %s" % dut['obj'].device)
        for link in dut['links']:
            finalResult.append(switchEnableInterface(dut['obj'],
                                                     dut['obj'].
                                                     linkPortMapping[link],
                                                     False))

    LogOutput('info', "Delete LAGs on DUTs")
    finalResult.append(lagCreate(dut01Obj, '1', False, [], 'off'))
    finalResult.append(lagCreate(dut02Obj, '1', False, [], 'off'))

    LogOutput('info', "Remove VLAN from DUTs")
    finalResult.append(vlanConfigure(dut01Obj, 900, False))
    finalResult.append(vlanConfigure(dut02Obj, 900, False))

    for i in finalResult:
        if not i:
            LogOutput('error', "Errors were detected while cleaning \
                    devices")
            return
    LogOutput('info', "Cleaned up devices")


class Test_ft_delete_low_number_of_members:

    def setup_class(cls):
        # Create Topology object and connect to devices
        Test_ft_delete_low_number_of_members.\
            testObj = testEnviron(topoDict=topoDict)
        Test_ft_delete_low_number_of_members.topoObj =\
            Test_ft_delete_low_number_of_members.testObj.topoObjGet()

    def teardown_class(cls):
        # clean devices
        clean_up_devices(
            cls.topoObj.deviceObjGet(device="dut01"),
            cls.topoObj.deviceObjGet(device="dut02"),
            cls.topoObj.deviceObjGet(device="wrkston01"),
            cls.topoObj.deviceObjGet(device="wrkston02"))
        # Terminate all nodes
        Test_ft_delete_low_number_of_members.topoObj.\
            terminate_nodes()

    def test_rebootSwitches(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Reboot the switches")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        devRebootRetStruct = switchReboot(dut01Obj)
        if not devRebootRetStruct:
            LogOutput('error', "Failed to reboot and clean Switch 1")
            assert(devRebootRetStruct)
        else:
            LogOutput('info', "Passed Switch 1 Reboot piece")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        devRebootRetStruct = switchReboot(dut02Obj)
        if not devRebootRetStruct:
            LogOutput('error', "Failed to reboot and clean Switch 2")
            assert(devRebootRetStruct)
        else:
            LogOutput('info', "Passed Switch 2 Reboot piece")

    def test_enableDUTsInterfaces(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Enable switches interfaces")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        dut01 = {'obj': dut01Obj, 'links': ['lnk01', 'lnk02', 'lnk03']}
        dut02 = {'obj': dut02Obj, 'links': ['lnk02', 'lnk03', 'lnk04']}
        for dut in [dut01, dut02]:
            LogOutput('info', "Configuring switch %s" % dut['obj'].device)
            for link in dut['links']:
                assert(switchEnableInterface(dut['obj'],
                                             dut['obj'].linkPortMapping[link],
                                             True))

    def test_createLAGs(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Create LAGs")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        links = ['lnk02', 'lnk03']
        for dut, mode in zip([dut01Obj, dut02Obj], ['active', 'passive']):
            assert(lagCreate(dut, '1', True, [
                dut.linkPortMapping[link] for link in links], mode))
            assert(lagVerifyNumber(dut, 1))


    def test_configureVLANs(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Configure VLANs on switches")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        dut01 = {'obj': dut01Obj, 'links': ['lag 1',
                                            dut01Obj.
                                            linkPortMapping['lnk01']]}
        dut02 = {'obj': dut02Obj, 'links': ['lag 1',
                                            dut02Obj.
                                            linkPortMapping['lnk04']]}
        for dut in [dut01, dut02]:
            LogOutput('info', 'Configure VLAN on %s' % dut['obj'].device)
            assert(vlanConfigure(dut['obj'], 900, True))
            for link in dut['links']:
                assert(vlanAddInterface(dut['obj'], 900, True, link))

    def test_configureWorkstations(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Configure workstations")
        LogOutput('info', "############################################")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        wrkston02Obj = self.topoObj.deviceObjGet(device="wrkston02")
        LogOutput('info', "Configuring workstation 1")
        assert(workstationConfigure(
            wrkston01Obj,
            wrkston01Obj.linkPortMapping[
                'lnk01'], "140.1.1.10", "255.255.255.0", "140.1.1.255", True))
        LogOutput('info', "Configuring workstation 2")
        assert(workstationConfigure(
            wrkston02Obj,
            wrkston02Obj.linkPortMapping[
                'lnk04'], "140.1.1.11", "255.255.255.0", "140.1.1.255", True))

    def test_LAGFormation1(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Test LAGs are correctly formed")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        wrkston02Obj = self.topoObj.deviceObjGet(device="wrkston02")
        flags1 = {'Activ': '1', 'TmOut': '0', 'Aggr': '1', 'Sync': '1',
                  'Col': '1', 'Dist': '1', 'Def': '0', 'Exp': '0'}
        flags2 = {'Activ': '0', 'TmOut': '0', 'Aggr': '1', 'Sync': '1',
                  'Col': '1', 'Dist': '1', 'Def': '0', 'Exp': '0'}
        assert(lagVerifyLACPStatusAndFlags(dut01Obj, dut02Obj, True,
                                           ['lnk02', 'lnk03'], 'lag1', 'lag1',
                                           dut01Flags=flags1,
                                           dut02Flags=flags2))

    def test_LACPTiming1(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Verify timing of LACP messages")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        for dut in [dut01Obj, dut02Obj]:
            assert(lagLACPTimeCheckAverage(dut, ['lnk02', 'lnk03'],
                                      False))

    def test_changeLACPRate(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Change LACP timeouts to fast on devices")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        links = ['lnk02', 'lnk03']
        for dut, mode in zip([dut01Obj, dut02Obj], ['active', 'passive']):
            assert(lagChangeLACPRate(dut, '1', lacpFastFlag=True))
            assert(lagVerifyConfig(dut, '1', [dut.linkPortMapping[link]\
                                              for link in links],
                                   lacpFastFlag=True, lacpMode=mode))

    def test_LAGFormation1(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Test LAGs are correctly formed")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        wrkston01Obj = self.topoObj.deviceObjGet(device="wrkston01")
        wrkston02Obj = self.topoObj.deviceObjGet(device="wrkston02")
        flags1 = {'Activ': '1', 'TmOut': '1', 'Aggr': '1', 'Sync': '1',
                  'Col': '1', 'Dist': '1', 'Def': '0', 'Exp': '0'}
        flags2 = {'Activ': '0', 'TmOut': '1', 'Aggr': '1', 'Sync': '1',
                  'Col': '1', 'Dist': '1', 'Def': '0', 'Exp': '0'}
        assert(lagVerifyLACPStatusAndFlags(dut01Obj, dut02Obj, True,
                                           ['lnk02', 'lnk03'], 'lag1', 'lag1',
                                           dut01Flags=flags1,
                                           dut02Flags=flags2))

    def test_LACPTiming1(self):
        LogOutput('info', "\n############################################")
        LogOutput('info', "Verify timing of LACP messages")
        LogOutput('info', "############################################")
        dut01Obj = self.topoObj.deviceObjGet(device="dut01")
        dut02Obj = self.topoObj.deviceObjGet(device="dut02")
        for dut in [dut01Obj, dut02Obj]:
            assert(lagLACPTimeCheckAverage(dut, ['lnk02', 'lnk03'],
                                      True))
