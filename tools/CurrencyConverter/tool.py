from __future__ import annotations
from .manifest import ToolManifest
import aiohttp
import discord
import logging
import json


class Tool(ToolManifest):
    """Tool to convert between different currencies using live exchange rates.

    Uses the ExchangeRate-API (https://exchangerate-api.com/) which provides:
    - Free tier with 1000 requests/month
    - Real-time exchange rates
    - Support for 170+ currencies
    - No API key required for basic usage
    """

    EXCHANGE_RATE_API_BASE = "https://open.er-api.com/v6/latest"

    # Common currency codes for better user experience
    COMMON_CURRENCIES = {
        "USD": "US Dollar",
        "EUR": "Euro",
        "GBP": "British Pound",
        "JPY": "Japanese Yen",
        "ARS": "Argentine Peso",
        "CAD": "Canadian Dollar",
        "AUD": "Australian Dollar",
        "CHF": "Swiss Franc",
        "CNY": "Chinese Yuan",
        "INR": "Indian Rupee",
        "BRL": "Brazilian Real",
        "MXN": "Mexican Peso",
        "KRW": "South Korean Won",
        "RUB": "Russian Ruble",
        "TRY": "Turkish Lira",
        "ZAR": "South African Rand",
        "SEK": "Swedish Krona",
        "NOK": "Norwegian Krone",
        "DKK": "Danish Krone",
        "PLN": "Polish Zloty",
    }

    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()
        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot

    async def _fetch_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Fetch the current exchange rate between two currencies."""
        if not hasattr(self.discord_bot, "_aiohttp_main_client_session"):
            raise Exception(
                "aiohttp client session is not initialized; cannot perform HTTP requests."
            )

        session: aiohttp.ClientSession = self.discord_bot._aiohttp_main_client_session

        # Normalize currency codes
        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()

        # If same currency, return 1.0
        if from_currency == to_currency:
            return 1.0

        try:
            # Use the free ExchangeRate-API
            url = f"{self.EXCHANGE_RATE_API_BASE}/{from_currency}"

            async with session.get(url, timeout=10) as resp:
                resp.raise_for_status()
                data = await resp.json()

                if data.get("result") == "success":
                    rates = data.get("rates", {})
                    if to_currency in rates:
                        return rates[to_currency]
                    else:
                        raise Exception(
                            f"Currency {to_currency} not found in exchange rates"
                        )
                else:
                    raise Exception(
                        f"API error: {data.get('error-type', 'Unknown error')}"
                    )

        except aiohttp.ClientError as e:
            logging.error(f"Failed to fetch exchange rate: {e}")
            raise Exception(f"Failed to fetch exchange rate: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse API response: {e}")
            raise Exception("Failed to parse exchange rate data")
        except Exception as e:
            logging.error(f"Unexpected error fetching exchange rate: {e}")
            raise Exception(f"Unexpected error: {e}")

    async def _tool_function_convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ):
        """Convert an amount from one currency to another."""
        try:
            # Validate inputs
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")

            if not from_currency or not to_currency:
                raise ValueError("Both from_currency and to_currency are required")

            # Normalize currency codes
            from_currency = from_currency.upper().strip()
            to_currency = to_currency.upper().strip()

            # Get exchange rate
            exchange_rate = await self._fetch_exchange_rate(from_currency, to_currency)

            # Calculate converted amount
            converted_amount = amount * exchange_rate

            # Format the response
            from_currency_name = self.COMMON_CURRENCIES.get(
                from_currency, from_currency
            )
            to_currency_name = self.COMMON_CURRENCIES.get(to_currency, to_currency)

            # Format numbers based on currency (some currencies don't use decimals)
            if to_currency in ["JPY", "KRW", "ARS"]:
                formatted_amount = f"{converted_amount:,.0f}"
            else:
                formatted_amount = f"{converted_amount:,.2f}"

            if from_currency in ["JPY", "KRW", "ARS"]:
                formatted_input = f"{amount:,.0f}"
            else:
                formatted_input = f"{amount:,.2f}"

            message = (
                f"💱 **Currency Conversion**\n"
                f"**{formatted_input} {from_currency}** ({from_currency_name}) = "
                f"**{formatted_amount} {to_currency}** ({to_currency_name})\n"
                f"💹 Exchange Rate: 1 {from_currency} = {exchange_rate:.6f} {to_currency}"
            )

            await self.method_send(message)

            return {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "amount": amount,
                "converted_amount": converted_amount,
                "exchange_rate": exchange_rate,
            }

        except ValueError as e:
            error_msg = f"❌ Invalid input: {str(e)}"
            await self.method_send(error_msg)
            raise
        except Exception as e:
            error_msg = f"❌ Conversion failed: {str(e)}"
            await self.method_send(error_msg)
            raise
