#ifndef DOT3ADAGGPORTTABLE_H
#define DOT3ADAGGPORTTABLE_H
#include <net-snmp/library/asn1.h>
#include "dot3adAggPortTable_oids.h"
#include "dot3adAggPortTable_enums.h"

void init_dot3adAggPortTable(void);
void shutdown_dot3adAggPortTable(void);

typedef netsnmp_data_list dot3adAggPortTable_registration;

typedef struct dot3adAggPortTable_data_s {
    long dot3adAggPortActorSystemPriority;
    char dot3adAggPortActorSystemID[255];
    size_t dot3adAggPortActorSystemID_len;
    long dot3adAggPortActorAdminKey;
    long dot3adAggPortActorOperKey;
    long dot3adAggPortPartnerAdminSystemPriority;
    long dot3adAggPortPartnerOperSystemPriority;
    char dot3adAggPortPartnerAdminSystemID[255];
    size_t dot3adAggPortPartnerAdminSystemID_len;
    char dot3adAggPortPartnerOperSystemID[255];
    size_t dot3adAggPortPartnerOperSystemID_len;
    long dot3adAggPortPartnerAdminKey;
    long dot3adAggPortPartnerOperKey;
    long dot3adAggPortSelectedAggID;
    long dot3adAggPortAttachedAggID;
    long dot3adAggPortActorPort;
    long dot3adAggPortActorPortPriority;
    long dot3adAggPortPartnerAdminPort;
    long dot3adAggPortPartnerOperPort;
    long dot3adAggPortPartnerAdminPortPriority;
    long dot3adAggPortPartnerOperPortPriority;
    u_long dot3adAggPortActorAdminState;
    u_long dot3adAggPortActorOperState;
    u_long dot3adAggPortPartnerAdminState;
    u_long dot3adAggPortPartnerOperState;
    long dot3adAggPortAggregateOrIndividual;
} dot3adAggPortTable_data;

typedef struct dot3adAggPortTable_mib_index_s {
    long dot3adAggPortIndex;
} dot3adAggPortTable_mib_index;

typedef struct dot3adAggPortTable_rowreq_ctx_s {
    netsnmp_index oid_idx;
    oid oid_tmp[MAX_OID_LEN];
    dot3adAggPortTable_mib_index tbl_idx;
    dot3adAggPortTable_data data;
    u_int rowreq_flags;
    netsnmp_data_list *dot3adAggPortTable_data_list;
} dot3adAggPortTable_rowreq_ctx;

typedef struct dot3adAggPortTable_ref_rowreq_ctx_s {
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx;
} dot3adAggPortTable_ref_rowreq_ctx;

int dot3adAggPortTable_pre_request(
    dot3adAggPortTable_registration *user_context);
int dot3adAggPortTable_post_request(
    dot3adAggPortTable_registration *user_context, int rc);
int dot3adAggPortTable_rowreq_ctx_init(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx, void *user_init_ctx);
void dot3adAggPortTable_rowreq_ctx_cleanup(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx);
dot3adAggPortTable_rowreq_ctx *
dot3adAggPortTable_row_find_by_mib_index(dot3adAggPortTable_mib_index *mib_idx);
extern const oid dot3adAggPortTable_oid[];
extern const int dot3adAggPortTable_oid_size;
#include "dot3adAggPortTable_interface.h"
#include "dot3adAggPortTable_data_access.h"
#include "dot3adAggPortTable_data_get.h"
#include "dot3adAggPortTable_data_set.h"

#endif