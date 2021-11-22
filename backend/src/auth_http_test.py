import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from auth import auth_login, auth_logout, auth_register, token_generate, get_reset_code

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

@pytest.fixture
def initial_users(url):
    # this function would clear all data and create 3 users
    requests.delete(url + 'clear')
    input = {
        'password' : 'password',
        'name_first': 'u',
        'name_last' : '1',
        }
    for idx in range(3):
        input['email'] = str(idx + 1) + 'test@test.com'
        requests.post(url + 'auth/register', json=input)

########################################
########## register tests ##############
########################################
# 1. standard test
# 2. error when invalid email
# 3. error when occupied email
# 4. error when invalid entered name

def test_register_standard(url):
    '''
    A simple test to register standard
    '''
    # create a standard user with len(password) == 6 and
    # len(first_name) == 1 and len(last_name) == 1
    input = {
        'email' : 'test1@test.com',
        'password' : '123456',
        'name_first': 'u',
        'name_last' : '1',
        }
    resp = requests.post(url + 'auth/register', json=input)
    assert resp.status_code == 200
    assert json.loads(resp.text)['u_id'] == 1
    assert json.loads(resp.text)['token'] == token_generate(1, 'register')

    # create a standard user with len(password) == 6 and
    # len(first_name) == 50 and len(last_name) == 50
    input = {
        'email' : 'test2@test.com',
        'password' : 'password',
        'name_first' : 'u' * 50,
        'name_last' : '2' * 50,
        }
    resp = requests.post(url + 'auth/register', json=input)
    assert resp.status_code == 200
    assert json.loads(resp.text)['u_id'] == 2
    assert json.loads(resp.text)['token'] == token_generate(2, 'register')

def test_register_error_invalid_email(url):
    '''
    A simple test for error when invalid email
    '''
    requests.delete(url + 'clear')
    input = {
        'email' : 'testtest.com',
        'password' : 'password',
        'name_first' : 'u',
        'name_last' : '1',
        }
    resp = requests.post(url + 'auth/register', json=input)
    assert resp.status_code == 400

def test_register_error_occupied_email(url):
    '''
    A simple test for error when occupied email
    '''
    requests.delete(url + 'clear')
    input = {
        'email' : 'test@test.com',
        'password' : 'password',
        'name_first' : 'u',
        'name_last' : '1',
        }
    resp = requests.post(url + 'auth/register', json=input)
    assert resp.status_code == 200
    resp = requests.post(url + 'auth/register', json=input)
    assert resp.status_code == 400

def test_register_error_invalid_name(url):
    '''
    A simple test for error when enterring invalid names
    '''
    requests.delete(url + 'clear')
    input = {
        'email' : 'test@test.com',
        'password' : 'password',
        'name_first' : '',
        'name_last' : '',
        }
    resp = requests.post(url + 'auth/register', json=input)
    assert resp.status_code == 400
    input['name_first'] = 'a' * 51
    resp = requests.post(url + 'auth/register', json=input)
    assert resp.status_code == 400
    input['name_last'] = 'a' * 51

########################################
############ login tests ###############
########################################
# 1. standard test
# 2. error when invalid email
# 3. error when incorrect password

def test_login_standard(url, initial_users):
    '''
    A simple test for register standard
    '''
    input = {
        'email' : '1test@test.com',
        'password' : 'password',
        }
    resp = requests.post(url + 'auth/login', json=input)
    assert resp.status_code == 200
    assert json.loads(resp.text)['u_id'] == 1
    assert json.loads(resp.text)['token'] == token_generate(1, 'login')

def test_login_error_invalid_email(url, initial_users):
    '''
    A simple test for invalid email
    '''
    input = {
        'email' : 'tetstest.com',
        'password' : 'password',
        }
    resp = requests.post(url + 'auth/login', json=input)
    assert resp.status_code == 400

def test_login_error_incorrect_pw(url, initial_users):
    '''
    A simple test for invalid password
    '''
    input = {
        'email' : '1tets@test.com',
        'password' : 'wrong_password',
        }
    resp = requests.post(url + 'auth/login', json=input)
    assert resp.status_code == 400
    
########################################
############ logout tests ##############
########################################
# 1. standard test
# 2. error when invalid token

def test_logout_standard(url, initial_users):
    '''
    A simple test for standard logout
    '''
    # login first
    input = {
        'email' : '1test@test.com',
        'password' : 'password',
        }
    requests.post(url + 'auth/login', json=input)
    # do logout
    resp = requests.post(url + 'auth/logout', json={'token': token_generate(1, 'login')})
    assert resp.status_code == 200
    assert json.loads(resp.text)['is_success'] is True

def test_logout_error_invalid_token(url):
    '''
    A simple test for invalid token
    '''
    # login first
    input = {
        'email' : '1test@test.com',
        'password' : 'password',
        }
    requests.post(url + 'auth/login', json=input)
    # do logout
    resp = requests.post(url + 'auth/logout', json={'token': 'invalid_token'})
    assert resp.status_code == 400

########################################
########### pwreset tests ##############
########################################

def test_pwreset_req_standard(url, initial_users):
    '''
    test pwreset_req works well
    no error
    user1 with email 1test@test.com calls pwreset_req
    '''
    data = {
        'email' : '1test@test.com'
        }
    resp = requests.post(url + 'auth/passwordreset/request', json=data)
    assert resp.status_code == 200

def test_pwreset_req_invalid_email(url, initial_users):
    '''
    error when entered email does not refer to a valid user
    pass an non-exist email address to pwreset_req
    '''
    data = {
        'email' : 'invalidemail@test.com'
        }
    resp = requests.post(url + 'auth/passwordreset/request', json=data)
    assert resp.status_code == 400

def test_pwreset_set_invalid_code(url, initial_users):
    '''
    test error raising when entered code is invalid
    1. non-existing
    2. empty string
    3. used code
    '''
    # call pwreset_req to set reset_code in database
    data = {
        'email' : '1test@test.com'
        }
    requests.post(url + 'auth/passwordreset/request', json=data)

    # 1. non-existing code
    data = {
        'reset_code' : 'invalid_code',
        'new_password' : '123456'
    }
    resp = requests.post(url + 'auth/passwordreset/reset', json=data)
    assert resp.status_code == 400

    # 2. empty string
    data['reset_code'] = ''
    resp = requests.post(url + 'auth/passwordreset/reset', json=data)
    assert resp.status_code == 400
