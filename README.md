### LikeHistory
#### Save Twitter likes to a local JSON file.
The script is based on Twitter API [GET favorites/list](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-favorites-list) entrypoint.</br>
A [developer account](https://developer.twitter.com/) is needed to create a project/application and the related credentials.</br>

### Install
```
python3 -m venv .
source bin/activate
pip3 install json2html requests
```

### Configuration
The operation of the script is based on a configuration file, also in JSON format. The file is named `<user_id>_config.json` and contains the following information:</br>
1 Bearer token, e.g. "AAAxMjwkf... UYAVhca"</br>
2 last timestamp, e.g. "2020-01-01-10"</br>
3 last index, e.g. "1924542778424577816"
See `config.json.txt` for an example.

#### 1. Bearer token
`OAuth 2.0 Bearer Token authenticates requests on behalf of your developer App. As this method is specific to the App, it does not involve any users. This method is typically for developers that need read-only access to public information.`</br>
source: https://developer.twitter.com/en/docs/authentication/oauth-2-0

#### 2. last timestamp
The timestamp (format: %Y-%m-%d-%H) associated to the last time the script ran. Last timestamp (`last_timestamp`) is also a pointer to the file containing the latest archive.</br>
**NOTE**: when setting up the application for the first time use the initial value: "" (empty string)

#### 3. last index
Last index (`last_index_str`) saves the latest `id_str` from a previous query. This value is used to generate the next query in an incremental fashion, e.g. `since_id = last_index_str`.</br>
**NOTE**: when setting up the application for the first time use the initial value: "" (empty string)

### Usage
```
usage: savemylikes.py [-h] [-d] [-v] [-g <User ID> | -p <User ID>]

Consumes Twitter API to retrieve the liked tweets in an incremental fashion, version 2.0, build 20200909.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Print extended information
  -v, --version         show program's version number and exit
  -g <User ID>, --get <User ID>
                        User ID or Twitter handle (w/o @)
  -p <User ID>, --print <User ID>
                        Print local archive to screen
```

### Error codes
10: no arguments
20: wrong user ID / config file not found
30: user ID is an empty string
40: local archive not found
50: empty Bearer token
60: archive directory not found
255: HTTP error

