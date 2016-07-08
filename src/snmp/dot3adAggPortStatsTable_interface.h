#ifndef DOT3ADAGGPORTSTATSTABLE_INTERFACE_H
#define DOT3ADAGGPORTSTATSTABLE_INTERFACE_H
#include "dot3adAggPortStatsTable.h"

void _dot3adAggPortStatsTable_initialize_interface(
    dot3adAggPortStatsTable_registration *user_ctx, u_long flags);
void _dot3adAggPortStatsTable_shutdown_interface(
    dot3adAggPortStatsTable_registration *user_ctx);
dot3adAggPortStatsTable_registration *
dot3adAggPortStatsTable_registration_get(void);
dot3adAggPortStatsTable_registration *dot3adAggPortStatsTable_registration_set(
    dot3adAggPortStatsTable_registration *newreg);
netsnmp_container *dot3adAggPortStatsTable_container_get(void);
int dot3adAggPortStatsTable_container_size(void);
dot3adAggPortStatsTable_rowreq_ctx *
dot3adAggPortStatsTable_allocate_rowreq_ctx(void *);
void dot3adAggPortStatsTable_release_rowreq_ctx(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx);
int dot3adAggPortStatsTable_index_to_oid(
    netsnmp_index *oid_idx, dot3adAggPortStatsTable_mib_index *mib_idx);
int dot3adAggPortStatsTable_index_from_oid(
    netsnmp_index *oid_idx, dot3adAggPortStatsTable_mib_index *mib_idx);
void dot3adAggPortStatsTable_valid_columns_set(netsnmp_column_info *vc);
#endif