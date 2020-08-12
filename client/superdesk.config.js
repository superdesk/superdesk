/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: [
            'superdesk-planning',
            'superdesk.analytics',
        ],
        importApps: [
            '../index',
            'superdesk-analytics',
            'superdesk-planning',
        ],

        defaultRoute: '/workspace/monitoring',

        langOverride: {
            en: {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY'
            }
        },

        view: {
            timeformat: 'HH:mm',
            dateformat: 'DD.MM.YYYY',
        },

        shortDateFormat: 'DD/MM',
        
        editor3: { browserSpellCheck: true, },

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
                publishAndContinue: true,
            },
            validatePointOfInterestForImages: true,
            editorHighlights: true,
            editFeaturedImage: true,
            searchShortcut: true,
            elasticHighlight: true,
            planning: true,
            autorefreshContent: true,
        },
        
        item_profile: { change_profile: 1 },

        workspace: {
            analytics: true,
            planning: true,
            assignments: true,
        },
        
        monitoring: {
            scheduled: {
                sort: {
                    default: { field: 'publish_schedule', order: 'asc' },
                    allowed_fields_to_sort: [ 'publish_schedule' ]
                }
            },
        },   

    };
};
