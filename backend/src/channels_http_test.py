import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from auth import token_generate

@pytest.fixture
def url():
    """
        Pytest fixture to start the server and get its URL.
    """
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

@pytest.fixture
def create_users(url):
    """
        Pytest fixture that registers and logs in two users via HTTP routing.
    """

    # clear data
    requests.delete(url + 'clear')

    # register & log in 2 users
    for i in range(2):
        password = 'validpass' + str(i+1)
        email = 'validuser' + str(i+1) + 'email@gmail.com'
        user_data = {
            'password' : password,
            'name_first': 'User',
            'name_last' : '0' + str(i+1),
            'email': email,
        }
        requests.post(url + 'auth/register', json=user_data)
        requests.post(url + 'auth/login', json={'email': email, 'password': password})


@pytest.fixture
def create_channels(url):
    """
        Pytest fixture that creates 6 test channels with tokens from two users
        via HTTP routing.
    """
    channel_data = {
        'token': token_generate(1, 'login'),
        'name': 'Channel 01',
        'is_public': True,
    }
    requests.post(url + 'channels/create', json=channel_data)

    channel_data = {
        'token': token_generate(1, 'login'),
        'name': 'Channel 02',
        'is_public': False,
    }
    requests.post(url + 'channels/create', json=channel_data)

    channel_data = {
        'token': token_generate(2, 'login'),
        'name': 'Channel 03 User 02',
        'is_public': True,
    }
    requests.post(url + 'channels/create', json=channel_data)

    channel_data = {
        'token': token_generate(2, 'login'),
        'name': 'Channel 04 User 02',
        'is_public': False,
    }
    requests.post(url + 'channels/create', json=channel_data)

def test_http_create_invalid_name(url, create_users):
    """
        Test for InputError exception thrown by channels_create() when name
        is longer than 20 characters.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """
    query = {
        'token': token_generate(1, 'login'),
        'name': 'n' * 21,
        'is_public': True,
    }
    resp = requests.post(url + 'channels/create', json=query)
    assert resp.status_code == 400

def test_http_create_standard(url, create_users):
    """
        Test for standard functionality of channels_create() according to spec.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """
    query = {
        'token': token_generate(1, 'login'),
        'name': 'Channel 01',
        'is_public': True,
    }
    resp = requests.post(url + 'channels/create', json=query)
    assert resp.status_code == 200
    query['is_public'] = False
    resp = requests.post(url + 'channels/create', json=query)
    assert resp.status_code == 200

def test_http_create_invalid_token(url, create_users):
    """
        When two channels with duplicate details are created.
        Ensure both are created as they differ by channel_id.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """    
    query = {
        'token': token_generate(1, 'logout'),
        'name': 'Channel 01',
        'is_public': True,
    }
    resp = requests.post(url + 'channels/create', json=query)
    assert resp.status_code == 400
    query['token'] = 'invalid_token'
    resp = requests.post(url + 'channels/create', json=query)
    assert resp.status_code == 400

def test_http_list_invalid_token(url, create_users, create_channels):
    """
        Test for AccessError exception thrown by channels_create() when token
        passed in is not a valid token.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # empty
    resp = requests.get(url + 'channels/list', params={'token': ''})
    assert resp.status_code == 400

    # None
    resp = requests.get(url + 'channels/list', params={'token': None})
    assert resp.status_code == 400

    # Not the correct data type
    resp = requests.get(url + 'channels/list', params={'token': 123})
    assert resp.status_code == 400

    # Not an authorised user
    bad_token = 'invalid_token'
    resp = requests.get(url + 'channels/list', params={'token': bad_token})
    assert resp.status_code == 400

def test_http_list_standard(url, create_users, create_channels):
    """
        Test for standard functionality of channels_list() according to spec.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    resp = requests.get(url + 'channels/list', params={'token': token_generate(1, 'login')})
    payload = resp.json()
    assert resp.status_code == 200

    # test length and accuracy of returned channels list, making sure
    # channels of User 2 is not listed
    assert len(payload['channels']) == 2
    channel_01_listed = payload['channels'][0]
    channel_02_listed = payload['channels'][1]
    assert channel_01_listed['channel_id'] == 1
    assert channel_01_listed['name'] == 'Channel 01'
    assert channel_02_listed['channel_id'] == 2
    assert channel_02_listed['name'] == 'Channel 02'

def test_http_list_standard_no_channel(url, create_users):
    """
        Test for standard functionality of channels_list() according to spec.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """
    resp = requests.get(url + 'channels/list', params={'token': token_generate(1, 'login')})
    payload = resp.json()
    assert resp.status_code == 200
    assert len(payload['channels']) == 0

def test_http_listall_invalid_token(url, create_users, create_channels):
    """
        Test for AccessError exception thrown by channels_create() when token
        passed in is not a valid token.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # empty
    resp = requests.get(url + 'channels/listall', params={'token': ''})
    assert resp.status_code == 400

    # None
    resp = requests.get(url + 'channels/listall', params={'token': None})
    assert resp.status_code == 400

    # Not the correct data type
    resp = requests.get(url + 'channels/listall', params={'token': 123})
    assert resp.status_code == 400

    # Not an authorised user
    resp = requests.get(url + 'channels/listall', params={'token': 'invalid_token'})
    assert resp.status_code == 400

def test_http_listall_standard(url, create_users, create_channels):
    """
        Test for standard functionality of channels_list() according to spec.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    resp = requests.get(url + 'channels/listall', params={'token': token_generate(1, 'login')})
    payload = resp.json()

    # test length and accuracy of returned channels list, making sure 
    # channels of User 2 is not listed
    assert len(payload['channels']) == 4
    channel_01_listed = payload['channels'][0]
    channel_02_listed = payload['channels'][1]
    channel_03_listed = payload['channels'][2]
    channel_04_listed = payload['channels'][3]
    assert channel_01_listed['channel_id'] == 1
    assert channel_01_listed['name'] == 'Channel 01'
    assert channel_02_listed['channel_id'] == 2
    assert channel_02_listed['name'] == 'Channel 02'
    assert channel_03_listed['channel_id'] == 3
    assert channel_03_listed['name'] == 'Channel 03 User 02'
    assert channel_04_listed['channel_id'] == 4
    assert channel_04_listed['name'] == 'Channel 04 User 02'

def test_http_listall_standard_no_channel(url, create_users):
    """
        Test for standard functionality of channels_listall() according to spec.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """
    resp = requests.get(url + 'channels/list', params={'token': token_generate(1, 'login')})
    payload = resp.json()
    assert resp.status_code == 200
    assert len(payload['channels']) == 0
