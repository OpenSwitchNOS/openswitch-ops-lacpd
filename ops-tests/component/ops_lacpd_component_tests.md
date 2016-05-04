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
- [LACP fallback mode CLI commands](#lacp-fallback-mode-CLI-commands)
- [LACP fallback timeout CLI commands](#lacp-fallback-timeout-CLI-commands)

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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 1 by toggling **admin** flag to `down`
* Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 1 by toggling **admin** flag to `up`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 2 by toggling **admin** flag to `down`
* Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 2 by toggling **admin** flag to `up`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
* Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
* Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Toggle LAG 1 **lacp** flag on switch 1 to be `passive`
* Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
* Toggle LAG 1 **lacp** flag on switch 1 to be `active`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Configure LAG 1 on both switches to set `other_config:lacp-fallback-ab` flag
to `false`
* Disable LAG 1 on switch 1 by toggling **admin** flag to `down`
* Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 1 by toggling **admin** flag to `up`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 2 by toggling **admin** flag to `down`
* Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 2 by toggling **admin** flag to `up`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Configure LAG 1 on both switches to set `other_config:lacp-fallback-ab` flag
to `false`
* Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Configure LAG 1 on both switches to set `other_config:lacp-fallback-ab` flag
to `false`
* Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
* Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 2 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
* Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Toggle LAG 1 **lacp** flag on switch 1 to be `passive`
* Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
* Verify that all state machines from interface 1 and 2 on switch 1 have the
following flags enabled
    * `aggregable`
    * `defaulted`
    * `expired`
* Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
* Toggle LAG 1 **lacp** flag on switch 1 to be `active`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Enable LAG 1 Fallback on both switches
* Disable LAG 1 on switch 1 by toggling **admin** flag to `down`
* Verify that state machine from interface 1 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
* Verify that state machine from interface 2 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
* Enable LAG 1 on switch 1 by toggling **admin** flag to `up`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 2 by toggling **admin** flag to `down`
* Verify that state machine from interface 1 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
* Verify that state machine from interface 2 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
* Enable LAG 1 on switch 2 by toggling **admin** flag to `up`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Enable LAG 1 Fallback on both switches
* Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
* Verify that state machine from interface 1 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
* Verify that state machine from interface 2 on switch 2 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
* Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
* Verify that state machine from interface 1 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
* Verify that state machine from interface 2 on switch 1 has the following
flags enabled
    * `active`
    * `aggregable`
    * `defaulted`
* Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
* Verify that all state machines from interface 1 and 2 on both switches have
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
* Configure LAG 1 on switch 2 with the following values
    * **lacp** `active`
    * **other_config:lacp-time** `fast`
    * **hw_config:enable** `true`
* Configure interfaces 1 and 2 on switch 1 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Configure interfaces 1 and 2 on switch 2 with the following values
    * **user_config:admin** `up`
    * **other_config:lacp-aggregation-key** `1`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Enable LAG 1 Fallback on both switches
* Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
* Disable LAG 1 on switch 1 by toggling **lacp** flag to `off`
* Verify that state machine from interface 1 on switch 2 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
* Verify that state machine from interface 2 on switch 2 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `defaulted`
* Enable LAG 1 on switch 1 by toggling **lacp** flag to `active`
* Toggle LAG 1 **lacp** flag on switch 2 to be `passive`
* Verify that all state machines from interface 1 and 2 on both switches have
this flags enabled
    * `active`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
* Toggle LAG 1 **lacp** flag on switch 1 to be `passive`
* Disable LAG 1 on switch 2 by toggling **lacp** flag to `off`
* Verify that state machine from interface 1 on switch 1 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `in-sync`
    * `collecting`
    * `distributing`
    * `defaulted`
* Verify that state machine from interface 2 on switch 1 has the following
flags enabled
    * `passive`
    * `aggregable`
    * `defaulted`
* Enable LAG 1 on switch 2 by toggling **lacp** flag to `active`
* Toggle LAG 1 **lacp** flag on switch 1 to be `active`
* Verify that all state machines from interface 1 and 2 on both switches have
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


# LACP fallback mode CLI commands
### Objective
Verify LACP fallback mode CLI commands set ovsdb lacp_fallback_mode value
properly.
Verify LACP fallback mode is contained in the otuput of "show running-config"
and "show lacp aggregates".
properly.
### Requirements
 - Modular framework
 - Script is in ops-tests/component/test_lacp_ct_vtysh_fallback_mode.py

### Setup
#### Topology Diagram
```
+------------+
|            |
|     s1     |
|            |
+------------+
```

### Description
1. Create one dynamic LAG in the switch.
*  Check the lacp_fallback_mode for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "lacp fallback mode all_active".
*  Check the lacp_fallback_mode for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "lacp fallback mode priority".
*  Check the lacp_fallback_mode for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "lacp fallback mode all_active".
*  Check the lacp_fallback_mode for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "no lacp fallback mode all_active".
*  Check the lacp_fallback_mode for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "lacp fallback mode all_active".
*  Check the lacp_fallback_mode for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "lacp fallback mode priority".
*  Check the lacp_fallback_mode for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'

### Test Result Criteria
#### Test Pass Criteria
- Initial lacp_fallback_mode value is empty.
- When fallback mode is configured as all_active, lacp_fallback_mode value is
  "all_active".
- When fallback mode is configured as priority or no all_active,
  lacp_fallback_mode value is empty.
- The output of 'show lacp aggregates' shows the correct fallback mode
  configuration (priority or all_active).
- When fallback mode is configured as all_active, the output of
  "show running-config" contains "lacp fallback mode all_active".
- When fallback mode is configured as priority, the output of
  "show running-config" does not contain "lacp fallback mode".
#### Test Fail Criteria
- Initial lacp_fallback_mode value is not empty.
- When fallback mode is configured as all_active, lacp_fallback_mode value is
  not "all_active".
- When fallback mode is configured as priority or no all_active,
  lacp_fallback_mode value is not empty.
- The output of 'show lacp aggregates' shows incorrect fallback mode
  configuration (priority or all_active).
- When fallback mode is configured as all_active, the output of
  "show running-config" does not contain "lacp fallback mode all_active".
- When fallback mode is configured as priority, the output of
  "show running-config" contains "lacp fallback mode".


# LACP fallback timeout CLI commands
### Objective
Verify LACP fallback timeout CLI commands set ovsdb lacp_fallback_timeout value
properly.
Verify LACP fallback timeout is contained in the otuput of
"show running-config" and "show lacp aggregates".
### Requirements
 - Modular framework
 - Script is in ops-tests/component/test_lacp_ct_vtysh_fallback_timeout.py

### Setup
#### Topology Diagram
```
+------------+
|            |
|     s1     |
|            |
+------------+
```

### Description
1. Create one dynamic LAG in the switch.
*  Check the lacp_fallback_timeout for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "lacp_fallback_timeout" with these valid values:
   1, 500 and 900.
*  Check the lacp_fallback_timeout for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "lacp_fallback_timeout" with these invalid values:
   0, 901, 'a' and 'string'.
*  Check the lacp_fallback_timeout for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "no lacp_fallback_timeout" with these invalid values:
   0, 901, 'a' and 'string'.
*  Check the lacp_fallback_timeout for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "no lacp_fallback_timeout 2".
*  Check the lacp_fallback_timeout for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'
*  Execute CLI command "no lacp_fallback_timeout" with the configured value.
*  Check the lacp_fallback_timeout for the LAG.
*  Check the output of 'show lacp aggregates' and 'show running-config'

### Test Result Criteria
#### Test Pass Criteria
- Initial lacp_fallback_timeout value is empty.
- When fallback timeout is configured with some value between 1 and 900,
  lacp_fallback_timeout value is set to the configured value.
- It is not allowed to configure fallback timeout to any of these values: 0,
  901, 'a', 'string'.
- It is not allowed to run "no lacp fallback timeout <value>" with a different
  value than the one already configured.
- When "no lacp fallback timeout <value>" is executed with the configured
  value, lacp_fallback_timeout value is empty.
- The output of 'show lacp aggregates' shows the configured fallback timeout
  value (default value is zero).
- When fallback timeout is different than zero, the output of
  "show running-config" contains "lacp fallback timeout <configured_value>".
- When fallback timeout is zero, the output of "show running-config" does not
  contain "lacp fallback timeout".
#### Test Fail Criteria
- Initial lacp_fallback_timeout value is not empty.
- When fallback timeout is configured as some value between 1 and 900,
  lacp_fallback_timeout value is not set to the configured value.
- It is allowed to configure fallback timeout to any of these values: 0, 901,
  'a', 'string'.
- It is allowed to run "no lacp fallback timeout <value>" with a different
  value than the one already configured.
- When "no lacp fallback timeout <value>" is executed with the configured
  value, lacp_fallback_timeout value is not empty.
- The output of 'show lacp aggregates' does not show the configured fallback
  timeout value (default value is not zero).
- When fallback timeout is different than zero, the output of
  "show running-config" does not contain "lacp fallback timeout <configured_value>".
- When fallback timeout is zero, the output of "show running-config" contains
  "lacp fallback timeout".
