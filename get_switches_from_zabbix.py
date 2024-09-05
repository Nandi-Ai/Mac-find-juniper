from pyzabbix import ZabbixAPI
import config


server = config.server # zabbix server ip address
username = config.username # username to enter in zabbix
password = config.password # zabbix password
group_name = config.group_name # zabbix group name where switches is located.


# function that connecting to zabbix server.
def connect_to_zabbix():
    """
    Connects to the Zabbix server using the provided credentials and returns a ZabbixAPI client object.
    Returns:
        ZabbixAPI: The ZabbixAPI client object if the connection is successful.
        bool: False if there is an error while connecting to the Zabbix server.
    """
    try:
        zabbix_conn = ZabbixAPI(server)     # Create a ZabbixAPI client instance with the server URL
        zabbix_conn.login(username, password)     # Attempt to log in with the provided username and password
        print(f"Logged in successfully. Auth Token: {zabbix_conn.auth}")
        return zabbix_conn
    except Exception as err:
        print(f"Error while connecting to zabbix.    Error Message:  {err}")
        return False

# function that getting switch names and ips from zabbix server.
def get_switches_from_zabbix() -> dict:
  
    switches = {}   # define empty dictionary for to append some data inside
    switch_count = 0    # counting  switches, how many exsist inside zabbix
    zabbix_conn = connect_to_zabbix()   # connecting to zabbix server
    
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

        # loop that getting switch names and ips from hosts. and appending in dictionary
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