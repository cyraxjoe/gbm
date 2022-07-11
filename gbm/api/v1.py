import gbm.urls

from gbm.api._abstract import AbstractAPI


class GBMAPIv1(AbstractAPI):

    def _url_builder(self, *args, **kwargs):
        return gbm.urls.api_v1_url(*args, **kwargs)

    def contracts(self):
        return self._get('/contracts')
