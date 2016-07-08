#ifndef DOT3ADAGGPORTLISTTABLE_OVSDB_GET_H
#define DOT3ADAGGPORTLISTTABLE_OVSDB_GET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

void dot3adAggPortListTable_ovsdb_idl_init(struct ovsdb_idl *idl);
void ovsdb_get_dot3adAggIndex(struct ovsdb_idl *idl,
                              const struct ovsrec_port *port_row,
                              long *dot3adAggIndex_val_ptr);

void ovsdb_get_dot3adAggPortListPorts(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    char *dot3adAggPortListPorts_val_ptr,
    size_t *dot3adAggPortListPorts_val_ptr_len);
#endif