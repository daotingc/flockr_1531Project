import sys
from auth import auth_login, auth_logout, auth_register, auth_pwreset_req, auth_pwreset_set, get_reset_code
from channel import channel_invite, channel_details, channel_messages, channel_leave
from channel import channel_join, channel_addowner, channel_removeowner
from channels import channels_create, channels_list, channels_listall
from message import message_send, message_remove, message_edit, message_send_later
from message import message_pin, message_unpin, message_react, message_unreact
from user import user_profile, user_profile_setemail, user_profile_sethandle, user_profile_setname, user_profile_uploadphoto
from other import clear, users_all, search, admin_userpermission_change
from standup import standup_start, standup_active, standup_send
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from error import InputError
from flask_mail import Mail, Message

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

########################################
############## auth.py #################
########################################
@APP.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    return dumps(auth_login(email, password))

@APP.route('/auth/logout', methods=['POST'])
def logout():
    token = request.get_json()['token']
    return dumps(auth_logout(token))

@APP.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    name_first = data['name_first']
    name_last = data['name_last']
    return dumps(auth_register(email, password, name_first, name_last))

@APP.route('/auth/passwordreset/request', methods=['POST'])
def pwreset_req():
    email = request.get_json()['email']
    auth_pwreset_req(email)
    send_code_email(email)
    return dumps({})

def send_code_email(email):
    mail= Mail(APP)
    APP.config['MAIL_SERVER']='smtp.gmail.com'
    APP.config['MAIL_PORT'] = 465
    APP.config['MAIL_USERNAME'] = 'cs1531wed17grape6bot@gmail.com'
    APP.config['MAIL_PASSWORD'] = 'wed17grape'
    APP.config['MAIL_USE_TLS'] = False
    APP.config['MAIL_USE_SSL'] = True
    mail = Mail(APP)
    msg = Message('Your UNSW Flockr password reset code',
                sender = 'cs1531wed17grape6bot@gmail.com',
                recipients = [email])
    msg.body = get_reset_code(email)
    mail.send(msg)
    return

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def pwreset_reset():
    data = request.get_json()
    return dumps(auth_pwreset_set(data['reset_code'], data['new_password']))

########################################
############# channel.py ###############
########################################
@APP.route('/channel/invite', methods=['POST'])
def invite():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    return dumps(channel_invite(token, channel_id, u_id))

@APP.route('/channel/details', methods=['GET'])
def get_details():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details(token, channel_id))

@APP.route('/channel/messages', methods=['GET'])
def recent_messages():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel_messages(token, channel_id, start))

@APP.route('/channel/leave', methods=['POST'])
def leave_channel():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    return dumps(channel_leave(token, channel_id))

@APP.route('/channel/join', methods=['POST'])
def join_channel():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    return dumps(channel_join(token, channel_id))

@APP.route('/channel/addowner', methods=['POST'])
def addowner():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    return dumps(channel_addowner(token, channel_id, u_id))

@APP.route('/channel/removeowner', methods=['POST'])
def removeowner():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    return dumps(channel_removeowner(token, channel_id, u_id))

########################################
############ channels.py ###############
########################################
@APP.route('/channels/create', methods=['POST'])
def create_channel():
    data = request.get_json()
    token = data['token']
    name = data['name']
    is_public = bool(data['is_public'])
    return dumps(channels_create(token, name, is_public))

@APP.route('/channels/list', methods=['GET'])
def list_joined_channels():
    token = request.args.get('token')
    return dumps(channels_list(token))

@APP.route('/channels/listall', methods=['GET'])
def list_all_channels():
    token = request.args.get('token')
    return dumps(channels_listall(token))

########################################
############# message.py ###############
########################################
@APP.route('/message/send', methods=['POST'])
def send_message():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    msg = data['message']
    return dumps(message_send(token, channel_id, msg))

@APP.route('/message/remove', methods=['DELETE'])
def delete_message():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    return dumps(message_remove(token, message_id))

@APP.route('/message/edit', methods=['PUT'])
def edit_message():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    message = data['message']
    return dumps(message_edit(token, message_id, message))

@APP.route('/message/sendlater', methods=['POST'])
def send_message_late():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    message = data['message']
    time_sent = int(data['time_sent'])
    return dumps(message_send_later(token, channel_id, message, time_sent))

@APP.route('/message/react', methods=['POST'])
def react_to_msg():
    data = request.get_json()
    token = data['token']
    msg_id = int(data['message_id'])
    react_id = int(data['react_id'])
    return dumps(message_react(token, msg_id, react_id))

@APP.route('/message/unreact', methods=['POST'])
def unreact_to_msg():
    data = request.get_json()
    token = data['token']
    msg_id = int(data['message_id'])
    react_id = int(data['react_id'])
    return dumps(message_unreact(token, msg_id, react_id))

@APP.route('/message/pin', methods=['POST'])
def pin_msg():
    data = request.get_json()
    token = data['token']
    msg_id = int(data['message_id'])
    return dumps(message_pin(token, msg_id))

@APP.route('/message/unpin', methods=['POST'])
def unpin_msg():
    data = request.get_json()
    token = data['token']
    msg_id = int(data['message_id'])
    return dumps(message_unpin(token, msg_id))

########################################
############### user.py ################
########################################
@APP.route('/user/profile', methods=['GET'])
def get_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    return dumps(user_profile(token, u_id))

@APP.route('/user/profile/setname', methods=["PUT"])
def set_name():
    data = request.get_json()
    return dumps(user_profile_setname(data['token'], data['name_first'], data['name_last']))

@APP.route('/user/profile/setemail', methods=['PUT'])
def set_email():
    data = request.get_json()
    return dumps(user_profile_setemail(data['token'], data['email']))

@APP.route('/user/profile/sethandle', methods=['PUT'])
def set_handle():
    data = request.get_json()
    return dumps(user_profile_sethandle(data['token'], data['handle_str']))

@APP.route('/user/profile/uploadphoto', methods=['POST'])
def set_photo():
    data = request.get_json()
    token = data['token']
    img_url = data['img_url']
    x_start = int(data['x_start'])
    y_start = int(data['y_start'])
    x_end = int(data['x_end'])
    y_end = int(data['y_end'])
    server_url = request.host
    return dumps(user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end, server_url))

@APP.route('/static/<path:path>')
def send_img(path):
    return send_from_directory('/static/', path)

########################################
############## other.py ################
########################################
@APP.route('/clear', methods=['DELETE'])
def clear_data():
    return dumps(clear())

@APP.route('/users/all', methods=['GET'])
def get_all_users():
    return dumps(users_all(request.args.get('token')))

@APP.route('/admin/userpermission/change', methods=['POST'])
def change_permission():
    data = request.get_json()
    return dumps(admin_userpermission_change(data['token'],
            int(data['u_id']), int(data['permission_id'])))

@APP.route('/search', methods=['GET'])
def search_msg():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(search(token, query_str))

########################################
############# standup.py ###############
########################################
@APP.route('/standup/start', methods=['POST'])
def start_standup():
    data = request.get_json()
    return dumps(standup_start(data['token'], int(data['channel_id']), int(data['length'])))

@APP.route('/standup/active', methods=['GET'])
def standup_active_check():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(standup_active(token, channel_id))

@APP.route('/standup/send', methods=['POST'])
def send_standup_msg():
    data = request.get_json()
    return dumps(standup_send(data['token'], int(data['channel_id']), data['message']))

if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
