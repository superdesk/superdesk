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
            sendToPersonal: true,
            publishFromPersonal: true,
        },
        shortTimeFormat: 'YYYY-MM-DD HH:mm',
        shortDateFormat: 'YYYY-MM-DD HH:mm',
        shortWeekFormat: 'YYYY-MM-DD HH:mm',
        longDateFromat: 'YYYY-MM-DD HH:mm',

        authoring: {
            stickyLineCount: true,
            timeToRead: false,
            lineLength: 64,
            preview: {
                hideContentLabels: true,
            },
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
            sendPublishSchedule: false,
            sendEmbargo: false,
            sendDefaultStage: 'working',

            authoring: {
                firstLine: {
                    wordCount: false,
                },
            },
        },

        search_cvs: [
            {id: 'products', name: 'Product', field: 'subject', list: 'products'},
            {id: 'subject', name: 'Subject', field: 'subject', list: 'subjectcodes'},
        ],

        search: {
            'slugline': 0,
            'headline': 1,
            'unique_name': 0,
            'story_text': 1,
            'byline': 1,
            'keywords': 0,
            'creator': 1,
            'from_desk': 0,
            'to_desk': 0,
            'spike': 1,
            'ingest_provider': 1,
            'marked_desks': 0,
            'firstpublished': 1,
            'sign_off': 1,
            'featuremedia': 1,
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
                'used',
            ]
        },
        gridViewFields: [
            'byline',
            'source',
            'copyright',
            'usageterms',
            'used',
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
        },
    };
};
