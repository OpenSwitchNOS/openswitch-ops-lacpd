#ifndef DOT3ADAGGTABLE_OVSDB_GET_H
#define DOT3ADAGGTABLE_OVSDB_GET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

void dot3adAggTable_ovsdb_idl_init(struct ovsdb_idl *idl);
void ovsdb_get_dot3adAggIndex(struct ovsdb_idl *idl,
                              const struct ovsrec_port *port_row,
                              long *dot3adAggIndex_val_ptr);

void ovsdb_get_dot3adAggMACAddress(struct ovsdb_idl *idl,
								   const struct ovsrec_system *system_row,
                                   char *dot3adAggMACAddress_val_ptr,
                                   size_t *dot3adAggMACAddress_val_ptr_len);
void ovsdb_get_dot3adAggActorSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    long *dot3adAggActorSystemPriority_val_ptr);
void ovsdb_get_dot3adAggActorSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    char *dot3adAggActorSystemID_val_ptr,
    size_t *dot3adAggActorSystemID_val_ptr_len);
void ovsdb_get_dot3adAggAggregateOrIndividual(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    long *dot3adAggAggregateOrIndividual_val_ptr);
void ovsdb_get_dot3adAggActorAdminKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggActorAdminKey_val_ptr);
void ovsdb_get_dot3adAggActorOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggActorOperKey_val_ptr);
void ovsdb_get_dot3adAggPartnerSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPartnerSystemID_val_ptr,
    size_t *dot3adAggPartnerSystemID_val_ptr_len);
void ovsdb_get_dot3adAggPartnerSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    long *dot3adAggPartnerSystemPriority_val_ptr);
void ovsdb_get_dot3adAggPartnerOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPartnerOperKey_val_ptr);
void ovsdb_get_dot3adAggCollectorMaxDelay(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    long *dot3adAggCollectorMaxDelay_val_ptr);
#endif
