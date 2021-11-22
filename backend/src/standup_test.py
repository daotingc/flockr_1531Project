import pytest
import standup
import time
from other import clear
from channels import channels_create
from error import InputError, AccessError
from data import users, channels
from standup import standup_start, standup_active, standup_send
from auth import auth_register, auth_login, token_generate
from channel import channel_join

@pytest.fixture
def initial_data():
    '''
    register 3 users and user 1 and user 3 create a channel
    user2 join channel1
    '''
    clear()
    auth_register('test1@test.com', 'password', 'user1', 'user1')
    auth_login('test1@test.com', 'password')
    auth_register('test2@test.com', 'password', 'user2', 'user2')
    auth_login('test2@test.com', 'password')
    auth_register('test3@test.com', 'password', 'user3', 'user3')
    auth_login('test3@test.com', 'password')
    channel_id_1 = channels_create(users[0]['token'], 'channel_1', True)['channel_id']
    channels_create(users[2]['token'], 'channel_1', True)
    channel_join(users[1]['token'], channel_id_1)

########################################
############# start tests ##############
########################################
# 1. standard test
# 2. access error when given token is invalid
# 3. input error when given channal_id is invalid
# 4. input error when channel has already started

def test_start_standard(initial_data):
    '''
    standard test without errors
    user 1 call standup_start in channel 1 and standup lasts 1 second
    check current time is not equal to finish_time
    curr_time add 1 second would be equal to finish_time
    '''
    curr_time = int(time.time())
    finish_time = standup_start(users[0]['token'], channels[0]['channel_id'], 1)['time_finish']
    assert curr_time != finish_time
    assert curr_time + 1 == finish_time

def test_start_error_invalid_token(initial_data):
    '''
    error test when given token is invalid
    1. non-existing
    2. logout token
    '''
    # 1. non-existing token
    with pytest.raises(AccessError):
        standup_start('invalid-token', channels[0]['channel_id'], 1)
    # 2. user1 logout token
    with pytest.raises(AccessError):
        standup_start(token_generate(0, 'logout'), channels[0]['channel_id'], 1)

def test_start_error_invalid_channel(initial_data):
    '''
    error test when given channel_id is invalid
    channel_id does not exist
    '''
    # non-existing channel with id 0
    with pytest.raises(InputError):
        standup_start(users[0]['token'], 0, 1)

def test_start_error_invalid_req(initial_data):
    '''
    error test when user calls standup_start when it is active in that channel
    user 1 calls standup_start in channel_1 and call start again
    '''
    standup_start(users[0]['token'], channels[0]['channel_id'], 3)
    with pytest.raises(InputError):
        standup_start(users[0]['token'], channels[0]['channel_id'], 3)

########################################
############# active tests #############
########################################
# 1. standard test
# 2. access error when given token is invalid
# 3. input error when given channal_id is invalid

def test_active_standard(initial_data):
    '''
    user1 calls start in channel_1
    user1 calls active in channel_1
    user3 calls active in channel_2
    '''
    standup_start(users[0]['token'], channels[0]['channel_id'], 2)
    curr_time = int(time.time())
    # chanenl 1
    active_info = standup_active(users[0]['token'], channels[0]['channel_id'])
    assert active_info['is_active'] is True
    assert active_info['time_finish'] == curr_time + 2
    # channel 2
    active_info = standup_active(users[2]['token'], channels[1]['channel_id'])
    assert active_info['is_active'] is False
    assert active_info['time_finish'] is None

def test_active_error_invalid_token(initial_data):
    '''
    error test when given token is invalid
    1. non-existing
    2. logout token
    '''
    # 1. non-existing token
    with pytest.raises(AccessError):
        standup_active('invalid-token', channels[0]['channel_id'])
    # 2. user1 logout token
    with pytest.raises(AccessError):
        standup_active(token_generate(0, 'logout'), channels[0]['channel_id'])

def test_active_error_invalid_channel(initial_data):
    '''
    error test when given channel_id is invalid
    channel_id does not exist
    '''
    # non-existing channel with id 0
    with pytest.raises(InputError):
        standup_active(users[0]['token'], 0)

########################################
############# send tests ###############
########################################
# 1. standard test (2 cases)
# 2. access error when given token is invalid
# 3. input error when given channel_id is invalid
# 4. input error when msg is too long (more than 1000 characters)
# 5. input error when standup_send in not-active channel
# 6. access error when standup_send in a channel which is not a member of

def test_send_standard_case1(initial_data):
    '''
    case1
    user1 calls start in channel1 and no send
    check no message in database
    '''
    # case1
    curr_time = int(time.time())
    finish_time = standup_start(users[0]['token'], channels[0]['channel_id'], 1)['time_finish']
    while curr_time != finish_time:
        curr_time = int(time.time())
    assert len(channels[0]['messages']) == 0

def test_send_standard_case2(initial_data):
    '''
    case2
    user1 calls start in channel1
    user1 calls standup send
    user2 calls standup send
    check msg is sent to database
    check msg time_created is correct
    check msg is sent by user1
    '''
    curr_time = int(time.time())
    finish_time = standup_start(users[0]['token'], channels[0]['channel_id'], 1)['time_finish']
    standup_send(users[0]['token'], channels[0]['channel_id'], '123')
    standup_send(users[1]['token'], channels[0]['channel_id'], '123')
    while curr_time != finish_time + 1:
        curr_time = int(time.time())
    assert len(channels[0]['messages']) == 1
    assert channels[0]['messages'][0]['time_created'] == finish_time
    assert channels[0]['messages'][0]['u_id'] == users[0]['u_id']

def test_send_error_invalid_token(initial_data):
    '''
    error test when given token is invalid
    1. non-existing
    2. logout token
    '''
    standup_start(users[0]['token'], channels[0]['channel_id'], 1)
    # 1. non-existing token
    with pytest.raises(AccessError):
        standup_send('invalid-token', channels[0]['channel_id'], '123')
    # 2. user1 logout token
    with pytest.raises(AccessError):
        standup_send(token_generate(0, 'logout'), channels[0]['channel_id'], '123')

def test_send_error_invalid_channel(initial_data):
    '''
    error test when given channel_id is invalid
    channel_id does not exist
    '''
    # non-existing channel with id 0
    with pytest.raises(InputError):
        standup_send(users[0]['token'], 0, 'msg')

def test_send_error_invalid_msg(initial_data):
    '''
    error test when msg is too long (1000 characters)
    user1 calls start in channel1 and send a too long msg
    '''
    standup_start(users[0]['token'], channels[0]['channel_id'], 1)
    with pytest.raises(InputError):
        standup_send(users[0]['token'], channels[0]['channel_id'], 'm' * 1001)

def test_send_error_not_active(initial_data):
    '''
    error test when standup is not active in given channel
    user 1 calls start in channel 1
    user 3 calls send in chanenl 2
    '''
    standup_start(users[0]['token'], channels[0]['channel_id'], 1)
    with pytest.raises(InputError):
        standup_send(users[2]['token'], channels[1]['channel_id'], 'msg')

def test_send_error_not_member(initial_data):
    '''
    error test when standup_send to wrong channel
    user 1 calls start in channel1
    user 3 calls standup_send to channel1
    '''
    standup_start(users[0]['token'], channels[0]['channel_id'], 1)
    with pytest.raises(AccessError):
        standup_send(users[2]['token'], channels[0]['channel_id'], 'msg')
