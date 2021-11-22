# Yicheng (Mike) Zhu
# Last updated 20/10/2020

"""
    data module contains users and channels list structures to store data
    and helper functions for creating a new user and a new channel

    error module contains custom exceptions, including InputError
    and AccessError
"""
from data import users, channels, create_new_channel
from error import InputError, AccessError
from helper import get_user_from_token, get_channel_from_id

#### INTERFACE FUNCTION IMPLEMENTATIONS ####
def channels_list(token):
    """
        Provides a list of all channels (and their associated details) that the 
        authorised user is a part of.

        :param token: The token of the user in question 
        :type token: str

        :return: A dictionary containing a list of channels that the user is a part of
        and their associated details. 
        :rtype: dict with nested list
    """
    # check token validity
    auth_user = get_user_from_token(token)
    if auth_user is None:
        raise AccessError(description="Unauthorised access")
    # get list of channel_id
    user_channels = auth_user['channels']
    return {
        'channels': list(map(channel_detail, user_channels)),
    }

def channels_listall(token):
    """
        Provides a list of all channels (and their associated details).

        :param token: The token of any authorised user 
        :type token: str

        :return: A dictionary containing a list of all channels and their associated
        details (name & channel_id) 
        :rtype: dict with nested list
    """

    # check token validity
    auth_user = get_user_from_token(token)
    if auth_user is None:
        raise AccessError(description="Unauthorised access")
    # get list of channel_id
    all_channels = []
    for channel in channels:
        all_channels.append(channel['channel_id'])
    return {
        'channels': list(map(channel_detail, all_channels)),
    }

def channels_create(token, name, is_public):
    """
        Creates a new channel with that name that is either a public or private 
        channel.

        :param token: The token of any authorised user 
        :type token: string

        :param name: The name of the new channel 
        :type name: string

        :param is_public: Boolean value indicating whether the new channel is public 
        :type is_public: boolean

        :return: A dictionary containing the new channel's channel_id (int) 
        :rtype: dict with int key value

    """

    user = get_user_from_token(token)
    # check name validity
    if len(name) > 20:
        raise InputError(description="Name cannot be longer than 20 characters")

    # check token validity
    if user is None:
        raise AccessError(description="Unauthorised access")

    # create new channel in data.py
    new_channel = create_new_channel(len(channels) + 1, is_public, name, user['u_id'])

    # add new channel_id to user's channels list
    user['channels'].append(new_channel['channel_id'])

    # return channel_id
    return {
        'channel_id': new_channel['channel_id'],
    }

def channel_detail(channel_id):
    """
        A helper function to get a channel's details from its id.

        :param channel_id: channel_id of channel whose details we want 
        :type token: int

        :return: A dictionary containing the new channel's details (id & name) as
        key value pairs 
        :rtype: dict

    """
    channel = get_channel_from_id(channel_id)
    return {
        'channel_id' : channel['channel_id'],
        'name' : channel['name'],
    }
