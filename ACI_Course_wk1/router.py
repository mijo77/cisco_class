#!/usr/bin/python


if __name__ == "__main__":
    print ('It is about time I started programming.')

def getRouter(rtr):
    router1 = {'os_version':'3.1.1', 'hostname':'nyc_router1', 'model':'nexus 9396', 'domain':'cisco.com', 'mgmt_ip':'10.1.50.11'}
    router2 = dict( os_version='3.2.1', hostname='rtp_router2', model='nexus 9396', domain='cisco.com', mgmt_ip='10.1.50.12' )
    router3 = { 'os_version':'3.1.1',
               'hostname':'ROUTER3',
               'model':'nexus 9396',
               'domain':'lab.cisco.com',
               'mgmt_ip':'10.1.50.13' }
    
    router_list = [router1,router2,router3]
    
    if rtr in router_list:
        return router1
    return 'No router found.'