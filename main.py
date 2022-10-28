from libs.sbermarket import SberMarket
from settings.user_config import CITIES

import asyncio


async def main():
    sber_market = SberMarket()

    retailers = await sber_market.gather_retailer_slugs()

    data = sber_market.get_parsing_data(CITIES, retailers)

    stores = []

    store_tasks = [sber_market.get_retailer_stores(inf, stores, len(data)) for inf in data]

    await asyncio.wait(store_tasks)

    categories_tasks = [sber_market.get_store_categories(store, len(stores)) for store in stores]

    await asyncio.wait(categories_tasks)

    sber_market.save_to_json(stores)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
