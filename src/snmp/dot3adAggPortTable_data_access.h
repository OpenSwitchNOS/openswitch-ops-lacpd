#ifndef DOT3ADAGGPORTTABLE_DATA_ACCESS_H
#define DOT3ADAGGPORTTABLE_DATA_ACCESS_H

extern struct ovsdb_idl *idl;

int dot3adAggPortTable_init_data(
    dot3adAggPortTable_registration *dot3adAggPortTable_reg);
#define DOT3ADAGGPORTTABLE_CACHE_TIMEOUT 30
void dot3adAggPortTable_container_init(netsnmp_container **container_ptr_ptr,
                                       netsnmp_cache *cache);
void dot3adAggPortTable_container_shutdown(netsnmp_container *container_ptr);
int dot3adAggPortTable_container_load(netsnmp_container *container);
void dot3adAggPortTable_container_free(netsnmp_container *container);
int dot3adAggPortTable_cache_load(netsnmp_container *container);
void dot3adAggPortTable_cache_free(netsnmp_container *container);
int dot3adAggPortTable_row_prep(dot3adAggPortTable_rowreq_ctx *rowreq_ctx);
#endif