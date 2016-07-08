#ifndef DOT3ADAGGPORTTABLE_OVSDB_GET_H
#define DOT3ADAGGPORTTABLE_OVSDB_GET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

void dot3adAggPortTable_ovsdb_idl_init(struct ovsdb_idl *idl);
void ovsdb_get_dot3adAggPortIndex(struct ovsdb_idl *idl,
                                  const struct ovsrec_interface *interface_row,
                                  long *dot3adAggPortIndex_val_ptr);

void ovsdb_get_dot3adAggPortActorSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorSystemPriority_val_ptr);
void ovsdb_get_dot3adAggPortActorSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    char *dot3adAggPortActorSystemID_val_ptr,
    size_t *dot3adAggPortActorSystemID_val_ptr_len);
void ovsdb_get_dot3adAggPortActorAdminKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorAdminKey_val_ptr);
void ovsdb_get_dot3adAggPortActorOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorOperKey_val_ptr);
void ovsdb_get_dot3adAggPortPartnerAdminSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminSystemPriority_val_ptr);
void ovsdb_get_dot3adAggPortPartnerOperSystemPriority(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperSystemPriority_val_ptr);
void ovsdb_get_dot3adAggPortPartnerAdminSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerAdminSystemID_val_ptr,
    size_t *dot3adAggPortPartnerAdminSystemID_val_ptr_len);
void ovsdb_get_dot3adAggPortPartnerOperSystemID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerOperSystemID_val_ptr,
    size_t *dot3adAggPortPartnerOperSystemID_val_ptr_len);
void ovsdb_get_dot3adAggPortPartnerAdminKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminKey_val_ptr);
void ovsdb_get_dot3adAggPortPartnerOperKey(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperKey_val_ptr);
void ovsdb_get_dot3adAggPortSelectedAggID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortSelectedAggID_val_ptr);
void ovsdb_get_dot3adAggPortAttachedAggID(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortAttachedAggID_val_ptr);
void ovsdb_get_dot3adAggPortActorPort(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPort_val_ptr);
void ovsdb_get_dot3adAggPortActorPortPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPortPriority_val_ptr);
void ovsdb_get_dot3adAggPortPartnerAdminPort(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPort_val_ptr);
void ovsdb_get_dot3adAggPortPartnerOperPort(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPort_val_ptr);
void ovsdb_get_dot3adAggPortPartnerAdminPortPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPortPriority_val_ptr);
void ovsdb_get_dot3adAggPortPartnerOperPortPriority(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPortPriority_val_ptr);
void ovsdb_get_dot3adAggPortActorAdminState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorAdminState_val_ptr);
void ovsdb_get_dot3adAggPortActorOperState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorOperState_val_ptr);
void ovsdb_get_dot3adAggPortPartnerAdminState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerAdminState_val_ptr);
void ovsdb_get_dot3adAggPortPartnerOperState(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerOperState_val_ptr);
void ovsdb_get_dot3adAggPortAggregateOrIndividual(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortAggregateOrIndividual_val_ptr);
#endif
