import { Page, Locator, expect } from '@playwright/test';

/**
 * Dashboard Page Object Model
 */
export class DashboardPage {
  readonly page: Page;
  readonly portfolioValue: Locator;
  readonly totalGain: Locator;
  readonly chart: Locator;
  readonly holdingsTable: Locator;
  readonly alertsSection: Locator;
  readonly refreshButton: Locator;
  readonly timeRangeSelector: Locator;

  constructor(page: Page) {
    this.page = page;
    this.portfolioValue = page.locator('[data-testid="portfolio-value"]').or(page.locator('.portfolio-value'));
    this.totalGain = page.locator('[data-testid="total-gain"]').or(page.locator('.total-gain'));
    this.chart = page.locator('[data-testid="portfolio-chart"]').or(page.locator('canvas').or(page.locator('.recharts-wrapper')));
    this.holdingsTable = page.locator('[data-testid="holdings-table"]').or(page.locator('table'));
    this.alertsSection = page.locator('[data-testid="alerts"]').or(page.locator('.alerts'));
    this.refreshButton = page.locator('[data-testid="refresh"]').or(page.locator('button:has-text("Refresh")'));
    this.timeRangeSelector = page.locator('[data-testid="time-range"]').or(page.locator('select'));
  }

  async goto() {
    await this.page.goto('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  async expectDashboardLoaded() {
    await expect(this.page).toHaveURL(/.*dashboard.*/);
    await expect(this.portfolioValue).toBeVisible();
  }

  async getPortfolioValue(): Promise<string> {
    return await this.portfolioValue.textContent() || '';
  }

  async getTotalGain(): Promise<string> {
    return await this.totalGain.textContent() || '';
  }

  async isPositiveGain(): Promise<boolean> {
    const gainText = await this.getTotalGain();
    return gainText.includes('+') || !gainText.includes('-');
  }

  async refreshData() {
    await this.refreshButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async selectTimeRange(range: '1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL') {
    await this.timeRangeSelector.selectOption(range);
    await this.page.waitForTimeout(500); // Wait for chart update
  }

  async getHoldingsCount(): Promise<number> {
    const rows = this.holdingsTable.locator('tbody tr');
    return await rows.count();
  }

  async clickHolding(symbol: string) {
    await this.holdingsTable.locator(`tr:has-text("${symbol}")`).click();
  }

  async expectChartVisible() {
    await expect(this.chart).toBeVisible();
  }

  async hasAlerts(): Promise<boolean> {
    return await this.alertsSection.isVisible();
  }
}
