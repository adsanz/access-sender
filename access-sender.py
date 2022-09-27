#!/usr/bin/python3


import boto3, yaml, json, requests, argparse, logging
from requests.auth import HTTPBasicAuth

TOKEN_OTS='PLACEHOLDER'
EMAIL_OTS='PLACEHOLDER'
TOKEN_SLACK='PLACEHOLDER'
AWS_PROFILE='PLACEHOLDER'
AWS_REGION='PLACEHOLDER'

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# boto secret manager client with profile
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
sm = session.client('secretsmanager')

def SecretReader(sm,secret_name):
    """
    Return in a nicely yaml format the secret
    """

    secret = sm.get_secret_value(SecretId=secret_name)
    return yaml.dump(json.loads(secret['SecretString']), default_flow_style=False)

def SecretLister(sm):
    """
    List secrets
    """
    secrets = sm.list_secrets()
    return yaml.dump(secrets['SecretList'], default_flow_style=False)
    #return secrets['SecretList']

def OneTimeSecretCreate(secret,api_token, user):
    """
    Create and print secret creation, return secret key
    """
    req = requests.post('https://onetimesecret.com/api/v1/share', 
    auth=HTTPBasicAuth(user, api_token),
    data={
        'secret': secret,
        'ttl': 604800,})
    logging.debug(yaml.dump(req.json(), default_flow_style=False))
    return req.json()['secret_key']

def SlackUserLookup(token,user):
    """
    Lookup user id
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Authorization': 'Bearer ' + token}
    payload = {
        "email": user
    }
    response = requests.post('https://slack.com/api/users.lookupByEmail', data=payload, headers=headers)
    return response.json()['user']['id']

def SlackMessage(token,user_id,message,secret_key):
    """
    Send the access via slack
    """
    headers = {'Content-Type': 'application/json; charset=UTF-8', 'Authorization': 'Bearer ' + token}
    payload = {
        "channel": user_id,
        "text": message+'https://onetimesecret.com/secret/'+secret_key,
        "as_user": True
    }
    response = requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers)
    return response.json()

def Str2Bool(v):
    """
    Helper function to allow boolean values for secret listing arg. I should upgrade to 3.9 to use: parser.add_argument('--feature', action=argparse.BooleanOptionalAction)
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')



parser = argparse.ArgumentParser(description='This script will create a secret in OneTimeSecret and send it to a user via Slack if email is provided')
parser.add_argument('-s','--secret', help='Secret to be send (do not use -n and -s at the same time)', required=False)
parser.add_argument('-n','--name', help='Secret name from AWS (name of the to be retrieved)', required=False)
parser.add_argument('-u','--user', help='Email for the user where we are going to send the secret', required=False)
parser.add_argument('-m','--message', help='Message to be sent', required=False)
parser.add_argument('-slk','--secret-lookup', help='Just get and print a secret', required=False)
parser.add_argument('-sls','--secret-list', help='If set it will list all secrets defined on the script regiion', required=False, type=Str2Bool, nargs='?', const=True, default=False)
args = vars(parser.parse_args())

logging.debug(args)

if args['secret_lookup']:
    secret_name = args['secret_lookup']
    logging.info('Reading secret: '+secret_name)
    secret = SecretReader(sm,secret_name)
    logging.info('Secret details: \n'+secret)
    exit(0)

if args['secret_list']:
    secret = SecretLister(sm)
    logging.info(secret)
    exit(0)

if args['name']:
    secret_name = args['name']
    logging.info('Reading secret: '+secret_name)
    secret = SecretReader(sm,secret_name)
elif args['secret']:
    secret = args['secret']
    #check if secret is a file
    try:
        with open(secret, 'r') as f:
            logging.info('Reading secret from file: '+secret)
            secret = f.read()
    except FileNotFoundError:
        pass
else:
    raise Exception('You need to provide a secret or a secret name')


secret_key = OneTimeSecretCreate(secret,TOKEN_OTS, EMAIL_OTS)
logging.info('Onetime secret: https://onetimesecret.com/secret/'+secret_key)
if args['user']:
    user_id = SlackUserLookup(TOKEN_SLACK,args['user'])
    logging.info('User id -> {} from user -> {}'.format(user_id,args['user']))
    slack_message = SlackMessage(TOKEN_SLACK,user_id,args['message'],secret_key)
    logging.debug(yaml.dump(slack_message, default_flow_style=False))
    logging.info('Slack message sent to user -> {}'.format(args['user']))