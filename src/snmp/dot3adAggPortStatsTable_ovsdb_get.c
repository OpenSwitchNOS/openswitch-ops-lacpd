#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggPortStatsTable_ovsdb_get.h"

void dot3adAggPortStatsTable_ovsdb_idl_init(struct ovsdb_idl *idl) {
    ovsdb_idl_add_column(idl, &ovsrec_port_col_name);
}

void ovsdb_get_dot3adAggPortStatsIndex(struct ovsdb_idl *idl,
                                  const struct ovsrec_port *port_row,
                                  long *dot3adAggPortIndex_val_ptr) {
    dot3adAggPortStatsIndex_custom_function(idl, port_row,
                                            dot3adAggPortIndex_val_ptr);
}

void ovsdb_get_dot3adAggPortStatsLACPDUsRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsLACPDUsRx_val_ptr) {
    *dot3adAggPortStatsLACPDUsRx_val_ptr = (u_long)NULL;
}

void ovsdb_get_dot3adAggPortStatsMarkerPDUsRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerPDUsRx_val_ptr) {
    *dot3adAggPortStatsMarkerPDUsRx_val_ptr = (u_long)NULL;
}

void ovsdb_get_dot3adAggPortStatsMarkerResponsePDUsRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerResponsePDUsRx_val_ptr) {
    *dot3adAggPortStatsMarkerResponsePDUsRx_val_ptr = (u_long)NULL;
}

void ovsdb_get_dot3adAggPortStatsUnknownRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsUnknownRx_val_ptr) {
    *dot3adAggPortStatsUnknownRx_val_ptr = (u_long)NULL;
}

void ovsdb_get_dot3adAggPortStatsIllegalRx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsIllegalRx_val_ptr) {
    *dot3adAggPortStatsIllegalRx_val_ptr = (u_long)NULL;
}

void ovsdb_get_dot3adAggPortStatsLACPDUsTx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsLACPDUsTx_val_ptr) {
    *dot3adAggPortStatsLACPDUsTx_val_ptr = (u_long)NULL;
}

void ovsdb_get_dot3adAggPortStatsMarkerPDUsTx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerPDUsTx_val_ptr) {
    *dot3adAggPortStatsMarkerPDUsTx_val_ptr = (u_long)NULL;
}

void ovsdb_get_dot3adAggPortStatsMarkerResponsePDUsTx(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    u_long *dot3adAggPortStatsMarkerResponsePDUsTx_val_ptr) {
    *dot3adAggPortStatsMarkerResponsePDUsTx_val_ptr = (u_long)NULL;
}
