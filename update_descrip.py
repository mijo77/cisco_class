#!/usr/bin/env python
"""
    update_descrip.py

    M. Odom, S. Sloan, S. Tsai, D. Virk

    Obtains the MAC and ARP tables from NX-OS to determine which IP address is present on a switchport,
    then executes a DNS query to attempt to resolve the hostname.
    If a hostname can be resolved, update the switchport description field.
    
    This script does not understand VRF or handle multiple IP's on a switchport
"""
from socket import gethostbyaddr
from device import Device
import json
import xmltodict


def get_mac(sw):
    """
     Obtain the mac address-table from NX-OS.  Not VRF aware.
    
     Input parameter: sw  -- Device object that is already .open()
    
     Returns a hash with the MAC address as the key and the port as the value.
     Values are stored in the same format returned by NX-OS
     ex { '1234.5678.90ab' : 'Ethernet1/1' }
    """
    
    result = {}

    getdata = sw.show('show mac address-table')
    show_mac = xmltodict.parse(getdata[1])
    data = show_mac['ins_api']['outputs']['output']['body']['TABLE_mac_address']['ROW_mac_address']

    for each in data:
        result[each['disp_mac_addr']] = each['disp_port']

    return result

def get_arp(sw):
    """
     Obtain the arp table from NX-OS.  Not VRF aware.
    
     Input parameter: sw -- Device object that is already .open()
    
     Returns a hash with the MAC address as the key and the IP Address as the value.
     Values are stored in the same format returned by NX-OS
     ex { '1234.5678.90ab' : '10.10.10.10' }
    """
    
    result={}
    
    getdata = sw.show('show ip arp')

    show_sw_dict = xmltodict.parse(getdata[1])

    arp_dict = show_sw_dict['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']['TABLE_adj']['ROW_adj']

    for each in arp_dict:
        if 'mac' in each:
            key =  each['mac']
            value =  each['ip-addr-out']
            result[key] = value


    return result

def write_descript(sw,intf,text):
    """
     Update description field of the specified interface (intf) with text
     
     Input parameters:
     sw  -- Device object that is already .open()
     intf -- String of the interface to update
     text -- String of the hostname to apply to the description of the interface     
    """
    
    command = 'conf t ; interface ' + intf + ' ; description *** AutoGen: Attached host is ' + text + " *** ;"
    
    sw.conf(command)

    return

def main():

    switch = Device(ip='172.31.217.133',username='admin',password='cisco123')
    switch.open()

    mac_table = get_mac(switch)
    arp_table = get_arp(switch)

    print "Will parse the following MAC and ARP tables obtained from the switch:"
    print json.dumps(mac_table, indent=4)   
    print json.dumps(arp_table, indent=4)
    
    # Loop through the MAC address table
    for mac_entry in mac_table:
        # If the MAC address is present in the ARP table
        if mac_entry in arp_table:

            #Attempt name resolution.  gethostbyaddr will throw an exception if host is not found
            try:
                
                ip_address = arp_table[mac_entry]
                interface_name = mac_table[mac_entry]
                
                hostname = gethostbyaddr(ip_address)
                
                print hostname[0] + " (" + ip_address + ") is on " + interface_name
                
                # Pass the result to write_descript to apply the hostname to the NX-OS interface
                write_descript(switch,interface_name,hostname[0])
                
            except:
                # For simplicity, we will assume that any exception is a host not found and move on
                print "No hostname for " + ip_address + " was found... skipping"



if __name__ == "__main__":
    main()

