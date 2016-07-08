#ifndef DOT3ADAGGPORTSTATSTABLE_DATA_GET_H
#define DOT3ADAGGPORTSTATSTABLE_DATA_GET_H
int dot3adAggPortStatsLACPDUsRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsLACPDUsRx_val_ptr);

int dot3adAggPortStatsMarkerPDUsRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerPDUsRx_val_ptr);

int dot3adAggPortStatsMarkerResponsePDUsRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerResponsePDUsRx_val_ptr);

int dot3adAggPortStatsUnknownRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsUnknownRx_val_ptr);

int dot3adAggPortStatsIllegalRx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsIllegalRx_val_ptr);

int dot3adAggPortStatsLACPDUsTx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsLACPDUsTx_val_ptr);

int dot3adAggPortStatsMarkerPDUsTx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerPDUsTx_val_ptr);

int dot3adAggPortStatsMarkerResponsePDUsTx_get(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortStatsMarkerResponsePDUsTx_val_ptr);

int dot3adAggPortStatsTable_indexes_set_tbl_idx(
    dot3adAggPortStatsTable_mib_index *tbl_idx, long dot3adAggPortIndex_val);

int dot3adAggPortStatsTable_indexes_set(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
    long dot3adAggPortIndex_val);
#endif
