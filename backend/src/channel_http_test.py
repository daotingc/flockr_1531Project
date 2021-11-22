import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest
from auth import token_generate

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
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
def initial_basics(url):
    # this function would clear all data and create 6 users
    # and last 3 users would create a channel
    requests.delete(url + 'clear')
    user_data = {
        'password' : 'password',
        'name_first': 'u',
        'name_last' : '1',
        }
    for idx in range(6):
        email = str(idx + 1) + 'test@test.com'
        user_data['email'] = email
        requests.post(url + 'auth/register', json=user_data)
        resp = requests.post(url + 'auth/login', json={'email': email, 'password': 'password'})
        if idx > 2:
            token = json.loads(resp.text)['token']
            channel_data = {
                'token' : token,
                'name' : 'channel' + str(idx - 2),
                'is_public' : True,
            }
            if idx == 5:
                channel_data['is_public'] = False
            requests.post(url + 'channels/create', json=channel_data)

########################################
############ invite tests ##############
########################################
# 1. standard test
# 2. error when invalid channel_id
# 3. error when invalid u_id
# 4. error when invalid token
# 5. error when authorised user is not a member of given channel
def test_invite_standard(url, initial_basics):
    '''
    valid test (user 4(channel1 public) invite users 1)
    valid test (user 6(channel3 private) invite users 2)
    '''
    # user 4 invites uesr1 to channel1
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'u_id' : 1,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 200

    # user 6 invites user2 to channel3
    data = {
        'token' : token_generate(6, 'login'),
        'channel_id' : 3,
        'u_id' : 2,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 200

def test_invite_error_invalid_channel(url, initial_basics):
    '''
    error when given channel_id refers to an invalid channel
    '''
    # user 4 invites uesr1 to a channel with channel_id 0 (not exist)
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 0,
        'u_id' : 1,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 400

def test_invite_error_invalid_uid(url, initial_basics):
    '''
    error when given u_id refers to an invalid user
    '''
    # user 4 invites a users with id 0 to channel 1
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'u_id' : 0,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 400

def test_invite_error_invalid_token(url, initial_basics):
    '''
    error when given token does refer to valid user
    1. not login user
    2. invalid token
    '''
    # a logout user
    data = {
        'token' : token_generate(4, 'logout'),
        'channel_id' : 1,
        'u_id' : 0,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 400
    # an invalid token
    data['token'] = 'invalid_token'
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 400

def test_invite_error_not_member(url, initial_basics):
    '''
    error when authorised user is not a member of given channel
    '''
    # user6 invite user1 to channel 2(belongs to user 7)
    data = {
        'token' : token_generate(4, 'logout'),
        'channel_id' : 2,
        'u_id' : 0,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 400
    # user2 invite user1 to channel 1(belongs to user 7)
    data = {
        'token' : token_generate(2, 'logout'),
        'channel_id' : 1,
        'u_id' : 0,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 400

########################################
########### details tests ##############
########################################
# 1. standard test
# 2. error when invalid channel_id
# 3. error when invalid token
# 4. error when authorised user is not a member of given channel

def test_details_standar(url, initial_basics):
    '''
    1. valid test user6 asks details of chnanel 1
    2. invite user1 and user2 to channel1 and user6 asks details of chnanel 1
    '''
    detail_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
    }
    resp = requests.get(url + 'channel/details', params=detail_data)
    assert resp.status_code == 200
    assert json.loads(resp.text)['name'] == 'channel1'
    assert len(json.loads(resp.text)['all_members']) == 1
    assert len(json.loads(resp.text)['owner_members']) == 1
    # invite user1 and user2 to channel1
    invite_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'u_id' : 1,
    }
    requests.post(url + 'channel/invite', json=invite_data)
    invite_data['u_id'] = 2
    requests.post(url + 'channel/invite', json=invite_data)
    # user2 ask details of channel1
    detail_data['token'] = token_generate(2, 'login')
    resp = requests.get(url + 'channel/details', params=detail_data)
    assert resp.status_code == 200
    assert json.loads(resp.text)['name'] == 'channel1'
    assert len(json.loads(resp.text)['all_members']) == 3
    assert len(json.loads(resp.text)['owner_members']) == 1

def test_details_error_invalid_channel(url, initial_basics):
    '''
    error when given channel_id is invalid
    '''
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 0,
    }
    resp = requests.get(url + 'channel/details', params=data)
    assert resp.status_code == 400

def test_details_error_invalid_token(url, initial_basics):
    '''
    error when given token is invalid
    '''
    data = {
        'token' : 'invalid_token',
        'channel_id' : 1,
    }
    resp = requests.get(url + 'channel/details', params=data)
    assert resp.status_code == 400

def test_details_error_not_member(url, initial_basics):
    '''
    error when authorised user is not a member
    '''
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
    }
    resp = requests.get(url + 'channel/details', params=data)
    assert resp.status_code == 400

########################################
########### messages tests #############
########################################
# 1. standard test
# 2. error when invalid channel_id
# 3. error when invalid token
# 4. error when authorised user is not a member of given channel
# 5. error when invalid start
def test_messages_standard(url, initial_basics):
    '''
    test standard
    '''
    send_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'message' : 'msg',
    }
    resp = requests.post(url + 'message/send', json=send_data)
    return_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'start' : 0,
    }
    resp = requests.get(url + 'channel/messages', params=return_data)
    assert resp.status_code == 200
    assert json.loads(resp.text)['end'] == -1
    assert len(json.loads(resp.text)['messages']) == 1

def test_messages_error_invalid_channel(url, initial_basics):
    '''
    error when given channel_id is invalid
    '''
    return_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 0,
        'start' : 0,
    }
    resp = requests.get(url + 'channel/messages', params=return_data)
    assert resp.status_code == 400

def test_messages_error_invalid_start(url, initial_basics):
    '''
    error when given channel_id is invalid
    '''
    return_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 0,
        'start' : 100,
    }
    resp = requests.get(url + 'channel/messages', params=return_data)
    assert resp.status_code == 400

def test_messages_error_invalid_token(url, initial_basics):
    '''
    error when given token is invalid
    '''
    send_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'message' : 'msg',
    }
    resp = requests.post(url + 'message/send', json=send_data)
    return_data = {
        'token' : 'invalid_token',
        'channel_id' : 0,
        'start' : 0,
    }
    resp = requests.get(url + 'channel/messages', params=return_data)
    assert resp.status_code == 400

def test_messages_error_not_member(url, initial_basics):
    '''
    error when given user is not a member
    '''
    send_data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'message' : 'msg',
    }
    resp = requests.post(url + 'message/send', json=send_data)
    return_data = {
        'token' : token_generate(5, 'login'),
        'channel_id' : 1,
        'start' : 0,
    }
    resp = requests.get(url + 'channel/messages', params=return_data)
    assert resp.status_code == 400

########################################
############ leave tests ###############
########################################
# 1. standard test
# 2. error when invalid channel_id
# 3. error when invalid token
# 4. error when authorised user is not a member of given channel
def test_leave_standard(url, initial_basics):
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
    }
    resp = requests.post(url + 'channel/leave', json=data)
    assert resp.status_code == 200
    
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'u_id' : 1,
    }
    resp = requests.post(url + 'channel/invite', json=data)
    assert resp.status_code == 400

def test_leave_error_invalid_channel(url, initial_basics):
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 0,
    }
    resp = requests.post(url + 'channel/leave', json=data)
    assert resp.status_code == 400

def test_leave_error_invalid_token(url, initial_basics):
    data = {
        'token' : 'invalid_token',
        'channel_id' : 1,
    }
    resp = requests.post(url + 'channel/leave', json=data)
    assert resp.status_code == 400

def test_leave_error_not_member(url, initial_basics):
    data = {
        'token' : token_generate(7, 'login'),
        'channel_id' : 1,
    }
    resp = requests.post(url + 'channel/leave', json=data)
    assert resp.status_code == 400

########################################
############# join tests ###############
########################################
# 1. standard test
# 2. error when invalid channel_id
# 3. error when invalid token
# 4. error when no permission
def test_join_standard(url, initial_basics):
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
    }
    resp = requests.post(url + 'channel/join', json=data)
    assert resp.status_code == 200
    data['channel_id'] = 3
    resp = requests.post(url + 'channel/join', json=data)
    assert resp.status_code == 200
    
def test_join_error_invalid_channel(url, initial_basics):
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 0,
    }
    resp = requests.post(url + 'channel/join', json=data)
    assert resp.status_code == 400

def test_join_error_invalid_token(url, initial_basics):
    data = {
        'token' : 'invalid_token',
        'channel_id' : 1,
    }
    resp = requests.post(url + 'channel/join', json=data)
    assert resp.status_code == 400

def test_join_error_no_permission(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 3,
    }
    resp = requests.post(url + 'channel/join', json=data)
    assert resp.status_code == 400

########################################
########### add owner tests ############
########################################
# 1. standard test
# 2. error when invalid channel_id
# 3. error when invalid token
# 4. error when no permission
# 5. error when add owner twice
def test_add_owner_standard(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data['token'] = token_generate(1, 'login')
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'u_id' : 2,
    }
    resp = requests.post(url + 'channel/addowner', json=data)
    assert resp.status_code == 200
    
def test_add_owner_error_invalid_channel(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    resp = requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 0,
        'u_id' : 2,
    }
    resp = requests.post(url + 'channel/addowner', json=data)
    assert resp.status_code == 400

def test_add_owner_error_add_twice(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'u_id' : 2,
    }
    requests.post(url + 'channel/addowner', json=data)
    resp = requests.post(url + 'channel/addowner', json=data)
    assert resp.status_code == 400

def test_add_owner_error_invalid_token(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : 'invalid_token',
        'channel_id' : 1,
        'u_id' : 2,
    }
    resp = requests.post(url + 'channel/addowner', json=data)
    assert resp.status_code == 400

def test_add_owner_error_no_permission(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data['token'] = token_generate(1, 'login')
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
        'u_id' : 2,
    }
    resp = requests.post(url + 'channel/addowner', json=data)
    assert resp.status_code == 400

########################################
########### rm owner tests #############
########################################
# 1. standard test
# 2. error when invalid channel_id
# 3. error when invalid token
# 4. error when no permission
# 5. error when add owner twice
def test_rmowner_standard(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'u_id' : 2,
    }
    requests.post(url + 'channel/addowner', json=data)
    data['token'] = token_generate(4, 'login')
    resp = requests.post(url + 'channel/removeowner', json=data)
    assert resp.status_code == 200

def test_rmowner_error_invalid_channel(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'u_id' : 2,
    }
    requests.post(url + 'channel/addowner', json=data)
    data['token'] = token_generate(4, 'login')
    data['channel_id'] = 0
    resp = requests.post(url + 'channel/removeowner', json=data)
    assert resp.status_code == 400

def test_rmowner_error_not_owner(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(4, 'login'),
        'channel_id' : 1,
        'u_id' : 2,
    }
    resp = requests.post(url + 'channel/removeowner', json=data)
    assert resp.status_code == 400

def test_rmowner_error_invalid_token(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(1, 'login'),
        'channel_id' : 1,
        'u_id' : 2,
    }
    requests.post(url + 'channel/addowner', json=data)
    data = {
        'token' : 'invalid_token',
        'channel_id' : 1,
        'u_id' : 2,
    }
    resp = requests.post(url + 'channel/removeowner', json=data)
    assert resp.status_code == 400

def test_rmowner_error_no_permissino(url, initial_basics):
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
    }
    requests.post(url + 'channel/join', json=data)
    data = {
        'token' : token_generate(2, 'login'),
        'channel_id' : 1,
        'u_id' : 4,
    }
    resp = requests.post(url + 'channel/removeowner', json=data)
    assert resp.status_code == 400
