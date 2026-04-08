import { test, expect } from '@playwright/test';

test.describe('TeaTime App', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.clear();
    });
  });

  test('app loads and shows timer page', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Active Steep')).toBeVisible();
    await expect(page.getByText('Set your intention')).toBeVisible();
  });

  test('timer displays correctly', async ({ page }) => {
    await page.goto('/');
    // Check the timer in the circular dial area
    await expect(page.locator('.font-mono').getByText('25')).toBeVisible();
  });

  test('category selection shows mode indicator', async ({ page }) => {
    await page.goto('/');
    // Check default category is selected (Deep Work)
    await expect(page.getByText('Deep Work Mode')).toBeVisible();
  });

  test('quick time buttons work', async ({ page }) => {
    await page.goto('/');
    // Click on 1 minute quick button
    const buttons = page.locator('button');
    await buttons.filter({ hasText: /^1$/ }).first().click();
  });

  test('start button is visible', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('button', { name: /start/i })).toBeVisible();
  });

  test('sessions tab shows history', async ({ page }) => {
    await page.goto('/');
    // Navigate to Sessions tab via bottom nav
    await page.locator('nav').getByText('Sessions').click();
    await expect(page.getByText('Your Steeps')).toBeVisible();
  });

  test('stats tab shows analytics', async ({ page }) => {
    await page.goto('/');
    await page.locator('nav').getByText('Stats').click();
    await expect(page.getByText('Statistics')).toBeVisible();
  });

  test('profile tab shows settings', async ({ page }) => {
    await page.goto('/');
    await page.locator('nav').getByText('Profile').click();
    await expect(page.getByText('Preferences')).toBeVisible();
  });

  test('timer session save flows into sessions stats and trends', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: /test save session/i }).click();
    await expect(page.getByText('Session saved!')).toBeVisible();

    await page.locator('nav').getByText('Sessions').click();
    await expect(page.getByText('Test session')).toBeVisible();
    await expect(page.getByText('Deep Work')).toBeVisible();

    await page.locator('nav').getByText('Stats').click();
    await expect(page.getByText('0h 1m').first()).toBeVisible();
    await expect(page.getByText('1 Sessions')).toBeVisible();

    await page.locator('nav').getByText('Trends').click();
    await expect(page.getByText('No category data yet. Complete some sessions!')).not.toBeVisible();
    await expect(page.getByText('Hit your first session to start the chain!')).not.toBeVisible();
  });
});
