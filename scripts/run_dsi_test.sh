#!/bin/bash
################################################################################
# DSI Test Execution Script
# This script executes the DSI test sequence without using the Ocelot wrapper
# Sequence: DSI_Port_Setup.xml > DSI_Delay.xml > DSI_TTR_B0.xml
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default variables (can be overridden by command line arguments)
PHY="cr"
PORT_SPEED_SET=25
TRAFFIC="ipsec"
LINERATE_TRAFFIC=65
LINERATE_SNAKE=0
LINERATE_PORT2X=65
DELAYS=20
PYTHON_CMD="python3"

# Working directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$WORKSPACE_ROOT/bin"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --phy)
            PHY="$2"
            shift 2
            ;;
        --port_speed_set)
            PORT_SPEED_SET="$2"
            shift 2
            ;;
        --traffic)
            TRAFFIC="$2"
            shift 2
            ;;
        --linerate_traffic)
            LINERATE_TRAFFIC="$2"
            shift 2
            ;;
        --linerate_snake)
            LINERATE_SNAKE="$2"
            shift 2
            ;;
        --linerate_port2x)
            LINERATE_PORT2X="$2"
            shift 2
            ;;
        --delays)
            DELAYS="$2"
            shift 2
            ;;
        --python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --phy <value>                PHY type (default: cr)"
            echo "  --port_speed_set <value>     Port speed: 10/25/50/100 (default: 25)"
            echo "  --traffic <value>            Traffic type: ipsec/clear (default: ipsec)"
            echo "  --linerate_traffic <value>   Line rate for traffic (default: 65)"
            echo "  --linerate_snake <value>     Line rate for snake (default: 0)"
            echo "  --linerate_port2x <value>    Line rate for port 2x (default: 65)"
            echo "  --delays <value>             Delay in seconds (default: 20)"
            echo "  --python <cmd>               Python command (default: python3)"
            echo "  -h, --help                   Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to print section headers
print_header() {
    echo ""
    echo "================================================================================"
    echo -e "${GREEN}$1${NC}"
    echo "================================================================================"
}

# Function to print step execution
print_step() {
    echo -e "${YELLOW}>>> $1${NC}"
}

# Function to check if previous command succeeded
check_status() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: $1${NC}"
        if [ "$2" != "ignore" ]; then
            exit 1
        fi
    else
        echo -e "${GREEN}Success: $1${NC}"
    fi
}

# Start test execution
echo "================================================================================"
echo "                    DSI Test Execution Script"
echo "================================================================================"
echo "Configuration:"
echo "  PHY Type:          $PHY"
echo "  Port Speed:        $PORT_SPEED_SET"
echo "  Traffic Type:      $TRAFFIC"
echo "  Line Rate Traffic: $LINERATE_TRAFFIC"
echo "  Line Rate Snake:   $LINERATE_SNAKE"
echo "  Line Rate Port2x:  $LINERATE_PORT2X"
echo "  Delays:            $DELAYS"
echo "================================================================================"
echo ""

# Get dynamic variables
print_header "PHASE 0: Setting Up Dynamic Variables"

print_step "Getting traffic type parameter..."
TRAFFIC_TYPE=$($PYTHON_CMD $SCRIPT_DIR/rate_validation/traffic_select.py -tr $TRAFFIC)
echo "Traffic type parameter: '$TRAFFIC_TYPE'"

print_step "Getting port speed parameter..."
PORT_SPEED=$($PYTHON_CMD $SCRIPT_DIR/rate_validation/port_speed_select.py -ps $PORT_SPEED_SET)
echo "Port speed parameter: '$PORT_SPEED'"

print_step "Getting PHY type parameter..."
PHY_TYPE=$($PYTHON_CMD $SCRIPT_DIR/rate_validation/phy_type_select.py -pt $PHY)
echo "PHY type parameter: '$PHY_TYPE'"

# PHASE 1: DSI Port Setup
print_header "PHASE 1: DSI Port Setup (DSI_Port_Setup.xml)"

print_step "Copying inline configuration file..."
$PYTHON_CMD $SCRIPT_DIR/copy_conf.py -tt 'inline'
check_status "Copy inline conf file completed"

print_step "Unloading DSI driver..."
/home/NAC/rdk/util/rmNAC.sh
check_status "DSI driver unload completed"

print_step "Loading DSI driver..."
bash -c "source /home/NAC/rdk/iwa_rdk.env && /home/NAC/rdk/util/loadNAC.sh"
check_status "DSI driver load completed"

# PHASE 2: DSI Delay
print_header "PHASE 2: DSI Delay (DSI_Delay.xml)"

print_step "Running delay script for $DELAYS seconds..."
$PYTHON_CMD $SCRIPT_DIR/run_delay.py -tdelay $DELAYS
check_status "Delay script completed"

# PHASE 3: DSI TTR B0
print_header "PHASE 3: DSI TTR B0 Test (DSI_TTR_B0.xml)"

# Launch CLI master process in background
print_step "Launching CLI master process..."
$PYTHON_CMD $SCRIPT_DIR/cli_master_process.py &
CLI_MASTER_PID=$!
check_status "CLI master process launched (PID: $CLI_MASTER_PID)" "ignore"
sleep 2

# Launch DSI test application
print_step "Setting up environment and launching DSI test application..."
bash -c "source /home/root/.profile"
check_status "Hugepages setup completed"

print_step "Launching DSI test application with parameters:"
echo "  PHY Type: $PHY_TYPE"
echo "  Traffic Type: $TRAFFIC_TYPE"
echo "  Port Speed: $PORT_SPEED"

nohup bash -c "source /home/NAC/rdk/iwa_rdk.env && /home/NAC/app/crypto_inline_eth_tx_ppv/build_asic/ci_eth_tx --vdev=net_ice_dsi0,pci-bdf=f5:00.0,rxq=20,txq=20,ipsec_enable=1,cmpltnq=20 -- -p 4 -i -e -l 512 -b 32 -c ${PHY_TYPE} -s 0 ${TRAFFIC_TYPE} ${PORT_SPEED}" > $BIN_DIR/dsi_app.log 2>&1 &
DSI_APP_PID=$!
check_status "DSI test application launched (PID: $DSI_APP_PID)" "ignore"

# Quad 0 - 25s delay
print_step "Starting Quad 0 test sequence (wait 25s)..."
sleep 25

print_step "Starting inline traffic (SA) for Quad 0..."
echo "sa" > /tmp/ci_eth_tx_opt
check_status "Start inline traffic for Quad 0"

print_step "Waiting 5 seconds for traffic to stabilize..."
sleep 5

print_step "Reading port rate for Quad 0..."
$PYTHON_CMD $SCRIPT_DIR/cli_processing_TTR.py -qd 0
check_status "Read port rate for Quad 0" "ignore"

# Quad 4 - Move to x4 at 40s
print_step "Moving to x4 (wait 10s)..."
sleep 10

echo "x4" > /tmp/ci_eth_tx_opt
check_status "Move to x4"

print_step "Waiting 10 seconds..."
sleep 10

print_step "Starting inline traffic (SA) for Quad 4..."
echo "sa" > /tmp/ci_eth_tx_opt
check_status "Start inline traffic for Quad 4"

print_step "Waiting 5 seconds for traffic to stabilize..."
sleep 5

print_step "Reading port rate for Quad 4..."
$PYTHON_CMD $SCRIPT_DIR/cli_processing_TTR.py -qd 4
check_status "Read port rate for Quad 4" "ignore"

# Quad 8 - Move to x8 at 65s
print_step "Moving to x8 (wait 10s)..."
sleep 10

echo "x8" > /tmp/ci_eth_tx_opt
check_status "Move to x8"

print_step "Waiting 10 seconds..."
sleep 10

print_step "Starting inline traffic (SA) for Quad 8..."
echo "sa" > /tmp/ci_eth_tx_opt
check_status "Start inline traffic for Quad 8"

print_step "Waiting 5 seconds for traffic to stabilize..."
sleep 5

print_step "Reading port rate for Quad 8..."
$PYTHON_CMD $SCRIPT_DIR/cli_processing_TTR.py -qd 8
check_status "Read port rate for Quad 8" "ignore"

# Quad 12 - Move to x12 at 90s
print_step "Moving to x12 (wait 10s)..."
sleep 10

echo "x12" > /tmp/ci_eth_tx_opt
check_status "Move to x12"

print_step "Waiting 10 seconds..."
sleep 10

print_step "Starting inline traffic (SA) for Quad 12..."
echo "sa" > /tmp/ci_eth_tx_opt
check_status "Start inline traffic for Quad 12"

print_step "Waiting 5 seconds for traffic to stabilize..."
sleep 5

print_step "Reading port rate for Quad 12..."
$PYTHON_CMD $SCRIPT_DIR/cli_processing_TTR.py -qd 12
check_status "Read port rate for Quad 12" "ignore"

# Quad 16 - Move to x16 at 115s
print_step "Moving to x16 (wait 10s)..."
sleep 10

echo "x16" > /tmp/ci_eth_tx_opt
check_status "Move to x16"

print_step "Waiting 10 seconds..."
sleep 10

print_step "Starting inline traffic (SA) for Quad 16..."
echo "sa" > /tmp/ci_eth_tx_opt
check_status "Start inline traffic for Quad 16"

print_step "Waiting 5 seconds for traffic to stabilize..."
sleep 5

print_step "Reading port rate for Quad 16..."
$PYTHON_CMD $SCRIPT_DIR/cli_processing_TTR.py -qd 16
check_status "Read port rate for Quad 16" "ignore"

# Stop traffic and exit
print_step "Stopping inline traffic (wait 10s)..."
sleep 10

echo "ta" > /tmp/ci_eth_tx_opt 2>&1 &
check_status "Stop inline traffic"

print_step "Exiting application (wait 10s)..."
sleep 10

echo "e" > /tmp/ci_eth_tx_opt 2>&1 &
check_status "Execute exit command" "ignore"

print_step "Killing CLI process..."
$PYTHON_CMD $SCRIPT_DIR/process_kill.py
check_status "Kill CLI process" "ignore"

print_step "Final cleanup (wait 10s)..."
sleep 10

$PYTHON_CMD $SCRIPT_DIR/process_kill.py
check_status "Final process kill" "ignore"

# PHASE 4: Log Validation
print_header "PHASE 4: Log Validation and Rate Validation"

print_step "Validating Quad 0 logs..."
$PYTHON_CMD $SCRIPT_DIR/DSI_sd.py $BIN_DIR/ituff_logging_quad0.txt
check_status "ITUFF processing for Quad 0" "ignore"

$PYTHON_CMD $SCRIPT_DIR/rate_validation/rate_validate_TTR.py -qd 0 -tr $TRAFFIC -t_lr $LINERATE_TRAFFIC -s_lr $LINERATE_SNAKE -2x_lr $LINERATE_PORT2X -ps $PORT_SPEED_SET -pt $PHY
check_status "Rate validation for Quad 0"

print_step "Validating Quad 4 logs..."
$PYTHON_CMD $SCRIPT_DIR/DSI_sd.py $BIN_DIR/ituff_logging_quad4.txt
check_status "ITUFF processing for Quad 4" "ignore"

$PYTHON_CMD $SCRIPT_DIR/rate_validation/rate_validate_TTR.py -qd 4 -tr $TRAFFIC -t_lr $LINERATE_TRAFFIC -s_lr $LINERATE_SNAKE -2x_lr $LINERATE_PORT2X -ps $PORT_SPEED_SET -pt $PHY
check_status "Rate validation for Quad 4"

print_step "Validating Quad 8 logs..."
$PYTHON_CMD $SCRIPT_DIR/DSI_sd.py $BIN_DIR/ituff_logging_quad8.txt
check_status "ITUFF processing for Quad 8" "ignore"

$PYTHON_CMD $SCRIPT_DIR/rate_validation/rate_validate_TTR.py -qd 8 -tr $TRAFFIC -t_lr $LINERATE_TRAFFIC -s_lr $LINERATE_SNAKE -2x_lr $LINERATE_PORT2X -ps $PORT_SPEED_SET -pt $PHY
check_status "Rate validation for Quad 8"

print_step "Validating Quad 12 logs..."
$PYTHON_CMD $SCRIPT_DIR/DSI_sd.py $BIN_DIR/ituff_logging_quad12.txt
check_status "ITUFF processing for Quad 12" "ignore"

$PYTHON_CMD $SCRIPT_DIR/rate_validation/rate_validate_TTR.py -qd 12 -tr $TRAFFIC -t_lr $LINERATE_TRAFFIC -s_lr $LINERATE_SNAKE -2x_lr $LINERATE_PORT2X -ps $PORT_SPEED_SET -pt $PHY
check_status "Rate validation for Quad 12"

print_step "Validating Quad 16 logs..."
$PYTHON_CMD $SCRIPT_DIR/DSI_sd.py $BIN_DIR/ituff_logging_quad16.txt
check_status "ITUFF processing for Quad 16" "ignore"

$PYTHON_CMD $SCRIPT_DIR/rate_validation/rate_validate_TTR.py -qd 16 -tr $TRAFFIC -t_lr $LINERATE_TRAFFIC -s_lr $LINERATE_SNAKE -2x_lr $LINERATE_PORT2X -ps $PORT_SPEED_SET -pt $PHY
check_status "Rate validation for Quad 16"

# Final Summary
print_header "Test Execution Completed"
echo -e "${GREEN}All DSI test phases have been executed successfully!${NC}"
echo ""
echo "Test Summary:"
echo "  Total execution time: approximately 160 seconds"
echo "  Phases executed:"
echo "    1. DSI Port Setup"
echo "    2. DSI Delay ($DELAYS seconds)"
echo "    3. DSI TTR B0 Test (5 quads: 0, 4, 8, 12, 16)"
echo "    4. Log Validation and Rate Validation"
echo ""
echo "Check logs in: $BIN_DIR"
echo "================================================================================"
