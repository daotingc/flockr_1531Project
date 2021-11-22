import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from auth import token_generate
import time

@pytest.fixture
def url():
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
    # this function would clear all data and create 3 users
    # user1 would create channel 1 and user3 would create channel2
    # user2 would join channel1
    requests.delete(url + 'clear')
    # create 3 users
    user_data = {
        'password' : 'password',
        'name_first': 'u',
        'name_last' : '1',
        }
    for idx in range(3):
        email = str(idx + 1) + 'test@test.com'
        user_data['email'] = email
        requests.post(url + 'auth/register', json=user_data)
        requests.post(url + 'auth/login', json={'email': email, 'password': 'password'})
    # create 2channels and user2 join channel1
    data = {
        'token' : token_generate(1, 'login'),
        'name' : 'channel_1',
        'is_public' : True,
    }
    requests.post(url + 'channels/create', json=data)
    data['token'] = token_generate(3, 'login')
    data['name'] = 'channel_1'
    requests.post(url + 'channels/create', json=data)
    requests.post(url + 'channel/join', json={'token': token_generate(2, 'login'), 'channel_id': 1})

########################################
############# start tests ##############
########################################
# 1. standard test
# 2. access error when given token is invalid
# 3. input error when given channal_id is invalid
# 4. input error when channel has already started
def test_start_standard(url, initial_data):
    '''
    standard test without errors
    user 1 call standup_start in channel 1 and standup lasts 1 second
    check current time is not equal to finish_time
    curr_time add 1 second would be equal to finish_time
    '''
    curr_time = int(time.time())
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    resp = requests.post(url + 'standup/start', json=data)
    assert resp.status_code == 200
    assert json.loads(resp.text) == {'time_finish': curr_time + 1}

def test_start_error_invalid_token(url, initial_data):
    '''
    error test when given token is invalid
    1. non-existing
    2. logout token
    '''
    data = {
        'channel_id' : 1,
        'length' : 1
    }
    # 1. non-existing token
    data['token'] = 'invalid_token'
    resp = requests.post(url + 'standup/start', json=data)
    assert resp.status_code == 400
    # 2. user1 logout token
    data['token'] = token_generate(0, 'logout')
    resp = requests.post(url + 'standup/start', json=data)
    assert resp.status_code == 400

def test_start_error_invalid_channel(url, initial_data):
    '''
    error test when given channel_id is invalid
    channel_id does not exist
    '''
    # non-existing channel with id 0
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 0,
        'length' : 1
    }
    resp = requests.post(url + 'standup/start', json=data)
    assert resp.status_code == 400

def test_start_error_invalid_req(url, initial_data):
    '''
    error test when user calls standup_start when it is active in that channel
    user 1 calls standup_start in channel_1 and call start again
    '''
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    resp = requests.post(url + 'standup/start', json=data)
    assert resp.status_code == 200
    resp = requests.post(url + 'standup/start', json=data)
    assert resp.status_code == 400

########################################
############# active tests #############
########################################
# 1. standard test
# 2. access error when given token is invalid
# 3. input error when given channal_id is invalid

def test_active_standard(url, initial_data):
    '''
    user1 calls start in channel_1
    user1 calls active in channel_1
    user3 calls active in channel_2
    '''
    # start standup in channel1
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    requests.post(url + 'standup/start', json=data)

    # chanenl 1 active check
    curr_time = int(time.time())
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
    }
    resp = requests.get(url + '/standup/active', params=data)
    assert resp.status_code == 200
    assert json.loads(resp.text)['is_active'] == True
    assert json.loads(resp.text)['time_finish'] == curr_time + 1
    # channel 2 active check
    data = {
        'token' : token_generate(3, 'login'),
        'channel_id' : 2,
    }
    resp = requests.get(url + '/standup/active', params=data)
    assert resp.status_code == 200
    assert json.loads(resp.text)['is_active'] == False
    assert json.loads(resp.text)['time_finish'] is None

def test_active_error_invalid_token(url, initial_data):
    '''
    error test when given token is invalid
    1. non-existing
    2. logout token
    '''
    data = {
        'token' : 'invalid_token',
        'channel_id' : 1,
    }
    # 1. non-existing token
    resp = requests.get(url + '/standup/active', params=data)
    assert resp.status_code == 400
    # 2. user1 logout token
    data['token'] = token_generate(1, 'logout')
    resp = requests.get(url + '/standup/active', params=data)
    assert resp.status_code == 400

def test_active_error_invalid_channel(url, initial_data):
    '''
    error test when given channel_id is invalid
    channel_id does not exist
    '''
    # non-existing channel with id 0
    data = {
        'token' : 'invalid_token',
        'channel_id' : 0,
    }
    resp = requests.get(url + '/standup/active', params=data)
    assert resp.status_code == 400

########################################
############# send tests ###############
########################################
# 1. standard test
# 2. access error when given token is invalid
# 3. input error when given channel_id is invalid
# 4. input error when msg is too long (more than 1000 characters)
# 5. input error when standup_send in not-active channel
# 6. access error when standup_send in a channel which is not a member of

def test_send_standard(url, initial_data):
    '''
    user1 calls start in channel1
    user1 calls standup send
    user2 calls standup send
    '''
    # start a standup
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    requests.post(url + 'standup/start', json=data)
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'message' : 'msg',
    }
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 200
    data['token'] = token_generate(2, 'login')
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 200

def test_send_error_invalid_token(url, initial_data):
    '''
    error test when given token is invalid
    1. non-existing
    2. logout token
    '''
    # start a standup
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    requests.post(url + 'standup/start', json=data)
    # 1. non-existing token
    data = {
        'token' : 'invalid_token',
        'channel_id' : 1,
        'message' : 'msg',
    }
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 400
    # 2. user1 logout token
    data = {
        'token' : token_generate(1, 'logout'),
        'channel_id' : 1,
        'message' : 'msg',
    }
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 400

def test_send_error_invalid_channel(url, initial_data):
    '''
    error test when given channel_id is invalid
    channel_id does not exist
    '''
    # start a standup
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    requests.post(url + 'standup/start', json=data)
    # 1. non-existing channel with id 0
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 0,
        'message' : 'msg'
    }
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 400

def test_send_error_invalid_msg(url, initial_data):
    '''
    error test when msg is too long (1000 characters)
    user1 calls start in channel1 and send a too long msg
    '''
    # start a standup
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    requests.post(url + 'standup/start', json=data)
    # send a too long msg
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'message' : 'm' * 1001
    }
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 400

def test_send_error_not_active(url, initial_data):
    '''
    error test when standup is not active in given channel
    user 1 calls start in channel 1
    user 3 calls send in chanenl 2
    '''
    # start a standup
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    requests.post(url + 'standup/start', json=data)
    # user 3 calls send in channel 2
    data = {
        'token' : token_generate(3, 'login'),
        'channel_id' : 2,
        'message' : 'msg'
    }
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 400

def test_send_error_not_member(url, initial_data):
    '''
    error test when standup_send to wrong channel
    user 1 calls start in channel1
    user 3 calls standup_send to channel1
    '''
    # start a standup
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'length' : 1
    }
    requests.post(url + 'standup/start', json=data)
    # user 3 calls send in channel 2
    data = {
        'token' : token_generate(3, 'login'),
        'channel_id' : 1,
        'message' : 'msg'
    }
    resp = requests.post(url + 'standup/send', json=data)
    assert resp.status_code == 400

