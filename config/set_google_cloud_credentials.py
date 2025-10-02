"""
Google Cloud Speech-to-Text Credentials Setup

This script helps you store your Google Cloud credentials securely using keyring.
You'll need a Google Cloud service account JSON key file.

How to get your credentials:
1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Speech-to-Text API
4. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Give it a name and description
   - Grant it the "Cloud Speech Client" role
   - Click "Create Key" and download the JSON file
5. Run this script and provide the path to your JSON file

The script will store the path securely in your system's keyring.
"""

import keyring
import os
import json
from pathlib import Path


def validate_credentials_file(file_path):
    """Validate that the file exists and is a valid Google Cloud credentials JSON."""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    try:
        with open(file_path, 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing = [field for field in required_fields if field not in creds]
        
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        if creds.get('type') != 'service_account':
            return False, "Not a service account credential file"
        
        return True, creds.get('project_id')
    
    except json.JSONDecodeError:
        return False, "Invalid JSON file"
    except Exception as e:
        return False, str(e)


def setup_google_cloud_credentials():
    """Interactive setup for Google Cloud Speech-to-Text credentials."""
    print("=" * 70)
    print("Google Cloud Speech-to-Text Credentials Setup")
    print("=" * 70)
    print()
    print(__doc__)
    print()
    
    # Get credentials file path
    while True:
        creds_path = input("Enter the path to your Google Cloud credentials JSON file: ").strip()
        creds_path = creds_path.strip('"').strip("'")  # Remove quotes if pasted
        
        if not creds_path:
            print("Error: Path cannot be empty")
            continue
        
        # Expand user home directory if needed
        creds_path = os.path.expanduser(creds_path)
        
        # Validate the file
        is_valid, message = validate_credentials_file(creds_path)
        
        if is_valid:
            project_id = message
            print(f"\n✓ Valid credentials file found!")
            print(f"  Project ID: {project_id}")
            break
        else:
            print(f"\n✗ Error: {message}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                print("Setup cancelled.")
                return False
    
    # Convert to absolute path
    creds_path = os.path.abspath(creds_path)
    
    # Store in keyring
    service_name = "GoogleCloudSTT"
    username = "credentials_path"
    
    try:
        keyring.set_password(service_name, username, creds_path)
        print(f"\n✓ Credentials path stored securely in keyring!")
        print(f"  Service: {service_name}")
        print(f"  Username: {username}")
        print(f"  Path: {creds_path}")
        print()
        print("Note: The JSON file will remain in its current location.")
        print("Do not delete or move it!")
        print()
        print("Setup complete! You can now use Google Cloud Speech-to-Text.")
        return True
    
    except Exception as e:
        print(f"\n✗ Error storing credentials: {e}")
        return False


def get_stored_credentials_path():
    """Retrieve the stored credentials path from keyring."""
    service_name = "GoogleCloudSTT"
    username = "credentials_path"
    
    try:
        creds_path = keyring.get_password(service_name, username)
        if creds_path and os.path.exists(creds_path):
            return creds_path
        elif creds_path:
            print(f"Warning: Stored credentials path does not exist: {creds_path}")
            return None
        return None
    except Exception as e:
        print(f"Error retrieving credentials: {e}")
        return None


if __name__ == "__main__":
    setup_google_cloud_credentials()

