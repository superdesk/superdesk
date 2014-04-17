define([
    'angular',
    'translations',
    'angular-gettext'
], function(angular) {
    'use strict';

    /**
     * Translate module
     *
     * This module provides localization support.
     * It's using angular-gettext.
     */
    return angular.module('superdesk.translate', ['gettext'])
        .run(['gettextCatalog', '$location', function(gettextCatalog, $location) {
            var params = $location.search();
            if ('lang' in params) {
                gettextCatalog.currentLanguage = params.lang;
                gettextCatalog.debug = true;
            }
        }])
        /**
         * Gettext service to be used in controllers/services/directives.
         *
         * Usage:
         * function($scope, gettext) { $scope.translatedMessage = gettext("Translate Me"); }
         *
         * This way "Translate Me" can be found by the string extractor and it will return
         * translated string if appropriet.
         */
        .factory('gettext', ['gettextCatalog', function(gettextCatalog) {
            return function(input) {
                return gettextCatalog.getString(input);
            };
        }]);
});
