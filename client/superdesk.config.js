/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name 'superdesk.config.js' found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        bodyClass: {
            'indent-article': 1
        },

        defaultTimezone: 'Europe/Oslo',

        shortTimeFormat: 'HH:mm, DD.MM.YYYY',
        shortDateFormat: 'HH:mm, DD.MM.YYYY',
        shortWeekFormat: 'HH:mm, DD.MM.YYYY',

        startingDay: '1',

        angular_i18n: 'angular-locale_no',

        view: {
            timeformat: 'HH:mm',
            dateformat: 'DD.MM.YYYY'
        },

        features: {
            preview: 1,
            alchemy: 1,
            customAuthoringTopbar: true,
            useTansaProofing: true,
            editFeaturedImage: 0,
            hideCreatePackage: true,
            customMonitoringWidget: true,
            scanpixSearchShortcut: true,
            noTakes: true
        },

        user: {
            'sign_off_mapping': 'email'
        },

        monitoring: {
            'scheduled': true
        },

        workspace: {
            ingest: 0,
            content: 0,
            tasks: 0
        },

        ui: {
            publishEmbargo: false,
            publishSendAdnContinue: false,
            italicAbstract: false
        },

        search_cvs: [
            {id: 'category', name:'Category', field: 'subject', list: 'category'},
            {id: 'subject', name:'Subject', field: 'subject', list: 'subject_custom'}
        ],

        search: {
            'slugline': 1,
            'headline': 1,
            'unique_name': 1,
            'story_text': 1,
            'byline': 1,
            'keywords': 0,
            'creator': 1,
            'from_desk': 1,
            'to_desk': 1
        },

        list: {
            priority: ['urgency'],
            firstLine: [
                'slugline',
                'takekey',
                'highlights',
                'headline',
                'provider',
                'update',
                'updated',
                'state',
                'versioncreated'
            ]
        },

        item_profile: {
            change_profile: 1
        },

        editor: {
            imageDragging: true
        },

        defaultRoute: '/workspace/monitoring',

        langOverride: {
            'en': {
                'Category': 'Service',
                'CATEGORY': 'SERVICE'
            },
            'de': {'My Profile': 'DE - My profile'}
        },

        requiredMediaMetadata: ['headline', 'description_text', 'alt_text']
    };
};
