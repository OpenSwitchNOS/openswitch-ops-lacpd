#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggPortStatsTable.h"
#include "dot3adAggPortStatsTable_data_access.h"
#include "dot3adAggPortStatsTable_ovsdb_get.h"

#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"

int dot3adAggPortStatsTable_init_data(
    dot3adAggPortStatsTable_registration *dot3adAggPortStatsTable_reg) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_init_data",
         "called\n"));
    return MFD_SUCCESS;
}

void dot3adAggPortStatsTable_container_init(
    netsnmp_container **container_ptr_ptr, netsnmp_cache *cache) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "container_init",
                "called\n"));
    if (NULL == container_ptr_ptr) {
        snmp_log(
            LOG_ERR,
            "bad container param to dot3adAggPortStatsTable_container_init\n");
        return;
    }
    *container_ptr_ptr = NULL;
    if (NULL == cache) {
        snmp_log(LOG_ERR,
                 "bad cache param to dot3adAggPortStatsTable_container_init\n");
        return;
    }
    cache->timeout = DOT3ADAGGPORTSTATSTABLE_CACHE_TIMEOUT;
}

void dot3adAggPortStatsTable_container_shutdown(
    netsnmp_container *container_ptr) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "container_shutdown",
                "called\n"));
    if (NULL == container_ptr) {
        snmp_log(LOG_ERR,
                 "bad params to dot3adAggPortStatsTable_container_shutdown\n");
        return;
    }
}

int dot3adAggPortStatsTable_container_load(netsnmp_container *container) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "container_load",
                "called\n"));
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx;
    size_t count = 0;

    const struct ovsrec_port *port_row = NULL;

    long dot3adAggPortIndex;

    u_long dot3adAggPortStatsLACPDUsRx;
    u_long dot3adAggPortStatsMarkerPDUsRx;
    u_long dot3adAggPortStatsMarkerResponsePDUsRx;
    u_long dot3adAggPortStatsUnknownRx;
    u_long dot3adAggPortStatsIllegalRx;
    u_long dot3adAggPortStatsLACPDUsTx;
    u_long dot3adAggPortStatsMarkerPDUsTx;
    u_long dot3adAggPortStatsMarkerResponsePDUsTx;

    port_row = ovsrec_port_first(idl);
    if (!port_row) {
        snmp_log(LOG_ERR, "not able to fetch port row");
        return -1;
    }

    OVSREC_PORT_FOR_EACH(port_row, idl) {
        if (dot3adAggPortStats_skip_function(idl, port_row)) {
            continue;
        }
        ovsdb_get_dot3adAggPortStatsIndex(idl, port_row, &dot3adAggPortIndex);

        ovsdb_get_dot3adAggPortStatsLACPDUsRx(idl, port_row,
                                              &dot3adAggPortStatsLACPDUsRx);
        ovsdb_get_dot3adAggPortStatsMarkerPDUsRx(
            idl, port_row, &dot3adAggPortStatsMarkerPDUsRx);
        ovsdb_get_dot3adAggPortStatsMarkerResponsePDUsRx(
            idl, port_row, &dot3adAggPortStatsMarkerResponsePDUsRx);
        ovsdb_get_dot3adAggPortStatsUnknownRx(idl, port_row,
                                              &dot3adAggPortStatsUnknownRx);
        ovsdb_get_dot3adAggPortStatsIllegalRx(idl, port_row,
                                              &dot3adAggPortStatsIllegalRx);
        ovsdb_get_dot3adAggPortStatsLACPDUsTx(idl, port_row,
                                              &dot3adAggPortStatsLACPDUsTx);
        ovsdb_get_dot3adAggPortStatsMarkerPDUsTx(
            idl, port_row, &dot3adAggPortStatsMarkerPDUsTx);
        ovsdb_get_dot3adAggPortStatsMarkerResponsePDUsTx(
            idl, port_row, &dot3adAggPortStatsMarkerResponsePDUsTx);

        rowreq_ctx = dot3adAggPortStatsTable_allocate_rowreq_ctx(NULL);
        if (rowreq_ctx == NULL) {
            snmp_log(LOG_ERR, "memory allocation failed");
            return MFD_RESOURCE_UNAVAILABLE;
        }
        if (MFD_SUCCESS != dot3adAggPortStatsTable_indexes_set(
                               rowreq_ctx, dot3adAggPortIndex)) {
            snmp_log(LOG_ERR, "error setting indexes while loading");
            dot3adAggPortStatsTable_release_rowreq_ctx(rowreq_ctx);
            continue;
        }

        rowreq_ctx->data.dot3adAggPortStatsLACPDUsRx =
            dot3adAggPortStatsLACPDUsRx;
        rowreq_ctx->data.dot3adAggPortStatsMarkerPDUsRx =
            dot3adAggPortStatsMarkerPDUsRx;
        rowreq_ctx->data.dot3adAggPortStatsMarkerResponsePDUsRx =
            dot3adAggPortStatsMarkerResponsePDUsRx;
        rowreq_ctx->data.dot3adAggPortStatsUnknownRx =
            dot3adAggPortStatsUnknownRx;
        rowreq_ctx->data.dot3adAggPortStatsIllegalRx =
            dot3adAggPortStatsIllegalRx;
        rowreq_ctx->data.dot3adAggPortStatsLACPDUsTx =
            dot3adAggPortStatsLACPDUsTx;
        rowreq_ctx->data.dot3adAggPortStatsMarkerPDUsTx =
            dot3adAggPortStatsMarkerPDUsTx;
        rowreq_ctx->data.dot3adAggPortStatsMarkerResponsePDUsTx =
            dot3adAggPortStatsMarkerResponsePDUsTx;
        CONTAINER_INSERT(container, rowreq_ctx);
        ++count;
    }
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "container_load",
                "inserted %d records\n", (int)count));
    return MFD_SUCCESS;
}

void dot3adAggPortStatsTable_container_free(netsnmp_container *container) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "container_free",
                "called\n"));
}

int dot3adAggPortStatsTable_row_prep(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_row_prep",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
    return MFD_SUCCESS;
}
