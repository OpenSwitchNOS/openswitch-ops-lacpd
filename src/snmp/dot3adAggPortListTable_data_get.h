#ifndef DOT3ADAGGPORTLISTTABLE_DATA_GET_H
#define DOT3ADAGGPORTLISTTABLE_DATA_GET_H
int dot3adAggPortListPorts_get(dot3adAggPortListTable_rowreq_ctx *rowreq_ctx,
                               char **dot3adAggPortListPorts_val_ptr_ptr,
                               size_t *dot3adAggPortListPorts_val_ptr_len_ptr);

int dot3adAggPortListTable_indexes_set_tbl_idx(
    dot3adAggPortListTable_mib_index *tbl_idx, long dot3adAggIndex_val);

int dot3adAggPortListTable_indexes_set(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx, long dot3adAggIndex_val);
#endif
