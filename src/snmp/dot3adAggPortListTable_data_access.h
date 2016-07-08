#ifndef DOT3ADAGGPORTLISTTABLE_DATA_ACCESS_H
#define DOT3ADAGGPORTLISTTABLE_DATA_ACCESS_H

extern struct ovsdb_idl *idl;

int dot3adAggPortListTable_init_data(
    dot3adAggPortListTable_registration *dot3adAggPortListTable_reg);
#define DOT3ADAGGPORTLISTTABLE_CACHE_TIMEOUT 30
void dot3adAggPortListTable_container_init(
    netsnmp_container **container_ptr_ptr, netsnmp_cache *cache);
void dot3adAggPortListTable_container_shutdown(
    netsnmp_container *container_ptr);
int dot3adAggPortListTable_container_load(netsnmp_container *container);
void dot3adAggPortListTable_container_free(netsnmp_container *container);
int dot3adAggPortListTable_cache_load(netsnmp_container *container);
void dot3adAggPortListTable_cache_free(netsnmp_container *container);
int dot3adAggPortListTable_row_prep(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx);
#endif