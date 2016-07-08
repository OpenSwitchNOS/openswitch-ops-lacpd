#ifndef DOT3ADAGGPORTSTATSTABLE_DATA_ACCESS_H
#define DOT3ADAGGPORTSTATSTABLE_DATA_ACCESS_H

extern struct ovsdb_idl *idl;

int dot3adAggPortStatsTable_init_data(
    dot3adAggPortStatsTable_registration *dot3adAggPortStatsTable_reg);
#define DOT3ADAGGPORTSTATSTABLE_CACHE_TIMEOUT 30
void dot3adAggPortStatsTable_container_init(
    netsnmp_container **container_ptr_ptr, netsnmp_cache *cache);
void dot3adAggPortStatsTable_container_shutdown(
    netsnmp_container *container_ptr);
int dot3adAggPortStatsTable_container_load(netsnmp_container *container);
void dot3adAggPortStatsTable_container_free(netsnmp_container *container);
int dot3adAggPortStatsTable_cache_load(netsnmp_container *container);
void dot3adAggPortStatsTable_cache_free(netsnmp_container *container);
int dot3adAggPortStatsTable_row_prep(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx);
#endif