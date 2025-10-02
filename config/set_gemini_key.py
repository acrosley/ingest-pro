import keyring
# For a generic password
service_name = "MyGeminiApp" # Or any name you choose
username = "gemini_api_key_user" # Can be a dummy username
api_key_value = "AIzaSyCZkI8UCsShz-Hn28y-8lNLuB7-6bEdEKc"

keyring.set_password(service_name, username, api_key_value)
print(f"API Key stored for service '{service_name}' and username '{username}'.")

# ren keyring.py set_gemini_key.py