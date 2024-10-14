from typing import Annotated

from litestar import Litestar, get
from litestar.exceptions import HTTPException
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.openapi.spec import Example, Contact
from litestar.params import Parameter
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
import uvicorn

from src.rates import RatesService, CurrencyNotFoundError

service = RatesService()

@get(
    path="/v1/api/rates",
    description="Converts a specified value from one currency to another using current exchange rates. The response "
                "returns the converted amount."
)
async def get_rates(
    from_currency: Annotated[
        str,
        Parameter(
            title="From Currency",
            description="The currency to convert from",
            min_length=3,
            max_length=4,
            examples=[Example(value="USD")],
        ),
    ],
    to_currency: Annotated[
        str,
        Parameter(
            title="To Currency",
            description="The currency to convert to",
            min_length=3,
            max_length=4,
            examples=[Example(value="RUB")],
        ),
    ],
    value: Annotated[
        float,
        Parameter(
            title="Amount",
            description="The amount to convert",
            gt=0,
            examples=[Example(value=100.0)],
        ),
    ] = 1
) -> dict:

    try:
        result = service.convert(from_currency.upper(), to_currency.upper(), value)
        return {"result": result}
    except CurrencyNotFoundError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred. Please check the logs for more information."
        )


ROUTERS = [
    get_rates,
]

app = Litestar(
    [*ROUTERS],
    openapi_config=OpenAPIConfig(
        title="Rates API",
        description="""
        This API provides real-time exchange rates and conversion capabilities for both traditional currencies and most popular cryptocurrencies. 
        It allows users to convert amounts between different currencies and cryptocurrencies using up-to-date exchange rates.

        Features:
        - Get current exchange rates for various currency and cryptocurrency pairs
        - Convert amounts between different currencies and cryptocurrencies
        - Support for major global currencies and popular cryptocurrencies
        - Real-time data from multiple reliable sources

        Usage:
        - Use the /v1/api/rates endpoint to perform currency and cryptocurrency conversions
        - Specify the source currency/crypto, target currency/crypto, and amount to convert
        - Use standard 3-letter codes for traditional currencies (e.g., USD, EUR, JPY)
        - Use common symbols or tickers for cryptocurrencies (e.g., BTC, ETH, USDT)

        Note: Exchange rates are updated in real-time to ensure accuracy for both traditional and crypto markets.

        Examples:
        - Convert USD to EUR: /v1/api/rates?from_currency=USD&to_currency=EUR&value=100
        - Convert BTC to USD: /v1/api/rates?from_currency=BTC&to_currency=USD&value=1
        - Convert ETH to JPY: /v1/api/rates?from_currency=ETH&to_currency=JPY&value=2.5
        """,
        contact=Contact(
            name="API Support",
            url="https://t.me/imelbow",
            email="lokdeaf@gmail.com"
        ),
        version="v1",
        render_plugins=[SwaggerRenderPlugin()],

    )
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
