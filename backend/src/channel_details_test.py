'''
    test:
        1. channel_detaisl() works well (no error)
        2. input error when Channel ID is not a valid channel
        3. access error when Authorised user is not a member of channel with channel_id
'''
import pytest
import auth
import channel
from channels import channels_create
from data import users, channels
from error import InputError, AccessError
from other import clear

def test_channel_details():
    '''
        #valid test
        # register user1 and create channel1
        # register user2 and create channel2
        # register user3 and join channel1
        # user1 requests channel_details for channel1
        # user2 requests channel_details for channel2
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    u3_id = auth.auth_register('test3@test.com', 'password', 'user3_name', 'user3_name')['u_id']
    auth.auth_login('test3@test.com', 'password')
    channel_id_1 = channels_create(token_1, 'channel_name_1', True)['channel_id']
    channel_id_2 = channels_create(token_2, 'channel_name_2', True)['channel_id']
    channel.channel_invite(token_1, channel_id_1, u3_id)

    details_1 = channel.channel_details(token_1, channel_id_1)
    assert details_1['name'] == 'channel_name_1'
    assert len(details_1['owner_members']) == 1
    assert details_1['owner_members'][0]['u_id'] == u1_id
    assert len(details_1['all_members']) == 2
    assert details_1['all_members'][0]['u_id'] == u1_id
    assert details_1['all_members'][1]['u_id'] == u3_id
    details_2 = channel.channel_details(token_2, channel_id_2)
    assert details_2['name'] == 'channel_name_2'
    assert len(details_2['owner_members']) == 1
    assert details_2['owner_members'][0]['u_id'] == u2_id
    assert len(details_2['all_members']) == 1
    assert details_2['all_members'][0]['u_id'] == u2_id

def test_details_inputerror_invalid_channel():
    '''
        #invalid test of worng channel id
        #register user1
        #user1 create a channel
        #user1 requests channel_details by wrong channel_id
    '''
    clear()
    auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    with pytest.raises(InputError):
        assert channel.channel_details(token_1, channel_id + 1)

def test_details_accesserror_not_authorised_member():
    '''
        #invalid test of the authorised user is not a member of channel
        #register user1 and user2
        #user1 create a channel1
        #user2 requests channel_details of channel1
    '''
    clear()
    auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    channel_id = channels_create(token_1, 'channel_name', True)['channel_id']
    with pytest.raises(AccessError):
        channel.channel_details(token_2, channel_id)
    # access error when given token does not refer to a valid user
    with pytest.raises(AccessError):
        assert channel.channel_details('invalid_token', channel_id)
