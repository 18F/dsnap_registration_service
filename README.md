# dsnap_registration_service
[![CircleCI](https://circleci.com/gh/18F/dsnap_registration_service.svg?style=svg)](https://circleci.com/gh/18F/dsnap_registration_service)

## Why this project

This is the backend service for the D-SNAP registration application. It supports the saving and retrieval of D-SNAP registration applications.

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for additional information.

## Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.


## Development

### Installation

Install project dependencies using:
```
pipenv install
```
Once the dependencies have been installed, you can run the rest of the commands by dropping into a virtual environment shell by running `pipenv shell`, or by preceding each command with a `pipenv run`.

### Testing

Run tests using:
```
pytest
```

### Deployment

The project has been set up for continuous integration and deployment through CirclCI and cloud.gov. The cloud.gov spaces, URLs and deployment triggers are:

| Space     | URL                                                      | Deployment trigger                          |
|-----------|----------------------------------------------------------|---------------------------------------------|
| dev       | https://dsnap-registration-service-dev.app.cloud.gov     | Any push to a branch other than `master`    |
| staging   | https://dsnap-registration-service-staging.app.cloud.gov | Any push to `master`                        |
| prod      | https://dsnap-registration-service.app.cloud.gov         | Any tag push with a tag that begins with 'v'|
| demo      | https://dsnap-registration-service-demo.app.cloud.gov    | Any tag push with a tag that begins with 'v'|

### Running locally
Create a local PostgreSQL database. Set the environment variable DATABASE_URL to point to this database, e.g.:
```
export DATABASE_URL=postgresql:///dsnap_registration
```
If this variable is not set, it defaults to `postgresql:///dsnap_registration` in development/local environments.

Migrate the database, if necessary, using:
```
python manage.py migrate
```
Start the app using:
```
python manage.py runserver
```

This will make the application available at `http://localhost:8000`, by default. To change the port and other settings, see https://docs.djangoproject.com/en/2.1/ref/django-admin/#runserver.

## Endpoints

| URL               | Verb     | Description
|-------------------|----------|--------------------|
| /registrations    | POST     | The endpoint for submitting new registrations to be persisted. Returns the id of the new registration                        |
| /registrations    | GET      | Returns registrations. Allows query string params `state_id`, `registrant_ssn`, `registrant_dob`, `registrant_last_name`. Allows pagination with `limit` and `offset` query string params. |
| /registrations/id | GET      | Returns the specified registration                                                                                           |
| /registrations/id | PUT      | Updates the specified registration                                                                                           |
| /registrations/id | DELETE   | Deletes the specified registration                                                                                           |
