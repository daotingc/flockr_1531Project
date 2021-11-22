import pytest
from other import clear
from data import users, channels
from channels import channels_create
from other import users_all, clear, search, admin_userpermission_change
from auth import auth_login, auth_register
from error import AccessError, InputError
from channel import channel_join
from message import message_send, message_react

@pytest.fixture
def create_users():
    """
        Pytest fixture that registers and logs in two users for use in relevant tests.
    """

    clear()
    auth_register('validuseremail@gmail.com', 'validpass', 'User', 'One')
    auth_register('validuser2email@gmail.com', 'validpass2', 'User', 'Two')
    auth_register('validuser3email@gmail.com', 'validpass3', 'User', 'Three')
    auth_login('validuseremail@gmail.com', 'validpass')
    auth_login('validuser2email@gmail.com', 'validpass2')
    auth_login('validuser3email@gmail.com', 'validpass3')

def test_clear_standard():
    """
        Test for standard functionality of clear() according to spec.
    """

    # initial clear
    clear()

    # preliminary assertions
    assert len(users) == 0
    assert len(channels) == 0

    # create users
    auth_register('validuseremail@gmail.com', 'validpass', 'User', 'One')
    auth_register('validuser2email@gmail.com', 'validpass2', 'User', 'Two')
    token_1 = auth_login('validuseremail@gmail.com', 'validpass')['token']
    token_2 = auth_login('validuser2email@gmail.com', 'validpass2')['token']

    # create channels
    channels_create(token_1, 'Channel 01', True)
    channels_create(token_1, 'Channel 02', False)
    channels_create(token_2, 'Channel 03', False)

    # intermediate assertions
    assert len(users) == 2
    assert len(channels) == 3

    # invoke clear() for testing
    clear()

    # final assertions
    assert len(users) == 0
    assert len(channels) == 0

def test_usersall_invalid_token(create_users):
    """
        Test for AccessError exception thrown by users_all() when token
        passed in is not a valid token.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """

    # empty
    with pytest.raises(AccessError):
        users_all('')

    # None
    with pytest.raises(AccessError):
        users_all(None)

    # Not the correct data type
    with pytest.raises(AccessError):
        users_all(123)

    # Not an authorised user
    bad_token = 'invalid_token'
    with pytest.raises(AccessError):
        users_all(bad_token)

def test_usersall_standard(create_users):
    """
        Test for standard functionality of users_all() according to spec.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """
    
    users_return = users_all(users[1]['token'])

    # check correct details have been returned
    assert users_return['users'][0]['u_id'] == users[0]['u_id']
    assert users_return['users'][0]['email'] == 'validuseremail@gmail.com'
    assert users_return['users'][0]['name_first'] == 'User'
    assert users_return['users'][0]['name_last'] == 'One'
    assert users_return['users'][0]['handle_str'] == 'userone'

    assert users_return['users'][1]['u_id'] == users[1]['u_id']
    assert users_return['users'][1]['u_id'] == users[1]['u_id']
    assert users_return['users'][1]['email'] == 'validuser2email@gmail.com'
    assert users_return['users'][1]['name_first'] == 'User'
    assert users_return['users'][1]['name_last'] == 'Two'
    assert users_return['users'][1]['handle_str'] == 'usertwo'

    assert users_return['users'][2]['u_id'] == users[2]['u_id']
    assert users_return['users'][2]['email'] == 'validuser3email@gmail.com'
    assert users_return['users'][2]['name_first'] == 'User'
    assert users_return['users'][2]['name_last'] == 'Three'
    assert users_return['users'][2]['handle_str'] == 'userthree'

def test_search_invalid_token(create_users):
    """
        Test for AccessError exception thrown by search() when token
        passed in is not a valid token.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """
    # empty
    with pytest.raises(AccessError):
        search('', 'query')

    # None
    with pytest.raises(AccessError):
        search(None, 'query')

    # Not the correct data type
    with pytest.raises(AccessError):
        search(123, 'query')

    # Not an authorised user
    with pytest.raises(AccessError):
        search('bad_token', 'query')

def test_search_no_cross_join_channel(create_users):
    """
        Test for standard functionality of search() according to spec when
        channel_join() is not used (i.e. only user in each channel is the channel creator).

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """

    # create channels for the first user
    user01_channel01 = channels_create(users[0]['token'], 'Channel 01 User 01', True)
    user01_channel02 = channels_create(users[0]['token'], 'Channel 02 User 01', False)

    # create channels for the second user
    user02_channel01 = channels_create(users[1]['token'], 'Channel 01 User 02', False)
    user02_channel02 = channels_create(users[1]['token'], 'Channel 02 User 02', True)

    # send messages for first user
    msg11 = message_send(users[0]['token'], user01_channel01['channel_id'], 'Hello, channel one')
    msg12 = message_send(users[0]['token'], user01_channel02['channel_id'], 'Hello, channel two?')
    msg13 = message_send(users[0]['token'], user01_channel01['channel_id'], 'Wait is this really channel one?')
    msg14 = message_send(users[0]['token'], user01_channel01['channel_id'], 'Yep it is?')
    msg15 = message_send(users[0]['token'], user01_channel02['channel_id'], 'Hola amigos!')

    # send messages for the second user
    msg21 = message_send(users[1]['token'], user02_channel01['channel_id'], 'What\'s up channel one')
    msg22 = message_send(users[1]['token'], user02_channel02['channel_id'], 'What\'s up channel two')
    msg23 = message_send(users[1]['token'], user02_channel01['channel_id'], 'You channel one or What?')
    msg24 = message_send(users[1]['token'], user02_channel01['channel_id'], 'What? Yeah I am')
    msg25 = message_send(users[1]['token'], user02_channel02['channel_id'], 'What?')

    # invoke and test search()
    messages = search(users[0]['token'], 'Hello')
    assert len(messages['messages']) == 2
    assert messages['messages'][0]['message_id'] == msg11['message_id']
    assert messages['messages'][0]['u_id'] == users[0]['u_id']
    assert messages['messages'][0]['message'] == 'Hello, channel one'
    assert messages['messages'][1]['message_id'] == msg12['message_id']
    assert messages['messages'][1]['u_id'] == users[0]['u_id']
    assert messages['messages'][1]['message'] == 'Hello, channel two?'

    messages = search(users[0]['token'], 'Hola')
    assert len(messages['messages']) == 1
    assert messages['messages'][0]['message_id'] == msg15['message_id']
    assert messages['messages'][0]['u_id'] == users[0]['u_id']
    assert messages['messages'][0]['message'] == 'Hola amigos!'

    messages = search(users[0]['token'], '?')
    assert len(messages['messages']) == 3
    assert messages['messages'][0]['message_id'] == msg13['message_id']
    assert messages['messages'][0]['u_id'] == users[0]['u_id']
    assert messages['messages'][0]['message'] == 'Wait is this really channel one?'
    assert messages['messages'][1]['message_id'] == msg14['message_id']
    assert messages['messages'][1]['u_id'] == users[0]['u_id']
    assert messages['messages'][1]['message'] == 'Yep it is?'
    assert messages['messages'][2]['message_id'] == msg12['message_id']
    assert messages['messages'][2]['u_id'] == users[0]['u_id']
    assert messages['messages'][2]['message'] == 'Hello, channel two?'

    messages = search(users[1]['token'], 'What')
    assert len(messages['messages']) == 5
    assert messages['messages'][0]['message_id'] == msg21['message_id']
    assert messages['messages'][0]['u_id'] == users[1]['u_id']
    assert messages['messages'][0]['message'] == 'What\'s up channel one'
    assert messages['messages'][1]['message_id'] == msg23['message_id']
    assert messages['messages'][1]['u_id'] == users[1]['u_id']
    assert messages['messages'][1]['message'] == 'You channel one or What?'
    assert messages['messages'][2]['message_id'] == msg24['message_id']
    assert messages['messages'][2]['u_id'] == users[1]['u_id']
    assert messages['messages'][2]['message'] == 'What? Yeah I am'
    assert messages['messages'][3]['message_id'] == msg22['message_id']
    assert messages['messages'][3]['u_id'] == users[1]['u_id']
    assert messages['messages'][3]['message'] == 'What\'s up channel two'
    assert messages['messages'][4]['message_id'] == msg25['message_id']
    assert messages['messages'][4]['u_id'] == users[1]['u_id']
    assert messages['messages'][4]['message'] == 'What?'

def test_search_cross_join_channel(create_users):
    """
        Test for standard functionality of search() according to spec when
        channel_join() is used and there are members in each channel which 
        are not the original channel creator.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """

    # create a channel from user 1
    channel = channels_create(users[0]['token'], 'Channel 01 User 01', True)

    # user 2 joins user 1's channel
    channel_join(users[1]['token'], channel['channel_id'])

    # send messages from both users
    msg1 = message_send(users[0]['token'], channel['channel_id'], 'What\'s up user two')
    msg2 = message_send(users[1]['token'], channel['channel_id'], 'What\'s up user one')
    msg3 = message_send(users[1]['token'], channel['channel_id'], 'You user one or What?')
    msg4 = message_send(users[0]['token'], channel['channel_id'], 'What? Yeah I am')
    msg5 = message_send(users[1]['token'], channel['channel_id'], 'What?')

    # react msg1
    message_react(users[0]['token'], 10001, 1)

    # search from first user
    messages = search(users[0]['token'], 'What')

    # make sure messages from both users are returned
    assert len(messages['messages']) == 5
    assert messages['messages'][0]['message_id'] == msg1['message_id']
    assert messages['messages'][0]['reacts'][0]['is_this_user_reacted'] is True
    assert messages['messages'][0]['u_id'] == users[0]['u_id']
    assert messages['messages'][0]['message'] == 'What\'s up user two'
    assert messages['messages'][1]['message_id'] == msg2['message_id']
    assert messages['messages'][1]['u_id'] == users[1]['u_id']
    assert messages['messages'][1]['message'] == 'What\'s up user one'
    assert messages['messages'][2]['message_id'] == msg3['message_id']
    assert messages['messages'][2]['u_id'] == users[1]['u_id']
    assert messages['messages'][2]['message'] == 'You user one or What?'
    assert messages['messages'][3]['message_id'] == msg4['message_id']
    assert messages['messages'][3]['u_id'] == users[0]['u_id']
    assert messages['messages'][3]['message'] == 'What? Yeah I am'
    assert messages['messages'][4]['message_id'] == msg5['message_id']
    assert messages['messages'][4]['u_id'] == users[1]['u_id']
    assert messages['messages'][4]['message'] == 'What?'

def test_userpermission_InputError(create_users):
    """
        Test for InputError exception thrown by admin_userpermission_change()
        when u_id does not refer to a valid user or whenpermission_id does not
        refer to a valid permission id.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """
    # u_id does not refer to a valid user
    with pytest.raises(InputError):
        admin_userpermission_change(users[0]['token'], 0, 1)

    # permission_id does not refer to a valid permission id
    with pytest.raises(InputError):
        admin_userpermission_change(users[0]['token'], users[1]['u_id'], 3)

    # permission_id does not refer to a valid permission id (wrong data type)
    with pytest.raises(InputError):
        admin_userpermission_change(users[0]['token'], users[1]['u_id'], 'str')

def test_userpermission_AccessError(create_users):
    """
        Test for AccessError exception thrown by admin_userpermission_change()
        when token passed in is not a valid token.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """

    # token is not an authorised user
    with pytest.raises(AccessError):
        admin_userpermission_change('invalid_token', users[0]['u_id'], 2)

    # token is an authorised user but not an owner
    with pytest.raises(AccessError):
        admin_userpermission_change(users[1]['token'], users[0]['u_id'], 2)

def test_userpermission_standard(create_users):
    """
        Test for standard functionality of admin_userpermission_change()
        according to spec.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture
    """

    # preliminary assertions
    assert users[0]['permission_id'] == 1
    assert users[1]['permission_id'] == 2
    assert users[2]['permission_id'] == 2

    # testing
    admin_userpermission_change(users[0]['token'], users[1]['u_id'], 1)
    assert users[1]['permission_id'] == 1

    admin_userpermission_change(users[0]['token'], users[2]['u_id'], 1)
    assert users[2]['permission_id'] == 1   
   
    admin_userpermission_change(users[1]['token'], users[2]['u_id'], 2)
    assert users[2]['permission_id'] == 2

    admin_userpermission_change(users[1]['token'], users[0]['u_id'], 2)
    assert users[0]['permission_id'] == 2
