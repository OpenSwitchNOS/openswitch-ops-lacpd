#ifndef DOT3ADAGGPORTLISTTABLE_INTERFACE_H
#define DOT3ADAGGPORTLISTTABLE_INTERFACE_H
#include "dot3adAggPortListTable.h"

void _dot3adAggPortListTable_initialize_interface(
    dot3adAggPortListTable_registration *user_ctx, u_long flags);
void _dot3adAggPortListTable_shutdown_interface(
    dot3adAggPortListTable_registration *user_ctx);
dot3adAggPortListTable_registration *
dot3adAggPortListTable_registration_get(void);
dot3adAggPortListTable_registration *dot3adAggPortListTable_registration_set(
    dot3adAggPortListTable_registration *newreg);
netsnmp_container *dot3adAggPortListTable_container_get(void);
int dot3adAggPortListTable_container_size(void);
dot3adAggPortListTable_rowreq_ctx *
dot3adAggPortListTable_allocate_rowreq_ctx(void *);
void dot3adAggPortListTable_release_rowreq_ctx(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx);
int dot3adAggPortListTable_index_to_oid(
    netsnmp_index *oid_idx, dot3adAggPortListTable_mib_index *mib_idx);
int dot3adAggPortListTable_index_from_oid(
    netsnmp_index *oid_idx, dot3adAggPortListTable_mib_index *mib_idx);
void dot3adAggPortListTable_valid_columns_set(netsnmp_column_info *vc);
#endif