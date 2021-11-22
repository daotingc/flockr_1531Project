import pytest
import auth
import channel 
from channels import channels_create
from data import users, channels
from error import InputError, AccessError
from other import clear

'''
    channel_invite_test:
        1. channel_invite() works well (no error) (contains invite twice and owner of flockr)
        2. input error, Channel ID is not a valid channel
        3. input error, u_id does not refer to a valid user
        4. access error, the authorised user is not already a member of the channel
    
    3 help functions:
        1. is_user_in_channel(channel_id, u_id)
            this will check does channel contain the given user or not
        2. is_channel_in_user_data(channel_id, u_id)
            this will check does user's data contain the given channel
        3. is_user_an_owner(channel_id, u_id)
            this will return True if user is a onwer of that channel
            return False if not
'''

def test_channel_invite():
    #valid test
    # register user1, user2 and user3
    # user2 create a channel and invite user1 and user3
    # user 1 will become the owner(check assumption for more details)
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    auth.auth_login('test1@test.com', 'password')
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    u3_id = auth.auth_register('test3@test.com', 'password', 'user3_name', 'user3_name')['u_id']
    auth.auth_login('test3@test.com', 'password')
    channel_id = channels_create(token_2,'channel_name', True)['channel_id']
    channel.channel_invite(token_2, channel_id, u3_id)
    channel.channel_invite(token_2, channel_id, u3_id) # invite a user who is already a member
    channel.channel_invite(token_2, channel_id, u1_id)
    assert u1_id in channels[0]['all_members']
    assert u2_id in channels[0]['all_members']
    assert u3_id in channels[0]['all_members']
    assert channel_id in users[0]['channels']
    assert channel_id in users[1]['channels']
    assert channel_id in users[2]['channels']
    assert u1_id not in channels[0]['owner_members']
    assert u2_id in channels[0]['owner_members']
    assert u3_id not in channels[0]['owner_members']
    
def test_invite_InputError_invalid_channel():
    #invalid test of worng channel id
    # register user1 and user2
    # user1 create a new channel and invite user2 with a wrong channel_id
    clear()
    auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    auth.auth_login('test2@test.com', 'password')
    channel_id = channels_create(token_1,'channel_name', True)['channel_id']
    with pytest.raises(InputError):
        assert channel.channel_invite(token_1, channel_id + 1, u2_id)
    assert u2_id not in channels[0]['all_members']
    assert channel_id not in users[1]['channels']


def test_invite_InputError_invalid_u_id():
    #invalid test of invalid u_id
    # register user1
    # user1 create a new channel and use correct channel_id to
    # invite another user which is not exist
    clear()
    auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    with pytest.raises(InputError):
        channel.channel_invite(token_1, channel_id, 0)

def test_invite_AccessError_not_authorised_member():
    #invalid test of the authorised user is not already a member of t he channel
    # register user1, user2 and user3
    # user1 create a new channel, and user2 invite user3
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    u3_id = auth.auth_register('test3@test.com', 'password', 'user3_name', 'user3_name')['u_id']
    auth.auth_login('test3@test.com', 'password')
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id'] 
    with pytest.raises(AccessError):
        channel.channel_invite(token_2, channel_id, u3_id)
    assert u1_id in channels[0]['all_members']
    assert u2_id not in channels[0]['all_members']
    assert u3_id not in channels[0]['all_members']
    assert channel_id in users[0]['channels']
    assert channel_id not in users[1]['channels']
    assert channel_id not in users[2]['channels']
    # access error when gievn token does not refer to a valid token
    with pytest.raises(AccessError):
        channel.channel_invite('invalid_token', channel_id, u2_id)
