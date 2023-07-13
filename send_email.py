# Name: get email of user from AD
# Task Type: set variable
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 11-08-2021
# Description:

import requests

# General script settings
# --------------------------------------------------
# General script settings
# --------------------------------------------------
webhook_id = 'ba0e9e2c-73db-41d1-8318-7efd82b98278'

subject = 'Hello from escript'
body = '''
Hello world

'''

# -------------- Test Environment ------------------


import urllib3
urllib3.disable_warnings()
authorization = 'Basic xxxx'
url = 'https://10.38.11.9:9440/api/nutanix/v3/{}'
username = 'husain@dc1.demo'

# -------------- Calm Environment ------------------
# authorization = 'Bearer @@{calm_jwt}@@'
# url = 'https://127.0.0.1:9440/api/nutanix/v3/{}'
# username = '@@{calm_username}@@'


kwargs = {
    'verify': False,
    'headers': {'Authorization': authorization}
}

# check if logged in user is domain user
if '@' not in username:
    print('INFO - logged in user {} not domain based, stopping script')
    exit(0)

# obtain domain name
domain_name = username[username.find('@')+1:]

# find domain uuid on Prism
payload = {'kind': 'directory_service'}
r = requests.post(url.format('directory_services/list'), json=payload, **kwargs)
directory_service_uuid = None
if r.status_code == 200:
    for entity in r.json()['entities']:
        if entity['spec']['resources']['domain_name'] == domain_name:
            directory_service_uuid = entity['metadata']['uuid']
            print('INFO - Found directory service uuid: {} for doamin {}'.format(directory_service_uuid, domain_name))
else:
    print('ERROR - API call failed, status code: {}, message: {}'.format(r.status_code, r.content))


# get email ID from directory service
payload = {
    'query': username,
    'returned_attribute_list': ['mail'],
    'searched_attribute_list': ['userPrincipalName'],
    'is_wildcard_search': True
}
r = requests.post(url.format('directory_services/'+directory_service_uuid+'/search'), json=payload, **kwargs)
user_email = None
if r.status_code == 200:
    if len(r.json()['search_result_list']):
        for attribute in r.json()['search_result_list'][0]['attribute_list']:
            if attribute['name'] == 'mail':
                user_email = attribute['value_list'][0]
                print('INFO - found email for user {}, {}'.format(username, user_email))
else:
    print('ERROR - API call failed, status code: {}, message: {}'.format(r.status_code, r.content))

if not user_email:
    print('INFO - No mail found for the user')
    exit(0)


payload = {
    'trigger_type': 'incoming_webhook_trigger',
    'trigger_instance_list': [{
        'webhook_id': webhook_id,
        'string1': user_email,
        'string2': subject,
        'string3': body
    }]
}

r = requests.post(url.format('action_rules/trigger'), json=payload, **kwargs)
print('Email api status code: {}, result: {}'.format(r.status_code, r.content))