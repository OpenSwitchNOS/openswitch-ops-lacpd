#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggPortListTable.h"
#include "dot3adAggPortListTable_data_access.h"
#include "dot3adAggPortListTable_ovsdb_get.h"

#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"

int dot3adAggPortListTable_init_data(
    dot3adAggPortListTable_registration *dot3adAggPortListTable_reg) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_init_data",
         "called\n"));
    return MFD_SUCCESS;
}

void dot3adAggPortListTable_container_init(
    netsnmp_container **container_ptr_ptr, netsnmp_cache *cache) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_container_init",
         "called\n"));
    if (NULL == container_ptr_ptr) {
        snmp_log(
            LOG_ERR,
            "bad container param to dot3adAggPortListTable_container_init\n");
        return;
    }
    *container_ptr_ptr = NULL;
    if (NULL == cache) {
        snmp_log(LOG_ERR,
                 "bad cache param to dot3adAggPortListTable_container_init\n");
        return;
    }
    cache->timeout = DOT3ADAGGPORTLISTTABLE_CACHE_TIMEOUT;
}

void dot3adAggPortListTable_container_shutdown(
    netsnmp_container *container_ptr) {
    DEBUGMSGTL(("verbose:dot3adAggPortListTable:dot3adAggPortListTable_"
                "container_shutdown",
                "called\n"));
    if (NULL == container_ptr) {
        snmp_log(LOG_ERR,
                 "bad params to dot3adAggPortListTable_container_shutdown\n");
        return;
    }
}

int dot3adAggPortListTable_container_load(netsnmp_container *container) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_container_load",
         "called\n"));
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx;
    size_t count = 0;

    const struct ovsrec_port *port_row = NULL;

    long dot3adAggIndex;

    char dot3adAggPortListPorts[255];
    size_t dot3adAggPortListPorts_len;

    port_row = ovsrec_port_first(idl);
    if (!port_row) {
        snmp_log(LOG_ERR, "not able to fetch port row");
        return -1;
    }

    OVSREC_PORT_FOR_EACH(port_row, idl) {
        if (Dot3adAggPortListEntry_skip_function(idl, port_row)) {
            continue;
        }
        ovsdb_get_dot3adAggIndex(idl, port_row, &dot3adAggIndex);

        ovsdb_get_dot3adAggPortListPorts(idl, port_row, dot3adAggPortListPorts,
                                         &dot3adAggPortListPorts_len);

        rowreq_ctx = dot3adAggPortListTable_allocate_rowreq_ctx(NULL);
        if (rowreq_ctx == NULL) {
            snmp_log(LOG_ERR, "memory allocation failed");
            return MFD_RESOURCE_UNAVAILABLE;
        }
        if (MFD_SUCCESS !=
            dot3adAggPortListTable_indexes_set(rowreq_ctx, dot3adAggIndex)) {
            snmp_log(LOG_ERR, "error setting indexes while loading");
            dot3adAggPortListTable_release_rowreq_ctx(rowreq_ctx);
            continue;
        }

        rowreq_ctx->data.dot3adAggPortListPorts_len =
            dot3adAggPortListPorts_len * sizeof(dot3adAggPortListPorts[0]);
        memcpy(rowreq_ctx->data.dot3adAggPortListPorts, dot3adAggPortListPorts,
               dot3adAggPortListPorts_len * sizeof(dot3adAggPortListPorts[0]));
        CONTAINER_INSERT(container, rowreq_ctx);
        ++count;
    }
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_container_load",
         "inserted %d records\n", (int)count));
    return MFD_SUCCESS;
}

void dot3adAggPortListTable_container_free(netsnmp_container *container) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_container_free",
         "called\n"));
}

int dot3adAggPortListTable_row_prep(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_row_prep",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
    return MFD_SUCCESS;
}
