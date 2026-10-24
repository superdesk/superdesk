/*
 * Shared access to the demo instance pair: accounts from the environment, login, the read-only request guard,
 * and opening/closing a Superdesk item without leaving it locked. Used by every spec in this folder.
 */
import {Page} from '@playwright/test';

export type App = 'sd' | 'nh';

export const env = (k: string, fallback = '') => process.env[k] ?? fallback;

// One entry per role. Each needs its own account on the test instance.
export const accounts: Record<string, {app: App; user: string; pass: string}> = {
    reporter: {app: 'sd', user: env('SD_USER_REPORTER'), pass: env('SD_PASS_REPORTER')},
    reviewer: {app: 'sd', user: env('SD_USER_REVIEWER'), pass: env('SD_PASS_REVIEWER')},
    orgadmin: {app: 'sd', user: env('SD_USER_ORGADMIN'), pass: env('SD_PASS_ORGADMIN')},
    sysadmin: {app: 'sd', user: env('SD_USER_SYSADMIN'), pass: env('SD_PASS_SYSADMIN')},
    partner: {app: 'nh', user: env('NH_USER_PARTNER'), pass: env('NH_PASS_PARTNER')},
    nhadmin: {app: 'nh', user: env('NH_USER_ADMIN'), pass: env('NH_PASS_ADMIN')},
};

export const baseUrl = (app: App) => (app === 'sd' ? env('SD_URL') : env('NH_URL'));

export const tid = (id: string) => `[data-test-id="${id}"]`;

export async function fillLogin(page: Page, role: string) {
    const a = accounts[role];

    if (a.app === 'sd') {
        await page.goto(baseUrl('sd') + '/');
        await page.locator('[data-test-id="login-page"] [data-test-id="username"]').fill(a.user);
        await page.locator('[data-test-id="login-page"] [data-test-id="password"]').fill(a.pass);
        await page.locator('[data-test-id="login-page"] [data-test-id="submit"]').click();
        await page.waitForURL(/#\//, {timeout: 90000});
        await page.locator(tid('my-profile')).waitFor({timeout: 90000});
        await page.waitForTimeout(3000);
    } else {
        await page.goto(baseUrl('nh') + '/login');
        await page.locator('input[name="email"]').fill(a.user);
        await page.locator('input[name="password"]').fill(a.pass);
        await page.locator('button[type="submit"], input[type="submit"]').first().click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
    }
}

// Aborts every write so a run cannot change the instance. Logging in and locking/unlocking items stay allowed
// (opening the editor locks the item, Close unlocks it). Blocked requests are collected in `blocked`.
export async function readOnlyGuard(page: Page, blocked: Array<string>) {
    await page.route('**/*', (route) => {
        const req = route.request();
        const url = req.url();
        const allowed = req.method() === 'GET' || req.method() === 'HEAD' || req.method() === 'OPTIONS'
            || /\/api\/auth_db\b|\/login\b|\/lock$|\/unlock$/.test(url.split('?')[0]);

        if (allowed) {
            return route.continue();
        }

        blocked.push(`${req.method()} ${url}`);

        return route.abort();
    });
}

// The `?item=...&action=edit` deep link does not open the editor, so the item is opened from the monitoring list.
export async function openItem(page: Page, itemId: string) {
    const item = page.locator(`${tid('article-item')}[id="${itemId}"]`).first();

    await item.waitFor({timeout: 60000});
    await item.scrollIntoViewIfNeeded();
    await item.dblclick();
    await page.locator(tid('authoring')).waitFor({timeout: 30000});
    await page.waitForTimeout(2500);
}

async function clickIfVisible(page: Page, selector: string) {
    const el = page.locator(selector).first();

    if (await el.isVisible().catch(() => false)) {
        await el.click({timeout: 5000}).catch(() => undefined);
        await page.waitForTimeout(500);
    }
}

export async function unlockItem(page: Page, itemId: string) {
    const token = await page.evaluate(() => {
        const raw = localStorage.getItem('sess:token');

        try {
            return raw == null ? null : JSON.parse(raw);
        } catch {
            return raw;
        }
    }).catch(() => null);

    if (token != null) {
        await page.request.post(`${baseUrl('sd')}/api/archive/${encodeURIComponent(itemId)}/unlock`, {
            headers: {Authorization: String(token), 'Content-Type': 'application/json'},
            data: {},
        }).catch(() => undefined);
    }
}

// Closes the editor without saving. Falls back to the unlock endpoint so a failed run never leaves the item locked.
export async function closeItem(page: Page, itemId: string) {
    await clickIfVisible(page, tid('multi-image-edit--cancel-upload'));
    await clickIfVisible(page, `${tid('interactive-actions-panel')} ${tid('close')}`);

    try {
        if (await page.locator(tid('authoring')).isVisible()) {
            await page.locator(`${tid('authoring-topbar')} ${tid('close')}`).click({timeout: 10000});
            const ignore = page.getByRole('button', {name: 'Ignore', exact: true});

            if (await ignore.isVisible({timeout: 1500}).catch(() => false)) {
                await ignore.click();
            }

            await page.locator(tid('authoring')).waitFor({state: 'hidden', timeout: 10000});
        }
    } catch {
        await unlockItem(page, itemId);
    }
}
