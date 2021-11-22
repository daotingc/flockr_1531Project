'''
import data.py for data storing
import error.py for error raising
from helper import some helper functions
'''
from error import InputError, AccessError
from helper import get_user_from_id, get_user_from_token, get_channel_from_id, is_user_an_owner

def channel_invite(token, channel_id, u_id):
    '''
    This will invite a user (with user id u_id) to join a channel with channel_id.
    Once invited the user is added to the channel immediately.

    Args:
        param1: invitor's token.
        param2: target channel.
        param3: invited user's u_id

    Returns:
        This will return an empty dictionary.

    Raises:
        InputError:
            1. channel_id does not refer to a valid channel.
            2. u_id does not refer to a valid user.
        AccessError:
            1. the authorised user is not already a member of the channel.
            2. given token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    invited_user = get_user_from_id(u_id)
    channel = get_channel_from_id(channel_id)

    # access error when given token does not refer to a valid user
    if auth_user is None:
        raise AccessError(description='Invalid Token')
    # input error when u_id does not refer to a valid user
    if invited_user is None:
        raise InputError(description='Invalid u_id')
    # input error when channel_id does not refer to a valid channel.
    if channel is None:
        raise InputError(description='Invalid channel_id')

    # accesss error when the authorised user is not a member of the channel
    if auth_user['u_id'] not in channel['all_members']:
        raise AccessError(description='Not a member')

    # invited_user is already in channel
    if invited_user['u_id'] in channel['all_members']:
        return {
        }

    channel['all_members'].append(u_id)
    invited_user['channels'].append(channel_id)
    return {
    }

def channel_details(token, channel_id):
    '''
    This will provide basic details about a channel whose Channel Id is channel_id.
    Also, the authorised user is part of that channel.

    Args:
        param1: authorised user's token.
        param2: target channel.

    Returns:
        This will return a dictionary with channel details.
        {
            'name': channel['name'],
            'owner_members': owner_details,
            'all_members': all_details,
        }

    Raises:
        InputError:
            1. channel_id does not refer to a valid channel.
            2. u_id does not refer to a valid user.
        AccessError:
            1. the authorised user is not already a member of the channel.
            2. given token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)

    # access error when given token does not refer to a valid user
    if auth_user is None:
        raise AccessError(description='Invalid token')
    # inputerror when Channel ID is not a valid channel
    if channel is None:
        raise InputError(description='Invalid channel_id')
    # access error when Authorised user is not a member of channel with channel_id
    if auth_user['u_id'] not in channel['all_members']:
        raise AccessError(description='Not a member')

    return {
        'name': channel['name'],
        'owner_members': list(map(member_initial, channel['owner_members'])),
        'all_members': list(map(member_initial, channel['all_members'])),
    }

def channel_messages(token, channel_id, start):
    '''
    This will return a list of messages from [start] of
    channel with channel_id. It contains up to 50 messages between
    index "start" and "start + 50". Message with index 0 is the most
    recent message in the channel. This function returns a new index "end"
    which is the value of "start + 50", or, if this function has returned
    the least recent messages in the channel, returns -1 in "end" to indicate
    there are no more messages to load after this return.

    Args:
        param1: authorised user's token.
        param2: target channel.
        param3: start index of messages

    Returns:
        This will return a dictionary.
        {
            'messages' : (a list of messages),
            'start' : (start index),
            'end' : (end index),
        }

    Raises:
        InputError:
            1. channel_id does not refer to a valid channel.
            2. start is greater than the total number of messages in the channel.
        AccessError:
            1. Authorised user is not a member of channel with channel_id.
            2. given token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    # access error when given token does not refer to a valid user
    if auth_user is None:
        raise AccessError(description='Invalid token')
    # input error when Channel ID is not a valid channel
    if channel is None:
        raise InputError(description='Invalid channel_id')

    all_msgs = list(reversed(channel['messages']))
    # input error when start is greater than the total number
    # of messages in the channel
    if start > len(all_msgs):
        raise InputError(description='Invalid start index')

    # access error when Authorised user is not a member of channel with channel_id
    if auth_user['u_id'] not in channel['all_members']:
        raise AccessError(description='Not a member')

    return_messages = []
    end = start + 50
    if end >= len(all_msgs):
        end = -1
        for msg in all_msgs[start:]:
            if auth_user['u_id'] in msg['reacts'][0]['u_ids']:
                msg['reacts'][0]['is_this_user_reacted'] = True
            else:
                msg['reacts'][0]['is_this_user_reacted'] = False
            return_messages.append(msg)
    else:
        for msg in all_msgs[start:end]:
            if auth_user['u_id'] in msg['reacts'][0]['u_ids']:
                msg['reacts'][0]['is_this_user_reacted'] = True
            else:
                msg['reacts'][0]['is_this_user_reacted'] = False
            return_messages.append(msg)
    return {
        'messages' : return_messages,
        'start' : start,
        'end' : end,
    }

def channel_leave(token, channel_id):
    '''
    This will remove authorised user from given channel.
    If the last user of that channel leaves, we will keep that channel in data.

    Args:
        param1: authorised user's token.
        param2: target channel.

    Returns:
        This will return an empty dictionary.

    Raises:
        InputError:
            Channel ID is not a valid channel
        AccessError:
            1. Authorised user is not a member of channel with channel_id
            2. given token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    # access error when the token does not refer to a valid token
    if auth_user is None:
        raise AccessError(description='Invalid token')
    # input error when Channel ID is not a valid channel
    if channel is None:
        raise InputError(description='Invalid channel_id')
    # access error when Authorised user is not a member of channel with channel_id
    if auth_user['u_id'] not in channel['all_members']:
        raise AccessError(description='Not a member')

    auth_user['channels'].remove(channel_id)
    channel['all_members'].remove(auth_user['u_id'])
    if auth_user['u_id'] in channel['owner_members']:
        channel['owner_members'].remove(auth_user['u_id'])
    return {
    }

def channel_join(token, channel_id):
    '''
    This will add authorised user to given channel. If user is the
    owner of flockr, it will set user as onwer of that channel.

    Args:
        param1: authorised user's token.
        param2: target channel.

    Returns:
        This will return an empty dictionary.

    Raises:
        InputError:
            Channel ID is not a valid channel
        AccessError:
            1. channel_id refers to a channel that is private
                (when the authorised user is not a global owner)
            2. given token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    # access error when the token does not refer to a valid token
    if auth_user is None:
        raise AccessError(description='Invalid token')
    # input error when Channel ID is not a valid channel
    if channel is None:
        raise InputError(description='Invalid channel_id')
    # access error when channel_id refers to a channel that is private
    # the authorised user is not a global owner
    if channel['public'] is False and auth_user['permission_id'] != 1:
        raise AccessError(description='Not permitted to join')

    # already in the channel
    if channel_id in auth_user['channels']:
        return {
        }

    channel['all_members'].append(auth_user['u_id'])
    auth_user['channels'].append(channel_id)
    return {
    }

def channel_addowner(token, channel_id, u_id):
    '''
    This will set the user with u_id as the owner of target channel.
    Token refers to one of the owner of target channel.
    It will return an empty dictionaty.

    Args:
        param1: authorised user's token.
        param2: target channel.
        param3: new owner's u_id

    Returns:
        This will return an empty dictionary.

    Raises:
        InputError:
            1. Channel ID is not a valid channel
            2. When user with user id u_id is already an owner of the channel
        AccessError:
            1. when the authorised user is not an owner of
                the flockr, or an owner of this channel
            2. given token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    invited_user = get_user_from_id(u_id)
    # access error when the token does not refer to a valid token
    if auth_user is None:
        raise AccessError(description='Invalid token')

    # input error when Channel ID is not a valid channel
    if channel is None:
        raise InputError(description='Invalid channel_id')

    # input error when u_id does not refer to a valid user
    if invited_user is None:
        raise InputError(description='Invalid u_id')

    # input error when When user with user id u_id
    # is already an owner of the channel
    if invited_user['u_id'] in channel['owner_members']:
        raise InputError(description='Already an owner')

    # access error when the authorised user is not
    # an owner of the flockr, or an owner of this channel
    if is_user_an_owner(token, channel_id) is False:
        raise AccessError(description='Not permitted to add')

    channel['owner_members'].append(u_id)
    return {
    }

def channel_removeowner(token, channel_id, u_id):
    '''
    This will remove the user with u_id from the owners of target channel.
    If u_id refers to the owner of flockr, it will ignore the request.
    Token refers to one of the owner of target channel.
    It will return an empty dictionaty.

    Args:
        param1: authorised user's token.
        param2: target channel.
        param3: the user's u_id who is removed from owners

    Returns:
        This will return an empty dictionary.

    Raises:
        InputError:
            1. Channel ID is not a valid channel
            2. When user with user id u_id is not an owner of the channel
        AccessError:
            1. when the authorised user is not an owner of
                the flockr, or an owner of this channel
            2. given token does not refer to a valid token
    '''
    auth_user = get_user_from_token(token)
    channel = get_channel_from_id(channel_id)
    removed_user = get_user_from_id(u_id)
    # access error when given token does not refer to a valid user
    if auth_user is None:
        raise AccessError(description='Invalid token')
    # input error when Channel ID is not a valid channel
    if channel is None:
        raise InputError(description='Invalid channel_id')
    # input error when u_id does not refer to a valid user
    if removed_user is None:
        raise InputError(description='Invalid u_id')
    # input error when user with user id u_id is not an owner of the channel
    if removed_user['u_id'] not in channel['owner_members']:
        raise InputError(description='Not a owner of channel')

    # accesss error when the authorised user is not
    # an owner of the flockr, or an owner of this channel
    if is_user_an_owner(token, channel_id) is False:
        raise AccessError(description='Not permitted to remove')
    channel['owner_members'].remove(u_id)
    return {
    }

########## help functions ##########

def member_initial(u_id):
    '''
    This is a simple helper function.
    It will return a member type data with given u_id if it exists in data,
    else return False

    Args:
        param1: u_id

    Returns:
        This will return member(dictionary) if u_id refers to a valid user in data,
        else return False.

    Raises:
        this will not raise any error
    '''
    user = get_user_from_id(u_id)
    return {
        'u_id' : user['u_id'],
        'name_first' : user['name_first'],
        'name_last' : user['name_last'],
        'profile_img_url' : user['profile_img_url'],
    }
