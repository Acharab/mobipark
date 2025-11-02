import requests
import pytest
from utils.session_manager import add_session

url = "http://localhost:8000"

USER_TOKEN = "mock-user-token"
ADMIN_TOKEN = "mock-admin-token"

USER_ACCOUNT = {"username": "mock_user", "role": "USER"}
ADMIN_ACCOUNT = {"username": "mock_admin", "role": "ADMIN"}


@pytest.fixture(autouse=True)
def setup_mock_sessions():
    add_session(USER_TOKEN, USER_ACCOUNT)
    add_session(ADMIN_TOKEN, ADMIN_ACCOUNT)


def auth_headers(user_type="USER"):
    if user_type == "ADMIN":
        return {"Authorization": ADMIN_TOKEN}
    return {"Authorization": USER_TOKEN}


#  tests voor billing endpoint

# basic auth 
def test_billing_no_token():
    res = requests.get(f"{url}/billing")
    assert res.status_code == 401
    assert "Unauthorized" in res.text


def test_billing_invalid_token():
    res = requests.get(f"{url}/billing", headers={"Authorization": "invalid-token"})
    assert res.status_code == 401


# user session 
def test_billing_user_only_own_sessions():
    res = requests.get(f"{url}/billing", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    for entry in data:
        assert entry["session"]["licenseplate"] is not None
        assert "hours" in entry["session"]
        assert "days" in entry["session"]

def test_billing_user_with_no_sessions():
    add_session("empty-user-token", {"username": "empty_user", "role": "USER"})
    res = requests.get(f"{url}/billing", headers={"Authorization": "empty-user-token"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) == 0


# admin session
def test_billing_admin_can_access_other_user():
    res = requests.get(f"{url}/billing/{USER_ACCOUNT['username']}", headers=auth_headers("ADMIN"))
    assert res.status_code == 200
    data = res.json()
    for entry in data:
        assert entry["session"]["licenseplate"] is not None

def test_billing_admin_access_nonexistent_user():
    res = requests.get(f"{url}/billing/nonexistent_user", headers=auth_headers("ADMIN"))
    assert res.status_code in (200, 404)

def test_billing_non_admin_cannot_access_other_user():
    res = requests.get(f"{url}/billing/{ADMIN_ACCOUNT['username']}", headers=auth_headers())
    assert res.status_code == 403
    assert "Access denied" in res.text


#session edge cases

def test_billing_user_with_empty_sessions():
    res = requests.get(f"{url}/billing", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_billing_short_session_free():
    import utils.storage_utils
    from datetime import datetime, timedelta
    short_start = (datetime.now() - timedelta(seconds=120)).strftime("%d-%m-%Y %H:%M:%S")
    def mock_load_json(filename):
        return {"s1": {"user": "mock_user", "licenseplate": "FREE-123", "started": short_start, "stopped": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}}
    import types
    utils.storage_utils.load_json = types.FunctionType(mock_load_json.__code__, globals())
    res = requests.get(f"{url}/billing", headers=auth_headers())
    data = res.json()
    assert data[0]["amount"] == 0


#payment edge cases
def test_billing_partial_payment():
    res = requests.get(f"{url}/billing", headers={"Authorization": USER_TOKEN})
    assert res.status_code == 200
    data = res.json()
    for entry in data:
        assert "amount" in entry and "payed" in entry and "balance" in entry
        assert entry["balance"] == entry["amount"] - entry["payed"]
        assert entry["balance"] >= 0

