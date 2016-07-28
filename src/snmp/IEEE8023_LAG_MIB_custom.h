#ifndef IEEE8023_LAG_MIB_CUSTOM_H
#define IEEE8023_LAG_MIB_CUSTOM_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "vswitch-idl.h"
#include "openswitch-idl.h"
#include "ops-utils.h"
#include "openswitch-dflt.h"



void parse_id_from_db (char *str, char **value1, char **value2);

int dot3adAggTable_skip_function(struct ovsdb_idl *idl,
                                 const struct ovsrec_port *port_row);

void dot3adAggIndex_custom_function(struct ovsdb_idl *idl,
                                    const struct ovsrec_port *port_row,
                                    long *dot3adAggIndex_val_ptr);

void dot3adAggActorSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    long *dot3adAggActorSystemPriority_val_ptr);

void dot3adAggActorSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    char * dot3adAggActorSystemID_val_ptr,
    size_t *dot3adAggActorSystemID_val_ptr_len);

void dot3adAggPartnerSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPartnerSystemID_val_ptr,
    size_t *dot3adAggPartnerSystemID_val_ptr_len);

void dot3adAggPartnerSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPartnerSystemPriority_val_ptr);

void dot3adAggCollectorMaxDelay_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    long *dot3adAggCollectorMaxDelay_val_ptr);

int Dot3adAggPortListEntry_skip_function(struct ovsdb_idl *idl,
                                         const struct ovsrec_port *port_row);

void dot3adAggPortListPorts_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    char *dot3adAggPortListPorts_val_ptr,
    size_t *dot3adAggPortListPorts_val_ptr_len);

int dot3adAggPortStats_skip_function(struct ovsdb_idl *idl,
                                     const struct ovsrec_port *port_row);

void dot3adAggPortStatsIndex_custom_function(struct ovsdb_idl *idl,
                                             const struct ovsrec_port *port_row,
                                             long *dot3adAggPortIndex_val_ptr);

int dot3adAggPortEntry_skip_function(struct ovsdb_idl *idl,
    const struct ovsrec_interface *interface_row);

void dot3adAggPortIndex_custom_function(struct ovsdb_idl *idl,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortIndex_val_ptr);

void dot3adAggPortActorSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorSystemPriority_val_ptr);

void dot3adAggPortActorSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    char *dot3adAggPortActorSystemID_val_ptr,
    size_t *dot3adAggPortActorSystemID_val_ptr_len);

void dot3adAggPortPartnerAdminSystemPriority_custom_function(
    struct ovsdb_idl *idl, 
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminSystemPriority_val_ptr);

void dot3adAggPortPartnerOperSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperSystemPriority_val_ptr);

void dot3adAggPortPartnerAdminSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerAdminSystemID_val_ptr,
    size_t *dot3adAggPortPartnerAdminSystemID_val_ptr_len);

void dot3adAggPortPartnerOperSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerOperSystemID_val_ptr,
    size_t *dot3adAggPortPartnerOperSystemID_val_ptr_len);

void dot3adAggPortSelectedAggID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortSelectedAggID_val_ptr);

void dot3adAggPortAttachedAggID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortAttachedAggID_val_ptr);

void dot3adAggPortActorPort_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPort_val_ptr);

void dot3adAggPortActorPortPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPortPriority_val_ptr);

void dot3adAggPortPartnerAdminPort_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPort_val_ptr);

void dot3adAggPortPartnerOperPort_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPort_val_ptr);

void dot3adAggPortPartnerAdminPortPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPortPriority_val_ptr);

void dot3adAggPortPartnerOperPortPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPortPriority_val_ptr);

void dot3adAggPortActorAdminState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorAdminState_val_ptr);

void dot3adAggPortActorOperState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorOperState_val_ptr);

void dot3adAggPortPartnerAdminState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerAdminState_val_ptr);

void dot3adAggPortPartnerOperState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerOperState_val_ptr);







#endif
