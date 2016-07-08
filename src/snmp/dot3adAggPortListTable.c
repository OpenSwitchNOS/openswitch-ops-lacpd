#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include <net-snmp/agent/mib_modules.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

#include "dot3adAggPortListTable.h"
#include "dot3adAggPortListTable_interface.h"
#include "dot3adAggPortListTable_ovsdb_get.h"

const oid dot3adAggPortListTable_oid[] = {DOT3ADAGGPORTLISTTABLE_OID};
const int dot3adAggPortListTable_oid_size =
    OID_LENGTH(dot3adAggPortListTable_oid);

dot3adAggPortListTable_registration dot3adAggPortListTable_user_context;
void initialize_table_dot3adAggPortListTable(void);
void shutdown_table_dot3adAggPortListTable(void);

void init_dot3adAggPortListTable(void) {
    DEBUGMSGTL(("verbose:dot3adAggPortListTable:init_dot3adAggPortListTable",
                "called\n"));

    dot3adAggPortListTable_registration *user_context;
    u_long flags;

    user_context =
        netsnmp_create_data_list("dot3adAggPortListTable", NULL, NULL);
    flags = 0;

    _dot3adAggPortListTable_initialize_interface(user_context, flags);

    dot3adAggPortListTable_ovsdb_idl_init(idl);
}

void shutdown_dot3adAggPortListTable(void) {
    _dot3adAggPortListTable_shutdown_interface(
        &dot3adAggPortListTable_user_context);
}

int dot3adAggPortListTable_rowreq_ctx_init(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx, void *user_init_ctx) {
    DEBUGMSGTL((
        "verbose:dot3adAggPortListTable:dot3adAggPortListTable_rowreq_ctx_init",
        "called\n"));

    netsnmp_assert(NULL != rowreq_ctx);

    return MFD_SUCCESS;
}

void dot3adAggPortListTable_rowreq_ctx_cleanup(
    dot3adAggPortListTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(("verbose:dot3adAggPortListTable:dot3adAggPortListTable_rowreq_"
                "ctx_cleanup",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
}

int dot3adAggPortListTable_pre_request(
    dot3adAggPortListTable_registration *user_context) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_pre_request",
         "called\n"));
    return MFD_SUCCESS;
}

int dot3adAggPortListTable_post_request(
    dot3adAggPortListTable_registration *user_context, int rc) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortListTable:dot3adAggPortListTable_post_request",
         "called\n"));
    return MFD_SUCCESS;
}
