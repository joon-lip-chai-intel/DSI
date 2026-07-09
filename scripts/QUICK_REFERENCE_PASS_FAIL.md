# Quick Reference: DSI Test Script Pass/Fail Output

## Sample Output - All Tests Passing

```bash
===============================================================================
PHASE 4: Log Validation and Rate Validation
===============================================================================
>>> Validating Quad 0 logs...
Success: ITUFF processing for Quad 0
? PASSED: Rate validation for Quad 0
  The linerate for Quad0 is above 95% for clear traffic and test Passed.
    ITUFF Data for Quad 0:
    LIMIT_LINERATE: 95:95:95:95:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:95:0:0
    READ_LINERATE:  100.0:100.0:100.0:100.0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:100.0:0.0:0.0

>>> Validating Quad 4 logs...
Success: ITUFF processing for Quad 4
? PASSED: Rate validation for Quad 4
  The linerate for Quad4 is above 95% for clear traffic and test Passed.
    ITUFF Data for Quad 4:
    LIMIT_LINERATE: 0:0:0:0:95:95:95:95:0:0:0:0:0:0:0:0:0:0:0:0:95:0:0
    READ_LINERATE:  0:0:0:0:100.0:100.0:100.0:100.0:0:0:0:0:0:0:0:0:0:0:0:0:100.0:0.0:0.0

>>> Validating Quad 8 logs...
Success: ITUFF processing for Quad 8
? PASSED: Rate validation for Quad 8
  The linerate for Quad8 is above 95% for clear traffic and test Passed.
    ITUFF Data for Quad 8:
    LIMIT_LINERATE: 0:0:0:0:0:0:0:0:95:95:95:95:0:0:0:0:0:0:0:0:95:0:0
    READ_LINERATE:  0:0:0:0:0:0:0:0:100.0:100.0:100.0:100.0:0:0:0:0:0:0:0:0:100.0:0.0:0.0

>>> Validating Quad 12 logs...
Success: ITUFF processing for Quad 12
? PASSED: Rate validation for Quad 12
  The linerate for Quad12 is above 95% for clear traffic and test Passed.
    ITUFF Data for Quad 12:
    LIMIT_LINERATE: 0:0:0:0:0:0:0:0:0:0:0:0:95:95:95:95:0:0:0:0:95:0:0
    READ_LINERATE:  0:0:0:0:0:0:0:0:0:0:0:0:100.0:100.0:100.0:100.0:0:0:0:0:100.0:0.0:0.0

>>> Validating Quad 16 logs...
Success: ITUFF processing for Quad 16
? PASSED: Rate validation for Quad 16
  The linerate for Quad16 is above 95% for clear traffic and test Passed.
    ITUFF Data for Quad 16:
    LIMIT_LINERATE: 0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:95:95:95:95:95:0:0
    READ_LINERATE:  0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:100.0:100.0:100.0:100.0:100.0:0.0:0.0

===============================================================================
Test Execution Summary
===============================================================================

================================================================================
                         TEST RESULTS
================================================================================

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

================================================================================
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
================================================================================

Ocelot Main: Result=SUCCESS Time: 161
```

## Key Indicators

### ? Test Passed
- Green checkmark ?
- Message: "The linerate for QuadX is above Y% for Z traffic and test Passed."
- All READ_LINERATE values ? LIMIT_LINERATE values

### ? Test Failed
- Red X mark ?
- Message: "The linerate for QuadX is below the threshold level of Y% and test Failed."
- One or more READ_LINERATE values < LIMIT_LINERATE values

## Exit Codes

- **0**: All tests passed ? SUCCESS
- **1**: One or more tests failed ? FAILED

Check exit code after script completes:
```bash
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic clear
echo "Exit code: $?"
```

## Understanding ITUFF Data

The ITUFF output shows colon-separated values for each port:

```
LIMIT_LINERATE: 95:95:95:95:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:95:0:0
                ?  ?  ?  ?  ?? Ports 4-19 (not active for this quad)
                ?  ?  ?  ????? Port 3 (95% required)
                ?  ?  ???????? Port 2 (95% required)
                ?  ??????????? Port 1 (95% required)
                ?????????????? Port 0 (95% required)

READ_LINERATE:  100.0:100.0:100.0:100.0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:100.0:0.0:0.0
                ?     ?     ?     ?     ?? Ports 4-19 (not measured)
                ?     ?     ?     ????????? Port 3 (100.0% measured) ?
                ?     ?     ??????????????? Port 2 (100.0% measured) ?
                ?     ????????????????????? Port 1 (100.0% measured) ?
                ??????????????????????????? Port 0 (100.0% measured) ?
```

**Pass Criteria**: For each active port, READ ? LIMIT

## Port Mapping

```
Quad  0: Ports  0- 3
Quad  4: Ports  4- 7
Quad  8: Ports  8-11
Quad 12: Ports 12-15
Quad 16: Ports 16-19
CPK:     Port  20
CPM:     Ports 21-22
```

## Color Legend

?? **Green**: Success, passed tests
?? **Red**: Failure, failed tests
?? **Blue**: Information, data display
?? **Yellow**: Warnings

## Automation Integration

Use in scripts:
```bash
#!/bin/bash
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic clear

if [ $? -eq 0 ]; then
    echo "All DSI tests passed!"
    # Continue with next step
else
    echo "DSI tests failed!"
    exit 1
fi
```

## Comparison: Ocelot vs Shell Script

| Feature | Ocelot Wrapper | Shell Script |
|---------|----------------|--------------|
| Pass/Fail Display | ? (at end) | ? (per quad + summary) |
| ITUFF Data | ? (XML at end) | ? (inline per quad) |
| Exit Code | ? | ? |
| Colored Output | Limited | Full color support |
| Timing | Fixed (160s+) | Adjustable (~95-150s) |
| Real-time Feedback | Limited | Per-quad results |

Both produce equivalent results, but the shell script provides:
- Faster execution (especially with `--fast` mode)
- More detailed real-time feedback
- Better visibility into individual quad results
- Easier customization of timing parameters
