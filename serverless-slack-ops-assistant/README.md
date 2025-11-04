# Serverless Slack Ops Assistant (AWS Lambda + API Gateway + S3)


This project connects **Slack** and **AWS** in a **serverless way** using **Lambda**, **API Gateway**, and **S3**.

It performs two simple but powerful tasks:
1. Enables Slack users to query S3 directly with a Slash Command (`/slash ls`, `/slash find <prefix>`).  
2. Sends **real-time Slack alerts** whenever a file is **uploaded or deleted** from the bucket — including timestamps.

No EC2. No servers. Just events and Lambdas,  the way serverless should be.

---

## 🧩 Architecture Overview

Here’s the architecture diagram illustrating the end-to-end flow:

![Serverless Slack Ops Assistant Architecture](serverless-slack-ops-assistant/Serverless-Slack-Ops.png)

### Flow Summary
- **Slack Slash Command** triggers **API Gateway**.
- **API Gateway** invokes **Lambda `slash-s3`**, which authenticates via **Slack Signing Secret** from **Secrets Manager** and performs S3 operations.
- **S3** events (`ObjectCreated`, `ObjectRemoved`) trigger **Lambda `s3-to-slack`**, which reads a Webhook URL from **Secrets Manager** and posts alerts to Slack.

---

## ⚙️ Components

### Lambda Functions
- **`slash-s3`** – Handles Slack Slash Commands (`ls`, `find`). Authenticates requests (HMAC) and interacts with S3.  
- **`s3-to-slack`** – Listens for `ObjectCreated:*` and `ObjectRemoved:*` events and sends Slack messages about added/deleted files.

### AWS Services
- **API Gateway (HTTP API)** – Public endpoint for Slash Commands.  
- **S3** – Object storage and event source.  
- **Secrets Manager** – Stores Slack Webhook and Signing Secret securely.  
- **CloudWatch** – Logs Lambda executions for debugging.  
- **Slack App** – Combines Slash Command and Incoming Webhook.

---

## 🧰 Slack App Setup

To connect this project with Slack, create a custom **Slack App**:

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps) → **Create New App**.  
2. Under **Features → Slash Commands**, click **Create New Command**:
   - **Command:** `/slash`  
   - **Request URL:** your API Gateway Invoke URL (e.g., `https://xxxx.execute-api.us-east-1.amazonaws.com/slash`)  
   - **Short Description:** “Query S3 bucket”  
   - **Usage Hint:** “ls / find <prefix>`  
3. Under **Features → Incoming Webhooks**, enable it and add a **Webhook URL** for the desired Slack channel.  
4. Copy these two secrets and store them in AWS Secrets Manager:
   - `SLACK_SIGNING_SECRET` (from *Basic Information → App Credentials*)  
   - `SLACK_WEBHOOK_URL` (from *Incoming Webhooks*)  
5. Redeploy your Lambda functions after saving the secrets.

---

## 💬 Example in Action

### Slash Command:
```
/slash ls
```

**Response:**

<img width="478" height="194" alt="image" src="https://github.com/user-attachments/assets/e7582d6f-65b4-47b3-a8d3-51eff851c2db" />

```
Last 5 objects in devops-lab-uploads-osher:
hello-world
logs/2025-11-04.json
```

### Automatic Slack Alerts:

<img width="856" height="87" alt="image" src="https://github.com/user-attachments/assets/d1d4e879-340b-4ade-b253-835fe08f30b9" />

```
📥 A new file named `video.mp4` was uploaded to bucket `devops-lab-uploads-osher` at 2025-11-04 10:43:32 UTC.
🗑️ The file `tmp/data.json` was deleted from bucket `devops-lab-uploads-osher` at 2025-11-04 10:55:10 UTC.
```

---

## 🔐 Environment Variables

| Lambda | Variable | Description |
|---------|-----------|-------------|
| `slash-s3` | `BUCKET` | Target S3 bucket name |
|  | `SLACK_SIGNING_SECRET_ARN` | ARN of secret containing the Slack Signing Secret |
|  | *(optional)* `DISABLE_SLACK_SIGNATURE` | Disable Slack signature verification (for testing) |
| `s3-to-slack` | `SLACK_SECRET_ARN` | ARN containing key `SLACK_WEBHOOK_URL` |
|  | `SLACK_WEBHOOK_URL` | Direct Slack Webhook (alternative) |

---
### 🧮 Setting Environment Variables in Lambda

After deploying both Lambda functions (`slash-s3` and `s3-to-slack`), make sure to configure the required **Environment Variables** in the AWS Console.

#### Lambda Service
1. Navigate to your Lambda function.  
2. Under **Configuration → Environment variables**, click **Edit**.  
3. Add the following key-value pairs:

**For `slash-s3`:**
```
BUCKET = your-s3-bucket-name
SLACK_SIGNING_SECRET_ARN = arn:aws:secretsmanager:region:account-id:secret:slack-signing-secret
```
(Optional for testing)
```
DISABLE_SLACK_SIGNATURE = true
```

**For `s3-to-slack`:**
```
SLACK_WEBHOOK_URL = https://hooks.slack.com/services/XXXXX/XXXXX/XXXXX
SLACK_SECRET_ARN = arn:aws:secretsmanager:region:account-id:secret:slack-webhook-secret
```

4. Click **Save** and then **Deploy** the function.
## 🪪 IAM Permissions

| Function | Required Permissions |
|-----------|----------------------|
| `slash-s3` | `secretsmanager:GetSecretValue`, `s3:ListBucket` |
| `s3-to-slack` | `secretsmanager:GetSecretValue` |

---

## 🛠️ Event Triggers

**API Gateway → `slash-s3`:**
- Method: `POST /slash`
- Auto-deploy to `$default`
- Set the Invoke URL as the **Slack Slash Command Request URL**.

**S3 → `s3-to-slack`:**
- Events: `s3:ObjectCreated:*` and `s3:ObjectRemoved:*`
- Destination: Lambda `s3-to-slack`.

---

## 🩺 Troubleshooting

- **`dispatch_failed` in Slack:**  
  - Check CloudWatch logs of `slash-s3`.  
  - Ensure correct ENV variables and IAM permissions.  
  - Verify `/slash` route path in API Gateway.
- **`Invalid length for parameter SecretId`** → ENV name mismatch.  
- **`401 invalid signature`** → Check Base64 decoding or Signing Secret value.



## 🧱 Repository Structure

```
serverless-slack-ops-assistant/
├─ slash-s3/
  ├─ lambda_function.py
├─s3-to-slack/
  └─ /lambda_function.py
|-Serverless-Slack-Ops.png
└─ README.md
```

