#ifndef DOT3ADAGGPORTSTATSTABLE_OVSDB_GET_H
#define DOT3ADAGGPORTSTATSTABLE_OVSDB_GET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

void dot3adAggPortStatsTable_ovsdb_idl_init(struct ovsdb_idl *idl);
void ovsdb_get_dot3adAggPortStatsIndex(struct ovsdb_idl *idl,
                                  const struct ovsrec_port *port_row,
                                  long *dot3adAggPortIndex_val_ptr);

void ovsdb_get_dot3adAggPortStatsLACPDUsRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsLACPDUsRx_val_ptr);
void ovsdb_get_dot3adAggPortStatsMarkerPDUsRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerPDUsRx_val_ptr);
void ovsdb_get_dot3adAggPortStatsMarkerResponsePDUsRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerResponsePDUsRx_val_ptr);
void ovsdb_get_dot3adAggPortStatsUnknownRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsUnknownRx_val_ptr);
void ovsdb_get_dot3adAggPortStatsIllegalRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsIllegalRx_val_ptr);
void ovsdb_get_dot3adAggPortStatsLACPDUsTx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsLACPDUsTx_val_ptr);
void ovsdb_get_dot3adAggPortStatsMarkerPDUsTx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerPDUsTx_val_ptr);
void ovsdb_get_dot3adAggPortStatsMarkerResponsePDUsTx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerResponsePDUsTx_val_ptr);
#endif
