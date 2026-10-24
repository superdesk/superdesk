/*
 * The screen reader flows with NVDA on Windows, through @guidepup/playwright.
 *
 * Meant for the GitHub Actions workflow in ../workflows/a11y-nvda.yml (windows-latest + guidepup/setup-action,
 * which installs a portable NVDA). Locally it needs a Windows machine prepared with `npx @guidepup/setup`.
 *
 * Run: npx playwright test nvda.spec.ts --workers 1 --reporter list
 * Output: out/nvda/superdesk.txt, out/nvda/newshub.txt
 */
import {nvdaTest as test, NVDAPlaywright} from '@guidepup/playwright';
import path from 'path';
import {Page} from '@playwright/test';
import {Driver, newshubFlow, superdeskFlow} from './sr/flows';

const OUT = path.join(__dirname, 'out', 'nvda');

test.use({headless: false, viewport: {width: 1280, height: 800}});
test.describe.configure({mode: 'serial', timeout: 900000});

// Guidepup's navigateToWebContent clicks the middle of <body> to put focus in the page. Unshielded, that click
// lands on whatever is there (a wire item opens its preview) and moves Chrome's Tab starting point to the middle
// of the page, so the next Tab skips everything above it. A transparent overlay prepended to <body> takes the
// click instead; once it is removed, the next Tab starts from the top of the page.
async function withClickShield(page: Page, fn: () => Promise<void>) {
    await page.evaluate(() => {
        const shield = document.createElement('div');

        shield.id = 'sr-click-shield';
        shield.setAttribute('aria-hidden', 'true');
        shield.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:transparent';
        document.body.prepend(shield);
    });

    try {
        await fn();
    } finally {
        await page.evaluate(() => document.getElementById('sr-click-shield')?.remove());
    }
}

// NVDA starts in browse mode on web content: Down arrow reads the next item, H moves to the next heading,
// Tab moves focus (and switches to focus mode on form fields).
function nvdaDriver(page: Page, nvda: NVDAPlaywright): Driver {
    return {
        name: 'NVDA (Windows)',
        settleMs: 500,
        begin: async () => {
            await page.bringToFront();
            await withClickShield(page, () => nvda.navigateToWebContent());
        },
        next: () => nvda.next(),
        previous: () => nvda.previous(),
        act: () => nvda.act(),
        press: (key) => nvda.press(key),
        nextHeading: () => nvda.perform(nvda.keyboardCommands.moveToNextHeading),
        phrases: () => nvda.spokenPhraseLog(),
    };
}

test('superdesk', async ({page, nvda}) => {
    await superdeskFlow(page, nvdaDriver(page, nvda), path.join(OUT, 'superdesk.txt'));
});

test('newshub', async ({page, nvda}) => {
    await newshubFlow(page, nvdaDriver(page, nvda), path.join(OUT, 'newshub.txt'));
});
