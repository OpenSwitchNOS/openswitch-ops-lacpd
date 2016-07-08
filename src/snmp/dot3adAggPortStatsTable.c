#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include <net-snmp/agent/mib_modules.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

#include "dot3adAggPortStatsTable.h"
#include "dot3adAggPortStatsTable_interface.h"
#include "dot3adAggPortStatsTable_ovsdb_get.h"

const oid dot3adAggPortStatsTable_oid[] = {DOT3ADAGGPORTSTATSTABLE_OID};
const int dot3adAggPortStatsTable_oid_size =
    OID_LENGTH(dot3adAggPortStatsTable_oid);

dot3adAggPortStatsTable_registration dot3adAggPortStatsTable_user_context;
void initialize_table_dot3adAggPortStatsTable(void);
void shutdown_table_dot3adAggPortStatsTable(void);

void init_dot3adAggPortStatsTable(void) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:init_dot3adAggPortStatsTable",
                "called\n"));

    dot3adAggPortStatsTable_registration *user_context;
    u_long flags;

    user_context =
        netsnmp_create_data_list("dot3adAggPortStatsTable", NULL, NULL);
    flags = 0;

    _dot3adAggPortStatsTable_initialize_interface(user_context, flags);

    dot3adAggPortStatsTable_ovsdb_idl_init(idl);
}

void shutdown_dot3adAggPortStatsTable(void) {
    _dot3adAggPortStatsTable_shutdown_interface(
        &dot3adAggPortStatsTable_user_context);
}

int dot3adAggPortStatsTable_rowreq_ctx_init(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx, void *user_init_ctx) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "rowreq_ctx_init",
                "called\n"));

    netsnmp_assert(NULL != rowreq_ctx);

    return MFD_SUCCESS;
}

void dot3adAggPortStatsTable_rowreq_ctx_cleanup(
    dot3adAggPortStatsTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_"
                "rowreq_ctx_cleanup",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
}

int dot3adAggPortStatsTable_pre_request(
    dot3adAggPortStatsTable_registration *user_context) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_pre_request",
         "called\n"));
    return MFD_SUCCESS;
}

int dot3adAggPortStatsTable_post_request(
    dot3adAggPortStatsTable_registration *user_context, int rc) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortStatsTable:dot3adAggPortStatsTable_post_request",
         "called\n"));
    return MFD_SUCCESS;
}
