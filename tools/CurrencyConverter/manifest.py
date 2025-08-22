class ToolManifest:
    tool_human_name = "Currency Converter"
    currency_conversion_description = "Convert between different currencies using live exchange rates from a reliable API."

    def __init__(self):
        _schema = {
            "name": "convert_currency",
            "description": self.currency_conversion_description,
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The amount to convert (e.g., 1000, 50.5)",
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "The source currency code (e.g., 'ARS', 'USD', 'EUR', 'GBP')",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "The target currency code (e.g., 'USD', 'ARS', 'EUR', 'GBP')",
                    },
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        }

        self.tool_schema = [_schema]
        self.tool_schema_openai = [{"type": "function", "function": _schema}]
