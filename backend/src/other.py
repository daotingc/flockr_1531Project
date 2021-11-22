# Yicheng (Mike) Zhu
# Last updated 22/10/2020

"""
    random and string modules allow for random string generation
    for invalid token tests

    data module contains users and channels list structures to store associated
    data

    auth module allows us to use auth_register() and auth_login() to register
    and log in test users
"""

from data import users, channels
from error import InputError, AccessError
from helper import get_user_from_token, get_user_from_id, get_channel_from_id

def clear():
    """
        Resets internal data of Flockr by removing all elements of "users" and 
        "channels" lists in data module.
    """
    users.clear()
    channels.clear()
    return {
    }

def users_all(token):
    """
        Returns a list of all users and their associated details.

        :param token: The token of any authorised user 
        :type token: str

        :return: A dictionary containing a list of all users and 
        their associated details 
        :rtype: dict with nested list
    """

    # check token validity
    if get_user_from_token(token) is None:
        raise AccessError(description="Unauthorised access")

    all_users = []
    for user in users:
        user_details = {}
        user_details['u_id'] = user['u_id']
        user_details['email'] = user['email']
        user_details['name_first'] = user['name_first']
        user_details['name_last'] = user['name_last']
        user_details['handle_str'] = user['handle']
        user_details['profile_img_url'] = user['profile_img_url']
        all_users.append(user_details)

    return {
        'users': all_users,
    }

def admin_userpermission_change(token, u_id, permission_id):
    """
        Given a user by their user ID, set their permissions to new permissions
        described by permission_id.

        :param token: The token of any Flockr owner
        :type token: str

        :param u_id: The user ID of the user whose permissions we want to change
        :type u_id: int

        :param permission_id: The ID of the new permission to be set on the user
        (1 for owner, 2 for member)
        :type permission_id: int
    """
    # check u_id validity
    user = get_user_from_id(u_id)
    if user is None:
        raise InputError(description=f"Cannot find user with ID of {u_id}")

    # check permission_id validity
    if permission_id not in [1, 2]:
        raise InputError(description="Invalid permission code")

    # check token validity
    if get_user_from_token(token) is None:
        raise AccessError(description="Unauthorised access")

    # check if token refers to an owner
    admin = get_user_from_token(token)
    if admin['permission_id'] != 1:
        raise AccessError(description="Members cannot modify permissions")

    # change permission of u_id user to permission_id
    user['permission_id'] = permission_id

    return {
    }

def search(token, query_str):
    """
        Given a query string, return a collection of messages in all of the 
        channels that the user has joined that match that query.

        :param token: The token of an authorised Flockr user
        :type token: str

        :param u_id: The user ID of the user whose permissions we want to change
        :type u_id: int

        :return: A dictionary with nested list of messages containing
        the query string
        :rtype: dict with nested list
    """

    # check token validity
    if get_user_from_token(token) is None:
        raise AccessError(description="Unauthorised access")

    result = []
    user = get_user_from_token(token)

    # search for messages with query string
    for channel_id in user['channels']:
        channel = get_channel_from_id(channel_id)
        for message in channel['messages']:
            if query_str in message['message']:
                if user['u_id'] in message['reacts'][0]['u_ids']:
                    message['reacts'][0]['is_this_user_reacted'] = True
                else:
                    message['reacts'][0]['is_this_user_reacted'] = False
                result.append(message)

    return {
        'messages': result
    }
