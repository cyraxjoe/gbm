import functools
import os
import tempfile
import atexit

import seleniumrequests
import selenium.webdriver

import gbm.urls


@functools.cache
def get_driver():
    options = selenium.webdriver.firefox.options.Options()
    options.add_argument("--headless")
    driver_args = {
        "options": options,
        "service_log_path": os.path.join(
            tempfile.gettempdir(),
            'gbm-geckodriver.log'
            )
     }
    # if self.proxy is not None:
    #     debug_msg("Using proxy for selenium driver")
    #     # get just the plain proxy network location,
    #     # for e.g.: http://test:8080 -> test:8080
    #     proxy_host = urlparse(self.proxy).netloc
    #     caps = selenium.webdriver.DesiredCapabilities.FIREFOX
    #     caps['marionette'] = True
    #     caps['proxy'] = {
    #         "proxyType": "MANUAL",
    #         "httpProxy": proxy_host,
    #         "ftpProxy": proxy_host,
    #         "sslProxy": proxy_host,
    #     }
    #     driver_args["capabilities"] = caps
    driver = seleniumrequests.Firefox(**driver_args)
    atexit.register(driver.quit)
    # get the page to get the incapsula cookie
    driver.get(gbm.urls.SIGNIN_FORM_URL)
    return driver
