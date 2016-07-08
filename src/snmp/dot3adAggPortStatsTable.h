#ifndef DOT3ADAGGPORTSTATSTABLE_H
#define DOT3ADAGGPORTSTATSTABLE_H
#include <net-snmp/library/asn1.h>
#include "dot3adAggPortStatsTable_oids.h"
#include "dot3adAggPortStatsTable_enums.h"

void init_dot3adAggPortStatsTable(void);
void shutdown_dot3adAggPortStatsTable(void);

typedef netsnmp_data_list dot3adAggPortStatsTable_registration;

typedef struct dot3adAggPortStatsTable_data_s {
    u_long dot3adAggPortStatsLACPDUsRx;
    u_long dot3adAggPortStatsMarkerPDUsRx;
    u_long dot3adAggPortStatsMarkerResponsePDUsRx;
    u_long dot3adAggPortStatsUnknownRx;
    u_long dot3adAggPortStatsIllegalRx;
    u_long dot3adAggPortStatsLACPDUsTx;
    u_long dot3adAggPortStatsMarkerPDUsTx;
    u_long dot3adAggPortStatsMarkerResponsePDUsTx;
} dot3adAggPortStatsTable_data;

typedef struct dot3adAggPortStatsTable_mib_index_s {
    long dot3adAggPortIndex;
} dot3adAggPortStatsTable_mib_index;

typedef struct dot3adAggPortStatsTable_rowreq_ctx_s {
    netsnmp_index oid_idx;
    oid oid_tmp[MAX_OID_LEN];
    dot3adAggPortStatsTable_mib_index tbl_idx;
    dot3adAggPortStatsTable_data data;
    u_int rowreq_flags;
    netsnmp_data_list *dot3adAggPortStatsTable_data_list;
} dot3adAggPortStatsTable_rowreq_ctx;

typedef struct dot3adAggPortStatsTable_ref_rowreq_ctx_s {
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx;
} dot3adAggPortStatsTable_ref_rowreq_ctx;

int dot3adAggPortStatsTable_pre_request(
    dot3adAggPortStatsTable_registration *user_context);
int dot3adAggPortStatsTable_post_request(
    dot3adAggPortStatsTable_registration *user_context, int rc);
int dot3adAggPortStatsTable_rowreq_ctx_init(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx, void *user_init_ctx);
void dot3adAggPortStatsTable_rowreq_ctx_cleanup(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx);
dot3adAggPortStatsTable_rowreq_ctx *
dot3adAggPortStatsTable_row_find_by_mib_index(
    dot3adAggPortStatsTable_mib_index *mib_idx);
extern const oid dot3adAggPortStatsTable_oid[];
extern const int dot3adAggPortStatsTable_oid_size;
#include "dot3adAggPortStatsTable_interface.h"
#include "dot3adAggPortStatsTable_data_access.h"
#include "dot3adAggPortStatsTable_data_get.h"
#include "dot3adAggPortStatsTable_data_set.h"

#endif