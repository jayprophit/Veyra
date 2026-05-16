# Browser Research Agent

## Goal

Provide a Manus-like research workflow without granting unrestricted account-changing automation.

## Active Behavior

`POST /api/browser/research` currently performs a bounded, auditable research run:

1. open the seed URL
2. extract readable content
3. follow verified same-domain next-page links
4. stop after the configured page limit
5. store every source page plus a paginated merged document for review

The response includes an explicit action log, the stored document, and the source-page list.

## Why bounded first

Reading and research are reversible. Purchases, account edits, transfers, and live trading are not. Those actions need approvals, receipts, and policy checks before Veyra should automate them.

## Upgrade Path

1. direct HTTP crawler for stable pages
2. Playwright for scripted browser control
3. Crawl4AI for dynamic-site crawling and page interaction
4. browser-use for higher-level agentic flows
5. policy engine and approval queue before any irreversible action
