import { Page, Locator, expect } from '@playwright/test';

/**
 * Login Page Object Model
 * Encapsulates all interactions with the login page
 */
export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;
  readonly registerLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('[data-testid="email-input"]').or(page.locator('input[type="email"]'));
    this.passwordInput = page.locator('[data-testid="password-input"]').or(page.locator('input[type="password"]'));
    this.loginButton = page.locator('[data-testid="login-button"]').or(page.locator('button:has-text("Login")')).or(page.locator('button:has-text("Sign In")'));
    this.errorMessage = page.locator('[data-testid="error-message"]').or(page.locator('.error')).or(page.locator('.alert-error'));
    this.forgotPasswordLink = page.locator('a:has-text("Forgot password")');
    this.registerLink = page.locator('a:has-text("Register")').or(page.locator('a:has-text("Sign up")'));
  }

  async goto() {
    await this.page.goto('/login');
    await this.page.waitForLoadState('networkidle');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async expectLoginSuccess() {
    // Should redirect to dashboard
    await expect(this.page).toHaveURL(/.*dashboard.*/);
    await expect(this.page.locator('h1')).toContainText(/Dashboard|Overview|Home/);
  }

  async expectLoginFailure() {
    await expect(this.errorMessage).toBeVisible();
    await expect(this.errorMessage).toContainText(/Invalid|Error|Failed/);
  }

  async clickForgotPassword() {
    await this.forgotPasswordLink.click();
  }

  async clickRegister() {
    await this.registerLink.click();
  }

  async expectOnLoginPage() {
    await expect(this.page).toHaveURL(/.*login.*/);
    await expect(this.loginButton).toBeVisible();
  }
}
