import requests

# Set your Trakt API credentials


# Set the list ID you want to retrieve series from
list_id = '25671797'

# Set the Trakt API base URL


# Get an access token
def get_access_token(client_id, client_secret, device_code, base_url = 'https://api.trakt.tv'):
   
    auth_url = f'{base_url}/oauth/device/token'

    values = f'''
    {{
        "code": {device_code},
        "client_id": {client_id},
        "client_secret": {client_secret},
    }}
    '''
    headers = {
        'Content-Type': 'application/json',
    }
    
    response = requests.post(auth_url, headers=headers, data=values)
    
    return response.json()['access_token']

# Get series from a Trakt list
def get_series_from_list(client_id, client_secret, device_code, base_url = 'https://api.trakt.tv'):
    
    access_token = get_access_token(client_id, client_secret, device_code)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': client_id
    }
    list_url = f'{base_url}/users/98B22287/lists'

    response = requests.get(list_url, headers=headers)

    series = []
    for item in response.json():
        if item['type'] == 'show':
            series.append(item['show']['title'])
    return series

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

client_id = '58b607e6f9ecedaf054be72665f538bc3038d4571be510ee920dd3fa5617ed0e'
client_secret = 'de4dbd9b7baaa317c9ab4adcc3ddca897dddf566348d8817a26502b6cefccb9a'

response = get_device_code(client_id)

device_code = response.json()['device_code']

# Call the function to get series from the Trakt list
series_list = get_series_from_list(client_id, client_secret, device_code)

# Print the series
# for series in series_list:
#     print(series)
