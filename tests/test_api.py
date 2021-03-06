import base64
import copy

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

TEST_USERNAME = "admin"
TEST_PASSWORD = "admin"
TEST_AUTHORIZATION = "Basic {}".format(str(base64.b64encode(
    f"{TEST_USERNAME}:{TEST_PASSWORD}".encode()), "utf-8"))

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
    ],
    "ebt_card_number": None
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
def test_authentication(client):
    payload = copy.deepcopy(GOOD_PAYLOAD)

    response = client.post('/registrations', data=payload,
                           content_type="application/json")
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    registration_id = result["id"]

    response = client.get(f'/registrations/{registration_id}',
                          content_type="application/json")
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    payload["preferred_language"] = "es"
    response = client.put(f'/registrations/{registration_id}', data=payload,
                          content_type="application/json")
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    response = client.delete(f'/registrations/{registration_id}',
                             content_type="application/json")
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    response = client.put(f'/registrations/{registration_id}/status',
                          content_type="application/json")
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_lifecycle(authenticated_client):
    payload = copy.deepcopy(GOOD_PAYLOAD)

    response = authenticated_client.post('/registrations', data=payload,
                                         content_type="application/json")
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert "id" in result
    assert "created_at" in result
    assert "modified_at" in result
    registration_id = result["id"]
    assert result["original_data"] == result["latest_data"]

    response = authenticated_client.get(f'/registrations/{registration_id}',
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["original_data"] == result["latest_data"]

    payload["preferred_language"] = "es"
    response = authenticated_client.put(f'/registrations/{registration_id}',
                                        data=payload,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    result = response.json()
    assert result["original_data"]["preferred_language"] == "en"
    assert result["latest_data"]["preferred_language"] == "es"

    response = authenticated_client.delete(
        f'/registrations/{registration_id}', content_type="application/json",
        HTTP_AUTHORIZATION=TEST_AUTHORIZATION
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = authenticated_client.get(f'/registrations/{registration_id}',
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_status(authenticated_client):
    payload = copy.deepcopy(GOOD_PAYLOAD)
    status_payload = {
        "rules_service_approved": True,
        "user_approved": True
    }

    response = authenticated_client.post('/registrations', data=payload,
                                         content_type="application/json",
                                         HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    registration_id = result["id"]
    response = authenticated_client.put(
        f'/registrations/{registration_id}/status',
        content_type="application/json", data=status_payload,
        HTTP_AUTHORIZATION=TEST_AUTHORIZATION
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["rules_service_approved"] == \
        status_payload["rules_service_approved"]
    assert result["user_approved"] == status_payload["user_approved"]

    # Strangely, the result of the PUT has the `approved_by` set to the
    # userid and not the username. A GET is needed for the username
    response = authenticated_client.get(f'/registrations/{registration_id}',
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    result = response.json()
    assert result["approved_by"] == "admin"


@pytest.mark.django_db
def test_ebt_accepted_on_put_but_null_on_post(authenticated_client):
    payload = copy.deepcopy(GOOD_PAYLOAD)
    payload['ebt_card_number'] = '123456789'
    response = authenticated_client.post(
        '/registrations', data=payload, content_type="application/json",
        HTTP_AUTHORIZATION=TEST_AUTHORIZATION
    )
    result = response.json()
    assert result['original_data'] == result['latest_data']
    assert result['original_data']['ebt_card_number'] is None

    registration_id = result["id"]
    response = authenticated_client.put(
        f'/registrations/{registration_id}', data=payload,
        content_type="application/json", HTTP_AUTHORIZATION=TEST_AUTHORIZATION
    )
    result = response.json()
    assert result['original_data']['ebt_card_number'] is None
    assert result['latest_data']['ebt_card_number'] ==\
        payload['ebt_card_number']


@pytest.mark.django_db
def test_search_by_registrant_ssn(authenticated_client,  payload1):
    search_url = '/registrations?registrant_ssn={}'.format(
        payload1['household'][0]['ssn'])
    response = authenticated_client.get(search_url,
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result) == 1
    assert result[0]["original_data"] == payload1


@pytest.mark.django_db
def test_search_by_state_id(authenticated_client,  payload1):
    search_url = '/registrations?state_id={}'.format(payload1['state_id'])
    response = authenticated_client.get(search_url,
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result) == 1
    assert result[0]["original_data"] == payload1


@pytest.mark.django_db
def test_search_by_non_registrant_ssn(authenticated_client,  payload1):
    search_url = '/registrations?registrant_ssn={}'.format(
        payload1['household'][1]['ssn'])
    response = authenticated_client.get(search_url,
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result) == 0


@pytest.mark.django_db
def test_search_by_registrant_last_name(
        authenticated_client, payload1, payload2):
    search_url = '/registrations?registrant_last_name={}'.format("doe")
    response = authenticated_client.get(search_url,
                                        HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result) == 2


@pytest.mark.django_db
def test_search_by_registrant_last_name_and_registrant_ssn(
        authenticated_client,  payload1, payload2):
    search_url = '/registrations?registrant_last_name={}&state_id={}'.format(
        "Doe", payload1["state_id"])
    response = authenticated_client.get(
        search_url, HTTP_AUTHORIZATION=TEST_AUTHORIZATION)
    assert response.status_code == status.HTTP_200_OK
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


@pytest.fixture
def authenticated_client(client):
    get_user_model().objects.create_superuser(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            email="admin@example.com")
    return client
