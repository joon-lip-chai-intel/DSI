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
## Filename: NAC.py                                                #
## Description: This script will select the traffic
before running this   #
##  check results for Pass/Fail            #
## Subsystem: IA                                                             #
## Test cases:   NA                                                          #
## Dependencies: python common library                                       #
## Execution Time (in seconds): 21                                           #
## Test time platform: SKL i7                                          #
## Test adjustments: Parameters can be selected according to the platform    #
## Owner:  $Author: deepakti $                                                #
## __version__ = $Revision: 22021 $                                          #
## Date: $Date: Feb 29, 2016 $                                               #
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
parser.add_argument("-tr", "--traffic", help="select what kind of  traffic options are  ipsec/clear", default="ipsec",type=str)
args = parser.parse_args()



def main():
    if args.traffic=="ipsec":
        print ("")
    else:
        print ("-n ")

if __name__=="__main__":
    main()