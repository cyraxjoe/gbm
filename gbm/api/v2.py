from gbm.api._abstract import AbstractAPI


class GBMAPIv2(AbstractAPI):

    def accounts(self, contract_id):
        return self._get("/contracts/{}/accounts".format(contract_id))

    def opening_status(self):
        return self._get("/opening-status")

    def intraday_trade_aggregates(self, exchange, security, timespan):
        url = "/markets/{}/securities/{}/intraday-trade-aggregates".format(
            exchange, security
        )
        return self._get(url, params={"timespan": timespan})

    def index_intraday(self, index):
        url = "/markets/indexs/securities/{}/intraday-trades".format(
            index
        )
        return self._get(url)
