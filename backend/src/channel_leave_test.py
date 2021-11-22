'''
    chennel_leave_test:
        1. channel_leave() works well (no error) (member leave)
        2. channel_leave() works well (no error) (owner leave)
        2. input error, Channel ID is not a valid channel
        3. access error, Authorised user is not a member of channel with channel_id

    3 help functions:
        1. is_user_in_channel(channel_id, u_id)
            this will check does channel contain the given user or not
        2. is_channel_in_user_data(channel_id, u_id)
            this will check does user's data contain the given channel
        check data.py for more details
        3. is_user_an_owner(channel_id, u_id)
            this will return True if user is a onwer of that channel
            return False if not
'''
import pytest
import auth
import channel
from channels import channels_create
from data import users, channels
from error import InputError, AccessError
from other import clear

def test_channel_leave_member():
    '''
        # valid test
        # regiser user1 and user2
        # user1 create a new channel and invite user2
        # then user2 leave the channel
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user2_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'test_channel', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    channel.channel_leave(token_2, channel_id)
    assert u1_id in channels[0]['all_members']
    assert u2_id not in channels[0]['all_members']
    assert channel_id in users[0]['channels']
    assert channel_id not in users[1]['channels']

def test_channel_leave_owner():
    '''
        # valid test
        # regiser user1 and user2
        # user1 create a new channel and invite user2
        # then user1 leave the channel
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user2_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    auth.auth_login('test2@test.com', 'password')
    channel_id = channels_create(token_1, 'test_channel', True)['channel_id']
    assert u1_id in channels[0]['owner_members']
    channel.channel_invite(token_1, channel_id, u2_id)
    channel.channel_leave(token_1, channel_id)
    assert u1_id not in channels[0]['all_members']
    assert u2_id in channels[0]['all_members']
    assert channel_id not in users[0]['channels']
    assert channel_id in users[1]['channels']
    assert u1_id not in channels[0]['owner_members']
    assert u2_id not in channels[0]['owner_members']

def test_leave_inputerror_channel():
    '''
        #10.14 change function name from "test_leave_InputError_channel" to
        #"test_leave_inputerror_channel"
        #invalid test of channel id is not a valid
        # regiser user1 and user2
        # user1 create a new channel and invite user2
        # then user2 leave channel with wrong channel_id
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_nanme')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    with pytest.raises(InputError):
        channel.channel_leave(token_2, channel_id + 1)
    assert u1_id in channels[0]['all_members']
    assert u2_id in channels[0]['all_members']
    assert channel_id in users[0]['channels']
    assert channel_id in users[1]['channels']

def test_leave_accesserror_not_authorised_member():
    '''
        #change function name from "test_leave_AccessError_not_authorised_member"
        #to "test_leave_accesserror_not_authorised_member"
        #invalid test of the authorised user is not already a member of t he channel
        # register user1 and user2
        # user1 create a new channel and DO NOT invite user2
        # user2 leave channel with user1's channel_id
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    with pytest.raises(AccessError):
        channel.channel_leave(token_2, channel_id)
    assert u1_id in channels[0]['all_members']
    assert u2_id not in channels[0]['all_members']
    assert channel_id in users[0]['channels']
    assert channel_id not in users[1]['channels']
    # access error when given token does not refer to a valid user
    with pytest.raises(AccessError):
        channel.channel_leave('invalid_token', channel_id)
