from selenium import webdriver
from seleniumwire import webdriver as proxy_driver
from typing import Optional

class Core:
    def __init__(self, executable_path: Optional[str], headless: bool = False) -> None:
        self._executable_path = executable_path

        self.options = webdriver.ChromeOptions()

        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--ignore-gpu-blacklist')
        self.options.add_argument('--use-gl')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36')
        self.options.add_experimental_option("excludeSwitches", ['enable-logging'])
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_experimental_option('prefs', {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })

    def initialize_driver(self, width: int = None, height: int = None) -> webdriver.Chrome:
        driver = webdriver.Chrome(executable_path=self._executable_path, options=self.options)

        if height or width:
            driver.set_window_size(
                width,
                height
            )

        return driver

class Docker(Core):
    def __init__(self) -> None:
        super().__init__(executable_path=None)
        self.options.add_argument("--disable-browser-side-navigation")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument('--dns-prefetch-disable')
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-web-security')

    def initialize_driver(self, height: int = None, width: int = None) -> webdriver.Chrome:
        driver = webdriver.Chrome(options=self.options)

        if height or width:
            driver.set_window_size(
                width, height
            )

        return driver

class Proxy(Core):
    def __init__(self, executable_path: Optional[str], proxy: str):
        super().__init__(executable_path)
        self._proxy = {
            'proxy': {
                'https': proxy
            }
        }

    def initialize_driver(self, width: int = None, height: int = None) -> webdriver.Chrome:
        driver = proxy_driver.Chrome(
            executable_path=self._executable_path,
            seleniumwire_options=self._proxy,
            chrome_options=self.options
        )

        if height or width:
            driver.set_window_size(
                width,
                height
            )

        return driver