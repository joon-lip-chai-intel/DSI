import re
from itertools import islice
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-ps", "--port_speed_set", help="select what kind of speed options are: 10G/25G/50G/100G.", default="25",type=int)
args = parser.parse_args()
# port_speed_set ='25'
def check_port_status():
    i = 0
    file_path = "//fs3//Ocelot//DSI//bin//EHM_Port_Status_4P.txt"
    file_path_ituff = "//fs3//Ocelot//DSI//bin//EHM_Port_ituff_4P.txt"
    failing_bit = 0
    port_status=[]

    # Minimal change: define required ports for this test case
    REQUIRED_PORTS = [str(p) for p in range(0,4)]

    with open(file_path, 'r') as file:
        # Updated slice to include all ports (0-22)
        relevant_lines = islice(file, 10, 36)  # line 12 to 35 (inclusive)

        for line_number, line in enumerate(relevant_lines, 12):

            # Ignore CLI prompts or empty lines
            if line.strip().startswith("<") or len(line.strip()) == 0:
                continue
            stripped_line = line.lstrip()  # only remove leading spaces

            # Only parse lines that start with a digit (port lines)
            if stripped_line and stripped_line[0].isdigit():
                # Extract port number from the line to avoid counter mismatch
                port_number = line.strip().split()[0]

                if re.search(r'\bup\s+up\b', line):
                    print(f'Port {port_number} is up')
                    port_status.append(f"{port_number}UP")
                else:
                    print(f"Port {port_number} is not up")
                    port_status.append(f"{port_number}DOWN")

                    # Only fail if this port is required
                    if port_number in REQUIRED_PORTS:
                        failing_bit = 1
            else:
                # Any unexpected line is skipped
                continue

    # Write ITUFF output once, after all lines are parsed
    with open(file_path_ituff, 'w') as file:
        file.write(f"##ITUFF_TOKEN##EHM_Port_{args.port_speed_set}G_Status\n")
        file.write("##ITUFF_PORT_STATUS##" + ':'.join(port_status))

    # Exit with proper code
    if failing_bit == 0:
        print('All Ports are UP')
        sys.exit(0)
    else:
        print("Port Setup Failed, some ports not able to link up")
        sys.exit(1)

if __name__ == "__main__":
    check_port_status()
