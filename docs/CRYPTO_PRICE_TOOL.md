# Cryptocurrency Price Tool Documentation

## Overview
The CryptoPrice tool has been updated to use the CoinMarketCap API, providing access to price data for over 2.4 million cryptocurrencies and tokens across 790+ exchanges.

## Features
- Support for all major cryptocurrencies (Bitcoin, Ethereum, Solana, etc.)
- Access to 14 years of historical price data
- Real-time market data with 60-second update frequency
- Support for 93 fiat currency conversions
- Additional market metrics (market cap, volume, price changes)
- Support for both cryptocurrency symbols and CoinMarketCap IDs

## Setup

### 1. Get CoinMarketCap API Key
1. Visit [CoinMarketCap Pro API](https://pro.coinmarketcap.com/)
2. Sign up for a free account
3. Get your API key from the dashboard

### 2. Configure Environment Variable
Add your API key to your environment configuration:

```bash
# In your dev.env file
COINMARKETCAP_API_KEY=your_api_key_here
```

## Usage Examples

### Basic Usage
```
$crypto BTC
$crypto ETH
$crypto SOL
```

### Using CoinMarketCap IDs
```
$crypto 1    # Bitcoin
$crypto 1027 # Ethereum
$crypto 5426 # Solana
```

## Supported Cryptocurrencies
The tool supports any cryptocurrency listed on CoinMarketCap, including:
- Major cryptocurrencies (BTC, ETH, SOL, etc.)
- Altcoins and tokens
- Stablecoins
- DeFi tokens
- NFT-related tokens
- Exchange tokens

## Response Format
The tool provides comprehensive market information:
- Current price in USD
- Market capitalization
- 24-hour trading volume
- Price changes (1h, 24h, 7d)
- Visual indicators for price movements

## Rate Limits
- Free tier: 333 calls per day
- Cached data updates every 60 seconds
- Proper error handling for rate limit exceeded scenarios

## Error Handling
The tool handles various error scenarios:
- Invalid API key
- Network connectivity issues
- Invalid cryptocurrency symbols/IDs
- Rate limiting
- API service interruptions

## Troubleshooting
1. **API Key Issues**: Ensure `COINMARKETCAP_API_KEY` is properly set in your environment
2. **Invalid Symbol**: Try using the CoinMarketCap ID instead of symbol
3. **Rate Limiting**: Wait for the rate limit to reset (daily at UTC midnight for free tier)
4. **Network Issues**: Check your internet connection and firewall settings
