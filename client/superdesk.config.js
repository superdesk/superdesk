/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        apps: ['ansa.superdesk', 'superdesk-planning'],
        importApps: ['../ansa', 'superdesk-planning'],
        defaultRoute: '/workspace/monitoring',
        workspace: {
            ingest: 1,
            content: 0,
            planning: 1,
            assignments: 1,
        },
        features: {
            preview: true,
            customAuthoringTopbar: {
                toDesk: false,
                publish: true,
                publishAndContinue: true,
            },
            editFeaturedImage: true,
            searchShortcut: true,
            editor3: true,
            validatePointOfInterestForImages: false,
            keepMetaTermsOpenedOnClick: true,
            showCharacterLimit: 64,
        },
        shortTimeFormat: 'YYYY-MM-DD HH:mm',
        shortDateFormat: 'YYYY-MM-DD HH:mm',
        shortWeekFormat: 'YYYY-MM-DD HH:mm',
        longDateFromat: 'YYYY-MM-DD HH:mm',

        authoring: {
            timeToRead: false,
            lineLength: 64,
        },

        language: 'it',
        profileLanguages: [
            'en',
            //'it',
        ],

        editor3: {
            browserSpellCheck: true,
        },

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

        item_profile: {
            change_profile: 1,
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

        ui: {
            italicAbstract: false,
            sendAndPublish: true,
        },

        search_cvs: [
            {id: 'products', name: 'Product', field: 'subject', list: 'products'},
            {id: 'subject', name: 'Subject', field: 'subject', list: 'subjectcodes'},
        ],

        list: {
            priority: [
                'priority',
                'urgency'
            ],
            firstLine: [
                'wordcount',
                'highlights',
                'markedDesks',
                'associatedItems',
                'publish_queue_errors',
                'headline',
                'versioncreated',
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
                'fetchedDesk',
                'copyright',
                'usageterms',
            ]
        },
        gridViewFields: [
            'byline',
            'source',
            'copyright',
            'usageterms',
        ],

        defaultSearch: {
            ingest: false,
            archive: false,
            archived: false,
            published: true,
        },

        enabledExtensions: {
            imageShortcuts: 1,
            ansaIptc: 1,
        },

        view: {
          timeformat: 'HH:mm:ss'
        }
    };
};
