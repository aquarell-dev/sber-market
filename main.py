from libs.sbermarket import SberMarket


def main():
    sber_market = SberMarket()

    sber_market.open_map()

    sber_market.gather_store_links(['53', '28'])

if __name__ == '__main__':
    main()
