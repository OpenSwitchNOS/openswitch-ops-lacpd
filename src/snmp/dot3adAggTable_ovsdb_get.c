#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggTable_ovsdb_get.h"

void dot3adAggTable_ovsdb_idl_init(struct ovsdb_idl *idl) {
    ovsdb_idl_add_column(idl, &ovsrec_system_col_lacp_config);
    ovsdb_idl_add_column(idl, &ovsrec_interface_col_lacp_status);
    ovsdb_idl_add_column(idl, &ovsrec_interface_col_other_config);
    ovsdb_idl_add_column(idl, &ovsrec_port_col_name);
}

void ovsdb_get_dot3adAggIndex(struct ovsdb_idl *idl,
                              const struct ovsrec_port *port_row,
                              long *dot3adAggIndex_val_ptr) {
    char * temp = port_row->name;
    *dot3adAggIndex_val_ptr = atoi(temp);
}

void ovsdb_get_dot3adAggMACAddress(struct ovsdb_idl *idl,
								   const struct ovsrec_system *system_row,
                                   char *dot3adAggMACAddress_val_ptr,
                                   size_t *dot3adAggMACAddress_val_ptr_len) {
    char *temp = (char *)system_row->system_mac;
    *dot3adAggMACAddress_val_ptr_len = temp != NULL ? strlen(temp) : 0;
    memcpy(dot3adAggMACAddress_val_ptr, temp, *dot3adAggMACAddress_val_ptr_len);
}

void ovsdb_get_dot3adAggActorSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    long *dot3adAggActorSystemPriority_val_ptr) {
    dot3adAggActorSystemPriority_custom_function(
        idl, port_row, system_row, dot3adAggActorSystemPriority_val_ptr);
}

void ovsdb_get_dot3adAggActorSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    char *dot3adAggActorSystemID_val_ptr,
    size_t *dot3adAggActorSystemID_val_ptr_len) {
    dot3adAggActorSystemID_custom_function(idl, port_row, system_row,
                                           dot3adAggActorSystemID_val_ptr,
                                           dot3adAggActorSystemID_val_ptr_len);
}

void ovsdb_get_dot3adAggAggregateOrIndividual(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    long *dot3adAggAggregateOrIndividual_val_ptr) {
    //
    //Always true
    *dot3adAggAggregateOrIndividual_val_ptr = 1;
}

void ovsdb_get_dot3adAggActorAdminKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggActorAdminKey_val_ptr) {
    char *temp =
	(char *)smap_get(&interface_row->other_config,
            INTERFACE_OTHER_CONFIG_MAP_LACP_AGGREGATION_KEY);
	if (temp == NULL) {
            *dot3adAggActorAdminKey_val_ptr = 0;
	} else {
            *dot3adAggActorAdminKey_val_ptr = (long)atoi(temp);
    }
}

void ovsdb_get_dot3adAggActorOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggActorOperKey_val_ptr) {
    char *temp =
        (char *)smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_ACTOR_KEY);
    if (temp == NULL) {
        *dot3adAggActorOperKey_val_ptr = 0;
    } else {
        *dot3adAggActorOperKey_val_ptr = (long)atoi(temp);
	}
}

void ovsdb_get_dot3adAggPartnerSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPartnerSystemID_val_ptr,
    size_t *dot3adAggPartnerSystemID_val_ptr_len) {
    dot3adAggPartnerSystemID_custom_function(
        idl, port_row, interface_row, dot3adAggPartnerSystemID_val_ptr,
        dot3adAggPartnerSystemID_val_ptr_len);
}

void ovsdb_get_dot3adAggPartnerSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    long *dot3adAggPartnerSystemPriority_val_ptr) {
    dot3adAggPartnerSystemPriority_custom_function(
        idl, port_row,interface_row, dot3adAggPartnerSystemPriority_val_ptr);
}

void ovsdb_get_dot3adAggPartnerOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPartnerOperKey_val_ptr) {
    char *temp =
        (char *)smap_get(&interface_row->lacp_status,
            INTERFACE_LACP_STATUS_MAP_PARTNER_KEY);

	if(temp == NULL)
            *dot3adAggPartnerOperKey_val_ptr = 0;
	else
            *dot3adAggPartnerOperKey_val_ptr = atoi(temp);

}

void ovsdb_get_dot3adAggCollectorMaxDelay(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    long *dot3adAggCollectorMaxDelay_val_ptr) {

    *dot3adAggCollectorMaxDelay_val_ptr = 1;
}
