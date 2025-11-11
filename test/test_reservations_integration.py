import pytest
import requests

URL = "http://localhost:8000"

#roles
ADMIN = "ADMIN"
USER = "USER"

ADMIN_LOGIN = {"username":"admin_tester", "password":"123", "name": "tester admin", "role": ADMIN}
USER_LOGIN = {"username":"user_tester", "password":"123", "name": "tester user", "role": USER}


# Give ADMIN or USER credentials and the role to register and login helper methods, to login as admin or user
def register_and_login(credentials: dict):

    if credentials["role"] == ADMIN:
        requests.post(f"{URL}/register", json=ADMIN_LOGIN)
    else: 
        requests.post(f"{URL}/register", json=USER_LOGIN)

    res = requests.post(f"{URL}/login", json=credentials)
    assert res.status_code == 200
    ses_token = res.json()["session_token"]
    return {"Authorization": ses_token}

# Register vehicle helper method for testing purposes.

def test_vehicle_creation_success():
    headers = register_and_login(USER_LOGIN)
    data = {"name": "My car", "license_plate": "AF-12-CD"}
    res = requests.post(f"{URL}/vehicles", json=data, headers=headers)

    assert res.status_code == 200
    res = res.json()
    assert res["license_plate"] == "AF-12-CD"
    assert res["name"] == "My car"
    assert "created_at" in res
    assert "updated_at" in res  # changed to support vehicle out model return.
    return res


#======================================================================================
"""POST reservations endpoint tests"""

# Test if creating a reservation as a user with a registered vehicle is succesfull with status code 201.
def test_create_reservation_as_user():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"],"start_time": "2025-12-04","end_time":"2025-12-05", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 201
    assert res.json()["status"] == "Success"
    reservation = res.json()["reservation"]
    for key in data:
        assert reservation[key] == data[key]

# Test if creating a reservation as a admin for a user with a registered vehicle is succesfull with status code 201.
def test_create_reservation_as_admin():
    headers = register_and_login(ADMIN_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["vehicle_id"],"start_time": "2025-12-04","end_time":"2025-12-05", "parking_lot_id": "1", "user": USER_LOGIN["username"]}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 201
    #assert res.json()["status"] == "Success"
    reservation = res.json()["reservation"]
    for key in data:
        assert reservation[key] == data[key]
    

# Test if an error occurs when trying to create a reservation for a user as an admin and the required user field is missing with status code 401.
def test_create_reservation_as_admin_missing_user():
    headers = register_and_login(ADMIN_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["vehicle_id"],"start_time": "2025-12-04","end_time":"2025-12-05", "parking_lot_id": "1"} #missing user field
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 401
    assert res.json()["error"] == "Required field missing"
    assert res.json()["field"] == "user" #indicates that the user field is missing


# Test missing required fields
def test_missing_parking_lot():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "2025-10-12"} 
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)

    assert res.status_code == 422
    assert res.json()["error"] == "Required field missing"
    assert res.json()["field"] == "parking_lot_id" 

def test_missing_vehicle_id():
    headers = register_and_login(USER_LOGIN)
    data = { "start_time": "2025-10-11", "end_time": "2025-10-12", "parking_lot_id": "1"} # missing vehicle_id field
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)

    assert res.status_code == 422
    assert res.json()[""]["error"] == "Required field missing"
    assert res.json()["field"] == "vehicle_id" 

def test_missing_start_time():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "end_time": "2025-10-12", "parking_lot_id": "1"} # missing start_time field
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)

    assert res.status_code == 422
    assert res.json()["error"] == "Required field missing"
    assert res.json()["field"] == "start_time" 

def test_missing_end_time():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "parking_lot_id": "1"} # missing end_time field
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)

    assert res.status_code == 422
    assert res.json()["error"] == "Required field missing"
    assert res.json()["field"] == "end_time" 


#Incorrect missing field type tests

def test_incorrect_vehicle_id_format():
    headers = register_and_login(USER_LOGIN)
    data = {"vehicle_id": "1233456", "start_time": "2025-10-11", "end_time": "2025-10-12", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 422
    assert res.json()["error"] == "Incorrect field format"
    assert res.json()["field"] == "vehicle_id"  


def test_incorrect_start_time_format():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "123456", "end_time": "2025-10-12", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 422
    assert res.json()["error"] == "Incorrect field format"
    assert res.json()["field"] == "start_time" 


def test_incorrect_end_time_format():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "123456", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 422
    assert res.json()["error"] == "Incorrect field format"
    assert res.json()["field"] == "end_time" 


def test_incorrect_parking_lot_id_format():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "2025-10-12", "parking_lot_id": "Z"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 422
    assert res.json()["error"] == "Incorrect field format"
    assert res.json()["field"] == "parking_lot_id" 

# Test if an error occurs when trying to create a reservation for the vehicle of a parking lot that doesn't exist with status code 404.
def test_parking_lot_id_not_found_user():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "2025-10-12", "parking_lot_id": "Z"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 404
    assert res.json()["detail"] == "Parking lot not found"

def test_parking_lot_id_not_found_admin():
    headers = register_and_login(ADMIN_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "2025-10-12", "parking_lot_id": "Z"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 404
    assert res.json()["detail"] == "Parking lot not found"
    


#======================================================================================
"""PUT reservations endpoint tests"""

# Test missing required fields

def test_update_missing_vehicle_id():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "2025-10-12","parking_lot_id": "3"} 
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)
    assert res.status_code == 201
    
    reservation_id = res.json()["reservation"]["id"]
    print(f"reservation id:: {reservation_id}")
    new_data = {"start_time": "2025-10-11","end_time": "2025-10-12","parking_lot_id": "1"}
    
    res_put = requests.put(f"{URL}/reservations/{reservation_id}", json= new_data, headers=headers)
 
    assert res_put.status_code == 422
    assert res_put.json()["error"] == "Required field missing"
    assert res_put.json()["field"] == "vehicle_id" #indicates which field is missing

def test_update_missing_start_time():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "2025-10-12","parking_lot_id": "3"} 
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)
    assert res.status_code == 201
    
    reservation_id = res.json()["reservation"]["id"]
    print(f"reservation id:: {reservation_id}")
    new_data = {"vehicle_id": vehicle["id"], "end_time": "2025-10-12","parking_lot_id": "1"}
    
    res_put = requests.put(f"{URL}/reservations/{reservation_id}", json= new_data, headers=headers)
 
    assert res_put.status_code == 422
    assert res_put.json()["error"] == "Required field missing"
    assert res_put.json()["field"] == "start_time"

def test_update_missing_end_date():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11", "end_time": "2025-10-12","parking_lot_id": "3"} 
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)
    assert res.status_code == 201
    
    reservation_id = res.json()["reservation"]["id"]
    print(f"reservation id:: {reservation_id}")
    new_data = {"vehicle_id": vehicle["id"], "start_time": "2025-10-11","parking_lot_id": "1"}
    
    res_put = requests.put(f"{URL}/reservations/{reservation_id}", json= new_data, headers=headers)
 
    assert res_put.status_code == 422
    assert res_put.json()["error"] == "Required field missing"
    assert res_put.json()["field"] == "end_time" 


def test_update_missing_parking_lot_id():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"],"start_time": "2025-10-11", "end_time": "2025-10-12", "parking_lot_id": "1"} 
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)
    assert res.status_code == 201
    
    reservation_id = res.json()["reservation"]["id"]
    print(f"reservation id:: {reservation_id}")
    new_data = {"vehicle_id": vehicle["id"],"start_time": "2025-10-11", "end_time": "2025-10-12",}
    
    res_put = requests.put(f"{URL}/reservations/{reservation_id}", json= new_data, headers=headers)
 
    assert res_put.status_code == 422
    assert res_put.json()["error"] == "Required field missing"
    assert res_put.json()["field"] == "parking_lot_id"
    
    
    
# Test if an error occurs when the reservation id is not found in the json file with status code 404.
def test_update_reservation_not_found():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    new_data = {"vehicle_id": vehicle["id"],"start_time": "2025-12-06","end_time":"2025-12-07", "parking_lot_id": "1"}
    res = requests.put(f"{URL}/reservations/9999999999999", json=new_data, headers=headers)

    assert res.status_code == 404
    assert res.json()["detail"] == "Reservation not found"
    

# Test if updating a reservation as a user is updated with status code 200.
def test_update_reservation_success():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"] ,"start_time": "2025-12-06","end_time":"2025-12-07", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    assert res.status_code == 201

    reservation_id = res.json()['id']
    new_data = {"vehicle_id": vehicle["id"],"start_time": "2025-12-06","end_time":"2025-12-08", "parking_lot_id": "1"}
    res_put = requests.put(f"{URL}/reservations/{reservation_id}", json=new_data, headers=headers)

    assert res_put.status_code == 200   
    assert res_put.json()["status"] == "Updated"
    reservation = res_put.json()
    for key in new_data:
        assert reservation[key] == new_data[key]

#======================================================================================
"""DELETE reservations endpoint tests"""

# Test if a deletion is possible and give status code 200.
def test_delete_reservation_deletion_succes():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"],"start_time": "2025-12-06","end_time":"2025-12-07", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)
    assert res.status_code == 201

    reservation_id = res.json()["id"]
    res_delete = requests.delete(f"{URL}/reservations/{reservation_id}", headers=headers)
    
    assert res_delete.status_code == 200
    assert res_delete.json()["status"] == "Deleted"
    assert res_delete.json()["id"] == reservation_id
    

# Test to see if an error occurs when a user that is not an admin or not the owner of the reservation can delete the reservation with status code 403.
def test_delete_reservation_nonowner_nonadmin():
    headers = register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"],"start_time": "2025-12-06","end_time":"2025-12-07", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json=data, headers=headers)

    reservation_id = res.json()['id']

    assert not headers['role'] == "ADMIN" or not "random_username" == reservation_id["user"]
    assert res.status_code == 403
    assert res.json()["detail"] == "Access denied"

# Test to see if an error occurs when a reservation id is not found with status code 404.
def test_reservation_not_found():
    headers = register_and_login(USER_LOGIN)
    res_delete = requests.delete(f"{URL}/reservations/19999999999999999", headers=headers)

    assert res_delete.status_code == 404
    assert res_delete.json()["detail"] == "Reservation not found"


#======================================================================================
"""GET reservations endpoint tests"""

# Test to see if an error occurs when a user that is not an admin and not the owner of the reservation can delete the reservation with status code 403.
def test_get_reservation_nonower_nonadmin():
    headers =  register_and_login(USER_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"],"start_time": "2025-12-06","end_time":"2025-12-07", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)

    reservation_id = res.json()['id']

    assert not headers['role'] == "ADMIN" and not "random_username" == reservation_id["user"]
    assert res.status_code == 403
    assert res.json()["detail"] == "Access denied"

# Test to see if getting a reservation by id is succesfull with status code 200
def test_get_reservation_succes():
    headers =  register_and_login(ADMIN_LOGIN)
    vehicle = test_vehicle_creation_success()
    data = {"vehicle_id": vehicle["id"],"start_time": "2025-12-06","end_time":"2025-12-07", "parking_lot_id": "1"}
    res = requests.post(f"{URL}/reservations/", json= data, headers=headers)

    reservation_id = res.json()['id']
    res = requests.get(f"{URL}/reservations/{reservation_id}", headers=headers)

    assert res.status_code == 200
    

