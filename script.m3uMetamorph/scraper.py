import requests

# Get an access token
def get_access_token():
    auth_url = f'{base_url}/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, data=data)
    return response.json()['access_token']

# Get an access token
def get_device_token(client_id, client_secret, device_code):
    auth_url = f'{base_url}/oauth/device/token'
    data = {
        'code': device_code,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(auth_url, data=data)

    print(response.json())

def get_device_code(client_id, base_url = 'https://api.trakt.tv'):
    values = f'''
    {{
        "client_id": "{client_id}"
    }}
    '''

    headers = {
    'Content-Type': 'application/json'
    }

    url = f'{base_url}/oauth/device/code'

    response_body = requests.post(url, data=values, headers=headers)

    return(response_body)

# Set your Trakt API credentials
client_id = '58b607e6f9ecedaf054be72665f538bc3038d4571be510ee920dd3fa5617ed0e'
client_secret = 'de4dbd9b7baaa317c9ab4adcc3ddca897dddf566348d8817a26502b6cefccb9a'

# Set the list ID you want to retrieve series from
list_id = '25671797'

# Set the Trakt API base URL
base_url = 'https://api.trakt.tv'

response = get_device_code(client_id)
device_code = response.json()['device_code']

get_device_token(client_id, client_secret, device_code)