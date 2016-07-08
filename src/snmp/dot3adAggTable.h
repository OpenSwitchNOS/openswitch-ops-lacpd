#ifndef DOT3ADAGGTABLE_H
#define DOT3ADAGGTABLE_H
#include <net-snmp/library/asn1.h>
#include "dot3adAggTable_oids.h"
#include "dot3adAggTable_enums.h"

void init_dot3adAggTable(void);
void shutdown_dot3adAggTable(void);

typedef netsnmp_data_list dot3adAggTable_registration;

typedef struct dot3adAggTable_data_s {
    char dot3adAggMACAddress[255];
    size_t dot3adAggMACAddress_len;
    long dot3adAggActorSystemPriority;
    char dot3adAggActorSystemID[255];
    size_t dot3adAggActorSystemID_len;
    long dot3adAggAggregateOrIndividual;
    long dot3adAggActorAdminKey;
    long dot3adAggActorOperKey;
    char dot3adAggPartnerSystemID[255];
    size_t dot3adAggPartnerSystemID_len;
    long dot3adAggPartnerSystemPriority;
    long dot3adAggPartnerOperKey;
    long dot3adAggCollectorMaxDelay;
} dot3adAggTable_data;

typedef struct dot3adAggTable_mib_index_s {
    long dot3adAggIndex;
} dot3adAggTable_mib_index;

typedef struct dot3adAggTable_rowreq_ctx_s {
    netsnmp_index oid_idx;
    oid oid_tmp[MAX_OID_LEN];
    dot3adAggTable_mib_index tbl_idx;
    dot3adAggTable_data data;
    u_int rowreq_flags;
    netsnmp_data_list *dot3adAggTable_data_list;
} dot3adAggTable_rowreq_ctx;

typedef struct dot3adAggTable_ref_rowreq_ctx_s {
    dot3adAggTable_rowreq_ctx *rowreq_ctx;
} dot3adAggTable_ref_rowreq_ctx;

int dot3adAggTable_pre_request(dot3adAggTable_registration *user_context);
int dot3adAggTable_post_request(dot3adAggTable_registration *user_context,
                                int rc);
int dot3adAggTable_rowreq_ctx_init(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                                   void *user_init_ctx);
void dot3adAggTable_rowreq_ctx_cleanup(dot3adAggTable_rowreq_ctx *rowreq_ctx);
dot3adAggTable_rowreq_ctx *
dot3adAggTable_row_find_by_mib_index(dot3adAggTable_mib_index *mib_idx);
extern const oid dot3adAggTable_oid[];
extern const int dot3adAggTable_oid_size;
#include "dot3adAggTable_interface.h"
#include "dot3adAggTable_data_access.h"
#include "dot3adAggTable_data_get.h"
#include "dot3adAggTable_data_set.h"

#endif