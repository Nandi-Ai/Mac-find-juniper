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

switch_username = config.switch_username # server username for ssh to connect 
switch_password = config.switch_password # server password

show_lldp_neighbors = config.show_lldp_neighbors # switch command 
show_ethernet_switching_table = config.show_ethernet_switching_table # switch command 

parser = argparse.ArgumentParser()
parser.add_argument('-m', required=True, help="Mac Address")
args = parser.parse_args()


# Establishing an ssh connection to execute commands on the server
def ssh_connect():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return ssh
    except Exception as err:
        print("Error While Estabilish an ssh Connection.  Error Message:", err)
        return False


# function that comparing est port to lldp port and searching if the specified port is located on Switch
def get_switch_name(lldp_lines, est_line, swirch_name):
    # spliting est line 
    etssplit = est_line.split()
   
    port = etssplit[4].split('.')[0]  # getting port from line and  deleting the last null
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
        try:
            print(f"Connecting to {switch_name}, ip: {switches[switch_name]}")
            ssh.connect(switches[switch_name], username=switch_username, password=switch_password, timeout=300)
            print("Successfully connected")
        except Exception as err:
            print(f"Error while connecting switch {switch_name}. Error Message: {err}")
            print("Returning False")
            return False, False, False, False
            
        estin, estout, est_err = ssh.exec_command(show_ethernet_switching_table)
        if estout: 
            est = estout.read().decode()
            est_lines = est.strip().split('\n')
            for est_line in est_lines:
                if mac_address in est_line:
                    lldpin, lldpout, lldperr = ssh.exec_command(show_lldp_neighbors)
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
        try:
            print(f"Connecting to switch: {sw_name}, ip: {ip}")
            ssh.connect(ip, username=switch_username, password=switch_password, timeout=300)
            print(f"Successfully Connected To  {sw_name}, {ip}")
        except Exception as err:
            print(f"Error while connecting to switch. Switch Name: {sw_name}, Ip: {ip}.   Error Message: ", err)
            # if its error while connecting to switch. we will continue work to connect Another switch
            continue
        
        # running show ethernet switching table inside the switch
        estin, estout, est_err = ssh.exec_command(show_ethernet_switching_table)
        if estout:
            # decoding output
            est = estout.read().decode()
            # spliting lines
            est_lines = est.strip().split('\n')

            for est_line in est_lines:
                if mac_address in est_line:
                    print(f"Mac address match in {sw_name},  Ip: {ip},  Mac_Address: {mac_address}")
                    # running show lldp neighbors inside the switch
                    lldpin, lldpout, lldp_err = ssh.exec_command(show_lldp_neighbors)
                    if lldpout:
                       lldpout = lldpout.read().decode()
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




