import requests
#import json
import xmltodict
import re
import argparse
import getpass
from cobra.mit.session import LoginSession
from cobra.mit.access import MoDirectory

requests.packages.urllib3.disable_warnings()

def apic_login(session, hostname, username, password):

    auth_payload = "<aaaUser name='{}' pwd='{}'/>".format(username, password)
    session.post(hostname+'/api/aaaLogin.xml', auth_payload, verify=False)
    
def get_EPG_stats(session, url):

    r_tmp = session.get(url,verify=False)
    response = xmltodict.parse(r_tmp.content)['imdata']['l2IngrBytesAgHist15min']
    return response

def mo_apic_login(hostname, username, password):
    url = hostname
    sess = LoginSession(url, username, password)
    modir = MoDirectory(sess)
    try:
        modir.login()
    except:
        print 'Login error'
        exit(1)
    return modir

def mo_build_uri(hostname,username,password):
    
    tenant_list = []
    ap_list = []
    epg_list = []
    
    modir = mo_apic_login(hostname, username, password)

    # Ask user for tenant

    tmp_tenant_list = modir.lookupByClass('fvTenant', parentDn='uni')      
   
    for entry in tmp_tenant_list:
        tenant_list.append(str(entry.dn))
        
    tenant_list.sort()
    
    tenant_choice = -1
    while tenant_choice < 0:
        i = 0
        for i in range(0,len(tenant_list)):
            print str(i) + " : " + tenant_list[i]    
        tenant_choice = input("Please choose tenant: ")
        if tenant_choice in range(0,len(tenant_list)):
            print "you chose Tenant: " + tenant_list[tenant_choice]
        else:
            tenant_choice = -1


    # Ask user for App Pool
            
    tmp_ap_list = modir.lookupByClass('fvAp', parentDn=tenant_list[tenant_choice])      
   
    for entry in tmp_ap_list:
        ap_list.append(str(entry.dn))
        
    ap_list.sort()
    
    ap_choice = -1
    while ap_choice < 0:
        i = 0
        for i in range(0,len(ap_list)):
            print str(i) + " : " + ap_list[i]    
        ap_choice = input("Please choose AP: ")
        if ap_choice in range(0,len(ap_list)):
            print "you chose ANP: " + ap_list[ap_choice]
        else:
            ap_choice = -1
    
    
    # Ask for EPG
    
    tmp_epg_list = modir.lookupByClass('fvAEPg', parentDn=ap_list[ap_choice])      
   
    for entry in tmp_epg_list:
        epg_list.append(str(entry.dn))
        
    epg_list.sort()
    
    epg_choice = -1
    while epg_choice < 0:
        i = 0
        for i in range(0,len(epg_list)):
            print str(i) + " : " + epg_list[i]    
        epg_choice = input("Please choose EPG: ")
        if epg_choice in range(0,len(epg_list)):
            print "you chose EPG: " + epg_list[epg_choice]
        else:
            epg_choice = -1    
    
               
    modir.logout()
    
    result_dn = epg_list[epg_choice]
    
    return result_dn


if __name__ == '__main__':
    
    headerwritten = False

    parser = argparse.ArgumentParser(description='Obtain EGP traffic statistics.')
    parser.add_argument('-i', '--hostname', help='IP or hostname of APIC')
    parser.add_argument('-u', '--username', help='APIC username')
    parser.add_argument('-p', '--password', help='APIC password')
    parser.add_argument('-f', '--filename', help='Output filename')
    
    args = parser.parse_args()
    
    if args.hostname:
        hostname = args.hostname
    else: 
        hostname = raw_input("Enter Hostname: ")
        
    if not(hostname.startswith('https://')):
        hostname = "https://" + hostname
    
    if args.username:
        username = args.username
    else:
        username = raw_input("Enter Username: ")
        
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter Password: ")
        
    if args.filename:
        filename = args.filename
    else:
        filename = raw_input("Enter output filename: ")
    
    
    sess = requests.Session()    
    apic_login(sess, hostname, username, password)
    
    outfile = open(filename, 'w')
    
    dn = mo_build_uri(hostname,username,password)
    
    print "\n\n\nPulling EPG stats from " + dn

    for i in range(0,25):
        #response = get_EPG_stats(sess, hostname + '/api/node/mo/uni/tn-Commercial/ap-Sharepoint/epg-Database/HDl2IngrBytesAg15min-' + str(i) + '.xml')
        response = get_EPG_stats(sess, hostname + '/api/node/mo/' + dn + '/HDl2IngrBytesAg15min-' + str(i) + '.xml')
        
        remove_char = re.compile('^\@')
        
        # Write the header on the first row
        if not(headerwritten):
            for each in response:
                outfile.write(remove_char.sub("", each) + ",")
            outfile.write("\n")
            headerwritten = True
        
        print "Writing CSV row " + str(i)
        
        # Write data rows
        for each in response:
            outfile.write(response[each] + ",")
        outfile.write("\n")
        
    outfile.close()
            
 