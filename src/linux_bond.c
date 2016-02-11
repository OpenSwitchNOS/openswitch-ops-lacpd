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
#define MAX_FILE_PATH_LEN       100

/**
 * Deletes a Linux bond interface previously created.
 *
 * @param bond_name is the name of the bond to be deleted
 *
 */
void delete_linux_bond(char* bond_name)
{
    FILE * masters_file;

    VLOG_DBG("bond: Deleting bond %s", bond_name);

    masters_file = fopen ("/sys/class/net/bonding_masters","w+");

    if(masters_file) {
        fprintf (masters_file, "-%s", bond_name);
        fclose(masters_file);
    }
    else {
        VLOG_ERR("bond: Failed to delete bond %s in linux", bond_name);
    }
} /* delete_linux_bond */

/**
 * Creates a Linux bond interface.
 *
 * @param bond_name is the name of the bond to be created
 *
 */
void create_linux_bond(char* bond_name)
{
    char file_path[MAX_FILE_PATH_LEN];
    FILE * masters_file;

    VLOG_DBG("bond: Creating bond %s", bond_name);

    masters_file = fopen ("/sys/class/net/bonding_masters","w+");

    if(masters_file) {
        fprintf (masters_file, "+%s", bond_name);
        fclose(masters_file);

        sprintf(file_path, "/sys/class/net/%s/bonding/mode", bond_name);
        masters_file = fopen (file_path,"w+");

        if(masters_file) {
            fprintf (masters_file, "2");
            fclose(masters_file);
        }
        else {
            VLOG_ERR("bond: Failed to set bonding mode in bond %s", bond_name);
        }
    }
    else {
        VLOG_ERR("bond: Failed to create bond %s in linux", bond_name);
    }
} /* create_linux_bond */

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

    VLOG_DBG("Setting bonding slave %s down", slave_name);

    sprintf(cmd_str, "ovs-vsctl set interface %s user_config={admin=down}", slave_name);
    if(!system(cmd_str) ) {
        VLOG_ERR("bond: Failed set interface to down. cmd: %s", cmd_str);
    }
} /* set_slave_interface_down */

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

    VLOG_DBG("Setting bonding slave %s up", slave_name);

    sprintf(cmd_str, "ovs-vsctl set interface %s user_config={admin=up} &", slave_name);
    if(!system(cmd_str) ) {
        VLOG_ERR("bond: Failed set interface %s to up", slave_name);
    }
} /* set_slave_interface_up */

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
    char file_path[MAX_FILE_PATH_LEN];
    FILE * slaves_file;

    VLOG_DBG("bond: Adding bonding slave %s to bond %s",
              slave_name, bond_name);

    sprintf(file_path, "/sys/class/net/%s/bonding/slaves", bond_name);

    slaves_file = fopen (file_path,"w+");

    if(slaves_file) {
        fprintf (slaves_file, "+%s", slave_name);
        fclose(slaves_file);
    }
    else {
        VLOG_ERR("bond: Failed to add interface %s to bond %s",
                 slave_name, bond_name);
    }
} /* add_slave_to_bond */

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
    char file_path[MAX_FILE_PATH_LEN];
    FILE * pFile;

    VLOG_DBG("bond: Removing bonding slave %s from bond %s", slave_name, bond_name);

    sprintf(file_path, "/sys/class/net/%s/bonding/slaves", bond_name);

    pFile = fopen (file_path,"w+");

    if(pFile) {
        fprintf (pFile, "-%s", slave_name);
        fclose(pFile);
    }
    else {
        VLOG_ERR("bond: Failed to remove interface %s from bond %s", slave_name, bond_name);
    }
} /* remove_slave_from_bond */

/**
 * Sets a Linux bond to up
 *
 * @param bond_name is the name of the bond to be set up.
 *
 */
void set_linux_bond_up(char* bond_name)
{
    struct rtareq req;

    VLOG_DBG("bond: Setting bond %s up", bond_name);

    memset(&req, 0, sizeof(req));

    req.n.nlmsg_len = NLMSG_SPACE(sizeof(struct ifinfomsg));
    req.n.nlmsg_pid     = getpid();
    req.n.nlmsg_type    = RTM_NEWLINK;
    req.n.nlmsg_flags   = NLM_F_REQUEST;

    req.i.ifi_family    = AF_UNSPEC;
    req.i.ifi_index     = if_nametoindex(bond_name);

    if (req.i.ifi_index == 0) {
        VLOG_ERR("bond: Unable to get ifindex for interface: %s", bond_name);
        return;
    }

    req.i.ifi_change |= IFF_UP;
    req.i.ifi_flags  |= IFF_UP;

    if (send(nl_sock, &req, req.n.nlmsg_len, 0) == -1) {
        VLOG_ERR("bond: Netlink failed to bring up the interface %s", bond_name);
    }
} /* set_linux_bond_up */

/**
 * Open a Netlink socket
 *
 */
void netlink_socket_open()
{
    struct sockaddr_nl s_addr;

    nl_sock = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);

    if (nl_sock < 0) {
        VLOG_ERR("bond: Netlink socket creation failed (%s)",strerror(errno));
        return;
    }

    memset((void *) &s_addr, 0, sizeof(s_addr));
    s_addr.nl_family = AF_NETLINK;
    s_addr.nl_pid = getpid();
    s_addr.nl_groups = RTMGRP_IPV4_IFADDR | RTMGRP_IPV6_IFADDR | RTMGRP_LINK;

    if (bind(nl_sock, (struct sockaddr *) &s_addr, sizeof(s_addr)) < 0) {
        VLOG_ERR("bond: Netlink socket bind failed (%s)",strerror(errno));
        return;
    }

    VLOG_DBG("bond: Netlink socket created. fd = %d",nl_sock);
} /* netlink_socket_open */
