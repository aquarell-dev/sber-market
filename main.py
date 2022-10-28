from libs.sbermarket import SberMarket
import asyncio


async def main():
    sber_market = SberMarket()

    retailers = await sber_market.gather_retailer_slugs()

    cities = ['8']

    info = [(city, retailer) for city in cities for retailer in retailers]

    info = info[:50:]

    stores = []

    store_tasks = [sber_market.get_retailer_stores(inf, stores, len(info)) for inf in info]

    await asyncio.wait(store_tasks)

    categories_tasks = [sber_market.get_store_categories(store, len(stores)) for store in stores]

    await asyncio.wait(categories_tasks)

    sber_market.save_to_json(stores)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
