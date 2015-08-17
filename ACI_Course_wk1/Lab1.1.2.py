router1 = {'os_version':'3.1.1', 'hostname':'nyc_router1', 'model':'nexus 9396', 'domain':'cisco.com', 'mgmt_ip':'10.1.50.11'}
router2 = dict( os_version='3.2.1', hostname='rtp_router2', model='nexus 9396', domain='cisco.com', mgmt_ip='10.1.50.12' )
router3 = { 'os_version':'3.1.1',
			'hostname':'ROUTER3',
			'model':'nexus 9396',
			'domain':'lab.cisco.com',
			'mgmt_ip':'10.1.50.13' }

print (router1['os_version'])
print (router3['hostname'])

router2['hostname'] = '3.1.1'
print (router2['hostname'])

router3['model']='nexus 9504'
print(router3['model'])

print (router3.keys())

router2.has_key('hostname')

