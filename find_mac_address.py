import paramiko
import argparse
import config
from get_switches_from_zabbix import get_switches_from_zabbix


# enter your switch names and ips
switches = {
            'Switch_1': 'ip Adress',
            'Switch_2': 'ip Adress', 
            'Switch_3': 'ip Adress',  
           }

switch_username = config.switch_username
switch_password = config.switch_password

show_lldp_neighbors = config.show_lldp_neighbors
show_ethernet_switching_table = config.show_ethernet_switching_table


# connect to ssh.
def ssh_connect():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return ssh
    except Exception as err:
        print("Error While Estabilish To ssh Connection.  Error Message:", err)
        return False


def get_switch_name(lldp_lines, est_line, swirch_name):
    etssplit = est_line.split()
    port = etssplit[4].split('.')[0]
    vlan = etssplit[0]            
    
    if  port[:2] == "ae":
        return False, port, vlan, False
    
    for lldp_line in lldp_lines:
        lldp_port = lldp_line.split()[0]
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
      
            
def jumping_switch_to_switch(switch_name, mac_address, ssh):
    while True:
        try:
            print(f"Connecting to {switch_name}, ip: {switches[switch_name]}")
            ssh.connect(switches[switch_name], username=switch_username, password=switch_password, timeout=300)
            print("Successfully connected")
        except Exception as err:
            print(f"error while connecting switch {switch_name} ip: {switches[switch_name]}. Error Message: {err}")
            continue
            
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

def find_mac_address(ssh, mac_address: str) -> dict:
        
    for sw_name, ip in switches.items():
        try:
            print(f"Connecting to switch: {sw_name}, ip: {ip}")
            ssh.connect(ip, username=switch_username, password=switch_password, timeout=300)
            print(f"Successfully Connected To  {sw_name}, {ip}")
        except Exception as err:
            print(f"Error while connecting to switch. Switch Name: {sw_name}, Ip: {ip}.   Error Message: ", err)
            continue
            
        estin, estout, est_err = ssh.exec_command(show_ethernet_switching_table)
        if estout:
            # decoding output
            est = estout.read().decode()
            # spliting lines
            est_lines = est.strip().split('\n')

            for est_line in est_lines:
                if mac_address in est_line:
                    print(f"Mac address match in {sw_name}, ip: {ip}, Mac_Address: {mac_address}")
                    lldpin, lldpout, lldp_err = ssh.exec_command(show_ethernet_switching_table)
                    if lldpout:
                       lldpout = lldpout.read().decode()
                       lldp_lines = lldpout.strip().split('\n')
                       
                       switch_name, port, vlan, status = get_switch_name(lldp_lines, est_line, sw_name)
                       if switch_name == False:
                           break
                       if status == False:
                           sw_n, port, vlan, status = jumping_switch_to_switch(switch_name, mac_address, ssh)
                           ssh.close()
                           return {"SWITCH_NAME": sw_n,
                                   "PORT": port,
                                   "VLAN": vlan
                                }
                       else:
                           print("couldn't find the switch in the lldp... connecting to next switch...")
                           break
                    elif lldp_err:
                        print("error while getting data from lldp... ", lldp_err)
        elif lldp_err:
            print("error while getting data from est...", lldp_err)
                  

parser = argparse.ArgumentParser()
parser.add_argument('-m', required=True, help="Mac Address")
args = parser.parse_args()


if __name__ == "__main__":
    result = get_switches_from_zabbix()
    if result:
        print("Using latest switch names and ips from zabbix server")
        switches = result
    else:
        print("Using locall switch names and ips")
        
    ssh = ssh_connect()
    if ssh:                     
        output = find_mac_address(ssh, args.m)
        if output:    
            print("****** Completed ******")
            print(output)




