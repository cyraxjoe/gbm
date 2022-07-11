import logging
from dataclasses import dataclass

import gbm.api
import gbm.auth
from gbm.base_request import get_driver

logger = logging.getLogger(__name__)

__version__ = '1.0'


@dataclass
class APIs:
    v1: gbm.api.GBMAPIv1
    v2: gbm.api.GBMAPIv2
    gbmp: gbm.api.GBMPro
    auth: gbm.auth.AuthAPIv1
    session: gbm.auth.Session


def api_init(user, password=None, load_session=False):
    driver = get_driver()
    if load_session:
        session = gbm.auth.Session.from_saved_session(user)
    else:
        session = gbm.auth.login(user, password)
    apis = {
        'v1': gbm.api.GBMAPIv1(session, driver),
        'v2': gbm.api.GBMAPIv2(session, driver),
        'gbmp': gbm.api.GBMPro(session, driver),
        'auth': gbm.auth.AuthAPIv1(driver, session),
        'session': session
    }
    return APIs(**apis)
