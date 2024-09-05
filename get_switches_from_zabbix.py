from pyzabbix import ZabbixAPI
import config

# zabbix server ip address
server = config.server
# username to enter in zabbix
username = config.username
# zabbix password
password = config.password
# zabbix group name where switches is located.
group_name = config.group_name


# function that connecting to zabbix server.
def connect_to_zabbix():
    try:
        zabbix_conn = ZabbixAPI(server)
        zabbix_conn.login(username, password)
        print(f"Logged in successfully. Auth Token: {zabbix_conn.auth}")
        return zabbix_conn
    except Exception as err:
        print(f"Error while connecting to zabbix.    Error Message:  {err}")
        return False

# function that getting switch names and ips from zabbix server.
def get_switches_from_zabbix() -> dict:
    # define empty dictionary for to append some data inside
    switches = {}
    # counting  switches, how many exsist inside zabbix
    switch_count = 0
    # connecting to zabbix server
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