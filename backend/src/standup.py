'''
import time module to get current time
import threading to start standup_end function
import error for error raising
import helper for getting data
'''
import time
import threading
from data import create_new_msg
from error import InputError, AccessError
from helper import get_user_from_token, get_channel_from_id

def standup_start(token, channel_id, length):
    '''
    This function would start a standup in given channel.
    Standup would last X second and X is equal to length.
    After time is up, what is send during standup would be buffered in one message
    and be sent to given channel.
    It would return the finish_time.

    Args:
        param1(str): request user's token
        param2(int): the id of target channel
        param3(int): the time would standup last (in second)

    Returns:
        It would return a dict with one tuple 'time_finish' and its value
        is an integer (unix timestamp)

    Raises:
        InputError:
            1. Channel ID is not a valid channel
            2. An active standup is currently running in this channel
        AccessError:
            given token is invalid
    '''
    user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    # access error when given token is invalid
    if user is None:
        raise AccessError(description='Invalid token')
    # input error when given channel_id is invalid
    if channel is None:
        raise InputError(description='Invalid channel_id')
    # input error when an active standup is currently runing in this channel
    if standup_active(token, channel_id)['is_active'] is True:
        raise InputError(description='Standup has started')

    # reset data for standup
    channel['time_standupend'] = int(time.time()) + length
    channel['standup_msg'] = ''
    # set standup_end
    timer = threading.Timer(length, standup_end, args=[user, channel])
    timer.start()
    return {
        'time_finish' : int(time.time()) + length
    }

def standup_active(token, channel_id):
    '''
    This funciton is for getting standup active infomation.
    For a given channel, return whether a standup is active in it,
    and what time the standup finishes.
    If no standup is active, then time_finish returns None.

    Args:
        param1(str): request user's token
        param2(int): the id of target channel

    Returns:
        It would return a dict containing relative info
        'is_active' (boolean) true if standup is active, else false
        'time_finish' (int unix timestamp) the time when the standup is finished

    Raises:
        InputError:
            1. Channel ID is not a valid channel
        AccessError:
            1. given token is invalid
    '''
    user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    # access error when given token is invalid
    if user is None:
        raise AccessError(description='Invalid token')
    # input error when given channel_id is invalid
    if channel is None:
        raise InputError(description='Invalid channel_id')

    if channel['time_standupend'] == 0:
        return {
            'is_active' : False,
            'time_finish' : None,
        }
    return {
        'is_active' : True,
        'time_finish' : channel['time_standupend'],
    }

def standup_send(token, channel_id, message):
    '''
    This function is for sending a message to get buffered
    in the standup queue, assuming a standup is currently active.

    Args:
        param1(str): request user's token
        param2(int): the id of target channel
        param3(str): sent message

    Returns:
        It would return an empty dict

    Raises:
        InputError:
            1. Channel ID is not a valid channel
            2. Message is more than 1000 characters
            3. An active standup is not currently running in this channel
        AccessError:
            1. given token is invalid
            2. The authorised user is not a member of the channel that the message is within
    '''
    user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    # access error when given token is invalid
    if user is None:
        raise AccessError(description='Invalid token')

    # input error when given channel_id is invalid
    if channel is None:
        raise InputError(description='Invalid channel_id')

    # input error when An active standup is not currently running in this channel
    if standup_active(token, channel_id)['is_active'] is False:
        raise InputError(description='No active standup')

    # input error when msg is too long
    if len(message) > 1000:
        raise InputError(description='Message is too long')

    # access error when The authorised user is not a member of
    # the channel that the message is within
    if channel_id not in user['channels']:
        raise AccessError(description='Not a member')

    channel['standup_msg'] += '\n' + user['handle'] + ': ' + message
    return {}

def standup_end(user, channel):
    '''
    This function is for endding standup.
    It would be executed after standup is finished.
    It would set channel['time_standupend] as 0 and send a msg to channel.
    If there is no msg, it would ignore it.

    Args:
        param1(dict): user who starts the standup
        param2(dict): channel at which standup is active

    Returns:
        no return
    '''
    channel['time_standupend'] = 0
    if len(channel['standup_msg']) != 0:
        new_msg = create_new_msg(channel['standup_msg'], channel, user['u_id'])
        channel['latest_msg_id'] += 1
        channel['messages'].append(new_msg)
