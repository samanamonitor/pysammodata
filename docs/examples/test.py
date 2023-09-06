import os
import pyodata
from requests import Session
from requests_ntlm import HttpNtlmAuth
import sys, logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
s = Session()
s.headers.update({'MaxDataServiceVersion': '2.0'})
username = environ['PYODATA_NTLM_USERNAME']
password = environ['PYODATA_NTLM_PASSWORD']
host_address = environ['PYODATA_HOSTADDRESS']
auth=HttpNtlmAuth(username, password)
s.auth = auth
SERVICE_URL='http://%s/citrix/monitor/odata/v2/Data/' % host_address
client = pyodata.Client(SERVICE_URL, s)
es=client.entity_sets
m_proxy=es.Machines.get_entity("c414a606-4a52-45a0-b1da-60ce9fedbcef")
m=m_proxy.execute()



aas=es.ApplicationActivitySummaries.get_entity(64).execute()
app=aas.nav('Application').execute()
ai=(es.ApplicationInstances.get_entities())
data=ai.execute()
session=data[0].nav('Session').execute()
session._entity_set=session._service.schema.entity_set('Sessions')
user_proxy=session.nav('User')
user=user_proxy.execute()





an=m._entity_set.entity_type.nav_proprty('Sessions')._association_info.name
m._service.schema._decls['Citrix.Monitor.Repository.V2'].association_sets[an]
association_set._end_roles[0].entity_set



ConnectionState_enum = [ 
	'Unknown', 
	'Connected', 
	'Disconnected', 
	'Terminated', 
	'PreparingSession', 
	'Active', 
	'Reconnecting', 
	'NonBrokeredSession', 
	'Other', 
	'Pending' 
	]
sessions=es.Sessions.get_entities().filter("ConnectionState ne 3'").execute()
def test():
	for s in sessions:
	  u=s.User.execute()
	  cc=s.CurrentConnection.execute()
	  m=s.Machine.execute()
	  print(s.SessionKey, ConnectionState_enum[int(s.ConnectionState)], 
	  	u.Upn, m.DnsName, cc.LogOnEndDate-cc.LogOnStartDate, s.LogOnDuration)

current_sessions=es.Sessions.get_entities().filter("ConnectionState ne 3").expand("User,CurrentConnection,Machine").execute()
es.SessionActivitySummaries.get_entities().order_by("Id desc").top(1).execute()

entity="Machines"
instance_param="DnsName"
tags=[ 
	"Catalog.Name",
	"DesktopGroup.Name",
	"DnsName",
	"IsInMaintenanceMode",
	]
metrics= [
	"CurrentLoadIndex.EffectiveLoadIndex",
	"CurrentLoadIndex.Cpu",
	"CurrentLoadIndex.Memory",
	"CurrentLoadIndex.Disk",
	"CurrentLoadIndex.Network",
	"CurrentLoadIndex.SessionCount",
	"CurrentSessionCount",
	"CurrentRegistrationState"
]
expand="Catalog,DesktopGroup,CurrentLoadIndex"

def get_fromstring(o, s):
	for i in s.split('.'):
		if o is None: return o
		o=o.__getattr__(i)
	return o

def get_metrics(m, instance_param, metrics, tags, expand):
	tagstring = ""
	data=""
	for t in tags:
		d=get_fromstring(m, t)
		if d is None: continue
		tagstring += "%s=\"%s\"," % (t.lower(), d)
	for metric in metrics:
		d=get_fromstring(m, metric)
		if d is None: continue
		data += "%s(%s) %s\n" % (metric.lower(), tagstring, d)
	return data

all_machines=es.__getattr__(entity).get_entities().expand(expand).execute()
for m in all_machines:
	if m.Name is None or m.Name == '': continue
	get_metrics(m, instance_param, metrics, tags, expand)

get_metrics(entity, instance_param, metrics, tags, expand)





from sammodata import OdataQuery
username = environ['PYODATA_NTLM_USERNAME']
password = environ['PYODATA_NTLM_PASSWORD']
instance_address = environ['PYODATA_HOSTADDRESS']
SERVICE_URL='http://%s/citrix/monitor/odata/v2/Data/' % instance_address
odq=OdataQuery(SERVICE_URL, auth_protocol='ntlm', username=username, password=password, entity='Machines', expand="Catalog,DesktopGroup,CurrentLoadIndex", filter="Name ne null")
i=iter(odq)
d=next(i)
d=next(i)
d['Catalog.Name']

odq=OdataQuery(SERVICE_URL, auth_protocol='ntlm', username=username, password=password, entity='Sessions', filter="ConnectionState ne 3", expand="User,CurrentConnection,Machine")

odq=OdataQuery(SERVICE_URL, auth_protocol='ntlm', username=username, password=password, entity='Catalogs')




