/*
 * (c) Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

/***************************************************************************
 *    File               : linux_bond.c
 *    Description        : Manages (creates, deletes, configures) Linux
 *                           bonding interfaces
 ***************************************************************************/

/**
 * TODO: Right now configuration is done by using system calls. The idea is to
 * replace those and use netlink in the future.
 */


#include "linux_bond.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


#include <lacp_cmn.h>
#include <mlacp_debug.h>
#include <lacp_fsm.h>

#include <ops-utils.h>

#include "lacp_ops_if.h"
#include "lacp.h"
#include "mlacp_fproto.h"
#include "mvlan_sport.h"

#include <unixctl.h>
#include <dynamic-string.h>
#include <openswitch-idl.h>
#include <openswitch-dflt.h>
#include <openvswitch/vlog.h>
#include <poll-loop.h>
#include <hash.h>
#include <shash.h>

VLOG_DEFINE_THIS_MODULE(linux_bond);

#define MAX_CMD_LEN             2048
#define SWNS_EXEC               "/sbin/ip netns exec swns"

/**
 * Loads the bonding module so it can be used
 *
 */
void load_bonding_driver()
{
    const char* cmd_str = "modprobe bonding";

    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed to enable bonding driver in linux");
    }
}

/**
 * Deletes a Linux bond interface previously created.
 *
 * @param bond_name is the name of the bond to be deleted
 *
 */
void delete_linux_bond(char* bond_name)
{
    char cmd_str[MAX_CMD_LEN];

    sprintf(cmd_str, "%s echo -%s >  /sys/class/net/bonding_masters",
            SWNS_EXEC, bond_name);
    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed to delete bond in linux");
    }
}

/**
 * Creates a Linux bond interface.
 *
 * @param bond_name is the name of the bond to be created
 *
 */
void create_linux_bond(char* bond_name)
{
    char cmd_str[MAX_CMD_LEN];

    VLOG_INFO("Creating bond %s, ", bond_name);
    sprintf(cmd_str, "%s echo +%s >  /sys/class/net/bonding_masters",
            SWNS_EXEC, bond_name);
    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed to create bond in linux");
    }
    sprintf(cmd_str, "%s echo balance-xor >  /sys/class/net/%s/bonding/mode",
            SWNS_EXEC, bond_name);
    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed set bonding mode");
    }
}

/**
 * Sets slave interface to down.
 * This is needed because in order to add a slave to a bond
 * the interface must be down.
 *
 * @param slave_name is the name of the slave interface to
 *           be set down.
 *
 */
void set_slave_interface_down(char* slave_name)
{
    char cmd_str[MAX_CMD_LEN];

    sprintf(cmd_str, "ovs-vsctl set interface %s user_config={admin=down}", slave_name);
    VLOG_INFO("Setting interface to down %s", cmd_str);
    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed set interface to down. cmd: %s", cmd_str);
    }
}

/**
 * Sets slave interface to up.
 *
 * @param slave_name is the name of the slave interface to
 *           be set up.
 *
 */
void set_slave_interface_up(char* slave_name)
{
    char cmd_str[MAX_CMD_LEN];

    sprintf(cmd_str, "ovs-vsctl set interface %s user_config={admin=up} &", slave_name);
    VLOG_INFO("Setting interface to up");
    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed set interface %s to up", slave_name);
    }
}

/**
 * Adds a slave to a Linux bond
 *
 * @param bond_name is the name of the bond.
 * @param slave_name is the name of the slave interface to
 *           be added.
 *
 */
void add_slave_to_bond(char* bond_name, char* slave_name)
{
    char cmd_str[MAX_CMD_LEN];

    VLOG_INFO("adding interface to bond");
    sprintf(cmd_str, "%s  echo +%s > /sys/class/net/%s/bonding/slaves",
             SWNS_EXEC, slave_name,  bond_name);

    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed to add interface to bonding");
    }
}

/**
 * Removes a slave from a Linux bond.
 *
 * @param bond_name is the name of the bond.
 * @param slave_name is the name of the slave interface to
 *           be removed.
 *
 */
void remove_slave_from_bond(char* bond_name, char* slave_name)
{
    char cmd_str[MAX_CMD_LEN];

    VLOG_INFO("adding interface to bond");
    sprintf(cmd_str, "%s  echo -%s > /sys/class/net/%s/bonding/slaves",
             SWNS_EXEC, slave_name,  bond_name);

    if (system(cmd_str) != 0) {
         VLOG_INFO("Failed to add interface to bonding");
    }
}

/**
 * Sets a Linux bond to up
 *
 * @param bond_name is the name of the bond to be set up.
 *
 */
void set_linux_bond_up(char* bond_name)
{
    char cmd_str[MAX_CMD_LEN];

    sprintf(cmd_str, "%s ifconfig %s up", SWNS_EXEC, bond_name);
    if (system(cmd_str) != 0) {
        VLOG_INFO("Failed setting bond to up");
    }
}
