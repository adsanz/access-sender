#!/usr/bin/python3


import boto3, yaml, json, requests, argparse, logging
from requests.auth import HTTPBasicAuth
from rich.logging import RichHandler
from rich.console import Console

TOKEN_OTS= None
EMAIL_OTS=None
TOKEN_SLACK=None
AWS_PROFILE=None
AWS_REGION=None
MAX_RESULTS=20


# Logger
FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

log.debug("[dim green underline]Current vars set: [/]", extra={"markup": True})
log.debug('[dim bold underline]AWS[/]', extra={"markup": True})
log.debug('[dim]AWS_PROFILE:[/] [underline dim yellow]{}[/]'.format(AWS_PROFILE), extra={"markup": True})
log.debug('[dim]AWS_REGION:[/] [underline dim yellow]{}[/]'.format(AWS_REGION), extra={"markup": True})
log.debug('[dim]MAX_RESULTS:[/] [underline dim yellow]{}[/]'.format(MAX_RESULTS), extra={"markup": True})
log.debug('[dim bold underline]SLACK[/]', extra={"markup": True})
log.debug('[dim]TOKEN_SLACK:[/] [underline dim yellow]{}[/]'.format(TOKEN_SLACK), extra={"markup": True})
log.debug('[dim bold underline]ONE TIME SECRET[/]', extra={"markup": True})
log.debug('[dim]EMAIL_OTS:[/] [underline dim yellow]{}[/]'.format(EMAIL_OTS), extra={"markup": True})
log.debug('[dim]TOKEN_OTS:[/] [underline dim yellow]{}[/]'.format(TOKEN_OTS), extra={"markup": True})

# boto secret manager client with profile
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
sm = session.client('secretsmanager')

def SecretReader(sm,secret_name):
    """
    Return in a nicely yaml format the secret
    """
    try:
        secret = sm.get_secret_value(SecretId=secret_name)
    except:
        log.exception('[red]Secret not found[/]', extra={"markup": True})
        exit(1)
    return yaml.dump(json.loads(secret['SecretString']), default_flow_style=False)

def SecretDumper(sm,secrets,secret_list):
    """
    Dump secrets
    """
    for secret in secrets['SecretList']:
        try:
            description = secret['Description']
        except KeyError:
            description = 'None'
        secret_list[secret['Name']] = description.strip()
    return secret_list

def merge_two_dicts(x, y):
    # https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z

def SecretLister(sm):
    """
    List secrets.
    """
    secret_list = {}
    try:
        with Console().status("[bold green]Listing secrets...[/]", spinner="dots"):
            secrets = sm.list_secrets(MaxResults=MAX_RESULTS)
            try:
                next_token = secrets['NextToken']
            except KeyError:
                next_token = None
            if next_token != None:
                while next_token != None:
                    try:
                        secrets = sm.list_secrets(MaxResults=MAX_RESULTS, NextToken=next_token)
                        next_token = secrets['NextToken']
                    except:
                        secrets = sm.list_secrets(MaxResults=MAX_RESULTS)
                        next_token = None
                    secret_list = merge_two_dicts(secret_list,SecretDumper(sm,secrets,secret_list))
            else:
                secrets = sm.list_secrets(MaxResults=MAX_RESULTS)
                secret_list = merge_two_dicts(secret_list,SecretDumper(sm,secrets,secret_list))
    except:
        log.exception('[red]Error listing secrets[/]', extra={"markup": True})
        exit(1)
    return yaml.dump(secret_list, default_flow_style=False)


def OneTimeSecretCreate(secret,api_token, user):
    """
    Create and print secret creation, return secret key
    """
    try:
        with Console().status("[bold green]Creating secret...[/]", spinner="dots"):
            response = requests.post('https://onetimesecret.com/api/v1/share', 
            auth=HTTPBasicAuth(user, api_token),
            data={
                'secret': secret,
                'ttl': 604800,})
    except:
        log.exception('[red]Error creating secret[/]', extra={"markup": True})
        exit(1)
    return response.json()['secret_key']

def SlackUserLookup(token,user):
    """
    Lookup user id
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Authorization': 'Bearer ' + token}
    payload = {
        "email": user
    }
    try:
        with Console().status("[bold green]Looking up user...[/]", spinner="dots"):
            response = requests.post('https://slack.com/api/users.lookupByEmail', data=payload, headers=headers)
    except:
        log.exception('[red]Error looking up user[/]', extra={"markup": True})
        exit(1)
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
    try:
        with Console().status("[bold green]Sending message...[/]", spinner="dots"):
            response = requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers)
    except:
        log.exception('[red]Error sending message to slack.[/] Make sure you have set-up [code]TOKEN_SLACK[/]', extra={"markup": True})
        exit(1)
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
parser.add_argument('-slk','--secret-lookup', help='Input the name of a secret to get its data', required=False)
parser.add_argument('-sls','--secret-list', help='If set it will list all secrets defined on the script region', required=False, type=Str2Bool, nargs='?', const=True, default=False)
args = vars(parser.parse_args())

log.info("[dim green underline]Current arguments for the script: [/]", extra={"markup": True})
for key, value in args.items():
    log.info('[dim]{}:[/] [underline dim yellow]{}[/]'.format(key,value), extra={"markup": True})

def main():
    log.info("[dim green underline]Starting script...[/]", extra={"markup": True})
    if args['secret_lookup']:
        secret_name = args['secret_lookup']
        log.info('[green]Reading secret: [/][bold yellow underline]{}[/]'.format(secret_name), extra={"markup": True})
        secret = SecretReader(sm,secret_name)
        log.info('[green dim]Secret details: [/]\n[green bold on black]{}[/]'.format(secret), extra={"markup": True})
        exit(0)


    if args['secret_list']:
        with Console().status("[bold green]Getting secrets...[/]", spinner="dots"):        
            secret = SecretLister(sm)
        for key, value in yaml.load(secret, Loader=yaml.FullLoader).items():
            log.info('[bold green]Secret[/]: [yellow bold underline]{}[/] [bold green]Description:[/] [yellow bold underline]{}[/]'.format(key, value), extra={"markup": True})
        exit(0)

    if args['name']:
        secret_name = args['name']
        log.info('[bold green]Reading secret:[/] [yellow bold underline]{}[/]'.format(secret_name),extra={"markup": True})
        secret = SecretReader(sm,secret_name)
    elif args['secret']:
        secret = args['secret']
        #check if secret is a file
        try:
            with open(secret, 'r') as f:
                log.info('[dim green]Secret is a file[/] [underline green dim]{}[/]'.format(args['secret']),extra={"markup": True})
                log.info('[green bold]Reading secret from file:[/] [green bold underline]{}[/]'.format(secret), extra={"markup": True})
                secret = f.read()
        except FileNotFoundError:
            pass
    else:
        log.exception('[yellow bold] :warning: You need to provide a secret or a secret name :warning: [/]', extra={"markup": True})
        exit(1)

    try:
        secret_key = OneTimeSecretCreate(secret,TOKEN_OTS, EMAIL_OTS)
    except:
        log.exception('[red]Error creating secret.[/] Make sure you have set-up [code]TOKEN_OTS[/] & [code]EMAIL_OTS[/]', extra={"markup": True})
        exit(1)

    log.info('[green bold]Onetime secret:[/] [yellow bold underline]https://onetimesecret.com/secret/{}[/]'.format(secret_key), extra={"markup": True})
    if args['user']:
        user_id = SlackUserLookup(TOKEN_SLACK,args['user'])
        log.info('[dim green]User id:[/] [dim yellow bold underline]]{}[/] [dim green]from user:[/] [bold yellow underline]{}[/]'.format(user_id,args['user']), extra={"markup": True})
        SlackMessage(TOKEN_SLACK,user_id,args['message'],secret_key)
        log.info('[green]Slack message sent to user:[/] [green bold underline]{}[/]'.format(args['user']), extra={"markup": True})


if __name__ == "__main__":
    main()