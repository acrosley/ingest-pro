# How to Create a Service Account Key (Not OAuth Client)

## The Difference

❌ **OAuth Client Credentials** (What you have now):
- Used for apps that need user permission
- JSON starts with `{"installed": {...}}`
- Won't work with our Speech-to-Text implementation

✅ **Service Account Key** (What you need):
- Used for server-to-server API calls
- JSON starts with `{"type": "service_account", ...}`
- Contains a `private_key` field
- This is what we need!

## Step-by-Step: Create Service Account Key

### 1. Go to Service Accounts Page
Open this link in your browser:
https://console.cloud.google.com/iam-admin/serviceaccounts?project=call-transcription-473916

### 2. Create a New Service Account
- Click **"+ CREATE SERVICE ACCOUNT"** at the top
- Fill in:
  - **Service account name**: `call-transcription-service`
  - **Service account ID**: (auto-filled, leave as is)
  - **Description**: "Service account for call transcription pipeline"
- Click **"CREATE AND CONTINUE"**

### 3. Grant Permissions
- In the "Role" dropdown, search for: **Cloud Speech Client**
- Select it
- Click **"CONTINUE"**
- Click **"DONE"** (skip the optional user access step)

### 4. Create and Download the Key
- You'll see your new service account in the list
- Click on the **email address** of the service account you just created
- Go to the **"KEYS"** tab at the top
- Click **"ADD KEY"** dropdown
- Select **"Create new key"**
- Choose **JSON** format
- Click **"CREATE"**
- A JSON file will automatically download (e.g., `call-transcription-473916-abc123.json`)

### 5. Verify the Downloaded File
Open the JSON file in a text editor. It should look like this:

```json
{
  "type": "service_account",
  "project_id": "call-transcription-473916",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "call-transcription-service@call-transcription-473916.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

✅ Key indicators you have the RIGHT file:
- First line is `"type": "service_account"`
- Has a `"private_key"` field with `-----BEGIN PRIVATE KEY-----`
- Has a `"client_email"` field ending in `.iam.gserviceaccount.com`

### 6. Save and Use the File
1. Move the downloaded JSON file to your secure location:
   ```
   D:\GoogleCloudKeys\call-transcription-service-account.json
   ```

2. Run the setup script again:
   ```powershell
   python config/set_google_cloud_credentials.py
   ```

3. Enter the path when prompted:
   ```
   D:\GoogleCloudKeys\call-transcription-service-account.json
   ```

## What Happened?

You accidentally downloaded **OAuth 2.0 client credentials** instead of a **service account key**. This is a common mistake! 

- OAuth credentials are for apps that need user permission (like "Sign in with Google")
- Service accounts are for server-to-server API calls (like our transcription pipeline)

## Quick Links

- Service Accounts page: https://console.cloud.google.com/iam-admin/serviceaccounts?project=call-transcription-473916
- Enable Speech-to-Text API: https://console.cloud.google.com/apis/library/speech.googleapis.com?project=call-transcription-473916

## Need Help?

If you still see errors after following these steps, check:
1. The JSON file starts with `"type": "service_account"`
2. The Speech-to-Text API is enabled in your project
3. The service account has the "Cloud Speech Client" role

