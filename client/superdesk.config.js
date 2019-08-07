/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: [
            'superdesk-publisher'
        ],
        importApps: [
            'superdesk-publisher'
        ],
        defaultRoute: '/workspace/personal',
        validatorMediaMetadata: {
            headline: {
                required: true
            },
            alt_text: {
                required: true
            },
            description_text: {
                required: true
            },
            copyrightholder: {
                required: false
            },
            byline: {
                required: false
            },
            usageterms: {
                required: false
            },
            copyrightnotice: {
                required: false
            }
        },

        publisher: {
            protocol: 'https',
            tenant: process.env.PUBLISHER_API_SUBDOMAIN || '',
            domain: process.env.PUBLISHER_API_DOMAIN || 'localhost',
            base: 'api/v2',
            wsDomain: process.env.PUBLISHER_WS_DOMAIN || process.env.PUBLISHER_API_DOMAIN,
            wsPath: process.env.PUBLISHER_WS_PATH || '',
            wsPort: process.env.PUBLISHER_WS_PORT || '8080'
        },

        langOverride: {
            'en': {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY'
            }
        },

        features: {
            preview: 1,
            swimlane: {columnsLimit: 4},
            editor3: true,
            editorHighlights: true,
            nestedItemsInOutputStage: true,
        },
        workspace: {
            analytics: true
        }
    };
};
