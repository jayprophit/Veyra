# Wealth Domains

Veyra should model wealth beyond listed securities, but each domain must preserve its own valuation rules, liquidity, risk, and legal context.

| Domain | Examples | Main Data Concerns |
| --- | --- | --- |
| Public markets | equities, ETFs, bonds, options | market feeds, corporate actions, market calendars |
| Physical metals | gold, silver, copper, palladium | spot price, storage, purity, dealer spreads |
| Agriculture | crops, farmland, livestock, food supply | seasonality, weather, yield, logistics |
| Property | land, houses, rentals, commercial assets | appraisals, debt, tax, maintenance, vacancies |
| Private business | operating companies, holding companies | cashflow, ownership, liabilities, concentration |
| Digital income | software, content, products, services | platform dependence, churn, margin, IP |
| Cashflow | wages, dividends, royalties, subscriptions | recurrence, reliability, taxation |

## Design Rule

Use one portfolio view, not one raw schema. Each domain needs its own ingest contract and then maps into shared reporting concepts such as value, cost basis, income, risk, and liquidity.

## First Useful Deliverables

- asset registry
- valuation timestamps
- source provenance
- liquidity score
- recurring-income model
- exposure rollups by domain, currency, geography, and ownership vehicle
