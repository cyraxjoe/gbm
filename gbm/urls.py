from gbm.constants import HBPRO_CLIENT_ID

API_V1_BASE_URL = "https://api.gbm.com/v1"
API_V2_BASE_URL = "https://api.gbm.com/v2"
API_GBMP_BASE_URL = "https://homebroker-api.gbm.com/GBMP/api"
AUTH_API_V1_BASE_URL = "https://auth.gbm.com/api/v1"
AUTH_BASE_URL = "https://auth.gbm.com"
SIGNIN_FORM_URL = AUTH_BASE_URL + (
    "/signin?client_id={}" .format(HBPRO_CLIENT_ID)
)


def auth_api_v1_url(url_segment):
    return "{}{}".format(AUTH_API_V1_BASE_URL, url_segment)


def api_v1_url(url_segment):
    return "{}{}".format(API_V1_BASE_URL, url_segment)


def api_v2_url(url_segment):
    return "{}{}".format(API_V2_BASE_URL, url_segment)


def api_gbmp_url(url_segment):
    return "{}{}".format(API_GBMP_BASE_URL, url_segment)
