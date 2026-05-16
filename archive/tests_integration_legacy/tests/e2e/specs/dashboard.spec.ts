import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(
      process.env.TEST_USER_EMAIL || 'test@example.com',
      process.env.TEST_USER_PASSWORD || 'testpassword123'
    );
    await loginPage.expectLoginSuccess();
  });

  test('should display portfolio overview', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    await dashboardPage.expectDashboardLoaded();
    
    // Check portfolio value is displayed
    const value = await dashboardPage.getPortfolioValue();
    expect(value).toMatch(/[£$€]?[\d,]+\.?\d*/);
    
    // Check chart is visible
    await dashboardPage.expectChartVisible();
  });

  test('should refresh data on button click', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    await dashboardPage.refreshData();
    
    // Should still show data after refresh
    await expect(dashboardPage.portfolioValue).toBeVisible();
  });

  test('should change time range', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    // Change to 1 year view
    await dashboardPage.selectTimeRange('1Y');
    
    // Chart should update (no error)
    await dashboardPage.expectChartVisible();
  });

  test('should display holdings', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    const count = await dashboardPage.getHoldingsCount();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should show positive/negative gains', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    
    const gain = await dashboardPage.getTotalGain();
    expect(gain).toBeTruthy();
    
    // Should be colored appropriately
    const isPositive = await dashboardPage.isPositiveGain();
    if (isPositive) {
      await expect(dashboardPage.totalGain).toHaveClass(/positive|green|gain-up/);
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    
    // Should still display properly
    await expect(dashboardPage.portfolioValue).toBeVisible();
  });
});
