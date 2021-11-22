import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
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
def initial_data(url):
    """
        Pytest fixture that registers and logs in two users and creates
        a channel via HTTP routing.
    """
    requests.delete(url + 'clear')
    data = {
        'email' : 'test1@test.com',
        'password' : 'password',
        'name_first' : 'name_first',
        'name_last' : 'name_last',
    }
    requests.post(url + 'auth/register', json=data)
    requests.post(url + 'auth/login', json={'email': data['email'], 'password': data['password']})
    data['email'] = 'test2@test.com'
    requests.post(url + 'auth/register', json=data)
    requests.post(url + 'auth/login', json={'email': data['email'], 'password': data['password']})
    data = {
        'token' : token_generate(1, 'login'),
        'name' : 'channel',
        'is_public' : False,
    }
    requests.post(url + 'channels/create', json=data)

########################################
############# clear tests ##############
########################################

def test_clear(url):
    """
        Test for standard functionality of clear() according to spec.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture
    """
    data = {
        'email' : 'test1@test.com',
        'password' : 'password',
        'name_first': 'u',
        'name_last' : '1',
        }
    requests.post(url + 'auth/register', json=data)
    data['email'] = 'test2@test.com'
    requests.post(url + 'auth/register', json=data)
    requests.post(url + 'auth/login', json={'email': data['email'], 'password': 'password'})
    resp = requests.get(url + 'users/all', params={'token': token_generate(2, 'login')})
    assert len(json.loads(resp.text)['users']) == 2

    # create a channel
    requests.post(url + 'channels/create', json=
                {'token': token_generate(2, 'login'), 'name': 'name', 'is_public': True})
    resp = requests.get(url + 'channels/listall', params={'token': token_generate(2, 'login')})
    assert resp.status_code == 200
    assert len(json.loads(resp.text)['channels']) == 1
    # do clear
    resp = requests.delete(url + 'clear')
    assert resp.status_code == 200
    # cannot get all users
    resp = requests.get(url + 'users/all', params={'token': token_generate(2, 'login')})
    assert resp.status_code == 400
    # cannot get all channels
    resp = requests.get(url + 'channels/listall', params={'token': token_generate(2, 'login')})
    assert resp.status_code == 400

########################################
########## permission tests ############
########################################
# 1. standard test
# 2. error when given u_id is invalid
# 3. error when given permission is invalid
# 4. error when given token is invalid
def test_pemission_standard(url, initial_data):
    """
        Test for InputError exception thrown by admin_userpermission_change()
        when u_id does not refer to a valid user or whenpermission_id does not
        refer to a valid permission id.

        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param initial_data: pytest fixture to create two users and a channel
        :type initial_data: pytest fixture
    """
    # user2 try to join a private channel
    channel_data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    resp = requests.post(url + 'channel/join', json=channel_data)
    assert resp.status_code == 400

    # user1 add user2 as an onwer of flockr and user 2 can join a private channel
    permission_data = {
        'token' : token_generate(1, 'login'),
        'u_id' : 2,
        'permission_id' : 1,
    }
    resp = requests.post(url + 'admin/userpermission/change', json=permission_data)
    assert resp.status_code == 200
    resp = requests.post(url + 'channel/join', json=channel_data)
    assert resp.status_code == 200
    # user2 leave channel and user1 set user2's permission+_id as 2
    requests.post(url + 'channel/leave', json=channel_data)
    permission_data['permission_id'] = 2
    resp = requests.post(url + 'admin/userpermission/change', json=permission_data)
    assert resp.status_code == 200
    resp = requests.post(url + 'channel/join', json=channel_data)
    assert resp.status_code == 400

def test_permission_invalid_uid(url, initial_data):
    """
        Test for InputError (code=400) thrown by admin_userpermission_change() when
        invalid u_id is given.
    
        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param initial_data: pytest fixture to create two users and a channel
        :type initial_data: pytest fixture
    """
    data = {
        'token' : token_generate(1, 'login'),
        'u_id' : 0,
        'permission_id' : 1,
    }
    resp = requests.post(url + 'admin/userpermission/change', json=data)
    assert resp.status_code == 400

def test_permission_invalid_permission_id(url, initial_data):
    """
        Test for InputError (code=400) thrown by admin_userpermission_change() when
        invalid permission_id is given.
    
        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param initial_data: pytest fixture to create two users and a channel
        :type initial_data: pytest fixture
    """
    data = {
        'token' : token_generate(1, 'login'),
        'u_id' : 2,
        'permission_id' : 3,
    }
    resp = requests.post(url + 'admin/userpermission/change', json=data)
    assert resp.status_code == 400

def test_permission_invalid_token(url, initial_data):
    """
        Test for AccessError (code=400) thrown by admin_userpermission_change() when
        invalid token is given.
    
        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param initial_data: pytest fixture to create two users and a channel
        :type initial_data: pytest fixture
    """
    data = {
        'token' : token_generate(1, 'logout'),
        'u_id' : 2,
        'permission_id' : 1,
    }
    resp = requests.post(url + 'admin/userpermission/change', json=data)
    assert resp.status_code == 400
    data['token'] = 'invalid_token'
    resp = requests.post(url + 'admin/userpermission/change', json=data)
    assert resp.status_code == 400

########################################
############ search tests ##############
########################################
# 1. standard
def test_search_standard(url, initial_data):
    """
        Test for standard functionality of search() according to spec.
    
        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param initial_data: pytest fixture to create two users and a channel
        :type initial_data: pytest fixture
    """
    # do send msgs
    msg_data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'message' : ''
    }
    for i in range(6):
        msg_data['message'] = 'msg' + str(i + 1)
        requests.post(url + 'message/send', json=msg_data)

    # user 1 search (1 output)
    search_data = {
        'token' : token_generate(1, 'login'),
        'query_str' : '3',
    }
    resp = requests.get(url + 'search', params=search_data)
    assert resp.status_code == 200
    assert len(json.loads(resp.text)['messages']) == 1
    assert json.loads(resp.text)['messages'][0]['message_id'] == 10003
    assert json.loads(resp.text)['messages'][0]['u_id'] == 1
    # user 2 search (no output)
    search_data['token'] = token_generate(2, 'login')
    resp = requests.get(url + 'search', params=search_data)
    assert resp.status_code == 200
    assert len(json.loads(resp.text)['messages']) == 0

def test_search_invalid_token(url, initial_data):
    """
        Test for AccessError (code=400) thrown by search() when
        invalid token is given.
    
        :param url: pytest fixture that starts the server and gets its URL 
        :type url: pytest fixture

        :param initial_data: pytest fixture to create two users and a channel
        :type initial_data: pytest fixture
    """
    data = {
        'token' : token_generate(1, 'logout'),
        'query_str' : '3',
    }
    resp = requests.get(url + 'search', params=data)
    assert resp.status_code == 400
    data['token'] = 'invalid_token'
    resp = requests.get(url + 'search', params=data)
    assert resp.status_code == 400
