import urllib3
import threading
import time
import logging

from common.config import config


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CurrencyNotFoundError(Exception):
    pass

class RatesService:
    def __init__(self, update_interval=10*60):
        if not config:
            raise ValueError("Config not loaded or empty. Check configuration file or environment variables.")

        self.PLATFORMS = config.get('platforms', {})
        self.EXCHANGERS = config.get('exchangers', {})
        self.SYMBOLS = config.get('symbols', {})

        self.crypto_rates = {}
        self.fiat_rates = {}
        self.http = urllib3.PoolManager()
        self.update_interval = update_interval

        self.update_thread = threading.Thread(target=self._periodic_update, daemon=True)
        self.update_thread.start()

    def _periodic_update(self):
        while True:
            logger.info("Starting periodic update of rates")
            self.get_crypto_rates()
            self.get_fiat_rates()
            logger.info("Rates update completed")
            time.sleep(self.update_interval)

    def get_crypto_rates(self):
        currency_rates = {v: [] for k, v in self.SYMBOLS.items()}
        for platform, data in self.PLATFORMS.items():
            symbols = data['symbols']
            base_url = data['url']

            for symbol in symbols:
                url = base_url.format(symbol=symbol)
                response = self.http.request('GET', url)

                if response.status != 200:
                    logger.warning(f'Non-ok response: {response.status}', 'warning')
                else:
                    response_data = response.json()
                    last_price = -1.0

                    try:
                        if platform == 'Binance':
                            last_price = float(response_data['price'])
                        elif platform == 'Bybit':
                            symbol_data = response_data['result']['list'][0]
                            last_price = float(symbol_data['lastPrice'])
                        elif platform == 'BitFinex':
                            last_price = float(response_data[6])
                        elif platform == 'Solarpath':
                            last_price = float(response_data['result']['priceUsd'])

                        mapped_symbol = self.SYMBOLS.get(symbol, symbol)
                        currency_rates[mapped_symbol].append(last_price)

                    except Exception as e:
                        logger.error(f'Error occurred while fetching data for {platform} and {symbol}: {e}')
                        continue
        for currency, rates in currency_rates.items():
            self.crypto_rates[currency] = round(sum(rates) / len(rates), 6) if len(rates) != 0 else -1

        logger.info(self.crypto_rates)

    def get_fiat_rates(self):
        currency_rates = {}

        for exchanger, data in self.EXCHANGERS.items():
            url = data['url']
            response = self.http.request('GET', url)

            if response.status != 200:
                logger.warning(f'Non-ok response: {response.status}')
            else:
                response_data = response.json()
                try:
                    if exchanger == 'Openexchange':
                        rates = response_data['rates']

                    for currency, rate in rates.items():
                        if currency not in currency_rates:
                            currency_rates[currency] = []
                        currency_rates[currency].append(1 / rate)
                except Exception as e:
                    logger.error(f'Error occurred while fetching data for {exchanger} {e}')
                    continue

        for currency, rates in currency_rates.items():
            self.fiat_rates[currency] = round(sum(rates) / len(rates), 6) if len(rates) != 0 else -1
        logger.info(f"Loaded {len(self.fiat_rates)} fiat currencies")

    def convert(self, c_from, c_to, amount):
        amount = float(amount)
        usdt = self.crypto_rates['USDT']

        if c_from in self.crypto_rates:
            c_from_rate = self.crypto_rates[c_from] * usdt
        elif c_from in self.fiat_rates:
            c_from_rate = self.fiat_rates[c_from]
        else:
            logger.error(f'Currency {c_from} not found')
            raise CurrencyNotFoundError(f'Currency {c_from} not found')

        if c_to in self.crypto_rates:
            c_to_rate = self.crypto_rates[c_to] * usdt
        elif c_to in self.fiat_rates:
            c_to_rate = self.fiat_rates[c_to]
        else:
            logger.error(f'Currency {c_to} not found')
            raise CurrencyNotFoundError(f'Currency {c_to} not found')

        converted_amount = amount * c_from_rate / c_to_rate
        return round(converted_amount, 8)