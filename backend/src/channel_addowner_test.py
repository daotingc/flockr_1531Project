'''
    test:
        1. channel_addowner works well (no errors)
            (contains the action is carried by 1.the original owner
                                               2. the owner of flockr
                                               3. new added owner)
        2. input error when Channel ID is not a valid channel
        3. input error when When user with user id u_id is already an owner of the channel
        4. access error when the authorised user is not an owner of the flockr,
           or an owner of this channel
'''
import pytest
import auth
import channel
from channels import channels_create
from data import channels
from error import InputError, AccessError
from other import clear

def test_channel_addowner():
    '''
        #valid test
        #register user1, user2, user3, user4 and user5
        #user2 create a channel
        #user2 invites user1, user3, user4 and user5
        #user2 adds user3 as new owner (original owner)
        #user1 adds user4 as new owner (the owner of flockr)
        #user3 adds user5 as new owner (new added owner)
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    u3_id = auth.auth_register('test3@test.com', 'password', 'user3_name', 'user3_name')['u_id']
    token_3 = auth.auth_login('test3@test.com', 'password')['token']
    u4_id = auth.auth_register('test4@test.com', 'password', 'user4_name', 'user4_name')['u_id']
    u5_id = auth.auth_register('test5@test.com', 'password', 'user5_name', 'user5_name')['u_id']

    # create channel and invites users
    channel_id = channels_create(token_2, 'channel_name', True)['channel_id']
    channel.channel_invite(token_2, channel_id, u1_id)
    channel.channel_invite(token_2, channel_id, u3_id)
    channel.channel_invite(token_2, channel_id, u4_id)
    channel.channel_invite(token_2, channel_id, u5_id)

    assert u1_id not in channels[0]['owner_members']
    assert u2_id in channels[0]['owner_members']
    assert u3_id not in channels[0]['owner_members']
    assert u4_id not in channels[0]['owner_members']
    assert u5_id not in channels[0]['owner_members']

    # do add owner
    channel.channel_addowner(token_2, channel_id, u3_id)
    channel.channel_addowner(token_1, channel_id, u4_id)
    channel.channel_addowner(token_3, channel_id, u5_id)
    assert u3_id in channels[0]['owner_members']
    assert u4_id in channels[0]['owner_members']
    assert u5_id in channels[0]['owner_members']

def test_addowner_inputerror_invalid_channel():
    '''
        #10.14 change function name from "test_addowner_InputError_invalid_channel" to
        #"test_addowner_inputerror_invalid_channel"
        #invalid test of wrong channel id
        #register user1 and user2
        #user1 invites user2
        #user1 add user2 as an owner with invalid channel id
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    auth.auth_login('test2@test.com', 'password')
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    with pytest.raises(InputError):
        assert channel.channel_addowner(token_1, channel_id + 1, u2_id)
    assert u1_id in channels[0]['owner_members']
    assert u2_id not in channels[0]['owner_members']

def test_addowner_inputerror_invalid_user():
    '''
        #change function name from "test_addowner_InputError_invalid_user" to
        #"test_addowner_inputerror_invalid_user"
        #invalid test of user id and u_id is already an owner of the channel
        # register user1 and user2
        # user1 create channel1
        # user1 invites user2
        # user1 add user1 as an owner(add himself)
        # user1 add user2 as an owner twice
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    auth.auth_login('test2@test.com', 'password')
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    # user1 add himself as an owner
    with pytest.raises(InputError):
        assert channel.channel_addowner(token_1, channel_id, u1_id)
    # user1 add user2 as an owner twice
    channel.channel_addowner(token_1, channel_id, u2_id)
    with pytest.raises(InputError):
        assert channel.channel_addowner(token_1, channel_id, u2_id)
    # given u_id does not refer to a valid user
    with pytest.raises(InputError):
        assert channel.channel_addowner(token_1, channel_id, 0)
    assert u1_id in channels[0]['owner_members']
    assert u2_id in channels[0]['owner_members']

def test_addowner_accesserror_invalid_channel():
    '''
        #change function name from "test_addowner_AccessError_invalid_channel" to
        #"test_addowner_accesserror_invalid_channel"
        #invalid test of the authorised user is not an owner
        #user1 is a flocker owner and channel owner
        # register user1, user2 and user3
        # user1 create channel1 and intites user2 and user3
        # user2 add user3 as an owner of channel1
    '''
    clear()
    auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    u3_id = auth.auth_register('test3@test.com', 'password', 'user3_name', 'user3_name')['u_id']
    auth.auth_login('test3@test.com', 'password')
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    channel.channel_invite(token_1, channel_id, u3_id)
    with pytest.raises(AccessError):
        assert channel.channel_addowner(token_2, channel_id, u3_id)
    assert u2_id not in channels[0]['owner_members']
    assert u3_id not in channels[0]['owner_members']

def test_addowner_invalid_token():
    # test when given token does not refer to a valid user
    clear()
    auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    with pytest.raises(AccessError):
        assert channel.channel_addowner('invalid_token', channel_id, u2_id)
    