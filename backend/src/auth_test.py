''' Tests:
        register:
            1. email validity
            2. email already used
            2. password validity
            3. name_first validity
            4. name_last validity
        login:
            1. email exists in data
            2. password incorrect
        logout:
            1. correct return
        data:
            1. elements correct
            2. user id in ascending order
            3. handle < 20 characters
            4. bighandle < 20 character
'''

import pytest
import auth
from other import clear
from error import InputError, AccessError
from data import users


def test_register_email():
    '''register success with valid email'''
    # invalid email
    clear()
    with pytest.raises(InputError):
        auth.auth_register('invalidemail.com', 'valid123', 'valid', 'valid')

    clear()
    with pytest.raises(InputError):
        auth.auth_register('invalidemail', 'valid123', 'valid', 'valid')

    clear()
    with pytest.raises(InputError):
        auth.auth_register('invalidemail@com', 'valid123', 'valid', 'valid')

    clear()
    with pytest.raises(InputError):
        auth.auth_register('invalidemail@.com', 'valid123', 'valid', 'valid')
    # already used email
    clear()
    auth.auth_register('validemail@gmail.com', 'valid123', 'valid', 'valid')
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', 'valid123', 'valid', 'valid')

def test_register_password():
    '''register success with valid password'''
    # password under 6 characters
    clear()
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', 'inval', 'valid', 'valid')
    # no password
    clear()
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', '', 'valid', 'valid')
    # valid password
    clear()
    auth.auth_register('validemail@gmail.com', 'valid123', 'valid', 'valid')
    auth.auth_login('validemail@gmail.com', 'valid123')

def test_register_namefirst():
    '''register success with valid firstname'''
    # no first name
    clear()
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', 'valid123', '', 'valid')
    # first name more than 50 characters
    clear()
    long_name = 'a' * 51
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', 'valid123', long_name, 'valid')

def test_register_namelast():
    '''register success with valid lastname'''
    # no last name
    clear()
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', 'valid123', 'valid', '')
    # last name more than 50 characters
    clear()
    long_name = 'a' * 51
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', 'valid123', 'valid', long_name)

def test_login_invalid_email():
    '''login failure with invalid email'''
    # login with non-existing user
    clear()
    auth.auth_register('validemail@gmail.com', 'valid123', 'valid', 'valid')
    with pytest.raises(InputError):
        auth.auth_login('diffemail@gmail.com', 'valid123')
    with pytest.raises(InputError):
        auth.auth_login('diffgmail.com', 'valid123')

    # login with existing user
    auth.auth_login('validemail@gmail.com', 'valid123')

def test_login_invalid_password():
    '''login failure with invalid password'''
    # incorrect password
    clear()
    auth.auth_register('validemail@gmail.com', 'valid123', 'valid', 'valid')
    with pytest.raises(InputError):
        auth.auth_login('validemail@gmail.com', 'diffpass')

def test_logout_success():
    '''logout if user logged in'''
    # logout user that's logged in
    clear()
    auth.auth_register('validemail@gmail.com', 'valid123', 'valid', 'valid')['token']
    login_token = auth.auth_login('validemail@gmail.com', 'valid123')['token']
    temp = auth.auth_logout(login_token)
    assert temp['is_success'] is True

    # logout with a logged out user
    temp = auth.auth_logout(auth.token_generate(1, 'logout'))
    assert temp['is_success'] is False

    #logout bad token
    clear()
    auth.auth_register('validemail@gmail.com', 'valid123', 'valid', 'valid')
    with pytest.raises(AccessError):
        auth.auth_logout('nonexistingtoken')

def test_data_changes():
    '''ensure data stored correctly'''
    # elements stored correctly
    clear()
    auth.auth_register('philsmart@gmail.com', 'bigboys111', 'Phil', 'Smart')

    assert users[0]['u_id'] == 1
    assert users[0]['email'] == 'philsmart@gmail.com'
    assert users[0]['password'] == auth.pw_encode('bigboys111')
    assert users[0]['name_first'] == 'Phil'
    assert users[0]['name_last'] == 'Smart'
    assert users[0]['channels'] == []
    assert users[0]['handle'] == 'philsmart'

    auth.auth_register('darryngarryn@gmail.com', 'niceice123', 'Darryn', 'Garryn')

    assert users[1]['u_id'] == 2
    assert users[1]['email'] == 'darryngarryn@gmail.com'
    assert users[1]['password'] == auth.pw_encode('niceice123')
    assert users[1]['name_first'] == 'Darryn'
    assert users[1]['name_last'] == 'Garryn'
    assert users[1]['channels'] == []
    assert users[1]['handle'] == 'darryngarryn'

    # u_id created in ascending order
    auth.auth_register('userid3@gmail.com', 'valid123', 'valid', 'valid')
    auth.auth_register('userid4@gmail.com', 'valid123', 'valid', 'valid')
    auth.auth_register('userid5@gmail.com', 'valid123', 'valid', 'valid')
    auth.auth_register('userid6@gmail.com', 'valid123', 'valid', 'valid')

    assert users[2]['u_id'] == 3
    assert users[3]['u_id'] == 4
    assert users[4]['u_id'] == 5
    assert users[5]['u_id'] == 6

    # handle cut off above 20 characters

    auth.auth_register('bighandle@gmail.com', 'valid123', 'Yothisisgonna', 'Bemassive')

    assert users[6]['handle'] == 'yothisisgonnabemassi'

    # duplicate handles
    auth.auth_register('twohandles@gmail.com', 'valid123', 'Name', 'Name')
    auth.auth_register('twohandles1@gmail.com', 'valid123', 'Name', 'Name')

    assert users[7]['handle'] == 'namename'
    assert users[8]['handle'] == '9namename'

    # duplicate with big handle

    auth.auth_register('bighandle2@gmail.com', 'valid123', 'Yothisisgonna', 'Bemassive')

    assert users[9]['handle'] == '10yothisisgonnabemas'

##############################
######## iter 3 part #########
##############################

def test_pwreset_req_standard():
    '''
    standard test (no error)
    create a user and the user requests to reset password
    '''
    clear()
    auth.auth_register('test@test.com', 'password', 'first_name', 'last_name')
    assert users[0]['password'] == auth.pw_encode('password')
    auth.auth_pwreset_req('test@test.com')
    code = auth.get_reset_code('test@test.com')
    assert code is not None
    assert users[0]['reset_code'] == code

def test_pwreset_req_invalid_email():
    '''
    input error when given email does not refer to a user(see assumption)
    '''
    clear()
    auth.auth_register('test@test.com', 'password', 'first_name', 'last_name')
    assert users[0]['password'] == auth.pw_encode('password')
    with pytest.raises(InputError):
        auth.auth_pwreset_req('notest@test.com')

def test_pwreset_set_standard():
    '''
    standard test (no error)
    create a user and the user resets his password
    logout and login with new password
    '''
    clear()
    auth.auth_register('test@test.com', 'password', 'first_name', 'last_name')
    assert users[0]['password'] == auth.pw_encode('password')
    auth.auth_pwreset_req('test@test.com')
    code = auth.get_reset_code('test@test.com')
    auth.auth_pwreset_set(code, 'newpassword')
    assert users[0]['password'] != auth.pw_encode('password')
    assert users[0]['password'] == auth.pw_encode('newpassword')
    auth.auth_logout(users[0]['token'])
    auth.auth_login('test@test.com', 'newpassword')

def test_pwreset_set_wrong_code():
    '''
    input error when entered code is not correct
    create a user and use wrong code for reset
    1. non-existing code
    2. empty string
    3. used code
    '''
    clear()
    auth.auth_register('test@test.com', 'password', 'first_name', 'last_name')
    assert users[0]['password'] == auth.pw_encode('password')
    auth.auth_pwreset_req('test@test.com')
    # non-existing code and empty string
    with pytest.raises(InputError):
        auth.auth_pwreset_set('wrong_code', 'newpassword')
    with pytest.raises(InputError):
        auth.auth_pwreset_set('', 'newpassword')
    # check database
    assert users[0]['password'] == auth.pw_encode('password')
    # 3. reset code
    code = auth.get_reset_code('test@test.com')
    auth.auth_pwreset_set(code, 'newpassword')
    assert users[0]['password'] != auth.pw_encode('password')
    assert users[0]['password'] == auth.pw_encode('newpassword')
    # 3. use used code to reset again
    with pytest.raises(InputError):
        auth.auth_pwreset_set(code, 'pppppp')
    assert users[0]['password'] == auth.pw_encode('newpassword')

def test_pwreset_set_invalid_newpw():
    '''
    input error when entered code is not correct
    create a user and use invalid new password for reset
    '''
    clear()
    auth.auth_register('test@test.com', 'password', 'first_name', 'last_name')
    assert users[0]['password'] == auth.pw_encode('password')
    auth.auth_pwreset_req('test@test.com')
    code = auth.get_reset_code('test@test.com')
    with pytest.raises(InputError):
        auth.auth_pwreset_set(code, 'newpa')
        auth.auth_pwreset_set(code, '')
