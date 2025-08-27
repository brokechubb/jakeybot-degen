class ToolManifest:
    tool_human_name = "Cryptocurrency Price"
    token_price_description = "Fetch the current trading price of any cryptocurrency (by symbol or CoinMarketCap ID) using CoinMarketCap API."

    def __init__(self):
        _schema = {
            "name": "get_token_price",
            "description": self.token_price_description,
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g. 'BTC', 'ETH', 'SOL') or CoinMarketCap ID.",
                    }
                },
                "required": ["token"],
            },
        }

        self.tool_schema = [_schema]
        self.tool_schema_openai = [{"type": "function", "function": _schema}]
