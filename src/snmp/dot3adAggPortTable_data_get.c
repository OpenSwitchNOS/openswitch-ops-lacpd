#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "dot3adAggPortTable.h"

int dot3adAggPortTable_indexes_set_tbl_idx(
    dot3adAggPortTable_mib_index *tbl_idx, long dot3adAggPortIndex_val) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortTable_indexes_set_tbl_idx",
         "called\n"));

    tbl_idx->dot3adAggPortIndex = dot3adAggPortIndex_val;
    return MFD_SUCCESS;
}

int dot3adAggPortTable_indexes_set(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long dot3adAggPortIndex_val) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_indexes_set",
                "called\n"));
    if (MFD_SUCCESS != dot3adAggPortTable_indexes_set_tbl_idx(
                           &rowreq_ctx->tbl_idx, dot3adAggPortIndex_val)) {
        return MFD_ERROR;
    }
    rowreq_ctx->oid_idx.len = sizeof(rowreq_ctx->oid_tmp) / sizeof(oid);
    if (0 != dot3adAggPortTable_index_to_oid(&rowreq_ctx->oid_idx,
                                             &rowreq_ctx->tbl_idx)) {
        return MFD_ERROR;
    }
    return MFD_SUCCESS;
}

int dot3adAggPortActorSystemPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortActorSystemPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortActorSystemPriority_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortActorSystemPriority_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortActorSystemPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggPortActorSystemPriority;
    return MFD_SUCCESS;
}

int dot3adAggPortActorSystemID_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPortActorSystemID_val_ptr_ptr,
    size_t *dot3adAggPortActorSystemID_val_ptr_len_ptr) {
    netsnmp_assert((NULL != dot3adAggPortActorSystemID_val_ptr_ptr) &&
                   (NULL != *dot3adAggPortActorSystemID_val_ptr_ptr));
    netsnmp_assert(NULL != dot3adAggPortActorSystemID_val_ptr_len_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortActorSystemID_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    if ((NULL == (*dot3adAggPortActorSystemID_val_ptr_ptr)) ||
        ((*dot3adAggPortActorSystemID_val_ptr_len_ptr) <
         (rowreq_ctx->data.dot3adAggPortActorSystemID_len *
          sizeof(rowreq_ctx->data.dot3adAggPortActorSystemID[0])))) {
        (*dot3adAggPortActorSystemID_val_ptr_ptr) =
            malloc(rowreq_ctx->data.dot3adAggPortActorSystemID_len *
                   sizeof(rowreq_ctx->data.dot3adAggPortActorSystemID[0]));
        if (NULL == (*dot3adAggPortActorSystemID_val_ptr_ptr)) {
            snmp_log(LOG_ERR, "could not allocate memory "
                              "(rowreq_ctx->data.dot3adAggPortActorSystemID)"
                              "\n");
            return MFD_ERROR;
        }
    }
    (*dot3adAggPortActorSystemID_val_ptr_len_ptr) =
        rowreq_ctx->data.dot3adAggPortActorSystemID_len *
        sizeof(rowreq_ctx->data.dot3adAggPortActorSystemID[0]);
    memcpy((*dot3adAggPortActorSystemID_val_ptr_ptr),
           rowreq_ctx->data.dot3adAggPortActorSystemID,
           rowreq_ctx->data.dot3adAggPortActorSystemID_len *
               sizeof(rowreq_ctx->data.dot3adAggPortActorSystemID[0]));
    return MFD_SUCCESS;
}

int dot3adAggPortActorAdminKey_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggPortActorAdminKey_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortActorAdminKey_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortActorAdminKey_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortActorAdminKey_val_ptr) =
        rowreq_ctx->data.dot3adAggPortActorAdminKey;
    return MFD_SUCCESS;
}

int dot3adAggPortActorOperKey_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                  long *dot3adAggPortActorOperKey_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortActorOperKey_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortActorOperKey_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortActorOperKey_val_ptr) =
        rowreq_ctx->data.dot3adAggPortActorOperKey;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerAdminSystemPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminSystemPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerAdminSystemPriority_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:"
                "dot3adAggPortPartnerAdminSystemPriority_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerAdminSystemPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerAdminSystemPriority;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerOperSystemPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerOperSystemPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerOperSystemPriority_val_ptr);
    DEBUGMSGTL((
        "verbose:dot3adAggPortTable:dot3adAggPortPartnerOperSystemPriority_get",
        "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerOperSystemPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerOperSystemPriority;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerAdminSystemID_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPortPartnerAdminSystemID_val_ptr_ptr,
    size_t *dot3adAggPortPartnerAdminSystemID_val_ptr_len_ptr) {
    netsnmp_assert((NULL != dot3adAggPortPartnerAdminSystemID_val_ptr_ptr) &&
                   (NULL != *dot3adAggPortPartnerAdminSystemID_val_ptr_ptr));
    netsnmp_assert(NULL != dot3adAggPortPartnerAdminSystemID_val_ptr_len_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortPartnerAdminSystemID_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    if ((NULL == (*dot3adAggPortPartnerAdminSystemID_val_ptr_ptr)) ||
        ((*dot3adAggPortPartnerAdminSystemID_val_ptr_len_ptr) <
         (rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID_len *
          sizeof(rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID[0])))) {
        (*dot3adAggPortPartnerAdminSystemID_val_ptr_ptr) = malloc(
            rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID_len *
            sizeof(rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID[0]));
        if (NULL == (*dot3adAggPortPartnerAdminSystemID_val_ptr_ptr)) {
            snmp_log(LOG_ERR, "could not allocate memory "
                              "(rowreq_ctx->data."
                              "dot3adAggPortPartnerAdminSystemID)\n");
            return MFD_ERROR;
        }
    }
    (*dot3adAggPortPartnerAdminSystemID_val_ptr_len_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID_len *
        sizeof(rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID[0]);
    memcpy((*dot3adAggPortPartnerAdminSystemID_val_ptr_ptr),
           rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID,
           rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID_len *
               sizeof(rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID[0]));
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerOperSystemID_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPortPartnerOperSystemID_val_ptr_ptr,
    size_t *dot3adAggPortPartnerOperSystemID_val_ptr_len_ptr) {
    netsnmp_assert((NULL != dot3adAggPortPartnerOperSystemID_val_ptr_ptr) &&
                   (NULL != *dot3adAggPortPartnerOperSystemID_val_ptr_ptr));
    netsnmp_assert(NULL != dot3adAggPortPartnerOperSystemID_val_ptr_len_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortPartnerOperSystemID_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    if ((NULL == (*dot3adAggPortPartnerOperSystemID_val_ptr_ptr)) ||
        ((*dot3adAggPortPartnerOperSystemID_val_ptr_len_ptr) <
         (rowreq_ctx->data.dot3adAggPortPartnerOperSystemID_len *
          sizeof(rowreq_ctx->data.dot3adAggPortPartnerOperSystemID[0])))) {
        (*dot3adAggPortPartnerOperSystemID_val_ptr_ptr) = malloc(
            rowreq_ctx->data.dot3adAggPortPartnerOperSystemID_len *
            sizeof(rowreq_ctx->data.dot3adAggPortPartnerOperSystemID[0]));
        if (NULL == (*dot3adAggPortPartnerOperSystemID_val_ptr_ptr)) {
            snmp_log(LOG_ERR, "could not allocate memory "
                              "(rowreq_ctx->data."
                              "dot3adAggPortPartnerOperSystemID)\n");
            return MFD_ERROR;
        }
    }
    (*dot3adAggPortPartnerOperSystemID_val_ptr_len_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerOperSystemID_len *
        sizeof(rowreq_ctx->data.dot3adAggPortPartnerOperSystemID[0]);
    memcpy((*dot3adAggPortPartnerOperSystemID_val_ptr_ptr),
           rowreq_ctx->data.dot3adAggPortPartnerOperSystemID,
           rowreq_ctx->data.dot3adAggPortPartnerOperSystemID_len *
               sizeof(rowreq_ctx->data.dot3adAggPortPartnerOperSystemID[0]));
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerAdminKey_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminKey_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerAdminKey_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortPartnerAdminKey_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerAdminKey_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerAdminKey;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerOperKey_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                    long *dot3adAggPortPartnerOperKey_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerOperKey_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortPartnerOperKey_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerOperKey_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerOperKey;
    return MFD_SUCCESS;
}

int dot3adAggPortSelectedAggID_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggPortSelectedAggID_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortSelectedAggID_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortSelectedAggID_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortSelectedAggID_val_ptr) =
        rowreq_ctx->data.dot3adAggPortSelectedAggID;
    return MFD_SUCCESS;
}

int dot3adAggPortAttachedAggID_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggPortAttachedAggID_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortAttachedAggID_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortAttachedAggID_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortAttachedAggID_val_ptr) =
        rowreq_ctx->data.dot3adAggPortAttachedAggID;
    return MFD_SUCCESS;
}

int dot3adAggPortActorPort_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                               long *dot3adAggPortActorPort_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortActorPort_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortActorPort_get", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortActorPort_val_ptr) = rowreq_ctx->data.dot3adAggPortActorPort;
    return MFD_SUCCESS;
}

int dot3adAggPortActorPortPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortActorPortPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortActorPortPriority_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortActorPortPriority_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortActorPortPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggPortActorPortPriority;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerAdminPort_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminPort_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerAdminPort_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortPartnerAdminPort_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerAdminPort_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerAdminPort;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerOperPort_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerOperPort_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerOperPort_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortPartnerOperPort_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerOperPort_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerOperPort;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerAdminPortPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminPortPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerAdminPortPriority_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortPartnerAdminPortPriority_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerAdminPortPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerAdminPortPriority;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerOperPortPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerOperPortPriority_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerOperPortPriority_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortPartnerOperPortPriority_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerOperPortPriority_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerOperPortPriority;
    return MFD_SUCCESS;
}

int dot3adAggPortActorAdminState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortActorAdminState_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortActorAdminState_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortActorAdminState_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortActorAdminState_val_ptr) =
        rowreq_ctx->data.dot3adAggPortActorAdminState;
    return MFD_SUCCESS;
}

int dot3adAggPortActorOperState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortActorOperState_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortActorOperState_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortActorOperState_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortActorOperState_val_ptr) =
        rowreq_ctx->data.dot3adAggPortActorOperState;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerAdminState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortPartnerAdminState_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerAdminState_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortPartnerAdminState_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerAdminState_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerAdminState;
    return MFD_SUCCESS;
}

int dot3adAggPortPartnerOperState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortPartnerOperState_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortPartnerOperState_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortPartnerOperState_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortPartnerOperState_val_ptr) =
        rowreq_ctx->data.dot3adAggPortPartnerOperState;
    return MFD_SUCCESS;
}

int dot3adAggPortAggregateOrIndividual_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortAggregateOrIndividual_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortAggregateOrIndividual_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortAggregateOrIndividual_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortAggregateOrIndividual_val_ptr) =
        rowreq_ctx->data.dot3adAggPortAggregateOrIndividual;
    return MFD_SUCCESS;
}
