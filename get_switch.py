import paramiko
import argparse

from get_switches_and_ips import get_switches_and_ips


switches = {
            'Juniper-3400-BB-FL-13': '172.28.150.15', 
            'Floor-14-down': '172.28.150.3', 
            'Floor-14-up': '172.28.150.2', 
            'Corp-User-SW-EX2200-48T': '172.28.150.9',
            'EX4600-Corp-Cluster': '70.2.3.51',
            'Corp-EX2300-UHJ': '172.29.50.55',
            'Juniper-Novis': '192.168.27.200', 
            'ESX-3400-Corp-Servers': '172.28.150.17',
            'Netapp-10G-SW': '172.28.150.7', 
            'Servers-SW-M0': '172.29.50.62', 
            'Juniper-User-SW-2-13': '172.28.150.14',
            'Corp-SW-USERS-M11': '172.29.50.31',
            'EX2300-48-KCR-M8': '172.29.50.48', 
            'Corp-EX2300-NBW': '70.2.3.57',
            'Corp-SW-USERS-POJ': '172.29.50.128',
            'M7_1': '70.2.92.202', 
            'Corp-EX2200-M1': '70.2.3.64', 
            'Corp-M6-1-EX2300-24': '172.29.50.25', 
            'Corp-M1-EX2200-48T': '172.29.50.28',
            'Corp-C-LLK': '172.29.50.124', 
            'Corp-B-122': '172.29.50.122', 
            'Corp-FLOOR-13-EX2300-48P': '172.28.150.11',
            'Pineapp': '10.2.51.10', 
            'Corp-EX3300-M4': '172.29.50.29',
            'Corp-M4-EX2300-24T': '172.29.50.22',
            'Corp-M10-24': '70.2.101.19', 
            'Corp-M1-EX2200-24T': '172.29.50.21',
            'Corp-M3-EX2300-48T': '172.29.50.16', 
            'NetApp-Hod': '80.2.10.233', 
            'Netapp-Corp': '70.2.11.16',
            'Corp-FL14-EX2300-24P': '172.28.150.8',
            'Corp-M6_2-EX2300-24': '172.29.50.24',
            'Corp-EX3300-M6': '70.2.101.3', 
            'Wifi-FL13-SW': '172.28.110.1', 
            'Wifi-SW-FL14': '172.28.110.2', 
            'Corp-B-EX2300-24': '172.29.50.71',
            'Corp-DVR-SW-1': '70.2.101.41', 
            'Corp-C1-2300-24': '172.29.50.33', 
            'Corp-C-2300-24-2': '172.29.50.44',
            'Corp-POE-C-2300-24P': '172.29.50.47',
            'Corp-M5-8UFG': '172.29.50.26', 
            'USB-DGL-1': '70.2.5.203',
            'USB-DGL-2': '70.2.5.204',
            'Corp-Steam-SW': '172.29.50.72', 
            'Corp-M6-3-EX2200-24T': '172.29.50.91'
        }


Username = "xxx"
Password = "XXXX"

show_lldp = "show lldp neighbors"
show_est = "show ethernet-switching table"


# connect to ssh.
def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return ssh

def get_sw_name(lldp_lines, est_line, s_name):
    # lldp_lines = lldpout.strip().split('\n')
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
                print(f"Switch_Name: {s_name}, Port: {port}, Vlan: {vlan}")
                exit(0)
            if len(sw_name) > 0:
                print(f"Found switch :   {sw_name}")
                return sw_name, port, vlan, False
            else:
                return sw_name, port, vlan, True
    print("Finish...")
    return s_name, port, vlan, True
      
            
def jmp_to_sw(switch_name, mac_address, ssh):
    print("starting function jump to switch")
    while True:
        try:
            print(f"Connecting ssh to  Switch: {switch_name}, IP: {switches[switch_name]}")
            ssh.connect(switches[switch_name], username=Username, password=Password, timeout=300)
            print("Successfully connected")
        except Exception as err:
            print(f"error while connecting switch... sw_name: {switch_name} ip: {switches[switch_name]}... error msg: ", err)
            continue
            
        estin, estout, esterr = ssh.exec_command(show_est)
        if estout:
            est_table = estout.read().decode()
            est_lines = est_table.strip().split('\n')
            for est_line in est_lines:
                if mac_address in est_line:
                    lldpin, lldpout, lldperr = ssh.exec_command(show_lldp)
                    if lldpout: 
                        lldpout1 = lldpout.read().decode()
                        lldp_lines = lldpout1.strip().split('\n')
                        s_name, port, vlan, bool = get_sw_name(lldp_lines, est_line, switch_name)
                        if bool:
                            return s_name, port, vlan, bool
                        else:
                            if s_name == False:
                                print("jumping to next switch in dict")
                                keys = list(switches.keys())
                                current_index = keys.index(switch_name)
                                next_sw = keys[current_index + 1]
                                switch_name = next_sw
                                break
                            else:
                                switch_name = s_name
                                break

def get_sys_name(ssh, mac_address):
        
    for sw_name, ip in switches.items():
        try:
            print(f"Connecting ssh to switch: {sw_name}, ip: {ip}")
            ssh.connect(ip, username=Username, password=Password, timeout=300)
            print("Successfully connected...")
        except Exception as err:
            print(f"Error while connecting to switch. continue... SW_NAME: {sw_name}, IP: {ip} ...  Error msg:", err)
            continue
            
        estin, estout, esterr = ssh.exec_command(show_est)
        if estout:
            est_table = estout.read().decode()
            est_lines = est_table.strip().split('\n')

            for est_line in est_lines:
                if mac_address in est_line:
                    print(f"Mac address match on... Switch_Name: {sw_name}, Ip: {ip}, Mac_Address: ", mac_address)
                    lldpin, lldpout, lldperr = ssh.exec_command(show_lldp)
                    if lldpout:
                       lldpout = lldpout.read().decode()
                       lldp_lines = lldpout.strip().split('\n')
                       
                       switch_name, p, v, bool = get_sw_name(lldp_lines, est_line, sw_name)
                       if switch_name == False:
                           break
                       if bool == False:
                           sw_n, port, vlan, bool = jmp_to_sw(switch_name, mac_address, ssh)
                           ssh.close()
                           return {"SWITCH_NAME": sw_n,
                                   "PORT": port,
                                   "VLAN": vlan
                                }
                       else:
                           print("couldn't find the switch in the lldp... connecting to next switch...")
                           break
                    elif lldperr:
                        print("error while getting data from lldp... ", lldperr)
        elif esterr:
            print("error while getting data from est...", esterr)
        
        
def main(mac_address: str):
    print("Starting main function...")
    ssh = ssh_connect()
    if ssh:
        output = get_sys_name(ssh, mac_address)
        return output
    else:
        print("Error while connecting to ssh...")
        

parser = argparse.ArgumentParser()
parser.add_argument('-m', required=True, help="Mac Address")
args = parser.parse_args()



if __name__ == "__main__":
    SW, MSG= get_switches_and_ips()
    if MSG:
        print("Using latest switch  names and ips")
        switches = SW
        output = main(args.m) 
        print(output)
    else:
        print("Using old locall switch names and ips")
        output = main(args.m) 
        print(output)




