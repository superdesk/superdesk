/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 *
 * The file is required by node (webpack.config.js and build-tools) and the returned
 * object is serialised into the bundle as __SUPERDESK_CONFIG__, so anything reachable
 * from here has to be plain JSON-serialisable data.
 */

// Exact-match English replacements that turn newsroom vocabulary into Briefdesk vocabulary.
// Webpack only watches this file for cache invalidation, not the modules it requires, so a
// change to the terminology pack needs the build restarting (or `client/node_modules/.cache`
// removing) before it shows up.
const terminology = require('./briefdesk/terminology');

module.exports = function() {
    return {
        apps: [
            'superdesk-planning',
        ],
        importApps: [
            '../index',
            'superdesk-planning',
        ],

        defaultRoute: '/workspace/monitoring',

        langOverride: {
            en: Object.assign({}, terminology, {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY',
                'multi-line quote': 'pullquote',
                'Multi-line quote': 'Pullquote',
            }),
        },

        view: {
            timeformat: 'HH:mm',
            dateformat: 'DD.MM.YYYY',
        },

        shortTimeFormat: 'HH:mm, DD.MM.YYYY',
        shortDateFormat: 'HH:mm, DD.MM.YYYY',
        shortWeekFormat: 'HH:mm, DD.MM.YYYY',
        startingDay: '1',
        defaultTimezone: 'Europe/Prague',

        editor3: {browserSpellCheck: true},

        // Each entry adds a filter to the search panel. `list` is a vocabulary _id, `field` is the
        // item field the values are stored in, and `id` has to differ from `field` or no query
        // filter is built for it (SearchService.ts). Custom vocabularies land in `subject`, so the
        // Briefdesk taxonomies all filter on `subject.qcode`; their qcodes do not overlap.
        search_cvs: [
            {id: 'severity', name: 'Severity', field: 'subject', list: 'severity'},
            {id: 'threat_type', name: 'Threat type', field: 'subject', list: 'threat_type'},
            {id: 'region', name: 'Region', field: 'subject', list: 'region'},
            {id: 'sector', name: 'Sector', field: 'subject', list: 'sector'},
        ],

        features: {
            preview: 1,
            swimlane: {
                columnsLimit: 99,
                defaultNumberOfColumns: 4,
            },
            editor3: true,
            editorHighlights: true,
            editorInlineComments: true,
            editorSuggestions: true,
            editorAttachments: true,
            noPublishOnAuthoringDesk: true,
            sendToPersonal: true,
            customAuthoringTopbar: {
                toDesk: true,
                publish: true,
            },
            validatePointOfInterestForImages: true,
            editFeaturedImage: true,
            searchShortcut: true,
            elasticHighlight: true,
            planning: true,
            autorefreshContent: true,
            nestedItemsInOutputStage: false,
        },

        item_profile: {change_profile: 1},

        workspace: {
            planning: true,
            assignments: true,
            analytics: false,
        },

        ui: {
            italicAbstract: false,
        },

        // Only the field names registered in superdesk-client-core
        // (scripts/apps/search/components/fields/index.ts) render here; an unknown name is
        // silently dropped. Severity and region live in `subject` and have no field component,
        // so they cannot be shown in a row without an extension.
        list: {
            priority: [
                'urgency',
            ],
            firstLine: [
                'slugline',
                'headline',
                'highlights',
                'markedDesks',
                'associatedItems',
                'versioncreated',
            ],
            secondLine: [
                'profile',
                'state',
                'update',
                'scheduledDateTime',
                'embargo',
                'flags',
                'updated',
                'provider',
                'desk',
                'fetchedDesk',
                'used',
                'nestedlink',
                'translations',
            ],
            compactView: {
                firstLine: [
                    'slugline',
                    'headline',
                ],
                secondLine: [
                    'profile',
                    'state',
                ],
            },
        },

        monitoring: {
            scheduled: {
                sort: {
                    default: {field: 'publish_schedule', order: 'asc'},
                    allowed_fields_to_sort: ['publish_schedule'],
                },
            },
        },
    };
};
