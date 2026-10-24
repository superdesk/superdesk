/*
 * The screen reader flows with the real VoiceOver on macOS, through @guidepup/playwright.
 *
 * Needs a Mac set up for VoiceOver automation (`npx @guidepup/setup`; `voiceOver.detect()` must return true).
 * It runs a headed Chromium, speaks aloud and takes the keyboard focus of the Mac: do not use the machine while
 * it runs. Each flow takes a few minutes.
 *
 * Run: npx playwright test voiceover.spec.ts --workers 1 --reporter list            (both flows)
 *      npx playwright test voiceover.spec.ts --workers 1 --reporter list -g newshub (one flow)
 * Output: out/voiceover/superdesk.txt, out/voiceover/newshub.txt
 */
import {voiceOverTest as test, VoiceOverPlaywright} from '@guidepup/playwright';
import path from 'path';
import {Page} from '@playwright/test';
import {Driver, newshubFlow, superdeskFlow} from './sr/flows';

const OUT = path.join(__dirname, 'out', 'voiceover');

test.use({headless: false, viewport: {width: 1280, height: 800}});
test.describe.configure({mode: 'serial', timeout: 900000});

function voiceOverDriver(page: Page, vo: VoiceOverPlaywright): Driver {
    return {
        name: 'VoiceOver (macOS)',
        settleMs: 300,
        begin: async () => {
            await page.bringToFront();
            await vo.navigateToWebContent();
        },
        next: () => vo.next(),
        previous: () => vo.previous(),
        act: () => vo.act(),
        press: (key) => vo.press(key),
        nextHeading: () => vo.perform(vo.keyboardCommands.findNextHeading),
        phrases: () => vo.spokenPhraseLog(),
    };
}

test('superdesk', async ({page, voiceOver}) => {
    await superdeskFlow(page, voiceOverDriver(page, voiceOver), path.join(OUT, 'superdesk.txt'));
});

test('newshub', async ({page, voiceOver}) => {
    await newshubFlow(page, voiceOverDriver(page, voiceOver), path.join(OUT, 'newshub.txt'));
});
