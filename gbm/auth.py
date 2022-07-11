import os
import time
import functools
import getpass
import json

import gbm.urls
from gbm.api._abstract import AbstractAPI
from gbm.constants import HBPRO_CLIENT_ID
from gbm.utilities import get_preferences_dir
from gbm.base_request import get_driver


def session_file_path(user):
    return os.path.join(
        get_preferences_dir(), '{}_session.json'.format(user)
    )


class Session:
    __slots__ = [
        '_raw_response',
        'user', 'access_token', 'identity_token', 'refresh_token',
        'token_type', 'expires_in', 'start_time'
    ]

    def __init__(self, user, json_rsp, start_time=None, auto_save=False):
        self._raw_response = dict(json_rsp)
        self.user = user
        relevant_keys = (
            ('accessToken', 'access_token'),
            ('identityToken', 'identity_token'),
            ('refreshToken', 'refresh_token'),
            ('tokenType', 'token_type'),
            ('expiresIn', 'expires_in')
        )
        for camel_key, snake_key in relevant_keys:
            setattr(self, snake_key, json_rsp[camel_key])

        if self.token_type != "Bearer":
            raise Exception(
                "Unsupported token type: {}".format(self.token_type)
            )
        if start_time is None:
            self.start_time = time.time()
        else:
            self.start_time = start_time
        if auto_save:
            self.save()

    @property
    def auth_access_header(self):
        return "{} {}".format(self.token_type, self.access_token)

    @property
    def auth_refresh_header(self):
        return "{} {}".format(self.token_type, self.refresh_token)

    @property
    def auth_identity_header(self):
        return "{} {}".format(self.token_type, self.identity_token)

    @property
    def expired(self):
        return time.time() > (self.start_time + self.expires_in)

    @property
    def remaining_time(self):
        return (self.start_time + self.expires_in) - time.time()

    def save(self):
        with open(session_file_path(self.user), 'w') as session_file:
            json.dump({
                'user': self.user,
                'raw_response': self._raw_response,
                'start_time': self.start_time
            }, session_file)

    @classmethod
    def from_saved_session(cls, user):
        with open(session_file_path(user)) as session_file:
            raw_values = json.load(session_file)
            return cls(
                raw_values['user'],
                raw_values['raw_response'],
                raw_values['start_time']
            )


def requires_session(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.session is None:
            raise Exception(
                "Unable to use this endpoint without a session."
            )
        return method(self, *args, **kwargs)
    return wrapper


class AuthAPIv1(AbstractAPI):

    def __init__(self, driver, session=None):
        self.driver = driver
        self.session = session
        self._http_headers = {
            'Accept': 'application/json',
        }

    def _url_builder(self, *args, **kwargs):
        return gbm.urls.auth_api_v1_url(*args, **kwargs)

    @property
    def http_headers(self):
        if self.session is None:
            return self._http_headers
        return dict(
            self._http_headers, Authorization=self.session.auth_access_header
        )

    def session_user(self, user, password):
        login_info = {
            "clientId": HBPRO_CLIENT_ID,
            "user": user,
            "password": password
        }
        return self._post('/session/user', json_payload=login_info)

    def delete_session_user(self, refresh_auth_header):
        return self._delete(
            "/session/user",
            params={"client_id": HBPRO_CLIENT_ID},
            headers={'Authorization': refresh_auth_header}
        )

    def session_user_challenge(self, user, session, two_factor_token):
        payload = {
            "challengeType": "SOFTWARE_TOKEN_MFA",
            "session": session,
            "user": user,
            "code": two_factor_token,
            "clientId": HBPRO_CLIENT_ID,
            "applicationName": "GBM+ Trading Pro"
        }
        return self._post("/session/user/challenge", json_payload=payload)

    @requires_session
    def token(self):
        return self._get("/token")

    @requires_session
    def security_settings(self):
        return self._get('/security-settings')


def login(user, password=None, driver=None):
    if driver is None:
        driver = get_driver()
    if password is None:
        password = getpass.getpass("GBM Password: ")
    auth_api = AuthAPIv1(driver)
    rsp = auth_api.session_user(user, password)
    cinfo = rsp["challengeInfo"]
    if cinfo["challengeType"] != "SOFTWARE_TOKEN_MFA":
        raise Exception("Unable to determine what to do")
    import pdb; pdb.set_trace()
    two_factor_token = input("Token: ")
    credentials = auth_api.session_user_challenge(
        user, cinfo['session'], two_factor_token
    )
    return Session(user, credentials)


def logout(session, driver=None):
    if driver is None:
        driver = get_driver()
    auth_api = AuthAPIv1(driver)
    return auth_api.delete_session_user(session.auth_refresh_header)
