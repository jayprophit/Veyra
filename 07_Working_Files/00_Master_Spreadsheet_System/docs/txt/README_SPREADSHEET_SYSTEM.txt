================================================================================
FINANCIAL MASTER SPREADSHEET & AI ENGINE SYSTEM
================================================================================
Version: 1.0 | Complete Data Extraction & Automation Framework
Location: c:\Users\jpowe\Desktop\Financial Master\07_Working_Files\00_Master_Spreadsheet_System\
================================================================================

SYSTEM OVERVIEW
--------------------------------------------------------------------------------
This folder contains the COMPLETE data extraction from the DeepSeek conversation
file, organized into customizable spreadsheets with formulas, plus a fully 
autonomous AI/ML engine for automation.

CONTENTS
--------------------------------------------------------------------------------

[CONFIGURATION FILES]
00_Master_System_Config.json          - Complete system configuration with all formulas
engine_config.json                    - AI engine configuration
system_config.json                    - Runtime configuration

[SPREADSHEETS - CSV FORMAT FOR EASY IMPORT]
01_Platform_Inventory_Master.csv      - All 39 trading/investing platforms with configs
02_Financial_Dashboard_Template.csv   - Main dashboard with all formulas
03_Debt_Paydown_Scheduler.csv         - Debt elimination schedule
04_Investment_Engine_Master.csv     - All 12 investment engines
05_Tax_Calculation_Engine.csv         - UK tax 2025/26 with formulas

[AI/ML PYTHON MODULES]
06_AI_Automation_Engine.py            - Core financial calculation engine
07_ML_Prediction_Model.py             - Price prediction & risk assessment
08_Data_Ingestion_Engine.py           - API connections for live data
09_Autonomous_Master_Controller.py    - Main autonomous orchestrator

================================================================================
HOW TO USE THE SPREADSHEETS
================================================================================

[GOOGLE SHEETS SETUP]
1. Go to sheets.google.com
2. Create new spreadsheet: "Financial_Command_Center"
3. Import each CSV as a separate sheet (File > Import)
4. Apply formulas - Blue cells are INPUTS, calculated cells are OUTPUTS

[EXCEL SETUP]
1. Open Excel
2. Data > From Text/CSV for each file
3. Enable "Data > Connections" for auto-refresh
4. Use Data Validation for dropdown inputs

[FORMULA REFERENCE]
All formulas follow this structure:
- Blue cells: User editable inputs
- White/Green cells: Auto-calculated outputs
- Red cells: Warnings/alerts

Key Formulas:
- Monthly Net Income: =Daily_Rate * Days * (1 - Tax_Rate)
- Monthly Surplus: =Net_Income - Essential_Outgoings
- Months to Debt Freedom: =Debt_Balance / (Min_Payment + Overpayment)
- Investment Allocation: =Available_Funds * Allocation_Percentage

================================================================================
HOW TO RUN THE AI/ML ENGINE
================================================================================

[REQUIREMENTS]
pip install pandas numpy scikit-learn requests schedule

[SINGLE CYCLE - TEST MODE]
python 09_Autonomous_Master_Controller.py --mode single

[CONTINUOUS MODE - FULL AUTONOMY]
python 09_Autonomous_Master_Controller.py --mode continuous

[CUSTOM CONFIG]
python 09_Autonomous_Master_Controller.py --config my_config.json --mode single

[MODULE TESTING]
python 06_AI_Automation_Engine.py      # Test calculations
python 07_ML_Prediction_Model.py       # Test ML models
python 08_Data_Ingestion_Engine.py     # Test API connections

================================================================================
DATA EXTRACTED FROM CONVERSATION
================================================================================

[PLATFORMS - 39 Total]
- Crypto Trading: Pionex, 3Commas, Cryptohopper, Bitsgap, Coinrule, TradeSanta, Gunbot
- Stock/ETF: Trading 212, Freetrade, eToro, Interactive Brokers, Lightyear, Hargreaves Lansdown
- Commodities: Goldwise, BullionVault, Minted, Bitpanda
- Crypto Interest: Nexo, Clapp, Coinbase Savings, Ledn
- Staking: Bitget, Gemini UK
- Forex: FOREX.com, Trading 212 CFD, Pepperstone, XM, Vantage Markets
- DeFi: Aave, Compound, Equalizer Finance, DeFi Saver
- Stock AI: Trade Ideas, Tickeron, TrendSpider, Composer
- Quant: QuantConnect, WunderTrading, TradingView Pine

[INVESTMENT ENGINES - 12 Total]
ENG001: Pionex DCA (£35/month, 35% allocation)
ENG002: Trading 212 ISA (£20/month, 25% allocation)
ENG003: Infrastructure ETF (£5/month)
ENG004: Goldwise (£10/month, 10% allocation)
ENG005: LISA (£20/month, 20% allocation)
ENG006: Bitget Staking (£10/month, 10% allocation)
ENG007: Pionex Spot-Futures Arb (Phase 4)
ENG008: Bitsgap LOOP Trading (Phase 4)
ENG009: FOREX.com Demo (Learning)
ENG010: Stock Equities (Phase 4)
ENG011: Tax Sinking Fund (£20/month)
ENG012: Emergency Fund (£200/month)

[TAX CONFIGURATION 2025/26]
- Personal Allowance: £12,570
- CGT Allowance: £3,000 (18% basic, 24% higher)
- Trading Allowance: £1,000
- Dividend Allowance: £500
- ISA Limit: £20,000
- LISA Limit: £4,000 + 25% bonus

[PHASE STRUCTURE]
Phase 1 (Months 1-3): Emergency Fund £1,000
Phase 2 (Months 4-6): Debt Elimination
Phase 3 (Months 7-12): Core Investment Engines
Phase 4 (Year 2): Advanced Automation
Phase 5 (Year 3+): Speculative Strategies

================================================================================
AUTOMATION FEATURES
================================================================================

[DAILY AUTONOMOUS ACTIONS]
- 09:00: Check Pionex DCA bot status
- 18:00: Update all portfolio prices
- Risk monitoring: Alert if portfolio drops >2%

[WEEKLY AUTONOMOUS ACTIONS]
- Sunday 10:00: Review paper trading stats
- Generate weekly performance report
- Check allocation deviations

[MONTHLY AUTONOMOUS ACTIONS]
- 1st of month: Execute all scheduled deposits
- 15th of month: Buy ETFs and metals
- Rebalance portfolio if >5% deviation

[QUARTERLY AUTONOMOUS ACTIONS]
- Export Koinly tax report
- Verify FCA registration of platforms
- Rebalance check and execution
- Tax liability estimate update

[ML/AI CAPABILITIES]
- Price prediction using ensemble models
- Risk assessment (VaR, CVaR, Sharpe, Max Drawdown)
- Trading signal generation with confidence scoring
- Portfolio optimization based on risk tolerance
- Automated rebalancing recommendations

================================================================================
CUSTOMIZATION GUIDE
================================================================================

[CHANGING YOUR INCOME]
Edit: 02_Financial_Dashboard_Template.csv
- B2: Daily Rate
- B3: Days per Month
- B4: Tax Rate
All calculations auto-update

[CHANGING ALLOCATION PERCENTAGES]
Edit: 02_Financial_Dashboard_Template.csv
- B23: Pionex allocation %
- B24: ISA allocation %
- B25: Goldwise allocation %
- B26: LISA allocation %
- B27: Staking allocation %
Must sum to 1.0 (100%)

[ADDING NEW ASSETS]
1. Add to 01_Platform_Inventory_Master.csv
2. Add allocation row to Dashboard
3. Update investment amounts formula
4. Add to portfolio tracking sheet

[CHANGING TAX YEAR]
Edit: 05_Tax_Calculation_Engine.csv
Update allowances for 2026/27 when announced

================================================================================
FILE INTEGRATION WITH FINANCIAL MASTER
================================================================================

These files integrate with the existing Financial Master system:
- Located in: 07_Working_Files\00_Master_Spreadsheet_System\
- Linked to: 00_START_HERE navigation documents
- Referenced in: 19_CONVERSATION_DATA_ABSTRACT.txt
- Use with: 10_EQUIPMENT_ACQUISITION_ROADMAP.txt

Spreadsheet data feeds into:
- 03_COMPLETE_MASTER_INDEX.txt
- Financial projections
- Equipment acquisition calculations
- Business insurance planning

================================================================================
NEXT STEPS
================================================================================

1. IMPORT: Load CSVs into Google Sheets or Excel
2. CUSTOMIZE: Update blue input cells with your data
3. VERIFY: Check all formulas calculate correctly
4. RUN AI: Execute single cycle to test automation
5. SCHEDULE: Set up continuous mode on a server/cloud
6. MONITOR: Review weekly reports and adjust as needed

================================================================================
SUPPORT & UPDATES
================================================================================
- Configuration files use JSON format for easy editing
- Python scripts include help: python script.py --help
- Logs saved to: autonomous_controller.log, ai_automation.log
- All timestamps use ISO 8601 format

================================================================================
END OF README
================================================================================
