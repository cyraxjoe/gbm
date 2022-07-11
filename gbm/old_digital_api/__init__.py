import getpass
import logging


from gbm.old_digital_api import api, session
from gbm.exceptions import GBMException


logger = logging.getLogger(__name__)


def _old_api_init(user=None, passwd=None, *,
                  json_pack=None, autosave=False, load_from_preferences=False):
    """
    Convenient function that wraps the most regular use case
    of the module, by contructing an GBMAPI object with an
    initialized GBMSession with the specific user and password.

    If passwd is None and no json representation of a gbm.session.SessionPack
    is supplied, then ask a password.

    If "load_from_preferences" it will try to load the api from the
    last saved session from the preferences directory.
    """
    session_inst = None
    if load_from_preferences:
        try:
            session_inst = _get_last_session(autosave)
        except GBMException as e:
            logger.error(str(e))
            logger.error(
                "Unable to load the last session, proceeding with other methods"
            )
    if session_inst is None:
        if json_pack is not None:
            sp = session.SessionPack.from_json(json_pack)
            session_inst = session.GBMSession.from_pack(sp, autosave)
        elif user is None:
            raise GBMException("No json_pack is supplied and no user is specified.")
        else:
            if passwd is None:
                passwd = getpass.getpass('GBM Password: ')
            session_inst = session.GBMSession.autostart(user, passwd, autosave)
    api_inst = api.GBMAPI(session_inst)
    return api_inst


def _get_last_session(autosave):
    json_pack = session.get_last_session()
    sp = session.SessionPack.from_json(json_pack)
    return session.GBMSession.from_pack(sp, autosave)
