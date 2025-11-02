import requests
import pytest
import hashlib
import uuid
from utils.session_manager import sessions

url = "http://localhost:8000"

TEST_USER = {"username": "test_user", "password": "password123", "name": "Test User"}
TEST_USER2 = {"username": "test_user2", "password": "secret456", "name": "Second User"}


@pytest.fixture(autouse=True)
def clear_sessions_and_users():
    sessions.clear()

    import utils.storage_utils
    utils.storage_utils.save_user_data([])


# register tests
def test_register_success():
    res = requests.post(f"{url}/register", json=TEST_USER)
    assert res.status_code == 200
    data = res.json()
    assert "session_token" in data

    token = data["session_token"]
    assert token in sessions

def test_register_missing_fields():
    res = requests.post(f"{url}/register", json={"username": "", "password": "", "name": ""})
    assert res.status_code == 400
    assert "Missing credentials" in res.text

def test_register_duplicate_username():
    requests.post(f"{url}/register", json=TEST_USER)
    res = requests.post(f"{url}/register", json=TEST_USER)
    assert res.status_code == 400
    assert "Username already exists" in res.text

#register edge cases
def test_register_missing_name():
    user_missing_name = {"username": "no_name", "password": "pass", "name": ""}
    res = requests.post(f"{url}/register", json=user_missing_name)
    assert res.status_code == 400
    assert "Missing credentials" in res.text

def test_register_special_characters():
    special_user = {"username": "user!@#", "password": "pa$$word!", "name": "Special Char"}
    res = requests.post(f"{url}/register", json=special_user)
    assert res.status_code == 200
    assert "session_token" in res.json()

# login tests
def test_login_success():
    requests.post(f"{url}/register", json=TEST_USER)
    login_data = {"username": TEST_USER["username"], "password": TEST_USER["password"]}
    res = requests.post(f"{url}/login", json=login_data)
    assert res.status_code == 200
    data = res.json()
    assert "session_token" in data
    token = data["session_token"]
    assert token in sessions
    assert sessions[token]["username"] == TEST_USER["username"]

def test_login_missing_fields():
    res = requests.post(f"{url}/login", json={"username": "", "password": ""})
    assert res.status_code == 400
    assert "Missing credentials" in res.text

def test_login_invalid_credentials():
    requests.post(f"{url}/register", json=TEST_USER)
    res = requests.post(f"{url}/login", json={"username": TEST_USER["username"], "password": "wrong"})
    assert res.status_code == 401
    assert "Invalid credentials" in res.text

    res2 = requests.post(f"{url}/login", json={"username": "nouser", "password": "nopass"})
    assert res2.status_code == 401

#login edge cases
def test_login_multiple_simultaneous_sessions():
    requests.post(f"{url}/register", json=TEST_USER)
    login_data = {"username": TEST_USER["username"], "password": TEST_USER["password"]}

    res1 = requests.post(f"{url}/login", json=login_data)
    token1 = res1.json()["session_token"]

    res2 = requests.post(f"{url}/login", json=login_data)
    token2 = res2.json()["session_token"]

    assert token1 != token2  
    assert token1 in sessions
    assert token2 in sessions
    assert sessions[token1]["username"] == TEST_USER["username"]
    assert sessions[token2]["username"] == TEST_USER["username"]

def test_login_incorrect_username_correct_password():
    requests.post(f"{url}/register", json=TEST_USER)
    res = requests.post(f"{url}/login", json={"username": "wrong_user", "password": TEST_USER["password"]})
    assert res.status_code == 401
    assert "Invalid credentials" in res.text

def test_login_whitespace_username_password():
    requests.post(f"{url}/register", json=TEST_USER)
    res = requests.post(f"{url}/login", json={"username": " ", "password": " "})
    assert res.status_code == 401
    assert "Invalid credentials" in res.text


# log out tests
def test_logout_success():
    res = requests.post(f"{url}/register", json=TEST_USER2)
    token = res.json()["session_token"]
    res2 = requests.post(f"{url}/logout", json={"token": token})
    assert res2.status_code == 200
    assert res2.json()["message"] == "User logged out"
    assert token not in sessions


def test_logout_no_active_session():
    res = requests.post(f"{url}/logout", json={"token": str(uuid.uuid4())})
    assert res.status_code == 404
    assert "No active session found" in res.text

#logout edge cases
def test_logout_twice():
    res = requests.post(f"{url}/register", json=TEST_USER)
    token = res.json()["session_token"]

    res1 = requests.post(f"{url}/logout", json={"token": token})
    assert res1.status_code == 200
    assert token not in sessions

    res2 = requests.post(f"{url}/logout", json={"token": token})
    assert res2.status_code == 404
    assert "No active session found" in res2.text

def test_logout_invalid_token():
    invalid_token = str(uuid.uuid4())
    res = requests.post(f"{url}/logout", json={"token": invalid_token})
    assert res.status_code == 404
    assert "No active session found" in res.text
