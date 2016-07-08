#ifndef DOT3ADAGGTABLE_INTERFACE_H
#define DOT3ADAGGTABLE_INTERFACE_H
#include "dot3adAggTable.h"

void _dot3adAggTable_initialize_interface(dot3adAggTable_registration *user_ctx,
                                          u_long flags);
void _dot3adAggTable_shutdown_interface(dot3adAggTable_registration *user_ctx);
dot3adAggTable_registration *dot3adAggTable_registration_get(void);
dot3adAggTable_registration *
dot3adAggTable_registration_set(dot3adAggTable_registration *newreg);
netsnmp_container *dot3adAggTable_container_get(void);
int dot3adAggTable_container_size(void);
dot3adAggTable_rowreq_ctx *dot3adAggTable_allocate_rowreq_ctx(void *);
void dot3adAggTable_release_rowreq_ctx(dot3adAggTable_rowreq_ctx *rowreq_ctx);
int dot3adAggTable_index_to_oid(netsnmp_index *oid_idx,
                                dot3adAggTable_mib_index *mib_idx);
int dot3adAggTable_index_from_oid(netsnmp_index *oid_idx,
                                  dot3adAggTable_mib_index *mib_idx);
void dot3adAggTable_valid_columns_set(netsnmp_column_info *vc);
#endif