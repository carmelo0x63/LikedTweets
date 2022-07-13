#!/usr/bin/env python3
# Script consuming Twitter API to retrieve the liked tweets for a specific user incrementally
# author: Carmelo C
# email: carmelo.califano@gmail.com
# history, date format ISO 8601:
#  2022-07-12  Moved to Twitter API v2

# External modules/dependencies
import argparse                # Parser for command-line options, arguments and sub-commands
import json                    # JSON encoder and decoder
import requests                # HTTP library for Python
import os                      # Miscellaneous operating system interfaces
#import shutil                  # High-level file operations
#import subprocess              # Subprocess management
import sys                     # System-specific parameters and functions
from datetime import datetime  # Basic date and time types
#from json2html import *        # Python wrapper for JSON to HTML-Table convertor

# Global settings
__version__ = '3.0'
__build__ = '20220712'
#MAXCOUNT = 200
#TWEET_MODE = "extended"
#BASEURL = APIENTRYPOINT + '?count=' + str(MAXCOUNT) + '&tweet_mode=' + TWEET_MODE
TIMESTAMP = datetime.now().strftime('%Y-%m-%d-%H')
ARCHIVEDIR = '_archive'
# Default fields: id, text
# Additional fields
tweet_fields = 'author_id,created_at'
query_params = dict([
    ('tweet.fields', tweet_fields)
])


def create_url(id):
    """
    create_url is an URL generator based on v2 endpoint + Twitter user ID
    """
    url = f'https://api.twitter.com/2/users/{id}/liked_tweets'
    return url


def read_conf(name):
    """
    read_conf() reads the application's configuration from an external file.
    The file is JSON-formatted and contains:
      the OAuth2 bearer tokens for any users,
      the last timestamp,
      the last index where we left off.
    """
    try:
        with open(name + '_configv2.json', 'r') as config_in:
            config_json = json.load(config_in)
        if ISVERBOSE: print('[+] Config file found for ' + name)
        if config_json['BEARER'] == '':
            print('[-] Bearer token empty!')
            print('[-] Quitting!', end = '\n\n')
            sys.exit(50)  # ERROR: empty Bearer token
        else:
            if ISVERBOSE: print('[+] Bearer token found!')
        if ISVERBOSE:
            beautify_last_index_str = config_json['last_index_str'] or 'EMPTY'
            beautify_last_timestamp = config_json['last_timestamp'] or 'EMPTY'
            print('[+] Last index is: ' + beautify_last_index_str)
            print('[+] Last timestamp is: ' + beautify_last_timestamp)
        return config_json
    except FileNotFoundError:
        print('[-] Config file not found for ' + name)
        print('[-] Quitting!', end = '\n\n')
        sys.exit(20)  # ERROR: wrong user ID / config file not found


#def bearer_oauth(r):
#    """
#    bearer_oauth() builds up the necessary OAuth headers
#    """
#    r.headers["Authorization"] = f'Bearer {bearer_token}'
#    r.headers["User-Agent"] = 'v2LikedTweetsPython'
#    return r


def connect_to_endpoint(url, bearer_token, query_params):
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = requests.request('GET', url, headers = headers, params = query_params)
    if response.status_code != 200:
        print('[-] An error has occurred')
        print(f"[-] status code = {response.status_code}, text = {response.json()['title']}")
        sys.exit(response.status_code)

    return response.json()


def main():
    """
    main() handles the input (through argparse), then implements the logic based on the input arguments.
    """
    parser = argparse.ArgumentParser(description='Consumes Twitter API to retrieve the liked tweets incrementally, version ' + __version__ + ', build ' + __build__ + '.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print extended information')
    parser.add_argument('-V', '--Version', action='version', version='%(prog)s {version}'.format(version=__version__))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-g', '--get', metavar='<User ID>', default='', type=str, help='User ID or Twitter handle (w/o @)')
    group.add_argument('-p', '--print', metavar='<User ID>', default='', type=str, help='Pretty print local JSON archive to screen')
    group.add_argument('-t', '--tohtml', metavar='<User ID>', default='', type=str, help='Convert local JSON archive to HTML')

    # In case of no arguments shows help message
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(10)  # ERROR: no arguments
    else:
        args = parser.parse_args() # parse command line

    # First off, read <name>_config.json to fetch where we left off and any tokens
    # Note: "get", "print", and "tohtml" arguments are mutually exclusive,
    # <User ID>'s default value is the empty string, if <User ID> has a non-empty value it must come from get/print/tohtml
    user_id = args.get + args.print + args.tohtml
    global ISVERBOSE
    ISVERBOSE = args.verbose
    if user_id != '':
        config_json = read_conf(user_id)
    else:
        print('[-] User ID is empty!', end = '\n\n')
        sys.exit(30)  # ERROR: user ID is an empty string

    twitter_id = config_json['twitter_id']
    url = create_url(twitter_id)
    bearer_token = config_json['BEARER']

    count = 0
    next_token = 'empty'
    while next_token:
        count += 1
        response_json = connect_to_endpoint(url, bearer_token, query_params)
        print('Iteration = ' + str(count), 'next_token = \'' + next_token + '\'')

        result_count = response_json['meta']['result_count']
        print('fetched ' + str(result_count) + ' records')

        if result_count == 0:
            print('[!] No data returned')
            print('[!] You\'ve reached the last page')
            break
        else:
            print('data length = ' + str(len(response_json['data'])))
            print('data[0] = ' + str(response_json['data'][0]))
            print('...')
            print('meta = ' + str(response_json['meta']), end = '\n\n')
            next_token = response_json['meta']['next_token']
            query_params.update([('pagination_token', next_token)])


if __name__ == '__main__':
    main()

