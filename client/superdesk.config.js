/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: ['ansa.superdesk'],
        importApps: ['../ansa'],
        defaultRoute: '/workspace/monitoring',
        workspace: {
            ingest: 1,
            content: 1,
            //planning: 1,
            //assignments: 1,
        },
        features: {
            customAuthoringTopbar: true,
            editFeaturedImage: true,
            searchShortcut: true
        },
        shortTimeFormat: 'YYYY-MM-DD HH:mm',
        shortDateFormat: 'YYYY-MM-DD HH:mm',
        shortWeekFormat: 'YYYY-MM-DD HH:mm',
        longDateFromat: 'YYYY-MM-DD HH:mm',

        langOverride: {
            'en': {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY'
            },
            'it': {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY'
            }
        }, 

        validatorMediaMetadata: {
            headline: {
                required: true
            },
            alt_text: {
                required: false
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

        list: {
            priority: [
                'priority',
                'urgency'
            ],
            firstLine: [
                'wordcount',
                'highlights',
                'markedDesks',
                'associations',
                'publish_queue_errors',
                'headline',
                'versioncreated'
            ],
            secondLine: [
                'profile',
                'state',
                'embargo',
                'update',
                'takekey',
                'signal',
                'broadcast',
                'flags',
                'updated',
                'category',
                'provider',
                'expiry',
                'desk',
                'fetchedDesk'
            ]
        }
    };
};
