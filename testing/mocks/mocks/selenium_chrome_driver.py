import multiprocessing
import platform

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork")  # Required on macOSX


@pytest.fixture(scope="class")
def selenium_chrome_driver(request, live_server):
    """
    Returns a Selenium Chrome driver as a fixture for testing.
    using an installed Chromedriver from the .venv chromedriver_py package
    install location. Accessible with the
    @pytest.mark.uses_fixture('selenium_chrome_driver')
    :return: A selenium chrome driver.
    """

    service_object = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # TODO: set chrome_options.binary_location = ...
    #  (if setting to run in container or on GitHub)
    chrome_driver = webdriver.Chrome(service=service_object, options=chrome_options)
    request.cls.driver = chrome_driver
    yield
    request.cls.driver.close()
