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
## Description: This script will copy and replace dev_conf file              #
## Subsystem: IA                                                             #
## Test cases:   NA                                                          #
## Dependencies: python common library                                       #
## Execution Time (in seconds):                                              #
## Test time platform: SKL i7                                                #
## Test adjustments: Parameters can be selected according to the platform    #
## Owner:  $Author: taipinnt $                                               #
## __version__ = $Revision: 230403 $                                         #
## Date: $Date: Apri 3, 2023 $                                               #
## Updated by: taipinnt 230403                                               #
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
parser.add_argument("-tt", "--testtype", help="select which config file to use", default="default",type=str)
args = parser.parse_args()

def main():
    if args.testtype=="inline":
        shutil.copy2('//home//NAC//rdk//etc//300xx_dev0.conf.inline_DSI', '//home//NAC//rdk//etc//300xx_dev0.conf.inline')  
    elif args.testtype=="lookaside":
        shutil.copy2('//home//NAC//rdk//etc//300xx_dev0.conf.inline_CPA', '//home//NAC//rdk//etc//300xx_dev0.conf.inline')  
    elif args.testtype=="default":
        shutil.copy2('//home//NAC//rdk//etc//300xx_dev0.conf.inline_Default', '//home//NAC//rdk//etc//300xx_dev0.conf.inline')  

if __name__=="__main__":
    main()
