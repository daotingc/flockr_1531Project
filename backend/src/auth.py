'''
import data.py for data storing
import re module to check email validity
import error.py for error raising
import hashlib module for encoding password
import jwt for token encoding and decoding
import string and random for generating unique code
from helper import some helper functions
global variable SECRET is for token encoding and decoding
'''
import re
import hashlib
import string
from random import randint
import jwt
from data import users, create_user
from error import InputError, AccessError
from helper import get_user_from_email, get_user_from_token, random_str_generate
SECRET = 'grape6'

def auth_login(email, password):
    '''
    This will activate a user with given email address and password.
    It will generate a valid token for the user to remain authenticated.
    It will return a dictionary with right data if success, else raise errors.

    Args:
        param1: user's email.
        param2: password.

    Returns:
        This will return a dictionary.
        {
            'u_id' :
            'token' :
        }

    Raises:
        InputError: 1. Email entered is not a valid email.
                    2. Email entered does not belong to a user.
                    3. Password is not correct
    '''
    if is_email_valid(email) is False:
        raise InputError(description='Email is invalid.')

    # inputerror when Email entered does not belong to a user
    user = get_user_from_email(email)
    if user is None:
        raise InputError(description='Email not registered.')

    # inputerror when Password is not correct
    if user['password'] != pw_encode(password):
        raise InputError(description='Password is incorrect.')

    # update token status and get a new token
    new_token = token_generate(user['u_id'], 'login')
    user['token'] = new_token
    return {
        'u_id' : user['u_id'],
        'token' : new_token,
    }

def auth_logout(token):
    '''
    This will invalidate user with given token to log the user out.
    This will return a dictionary with success information if success,
    else raise errors.

    Args:
        param1: token

    Returns:
        This will return a dictionary.
        {
            'is_success' : (boolean)
        }

    Raises:
        AccessError: token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    # access error when given token does not refer to a exsiting user
    exist = False
    for user in users:
        if user['token'] == token:
            exist = True
    if exist is False:
        raise AccessError(description='Invalid token.')

    # return false if auth_user's status is logout
    if auth_user is None:
        return {
            'is_success' : False
        }
    # return true and update token if logout success
    auth_user['token'] = token_generate(auth_user['u_id'], 'logout')
    return {
        'is_success' : True
    }

def auth_register(email, password, name_first, name_last):
    '''
    This will create a new user in data with given information.
    This will also create a handle for user relative to user's name.
    This will return a new token for authentication in their session.

    Args:
        param1: email
        param2: password
        param3: first name
        param4: last name

    Returns:
        This will return a dictionary.
        {
            'u_id' :
            'token' :
        }

    Raises:
        InputError: 1. Email entered is not a valid email.
                    2. Email address is already being used by another user.
                    3. Password entered is less than 6 characters long.
                    4. name_first not is between 1 and 50 characters inclusively in length.
                    5. name_last is not between 1 and 50 characters inclusively in length.
    '''
    # inputerror when Email entered is not a valid email
    if is_email_valid(email) is False:
        raise InputError(description='Email is invalid.')

    # inputerror when Email address is already being used by another user
    if get_user_from_email(email) is not None:
        raise InputError(description='Email alsready in use.')

    # password length check
    if len(password) < 6:
        raise InputError(description='Password must be 6 characters or more.')
    if len(name_first) == 0 or len(name_last) == 0:
        raise InputError(description='Name cannot be empty')
    if len(name_first) > 50 or len(name_last) > 50:
        raise InputError(description='Name too long')

    # check data.py for more details of data storing
    handle = handle_initial(name_first, name_last, len(users) + 1)
    token = token_generate(len(users) + 1, 'register')
    new_user = create_user(email, pw_encode(password), name_first, name_last, handle, token)
    return {
        'u_id' : new_user['u_id'],
        'token' : new_user['token'],
    }

def auth_pwreset_req(email):
    '''
    This function is for password reset request.
    It would call a helper function to generate a unique code and
    store it in data.

    Args:
        param1(str): email of request user

    Returns:
        It would return an empty dict

    Raises:
        InputError:
            given email does not refer to a valid user
    '''
    # get user from email
    user = get_user_from_email(email)
    # InputError when there is not such a user
    # see assmuption for more details
    if user is None:
        raise InputError(description='User does not exist')
    # get unique code and store it
    code = random_str_generate(50)
    user['reset_code'] = code
    return {}

def auth_pwreset_set(reset_code, new_password):
    '''
    This function is for password reset part
    It would check the validity of reset_code
    If code is valid, it would store new_password into database.
    Otherwise, it would raise an InputError

    Args:
        param1(str): an unique code with length 50
        param2(str): new password

    Returns:
        It would return an empty dict

    Raises:
        InputError:
            1. reset_code is not a valid reset code
            2. Password entered is not a valid password
    '''
    # input check
    if reset_code == '':
        raise InputError(description='Reset code cannot be empty')
    # get user whose reset_code is equal to entered code
    found = False
    for user in users:
        if user['reset_code'] == reset_code:
            found = True
            break
    # found is false means that there is not such a user has the same reset_code
    # I.E. given reset code is invalid
    if found is False:
        raise InputError(description='Invalid reset code')
    # raise InputError when new_password is invalid
    if len(new_password) < 6:
        raise InputError(description='Invalid new password')
    # store new password
    user['password'] = pw_encode(new_password)
    user['reset_code'] = ''
    return {}

def handle_initial(name_first, name_last, u_id):
    '''
    This is a simple helper function to generate a handle(string) which combines
    user's first name and last name(all low case).
    If length of handle is more than 20, it will cut it at 20th characters.
    If generated handle is duplicate in data, it will add user's u_id to handle
    like this handle = str(u_id) + origin_handle.

    Args:
        param1: first name
        param2: last name
        param3: u_id

    Returns:
        This will return a handle (string) which contains first name and last name.

    Raises:
        This will not raise any error.
    '''
    handle = (name_first + name_last).lower()
    if len(handle) > 20:
        handle = handle[:20]
    for user in users:
        if user['handle'] == handle:
            handle = (str(u_id) + handle)[:20]
    return handle

def pw_encode(password):
    '''
    this is for password encoding by sha256 from hashlib.

    Args:
        param1: entered password

    Return:
        encoded password
    '''
    return hashlib.sha256(password.encode()).hexdigest()

def token_generate(u_id, action):
    '''
    this is a helper functino for token status updating.
    it will return a brand new token according to action.

    Args:
        param1: user's id
        param2: action 'login' / 'logout' / 'register'

    Returns:
        token should contain u_id and login status
        it will return a new encoded token by jwt
    '''
    info = {
        'u_id' : u_id,
        'has_login' : True,
    }
    if action == 'logout':
        info['has_login'] = False
    new_token = jwt.encode(info, SECRET, algorithm='HS256').decode('utf-8')
    return new_token

def is_email_valid(email):
    '''
    This is a simple helper function to test email validity.
    This will return True if email is valid, else return False

    Args:
        param1: email

    Returns:
        This will return a boolean value.
        True for valid, False for invalid.

    Raises:
        This will not raise any error.
    '''
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    return False

def get_reset_code(email):
    '''
    a helper function for get stored reset_code from database

    Args:
        param(str): target user's email

    Returns:
        It would return what is stored in database(str)
    '''
    return get_user_from_email(email)['reset_code']
