import subprocess
import os

command_cli="tmux new -d -s my-session ' source /home/NAC/rdk/iwa_rdk.env; cd /home/NAC/rdk/bin; ./cli -k 1 -m'"
process = subprocess.Popen(command_cli, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
process.communicate()
