import os
import subprocess
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-qd", "--quad", help="to append quad number", default="0",type=int)
args = parser.parse_args()

os.system("rm -rf /fs3/Ocelot/DSI/bin/bit_rate_quad" + str(args.quad) + ".txt")
time.sleep(5)

command_cli = " source /home/NAC/rdk/iwa_rdk.env; nohup /home/NAC/rdk/bin/cli -k 1 < /fs3/ocelot/DSI/scripts/bit_rate_all.txt >> /fs3/Ocelot/DSI/bin/bit_rate_quad" + str(args.quad) + ".txt"
process = subprocess.Popen(command_cli, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
process.communicate()
