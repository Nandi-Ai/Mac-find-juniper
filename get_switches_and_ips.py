from pyzabbix import ZabbixAPI


zabbix_server = "http://ip_address"
zabbix_user = "username"
zabbix_password = "password"
group_name = "groupname"

switches = {}

def get_switches_and_ips():
    try:
        zapi = ZabbixAPI(zabbix_server)
        zapi.login(zabbix_user, zabbix_password)
        print(f"Logged in successfully. Auth Token: {zapi.auth}")
    except Exception as e:
        return f"An error occurred: {e}", False
    try:
        group = zapi.hostgroup.get(filter={"name": group_name})
    except Exception as err:
        return f"No host group found with the name '{group_name}'... Error {err}", False 
    try:
        group_id = group[0]['groupid']
        hosts = zapi.host.get(groupids=group_id, output=["hostid", "name"], selectInterfaces=["ip"])
    except Exception as err:
        return f"No hosts found in the host group:'{group_name}'... Error: {err}", False

    count = 0
    for host in hosts:
        try: 
            count += 1
            for interface in host['interfaces']:
                switches[host['name']] = interface['ip']
        except Exception as err:
            print("err", err)
            continue
    print(f"Total {count} Switch...")
    return switches, True

if __name__ == "__main__":
    output, MSG = get_switches_and_ips()
    print(output)