### LikedTweets
#### Save Twitter likes to a local JSON file, also convert the list to handy HTML for easy browsing.
The script is based on Twitter API v2 [GET /2/users/:id/liked_tweets](https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-users-id-liked_tweets) entrypoint.</br>
A [developer account](https://developer.twitter.com/) is needed to create a project/application and the related credentials.</br>

### Install
```
$ python3 -m venv .

$ source bin/activate

$ python3 -m pip install --upgrade pip setuptools wheel

$ python3 -m pip install json2html requests
```

### Configuration
The operation of the script is based on a configuration file, also in JSON format. The file is named `<user_id>_configv2.json` and contains the following information:</br>
1. Twitter ID, e.g. "1234567890"</br>
2. Bearer token, e.g. "AAAxMjwkf... UYAVhca"</br>
3. last timestamp, e.g. "2020-01-01-10"</br>
See `user_configv2.json.txt` for an example.

#### 1. Twitter ID
This is the unique identifies associated to your Twitter username/handle.

#### 2. Bearer token
From [Authentication](https://developer.twitter.com/en/docs/authentication/oauth-2-0), "OAuth 2.0 Bearer Token authenticates requests on behalf of your developer App. As this method is specific to the App, it does not involve any users. This method is typically for developers that need read-only access to public information."</br>

#### 3. last timestamp
The timestamp (format: %Y-%m-%d-%H) associated to the last time the script ran. Last timestamp (`last_timestamp`) is also a pointer to the file containing the latest archive.</br>
**NOTE**: when setting up the application for the first time use the initial value: "" (empty string)

### Usage
```
usage: likedtweetsv2.py [-h] [-v] [-V] [-g <User ID> | -p <User ID> | -t <User ID>]

Consumes Twitter API to retrieve the liked tweets incrementally, version 2.5, build 20210511.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print extended information
  -V, --Version         show program's version number and exit
  -g <User ID>, --get <User ID>
                        User ID or Twitter handle (w/o @)
  -p <User ID>, --print <User ID>
                        Pretty print local JSON archive to screen
  -t <User ID>, --tohtml <User ID>
                        Convert local JSON archive to HTML
```

### Error codes
10: no arguments</br>
20: wrong user ID / config file not found</br>
30: user ID is an empty string</br>
40: local archive not found</br>
50: empty Bearer token</br>
60: archive directory not found</br>
??: when an HTTP error occurs, the application simply reflects the received HTTP status code</br>

