# Financial Master API Documentation
## Complete REST API Reference

**Version:** 6.0.9  
**Base URL:** `http://localhost:8000`  
**Coverage:** 99%+ DeepSeek Match

---

## TABLE OF CONTENTS

1. [Authentication](#authentication)
2. [Core Trading API](#core-trading-api)
3. [DeFi & Web3 API](#defi--web3-api)
4. [Tax & Compliance API](#tax--compliance-api)
5. [Tax Identifiers API](#tax-identifiers-api)
6. [Multi-Jurisdiction API](#multi-jurisdiction-api)
7. [Debt Management API](#debt-management-api)
8. [Scoring Systems API](#scoring-systems-api)
9. [Expense & Budget API](#expense--budget-api)
10. [Employment & Income API](#employment--income-api)
11. [Comprehensive Wealth API](#comprehensive-wealth-api)
12. [Error Handling](#error-handling)

---

## AUTHENTICATION

All API endpoints require authentication using Bearer tokens.

### Headers
```
Authorization: Bearer {your_token}
Content-Type: application/json
```

### Test Token
For development: `test-token`

---

## CORE TRADING API

### Market Data

#### Get Quote
```http
GET /api/v1/market/quote/{symbol}
```

**Response:**
```json
{
  "symbol": "BTC-USD",
  "price": 43250.50,
  "change_24h": 2.5,
  "volume": 1500000000,
  "timestamp": "2026-04-26T12:00:00Z"
}
```

#### Get Order Book
```http
GET /api/v1/market/orderbook/{symbol}
```

### Trading

#### Place Order
```http
POST /api/v1/order
```

**Request Body:**
```json
{
  "symbol": "BTC-USD",
  "side": "buy",
  "quantity": 0.5,
  "order_type": "market",
  "broker": "binance"
}
```

**Response:**
```json
{
  "order_id": "ord_123456",
  "status": "filled",
  "filled_quantity": 0.5,
  "average_price": 43250.50,
  "total_cost": 21625.25
}
```

#### Get Positions
```http
GET /api/v1/position
```

### Brokers

#### Connect Broker
```http
POST /api/v1/broker/{broker}/connect
```

**Supported Brokers:**
- `pionex` - 16 free trading bots
- `binance` - Spot & futures
- `ibkr` - Interactive Brokers
- `mt5` - MetaTrader 5

---

## DEFI & WEB3 API

### DEX Trading

#### Get DEX Quote
```http
GET /true-gaps/dex/price?chain=ethereum&token_in=ETH&token_out=USDC&amount=1.0
```

#### Execute Swap
```http
POST /true-gaps/dex/swap
```

**Request:**
```json
{
  "chain": "ethereum",
  "dex": "uniswap_v3",
  "token_in": "ETH",
  "token_out": "USDC",
  "amount": 1.0,
  "slippage": 0.5
}
```

### Layer 2

#### Deposit to L2
```http
POST /true-gaps/l2/deposit
```

**Request:**
```json
{
  "from_chain": "ethereum",
  "to_chain": "arbitrum",
  "token": "ETH",
  "amount": 0.5
}
```

### Cross-Chain Bridges

#### Get Bridge Quote
```http
GET /true-gaps/bridge/quote?source=ethereum&destination=polygon&token=USDC&amount=1000
```

#### Execute Bridge Transfer
```http
POST /true-gaps/bridge/execute
```

### NFTs

#### Buy NFT (Cheapest)
```http
POST /true-gaps/nft/buy-cheapest
```

**Request:**
```json
{
  "collection": "0x...",
  "token_id": "1234",
  "max_price_eth": 1.5,
  "wallet": "0x..."
}
```

---

## TAX & COMPLIANCE API

### Tax Calculations

#### Calculate Tax
```http
POST /phase10/tax/calculate
```

**Request:**
```json
{
  "tax_year": 2026,
  "income": 45000,
  "capital_gains": 5000,
  "dividends": 2000
}
```

**Response:**
```json
{
  "total_tax_due": 8750.00,
  "breakdown": {
    "income_tax": 6500.00,
    "national_insurance": 2250.00,
    "capital_gains_tax": 0,
    "dividend_tax": 0
  },
  "effective_rate": 19.4
}
```

### ISA Management

#### Get ISA Status
```http
GET /phase10/isa/status
```

#### Contribute to ISA
```http
POST /phase10/isa/contribute
```

**Request:**
```json
{
  "amount": 500,
  "account": "stocks_shares_isa"
}
```

### LISA (Lifetime ISA)

#### Get LISA Bonus
```http
POST /phase10/lisa/bonus
```

**Response:**
```json
{
  "contribution": 4000,
  "government_bonus": 1000,
  "total": 5000
}
```

---

## DEBT MANAGEMENT API

### Track Debts

#### Add Debt
```http
POST /debt/add
```

**Request:**
```json
{
  "name": "Credit Card",
  "creditor": "Barclaycard",
  "debt_type": "credit_card",
  "original_balance": 5000,
  "current_balance": 3500,
  "interest_rate_annual": 19.9,
  "min_monthly_payment": 100
}
```

#### Get Payoff Plan
```http
GET /debt/payoff-plan/{strategy}
```

**Strategies:** `snowball`, `avalanche`

**Response:**
```json
{
  "strategy": "avalanche",
  "months_to_debt_free": 18,
  "total_interest_paid": 450.00,
  "payoff_order": ["Credit Card", "Personal Loan"],
  "completion_date": "2027-10-15"
}
```

#### Compare Strategies
```http
GET /debt/compare-strategies
```

---

## SCORING SYSTEMS API

### Credit Score

#### Add Credit Score
```http
POST /scoring/credit/add
```

**Request:**
```json
{
  "agency": "experian",
  "score": 850,
  "factors": {
    "payment_history": "excellent",
    "credit_utilization": 15
  }
}
```

#### Get Improvement Plan
```http
GET /scoring/credit/improvement-plan
```

### Fuel & Mileage

#### Record Trip
```http
POST /scoring/fuel/trip
```

**Request:**
```json
{
  "vehicle_id": "vehicle_1",
  "date": "2026-04-26",
  "start_location": "Home",
  "end_location": "Client Office",
  "distance_miles": 45,
  "trip_type": "business",
  "purpose": "Site visit"
}
```

#### Get HMRC Claim
```http
GET /scoring/fuel/hmrc-claim?tax_year=2026
```

**Response:**
```json
{
  "tax_year": "2026-2027",
  "total_business_miles": 2500,
  "total_claim_amount": 1125.00,
  "hmrc_approved": true
}
```

### Financial Behavior Score

#### Calculate Score
```http
POST /scoring/behavior/calculate
```

**Request:**
```json
{
  "savings_balance": 10000,
  "monthly_income": 2500,
  "savings_rate": 20,
  "savings_consistency_months": 6,
  "total_debt": 5000,
  "debt_to_income": 20,
  "on_time_payments": 12,
  "payoff_progress": 30,
  "dca_streak": 3,
  "under_budget_months": 4,
  "no_spend_streak": 7,
  "isa_contribution": 4000,
  "emergency_fund_months": 4
}
```

**Response:**
```json
{
  "overall_score": 78,
  "percentile": 82,
  "level": 7,
  "title": "Expert",
  "xp": 2450,
  "achievements": [
    {
      "name": "Savings Starter",
      "tier": "silver",
      "icon": "💎"
    }
  ],
  "next_goals": [
    "Increase savings rate to 25%",
    "Build 6-month emergency fund"
  ]
}
```

### Security Score

#### Add Account
```http
POST /scoring/security/account
```

**Request:**
```json
{
  "name": "Main Bank",
  "account_type": "bank",
  "has_2fa": true,
  "password_strength": "strong",
  "uses_password_manager": true
}
```

#### Get Security Checklist
```http
GET /scoring/security/checklist
```

---

## EXPENSE & BUDGET API

### Transactions

#### Add Transaction
```http
POST /expenses/transaction
```

**Request:**
```json
{
  "date": "2026-04-26",
  "amount": 45.50,
  "transaction_type": "expense",
  "category": "food",
  "description": "Weekly shop",
  "merchant": "Tesco",
  "payment_method": "card",
  "account": "main",
  "tags": ["groceries", "essentials"],
  "is_tax_deductible": false
}
```

#### List Transactions
```http
GET /expenses/transactions?start_date=2026-04-01&end_date=2026-04-30&category=food
```

### Budgets

#### Set Budget
```http
POST /expenses/budget
```

**Request:**
```json
{
  "category": "food",
  "amount": 200,
  "period": "monthly",
  "rollover": false,
  "alert_threshold": 0.8
}
```

### Budget Rules

#### List All Rules
```http
GET /expenses/budget-rules
```

#### Analyze Against Rule
```http
POST /expenses/budget-rules/analyze
```

**Request:**
```json
{
  "rule_type": "50_30_20",
  "income": 2500,
  "spending": {
    "needs": 1250,
    "wants": 750,
    "savings": 500
  }
}
```

**Response:**
```json
{
  "compliance_score": 100,
  "target_allocation": {"needs": 1250, "wants": 750, "savings": 500},
  "actual_spending": {"needs": 1250, "wants": 750, "savings": 500},
  "variance_percent": {"needs": 0, "wants": 0, "savings": 0},
  "years_to_financial_independence": 25,
  "recommendations": ["Perfect adherence to 50/30/20 rule!"]
}
```

#### Get Recommended Rule
```http
POST /expenses/budget-rules/recommend
```

**Request:**
```json
{
  "income": 2500,
  "age": 30,
  "has_debt": false,
  "family_size": 2,
  "lifestyle": "balanced",
  "discipline_level": "medium"
}
```

### Monthly Summary

#### Get Summary
```http
GET /expenses/summary/monthly/2026/4
```

**Response:**
```json
{
  "period": "2026-04",
  "income": {"total": 2555.00},
  "expenses": {
    "total": 1887.00,
    "essential": 1500.00,
    "discretionary": 387.00
  },
  "cash_flow": {
    "net": 668.00,
    "savings_rate": 26.1,
    "on_target": true
  },
  "rule_50_30_20": {
    "needs_actual": 58.7,
    "wants_actual": 15.1,
    "savings_actual": 26.1,
    "assessment": "Good - Minor adjustments needed"
  }
}
```

---

## EMPLOYMENT & INCOME API

### Income Sources

#### Add Income Source
```http
POST /expenses/income-source
```

**Request:**
```json
{
  "name": "ABC Ltd Contract",
  "employment_type": "contract",
  "employer_client": "ABC Ltd",
  "pay_frequency": "monthly",
  "tax_status": "ir35_inside",
  "day_rate": 400,
  "typical_days_per_month": 15,
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "includes_pension": false
}
```

**Employment Types:**
- `full_time`, `part_time`, `contract`, `freelance`
- `consultant`, `gig_economy`, `commission`, `zero_hours`
- `seasonal`, `temporary`, `casual`, `second_job`
- `side_hustle`, `investment_income`, `pension`, `benefits`

**Pay Frequencies:**
- `weekly`, `biweekly`, `four_weekly`, `monthly`, `bimonthly`
- `quarterly`, `annually`, `irregular`, `on_completion`, `milestone`

**Tax Statuses:**
- `paye` - Employer deducts tax
- `self_assessment` - You report tax
- `ir35_inside` - Deemed employee
- `ir35_outside` - Genuine contractor

#### Record Payment
```http
POST /expenses/income-payment
```

**Request:**
```json
{
  "source_id": "income_1",
  "date": "2026-04-26",
  "gross_amount": 6000,
  "tax_deducted": 1200,
  "ni_deducted": 300,
  "days_worked": 15,
  "description": "April contract payment"
}
```

#### Get Employment Types Reference
```http
GET /expenses/income/employment-types
```

#### Forecast Income
```http
GET /expenses/income/forecast?months=3
```

**Response:**
```json
{
  "forecast_period_months": 3,
  "forecasts": [
    {
      "source": "ABC Ltd Contract",
      "period": "2026-05",
      "predicted_gross": 6000,
      "predicted_net": 4500,
      "confidence": "high",
      "factors": ["Based on 6 historical payments"]
    }
  ],
  "total_predicted_monthly": 4500
}
```

#### Calculate Irregular Income Buffer
```http
GET /expenses/income/irregular-buffer/income_1?target_months=3
```

**Response:**
```json
{
  "target_months": 3,
  "monthly_expenses": 2000,
  "current_buffer": 4000,
  "target_buffer": 6000,
  "progress_percent": 66.7,
  "monthly_contribution_needed": 400,
  "months_until_fully_funded": 5,
  "status": "building"
}
```

---

## ERROR HANDLING

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid or missing token |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid budget rule type",
    "details": {
      "field": "rule_type",
      "provided": "invalid_rule",
      "valid_options": ["50_30_20", "90_10", "60_20_20"]
    }
  }
}
```

---

## RATE LIMITING

- 1000 requests per hour per API key
- 100 requests per minute for trading endpoints
- WebSocket connections: 10 concurrent per client

---

## WEBSOCKET API

### Real-time Market Data
```
ws://localhost:8000/ws/market
```

### Subscribe to Symbol
```json
{
  "action": "subscribe",
  "symbols": ["BTC-USD", "ETH-USD"]
}
```

---

## SDK & CLIENTS

### Python Client
```python
from financial_master import Client

client = Client(api_key="your_key")

# Get quote
quote = client.market.get_quote("BTC-USD")

# Add expense
client.expenses.add_transaction(
    amount=50.00,
    category="food",
    description="Groceries"
)
```

### JavaScript/TypeScript Client
```typescript
import { FinancialMasterClient } from '@financial-master/sdk';

const client = new FinancialMasterClient({ apiKey: 'your_key' });

// Analyze budget
const analysis = await client.budgetRules.analyze({
  ruleType: '50_30_20',
  income: 2500,
  spending: { needs: 1250, wants: 750, savings: 500 }
});
```

---

## EXAMPLES

### Complete Monthly Budget Flow

```bash
# 1. Set up income sources
POST /expenses/income-source
{
  "name": "Main Job",
  "employment_type": "full_time",
  "annual_salary": 35000
}

# 2. Set budgets for categories
POST /expenses/budget
{ "category": "food", "amount": 200 }

POST /expenses/budget
{ "category": "transport", "amount": 150 }

POST /expenses/budget
{ "category": "entertainment", "amount": 100 }

# 3. Track daily expenses
POST /expenses/transaction
{
  "date": "2026-04-26",
  "amount": 45.50,
  "category": "food",
  "description": "Tesco shop"
}

# 4. Check monthly progress
GET /expenses/summary/monthly/2026/4

# 5. Get budget recommendations
POST /expenses/budget-rules/recommend
{
  "income": 2555,
  "age": 30,
  "has_debt": false,
  "family_size": 2
}

# 6. Analyze against 50/30/20 rule
POST /expenses/budget-rules/analyze
{
  "rule_type": "50_30_20",
  "income": 2555,
  "spending": {
    "needs": 1500,
    "wants": 400,
    "savings": 655
  }
}
```

---

## TAX IDENTIFIERS API

### Overview
Manage all UK tax identifiers: UTR, VAT, NINO, PAYE, Corporation Tax, and more.

### Add Tax Identifier
```http
POST /tax/identifiers/add
```

**Request:**
```json
{
  "identifier_type": "utr",
  "reference_number": "1234567890",
  "entity_name": "John Smith",
  "entity_type": "individual"
}
```

**Supported Types:**
- `utr` - Unique Taxpayer Reference (10 digits)
- `nino` - National Insurance Number (AB123456C)
- `vat_number` - VAT Registration (GB123456789)
- `paye_reference` - Employer PAYE Reference
- `ct_utr` - Corporation Tax UTR
- `gateway_id` - Government Gateway ID
- And 12 more...

### Validate Identifier
```http
GET /tax/identifiers/validate/{type}?value={number}
```

**Example:**
```http
GET /tax/identifiers/validate/utr?value=1234567890
```

**Response:**
```json
{
  "identifier_type": "utr",
  "value": "1234567890",
  "valid": true,
  "format": "10 digits (e.g., 1234567890)"
}
```

### VAT Registration
```http
POST /tax/identifiers/vat/registration
```

**Request:**
```json
{
  "vat_number": "GB123456789",
  "scheme": "standard",
  "flat_rate_percentage": null,
  "return_period": "quarterly"
}
```

### Self Assessment Records
```http
POST /tax/identifiers/sa/record
```

**Request:**
```json
{
  "utr": "1234567890",
  "current_tax_year": 2026,
  "tax_calculated": 5000.00,
  "tax_paid": 2000.00
}
```

### Compliance Summary
```http
GET /tax/identifiers/compliance
```

**Response:**
```json
{
  "vat_registrations": 1,
  "sa_accounts": 1,
  "paye_schemes": 1,
  "ct_accounts": 0,
  "upcoming_deadlines": [...],
  "outstanding_payments": [...],
  "total_outstanding": 3000.00
}
```

---

## MULTI-JURISDICTION API

### Overview
Track tax, investments, and compliance across 32 jurisdictions globally.

### List Jurisdictions
```http
GET /jurisdiction/list
```

**Supported Regions:**
- **UK:** England, Scotland, Wales, Northern Ireland
- **Europe:** Ireland, Germany, France, Netherlands, Switzerland, etc.
- **Americas:** USA, Canada, Brazil, Mexico
- **Asia-Pacific:** Australia, Singapore, Hong Kong, Japan, UAE
- **Offshore:** Cayman Islands, Bermuda, BVI, Jersey, Guernsey

### Get Tax Rules
```http
GET /jurisdiction/rules/{jurisdiction}
```

**Example:** `GET /jurisdiction/rules/uk_england`

**Response includes:**
- Personal tax bands and allowances
- Corporate tax rates
- VAT/GST rates
- Social security rates
- Wealth and inheritance taxes
- Currency and tax year dates

### Compare Tax Across Jurisdictions
```http
POST /jurisdiction/tax/compare
```

**Request:**
```json
{
  "jurisdictions": ["uk_england", "usa", "singapore"],
  "income": 100000,
  "income_type": "employment"
}
```

**Response:**
```json
{
  "income": 100000,
  "comparisons": [
    {"jurisdiction": "singapore", "total_tax": 5650, "effective_rate": 5.7},
    {"jurisdiction": "usa", "total_tax": 18021, "effective_rate": 18.0},
    {"jurisdiction": "uk_england", "total_tax": 26428, "effective_rate": 26.4}
  ],
  "most_favorable": "singapore"
}
```

### Cross-Border Investment Tracking
```http
POST /jurisdiction/investment/add
```

**Request:**
```json
{
  "asset_name": "Apple Inc",
  "asset_type": "stock",
  "investor_jurisdiction": "uk_england",
  "asset_jurisdiction": "usa",
  "acquisition_cost": 10000,
  "base_currency": "GBP",
  "local_currency": "USD"
}
```

**Auto-flags:**
- FATCA reportable (US investments)
- CRS reportable (OECD standard)

### FATCA/CRS Compliance
```http
GET /jurisdiction/compliance/fatca-crs
```

**Response:**
```json
{
  "fatca": {
    "reportable_accounts": 2,
    "total_value": 25000.00,
    "accounts": [...]
  },
  "crs": {
    "reportable_accounts": 3,
    "total_value": 45000.00,
    "accounts": [...]
  }
}
```

### Tax Treaty Information
```http
GET /jurisdiction/compliance/tax-treaties?residence=uk&source=usa
```

**Response:**
```json
{
  "residence": "uk",
  "source": "usa",
  "treaty_exists": true,
  "withholding_rates": {
    "dividends": 15,
    "interest": 0,
    "royalties": 0
  }
}
```

---

## COMPREHENSIVE WEALTH API

### Overview
Track ALL types of wealth, assets, income, and investment opportunities globally.

### Asset Classes Supported (22+)
```
Traditional:    Cash, Stocks, Bonds, ETFs
Real Assets:    Real Estate, Gold, Silver
Alternative:    Art, Wine, Classic Cars, Luxury Watches
Digital:        Crypto, NFTs, DeFi tokens
Private:        Private Equity, VC, Hedge Funds
Business:       Business Equity, IP, Patents, Franchises
Other:          P2P Lending, Commodities, Forex, Derivatives
```

### Income Types Supported (15+)
```
Active:         Salary, Bonus, Freelance, Consulting, Business Profit
Passive:        Dividends, Interest, Rent, Royalties
Digital:        Crypto Staking, DeFi Yield, P2P Interest
Retirement:     Pension Income, Annuities
```

### Get Asset Classes
```http
GET /wealth/asset-classes
```

### Add Wealth Holding
```http
POST /wealth/holding/add
```

**Request:**
```json
{
  "asset_class": "classic_cars",
  "name": "1967 Ford Mustang GT",
  "jurisdiction": "uk",
  "acquisition_cost": 85000,
  "current_value": 120000
}
```

**All Supported Asset Classes:**
- `cash` - Cash & Bank Accounts
- `stocks` - Individual Stocks
- `bonds` - Government & Corporate Bonds
- `etf` - Exchange Traded Funds
- `real_estate` - Property
- `precious_metals` - Gold, Silver
- `art` - Artwork & Collectibles
- `wine` - Fine Wine & Whisky
- `classic_cars` - Vintage Automobiles
- `watches` - Luxury Timepieces
- `crypto` - Cryptocurrencies
- `nft` - Non-Fungible Tokens
- `private_equity` - Private Company Shares
- `venture_capital` - Startup Investments
- `hedge_funds` - Alternative Funds
- `p2p_lending` - Peer-to-Peer Loans
- `business` - Business Equity
- `pension` - Retirement Accounts
- `commodities` - Oil, Gas, Agriculture
- `forex` - Foreign Exchange
- `derivatives` - Options, Futures, CFDs
- `intellectual_property` - Patents, Copyrights, Trademarks

### List Holdings
```http
GET /wealth/holdings/list?asset_class=crypto&jurisdiction=uk
```

### Add Income Stream
```http
POST /wealth/income/add-stream
```

**Request:**
```json
{
  "income_type": "crypto_staking",
  "source": "Ethereum Staking",
  "amount_monthly": 150,
  "is_passive": true,
  "jurisdiction": "international"
}
```

### Get Passive Income Summary
```http
GET /wealth/income/passive
```

**Response:**
```json
{
  "monthly_passive": 2500,
  "annual_passive": 30000,
  "breakdown": {
    "dividends": 800,
    "interest": 200,
    "rent": 1200,
    "crypto_staking": 150,
    "defi_yield": 100,
    "royalties": 50
  }
}
```

### Get Total Wealth Summary
```http
GET /wealth/total
```

**Response:**
```json
{
  "total_wealth_gbp": 1250000,
  "by_asset_class": {
    "real_estate": 500000,
    "stocks": 300000,
    "crypto": 100000,
    "bonds": 150000,
    "classic_cars": 120000,
    "art": 80000
  },
  "by_jurisdiction": {
    "uk": 850000,
    "usa": 250000,
    "eu": 150000
  },
  "passive_income": {
    "monthly": 2500,
    "annual": 30000
  },
  "fi_metrics": {
    "fi_number_4pct_rule": 50000,
    "annual_passive": 30000,
    "passive_coverage_pct": 60
  },
  "diversification": {
    "asset_classes": 6,
    "jurisdictions": 3,
    "foreign_exposure_pct": 32
  }
}
```

### Get Investment Opportunities
```http
GET /wealth/opportunities?passive_income_focus=true&jurisdiction=uk
```

**Response:**
```json
{
  "opportunities": [
    {
      "asset_class": "crypto",
      "name": "Ethereum Staking",
      "expected_yield": 4.5,
      "risk_level": "high",
      "passive": true
    },
    {
      "asset_class": "real_estate",
      "name": "UK REITs",
      "expected_yield": 5.0,
      "risk_level": "medium",
      "passive": true
    }
  ]
}
```

### Get International Summary
```http
GET /wealth/international/summary
```

---

## CHANGELOG

### v6.0.9 (Latest)
- Added Comprehensive Wealth Tracking (22+ asset classes, 15+ income types)
- Added alternative investments (art, wine, cars, watches, IP)
- Added digital asset income tracking (staking, DeFi, yield)
- Added investment opportunity discovery
- Added Financial Independence metrics (4% rule, passive coverage)

### v6.0.8
- Added Tax Identifiers tracking (19 types: UTR, VAT, NINO, PAYE, CT, etc.)
- Added Multi-Jurisdiction support (32 jurisdictions)
- Added cross-border investment tracking (FATCA/CRS)
- Added transfer pricing documentation
- Added FX exposure management

### v6.0.7
- Added Tax Identifiers module (UTR, VAT, NINO, PAYE, CT)
- Tax code calculations and validation
- HMRC compliance tracking

### v6.0.6
- Added Employment & Income Tracking (19 types)
- Added Budget Rules Engine (10 rules)
- Added Expense Tracker (25 categories)

### v6.0.5
- Added Security Score module
- Added Credit Score tracking
- Added Fuel & Mileage tracker
- Added Financial Behavior Scoring

### v6.0.0
- TRUE GAPS implementation
- MetaTrader 5 integration
- DEX connectors (Uniswap, Curve)
- Layer 2 networks (Arbitrum, Optimism)
- Cross-chain bridges
- NFT marketplaces

---

## SUPPORT

- **Documentation:** https://docs.financialmaster.io
- **API Status:** https://status.financialmaster.io
- **Support Email:** api-support@financialmaster.io
- **GitHub:** https://github.com/financialmaster/api

---

**© 2026 Financial Master. All rights reserved.**
