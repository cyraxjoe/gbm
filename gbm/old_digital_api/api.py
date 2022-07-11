import enum
import urllib.parse

import requests

import gbm.common


class InstrumentType(enum.Enum):
    """
    Constants that represent the two main different types of
    securities available on the GBM account.
    """
    BMV = 0
    SIC = 2


def get_itype_value(instrument_type):
    """
    Return the value for the instrument type/enum and validate for valid types.
    """
    if isinstance(instrument_type, InstrumentType):
        return instrument_type.value
    elif instrument_type in (0, 2):
        return instrument_type # no need to do anything
    else:
        raise Exception("Invalid instrument type {}".format(instrument_type))

class GBMAPI:

    def __init__(self, session=None):
        self.session       = session
        self.app_mgmt      = AppManagement(session)
        self.cash          = Cash(session)
        self.contract_mgmt = ContractManagement(session)
        self.market        = Market(session)
        self.operation     = Operation(session)
        self.portfolio     = Portfolio(session)
        self.research      = Research(session)
        self.security      = Security(session)
        self.user          = User(session)
        self.utilities     = Utilities(session)
        self._contract_id  = None

    def _get_first_contract_id(self):
        contracts = self.contract_mgmt.contracts_BP()
        if not contracts:
            raise Exception("Unable to retrieve any contracts for the account.")
        contract = contracts[0]
        return contract['contractId']

    @property
    def contract_id(self):
        """
        Convenient property to return the first contract id of the account.
        For the regular single contract account of an individual.

        The contract id is used on a lot of the method of the API.
        """
        if self._contract_id:
            return self._contract_id
        else:
            self._contract_id = self._get_first_contract_id()
            return self._contract_id


class _APISegment:

    def __init__(self, session=None):
        self.session = session

    def _apicall(
            self,
            fragment, *args,
            method='post',
            parent=None,
            headers=None, # ignore the session if this is not None
            raw=False, # return the whole request object
            **kwargs):
        if parent is None:
            parent = self.__class__.__name__
        if headers is None:
            if self.session is None:
                raise Exception("There is no headers or session to make the request.")
            headers = self.session.headers
        path = gbm.common.gbm_url(parent + '/' + fragment)
        if method == 'post':
            reqmethod = requests.post
        elif method == 'get':
            reqmethod = requests.get
        else:
            raise Exception("Unsupported method {}".format(method))
        rsp = reqmethod(path, headers=headers, **kwargs)
        if raw:
            return rsp
        else:
            return rsp.json()


class AppManagement(_APISegment):

    def _lower_apicall(self, *args, **kwargs):
        """
        Some parts of the api are called on a lowercase path, this is strictly
        not required but we will follow the js error to blend into their
        system.
        """
        parent = self.__class__.__name__.lower()
        return self._api_call(*args, parent=parent, **kwargs)

    #######################
    ## Lowercase methods ##
    #######################

    def agreement_type(self):
        """
        URL: GetAgreementType
        Method: GET
        Response:
        [1,2]
        """
        return self._lower_apicall('GetAgreementType', method='get')

    def agreement_log(self, agreement_type_id):
        """
        URL: GetAgreementLog
        Method: POST
        Body:
        {"agreementTypeId":0}
        Response:
           [{"employeeId": 14080,"applicationId":1,"agreementTypeId":1,"agreementStatusTypeId":2,
             "contractId":"<reducted>","processDate":"2016-05-23T10:46:12.42-05:00"},
           {"employeeId": <reducted>,"applicationId":1,"agreementTypeId":2,"agreementStatusTypeId":2,
            "contractId":"<reducted>","processDate":"2016-05-24T14:15:46.2-05:00"}]
        """
        return self._lower_apicall('GetAgreementLog', json={
            'agreementTypeId': agreement_type_id
        })

    def commisions_badges(self, global_contract=False):
        """
        URL: GetCommisionsBadges
        Method: POST
        Body:
        {"GlobalContract":false}
        Response:
          [{"badgeId":1,"commisionPercentage":0.25,"minAmount":0.0,
           "maxAmount":1000000.0,"description":"INVERSIONISTA","globalContract":false},
          {"badgeId":2,"commisionPercentage":0.2,"minAmount":1000001.0,"maxAmount":3000000.0,
           "description":"SILVER","globalContract":false},
         {"badgeId":3,"commisionPercentage":0.15,"minAmount":3000001.0,
          "description":"GOLD","globalContract":false}]
        """
        return self._lower_apicall('GetCommisionsBadges', json={
            'GlobalContract': global_contract
        })


    def user_widgets_types(self):
        """
        URL: getUserWidgetTypes
        Method: GET
        Response:

         [{"widgetTypeId":1,"name":"Operación","description":"Widget de Operación","categoryId":5298,"canMaximize":false,
           "draggable":false,"canOperate":true,"maxInstances":10,"solaceNotifications":true,"othersNotifications":false,
            "maxCol":4,"maxRow":7,"minRow":4,"minCol":3,"isEnabled":true},
          {"widgetTypeId":2,"name":"Monitor","description":"Widget de Monitor de Precios",
            "categoryId":5298,"canMaximize":true,"draggable":true,"canOperate":false,"maxInstances":2,
            "solaceNotifications":false,"othersNotifications":true,"maxCol":9,"maxRow":8,"minRow":3,
            "minCol":6,"isEnabled":true},
          {"widgetTypeId":4,"name":"Ordenes","description":"Widget de Ordenes","categoryId":5298,"canMaximize":true,
           "draggable":true,"canOperate":false,"maxInstances":2,"solaceNotifications":false,"othersNotifications":true,
          "maxCol":12,"maxRow":7,"minRow":3,"minCol":6,"isEnabled":true},
          {"widgetTypeId":7,"name":"Gráfica Emisora","description":"Widget de Gráfica Emisora",
          "categoryId":5298,"canMaximize":true,"draggable":true,"canOperate":false,"maxInstances":10,
          "solaceNotifications":false,"othersNotifications":true,"maxCol":4,"maxRow":6,"minRow":3,
          "minCol":3,"isEnabled":true},
          {"widgetTypeId":8,"name":"Gráfica Índice","description":"Widget de Gráfica Índice","categoryId":5298,
          "canMaximize":true,"draggable":true,"canOperate":false,"maxInstances":4,"solaceNotifications":false,
          "othersNotifications":true,"maxCol":4,"maxRow":6,"minRow":3,"minCol":3,"isEnabled":true},
          {"widgetTypeId":9,"name":"Índices","description":"Widget de Índices","categoryId":5298,
          "canMaximize":true,"draggable":true,"canOperate":false,"maxInstances":4,"solaceNotifications":false,"othersNotifications":true,
          "maxCol":5,"maxRow":6,"minRow":3,"minCol":3,"isEnabled":true},
          {"widgetTypeId":10,"name":"Gráficas Avanzadas","description":"Description Test Modified","categoryId":5298,"canMaximize":true,
          "draggable":true,"canOperate":false,"maxInstances":10,"solaceNotifications":false,"othersNotifications":true,"maxCol":9,
          "maxRow":6,"minRow":4,"minCol":7,"isEnabled":true},
          {"widgetTypeId":11,"name":"Histórico de Transacciones","description":"Widget de Histórico de Transacciones",
          "categoryId":5298,"canMaximize":true,"draggable":true,"canOperate":false,"maxInstances":2,"solaceNotifications":false,
          "othersNotifications":true,"maxCol":8,"maxRow":4,"minRow":4,"minCol":8,"isEnabled":true},
          {"widgetTypeId":13,"name":"Detalle de Emisora","description":"Widget de Detalle de Emisora",
          "categoryId":5298,"canMaximize":true,"draggable":true,"canOperate":false,"maxInstances":2,"solaceNotifications":false,
          "othersNotifications":true,"maxCol":5,"maxRow":6,"minRow":2,"minCol":3,"isEnabled":true},
          {"widgetTypeId":14,"name":"Posición","description":"Widget de Posición","categoryId":5298,"canMaximize":false,"draggable":true,
          "canOperate":false,"maxInstances":1,"solaceNotifications":true,"othersNotifications":false,"maxCol":8,"maxRow":6,"minRow":3,
          "minCol":6,"isEnabled":true},
          {"widgetTypeId":15,"name":"Top Ten","description":"Widget de Top Ten","categoryId":5298,"canMaximize":true,"draggable":true,
          "canOperate":true,"maxInstances":3,"solaceNotifications":true,"othersNotifications":true,"maxCol":4,"maxRow":7,"minRow":3,"minCol":3,"isEnabled":true}
        ]
        """
        return self._lower_apicall('getUserWidgetTypes', method='get')

    def user_dashboards(self, width=1920, height=1080):
        """
        URL: getUserDashboards
        Method: POST
        Body:
          {"width":1920,"height":1080}
        Response:
        [{"employeeId":0,"dashBoardId":21604,"name":"charts","isActive":false,
          "widgets":"[{\"id\":263374,\"col\":0,\"row\":0,\"size_y\":7,\"size_x\":9,\"name\":\"Monitor\"}]",
           "applicationId":0,"height":0,"width":0},
        {"employeeId":0,"dashBoardId":19923,"name":"En la mira","isActive":false,
        "widgets":"[{\"id\":227172,\"col\":7,\"row\":5,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                    {\"id\":227183,\"col\":0,\"row\":5,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                    {\"id\":227180,\"col\":7,\"row\":9,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                    {\"id\":227181,\"col\":0,\"row\":9,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                   {\"id\":227193,\"col\":0,\"row\":13,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                   {\"id\":227194,\"col\":7,\"row\":13,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                   {\"id\":227223,\"col\":0,\"row\":17,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                   {\"id\":227224,\"col\":7,\"row\":17,\"size_y\":4,\"size_x\":7,\"name\":\"Gráficas Avanzadas\"},
                   {\"id\":238353,\"col\":0,\"row\":0,\"size_y\":5,\"size_x\":14,\"name\":\"Monitor\"}]",
        "applicationId":0,"height":0,"width":0}, ...]
        """
        return self._lower_apicall('getUserDashboards', json={
            "width": width,
            "height": height
        })

    def widget_configuration(self, widget_id):
        """
        URL: getWidgetConfiguration/<widget-id>
        Method: GET
        Response:
          {"widgetTypeId":15,
           "config":{"bindNotifications":true,"binding":"alpha",
           "properties":{"default":{"marketSelectedTabId":"IPC","topicSelectedTabId":2}}}}
        """
        return self._lower_apicall('getWidgetConfiguration/' + str(widget_id), method='get')

    def widgets_in_user_dashboard(self, dashboard_id):
        """
        URL: getWidgetsInUserDashBoard/<dashboard-id>
        Method: GET
        Response:
        [{"min_sizey":3,"min_sizex":6,"max_sizey":8,"max_sizex":9,"init":false,
          "widgetTypeId":2,"id":263374,"col":0,"row":0,
          "size_y":7,"size_x":9,"name":"Monitor"}]
        """
        return self._lower_apicall('getWidgetsInUserDashBoard/' + str(dashboard_id),
                                   method='get')

    def update_widgets_configuration(self, config):
        """
        URL: updateWidgetsConfiguration
        Method: POST
        Body:
          [{"widgetId":234001,
           "configuration":{"widgetTypeId":1,
                          "config":{"bindNotifications":true,"binding":"alpha",
                                    "properties":{"default":{"selectedTabId":0}
                                                  "operationcapital":{"issue":"GFINBUR O","selectedTabId":1,"tradeMode":0,"amount":9090,
        "customButton1":"1M","customButton2":"5M","customButton3":"10M","toggleDisplayL2Value":true},
        "operationfund":{"selectedTabId":true,"customButtonFund1":"1M","customButtonFund2":"5M",
        "customButtonFund3":"10M"},"operationcash":{}}}}},
        {"widgetId":248876,"configuration":{"widgetTypeId":10,"config":{"bindNotifications":true,"binding":"alpha",
        "properties":{"default":{"symbol":"GFINBUR O","interval":"1D"}}}}},
        {"widgetId":227519,"configuration":{"widgetTypeId":10,"config":{"bindNotifications":true,"binding":"alpha",
        "properties":{"default":{"symbol":"GFINBUR O","interval":"1D"}}}}}]
        Response:
         <no-data> use httpcode
        """
        return self._lower_apicall('updateWidgetsConfiguration', json=config)

    ##############################
    ## End of Lowercase methods ##
    ##############################

    def user_default_configuration(self):
        """
        URL: GetUserDefaultConfiguration
        HTTP method: GET
        Expected return value:
        {
            "cultureId": <int>,
            "solaceNotifications": <bool>,
            "themeName": <str>,
            "alias": <str>,
            "userName": <str>,
            "notificationsEmail": <str>,
            "telephone": <str>
        }
        """
        return self._apicall('GetUserDefaultConfiguration', method='get')


    def capital_market_operation_time(self):
        """
        URL: GetCapitalMarketOperationTime
        HTTP method: GET
        Expected return value:
        {
            "isNormalOperationTime": <bool>, # true
            "startTime":"<datetime iso>",
            "endTime":"<datetime iso>"
        }
        """
        return self._apicall('GetCapitalMarketOperationTime', method='get')

    def cultures(self):
        """
        URL: GetCultures
        HTTP method: GET
        Expected return value:
        [
          {
            "cultureId": 1,
            "name": "Español",
            "code": "es-MX",
            "isEnabled": true,
            "isDefault": true },
          {
           "cultureId":2,
           "name": "Inglés",
           "code":"en-US",
           "isEnabled": true,
           "isDefault": false}
        ]
        """
        return self._apicall('GetCultures', method='get')

    def user_app_configuration(self):
        """
        URL: GetUserAppConfiguration
        HTTP method: GET
        Expected return value:
        {
        "cultureId":1,
        "cultureDescription":"es-MX",
        "solaceNotifications":true,
        "themeName":"Tema",
        "isMultiSession":false,
        "uiConfiguration":
          "{\"contractId\": \"<int>\",
            \"dashboardSorting\":[21604,19923,19507,19506,19925,19505,19922,19504]}"
        }
        """
        return self._apicall('GetUserAppConfiguration', method='get')

    ## Solace methods
    def solace_data_topic(self, is_sic=False, instruments=('*',)):
        """
        URL: GetSolaceDataTopic
        HTTP method: POST
        Body:
          {
            "isRealTime": true,
            "issic": false, # if true will return the sic topics
            "instruments": ["*"]
         }
        Expected return value:
        {
        "dataServiceAgent": "svc/GBM/R/MD",
        "dataSubscription": ["dat/GBM/R/MDWEB/MEX/E/BMV/NAC/*"],
        "aggServiceAgent": "svc/GBM/R/MD",
        "aggSubscription": ["dat/GBM/R/AGG/MEX/E/BMV/NAC/*"]
        }
        """
        return self._apicall('GetSolaceDataTopic', json={
            'isRealTime': True,
            'issic': is_sic,
            'instruments': instruments
        })

    def solace_topic(self, is_sic=False, instruments=('*',)):
        """
        URL: GetSolaceLTopic/true
        Method: POST
        Body:
           {"isRealTime":true,"issic":false,"instruments":["*"]}
        Return:
        {"dataServiceAgent":"svc/GBM/R/MD","dataSubscription":["dat/GBM/R/L2/MEX/E/BMV/NAC/*"],
        "aggServiceAgent":"svc/GBM/R/MD","aggSubscription":["dat/GBM/R/AGG/MEX/E/BMV/NAC/*"]}
        """
        return self._apicall('GetSolaceLTopic/true', json={
            'isRealTime': True,
            'issic': is_sic,
            'instruments': instruments
        })

    def solace_indexes_topic(self):
        """
        URL: GetSolaceIndexesTopic
        Method: POST
        Returns:
            {"serviceAgent":"svc/GBM/R/MD","suscription":["dat/GBM/R/Indices2/MEX/*"]}
        """
        return self._apicall('GetSolaceIndexesTopic')

    def update_user_app_configuration(self, ui_config):
        """
        URL: UpdateUserAppConfiguration
        Method: POST
        Body:
           {"cultureId":1,"cultureDescription":"es-MX","solaceNotifications":true,"themeName":"Tema",
            "isMultiSession":false,
        "uiConfiguration":
           "{\"contractId\":\"<int>\",
            \"dashboardSorting\":[21604,19923,19507,19506,19925,19505,19922,19504]}"}
        Response: None
        """
        return NotImplemented # too dangerous
        return self._apicall('UpdateUserAppConfiguration', json={
            "cultureId": 1,
            "cultureDescription": "es-MX",
            "solaceNotifications": True,
            "themeName":"Tema",
            "isMultiSession": False,
            'uiconfiguration': ui_config
        })


class Cash(_APISegment):

    def all_bank_account_information(self, contract_id):
        """
        URL: GetAllBankAccountInformation
        HTTP method: POST
        Body params:
           {"accountId":"<int>","contractId":"<int>"} # same value in both fields
        Response:
           [{"accountId":"<int>","bankAccountId":<int>,
            "bankAccountNumber":"XXXXXXXXXXXXXXX-<int>",
             "bankId": <int>,"bankName": <str>
             "automaticDeposits":true,"termsAndConditions":false,
            "subAccountId":0,"ssiId":0,"isPropietaryAccount":false,
            "isAuthorizedByTransactDesk":false,"isAuthorizedByTreasury":false}]
        """
        return self._apicall('GetAllBankAccountInformation', json={
            'accountId': str(contract_id),
            'contractId': str(contract_id)
        })

    def deposit_account_information(self, contract_id):
        """
        URL: getDepositAccountInformation/undefined
        Method: POST
        Body:
          {"contractId":"<int>"}
        Response:
           {"response":"<int>"}
        """
        return self._apicall('getDepositAccountInformation/undefined', json={
            'contractId': contract_id
        })


class ContractManagement(_APISegment):
    """
    Contact management of the account.

    The method `contracts_BP` is the primary way to get the contact id of the account.
    """


    def contracts_BP(self):
        """
        URL: GetContractsBP
        Method: GET
        Response:
        [{"contractId":"<int>","isEnabled":true,"isDefault":true,
          "isPublic":false,"processDate":"<datetime-iso>","subAccountId":0}]
        """
        return self._apicall('GetContractsBP', method='get')


    def contracts(self, contract_id):
        """
        This method is only relevant to see what features are enabled to the
        given contract. Also it's pretty slow, probably is better to use
        `contracts_BP` and `contract`.

        URL: GetContracts
        Method: POST
        Body:
           {"request":"<contract-id>"}
        Response:
           [{"contractID":"<int-id>","memberSince":"<datetime-iso>",
            "active":true,"isgbmEmployee":false,"profile":0,"commissionBuy":0.2,
            "commissionSell":0.2,"spreadLimit":0.03,"tradePhysicalPersonFunds":true,
            "birthDay":"<datetime-iso>","contractGender":2,
            "tradeSIC":true, "tradeShortSell":true,"partyType":0,
            "tradeMargin":true,"isppr":false,"affiliateTypeId":0,
            "clientType":1,"canOperate":false}]
        """
        return self._apicall('GetContracts', json={
            'request': str(request)
        })

    def contract(self, contract_id):
        """
        URL: GetContract
        Method: POST
        Body:
        {"contractId":"<int>"}
        Response:
        {"contractID":"<int>","memberSince":"<datetime-iso>","active":true,
        "isgbmEmployee":false,"profile":0,"commissionBuy":0.2,"commissionSell":0.2,
        "spreadLimit":0.03,"tradePhysicalPersonFunds":true,"birthDay":"<datetime-iso>",
        "contractGender":2,"tradeSIC":true,"tradeShortSell":true,"partyType":0,
        "tradeMargin":true,"isppr":false,"affiliateTypeId":0,"clientType":1,"canOperate":false}
        """
        return self._apicall('GetContract', json={
            'contractId': str(contract_id)
        })


class Market(_APISegment):

    def capital_market_historic_price(self, issue_id, instrument_type, start_date, end_date):
        """
        One of the primary methods to get the historic data.

        `start_date` and `end_date` must be iso encoded datestrings

        URL: GetCapitalMarketHistoricPrice
        Method: POST
        Body:
           {"issueId":"<str>","instrumentType":0,"IsOnLine":true,
            "startDate":"<datetime>","endDate":"<datetime>"}
        Response:
        [
        {"date":"2016-07-18T00:00:00-05:00",
         "closePrice":31.73,
         "openPrice":32.2,"maxPrice":32.4,
         "minPrice":31.24,
         "percentageChange":-0.532915360501562,
         "volume":1513085}, ...
        ]
        """
        return self._apicall('GetCapitalMarketHistoricPrice', json={
            'issueId': issue_id,
            'instrumentType': get_itype_value(instrument_type),
            'isOnline': True,
            'startDate': start_date,
            'endDate': end_date
        })

    def instrument_prices_intraday_complete(self, instrument, request=60):
        """
        URL: GetInstrumentPricesIntradayComplete/<url-encoded-instrument>
        Method: POST
        Body:
           {"IsOnLine":true,"request":60} # 1800?
        Response:
        [
        {"date":"2016-07-18T00:00:00-05:00",
         "closePrice":31.73,
         "openPrice":32.2,"maxPrice":32.4,
         "minPrice":31.24,
         "percentageChange":-0.532915360501562,
         "volume":1513085}, ...
        ]
        """
        instrument = urllib.parse.quote(instrument)
        return self._apicall('GetInstrumentPricesIntradayComplete/' + instrument, json={
            'IsOnline': True,
            'request': request
        })

    def instrument_prices_intraday_ppp(self, instrument_id):
        """
        The same as complete intraday but with Precio Promedio Ponderado (weighted average price).

        This method is used on the simple chart widget.

        URL: GetInstrumentPricesIntradayPPP/<instrument-id>
        Method: POST
        Body:
           params: isOnline
        Response:
        [{'date': '2016-08-01T14:58:00-05:00',
          'percentageChange': 1.61001788908765,
          'price': 5.68,
          'volume': 67748},
        {'date': '2016-08-01T14:59:00-05:00',
        'percentageChange': 1.43112701252236,
        'price': 5.67,
        'volume': 17976}, ...]
        """
        instrument_id = urllib.parse.quote(instrument_id)
        return self._apicall('GetInstrumentPricesIntradayPPP/' + instrument_id, json={
            'IsOnLine': True
        })



    def market_price_monitor_detail(self, instrument_type=InstrumentType.BMV):
        """
        URL: GetMarketPriceMonitorDetail
        Method: POST
        Body:
           {"isOnLine":true,"instrumentType":2}
        Response:
        benchmarks can be empty
        For BMV:
        [
          {
            "aggregatedVolume": 529905,
            "askPrice": 128.73,
            "askVolume": 2878,
            "averageVolume6M": 1253801,
            "benchmarks": [
                {
                    "benchmarkDesc": "\u00cdndice de Precios y Cotizaciones",
                    "benchmarkId": 1,
                    "benchmarkName": "IPC",
                    "benchmarkPercentage": 1.0
                }
            ],
            "bidPrice": 128.57,
            "bidVolume": 275,
            "bursatilityType": 1,
            "closePrice": 127.89,
            "instrumentType": 0,
            "ipcParticipationRate": 3.96364878387649,
            "isFundOfFunds": false,
            "issueID": "AC *",
            "issueName": "ARCA CONTINENTAL, S.A.B. DE C.V.",
            "lastPrice": 128.89,
            "maxPrice": 129.3,
            "minPrice": 127.5,
            "minimumAmount": 0.0,
            "openPrice": 127.79,
            "percentageChange": 0.781921964187963,
            "ppp": 128.89,
            "sectorId": "1",
            "serie": "*",
            "symbol": "AC",
            "tradingLineId": 0,
            "valueChange": 0.999999999999986
          }, ...
        ]


        For SIC:

        [
            {
                "aggregatedVolume": 0,
                "askPrice": 0.0,
                "askVolume": 0,
                "averageVolume6M": 0,
                "benchmarks": [
                          {
                              "benchmarkDesc": "\u00cdndice Standard & Poor's 500",
                              "benchmarkId": 16,
                              "benchmarkName": "SPX",
                              "benchmarkPercentage": 1.0
                          }
                      ],
                "bidPrice": 0.0,
                "bidVolume": 0,
                "bursatilityType": 1,
                "closePrice": 306.851837,
                "instrumentType": 2,
                "ipcParticipationRate": 0.0,
                "isFundOfFunds": false,
                "issueID": "0H6U N",
                "issueName": "ASSA ABLOY AB",
                "lastPrice": 0.0,
                "maxPrice": 0.0,
                "minPrice": 0.0,
                "minimumAmount": 0.0,
                "openPrice": 0.0,
                "percentageChange": 0.0,
                "ppp": 0.0,
                "sectorId": "-1",
                "serie": "N",
                "symbol": "0H6U",
                "tradingLineId": 0,
                "valueChange": -306.851837
            }, ...
        ]
        """
        return self._apicall('GetMarketPriceMonitorDetail', json={
            'isOnLine': True,
            'instrumentType': get_itype_value(instrument_type)
        })


    def index_intraday(self, index_id):
        """
        Use commodities_by_type with None to get the available indices.

        URL: GetIndexIntraday/<index>
        Method: POST
        Body:
         {"IsOnLine":true}
        Response:
         [
          {date:"2016-08-01T05:31:36.24-05:00",
           percentageChange: 0,
          price: 46660.67, volume: 0}, ...]
        """
        return self._apicall('GetIndexIntraday/' + urllib.parse.quote(index_id), json={
            'IsOnline': True
        })


    def commodities_by_type(self, commodity_type=-3):
        """
        The -3 is the magic number that see the most that gets used on HBPro.

        Valid types:

          -3
           18: Currencies


        This will return the information of the commodities as is diplayed on
        the market info widget.

        URL: GetCommoditiesByType
        Method: POST
        Body:
         if:
           {"commodityType":-3}
          Response:
           [{"name":"ADM","description":"ADM","lastValue":43.96,"closeValue":43.87,
             "buyPrice":0.0,"sellPrice":0.0,"percentageChange":0.205152,"unitChange":0.09,
             "volume":265306,"currencyType":0,"commodityType":5}, ...]
        if commodity_type is None:

          [{"name":"BOVESPA","description":"BOVESPA","lastValue":56755.76,"closeValue":57308.21,"buyPrice":0.0,
            "sellPrice":0.0,"percentageChange":-0.963998,"unitChange":-552.45,"volume":0,
            "currencyType":0,"commodityType":15},
           {"name":"DJI","description":"DJI","lastValue":18404.51,"closeValue":18432.24,"buyPrice":0.0,
            "sellPrice":0.0,"percentageChange":-0.150443,"unitChange":-27.73,"volume":83472994,"currencyType":0,
            "commodityType":15},
           {"name":"IPC","description":"IPC","lastValue":46807.24,"closeValue":46660.67,"buyPrice":0.0,
            "sellPrice":0.0,"percentageChange":0.310000002384186,"unitChange":146.57,"volume":164907654,
            "currencyType":0,"commodityType":15},
           {"name":"MEXBOL","description":"MEXBOL","lastValue":46807.24,"closeValue":46660.67,"buyPrice":0.0,
            "sellPrice":0.0,"percentageChange":0.314119,"unitChange":146.57,"volume":291765276,"currencyType":0,
            "commodityType":15},
           {"name":"NASDAQ","description":"NASDAQ","lastValue":5184.195,"closeValue":5162.131,"buyPrice":0.0,
            "sellPrice":0.0,"percentageChange":0.42742,"unitChange":22.064,"volume":0,"currencyType":0,"commodityType":15}]

        """
        if commodity_type is None:
            # this will return the name of the indices available to do intraday chart
            data = {'isOnLine': True}
        else:
            data = {
                'commodityType': commodity_type
            }

        return self._apicall('GetCommoditiesByType', json=data)

    def search_issue(self, issue_query):
        """
        URL: SearchIssue/<issue-query>
        Method: GET
        Response:
          [{"instrumentType":2,"issueID":"IBM *",
           "issueName":"INTERNATIONAL BUSINESS MACHINES CORP."}, ...]
        """
        return self._apicall('SearchIssue/' + urllib.parse.quote(issue_query), method='get')

    def watchlist(self):
        """
        URL: GetWatchList
        Method: GET
        Response:
          [{"watchListTypeId":2,"configuration":"","title":"<title-for-2>"},
           ...,
           {"watchListTypeId":7,"configuration":"","title":"<title-for-7>"}]
        """
        return self._apicall('GetWatchList', method='get')

    def watch_list_detail(self, watch_list_type):
        """
        URL: GetWatchListDetail
        Method: POST
        Body:
        {"watchListType": <int>,"isOnLine":true}
        Response:
         [{"watchlistType":6,"symbol":"TLT","serie":"*","tipoValorIndeval":"1I",
           "issueID":"TLT *","issueName":"iShares 20+ Year Treasury Bond ETF",
           "lastPrice":0.0,"closePrice":2658.1,"sectorId":"-1",
           "benchmarks":[
              {"benchmarkId":16,"benchmarkName":"SPX","benchmarkDesc":"Índice Standard & Poor's 500","benchmarkPercentage":1.0}
           ],
           "instrumentType":2,"tradingLineId":0,"minimumAmount":0.0,"isFundOfFunds":false},
         {"watchlistType":6,"symbol":"TLH","serie":"*","tipoValorIndeval":"1I","issueID":"TLH *",
          "issueName":"ISHARES LEHMAN 10-20 YEAR TREASURY","lastPrice":0.0,"closePrice":2680.0,
           "sectorId":"-1","benchmarks":[
             {"benchmarkId":16,"benchmarkName":"SPX","benchmarkDesc":"Índice Standard & Poor's 500","benchmarkPercentage":1.0}
            ],"instrumentType":2,"tradingLineId":0,"minimumAmount":0.0,"isFundOfFunds":false},
         ...]
        """
        return self._apicall('GetWatchListDetail', json={
            'watchListType': watch_list_type,
            'isOnline': True
        })


    # datos de transacciones en el mercado
    def l2_market_data(self, instrument_id):
        """
        URL: /GetL2MarketData/<url-encoded-instrument>
        Method: GET
        Response:
        [
          {"sequence":1,"buyNumOrders":4,"buyPrice":5.89,
           "buyVolume":33300,"sellNumOrders":8,"sellPrice":5.9,"sellVolume":17120},
          {"sequence":2,"buyNumOrders":2,"buyPrice":5.88,"buyVolume":120,
           "sellNumOrders":2,"sellPrice":5.93,"sellVolume":2500},
          {"sequence":3,"buyNumOrders":1,"buyPrice":5.87,"buyVolume":100,"sellNumOrders":3,
           "sellPrice":5.94,"sellVolume":8100},
          {"sequence":4,"buyNumOrders":3,"buyPrice":5.86,"buyVolume":1819,
           "sellNumOrders":1,"sellPrice":5.95,"sellVolume":9377},
          {"sequence":5,"buyNumOrders":2,"buyPrice":5.85,"buyVolume":11000,"sellNumOrders":4,
          "sellPrice":5.96,"sellVolume":13000}
        ]
        """
        instrument_id = urllib.parse.quote(instrument_id)
        return self._apicall('GetL2MarketData/' + instrument_id, method='get')

    def md_market_data(self, instrument_id):
        """
        Get the trading information from all the participants.

        URL: GetMDMarketData/<instrument-id>
        Method: GET
        Response:
        [{'buyer': 'ACTIN',
           'issic': False,
           'last': 5.26,
           'oddLot': 'P',
           'operationVolume': 50,
           'regType': 'P',
           'seller': 'MS',
           'sequence': 5160486,
           'stockSeries': 'AXTEL CPO',
           'time': '2016-08-10T14:59:32.183-05:00',
           'trans': 'A',
           'typeOper': 'CO'}, ...]
        """
        instrument_id = urllib.parse.quote(instrument_id)
        return self._apicall('GetMDMarketData/'+ instrument_id, method='get')

    def company_share_percentage(self, instrument_id):
        """
        URL: GetCompanySharePercentage/<instrument-id>
        Method: POST
        Response:
        [{'amount': 89751.83,
          'averagePrice': 5.630250925287,
          'casaBolsa': 'VECTO',
          'companySharePercentage': 0.790888302350276,
          'descriptionOper': 'Compra',
          'numOper': 13,
          'volume': 15941}, ...]
        """
        instrument_id = urllib.parse.quote(instrument_id)
        return self._apicall('GetCompanySharePercentage/' + instrument_id)

    # el blotter esta en operacion


class Operation(_APISegment):

    def iva(self):
        """
        URL: GetIVA
        Method: GET
        Response:
           {"response":0.16}
        """
        return self._apicall('GetIVA', method='get')

    def available_funds_for_trade(self):
        """
        URL: GetAvailableFundsForTrade/true
        Method: GET
        Response:
         [{"tradeTime":"2016-07-27T13:45:00-05:00",
           "settlementTypeBuy":3,"settlementTypeSell":3,
           "minQuantity":1,"symbol":"GBM101",
           "serie":"B","issueID":"GBM101 B",
            "issueName":"GBM 101, S. A. de C. V., Sociedad de Inv",
            "lastPrice":1.099818,"closePrice":1.099818,"sectorId":"-1",
            "instrumentType":28,"tradingLineId":0,"minimumAmount":0.0,
           "isFundOfFunds":false}, ...]
        """
        return self._apicall('GetAvailableFundsForTrade/true', method='get')

    def capital_market_contract_risk(self, contract_id):
        """
        URL: GetCapitalMarketContractRisk
        Method: POST
        Body:
           {"contractId":"<reducted>"}
        Response:
           {"pendingOrdersRisk":0.0,"registeredOrdersValue":0.0,
            "reportos":0.0,"virtualSalesGBMF2":0.0}
        """
        return self._apicall('GetCapitalMarketContractRisk', json={
            'contractId': contract_id
        })

    def contract_properties(self, contract_id):
        """
        URL: GetContractProperties
        Method: POST
        Body:
        {"contractId":"<reducted>"}
        Response:
        {"sellingPower": <reducted-float>,"marginHB": <reducted-float>,
         "contractRisk":{"pendingOrdersRisk":0.0,"registeredOrdersValue":0.0,
                          "reportos":0.0,"virtualSalesGBMF2":0.0}}
        """
        return self._apicall('GetContractProperties', json={
            'contractId': contract_id
        })

    def blotter_capital_market(self, instrument_types, orders_id, process_date, contract_id):
        """
        URL: GetBlotterCapitalMarket
        Method: POST
        Body:
        {"instrumentTypes":[27,28],"ordersId":null,
         "processDate":"2016-07-27T09:17:27.246-05:00",
        "accountId":"00000","contractId":"000000"}
        Response:
         for [-1] and :[27,28]
         []
         or
         for instrumentTypes: [0,2]
        [{"sobId":9008423,"preorderId":0,"vigenciaId":0,"mainOrderAMId":0,"accountId":"0000",
          "instrumentType":2,"processDate":"2016-07-27T08:27:52.243-05:00",
          "gbmIntProcessStatus":9,"capitalOrderTypeId":1,"algoTradingTypeId":0,
          "treasuryOrderTypeId":-1,"bitBuy":true,"issueId":"AAPL *","price":1920.1,
          "averagePrice":0.0,"originalQuantity":10,"assignedQuantity":0,"cancelQuantity":0,
          "commision":0.0,"iva":0.0,"stopPrice":0.0,"duration":0,"triggerPrice":0.0,
          "pegOffsetValue":0,"maxFloor":0,"minQty":0,"isCancelable":false,"predespachador":false,
          "vigencia":false},
        {"sobId":9007542,"preorderId":0,"vigenciaId":2350275,"mainOrderAMId":0,"accountId":"00000",
          "instrumentType":2,"processDate":"2016-07-27T08:05:03.337-05:00",
          "gbmIntProcessStatus":2,"capitalOrderTypeId":8,"algoTradingTypeId":0,
          "treasuryOrderTypeId":-1,"bitBuy":false,"issueId":"JPM *","price":1222.0,
          "averagePrice":0.0,"originalQuantity":45,
          "assignedQuantity":0,"cancelQuantity":0,"commision":0.0,"iva":0.0,"stopPrice":0.0,
          "duration":6,"triggerPrice":0.0,"pegOffsetValue":0,"maxFloor":0,"minQty":0,
          "isCancelable":true,"predespachador":false,"vigencia":false}]
        """
        return self._apicall('GetBlotterCapitalMarket', json={
            'instrumentTypes': instrument_types,
            'ordersId': orders_id,
            'processDate': process_date,
            'contractId': contract_id
        })



class Portfolio(_APISegment):

    def transactions(self, contract_id, process_date, start_date, end_date,
                     **params):
        """
        URL: GetTransactions
        Method: POST
        Body:
        {"processDate":"2016-07-23T18:04:56.997Z","isSettlement":false,"pageIndex":0,
         "pageSize":10,"sortTransaction":23,"startDate":"2016-07-23T05:00:00.000Z",
        "endDate":"2016-07-24T04:59:59.000Z","contractId":"00000",
        "ascendent":true,"rowNumber":null}

        Response:

        This is an empty response:

        {"transactionTypeId":0,"subTransactionTypeId":0,"transactionsId":0,
         "ammount":0.0,"processDate":"0001-01-01T00:00:00-06:00",
         "settlementDate":"0001-01-01T00:00:00-06:00","contractId":"00000",
        "transactionsRowNumber":0,"transactionsPageId":0}
        """
        valid_keys = {
            'is_settlement', 'page_index', 'page_size',
            'sort_transaction', 'ascendent', 'row_number'
        }
        if not set(params.keys()).issubset(valid_keys):
            raise Exception("Invalid parameters {}".format(set(params.keys()) - valid_keys))
        return self._apicall('GetTransactions', json={
            "processDate": process_date,
            "isSettlement": params.get('is_settlement', False),
            "pageIndex": params.get('page_index', 0),
            "pageSize": params.get('page_size', 10),
            "sortTransaction": params.get('sort_transaction', 23), # magic number?
            "startDate": start_date,
            "endDate": end_date,
            "contractId": str(contract_id),
            "ascendent": params.get('ascendent', True),
            "rowNumber": params.get('row_number', None)
        })


    def position(self, contract_id):
        """
        positionValueType
           1.- Largo
           5.- Fondos de inversion
           8.- Garantia
          26.- Corto
          27.- Efectivo
        1000.- Total de cartera

        URL: GetPosition
        Method: POST
        Body:
        {"contractId":"<reducted>"}
        Response:

        [{"positionType":0,"averageCost":124.08000000,"shares":41,"positionValueType":1,
          "instrument":{"symbol":"AC","serie":"*","tipoValorIndeval":"1","issueID":"AC *",
             "issueName":"ARCA CONTINENTAL, S.A.B. DE C.V.","lastPrice":123.61,"closePrice":122.59,
             "sectorId":"01",
             "benchmarks":[{"benchmarkId":1,"benchmarkName":"IPC","benchmarkDesc":"Índice de Precios y Cotizaciones","benchmarkPercentage":1.0}],
             "instrumentType":0,"tradingLineId":0,"minimumAmount":0.0,"isFundOfFunds":false
          },
         "marketValue":5068.01,"custodyType":0,"positionDate":"0001-01-01T00:00:00-06:00",
        "portfolioId":0}, ...]
        """
        return self._apicall('GetPosition', json={
            'contractId': contract_id
        })

    def capital_transactions_amount_by_range(self, contract_id, start_date, end_date, global_contract=False):
        """
        Se usa para determinar el nivel de inversionista.

        URL: GetCapitalTransactionsAmountByRange
        Method: POST
        Body:
        {"contractId":"<reducted>","startDate":"2016-07-01T05:00:00.000Z","endDate":"2016-07-27T14:17:24.852Z","globalContract":false}
        Response:
        1401625.9200
        """
        return self._apicall('GetCapitalTransactionsAmountByRange', json={
            "contractId": contract_id,
            "startDate": start_date,
            "endDate": end_date,
            "globalContract": global_contract
        })

class Research(_APISegment):

    def interactive_data_user(self):
        """
        URL: GetInteractiveDataUser
        Method: POST
        Response:
        {"response":false}
        """
        return self._apicall('GetInteractiveDataUser')

class Security(_APISegment):

    def user_key(self, user, public_ip=None):
        """
        User can be the email or the legacy user.

        URL: GetUserKey
        Method: POST
        Body:
           {"user":"<reducted>"}
        Response:
          {"key":"<reducted>"}

        **This method does not depends on the security headers.**
        """
        if public_ip is not None:
            headers = gbm.common.base_headers(**{
                'X-Forwarded-For': public_ip
            })
        else:
            headers = None
        rsp = self._apicall('GetUserKey', headers=headers, json={
            'user': user
        })
        return rsp['key']

    def sign_in(self, user_hash, passwd, public_ip=None):
        """
        The user in the request is the hash of the user, obtained from the user_key method.

        On the response:

        The alias field on the response correspond to the user email.

        The user field on the response correspond to the user id.

        The hash is the primary field that is going to be used on all the rest of the calls.

        URL: SignIn/false
        Method: POST
        Body:
        {"user":"<reducted>","password":"<reducted>","token":"","deviceType":"1"}
        Response:
        {"user":<reducted>,"hash":"<reducted>","name":"<reducted>",
        "photo":"","hasLevel2":true,"isReadAndWrite":false,
        "alias":"<reducted>","timeExpiresReadSession":480,"timeExpiresOperationSession":20}
        """
        if public_ip is not None:
            headers = gbm.common.base_headers(**{
                'X-Forwarded-For': public_ip
            })
        else:
            headers = None
        return self._apicall('SignIn/false', headers=headers, json={
            'user': user_hash,
            'password': passwd,
            'token': '',
            'deviceType': '1'
        })

    def slide_session(self):
        """
        Slide the session on the server to extend the expiration of the session.

        URL: SlideSession
        Method: POST
        Body:
         {}
        Response:
          {"response":true}
        """
        return self._apicall('SlideSession', json={})['response']

    def sign_out(self):
        """
        URL: SignOut
        Method: GET
        Response: <none>
        Use http code to determine the result
        """
        rsp = self._apicall('SignOut', method='get', raw=True)
        return rsp.status_code == 200

class User(_APISegment):

    def user(self):
        """
        alias is the user email

        URL: GetUser
        Method: GET
        Response:
        {"employeeId": <reducted>, "userName":"<reducted>","name":"<reducted>","lastName1":"<reducted>","lastName2":"<reducted>",
        "creationDate":"2016-04-13T17:00:07.783-05:00","statusId":4,"telephone":"<reducted>",
        "folioCRM":"","picture":"","hasLevel2":true,"isReadAndWrite":false,"alias":"<reducted>",
        "userNameLegacy":"<reducted>","contracts":0,"notificationEmail":"<reducted>"}
        """
        return self._apicall('GetUser', method='get')



class Utilities(_APISegment):


    def public_ip(self):
        """
        URL: GetPublicIP
        Method: GET
        Response:
        {"response":"10.21.2.1"}

        **This method does not depends on the security headers.**
        """
        rsp = self._apicall('GetPublicIP', method='get', headers=gbm.common.base_headers())
        return rsp['response']

    def central_hour(self):
        """
        URL: GetCentralHour
        Method: GET
        Response:
        {"response":"2016-07-27T09:18:27.1489496-05:00"}
        """
        return self._apicall('GetCentralHour', method='get')
