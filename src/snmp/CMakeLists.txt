# (C) Copyright 2016 Hewlett Packard Enterprise Development LP
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

cmake_minimum_required (VERSION 2.8)

set (OPSLACPD ops-lacpd)
project (${OPSLACPD})

set (INCL_DIR ${CMAKE_SOURCE_DIR}/include)
set (LIBLACPSNMP lacp_snmp)

# This option is specified in Yocto -- openswitch.bbclass.
OPTION( CPU_LITTLE_ENDIAN "Specifies CPU architecture is Little-Endian" OFF )

# Define compile flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu99 -Wall -ggdb -g3 -O0")
set(LDFLAGS "${CMAKE_MODULE_LINKER_FLAGS}  -module -shared -avoid-version")

add_definitions(-DHAVE_CONFIG_H -DHAVE_SOCKLEN_T -DSYSCONFDIR=\"/etc/\")

# Rules to locate needed libraries
include(FindPkgConfig)
pkg_check_modules(OVSCOMMON REQUIRED libovscommon)
pkg_check_modules(OVSDB REQUIRED libovsdb)
pkg_check_modules(OPSUTILS REQUIRED opsutils)

include_directories (${INCL_DIR}
                     ${PROJECT_SOURCE_DIR}
                     ${OVSCOMMON_INCLUDE_DIRS}
                     ${OPSUTILS_INCLUDE_DIRS}
                     )

# SNMP libraries source files
set (SOURCES_SNMP ${PROJECT_SOURCE_DIR}/dot3adAggPortListTable.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortListTable_data_access.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortListTable_data_get.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortListTable_data_set.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortListTable_interface.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortListTable_ovsdb_get.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortStatsTable.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortStatsTable_data_access.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortStatsTable_data_get.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortStatsTable_data_set.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortStatsTable_interface.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortStatsTable_ovsdb_get.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortTable.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortTable_data_access.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortTable_data_get.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortTable_data_set.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortTable_interface.c
		${PROJECT_SOURCE_DIR}/dot3adAggPortTable_ovsdb_get.c
		${PROJECT_SOURCE_DIR}/dot3adAggTable.c
		${PROJECT_SOURCE_DIR}/dot3adAggTable_data_access.c
		${PROJECT_SOURCE_DIR}/dot3adAggTable_data_get.c
		${PROJECT_SOURCE_DIR}/dot3adAggTable_data_set.c
		${PROJECT_SOURCE_DIR}/dot3adAggTable_interface.c
		${PROJECT_SOURCE_DIR}/dot3adAggTable_ovsdb_get.c
		${PROJECT_SOURCE_DIR}/IEEE8023_LAG_MIB_custom.c
		${PROJECT_SOURCE_DIR}/IEEE8023_LAG_MIB_plugins.c
		${PROJECT_SOURCE_DIR}/IEEE8023_LAG_MIB_scalars.c
		${PROJECT_SOURCE_DIR}/IEEE8023_LAG_MIB_scalars_ovsdb_get.c )

add_library (${LIBLACPSNMP} SHARED ${SOURCES_SNMP})

# Installation
install(TARGETS ${LIBLACPSNMP}
        LIBRARY DESTINATION /usr/lib/snmp/plugins)

