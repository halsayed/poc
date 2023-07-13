# region headers
# -----------------------------------------------
# Name: Generate VM name based on xxx naming
# Task Type: set variable
# Script Type: EScript
# Author: Husain Ebrahim <husain.ebrahim@nutanix.com>
# Date: 01-08-2021
# Description:  The script will obtain the cluster name/environment name and generate a VM name based on ELM naming
#               Beside the name, assuming cluster name is already selected in NETWORK_TARGET
# endregion

# region general settings
# -----------------------------------------------
vm_identifier = 'VM1'
vm_name = ''
os_type = 'Windows'
# endregion

# region test-environment
# -----------------------------------------------
from decouple import config
import requests
import urllib3
import json
import base64
from time import sleep

urllib3.disable_warnings()

# prism central config
pc_host = config('PC_HOST')
pc_port = config('PC_PORT', '9440')
pc_username = config('PC_USERNAME')
pc_password = config('PC_PASSWORD')
pc_authorization = 'Basic ' + base64.b64encode('{}:{}'.format(pc_username, pc_password).encode()).decode()

# app settings
target_network = config('TARGET_NETWORK')
project_name = 'DEMO'
environment_name = 'DEV'
app_type = 'GN - Generic Application'
# endregion


# region calm-environment
# -----------------------------------------------
# import requests

# # prism central config
# pc_host = '127.0.0.1'
# pc_port = '9440'
# pc_authorization = 'Bearer @@{calm_jwt}@@'

# # app settings
# target_network = '@@{TARGET_NETWORK}@@'
# project_name = '@@{calm_project_name}@@'
# åenvironment_name = '@@{calm_environment_name}@@'
# app_type = '@@{APP_TYPE}@@'
# endregion

# region http headers
# -----------------------------------------------
pc_url = 'https://{}:{}/api/nutanix/v3/{}'.format(pc_host, pc_port, '{}')
pc_kwargs = {
    'verify': False,
    'headers': {'Authorization': pc_authorization}
}
# endregion


# region generate vm prefix
# -----------------------------------------------
env_prefix = environment_name[:1].lower() if environment_name else 'x'
project_prefix = project_name[:3].lower() if project_name else 'xxx'
os_prefix = os_type[:1].lower() if os_type else 'x'
app_prefix = app_type[:2].lower() if app_type else 'xx'

vm_prefix = '{}-{}-{}v-{}'.format(env_prefix, project_prefix, os_prefix, app_prefix)
print('INFO: generated vm prefix: {}'.format(vm_prefix))
# endregion

# region get next vm number and generate the full name
# -----------------------------------------------
payload = {
    'kind': 'vm',
    'filter': 'vm_name=={}.*'.format(vm_prefix),
    'length': 1000,
    'sort_attribute': 'vm_name',
    'sort_order': 'DESCENDING'
}
r = requests.post(pc_url.format('vms/list'), json=payload, **pc_kwargs)
if r.status_code != 200:
    print('ERROR: failed to get vm list, status code: {}, msg: {}'.format(r.status_code, r.content))
    exit(1)

vm_list = r.json()['entities']
print('INFO: found {} VMs with prefix: {}'.format(len(vm_list), vm_prefix))
if len(vm_list) == 0:
    vm_number = 1
else:
    vm_number = int(vm_list[0]['status']['name'][-2:]) + 1

vm_name = vm_prefix + '{0:0=2d}'.format(vm_number)
print('VM_NAME={}'.format(vm_name))

# endregion
