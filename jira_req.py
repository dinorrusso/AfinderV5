#!/usr/bin/env python3
import requests
from jira import JIRA
import json
import os
from dotenv import load_dotenv
import aflog
logger = aflog.logging.getLogger(__name__)

def get_jira_devices(email_id):
    load_dotenv()
    '''
    This function takes in an email address and returns a list
    of found devices or an empty list.
    Each device in the list is represented by a list of strings
    that are device name, device serial number and device asset tag. 
    '''
    
    #.env holds secrets
    jira_url = os.environ.get("JIRASERVER")
    jira_user = os.environ.get('JIRAUSERNAME')
    jira_token = os.environ.get('JIRAPASSWORD')

    #init the device list to return
    device_list = []

    # Specify a server key. It should be your
    # domain name link. yourdomainname.atlassian.net
    jiraOptions = {'server': jira_url}

    # Get a JIRA client instance
    lyftjira = JIRA(options=jiraOptions, basic_auth=(jira_user,jira_token))

    # Search all issues mentioned against a project name.
    jql_str = 'project = OB AND status = Closed AND Email ~ "' + email_id +'" ORDER BY created DESC'
    for singleIssue in lyftjira.search_issues(jql_str):
        comments = lyftjira.comments(singleIssue.key)
        logger.info('comments = {}'.format(comments))
        if len(comments) > 0:
            comment_text = comments[0].body
            logger.info(comment_text)
            temp = comment_text.splitlines(0)
            for t in temp:
                if t != '':
                    device_list.append(t)

    return device_list
    
    


def main():
    logger.info('starting jira_req.py main')
    email_address = input('\nEnter email address:')
    list = get_jira_devices(email_address)
    logger.info('list={}'.format(list))
    print('For {} - {} Jira items found'.format(email_address, len(list)))
    for items in list:
        print(items)

if __name__ == '__main__':
    main()





