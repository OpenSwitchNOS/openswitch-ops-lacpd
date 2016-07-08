#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggPortTable_ovsdb_get.h"

void dot3adAggPortTable_ovsdb_idl_init(struct ovsdb_idl *idl) {
    ovsdb_idl_add_column(idl, &ovsrec_port_col_other_config);
    ovsdb_idl_add_column(idl, &ovsrec_interface_col_lacp_status);
    ovsdb_idl_add_column(idl, &ovsrec_interface_col_other_config);
    ovsdb_idl_add_column(idl, &ovsrec_port_col_name);
}
void ovsdb_get_dot3adAggPortIndex(struct ovsdb_idl *idl,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortIndex_val_ptr){
    dot3adAggPortIndex_custom_function(idl, interface_row,
                                  dot3adAggPortIndex_val_ptr);
}

void ovsdb_get_dot3adAggPortActorSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorSystemPriority_val_ptr) {
    dot3adAggPortActorSystemPriority_custom_function(
        idl, interface_row, dot3adAggPortActorSystemPriority_val_ptr);
}

void ovsdb_get_dot3adAggPortActorSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    char *dot3adAggPortActorSystemID_val_ptr,
    size_t *dot3adAggPortActorSystemID_val_ptr_len) {
    dot3adAggPortActorSystemID_custom_function(
        idl,interface_row, dot3adAggPortActorSystemID_val_ptr,
        dot3adAggPortActorSystemID_val_ptr_len);
}

void ovsdb_get_dot3adAggPortActorAdminKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorAdminKey_val_ptr) {
    const char *agg_key = NULL;

    agg_key = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_ACTOR_KEY);
    if(agg_key == NULL)
        *dot3adAggPortActorAdminKey_val_ptr = 0;
    else
        *dot3adAggPortActorAdminKey_val_ptr = atoi(agg_key);
}

void ovsdb_get_dot3adAggPortActorOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorOperKey_val_ptr) {
    const char *agg_key = NULL;

    agg_key = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_ACTOR_KEY);
    if(agg_key == NULL)
        *dot3adAggPortActorOperKey_val_ptr = 0;
    else
        *dot3adAggPortActorOperKey_val_ptr = atoi(agg_key);

}

void ovsdb_get_dot3adAggPortPartnerAdminSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminSystemPriority_val_ptr) {
    dot3adAggPortPartnerAdminSystemPriority_custom_function(
        idl, interface_row, dot3adAggPortPartnerAdminSystemPriority_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerOperSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperSystemPriority_val_ptr) {
    dot3adAggPortPartnerOperSystemPriority_custom_function(
        idl, interface_row, dot3adAggPortPartnerOperSystemPriority_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerAdminSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerAdminSystemID_val_ptr,
    size_t *dot3adAggPortPartnerAdminSystemID_val_ptr_len) {
    dot3adAggPortPartnerAdminSystemID_custom_function(
        idl, port_row, interface_row, dot3adAggPortPartnerAdminSystemID_val_ptr,
        dot3adAggPortPartnerAdminSystemID_val_ptr_len);
}

void ovsdb_get_dot3adAggPortPartnerOperSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerOperSystemID_val_ptr,
    size_t *dot3adAggPortPartnerOperSystemID_val_ptr_len) {
    dot3adAggPortPartnerOperSystemID_custom_function(
        idl, port_row, interface_row, dot3adAggPortPartnerOperSystemID_val_ptr,
        dot3adAggPortPartnerOperSystemID_val_ptr_len);
}

void ovsdb_get_dot3adAggPortPartnerAdminKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminKey_val_ptr) {
    const char *p_key = NULL;
    p_key = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_PARTNER_KEY);
    if(p_key == NULL)
        *dot3adAggPortPartnerAdminKey_val_ptr = 0;
    else
        *dot3adAggPortPartnerAdminKey_val_ptr = atoi(p_key);

}

void ovsdb_get_dot3adAggPortPartnerOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperKey_val_ptr) {
    const char *p_key = NULL;

    p_key = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_PARTNER_KEY);
    if(p_key == NULL)
        *dot3adAggPortPartnerOperKey_val_ptr = 0;
    else
        *dot3adAggPortPartnerOperKey_val_ptr = atoi(p_key);

}

void ovsdb_get_dot3adAggPortSelectedAggID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortSelectedAggID_val_ptr) {
    dot3adAggPortSelectedAggID_custom_function(
        idl, port_row, interface_row, dot3adAggPortSelectedAggID_val_ptr);
}

void ovsdb_get_dot3adAggPortAttachedAggID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortAttachedAggID_val_ptr) {
    dot3adAggPortAttachedAggID_custom_function(
        idl, port_row, interface_row, dot3adAggPortAttachedAggID_val_ptr);
}

void ovsdb_get_dot3adAggPortActorPort(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPort_val_ptr) {
    dot3adAggPortActorPort_custom_function(idl, port_row, interface_row,
                                           dot3adAggPortActorPort_val_ptr);
}

void ovsdb_get_dot3adAggPortActorPortPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPortPriority_val_ptr) {
    dot3adAggPortActorPortPriority_custom_function(
        idl, port_row, interface_row, dot3adAggPortActorPortPriority_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerAdminPort(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPort_val_ptr) {
    dot3adAggPortPartnerAdminPort_custom_function(
        idl, port_row, interface_row, dot3adAggPortPartnerAdminPort_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerOperPort(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPort_val_ptr) {
    dot3adAggPortPartnerOperPort_custom_function(
        idl, port_row, interface_row, dot3adAggPortPartnerOperPort_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerAdminPortPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPortPriority_val_ptr) {
    dot3adAggPortPartnerAdminPortPriority_custom_function(
        idl, port_row, interface_row,
        dot3adAggPortPartnerAdminPortPriority_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerOperPortPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPortPriority_val_ptr) {
    dot3adAggPortPartnerOperPortPriority_custom_function(
        idl, port_row, interface_row,
        dot3adAggPortPartnerOperPortPriority_val_ptr);
}

void ovsdb_get_dot3adAggPortActorAdminState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorAdminState_val_ptr) {
    dot3adAggPortActorAdminState_custom_function(
        idl, port_row, interface_row, dot3adAggPortActorAdminState_val_ptr);
}

void ovsdb_get_dot3adAggPortActorOperState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorOperState_val_ptr) {
    dot3adAggPortActorOperState_custom_function(
        idl, port_row, interface_row, dot3adAggPortActorOperState_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerAdminState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerAdminState_val_ptr) {
    dot3adAggPortPartnerAdminState_custom_function(
        idl, port_row, interface_row, dot3adAggPortPartnerAdminState_val_ptr);
}

void ovsdb_get_dot3adAggPortPartnerOperState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerOperState_val_ptr) {
    dot3adAggPortPartnerOperState_custom_function(
        idl, port_row, interface_row, dot3adAggPortPartnerOperState_val_ptr);
}

void ovsdb_get_dot3adAggPortAggregateOrIndividual(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortAggregateOrIndividual_val_ptr) {
    //This must change to always true
    *dot3adAggPortAggregateOrIndividual_val_ptr = 1;
}
