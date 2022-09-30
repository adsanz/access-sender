# Access Sender

This script allows a user to:

1. Get a secret from secret-manager, or a command line arg, or a file
2. Create a secret on onetimesecret with that content
3. Send it on slack if user is provided 

## Requirements

On the script, you shall fill this variables:
- TOKEN_OTS: holds the token for your OTS account
- EMAIL_OTS: holds the email of your OTS account
- TOKEN_SLACK: holds the token of the "Bot user token" from an slack app
- AWS_PROFILE: AWS profile used to gather secret info from secret manager
- AWS_REGION: AWS region where we are going to search those secrets

### Slack APP

To be able to send the message via slack, you will require the next scope permissions on "Bot scope":
- `im:write`
- `mpim:write`
- `users:read`
- `users:read:email`

## Usage

I'll show usage via examples:

1. Gathering a secret from AWS and sending it via slack

```log
❯ python3 access-sender.py -n "dev-db-auth" -u "example@example.com" -m "DB details:  "
23-Sep-22 11:56:27 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 11:56:29 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
23-Sep-22 11:56:29 - INFO - User id -> UY652SRT6 from user -> example@example.com
23-Sep-22 11:56:29 - INFO - Slack message sent to user -> example@example.com
```

2. Secret from command line

```log
❯ python3 access-sender.py -s "General Kenobi" -u "example@example.com" -m "Hello there! "
23-Sep-22 11:59:58 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 11:59:58 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
23-Sep-22 11:59:59 - INFO - User id -> UY652SRT6 from user -> example@example.com
23-Sep-22 11:59:59 - INFO - Slack message sent to user -> example@example.com
```

3. Secret from a file

```log
❯ cat test
Hello
❯ python3 access-sender.py -s $(pwd)/test -u "example@example.com" -m "Hello there! "
23-Sep-22 12:01:40 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 12:01:40 - INFO - Reading secret from file: /home/adsanz/projects/disco_sec/development/access-sender/test
23-Sep-22 12:01:41 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
23-Sep-22 12:01:41 - INFO - User id -> UY652SRT6 from user -> example@example.com
23-Sep-22 12:01:41 - INFO - Slack message sent to user -> example@example.com
```

4. Not sending the message via slack, just generate the secret

```log
❯ python3 access-sender.py -s "Hello there" -m "Bye"
23-Sep-22 12:03:26 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 12:03:26 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
```

I've also added two extra features to help with secret gathering, or if you just want the plaintext secret:

5. List all secrets on a region

```log
❯ python3 access-sender.py --secret-list
30-Sep-22 16:44:54 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
30-Sep-22 16:44:56 - INFO - 
xxx-xxxxx-xx: xxxxx secret key
xxx-xxx: beta xxx xxxxx key
xxx-xxx: xxxx auth xxx for xxxx

```

6. Get the value of a secret

```
❯ python3 access-sender.py --secret-lookup xxxxx-xx
27-Sep-22 16:31:33 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
27-Sep-22 16:31:33 - INFO - Reading secret: xxxx-xx
27-Sep-22 16:31:34 - INFO - Secret details: 
dbname: xxxx
host: xxxxxxxx.xxxxx.amazonaws.com
host_ro: xxxxxxxx.xxxxx.amazonaws.com
password: xxxx
username: xxxxx
```

### Note 

If you don't require slack, or OTS because you need only a secret-retrieval tool from AWS just fill AWS_REGION and AWS_PROFILE variables, or if you want to gather and create the secret on OTS fill up the AWS vars + TOKEN_OTS & EMAIL_OTS vars.

## Features

PR's are welcome!

## Notes

Tested with Python 3.8