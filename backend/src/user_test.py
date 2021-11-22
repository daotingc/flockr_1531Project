'''
    test for user/profile:
        1.valid test for profile
        2.invalid test for uid
        3.invalid test for token

    test of user/profile/setname
        1.valid test
        2.name_first is not between 1 and 50 characters inclusively in length
        3.name_last is not between 1 and 50 characters inclusively in length

    test of user/profile/setemail
        1.valid test for setemail
        2.invalid email for setemail test
        3.invalid token for setemail test

    test of user/prifile/sethandle
        1.valid test for sethandle
        2.incorrect handle length
        3.handle being

    test of invalid token
'''
import pytest
from auth import auth_login, auth_register
from error import InputError, AccessError
from other import clear
from data import users
from user import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle, user_profile_uploadphoto

@pytest.fixture
def initial_users():
    clear()
    auth_register('test1@test.com', 'password', 'first_name', 'last_name')
    auth_login('test1@test.com', 'password')
    auth_register('test2@test.com', 'password', 'user2_name', 'user2_name')
    auth_login('test2@test.com', 'password')
    auth_register('test3@test.com', 'password', 'user3_first_name', 'user3_last_name')
    auth_login('test3@test.com', 'password')

def test_user_profile(initial_users):
    '''
        valid test
        register and login user1
        test for accuracy of details of returned details
    '''
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['u_id'] == users[0]['u_id']
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['email'] == 'test1@test.com'
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['name_first'] == 'first_name'
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['name_last'] == 'last_name'
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['handle_str'] == 'first_namelast_name'

def test_profile_invalid_uid(initial_users):
    '''
        invalid uid to check
    '''
    with pytest.raises(InputError):
        user_profile(users[0]['token'], 0)

def test_profile_invalid_token(initial_users):
    '''
    test the token does not refer to a valid user
    '''
    with pytest.raises(AccessError):
        user_profile('invalid_token', users[0]['u_id'])

### TEST OF SETNAME ###


def test_valid_setname(initial_users):
    '''
        valid test
        register and login user1
        update the authorised user's first and last name
    '''
    #normal test
    user_profile_setname(users[0]['token'], 'first_name', 'last_name')
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['name_first'] == 'first_name'
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['name_last'] == 'last_name'
    # test for length 50
    long_name = '0123456789' * 5
    user_profile_setname(users[1]['token'], long_name, long_name)
    assert user_profile(users[1]['token'], users[1]['u_id'])['user']['name_first'] == long_name
    assert user_profile(users[1]['token'], users[1]['u_id'])['user']['name_last'] == long_name
    #test for length 1
    user_profile_setname(users[2]['token'], '1', '1')
    assert user_profile(users[2]['token'], users[2]['u_id'])['user']['name_first'] == '1'
    assert user_profile(users[2]['token'], users[2]['u_id'])['user']['name_last'] == '1'

def test_setname_invalid_firstname(initial_users):
    '''
        invalid test of 0 characters and 26 characters of firstname
    '''
    long_name = '0123456789' * 5 + '1'
    with pytest.raises(InputError):
        user_profile_setname(users[0]['token'], long_name, 'last_name')
    with pytest.raises(InputError):
        user_profile_setname(users[0]['token'], '', 'last_name')

def test_setname_invalid_lastname(initial_users):
    '''
        invalid test of 0 characters and 26 characters of last name
    '''
    long_name = '0123456789' * 5 + '1'
    with pytest.raises(InputError):
        user_profile_setname(users[0]['token'], 'first_name', long_name)
    with pytest.raises(InputError):
        user_profile_setname(users[0]['token'], 'first_name', '')

def test_setname_invalid_token(initial_users):
    '''
    test the token does not refer to any valid user
    '''
    with pytest.raises(AccessError):
        user_profile_setname('invalid_token', 'new_first_name', 'new_last_name')

###TEST OF SETEMAIL###

def test_profile_setemail_valid(initial_users):
    '''
        valid test for profile setemail
        register and login user
        update the email
    '''
    user_profile_setemail(users[0]['token'], 'testvalid@test.com')
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['email'] == 'testvalid@test.com'

def test_setemail_invalid_email(initial_users):
    '''
        invalid test for profile setemail
        register and login user
        give an invalid email
    '''
    with pytest.raises(InputError):
        user_profile_setemail(users[0]['token'], 'testvalidtest.com')

def test_setemail_occupied_email(initial_users):
    '''
        invalid test for the profile email being used
        register and login user
        give an used email
    '''
    with pytest.raises(InputError):
        user_profile_setemail(users[0]['token'], 'test2@test.com')

def test_setemail_invalid_token(initial_users):
    '''
    test the token does not refer to a valid user
    '''
    with pytest.raises(AccessError):
        user_profile_setemail('invalid_token', 'newemail@test.com')

###TEST OF SETHANDLE###

def test_sethandle_valid(initial_users):
    '''
        valid test for sethandle
    '''
    #test for normal case
    user_profile_sethandle(users[0]['token'], 'updatename')
    assert user_profile(users[0]['token'], users[0]['u_id'])['user']['handle_str'] == 'updatename'

    #test for length 3
    user_profile_sethandle(users[1]['token'], 'abc')
    assert user_profile(users[1]['token'], users[1]['u_id'])['user']['handle_str'] == 'abc'

    #test for length 20
    user_profile_sethandle(users[2]['token'], '01234567890123456789')
    assert user_profile(users[2]['token'], users[2]['u_id'])['user']['handle_str'] == '01234567890123456789'

def test_sethandle_invalid_length(initial_users):
    '''
        invalid test for the incorrect length:
            1. characters less than 3
            2. characters more than 20
    '''
    with pytest.raises(InputError):
        user_profile_sethandle(users[0]['token'], 'u')
    with pytest.raises(InputError):
        user_profile_sethandle(users[0]['token'], '012345678901234567890')
    with pytest.raises(InputError):
        user_profile_sethandle(users[0]['token'], '')
    with pytest.raises(InputError):
        user_profile_sethandle(users[0]['token'], '12')

def test_sethandle_being_used(initial_users):
    '''
        invalid test for the handle has being used
    '''
    temp1_handle_str = user_profile(users[0]['token'], users[0]['u_id'])['user']['handle_str']
    temp2_handle_str = user_profile(users[1]['token'], users[1]['u_id'])['user']['handle_str']
    with pytest.raises(InputError):
        user_profile_sethandle(users[0]['token'], temp2_handle_str)
    with pytest.raises(InputError):
        user_profile_sethandle(users[1]['token'], temp1_handle_str)

def test_sethandle_invalid_token(initial_users):
    '''
    test the token does not refer to a valid user
    '''
    with pytest.raises(AccessError):
        user_profile_sethandle('invalidtoken', 'newhandle')

def test_upload_photo_standart(initial_users):
    '''
    standard test without error
    it only tests no error raising
    '''
    img_url = 'https://sm.pcmag.com/t/pcmag_ap/review/a/adobe-phot/adobe-photoshop-for-ipad_tqxk.3840.jpg'
    user_profile_uploadphoto(users[0]['token'], img_url, 0, 0, 200, 200, 'localhost')

def test_upload_photo_invalid_url(initial_users):
    '''
    input error when given url is invalid
    '''
    img_url = 'https://img1.looper.com.jpg'
    with pytest.raises(InputError):
        user_profile_uploadphoto(users[0]['token'], img_url, 0, 0, 200, 200, 'localhost')

def test_upload_photo_invalid_form(initial_users):
    '''
    input error when uploading url is not in jpg form
    '''
    img_url = 'data:image/jpeg;base64,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'
    with pytest.raises(InputError):
        user_profile_uploadphoto(users[0]['token'], img_url, 0, 0, 10, 10, 'localserver')

def test_upload_photo_invalid_bounds(initial_users):
    '''
    input error when given bounds are invalid
    1. negative
    2. out of range
    '''
    img_url = 'https://sm.pcmag.com/t/pcmag_ap/review/a/adobe-phot/adobe-photoshop-for-ipad_tqxk.3840.jpg'
    # 1. negative
    with pytest.raises(InputError):
        user_profile_uploadphoto(users[0]['token'], img_url, -1, 0, 200, 200, 'localhost')
    # 2. out of range
    with pytest.raises(InputError):
        user_profile_uploadphoto(users[0]['token'], img_url, 0, 0, 999999, 20, 'locahost')

def test_upload_photo_invalid_token(initial_users):
    '''
    access error when given token is invalid
    '''
    img_url = 'https://img1.looper.com/img/gallery/things-only-adults-notice-in-shrek/intro-1573597941.jpg'
    with pytest.raises(AccessError):
        user_profile_uploadphoto('invalid', img_url, 0, 0, 200, 200, 'localhost')
