/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function() {
    return {
        apps: [
            'superdesk-planning',
            'superdesk.analytics',
            'superdesk-publisher',
        ],
        importApps: [
            '../index',
            'superdesk-planning',
            'superdesk-analytics',
            'superdesk-publisher',
        ],

        defaultRoute: '/workspace/monitoring',

        langOverride: {
            en: {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY',
                'multi-line quote': 'pullquote',
                'Multi-line quote': 'Pullquote',
            }
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

        editor3: { browserSpellCheck: true, },

        search_cvs: [
            {id: 'topics', name:'Topics', field: 'subject', list: 'topics'},
            {id: 'language', name:'Language', field: 'language', list: 'languages'}
        ],

        features: {
            preview: 1,
            swimlane: {columnsLimit: 99},
            swimlane: {defaultNumberOfColumns: 4},
            editor3: true,
            editorHighlights: true,
            noPublishOnAuthoringDesk: true,
            customAuthoringTopbar: {
                toDesk: true,
                publish: true,
            },
            validatePointOfInterestForImages: true,
            editorHighlights: true,
            editFeaturedImage: true,
            searchShortcut: true,
            elasticHighlight: true,
            planning: true,
            autorefreshContent: true,
            nestedItemsInOutputStage: true,
            planning: true,
            customAuthoringTopbar: {
                toDesk: true,
            },
        },

        item_profile: { change_profile: 1 },

        workspace: {
            analytics: true,
            assignments: true,
            planning: true,
        },

        ui: {
            italicAbstract: false,
            },

        list: {
            priority: [
                'urgency'
            ],
            firstLine: [
                'headline',
                'highlights',
                'markedDesks',
                'associatedItems',
                'versioncreated'
            ],
            secondLine: [
                'state',
                'update',
                'scheduledDateTime',
                'flags',
                'updated',
                'provider',
                'desk',
                'fetchedDesk',
                'used',
                'nestedlink',
                'translations'
            ]
        },

        monitoring: {
            scheduled: {
                sort: {
                    default: { field: 'publish_schedule', order: 'asc' },
                    allowed_fields_to_sort: [ 'publish_schedule' ]
                }
            },
        },

        publisher: {
            protocol: 'https',                /* http or https */
            tenant: '',              /* tenant - semantically subdomain, '' is allowed */
            domain: 'sp-publisher.superdesk.pro',           /* domain name for the publisher */
            base: 'api/v2',                  /* api base path */

            wsProtocol: 'wss',                /* ws or wss (websocket); if unspecified or '' defaults to 'wss' */
            wsDomain: 'sp-publisher.superdesk.pro',  /* domain name (usually domain as above) */
                                            /* e.g.: example.com, abc.example.com */
                                            /* tenant, as above, is NOT used for websocket */
            wsPath: '/ws',                    /* path to websocket root dir */
            wsPort: '80',                   /* if not specified: defaults to 443 for wss, 80 for ws */
            hideContentRoutesInPublishPane: false, /* hides routes of type "content" from select box in publish panes in monitoring view as well as in output control. If not specified: defaults to false */
            hideCustomRoutesInPublishPane: false   /* hides routes of type "custom" from select box in publish panes in monitoring view as well as in output control. If not specified: defaults to false */
        },
    };
};
