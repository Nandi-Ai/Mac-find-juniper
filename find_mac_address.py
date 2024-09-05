import paramiko
import argparse
import config

from get_switches_from_zabbix import get_switches_from_zabbix


# enter your switch names and ips
switches = {
            'Switch_Name': 'IP_Address', 
            'Switch_Name': 'IP_Address', 
            'Switch_Name': 'IP_Address', 
           }

switch_username = config.switch_username    # server username for ssh to connect 
switch_password = config.switch_password    # server password

show_lldp_neighbors = config.show_lldp_neighbors    # switch command 
show_ethernet_switching_table = config.show_ethernet_switching_table    # switch command 

# Create an ArgumentParser object to handle command-line arguments
parser = argparse.ArgumentParser()
# Define an argument for the script: '-m' is the flag, and it is required
# The `help` parameter provides a description for this argument
parser.add_argument('-m', required=True, help="Mac Address")
# Parse the command-line arguments and store them in the `args` variable
args = parser.parse_args()


# Establishing an ssh connection to execute commands on the server
def ssh_connect() -> paramiko.SSHClient:
    """
    Establishes and returns an SSH client object. Configures the SSH client to automatically accept unknown host keys.
    Returns:
        paramiko.SSHClient: The configured SSH client object if successful.
        bool: False if there is an error during initialization.
    """
    try:
        ssh = paramiko.SSHClient()    # Create a new SSH client object
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())    # Automatically add the SSH client's host key if it's missing
        return ssh
    except Exception as err:
        print("Error While Estabilish an ssh Connection.  Error Message:", err)
         # Return False to indicate that the connection could not be established
        return False
    
    
def ssh_connect_to_device(ip: str, timeout: int) -> paramiko.SSHClient:
    """
    Args:
        ip (str): IP address of the switch.
        username (str): SSH username for authentication.
        password (str): SSH password for authentication.
        timeout (int, optional): Timeout for the SSH connection in seconds.
    Returns:
        paramiko.SSHClient: The SSH client object if the connection is successful.
        None: If the connection fails.
    """
    try:
        # Connect to the switch
        ssh.connect(ip, username=switch_username, password=switch_password, timeout=timeout)
        print(f"Successfully connected to {ip}")
        return ssh
    except paramiko.AuthenticationException:
        print(f"Authentication failed when connecting to {ip}")
    except paramiko.SSHException as ssh_err:
        print(f"Failed to establish SSH connection to {ip}. SSH Exception: {ssh_err}")
    except Exception as err:
        print(f"Error while connecting to {ip}. Error Message: {err}")
    return None
    

def execute_ssh_command(ssh: paramiko.SSHClient, command: str, timeout: int) -> tuple:
    try:
        # Execute the command on the SSH client
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        
        # Read the output and error streams
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        # Get the exit status of the command        
        return output, error
    except paramiko.SSHException as ssh_err:
        print(f"SSH Exception occurred while executing command '{command}': {ssh_err}")
        return "", str(ssh_err)
    except Exception as err:
        print(f"Error occurred while executing command '{command}': {err}")
        return "", str(err)


# function that comparing est port to lldp port and searching if the specified port is located on Switch
def get_switch_name(lldp_lines, est_line, swirch_name):
    etssplit = est_line.split()     # spliting est line 
    port = etssplit[4].split('.')[0]    # getting port from line and  deleting the last null
    vlan = etssplit[0]  # getting vlan 
    
    # if port is ae we return false and conitinue process
    if  port[:2] == "ae":
        return False, port, vlan, False
    # searching port in lldp line
    for lldp_line in lldp_lines:
        lldp_port = lldp_line.split()[0]
        # comparing mac adrress port to lldp port
        if port == lldp_port:
            sw_name = lldp_line.split()
            if len(sw_name) > 4:
                sw_name = sw_name[4]
            else:
                print(f"Switch_Name: {swirch_name}, Port: {port}, Vlan: {vlan}")
                exit(0)
            if len(sw_name) > 0:
                print(f"Found switch :   {sw_name}")
                return sw_name, port, vlan, False
            else:
                return sw_name, port, vlan, True
    print("Finish")
    return swirch_name, port, vlan, True
      
      
# function that jumping swtich to switch until it finds the final switch
def jumping_switch_to_switch(switch_name, mac_address, ssh):
    while True:
        print(f"Connecting to {switch_name}, ip: {switches[switch_name]}")
        ssh = ssh_connect_to_device(switches[switch_name], 10)
        if ssh is None:
            return False, False, False, False
        else:
            # Execute the command on the switch to get the Ethernet switching table
            estout, est_err = execute_ssh_command(ssh, show_ethernet_switching_table, 10)            
            if estout: 
                est_lines = estout.strip().split('\n')
                for est_line in est_lines:
                    if mac_address in est_line:
                        lldpout, lldperr = execute_ssh_command(ssh, show_lldp_neighbors, 10)
                        if lldpout: 
                            lldpout = lldpout.read().decode()
                            lldp_lines = lldpout.strip().split('\n')
                            switchname, port, vlan, status = get_switch_name(lldp_lines, est_line, switch_name)
                            if status:
                                return switchname, port, vlan, status
                            else:
                                if switchname == False:
                                    print("jumping to next switch in switches dictionary")
                                    keys = list(switches.keys())
                                    current_index = keys.index(switch_name)
                                    next_switch = keys[current_index + 1]
                                    switch_name = next_switch
                                    break
                                else:
                                    switch_name = switchname
                                    break

# function that trying to find mac address in switch
def find_mac_address(ssh, mac_address: str) -> dict:
    for sw_name, ip in switches.items():
        print(f"Connecting to switch: {sw_name}, ip: {ip}")
        ssh = ssh_connect_to_device(switches[switch_name], 10)            
        if ssh is None:
            # if its error while connecting to switch. we will continue work to connect Another switch
            continue
        else:
            # running show ethernet switching table inside the switch
            estout, est_err = execute_ssh_command(ssh, show_ethernet_switching_table, 10)
            if estout:
                # spliting lines
                est_lines = estout.strip().split('\n')

                for est_line in est_lines:
                    if mac_address in est_line:
                        print(f"Mac address match in {sw_name},  Ip: {ip},  Mac_Address: {mac_address}")
                        # running show lldp neighbors inside the switch
                        lldpout, lldp_err= execute_ssh_command(ssh, show_lldp_neighbors, 10)
                        if lldpout:
                            lldp_lines = lldpout.strip().split('\n')
                            
                            switch_name, port, vlan, status = get_switch_name(lldp_lines, est_line, sw_name)
                            if switch_name == False:
                                break
                            if status == False:
                                switchname, port, vlan, status = jumping_switch_to_switch(switch_name, mac_address, ssh)
                                ssh.close()
                                return {"SWITCH_NAME": switchname,
                                        "PORT": port,
                                        "VLAN": vlan
                                        }
                            else:
                                print("couldn't find the switch in the lldp, connecting to next switch")
                                break
                        elif lldp_err:
                            print("error while getting data from show lldp output", lldp_err)
            elif est_err:
                print("error while getting data from est output", est_err)


##########################
if __name__ == "__main__":
    # If function get_switches_from_zabbix cant connect to zabbix or there is some network issue, 
    # we will use local dictionary
    result = get_switches_from_zabbix()
    if result:
        print("Using latest switch names and ips from zabbix server")
        switches = result
    else:
        print("Using locall switch names and ips")
    
    ssh = ssh_connect() # trying to estabilish an ssh connection
    # if ssh exsist 
    if ssh:                            #MacAddress
        output = find_mac_address(ssh, args.m)
        if output:    
            print("****** Completed ******")
            print(output)
            # Finish




