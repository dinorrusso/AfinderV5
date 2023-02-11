#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv
import aflog
logger = aflog.logging.getLogger(__name__)

def get_jamf_devices(email_id):
    load_dotenv()
    '''
    This function takes in an email address and returns a list
    of found devices or an empty list.
    Each device in the list is represented by a list of strings
    that are device name, device serial number and device asset tag. 
    '''
    
    #.env holds secrets
    jamf_url = os.environ.get("JAMFURL")
    jamf_token = os.environ.get('JAMFTOKEN')

    #init the device list to return
    device_list = []

    #call the api match function using email
    response = requests.get(
        jamf_url + 'computers/match/' + email_id,
        headers={"Accept": "application/json",
                "Authorization": "Basic " + jamf_token},
    )
    logger.info(response.status_code)
    res = response.text
    res_dict = json.loads(res)
    computer_list = res_dict['computers']
    logger.info(' {} items returned from JAMF'.format(len(computer_list)))
    for computer in computer_list:
        device_data = []
        device_data.append(computer['name'])
        device_data.append(computer['serial_number'])
        device_data.append(computer['asset_tag'])
        device_list.append(device_data)
    return(device_list)

def main():
    logger.info('starting jamf_req.py main')
    email_address = input('\nEnter email address:')
    list = get_jamf_devices(email_address)

    logger.info('list={}'.format(list))
    for items in list:
        print(items)

if __name__ == '__main__':
    main()