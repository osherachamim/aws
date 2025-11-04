import json, os, urllib.request
import boto3
from datetime import datetime

sm = boto3.client('secretsmanager')

def get_webhook():
    arn = os.environ.get('SLACK_SECRET_ARN', '')
    if arn:
        val = sm.get_secret_value(SecretId=arn)['SecretString']
        return json.loads(val).get('SLACK_WEBHOOK_URL') if val.startswith('{') else val
    return os.environ['SLACK_WEBHOOK_URL']

def post_to_slack(text):
    req = urllib.request.Request(get_webhook(),
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)

def lambda_handler(event, context):
    rec = event['Records'][0]
    event_name = rec['eventName']       # ← מזהה איזה אירוע התרחש
    bucket = rec['s3']['bucket']['name']
    key = rec['s3']['object']['key']
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if event_name.startswith("ObjectRemoved"):
        post_to_slack(f":wastebasket: The file `{key}` was **deleted** from bucket `{bucket}` at {timestamp}.")
    elif event_name.startswith("ObjectCreated"):
        post_to_slack(f":inbox_tray: A new file named `{key}` was uploaded to bucket `{bucket}` at {timestamp}.")
    else:
        post_to_slack(f":grey_question: An unrecognized event occurred in bucket `{bucket}` at {timestamp}.")

    return {"statusCode": 200}