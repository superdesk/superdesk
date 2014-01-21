define([], function() {
    'use strict';

    /**
      * Return url for given view within an app
      *
      * @param {string} view
      * @param {Object} app
      * @returns {string} url
      */
    return function(view, app) {
        return 'scripts/' + app.name.replace('.', '-') + '/views/' + view;
    };
});