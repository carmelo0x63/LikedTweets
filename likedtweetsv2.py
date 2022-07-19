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
expansions = 'author_id'
tweet_fields = 'author_id,created_at'
user_fields = 'id,name,username'
query_params = dict([
    ('expansions', expansions),
    ('tweet.fields', tweet_fields),
    ('user.fields', user_fields),
    ('max_results', 5)  ## DEBUG
])


def create_url(id):
    """
    create_url is an URL generator based on v2 endpoint + Twitter ID
    """
    url = f'https://api.twitter.com/2/users/{id}/liked_tweets'
    return url


def readConf(name):
    """
    readConf() reads the application's configuration from an external file.
    The file is JSON-formatted and contains:
    - the twitter ID,
    - the OAuth2 bearer token,
    - the last timestamp.
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
#            beautify_last_index_str = config_json['last_index_str'] or 'EMPTY'
            beautify_last_timestamp = config_json['last_timestamp'] or 'EMPTY'
#            print('[+] Last index is: ' + beautify_last_index_str)
            print('[+] Last timestamp is: ' + beautify_last_timestamp)
        return config_json
    except FileNotFoundError:
        print('[-] Config file not found for ' + name)
        print('[-] Quitting!', end = '\n\n')
        sys.exit(20)  # ERROR: wrong user name / config file not found


def connect_to_endpoint(url, bearer_token, query_params):
    """
    connect_to_endpoint() consumes Twitter v2 API "liked_tweets" endpoint. The response, once converted to JSON,
    consists of the following keys:
    - data: type = list of dicts, each element contains the fundamental info about the tweet
    - includes: type = dict, optional, its contents depends on the chosen expansion(s)
    - meta: type = dict, contains useful info such as result_count, next_token, previous_token
    """
    headers = {'Authorization': f'Bearer {bearer_token}'}
    response = requests.request('GET', url, headers = headers, params = query_params)
    if response.status_code != 200:
        print('[-] An error has occurred')
        print(f'[-] HTTP status code = {response.status_code}')
        print(f'[-] HTTP reason = {response.reason}')
        print('[-] Quitting!', end = '\n\n')
        sys.exit(response.status_code)
    else:
        if ISVERBOSE: print(f'[+] HTTP status code = {response.status_code}')
    return response.json()


def mergeExpansions(data_json, includes_json):
    """
    mergeExpansion() parses 'response_json' for returned tweets, it searches the 'include' key to match 'tweet/author_id' and 'users/id'.
    Once that's done, it merges both dictionaries into one record comprised of:
    - id, text (from 'data', default values)
    - author_id, created_at (from 'data', optional values as per 'tweet.fields')
    - name, username (from 'includes', defined by 'expansions')
    """
    for tweet in data_json:
        author = tweet['author_id']
        for user in includes_json:
            if user['id'] == author:
                tweet.update({'author_name': user['name'], 'author_handle': user['username']})
    return data_json


def saveData(name, output_json):
    with open(name + '_likedtweets_' + TIMESTAMP + '.json', 'w') as output_file:
        json.dump(output_json, output_file)


def updateConf(config_json, name):
    """
    updateConf() updates the external configuration file with the last timestamp.
    """
    config_json.update(last_timestamp = TIMESTAMP)
    with open(name + '_configv2.json', 'w') as config_out:
        json.dump(config_json, config_out)


def main():
    """
    main() handles the input (through argparse), then implements the logic based on the input arguments.
    """
    parser = argparse.ArgumentParser(description = 'Consumes Twitter API to retrieve the liked tweets incrementally, version ' + __version__ + ', build ' + __build__ + '.')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'Print extended information')
    parser.add_argument('-V', '--Version', action = 'version', version = '%(prog)s {version}'.format(version=__version__))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-g', '--get', metavar = '<User name>', default = '', type = str, help = 'User name or Twitter handle (w/o @)')
    group.add_argument('-p', '--print', metavar = '<User name>', default = '', type = str, help = 'Pretty print local JSON archive to screen')
    group.add_argument('-t', '--tohtml', metavar = '<User name>', default = '', type = str, help = 'Convert local JSON archive to HTML')

    # In case of no arguments help message is shown
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(10)  # ERROR: no arguments
    else:
        args = parser.parse_args() # parse command line

    # First off, <name>_configv2.json s read to fetch the user's Twitter ID and any tokens
    # Note: "get", "print", and "tohtml" arguments are mutually exclusive,
    # <User name>'s default value is the empty string, if <User name> has a non-empty value it must come from get/print/tohtml
    twitter_name = args.get + args.print + args.tohtml
    global ISVERBOSE
    ISVERBOSE = args.verbose
    if twitter_name != '':
        config_json = readConf(twitter_name)
    else:
        print('[-] User ID is empty!', end = '\n\n')
        sys.exit(30)  # ERROR: user ID is an empty string

    twitter_id = config_json['twitter_id']
    url = create_url(twitter_id)
    bearer_token = config_json['BEARER']
    last_timestamp = config_json['last_timestamp']

    count = records = 0
    next_token = 'dummy'  ## this is only used once, to trigger the 'while' loop
    output_list = []
    while next_token:
        count += 1
        response_json = connect_to_endpoint(url, bearer_token, query_params)
        if ISVERBOSE: print('[!] Iteration = ' + str(count) + ', next_token = \'' + next_token + '\'')

        result_count = response_json['meta']['result_count']
        if ISVERBOSE: print('[!] Fetched ' + str(result_count) + ' records')
        records += result_count
        if ISVERBOSE: print('[!] Partial count: ' + str(records) + ' records thus far...')

        if result_count == 0:
            if ISVERBOSE:
                print('[!] No data returned')
                print('[!] Last page reached')
            print('[+] Operation completed, fetched ' + str(records) + ' records')
            break
        else:
            if ISVERBOSE:
                print('data: ')
                print(response_json['data'])
                print('includes: ')
                print(response_json['includes']['users'], end = '\n\n')

            merged_json = mergeExpansions(response_json['data'], response_json['includes']['users'])
            if ISVERBOSE:
                print('merged data: ')
                print(merged_json, end = '\n\n')

            output_list += merged_json
            if ISVERBOSE:
                print('data length = ' + str(len(response_json['data'])))
                print('current output len = ' + str(len(output_list)))
                print('meta = ' + str(response_json['meta']), end = '\n\n')

            next_token = response_json['meta']['next_token']
            query_params.update([('pagination_token', next_token)])

    if ISVERBOSE: print('[!] Storing liked_tweets to local file')
    saveData(twitter_name, output_list)
    if ISVERBOSE: print('[!] Updating config')
    updateConf(config_json, twitter_name)
    print('DELETE ' + twitter_name + '_likedtweets_' + last_timestamp + '.json')


if __name__ == '__main__':
    main()

