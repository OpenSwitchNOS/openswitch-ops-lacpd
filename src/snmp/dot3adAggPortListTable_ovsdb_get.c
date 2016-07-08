#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggPortListTable_ovsdb_get.h"

void dot3adAggPortListTable_ovsdb_idl_init(struct ovsdb_idl *idl) {
    ovsdb_idl_add_column(idl, &ovsrec_port_col_interfaces);
    ovsdb_idl_add_column(idl, &ovsrec_port_col_name);
}

void ovsdb_get_dot3adAggPortListPorts(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    char *dot3adAggPortListPorts_val_ptr,
    size_t *dot3adAggPortListPorts_val_ptr_len) {
    dot3adAggPortListPorts_custom_function(idl, port_row,
                                           dot3adAggPortListPorts_val_ptr,
                                           dot3adAggPortListPorts_val_ptr_len);
}
