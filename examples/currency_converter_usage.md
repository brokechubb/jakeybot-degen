# CurrencyConverter Tool Usage Examples

## Basic Usage

Once you've enabled the CurrencyConverter tool with `/feature CurrencyConverter`, you can ask JakeyBot to convert currencies in natural language:

### Simple Conversions

**User:** "Convert 1000 ARS to USD"
**JakeyBot:**

```
💱 Currency Conversion
1,000 ARS (Argentine Peso) = 1.10 USD (US Dollar)
💹 Exchange Rate: 1 ARS = 0.001100 USD
```

**User:** "What's 50 EUR worth in GBP?"
**JakeyBot:**

```
💱 Currency Conversion
50.00 EUR (Euro) = 43.10 GBP (British Pound)
💹 Exchange Rate: 1 EUR = 0.862000 GBP
```

### Different Amounts

**User:** "How much is 10000 USD in ARS?"
**JakeyBot:**

```
💱 Currency Conversion
10,000.00 USD (US Dollar) = 9,090,909 ARS (Argentine Peso)
💹 Exchange Rate: 1 USD = 909.090909 ARS
```

**User:** "Convert 2500 MXN to CAD"
**JakeyBot:**

```
💱 Currency Conversion
2,500.00 MXN (Mexican Peso) = 150.25 CAD (Canadian Dollar)
💹 Exchange Rate: 1 MXN = 0.060100 CAD
```

## Advanced Usage

### Multiple Conversions in One Chat

You can ask for multiple conversions in the same conversation:

**User:** "I have 1000 USD, 500 EUR, and 10000 ARS. How much is that in total USD?"
**JakeyBot:** (Will convert each currency and sum them up)

### Currency Code Variations

The tool accepts various currency code formats:

- **USD** or **usd** → US Dollar
- **ARS** or **ars** → Argentine Peso
- **EUR** or **eur** → Euro

### Natural Language Variations

The tool understands various ways to ask for conversions:

- "Convert X [currency] to [currency]"
- "What's X [currency] in [currency]?"
- "How much is X [currency] worth in [currency]?"
- "X [currency] to [currency]"
- "Change X [currency] to [currency]"

## Supported Currency Pairs

The tool supports conversion between any of these 170+ currencies:

### Major Currencies

- **USD** - US Dollar
- **EUR** - Euro  
- **GBP** - British Pound
- **JPY** - Japanese Yen
- **CAD** - Canadian Dollar
- **AUD** - Australian Dollar
- **CHF** - Swiss Franc

### Latin American Currencies

- **ARS** - Argentine Peso
- **BRL** - Brazilian Real
- **MXN** - Mexican Peso
- **CLP** - Chilean Peso
- **COP** - Colombian Peso
- **PEN** - Peruvian Sol

### Asian Currencies

- **CNY** - Chinese Yuan
- **KRW** - South Korean Won
- **INR** - Indian Rupee
- **SGD** - Singapore Dollar
- **THB** - Thai Baht
- **VND** - Vietnamese Dong

### And Many More

## Error Handling Examples

### Invalid Currency Code

**User:** "Convert 100 USD to XXX"
**JakeyBot:**

```
❌ Conversion failed: Currency XXX not found in exchange rates
```

### Invalid Amount

**User:** "Convert -50 EUR to USD"
**JakeyBot:**

```
❌ Invalid input: Amount must be greater than 0
```

### Network Issues

**User:** "Convert 100 USD to EUR" (when API is down)
**JakeyBot:**

```
❌ Conversion failed: Failed to fetch exchange rate: Connection timeout
```

## Tips for Best Results

1. **Use Standard Currency Codes**: Stick to 3-letter codes like USD, EUR, ARS
2. **Be Specific**: Include both the amount and both currencies
3. **Check Spelling**: Ensure currency codes are spelled correctly
4. **Reasonable Amounts**: Very large or very small amounts may have precision limits

## Integration with Other Tools

The CurrencyConverter tool works alongside other JakeyBot tools:

- **CryptoPrice**: Get crypto prices in different fiat currencies
- **CodeExecution**: Perform complex currency calculations
- **ExaSearch**: Research currency trends and economic data

---

*For more information, see the full [CurrencyConverter documentation](../docs/CURRENCY_CONVERTER.md)*
