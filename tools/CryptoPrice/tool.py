from __future__ import annotations
from .manifest import ToolManifest
import aiohttp
import discord
import logging


class Tool(ToolManifest):
    """Tool to fetch live price for any Solana token using Jupiter price oracle.

    Logic:
    1. Map user-provided symbol (e.g. "BONK") to mint address using the Jupiter token list.
       The list is cached per-process to avoid repeated downloads.
    2. Query Jupiter price endpoint (v4, fallback v1) with the mint address.
    3. Gracefully fall back to CoinGecko simple price for SOL if Jupiter unavailable.
    """

    JUP_PRICE_V4 = "https://price.jup.ag/v4/price?ids={ids}"
    JUP_PRICE_V1 = "https://price.jup.ag/v1/price?id={id}"
    JUP_TOKENLIST = "https://token.jup.ag/all"
    COINGECKO_SOL = (
        "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    )

    # cache across instances
    _token_map: dict[str, str] | None = None  # symbol -> mint address

    def __init__(self, method_send, discord_ctx, discord_bot):
        super().__init__()
        self.method_send = method_send
        self.discord_ctx = discord_ctx
        self.discord_bot = discord_bot

    # ---------------------------------------------------------
    async def _ensure_token_map(self, session: aiohttp.ClientSession):
        if Tool._token_map is not None:
            return
        try:
            async with session.get(self.JUP_TOKENLIST, timeout=10) as resp:
                resp.raise_for_status()
                tokens = await resp.json()
        except aiohttp.ClientError as e:
            logging.warning("Failed to fetch Jupiter token list: %s", e)
            Tool._token_map = {}
            return

        mapping: dict[str, str] = {}
        for t in tokens:
            if symbol := t.get("symbol"):
                mapping[symbol.upper()] = t["address"]
        Tool._token_map = mapping

    # ---------------------------------------------------------
    async def _fetch_price_from_jupiter(
        self, session: aiohttp.ClientSession, mint_or_symbol: str
    ) -> tuple[str, float] | None:
        token_id = mint_or_symbol

        # Try v4
        for url_tmpl in (self.JUP_PRICE_V4, self.JUP_PRICE_V1):
            url = url_tmpl.format(ids=token_id, id=token_id)
            try:
                async with session.get(url, timeout=10) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            except aiohttp.ClientError:
                continue

            # Normalize response structures
            if "data" in data:  # v4
                key = next(iter(data["data"]))
                pinfo = data["data"][key]
                return pinfo.get("mintSymbol", key), float(pinfo["price"])
            elif "price" in data:  # v1
                return mint_or_symbol.upper(), float(data["price"])

        return None

    # ---------------------------------------------------------
    async def _tool_function_get_token_price(self, token: str):
        token = token.strip()
        if not token:
            raise ValueError("token parameter cannot be empty")
        token_upper = token.upper()

        if not hasattr(self.discord_bot, "_aiohttp_main_client_session"):
            raise Exception(
                "aiohttp client session is not initialized; cannot perform HTTP requests."
            )

        session: aiohttp.ClientSession = self.discord_bot._aiohttp_main_client_session

        # Load token map
        await self._ensure_token_map(session)

        mint_addr = token  # assume user provided address
        if len(token) <= 11:  # likely a symbol (short string)
            mint_addr = Tool._token_map.get(token_upper, None)
            if mint_addr is None and token_upper != "SOL":
                raise Exception(
                    "Unrecognized token symbol; please provide a Solana mint address instead."
                )

        # Fetch from Jupiter
        result = await self._fetch_price_from_jupiter(session, mint_addr)
        if result is None:
            # Fallback for SOL via CoinGecko (Jupiter might be down)
            if token_upper == "SOL":
                try:
                    async with session.get(self.COINGECKO_SOL, timeout=10) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        price = data["solana"]["usd"]
                        symbol = "SOL"
                except aiohttp.ClientError as e:
                    raise Exception(f"Failed to fetch price data: {e}")
            else:
                raise Exception("Failed to fetch price from Jupiter.")
        else:
            symbol, price = result

        await self.method_send(
            f"💰 Current {symbol} price: **${price:,.6f} USD** (via Jupiter)"
        )
        return {"symbol": symbol, "price_usd": price}
