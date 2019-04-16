import copy

import pytest
from rest_framework import status

GOOD_PAYLOAD = {
    "disaster_id": 34,
    "preferred_language": "en",
    "phone": "2165555555",
    "email": "adam@email.biz",
    "state_id": "ABC9876",
    "money_on_hand": 100,
    "residential_address": {
        "street1": "250 Oakland Way",
        "street2": "",
        "city": "Oakland",
        "state": "CA",
        "zipcode": "94612"
    },
    "mailing_address": {
        "street1": "365 Campus Rd",
        "street2": "",
        "city": "Cleveland",
        "state": "OH",
        "zipcode": "44121"
    },
    "county": "Alameda",
    "household": [
        {
            "first_name": "John",
            "last_name": "Doe",
            "ssn": "123456789",
            "sex": "male",
            "race": "",
            "ethnicity": "Hispanic or Latino"
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "ssn": "223456789",
            "sex": "female",
            "race": "White",
            "ethnicity": "Not Hispanic or Latino"
        },
    ]
}


def test_missing_required_field(client):
    payload = copy.deepcopy(GOOD_PAYLOAD)
    del payload["disaster_id"]

    response = client.post('/registrations', data=payload,
                           content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "Invalid request":
            ["""Validation failed: ["'disaster_id' is a required property"]"""]
    }


def test_extra_field(client):
    payload = copy.deepcopy(GOOD_PAYLOAD)
    payload["EXTRA_FIELD"] = "Some extra value"

    response = client.post('/registrations', data=payload,
                           content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "Invalid request":
            ['Validation failed: '
             '["Additional properties are not allowed '
             '(\'EXTRA_FIELD\' was unexpected)"]']
    }


@pytest.mark.django_db
def test_lifecycle(client):
    payload = copy.deepcopy(GOOD_PAYLOAD)

    response = client.post('/registrations', data=payload,
                           content_type="application/json")
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert "id" in result
    assert "created_at" in result
    assert "modified_at" in result
    registration_id = result["id"]
    assert result["original_data"] == result["latest_data"]

    response = client.get(f'/registrations/{registration_id}',
                          content_type="application/json")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["original_data"] == result["latest_data"]

    payload["preferred_language"] = "es"
    response = client.put(f'/registrations/{registration_id}', data=payload,
                          content_type="application/json")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["original_data"]["preferred_language"] == "en"
    assert result["latest_data"]["preferred_language"] == "es"

    response = client.delete(f'/registrations/{registration_id}',
                             content_type="application/json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(f'/registrations/{registration_id}',
                          content_type="application/json")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_search_by_registrant_ssn(client, payload1):
    search_url = '/registrations?registrant_ssn={}'.format(
        payload1['household'][0]['ssn'])
    response = client.get(search_url)
    result = response.json()
    assert len(result) == 1
    assert result[0]["original_data"] == payload1


@pytest.mark.django_db
def test_search_by_state_id(client, payload1):
    search_url = '/registrations?state_id={}'.format(payload1['state_id'])
    response = client.get(search_url)
    result = response.json()
    assert len(result) == 1
    assert result[0]["original_data"] == payload1


@pytest.mark.django_db
def test_search_by_non_registrant_ssn(client, payload1):
    search_url = '/registrations?registrant_ssn={}'.format(
        payload1['household'][1]['ssn'])
    response = client.get(search_url)
    result = response.json()
    assert len(result) == 0


@pytest.mark.django_db
def test_search_by_registrant_last_name(client, payload1, payload2):
    search_url = '/registrations?registrant_last_name={}'.format("Doe")
    response = client.get(search_url)
    result = response.json()
    assert len(result) == 2


@pytest.mark.django_db
def test_search_by_registrant_last_name_and_registrant_ssn(
        client, payload1, payload2):
    search_url = '/registrations?registrant_last_name={}&state_id={}'.format(
        "Doe", payload1["state_id"])
    response = client.get(search_url)
    result = response.json()
    assert len(result) == 1


@pytest.fixture
def payload1(client):
    payload1 = copy.deepcopy(GOOD_PAYLOAD)
    client.post('/registrations', data=payload1,
                content_type="application/json")
    return payload1


@pytest.fixture
def payload2(client):
    payload2 = copy.deepcopy(GOOD_PAYLOAD)
    payload2["state_id"] = "ZZ987654321"
    payload2["household"][0]["ssn"] = "987654321"
    del payload2["household"][1]
    client.post('/registrations', data=payload2,
                content_type="application/json")
    return payload2
