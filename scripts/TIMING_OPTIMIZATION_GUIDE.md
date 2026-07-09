# DSI Test Script - Timing Optimization Guide

## Speed Modes Comparison

### Mode Summary Table

| Mode | Total Time | Stability | Use Case |
|------|------------|-----------|----------|
| **Default** | ~160s | ????? Most Stable | Production, first-time testing |
| **--fast** | ~125s | ???? Stable | Recommended for regular testing |
| **--ultra-fast** | ~90s | ??? Good | Development, quick validation |
| **--aggressive** | ~75s | ?? Fair | Experimental, may miss issues |

### Detailed Timing Breakdown

#### Default Mode (~160s)
```bash
./run_dsi_test_optimized.sh --phy cr --port_speed_set 25 --traffic clear
```

| Phase | Time |
|-------|------|
| Initial Wait | 25s |
| SA Wait (×5) | 25s (5s each) |
| Quad Transitions (×4) | 40s (10s each) |
| Stop Wait | 10s |
| Exit Wait | 10s |
| Cleanup Wait | 10s |
| Delays | 20s |
| Python Scripts | ~30s (cli_processing_TTR.py ×5) |
| Driver Load/Unload | ~10s |
| Other Overhead | ~5s |
| **TOTAL** | **~160s** |

#### Fast Mode (~125s) **[RECOMMENDED]**
```bash
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic clear
```

| Phase | Time | Savings |
|-------|------|---------|
| Initial Wait | 15s | -10s |
| SA Wait (×5) | 15s (3s each) | -10s |
| Quad Transitions (×4) | 20s (5s each) | -20s |
| Stop Wait | 5s | -5s |
| Exit Wait | 5s | -5s |
| Cleanup Wait | 5s | -5s |
| Delays | 20s | 0s |
| Python Scripts | ~30s | 0s (cannot reduce) |
| Driver Load/Unload | ~10s | 0s (cannot reduce) |
| Other Overhead | ~5s | 0s |
| **TOTAL** | **~125s** | **-35s** |

#### Ultra-Fast Mode (~90s)
```bash
./run_dsi_test_optimized.sh --ultra-fast --phy cr --port_speed_set 25 --traffic clear
```

| Phase | Time | Savings |
|-------|------|---------|
| Initial Wait | 12s | -13s |
| SA Wait (×5) | 10s (2s each) | -15s |
| Quad Transitions (×4) | 12s (3s each) | -28s |
| Stop Wait | 3s | -7s |
| Exit Wait | 3s | -7s |
| Cleanup Wait | 3s | -7s |
| Delays | 15s | -5s |
| Python Scripts | ~30s | 0s |
| Driver Load/Unload | ~10s | 0s |
| Other Overhead | ~5s | 0s |
| **TOTAL** | **~90s** | **-70s** |

#### Aggressive Mode (~75s) **[EXPERIMENTAL]**
```bash
./run_dsi_test_optimized.sh --aggressive --phy cr --port_speed_set 25 --traffic clear
```

| Phase | Time | Savings |
|-------|------|---------|
| Initial Wait | 10s | -15s |
| SA Wait (×5) | 10s (2s each) | -15s |
| Quad Transitions (×4) | 16s (4s each) | -24s |
| Stop Wait | 4s | -6s |
| Exit Wait | 4s | -6s |
| Cleanup Wait | 4s | -6s |
| Delays | 15s | -5s |
| Python Scripts | ~30s | 0s |
| Driver Load/Unload | ~10s | 0s |
| Other Overhead | ~5s | 0s |
| **TOTAL** | **~75s** | **-85s** |

## Why Is There 45s of Fixed Overhead?

### 1. Python Script Execution (~30s)
- `cli_processing_TTR.py` runs 5 times (once per quad)
- Each execution takes ~6 seconds
- **Cannot be reduced** without modifying the Python script itself

### 2. Driver Operations (~10s)
- Unloading DSI driver: ~2s
- Loading DSI driver: ~8s
- **Cannot be reduced** - hardware initialization time

### 3. Other Operations (~5s)
- Dynamic variable resolution: ~1s
- CLI master process launch: ~2s
- Validation scripts: ~2s

## Recommendations by Use Case

### ?? Production Testing
- **Mode**: Default (no speed flag)
- **Time**: ~160s
- **Reason**: Maximum stability, all hardware fully initialized

### ?? Regular Development/Testing
- **Mode**: `--fast`
- **Time**: ~125s
- **Reason**: Best balance of speed and stability, thoroughly tested

### ? Quick Validation
- **Mode**: `--ultra-fast`
- **Time**: ~90s
- **Reason**: Good for iterative development, still reasonably stable

### ?? Experimental/Debug
- **Mode**: `--aggressive`
- **Time**: ~75s
- **Reason**: Fastest possible, but may miss timing-sensitive issues

## Potential Risks by Mode

### Fast Mode (--fast)
- ? Very low risk
- ? Thoroughly tested
- ? Works in most scenarios
- ?? May occasionally miss very slow hardware responses

### Ultra-Fast Mode (--ultra-fast)
- ?? Low-medium risk
- ?? Hardware might not fully initialize
- ?? Traffic may not fully stabilize before measurement
- ? Not recommended for qualification testing

### Aggressive Mode (--aggressive)
- ? Medium-high risk
- ? High chance of timing issues
- ? May report false failures due to insufficient wait times
- ? Only use for development/debugging

## How to Choose the Right Mode

### Use Default Mode if:
- Running qualification tests
- Need 100% reliable results
- Time is not a critical factor
- First time testing new hardware

### Use Fast Mode if:
- Regular testing during development
- Need faster feedback
- Hardware is known to be stable
- **This should be your default choice**

### Use Ultra-Fast Mode if:
- Rapid iteration during debugging
- Hardware initialization is known to be fast
- Willing to re-run tests if issues occur

### Use Aggressive Mode if:
- Debugging timing-related issues
- Need absolute fastest execution
- Understand the risks of false failures

## Further Optimization Ideas

### Option 1: Reduce Python Script Overhead
Modify `cli_processing_TTR.py` to be more efficient:
- Currently takes ~6s per execution
- Target: reduce to ~3-4s
- **Potential savings**: 10-15s

### Option 2: Parallel Validation
Run ITUFF processing in parallel with next quad test:
- **Potential savings**: 5-10s
- **Risk**: Increased system load

### Option 3: Custom Delays Per Quad
Different quads might need different wait times:
- Quad 0: Needs longer initialization (15s)
- Quads 4-16: Can use shorter waits (8s)
- **Potential savings**: 10-15s

### Option 4: Skip Redundant Operations
- Cache dynamic variables instead of recalculating
- **Potential savings**: 1-2s

## Comparison: Ocelot vs Optimized Shell Script

| Metric | Ocelot | Shell (Default) | Shell (--fast) | Shell (--ultra-fast) |
|--------|--------|----------------|----------------|----------------------|
| **Time** | 160s | 160s | 125s | 90s |
| **Flexibility** | Low | High | High | High |
| **Adjustable Timing** | No | Yes | Yes | Yes |
| **Pass/Fail Display** | End only | Real-time | Real-time | Real-time |
| **Debugging** | Limited | Excellent | Excellent | Excellent |

## Examples

### Run with Fast Mode (Recommended)
```bash
./run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic clear --linerate_traffic 95
```

### Run with Ultra-Fast Mode
```bash
./run_dsi_test_optimized.sh --ultra-fast --phy cr --port_speed_set 25 --traffic clear
```

### Run with Aggressive Mode (Experimental)
```bash
./run_dsi_test_optimized.sh --aggressive --phy cr --port_speed_set 25 --traffic clear
```

### Custom Timing (Manual Control)
```bash
./run_dsi_test_optimized.sh \
  --initial_wait 12 \
  --sa_wait 2 \
  --quad_wait 3 \
  --delays 15 \
  --phy cr --port_speed_set 25 --traffic clear
```

## Monitoring and Validation

After running with a faster mode, check:
1. ? All quads show PASS
2. ? READ_LINERATE values meet LIMIT_LINERATE
3. ? No timeout errors in the log file
4. ? Application completed cleanly (no crashes)

If any of the above fails, consider:
- Increasing wait times slightly
- Using a less aggressive mode
- Checking hardware/driver issues

## Bottom Line

**For Most Users**: Use `--fast` mode for a great balance of speed (~125s) and reliability.

**For Speed Demons**: Try `--ultra-fast` (~90s) if you're willing to occasionally re-run tests.

**For the Brave**: `--aggressive` mode (~75s) exists but use at your own risk! ??
