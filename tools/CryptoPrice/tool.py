from __future__ import annotations
from .manifest import ToolManifest
import aiohttp
import discord
import logging
from os import environ


class Tool(ToolManifest):
    """Tool to fetch live price for any cryptocurrency using CoinMarketCap API.

    Logic:
    1. Get CoinMarketCap API key from environment variables
    2. Query CoinMarketCap API v2/cryptocurrency/quotes/latest endpoint
    3. Support both cryptocurrency symbols and CoinMarketCap IDs
    4. Return formatted price information with additional market data
    """

    CMC_QUOTES_LATEST = (
        "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    )
    CMC_ID_MAP = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"

    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()
        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot

    async def _tool_function_get_token_price(self, token: str):
        """Fetch the current price of a cryptocurrency token."""
        token = token.strip()
        if not token:
            raise ValueError("token parameter cannot be empty")

        # Get API key from environment
        api_key = environ.get("COINMARKETCAP_API_KEY")
        if not api_key:
            error_msg = "❌ COINMARKETCAP_API_KEY not set in environment variables. Please configure your API key in dev.env"
            await self.method_send(error_msg)
            raise Exception("COINMARKETCAP_API_KEY not set in environment variables")

        # Check if aiohttp session is available
        if not hasattr(self.discord_bot, "_aiohttp_main_client_session"):
            error_msg = "❌ HTTP client session not initialized. Please contact the bot administrator."
            await self.method_send(error_msg)
            raise Exception(
                "aiohttp client session is not initialized; cannot perform HTTP requests."
            )

        session: aiohttp.ClientSession = self.discord_bot._aiohttp_main_client_session

        # Determine if token is a symbol or ID
        is_numeric = token.isdigit()

        # Prepare API request parameters
        params = {}
        if is_numeric:
            params["id"] = token
        else:
            params["symbol"] = token.upper()

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key,
        }

        try:
            # Fetch price data from CoinMarketCap
            async with session.get(
                self.CMC_QUOTES_LATEST, params=params, headers=headers, timeout=10
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

            # Parse response
            if "data" not in data:
                error_msg = "❌ Invalid response from CoinMarketCap API. Please try again later."
                await self.method_send(error_msg)
                raise Exception("Invalid response from CoinMarketCap API")

            # Handle symbol vs ID response structure
            crypto_data = None
            if is_numeric:
                if token in data["data"]:
                    crypto_data = data["data"][token]
                else:
                    error_msg = f"❌ Cryptocurrency with ID {token} not found. Please check the ID and try again."
                    await self.method_send(error_msg)
                    raise Exception(f"Cryptocurrency with ID {token} not found")
            else:
                token_upper = token.upper()
                if token_upper in data["data"]:
                    # Handle case where multiple coins might have the same symbol
                    crypto_list = data["data"][token_upper]
                    if isinstance(crypto_list, list) and len(crypto_list) > 0:
                        crypto_data = crypto_list[0]  # Get first match
                    elif isinstance(crypto_list, dict):
                        crypto_data = crypto_list
                    else:
                        error_msg = f"❌ Cryptocurrency {token_upper} not found. Please check the symbol and try again."
                        await self.method_send(error_msg)
                        raise Exception(f"Cryptocurrency {token_upper} not found")
                else:
                    error_msg = f"❌ Cryptocurrency {token_upper} not found. Please check the symbol and try again."
                    await self.method_send(error_msg)
                    raise Exception(f"Cryptocurrency {token_upper} not found")

            if not crypto_data:
                error_msg = (
                    f"❌ Failed to fetch data for {token}. Please try again later."
                )
                await self.method_send(error_msg)
                raise Exception(f"Failed to fetch data for {token}")

            # Extract price and market data
            symbol = crypto_data.get("symbol", token.upper())
            name = crypto_data.get("name", "Unknown")

            # Get USD quote data
            quote = crypto_data.get("quote", {}).get("USD", {})
            if not quote:
                error_msg = "❌ No USD price data available for this cryptocurrency."
                await self.method_send(error_msg)
                raise Exception("No USD price data available")

            price = quote.get("price")
            if price is None:
                error_msg = "❌ Price data not available for this cryptocurrency."
                await self.method_send(error_msg)
                raise Exception("Price data not available")

            # Get additional market data
            market_cap = quote.get("market_cap")
            volume_24h = quote.get("volume_24h")
            percent_change_1h = quote.get("percent_change_1h")
            percent_change_24h = quote.get("percent_change_24h")
            percent_change_7d = quote.get("percent_change_7d")

            # Format the response message
            price_formatted = f"${price:,.6f}" if price < 1 else f"${price:,.2f}"

            message = f"💰 Current {name} ({symbol}) price: **{price_formatted} USD** (via CoinMarketCap)"

            # Add additional market data if available
            if market_cap is not None:
                market_cap_formatted = (
                    f"${market_cap:,.0f}" if market_cap >= 1 else f"${market_cap:.6f}"
                )
                message += f"\n📊 Market Cap: {market_cap_formatted}"

            if volume_24h is not None:
                volume_formatted = (
                    f"${volume_24h:,.0f}" if volume_24h >= 1 else f"${volume_24h:.2f}"
                )
                message += f"\n📈 24h Volume: {volume_formatted}"

            if percent_change_1h is not None:
                emoji = "🟢" if percent_change_1h >= 0 else "🔴"
                message += f"\n{emoji} 1h Change: {percent_change_1h:+.2f}%"

            if percent_change_24h is not None:
                emoji = "🟢" if percent_change_24h >= 0 else "🔴"
                message += f"\n{emoji} 24h Change: {percent_change_24h:+.2f}%"

            if percent_change_7d is not None:
                emoji = "🟢" if percent_change_7d >= 0 else "🔴"
                message += f"\n{emoji} 7d Change: {percent_change_7d:+.2f}%"

            await self.method_send(message)
            return {"symbol": symbol, "name": name, "price_usd": price, "quote": quote}

        except aiohttp.ClientError as e:
            error_msg = f"❌ Failed to fetch price data from CoinMarketCap: {str(e)}. Please try again later."
            await self.method_send(error_msg)
            logging.error(f"CoinMarketCap API request failed: {e}")
            raise Exception(f"Failed to fetch price data from CoinMarketCap: {e}")
        except Exception as e:
            error_msg = f"❌ Error processing cryptocurrency price data: {str(e)}"
            await self.method_send(error_msg)
            logging.error(f"Error processing CoinMarketCap response: {e}")
            raise Exception(f"Error processing cryptocurrency price data: {e}")

    async def _tool_function(self, token: str):
        """Legacy function name for backward compatibility."""
        return await self._tool_function_get_token_price(token)
