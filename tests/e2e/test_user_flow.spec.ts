/**
 * End-to-End Tests for Aurora User Flow
 * 
 * Tests complete user journeys through the Aurora SaaS application.
 */
import { test, expect } from '@playwright/test';

describe('User Authentication Flow', () => {
  test('complete login and dashboard access', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill in login credentials
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    
    // Click login button
    await page.click('[data-testid="login-button"]');
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  });

  test('failed login shows error message', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[data-testid="email-input"]', 'invalid@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });
});

describe('User Profile Management', () => {
  test('update user profile', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Navigate to profile
    await page.click('[data-testid="profile-menu"]');
    await page.click('[data-testid="profile-settings"]');
    
    // Update profile
    await page.fill('[data-testid="display-name"]', 'Updated Name');
    await page.click('[data-testid="save-button"]');
    
    // Verify success
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });
});

describe('Billing Flow', () => {
  test('view invoices', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Navigate to billing
    await page.click('[data-testid="billing-nav"]');
    
    // Verify invoices page loads
    await expect(page.locator('[data-testid="invoices-list"]')).toBeVisible();
  });
});

describe('Task Management', () => {
  test('create and complete task', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Navigate to tasks
    await page.click('[data-testid="tasks-nav"]');
    
    // Create new task
    await page.click('[data-testid="new-task-button"]');
    await page.fill('[data-testid="task-title"]', 'Test Task');
    await page.click('[data-testid="save-task-button"]');
    
    // Verify task created
    await expect(page.locator('[data-testid="task-item"]')).toBeVisible();
    
    // Mark task as complete
    await page.click('[data-testid="task-checkbox"]');
    
    // Verify task completed
    await expect(page.locator('[data-testid="completed-badge"]')).toBeVisible();
  });
});
