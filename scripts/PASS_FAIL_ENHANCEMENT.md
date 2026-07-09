# DSI Test Script - Pass/Fail Display Enhancement

## Overview
Enhanced the DSI test script to display clear **PASS/FAIL** status for each quad validation, matching the ocelot wrapper's behavior.

## What Was Added

### 1. Pass/Fail Tracking
- **Test counters**: Tracks total tests, passed tests, and failed tests
- **Exit code checking**: Captures the exit code from `rate_validate_TTR.py`
  - Exit code 0 = PASS
  - Exit code 1 = FAIL

### 2. Enhanced Output Display

#### During Phase 4 Validation
For each quad, the script now shows:

**When PASSED:**
```
>>> Validating Quad 0 logs...
Success: ITUFF processing for Quad 0
? PASSED: Rate validation for Quad 0
  The linerate for Quad0 is above 95% for clear traffic and test Passed.
    ITUFF Data for Quad 0:
    LIMIT_LINERATE: 95:95:95:95:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:95:0:0
    READ_LINERATE:  100.0:100.0:100.0:100.0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:100.0:0.0:0.0
```

**When FAILED:**
```
>>> Validating Quad 4 logs...
Success: ITUFF processing for Quad 4
? FAILED: Rate validation for Quad 4
  The linerate for Quad4 is below the threshold level of 95% and test Failed.
    ITUFF Data for Quad 4:
    LIMIT_LINERATE: 0:0:0:0:95:95:95:95:0:0:0:0:0:0:0:0:0:0:0:0:95:0:0
    READ_LINERATE:  0:0:0:0:85.5:87.2:89.3:90.1:0:0:0:0:0:0:0:0:0:0:0:0:88.0:0.0:0.0
```

#### Final Summary
At the end of the test, a comprehensive summary is displayed:

**When All Tests Pass:**
```
===============================================================================
                         TEST RESULTS
===============================================================================

Configuration:
  PHY Type:          cr
  Port Speed:        25G
  Traffic Type:      clear
  Line Rate Traffic: 95%

Test Results by Quad:
  Total Quads Tested: 5
  Passed: 5
  Failed: 0

??????????????????????????????????????????
?     OVERALL RESULT: ? PASSED          ?
??????????????????????????????????????????

===============================================================================
Phases Executed:
  1. DSI Port Setup
  2. DSI Delay (20 seconds)
  3. DSI TTR B0 Test (5 quads: 0, 4, 8, 12, 16)
  4. Log Validation and Rate Validation

Output files:
  Test log:        /fs3/Ocelot/DSI/bin/dsi_test_20180318_062148.log
  Application log: /fs3/Ocelot/DSI/bin/dsi_app.log
  ITUFF logs:      /fs3/Ocelot/DSI/bin/ituff_logging_quad*.txt
  ITUFF XML:       /fs3/Ocelot/DSI/bin/ituff_logging_quad*_structured.xml
===============================================================================

Ocelot Main: Result=SUCCESS Time: 161
```

**When Any Test Fails:**
```
Test Results by Quad:
  Total Quads Tested: 5
  Passed: 3
  Failed: 2

??????????????????????????????????????????
?     OVERALL RESULT: ? FAILED          ?
??????????????????????????????????????????

Ocelot Main: Result=FAILED Time: 161
```

### 3. ITUFF Data Display
The script now shows the comparison data inline during validation:
- **LIMIT_LINERATE**: Expected threshold values (from test configuration)
- **READ_LINERATE**: Actual measured values (from hardware)

This matches the ocelot output format:
```xml
<ITUFF name="DSI_CR_CLEAR_25G_QUAD_0">
    <LIMIT_LINERATE>95:95:95:95:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:95:0:0</LIMIT_LINERATE>
    <READ_LINERATE>100.0:100.0:100.0:100.0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:100.0:0.0:0.0</READ_LINERATE>
</ITUFF>
```

### 4. Exit Code
The script now exits with the correct status:
- **Exit 0**: All tests passed (SUCCESS)
- **Exit 1**: One or more tests failed (FAILED)

This allows integration with automation systems and CI/CD pipelines.

## How Pass/Fail is Determined

The `rate_validate_TTR.py` script compares:
1. **READ_LINERATE** (actual measured rates) 
2. **LIMIT_LINERATE** (expected threshold rates)

**Pass Criteria**: All measured rates must be ? threshold rates

**Example:**
```
Port 0: READ=100.0%, LIMIT=95% ? ? PASS (100.0 >= 95)
Port 1: READ=100.0%, LIMIT=95% ? ? PASS (100.0 >= 95)
Port 2: READ=100.0%, LIMIT=95% ? ? PASS (100.0 >= 95)
Port 3: READ=100.0%, LIMIT=95% ? ? PASS (100.0 >= 95)
Port 20: READ=100.0%, LIMIT=95% ? ? PASS (100.0 >= 95)

Result: QUAD 0 PASSED (all ports meet threshold)
```

## Color Coding

- ?? **Green**: PASSED tests and success messages
- ?? **Red**: FAILED tests and error messages
- ?? **Blue**: Informational messages (ITUFF data, timing info)
- ?? **Yellow**: Warnings (missing files, ignored errors)

## Comparison with Ocelot

### Ocelot Output
```
Ocelot Main: Result=SUCCESS Time: 160.95
================= Start ITUFF Output ===================
<ITUFF name="DSI_CR_CLEAR_25G_QUAD_0">
    <LIMIT_LINERATE>95:95:95:95:...</LIMIT_LINERATE>
    <READ_LINERATE>100.0:100.0:100.0:100.0:...</READ_LINERATE>
</ITUFF>
================= End ITUFF Output ===============
```

### Shell Script Output
```
? PASSED: Rate validation for Quad 0
  The linerate for Quad0 is above 95% for clear traffic and test Passed.
  ITUFF Data for Quad 0:
    LIMIT_LINERATE: 95:95:95:95:...
    READ_LINERATE:  100.0:100.0:100.0:100.0:...

??????????????????????????????????????????
?     OVERALL RESULT: ? PASSED          ?
??????????????????????????????????????????

Ocelot Main: Result=SUCCESS Time: 161
```

## Benefits

1. **Clear visibility**: Immediately see which quads passed/failed
2. **Detailed feedback**: Shows actual vs expected values
3. **Automation friendly**: Proper exit codes for scripting
4. **Ocelot compatible**: Similar output format and terminology
5. **Better debugging**: ITUFF data displayed inline for quick analysis

## Testing

Run the script to verify the new output:
```bash
cd /fs3/Ocelot/DSI/scripts
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic clear --linerate_traffic 95
```

Check for:
- ?/? symbols for pass/fail
- ITUFF data display for each quad
- Overall result summary box
- Correct exit code (`echo $?` after script finishes)
