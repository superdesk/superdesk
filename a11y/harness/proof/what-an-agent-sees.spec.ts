import {test} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'fs';

const URL = process.env.SD_URL ?? 'https://sd-hgbriefdeskdemo.test.superdesk.org/';

test('login page: accessibility tree, keyboard walk, axe', async ({page}) => {
    await page.goto(URL);
    await page.locator('[data-test-id="login-page"]').waitFor();

    // 1. What a screen reader is given: the accessibility tree as roles and names.
    const tree = await page.locator('body').ariaSnapshot();
    fs.writeFileSync('proof/aria-snapshot.yaml', tree);

    // 2. Keyboard walk: press Tab 12 times and record where focus lands and whether it is visible.
    const walk: Array<string> = [];
    for (let i = 0; i < 12; i++) {
        await page.keyboard.press('Tab');
        walk.push(await page.evaluate(() => {
            const el = document.activeElement as HTMLElement | null;
            if (!el || el === document.body) return 'BODY (focus lost)';
            const cs = getComputedStyle(el);
            const name = el.getAttribute('aria-label') || el.textContent?.trim().slice(0, 40) || el.getAttribute('placeholder') || '';
            const visible = cs.outlineStyle !== 'none' && cs.outlineWidth !== '0px' || cs.boxShadow !== 'none';
            return `${el.tagName.toLowerCase()}#${el.id || '-'} name="${name}" focusVisible=${visible}`;
        }));
    }
    fs.writeFileSync('proof/keyboard-walk.txt', walk.join('\n'));

    // 3. axe
    const results = await new AxeBuilder({page}).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']).analyze();
    const summary = results.violations.map((v) => `${v.id} [${v.impact}] ${v.tags.filter((t) => /^wcag\d/.test(t)).join(',')} x${v.nodes.length}: ${v.help}`);
    fs.writeFileSync('proof/axe-violations.txt', summary.join('\n'));
});
