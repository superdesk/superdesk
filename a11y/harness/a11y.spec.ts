/*
 * WCAG 2.2 AA automated sweep for a running Superdesk + Newshub instance.
 * DRAFT, NOT YET RUN. Routes, selectors and accounts must be checked against the target instance.
 *
 * Setup (project-local, nothing global):
 *   cd <this folder> && npm init -y && npm i -D @playwright/test@1.61.0 @axe-core/playwright@4.10.2
 *   (or reuse superdesk-client-core/e2e/client/node_modules, which already has @playwright/test and its Chromium)
 * Run:
 *   SD_URL=https://sd-test.example SD_USER_REPORTER=... SD_PASS_REPORTER=... NH_URL=https://nh-test.example ... \
 *   npx playwright test a11y.spec.ts --workers 1 --reporter list
 * Output: ./out/<role>/<page>/{axe.json,checks.json,*.png} and ./out/summary-by-sc.json
 */
import {test, Page} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'fs';
import path from 'path';

type Target = {role: string; app: 'sd' | 'nh'; name: string; path: string; prepare?: (page: Page) => Promise<void>};

const OUT = path.join(__dirname, 'out');
const env = (k: string) => process.env[k] ?? '';

// One entry per role. Each needs its own account on the test instance.
const accounts: Record<string, {app: 'sd' | 'nh'; user: string; pass: string}> = {
    reporter: {app: 'sd', user: env('SD_USER_REPORTER'), pass: env('SD_PASS_REPORTER')},
    reviewer: {app: 'sd', user: env('SD_USER_REVIEWER'), pass: env('SD_PASS_REVIEWER')},
    orgadmin: {app: 'sd', user: env('SD_USER_ORGADMIN'), pass: env('SD_PASS_ORGADMIN')},
    sysadmin: {app: 'sd', user: env('SD_USER_SYSADMIN'), pass: env('SD_PASS_SYSADMIN')},
    partner: {app: 'nh', user: env('NH_USER_PARTNER'), pass: env('NH_PASS_PARTNER')},
    nhadmin: {app: 'nh', user: env('NH_USER_ADMIN'), pass: env('NH_PASS_ADMIN')},
};

// Verify every route on the instance. Add `prepare` steps to open modals/panels so their DOM is scanned too.
const targets: Target[] = [
    {role: 'reporter', app: 'sd', name: 'login', path: '/'},
    {role: 'reporter', app: 'sd', name: 'monitoring', path: '/#/workspace/monitoring'},
    {role: 'reporter', app: 'sd', name: 'personal-space', path: '/#/workspace/personal'},
    {role: 'reporter', app: 'sd', name: 'authoring-open-story', path: '/#/workspace/monitoring?item=' + env('SD_SAMPLE_ITEM') + '&action=edit'},
    {role: 'reporter', app: 'sd', name: 'search', path: '/#/search'},
    {role: 'reviewer', app: 'sd', name: 'monitoring', path: '/#/workspace/monitoring'},
    {role: 'reviewer', app: 'sd', name: 'authoring-review', path: '/#/workspace/monitoring?item=' + env('SD_REVIEW_ITEM') + '&action=edit'},
    {role: 'orgadmin', app: 'sd', name: 'users', path: '/#/settings/users'},
    {role: 'orgadmin', app: 'sd', name: 'desks', path: '/#/settings/desks'},
    {role: 'sysadmin', app: 'sd', name: 'vocabularies', path: '/#/settings/vocabularies'},
    {role: 'partner', app: 'nh', name: 'login', path: '/login'},
    {role: 'partner', app: 'nh', name: 'wire-home', path: '/wire'},
    {role: 'partner', app: 'nh', name: 'wire-item', path: '/wire?item=' + env('NH_SAMPLE_ITEM')},
    {role: 'nhadmin', app: 'nh', name: 'companies', path: '/settings/companies'},
];

const baseUrl = (app: 'sd' | 'nh') => (app === 'sd' ? env('SD_URL') : env('NH_URL'));

async function login(page: Page, role: string) {
    const a = accounts[role];

    if (a.app === 'sd') {
        await page.goto(baseUrl('sd') + '/');
        await page.locator('[data-test-id="login-page"] [data-test-id="username"]').fill(a.user);
        await page.locator('[data-test-id="login-page"] [data-test-id="password"]').fill(a.pass);
        await page.locator('[data-test-id="login-page"] [data-test-id="submit"]').click();
        await page.locator('[data-test-id="dashboard"], .sd-main-content-grid, #main-container').first().waitFor();
    } else {
        await page.goto(baseUrl('nh') + '/login');
        await page.locator('input[name="email"]').fill(a.user);
        await page.locator('input[name="password"]').fill(a.pass);
        await page.locator('button[type="submit"], input[type="submit"]').first().click();
        await page.waitForLoadState('networkidle');
    }
}

async function axeScan(page: Page) {
    const res = await new AxeBuilder({page})
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
        .analyze();

    return res;
}

// Scripted checks for criteria axe does not cover. Results are signals for a human, not verdicts.
async function scriptedChecks(page: Page, dir: string) {
    const out: Record<string, unknown> = {};

    out.lang = await page.evaluate(() => document.documentElement.getAttribute('lang')); // 3.1.1
    out.title = await page.title(); // 2.4.2 (does it change per view?)
    out.liveRegions = await page.evaluate(() => document.querySelectorAll('[aria-live],[role="status"],[role="alert"],[role="log"]').length); // 4.1.3

    // 1.4.10 Reflow: 320 CSS px wide equals 1280 px at 400% zoom.
    const original = page.viewportSize() ?? {width: 1280, height: 800};
    await page.setViewportSize({width: 320, height: 256});
    await page.waitForTimeout(500);
    out.reflowHorizontalScroll = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
    await page.screenshot({path: path.join(dir, 'reflow-320.png'), fullPage: true});
    // 1.4.4 Resize text approximation: 640 px wide equals 1280 px at 200%.
    await page.setViewportSize({width: 640, height: 400});
    await page.screenshot({path: path.join(dir, 'zoom-200.png'), fullPage: true});
    await page.setViewportSize(original);

    // 1.4.12 Text spacing: inject the WCAG bookmarklet values, screenshot for clipping review.
    const spacing = await page.addStyleTag({content: '* { line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important; } p { margin-bottom: 2em !important; }'});
    await page.screenshot({path: path.join(dir, 'text-spacing.png'), fullPage: true});
    await spacing.evaluate((el) => el.remove());

    // Windows High Contrast proxy (forced colours), relevant to Windows users of assistive technology.
    await page.emulateMedia({forcedColors: 'active'});
    await page.screenshot({path: path.join(dir, 'forced-colors.png'), fullPage: true});
    await page.emulateMedia({forcedColors: 'none'});

    // 2.1.1 / 2.1.2 / 2.4.3 / 2.4.7 / 2.4.11: walk the tab order and record what happens.
    const walk: Array<Record<string, unknown>> = [];
    await page.locator('body').click({position: {x: 1, y: 1}}).catch(() => undefined);

    for (let i = 0; i < 60; i++) {
        await page.keyboard.press('Tab');
        const info = await page.evaluate(() => {
            const el = document.activeElement as HTMLElement | null;

            if (el == null || el === document.body) {
                return {onBody: true};
            }

            const r = el.getBoundingClientRect();
            const cs = getComputedStyle(el);
            const points = [[r.left + r.width / 2, r.top + r.height / 2], [r.left + 1, r.top + 1], [r.right - 1, r.bottom - 1]];
            const covered = points.every(([x, y]) => {
                const top = document.elementFromPoint(x, y);

                return top != null && top !== el && !el.contains(top) && !top.contains(el);
            });

            return {
                tag: el.tagName.toLowerCase(),
                role: el.getAttribute('role'),
                name: (el.getAttribute('aria-label') ?? el.textContent ?? '').trim().slice(0, 60),
                testId: el.getAttribute('data-test-id'),
                outline: cs.outlineStyle + ' ' + cs.outlineWidth,
                boxShadow: cs.boxShadow,
                offscreen: r.bottom < 0 || r.top > innerHeight || r.width === 0 || r.height === 0,
                fullyCovered: covered, // 2.4.11 signal
            };
        });

        walk.push(info);
    }

    out.tabWalk = walk;
    const seen = walk.map((w) => JSON.stringify([w.tag, w.name, w.testId]));
    out.possibleTrap = seen.length > 10 && new Set(seen.slice(-20)).size <= 2; // 2.1.2 signal
    out.noVisibleOutlineCount = walk.filter((w) => w.outline === 'none 0px' && w.boxShadow === 'none').length; // 2.4.7 signal, confirm visually

    return out;
}

const summary: Record<string, Array<{role: string; page: string; rule: string; impact: string | null | undefined; nodes: number}>> = {};

for (const t of targets) {
    test(`${t.role} / ${t.name}`, async ({page}) => {
        const dir = path.join(OUT, t.role, t.name);
        fs.mkdirSync(dir, {recursive: true});

        if (t.name !== 'login') {
            await login(page, t.role);
        }

        await page.goto(baseUrl(t.app) + t.path);
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1500); // SPA settle

        if (t.prepare != null) {
            await t.prepare(page);
        }

        const axe = await axeScan(page);
        fs.writeFileSync(path.join(dir, 'axe.json'), JSON.stringify(axe, null, 2));
        await page.screenshot({path: path.join(dir, 'page.png'), fullPage: true});

        for (const v of axe.violations) {
            const scs = v.tags.filter((x) => /^wcag\d{3,4}$/.test(x)).map((x) => x.replace(/^wcag(\d)(\d)(\d+)$/, '$1.$2.$3'));

            for (const sc of scs.length > 0 ? scs : ['best-practice']) {
                (summary[sc] ??= []).push({role: t.role, page: t.name, rule: v.id, impact: v.impact, nodes: v.nodes.length});
            }
        }

        fs.writeFileSync(path.join(dir, 'checks.json'), JSON.stringify(await scriptedChecks(page, dir), null, 2));
    });
}

test.afterAll(() => {
    fs.mkdirSync(OUT, {recursive: true});
    fs.writeFileSync(path.join(OUT, 'summary-by-sc.json'), JSON.stringify(summary, null, 2));
});
