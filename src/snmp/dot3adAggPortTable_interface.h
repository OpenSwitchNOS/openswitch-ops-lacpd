#ifndef DOT3ADAGGPORTTABLE_INTERFACE_H
#define DOT3ADAGGPORTTABLE_INTERFACE_H
#include "dot3adAggPortTable.h"

void _dot3adAggPortTable_initialize_interface(
    dot3adAggPortTable_registration *user_ctx, u_long flags);
void _dot3adAggPortTable_shutdown_interface(
    dot3adAggPortTable_registration *user_ctx);
dot3adAggPortTable_registration *dot3adAggPortTable_registration_get(void);
dot3adAggPortTable_registration *
dot3adAggPortTable_registration_set(dot3adAggPortTable_registration *newreg);
netsnmp_container *dot3adAggPortTable_container_get(void);
int dot3adAggPortTable_container_size(void);
dot3adAggPortTable_rowreq_ctx *dot3adAggPortTable_allocate_rowreq_ctx(void *);
void dot3adAggPortTable_release_rowreq_ctx(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx);
int dot3adAggPortTable_index_to_oid(netsnmp_index *oid_idx,
                                    dot3adAggPortTable_mib_index *mib_idx);
int dot3adAggPortTable_index_from_oid(netsnmp_index *oid_idx,
                                      dot3adAggPortTable_mib_index *mib_idx);
void dot3adAggPortTable_valid_columns_set(netsnmp_column_info *vc);
#endif