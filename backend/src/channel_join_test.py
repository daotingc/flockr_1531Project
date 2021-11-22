'''
    channel_join_test:
        1. channel_join() works well (default user) (no error) (contains twice join)
        2. channel_join() works well (flockr owner joins private channel) (no error)
        3. input error, Channel ID is not a valid channel
        4. access error, channel_id refers to a channel that is private
            (when the authorised user is not a global owner)
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

def test_channel_join_default_user():
    '''
        #valid test
        # register user1 and user2
        # user1 create a public channel
        # user2 join that channel
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    channel.channel_join(token_2, channel_id)
    assert u1_id in channels[0]['all_members']
    assert u2_id in channels[0]['all_members']
    assert u1_id in channels[0]['owner_members']
    assert u2_id not in channels[0]['owner_members']
    assert channel_id in users[0]['channels']
    assert channel_id in users[1]['channels']
    channel.channel_join(token_1, channel_id)
    channel.channel_join(token_2, channel_id) # user join a channel which contains that user

def test_channel_join_flockr_owner():
    '''
        #valid test
        # register user1 and user2
        # user2 create a private channel
        # user1 join that channel
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_2, 'channel_name', False)['channel_id']
    channel.channel_join(token_1, channel_id)
    assert u1_id in channels[0]['all_members']
    assert u2_id in channels[0]['all_members']
    assert channel_id in users[0]['channels']
    assert channel_id in users[1]['channels']
    assert u1_id not in channels[0]['owner_members']
    assert u2_id in channels[0]['owner_members']

def test_join_inputerror_channel():
    '''
        #10.14 change function name from "test_join_InputError_channel" to
        "test_join_inputerror_channel"
        #invalid test of the invalid channel ID
        # register user1 and user2
        # user1 create a public channel
        # user2 join channel with wrong channel_id
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    with pytest.raises(InputError):
        channel.channel_join(token_2, channel_id + 1)
    assert u1_id in channels[0]['all_members']
    assert u2_id not in channels[0]['all_members']
    assert channel_id in users[0]['channels']
    assert channel_id not in users[1]['channels']

def test_join_accesserror_channel():
    '''
        #10.14 change function name from "test_join_AccessError_channel"
        to "test_join_accesserror_channel"
        #invalid test of the private channel
        # register user1 and user2
        # user1 create a NOT-public channel
        # user2 join that channel
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', False)['channel_id']
    with pytest.raises(AccessError):
        channel.channel_join(token_2, channel_id)    
    assert u1_id in channels[0]['all_members']
    assert u2_id not in channels[0]['all_members']   
    assert channel_id in users[0]['channels']
    assert channel_id not in users[1]['channels']

    # access error when given token does not refer to a valid user
    with pytest.raises(AccessError):
        channel.channel_join('invalid_token', channel_id)
