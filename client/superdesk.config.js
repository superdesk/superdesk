/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        defaultRoute: '/workspace/personal',

        apps: [
            'superdesk.analytics',
            'superdesk-planning',
        ],

        importApps: [
            '../index',
            'superdesk-analytics',
            'superdesk-planning',
        ],

        view: {
            timeformat: 'HH:mm',
            dateformat: 'DD.MM.YYYY'
        },

        features: {
            preview: 1,
            swimlane: {columnsLimit: 4},
            noTakes: true,
            editor3: true,
            validatePointOfInterestForImages: false,
            editorHighlights: true,
            noPublishOnAuthoringDesk: true,
            noMissingLink: true,
            planning: true,
        },

        workspace: {
            planning: true,
            analytics: true,
            assignments: true,
        },
    };
};
