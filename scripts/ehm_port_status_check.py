import re
from itertools import islice
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    "-ps", "--port_speed_set",
    help="select what kind of speed options are: 10G/25G/50G/100G.",
    default="25",
    type=int
)
args = parser.parse_args()

def check_port_status():
    i = 0
    file_path = "//fs3//Ocelot//DSI//bin//EHM_Port_Status.txt"
    file_path_ituff = "//fs3//Ocelot//DSI//bin//EHM_Port_ituff.txt"

    failing_bit = 0
    port_status = []

    with open(file_path, 'r') as file:
        relevant_lines = islice(file, 11, 35)

        for line_number, line in enumerate(relevant_lines, 12):

            # ORIGINAL CHECK (unchanged)
            if line.strip().startswith(tuple(map(str, range(10)))):

                if re.search(r'\bup\s+up\b', line):
                    print(f'Port {i} is up')
                    port_status.append(line.strip().split()[0] + "UP")
                else:
                    print(f"Port {i} is not up")
                    port_status.append(line.strip().split()[0] + "DOWN")
                    failing_bit = 1

                i += 1

            else:
                ### FIX: ignore CLI prompt / junk lines instead of exiting
                if line.strip().startswith("<"):
                    continue
                else:
                    print("Error: Setup Port Driver failed, did not manage to see Port")
                    failing_bit = 1
                    continue

    # WRITE OUTPUT ONCE (unchanged logic)
    with open(file_path_ituff, 'w') as file:
        file.write(f"##ITUFF_TOKEN##EHM_Port_{args.port_speed_set}G_Status\n")
        file.write("##ITUFF_PORT_STATUS##" + ':'.join(port_status))

    if failing_bit == 0:
        print('All Ports are UP')
        sys.exit(0)
    else:
        print("Port Setup Failed, some ports not able to link up")
        sys.exit(1)

if __name__ == "__main__":
    check_port_status()
