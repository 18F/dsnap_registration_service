import copy

import pytest
from rest_framework import status

GOOD_PAYLOAD = {
    "disaster_id": 34,
    "preferred_language": "English",
    "phone": "2165555555",
    "email": "adam@email.biz",
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
            "ssn": "123456789"
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "ssn": "223456789"
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
    payload["EXTRA_FIELD"] = "Some extra valie"

    response = client.post('/registrations', data=payload,
                           content_type="application/json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "Invalid request":
            ["""Validation failed: ["Additional properties are not allowed (\'EXTRA_FIELD\' was unexpected)"]"""]
    }


@pytest.mark.django_db
def test_lifecycle(client):
    payload = copy.deepcopy(GOOD_PAYLOAD)

    response = client.post('/registrations', data=payload,
                           content_type="application/json")
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert "id" in result
    assert "created_date" in result
    assert "modified_date" in result
    registration_id = result["id"]
    assert result["original_data"] == result["latest_data"]

    response = client.get(f'/registrations/{registration_id}',
                          content_type="application/json")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["original_data"] == result["latest_data"]

    payload["preferred_language"] = "Spanish"
    response = client.put(f'/registrations/{registration_id}', data=payload,
                          content_type="application/json")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["original_data"]["preferred_language"] == "English"
    assert result["latest_data"]["preferred_language"] == "Spanish"

    response = client.delete(f'/registrations/{registration_id}',
                          content_type="application/json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(f'/registrations/{registration_id}',
                          content_type="application/json")
    assert response.status_code == status.HTTP_404_NOT_FOUND
