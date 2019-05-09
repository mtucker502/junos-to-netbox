def iter_units(interface_name, interface_data):
    if 'units' in interface_data.keys():
        for unit, unit_data in interface_data['units'].items():
            if 'vlan' in unit_data.keys():
                vlan_name = 'vlan{}'.format(unit_data['vlan'])
                try:
                    vid = netbox.ipam.get_vlans(name=vlan_name)[0]['id']
                except IndexError:
                    netbox.ipam.create_vlan(vid=unit_data['vlan'], vlan_name=vlan_name)
                    vid = netbox.ipam.get_vlans(name=vlan_name)[0]['id']

                vid_list = []
                vid_list.append(str(vid))
                try:
                    netbox.dcim.create_interface(name='{0}.{1}'.format(interface_name, unit),
                                                 form_factor='0',
                                                 device_id=device_id,
                                                 tagged_vlans=vid_list)
                except CreateException as err:
                    if 'unique set' in str(err):
                        pass
                    else:
                        print(err)
            else:
                try:
                    netbox.dcim.create_interface(name='{0}.{1}'.format(interface_name, unit),
                                                 form_factor='0',
                                                 device_id=device_id)
                except CreateException as err:
                    if 'unique set' in str(err):
                        pass
                    else:
                        print(err)
            interface_id = netbox.dcim.get_interfaces(device=device_hostname, name='{0}.{1}'.format(interface_name, unit))[0]['id']
            for key, value in unit_data.items():
                for address in value:
                    try:
                        ip_id = netbox.ipam.get_ip_addresses(address=address)[0]['id']
                    except IndexError:
                        netbox.ipam.create_ip_address(address=address, interface=interface_id)

if __name__ == '__main__':
    from junos_tools import JunosConfig
    from netbox import NetBox
    from netbox.exceptions import CreateException
    from pprint import pprint
    import sys

    with open(sys.argv[1], 'r') as stream:
        conf = JunosConfig(stream.read())

    conf.parse_config()

    # Create:
    # Manufacturer Name: "Juniper Networks" slug: "juniper-networks"
    # Device Type Name: "SRX5800" slug: "srx5800"
    # Device role Name: "Firewall" slug: "firewall" color: "Dark Red" (aa1409)
    # Site Name: "Concord" slug: "concord"

    # Create Device: name, device_role, manufacturer, model_name, site

    manufacturer = {}
    device_type = {}
    device_role = {}
    device_site = {}
    device_hostname = conf.hostname

    manufacturer['name'] = 'Juniper Networks'
    manufacturer['slug'] = 'juniper-networks'
    device_type['model'] = 'SRX5800'
    device_type['slug'] = 'srx5800'
    device_role['name'] = 'Firewall'
    device_role['slug'] = 'firewall'
    device_role['color'] = 'aa1409'
    device_site['name'] = 'Florida'
    device_site['slug'] = 'florida'

    interface_types = {}
    interface_types['ge'] = '1000'
    interface_types['ae'] = '200'
    interface_types['xe'] = '1150'
    interface_types['fx'] = '0'
    interface_types['re'] = '200'

    netbox = NetBox(host='127.0.0.1', port=32768, use_ssl=False, auth_token='0123456789abcdef0123456789abcdef01234567')

    try:
        netbox.dcim.create_manufacturer(name=manufacturer['name'],
                                        slug=manufacturer['slug'])
    except CreateException as err:
        if 'already exist' in str(err):
            pass
        else:
            print(err)
    manufacturer['id'] = netbox.dcim.get_manufacturers(name=manufacturer['name'])[0]['id']

    try:
        netbox.dcim.create_device_type(model=device_type['model'],
                                       slug=device_type['slug'],
                                       manufacturer=manufacturer['id'])
    except CreateException as err:
        if 'unique set' in str(err):
            pass
        else:
            print(err)
    device_type['id'] = netbox.dcim.get_device_types(model=device_type['model'])[0]['id']

    try:
        netbox.dcim.create_device_role(name=device_role['name'],
                                       slug=device_role['slug'],
                                       color=device_role['color'])
    except CreateException as err:
        if 'already exist' in str(err):
            pass
        else:
            print(err)
    device_role['id'] = netbox.dcim.get_device_roles(name=device_role['name'])[0]['id']

    try:
        netbox.dcim.create_site(name=device_site['name'],
                                slug=device_site['slug'])
    except CreateException as err:
        if 'already exist' in str(err):
            pass
        else:
            print(err)
    device_site['id'] = netbox.dcim.get_sites(name=device_site['name'])[0]['id']

    try:
        netbox.dcim.create_device(name=device_hostname,
                                  device_role=device_role['name'],
                                  device_type=device_type['model'],
                                  site_name=device_site['name'])
    except CreateException as err:
        if 'already exist' in str(err):
            pass
        else:
            print(err)
    device_id = netbox.dcim.get_devices(name=device_hostname)[0]['id']

    # Create Parent LAGs first
    for interface_name, interface_data in conf.interfaces.items():
        # Regular interface
        if 'parent' not in interface_data.keys():
            try:
                netbox.dcim.create_interface(name=interface_name, form_factor=interface_types[interface_name[0:2]], device_id=device_id)
            except CreateException as err:
                if 'unique set' in str(err):
                    pass
                else:
                    print(err)
            iter_units(interface_name, interface_data)
        # LAG interface
        elif 'ae' in interface_name or 'reth' in interface_name:
            try:
                netbox.dcim.create_interface(name=interface_name, form_factor='200', device_id=device_id)
            except CreateException as err:
                if 'unique set' in str(err):
                    pass
                else:
                    print(err)
            iter_units(interface_name, interface_data)

    for interface_name, interface_data in conf.interfaces.items():
        # Child interface
        if 'parent' in interface_data.keys():
            parent_id = netbox.dcim.get_interfaces(device=device_hostname, name=interface_data['parent'])[0]['id']
            try:
                netbox.dcim.create_interface(name=interface_name, form_factor=interface_types[interface_name[0:2]], device_id=device_id, lag=parent_id)
            except CreateException as err:
                if 'unique set' in str(err):
                    pass
                else:
                    print(err)
