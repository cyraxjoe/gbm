class AbstractAPI:

    def __init__(self, session, driver):
        self.session = session
        self.driver = driver

    def _url_builder(self, url, *args, **kwargs):
        raise NotImplementedError()

    @property
    def http_headers(self):
        return {
            'Accept': 'application/json',
            "Authorization": self.session.auth_access_header
        }

    def _request(
        self, method, url_segment, params=None, json_payload=None, headers=None
    ):
        url = self._url_builder(url_segment)
        kwargs = {'headers': self.http_headers}
        if json_payload is not None:
            kwargs['json'] = json_payload
        if params is not None:
            kwargs['params'] = params
        if headers is not None:
            kwargs['headers'].update(headers)
        rsp = self.driver.request(method, url, **kwargs)
        if rsp.ok:
            return rsp.json()
        else:
            raise Exception(
                "API error: code: {}, text: {}".format(
                    rsp.status_code, rsp.text
                )
            )

    def _get(self, url_segment, **kwargs):
        return self._request("GET", url_segment, **kwargs)

    def _post(self, url_segment, **kwargs):
        return self._request("POST", url_segment, **kwargs)

    def _delete(self, url_segment, **kwargs):
        return self._request("DELETE", url_segment, **kwargs)

    def _options(self, url_segment, **kwargs):
        return self._request("OPTIONS", url_segment, **kwargs)
