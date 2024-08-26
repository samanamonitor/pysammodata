from pyodata import Client
from pyodata.v2.service import EntityProxy
from requests import Session
from requests_ntlm import HttpNtlmAuth
import sys, logging
from datetime import datetime

def dict_from_entity_proxy(entity_proxy):
    if not isinstance(entity_proxy, EntityProxy):
        return None
    data = {}
    cache = entity_proxy._cache
    for i in cache.keys():
        if isinstance(cache[i], EntityProxy):
            data[i] = dict_from_entity_proxy(cache[i])
        elif isinstance(cache[i], list):
            data[i] = []
            for j in cache[i]:
                if isinstance(j, EntityProxy):
                    data[i].append(dict_from_entity_proxy(j))
                else:
                    data[i].append(j)
        elif isinstance(cache[i], datetime):
            data[i] = cache[i].timestamp()
        else:
            data[i] = cache[i]
    return data

def value_from_entity_proxy(entity_proxy, key):
    if not isinstance(entity_proxy, EntityProxy):
        raise TypeError("Expecting EntityProxy class as input")
    if not isinstance(key, str):
        raise KeyError
    keylist = key.split(".", 1)
    value = entity_proxy.__getattr__(keylist[0])
    if not isinstance(value, EntityProxy):
        if value is None:
            raise KeyError("Invalid value for key %s" % key)
        if isinstance(value, datetime):
            return value.timestamp() * 1000
        return value
    if len(keylist) < 2:
        raise KeyError("Invalid key %s" % key)
    return value_from_entity_proxy(value, keylist[1])

def key_in_entity_proxy(entity_proxy, key):
    if not isinstance(entity_proxy, EntityProxy):
        raise ValueError
    keylist = key.split(".", 1)
    if len(keylist) == 0:
        return False
    if not keylist[0] in entity_proxy._cache:
        return False
    if len(keylist) == 1:
        return True
    value = entity_proxy.__getattr__(keylist[0])
    if isinstance(value, EntityProxy):
        return key_in_entity_proxy(value, keylist[1])
    else:
        return False


class OdataEntry:
    def __init__(self, entry):
        if not isinstance(entry, EntityProxy):
            raise TypeError
        self._entry = entry

    def __contains__(self, key):
        key_in_entity_proxy(self._entry, key)

    def get(self, key, default=None):
        try:
            return value_from_entity_proxy(self._entry, key)
        except KeyError:
            return default

    def __getitem__(self, key):
        return value_from_entity_proxy(self._entry, key)

    def __iter__(self):
        return iter(self.__dict__.items())

    @property
    def __dict__(self):
        return dict_from_entity_proxy(self._entry)


class OdataQuery:
    def __init__(self, service_url=None, auth_protocol=None, username=None, password=None,
            entity=None, filter=None, expand=None):
        if not isinstance(service_url, str) or service_url == '':
            raise TypeError("service_url must be str")
        if not isinstance(entity, str) or entity == '':
            raise TypeError("Invalid entity")

        self._service_url = service_url
        self._http_session = Session()
        self._http_session.headers.update({'MaxDataServiceVersion': '2.0'})
        self._entity = entity
        if isinstance(auth_protocol, str) and auth_protocol == 'ntlm':
            if not username or username == '':
                raise TypeError("Invalid username")
            if not password or password == '':
                raise TypeError("Invalid password")
            self._http_session.auth = HttpNtlmAuth(username, password)
        else:
            raise TypeError("Invalid authentication protocol %s" % auth_protocol)

        self._expand = expand
        self._filter = filter

        
    def __iter__(self):
        self._client = Client(self._service_url, self._http_session)
        self._entity_set_request = self._client.entity_sets.__getattr__(self._entity).get_entities()
        if self._expand:
            self._entity_set_request.expand(self._expand)
        if self._filter:
            self._entity_set_request.filter(self._filter)
        self._entity_set = self._entity_set_request.execute()
        self._es_iterator = iter(self._entity_set)
        return self

    def __next__(self):
        return OdataEntry(next(self._es_iterator))


    def _get_fromstring(o, s):
        for i in s.split('.'):
            if o is None: return o
            o=o.__getattr__(i)
        return o
