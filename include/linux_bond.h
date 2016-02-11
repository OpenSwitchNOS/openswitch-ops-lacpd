/*
 * (c) Copyright 2016 Hewlett Packard Enterprise Development LP
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

#ifndef _LINUX_BOND_H_
#define _LINUX_BOND_H_

#define SWNS_EXEC "/sbin/ip netns exec swns"

void load_bonding_driver();
void delete_linux_bond(char* bond_name);
void create_linux_bond(char* bond_name);
void add_slave_to_bond(char* bond_name, char* slave_name);
void remove_slave_from_bond(char* bond_name, char* slave_name);
void set_linux_bond_up(char* bond_name);
void set_slave_interface_down(char* slave_name);
void set_slave_interface_up(char* slave_name);

#endif /* _LINUX_BOND_H_ */
