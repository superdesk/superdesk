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
            customAuthoringTopbar: true
        },
        shortTimeFormat: 'YYYY-MM-DD HH:mm',
        shortDateFormat: 'YYYY-MM-DD HH:mm',
        shortWeekFormat: 'YYYY-MM-DD HH:mm',
        longDateFromat: 'YYYY-MM-DD HH:mm'
    };
};
