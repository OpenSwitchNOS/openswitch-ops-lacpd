#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-features.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/agent/net-snmp-agent-includes.h>
#include "IEEE8023_LAG_MIB_custom.h"
#include "dot3adAggTable.h"
#include "dot3adAggTable_data_access.h"
#include "dot3adAggTable_ovsdb_get.h"

#include "openswitch-idl.h"
#include "ovsdb-idl.h"
#include "vswitch-idl.h"
#include "openvswitch/vlog.h"

int dot3adAggTable_init_data(dot3adAggTable_registration *dot3adAggTable_reg) {
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggTable_init_data", "called\n"));
    return MFD_SUCCESS;
}

void dot3adAggTable_container_init(netsnmp_container **container_ptr_ptr,
                                   netsnmp_cache *cache) {
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggTable_container_init", "called\n"));
    if (NULL == container_ptr_ptr) {
        snmp_log(LOG_ERR,
                 "bad container param to dot3adAggTable_container_init\n");
        return;
    }
    *container_ptr_ptr = NULL;
    if (NULL == cache) {
        snmp_log(LOG_ERR, "bad cache param to dot3adAggTable_container_init\n");
        return;
    }
    cache->timeout = DOT3ADAGGTABLE_CACHE_TIMEOUT;
}

void dot3adAggTable_container_shutdown(netsnmp_container *container_ptr) {
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggTable_container_shutdown",
                "called\n"));
    if (NULL == container_ptr) {
        snmp_log(LOG_ERR, "bad params to dot3adAggTable_container_shutdown\n");
        return;
    }
}

const struct ovsrec_interface * gethighestPriorityInterfaceforPort(const struct ovsrec_port *port_row )
{

	int intf_index = 0;
	char *port_id = NULL, *port_priority = NULL;
	char *temp = NULL;
	int interface_ix = 0;
	int interface_priority = 0;
	const struct ovsrec_interface *interface_row = NULL;

	for (intf_index = 0; intf_index < port_row->n_interfaces; intf_index++)
	{

		interface_row = port_row->interfaces[intf_index];
		temp =
			(char *)smap_get(&interface_row->other_config,
							 PORT_OTHER_CONFIG_MAP_LACP_SYSTEM_PRIORITY);
		if (temp == NULL) {
			temp= strdup(smap_get(&interface_row->lacp_status,
								  INTERFACE_LACP_STATUS_MAP_ACTOR_PORT_ID));
			parse_id_from_db(temp, &port_priority, &port_id);

			if(interface_priority > atoi(port_priority) || interface_priority == 0)
			{
				interface_priority = atoi(port_priority);
				interface_ix = intf_index;
			}

			if (temp){
				free(temp);
				temp = NULL;
			}
		}
		else
		{
			interface_priority = atoi(temp);
			interface_ix = intf_index;
		}
	}
	return  port_row->interfaces[interface_ix];
}

int dot3adAggTable_container_load(netsnmp_container *container) {
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggTable_container_load", "called\n"));
    dot3adAggTable_rowreq_ctx *rowreq_ctx;
    size_t count = 0;

    const struct ovsrec_port *port_row = NULL;
    const struct ovsrec_system *system_row = NULL;
    const struct ovsrec_interface *interface_row = NULL;

    long dot3adAggIndex;

    char dot3adAggMACAddress[255];
    size_t dot3adAggMACAddress_len;
    long dot3adAggActorSystemPriority;
    char dot3adAggActorSystemID[255];
    size_t dot3adAggActorSystemID_len;
    long dot3adAggAggregateOrIndividual;
    long dot3adAggActorAdminKey;
    long dot3adAggActorOperKey;
    char dot3adAggPartnerSystemID[255];
    size_t dot3adAggPartnerSystemID_len;
    long dot3adAggPartnerSystemPriority;
    long dot3adAggPartnerOperKey;
    long dot3adAggCollectorMaxDelay;

    port_row = ovsrec_port_first(idl);
    if (!port_row) {
        snmp_log(LOG_ERR, "not able to fetch port row");
        return -1;
    }

    system_row = ovsrec_system_first(idl);
    if (!system_row) {
        snmp_log(LOG_ERR, "not able to fetch system row");
        return -1;
    }

    //interface_row = ovsrec_interface_first(idl);
    //if (!interface_row) {
    //    snmp_log(LOG_ERR, "not able to fetch interface row");
    //    return -1;
    //}

       OVSREC_PORT_FOR_EACH(port_row, idl) {
        if (dot3adAggTable_skip_function(idl, port_row)) {
            continue;
        }
		//Get the highest priority interface
		interface_row = gethighestPriorityInterfaceforPort(port_row);


        ovsdb_get_dot3adAggIndex(idl, port_row, &dot3adAggIndex);

        ovsdb_get_dot3adAggMACAddress(idl, system_row,
                                      dot3adAggMACAddress,
                                      &dot3adAggMACAddress_len);

        ovsdb_get_dot3adAggActorSystemPriority(idl, port_row, system_row,
                                               &dot3adAggActorSystemPriority);

        ovsdb_get_dot3adAggActorSystemID(idl, port_row, system_row,
                                         dot3adAggActorSystemID,
                                         &dot3adAggActorSystemID_len);

        ovsdb_get_dot3adAggAggregateOrIndividual(
            idl, port_row, &dot3adAggAggregateOrIndividual);

        ovsdb_get_dot3adAggActorAdminKey(idl, port_row, interface_row,
                                         &dot3adAggActorAdminKey);

        ovsdb_get_dot3adAggActorOperKey(idl, port_row, interface_row,
                                        &dot3adAggActorOperKey);

        ovsdb_get_dot3adAggPartnerSystemID(idl, port_row, interface_row,
                                           dot3adAggPartnerSystemID,
                                           &dot3adAggPartnerSystemID_len);

        ovsdb_get_dot3adAggPartnerSystemPriority(
            idl, port_row,interface_row, &dot3adAggPartnerSystemPriority);

        ovsdb_get_dot3adAggPartnerOperKey(idl, port_row, interface_row,
                                          &dot3adAggPartnerOperKey);

        ovsdb_get_dot3adAggCollectorMaxDelay(idl, port_row,
                                             &dot3adAggCollectorMaxDelay);

        rowreq_ctx = dot3adAggTable_allocate_rowreq_ctx(NULL);
        if (rowreq_ctx == NULL) {
            snmp_log(LOG_ERR, "memory allocation failed");
            return MFD_RESOURCE_UNAVAILABLE;
        }
        if (MFD_SUCCESS !=
            dot3adAggTable_indexes_set(rowreq_ctx, dot3adAggIndex)) {
            snmp_log(LOG_ERR, "error setting indexes while loading");
            dot3adAggTable_release_rowreq_ctx(rowreq_ctx);
            continue;
        }

        rowreq_ctx->data.dot3adAggMACAddress_len =
            dot3adAggMACAddress_len * sizeof(dot3adAggMACAddress[0]);
        memcpy(rowreq_ctx->data.dot3adAggMACAddress, dot3adAggMACAddress,
               dot3adAggMACAddress_len * sizeof(dot3adAggMACAddress[0]));
        rowreq_ctx->data.dot3adAggActorSystemPriority =
            dot3adAggActorSystemPriority;
        rowreq_ctx->data.dot3adAggActorSystemID_len =
            dot3adAggActorSystemID_len * sizeof(dot3adAggActorSystemID[0]);
        memcpy(rowreq_ctx->data.dot3adAggActorSystemID, dot3adAggActorSystemID,
               dot3adAggActorSystemID_len * sizeof(dot3adAggActorSystemID[0]));
        rowreq_ctx->data.dot3adAggAggregateOrIndividual =
            dot3adAggAggregateOrIndividual;
        rowreq_ctx->data.dot3adAggActorAdminKey = dot3adAggActorAdminKey;
        rowreq_ctx->data.dot3adAggActorOperKey = dot3adAggActorOperKey;
        rowreq_ctx->data.dot3adAggPartnerSystemID_len =
            dot3adAggPartnerSystemID_len * sizeof(dot3adAggPartnerSystemID[0]);
        memcpy(
            rowreq_ctx->data.dot3adAggPartnerSystemID, dot3adAggPartnerSystemID,
            dot3adAggPartnerSystemID_len * sizeof(dot3adAggPartnerSystemID[0]));
        rowreq_ctx->data.dot3adAggPartnerSystemPriority =
            dot3adAggPartnerSystemPriority;
        rowreq_ctx->data.dot3adAggPartnerOperKey = dot3adAggPartnerOperKey;
        rowreq_ctx->data.dot3adAggCollectorMaxDelay =
            dot3adAggCollectorMaxDelay;
        CONTAINER_INSERT(container, rowreq_ctx);
        ++count;
    }
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggTable_container_load",
                "inserted %d records\n", (int)count));
    return MFD_SUCCESS;
}

void dot3adAggTable_container_free(netsnmp_container *container) {
    DEBUGMSGTL(
        ("verbose:dot3adAggTable:dot3adAggTable_container_free", "called\n"));
}

int dot3adAggTable_row_prep(dot3adAggTable_rowreq_ctx *rowreq_ctx) {
    DEBUGMSGTL(("verbose:dot3adAggTable:dot3adAggTable_row_prep", "called\n"));
    netsnmp_assert(NULL != rowreq_ctx);
    return MFD_SUCCESS;
}
