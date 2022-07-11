from urllib.parse import urljoin


APPLICATION_ID = '1'


def base_headers(referer='/HBPro/login', **kwargs):
    user_agent = ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-MX',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'DNT': '1',
        'GBMDigitalIdentityApp': APPLICATION_ID,
        'User-Agent': user_agent,
    }
    if referer is not None:
        headers['Referer'] = gbm_url(referer, is_api=False)
    headers.update(kwargs)
    return headers


def gbm_url(path, is_api=True):
    base_host = 'https://www.gbmhomebroker.com/'
    if is_api:
        url = urljoin(base_host + 'GBMDigital/api/', path)
    else:
        url = urljoin(base_host, path)
    return url
