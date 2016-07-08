#ifndef DOT3ADAGGTABLE_DATA_ACCESS_H
#define DOT3ADAGGTABLE_DATA_ACCESS_H

extern struct ovsdb_idl *idl;

int dot3adAggTable_init_data(dot3adAggTable_registration *dot3adAggTable_reg);
#define DOT3ADAGGTABLE_CACHE_TIMEOUT 30
void dot3adAggTable_container_init(netsnmp_container **container_ptr_ptr,
                                   netsnmp_cache *cache);
void dot3adAggTable_container_shutdown(netsnmp_container *container_ptr);
int dot3adAggTable_container_load(netsnmp_container *container);
void dot3adAggTable_container_free(netsnmp_container *container);
int dot3adAggTable_cache_load(netsnmp_container *container);
void dot3adAggTable_cache_free(netsnmp_container *container);
int dot3adAggTable_row_prep(dot3adAggTable_rowreq_ctx *rowreq_ctx);
#endif