from selenium.common.exceptions import WebDriverException
from selenium.common import exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from typing import Tuple, List, Union

from settings.dev_config import CHROMEDRIVER

from .core import Core


class SberMarket:
    def __init__(self):
        self._driver = Core(executable_path=CHROMEDRIVER).initialize_driver()
        # self._driver = Docker().initialize_driver()

        self._wait = WebDriverWait(self._driver, 10)
        self._ac = ActionChains(self._driver)

    def open_map(self):
        if not self._safe_get('https://sbermarket.ru/'):
            raise RuntimeError('Не установлено соединение с сайтом.')

        # map_btn_locator = (By.XPATH, '//button[@type="button" and contains(., "Показать на карте")]')
        map_btn_locator = (By.XPATH, '//*[@id="by_courier"]/div[1]/div/div[1]/button')

        self._safe_click(map_btn_locator, 'Кнопка карты не найдена.')

        pickup_btn_locator = (By.XPATH, '/html/body/div[3]/div/div[3]/main/div/div/div[1]/div[1]/button[2]')

        self._safe_click(pickup_btn_locator, 'Кнопка самовывоза не найдена')

        show_list_btn_locator = (By.XPATH, '/html/body/div[3]/div/div[3]/main/div/div/div/button')

        self._safe_click(show_list_btn_locator, 'Кнопка показа списка магазинов не найдена.')

    def _select_city(self, value: str):
        select_locator = (By.XPATH, '/html/body/div[4]/div/div[3]/main/div[1]/select')

        select = Select(self._scroll_down_modal(select_locator, 'Дроп-даун не найден.'))

        select.select_by_value(value)

    def gather_store_links(self, city_values: List[str]):
        modal_locator = (By.XPATH, '//div[@class="PickupStoresModal_retailers__qcstX"]')

        for value in city_values:
            self._select_city(value)

            modal = self._scroll_down_modal(modal_locator, 'Модальное окно не найдено.')

            stores_locator = (By.XPATH, '//div[@class="RetailerItem_root__PRA2_"]')
            store_locator = (By.XPATH, '//div[@class="Store_root__Rn8Lu"]')

            if not self._does_element_exist(stores_locator): continue

            stores = modal.find_elements(*stores_locator)

            for store in stores[::-1]:
                self._ac.move_to_element(store).click().perform()

                if not self._does_element_exist(store_locator): continue

                small_stores = None

    def _does_element_exist(self, locator: Tuple[str, str]) -> bool:
        """ Returns True if element exists or else False. """
        try:
            self._wait.until(
                EC.presence_of_element_located(
                    locator
                )
            )
        except (exceptions.TimeoutException, exceptions.StaleElementReferenceException):
            return False

        return True

    def _safe_get(self, url: str) -> bool:
        """ Goes to the page or else throws an error. """
        try:
            self._driver.get(url)
        except WebDriverException:
            return False

        return True

    def _move_and_click(self, element: WebElement):
        self._ac.move_to_element(element).click().perform()

    def _raise_if_not_found(self, locator: Tuple[str, str], message: str):
        if not self._does_element_exist(locator):
            raise RuntimeError(message)

    def _scroll_down_modal(self, locator: Tuple[str, str], message: str) -> Union[WebElement, Select]:
        self._raise_if_not_found(locator, message)

        element = self._driver.find_element(*locator)

        # load select inner html
        self._ac.move_to_element(element).click().send_keys(Keys.END).perform()

        return element

    def _safe_click(self, locator: Tuple[str, str], not_found_error_msg: str):
        """
        Waits till element is found else throws an error.
        Moves to the element and clicks it.
        """
        self._raise_if_not_found(locator, not_found_error_msg)

        self._move_and_click(
            self._driver.find_element(*locator)
        )
