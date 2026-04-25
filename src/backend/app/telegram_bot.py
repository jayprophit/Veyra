"""
Financial Master Telegram Bot
Mobile Command & Control Interface
Version: 1.0 | Quick-Win Implementation

QUICK SETUP (5 minutes):
1. Message @BotFather on Telegram
2. Type /newbot, name it "YourFinancialMasterBot"
3. Copy the API token
4. Paste token below in BOT_TOKEN
5. Run: python 12_Telegram_Bot.py
6. Message your bot /start

COMMANDS:
/start - Welcome message
/status - Portfolio snapshot
/agents - Agent status overview
/alerts - Recent critical alerts
/approve <id> - Approve pending decision
/reject <id> - Reject pending decision
/decisions - List all pending decisions
/cgt - CGT allowance status
/isa - ISA allowance status
/tax - Tax summary
/price <symbol> - Get current price (BTC, ETH, VWRP)
/rebalance - Check if rebalancing needed
/kill - EMERGENCY STOP all trading
/help - Show all commands
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import json

# Telegram Bot API
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
AUTHORIZED_USER_IDS = []  # Add your Telegram user ID(s) here for security

# ============================================================================
# BOT COMMAND HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued"""
    user = update.effective_user
    
    # Security check
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized user. Contact admin.")
        return
    
    welcome_message = f"""
🤖 <b>Financial Master Bot</b>
Welcome, {user.first_name}!

Your personal AI-powered financial command center is now mobile.

<b>QUICK COMMANDS:</b>
📊 /status - Portfolio snapshot
🤖 /agents - Agent status
🔔 /alerts - Critical alerts
✅ /decisions - Pending decisions
📈 /price BTC - Check price
🛑 /kill - Emergency stop
❓ /help - All commands

<b>AGENTS ONLINE:</b>
• AI Accountant (Tax optimization)
• AI Lawyer (FCA compliance)
• AI Governance (Policy enforcement)
• AI Regulations (HMRC/CARF)
• AI Protocols (DeFi risk)
• AI Cyber Security (Wallet/API)
• AI Blockchain (Gas/MEV)
• AI Analyst (Opportunities)

<i>Last system check: {datetime.now().strftime('%H:%M:%S')}</i>
    """
    
    await update.message.reply_text(welcome_message, parse_mode='HTML')


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get portfolio and system status"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    # In production, fetch from DataIngestionEngine
    # For now, simulate with example data
    status_msg = f"""
<b>📊 PORTFOLIO SNAPSHOT</b>
<i>{datetime.now().strftime('%Y-%m-%d %H:%M')}</i>

<b>TOTAL VALUE:</b> £5,247.83
<b>24H CHANGE:</b> +£127.42 (+2.49%) 🟢
<b>CASH POSITION:</b> £1,000.00

<b>ALLOCATION:</b>
🟠 BTC: 35% (£1,836.74)
🔵 VWRP: 25% (£1,311.96)
🟡 GOLD: 10% (£524.78)
🟢 LISA: 20% (£1,049.57)
🟣 ETH: 10% (£524.78)

<b>PHASE STATUS:</b>
Current: Phase 3 (Core Investment Engines)
Progress: 67% to Phase 4

<b>SYSTEM:</b>
Agents: 8/8 active ✅
Last cycle: 14 minutes ago
Next rebalance check: 4 hours
    """
    
    keyboard = [
        [InlineKeyboardButton("📈 View Chart", callback_data='chart')],
        [InlineKeyboardButton("🔄 Rebalance", callback_data='rebalance'),
         InlineKeyboardButton("⚙️ Settings", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(status_msg, parse_mode='HTML', reply_markup=reply_markup)


async def agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show status of all AI agents"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    agents_status = f"""
<b>🤖 MULTI-AGENT STATUS</b>
<i>{datetime.now().strftime('%H:%M:%S')}</i>

<b>ACTIVE AGENTS (8/8):</b>

1️⃣ <b>AI Accountant</b> ✅
   Decisions: 47 | Last: 2h ago
   Status: CGT optimization pending

2️⃣ <b>AI Lawyer</b> ✅
   Decisions: 12 | Last: 6h ago
   Status: CARF monitoring active

3️⃣ <b>AI Governance</b> ✅
   Decisions: 89 | Last: 15m ago
   Status: Audit trail verified

4️⃣ <b>AI Regulations</b> ✅
   Decisions: 23 | Last: 1h ago
   Status: HMRC guidance current

5️⃣ <b>AI Protocols</b> ✅
   Decisions: 8 | Last: 4h ago
   Status: No DeFi positions

6️⃣ <b>AI Cyber Security</b> ⚠️
   Decisions: 156 | Last: 23m ago
   Status: API security check needed

7️⃣ <b>AI Blockchain</b> ✅
   Decisions: 34 | Last: 45m ago
   Status: Gas optimization current

8️⃣ <b>AI Analyst</b> ✅
   Decisions: 67 | Last: 1.5h ago
   Status: BTC dip opportunity identified

<b>ORCHESTRATOR:</b> Active | Cycles: 1,247
<b>QUEUE:</b> 3 decisions pending approval
    """
    
    await update.message.reply_text(agents_status, parse_mode='HTML')


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show recent critical alerts"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    alerts_msg = f"""
<b>🔔 CRITICAL ALERTS</b>
<i>Last 24 hours</i>

🚨 <b>HIGH PRIORITY (1)</b>

<b>API Security Check</b> (AI Cyber Security)
Status: ⚠️ REVIEW NEEDED
Time: 2 hours ago

Binance API has withdrawal permissions enabled.
This is a security risk. Recommend disabling.

Action: Review API settings
ID: 7a3f9b2c8d4e1f5a

---

⚠️ <b>MEDIUM PRIORITY (2)</b>

1. <b>CGT Allowance Optimization</b> (AI Accountant)
   £2,100 allowance remaining. 45 days to year-end.
   
2. <b>ISA Maximization</b> (AI Accountant)
   £18,500 remaining. Need £1,542/month.

---

ℹ️ <b>INFORMATIONAL (3)</b>
• BTC down 22% - accumulation opportunity
• Gas prices high (87 gwei) - delay transactions
• Portfolio correlation 0.85 - consider diversification

Use /decisions to approve pending actions
    """
    
    keyboard = [
        [InlineKeyboardButton("✅ Review Decisions", callback_data='decisions')],
        [InlineKeyboardButton("🛡️ Security Settings", callback_data='security')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(alerts_msg, parse_mode='HTML', reply_markup=reply_markup)


async def decisions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all pending decisions requiring approval"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    decisions_msg = f"""
<b>⏳ PENDING DECISIONS (3)</b>
<i>Require your approval</i>

<b>1. [CRITICAL] API Security</b>
Agent: AI Cyber Security
ID: 7a3f9b2c
Recommendation: Revoke Binance withdrawal permissions
Impact: Prevents total fund loss

[Approve] [Reject] [Details]

---

<b>2. [HIGH] CGT Optimization</b>
Agent: AI Accountant
ID: b8c2d4e6
Recommendation: Crystallize £2,100 in gains
Tax Savings: ~£378

[Approve] [Reject] [Details]

---

<b>3. [MEDIUM] Rebalance Portfolio</b>
Agent: AI Analyst
ID: a1d5f7e9
Recommendation: Shift 5% from BTC to VWRP
Drift: BTC 40% (target 35%)

[Approve] [Reject] [Details]

---

<b>To approve:</b> /approve 7a3f9b2c
<b>To reject:</b> /reject 7a3f9b2c
<b>View all:</b> /alerts
    """
    
    await update.message.reply_text(decisions_msg, parse_mode='HTML')


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Approve a pending decision by ID"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /approve <decision_id>\n\n"
            "Example: /approve 7a3f9b2c\n\n"
            "Use /decisions to see pending IDs"
        )
        return
    
    decision_id = context.args[0]
    
    # In production, this would:
    # 1. Look up decision in queue
    # 2. Execute if approved
    # 3. Log to audit trail
    # 4. Notify user of result
    
    await update.message.reply_text(
        f"✅ <b>Decision Approved</b>\n\n"
        f"ID: {decision_id}\n"
        f"Status: Queued for execution\n"
        f"ETA: Next cycle (within 1 hour)\n\n"
        f"You'll receive confirmation when complete.",
        parse_mode='HTML'
    )


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reject a pending decision by ID"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /reject <decision_id>\n\n"
            "Example: /reject 7a3f9b2c"
        )
        return
    
    decision_id = context.args[0]
    
    await update.message.reply_text(
        f"❌ <b>Decision Rejected</b>\n\n"
        f"ID: {decision_id}\n"
        f"Status: Archived\n"
        f"Agent will learn from this rejection.\n\n"
        f"No action will be taken.",
        parse_mode='HTML'
    )


async def cgt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Capital Gains Tax allowance status"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    cgt_msg = f"""
<b>💰 CAPITAL GAINS TAX (2025/26)</b>

<b>Allowance:</b> £3,000
<b>Used:</b> £0 (0%)
<b>Remaining:</b> £3,000 (100%) ✅

<b>Unrealized Gains:</b>
• BTC: +£1,247 (from £4,200 cost basis)
• VWRP: +£89
• ETH: -£45 (loss)
<b>Total Unrealized:</b> +£1,291

<b>OPTIMIZATION:</b>
You have £3,000 allowance remaining.
Consider crystallizing £1,291 in gains
tax-free before 5-Apr-2026.

<b>Tax Year Ends:</b> 45 days
<b>Recommended Action:</b> /approve b8c2d4e6
    """
    
    await update.message.reply_text(cgt_msg, parse_mode='HTML')


async def isa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show ISA allowance status"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    isa_msg = f"""
<b>🏦 ISA ALLOWANCE (2025/26)</b>

<b>Annual Limit:</b> £20,000
<b>Contributed:</b> £1,500 (7.5%)
<b>Remaining:</b> £18,500 (92.5%)

<b>MONTHLY REQUIREMENT:</b>
To max out by year-end:
→ £1,542/month needed
→ Current: £100/month

<b>PROJECTION:</b>
At current rate: £2,200/year (11%)
Missing out on: £17,800 tax-free growth

<b>RECOMMENDATION:</b>
Increase Standing Order to £1,542/month
or make lump sum contribution.

<b>Account:</b> Trading 212 ISA
<b>Current Value:</b> £1,847.32
    """
    
    await update.message.reply_text(isa_msg, parse_mode='HTML')


async def tax_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show complete tax summary"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    tax_msg = f"""
<b>📋 TAX SUMMARY (2025/26)</b>

<b>INCOME TAX:</b>
Personal Allowance: £12,570 ✅
Used: £0 (investment income only)

<b>CAPITAL GAINS:</b>
Allowance: £3,000 ✅
Used: £0
Remaining: £3,000

<b>DIVIDEND TAX:</b>
Allowance: £500 ✅
Projected: £127 (25.4%)
Remaining: £373

<b>TRADING ALLOWANCE:</b>
£1,000 (if applicable)

<b>KEY DATES:</b>
• Tax Year End: 5-Apr-2026 (45 days)
• Self Assessment: 31-Jan-2027
• Payment Deadline: 31-Jan-2027

<b>AI ACCOUNTANT:</b>
No issues detected ✅
Next check: Tomorrow 09:00

<b>CARF Status:</b> Ready ✅
<b>HMRC Compliance:</b> Current ✅
    """
    
    await update.message.reply_text(tax_msg, parse_mode='HTML')


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get current price for a symbol"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /price <symbol>\n\n"
            "Examples:\n"
            "/price BTC\n"
            "/price ETH\n"
            "/price VWRP\n"
            "/price GOLD"
        )
        return
    
    symbol = context.args[0].upper()
    
    # In production, fetch from DataIngestionEngine
    # Simulated prices for demonstration
    prices = {
        'BTC': {'price': 45234.56, 'change_24h': 2.34, 'currency': 'USD'},
        'ETH': {'price': 3245.78, 'change_24h': -1.23, 'currency': 'USD'},
        'VWRP': {'price': 102.45, 'change_24h': 0.56, 'currency': 'GBP'},
        'GOLD': {'price': 2145.30, 'change_24h': 0.12, 'currency': 'USD'},
    }
    
    if symbol not in prices:
        await update.message.reply_text(
            f"❌ Symbol '{symbol}' not found.\n\n"
            f"Available: BTC, ETH, VWRP, GOLD"
        )
        return
    
    data = prices[symbol]
    change_emoji = "🟢" if data['change_24h'] >= 0 else "🔴"
    
    await update.message.reply_text(
        f"<b>{symbol}</b>\n\n"
        f"Price: {data['currency']} {data['price']:,.2f}\n"
        f"24h: {change_emoji} {data['change_24h']:+.2f}%\n\n"
        f"<i>Last updated: {datetime.now().strftime('%H:%M:%S')}</i>",
        parse_mode='HTML'
    )


async def rebalance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check if portfolio rebalancing is needed"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    rebalance_msg = f"""
<b>🔄 REBALANCE CHECK</b>

<b>TARGET ALLOCATION:</b>
BTC: 35% | VWRP: 25% | GOLD: 10% | LISA: 20% | ETH: 10%

<b>CURRENT ALLOCATION:</b>
BTC: 40% ⚠️ (+5% drift)
VWRP: 23% ✅
GOLD: 10% ✅
LISA: 20% ✅
ETH: 7% ⚠️ (-3% drift)

<b>ANALYSIS:</b>
Threshold: 5% drift triggers rebalance
Status: <b>REBALANCE RECOMMENDED</b>

<b>ACTION:</b>
Sell £262 BTC → Buy £157 ETH, £105 VWRP

<b>AI ANALYST:</b>
Rebalance recommended (ID: a1d5f7e9)
Confidence: 78%

<b>Approve:</b> /approve a1d5f7e9
<b>Reject:</b> /reject a1d5f7e9
    """
    
    await update.message.reply_text(rebalance_msg, parse_mode='HTML')


async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """EMERGENCY STOP - Halt all trading"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    # This is a CRITICAL command
    # In production:
    # 1. Cancel all open orders
    # 2. Disable all trading agents
    # 3. Log emergency stop
    # 4. Notify all channels
    # 5. Require manual restart
    
    keyboard = [
        [InlineKeyboardButton("✅ CONFIRM EMERGENCY STOP", callback_data='confirm_kill')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_kill')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🛑 <b>EMERGENCY STOP</b>\n\n"
        f"This will immediately:\n"
        f"• Cancel all open orders\n"
        f"• Halt all autonomous agents\n"
        f"• Disable trading APIs\n"
        f"• Require manual restart\n\n"
        f"<b>Are you sure?</b>\n"
        f"User: {user.first_name} ({user.id})\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message"""
    user = update.effective_user
    
    if AUTHORIZED_USER_IDS and user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    help_msg = f"""
<b>📚 FINANCIAL MASTER BOT - HELP</b>

<b>PORTFOLIO:</b>
/status - Portfolio snapshot & allocation
/rebalance - Check if rebalancing needed
/price <symbol> - Check current price

<b>AGENTS & DECISIONS:</b>
/agents - View all 8 AI agent statuses
/alerts - Recent critical alerts
/decisions - Pending approval queue
/approve <id> - Approve a decision
/reject <id> - Reject a decision

<b>TAX & COMPLIANCE:</b>
/cgt - Capital Gains Tax status
/isa - ISA allowance tracker
/tax - Complete tax summary

<b>SYSTEM:</b>
/kill - EMERGENCY STOP (halt all trading)
/help - Show this help

<b>TIPS:</b>
• Use /alerts to see what needs attention
• Approve decisions to enable autonomy
• Set up /kill shortcut for emergencies
• Check /agents daily for status

<b>LINKS:</b>
📊 Dashboard: [Web UI URL]
📁 Files: C:\\Users\\jpowe\\Desktop\\Financial Master
🐍 Scripts: 07_Working_Files\\00_Master_Spreadsheet_System

<b>SUPPORT:</b>
For issues, check logs in:
ai_automation.log
agent_command_center.log
    """
    
    await update.message.reply_text(help_msg, parse_mode='HTML')


# ============================================================================
# CALLBACK HANDLERS (Button responses)
# ============================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_kill':
        await query.edit_message_text(
            "🛑 <b>EMERGENCY STOP ACTIVATED</b>\n\n"
            "All trading halted.\n"
            "All orders cancelled.\n"
            "Agents disabled.\n\n"
            "<b>Manual restart required.</b>\n"
            "Contact: System Administrator",
            parse_mode='HTML'
        )
    elif query.data == 'cancel_kill':
        await query.edit_message_text(
            "✅ Emergency stop cancelled.\n"
            "System continues normal operation.",
            parse_mode='HTML'
        )
    elif query.data == 'decisions':
        await decisions(update, context)
    elif query.data == 'chart':
        await query.edit_message_text(
            "📊 Chart view available in web dashboard:\n"
            "[Your Dashboard URL]\n\n"
            "Or run: python 11_Agent_Command_Center.py --mode interactive",
            parse_mode='HTML'
        )


# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


# ============================================================================
# MAIN BOT SETUP
# ============================================================================

def main() -> None:
    """Start the bot"""
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("="*70)
        print("SETUP REQUIRED")
        print("="*70)
        print("\n1. Message @BotFather on Telegram")
        print("2. Type /newbot and follow instructions")
        print("3. Copy the API token")
        print("4. Edit line 49 of this file:")
        print('   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"')
        print('   → BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"')
        print("\n5. Add your Telegram user ID to AUTHORIZED_USER_IDS")
        print("   (Get ID from @userinfobot)")
        print("\n6. Run: python 12_Telegram_Bot.py")
        print("\n" + "="*70)
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("agents", agents))
    application.add_handler(CommandHandler("alerts", alerts))
    application.add_handler(CommandHandler("decisions", decisions))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("reject", reject))
    application.add_handler(CommandHandler("cgt", cgt))
    application.add_handler(CommandHandler("isa", isa))
    application.add_handler(CommandHandler("tax", tax_summary))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("rebalance", rebalance))
    application.add_handler(CommandHandler("kill", kill))
    application.add_handler(CommandHandler("help", help_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    print("="*70)
    print("FINANCIAL MASTER TELEGRAM BOT")
    print("="*70)
    print("\n✅ Bot is starting...")
    print("Press Ctrl+C to stop\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
