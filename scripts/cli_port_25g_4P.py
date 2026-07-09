import os
import subprocess
import time
os.system("rm -rf /fs3/Ocelot/DSI/bin/bit_rate.txt")
time.sleep(5)
command_cli = " source /home/NAC/rdk/iwa_rdk.env; nohup /home/NAC/rdk/bin/cli -k 1 < /fs3/ocelot/DSI/scripts/port_25G_4P.txt"
process = subprocess.Popen(command_cli, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
process.communicate()
