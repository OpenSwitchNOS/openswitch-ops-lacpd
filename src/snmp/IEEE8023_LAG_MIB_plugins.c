#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "IEEE8023_LAG_MIB_plugins.h"
#include "IEEE8023_LAG_MIB_scalars.h"
#include "dot3adAggTable.h"
#include "dot3adAggPortListTable.h"
#include "dot3adAggPortStatsTable.h"
#include "dot3adAggPortTable.h"

void ops_snmp_init(void) {

    init_dot3adAggTable();
    init_dot3adAggPortListTable();
    init_dot3adAggPortStatsTable();
    init_dot3adAggPortTable();
}

void ops_snmp_run(void) {}
void ops_snmp_wait(void) {}
void ops_snmp_destroy(void) {
    shutdown_dot3adAggTable();
    shutdown_dot3adAggPortListTable();
    shutdown_dot3adAggPortStatsTable();
    shutdown_dot3adAggPortTable();
}
