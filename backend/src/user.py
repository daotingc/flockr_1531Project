'''
import users to access data
import AccessError and InputError for error raising
import re module for email checking
import urllib for downloading image
import Image from PIL for cropping photo
'''
from error import AccessError, InputError
from data import users
from helper import get_user_from_token, get_user_from_id, random_str_generate
from auth import is_email_valid
import urllib
from PIL import Image
import requests
import ssl

def user_profile(token, u_id):
    '''
    This function is for showing user's profile.
    It will return the information of user's file.

    Args:
        param1: authorised user's token
        param2: authorised user's u_id

    Returns:
        a dictionary containing profile
        {
            'user': {
                'u_id': 1,
                'email': 'cs1531@cse.unsw.edu.au',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'hjacobs',
                'profile_img_url' : img_url,
            },
        }

    Raises:
        InputError: User with u_id is not a valid user
        AccessError: given token does not refer to a valid user
    '''
    request_user = get_user_from_token(token)
    target_user = get_user_from_id(u_id)
    # raise AccessError when given token does not refer to a valid user
    if request_user is None:
        raise AccessError(description='Invalid token')

    # raise InputError when given u_id is not correct
    if target_user is None:
        raise InputError(description='Invalid u_id')

    return {
        'user' : {
            'u_id' : target_user['u_id'],
            'email' : target_user['email'],
            'name_first' : target_user['name_first'],
            'name_last' : target_user['name_last'],
            'handle_str' : target_user['handle'],
            'profile_img_url' : target_user['profile_img_url'],
        },
    }

def user_profile_setname(token, name_first, name_last):
    '''
    This function is for updating the authorised user's first and last name.

    Args:
        param1: authorised user's token
        param2: new first name
        param3: new last name

    Returns:
        it will return an empty dictionary

    Raises:
        InputError:
            1. name_first is not between 1 and 50 characters inclusively in length
            2. name_last is not between 1 and 50 characters inclusively in length
        AccessError: given token does not refer to a valid user
    '''
    request_user = get_user_from_token(token)
    # raise AccessError when given token does not refer to a valid user
    if request_user is None:
        raise AccessError(description='Invalid token')

    if len(name_first) == 0 or len(name_last) == 0:
        raise InputError(description='Name cannot be empty')
    if len(name_first) > 50 or len(name_last) > 50:
        raise InputError(description='Name too long')

    request_user['name_first'] = name_first
    request_user['name_last'] = name_last
    return {
    }

def user_profile_setemail(token, email):
    '''
    This function is for updating the authorised user's email.

    Args:
        param1: authorised user's token
        param2: new email

    Returns:
        it will return an empty dictionary

    Raises:
        InputError:
            1. Email entered is not a valid email
            2. Email address is already being used by another user
        AccessError: given token does not refer to a valid user
    '''
    request_user = get_user_from_token(token)
    # raise AccessError when given token does not refer to a valid user
    if request_user is None:
        raise AccessError(description='Invalid token')

    # raise InputError when new email is invalid
    if is_email_valid(email) is False:
        raise InputError(description='Invalid email')

    # raise InputError when new email has been occupied
    for user in users:
        if user['email'] == email:
            raise InputError(description='Email already in use')

    request_user['email'] = email
    return {
    }

def user_profile_sethandle(token, handle_str):
    '''
    This function is for updating the authorised user's handle.

    Args:
        param1: authorised user's token
        param2: new handle

    Returns:
        it will return an empty dictionary

    Raises:
        InputError:
            1. handle_str in not between 3 and 20 characters inclusive
            2. handle is already used by another user
        AccessError: given token does not refer to a valid user
    '''
    request_user = get_user_from_token(token)
    # raise AccessError when given token does not refer to a valid user
    if request_user is None:
        raise AccessError(description='Invalid token')

    # raise InputError if the length of handle is not valid
    if len(handle_str) > 20 or len(handle_str) < 3:
        raise InputError(description='Invalid length of handle')

    # raise InputError if new handle has been occupied by someone
    for user in users:
        if user['handle'] == handle_str:
            raise InputError(description='Handle already in use')

    request_user['handle'] = handle_str
    return {
    }

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end, server_url):
    '''
    Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.

    Args:
        param1(str): authorised user
        param2(str): photo path
        param3-6(int): bounds of photo
        param6(str): server url

    Returns:
        It will return am empty dict

    Args:
        InputError:
            1. img_url returns an HTTP status other than 200.
            2. any of x_start, y_start, x_end, y_end are not
                within the dimensions of the image at the URL.
            3. Image uploaded is not a JPG
        AccessError:
            given token does not refer to a valid user
    '''
    ssl._create_default_https_context = ssl._create_unverified_context
    auth_user = get_user_from_token(token)
    # access error when given token is invalid
    if auth_user is None:
        raise AccessError(description='Invalid token')
    file_path = './src/static/'
    file_name = str(auth_user['u_id']) + '.jpg'
    # input error when given img is not in jpg form
    if img_url[-4:] != '.jpg':
        raise InputError(description='Invalid form')
    # input error when given url is invalid
    try:
        urllib.request.urlretrieve(img_url, file_path + file_name)
    except:
        raise InputError(description='Invalid url')
    img_object = Image.open(file_path + file_name)
    # input error when given bounds are invalid
    width, height = img_object.size
    if x_start > width or x_end > width or y_start > height or y_end > height:
        raise InputError(description='Invalid bounds')
    if x_start < 0 or x_end < 0 or y_start < 0 or y_end < 0:
        raise InputError(description='Invalid bounds')
    # do crop
    cropped = img_object.crop((x_start, y_start, x_end, y_end))
    cropped.save(file_path + file_name)
    # do store url
    auth_user['profile_img_url'] = server_url + '/static/' + file_name
    return {}
