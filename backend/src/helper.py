import jwt
import string
from random import randint
from data import users, channels

SECRET = 'grape6'

def get_user_from_email(email):
    '''
    This is a simple helper function to test email duplication.
    This will return corresponding user data if email is duplicate, else return None

    Args:
        param1: email

    Returns:
        This will return user(a dictionary) if the email belongs to an
        exsiting user, else return None.
    '''
    for user in users:
        if user['email'] == email:
            return user
    return None

def get_user_from_id(u_id):
    '''
    This is a simple helper function.
    It will return a user with given u_id if it exists in data,
    else return False

    Args:
        param1: u_id

    Returns:
        This will return uesr(dictionary) if u_id refers to a valid user in data,
        else return False.
    '''
    for user in users:
        if user['u_id'] == u_id:
            return user
    return None

def get_user_from_token(token):
    '''
    This is a simple helper function.
    It will return a user with given token can be decoded and is a login user,
    else return none

    Args:
        param1: u_id

    Returns:
        This will return uesr(dictionary) if token can be decoded and user has login,
        else return False.

    Raises:
        this will not raise any error
    '''
    try:
        info = jwt.decode(token.encode('utf-8'), SECRET, algorithms=['HS256'])
        if info['has_login'] is False:
            return None
        return get_user_from_id(info['u_id'])
    except:
        return None

def get_channel_from_id(channel_id):
    '''
    This is a simple helper function.
    It will return a channel with given channel_id if it exists in data,
    else return None

    Args:
        param1: channel_id

    Returns:
        This will return channel(dictionary) if token refers to a valid chanenl in data,
        else return False.
    '''
    for channel in channels:
        if channel['channel_id'] == channel_id:
            return channel
    return None

def is_user_an_owner(token, channel_id):
    '''
    this is a helper function to check ownership.

    Args:
        param1: authorised user's token
        param2: target channel

    Returns:
        it will return True if user is the owner of channel or flockr,
        else return False
    '''
    user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    if user['permission_id'] == 1:
        return True
    if user['u_id'] in channel['owner_members']:
        return True
    return False

def random_str_generate(length):
    '''
    a helper function for generation a unique code
    the unique code is a combination of uppercase and number with given length
    see assumption for more details

    Args:
        It does not have arguments

    Returns:
        It would return a unique code(str)
    '''
    chars = string.ascii_uppercase + '0123456789'
    code = ''
    while len(code) < length:
        selection = randint(0, len(chars) - 1)
        code += chars[selection]
    return code
