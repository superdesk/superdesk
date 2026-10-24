/*
 * WCAG 2.2 AA automated sweep for a running Superdesk + Newshub instance pair.
 * See README.md in this folder for the environment variables, how to run it and what each output file means.
 *
 * Run (from this folder):
 *   SD_URL=... NH_URL=... SD_USER_REPORTER=... SD_PASS_REPORTER=... (all variables below) \
 *   npx playwright test a11y.spec.ts --workers 1 --reporter list
 * Output: ./out/<role>/<page>/{axe.json,checks.json,*.png}, ./out/summary-by-sc.json, ./out/summary-checks.json
 *
 * The run is read only: see `readOnlyGuard` in lib/instance.ts. Blocked requests are listed in checks.json.
 */
import {test, Browser, BrowserContext, Page} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'fs';
import path from 'path';
import {App, baseUrl, closeItem, env, fillLogin, openItem, readOnlyGuard, tid} from './lib/instance';

type Target = {
    role: string;
    app: App;
    name: string;
    path: string;
    prepare?: (page: Page) => Promise<void>;
    cleanup?: (page: Page) => Promise<void>;
};

const OUT = path.join(__dirname, 'out');

test.describe.configure({timeout: 180000});

// ---------------------------------------------------------------------------------------------
// Superdesk helpers

const openPanel = (tab: 'Publish' | 'Send to') => async (page: Page) => {
    await openItem(page, env('SD_REVIEW_ITEM'));
    const open = page.locator(`${tid('authoring')} ${tid('open-send-publish-pane')}`);

    // Hidden when the item opens read only, which happens when another session holds its lock.
    await open.waitFor({state: 'visible', timeout: 20000}).catch(() => {
        throw new Error('Send to / Publish is not available: the item opened read only (locked by another session?)');
    });
    await open.click();
    const panel = page.locator(tid('interactive-actions-panel'));

    await panel.waitFor({timeout: 15000});
    await panel.locator(tid('tabs')).getByRole('tab', {name: tab, exact: true}).click().catch(() => undefined);
    await page.waitForTimeout(1500);
};

// ---------------------------------------------------------------------------------------------
// Newshub helpers

async function openProfileMenu(page: Page, entry: string) {
    // The avatar is a <figure>, not a button, so the menu can only be opened by mouse.
    await page.locator('.header-profile figure, .header-profile').first().click();
    await page.getByRole('link', {name: entry, exact: true}).click();
    await page.getByRole('heading', {name: entry, exact: true}).first().waitFor({timeout: 15000});
    await page.waitForTimeout(1000);
}

// ---------------------------------------------------------------------------------------------
// Targets. `prepare` opens a dialog or panel before the scan, `cleanup` closes it without acting.

const sampleItem = env('SD_SAMPLE_ITEM');
const reviewItem = env('SD_REVIEW_ITEM');

const targets: Target[] = [
    {role: 'reporter', app: 'sd', name: 'login', path: '/'},
    {role: 'reporter', app: 'sd', name: 'monitoring', path: '/#/workspace/monitoring'},
    {role: 'reporter', app: 'sd', name: 'personal-space', path: '/#/workspace/personal'},
    {
        role: 'reporter', app: 'sd', name: 'authoring-open-story', path: '/#/workspace/monitoring',
        prepare: (page) => openItem(page, sampleItem),
        cleanup: (page) => closeItem(page, sampleItem),
    },
    {
        role: 'reporter', app: 'sd', name: 'authoring-media-upload', path: '/#/workspace/monitoring',
        prepare: async (page) => {
            await openItem(page, sampleItem);
            await page.locator(tid('authoring')).getByRole('button', {name: 'Media', exact: true}).first().click();
            await page.locator(tid('multi-image-edit--cancel-upload')).waitFor({timeout: 15000});
            await page.waitForTimeout(1000);
        },
        cleanup: (page) => closeItem(page, sampleItem),
    },
    {role: 'reporter', app: 'sd', name: 'search', path: '/#/search'},
    {role: 'reviewer', app: 'sd', name: 'monitoring', path: '/#/workspace/monitoring'},
    {
        role: 'reviewer', app: 'sd', name: 'authoring-review', path: '/#/workspace/monitoring',
        prepare: (page) => openItem(page, reviewItem),
        cleanup: (page) => closeItem(page, reviewItem),
    },
    {
        role: 'reviewer', app: 'sd', name: 'send-to-panel', path: '/#/workspace/monitoring',
        prepare: openPanel('Send to'),
        cleanup: (page) => closeItem(page, reviewItem),
    },
    {
        role: 'reviewer', app: 'sd', name: 'publish-panel', path: '/#/workspace/monitoring',
        prepare: openPanel('Publish'),
        cleanup: (page) => closeItem(page, reviewItem),
    },
    // User management lives at /#/users/; /#/settings/users renders an empty page.
    {role: 'orgadmin', app: 'sd', name: 'users', path: '/#/users/'},
    {
        role: 'orgadmin', app: 'sd', name: 'user-edit', path: '/#/users/',
        prepare: async (page) => {
            const items = page.locator(`${tid('users-list')} ${tid('users-list-item')}`);

            await items.first().waitFor({timeout: 30000});
            const other = items.filter({hasNotText: env('SD_USER_ORGADMIN')});

            await ((await other.count()) > 0 ? other.first() : items.first()).click();
            await page.locator(tid('view-full-profile')).click();
            await page.locator(tid('user-details-form')).waitFor({timeout: 15000});
            await page.waitForTimeout(1000);
        },
    },
    {role: 'orgadmin', app: 'sd', name: 'desks', path: '/#/settings/desks'},
    {role: 'sysadmin', app: 'sd', name: 'vocabularies', path: '/#/settings/vocabularies'},
    {role: 'sysadmin', app: 'sd', name: 'content-profiles', path: '/#/settings/content-profiles'},
    {
        role: 'sysadmin', app: 'sd', name: 'content-profile-editor', path: '/#/settings/content-profiles',
        prepare: async (page) => {
            await page.locator(`${tid('content-profile')}[data-test-value="Story"] ${tid('content-profile-actions')}`).click();
            await page.locator(tid('content-profile-actions--options')).getByRole('button', {name: 'Edit'}).click();
            await page.locator(tid('content-profile-editing-modal')).waitFor({timeout: 15000});
            await page.waitForTimeout(1500);
        },
        cleanup: async (page) => {
            await page.locator(tid('content-profile-editing-modal')).getByRole('button', {name: 'Cancel'}).first()
                .click({timeout: 5000}).catch(() => undefined);
        },
    },
    {role: 'sysadmin', app: 'sd', name: 'templates', path: '/#/settings/templates'},
    {role: 'sysadmin', app: 'sd', name: 'roles', path: '/#/settings/user-roles'},
    {role: 'partner', app: 'nh', name: 'login', path: '/login'},
    {role: 'partner', app: 'nh', name: 'wire-home', path: '/wire'},
    {role: 'partner', app: 'nh', name: 'wire-item', path: '/wire?item=' + env('NH_SAMPLE_ITEM')},
    {
        role: 'partner', app: 'nh', name: 'item-download', path: '/wire?item=' + env('NH_SAMPLE_ITEM'),
        prepare: async (page) => {
            await page.getByRole('dialog', {name: 'Item Detail'}).getByRole('button', {name: 'Download'}).click();
            await page.getByRole('dialog', {name: 'Download Items'}).waitFor({timeout: 15000});
            await page.waitForTimeout(800);
        },
        cleanup: async (page) => {
            await page.getByRole('dialog', {name: 'Download Items'}).getByRole('button', {name: 'Cancel'})
                .click({timeout: 5000}).catch(() => undefined);
        },
    },
    {role: 'partner', app: 'nh', name: 'saved', path: '/bookmarks_wire'},
    {role: 'partner', app: 'nh', name: 'my-topics', path: '/wire', prepare: (page) => openProfileMenu(page, 'My Wire Topics')},
    {
        role: 'partner', app: 'nh', name: 'profile', path: '/wire',
        prepare: (page) => openProfileMenu(page, 'My Profile'),
        cleanup: async (page) => {
            await page.getByRole('button', {name: 'Cancel', exact: true}).first().click({timeout: 5000}).catch(() => undefined);
        },
    },
    // The partner account gets 403 on /company_admin, so the company admin users page is not scanned (see README).
    {role: 'nhadmin', app: 'nh', name: 'companies', path: '/settings/companies'},
    {role: 'nhadmin', app: 'nh', name: 'products', path: '/settings/products'},
];

// ---------------------------------------------------------------------------------------------
// Sessions: each role logs in once per worker; later targets reuse the storage state (kept in memory only).

const sessions: Record<string, Awaited<ReturnType<BrowserContext['storageState']>>> = {};

async function contextFor(browser: Browser, t: Target): Promise<BrowserContext> {
    if (t.name === 'login') {
        return browser.newContext();
    }

    if (sessions[t.role] == null) {
        const ctx = await browser.newContext();
        await fillLogin(await ctx.newPage(), t.role);
        sessions[t.role] = await ctx.storageState();
        await ctx.close();
    }

    return browser.newContext({storageState: sessions[t.role]});
}

async function axeScan(page: Page) {
    return new AxeBuilder({page})
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
        .analyze();
}

// ---------------------------------------------------------------------------------------------
// Scripted checks for criteria axe does not cover. Results are signals for a human, not verdicts.

// Runs in the page: colour, name and visibility helpers shared by the checks and the Tab walk.
function installPageHelpers() {
    const w = window as any;

    if (w.__a11y != null) {
        return;
    }

    const parse = (c: string | null): [number, number, number, number] | null => {
        if (c == null) {
            return null;
        }

        const m = c.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)/);

        if (m == null) {
            return null;
        }

        const a = m[4] == null ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : parseFloat(m[4]);

        return [+m[1], +m[2], +m[3], a];
    };
    const over = (fg: number[], bg: number[]) => [0, 1, 2].map((i) => fg[i] * fg[3] + bg[i] * (1 - fg[3])).concat(1);
    const lum = (c: number[]) => {
        const f = (v: number) => {
            const s = v / 255;

            return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
        };

        return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
    };
    const ratio = (a: number[], b: number[]) => {
        const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);

        return Math.round(((x + 0.05) / (y + 0.05)) * 100) / 100;
    };
    // Effective background behind `el`, compositing translucent layers up to the white canvas.
    const background = (el: Element | null) => {
        const layers: number[][] = [];
        let image = false;

        for (let n = el; n != null && n.nodeType === 1; n = n.parentElement) {
            const cs = getComputedStyle(n);
            const c = parse(cs.backgroundColor);

            if (cs.backgroundImage !== 'none') {
                image = true;
            }

            if (c != null && c[3] > 0) {
                layers.push(c);

                if (c[3] >= 1) {
                    break;
                }
            }
        }

        let result = [255, 255, 255, 1];

        for (const l of layers.reverse()) {
            result = over(l, result);
        }

        return {color: result, image};
    };
    const name = (el: Element) => {
        const labelledby = el.getAttribute('aria-labelledby');
        const byIds = labelledby == null ? '' : labelledby.split(/\s+/).map((id) => document.getElementById(id)?.textContent ?? '').join(' ');
        const img = el.querySelector('img[alt]');
        const raw = el.getAttribute('aria-label') || byIds || (el as HTMLElement).innerText || el.textContent
            || el.getAttribute('title') || (el as HTMLInputElement).placeholder || (el as HTMLInputElement).value || img?.getAttribute('alt') || '';

        return raw.replace(/\s+/g, ' ').trim().slice(0, 60);
    };
    const describe = (el: Element) => ({
        tag: el.tagName.toLowerCase(),
        role: el.getAttribute('role'),
        name: name(el),
        testId: el.getAttribute('data-test-id'),
        cls: (el.getAttribute('class') ?? '').slice(0, 60),
    });
    const visible = (el: Element) => {
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);

        return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && el.closest('[aria-hidden="true"], [inert]') == null;
    };
    // Colour of the focus indicator (outline first, then the first box-shadow) and its contrast with what surrounds it.
    const focusRing = (el: Element) => {
        const cs = getComputedStyle(el);
        let ring: number[] | null = null;
        let source = 'none';
        let inset = false;
        let raw = '';

        if (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) {
            ring = parse(cs.outlineColor);
            source = 'outline';
            raw = cs.outlineColor;
        } else if (cs.boxShadow !== 'none') {
            const first = cs.boxShadow.split(/,(?![^(]*\))/)[0];

            ring = parse(first);
            inset = /inset/.test(first);
            source = inset ? 'box-shadow inset' : 'box-shadow';
            raw = first.trim();
        }

        // A fully transparent shadow or outline draws nothing.
        if (ring == null || ring[3] === 0) {
            return {source: ring == null ? source : 'none', color: raw || null, background: null, contrast: null};
        }

        const bg = background(inset ? el : el.parentElement);
        const effective = over(ring, bg.color);
        const fmt = (c: number[]) => `rgb(${c.slice(0, 3).map((v) => Math.round(v)).join(',')})`;

        return {
            source,
            color: raw,
            background: fmt(bg.color) + (bg.image ? ' (background image present)' : ''),
            contrast: ratio(effective, bg.color),
        };
    };

    w.__a11y = {describe, visible, focusRing, name};
}

async function pageChecks(page: Page) {
    return page.evaluate(() => {
        const {describe, visible} = (window as any).__a11y;
        const out: Record<string, unknown> = {};

        // 2.5.8 Target size (minimum): interactive elements under 24 x 24 CSS px, with the spacing and inline exceptions.
        const interactive = [...document.querySelectorAll<HTMLElement>(
            'a[href], button, input:not([type="hidden"]), select, textarea, summary, [role="button"], [role="link"], [role="tab"], '
            + '[role="menuitem"], [role="checkbox"], [role="radio"], [role="switch"], [role="option"], [tabindex]:not([tabindex="-1"])',
        )].filter((el) => {
            const r = el.getBoundingClientRect();

            // 1 px elements are the visually-hidden pattern (a styled checkbox's real input), not pointer targets.
            return visible(el) && !(el as HTMLButtonElement).disabled && r.width > 1 && r.height > 1;
        });
        const rects = interactive.map((el) => el.getBoundingClientRect());
        const small = interactive.map((el, i) => rects[i].width < 24 || rects[i].height < 24);
        const centre = (r: DOMRect) => [r.left + r.width / 2, r.top + r.height / 2];
        const distToRect = (p: number[], r: DOMRect) => Math.hypot(Math.max(r.left - p[0], 0, p[0] - r.right), Math.max(r.top - p[1], 0, p[1] - r.bottom));
        const undersized: Array<Record<string, unknown>> = [];

        interactive.forEach((el, i) => {
            if (!small[i]) {
                return;
            }

            const c = centre(rects[i]);
            const spacingOk = interactive.every((other, j) => {
                if (j === i || el.contains(other) || other.contains(el)) {
                    return true;
                }

                return small[j] ? Math.hypot(c[0] - centre(rects[j])[0], c[1] - centre(rects[j])[1]) >= 24 : distToRect(c, rects[j]) >= 12;
            });
            const parent = el.parentElement;
            const inline = getComputedStyle(el).display === 'inline' && parent != null
                && [...parent.childNodes].some((n) => n.nodeType === 3 && (n.textContent ?? '').trim().length > 0);

            undersized.push({...describe(el), width: Math.round(rects[i].width * 10) / 10, height: Math.round(rects[i].height * 10) / 10, spacingOk, inline});
        });
        out.targetSize = {
            interactiveCount: interactive.length,
            undersizedCount: undersized.length,
            failingCount: undersized.filter((u) => !u.spacingOk && !u.inline).length,
            undersized: undersized.slice(0, 200),
        };

        // 1.3.1 / 2.4.6 Headings outline in DOM order, as a screen reader lists them.
        const headings = [...document.querySelectorAll<HTMLElement>('h1, h2, h3, h4, h5, h6, [role="heading"]')]
            .filter((h) => h.closest('[aria-hidden="true"]') == null && getComputedStyle(h).display !== 'none' && getComputedStyle(h).visibility !== 'hidden')
            .map((h) => ({
                level: Number(h.getAttribute('aria-level') ?? (/^h\d$/i.test(h.tagName) ? h.tagName[1] : 2)),
                text: (h.innerText || h.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80),
                visible: h.getBoundingClientRect().width > 1,
            }));
        const issues: Array<string> = [];

        if (!headings.some((h) => h.level === 1)) {
            issues.push('no level 1 heading');
        }

        if (headings.filter((h) => h.level === 1).length > 1) {
            issues.push('more than one level 1 heading');
        }

        headings.forEach((h, i) => {
            if (h.text === '') {
                issues.push(`empty heading at position ${i} (level ${h.level})`);
            }

            if (i > 0 && h.level > headings[i - 1].level + 1) {
                issues.push(`skips from level ${headings[i - 1].level} to ${h.level} at "${h.text}"`);
            }
        });
        out.headings = {outline: headings, issues};

        // 1.3.1 / 2.4.1 Landmarks.
        const roleOf = (el: Element): string | null => {
            const explicit = el.getAttribute('role');

            if (explicit != null) {
                return explicit.split(/\s+/)[0];
            }

            const tag = el.tagName.toLowerCase();
            const sectioning = el.parentElement?.closest('article, aside, main, nav, section') != null;
            const named = el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby');

            return ({
                main: 'main', nav: 'navigation', aside: 'complementary', search: 'search',
                header: sectioning ? null : 'banner', footer: sectioning ? null : 'contentinfo',
                section: named ? 'region' : null, form: named ? 'form' : null,
            } as Record<string, string | null>)[tag] ?? null;
        };
        const landmarkRoles = ['main', 'navigation', 'banner', 'contentinfo', 'complementary', 'search', 'region', 'form'];
        const counts: Record<string, number> = Object.fromEntries(landmarkRoles.map((r) => [r, 0]));

        document.querySelectorAll('main, nav, aside, header, footer, section, form, search, [role]').forEach((el) => {
            const r = roleOf(el);

            if (r != null && landmarkRoles.includes(r) && el.closest('[aria-hidden="true"]') == null && getComputedStyle(el).display !== 'none') {
                counts[r]++;
            }
        });
        out.landmarks = {counts, missing: ['main', 'navigation', 'banner'].filter((r) => counts[r] === 0)};

        // 4.1.2 Controls that open a menu or panel should expose aria-expanded.
        const togglers = [...document.querySelectorAll<HTMLElement>(
            '[aria-haspopup]:not([aria-haspopup="false"]), .dropdown-toggle, .dropdown__toggle, [data-toggle="dropdown"], '
            + '[data-bs-toggle="dropdown"], [data-toggle="collapse"], [data-bs-toggle="collapse"], button[aria-controls], [role="button"][aria-controls]',
        )].filter(visible);
        const missingExpanded = togglers.filter((el) => !el.hasAttribute('aria-expanded'));

        out.ariaExpanded = {
            togglerCount: togglers.length,
            missingCount: missingExpanded.length,
            missing: missingExpanded.slice(0, 50).map((el) => ({...describe(el), haspopup: el.getAttribute('aria-haspopup')})),
        };

        // 1.3.5 Identify input purpose on login forms.
        if ([...document.querySelectorAll('input[type="password"]')].some(visible)) {
            const fields = [...document.querySelectorAll<HTMLInputElement>(
                'input[type="password"], input[type="email"], input[name*="user" i], input[name*="email" i], input[name*="login" i], input[id*="user" i]',
            )].filter(visible);

            out.loginAutocomplete = fields.map((f) => ({
                name: f.name || f.id, type: f.type, autocomplete: f.getAttribute('autocomplete'),
                ok: f.getAttribute('autocomplete') != null && !/^(off|on)$/i.test(f.getAttribute('autocomplete') ?? ''),
            }));
        }

        // 4.1.3 Live regions.
        const live = [...document.querySelectorAll<HTMLElement>('[aria-live], [role="status"], [role="alert"], [role="log"], output')];

        out.liveRegions = live.length;
        out.liveRegionDetails = live.slice(0, 30).map((el) => ({
            tag: el.tagName.toLowerCase(), role: el.getAttribute('role'), ariaLive: el.getAttribute('aria-live'),
            id: el.id || null, cls: (el.getAttribute('class') ?? '').slice(0, 60), text: (el.textContent ?? '').trim().slice(0, 60),
        }));

        return out;
    });
}

async function scriptedChecks(page: Page, dir: string) {
    const out: Record<string, unknown> = {};

    out.lang = await page.evaluate(() => document.documentElement.getAttribute('lang')); // 3.1.1
    out.title = await page.title(); // 2.4.2 (does it change per view?)
    await page.evaluate(installPageHelpers);
    Object.assign(out, await pageChecks(page));

    // 1.4.10 Reflow: 320 CSS px wide equals 1280 px at 400% zoom.
    const original = page.viewportSize() ?? {width: 1280, height: 720};
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

    // 2.1.1 / 2.1.2 / 2.4.3 / 2.4.7 / 2.4.11 / 2.4.13: walk the tab order and record what happens.
    const walk: Array<Record<string, unknown>> = [];
    await page.locator('body').click({position: {x: 1, y: 1}}).catch(() => undefined);

    for (let i = 0; i < 60; i++) {
        await page.keyboard.press('Tab');
        const info = await page.evaluate(() => {
            const el = document.activeElement as HTMLElement | null;

            if (el == null || el === document.body) {
                return {onBody: true};
            }

            const {focusRing} = (window as any).__a11y;
            const r = el.getBoundingClientRect();
            const cs = getComputedStyle(el);
            const points = [[r.left + r.width / 2, r.top + r.height / 2], [r.left + 1, r.top + 1], [r.right - 1, r.bottom - 1]];
            const covered = points.every(([x, y]) => {
                const top = document.elementFromPoint(x, y);

                return top != null && top !== el && !el.contains(top) && !top.contains(el);
            });
            const ring = focusRing(el);

            return {
                tag: el.tagName.toLowerCase(),
                role: el.getAttribute('role'),
                name: (el.getAttribute('aria-label') ?? el.textContent ?? '').trim().slice(0, 60),
                testId: el.getAttribute('data-test-id'),
                outline: cs.outlineStyle + ' ' + cs.outlineWidth,
                boxShadow: cs.boxShadow,
                ringSource: ring.source,
                ringColor: ring.color,
                ringBackground: ring.background,
                ringContrast: ring.contrast,
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
    // 1.4.11 / 2.4.13 signal: a focus ring below 3:1 against the colours around it.
    out.lowContrastFocusCount = walk.filter((w) => typeof w.ringContrast === 'number' && (w.ringContrast as number) < 3).length;

    return out;
}

// ---------------------------------------------------------------------------------------------

for (const t of targets) {
    test(`${t.role} / ${t.name}`, async ({browser}) => {
        const dir = path.join(OUT, t.role, t.name);
        fs.mkdirSync(dir, {recursive: true});

        for (const f of ['axe.json', 'checks.json']) {
            fs.rmSync(path.join(dir, f), {force: true});
        }

        const context = await contextFor(browser, t);
        const page = await context.newPage();
        const blocked: Array<string> = [];

        await readOnlyGuard(page, blocked);

        try {
            await page.goto(baseUrl(t.app) + t.path);
            await page.waitForLoadState('networkidle');

            if (t.app === 'sd' && t.name !== 'login') {
                await page.locator(tid('my-profile')).waitFor({timeout: 60000});
            }

            await page.waitForTimeout(1500); // SPA settle

            if (t.prepare != null) {
                await t.prepare(page);
            }

            const axe = await axeScan(page);
            fs.writeFileSync(path.join(dir, 'axe.json'), JSON.stringify(axe, null, 2));
            await page.screenshot({path: path.join(dir, 'page.png'), fullPage: true});

            const checks = await scriptedChecks(page, dir);

            checks.blockedWrites = blocked;
            fs.writeFileSync(path.join(dir, 'checks.json'), JSON.stringify(checks, null, 2));
        } finally {
            if (t.cleanup != null) {
                await t.cleanup(page).catch(() => undefined);
            }

            await context.close();
        }
    });
}

// Summaries are rebuilt from the files on disk so a worker restart after a failure does not drop earlier results.
test.afterAll(() => {
    const summary: Record<string, Array<{role: string; page: string; rule: string; impact: string | null | undefined; nodes: number}>> = {};
    const checks: Record<string, Record<string, unknown>> = {};
    const missing: Array<string> = [];

    for (const t of targets) {
        const dir = path.join(OUT, t.role, t.name);
        const axeFile = path.join(dir, 'axe.json');
        const checksFile = path.join(dir, 'checks.json');

        if (!fs.existsSync(axeFile)) {
            missing.push(`${t.role}/${t.name}`);
            continue;
        }

        const axe = JSON.parse(fs.readFileSync(axeFile, 'utf8'));

        for (const v of axe.violations) {
            const scs = v.tags.filter((x: string) => /^wcag\d{3,4}$/.test(x)).map((x: string) => x.replace(/^wcag(\d)(\d)(\d+)$/, '$1.$2.$3'));

            for (const sc of scs.length > 0 ? scs : ['best-practice']) {
                (summary[sc] ??= []).push({role: t.role, page: t.name, rule: v.id, impact: v.impact, nodes: v.nodes.length});
            }
        }

        if (fs.existsSync(checksFile)) {
            const c = JSON.parse(fs.readFileSync(checksFile, 'utf8'));

            checks[`${t.role}/${t.name}`] = {
                lang: c.lang,
                liveRegions: c.liveRegions,
                reflowHorizontalScroll: c.reflowHorizontalScroll,
                possibleTrap: c.possibleTrap,
                noVisibleOutlineCount: c.noVisibleOutlineCount,
                lowContrastFocusCount: c.lowContrastFocusCount,
                undersizedTargets: c.targetSize?.undersizedCount,
                failingTargets: c.targetSize?.failingCount,
                headingIssues: c.headings?.issues?.length,
                landmarksMissing: c.landmarks?.missing,
                ariaExpandedMissing: c.ariaExpanded?.missingCount,
                loginAutocompleteIssues: c.loginAutocomplete == null ? undefined : c.loginAutocomplete.filter((f: {ok: boolean}) => !f.ok).length,
                blockedWrites: c.blockedWrites?.length,
            };
        }
    }

    fs.mkdirSync(OUT, {recursive: true});
    fs.writeFileSync(path.join(OUT, 'summary-by-sc.json'), JSON.stringify(summary, null, 2));
    fs.writeFileSync(path.join(OUT, 'summary-checks.json'), JSON.stringify({pages: checks, missing}, null, 2));
});
