# Yicheng (Mike) Zhu
# Last updated 20/10/2020

"""
    random and string modules allow for random string generation
    for test_*_invalid_token tests

    pytest module allows us to test if exceptions are thrown at appropriate times

    channels module contains functions that need to be tested

    data module contains users and channels list structures to store data
    and helper functions for creating a new user and a new channel

    other module contains clear() which allows us to reset the data module
    before each test

    error module contains custom exceptions, including InputError
    and AccessError

"""
import pytest
from auth import auth_login, auth_register
from channels import channels_list, channels_listall, channels_create
from data import users, channels
from other import clear
from error import InputError, AccessError

##### GLOBAL VARIABLES #####
channel_01 = None
channel_02 = None
channel_03 = None
channel_04 = None
channel_05 = None
channel_06 = None

@pytest.fixture
def create_users():
    """
        Pytest fixture that registers and logs in two users for use in relevant tests.
    """

    clear()
    auth_register('validuseremail@gmail.com', 'validpass', 'User', 'One')
    auth_register('validuser2email@gmail.com', 'validpass2', 'User', 'Two')
    auth_login('validuseremail@gmail.com', 'validpass')
    auth_login('validuser2email@gmail.com', 'validpass2')

@pytest.fixture
def create_channels():
    """
        Pytest fixture that creates 6 test channels with tokens from two users.
        Returned channel_id's are stored in global variables.
    """
    global channel_01, channel_02, channel_03, channel_04, channel_05, channel_06

    channel_01 = channels_create(users[0]['token'], 'Channel 01', True)
    channel_02 = channels_create(users[0]['token'], 'Channel 02', False)
    channel_03 = channels_create(users[0]['token'], 'Channel 03', True)
    channel_04 = channels_create(users[1]['token'], 'Channel 04 User 2', True)
    channel_05 = channels_create(users[1]['token'], 'Channel 05 User 2', False)
    channel_06 = channels_create(users[1]['token'], 'Channel 06 User 2', False)

##### TEST IMPLEMENTATIONS #####
def test_list_invalid_token(create_users, create_channels):
    """
        Test for AccessError exception thrown by channels_create() when token
        passed in is not a valid token.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # empty
    with pytest.raises(AccessError):
        channels_list('')

    # None
    with pytest.raises(AccessError):
        channels_list(None)

    # Not the correct data type
    with pytest.raises(AccessError):
        channels_list(123)

    # Not an authorised user
    bad_token = 'invalid_token'

    with pytest.raises(AccessError):
        channels_list(bad_token)

def test_list_standard(create_users, create_channels):
    """
        Test for standard functionality of channels_list() according to spec.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # test length of returned channels list, making sure channels of
    # User 2 is not listed
    temp = channels_list(users[0]['token'])
    assert len(temp['channels']) == 3

    # test for accuracy of details of returned channels list
    channel_01_listed = temp['channels'][0]
    channel_02_listed = temp['channels'][1]
    channel_03_listed = temp['channels'][2]
    assert channel_01_listed['channel_id'] == channel_01['channel_id']
    assert channel_01_listed['name'] == 'Channel 01'
    assert channel_02_listed['channel_id'] == channel_02['channel_id']
    assert channel_02_listed['name'] == 'Channel 02'
    assert channel_03_listed['channel_id'] == channel_03['channel_id']
    assert channel_03_listed['name'] == 'Channel 03'

def test_listall_invalid_token(create_users, create_channels):
    """
        Test for AccessError exception thrown by channels_create() when token
        passed in is not a valid token.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # empty
    with pytest.raises(AccessError):
        channels_listall('')

    # None
    with pytest.raises(AccessError):
        channels_listall(None)

    # Not the correct data type
    with pytest.raises(AccessError):
        channels_listall(123)

    # Not an authorised user
    bad_token = 'invalid_token'

    with pytest.raises(AccessError):
        channels_listall(bad_token)

def test_listall_standard(create_users, create_channels):
    """
        Test for standard functionality of channels_listall() according to spec.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # test length of returned channels list, making sure both
    # users' channels are listed
    temp = channels_listall(users[0]['token'])
    assert len(temp['channels']) == 6

    # test for accuracy of details of returned channels list
    channel_01_listed = temp['channels'][0]
    channel_02_listed = temp['channels'][1]
    channel_03_listed = temp['channels'][2]
    channel_04_listed = temp['channels'][3]
    channel_05_listed = temp['channels'][4]
    channel_06_listed = temp['channels'][5]
    assert channel_01_listed['channel_id'] == channel_01['channel_id']
    assert channel_01_listed['name'] == 'Channel 01'
    assert channel_02_listed['channel_id'] == channel_02['channel_id']
    assert channel_02_listed['name'] == 'Channel 02'
    assert channel_03_listed['channel_id'] == channel_03['channel_id']
    assert channel_03_listed['name'] == 'Channel 03'
    assert channel_04_listed['channel_id'] == channel_04['channel_id']
    assert channel_04_listed['name'] == 'Channel 04 User 2'
    assert channel_05_listed['channel_id'] == channel_05['channel_id']
    assert channel_05_listed['name'] == 'Channel 05 User 2'
    assert channel_06_listed['channel_id'] == channel_06['channel_id']
    assert channel_06_listed['name'] == 'Channel 06 User 2'

def test_create_invalid_name(create_users, create_channels):
    """
        Test for InputError exception thrown by channels_create() when name
        is longer than 20 characters.


        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    with pytest.raises(InputError):
        channels_create(users[0]['token'], 'Channel NameThatHasMoreThanTwentyCharacters', True)

def test_create_invalid_token(create_users, create_channels):
    """
        Test for AccessError exception thrown by channels_create() when token
        passed in is not a valid token.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # empty
    with pytest.raises(AccessError):
        channels_create('', 'Channel_01', True)

    # None
    with pytest.raises(AccessError):
        channels_create(None, 'Channel_01', True)

    # Not the correct data type
    with pytest.raises(AccessError):
        channels_create(123, 'Channel_01', True)

    # Not an authorised user
    bad_token = 'invalid_token'

    with pytest.raises(AccessError):
        channels_create(bad_token, 'Channel_01', True)

def test_create_standard(create_users, create_channels):
    """
        Test for standard functionality of channels_create() according to spec.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """
    # test for accuracy of details in channels
    assert len(channels) == 6
    assert channels[0]['channel_id'] == channel_01['channel_id']
    assert channels[0]['name'] == 'Channel 01'
    assert channels[0]['public']
    assert channels[1]['channel_id'] == channel_02['channel_id']
    assert channels[1]['name'] == 'Channel 02'
    assert not channels[1]['public']
    assert channels[2]['channel_id'] == channel_03['channel_id']
    assert channels[2]['name'] == 'Channel 03'
    assert channels[2]['public']
    assert channels[3]['channel_id'] == channel_04['channel_id']
    assert channels[3]['name'] == 'Channel 04 User 2'
    assert channels[3]['public']
    assert channels[4]['channel_id'] == channel_05['channel_id']
    assert channels[4]['name'] == 'Channel 05 User 2'
    assert not channels[4]['public']
    assert channels[5]['channel_id'] == channel_06['channel_id']
    assert channels[5]['name'] == 'Channel 06 User 2'
    assert not channels[5]['public']

    # test for accuracy of details in users' channels list
    user_1_channels = users[0]['channels']
    user_2_channels = users[1]['channels']
    assert len(user_1_channels) == 3
    assert len(user_2_channels) == 3
    assert user_1_channels[0] == channel_01['channel_id']
    assert user_1_channels[1] == channel_02['channel_id']
    assert user_1_channels[2] == channel_03['channel_id']
    assert user_2_channels[0] == channel_04['channel_id']
    assert user_2_channels[1] == channel_05['channel_id']
    assert user_2_channels[2] == channel_06['channel_id']

    # check for channel ownership and membership of first user
    u_id_1 = users[0]['u_id']
    assert check_ownership(u_id_1, 0, 3)

    # check for channel ownership of second user
    u_id_2 = users[1]['u_id']
    assert check_ownership(u_id_2, 4, 6)

def test_create_duplicate(create_users, create_channels):
    """
        Test for when two channels with duplicate details are created.
        Ensure both are created as they differ by channel_id.

        :param create_users: pytest fixture to create two test users 
        :type create_users: pytest fixture

        :param create_channels: pytest fixture to create six test channels 
        :type create_channels: pytest fixture
    """

    # create test channels
    global channel_01, channel_02
    channel_01 = channels_create(users[0]['token'], 'Channel Same Name', True)
    channel_02 = channels_create(users[0]['token'], 'Channel Same Name', True)

    # test for accuracy of details in channels
    assert len(channels) == 8
    assert channels[6]['channel_id'] == channel_01['channel_id']
    assert channels[6]['name'] == 'Channel Same Name'
    assert channels[6]['public']
    assert channels[7]['channel_id'] == channel_02['channel_id']
    assert channels[7]['name'] == 'Channel Same Name'
    assert channels[7]['public']

    # check for channel ownership and membership
    u_id = users[0]['u_id']
    is_owner = False
    is_member = False
    for channel in channels:
        for owner in channel['owner_members']:
            if owner == u_id:
                is_owner = True
                break
        for member in channel['all_members']:
            if member == u_id:
                is_member = True
                break

    assert is_owner is True
    assert is_member is True

    # test for accuracy of details in users' channels list
    user_channels = users[0]['channels']
    assert len(user_channels) == 5
    assert user_channels[3] == channel_01['channel_id']
    assert user_channels[4] == channel_02['channel_id']

    # ensure the two "duplicate" channels differ by channel_id
    assert channel_01['channel_id'] != channel_02['channel_id']

def check_ownership(u_id, start, end):
    """
        Checks whether the channels created by the user (given u_id) have correct 
        ownership involving the user. The range of channels to check is denoted by 
        start and end parameters.

        :param u_id: u_id of user whose ownership of channels is to be checked 
        :type u_id: int

        :param start: start of range of channels to check 
        :type start: int

        :param end: end of range of channels to check 
        :type end: int

        :return: True if ownership is correct for all channels checked, 
        False if incorrect for any of the channels checked 
        :rtype: bool    
    """

    is_owner = False
    is_member = False
    for i in range(start, end):
        for owner in channels[i]['owner_members']:
            if owner == u_id:
                is_owner = True
                break
        for member in channels[i]['all_members']:
            if member == u_id:
                is_member = True
                break

    if is_owner and is_member:
        return True

    return False
