# swagger_client.DefaultApi

All URIs are relative to *https://api-hosting.minet.net/2.0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_dns**](DefaultApi.md#create_dns) | **POST** /dns | create dns entry
[**create_vm**](DefaultApi.md#create_vm) | **POST** /vm | create vm
[**delete_dns_id**](DefaultApi.md#delete_dns_id) | **DELETE** /dns/{dnsid} | delete dns entry by id
[**delete_vm_id**](DefaultApi.md#delete_vm_id) | **DELETE** /vm/{vmid} | delete vm by id
[**get_dns**](DefaultApi.md#get_dns) | **GET** /dns | get all user&#x27;s dns entries
[**get_dns_id**](DefaultApi.md#get_dns_id) | **GET** /dns/{dnsid} | get a dns entry by id
[**get_historyip**](DefaultApi.md#get_historyip) | **GET** /history/{vmid} | get the ip history of a vm
[**get_historyipall**](DefaultApi.md#get_historyipall) | **GET** /historyall | get the ip history of all the vm
[**get_vm**](DefaultApi.md#get_vm) | **GET** /vm | get all user vms
[**get_vm_id**](DefaultApi.md#get_vm_id) | **GET** /vm/{vmid} | get a vm by id
[**is_cotisation_uptodate**](DefaultApi.md#is_cotisation_uptodate) | **GET** /cotisation | check is the cotisation is up to date for a user
[**patch_vm**](DefaultApi.md#patch_vm) | **PATCH** /vm/{vmid} | update a vm

# **create_dns**
> create_dns(body=body)

create dns entry

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
body = swagger_client.DnsItem() # DnsItem | Dns entry to add (optional)

try:
    # create dns entry
    api_instance.create_dns(body=body)
except ApiException as e:
    print("Exception when calling DefaultApi->create_dns: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DnsItem**](DnsItem.md)| Dns entry to add | [optional] 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_vm**
> create_vm(body=body)

create vm

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
body = swagger_client.VmItem() # VmItem | VM to create (optional)

try:
    # create vm
    api_instance.create_vm(body=body)
except ApiException as e:
    print("Exception when calling DefaultApi->create_vm: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**VmItem**](VmItem.md)| VM to create | [optional] 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_dns_id**
> delete_dns_id(dnsid)

delete dns entry by id

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
dnsid = 'dnsid_example' # str | id of the dns entry to delete

try:
    # delete dns entry by id
    api_instance.delete_dns_id(dnsid)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_dns_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dnsid** | **str**| id of the dns entry to delete | 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_vm_id**
> delete_vm_id(vmid)

delete vm by id

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
vmid = 'vmid_example' # str | vmid to get

try:
    # delete vm by id
    api_instance.delete_vm_id(vmid)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_vm_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **vmid** | **str**| vmid to get | 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dns**
> list[DnsEntryItem] get_dns()

get all user's dns entries

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))

try:
    # get all user's dns entries
    api_response = api_instance.get_dns()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_dns: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[DnsEntryItem]**](DnsEntryItem.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dns_id**
> DnsItem get_dns_id(dnsid)

get a dns entry by id

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
dnsid = 'dnsid_example' # str | id of the dns entry entry to get

try:
    # get a dns entry by id
    api_response = api_instance.get_dns_id(dnsid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_dns_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dnsid** | **str**| id of the dns entry entry to get | 

### Return type

[**DnsItem**](DnsItem.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_historyip**
> list[HistoryIdItem] get_historyip(vmid)

get the ip history of a vm

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
vmid = 'vmid_example' # str | vmid to get history

try:
    # get the ip history of a vm
    api_response = api_instance.get_historyip(vmid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_historyip: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **vmid** | **str**| vmid to get history | 

### Return type

[**list[HistoryIdItem]**](HistoryIdItem.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_historyipall**
> list[HistoryIdItem] get_historyipall()

get the ip history of all the vm

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))

try:
    # get the ip history of all the vm
    api_response = api_instance.get_historyipall()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_historyipall: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[HistoryIdItem]**](HistoryIdItem.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_vm**
> list[VmIdItem] get_vm()

get all user vms

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))

try:
    # get all user vms
    api_response = api_instance.get_vm()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_vm: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[VmIdItem]**](VmIdItem.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_vm_id**
> VmItem get_vm_id(vmid)

get a vm by id

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
vmid = 'vmid_example' # str | vmid to get

try:
    # get a vm by id
    api_response = api_instance.get_vm_id(vmid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_vm_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **vmid** | **str**| vmid to get | 

### Return type

[**VmItem**](VmItem.md)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **is_cotisation_uptodate**
> is_cotisation_uptodate()

check is the cotisation is up to date for a user

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))

try:
    # check is the cotisation is up to date for a user
    api_instance.is_cotisation_uptodate()
except ApiException as e:
    print("Exception when calling DefaultApi->is_cotisation_uptodate: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_vm**
> patch_vm(vmid, body=body)

update a vm

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: OAuth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
vmid = 'vmid_example' # str | vmid to update
body = swagger_client.VmItem() # VmItem | VM to update (optional)

try:
    # update a vm
    api_instance.patch_vm(vmid, body=body)
except ApiException as e:
    print("Exception when calling DefaultApi->patch_vm: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **vmid** | **str**| vmid to update | 
 **body** | [**VmItem**](VmItem.md)| VM to update | [optional] 

### Return type

void (empty response body)

### Authorization

[OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

