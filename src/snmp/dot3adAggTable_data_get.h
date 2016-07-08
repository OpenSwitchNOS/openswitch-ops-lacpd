#ifndef DOT3ADAGGTABLE_DATA_GET_H
#define DOT3ADAGGTABLE_DATA_GET_H
int dot3adAggMACAddress_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                            char **dot3adAggMACAddress_val_ptr_ptr,
                            size_t *dot3adAggMACAddress_val_ptr_len_ptr);

int dot3adAggActorSystemPriority_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggActorSystemPriority_val_ptr);

int dot3adAggActorSystemID_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                               char **dot3adAggActorSystemID_val_ptr_ptr,
                               size_t *dot3adAggActorSystemID_val_ptr_len_ptr);

int dot3adAggAggregateOrIndividual_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggAggregateOrIndividual_val_ptr);

int dot3adAggActorAdminKey_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                               long *dot3adAggActorAdminKey_val_ptr);

int dot3adAggActorOperKey_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                              long *dot3adAggActorOperKey_val_ptr);

int dot3adAggPartnerSystemID_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPartnerSystemID_val_ptr_ptr,
    size_t *dot3adAggPartnerSystemID_val_ptr_len_ptr);

int dot3adAggPartnerSystemPriority_get(
    dot3adAggTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPartnerSystemPriority_val_ptr);

int dot3adAggPartnerOperKey_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                                long *dot3adAggPartnerOperKey_val_ptr);

int dot3adAggCollectorMaxDelay_get(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggCollectorMaxDelay_val_ptr);

int dot3adAggTable_indexes_set_tbl_idx(dot3adAggTable_mib_index *tbl_idx,
                                       long dot3adAggIndex_val);

int dot3adAggTable_indexes_set(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                               long dot3adAggIndex_val);
#endif
