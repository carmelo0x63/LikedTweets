#!/usr/bin/env python3
# Script consuming Twitter API to retrieve the liked tweets for a specific user incrementally
# author: Carmelo C
# email: carmelo.califano@gmail.com
# history, date format ISO 8601:
#  2021-04-22  2.4: changed option from -c to -t
#  2021-03-24  2.3: automatically moves obsolete files to ARCHIVEDIR
#  2020-10-01  2.2: introduced tweet_mode, convert_all(); expanded print_all()
#  2020-09-25  2.1: print_all() prints in reverse order
#  2020-09-02  2.0: refactored to split the GET workflow into "first" (=backwards) and "incremental"
#  2020-09-07  1.1: rearranged options so that "get" and "print" are mutually exclusive and both require an UID
#  2020-09-04  1.0: initial version

# External modules/dependencies
import argparse                # Parser for command-line options, arguments and sub-commands
import json                    # JSON encoder and decoder
import requests                # HTTP library for Python
import os                      # Miscellaneous operating system interfaces
import shutil                  # High-level file operations
import sys                     # System-specific parameters and functions
from datetime import datetime  # Basic date and time types
from json2html import *        # Python wrapper for JSON to HTML-Table convertor

# Global settings
__version__ = '2.4'
__build__ = '20210423'
APIENTRYPOINT = 'https://api.twitter.com/1.1/favorites/list.json'
MAXCOUNT = 200
TWEET_MODE = "extended"
BASEURL = APIENTRYPOINT + '?count=' + str(MAXCOUNT) + '&tweet_mode=' + TWEET_MODE
TIMESTAMP = datetime.now().strftime('%Y-%m-%d-%H')
ARCHIVEDIR = '_archive'

"""
read_conf() reads the application's configuration from an external file.
The file is JSON-formatted and contains:
  the OAuth2 bearer tokens for any users,
  the last timestamp,
  the last index where we left off.
"""
def read_conf(name):
    try:
        with open(name + '_config.json', 'r') as config_in:
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

"""
update_conf() updates the external configuration file with the last fetched value, "last_index_str".
Incremental API requests must comply with "since_id = last_index_str".
"""
def update_conf(config_json, name, new_index_str):
    config_json.update(last_index_str = new_index_str, last_timestamp = TIMESTAMP)
    with open(name + '_config.json', 'w') as config_out:
        json.dump(config_json, config_out)

"""
print_all() displays the local archive in a nicely formatted fashion
"""
def print_all(file_json):
    for index in range(len(file_json) - 1, -1, -1):
        print('{')
        print('\t"ROW": "' + str(index) + '",')
        print('\t"TWEET_ID": "' + file_json[index]['id_str'] + '",')
        print('\t"TWEET_FULL_TEXT": """' + file_json[index]['full_text'] + '""",')
        print('\t"TWEET_DATE": "' + file_json[index]['created_at'] + '",')
        print('\t"USER_ID": "' + file_json[index]['user']['id_str'] + '",')
        print('\t"USER_NAME": "' + file_json[index]['user']['name'] + '",')
        print('\t"USER_HANDLE": "' + file_json[index]['user']['screen_name'] + '",')
        try:
            print('\t"URL": "' + file_json[index]['entities']['urls'][0]['expanded_url'] + '"')
        except:
            print('\t"URL": "N/A"')
        print('}', end = '\n\n')

"""
requests_get() handles the HTTP GET part, depends on 'Requests' external module
"""
def requests_get(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print('[-] An error has occurred!')
        print('[-] HTTP status code: ' + str(response.status_code))
        print('[-] Quitting!', end = '\n\n')
        sys.exit(255)  # ERROR: HTTP error
    else:
        print('[+] HTTP status code: ' + str(response.status_code))

    return response.json()

"""
dump_json() appends any new data 'on top' of the local archive. If no previous local archive is present, we'll just save the contents of our request.
"""
def dump_json(response_json, name, old_ts):
    if old_ts == '':
        old_ts = 'EMPTY'

    if ISVERBOSE:
        print('[+] Saving raw incremental data file for ' + name)
        print('[+] New file: ' + name + '_twitter_likes_' + TIMESTAMP + '.json')

    try:
        with open(name + '_twitter_likes_' + old_ts + '.json', 'r') as previous_in:
            previous_json = json.load(previous_in)
            print('[+] Records (previous): ' + str(len(previous_json)))
    except FileNotFoundError:
        if ISVERBOSE:
            print('[!] Starting from an empty archive')
        previous_json = []

    if old_ts != TIMESTAMP:
        archive_file(name, old_ts)

    new_json = response_json + previous_json
    print('[+] Records (new): ' + str(len(new_json)))

    with open(name + '_twitter_likes_' + TIMESTAMP + '.json', 'w') as response_out:
        json.dump(new_json, response_out)
    if ISVERBOSE:
        print('[+] New file: ' + name + '_twitter_likes_' + TIMESTAMP + '.json saved to disk')

"""
convert_all() converts the raw JSON file into a table-based HTML file
"""
def convert_all(tweets_json, name, old_ts):
    tweets_json_out = []

    for index in range(0, len(tweets_json)):
        tweet = {"ROW": "", "USER INFO": "", "TWEET INFO": "", "FULL TEXT": "", "URL": ""}
        tweet.update({"ROW": index})
        tweet.update({"USER INFO": {"USER_ID": tweets_json[index]['user']['id_str'], "USER_NAME": tweets_json[index]['user']['name'], "USER_HANDLE": tweets_json[index]['user']['screen_name']}})
        tweet.update({"TWEET INFO": {"TWEET_ID": tweets_json[index]['id_str'], "TWEET_DATE": tweets_json[index]['created_at']}})
        tweet.update({"FULL TEXT": tweets_json[index]['full_text']})
        try:
            tweet.update({"URL": tweets_json[index]['entities']['urls'][0]['expanded_url']})
        except:
            tweet.update({"URL": "N/A"})
        tweets_json_out.append(tweet)

    index_out = json2html.convert(json = tweets_json_out)

    with open(name + '_index_' + TIMESTAMP + '.html', 'w') as html_out:
        html_out.write(index_out)
    if ISVERBOSE:
        print('[+] New file: ' + name + '_index_' + TIMESTAMP + '.html saved to disk')

"""
archive_file() obsoletes an old archive by moving the file to ARCHIVEDIR
"""
def archive_file(name, old_ts):
    files = [name + '_twitter_likes_' + old_ts + '.json', name + '_index_' + old_ts + '.html']
    for file in files:
        if os.path.isfile(file):
          if os.path.isdir(ARCHIVEDIR):
              shutil.move(file, ARCHIVEDIR + '/' + file)
              if ISVERBOSE:
                  print('[+] Archived file: ' + file)
          else:
              print('[-] "' + ARCHIVEDIR + '" is not present!')
              sys.exit(60)  # ERROR: archive directory not found
        else:
          print('[!] "' + file + '" is not present, skipping!')

"""
main() handles the input (through argparse), then implements the logic based on the input arguments.
"""
def main():
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
    # Note: "get", "print", and "convert" are mutually exclusive, default = '', user_id is necessarily one of them 
    user_id = args.get + args.print + args.convert
    global ISVERBOSE
    ISVERBOSE = args.verbose
    if user_id != '':
        config_json = read_conf(user_id)
    else:
        print('[-] User ID is empty!', end = '\n\n')
        sys.exit(30)  # ERROR: user ID is an empty string

    # If "print" mutually exclusive option is chosen we take a shortcut here
    if args.print:
        try:
            if ISVERBOSE: print('[+] Printing local archive for user ' + user_id)
            filename = user_id + '_twitter_likes_' + config_json['last_timestamp'] + '.json'
            with open(filename, 'r') as archive_in:
                archive_json = json.load(archive_in)
            print_all(archive_json)
            sys.exit(0)
        except FileNotFoundError:
            print('[-] Local archive ' + filename + ' not found')
            print('[-] Quitting!', end = '\n\n')
            sys.exit(40)  # ERROR: local archive not found
    # Once "print" is done the script exits in a controlled fashion

    # If "convert" mutually exclusive option is chosen we do the same as with "print"
    if args.convert:
        try:
            if ISVERBOSE: print('[+] Generating HTML output for user ' + user_id)
            filename = user_id + '_twitter_likes_' + config_json['last_timestamp'] + '.json'
            with open(filename, 'r') as archive_in:
                archive_json = json.load(archive_in)
            convert_all(archive_json, user_id, config_json['last_timestamp'])
            sys.exit(0)
        except FileNotFoundError:
            print('[-] Local archive ' + filename + ' not found')
            print('[-] Quitting!', end = '\n\n')
            sys.exit(40)  # ERROR: local archive not found
    # Once "convert" is done the script exits in a controlled fashion

    # The only other possibility is "get", that comes in two flavours:
    # 1. "first": we must query the API starting from the most recent tweets and dig backwards,
    #             the resulting JSON archive = page1 + ... + pageN
    # 2. "incremental": we only need to gather the latest tweets by means of "since_id = last_index_str",
    #                   the response is added on top of the existing archive

    # Let's build the authentication and the entry point that we shall send in our GET request
    # The variable "response" will contain the retrieved raw information
    headers = {
               'Authorization': 'Bearer ' + config_json['BEARER'],
               'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
              }
    print('[+] Fetching tweets for ' + user_id)

    if config_json['last_timestamp'] == '' or config_json['last_index_str'] == '':
        # Flavour = "first"
        print('[!] First run! We\'ll attempt to fetch each and every Likes recursively...')

        archive_json = []
        is_first = True
        page_num = 1
        url_first = BASEURL + '&screen_name=' + user_id
        while True:
            print('[+] Page N.: ' + str(page_num))
            page_num += 1
            if not is_first:
                # From the 2nd loop onwards, the url will contain "max_id", slightly decremented so that the next "page" can be fetched
                url = url_first + '&max_id=' + str(last_id - 1)
            else:
                # When the while loop is run for the first time url does not contain "max_id"
                url = url_first
                is_first = False
            response_json = requests_get(url, headers)
            response_len = len(response_json)
            # archive_json aggregates the various response_json's
            archive_json += response_json
            try:
                last_id = response_json[response_len - 1]['id']
            except IndexError:
                print('[+] That was the last page')
                break
            if ISVERBOSE:
                print('[+] Received ' + str(response_len) + ' items')
                print('[+] Last ID is: ' + str(last_id))
                print('[+] Archive length is: ' + str(len(archive_json)))
        # Finally, the in-memory JSON archive is saved to file
        dump_json(archive_json, user_id, config_json['last_timestamp'])
        new_index_str = archive_json[0]['id_str']
        if ISVERBOSE: print('[+] New last index is: ' + new_index_str)
        update_conf(config_json, user_id, new_index_str)
    else:
        # Flavour = "incremental", "since_id" is used set the the value we fetch from the config file
        url = BASEURL + '&screen_name=' + user_id + '&since_id=' + config_json['last_index_str']
        if ISVERBOSE: print('[+] URL: ' + url)  ##DEBUG

        response_json = requests_get(url, headers)
        response_len = len(response_json)
        print('[+] Retrieved ' + str(response_len) + ' new tweets')

        if response_len > 0:
            # Saving the current response_json on top of the existing archive
            # Filename format is "<name>_twitter_likes_%Y-%m-%d-%H.json"
            dump_json(response_json, user_id, config_json['last_timestamp'])

            # Last step is to update the <name>_config.json file with the current last index
            new_index_str = response_json[0]['id_str']
            if ISVERBOSE: print('[+] New last index is: ' + new_index_str)
            update_conf(config_json, user_id, new_index_str)
        else:
            print('[+] No updates!')

if __name__ == '__main__':
    main()

