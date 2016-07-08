// Define Custom Functions for IEEE8023_LAG_MIB MIB in this fileNameint lldpPortConfigTable_skip_function(const struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row) {
#include <stdlib.h>
#include <net/if.h>
#include <errno.h>
#include "lacp_cmn.h"
#include "ovsdb-idl.h"
#include "lacp_ops_if.h"
#include "IEEE8023_LAG_MIB_custom.h"

#define LACP_STATUS_FIELD_COUNT 8

void
parse_id_from_db (char *str, char **value1, char **value2)
{
  *value1 = strsep(&str, ",");
  *value2 = strsep(&str, ",");
}

int
parse_state_from_db(const char *str, int *ret_str)
{
    
 return sscanf(str, "%*[^01]%d%*[^01]%d%*[^01]%d%*[^01]%d%*[^01]%d%*[^01]%d%*[^01]%d%*[^01]%d",
               &ret_str[0], &ret_str[1], &ret_str[2], &ret_str[3], &ret_str[4], &ret_str[5],
               &ret_str[6], &ret_str[7]);
}

int
get_lacp_state(const int *state)
{
   /* +1 for the event where all flags are ON then we have a place to store \0 */
   int ret = 0;

   if(state == NULL) return 0;
   
   ret |= state[0]? 128:0;
   ret |= state[1]? 64:0;
   ret |= state[2]? 32:0;
   ret |= state[3]? 16:0;
   ret |= state[4]? 8:0;
   ret |= state[5]? 4:0;
   ret |= state[6]? 2:0;
   ret |= state[7]? 1:0;

   return ret;
}
int dot3adAggTable_skip_function(struct ovsdb_idl *idl,
const struct ovsrec_port *port_row) {
	
	if (strncmp(port_row->name, LAG_PORT_NAME_PREFIX, LAG_PORT_NAME_PREFIX_LENGTH) == 0)
        return 0;
	
    return 1;
}
void dot3adAggIndex_custom_function(struct ovsdb_idl *idl,
                                    const struct ovsrec_port *port_row,
                                    long *dot3adAggIndex_val_ptr){
    char * temp = port_row->name;
    *dot3adAggIndex_val_ptr = atoi(temp);
}

void dot3adAggActorSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    long *dot3adAggActorSystemPriority_val_ptr){
	
    int temp = smap_get_int(&port_row->other_config, PORT_OTHER_CONFIG_MAP_LACP_SYSTEM_PRIORITY,0);
	if(temp == 0)
		temp = smap_get_int(&system_row->lacp_config, SYSTEM_LACP_CONFIG_MAP_LACP_SYSTEM_PRIORITY, DFLT_SYSTEM_LACP_CONFIG_SYSTEM_PRIORITY);
    
	*dot3adAggActorSystemPriority_val_ptr = (long)temp;

}

void dot3adAggActorSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_system *system_row,
    char *dot3adAggActorSystemID_val_ptr,
	size_t *dot3adAggActorSystemID_val_ptr_len){
	
    char *sys_mac =
        (char *)smap_get(&port_row->other_config, PORT_OTHER_CONFIG_MAP_LACP_SYSTEM_ID);
	if(sys_mac == NULL)
	sys_mac =
                (char *)smap_get(&system_row->lacp_config, SYSTEM_LACP_CONFIG_MAP_LACP_SYSTEM_ID  );
	
	/* If LACP system ID is not configured, then use system mac. */
	if (sys_mac == NULL || (strlen(sys_mac) != OPS_MAC_STR_SIZE - 1)) {
		sys_mac = system_row->system_mac;
	}
			
	
	*dot3adAggActorSystemID_val_ptr_len = sys_mac != NULL ? strlen(sys_mac) : 0;
        strcpy(dot3adAggActorSystemID_val_ptr, sys_mac);
}

void dot3adAggPartnerSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    char *dot3adAggPartnerSystemID_val_ptr,
    size_t *dot3adAggPartnerSystemID_val_ptr_len){

	char *system_id = NULL, *system_priority = NULL;
	char *system_priority_id_ovsdb = NULL;
	
	char* tmp = NULL;
	
	tmp = (char *)smap_get(&interface_row->lacp_status,
			 INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID);
	if(tmp !=NULL)
	{
	
	
		system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
									  INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID));

		
		parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
		
		strcpy(dot3adAggPartnerSystemID_val_ptr,system_id);
			
		*dot3adAggPartnerSystemID_val_ptr_len = strlen(system_id);
	
		if (system_priority_id_ovsdb){
			free(system_priority_id_ovsdb);
			system_priority_id_ovsdb = NULL;
			}
	}else
	{
		*dot3adAggPartnerSystemID_val_ptr_len = 0;
	}

}

void dot3adAggPartnerSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    long *dot3adAggPartnerSystemPriority_val_ptr){
	
	char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;
	
	char* tmp = NULL;
	
	tmp = (char *)smap_get(&interface_row->lacp_status,
						   INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID);
	if(tmp !=NULL)
	{
		
		system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
									  INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID));

		parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
		
		*dot3adAggPartnerSystemPriority_val_ptr = atoi(system_priority);
		
		if (system_priority_id_ovsdb){
			free(system_priority_id_ovsdb);
			system_priority_id_ovsdb = NULL;
		}else
		{
			*dot3adAggPartnerSystemPriority_val_ptr = 0;
		}
	}
}

void dot3adAggCollectorMaxDelay_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    long *dot3adAggCollectorMaxDelay_val_ptr){
    *dot3adAggCollectorMaxDelay_val_ptr = 1;
}

/************************************************************/
int Dot3adAggPortListEntry_skip_function(struct ovsdb_idl *idl,
		const struct ovsrec_port *port_row)
{
	if (strncmp(port_row->name, LAG_PORT_NAME_PREFIX, LAG_PORT_NAME_PREFIX_LENGTH) == 0)
	{
		if(port_row->interfaces == NULL)
			return 1;
		else
			return 0;
	}
    return 1;
		
}


void dot3adAggPortListPorts_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    char *dot3adAggPortListPorts_val_ptr,
    size_t *dot3adAggPortListPorts_val_ptr_len)
{
	const struct ovsrec_interface *if_row = NULL;
	int intf_index=0;
	
	for (intf_index = 0; intf_index < port_row->n_interfaces; intf_index++)
	{
		
        if_row = port_row->interfaces[intf_index];

		char *temp = (char *)if_row->name;
		if(dot3adAggPortListPorts_val_ptr_len > 0)
		{
			if(intf_index == 0)
			{
				strcpy(dot3adAggPortListPorts_val_ptr, temp);
			}else
			{
				strcat(dot3adAggPortListPorts_val_ptr,",");
				strcat(dot3adAggPortListPorts_val_ptr , temp);
			}
		}
		
		*dot3adAggPortListPorts_val_ptr_len = strlen(dot3adAggPortListPorts_val_ptr);
	}

}

int dot3adAggPortStats_skip_function(struct ovsdb_idl *idl,
                                     const struct ovsrec_port *port_row)
{
	if (strncmp(port_row->name, LAG_PORT_NAME_PREFIX, LAG_PORT_NAME_PREFIX_LENGTH) == 0)
        return 0;
	
    return 1;
}

void dot3adAggPortStatsIndex_custom_function(struct ovsdb_idl *idl,
		const struct ovsrec_port *port_row,
		long *dot3adAggPortIndex_val_ptr)
{
    char * temp = port_row->name;
    *dot3adAggPortIndex_val_ptr = atoi(temp);
}

int dot3adAggPortEntry_skip_function(struct ovsdb_idl *idl,
    const struct ovsrec_interface *interface_row)
{
	const char * agg_key = NULL;
	
	agg_key = smap_get(&interface_row->other_config,
					   INTERFACE_OTHER_CONFIG_MAP_LACP_AGGREGATION_KEY);
        if(agg_key == NULL)
            return 1;
        
	if (atoi(agg_key)>0)
            return 0;
	
    return 1;
}
void dot3adAggPortIndex_custom_function(struct ovsdb_idl *idl,
		const struct ovsrec_interface *interface_row,
		long *dot3adAggPortIndex_val_ptr)
{
    char * temp = interface_row->name;
    *dot3adAggPortIndex_val_ptr = atoi(temp);
}

void dot3adAggPortActorSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorSystemPriority_val_ptr)
{
	char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;
	
	system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
									  INTERFACE_LACP_STATUS_MAP_ACTOR_SYSTEM_ID));
	parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
	
	if(system_priority == NULL)
	{
		*dot3adAggPortActorSystemPriority_val_ptr = 0;
	}else
	{
		*dot3adAggPortActorSystemPriority_val_ptr = atoi(system_priority);
	}
	
	if (system_priority_id_ovsdb){
		free(system_priority_id_ovsdb);
		system_priority_id_ovsdb = NULL;
	}

}

void dot3adAggPortActorSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    char *dot3adAggPortActorSystemID_val_ptr,
    size_t *dot3adAggPortActorSystemID_val_ptr_len)
{

	
	char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;
	
	system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
									  INTERFACE_LACP_STATUS_MAP_ACTOR_SYSTEM_ID));
	parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
	
	*dot3adAggPortActorSystemID_val_ptr_len = system_id != NULL ? strlen(system_id) : 0;
	if(dot3adAggPortActorSystemID_val_ptr_len > 0)
	{
		strcpy(dot3adAggPortActorSystemID_val_ptr, system_id);
	}
	
	if (system_priority_id_ovsdb){
		free(system_priority_id_ovsdb);
		system_priority_id_ovsdb = NULL;
	}

}

void dot3adAggPortPartnerAdminSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminSystemPriority_val_ptr){

	char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;
	char * tmp = NULL;
	
	tmp = (char *)smap_get(&interface_row->lacp_status,
						   INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID);
	if(tmp != NULL)
	{
		system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
										  INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID));
		
		parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
		*dot3adAggPortPartnerAdminSystemPriority_val_ptr = strlen(system_priority);
		
		if (system_priority_id_ovsdb){
			free(system_priority_id_ovsdb);
			system_priority_id_ovsdb = NULL;
		}
	}
	else
	{
		*dot3adAggPortPartnerAdminSystemPriority_val_ptr = 0;
	}

}

void dot3adAggPortPartnerOperSystemPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperSystemPriority_val_ptr)
{
	char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;
	
	char * tmp = NULL;
	
	tmp = (char *)smap_get(&interface_row->lacp_status,
						   INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID);
	
	if(tmp != NULL)
	{
		
		system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
										  INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID));
		
		parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
		
		*dot3adAggPortPartnerOperSystemPriority_val_ptr = strlen(system_priority);
		
		if (system_priority_id_ovsdb){
			free(system_priority_id_ovsdb);
			system_priority_id_ovsdb = NULL;
		}
	}
	else
	{
		*dot3adAggPortPartnerOperSystemPriority_val_ptr = 0;
	}

}

void dot3adAggPortPartnerAdminSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerAdminSystemID_val_ptr,
    size_t *dot3adAggPortPartnerAdminSystemID_val_ptr_len)
{
	char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;
	
	char * tmp = NULL;
	
	tmp = (char *)smap_get(&interface_row->lacp_status,
			 INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID);
	
	if(tmp != NULL)
	{
			  
		system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
										  INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID));
		
		parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
		
		strcpy(dot3adAggPortPartnerAdminSystemID_val_ptr,system_id);
		
		*dot3adAggPortPartnerAdminSystemID_val_ptr_len = strlen(system_id);
		
		if (system_priority_id_ovsdb){
			free(system_priority_id_ovsdb);
			system_priority_id_ovsdb = NULL;
		}
	}
	else
	{
		*dot3adAggPortPartnerAdminSystemID_val_ptr_len = 0;
	}
		

}

void dot3adAggPortPartnerOperSystemID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    char *dot3adAggPortPartnerOperSystemID_val_ptr,
    size_t *dot3adAggPortPartnerOperSystemID_val_ptr_len)
{
	char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;
	char *tmp = NULL;
	
	tmp = (char *)smap_get(&interface_row->lacp_status,
				   INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID);
	if(tmp != NULL)
	{
		system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
										  INTERFACE_LACP_STATUS_MAP_PARTNER_SYSTEM_ID));
		
		parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);
		
		strcpy(dot3adAggPortPartnerOperSystemID_val_ptr,system_id);
		
		*dot3adAggPortPartnerOperSystemID_val_ptr_len = strlen(system_id);
		
		if (system_priority_id_ovsdb){
			free(system_priority_id_ovsdb);
			system_priority_id_ovsdb = NULL;
		}
	}else
	{
		strcpy(dot3adAggPortPartnerOperSystemID_val_ptr," ");
		*dot3adAggPortPartnerOperSystemID_val_ptr_len =strlen(dot3adAggPortPartnerOperSystemID_val_ptr);
	}

}

void dot3adAggPortPartnerOperPort_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPort_val_ptr)
{
    char *partner_priority_id_ovsdb = NULL;
    char *partner_id = NULL, *partner_priority = NULL;

    partner_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
            INTERFACE_LACP_STATUS_MAP_PARTNER_PORT_ID));

    parse_id_from_db(partner_priority_id_ovsdb, &partner_priority, &partner_id);

    if(partner_id == NULL)
        *dot3adAggPortPartnerOperPort_val_ptr = 0;
    else
        *dot3adAggPortPartnerOperPort_val_ptr = atoi(partner_id);

    if (partner_priority_id_ovsdb){
            free(partner_priority_id_ovsdb);
            partner_priority_id_ovsdb = NULL;
    }
	
	
	
}

void dot3adAggPortSelectedAggID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    long *dot3adAggPortSelectedAggID_val_ptr)
{
	char *port_priority_id_ovsdb = NULL;
	char *port_id = NULL, *port_priority = NULL;
	
	char *tmp = NULL;
	tmp = (char *)smap_get(&interface_row->lacp_status,
                INTERFACE_LACP_STATUS_MAP_ACTOR_PORT_ID);
	
	if(tmp != NULL)
	{
		port_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
                        INTERFACE_LACP_STATUS_MAP_ACTOR_PORT_ID));
		parse_id_from_db(port_priority_id_ovsdb, &port_priority, &port_id);

		*dot3adAggPortSelectedAggID_val_ptr = atoi(port_id);
		
		if (port_priority_id_ovsdb){
			free(port_priority_id_ovsdb);
			port_priority_id_ovsdb = NULL;
	}
	}else
	{
		*dot3adAggPortSelectedAggID_val_ptr = 0;
	}
}
void dot3adAggPortAttachedAggID_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortAttachedAggID_val_ptr)
{
    int if_idx = 0;
    
    if_idx = if_nametoindex(interface_row->name);
    *dot3adAggPortAttachedAggID_val_ptr = if_idx;
    
}
void dot3adAggPortActorPort_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPort_val_ptr)
{
    char *system_priority_id_ovsdb = NULL;
	char *system_id = NULL, *system_priority = NULL;

        system_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
                INTERFACE_LACP_STATUS_MAP_ACTOR_PORT_ID));

        parse_id_from_db(system_priority_id_ovsdb, &system_priority, &system_id);

        if(system_id == NULL)
            *dot3adAggPortActorPort_val_ptr = 0;
        else
            *dot3adAggPortActorPort_val_ptr = atoi(system_id);

        if (system_priority_id_ovsdb){
                free(system_priority_id_ovsdb);
                system_priority_id_ovsdb = NULL;
        }
	
}
void dot3adAggPortActorPortPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    long *dot3adAggPortActorPortPriority_val_ptr)
{
    char *actor_priority_id_ovsdb = NULL;
    char *actor_id = NULL, *actor_priority = NULL;
    char *tmp = NULL;

    tmp = (char*)smap_get(&interface_row->lacp_status,
                                              INTERFACE_LACP_STATUS_MAP_ACTOR_PORT_ID);
    if(tmp !=NULL)
    {
            actor_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
                                                                              INTERFACE_LACP_STATUS_MAP_ACTOR_PORT_ID));

            parse_id_from_db(actor_priority_id_ovsdb, &actor_priority, &actor_id);

            *dot3adAggPortActorPortPriority_val_ptr = atoi(actor_priority);

            if (actor_priority_id_ovsdb){
                    free(actor_priority_id_ovsdb);
                    actor_priority_id_ovsdb = NULL;
            }
    }else
    {
            *dot3adAggPortActorPortPriority_val_ptr = 0;
    }

}

void dot3adAggPortPartnerAdminPort_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPort_val_ptr)
{
    char *partner_priority_id_ovsdb = NULL;
    char *partner_id = NULL, *partner_priority = NULL;

    partner_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
            INTERFACE_LACP_STATUS_MAP_PARTNER_PORT_ID));

    parse_id_from_db(partner_priority_id_ovsdb, &partner_priority, &partner_id);

    if(partner_id == NULL)
        *dot3adAggPortPartnerAdminPort_val_ptr = 0;
    else
        *dot3adAggPortPartnerAdminPort_val_ptr = atoi(partner_id);

    if (partner_priority_id_ovsdb){
            free(partner_priority_id_ovsdb);
            partner_priority_id_ovsdb = NULL;
    }

    
}

void dot3adAggPortPartnerAdminPortPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerAdminPortPriority_val_ptr)
{
    char *partner_priority_id_ovsdb = NULL;
    char *partner_id = NULL, *partner_priority = NULL;

    char* tmp = NULL;

    tmp = (char *)smap_get(&interface_row->lacp_status,
                                               INTERFACE_LACP_STATUS_MAP_PARTNER_PORT_ID);
    if(tmp != NULL)
    {
            partner_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
                                                                              INTERFACE_LACP_STATUS_MAP_PARTNER_PORT_ID));

            parse_id_from_db(partner_priority_id_ovsdb, &partner_priority, &partner_id);

            *dot3adAggPortPartnerAdminPortPriority_val_ptr = atoi(partner_priority);

            if (partner_priority_id_ovsdb){
                    free(partner_priority_id_ovsdb);
                    partner_priority_id_ovsdb = NULL;
            }
    }else
    {
            *dot3adAggPortPartnerAdminPortPriority_val_ptr = 0;
    }

}

void dot3adAggPortPartnerOperPortPriority_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    long *dot3adAggPortPartnerOperPortPriority_val_ptr)
{

	char *partner_priority_id_ovsdb = NULL;
	char *partner_id = NULL, *partner_priority = NULL;
	
	char* tmp = NULL;
	
	tmp = (char *)smap_get(&interface_row->lacp_status,
						   INTERFACE_LACP_STATUS_MAP_PARTNER_PORT_ID);
	if(tmp != NULL)
	{
			
		partner_priority_id_ovsdb = strdup(smap_get(&interface_row->lacp_status,
										   INTERFACE_LACP_STATUS_MAP_PARTNER_PORT_ID));
		
		parse_id_from_db(partner_priority_id_ovsdb, &partner_priority, &partner_id);
		
		*dot3adAggPortPartnerOperPortPriority_val_ptr = atoi(partner_priority);
		
		if (partner_priority_id_ovsdb){
			free(partner_priority_id_ovsdb);
			partner_priority_id_ovsdb = NULL;
		}
	}else
	{
		*dot3adAggPortPartnerOperPortPriority_val_ptr = 0;
	}
}

void dot3adAggPortActorAdminState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
	const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorAdminState_val_ptr)
{
    const char *data_in_db = NULL;
    int lacp_state = 0;
    int lacp_state_ovsdb[LACP_STATUS_FIELD_COUNT];
       
	data_in_db = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_ACTOR_STATE);
	if(data_in_db)
	{
          if (parse_state_from_db(data_in_db, lacp_state_ovsdb) == LACP_STATUS_FIELD_COUNT)
          {
            lacp_state = get_lacp_state(lacp_state_ovsdb);
          }
          *dot3adAggPortActorAdminState_val_ptr = lacp_state;
            
	}
}

void dot3adAggPortActorOperState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortActorOperState_val_ptr)
{
    const char *data_in_db = NULL;
    int lacp_state = 0;
    int lacp_state_ovsdb[LACP_STATUS_FIELD_COUNT];
       
	data_in_db = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_ACTOR_STATE);
	if(data_in_db)
	{
          if (parse_state_from_db(data_in_db, lacp_state_ovsdb) == LACP_STATUS_FIELD_COUNT)
          {
            lacp_state = get_lacp_state(lacp_state_ovsdb);
          }
          *dot3adAggPortActorOperState_val_ptr = lacp_state;
            
	}
}
void dot3adAggPortPartnerAdminState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerAdminState_val_ptr)
{
    const char *data_in_db = NULL;
    int lacp_state = 0;
    int lacp_state_ovsdb[LACP_STATUS_FIELD_COUNT];
       
	data_in_db = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_PARTNER_STATE);
	if(data_in_db)
	{
          if (parse_state_from_db(data_in_db, lacp_state_ovsdb) == LACP_STATUS_FIELD_COUNT)
          {
            lacp_state = get_lacp_state(lacp_state_ovsdb);
          }
          *dot3adAggPortPartnerAdminState_val_ptr = lacp_state;
            
	}
}

void dot3adAggPortPartnerOperState_custom_function(
    struct ovsdb_idl *idl, const struct ovsrec_port *port_row,
    const struct ovsrec_interface *interface_row,
    u_long *dot3adAggPortPartnerOperState_val_ptr)
{
    const char *data_in_db = NULL;
    int lacp_state = 0;
    int lacp_state_ovsdb[LACP_STATUS_FIELD_COUNT];

    data_in_db = smap_get(&interface_row->lacp_status, INTERFACE_LACP_STATUS_MAP_PARTNER_STATE);
    if(data_in_db)
    {
        if (parse_state_from_db(data_in_db, lacp_state_ovsdb) == LACP_STATUS_FIELD_COUNT)
          {
            lacp_state = get_lacp_state(lacp_state_ovsdb);
          }
          *dot3adAggPortPartnerOperState_val_ptr = lacp_state;

    }
}


