#!/bin/python3

'''
Acquires targets from HackerOne directory
'''

# Launch the query to HackerOne for the first 25 records
# Get the endcursor to use in the next query
# Repeat process until the program id is already present in the database
# or no records are returned

# Query the HackerOne directory for programs that offer bounties and have domains
import json
import logging
import os
import re
import requests
from bs4 import BeautifulSoup

from floodlight import TARGET_FILE

HACKERONE_BASE_URL = 'https://hackerone.com'
HACKERONE_DIRECTORY_URL = (
    f'{HACKERONE_BASE_URL}/directory/programs?offers_bounties=true'
    f'&asset_type=URL&order_direction=DESC&order_field=launched_at'
)
HACKERONE_QUERY_URL = f'{HACKERONE_BASE_URL}/graphql'
QUERY_SIZE = 25


def query_directory():
    '''
    Queries the HackerOne directory for potential targets
    '''
    headers = {
        'authority': 'hackerone.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://hackerone.com',
        'referer': 'https://hackerone.com/directory/programs?offers_bounties=true&' +
        'asset_type=URL&order_direction=DESC&order_field=launched_at',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' +
        ' (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36',
    }

    payload = {
        'operationName': 'DirectoryQuery',
        'variables': {
            'where': {
                '_and': [
                    {
                        '_or': [
                            {
                                'offers_bounties': {
                                    '_eq': True
                                }
                            },
                            {
                                'external_program': {
                                    'offers_rewards': {
                                        '_eq': True
                                    }
                                }
                            }
                        ]
                    },
                    {
                        'structured_scopes': {
                            '_and': [
                                {
                                    'asset_type': {
                                        '_eq': 'URL'
                                    }
                                },
                                {
                                    'is_archived': False
                                }
                            ]
                        }
                    },
                    {
                        '_or': [
                            {
                                'submission_state': {
                                    '_eq': 'open'
                                }
                            },
                            {
                                'submission_state': {
                                    '_eq': 'api_only'
                                }
                            },
                            {
                                'external_program': {}
                            }
                        ]
                    },
                    {
                        '_not': {
                            'external_program': {}
                        }
                    },
                    {
                        '_or': [
                            {
                                '_and': [
                                    {
                                        'state': {
                                            '_neq': 'sandboxed'
                                        }
                                    },
                                    {
                                        'state': {
                                            '_neq': 'soft_launched'
                                        }
                                    }
                                ]
                            },
                            {
                                'external_program': {}
                            }
                        ]
                    }
                ]
            },
            'first': 25,
            # 'cursor': 'MjU',
            'secureOrderBy': {
                'launched_at': {
                    '_direction': 'DESC'
                }
            }
        },
        'query': '''
            query DirectoryQuery(
                $cursor: String,
                $secureOrderBy: FiltersTeamFilterOrder,
                $where: FiltersTeamFilterInput
            ) {
                teams(
                    first: 25,
                    after: $cursor,
                    secure_order_by: $secureOrderBy,
                    where: $where
                ) {
                    pageInfo {
                        endCursor
                        hasNextPage
                        __typename
                    }
                    edges {
                        node {
                            id
                            bookmarked
                            ...TeamTableAvatarAndTitle
                            ...TeamTableLaunchDate
                            structured_scopes {
                                edges {
                                    node {
                                        id
                                        asset_identifier
                                        asset_type
                                        __typename
                                    }
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }


            fragment TeamTableAvatarAndTitle on Team {
                id
                name
                handle
                __typename
            }
            
            
            fragment TeamTableLaunchDate on Team {
                id
                launched_at
                __typename
            }

        '''
    }

    session = requests.session()

    response = session.get(HACKERONE_DIRECTORY_URL)

    xml_data = BeautifulSoup(response.text, 'lxml')
    csrf_token = xml_data.find('meta', {'name': 'csrf-token'}).get('content')
    headers['x-csrf-token'] = csrf_token

    has_next_page = True

    hosts = []

    while has_next_page:
        response = session.post(
            HACKERONE_QUERY_URL, json=payload, headers=headers)

        if response.status_code != 200:
            logging.error('An error occurred while querying for targets')
            logging.error('Response Status: %(response.status_code)d')
            logging.error('Response Reason: %(response.reason)s')
            break

        response_dict = json.loads(response.content.decode())['data']['teams']

        has_next_page = response_dict['pageInfo']['hasNextPage']
        payload['variables']['cursor'] = response_dict['pageInfo']['endCursor']
        edge_list = response_dict['edges']

        for edge in edge_list:
            scopes_list = edge['node']['structured_scopes']['edges']

            for scope in scopes_list:
                if scope['node']['asset_type'] != 'URL':
                    continue

                host_items = scope['node']['asset_identifier'].split(',')

                for host in host_items:
                    host_substr = re.search(r'[^./]*\.[^\.]+$', host).group()

                    if '/' in host_substr:
                        host_substr = host_substr[:host_substr.find('/')]

                    if host_substr not in hosts:
                        hosts.append(host_substr)

    with open(TARGET_FILE, mode='w+', encoding='utf-8') as target_file:
        for host in hosts:
            target_file.write(host + os.linesep)


if __name__ == '__main__':
    query_directory()
