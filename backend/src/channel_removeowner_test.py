'''
    test:
        1. removeowner works well (no error)
            (contains normal case and rm owner of superuser)
        2. input error when Channel ID is not a valid channel
        3. input error when user with user id u_id is not an owner of the channel
        4. access error when authorised user is not an owner of the flockr,
        or an owner of this channel
'''
import pytest
import auth
import channel
from channels import channels_create
from data import channels
from error import InputError, AccessError
from other import clear

def test_channel_removeowner():
    '''
    # valid test, it would work well
    # register user1, user2 and user3
    # user2 creates channel1 and invites user1 and user3
    # user2 add user1(automatically) and user3 as owners
    # user2 remove user3 owner permission
    # user2 remove user1 owner permission(cannot happen since user1 is
    #                                     the owner of flockr)
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    auth.auth_login('test1@test.com', 'password')
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    u3_id = auth.auth_register('test3@test.com', 'password', 'user3_name', 'user3_name')['u_id']
    auth.auth_login('test3@test.com', 'password')

    channel_id = channels_create(token_2, 'channel name', True)['channel_id']
    channel.channel_invite(token_2, channel_id, u1_id)
    channel.channel_invite(token_2, channel_id, u3_id)
    assert u1_id not in channels[0]['owner_members']
    assert u2_id in channels[0]['owner_members']
    assert u3_id not in channels[0]['owner_members']

    channel.channel_addowner(token_2, channel_id, u3_id)
    assert u3_id in channels[0]['owner_members']
    channel.channel_removeowner(token_2, channel_id, u3_id)
    assert u3_id not in channels[0]['owner_members']

def test_removeowner_inputerror_invalid_channel():
    '''
    # input error when Channel ID is not a valid channel
    # register user1 and user2
    # user1 creates channel1, invites user2 and set user2 as owner
    # user1 remove user2 owner permission with invalid channel_id
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    auth.auth_login('test2@test.com', 'password')
    channel_id = channels_create(token_1, 'channel name', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    channel.channel_addowner(token_1, channel_id, u2_id)
    assert u1_id in channels[0]['owner_members']
    assert u2_id in channels[0]['owner_members']
    with pytest.raises(InputError):
        assert channel.channel_removeowner(token_1, channel_id + 1, u2_id)
    assert u2_id in channels[0]['owner_members']

def test_removeowner_inputerror_invalid_uid():
    '''
    # input error when user with user id u_id is not an owner of the channel
    # register user1 and user2
    # user1 creates channel1, invites user2 and set user2 as owner
    # user1 remove user2 owner permission with invalid channel_id
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    token_1 = auth.auth_login('test1@test.com', 'password')['token']
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    auth.auth_login('test2@test.com', 'password')

    channel_id = channels_create(token_1, 'channel name', True)['channel_id']
    channel.channel_invite(token_1, channel_id, u2_id)
    assert u1_id in channels[0]['owner_members']
    assert u2_id not in channels[0]['owner_members']
    with pytest.raises(InputError):
        assert channel.channel_removeowner(token_1, channel_id, u2_id)
    assert u2_id not in channels[0]['owner_members']
    # given u_id does not refer to a valid user
    with pytest.raises(InputError):
        channel.channel_removeowner(token_1, channel_id, 0)

def test_removeowner_accesserror_no_permission():
    '''
    # access error when the authorised user is not
    # an owner of the flockr, or an owner of this channel
    # register user1, user2 and user3
    # user2 create channel1 and invite user1 and user3
    # user3 remove user2 owner permission (access error)
    '''
    clear()
    u1_id = auth.auth_register('test1@test.com', 'password', 'user1_name', 'user1_name')['u_id']
    auth.auth_login('test1@test.com', 'password')
    u2_id = auth.auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')['u_id']
    token_2 = auth.auth_login('test2@test.com', 'password')['token']
    u3_id = auth.auth_register('test3@test.com', 'password', 'user3_name', 'user3_name')['u_id']
    token_3 = auth.auth_login('test3@test.com', 'password')['token']

    channel_id = channels_create(token_2, 'channel name', True)['channel_id']
    channel.channel_invite(token_2, channel_id, u1_id)
    channel.channel_invite(token_2, channel_id, u3_id)
    assert u2_id in channels[0]['owner_members']
    assert u3_id not in channels[0]['owner_members']
    with pytest.raises(AccessError):
        assert channel.channel_removeowner(token_3, channel_id, u2_id)
    assert u2_id in channels[0]['owner_members']
    assert u3_id not in channels[0]['owner_members']
    # access error when given token does not refer to a valid user
    with pytest.raises(AccessError):
        assert channel.channel_removeowner('invalid_token', channel_id, u3_id)
    