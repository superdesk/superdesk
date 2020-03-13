/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: ['superdesk-planning'],
        importApps: ['superdesk-planning', '../index'],
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

        langOverride: {
            'en': {
                'ANPA Category': 'Category',
                'ANPA CATEGORY': 'CATEGORY'
            }
        },

        features: {
            swimlane: {columnsLimit: 4},
            editor3: true
        },

        workspace: {
            planning: true,
            assignments: true
        },

        list: {
            priority: [
                'priority',
                'urgency'
            ],
            firstLine: [
                'wordcount',
                'slugline',
                'highlights',
                'markedDesks',
                'associations',
                'publish_queue_errors',
                'headline',
                'assignment',
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
