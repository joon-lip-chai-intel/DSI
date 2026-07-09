# DSI Test Script - Phase 4 Error Fix

## Problem
The script was showing errors during ITUFF processing in Phase 4:
```
Error: ITUFF processing for Quad 0
Error: ITUFF processing for Quad 4
...
```

## Root Cause
The `DSI_sd.py` script requires **3 command-line arguments**:
1. Test name (e.g., "DSI_Tests")
2. Raw datalog input file path (e.g., `/fs3/Ocelot/DSI/bin/ituff_logging_quad0.txt`)
3. Structured datalog output file path (e.g., `/fs3/Ocelot/DSI/bin/ituff_logging_quad0_structured.xml`)

The original script was only passing 1 argument (the input file).

## Solution Applied
Updated the `validate_quad()` function to call `DSI_sd.py` with all required arguments:

**Before:**
```bash
$PYTHON_CMD $SCRIPT_DIR/DSI_sd.py $BIN_DIR/ituff_logging_quad$quad_num.txt >> "$LOG_FILE" 2>&1
```

**After:**
```bash
$PYTHON_CMD $SCRIPT_DIR/DSI_sd.py "DSI_Tests" "$BIN_DIR/ituff_logging_quad$quad_num.txt" "$BIN_DIR/ituff_logging_quad${quad_num}_structured.xml" >> "$LOG_FILE" 2>&1
```

## Expected Result
After running the script again, Phase 4 should now show:
```
===============================================================================
PHASE 4: Log Validation and Rate Validation
===============================================================================
>>> Validating Quad 0 logs...
Success: ITUFF processing for Quad 0
Success: Rate validation for Quad 0
>>> Validating Quad 4 logs...
Success: ITUFF processing for Quad 4
Success: Rate validation for Quad 4
...
```

## New Output Files
The script now generates structured XML files in addition to the raw ITUFF logs:
- `ituff_logging_quad0_structured.xml`
- `ituff_logging_quad4_structured.xml`
- `ituff_logging_quad8_structured.xml`
- `ituff_logging_quad12_structured.xml`
- `ituff_logging_quad16_structured.xml`

These XML files contain the parsed ITUFF data in a structured format.

## Testing
To test the fix, run the script again:
```bash
cd /fs3/Ocelot/DSI/scripts
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic ipsec
```

Check the log file for ITUFF processing success messages and verify the structured XML files are created in the `bin/` directory.
