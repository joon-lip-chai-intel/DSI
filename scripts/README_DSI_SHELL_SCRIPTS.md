# DSI Test Execution Shell Scripts

This directory contains shell scripts to execute DSI test sequences without using the Ocelot wrapper, providing faster execution and easier timing adjustments.

## Scripts Available

### 1. `run_dsi_test.sh` - Standard Version
The standard version follows the exact timing from the XML files (DSI_Port_Setup.xml > DSI_Delay.xml > DSI_TTR_B0.xml).

**Usage:**
```bash
cd /fs3/Ocelot/DSI/scripts
chmod +x run_dsi_test.sh
./run_dsi_test.sh
```

**With custom parameters:**
```bash
./run_dsi_test.sh --phy cr --port_speed_set 25 --traffic ipsec --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65
```

### 2. `run_dsi_test_optimized.sh` - Optimized Version (Recommended)
The optimized version includes:
- Configurable timing parameters
- Visual countdown timers
- Better logging with timestamps
- Fast mode option for quicker execution
- Progress tracking

**Usage:**
```bash
cd /fs3/Ocelot/DSI/scripts
chmod +x run_dsi_test_optimized.sh

# Run with default timing
./run_dsi_test_optimized.sh

# Run with custom parameters (same as Ocelot command)
./run_dsi_test_optimized.sh --phy cr --port_speed_set 25 --traffic ipsec --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65

# Run in fast mode (50% time reduction)
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic ipsec

# Fine-tune individual timing parameters
./run_dsi_test_optimized.sh --initial_wait 20 --sa_wait 3 --quad_wait 8
```

## Command Line Options

### Test Configuration
- `--phy <value>`: PHY type (default: cr)
- `--port_speed_set <value>`: Port speed - 10/25/50/100 (default: 25)
- `--traffic <value>`: Traffic type - ipsec/clear (default: ipsec)
- `--linerate_traffic <value>`: Line rate for traffic (default: 65)
- `--linerate_snake <value>`: Line rate for snake (default: 0)
- `--linerate_port2x <value>`: Line rate for port 2x (default: 65)
- `--delays <value>`: Delay in seconds (default: 20)
- `--python <cmd>`: Python command to use (default: python3)

### Timing Configuration (Optimized Version Only)
- `--initial_wait <sec>`: Wait before first SA command (default: 25)
- `--sa_wait <sec>`: Wait after SA before reading port rate (default: 5)
- `--quad_wait <sec>`: Wait between quad transitions (default: 10)
- `--stop_wait <sec>`: Wait before stopping traffic (default: 10)
- `--exit_wait <sec>`: Wait before exit (default: 10)
- `--cleanup_wait <sec>`: Wait before final cleanup (default: 10)
- `--fast`: Use faster timing preset (50% reduction on all waits)

## Test Sequence

The scripts execute the following phases:

### Phase 0: Setup Dynamic Variables
- Get traffic type parameter
- Get port speed parameter
- Get PHY type parameter

### Phase 1: DSI Port Setup
1. Copy inline configuration file
2. Unload DSI driver
3. Load DSI driver

### Phase 2: DSI Delay
- Run delay script for specified duration

### Phase 3: DSI TTR B0 Test
1. Launch CLI master process
2. Setup environment and launch DSI test application
3. Run tests for 5 quads (0, 4, 8, 12, 16):
   - Move to quad (except for quad 0)
   - Start inline traffic (SA)
   - Wait for traffic stabilization
   - Read port rate

4. Stop traffic and cleanup

### Phase 4: Log Validation
- Validate ITUFF logs for all quads
- Run rate validation for all quads

## Comparison with Ocelot Wrapper

### Ocelot Command:
```bash
ocelot --write_summary_log_file_to_stdout on \
       --flow /fs3/Ocelot/DSI/flows/DSI_TTR_B0.xml \
       --vars phy=cr port_speed_set=25 traffic=ipsec \
              linerate_traffic=65 linerate_snake=0 linerate_port2x=65 \
       --ituff on
```

### Equivalent Shell Script:
```bash
./run_dsi_test_optimized.sh --phy cr --port_speed_set 25 --traffic ipsec \
                            --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65
```

## Advantages of Shell Scripts

1. **Faster Execution**: Direct execution without Ocelot wrapper overhead
2. **Tunable Timing**: Easily adjust wait times without modifying XML files
3. **Better Visibility**: Real-time progress with countdown timers
4. **Detailed Logging**: Comprehensive log files with timestamps
5. **Easy Debugging**: Clear error messages and status checks
6. **Flexible**: Fast mode and custom timing options
7. **No Manual Tuning**: Automatic coordination of all steps

## Tuning Recommendations

If you want to optimize execution time:

1. **Start with fast mode**:
   ```bash
   ./run_dsi_test_optimized.sh --fast
   ```

2. **Monitor the logs** to see if tests are passing

3. **Fine-tune specific timings** if needed:
   ```bash
   # If traffic needs more time to stabilize
   ./run_dsi_test_optimized.sh --sa_wait 7

   # If quad transitions are too fast
   ./run_dsi_test_optimized.sh --quad_wait 12
   ```

4. **Test incrementally**: Reduce waits by 10-20% at a time

## Output Files

- `dsi_test_YYYYMMDD_HHMMSS.log`: Complete test execution log (optimized version)
- `dsi_app.log`: DSI application output
- `ituff_logging_quad*.txt`: ITUFF logs for each quad

## Troubleshooting

### Script won't execute
```bash
chmod +x run_dsi_test.sh run_dsi_test_optimized.sh
```

### Python command not found
```bash
./run_dsi_test.sh --python python
# or
./run_dsi_test.sh --python python2
```

### Timing issues
- Increase specific wait times using timing parameters
- Check application logs: `tail -f /fs3/Ocelot/DSI/bin/dsi_app.log`
- Review test log for failures

### Process cleanup issues
- Manually kill processes: `pkill -f ci_eth_tx`
- Run process_kill.py: `python3 scripts/process_kill.py`

## Examples

### Example 1: Standard execution with default parameters
```bash
./run_dsi_test_optimized.sh
```

### Example 2: Fast execution with custom port speed
```bash
./run_dsi_test_optimized.sh --fast --port_speed_set 50
```

### Example 3: Clear traffic with custom line rates
```bash
./run_dsi_test_optimized.sh --traffic clear --linerate_traffic 80 --linerate_port2x 80
```

### Example 4: Custom timing for slower systems
```bash
./run_dsi_test_optimized.sh --initial_wait 30 --sa_wait 8 --quad_wait 15
```

### Example 5: Aggressive optimization
```bash
./run_dsi_test_optimized.sh --initial_wait 15 --sa_wait 2 --quad_wait 5 --stop_wait 3 --exit_wait 3
```

## Notes

- Ensure all prerequisite scripts and binaries are available
- Run from the scripts directory: `cd /fs3/Ocelot/DSI/scripts`
- Check logs for any failures or errors
- Adjust timing parameters based on your hardware performance
- The optimized version is recommended for production use

## Support

For issues or questions, check:
1. Test execution logs
2. Application logs in `/fs3/Ocelot/DSI/bin/`
3. ITUFF log files
