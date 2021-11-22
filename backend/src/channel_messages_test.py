import pytest
import auth
import channel
import message
from data import users, channels
from error import InputError, AccessError
from channels import  channels_create
from other import clear

'''
    unfinished version, we need message_send() in iteration
    this test will mainly test errors
    test:
        1. (cannot test now) channel_messages() works well
        2. input error when Channel ID is not a valid channel
        3. input error when start is greater than the total number of messages in the channel
        4. (cannot test now) access error when Authorised user 
            is not a member of channel with channel_id

'''

@pytest.fixture
def initial_users():
    clear()
    auth.auth_register('test1@test.com', 'password', 'name_first', 'name_last')
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    auth.auth_register('test2@test.com', 'password', 'name_first', 'name_last')
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    auth.auth_register('test3@test.com', 'password', 'name_first', 'name_last')
    token_3 = auth.auth_login('test3@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel1', True)['channel_id']
    channels_create(token_3, 'channel1', True)
    channel.channel_join(token_2, channel_id)

@pytest.fixture
def initial_msg():
    for index in range(50):
        message.message_send(users[0]['token'], channels[0]['channel_id'], str(index + 1))
    message.message_send(users[1]['token'], channels[0]['channel_id'], 'user2_msg')

def test_valid_with_msg(initial_users, initial_msg):
    #assert len(channels[0]['messages']) == 51
    # get 50 from 51 msgs from 0
    resp = channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 0)
    assert len(resp['messages']) == 50
    assert resp['end'] == 50
    assert resp['messages'][0]['message'] == 'user2_msg'
    assert resp['messages'][0]['u_id'] == users[1]['u_id']
    assert resp['messages'][0]['message_id'] == 10051
    assert resp['messages'][0]['reacts'][0]['u_ids'] == []
    assert resp['messages'][0]['reacts'][0]['is_this_user_reacted'] is False
    assert resp['messages'][49]['message'] == '2'
    assert resp['messages'][49]['u_id'] == users[0]['u_id']
    assert resp['messages'][49]['message_id'] == 10002
    assert resp['messages'][49]['reacts'][0]['u_ids'] == []
    assert resp['messages'][49]['reacts'][0]['is_this_user_reacted'] is False


    # get 50 from 51 msgs from 1
    resp = channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 1)
    assert len(resp['messages']) == 50
    assert resp['end'] == -1
    assert resp['messages'][0]['message'] == '50'
    assert resp['messages'][0]['u_id'] == users[0]['u_id']
    assert resp['messages'][0]['message_id'] == 10050
    assert resp['messages'][49]['message'] == '1'
    assert resp['messages'][49]['u_id'] == users[0]['u_id']
    assert resp['messages'][49]['message_id'] == 10001

    # get 49 from 51 msgs from 2
    resp = channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 2)
    assert len(resp['messages']) == 49
    assert resp['end'] == -1
    assert resp['messages'][0]['message'] == '49'
    assert resp['messages'][0]['u_id'] == users[0]['u_id']
    assert resp['messages'][0]['message_id'] == 10049
    assert resp['messages'][48]['message'] == '1'
    assert resp['messages'][48]['u_id'] == users[0]['u_id']
    assert resp['messages'][48]['message_id'] == 10001

    # get 1 from 51 msgs from 50
    resp = channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 50)
    assert len(resp['messages']) == 1
    assert resp['end'] == -1
    assert resp['messages'][0]['message'] == '1'
    assert resp['messages'][0]['u_id'] == users[0]['u_id']
    assert resp['messages'][0]['message_id'] == 10001

def test_valid_without_msg(initial_users):
    resp = channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 0)
    assert len(resp['messages']) == 0
    assert resp['end'] == -1

def test_input_error_channelID(initial_users, initial_msg):
    # input error when Channel ID is not a valid channel
    with pytest.raises(InputError):
        assert channel.channel_messages(users[0]['token'], 123123, 0)

def test_input_error_invalid_start(initial_users, initial_msg):
    # input error when start is greater than
    # the total number of messages in the channel
    with pytest.raises(InputError):
        assert channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 52)

def test_access_error(initial_users, initial_msg):
    # access error when Authorised user is not 
    # a member of channel with channel_id
    with pytest.raises(AccessError):
        assert channel.channel_messages(users[2]['token'], channels[0]['channel_id'], 0)
    # access error when given token does not refer to a valid user
    with pytest.raises(AccessError):
        assert channel.channel_messages('invalid_token', channels[0]['channel_id'], 0)

def test_message_standard_with_react(initial_users, initial_msg):
    '''
    standard test with react
    user1 reacts msg 10002 and calls channel_messages
    '''
    message.message_react(users[0]['token'], 10002, 1)
    resp = channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 0)
    assert len(resp['messages']) == 50
    assert resp['end'] == 50
    assert resp['messages'][49]['message'] == '2'
    assert resp['messages'][49]['u_id'] == users[0]['u_id']
    assert resp['messages'][49]['message_id'] == 10002
    assert resp['messages'][49]['reacts'][0]['u_ids'] == [1]
    assert resp['messages'][49]['reacts'][0]['is_this_user_reacted'] is True

    resp = channel.channel_messages(users[0]['token'], channels[0]['channel_id'], 2)
    assert len(resp['messages']) == 49
    assert resp['messages'][47]['message_id'] == 10002
    assert resp['messages'][47]['reacts'][0]['u_ids'] == [1]
    assert resp['messages'][47]['reacts'][0]['is_this_user_reacted'] is True
