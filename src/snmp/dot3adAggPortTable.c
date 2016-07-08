#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include <net-snmp/agent/mib_modules.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

#include "dot3adAggPortTable.h"
#include "dot3adAggPortTable_interface.h"
#include "dot3adAggPortTable_ovsdb_get.h"

const oid dot3adAggPortTable_oid[] = {DOT3ADAGGPORTTABLE_OID};
const int dot3adAggPortTable_oid_size = OID_LENGTH(dot3adAggPortTable_oid);

dot3adAggPortTable_registration dot3adAggPortTable_user_context;
void initialize_table_dot3adAggPortTable(void);
void shutdown_table_dot3adAggPortTable(void);

void init_dot3adAggPortTable(void) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:init_dot3adAggPortTable", "called\n"));

    dot3adAggPortTable_registration *user_context;
    u_long flags;

    user_context = netsnmp_create_data_list("dot3adAggPortTable", NULL, NULL);
    flags = 0;

    _dot3adAggPortTable_initialize_interface(user_context, flags);

    dot3adAggPortTable_ovsdb_idl_init(idl);
}

void shutdown_dot3adAggPortTable(void) {
    _dot3adAggPortTable_shutdown_interface(&dot3adAggPortTable_user_context);
}

int dot3adAggPortTable_rowreq_ctx_init(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx, void *user_init_ctx) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_rowreq_ctx_init",
                "called\n"));

    netsnmp_assert(NULL != rowreq_ctx);

    return MFD_SUCCESS;
}

void dot3adAggPortTable_rowreq_ctx_cleanup(
    dot3adAggPortTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(
        ("verbose:dot3adAggPortTable:dot3adAggPortTable_rowreq_ctx_cleanup",
         "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
}

int dot3adAggPortTable_pre_request(
    dot3adAggPortTable_registration *user_context) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_pre_request",
                "called\n"));
    return MFD_SUCCESS;
}

int dot3adAggPortTable_post_request(
    dot3adAggPortTable_registration *user_context, int rc) {
    DEBUGMSGTL(("verbose:dot3adAggPortTable:dot3adAggPortTable_post_request",
                "called\n"));
    return MFD_SUCCESS;
}
