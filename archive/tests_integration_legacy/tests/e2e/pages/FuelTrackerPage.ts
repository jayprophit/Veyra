import { Page, Locator, expect } from '@playwright/test';

/**
 * Fuel Tracker Page Object Model
 */
export class FuelTrackerPage {
  readonly page: Page;
  readonly addVehicleButton: Locator;
  readonly logMileageButton: Locator;
  readonly vehiclesList: Locator;
  readonly mileageTable: Locator;
  readonly hmrcSummary: Locator;
  readonly makeInput: Locator;
  readonly modelInput: Locator;
  readonly registrationInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.addVehicleButton = page.locator('[data-testid="add-vehicle"]').or(page.locator('button:has-text("Add Vehicle")'));
    this.logMileageButton = page.locator('[data-testid="log-mileage"]').or(page.locator('button:has-text("Log Mileage")'));
    this.vehiclesList = page.locator('[data-testid="vehicles-list"]').or(page.locator('.vehicles-list'));
    this.mileageTable = page.locator('[data-testid="mileage-table"]').or(page.locator('table'));
    this.hmrcSummary = page.locator('[data-testid="hmrc-summary"]').or(page.locator('.hmrc-summary'));
    
    // Form inputs
    this.makeInput = page.locator('input[name="make"]').or(page.locator('[data-testid="vehicle-make"]'));
    this.modelInput = page.locator('input[name="model"]').or(page.locator('[data-testid="vehicle-model"]'));
    this.registrationInput = page.locator('input[name="registration"]').or(page.locator('[data-testid="vehicle-registration"]'));
    this.submitButton = page.locator('button[type="submit"]').or(page.locator('[data-testid="submit-vehicle"]'));
  }

  async goto() {
    await this.page.goto('/fuel');
    await this.page.waitForLoadState('networkidle');
  }

  async expectFuelPageLoaded() {
    await expect(this.page).toHaveURL(/.*fuel.*/);
  }

  async addVehicle(make: string, model: string, registration: string) {
    await this.addVehicleButton.click();
    await this.makeInput.fill(make);
    await this.modelInput.fill(model);
    await this.registrationInput.fill(registration);
    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async logMileage(vehicleId: string, distance: number, purpose: string) {
    await this.logMileageButton.click();
    // Fill mileage form
    await this.page.locator('input[name="distance"]').fill(distance.toString());
    await this.page.locator('input[name="purpose"]').fill(purpose);
    await this.page.locator('button[type="submit"]').click();
  }

  async getVehiclesCount(): Promise<number> {
    const vehicles = this.vehiclesList.locator('.vehicle-card, .vehicle-item, tr');
    return await vehicles.count();
  }

  async getHMRCClaimableAmount(): Promise<string> {
    return await this.hmrcSummary.locator('.claimable-amount').textContent() || '';
  }

  async expectVehicleExists(make: string, model: string) {
    await expect(this.vehiclesList).toContainText(make);
    await expect(this.vehiclesList).toContainText(model);
  }
}
