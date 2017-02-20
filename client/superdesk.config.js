/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        defaultRoute: '/workspace/monitoring',
        requiredMediaMetadata: ['description_text'],
        workspace: {
            ingest: 1,
            content: 1
        },
        features: {
            customAuthoringTopbar: true,
            editFeaturedImage: true
        },
        shortTimeFormat: 'YYYY-MM-DD HH:mm',
        shortDateFormat: 'YYYY-MM-DD HH:mm',
        shortWeekFormat: 'YYYY-MM-DD HH:mm',
        longDateFromat: 'YYYY-MM-DD HH:mm',

        publisher: {
            protocol: 'http',
            tenant: 'default',
            domain: '172.20.14.91',
            base: 'api/v1'
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
    };
};
