#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include <net-snmp/agent/table_container.h>
#include <net-snmp/library/container.h>
#include "dot3adAggPortStatsTable.h"
#include "dot3adAggPortStatsTable_interface.h"

netsnmp_feature_require(baby_steps) netsnmp_feature_require(row_merge)
    netsnmp_feature_require(check_all_requests_error)

        typedef struct dot3adAggPortStatsTable_interface_ctx_s {
    netsnmp_container *container;
    netsnmp_cache *cache;
    dot3adAggPortStatsTable_registration *user_ctx;
    netsnmp_table_registration_info tbl_info;
    netsnmp_baby_steps_access_methods access_multiplexer;
} dot3adAggPortStatsTable_interface_ctx;

static dot3adAggPortStatsTable_interface_ctx dot3adAggPortStatsTable_if_ctx;
static void _dot3adAggPortStatsTable_container_init(
    dot3adAggPortStatsTable_interface_ctx *if_ctx);
static void _dot3adAggPortStatsTable_container_shutdown(
    dot3adAggPortStatsTable_interface_ctx *if_ctx);

netsnmp_container *dot3adAggPortStatsTable_container_get(void) {
    return dot3adAggPortStatsTable_if_ctx.container;
}

dot3adAggPortStatsTable_registration *
dot3adAggPortStatsTable_registration_get(void) {
    return dot3adAggPortStatsTable_if_ctx.user_ctx;
}

dot3adAggPortStatsTable_registration *dot3adAggPortStatsTable_registration_set(
    dot3adAggPortStatsTable_registration *newreg) {
    dot3adAggPortStatsTable_registration *old =
        dot3adAggPortStatsTable_if_ctx.user_ctx;
    dot3adAggPortStatsTable_if_ctx.user_ctx = newreg;
    return old;
}

int dot3adAggPortStatsTable_container_size(void) {
    return CONTAINER_SIZE(dot3adAggPortStatsTable_if_ctx.container);
}

static Netsnmp_Node_Handler _mfd_dot3adAggPortStatsTable_pre_request;
static Netsnmp_Node_Handler _mfd_dot3adAggPortStatsTable_post_request;
static Netsnmp_Node_Handler _mfd_dot3adAggPortStatsTable_object_lookup;
static Netsnmp_Node_Handler _mfd_dot3adAggPortStatsTable_get_values;

void _dot3adAggPortStatsTable_initialize_interface(
    dot3adAggPortStatsTable_registration *reg_ptr, u_long flags) {
    netsnmp_baby_steps_access_methods *access_multiplexer =
        &dot3adAggPortStatsTable_if_ctx.access_multiplexer;
    netsnmp_table_registration_info *tbl_info =
        &dot3adAggPortStatsTable_if_ctx.tbl_info;
    netsnmp_handler_registration *reginfo;
    netsnmp_mib_handler *handler;
    int mfd_modes = 0;

    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_dot3adAggPortStatsTable_"
                "initialize_interface",
                "called\n"));

    netsnmp_table_helper_add_indexes(tbl_info, ASN_INTEGER, 0);

    tbl_info->min_column = DOT3ADAGGPORTSTATSTABLE_MIN_COL;
    tbl_info->max_column = DOT3ADAGGPORTSTATSTABLE_MAX_COL;
    dot3adAggPortStatsTable_if_ctx.user_ctx = reg_ptr;
    dot3adAggPortStatsTable_init_data(reg_ptr);
    _dot3adAggPortStatsTable_container_init(&dot3adAggPortStatsTable_if_ctx);
    if (NULL == dot3adAggPortStatsTable_if_ctx.container) {
        snmp_log(
            LOG_ERR,
            "could not initialize container for dot3adAggPortStatsTable\n");
        return;
    }

    access_multiplexer->object_lookup =
        _mfd_dot3adAggPortStatsTable_object_lookup;
    access_multiplexer->get_values = _mfd_dot3adAggPortStatsTable_get_values;

    access_multiplexer->pre_request = _mfd_dot3adAggPortStatsTable_pre_request;
    access_multiplexer->post_request =
        _mfd_dot3adAggPortStatsTable_post_request;

    DEBUGMSGTL(
        ("dot3adAggPortStatsTable:init_dot3adAggPortStatsTable",
         "Registering dot3adAggPortStatsTable as a mibs-for-dummies table.\n"));

    handler = netsnmp_baby_steps_access_multiplexer_get(access_multiplexer);
    reginfo = netsnmp_handler_registration_create(
        "dot3adAggPortStatsTable", handler, dot3adAggPortStatsTable_oid,
        dot3adAggPortStatsTable_oid_size,
        HANDLER_CAN_BABY_STEP | HANDLER_CAN_RONLY);

    if (NULL == reginfo) {
        snmp_log(LOG_ERR, "error registering table dot3adAggPortStatsTable\n");
        return;
    }

    reginfo->my_reg_void = &dot3adAggPortStatsTable_if_ctx;

    if (access_multiplexer->object_lookup)
        mfd_modes |= BABY_STEP_OBJECT_LOOKUP;
    if (access_multiplexer->pre_request)
        mfd_modes |= BABY_STEP_PRE_REQUEST;
    if (access_multiplexer->post_request)
        mfd_modes |= BABY_STEP_POST_REQUEST;

    handler = netsnmp_baby_steps_handler_get(mfd_modes);
    netsnmp_inject_handler(reginfo, handler);

    handler = netsnmp_get_row_merge_handler(reginfo->rootoid_len + 2);
    netsnmp_inject_handler(reginfo, handler);

    handler = netsnmp_container_table_handler_get(
        tbl_info, dot3adAggPortStatsTable_if_ctx.container,
        TABLE_CONTAINER_KEY_NETSNMP_INDEX);
    netsnmp_inject_handler(reginfo, handler);

    if (NULL != dot3adAggPortStatsTable_if_ctx.cache) {
        handler =
            netsnmp_cache_handler_get(dot3adAggPortStatsTable_if_ctx.cache);
        netsnmp_inject_handler(reginfo, handler);
    }

    netsnmp_register_table(reginfo, tbl_info);
}

void _dot3adAggPortStatsTable_shutdown_interface(
    dot3adAggPortStatsTable_registration *reg_ptr) {
    _dot3adAggPortStatsTable_container_shutdown(
        &dot3adAggPortStatsTable_if_ctx);
}

void dot3adAggPortStatsTable_valid_columns_set(netsnmp_column_info *vc) {
    dot3adAggPortStatsTable_if_ctx.tbl_info.valid_columns = vc;
}

int dot3adAggPortStatsTable_index_to_oid(
    netsnmp_index *oid_idx, dot3adAggPortStatsTable_mib_index *mib_idx) {
    int err = SNMP_ERR_NOERROR;
    netsnmp_variable_list var_dot3adAggPortIndex;

    memset(&var_dot3adAggPortIndex, 0x00, sizeof(var_dot3adAggPortIndex));
    var_dot3adAggPortIndex.type = ASN_INTEGER;
    var_dot3adAggPortIndex.next_variable = NULL;

    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_index_to_oid",
         "called\n"));

    snmp_set_var_value(&var_dot3adAggPortIndex, &mib_idx->dot3adAggPortIndex,
                       sizeof(mib_idx->dot3adAggPortIndex));
    err = build_oid_noalloc(oid_idx->oids, oid_idx->len, &oid_idx->len, NULL, 0,
                            &var_dot3adAggPortIndex);
    if (err) {
        snmp_log(LOG_ERR, "error %d converting index to oid\n", err);
    }

    snmp_reset_var_buffers(&var_dot3adAggPortIndex);
    return err;
}

int dot3adAggPortStatsTable_index_from_oid(
    netsnmp_index *oid_idx, dot3adAggPortStatsTable_mib_index *mib_idx) {
    int err = SNMP_ERR_NOERROR;
    netsnmp_variable_list var_dot3adAggPortIndex;

    memset(&var_dot3adAggPortIndex, 0x00, sizeof(var_dot3adAggPortIndex));
    var_dot3adAggPortIndex.type = ASN_INTEGER;
    var_dot3adAggPortIndex.next_variable = NULL;

    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_index_"
                "from_oid",
                "called\n"));

    err =
        parse_oid_indexes(oid_idx->oids, oid_idx->len, &var_dot3adAggPortIndex);
    if (err == SNMP_ERR_NOERROR) {
        mib_idx->dot3adAggPortIndex =
            *((long *)var_dot3adAggPortIndex.val.string);
    }

    snmp_reset_var_buffers(&var_dot3adAggPortIndex);
    return err;
}

dot3adAggPortStatsTable_rowreq_ctx *
dot3adAggPortStatsTable_allocate_rowreq_ctx(void *user_init_ctx) {
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx =
        SNMP_MALLOC_TYPEDEF(dot3adAggPortStatsTable_rowreq_ctx);

    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "allocate_rowreq_ctx",
                "called\n"));

    if (NULL == rowreq_ctx) {
        snmp_log(LOG_ERR, "Could not allocate memory for a "
                          "dot3adAggPortStatsTable_rowreq_ctx.\n");
        return NULL;
    }

    rowreq_ctx->oid_idx.oids = rowreq_ctx->oid_tmp;
    rowreq_ctx->dot3adAggPortStatsTable_data_list = NULL;
    if (!(rowreq_ctx->rowreq_flags & MFD_ROW_DATA_FROM_USER)) {
        if (SNMPERR_SUCCESS != dot3adAggPortStatsTable_rowreq_ctx_init(
                                   rowreq_ctx, user_init_ctx)) {
            dot3adAggPortStatsTable_release_rowreq_ctx(rowreq_ctx);
            rowreq_ctx = NULL;
        }
    }
    return rowreq_ctx;
}

void dot3adAggPortStatsTable_release_rowreq_ctx(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "release_rowreq_ctx",
                "called\n"));

    netsnmp_assert(NULL != rowreq_ctx);

    dot3adAggPortStatsTable_rowreq_ctx_cleanup(rowreq_ctx);
    if (rowreq_ctx->oid_idx.oids != rowreq_ctx->oid_tmp) {
        free(rowreq_ctx->oid_idx.oids);
    }

    SNMP_FREE(rowreq_ctx);
}

static int _mfd_dot3adAggPortStatsTable_pre_request(
    netsnmp_mib_handler *handler, netsnmp_handler_registration *reginfo,
    netsnmp_agent_request_info *agtreq_info, netsnmp_request_info *requests) {
    int rc;
    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_mfd_dot3adAggPortStatsTable_"
                "pre_request",
                "called\n"));

    if (1 != netsnmp_row_merge_status_first(reginfo, agtreq_info)) {
        DEBUGMSGTL(("internal:dot3adAggPortStatsTable",
                    "skipping additional pre_request\n"));
        return SNMP_ERR_NOERROR;
    }

    rc = dot3adAggPortStatsTable_pre_request(
        dot3adAggPortStatsTable_if_ctx.user_ctx);
    if (MFD_SUCCESS != rc) {
        DEBUGMSGTL(("dot3adAggPortStatsTable",
                    "error %d from dot3adAggPortStatsTable_pre_requests\n",
                    rc));
        netsnmp_request_set_error_all(requests, SNMP_VALIDATE_ERR(rc));
    }

    return SNMP_ERR_NOERROR;
}

static int _mfd_dot3adAggPortStatsTable_post_request(
    netsnmp_mib_handler *handler, netsnmp_handler_registration *reginfo,
    netsnmp_agent_request_info *agtreq_info, netsnmp_request_info *requests) {
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx =
        (dot3adAggPortStatsTable_rowreq_ctx *)
            netsnmp_container_table_row_extract(requests);
    int rc, packet_rc;
    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_mfd_dot3adAggPortStatsTable_"
                "post_request",
                "called\n"));

    if (rowreq_ctx && (rowreq_ctx->rowreq_flags & MFD_ROW_DELETED)) {
        dot3adAggPortStatsTable_release_rowreq_ctx(rowreq_ctx);
    }

    if (1 != netsnmp_row_merge_status_last(reginfo, agtreq_info)) {
        DEBUGMSGTL(("internal:dot3adAggPortStatsTable",
                    "waiting for last post_request\n"));
        return SNMP_ERR_NOERROR;
    }

    packet_rc = netsnmp_check_all_requests_error(agtreq_info->asp, 0);
    rc = dot3adAggPortStatsTable_post_request(
        dot3adAggPortStatsTable_if_ctx.user_ctx, packet_rc);
    if (MFD_SUCCESS != rc) {
        DEBUGMSGTL(("dot3adAggPortStatsTable",
                    "error %d from dot3adAggPortStatsTable_post_request\n",
                    rc));
    }
    return SNMP_ERR_NOERROR;
}

static int _mfd_dot3adAggPortStatsTable_object_lookup(
    netsnmp_mib_handler *handler, netsnmp_handler_registration *reginfo,
    netsnmp_agent_request_info *agtreq_info, netsnmp_request_info *requests) {
    int rc = SNMP_ERR_NOERROR;
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx =
        (dot3adAggPortStatsTable_rowreq_ctx *)
            netsnmp_container_table_row_extract(requests);

    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_mfd_dot3adAggPortStatsTable_"
                "object_lookup",
                "called\n"));

    if (NULL == rowreq_ctx) {
        rc = SNMP_ERR_NOCREATION;
    }

    if (MFD_SUCCESS != rc) {
        netsnmp_request_set_error_all(requests, rc);
    } else {
        dot3adAggPortStatsTable_row_prep(rowreq_ctx);
    }

    return SNMP_VALIDATE_ERR(rc);
}

NETSNMP_STATIC_INLINE int _dot3adAggPortStatsTable_get_column(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx, netsnmp_variable_list *var,
    int column) {
    int rc = SNMPERR_SUCCESS;

    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_mfd_dot3adAggPortStatsTable_"
                "get_column",
                "called for %d\n", column));

    netsnmp_assert(NULL != rowreq_ctx);

    switch (column) {
    case COLUMN_DOT3ADAGGPORTSTATSLACPDUSRX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsLACPDUsRx_get(rowreq_ctx,
                                             (u_long *)var->val.string);
    } break;
    case COLUMN_DOT3ADAGGPORTSTATSMARKERPDUSRX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsMarkerPDUsRx_get(rowreq_ctx,
                                                (u_long *)var->val.string);
    } break;
    case COLUMN_DOT3ADAGGPORTSTATSMARKERRESPONSEPDUSRX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsMarkerResponsePDUsRx_get(
            rowreq_ctx, (u_long *)var->val.string);
    } break;
    case COLUMN_DOT3ADAGGPORTSTATSUNKNOWNRX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsUnknownRx_get(rowreq_ctx,
                                             (u_long *)var->val.string);
    } break;
    case COLUMN_DOT3ADAGGPORTSTATSILLEGALRX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsIllegalRx_get(rowreq_ctx,
                                             (u_long *)var->val.string);
    } break;
    case COLUMN_DOT3ADAGGPORTSTATSLACPDUSTX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsLACPDUsTx_get(rowreq_ctx,
                                             (u_long *)var->val.string);
    } break;
    case COLUMN_DOT3ADAGGPORTSTATSMARKERPDUSTX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsMarkerPDUsTx_get(rowreq_ctx,
                                                (u_long *)var->val.string);
    } break;
    case COLUMN_DOT3ADAGGPORTSTATSMARKERRESPONSEPDUSTX: {
        var->type = ASN_COUNTER;
        var->val_len = sizeof(u_long);
        rc = dot3adAggPortStatsMarkerResponsePDUsTx_get(
            rowreq_ctx, (u_long *)var->val.string);
    } break;
    default:
        if (DOT3ADAGGPORTSTATSTABLE_MIN_COL <= column &&
            column <= DOT3ADAGGPORTSTATSTABLE_MAX_COL) {
            DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_mfd_"
                        "dot3adAggPortStatsTable_get_column",
                        "assume column %d is reserved\n", column));
            rc = MFD_SKIP;
        } else {
            snmp_log(
                LOG_ERR,
                "unknown column %d in _dot3adAggPortStatsTable_get_column\n",
                column);
        }
        break;
    }

    return rc;
}

int _mfd_dot3adAggPortStatsTable_get_values(
    netsnmp_mib_handler *handler, netsnmp_handler_registration *reginfo,
    netsnmp_agent_request_info *agtreq_info, netsnmp_request_info *requests) {
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx =
        (dot3adAggPortStatsTable_rowreq_ctx *)
            netsnmp_container_table_row_extract(requests);
    netsnmp_table_request_info *tri;
    u_char *old_string;
    void (*dataFreeHook)(void *);
    int rc;

    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_mfd_dot3adAggPortStatsTable_"
                "get_values",
                "called\n"));

    netsnmp_assert(NULL != rowreq_ctx);

    for (; requests; requests = requests->next) {
        old_string = requests->requestvb->val.string;
        dataFreeHook = requests->requestvb->dataFreeHook;
        if (NULL == requests->requestvb->val.string) {
            requests->requestvb->val.string = requests->requestvb->buf;
            requests->requestvb->val_len = sizeof(requests->requestvb->buf);
        } else if (requests->requestvb->buf ==
                   requests->requestvb->val.string) {
            if (requests->requestvb->val_len !=
                sizeof(requests->requestvb->buf)) {
                requests->requestvb->val_len = sizeof(requests->requestvb->buf);
            }
        }

        tri = netsnmp_extract_table_info(requests);
        if (NULL == tri) {
            continue;
        }
        rc = _dot3adAggPortStatsTable_get_column(
            rowreq_ctx, requests->requestvb, tri->colnum);
        if (rc) {
            if (MFD_SKIP == rc) {
                requests->requestvb->type = SNMP_NOSUCHINSTANCE;
                rc = SNMP_ERR_NOERROR;
            }
        } else if (NULL == requests->requestvb->val.string) {
            snmp_log(LOG_ERR, "NULL varbind data pointer!\n");
            rc = SNMP_ERR_GENERR;
        }
        if (rc) {
            netsnmp_request_set_error(requests, SNMP_VALIDATE_ERR(rc));
        }

        if (old_string && (old_string != requests->requestvb->buf) &&
            (requests->requestvb->val.string != old_string)) {
            if (dataFreeHook) {
                (*dataFreeHook)(old_string);
            } else {
                free(old_string);
            }
        }
    }

    return SNMP_ERR_NOERROR;
}

static void _container_free(netsnmp_container *container);

static int _cache_load(netsnmp_cache *cache, void *vmagic) {
    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_cache_load", "called\n"));

    if ((NULL == cache) || (NULL == cache->magic)) {
        snmp_log(LOG_ERR,
                 "invalid cache for dot3adAggPortStatsTable_cache_load\n");
        return -1;
    }

    netsnmp_assert((0 == cache->valid) || (1 == cache->expired));

    return dot3adAggPortStatsTable_container_load(
        (netsnmp_container *)cache->magic);
}

static void _cache_free(netsnmp_cache *cache, void *magic) {
    netsnmp_container *container;
    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_cache_free", "called\n"));

    if ((NULL == cache) || (NULL == cache->magic)) {
        snmp_log(LOG_ERR,
                 "invalid cache in dot3adAggPortStatsTable_cache_free\n");
        return;
    }

    container = (netsnmp_container *)cache->magic;
    _container_free(container);
}

static void _container_item_free(dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx,
                                 void *context) {
    DEBUGMSGTL(
        ("internal:dot3adAggPortStatsTable:_container_item_free", "called\n"));

    if (NULL == rowreq_ctx) {
        return;
    }
    dot3adAggPortStatsTable_release_rowreq_ctx(rowreq_ctx);
}

static void _container_free(netsnmp_container *container) {
    DEBUGMSGTL(
        ("internal:dot3adAggPortStatsTable:_container_free", "called\n"));

    if (NULL == container) {
        snmp_log(
            LOG_ERR,
            "invalid container in dot3adAggPortStatsTable_container_free\n");
        return;
    }
    dot3adAggPortStatsTable_container_free(container);
    CONTAINER_CLEAR(container,
                    (netsnmp_container_obj_func *)_container_item_free, NULL);
}

void _dot3adAggPortStatsTable_container_init(
    dot3adAggPortStatsTable_interface_ctx *if_ctx) {
    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_dot3adAggPortStatsTable_"
                "container_init",
                "called\n"));

    if_ctx->cache = netsnmp_cache_create(30, _cache_load, _cache_free,
                                         dot3adAggPortStatsTable_oid,
                                         dot3adAggPortStatsTable_oid_size);

    if (NULL == if_ctx->cache) {
        snmp_log(LOG_ERR, "error creating cache for dot3adAggPortStatsTable\n");
        return;
    }

    if_ctx->cache->flags = NETSNMP_CACHE_DONT_INVALIDATE_ON_SET;
    dot3adAggPortStatsTable_container_init(&if_ctx->container, if_ctx->cache);
    if (NULL == if_ctx->container) {
        if_ctx->container =
            netsnmp_container_find("dot3adAggPortStatsTable:table_container");
    }
    if (NULL == if_ctx->container) {
        snmp_log(LOG_ERR, "error creating container in "
                          "dot3adAggPortStatsTable_container_init\n");
        return;
    }

    if (NULL != if_ctx->cache) {
        if_ctx->cache->magic = (void *)if_ctx->container;
    }
}

void _dot3adAggPortStatsTable_container_shutdown(
    dot3adAggPortStatsTable_interface_ctx *if_ctx) {
    DEBUGMSGTL(("internal:dot3adAggPortStatsTable:_dot3adAggPortStatsTable_"
                "container_shutdown",
                "called\n"));

    dot3adAggPortStatsTable_container_shutdown(if_ctx->container);
    _container_free(if_ctx->container);
}

dot3adAggPortStatsTable_rowreq_ctx *
dot3adAggPortStatsTable_row_find_by_mib_index(
    dot3adAggPortStatsTable_mib_index *mib_idx) {
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx;
    oid oid_tmp[MAX_OID_LEN];
    netsnmp_index oid_idx;
    int rc;

    oid_idx.oids = oid_tmp;
    oid_idx.len = sizeof(oid_tmp) / sizeof(oid);

    rc = dot3adAggPortStatsTable_index_to_oid(&oid_idx, mib_idx);
    if (MFD_SUCCESS != rc) {
        return NULL;
    }

    rowreq_ctx = (dot3adAggPortStatsTable_rowreq_ctx *)CONTAINER_FIND(
        dot3adAggPortStatsTable_if_ctx.container, &oid_idx);

    return rowreq_ctx;
}