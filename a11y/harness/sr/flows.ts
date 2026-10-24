/*
 * Screen reader flows shared by voiceover.spec.ts, nvda.spec.ts and virtual-sr.spec.ts.
 *
 * Each flow drives the page the way a screen reader user would (Tab, Enter, Space, the reader's own
 * "next item" and "next heading" commands) through a `Driver`, and records what the reader says at every
 * step in a `Transcript`. Text is typed into fields with Playwright so passwords never pass through the
 * reader's echo; every phrase is also redacted against the passwords before it is written.
 */
import {Page} from '@playwright/test';
import fs from 'fs';
import path from 'path';
import {accounts, baseUrl, closeItem, env, readOnlyGuard, tid} from '../lib/instance';

export type Driver = {
    name: string;
    // Puts the reader on the web content. Called after the first page load and after full page loads.
    begin: (page: Page) => Promise<void>;
    next: () => Promise<void>;
    previous: () => Promise<void>;
    press: (key: string) => Promise<void>;
    // Sends the key to the page without the reader acting on it first. Only for readers that turn some keys into
    // their own commands (NVDA's browse mode turns Enter into a click), so a flow can retry the page's own handling.
    pressThrough?: (key: string) => Promise<void>;
    act: () => Promise<void>;
    nextHeading: () => Promise<void>;
    // Everything spoken so far, in order.
    phrases: () => Promise<Array<string>>;
    // Pause after a key press so the reader has finished speaking before the log is read.
    settleMs: number;
};

type Step = {label: string; phrases: Array<string>; notes: Array<string>; error?: string};

// Short passwords (such as a deployment default) would redact ordinary words, so only real passwords are matched.
const secrets = () => Object.values(accounts).map((a) => a.pass).filter((p) => p.length >= 8);

function redact(text: string) {
    return secrets().reduce((t, s) => t.split(s).join('<password>'), text);
}

// Phrases that are only a role with no name, as each reader words them.
const UNNAMED = /^(button|link|clickable|edit text|textbox|text field|edit|checkbox|check box|combo box|combobox|menu item|tab|image|group|unlabelled|unlabeled)[,.]?\s*(button|link)?$/i;

export class Transcript {
    steps: Array<Step> = [];
    private current: Step | null = null;

    constructor(private driver: Driver, private file: string) {}

    note(text: string) {
        this.current?.notes.push(text);
    }

    async step(label: string, fn: () => Promise<void>) {
        const before = (await this.driver.phrases()).length;
        const step: Step = {label, phrases: [], notes: []};

        this.current = step;

        try {
            await fn();
        } catch (e) {
            step.error = String((e as Error).message ?? e).split('\n')[0];
        }

        const all = await this.driver.phrases();

        step.phrases = all.slice(before).map(redact);

        if (step.phrases.length === 0) {
            step.notes.push('FLAG: nothing was spoken in this step');
        }

        for (const p of step.phrases) {
            if (UNNAMED.test(p.trim())) {
                step.notes.push(`FLAG: unnamed element spoken as "${p.trim()}"`);
            }
        }

        this.steps.push(step);
        this.current = null;
        this.write();

        if (step.error != null) {
            throw new Error(`${label}: ${step.error}`);
        }
    }

    write() {
        const lines = [`# ${path.basename(this.file, '.txt')} (${this.driver.name}, ${new Date().toISOString()})`, ''];

        this.steps.forEach((s, i) => {
            lines.push(`## ${i + 1}. ${s.label}`);
            s.phrases.forEach((p) => lines.push(`  > ${p}`));
            s.notes.forEach((n) => lines.push(`  ! ${redact(n)}`));

            if (s.error != null) {
                lines.push(`  ! ERROR: ${redact(s.error)}`);
            }

            lines.push('');
        });
        fs.mkdirSync(path.dirname(this.file), {recursive: true});
        fs.writeFileSync(this.file, lines.join('\n'));
    }
}

type Focused = {tag: string; name: string; title: string; testId: string | null; id: string; cls: string; label: string; role: string | null; checked: boolean | null};

async function focused(page: Page): Promise<Focused> {
    return page.evaluate(() => {
        const el = document.activeElement as HTMLElement | null;

        if (el == null) {
            return {tag: 'none', name: '', title: '', testId: null, id: '', cls: '', label: '', role: null, checked: null};
        }

        const input = el as HTMLInputElement;
        const label = el.getAttribute('aria-label')
            || (input.labels != null && input.labels.length > 0 ? input.labels[0].textContent : null)
            || el.textContent?.trim() || el.querySelector('[aria-label]')?.getAttribute('aria-label') || '';

        return {
            tag: el.tagName.toLowerCase(),
            name: input.name ?? '',
            title: el.getAttribute('title') ?? el.querySelector('[title]')?.getAttribute('title') ?? '',
            testId: el.getAttribute('data-test-id'),
            id: el.id,
            cls: String(el.className ?? ''),
            label: label.replace(/\s+/g, ' ').trim().slice(0, 80),
            role: el.getAttribute('role'),
            checked: input.type === 'checkbox' ? input.checked : null,
        };
    });
}

const describeFocus = (f: Focused) => `${f.tag}${f.role ? `[role=${f.role}]` : ''}${f.testId ? `[data-test-id=${f.testId}]` : ''} "${f.label.slice(0, 50)}"`;

// Presses Tab through the reader until the focused element matches, recording what is said on the way.
async function tabUntil(page: Page, sr: Driver, t: Transcript, match: (f: Focused) => boolean, max: number, what: string, key = 'Tab') {
    for (let i = 0; i < max; i++) {
        await sr.press(key);
        await page.waitForTimeout(sr.settleMs);
        const f = await focused(page);

        if (match(f)) {
            t.note(`focus reached ${what} after ${i + 1} ${key} presses: ${describeFocus(f)}`);

            return f;
        }
    }

    throw new Error(`${what} not reached after ${max} ${key} presses (focus is on ${describeFocus(await focused(page))})`);
}

async function flagFocusLoss(page: Page, t: Transcript, after: string) {
    const f = await focused(page);

    t.note(`after ${after}, focus is on ${describeFocus(f)}`);

    if (f.tag === 'body' || f.tag === 'none') {
        t.note(`FLAG: focus is lost to the page body after ${after}`);
    }
}

async function readNext(page: Page, sr: Driver, count: number) {
    for (let i = 0; i < count; i++) {
        await sr.next();
    }
}

async function nextUntil(sr: Driver, pattern: RegExp, max: number, move: () => Promise<void>) {
    for (let i = 0; i < max; i++) {
        await move();
        const all = await sr.phrases();

        if (pattern.test(all[all.length - 1] ?? '')) {
            return true;
        }
    }

    return false;
}

// Superdesk, reviewer: log in, go to Monitoring, open the first item in Review Pending, read it, close it.
export async function superdeskFlow(page: Page, sr: Driver, file: string) {
    const t = new Transcript(sr, file);
    const blocked: Array<string> = [];
    const a = accounts.reviewer;
    const reviewItem = env('SD_REVIEW_ITEM');

    await readOnlyGuard(page, blocked);

    try {
        await t.step('Login page, read from the top', async () => {
            await page.goto(baseUrl('sd') + '/');
            await page.locator('[data-test-id="login-page"] [data-test-id="username"]').waitFor({timeout: 60000});
            await page.waitForTimeout(1000);
            await sr.begin(page);
            await readNext(page, sr, 8);
        });

        await t.step('Tab to the username field (typed with Playwright)', async () => {
            await tabUntil(page, sr, t, (f) => f.testId === 'username', 6, 'the username field');
            await page.locator('[data-test-id="login-page"] [data-test-id="username"]').fill(a.user);
        });

        await t.step('Tab to the password field (typed with Playwright)', async () => {
            await tabUntil(page, sr, t, (f) => f.testId === 'password', 4, 'the password field');
            await page.locator('[data-test-id="login-page"] [data-test-id="password"]').fill(a.pass);
        });

        await t.step('Press Enter to log in', async () => {
            await sr.press('Enter');
            await page.locator(tid('my-profile')).waitFor({timeout: 90000});
            await page.waitForTimeout(4000);
            t.note(`after login, focus is on ${describeFocus(await focused(page))}`);
        });

        await t.step('Tab to Monitoring in the left navigation and press Enter', async () => {
            await sr.begin(page);
            await tabUntil(page, sr, t, (f) => f.testId === 'Monitoring' || (f.tag === 'a' && /^monitoring$/i.test(f.label)), 20, 'the Monitoring link');
            await sr.press('Enter');
            await page.locator(tid('article-item')).first().waitFor({timeout: 60000});
            await page.waitForTimeout(sr.settleMs);
        });

        await t.step('Tab to the first item in Review Pending', async () => {
            const f = await tabUntil(page, sr, t, (x) => x.testId === 'article-item', 60, 'the first monitoring item');

            if (f.id !== reviewItem) {
                t.note(`FLAG: the first focused item is ${f.id}, expected the Review Pending item ${reviewItem}`);
            }
        });

        await t.step('Press Enter to open it in the editor', async () => {
            const editor = page.locator(tid('authoring'));
            const opens = (timeout: number) => editor.waitFor({timeout}).then(() => true, () => false);

            await sr.press('Enter');

            if (!await opens(sr.pressThrough != null ? 15000 : 30000)) {
                if (sr.pressThrough == null) {
                    throw new Error('the editor did not open after Enter');
                }

                t.note(`FLAG: Enter through the reader does not open the editor (focus is on ${describeFocus(await focused(page))}); pressed Enter again, passed straight through to the page`);
                await sr.pressThrough('Enter');

                if (!await opens(30000)) {
                    throw new Error('the editor did not open after Enter passed through to the page');
                }
            }

            await page.waitForTimeout(Math.max(2000, sr.settleMs));
            const f = await focused(page);

            t.note(`after opening, focus is on ${describeFocus(f)}`);

            if (f.testId === 'article-item') {
                t.note('FLAG: focus stays on the list item; the editor opens without moving focus or announcing itself');
            }
        });

        await t.step('Move by headings to the editor, then read the title and the first field labels', async () => {
            const found = await nextUntil(sr, /authoring/i, 25, () => sr.nextHeading());

            if (!found) {
                t.note('FLAG: the "Authoring" heading was not reached with the next-heading command');
            }

            await readNext(page, sr, 30);
        });

        await t.step('Move back to the Close button and activate it', async () => {
            const found = await nextUntil(sr, /\bclose\b/i, 80, () => sr.previous());

            if (found) {
                await sr.act();
            } else {
                t.note('FLAG: Close was not reached with the next-item command; closed with Playwright instead');
                await closeItem(page, reviewItem);
            }

            await page.locator(tid('authoring')).waitFor({state: 'hidden', timeout: 15000});
            await flagFocusLoss(page, t, 'closing the editor');
        });
    } finally {
        await closeItem(page, reviewItem);

        if (blocked.length > 0) {
            t.steps.push({label: 'Writes blocked by the read-only guard', phrases: [], notes: blocked});
        }

        t.write();
    }
}

// Newshub, partner: log in, open the wire filters, filter by one local authority, open the first item,
// reach the download control, close the item.
export async function newshubFlow(page: Page, sr: Driver, file: string) {
    const t = new Transcript(sr, file);
    const blocked: Array<string> = [];
    const a = accounts.partner;
    const authority = env('NH_FILTER_AUTHORITY', 'Kirklees Council');

    await readOnlyGuard(page, blocked);

    try {
        await t.step('Login page, read from the top', async () => {
            await page.goto(baseUrl('nh') + '/login');
            await page.locator('input[name="email"]').waitFor({timeout: 60000});
            await sr.begin(page);
            await readNext(page, sr, 8);
        });

        await t.step('Tab to the e-mail field (typed with Playwright)', async () => {
            await tabUntil(page, sr, t, (f) => f.name === 'email', 8, 'the e-mail field');
            await page.locator('input[name="email"]').fill(a.user);
        });

        await t.step('Tab to the password field (typed with Playwright)', async () => {
            await tabUntil(page, sr, t, (f) => f.name === 'password', 4, 'the password field');
            await page.locator('input[name="password"]').fill(a.pass);
        });

        await t.step('Press Enter to log in', async () => {
            await sr.press('Enter');
            await page.waitForURL((u) => !/\/login/.test(u.pathname), {timeout: 60000});
            await page.waitForLoadState('networkidle');
            await page.waitForTimeout(2000);
        });

        await t.step('Tab to Wire in the side navigation and press Enter', async () => {
            await sr.begin(page);
            await tabUntil(page, sr, t, (f) => /^wire$/i.test(f.label), 15, 'the Wire link');
            await sr.press('Enter');
            await page.waitForURL(/\/wire/, {timeout: 30000});
            await page.waitForLoadState('networkidle');
            await page.waitForTimeout(2000);
        });

        await t.step('Open the filter panel and the Filters tab', async () => {
            await sr.begin(page);
            const f = await tabUntil(page, sr, t, (x) => /filter panel/i.test(x.label), 15, 'the filter panel button');

            if (/open filter panel/i.test(f.label)) {
                await sr.press('Enter');
                await page.waitForTimeout(sr.settleMs + 1000);
            } else {
                t.note('the filter panel was already open');
            }

            const tab = page.getByRole('tab', {name: 'Filters'});

            if (await tab.getAttribute('aria-selected') !== 'true') {
                await tabUntil(page, sr, t, (x) => x.role === 'tab' && /^filters$/i.test(x.label), 10, 'the Filters tab');
                await sr.press('Enter');
                await page.waitForTimeout(sr.settleMs + 1000);
            }
        });

        await t.step(`Tab to the "${authority}" checkbox and press Space`, async () => {
            await tabUntil(page, sr, t, (x) => x.tag === 'input' && x.label.includes(authority), 30, `the ${authority} checkbox`);
            const before = await page.locator('.wire-articles__item-headline-inner').allInnerTexts();

            await sr.press('Space');
            await page.waitForTimeout(2000 + sr.settleMs);
            const f = await focused(page);
            const after = await page.locator('.wire-articles__item-headline-inner').allInnerTexts();

            t.note(`checkbox checked after Space: ${f.checked}; results changed: ${JSON.stringify(before) !== JSON.stringify(after)}`);
        });

        await t.step('Tab to the Search button in the filter panel and press Enter to apply the filter', async () => {
            await tabUntil(page, sr, t, (x) => x.tag === 'button' && /^search$/i.test(x.label), 25, 'the filter Search button');
            await sr.press('Enter');
            await page.waitForLoadState('networkidle');
            await page.waitForTimeout(2000 + sr.settleMs);
            const results = await page.locator('.wire-articles__item-headline-inner').allInnerTexts();
            const off = results.filter((r) => !r.toUpperCase().startsWith(authority.toUpperCase()));

            t.note(`${results.length} results after applying; ${off.length} do not start with "${authority}"`);
            t.note('the result change is announced only if a phrase above says so (Newshub has no live region on the wire page)');
        });

        // Space is not tried: on a result it toggles the result's selection checkbox.
        await t.step('Tab to the first result and press Enter to open it', async () => {
            await tabUntil(page, sr, t, (x) => x.cls.includes('wire-articles__item'), 40, 'the first result');
            const open = page.locator('.wire-column__preview--open');

            await sr.press('Enter');
            await page.waitForTimeout(2000 + sr.settleMs);

            if (await open.count() === 0 && sr.pressThrough != null) {
                t.note('FLAG: Enter through the reader does not open the focused result; pressed Enter again, passed straight through to the page');
                await sr.pressThrough('Enter');
                await page.waitForTimeout(2000 + sr.settleMs);
            }

            if (await open.count() === 0) {
                t.note('FLAG: Enter on the focused result does not open it');
                t.note('FLAG: the item cannot be opened from the keyboard; opened with a mouse click so the flow can continue');
                await page.locator('.wire-articles__item').first().click();
                await page.waitForTimeout(2000 + sr.settleMs);
            }

            t.note(`after opening, focus is on ${describeFocus(await focused(page))}`);
        });

        await t.step('Tab to the Download control', async () => {
            await tabUntil(page, sr, t, (x) => /^download/i.test(x.label), 30, 'the Download button');
        });

        await t.step('Close the item (Escape, then the Close button if Escape does nothing)', async () => {
            const preview = page.locator('.wire-column__preview--open');
            const openBefore = await preview.count();

            await sr.press('Escape');
            await page.waitForTimeout(1000 + sr.settleMs);

            if (openBefore > 0 && await preview.count() >= openBefore) {
                t.note('FLAG: Escape did not close the item');
                await tabUntil(page, sr, t, (x) => x.tag === 'button' && /close/i.test(`${x.label} ${x.title} ${x.cls}`) && !/filter/i.test(x.label), 12, 'the preview Close button', 'Shift+Tab');
                await sr.press('Enter');
                await page.waitForTimeout(1000 + sr.settleMs);
            }

            await flagFocusLoss(page, t, 'closing the item');
        });
    } finally {
        if (blocked.length > 0) {
            t.steps.push({label: 'Writes blocked by the read-only guard', phrases: [], notes: blocked});
        }

        t.write();
    }
}
