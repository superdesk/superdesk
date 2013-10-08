define([
    'angular',
    'angular-gettext',
    'translations'
], function(angular) {
    'use strict';

    angular.module('superdesk.l10n', ['gettext']).
        run(function(gettextCatalog, $location) {
            var params = $location.search();
            if ('lang' in params) {
                gettextCatalog.currentLanguage = params.lang;
                gettextCatalog.debug = true;
            }
        });
});