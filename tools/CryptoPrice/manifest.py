class ToolManifest:
    tool_human_name = "Solana Token Price"
    token_price_description = "Fetch the current trading price of any Solana token (by symbol or mint address) using Jupiter price oracle."

    def __init__(self):
        _schema = {
            "name": "get_token_price",
            "description": self.token_price_description,
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "Token symbol (e.g. 'SOL', 'BONK') or Solana mint address.",
                    }
                },
                "required": ["token"],
            },
        }

        self.tool_schema = [_schema]
        self.tool_schema_openai = [{"type": "function", "function": _schema}]
