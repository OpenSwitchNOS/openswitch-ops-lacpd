#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "dot3adAggPortListTable.h"

int dot3adAggPortListTable_indexes_set_tbl_idx(
    dot3adAggPortListTable_mib_index *tbl_idx, long dot3adAggIndex_val) {
    DEBUGMSGTL(("verbose:dot3adAggPortListTable:dot3adAggPortListTable_indexes_"
                "set_tbl_idx",
                "called\n"));

    tbl_idx->dot3adAggIndex = dot3adAggIndex_val;
    return MFD_SUCCESS;
}

int dot3adAggPortListTable_indexes_set(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx, long dot3adAggIndex_val) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_indexes_set",
         "called\n"));
    if (MFD_SUCCESS != dot3adAggPortListTable_indexes_set_tbl_idx(
                           &rowreq_ctx->tbl_idx, dot3adAggIndex_val)) {
        return MFD_ERROR;
    }

    rowreq_ctx->oid_idx.len = sizeof(rowreq_ctx->oid_tmp) / sizeof(oid);
    if (0 != dot3adAggPortListTable_index_to_oid(&rowreq_ctx->oid_idx,
                                                 &rowreq_ctx->tbl_idx)) {
        return MFD_ERROR;
    }
    return MFD_SUCCESS;
}

int dot3adAggPortListPorts_get(dot3adAggPortListTable_rowreq_ctx *rowreq_ctx,
                               char **dot3adAggPortListPorts_val_ptr_ptr,
                               size_t *dot3adAggPortListPorts_val_ptr_len_ptr) {
    netsnmp_assert((NULL != dot3adAggPortListPorts_val_ptr_ptr) &&
                   (NULL != *dot3adAggPortListPorts_val_ptr_ptr));
    netsnmp_assert(NULL != dot3adAggPortListPorts_val_ptr_len_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortListTable:dot3adAggPortListPorts_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    if ((NULL == (*dot3adAggPortListPorts_val_ptr_ptr)) ||
        ((*dot3adAggPortListPorts_val_ptr_len_ptr) <
         (rowreq_ctx->data.dot3adAggPortListPorts_len *
          sizeof(rowreq_ctx->data.dot3adAggPortListPorts[0])))) {
        (*dot3adAggPortListPorts_val_ptr_ptr) =
            malloc(rowreq_ctx->data.dot3adAggPortListPorts_len *
                   sizeof(rowreq_ctx->data.dot3adAggPortListPorts[0]));
        if (NULL == (*dot3adAggPortListPorts_val_ptr_ptr)) {
            snmp_log(LOG_ERR, "could not allocate memory "
                              "(rowreq_ctx->data.dot3adAggPortListPorts)\n");
            return MFD_ERROR;
        }
    }
    (*dot3adAggPortListPorts_val_ptr_len_ptr) =
        rowreq_ctx->data.dot3adAggPortListPorts_len *
        sizeof(rowreq_ctx->data.dot3adAggPortListPorts[0]);
    memcpy((*dot3adAggPortListPorts_val_ptr_ptr),
           rowreq_ctx->data.dot3adAggPortListPorts,
           rowreq_ctx->data.dot3adAggPortListPorts_len *
               sizeof(rowreq_ctx->data.dot3adAggPortListPorts[0]));
    return MFD_SUCCESS;
}
