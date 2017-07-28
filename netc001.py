#!/usr/bin/python3
# Demonstrates netconf using ncclient

from ncclient import manager
from xml.dom import minidom
import xmltodict
import json

# Note: I am using an always-on sandbox from https://devnetsandbox.cisco.com/
host = "ios-xe-mgmt.cisco.com"
username = "root"
password = "D_Vay!_10&"
port = 10000

# Connect to the host
# note: look_for_keys=False, allow_agent=False, hostkey_verify=False are there to deal with certificate
with manager.connect(host=host, port=port, username=username, password=password,
                     look_for_keys=False, allow_agent=False, hostkey_verify=False,
                     device_params={'name': 'default'}) as m:

    # This will be use for filtering interface
    xml_filter = '''
                <filter>
                    <interfaces>
                    </interfaces>
                </filter>
                '''

    # Get information from running command and use the filter so it will only get XML under interfaces
    # You can remove the filter argument if you want to see the whole config in XML
    # You can then get an idea of which elements you can filter
    result = m.get_config(source='running', filter=xml_filter)

    
    # Printing part

    # Print the filtered result in a pretty XML format
    print("XML----------------------------------------------------------")
    print(minidom.parseString(result.xml).toprettyxml())

    # Print in json format# Print the filtered result in a indented JSON format
    root = xmltodict.parse(result.xml)
    print("JSON---------------------------------------------------------")
    print(json.dumps(root['rpc-reply']['data']['interfaces']['interface'], indent=4))

    # Get ietf-interfaces YANG model schema
    my_schema = m.get_schema('ietf-interfaces')
    print("YANG---------------------------------------------------------")
    print(my_schema)


    # Parse the result so I can get and print IP address information of each interface
    # I am basically converting XML to dict since I find it really easy for me to understand dictionaries than XML
    print("INTERFACES---------------------------------------------------")
    root = xmltodict.parse(result.xml)
    for elements in root['rpc-reply']['data']['interfaces']['interface']:
        print("----------------------------------------------------------")
        print("Interface Name: %s" % elements['name'])
        print("\tEnabled: %s" % elements['enabled'])

        # Print description if there's any
        try:
            print("\tDescription: %s" % elements['description'])
        except:
            print("\tDescription: N/A")

        # print IPV4 ip address and netmask if it exists
        print("\tIPV4")
        try:
            print("\t\tIP: %s" % elements['ipv4']['address']['ip'])
            print("\t\tSubnet: %s" % elements['ipv4']['address']['netmask'])
        except:
            print("\t\tN/A")

        # print IPV6 ip address if it exists
        print("\tIPV6")
        try:
            print("\t\tIP: %s" % elements['ipv6']['address']['ip'])
        except:
            print("\t\tN/A")