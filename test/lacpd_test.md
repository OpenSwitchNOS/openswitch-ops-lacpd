# lacpd Test Cases

## Static LAG membership
### Objective
Verify that the configured interfaces are included or excluded from a static LAG depending on their link status.
### Requirements
Add the Python script where this test is implemented. This applies to all test cases in this document.
### Setup
#### Topology diagram
```
[h1] <--> [s1] <--> [s2] <--> [h2]
```
### Description ###
1. Create LAGs with 1 Gb, 10 Gb, and 40 Gb interfaces. Verify that the interfaces are not operating in LAGs (because they are not enabled).
2. Enable all the interfaces. Verify that interfaces are operating in LAGs (because they have been enabled and are linked).
3. Remove an interface from a LAG. Verify that removed interface is not operating in LAG (because it has been removed from configuration).
4. Add the interface back into the LAG. Verify that the added interface is operating inside of the LAG.
5. Remove all but two interfaces from a LAG. Confirm that the remaining interfaces are still in the LAG. Verify that the removed inerface are not in the LAG.
6. Disable one of two interfaces in the LAG. Verify that removed interface is not in the LAG.
7. Enable an interface in the LAG. Confirm that the interface is in the LAG.
8. Clear all user configurations.
### Test result criteria
#### Test pass criteria
All verifications succeed.
#### Test fail criteria
One or more verifications fail.

## Static LAG membership exclusion rules
### Objective
Verify that interfaces that violate one or more LAG exclusion rules do not operate in LAGs.
### Requirements
The Virtual Mininet test setup is required for this test.
### Setup
#### Topology diagram
```
[h1] <--> [s1] <--> [s2] <--> [h2]
```
### Description
1. Enable 1 Gb and 10 Gb interfaces.
2. Create a LAG with 1 Gb interfaces.
3. Add 10 Gb interfaces to the LAG. Verify that the 1 Gb interfaces are operating in the LAG. Confirm that 10 Gb interfaces are not operating in the LAG (mismatched speed).
4. Remove 1 Gb interfaces from the LAG. Verify that the 10 Gb interfaces are operating in the LAG (no 1 Gb links remain).
5. Clear all user configurations.
### Test result criteria
#### Test pass criteria
All verifications succeed.
#### Test fail criteria
One or more verifications fail.

## LACP user configuration
### Objective
Verify that the lacpd is processing the LACP configuration and the protocol correctly.
### Requirements
 - Virtual mininet test setup
### Setup
#### Topology diagram
```
[h1] <--> [s1] <--> [s2] <--> [h2]
```
### Description
1. Access system\_mac (system:system\_mac) for s1 and s2.
2. Create a LACP LAG on s1 and s2 (connected interfaces). Verify that the lacp\_status in interfaces configured with LACP LAGs are formed and are using the default system\_mac values.
3. Override system parameters on s1 and s2 (set system:lacp\_config lacp-system-id and lacp-system-priority). Confirm that LAGs are formed and are using newly specified [system] override values in lacp\_status for interfaces configued in LACP.
4. Set port:other\_config lacp-system-id and lacp-system-priority to supercede the system-level override. Verify that the LAGs are formed and are using newly specified [port] override values in lacp\_status, for interfaces configured in LACP.
5. Delete and recreate LACP LAG on s1 and s2. Confirm that the LAGs are formed and are using [system] override values in lacp\_status for interfaces configured in LACP.
6. Delete all the LAGs.
7. Create a LACP LAG on s1 and s2 using 1 Gb interfaces.
   Verify that the interfaces are linked and operating at 1 Gb.
   Confirm that the interfaces are operating in the LAG.
8. Override the 'set system:lacp\_config lacp-system-id' and 'lacp-system-priority' system parameters on s1. Verify that system-level overrides are used in the interfaces.
9. Clear the system parameters on s1. Verify that the default values for system id and system priority are used in interfaces.
10. Set invalid system:lacp\_config values. Confirm that the invalid values are ignored.
11. Change LACP in port from "active" to "passive". Verify that the interface:lacp\_status actor\_state has an Active: field parameter of 0.
12. Change LACP in the port from "passive" to "off". Ensure that the interface:lacp\_status actor\_state parameter is empty (LACP is disabled).
13. Change LACP in the port from "off" to "active". Verify that interface:lacp\_status has an Active field of 1.
14. Set the port:other\_config lacp-timer to "slow". Confirm that the TmOut in the interface:actor\_state is set to 0.
15. Set the port:other\_config lacp-timer to "fast". Ensure that the TmOut in the interface:actor\_state is set to 1.
16. Set interface:other\_config lacp-port-id and lacp-port-priority parameters. Verify that the interface:lacp\_status actor\_port\_id uses new values.
17. Set the interface:other\_config lacp-port-id and lacp-port-priority to invalid values.Confirm that interface:lacp\_status actor\_port\_id parameters uses default values and ignores invalid values.
18. Remove the interface:other\_config lacp-port-id and lacp-port-priority values. Ensure that the interface:lacp\_status actor\_port\_id uses default values. Verify that the port:lacp\_status bond\_speed is 1000 and bond\_status is "ok". Confirm that the interface:lacp\_status values are correct.
19. Set system:lacp\_config lacp-system-id and lacp-system-priority. Verify that interfaces are using system-level overrides.
20. Create a new LAG (lag1) on s2.
21. Enable interfaces in lag1. Verify that the interface:lacp\_status values in lag1 are using system-level overrides.
22. Set lag0:other\_config lacp-system-id and lacp-system-priority. Confirm that the lag0 interfaces are using port-level overrides. Ensure that lag1 interfaces are using system-level overrides.
23. Add an interface to lag0. Verify that the added interface is using port-level overrides.
24. Clear port-level overrides from lag0. Verify that the lag0 interfaces are using system-level overrides.
### Test result criteria
#### Test pass criteria
All verifications succeed.
#### Test fail criteria
One or more verifications fail.
