# Browser Automation

Pluggable browser automation boundary.

- `Playwright` is the direct-control adapter for page snapshots and future scripted workflows.
- `Crawl4AI` is the preferred future adapter for dynamic-page crawling and scripted interaction.
- `browser-use` is the agentic-browser adapter candidate for AI-guided multi-step tasks.
- `POST /api/browser/research` is the active bounded agentic workflow today: it opens a page, follows real next-page links, extracts readable text, preserves source pages, and stores a paginated local document.

The default install keeps heavy browser dependencies optional so the local API remains light. Install `requirements-browser.txt` only when richer dynamic-page automation is needed:

```powershell
powershell -ExecutionPolicy Bypass -File tools/scripts/install-browser-stack.ps1
```
