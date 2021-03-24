### LikeHistory
#### Save Twitter likes to a local JSON file.
The script is based on Twitter API [GET favorites/list](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-favorites-list) entrypoint.</br>
A [developer account](https://developer.twitter.com/) is needed to create a project/application and the related credentials.</br>

### Install
```
python3 -m venv .
source bin/activate
pip3 install --upgrade pip
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
usage: savemylikes.py [-h] [-v] [-V] [-g <User ID> | -p <User ID> | -c <User ID>]

Consumes Twitter API to retrieve the liked tweets incrementally, version 2.3, build 20210324.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print extended information
  -V, --Version         show program's version number and exit
  -g <User ID>, --get <User ID>
                        User ID or Twitter handle (w/o @)
  -p <User ID>, --print <User ID>
                        Pretty print local JSON archive to screen
  -c <User ID>, --convert <User ID>
                        Convert local JSON archive to HTML
```

### Error codes
10: no arguments</br>
20: wrong user ID / config file not found</br>
30: user ID is an empty string</br>
40: local archive not found</br>
50: empty Bearer token</br>
60: archive directory not found</br>
255: HTTP error</br>

