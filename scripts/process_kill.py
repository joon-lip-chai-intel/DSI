import os
import subprocess
output = subprocess.check_output("ps -C cli|grep cli|awk '{print $1;}'", shell=True)

process_id=(output.decode('UTF-8'))

if len(output.strip())==0:
   print ("process value doesn't exist")
else:
   os.system("kill -9 " +str(process_id))


