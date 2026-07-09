#!/usr/bin/env python
"""
############################################################################
# INTEL CONFIDENTIAL
# Copyright 2014-2016 Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related
# to the source code ("Material") are owned by Intel Corporation or its
# suppliers or licensors. Title to the Material remains with Intel Corp-
# oration or its suppliers and licensors. The Material may contain trade
# secrets and proprietary and confidential information of Intel Corpor-
# ation and its suppliers and licensors, and is protected by worldwide
# copyright and trade secret laws and treaty provisions. No part of the
# Material may be used, copied, reproduced, modified, published, uploaded,
# posted, transmitted, distributed, or disclosed in any way without
# Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellect-
# ual property right is granted to or conferred upon you by disclosure or
# delivery of the Materials, either expressly, by implication, inducement,
# estoppel or otherwise. Any license under such intellectual property
# rights must be express and approved by Intel in writing.
############################################################################

##############################################################################
## INTEL CONFIDENTIAL - DO NOT RE-DISTRIBUTE                                 #
## Copyright 2014-2016 Intel Corporation All Rights Reserved.                #
##                                                                           #
## Filename: NAC.py                                                          #
## Description: This script will test validate the rates for ipsec traffic   #
## before running this                                                       # 
## check results for Pass/Fail                                               #
## Subsystem: IA                                                             #
## Test cases:   NA                                                          #
## Dependencies: python common library                                       #
## Execution Time (in seconds): 21                                           #
## Test time platform: SKL i7                                                #
## Test adjustments: Parameters can be selected according to the platform    #
## Owner:  $Author: deepakti $                                               #
## __version__ = $Revision: 22021 $                                          #
## Date: $Date: Feb 29, 2016 $                                               #
## Updated by: taipinnt 230323
##############################################################################
"""

import os
import subprocess
import glob
import argparse
DEVNULL = open(os.devnull, 'wb')
import sys
import inspect
import logging
import shutil
import time
import math
import re
import signal

parser = argparse.ArgumentParser()
parser.add_argument("-pt", "--phy", help="for ituff logging of phy_type", default="aui",type=str)
parser.add_argument("-ps", "--port_speed_set", help="select what kind of speed options are: 10G/25G/50G/100G.", default="25",type=int)
parser.add_argument("-tr", "--traffic", help="select what kind of traffic options are: ipsec/clear.", default="ipsec",type=str)
parser.add_argument("-t_lrm", "--linerate_traffic_multi", help="select what 100G multilane linerate for traffic to verify against.", default="30",type=int)
parser.add_argument("-t_lrs", "--linerate_traffic_single", help="select what 50G singlelane linerate for traffic to verify against.", default="30",type=int)
parser.add_argument("-s_lr", "--linerate_snake", help="select what linerate for snake to verify against.", default="30",type=int)
parser.add_argument("-2x_lr", "--linerate_port2x", help="select what linerate of port 20-22 to verify against.", default="30",type=int)
parser.add_argument("-qd", "--quad", help="select which port to start the traffic.", default="0",type=int)
args = parser.parse_args()

print(f"#DSI_START#Checking for {args.port_speed_set}G {args.traffic} multilane traffic on Quad starting with Port{args.quad} with minimum linerate expected: {args.linerate_traffic_multi}%")

def run():
    
        """
        mapping of the ports are in order per quad
        quad 0 : ports 0 till 3
        quad 4 : ports 4 till 7
        quad 8 : ports 8 till 11
        quad 12: ports 12 till 15 
        quad 16: ports 16 till 19
        CPK    : port 20
        CPM    : ports 21 & 22
        """
        
        #remap phy-type according to speed
        if args.port_speed_set==10:
            args.phy="SFI"
        if args.port_speed_set==25:
            args.phy="CR"
        #50G/100G is pushed in, no need set, in fact can't hardcode.

        # use of range() to define a range of values
        port_range = range(20)
        port2x_range = range(20,23)
        port_dict = {}
        
        #define initial values, especially for 50G, when not all ports can be up at the same time.
        for a in port_range:
            port_dict['line_rate{0}'.format(a)] = 0
        for a in port2x_range:
            port_dict['line_rate{0}'.format(a)] = 0
        
        f = open("//fs3//Ocelot//DSI//bin//bit_rate_quad" + str(args.quad) + ".txt", "r")
        found_port = 0
        found_port2x = 0
        for line in f:
            for i in port_range:
                if "  " + str(i) + "  " + str(args.port_speed_set) + "G" in line:
                    port_dict['line_rate{0}'.format(i)] = float(line.split()[-6])
                    if not port_dict['line_rate{0}'.format(i)] == 0.0:
                        found_port = found_port + 1
                    #logging.info("##The linerate for port", i, "operating at", args.port_speed_set,"G is", port_dict['line_rate{0}'.format(i)])
                    #print("##The linerate for port", i, "operating at", args.port_speed_set,"G is", port_dict['line_rate{0}'.format(i)])
                elif "  " + str(i) + "   " + "50G" in line:
                    port_dict['line_rate{0}'.format(i)] = float(line.split()[-6])
                    if not port_dict['line_rate{0}'.format(i)] == 0.0:
                        found_port = found_port + 1
                    #logging.info("##The linerate for port", i, "operating at", args.port_speed_set,"G is", port_dict['line_rate{0}'.format(i)])
                    #print("##The linerate for port", i, "operating at", args.port_speed_set,"G is", port_dict['line_rate{0}'.format(i)])
            for i in port2x_range:
                if "  " + str(i) + "  " + "100G" in line:
                    port_dict['line_rate{0}'.format(i)] = float(line.split()[-6])
                    if not port_dict['line_rate{0}'.format(i)] == 0.0:
                        found_port2x = found_port2x + 1
                    #logging.info("##The linerate for port", i, "operating at 100G is", port_dict['line_rate{0}'.format(i)])
                    #print("##The linerate for port", i, "operating at 100G is", port_dict['line_rate{0}'.format(i)])
        
        #print for tested quad for traffic first
        x = 0 #counter for printing messages
        for i in range(args.quad,args.quad + 4):
            #logging.info("##The linerate for port", i, "operating at", args.port_speed_set,"G is", port_dict['line_rate{0}'.format(i)])
            x = x + 1
            if x==1:
                print(f"##The Multi-lane linerate for port{i} operating at {args.port_speed_set}G is {port_dict['line_rate{0}'.format(i)]}%")
            elif x==2:
                continue
            else:
                print(f"##The Single-lane linerate for port{i} operating at 50G is {port_dict['line_rate{0}'.format(i)]}%")
        #print for port2x
        for i in port2x_range:
            #logging.info("##The linerate for port", i, "operating at 100G is", port_dict['line_rate{0}'.format(i)])
            print(f"##The linerate for port{i} operating at 100G is {port_dict['line_rate{0}'.format(i)]}%")

        #print for the rest of the world
        for a in port_range:
            print (f"##Linerate Port{a}: {port_dict['line_rate{0}'.format(a)]}%")
        for a in port2x_range:
            print (f"##Linerate Port{a}: {port_dict['line_rate{0}'.format(a)]}%")
        
        ###ITUFF LOGGING STUFF HERE
        linerate_limit = []
        #ipsec traffic limit
        if args.traffic=="ipsec":
            if args.quad==0:
                for j in range (0,4):
                    if j==0:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==1:            
                        linerate_limit.append(str(0))
                    if (j==2 or j==3):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (4,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==4:
                for k in range (0,4):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (4,8):
                    if j==4:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==5:            
                        linerate_limit.append(str(0))
                    if (j==6 or j==7):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (8,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==8:
                for k in range (0,8):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (8,12):
                    if j==8:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==9:            
                        linerate_limit.append(str(0))
                    if (j==10 or j==11):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (12,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==12:
                for k in range (0,12):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (12,16):
                    if j==12:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==13:            
                        linerate_limit.append(str(0))
                    if (j==14 or j==15):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (16,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==16:
                for k in range (0,16):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (16,20):
                    if j==16:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==17:            
                        linerate_limit.append(str(0))
                    if (j==18 or j==19):
                        linerate_limit.append(str(args.linerate_traffic_single))
        
            for m in port2x_range:
                linerate_limit.append(str(args.linerate_port2x))
        
        #clear traffic limit
        if args.traffic=="clear":
            if args.quad==0:
                for j in range (0,4):
                    if j==0:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==1:            
                        linerate_limit.append(str(0))
                    if (j==2 or j==3):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (4,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==4:
                for k in range (0,4):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (4,8):
                    if j==4:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==5:            
                        linerate_limit.append(str(0))
                    if (j==6 or j==7):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (8,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==8:
                for k in range (0,8):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (8,12):
                    if j==8:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==9:            
                        linerate_limit.append(str(0))
                    if (j==10 or j==11):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (12,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==12:
                for k in range (0,12):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (12,16):
                    if j==12:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==13:            
                        linerate_limit.append(str(0))
                    if (j==14 or j==15):
                        linerate_limit.append(str(args.linerate_traffic_single))
                for k in range (16,20):
                    linerate_limit.append(str(args.linerate_snake))
            if args.quad==16:
                for k in range (0,16):
                    linerate_limit.append(str(args.linerate_snake))
                for j in range (16,20):
                    if j==16:
                        linerate_limit.append(str(args.linerate_traffic_multi))
                    if j==17:            
                        linerate_limit.append(str(0))
                    if (j==18 or j==19):
                        linerate_limit.append(str(args.linerate_traffic_single))   
            
            linerate_limit.append(str(args.linerate_port2x))
            linerate_limit.append(str(0))
            linerate_limit.append(str(0))
            
        #Actual values
        linerate_arr = []
        for a in port_range:
            linerate_arr.append(str(port_dict['line_rate{0}'.format(a)]))
        for a in port2x_range:
             linerate_arr.append(str(port_dict['line_rate{0}'.format(a)]))
        
        ituff_limit = "##ITUFF_LIMIT##" + ':'.join(linerate_limit)
        ituff_value = "##ITUFF_VALUE##" + ':'.join(linerate_arr)
        print (f"##ITUFF_TOKEN##DSI_{args.phy.upper()}_{args.traffic.upper()}_{args.port_speed_set}G_QUAD_{args.quad}")
        print (f"{ituff_limit}")
        print (f"{ituff_value}")
        with open ("//fs3//Ocelot//DSI//bin//ituff_logging_quad" + str(args.quad) + ".txt", "w") as output_file:
            output_file.write (f"##ITUFF_TOKEN##DSI_{args.phy.upper()}_{args.traffic.upper()}_{args.port_speed_set}G_QUAD_{args.quad}\n")
            output_file.write (f"{ituff_limit}\n")
            output_file.write (f"{ituff_value}\n")

        ##ITUFF LOGGING END
        #if no ports up, test may not have ran properly, kill test.
        if args.linerate_snake > 0:
            port_up_default = 20 #checking for snake traffic too, require all 20 ports up
        else:
            port_up_default = 3 #checking inline traffic only, ignore the other ports, require 3 ports up (first two ports will be multilane 100G, 3rd and 4th single lanes)

        if args.traffic == "ipsec":
            port2x_up_default = 3 #ipsec traffic: CPK + CPM ports 20,21,22
        else:
            port2x_up_default = 1 #clear traffic: CPK only port 20
        
        if found_port < port_up_default or found_port2x < port2x_up_default:
            print (f"##Expecting: {port_up_default} Port. Actual: {found_port} port/s up.")
            print (f"##Expecting: {port2x_up_default} Port2x. Actual {found_port2x} port/s up.")
            print (f"##Test Failed.#DSI_END#")
            exit(1)
        else:
            print (f"##Expecting {port_up_default} Port. Actual: {found_port} up.")
            print (f"##Expecting {port2x_up_default} Port2x. Actual: {found_port2x} up.")
            
        #Start parsing linerate against threshold
        if args.quad==0 and args.traffic=="ipsec":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (0,4):
                if j==0:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==1:
                    continue
                if (j==2 or j==3):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (4,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for m in port2x_range:
                if not port_dict['line_rate{0}'.format(m)] >= line_rate_2xport:
                    Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)
    
        if args.quad==4 and args.traffic=="ipsec":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (4,8):
                if j==4:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==5:
                    continue
                if (j==6 or j==7):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,4):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for k in range (8,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for m in port2x_range:
                if not port_dict['line_rate{0}'.format(m)] >= line_rate_2xport:
                    Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)
    
        if args.quad==8 and args.traffic=="ipsec":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (8,12):
                if j==8:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==9:
                    continue
                if (j==10 or j==11):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,8):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for k in range (12,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for m in port2x_range:
                if not port_dict['line_rate{0}'.format(m)] >= line_rate_2xport:
                    Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)

        if args.quad==12 and args.traffic=="ipsec":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (12,16):
                if j==12:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==13:
                    continue
                if (j==14 or j==15):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,12):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for k in range (16,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for m in port2x_range:
                if not port_dict['line_rate{0}'.format(m)] >= line_rate_2xport:
                    Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)

        if args.quad==16 and args.traffic=="ipsec":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (16,20):
                if j==16:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==17:
                    continue
                if (j==18 or j==19):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,16):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for m in port2x_range:
                if not port_dict['line_rate{0}'.format(m)] >= line_rate_2xport:
                    Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)

        if args.quad==0 and args.traffic=="clear":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (0,4):
                if j==0:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==1:
                    continue
                if (j==2 or j==3):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (4,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            if not port_dict['line_rate{0}'.format(20)] >= line_rate_2xport:
                    Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)
    
        if args.quad==4 and args.traffic=="clear":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (4,8):
                if j==4:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==5:
                    continue
                if (j==6 or j==7):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,4):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for k in range (8,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            if not port_dict['line_rate{0}'.format(20)] >= line_rate_2xport:
                Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)
    
    
        if args.quad==8 and args.traffic=="clear":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (8,12):
                if j==8:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==9:
                    continue
                if (j==10 or j==11):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,8):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for k in range (12,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            if not port_dict['line_rate{0}'.format(20)] >= line_rate_2xport:
                Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)

        if args.quad==12 and args.traffic=="clear":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (12,16):
                if j==12:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==13:
                    continue
                if (j==14 or j==15):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,12):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            for k in range (16,20):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            if not port_dict['line_rate{0}'.format(20)] >= line_rate_2xport:
                Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)

        if args.quad==16 and args.traffic=="clear":
            line_rate_limit_traffic_multi = args.linerate_traffic_multi
            line_rate_limit_traffic_single = args.linerate_traffic_single
            line_rate_limit_snake = args.linerate_snake
            line_rate_2xport = args.linerate_port2x
            Fail = 0
            for j in range (16,20):
                if j==16:
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_multi:
                        Fail = Fail + 1
                if j==17:
                    continue
                if (j==18 or j==19):
                    if not port_dict['line_rate{0}'.format(j)] >= line_rate_limit_traffic_single:
                        Fail = Fail + 1
            for k in range (0,16):
                if not port_dict['line_rate{0}'.format(k)] >= line_rate_limit_snake:
                    Fail = Fail + 1
            if not port_dict['line_rate{0}'.format(20)] >= line_rate_2xport:
                Fail = Fail + 1
            if Fail==0:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is above {line_rate_limit_traffic_multi}% for {args.traffic} traffic, 50G Single-lane linerate is above {line_rate_limit_traffic_single}% and test Passed.#DSI_END#")
                exit(0)
            else:
                print (f"##The 100G Multi-lane linerate for Quad{args.quad} is below the threshold level of {line_rate_limit_traffic_multi}% or 50G Single-lane linerate is below {line_rate_limit_traffic_single}% and test Failed.#DSI_END#")
                exit(1)

def main():
    run()


if __name__ == "__main__":
    main()
