#ifndef DOT3ADAGGPORTLISTTABLE_H
#define DOT3ADAGGPORTLISTTABLE_H
#include <net-snmp/library/asn1.h>
#include "dot3adAggPortListTable_oids.h"
#include "dot3adAggPortListTable_enums.h"

void init_dot3adAggPortListTable(void);
void shutdown_dot3adAggPortListTable(void);

typedef netsnmp_data_list dot3adAggPortListTable_registration;

typedef struct dot3adAggPortListTable_data_s {
    char dot3adAggPortListPorts[255];
    size_t dot3adAggPortListPorts_len;
} dot3adAggPortListTable_data;

typedef struct dot3adAggPortListTable_mib_index_s {
    long dot3adAggIndex;
} dot3adAggPortListTable_mib_index;

typedef struct dot3adAggPortListTable_rowreq_ctx_s {
    netsnmp_index oid_idx;
    oid oid_tmp[MAX_OID_LEN];
    dot3adAggPortListTable_mib_index tbl_idx;
    dot3adAggPortListTable_data data;
    u_int rowreq_flags;
    netsnmp_data_list *dot3adAggPortListTable_data_list;
} dot3adAggPortListTable_rowreq_ctx;

typedef struct dot3adAggPortListTable_ref_rowreq_ctx_s {
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx;
} dot3adAggPortListTable_ref_rowreq_ctx;

int dot3adAggPortListTable_pre_request(
    dot3adAggPortListTable_registration *user_context);
int dot3adAggPortListTable_post_request(
    dot3adAggPortListTable_registration *user_context, int rc);
int dot3adAggPortListTable_rowreq_ctx_init(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx, void *user_init_ctx);
void dot3adAggPortListTable_rowreq_ctx_cleanup(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx);
dot3adAggPortListTable_rowreq_ctx *dot3adAggPortListTable_row_find_by_mib_index(
    dot3adAggPortListTable_mib_index *mib_idx);
extern const oid dot3adAggPortListTable_oid[];
extern const int dot3adAggPortListTable_oid_size;
#include "dot3adAggPortListTable_interface.h"
#include "dot3adAggPortListTable_data_access.h"
#include "dot3adAggPortListTable_data_get.h"
#include "dot3adAggPortListTable_data_set.h"

#endif