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
// Not serial: a failure in one flow must not skip the other. `--workers 1` still runs them one after the other.
test.describe.configure({timeout: 900000});

// Puts NVDA in browse mode on the page with its cursor at the top, without Guidepup's navigateToWebContent.
// That helper clicks the middle of <body>, which lands on whatever is there (a wire item opens its preview),
// and then presses Tab (a Firefox workaround), which moves focus to the first control before the flow starts.
// Here the click goes to a transparent overlay that is removed again before NVDA rebuilds its browse-mode view.
async function toWebContent(page: Page, nvda: NVDAPlaywright) {
    const kept = [...await nvda.spokenPhraseLog()];
    const title = (await page.title()).toLowerCase();

    // NVDA reads the foreground window, so make sure it is the browser (Alt+Escape cycles the windows).
    for (let i = 0; i < 10; i++) {
        await nvda.perform(nvda.keyboardCommands.reportTitle);
        const spoken = (await nvda.lastSpokenPhrase()).toLowerCase();

        if (spoken.includes('chrome') || (title.length > 0 && spoken.includes(title))) {
            break;
        }

        await nvda.press('Alt+Escape');
        await page.waitForTimeout(500);
    }

    await page.bringToFront();
    await page.evaluate(() => {
        const shield = document.createElement('div');

        shield.id = 'sr-click-shield';
        shield.setAttribute('aria-hidden', 'true');
        shield.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:transparent';
        document.body.prepend(shield);
    });

    try {
        await page.locator('#sr-click-shield').click();
    } finally {
        await page.evaluate(() => {
            document.getElementById('sr-click-shield')?.remove();
            (document.activeElement as HTMLElement | null)?.blur();
        });
    }

    await page.waitForTimeout(1000);
    await nvda.clearSpokenPhraseLog();
    (await nvda.spokenPhraseLog()).push(...kept);
    await nvda.press('Control+Home');
}

// NVDA starts in browse mode on web content: Down arrow reads the next item, H moves to the next heading,
// Tab moves focus (and switches to focus mode on form fields).
function nvdaDriver(page: Page, nvda: NVDAPlaywright): Driver {
    return {
        name: 'NVDA (Windows)',
        settleMs: 500,
        begin: async () => {
            await toWebContent(page, nvda);
        },
        next: () => nvda.next(),
        previous: () => nvda.previous(),
        act: () => nvda.act(),
        press: (key) => nvda.press(key),
        pressThrough: async (key) => {
            await nvda.perform(nvda.keyboardCommands.ignoreNextKeyCombination);
            await nvda.press(key);
        },
        // In focus mode H would be typed into the focused field (the article body in the editor), so leave
        // focus mode first when a field has focus; Escape is NVDA's own key there and does not reach the page.
        nextHeading: async () => {
            const editable = await page.evaluate(() => {
                const el = document.activeElement as HTMLElement | null;

                return el != null && (el.isContentEditable || /^(input|textarea|select)$/i.test(el.tagName));
            });

            if (editable) {
                await nvda.perform(nvda.keyboardCommands.exitFocusMode);
            }

            await nvda.perform(nvda.keyboardCommands.moveToNextHeading);
        },
        phrases: () => nvda.spokenPhraseLog(),
    };
}

test('superdesk', async ({page, nvda}) => {
    await superdeskFlow(page, nvdaDriver(page, nvda), path.join(OUT, 'superdesk.txt'));
});

test('newshub', async ({page, nvda}) => {
    await newshubFlow(page, nvdaDriver(page, nvda), path.join(OUT, 'newshub.txt'));
});
