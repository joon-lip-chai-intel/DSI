#!/bin/bash
################################################################################
# Quick launcher for DSI tests
# This script provides an interactive menu to run DSI tests
################################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clear
echo -e "${CYAN}================================================================================${NC}"
echo -e "${CYAN}                    DSI Test Quick Launcher${NC}"
echo -e "${CYAN}================================================================================${NC}"
echo ""
echo "Select test configuration:"
echo ""
echo -e "${GREEN}1)${NC} Standard Test (Original timing)"
echo -e "${GREEN}2)${NC} Fast Test (50% faster)"
echo -e "${GREEN}3)${NC} Custom Test (specify all parameters)"
echo -e "${GREEN}4)${NC} Quick 25G IPSec Test (Fast mode, 25G, IPSec)"
echo -e "${GREEN}5)${NC} Quick 50G IPSec Test (Fast mode, 50G, IPSec)"
echo -e "${GREEN}6)${NC} Quick 10G Clear Test (Fast mode, 10G, Clear)"
echo -e "${GREEN}7)${NC} Quick 100G IPSec Test (Fast mode, 100G, IPSec)"
echo ""
echo -e "${YELLOW}q)${NC} Quit"
echo ""
echo -n "Enter your choice [1-7, q]: "
read choice

case $choice in
    1)
        echo -e "\n${BLUE}Running Standard Test...${NC}"
        $SCRIPT_DIR/run_dsi_test_optimized.sh
        ;;
    2)
        echo -e "\n${BLUE}Running Fast Test...${NC}"
        $SCRIPT_DIR/run_dsi_test_optimized.sh --fast
        ;;
    3)
        echo -e "\n${YELLOW}Custom Test Configuration${NC}"
        echo ""
        echo -n "PHY type (cr/kr) [cr]: "
        read phy
        phy=${phy:-cr}

        echo -n "Port speed (10/25/50/100) [25]: "
        read port_speed
        port_speed=${port_speed:-25}

        echo -n "Traffic type (ipsec/clear) [ipsec]: "
        read traffic
        traffic=${traffic:-ipsec}

        echo -n "Line rate traffic [65]: "
        read lr_traffic
        lr_traffic=${lr_traffic:-65}

        echo -n "Line rate snake [0]: "
        read lr_snake
        lr_snake=${lr_snake:-0}

        echo -n "Line rate port2x [65]: "
        read lr_port2x
        lr_port2x=${lr_port2x:-65}

        echo -n "Use fast mode? (y/n) [n]: "
        read fast_mode

        if [ "$fast_mode" = "y" ] || [ "$fast_mode" = "Y" ]; then
            fast_flag="--fast"
        else
            fast_flag=""
        fi

        echo -e "\n${BLUE}Running Custom Test...${NC}"
        $SCRIPT_DIR/run_dsi_test_optimized.sh $fast_flag --phy $phy --port_speed_set $port_speed --traffic $traffic --linerate_traffic $lr_traffic --linerate_snake $lr_snake --linerate_port2x $lr_port2x
        ;;
    4)
        echo -e "\n${BLUE}Running Quick 25G IPSec Test...${NC}"
        $SCRIPT_DIR/run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 25 --traffic ipsec --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65
        ;;
    5)
        echo -e "\n${BLUE}Running Quick 50G IPSec Test...${NC}"
        $SCRIPT_DIR/run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 50 --traffic ipsec --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65
        ;;
    6)
        echo -e "\n${BLUE}Running Quick 10G Clear Test...${NC}"
        $SCRIPT_DIR/run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 10 --traffic clear --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65
        ;;
    7)
        echo -e "\n${BLUE}Running Quick 100G IPSec Test...${NC}"
        $SCRIPT_DIR/run_dsi_test_optimized.sh --fast --phy cr --port_speed_set 100 --traffic ipsec --linerate_traffic 65 --linerate_snake 0 --linerate_port2x 65
        ;;
    q|Q)
        echo -e "\n${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

exit_code=$?

echo ""
echo -e "${CYAN}================================================================================${NC}"
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}Test completed successfully!${NC}"
else
    echo -e "${RED}Test failed with exit code: $exit_code${NC}"
fi
echo -e "${CYAN}================================================================================${NC}"

exit $exit_code
