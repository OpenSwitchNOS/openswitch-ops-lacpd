#ifndef DOT3ADAGGPORTTABLE_DATA_GET_H
#define DOT3ADAGGPORTTABLE_DATA_GET_H
int dot3adAggPortActorSystemPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortActorSystemPriority_val_ptr);

int dot3adAggPortActorSystemID_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPortActorSystemID_val_ptr_ptr,
    size_t *dot3adAggPortActorSystemID_val_ptr_len_ptr);

int dot3adAggPortActorAdminKey_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggPortActorAdminKey_val_ptr);

int dot3adAggPortActorOperKey_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                  long *dot3adAggPortActorOperKey_val_ptr);

int dot3adAggPortPartnerAdminSystemPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminSystemPriority_val_ptr);

int dot3adAggPortPartnerOperSystemPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerOperSystemPriority_val_ptr);

int dot3adAggPortPartnerAdminSystemID_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPortPartnerAdminSystemID_val_ptr_ptr,
    size_t *dot3adAggPortPartnerAdminSystemID_val_ptr_len_ptr);

int dot3adAggPortPartnerOperSystemID_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    char **dot3adAggPortPartnerOperSystemID_val_ptr_ptr,
    size_t *dot3adAggPortPartnerOperSystemID_val_ptr_len_ptr);

int dot3adAggPortPartnerAdminKey_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminKey_val_ptr);

int dot3adAggPortPartnerOperKey_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                    long *dot3adAggPortPartnerOperKey_val_ptr);

int dot3adAggPortSelectedAggID_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggPortSelectedAggID_val_ptr);

int dot3adAggPortAttachedAggID_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long *dot3adAggPortAttachedAggID_val_ptr);

int dot3adAggPortActorPort_get(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                               long *dot3adAggPortActorPort_val_ptr);

int dot3adAggPortActorPortPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortActorPortPriority_val_ptr);

int dot3adAggPortPartnerAdminPort_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminPort_val_ptr);

int dot3adAggPortPartnerOperPort_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerOperPort_val_ptr);

int dot3adAggPortPartnerAdminPortPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerAdminPortPriority_val_ptr);

int dot3adAggPortPartnerOperPortPriority_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortPartnerOperPortPriority_val_ptr);

int dot3adAggPortActorAdminState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortActorAdminState_val_ptr);

int dot3adAggPortActorOperState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortActorOperState_val_ptr);

int dot3adAggPortPartnerAdminState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortPartnerAdminState_val_ptr);

int dot3adAggPortPartnerOperState_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    u_long *dot3adAggPortPartnerOperState_val_ptr);

int dot3adAggPortAggregateOrIndividual_get(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
    long *dot3adAggPortAggregateOrIndividual_val_ptr);

int dot3adAggPortTable_indexes_set_tbl_idx(
    dot3adAggPortTable_mib_index *tbl_idx, long dot3adAggPortIndex_val);

int dot3adAggPortTable_indexes_set(dot3adAggPortTable_rowreq_ctx *rowreq_ctx,
                                   long dot3adAggPortIndex_val);
#endif
