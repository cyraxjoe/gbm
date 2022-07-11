import time
import pprint
import json
import logging
import warnings


import requests

import gbm.utilities
import gbm.api
from gbm.exceptions import GBMException
from gbm.common import (
    gbm_url,
    base_headers,
    APPLICATION_ID
)

logger = logging.getLogger(__name__)


def last_session_path():
    return gbm.utilities.get_preferences_dir() + '/last_session.json'

def save_session(session):
    """
    Save the JSON representation of the session as the last session
    on the preferences, overriding any previous session.
    """
    pack = session.export()
    json_pack = pack.to_json()
    logger.debug("Saving session")
    with open(last_session_path(), 'w') as session_file:
        session_file.write(json_pack)

def get_last_session():
    """
    Return the last session JSON representation from the preferences dir.
    """
    logger.debug("Loading last session")
    try:
        with open(last_session_path()) as session_file:
            return session_file.read()
    except FileNotFoundError:
        raise GBMException("There is no last session")


class SessionPack:
    """
    Simple class that contains the main properties to recreate a fully functional
    GBMSession  without the need of a user and password.
    """
    # the slots attribute is set only to make it explicit
    # that this class is not a general purpose container,
    # and it should be kept as minimally as possible
    __slots__ = (
        'public_ip', 'user', 'user_key',
        'signin_payload', 'start_ts',
        'last_slide_ts'
    )
    _attributes = (
        'public_ip', 'user', 'user_key',
        'signin_payload', 'start_ts',
        'last_slide_ts'
    )

    def __init__(self, *, public_ip, user, user_key,
                 signin_payload, start_ts, last_slide_ts):
        self.public_ip = public_ip
        self.user = user
        self.user_key = user_key
        self.signin_payload = signin_payload
        self.start_ts = start_ts
        self.last_slide_ts = last_slide_ts

    def __repr__(self):
        return "<gbm.session.SessionPack at {} for user: {}>".format(
            hex(id(self)), self.user
        )

    @classmethod
    def from_json(cls, json_str):
        attributes = json.loads(json_str)
        return cls(**attributes)

    def to_json(self):
        return json.dumps({
            a: getattr(self, a)
            for a in self._attributes
        })

    def inject(self, session):
        """
        Set the expected attributes on the session and set the password to None.
        """
        session.passwd = None
        for attrib in self._attributes:
            setattr(session, attrib, getattr(self, attrib))
        return session

class GBMSession:
    """
    GBM HomebrokerPro session.

    The public interface of this object is by using the methods:

      * start
      * stop
      * slide
      * export

    And the properties:

      * remaining_time
      * headers

    ``headers`` is the primary external interface, it will return a dictionary
    with the required headers to be used on the api calls.
    """
    public_ip = None
    user_key = None
    signin_payload = None
    start_ts = None
    last_slide_ts = None

    def __init__(self, user, passwd, *, autosave=False):
        """
        user is either the email used for the user account in GBM or
        the asigned user by GBM.

        If autosave is True, save the session on the preferences dir
        every time the slide method gets called or the session is initialized.
        """
        self.user = user
        self.passwd = passwd
        self.started = False
        # set to True when is constructed from the `from_pack` classmethod
        self._build_from_pack = False
        self._security_api = gbm.api.Security(self)
        self._autosave = autosave

    @property
    def remaining_time(self):
        """
        Return the remaning time of the session in minutes.
        """
        # for now we hardcode the read only time expires session
        # the timeExpiresReadSession is in minutes
        if not self.started:
            warnings.warn("The session has not started")
            return None
        window_sec = self.signin_payload['timeExpiresReadSession'] * 60
        if self.last_slide_ts is not None:
            exptime = self.last_slide_ts + window_sec
        else:
            exptime = self.start_ts + window_sec
        rtime_sec = exptime - time.time()
        return rtime_sec / 60.

    @property
    def headers(self):
        """
        Main property to be used to authenticate the API requests.

        This inclues the complete http headers to be used on the standard
        API calls.
        """
        return base_headers(**{
            'X-Forwarded-For': self.public_ip,
            'GBMDigitalIdentityUser': self.signin_payload['user'],
            'GBMDigitalIdentityHash': self.signin_payload['hash'],
        })

    @classmethod
    def autostart(cls, user, passwd, autosave):
        inst = cls(user, passwd, autosave=autosave)
        inst.start()
        return inst

    @classmethod
    def from_pack(cls, pack, autosave=False):
        """
        Load the GBMSession for a SessionPack. If autosave is True, then
        save the SessionPack JSON representation after every call to the
        slide method.
        """
        if not isinstance(pack, SessionPack):
            raise GBMException("The pack argument is not of the type SessionPack")
        inst = pack.inject(cls(None, None, autosave=autosave))
        inst.started = True
        inst._build_from_pack = True
        if inst.remaining_time <= 0:
            raise GBMException(
                "The session from the SessionPack is already expired.\n"
                "Remaining time: {}".format(inst.remaining_time)
            )
        return inst

    def export(self):
        """
        Return the SessionPack instance representing the current state
        of the session to later be recreated with `from_pack`.
        """
        return SessionPack(
            public_ip=self.public_ip,
            user=self.user,
            user_key=self.user_key,
            signin_payload=self.signin_payload,
            start_ts=self.start_ts,
            last_slide_ts=self.last_slide_ts
        )

    def start(self):
        """
        Initialize the session by going to the authentication workflow,
        this includes starting the Application session along with the Account
        session, it seems that GBM makes a distinction between the two,
        but the two are required to operate.

        If the session is successfully started return True and set the
        properties:

            public_ip
            user_key
            signin_payload
            started
            start_ts

        If the started property evaluate to True then it will return False and
        print a warning.

        And in case of any error while making starting the session raise an Exception.
        """
        if self.started:
            warnings.warn("The session has already started")
            return False
        self.public_ip = gbm.api.Utilities().public_ip()
        self.user_key = self._security_api.user_key(self.user, self.public_ip)
        self.signin_payload = self._app_signin()
        self.started = self._start_account_session()
        self.start_ts = time.time()
        if self._autosave:
            save_session(self)
        return self

    def slide(self):
        """
        Slide the session on the server.

        If the `_autosave` property is True, save the session in the preferences
        directory on each call.
        """
        rst = self._security_api.slide_session()
        if rst:
            self.last_slide_ts = time.time()
            if self._autosave:
                save_session(self)
            return True
        else:
            raise GBMException(
                "Unable to slide the Session. rst = {}".format(rst)
            )

    def stop(self):
        """
        Stop the session by going to the de-authentication workflow,
        this includes stopping the Application session along with the Account
        session, it seems that GBM makes a distinction between the two,
        but the two are required to operate and also to be fully logged out.

        If the session is successfully stopped return True and set the
        properties to:
           started = False
           strt_ts = None
        If the started property evaluate to False then it will return False and
        print a warning.

        And in case of any error while making the closing calls to finish the
        session raise an Exception.
        """
        if not self.started:
            warnings.warn("The session has not been started")
            return False
        close_account_rst = self._close_account_session()
        app_signout_rst = self._security_api.sign_out()
        if close_account_rst and app_signout_rst:
            self.started = False
            self.start_ts = None
            self._security_api.session = None
            return True
        else:
            raise GBMException(
                "An error has ocurrent while trying to close the session."
                "[account: {}, app: {}]".format(
                    close_account_rst, app_signout_rst
                )
            )

    def _app_signin(self):
        """
        Make the primary loging against the GBM server.

        The return value should be a dictionary based on the authentication
        payload for the user of the form:

        {'alias': ..., # the alias is the email
        'hasLevel2': True,
        'hash': ...,
        'isReadAndWrite': False,
        'name': ...,
        'photo': ...,
        'timeExpiresOperationSession': 20, # for session with token
        'timeExpiresReadSession': 480, # without token
        'user': <user_id_number>},
        """
        payload = self._security_api.sign_in(
            self.user_key, self.passwd, self.public_ip)
        # in case that the supplied credentials is wrong the possible payload
        # is something like:
        # {'ErrorCode': 3003,
        #  'IsBussinessError': False,
        #  'ErrorMessage': 'El usuario o la contraseña son incorrectos.',
        #  'EventId': 20810}
        if 'ErrorCode' in payload:
            if 'ErrorMessage' in payload:
                error_code = payload['ErrorCode']
                error_msg = payload['ErrorMessage']
                raise GBMException('{} <code: {}>'.format(error_msg, error_code))
            else:
                raise GBMException('Unable to authenticate.\n{}'.format(
                    pprint.pformat(payload))
                )
        elif 'user' in payload:
            # the key "user" in reality it means user id,
            # to avoid having headers with integers as values we use "str"
            payload['user'] = str(payload['user'])
            return payload
        else:
            raise GBMException('Unexpected payload.\n{}'.format(
                pprint.pformat(payload))
            )
    def _start_account_session(self):
        """
        The signin_payload should be obtained from the `self._app_signin` method.

        Returns `True` in case that the session was successfully started.
        """
        url = gbm_url('HBPro/loadPartial/Account/StartSession', is_api=False)
        json_body = {
            "name": self.signin_payload['name'],
            "user": self.signin_payload['user'],
            "sessionid": self.signin_payload['hash'],
            "hasLevel2": self.signin_payload['hasLevel2'],
            "isReadAndWrite": self.signin_payload['isReadAndWrite'],
            "applicationid": APPLICATION_ID,
            "ipaddress": self.public_ip,
            "timeExpiresReadSession": self.signin_payload['timeExpiresReadSession'],
            "timeExpiresOperationSession": self.signin_payload['timeExpiresOperationSession']
        }
        #rsp = requests.post(url, json=json_body, headers=self.headers)
        rsp = d.request("POST", url, json=json_body, headers=self.headers)
        breakpoint()
        return rsp.json()

    def _close_account_session(self):
        """
        Close the account session on the server.

        Returns `True` in case that the session was successfully closed.
        """

        url = gbm_url('HBPro/loadPartial/Account/CloseSession', is_api=False)
        rsp = requests.post(url, json={}, headers=self.headers)
        return rsp.json()
