define([
    'angular',
    'angular-gettext',
    'translations'
], function(angular) {
    'use strict';

    angular.module('superdesk.services.translate', ['gettext']).
        run(['gettextCatalog', '$location', function(gettextCatalog, $location) {
            var params = $location.search();
            if ('lang' in params) {
                gettextCatalog.currentLanguage = params.lang;
                gettextCatalog.debug = true;
            }
        }]).
        factory('gettext', function(gettextCatalog) {
            return function(input) {
                return gettextCatalog.getString(input);
            };
        });
});