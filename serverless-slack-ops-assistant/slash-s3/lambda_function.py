import os, json, urllib.parse, urllib.request, hmac, hashlib, time, base64
import boto3
from datetime import datetime

sm = boto3.client('secretsmanager')
s3 = boto3.client('s3')

BUCKET = os.environ.get("BUCKET", "")
SIGNING_SECRET_ARN = os.environ.get("SLACK_SIGNING_SECRET_ARN", "")

def get_signing_secret():
    if not SIGNING_SECRET_ARN:
        raise Exception("Missing SLACK_SIGNING_SECRET_ARN")
    val = sm.get_secret_value(SecretId=SIGNING_SECRET_ARN)['SecretString']
    try:
        return json.loads(val)['SLACK_SIGNING_SECRET']
    except Exception:
        return val  

def verify_slack_request(headers, body_raw):
    h = { (k or "").lower(): v for k, v in (headers or {}).items() }
    ts  = h.get('x-slack-request-timestamp')
    sig = h.get('x-slack-signature')
    if not ts or not sig:
        print("DBG: Missing signature headers")
        return False
    if abs(time.time() - int(ts)) > 60*5:
        print("DBG: Timestamp too old")
        return False
    base = f"v0:{ts}:{body_raw}".encode("utf-8")
    my   = "v0=" + hmac.new(get_signing_secret().encode("utf-8"), base, hashlib.sha256).hexdigest()
    ok = hmac.compare_digest(my, sig)
    if not ok:
        print("DBG: Signature mismatch")
    return ok

def respond(text, public=False):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "response_type": "in_channel" if public else "ephemeral",
            "text": text
        })
    }

def lambda_handler(event, context):
    body_raw = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body_raw = base64.b64decode(body_raw).decode("utf-8")
    headers  = event.get("headers") or {}

    print("DBG keys:", list((headers or {}).keys())[:8], "b64?", event.get("isBase64Encoded"))
    print("DBG body prefix:", body_raw[:80])

    
    if os.getenv("DISABLE_SLACK_SIGNATURE") == "true":
        print("DBG: signature verification DISABLED")
    elif not verify_slack_request(headers, body_raw):
        return {"statusCode": 401, "body": "invalid signature"}

    
    form = urllib.parse.parse_qs(body_raw)
    command = (form.get("command", [""])[0] or "").strip()
    text    = (form.get("text", [""])[0] or "").strip()
    user    = (form.get("user_name", ["unknown"])[0] or "unknown")
    ts      = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if text == "ls":
        resp = s3.list_objects_v2(Bucket=BUCKET, MaxKeys=5)
        names = [o["Key"] for o in resp.get("Contents", [])]
        listing = "\n".join(names) if names else "(bucket is empty)"
        return respond(f"*Last 5 objects in* `{BUCKET}`:\n{listing}")

    if text.startswith("find "):
        prefix = text.split(" ", 1)[1]
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix, MaxKeys=10)
        names = [o["Key"] for o in resp.get("Contents", [])]
        listing = "\n".join(names) if names else "(no matches)"
        return respond(f"*Search `{prefix}` in* `{BUCKET}`:\n{listing}")

    return respond(
        "Usage:\n"
        "• `/slash ls` – list last 5 objects\n"
        "• `/slash find <prefix>` – search by prefix\n"
        f"(Hi {user}, seen at {ts})"
    )
