# fallback Test Cases

[TOC]

## Static LAG Membership
### Objective
Verify that configured LAG to either disable all ports or to fallback to active/backup (a single port forwarding and the other blocking) when dynamic LACP is configured and the LACP negotiation fail(due to the lack of an LACP partner).
### Requirements
 - Virtual Mininet Test Setup
### Setup
#### Topology Diagram
```
[s1] <--> [s2]
```
### Description ###
1. Create LAGs with 1 Gb interfaces.
   Verify that interfaces are not operating in LAGs (because they are not enabled)
2. Enable all the interfaces
   Verify that interfaces are operating in LAGs (because they have been enabled and are linked)
3. Create a LACP LAG on s1 and s2 (connected interfaces)
   Verify lacp\_status in interfaces configured in LACP LAGs (LAGs are formed and are using defa
4. Override port parameters on s1 and s2 (set other\_config lacp-time)
5. Verify that interfaces are linked and operating at 1 Gb
   Verify that interfaces are operating in LAG
6. Override port parameters on s1 and s2 (set other\_config lacp-fallback-ab as true)
7. Change lacp in port from "active" to "off" on s2
   Vefiry that interface 1 continue up
   Verify that interfaces were down on LAG
8. LACP back to active on s2
   Verify that interfaces are in LAG
9. Set port:other\_config lacp-fallback to "false"
10. Change lacp in port from "active" to "off" on s2
    Verify that interfaces were down on LAG
11. Clear all user configuration
### Test Result Criteria
#### Test Pass Criteria
All verifications succeed.
#### Test Fail Criteria
One or more verifications fail.
