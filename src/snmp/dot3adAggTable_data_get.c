#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "dot3adAggTable.h"

int dot3adAggTable_indexes_set_tbl_idx(dot3adAggTable_mib_index *tbl_idx,
                                       long dot3adAggIndex_val) {
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggTable_indexes_set_tbl_idx",
                "called\n"));

    tbl_idx->dot3adAggIndex = dot3adAggIndex_val;
    return MFD_SUCCESS;
}

int dot3adAggTable_indexes_set(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                               long dot3adAggIndex_val) {
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggTable_indexes_set", "called\n"));
    if (MFD_SUCCESS != dot3adAggTable_indexes_set_tbl_idx(&rowreq_ctx->tbl_idx,
                                                          dot3adAggIndex_val)) {
        return MFD_ERROR;
    }
    rowreq_ctx->oid_idx.len = sizeof(rowreq_ctx->oid_tmp) / sizeof(oid);
    if (0 != dot3adAggTable_index_to_oid(&rowreq_ctx->oid_idx,
                                         &rowreq_ctx->tbl_idx)) {
        return MFD_ERROR;
    }
    return MFD_SUCCESS;
}

int dot3adAggMACAddress_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                            char **dot3adAggMACAddress_val_ptr_ptr,
                            size_t *dot3adAggMACAddress_val_ptr_len_ptr) {
    netsnmp_assert((NULL != dot3adAggMACAddress_val_ptr_ptr) &&
                   (NULL != *dot3adAggMACAddress_val_ptr_ptr));
    netsnmp_assert(NULL != dot3adAggMACAddress_val_ptr_len_ptr);
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggMACAddress_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    if ((NULL == (*dot3adAggMACAddress_val_ptr_ptr)) ||
        ((*dot3adAggMACAddress_val_ptr_len_ptr) <
         (rowreq_ctx->data.dot3adAggMACAddress_len *
          sizeof(rowreq_ctx->data.dot3adAggMACAddress[0])))) {
        (*dot3adAggMACAddress_val_ptr_ptr) =
            malloc(rowreq_ctx->data.dot3adAggMACAddress_len *
                   sizeof(rowreq_ctx->data.dot3adAggMACAddress[0]));
        if (NULL == (*dot3adAggMACAddress_val_ptr_ptr)) {
            snmp_log(LOG_ERR, "could not allocate memory "
                              "(rowreq_ctx->data.dot3adAggMACAddress)\n");
            return MFD_ERROR;
        }
    }
    (*dot3adAggMACAddress_val_ptr_len_ptr) =
        rowreq_ctx->data.dot3adAggMACAddress_len *
        sizeof(rowreq_ctx->data.dot3adAggMACAddress[0]);
    memcpy((*dot3adAggMACAddress_val_ptr_ptr),
           rowreq_ctx->data.dot3adAggMACAddress,
           rowreq_ctx->data.dot3adAggMACAddress_len *
               sizeof(rowreq_ctx->data.dot3adAggMACAddress[0]));
    return MFD_SUCCESS;
}

int dot3adAggActorSystemPriority_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggActorSystemPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggActorSystemPriority_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggActorSystemPriority_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggActorSystemPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggActorSystemPriority;
    return MFD_SUCCESS;
}

int dot3adAggActorSystemID_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                               char **dot3adAggActorSystemID_val_ptr_ptr,
                               size_t *dot3adAggActorSystemID_val_ptr_len_ptr) {
    netsnmp_assert((NULL != dot3adAggActorSystemID_val_ptr_ptr) &&
                   (NULL != *dot3adAggActorSystemID_val_ptr_ptr));
    netsnmp_assert(NULL != dot3adAggActorSystemID_val_ptr_len_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggActorSystemID_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    if ((NULL == (*dot3adAggActorSystemID_val_ptr_ptr)) ||
        ((*dot3adAggActorSystemID_val_ptr_len_ptr) <
         (rowreq_ctx->data.dot3adAggActorSystemID_len *
          sizeof(rowreq_ctx->data.dot3adAggActorSystemID[0])))) {
        (*dot3adAggActorSystemID_val_ptr_ptr) =
            malloc(rowreq_ctx->data.dot3adAggActorSystemID_len *
                   sizeof(rowreq_ctx->data.dot3adAggActorSystemID[0]));
        if (NULL == (*dot3adAggActorSystemID_val_ptr_ptr)) {
            snmp_log(LOG_ERR, "could not allocate memory "
                              "(rowreq_ctx->data.dot3adAggActorSystemID)\n");
            return MFD_ERROR;
        }
    }
    (*dot3adAggActorSystemID_val_ptr_len_ptr) =
        rowreq_ctx->data.dot3adAggActorSystemID_len *
        sizeof(rowreq_ctx->data.dot3adAggActorSystemID[0]);
    memcpy((*dot3adAggActorSystemID_val_ptr_ptr),
           rowreq_ctx->data.dot3adAggActorSystemID,
           rowreq_ctx->data.dot3adAggActorSystemID_len *
               sizeof(rowreq_ctx->data.dot3adAggActorSystemID[0]));
    return MFD_SUCCESS;
}

int dot3adAggAggregateOrIndividual_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggAggregateOrIndividual_val_ptr) {
    netsnmp_assert(NULL != dot3adAggAggregateOrIndividual_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggAggregateOrIndividual_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggAggregateOrIndividual_val_ptr) =
        rowreq_ctx->data.dot3adAggAggregateOrIndividual;
    return MFD_SUCCESS;
}

int dot3adAggActorAdminKey_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                               long *dot3adAggActorAdminKey_val_ptr) {
    netsnmp_assert(NULL != dot3adAggActorAdminKey_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggActorAdminKey_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggActorAdminKey_val_ptr) = rowreq_ctx->data.dot3adAggActorAdminKey;
    return MFD_SUCCESS;
}

int dot3adAggActorOperKey_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                              long *dot3adAggActorOperKey_val_ptr) {
    netsnmp_assert(NULL != dot3adAggActorOperKey_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggActorOperKey_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggActorOperKey_val_ptr) = rowreq_ctx->data.dot3adAggActorOperKey;
    return MFD_SUCCESS;
}

int dot3adAggPartnerSystemID_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPartnerSystemID_val_ptr_ptr,
    size_t *dot3adAggPartnerSystemID_val_ptr_len_ptr) {
    netsnmp_assert((NULL != dot3adAggPartnerSystemID_val_ptr_ptr) &&
                   (NULL != *dot3adAggPartnerSystemID_val_ptr_ptr));
    netsnmp_assert(NULL != dot3adAggPartnerSystemID_val_ptr_len_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggPartnerSystemID_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    if ((NULL == (*dot3adAggPartnerSystemID_val_ptr_ptr)) ||
        ((*dot3adAggPartnerSystemID_val_ptr_len_ptr) <
         (rowreq_ctx->data.dot3adAggPartnerSystemID_len *
          sizeof(rowreq_ctx->data.dot3adAggPartnerSystemID[0])))) {
        (*dot3adAggPartnerSystemID_val_ptr_ptr) =
            malloc(rowreq_ctx->data.dot3adAggPartnerSystemID_len *
                   sizeof(rowreq_ctx->data.dot3adAggPartnerSystemID[0]));
        if (NULL == (*dot3adAggPartnerSystemID_val_ptr_ptr)) {
            snmp_log(LOG_ERR, "could not allocate memory "
                              "(rowreq_ctx->data.dot3adAggPartnerSystemID)\n");
            return MFD_ERROR;
        }
    }
    (*dot3adAggPartnerSystemID_val_ptr_len_ptr) =
        rowreq_ctx->data.dot3adAggPartnerSystemID_len *
        sizeof(rowreq_ctx->data.dot3adAggPartnerSystemID[0]);
    memcpy((*dot3adAggPartnerSystemID_val_ptr_ptr),
           rowreq_ctx->data.dot3adAggPartnerSystemID,
           rowreq_ctx->data.dot3adAggPartnerSystemID_len *
               sizeof(rowreq_ctx->data.dot3adAggPartnerSystemID[0]));
    return MFD_SUCCESS;
}

int dot3adAggPartnerSystemPriority_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPartnerSystemPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPartnerSystemPriority_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggPartnerSystemPriority_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPartnerSystemPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggPartnerSystemPriority;
    return MFD_SUCCESS;
}

int dot3adAggPartnerOperKey_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                                long *dot3adAggPartnerOperKey_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPartnerOperKey_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggPartnerOperKey_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPartnerOperKey_val_ptr) =
        rowreq_ctx->data.dot3adAggPartnerOperKey;
    return MFD_SUCCESS;
}

int dot3adAggCollectorMaxDelay_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggCollectorMaxDelay_val_ptr) {
    netsnmp_assert(NULL != dot3adAggCollectorMaxDelay_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggCollectorMaxDelay_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggCollectorMaxDelay_val_ptr) =
        rowreq_ctx->data.dot3adAggCollectorMaxDelay;
    return MFD_SUCCESS;
}
