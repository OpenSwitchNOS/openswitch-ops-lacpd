/*
 * Copyright (C) 1997, 98 Kunihiro Ishiguro
 * Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
 *
 * GNU Zebra is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2, or (at your option) any
 * later version.
 *
 * GNU Zebra is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GNU Zebra; see the file COPYING.  If not, write to the Free
 * Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
 * 02111-1307, USA.
 */
/******************************************************************************
 *    File               : mstp_lag.c
 *    Description        : MSTP Protocol show running config API
 ******************************************************************************/
#include "vtysh/command.h"
#include "vtysh/vtysh.h"
#include "vtysh/vtysh_user.h"
#include "vswitch-idl.h"
#include "ovsdb-idl.h"
#include "openvswitch/vlog.h"
#include "openswitch-idl.h"
#include "vtysh/vtysh_ovsdb_if.h"
#include "vtysh/vtysh_ovsdb_config.h"

#define DEF_BPDU_STATUS              false
#define DEF_ADMIN_EDGE               false
#define DEF_MSTP_PORT_PRIORITY       8
#define DEF_MSTP_COST                0

extern struct ovsdb_idl *idl;

/*-----------------------------------------------------------------------------
 | Function:        vtysh_ovsdb_parse_mstp_intf_config
 | Responsibility:  Client callback routine for show running-config
 |                  displays the commands configured on interface
 | Parameters:
 |      p_private:  void type object typecast to required
 | Return:
 |      e_vtysh_ok on success else e_vtysh_error
 ------------------------------------------------------------------------------
 */
int
mstp_lag_show_running_config(const struct ovsrec_port *port_row) {
    const struct ovsrec_mstp_common_instance_port *cist_port = NULL;
    const struct ovsrec_mstp_instance *mstp_row = NULL;
    const struct ovsrec_mstp_instance_port *mstp_port_row = NULL;
    const struct ovsrec_bridge *bridge_row = NULL;
    int i = 0, j = 0;

    if(!port_row) {
        assert(0);
        return e_vtysh_error;
    }

    OVSREC_MSTP_COMMON_INSTANCE_PORT_FOR_EACH(cist_port, idl) {
        if(!cist_port->port) {
            continue;
        }
        if (VTYSH_STR_EQ(cist_port->port->name, port_row->name)) {
            if (cist_port->loop_guard_disable &&
                    *cist_port->loop_guard_disable != DEF_BPDU_STATUS) {
                vty_out(vty, "%4s%s%s", "",
                            "spanning-tree loop-guard enable", VTY_NEWLINE);
            }
            if (cist_port->root_guard_disable &&
                    *cist_port->root_guard_disable != DEF_BPDU_STATUS) {
                vty_out(vty, "%4s%s%s", "",
                             "spanning-tree root-guard enable", VTY_NEWLINE);
            }
            if (cist_port->bpdu_guard_disable &&
                    *cist_port->bpdu_guard_disable != DEF_BPDU_STATUS) {
                vty_out(vty, "%4s%s%s", "",
                             "spanning-tree bpdu-guard enable", VTY_NEWLINE);
            }
            if (cist_port->bpdu_filter_disable &&
                    *cist_port->bpdu_filter_disable != DEF_BPDU_STATUS) {
                vty_out(vty, "%4s%s%s", "",
                             "spanning-tree bpdu-filter enable", VTY_NEWLINE);
            }
            if (cist_port->admin_edge_port_disable &&
                  *cist_port->admin_edge_port_disable != DEF_ADMIN_EDGE) {
                vty_out(vty, "%4s%s%s", "",
                          "spanning-tree port-type admin-edge", VTY_NEWLINE);
            }
            if (cist_port->port_priority &&
                    *cist_port->port_priority != DEF_MSTP_PORT_PRIORITY) {
                vty_out(vty, "%4s%s %ld%s", "",
                        "spanning-tree port-priority", *cist_port->port_priority, VTY_NEWLINE);
            }
            if (cist_port->admin_path_cost &&
                    *cist_port->admin_path_cost != DEF_MSTP_COST) {
                vty_out(vty, "%4s%s %ld%s", "",
                        "spanning-tree cost", *cist_port->admin_path_cost, VTY_NEWLINE);
            }
        }
    }

    bridge_row = ovsrec_bridge_first(idl);
    if (!bridge_row) {
        assert(0);
        return e_vtysh_ok;
    }

    /* Loop for all instance in bridge table */
    for (i=0; i < bridge_row->n_mstp_instances; i++) {
        mstp_row = bridge_row->value_mstp_instances[i];
        if(!mstp_row) {
            assert(0);
            return e_vtysh_error;
        }

        /* Loop for all ports in the MSTP instance table */
        for (j=0; j<mstp_row->n_mstp_instance_ports; j++) {
            mstp_port_row = mstp_row->mstp_instance_ports[j];
            if(!mstp_port_row) {
                assert(0);
                return e_vtysh_error;
            }
            if (VTYSH_STR_EQ(mstp_port_row->port->name, port_row->name)) {
                if (mstp_port_row->port_priority &&
                   (*mstp_port_row->port_priority != DEF_MSTP_PORT_PRIORITY)) {
                    vty_out(vty, "%4s%s %ld %s %ld%s", "",
                            "spanning-tree instance",
                            bridge_row->key_mstp_instances[i],
                            "port-priority",
                            *mstp_port_row->port_priority, VTY_NEWLINE);
                }
                if (mstp_port_row->admin_path_cost &&
                        (*mstp_port_row->admin_path_cost != DEF_MSTP_COST)) {
                    vty_out(vty, "%4s%s %ld %s %ld%s", "",
                            "spanning-tree instance",
                            bridge_row->key_mstp_instances[i],
                            "cost",
                            *mstp_port_row->admin_path_cost, VTY_NEWLINE);
                }
            }
        }
    }
    return e_vtysh_ok;
}
