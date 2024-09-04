from pyzabbix import ZabbixAPI
import config


server = config.server
username = config.username
password = config.password
group_name = config.group_name

def connect_to_zabbix():
    try:
        zabbix_conn = ZabbixAPI(server)
        zabbix_conn.login(username, password)
        print(f"Logged in successfully. Auth Token: {zabbix_conn.auth}")
        return zabbix_conn
    except Exception as err:
        print(f"Error while connecting to zabbix.    Error Message:  {err}")
        return False

def get_switches_from_zabbix() -> dict:
    switches = {}
    switch_count = 0
    
    zabbix_conn = connect_to_zabbix()
    
    if zabbix_conn:
        try:
            group = zabbix_conn.hostgroup.get(filter={"name": group_name})
        except Exception as err:
            print(f"No host group found with the name '{group_name}'.  Error Message: {err}")
            return False 
        try:
            group_id = group[0]['groupid']
            hosts = zabbix_conn.host.get(groupids=group_id, output=["hostid", "name"], selectInterfaces=["ip"])
        except Exception as err:
            print(f"No hosts found in the host group: '{group_name}'.   Error Message: {err}")
            return False

        for host in hosts:
            try: 
                switch_count += 1
                for interface in host['interfaces']:
                    switches[host['name']] = interface['ip']
            except Exception as err:
                print("Error while getting data from dictionary:  ", err)
                continue
        print(f"Total {switch_count} Switch.")
        return switches
    else:
        return False


# Section for manual run
if __name__ == "__main__":
    result = get_switches_from_zabbix()
    print(result)