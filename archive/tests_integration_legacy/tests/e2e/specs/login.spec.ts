import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page before each test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('should login with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await loginPage.login(
      process.env.TEST_USER_EMAIL || 'test@example.com',
      process.env.TEST_USER_PASSWORD || 'testpassword123'
    );
    
    await loginPage.expectLoginSuccess();
    
    // Verify we're on dashboard
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectDashboardLoaded();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await loginPage.login('invalid@example.com', 'wrongpassword');
    
    await loginPage.expectLoginFailure();
    await loginPage.expectOnLoginPage();
  });

  test('should show error with empty email', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await loginPage.login('', 'somepassword');
    
    // Should show validation error
    await expect(page.locator('text=Email is required')).toBeVisible();
  });

  test('should show error with empty password', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await loginPage.login('test@example.com', '');
    
    // Should show validation error
    await expect(page.locator('text=Password is required')).toBeVisible();
  });

  test('should navigate to forgot password page', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await loginPage.clickForgotPassword();
    
    await expect(page).toHaveURL(/.*forgot-password.*/);
  });

  test('should navigate to register page', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    await loginPage.clickRegister();
    
    await expect(page).toHaveURL(/.*register.*/);
  });

  test('should persist session after refresh', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    // Login
    await loginPage.login(
      process.env.TEST_USER_EMAIL || 'test@example.com',
      process.env.TEST_USER_PASSWORD || 'testpassword123'
    );
    
    await loginPage.expectLoginSuccess();
    
    // Refresh page
    await page.reload();
    
    // Should still be logged in (on dashboard)
    await expect(page).toHaveURL(/.*dashboard.*/);
  });
});
