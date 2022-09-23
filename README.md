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

```bash
❯ python3 ez.py -n "dev-db-auth" -u "example@example.com" -m "DB details:  "
23-Sep-22 11:56:27 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 11:56:29 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
23-Sep-22 11:56:29 - INFO - User id -> UY652SRT6 from user -> example@example.com
23-Sep-22 11:56:29 - INFO - Slack message sent to user -> example@example.com
```

2. Secret from command line

```bash
❯ python3 ez.py -s "General Kenobi" -u "example@example.com" -m "Hello there! "
23-Sep-22 11:59:58 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 11:59:58 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
23-Sep-22 11:59:59 - INFO - User id -> UY652SRT6 from user -> example@example.com
23-Sep-22 11:59:59 - INFO - Slack message sent to user -> example@example.com
```

3. Secret from a file

```bash
❯ cat test
Hello
❯ python3 ez.py -s $(pwd)/test -u "example@example.com" -m "Hello there! "
23-Sep-22 12:01:40 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 12:01:40 - INFO - Reading secret from file: /home/adsanz/projects/disco_sec/development/access-sender/test
23-Sep-22 12:01:41 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
23-Sep-22 12:01:41 - INFO - User id -> UY652SRT6 from user -> example@example.com
23-Sep-22 12:01:41 - INFO - Slack message sent to user -> example@example.com
```

4. Not sending the message via slack, just generate the secret

```bash
❯ python3 ez.py -s "Hello there" -m "Bye"
23-Sep-22 12:03:26 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
23-Sep-22 12:03:26 - INFO - Onetime secret: https://onetimesecret.com/secret/cdsaf3arfesf3wre2a3e24rat
```

<video src='https://github.com/adsanz/access-sender/blob/master/access_sender.mkv' width=180/>


## Features

PR's are welcome!

## Notes

Tested with Python 3.8