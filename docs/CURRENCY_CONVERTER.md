# 💱 CurrencyConverter Tool

## Overview

The **CurrencyConverter** tool allows JakeyBot to convert between different currencies using live exchange rates. This tool provides reliable, real-time currency conversion for over 170 currencies worldwide.

## ✨ Features

- **Live Exchange Rates**: Real-time conversion rates updated frequently
- **170+ Currencies**: Support for major and minor world currencies
- **No API Key Required**: Uses free tier of ExchangeRate-API
- **Smart Formatting**: Automatic number formatting based on currency type
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## 🚀 Usage

### Enabling the Tool

To use the CurrencyConverter tool, enable it with the `/feature` command:

```
/feature CurrencyConverter
```

### How It Works

The tool automatically detects when you ask for currency conversion and calls the appropriate function. You can ask questions like:

- "Convert 1000 ARS to USD"
- "What's 50 EUR in GBP?"
- "How much is 1000 USD worth in ARS?"

### Supported Currencies

The tool supports all major currencies including:

- **Americas**: USD, ARS, CAD, BRL, MXN
- **Europe**: EUR, GBP, CHF, SEK, NOK, DKK, PLN
- **Asia**: JPY, CNY, KRW, INR, RUB, TRY
- **Oceania**: AUD, NZD
- **Africa**: ZAR, EGP, NGN

## 🔧 Technical Details

### API Provider

- **Service**: ExchangeRate-API (<https://exchangerate-api.com/>)
- **Rate Limits**: 1000 requests/month (free tier)
- **Update Frequency**: Real-time
- **Reliability**: High uptime with fallback handling

### Implementation

The tool follows JakeyBot's standard tool architecture:

```
tools/CurrencyConverter/
├── __init__.py          # Tool initialization
├── manifest.py          # Tool schema and metadata
└── tool.py             # Main implementation
```

### Function Schema

```json
{
  "name": "convert_currency",
  "description": "Convert between different currencies using live exchange rates",
  "parameters": {
    "type": "object",
    "properties": {
      "amount": {
        "type": "number",
        "description": "The amount to convert"
      },
      "from_currency": {
        "type": "string", 
        "description": "Source currency code (e.g., 'ARS', 'USD')"
      },
      "to_currency": {
        "type": "string",
        "description": "Target currency code (e.g., 'USD', 'EUR')"
      }
    },
    "required": ["amount", "from_currency", "to_currency"]
  }
}
```

## 📊 Example Responses

### Successful Conversion

```
💱 Currency Conversion
10,000 ARS (Argentine Peso) = 11.00 USD (US Dollar)
💹 Exchange Rate: 1 ARS = 0.001100 USD
```

### Error Handling

```
❌ Conversion failed: Currency XXX not found in exchange rates
```

## 🔗 Integration

The CurrencyConverter tool is automatically discovered by JakeyBot's tool system and integrates seamlessly with:

- **All AI Models**: Works with Gemini, OpenAI, Claude, and other supported models
- **Chat History**: Maintains context within conversations
- **Tool Management**: Can be enabled/disabled via `/feature` command
- **Default Configuration**: Can be set as default tool via environment variables

## 🛠️ Management & Monitoring

### Tool Status

Check the tool's status and configuration:

```bash
# View all tools status
python scripts/manage_tools.py

# Check specific tool status
python scripts/manage_tools.py status CurrencyConverter
```

### Set as Default Tool

Make CurrencyConverter the default tool for new users:

```bash
# Set as default tool
python scripts/set_default_tool.py CurrencyConverter

# Or set in environment
DEFAULT_TOOL=CurrencyConverter
```

### Tool Health Check

Verify the tool is working correctly:

```bash
# Check tool files and configuration
python scripts/manage_tools.py status CurrencyConverter
```

## 🚨 Troubleshooting

### Common Issues

1. **Tool Not Available**: Ensure you've enabled it with `/feature CurrencyConverter`
2. **API Errors**: The tool includes fallback handling for API failures
3. **Unsupported Currency**: Check that both currencies are valid 3-letter codes

### Performance

- **Response Time**: Typically 1-3 seconds for live rates
- **Caching**: Exchange rates are fetched fresh for each request
- **Reliability**: 99%+ uptime with graceful error handling

## 🔮 Future Enhancements

Potential improvements for future versions:

- **Historical Rates**: Access to historical exchange rate data
- **Currency Charts**: Visual representation of rate trends
- **Batch Conversion**: Convert multiple amounts simultaneously
- **Custom Rate Alerts**: Notifications for target exchange rates

## 📚 Additional Resources

### Related Documentation

- **Tools Overview**: `docs/TOOLS.md`
- **Configuration Guide**: `docs/CONFIG.md`
- **Scripts Documentation**: `scripts/README.md`

### Management Scripts

- **Tool Management**: `python scripts/manage_tools.py`
- **Default Tool Setting**: `python scripts/set_default_tool.py CurrencyConverter`
- **Security Check**: `python scripts/security_check.py`

## 🆘 Support

For issues with the CurrencyConverter tool:

1. Check that the tool is properly enabled
2. Verify your internet connection
3. Try a different currency pair
4. Use the management scripts to diagnose issues
5. Contact bot administrators if problems persist

---

*Last updated: January 2025*
