#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggPortTable.h"
#include "dot3adAggPortTable_data_access.h"
#include "dot3adAggPortTable_ovsdb_get.h"

#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"

int dot3adAggPortTable_init_data(
    dot3adAggPortTable_registration *dot3adAggPortTable_reg) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_init_data",
                "called\n"));
    return MFD_SUCCESS;
}

void dot3adAggPortTable_container_init(netsnmp_container **container_ptr_ptr,
                                       netsnmp_cache *cache) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_container_init",
                "called\n"));
    if (NULL == container_ptr_ptr) {
        snmp_log(LOG_ERR,
                 "bad container param to dot3adAggPortTable_container_init\n");
        return;
    }
    *container_ptr_ptr = NULL;
    if (NULL == cache) {
        snmp_log(LOG_ERR,
                 "bad cache param to dot3adAggPortTable_container_init\n");
        return;
    }
    cache->timeout = DOT3ADAGGPORTTABLE_CACHE_TIMEOUT;
}

void dot3adAggPortTable_container_shutdown(netsnmp_container *container_ptr) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortTable_container_shutdown",
         "called\n"));
    if (NULL == container_ptr) {
        snmp_log(LOG_ERR,
                 "bad params to dot3adAggPortTable_container_shutdown\n");
        return;
    }
}

int dot3adAggPortTable_container_load(netsnmp_container *container) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_container_load",
                "called\n"));
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx;
    size_t count = 0;
    const struct ovsrec_port *port_row = NULL;
    const struct ovsrec_interface *interface_row = NULL;
    long dot3adAggPortIndex;
    long dot3adAggPortActorSystemPriority;
    char dot3adAggPortActorSystemID[255];
    size_t dot3adAggPortActorSystemID_len;
    long dot3adAggPortActorAdminKey;
    long dot3adAggPortActorOperKey;
    long dot3adAggPortPartnerAdminSystemPriority;
    long dot3adAggPortPartnerOperSystemPriority;
    char dot3adAggPortPartnerAdminSystemID[255];
    size_t dot3adAggPortPartnerAdminSystemID_len;
    char dot3adAggPortPartnerOperSystemID[255];
    size_t dot3adAggPortPartnerOperSystemID_len;
    long dot3adAggPortPartnerAdminKey;
    long dot3adAggPortPartnerOperKey;
    long dot3adAggPortSelectedAggID;
    long dot3adAggPortAttachedAggID;
    long dot3adAggPortActorPort;
    long dot3adAggPortActorPortPriority;
    long dot3adAggPortPartnerAdminPort;
    long dot3adAggPortPartnerOperPort;
    long dot3adAggPortPartnerAdminPortPriority;
    long dot3adAggPortPartnerOperPortPriority;
    u_long dot3adAggPortActorAdminState;
    u_long dot3adAggPortActorOperState;
    u_long dot3adAggPortPartnerAdminState;
    u_long dot3adAggPortPartnerOperState;
    long dot3adAggPortAggregateOrIndividual;

    port_row = ovsrec_port_first(idl);
    if (!port_row) {
        snmp_log(LOG_ERR, "not able to fetch port row");
        return -1;
    }

    interface_row = ovsrec_interface_first(idl);
    if (!interface_row) {
        snmp_log(LOG_ERR, "not able to fetch interface row");
        return -1;
    }

    OVSREC_INTERFACE_FOR_EACH(interface_row, idl) {
        if (dot3adAggPortEntry_skip_function(idl, interface_row)) {
            continue;
        }

        ovsdb_get_dot3adAggPortIndex(idl, interface_row, &dot3adAggPortIndex);

        ovsdb_get_dot3adAggPortActorSystemPriority(
            idl, interface_row, &dot3adAggPortActorSystemPriority);
        ovsdb_get_dot3adAggPortActorSystemID(idl, interface_row,
                                             dot3adAggPortActorSystemID,
                                             &dot3adAggPortActorSystemID_len);

        ovsdb_get_dot3adAggPortActorAdminKey(idl, port_row, interface_row,
                                             &dot3adAggPortActorAdminKey);

        ovsdb_get_dot3adAggPortActorOperKey(idl, port_row, interface_row,
                                            &dot3adAggPortActorOperKey);

        ovsdb_get_dot3adAggPortPartnerAdminSystemPriority(
            idl, interface_row, &dot3adAggPortPartnerAdminSystemPriority);

        ovsdb_get_dot3adAggPortPartnerOperSystemPriority(
            idl, interface_row, &dot3adAggPortPartnerOperSystemPriority);

        ovsdb_get_dot3adAggPortPartnerAdminSystemID(
            idl, port_row, interface_row, dot3adAggPortPartnerAdminSystemID,
            &dot3adAggPortPartnerAdminSystemID_len);

        ovsdb_get_dot3adAggPortPartnerOperSystemID(
            idl, port_row, interface_row, dot3adAggPortPartnerOperSystemID,
            &dot3adAggPortPartnerOperSystemID_len);

        ovsdb_get_dot3adAggPortPartnerAdminKey(idl, port_row, interface_row,
                                               &dot3adAggPortPartnerAdminKey);

        ovsdb_get_dot3adAggPortPartnerOperKey(idl, port_row, interface_row,
                                              &dot3adAggPortPartnerOperKey);

        ovsdb_get_dot3adAggPortSelectedAggID(idl, port_row, interface_row,
                                             &dot3adAggPortSelectedAggID);

        ovsdb_get_dot3adAggPortAttachedAggID(idl, port_row, interface_row,
                                             &dot3adAggPortAttachedAggID);

        ovsdb_get_dot3adAggPortActorPort(idl, port_row, interface_row,
                                         &dot3adAggPortActorPort);

        ovsdb_get_dot3adAggPortActorPortPriority(
            idl, port_row, interface_row, &dot3adAggPortActorPortPriority);

        ovsdb_get_dot3adAggPortPartnerAdminPort(idl, port_row, interface_row,
                                                &dot3adAggPortPartnerAdminPort);

        ovsdb_get_dot3adAggPortPartnerOperPort(idl, port_row, interface_row,
                                               &dot3adAggPortPartnerOperPort);

        ovsdb_get_dot3adAggPortPartnerAdminPortPriority(
            idl, port_row, interface_row,
            &dot3adAggPortPartnerAdminPortPriority);

        ovsdb_get_dot3adAggPortPartnerOperPortPriority(
            idl, port_row, interface_row,
            &dot3adAggPortPartnerOperPortPriority);

        ovsdb_get_dot3adAggPortActorAdminState(idl, port_row, interface_row,
                                               &dot3adAggPortActorAdminState);

        ovsdb_get_dot3adAggPortActorOperState(idl, port_row, interface_row,
                                              &dot3adAggPortActorOperState);

        ovsdb_get_dot3adAggPortPartnerAdminState(
            idl, port_row, interface_row, &dot3adAggPortPartnerAdminState);

        ovsdb_get_dot3adAggPortPartnerOperState(idl, port_row, interface_row,
                                                &dot3adAggPortPartnerOperState);

        ovsdb_get_dot3adAggPortAggregateOrIndividual(
            idl, port_row, interface_row, &dot3adAggPortAggregateOrIndividual);

        rowreq_ctx = dot3adAggPortTable_allocate_rowreq_ctx(NULL);
        if (rowreq_ctx == NULL) {
            snmp_log(LOG_ERR, "memory allocation failed");
            return MFD_RESOURCE_UNAVAILABLE;
        }
        if (MFD_SUCCESS !=
            dot3adAggPortTable_indexes_set(rowreq_ctx, dot3adAggPortIndex)) {
            snmp_log(LOG_ERR, "error setting indexes while loading");
            dot3adAggPortTable_release_rowreq_ctx(rowreq_ctx);
            continue;
        }

        rowreq_ctx->data.dot3adAggPortActorSystemPriority =
            dot3adAggPortActorSystemPriority;
        rowreq_ctx->data.dot3adAggPortActorSystemID_len =
            dot3adAggPortActorSystemID_len *
            sizeof(dot3adAggPortActorSystemID[0]);
        memcpy(rowreq_ctx->data.dot3adAggPortActorSystemID,
               dot3adAggPortActorSystemID,
               dot3adAggPortActorSystemID_len *
                   sizeof(dot3adAggPortActorSystemID[0]));
        rowreq_ctx->data.dot3adAggPortActorAdminKey =
            dot3adAggPortActorAdminKey;
        rowreq_ctx->data.dot3adAggPortActorOperKey = dot3adAggPortActorOperKey;
        rowreq_ctx->data.dot3adAggPortPartnerAdminSystemPriority =
            dot3adAggPortPartnerAdminSystemPriority;
        rowreq_ctx->data.dot3adAggPortPartnerOperSystemPriority =
            dot3adAggPortPartnerOperSystemPriority;
        rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID_len =
            dot3adAggPortPartnerAdminSystemID_len *
            sizeof(dot3adAggPortPartnerAdminSystemID[0]);
        memcpy(rowreq_ctx->data.dot3adAggPortPartnerAdminSystemID,
               dot3adAggPortPartnerAdminSystemID,
               dot3adAggPortPartnerAdminSystemID_len *
                   sizeof(dot3adAggPortPartnerAdminSystemID[0]));
        rowreq_ctx->data.dot3adAggPortPartnerOperSystemID_len =
            dot3adAggPortPartnerOperSystemID_len *
            sizeof(dot3adAggPortPartnerOperSystemID[0]);
        memcpy(rowreq_ctx->data.dot3adAggPortPartnerOperSystemID,
               dot3adAggPortPartnerOperSystemID,
               dot3adAggPortPartnerOperSystemID_len *
                   sizeof(dot3adAggPortPartnerOperSystemID[0]));
        rowreq_ctx->data.dot3adAggPortPartnerAdminKey =
            dot3adAggPortPartnerAdminKey;
        rowreq_ctx->data.dot3adAggPortPartnerOperKey =
            dot3adAggPortPartnerOperKey;
        rowreq_ctx->data.dot3adAggPortSelectedAggID =
            dot3adAggPortSelectedAggID;
        rowreq_ctx->data.dot3adAggPortAttachedAggID =
            dot3adAggPortAttachedAggID;
        rowreq_ctx->data.dot3adAggPortActorPort = dot3adAggPortActorPort;
        rowreq_ctx->data.dot3adAggPortActorPortPriority =
            dot3adAggPortActorPortPriority;
        rowreq_ctx->data.dot3adAggPortPartnerAdminPort =
            dot3adAggPortPartnerAdminPort;
        rowreq_ctx->data.dot3adAggPortPartnerOperPort =
            dot3adAggPortPartnerOperPort;
        rowreq_ctx->data.dot3adAggPortPartnerAdminPortPriority =
            dot3adAggPortPartnerAdminPortPriority;
        rowreq_ctx->data.dot3adAggPortPartnerOperPortPriority =
            dot3adAggPortPartnerOperPortPriority;
        rowreq_ctx->data.dot3adAggPortActorAdminState =
            dot3adAggPortActorAdminState;
        rowreq_ctx->data.dot3adAggPortActorOperState =
            dot3adAggPortActorOperState;
        rowreq_ctx->data.dot3adAggPortPartnerAdminState =
            dot3adAggPortPartnerAdminState;
        rowreq_ctx->data.dot3adAggPortPartnerOperState =
            dot3adAggPortPartnerOperState;
        rowreq_ctx->data.dot3adAggPortAggregateOrIndividual =
            dot3adAggPortAggregateOrIndividual;
        CONTAINER_INSERT(container, rowreq_ctx);
        ++count;
    }
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_container_load",
                "inserted %d records\n", (int)count));
    return MFD_SUCCESS;
}

void dot3adAggPortTable_container_free(netsnmp_container *container) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_container_free",
                "called\n"));
}

int dot3adAggPortTable_row_prep(dot3adAggPortTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortTable_row_prep", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
    return MFD_SUCCESS;
}
