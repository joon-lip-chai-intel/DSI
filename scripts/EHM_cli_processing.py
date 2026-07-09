import os
import subprocess
import time
os.system("rm -rf /fs3/Ocelot/DSI/bin/EHM_port_status.txt")
os.system("rm -rf /fs3/Ocelot/DSI/bin/EHM_Port_ituff.txt")
time.sleep(5)
command_cli = " source /home/NAC/rdk/iwa_rdk.env; nohup /home/NAC/rdk/bin/cli -k 1 < /fs3/ocelot/DSI/scripts/EHM_Show_Port.txt >> /fs3/Ocelot/DSI/bin/EHM_port_status.txt"
process = subprocess.Popen(command_cli, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
process.communicate()
