/**
 * This is the default configuration file for the Superdesk application. By default,
 * the app will use the file with the name "superdesk.config.js" found in the current
 * working directory, but other files may also be specified using relative paths with
 * the SUPERDESK_CONFIG environment variable or the grunt --config flag.
 */
module.exports = function(grunt) {
    return {
        shortTimeFormat: 'HH:mm',
        shortWeekFormat: 'dddd, HH:mm',
        shortDateFormat: 'DD/MM',

        previewSubjectFilterKey: 'patopic',

        features: {
            preview: 1,
            alchemy: 1,
            autopopulateByline: 1
        },

        view: {
            dateformat: 'D/M/YYYY',
            timeformat: 'H:mm'
        },

        editor: {
            imageDragging: true,
            vidible: true // enable vidible as embed provider
        },

        ui: {
            italicAbstract: true
        }
    };
};
