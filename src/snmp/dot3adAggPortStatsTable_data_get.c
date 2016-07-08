#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "dot3adAggPortStatsTable.h"

int dot3adAggPortStatsTable_indexes_set_tbl_idx(
    dot3adAggPortStatsTable_mib_index *tbl_idx, long dot3adAggPortIndex_val) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "indexes_set_tbl_idx",
                "called\n"));

    tbl_idx->dot3adAggPortIndex = dot3adAggPortIndex_val;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsTable_indexes_set(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    long dot3adAggPortIndex_val) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_indexes_set",
         "called\n"));
    if (MFD_SUCCESS != dot3adAggPortStatsTable_indexes_set_tbl_idx(
                           &rowreq_ctx->tbl_idx, dot3adAggPortIndex_val)) {
        return MFD_ERROR;
    }
    rowreq_ctx->oid_idx.len = sizeof(rowreq_ctx->oid_tmp) / sizeof(oid);
    if (0 != dot3adAggPortStatsTable_index_to_oid(&rowreq_ctx->oid_idx,
                                                  &rowreq_ctx->tbl_idx)) {
        return MFD_ERROR;
    }
    return MFD_SUCCESS;
}

int dot3adAggPortStatsLACPDUsRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsLACPDUsRx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsLACPDUsRx_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsLACPDUsRx_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsLACPDUsRx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsLACPDUsRx;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsMarkerPDUsRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerPDUsRx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsMarkerPDUsRx_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsMarkerPDUsRx_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsMarkerPDUsRx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsMarkerPDUsRx;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsMarkerResponsePDUsRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerResponsePDUsRx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsMarkerResponsePDUsRx_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:"
                "dot3adAggPortStatsMarkerResponsePDUsRx_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsMarkerResponsePDUsRx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsMarkerResponsePDUsRx;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsUnknownRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsUnknownRx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsUnknownRx_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsUnknownRx_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsUnknownRx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsUnknownRx;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsIllegalRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsIllegalRx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsIllegalRx_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsIllegalRx_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsIllegalRx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsIllegalRx;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsLACPDUsTx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsLACPDUsTx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsLACPDUsTx_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsLACPDUsTx_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsLACPDUsTx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsLACPDUsTx;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsMarkerPDUsTx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerPDUsTx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsMarkerPDUsTx_val_ptr);
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsMarkerPDUsTx_get",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsMarkerPDUsTx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsMarkerPDUsTx;
    return MFD_SUCCESS;
}

int dot3adAggPortStatsMarkerResponsePDUsTx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerResponsePDUsTx_val_ptr) {
    netsnmp_assert(NULL != dot3adAggPortStatsMarkerResponsePDUsTx_val_ptr);
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:"
                "dot3adAggPortStatsMarkerResponsePDUsTx_get",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);

    (*dot3adAggPortStatsMarkerResponsePDUsTx_val_ptr) =
        rowreq_ctx->data.dot3adAggPortStatsMarkerResponsePDUsTx;
    return MFD_SUCCESS;
}
