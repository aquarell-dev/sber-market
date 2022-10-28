from typing import Tuple, List
from .types import Urls, Store, Category

from .asyncfetch import Fetch
from settings.dev_config import TEMP
from settings.dev_config import threads, cool_down

import asyncio

import json, os, datetime


class SberMarket:
    def __init__(self):
        self._fetch = Fetch()
        self._semaphore = asyncio.BoundedSemaphore(threads)

        self._store_counter = 0
        self._category_counter = 0

        self._data = Urls(
            retailer_url='https://sbermarket.ru/api/retailers',
            stores_url='https://sbermarket.ru/api/stores?city_id=%s&retailer_id=%s&include=full_address,distance,opening_hours_text&shipping_method=pickup_from_store&zero_price=true',
            categories_url='https://sbermarket.ru/api/stores/%s/categories?depth=2&include=&reset_cache=true'
        )

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'client-token': '7ba97b6f4049436dab90c789f946ee2f',
        'api-version': '3.0'
    }

    async def gather_retailer_slugs(self) -> List[str]:
        retailers, status = await self._fetch.fetch(
            url=self._data.retailer_url,
            message='[+] Собраны ритейлеры',
        )

        if status != 200: raise RuntimeError('[-] Ошибка при выполнении запроса')

        retailer_slugs = []

        retailers = retailers['retailers']

        print(f'[+] Найдено {len(retailers)} ритейлеров')

        for retailer in retailers:
            retailer_slugs.append(retailer['slug'])

        return retailer_slugs

    async def get_retailer_stores(self, store_data: Tuple[str, str], retailer_stores: List[Store], total: int):
        city_id, retailer_id = store_data

        stores, status = await self._fetch.boundFetch(
            semaphore=self._semaphore,
            url=self._data.get_stores_url(city_id, retailer_id),
            headers=self.headers,
            time_sleep=cool_down,
        )

        self._store_counter += 1

        if status == 404: return print(f'[-] Сеть магазинов {retailer_id} не найдена в городе {city_id} ({self._get_percentage(self._store_counter, total)})')

        if status != 200: return print(f'[-] Ошибка при выполнении запроса ({self._get_percentage(self._store_counter, total)})')

        print(f'[+] Найдена сеть {retailer_id} в городе {city_id} ({self._get_percentage(self._store_counter, total)})')

        for store in stores:
            retailer_stores.append(
                Store(
                    sid=store['store_id'],
                    address=store['full_address'],
                    retailer_id=retailer_id,
                    title=store['name'],
                    url=f'https://sbermarket.ru/{retailer_id}?sid={store["store_id"]}'
                )
            )

    async def get_store_categories(self, store: Store, total: int):
        categories, status = await self._fetch.boundFetch(
            semaphore=self._semaphore,
            url=self._data.get_categories_url(store.sid),
            headers=self.headers,
            time_sleep=cool_down,
        )

        self._category_counter += 1

        if status != 200: return print(f'[-] Не удалось получить категории магазина '
                                       f'{store.title} ({self._get_percentage(self._category_counter, total)})')

        print(f'[+] Категории(кол-во: {len(categories)}) магазина {store.title} получены. ({self._get_percentage(self._category_counter, total)})')

        categories_list = []

        for category in categories['categories']:
            children = []

            if category.get('children'):
                for child in category['children']:
                    children.append(
                        Category(
                            title=child['name'],
                            url=f"https://sbermarket.ru/{store.retailer_id}/c/{child['slug']}?sid={store.sid}&source=category"
                        )
                    )

            categories_list.append(
                Category(
                    title=category['name'],
                    url=f"https://sbermarket.ru/{store.retailer_id}/c/{category['slug']}?sid={store.sid}",
                    children=children
                )
            )

        store.categories = categories_list

    def get_parsing_data(self, cities, retailers) -> list:
        return [(city, retailer) for city in cities for retailer in retailers]

    def _get_percentage(self, current: int, total: int) -> str:
        return str(round(current/total*100, 2)) + '%'

    def _store_to_dict(self, store) -> dict:
        categories = []

        if store.categories:
            for category in store.categories:
                children = []

                if category.children:
                    for child in category.children:
                        children.append({
                            'title': child.title,
                            'url': child.url
                        })

                categories.append({
                    'title': category.title,
                    'url': category.url,
                    'children': children
                })

        return {
            'title': store.title,
            'sid': store.sid,
            'address': store.address,
            'url': store.url,
            'categories': categories
        }

    def save_to_json(self, stores):
        stores = [self._store_to_dict(store) for store in stores]

        data = {
            'data': stores
        }

        date = datetime.datetime.now().strftime('%H-%M-%Y-%m-%d')

        path = os.path.join(TEMP, f'sber-{date}.json')

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f'[+] File saved. Path: {path}.')
