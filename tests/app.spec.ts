import { test, expect } from '@playwright/test';

test.describe('TeaTime App', () => {
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
});
