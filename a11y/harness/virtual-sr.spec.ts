/*
 * The screen reader flows with Guidepup's Virtual Screen Reader: headless, runs anywhere (CI, Linux, a laptop).
 * It computes what a screen reader would announce from the accessibility tree; it is not a real reader, so use it
 * for quick coverage and regressions and confirm with voiceover.spec.ts / nvda.spec.ts.
 *
 * Run: npx playwright test virtual-sr.spec.ts --workers 1 --reporter list
 * Output: out/virtual-sr/superdesk.txt, out/virtual-sr/newshub.txt
 */
import {test, Page} from '@playwright/test';
import fs from 'fs';
import path from 'path';
import {Driver, newshubFlow, superdeskFlow} from './sr/flows';

const OUT = path.join(__dirname, 'out', 'virtual-sr');

// The browser build is an ES module ending in `export{...}`; rewrite the export so the library lands on `window.__vsr`.
const LIBRARY = (() => {
    const dir = path.dirname(require.resolve('@guidepup/virtual-screen-reader/package.json'));
    const src = fs.readFileSync(path.join(dir, 'lib', 'esm', 'index.browser.js'), 'utf8');

    return src.replace(/export\s*\{([^}]*)\}\s*;?/, (_m, names: string) => {
        const pair = names.split(',').map((x) => x.trim().split(/\s+as\s+/)).find((p) => p[1] === 'virtual');

        if (pair == null) {
            throw new Error('virtual export not found in the Virtual Screen Reader bundle');
        }

        return `window.__vsr = ${pair[0]};`;
    });
})();

test.use({bypassCSP: true, viewport: {width: 1280, height: 800}});
test.describe.configure({mode: 'serial', timeout: 300000});

// The reader lives in the page, so a full page load drops it. `ensure` re-injects it and keeps the earlier log.
function virtualDriver(page: Page): Driver {
    let archive: Array<string> = [];
    let lastKnown: Array<string> = [];

    const alive = () => page.evaluate(() => (window as any).__vsr?.__started === true).catch(() => false);
    const ensure = async () => {
        if (await alive()) {
            return;
        }

        archive = archive.concat(lastKnown);
        lastKnown = [];
        await page.addScriptTag({type: 'module', content: LIBRARY});
        await page.waitForFunction(() => (window as any).__vsr != null);
        await page.evaluate(async () => {
            const vsr = (window as any).__vsr;

            await vsr.start({container: document.body});
            vsr.__started = true;
        });
    };
    const snapshot = async () => {
        lastKnown = await page.evaluate(() => (window as any).__vsr.spokenPhraseLog()).catch(() => lastKnown);
    };
    const run = async (fn: () => Promise<unknown>) => {
        await ensure();
        await fn();
        await page.waitForTimeout(150);
        await snapshot();
    };

    return {
        name: 'Guidepup Virtual Screen Reader',
        settleMs: 200,
        begin: async () => run(async () => undefined),
        next: () => run(() => page.evaluate(() => (window as any).__vsr.next())),
        previous: () => run(() => page.evaluate(() => (window as any).__vsr.previous())),
        act: () => run(() => page.evaluate(() => (window as any).__vsr.act())),
        nextHeading: () => run(() => page.evaluate(() => {
            const vsr = (window as any).__vsr;

            return vsr.perform(vsr.commands.moveToNextHeading);
        })),
        // Real key presses from Playwright; the virtual reader follows the focus they move.
        press: (key) => run(() => page.keyboard.press(key.replace(/^Space$/, ' '))),
        phrases: async () => {
            if (await alive()) {
                await snapshot();
            }

            return archive.concat(lastKnown);
        },
    };
}

test('superdesk', async ({page}) => {
    await superdeskFlow(page, virtualDriver(page), path.join(OUT, 'superdesk.txt'));
});

test('newshub', async ({page}) => {
    await newshubFlow(page, virtualDriver(page), path.join(OUT, 'newshub.txt'));
});
