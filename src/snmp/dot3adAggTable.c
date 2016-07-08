#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include <net-snmp/agent/mib_modules.h>
#include "vswitch-idl.h"
#include "ovsdb-idl.h"

#include "dot3adAggTable.h"
#include "dot3adAggTable_interface.h"
#include "dot3adAggTable_ovsdb_get.h"

const oid dot3adAggTable_oid[] = {DOT3ADAGGTABLE_OID};
const int dot3adAggTable_oid_size = OID_LENGTH(dot3adAggTable_oid);

dot3adAggTable_registration dot3adAggTable_user_context;
void initialize_table_dot3adAggTable(void);
void shutdown_table_dot3adAggTable(void);

void init_dot3adAggTable(void) {
    DEBUGMSGTL(("verbose:dot3adAggTable:init_dot3adAggTable", "called\n"));

    dot3adAggTable_registration *user_context;
    u_long flags;

    user_context = netsnmp_create_data_list("dot3adAggTable", NULL, NULL);
    flags = 0;

    _dot3adAggTable_initialize_interface(user_context, flags);

    dot3adAggTable_ovsdb_idl_init(idl);
}

void shutdown_dot3adAggTable(void) {
    _dot3adAggTable_shutdown_interface(&dot3adAggTable_user_context);
}

int dot3adAggTable_rowreq_ctx_init(dot3adAggTable_rowreq_ctx *rowreq_ctx,
                                   void *user_init_ctx) {
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggTable_rowreq_ctx_init", "called\n"));

    netsnmp_assert(NULL != rowreq_ctx);

    return MFD_SUCCESS;
}

void dot3adAggTable_rowreq_ctx_cleanup(dot3adAggTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggTable_rowreq_ctx_cleanup",
                "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
}

int dot3adAggTable_pre_request(dot3adAggTable_registration *user_context) {
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggTable_pre_request", "called\n"));
    return MFD_SUCCESS;
}

int dot3adAggTable_post_request(dot3adAggTable_registration *user_context,
                                int rc) {
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggTable_post_request", "called\n"));
    return MFD_SUCCESS;
}
