# DSI Shell Script Implementation Summary

## Overview
Created shell scripts to replace the Ocelot wrapper for DSI testing, providing faster execution and easier timing configuration.

## Files Created

### 1. `scripts/run_dsi_test.sh`
- **Purpose**: Standard version that follows exact XML timing
- **Features**:
  - Direct execution of all DSI test phases
  - Follows original timing from XML files
  - Colored output for better visibility
  - Error handling and status checks
  - Command-line parameter support

### 2. `scripts/run_dsi_test_optimized.sh` (Recommended)
- **Purpose**: Enhanced version with configurable timing and better features
- **Features**:
  - All features from standard version
  - Configurable timing parameters
  - Visual countdown timers
  - Comprehensive logging with timestamps
  - Fast mode (50% time reduction)
  - Progress tracking
  - Automatic log file generation
  - Better error reporting

### 3. `scripts/launch_dsi_test.sh`
- **Purpose**: Interactive menu launcher
- **Features**:
  - User-friendly menu interface
  - Pre-configured test scenarios
  - Quick launch options for common configurations
  - Custom parameter input

### 4. `scripts/README_DSI_SHELL_SCRIPTS.md`
- **Purpose**: Comprehensive documentation
- **Contents**:
  - Usage instructions
  - Command-line options reference
  - Test sequence explanation
  - Comparison with Ocelot
  - Tuning recommendations
  - Troubleshooting guide
  - Multiple examples

## How to Use

### Quick Start
```bash
cd /fs3/Ocelot/DSI/scripts

# Make scripts executable
chmod +x run_dsi_test.sh run_dsi_test_optimized.sh launch_dsi_test.sh

# Option 1: Interactive menu
./launch_dsi_test.sh

# Option 2: Direct execution (recommended)
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic ipsec

# Option 3: Standard version
./run_dsi_test.sh --phy cr --port_speed_set 25 --traffic ipsec
```

### Equivalent to Original Ocelot Command
**Original:**
```bash
ocelot --write_summary_log_file_to_stdout on \
       --flow /fs3/Ocelot/DSI/flows/DSI_TTR_B0.xml \
       --vars phy=cr port_speed_set=25 traffic=ipsec \
              linerate_traffic=65 linerate_snake=0 linerate_port2x=65 \
       --ituff on
```

**New:**
```bash
./run_dsi_test_optimized.sh --phy cr --port_speed_set 25 --traffic ipsec \
                            --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65
```

## Test Sequence Implementation

### Phase 0: Dynamic Variables
- Calls `traffic_select.py` to get traffic type parameter
- Calls `port_speed_select.py` to get port speed parameter  
- Calls `phy_type_select.py` to get PHY type parameter

### Phase 1: Port Setup (from DSI_Port_Setup.xml)
1. `copy_conf.py -tt 'inline'` - Copy configuration
2. `/home/NAC/rdk/util/rmNAC.sh` - Unload driver
3. `/home/NAC/rdk/util/loadNAC.sh` - Load driver

### Phase 2: Delay (from DSI_Delay.xml)
- `run_delay.py -tdelay $DELAYS` - Execute delay

### Phase 3: TTR B0 Test (from DSI_TTR_B0.xml)
1. Launch `cli_master_process.py` in background
2. Setup hugepages
3. Launch DSI test application with dynamic parameters
4. For each quad (0, 4, 8, 12, 16):
   - Move to quad position (x4, x8, x12, x16)
   - Start inline traffic (echo "sa")
   - Wait for stabilization
   - Read port rate using `cli_processing_TTR.py`
5. Stop traffic (echo "ta")
6. Exit application (echo "e")
7. Kill processes using `process_kill.py`

### Phase 4: Validation
- Process ITUFF logs using `DSI_sd.py` for each quad
- Validate rates using `rate_validate_TTR.py` for each quad

## Timing Configuration

### Default Timing (matches XML)
- Initial wait: 25 seconds
- SA wait: 5 seconds
- Quad transition: 10 seconds
- Stop wait: 10 seconds
- Exit wait: 10 seconds
- Cleanup wait: 10 seconds
- **Total time**: ~160 seconds

### Fast Mode (--fast)
- Initial wait: 15 seconds (-40%)
- SA wait: 3 seconds (-40%)
- Quad transition: 5 seconds (-50%)
- Stop wait: 5 seconds (-50%)
- Exit wait: 5 seconds (-50%)
- Cleanup wait: 5 seconds (-50%)
- **Total time**: ~90 seconds

### Custom Timing
All timing parameters can be individually configured:
```bash
./run_dsi_test_optimized.sh --initial_wait 20 --sa_wait 4 --quad_wait 8
```

## Advantages Over Ocelot Wrapper

1. **Performance**:
   - No wrapper overhead
   - Direct bash execution
   - Faster startup and teardown
   - Fast mode reduces time by ~44%

2. **Flexibility**:
   - Easy timing adjustments without XML modification
   - Command-line control of all parameters
   - Can tune timing per deployment

3. **Visibility**:
   - Real-time progress with countdowns
   - Colored output for easy reading
   - Detailed logging to file
   - Better error messages

4. **Maintainability**:
   - Simpler to understand and modify
   - No need to manually tune XML delays
   - Can version control timing presets
   - Easy to debug

5. **Usability**:
   - Interactive launcher option
   - Help system built-in
   - Pre-configured test scenarios
   - Comprehensive documentation

## Testing Recommendations

1. **Initial Test**: Run with default timing to establish baseline
   ```bash
   ./run_dsi_test_optimized.sh
   ```

2. **Speed Test**: Try fast mode to see if it works on your hardware
   ```bash
   ./run_dsi_test_optimized.sh --fast
   ```

3. **Fine-tune**: Adjust individual parameters if needed
   ```bash
   ./run_dsi_test_optimized.sh --initial_wait 18 --sa_wait 4
   ```

4. **Monitor**: Check logs for any timing-related failures
   ```bash
   tail -f /fs3/Ocelot/DSI/bin/dsi_test_*.log
   tail -f /fs3/Ocelot/DSI/bin/dsi_app.log
   ```

## Output Files

All output files are created in `/fs3/Ocelot/DSI/bin/`:
- `dsi_test_YYYYMMDD_HHMMSS.log` - Complete test log (optimized version)
- `dsi_app.log` - DSI application output
- `ituff_logging_quad0.txt` through `ituff_logging_quad16.txt` - ITUFF logs
- `EHM_port_status*.txt` - Port status files

## Notes

- Scripts are designed to be run from the `scripts` directory
- All paths are calculated relative to script location
- Original XML files are not modified
- Can be used alongside Ocelot wrapper (not simultaneously)
- Compatible with existing Python scripts and utilities

## Future Enhancements (Optional)

Consider adding:
1. Parallel execution for validation phase
2. Automatic retry on failures
3. Performance metrics collection
4. Email notifications on completion
5. Integration with test management systems
6. Support for additional test flows (DSI_Delay, other XMLs)

## Compatibility

- **Shell**: Bash 4.0+
- **Python**: 2.7+ or 3.x (configurable via --python)
- **OS**: Linux (tested on target platform)
- **Dependencies**: All existing DSI Python scripts and utilities

## Support

For issues:
1. Check `README_DSI_SHELL_SCRIPTS.md` for detailed help
2. Review log files in `/fs3/Ocelot/DSI/bin/`
3. Use `--help` flag for usage information
4. Verify all prerequisite scripts are available
