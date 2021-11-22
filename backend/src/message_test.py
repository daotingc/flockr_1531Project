''' Test file for message.py '''

import pytest
import auth
from other import clear
from error import InputError, AccessError
from message import message_send, message_edit, message_remove, message_send_later, message_react, message_unreact, message_pin, message_unpin
from data import channels, users
from channels import channels_create
from channel import channel_join
import time

@pytest.fixture
def initial_data():
    '''
    it is a fixture for tests.
    create user 1, user 2 and user 3
    user 1 creates channel_1 and users3 creates channel_2
    user 2 join channel_1
    '''
    clear()
    auth.auth_register('test1@test.com', 'password', 'name_first', 'name_last')
    auth.auth_register('test2@test.com', 'password', 'name_first', 'name_last')
    auth.auth_register('test3@test.com', 'password', 'name_first', 'name_last')
    auth.auth_login('test1@test.com', 'password')
    auth.auth_login('test2@test.com', 'password')
    auth.auth_login('test3@test.com', 'password')
    channels_create(users[0]['token'], 'channel_1', True)
    channel_join(users[1]['token'], channels[0]['channel_id'])
    channels_create(users[2]['token'], 'channel_2', True)

@pytest.fixture
def initial_msgs():
    '''
    it is a fixture for tests.
    user 1 send 'msg_1' to channel_1 with msg_id 10001
    user 2 send 'msg_2' to channel_1 with msg_id 10002
    user 3 send 'msg_3' to channel_2 with msg_id 20001
    '''
    message_send(users[0]['token'], channels[0]['channel_id'], 'msg_1')
    message_send(users[1]['token'], channels[0]['channel_id'], 'msg_2')
    message_send(users[2]['token'], channels[1]['channel_id'], 'msg_3')

def test_msg_send(initial_data):
    '''test for message_send'''
    # 1. msg_send works well
    message_send(users[0]['token'], channels[0]['channel_id'], 'msg_1')
    message_send(users[1]['token'], channels[0]['channel_id'], 'a' * 1000)
    message_send(users[2]['token'], channels[1]['channel_id'], '')

    all_messages = channels[0]['messages']
    assert len(all_messages) == 2
    assert all_messages[0]['u_id'] == users[0]['u_id']
    assert all_messages[0]['message'] == 'msg_1'
    assert all_messages[0]['message_id'] == 10001
    assert all_messages[1]['u_id'] == users[1]['u_id']
    assert all_messages[1]['message'] == 'a' * 1000
    assert all_messages[1]['message_id'] == 10002

    all_messages = channels[1]['messages']
    assert len(all_messages) == 1
    assert all_messages[0]['u_id'] == users[2]['u_id']
    assert all_messages[0]['message'] == ''
    assert all_messages[0]['message_id'] == 20001

    # 2. input error when message is more than 1000 characters
    with pytest.raises(InputError):
        message_send(users[0]['token'], channels[0]['channel_id'], 'a' * 1001)

    # 3. access error 1 when given token does not refer to a valid user
    with pytest.raises(AccessError):
        message_send('invalid_token', channels[0]['channel_id'], 'msg')

    # 4. access error 2 when the authorised user has not joined the channel
    #    they are trying to post to or non-exsiting channel
    with pytest.raises(AccessError):
        message_send(users[0]['token'], channels[1]['channel_id'], 'msg')
    with pytest.raises(AccessError):
        message_send(users[1]['token'], channels[1]['channel_id'], 'msg')
    with pytest.raises(AccessError):
        message_send(users[2]['token'], channels[0]['channel_id'], 'msg')
    with pytest.raises(AccessError):
        message_send(users[2]['token'], 0, 'msg')

def test_msg_remove(initial_data, initial_msgs):
    ''' test for msg_remove'''
    # 1. msg_remove works well
    message_remove(users[1]['token'], 10002)    # removed by sender
    message_send(users[0]['token'], channels[0]['channel_id'], 'msg_4')
    all_messages = channels[0]['messages']
    assert len(all_messages) == 2
    assert all_messages[0]['u_id'] == users[0]['u_id']
    assert all_messages[0]['message'] == 'msg_1'
    assert all_messages[0]['message_id'] == 10001
    assert all_messages[1]['u_id'] == users[0]['u_id']
    assert all_messages[1]['message'] == 'msg_4'
    assert all_messages[1]['message_id'] == 10003

    message_remove(users[2]['token'], 20001) # removed by owner
    message_send(users[2]['token'], channels[1]['channel_id'], 'msg_5')
    message_send(users[2]['token'], channels[1]['channel_id'], 'msg_6')
    all_messages = channels[1]['messages']
    assert len(all_messages) == 2
    assert all_messages[0]['u_id'] == users[2]['u_id']
    assert all_messages[0]['message'] == 'msg_5'
    assert all_messages[0]['message_id'] == 20002
    assert all_messages[1]['u_id'] == users[2]['u_id']
    assert all_messages[1]['message'] == 'msg_6'
    assert all_messages[1]['message_id'] == 20003

    # 2. input error when message (based on ID) no longer exists
    with pytest.raises(InputError):
        message_remove(users[1]['token'], 10002)
    with pytest.raises(InputError):
        message_remove(users[1]['token'], 100002)

    # 3. access error 1 when given token does not refer to a valid user
    with pytest.raises(AccessError):
        message_remove('invalid_token', 10003)

    # 4. access error 2 when Message with message_id was sent by
    #   the authorised user making this request
    #   or The authorised user is an owner of this channel or the flockr
    with pytest.raises(AccessError):
        message_remove(users[1]['token'], 10003)

def test_msg_edit(initial_data, initial_msgs):
    '''test for msg_edit'''
    # 1. msg_edit works well
    message_edit(users[0]['token'], 10001, 'msg_new')
    message_edit(users[1]['token'], 10002, '')
    all_messages = channels[0]['messages']
    assert len(all_messages) == 1
    assert all_messages[0]['u_id'] == users[0]['u_id']
    assert all_messages[0]['message'] == 'msg_new'
    assert all_messages[0]['message_id'] == 10001

    message_edit(users[2]['token'], 20001, 'msg_new_2')
    all_messages = channels[1]['messages']
    assert len(all_messages) == 1
    assert all_messages[0]['u_id'] == users[2]['u_id']
    assert all_messages[0]['message'] == 'msg_new_2'
    assert all_messages[0]['message_id'] == 20001

    # 2. access error when given token does not refer to a valid user
    with pytest.raises(AccessError):
        message_edit('invalid_token', 20001, 'msg')

    # 3. access error when Message with message_id was sent by
    #   the authorised user making this request
    #   or The authorised user is an owner of this channel or the flockr
    with pytest.raises(AccessError):
        message_edit(users[1]['token'], 10001, 'msg')

def test_msg_send_later_standard_1(initial_data, initial_msgs):
    '''
    no error
    user 1 calls msg_send_later in 1 second and send another msg immediately
    '''
    curr_time = int(time.time())
    end_time = curr_time + 2
    resp = message_send_later(users[0]['token'], 1, 'late msg', curr_time + 1)
    message_send(users[0]['token'], 1, 'imme msg')
    assert len(channels[0]['messages']) == 3
    while curr_time != end_time:
        curr_time = int(time.time())
    assert len(channels[0]['messages']) == 4
    assert resp['message_id'] == 10003

def test_msg_send_later_standard_2(initial_data, initial_msgs):
    '''
    no error
    user 1 calls msg_send_later in 0 second and send another msg immediately
    '''
    curr_time = int(time.time())
    resp = message_send_later(users[0]['token'], 1, 'late msg', curr_time)
    message_send(users[0]['token'], 1, 'imme msg')
    assert len(channels[0]['messages']) == 4
    assert resp['message_id'] == 10003

def test_msg_send_later_invalid_channel(initial_data, initial_msgs):
    '''
    input error
    user 1 calls msg_send_later to an non-existing channel (0)
    '''
    curr_time = int(time.time())
    with pytest.raises(InputError):
        message_send_later(users[0]['token'], 0, 'late msg', curr_time + 1)

def test_msg_send_later_invalid_msglength(initial_data, initial_msgs):
    '''
    input error
    user 1 calls msg_send_later to channel 1 with a too long msg
    '''
    curr_time = int(time.time())
    with pytest.raises(InputError):
        message_send_later(users[0]['token'], 1, 'm' * 1001, curr_time + 1)

def test_msg_send_later_invalid_time(initial_data, initial_msgs):
    '''
    input error
    user 1 calls msg_send_later to channel 1 with a time in the past
    '''
    curr_time = int(time.time())
    with pytest.raises(InputError):
        message_send_later(users[0]['token'], 1, 'late msg', curr_time - 1)

def test_msg_send_later_invalid_membership(initial_data, initial_msgs):
    '''
    access error
    user1 calls msg_send_later to channel 2
    '''
    curr_time = int(time.time())
    with pytest.raises(AccessError):
        message_send_later(users[0]['token'], 2, 'late msg', curr_time + 1)

def test_msg_send_later_invalid_token(initial_msgs, initial_data):
    '''
    access error
    pass an invalid token to msg_send_later
    '''
    curr_time = int(time.time())
    with pytest.raises(AccessError):
        message_send_later('invalid_token', 1, 'late msg', curr_time + 1)

def test_react_unreact_standard(initial_data, initial_msgs):
    '''
    no error
    user 1 reacts to the msg with msg_id 10001
    user 1 unreacts to the msg with msg_id 10001
    '''
    msg_info = channels[0]['messages'][0]
    # 1. Basic react/unreact
    # user 1 reacts to the msg with msg_id 10001
    message_react(users[0]['token'], 10001, 1)
    assert msg_info['reacts'][0]['u_ids'] == [users[0]['u_id']]
    # user 1 unreacts to the msg with msg_id 10001
    message_unreact(users[0]['token'], 10001, 1)
    assert msg_info['reacts'][0]['u_ids'] == []

def test_react_unreact_invalid_msg(initial_data, initial_msgs):
    '''
    input error
    user1 reacts to the msg with msg_id 20001
    user1 reacts to a msg with non-existing msg_id
    '''
    # user1 reacts to the msg with msg_id 20001
    with pytest.raises(InputError):
        message_react(users[0]['token'], 20001, 1)
    with pytest.raises(InputError):
        message_unreact(users[0]['token'], 20001, 1)
    # user1 reacts to a msg with non-existing msg_id
    with pytest.raises(InputError):
        message_unreact(users[1]['token'], 10004, 1)
    with pytest.raises(InputError):
        message_react(users[1]['token'], 10004, 1)

def test_react_unreact_invalid_reactid(initial_data, initial_msgs):
    '''
    input error
    user1 reacts and unreacts to the msg 10001 with wrong react_id
    '''
    with pytest.raises(InputError):
        message_react(users[0]['token'], 10001, 0)
    with pytest.raises(InputError):
        message_unreact(users[0]['token'], 10001, 0)
    
def test_react_unreact_already_done(initial_data, initial_msgs):
    '''
    input error
    user 2 reacts to msg 10002 and does it again
    user 2 unreacts to msg 10002 and does it again
    '''
    message_react(users[1]['token'], 10002, 1)
    with pytest.raises(InputError):
        message_react(users[1]['token'], 10002, 1)
    message_unreact(users[1]['token'], 10002, 1)
    with pytest.raises(InputError):
        message_unreact(users[1]['token'], 10002, 1)

def test_react_unreact_invalid_token(initial_msgs, initial_data):
    '''
    given token does not refer to a valid user
    '''
    with pytest.raises(AccessError):
        message_react('invalid_token', 10002, 1)
    with pytest.raises(AccessError):
        message_unreact('invalid_token', 10002, 1)

def test_pin_unpin_standard(initial_data, initial_msgs):
    '''
    no error
    user 1 pin 10002 msg and unpin it
    '''
    msg_info = channels[0]['messages'][1]
    message_pin(users[0]['token'], 10002)
    assert msg_info['is_pinned'] is True

    message_unpin(users[0]['token'], 10002)
    assert msg_info['is_pinned'] is False

def test_pin_unpin_invalid_msg(initial_data, initial_msgs):
    '''
    input error
    user 1 pin and unpin a non-existing msg
    '''
    with pytest.raises(InputError):
        message_pin(users[0]['token'], 10003)
    with pytest.raises(InputError):
        message_unpin(users[0]['token'], 10003)

def test_pin_unpin_already_done(initial_data, initial_msgs):
    '''
    input error
    user1 pin msg 10001 and pin it again
    user1 unpin msg 10001 and unpin it again
    '''
    message_pin(users[0]['token'], 10001)
    with pytest.raises(InputError):
        message_pin(users[0]['token'], 10001)
    # user 1 unpin msg 10001 and pin it again
    message_unpin(users[0]['token'], 10001)
    with pytest.raises(InputError):
        message_unpin(users[0]['token'], 10001)

def test_pin_unpin_not_member(initial_data, initial_msgs):
    '''
    access error
    user1 pin msg 20001 and unpin it
    '''
    with pytest.raises(AccessError):
        message_pin(users[0]['token'], 20001)
    with pytest.raises(AccessError):
        message_unpin(users[0]['token'], 20001)

def test_pin_unpin_not_owner(initial_data, initial_msgs):
    '''
    access error
    user 2 pin msg 10001 and unpin it
    '''
    with pytest.raises(AccessError):
        message_pin(users[1]['token'], 10002)
    with pytest.raises(AccessError):
        message_unpin(users[1]['token'], 10002)

def test_pin_unpin_invalid_token(initial_data, initial_msgs):
    '''
    access error
    given token is invalid
    '''
    with pytest.raises(AccessError):
        message_pin('invalid_token', 10001)
    with pytest.raises(AccessError):
        message_unpin('invalid_token', 10001)
