LACP Fallback Tests
===================

## Contents

- [Fallback disabled and toggle admin flag](#fallback-disabled-and-toggle-admin-flag)
- [Fallback disabled and toggle lacp flag as active](#fallback-disabled-and-toggle-lacp-flag-as-active)
- [Fallback disabled and toggle lacp flag as passive](#fallback-disabled-and-toggle-lacp-flag-as-passive)
- [Fallback disabled with false flag and toggle admin flag](#fallback-disabled-with-false-flag-and-toggle-admin-flag)
- [Fallback disabled with false flag and toggle lacp flag as active](#fallback-disabled-with-false-flag-and-toggle-lacp-flag-as-active)
- [Fallback disabled with false flag and toggle lacp flag as passive](#fallback-disabled-with-false-flag-and-toggle-lacp-flag-as-passive)
- [Fallback enabled and toggle admin flag](#fallback-enabled-and-toggle-admin-flag)
- [Fallback enabled and toggle lacp flag as active](#fallback-enabled-and-toggle-lacp-flag-as-active)
- [Fallback enabled and toggle lacp flag as passive](#fallback-enabled-and-toggle-lacp-flag-as-passive)

## Fallback Disabled and toggle admin flag
### Objective
This test will verify fallback functionality, disabled for this test, that all
interfaces will be `Defaulted and Expired`, no interfaces will be in
`Collecting and Distributing`. For this test the **admin** flag will be toggled
from `up` to `down` and viceversa.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Disable LAG 1 on switch 1 by toggling **admin** flag to `down`
7. Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
8. Enable LAG 1 on switch 1 by toggling **admin** flag to `up`
9. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
10. Disable LAG 1 on switch 2 by toggling **admin** flag to `down`
11. Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
12. Enable LAG 1 on switch 2 by toggling **admin** flag to `up`
13. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Disabled and toggle lacp flag as active
### Objective
This test will verify fallback functionality, disabled for this test, that all
interfaces will be `Defaulted and Expired`, no interfaces will be in
`Collecting and Distributing`. For this test the **lacp** flag will be toggled
from `[] (cleared value)` to `active` and viceversa.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
7. Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
8. Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
9. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
10. Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
11. Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
12. Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
13. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Disabled and toggle lacp flag as passive
### Objective
This test will verify fallback functionality, disabled for this test, that all
interfaces will be `Defaulted and Expired`, no interfaces will be in
`Collecting and Distributing`. For this test the **lacp** flag will be toggled
from `[] (cleared value)` to `passive` and viceversa.

**Note**: Both switches cannot be in lacp mode `passive`, it will break the
connectivity and the daemon will manage as if there is no partner connected.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
7. Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
8. Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
9. Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
10. Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
11. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
12. Toggle LAG 1 **lacp** flag on switch 1 to be `passive`
13. Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
14. Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
15. Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
16. Toggle LAG 1 **lacp** flag on switch 1 to be `active`
17. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Disabled with false flag and toggle admin flag
### Objective
This test will verify fallback functionality, disabled for this test, that all
interfaces will be `Defaulted and Expired`, no interfaces will be in
`Collecting and Distributing`. For this test there will be set the
`lacp-fallback-ab` flag to `false` and the **admin** flag will be toggled from
`up` to `down` and viceversa.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Configure LAG 1 on both switches to set `other_config:lacp-fallback-ab` flag
to `false`
7. Disable LAG 1 on switch 1 by toggling **admin** flag to `down`
8. Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
9. Enable LAG 1 on switch 1 by toggling **admin** flag to `up`
10. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
11. Disable LAG 1 on switch 2 by toggling **admin** flag to `down`
12. Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
13. Enable LAG 1 on switch 2 by toggling **admin** flag to `up`
14. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Disabled with false flag and toggle lacp flag as active
### Objective
This test will verify fallback functionality, disabled for this test, that all
interfaces will be `Defaulted and Expired`, no interfaces will be in
`Collecting and Distributing`. For this test there will be set the
`lacp-fallback-ab` flag to `false` and the **lacp** flag will be toggled from
`[] (cleared value)` to `active` and viceversa.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Configure LAG 1 on both switches to set `other_config:lacp-fallback-ab` flag
to `false`
7. Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
8. Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
9. Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
10. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
11. Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
12. Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
13. Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
14. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Disabled with false flag and toggle lacp flag as passive
### Objective
This test will verify fallback functionality, disabled for this test, that all
interfaces will be `Defaulted and Expired`, no interfaces will be in
`Collecting and Distributing`. For this test there will be set the
`lacp-fallback-ab` flag to `false` and the **lacp** flag will be toggled from
`[] (cleared value)` to `passive` and viceversa.

**Note**: Both switches cannot be in lacp mode `passive`, it will break the
connectivity and the daemon will manage as if there is no partner connected.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Configure LAG 1 on both switches to set `other_config:lacp-fallback-ab` flag
to `false`
7. Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
8. Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
9. Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
10. Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
11. Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
12. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
13. Toggle LAG 1 **lacp** flag on switch 1 to be `passive`
14. Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
15. Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
16. Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
17. Toggle LAG 1 **lacp** flag on switch 1 to be `active`
18. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Enabled and toggle admin flag
### Objective
This test will verify fallback functionality, enabled for this test, will have
one interface that must be in 'Collecting and Distributing' and other LAG
interfaces will be `Defaulted`. For this test the **admin** flag will be
toggled from `up` to `down` and viceversa.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Enable LAG 1 Fallback on both switches
7. Disable LAG 1 on switch 1 by toggling **admin** flag to `down`
8. Verify that state machine from interface 1 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
9. Verify that state machine from interface 2 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
10. Enable LAG 1 on switch 1 by toggling **admin** flag to `up`
11. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
12. Disable LAG 1 on switch 2 by toggling **admin** flag to `down`
13. Verify that state machine from interface 1 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
14. Verify that state machine from interface 2 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
15. Enable LAG 1 on switch 2 by toggling **admin** flag to `up`
16. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Enabled and toggle lacp flag as active
### Objective
This test will verify fallback functionality, enabled for this test, will have
one interface that must be in 'Collecting and Distributing' and other LAG
interfaces will be `Defaulted`. For this test the **lacp** flag will be toggled
from `[] (cleared value)` to `active` and viceversa.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Enable LAG 1 Fallback on both switches
7. Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
8. Verify that state machine from interface 1 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
9. Verify that state machine from interface 2 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
10. Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
11. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
12. Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
13. Verify that state machine from interface 1 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
14. Verify that state machine from interface 2 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
15. Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
16. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.

## Fallback Enabled and toggle lacp flag as passive
### Objective
This test will verify fallback functionality, disabled for this test, that all
interfaces will be `Defaulted and Expired`, no interfaces will be in
`Collecting and Distributing`. For this test the **lacp** flag will be toggled
from `[] (cleared value)` to `passive` and viceversa.

**Note**: Both switches cannot be in lacp mode `passive`, it will break the
connectivity and the daemon will manage as if there is no partner connected.

### Requirements
- Physical/Virtual switches
- **CT File**: `ops-tests/component/test_lacpd_ct_lag_fallback.py`

### Setup
#### Topology diagram

```ditaa
            +------------+                              +------------+
            |            | 1                          1 |            |
            |            <----------------------------->             |
            |  Switch 1  |                              |  Switch 2  |
            |            |                              |            |
            |   (LAG 1)  |                              |   (LAG 1)  |
            |            <------------------------------>            |
            |            | 2                          2 |            |
            +------------+                              +------------+
```

### Description
Configure a topology with two switches, connected as shown in the
topology diagram.

1. Configure LAG 1 on switch 1 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
2. Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
3. Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
4. Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
5. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
6. Enable LAG 1 Fallback on both switches
7. Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
8. Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
9. Verify that state machine from interface 1 on switch 2 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
10. Verify that state machine from interface 2 on switch 2 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `defaulted`
11. Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
12. Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
13. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
14. Toggle LAG 1 **lacp** flag on switch 1 to be `passive`
15. Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
16. Verify that state machine from interface 1 on switch 1 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
17. Verify that state machine from interface 2 on switch 1 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `defaulted`
18. Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
19. Toggle LAG 1 **lacp** flag on switch 1 to be `active`
20. Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`

### Test result criteria
#### Test pass criteria
- All interfaces state machines on switch 1 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 2.
- All interfaces state machines on switch 2 fulfill with all the expected flags
enabled when LAG 1 is disabled on switch 1.
- All interfaces state machines fullfil with all the expected flags enabled
when both LAGs 1 are enabled on both switches.
#### Test fail criteria
- At least one interface state machine on switch 1 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 2.
- At least one interface state machine on switch 2 does not fulfill with all
the expected flags enabled when LAG 1 is disabled on switch 1.
- At least one interface state machine does not fulfill with all the expected
flags enabled when both LAGs 1 are enabled on both switches.
